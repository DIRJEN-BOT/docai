"""FastAPI wrapper — expose the docai parser as a REST API.

Run with:
    uvicorn docai.api:app --host 0.0.0.0 --port 8000
or simply:
    python -m docai.api

Endpoints:
    GET  /health            → service status + supported banks
    GET  /                  → demo landing page (static web/index.html)
    POST /parse             → parse an uploaded statement PDF
         multipart: file (PDF), bank (default "bca")
         query: format=json|csv (default json)
    POST /verify-income     → parse + income verification report
"""

from __future__ import annotations

import io
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Optional, Tuple

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response

from docai.base import ParseError, PasswordProtectedError
from docai.models import ParseResult
from docai.parsers.registry import get_parser, list_banks
from docai.serialization import result_to_csv, result_to_dict
from docai.validation import ValidationError, validate_statement

app = FastAPI(
    title="DocAI — Indonesian Bank Statement Parser",
    description=(
        "Parse Indonesian bank e-statement PDFs (BCA, and soon Mandiri/BNI/BRI) "
        "into structured JSON or CSV — deterministic, with built-in balance validation."
    ),
    version="0.1.0",
)

# --- API key authentication ---------------------------------------------------

# Hardcoded keys (will move to env/database later)
API_KEYS: dict[str, dict] = {
    "docai-dev-key-12345": {"tier": "free", "name": "Development"},
}

_EXEMPT_PATHS = frozenset({"/health", "/", "/docs", "/openapi.json"})


async def _verify_api_key(request: Request) -> None:
    """Verify API key from X-API-Key header. Exempt health/landing/docs."""
    if request.url.path in _EXEMPT_PATHS:
        return
    key = request.headers.get("X-API-Key")
    if not key or key not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "unauthorized",
                "message": "Missing or invalid X-API-Key header",
            },
        )


# Allow browser demo pages (file:// or any origin) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = Path(__file__).resolve().parent.parent.parent / "web"


def _http_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"error": code, "message": message})


@app.exception_handler(HTTPException)
async def _handle_http_exception(request, exc: HTTPException) -> JSONResponse:
    """Return errors as {"error": <code>, "message": <text>} instead of {"detail": ...}."""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "error", "message": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def _handle_validation_error(request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "message": str(exc.errors()[0]["msg"])},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "banks": list_banks()}


@app.get("/", include_in_schema=False)
def landing() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


def _decrypt_pdf(src_path: str, password: str) -> str:
    """Decrypt a password-protected PDF and write the unlocked copy to a temp file.

    Returns the path to the decrypted file.  Caller is responsible for cleanup.
    Password is never logged or stored.
    """
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(src_path)
    if not reader.decrypt(password):
        raise PasswordProtectedError("Incorrect password for this PDF.")
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    with open(tmp.name, "wb") as f:
        writer.write(f)
    return tmp.name


def _parse_and_validate(
    file: UploadFile,
    bank: str,
    password: Optional[str] = None,
) -> Tuple[ParseResult, str, Optional[str]]:
    """Persist the upload to disk, parse it, and run the balance check.

    If *password* is provided and the PDF is encrypted, decrypt first.
    Returns (result, balance_status, validation_error).  Temp files are
    always removed, even when parsing raises.
    """
    tmp_path: Optional[str] = None
    decrypted_path: Optional[str] = None
    try:
        # pdfplumber/pypdf need a real file path, so we write the upload to a
        # temp file. Using a fixed ".pdf" suffix lets the parser's own checks
        # decide what is actually a valid PDF.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        parser = get_parser(bank)
        try:
            result = parser.parse(tmp_path)
        except PasswordProtectedError:
            if not password:
                raise
            # Decrypt and retry
            decrypted_path = _decrypt_pdf(tmp_path, password)
            result = parser.parse(decrypted_path)
    finally:
        if tmp_path is not None:
            Path(tmp_path).unlink(missing_ok=True)
        if decrypted_path is not None:
            Path(decrypted_path).unlink(missing_ok=True)

    balance_status = "passed"
    validation_error: Optional[str] = None
    try:
        validate_statement(result)
    except ValidationError as e:
        balance_status = "failed"
        validation_error = str(e)
    return result, balance_status, validation_error


