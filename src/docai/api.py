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
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional, Tuple

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
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


def _parse_and_validate(
    file: UploadFile, bank: str
) -> Tuple[ParseResult, str, Optional[str]]:
    """Persist the upload to disk, parse it, and run the balance check.

    Returns (result, balance_status, validation_error). The temp file is
    always removed, even when parsing raises.
    """
    tmp_path: Optional[str] = None
    try:
        # pdfplumber/pypdf need a real file path, so we write the upload to a
        # temp file. Using a fixed ".pdf" suffix lets the parser's own checks
        # decide what is actually a valid PDF.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        parser = get_parser(bank)
        result = parser.parse(tmp_path)
    finally:
        if tmp_path is not None:
            Path(tmp_path).unlink(missing_ok=True)

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
    file: UploadFile = File(...),
    bank: str = Form("bca"),
    format: str = Query("json", pattern="^(json|csv)$"),
):
    try:
        result, balance_status, validation_error = _parse_and_validate(file, bank)
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("docai.api:app", host="0.0.0.0", port=8000, reload=True)