@app.post("/parse", response_model=None)
def parse(
    _auth: None = Depends(_verify_api_key),
    file: UploadFile = File(..., description="Bank statement PDF"),
    bank: str = Form("bca", description="Bank identifier or 'auto'"),
    password: Optional[str] = Form(None, description="PDF password (DOB DDMMYYYY)"),
    format: str = Query("json", pattern="^(json|csv)$"),
):
    try:
        result, balance_status, validation_error = _parse_and_validate(
            file, bank, password=password
        )
    except PasswordProtectedError as e:
        raise _http_error(400, "password_protected", str(e))
    except ParseError as e:
        raise _http_error(400, "parse_error", str(e))
    except ValueError as e:
        raise _http_error(400, "invalid_request", str(e))

    if format == "csv":
        csv_text = result_to_csv(result)
        return Response(
            content=csv_text,
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="mutasi.csv"'
            },
        )

    payload = result_to_dict(result, balance_status)
    if validation_error is not None:
        payload["validation_error"] = validation_error
    return payload


# --- Income verification ------------------------------------------------------

try:
    from docai.scoring import analyze_income, IncomeReport  # type: ignore[import-untyped]
except ImportError:

    def analyze_income(result: ParseResult) -> dict:  # type: ignore[misc]
        """Stub scoring — returns basic report when scoring module is unavailable."""
        credits = [t.credit for t in result.transactions if t.credit > 0]
        total_credit = sum(credits, result.opening_balance.__class__(0))
        return {
            "verification_score": 0,
            "confidence": "low",
            "detected_monthly_income": 0,
            "income_source": "undetected",
            "salary_months_detected": 0,
            "monthly_incomes": [],
            "consistency_score": 0,
            "income_cv": 0.0,
            "has_gaps": False,
            "gap_months": [],
            "fraud_flags": [],
            "balance_valid": True,
            "has_suspicious_patterns": False,
            "statement_period": result.statement_period,
            "total_months_covered": 0,
            "total_transactions": len(result.transactions),
            "total_credit": float(total_credit),
            "total_debit": float(result.total_debit),
            "bank": result.bank.value,
            "account_number": result.account_number,
        }


@app.post("/verify-income", response_model=None)
def verify_income(
    _auth: None = Depends(_verify_api_key),
    file: UploadFile = File(..., description="Bank statement PDF"),
    bank: str = Form("bca", description="Bank identifier or 'auto'"),
    password: Optional[str] = Form(None, description="PDF password (DOB DDMMYYYY)"),
):
    """Parse a bank statement and return income verification report."""
    try:
        result, balance_status, _validation_error = _parse_and_validate(
            file, bank, password=password
        )
    except PasswordProtectedError as e:
        raise _http_error(400, "password_protected", str(e))
    except ParseError as e:
        raise _http_error(400, "parse_error", str(e))
    except ValueError as e:
        raise _http_error(400, "invalid_request", str(e))

    report = analyze_income(result)
    # IncomeReport is a dataclass with Decimal fields — convert for JSON
    from dataclasses import asdict

    report_dict = asdict(report)
    # JSON-encode Decimals → floats
    for key in ("detected_monthly_income", "total_credit", "total_debit"):
        if isinstance(report_dict.get(key), Decimal):
            report_dict[key] = float(report_dict[key])
    for mi in report_dict.get("monthly_incomes", []):
        if isinstance(mi.get("amount"), Decimal):
            mi["amount"] = float(mi["amount"])
    report_dict["balance_valid"] = balance_status == "passed"
    report_dict["bank"] = result.bank.value
    report_dict["account_number"] = result.account_number
    return report_dict


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("docai.api:app", host="0.0.0.0", port=8000, reload=True)
