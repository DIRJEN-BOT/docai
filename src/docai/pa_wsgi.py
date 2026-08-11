"""Pure-WSGI adapter for PythonAnywhere.

Serves the same endpoints as the FastAPI app in ``docai.api`` but with zero
framework dependencies (no fastapi / a2wsgi / anyio), so it runs reliably
under PythonAnywhere's uWSGI worker:

    GET  /health  → {"status": "ok", "banks": [...]}
    GET  /        → static demo page (web/index.html)
    POST /parse   → multipart PDF upload, JSON or CSV response

The FastAPI app remains the canonical API for local development; this module
is a thin, synchronous WSGI mirror used only for PA hosting.
"""

from __future__ import annotations

import io
import json
import os
import tempfile
import urllib.parse
from pathlib import Path
from typing import List, Tuple

from python_multipart import parse_form

from docai.base import ParseError, PasswordProtectedError
from docai.parsers.registry import get_parser, list_banks
from docai.serialization import result_to_csv, result_to_dict
from docai.validation import ValidationError, validate_statement

WEB_DIR = Path(__file__).resolve().parent.parent.parent / "web"

# --- API key authentication ---------------------------------------------------

API_KEYS: dict[str, dict] = {
    "docai-dev-key-12345": {"tier": "free", "name": "Development"},
}

_EXEMPT_PATHS = frozenset({"/health", "/", "/docs", "/openapi.json"})


def _check_api_key(environ) -> None:
    """Raise if X-API-Key header is missing/invalid. Exempt paths skip check."""
    path = environ.get("PATH_INFO", "") or "/"
    if path in _EXEMPT_PATHS:
        return
    key = environ.get("HTTP_X_API_KEY", "")
    if not key or key not in API_KEYS:
        raise PermissionError("Missing or invalid X-API-Key header")


def _decrypt_pdf_wsgi(src_path: str, password: str) -> str:
    """Decrypt a password-protected PDF to a temp file.  Caller cleans up."""
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


def _json_response(
    start_response,
    status: str,
    payload,
    extra_headers: List[Tuple[str, str]] = (),
):
    body = json.dumps(payload).encode("utf-8")
    start_response(
        status,
        [("Content-Type", "application/json"), ("Content-Length", str(len(body)))]
        + list(extra_headers),
    )
    return [body]


def _file_response(start_response, path: Path, media_type: str):
    data = path.read_bytes()
    start_response(
        "200 OK",
        [("Content-Type", media_type), ("Content-Length", str(len(data)))],
    )
    return [data]


def _handle_parse(environ, start_response):
    content_type = environ.get("CONTENT_TYPE", "")
    length = environ.get("CONTENT_LENGTH") or "0"
    try:
        length = int(length)
    except ValueError:
        length = 0
    if length <= 0:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "invalid_request", "message": "Empty request body"},
        )
    raw = environ["wsgi.input"].read(length)

    qs = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
    fmt = qs.get("format", ["json"])[0]
    if fmt not in ("json", "csv"):
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "invalid_request", "message": "format must be json or csv"},
        )

    fields: dict = {}
    uploaded = []

    def on_field(f):
        if f.field_name is not None and f.value is not None:
            fields[f.field_name.decode("utf-8", "replace")] = f.value.decode(
                "utf-8", "replace"
            )

    def on_file(f):
        uploaded.append(f)

    parse_form(
        headers={"Content-Type": content_type},
        input_stream=io.BytesIO(raw),
        on_field=on_field,
        on_file=on_file,
    )

    bank = fields.get("bank", "bca")
    password = fields.get("password") or None
    if not uploaded:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "invalid_request", "message": "No file uploaded (field 'file')"},
        )
    file_obj = uploaded[0].file_object
    file_obj.seek(0)  # python_multipart leaves the stream at EOF after parsing
    data = file_obj.read()
    if not data:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "invalid_request", "message": "Empty file uploaded"},
        )

    tmp_path = None
    decrypted_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        parser = get_parser(bank)
        try:
            result = parser.parse(tmp_path)
        except PasswordProtectedError:
            if not password:
                raise
            decrypted_path = _decrypt_pdf_wsgi(tmp_path, password)
            result = parser.parse(decrypted_path)
    except PasswordProtectedError as e:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "password_protected", "message": str(e)},
        )
    except ParseError as e:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "parse_error", "message": str(e)},
        )
    except ValueError as e:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "invalid_request", "message": str(e)},
        )
    finally:
        for p in (tmp_path, decrypted_path):
            if p is not None:
                try:
                    os.unlink(p)
                except OSError:
                    pass

    balance_status = "passed"
    validation_error = None
    try:
        validate_statement(result)
    except ValidationError as e:
        balance_status = "failed"
        validation_error = str(e)

    if fmt == "csv":
        csv_text = result_to_csv(result)
        body = csv_text.encode("utf-8")
        start_response(
            "200 OK",
            [
                ("Content-Type", "text/csv; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Content-Disposition", 'attachment; filename="mutasi.csv"'),
            ],
        )
        return [body]

    payload = result_to_dict(result, balance_status)
    if validation_error is not None:
        payload["validation_error"] = validation_error
    return _json_response(start_response, "200 OK", payload)


# --- Income verification ------------------------------------------------------

try:
    from docai.scoring import analyze_income as _analyze_income  # type: ignore[import-untyped]
except ImportError:

    def _analyze_income(result):  # type: ignore[misc]
        """Stub scoring — returns basic report when scoring module is unavailable."""
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
            "total_credit": float(result.total_credit),
            "total_debit": float(result.total_debit),
            "bank": result.bank.value,
            "account_number": result.account_number,
        }


def _handle_verify_income(environ, start_response):
    """POST /verify-income — parse + income verification report."""
    content_type = environ.get("CONTENT_TYPE", "")
    length = environ.get("CONTENT_LENGTH") or "0"
    try:
        length = int(length)
    except ValueError:
        length = 0
    if length <= 0:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "invalid_request", "message": "Empty request body"},
        )
    raw = environ["wsgi.input"].read(length)

    fields: dict = {}
    uploaded = []

    def on_field(f):
        if f.field_name is not None and f.value is not None:
            fields[f.field_name.decode("utf-8", "replace")] = f.value.decode(
                "utf-8", "replace"
            )

    def on_file(f):
        uploaded.append(f)

    parse_form(
        headers={"Content-Type": content_type},
        input_stream=io.BytesIO(raw),
        on_field=on_field,
        on_file=on_file,
    )

    bank = fields.get("bank", "bca")
    password = fields.get("password") or None
    if not uploaded:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "invalid_request", "message": "No file uploaded (field 'file')"},
        )
    file_obj = uploaded[0].file_object
    file_obj.seek(0)
    data = file_obj.read()
    if not data:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "invalid_request", "message": "Empty file uploaded"},
        )

    tmp_path = None
    decrypted_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        parser = get_parser(bank)
        try:
            result = parser.parse(tmp_path)
        except PasswordProtectedError:
            if not password:
                raise
            decrypted_path = _decrypt_pdf_wsgi(tmp_path, password)
            result = parser.parse(decrypted_path)
    except PasswordProtectedError as e:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "password_protected", "message": str(e)},
        )
    except ParseError as e:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "parse_error", "message": str(e)},
        )
    except ValueError as e:
        return _json_response(
            start_response,
            "400 Bad Request",
            {"error": "invalid_request", "message": str(e)},
        )
    finally:
        for p in (tmp_path, decrypted_path):
            if p is not None:
                try:
                    os.unlink(p)
                except OSError:
                    pass

    balance_status = "passed"
    try:
        validate_statement(result)
    except ValidationError:
        balance_status = "failed"

    from dataclasses import asdict
    from decimal import Decimal as _D

    report = _analyze_income(result)
    report_dict = asdict(report)
    for key in ("detected_monthly_income", "total_credit", "total_debit"):
        if isinstance(report_dict.get(key), _D):
            report_dict[key] = float(report_dict[key])
    for mi in report_dict.get("monthly_incomes", []):
        if isinstance(mi.get("amount"), _D):
            mi["amount"] = float(mi["amount"])
    report_dict["balance_valid"] = balance_status == "passed"
    report_dict["bank"] = result.bank.value
    report_dict["account_number"] = result.account_number
    return _json_response(start_response, "200 OK", report_dict)


def application(environ, start_response):
    path = environ.get("PATH_INFO", "") or "/"
    method = environ.get("REQUEST_METHOD", "GET")
    try:
        _check_api_key(environ)
    except PermissionError as e:
        return _json_response(
            start_response,
            "401 Unauthorized",
            {"error": "unauthorized", "message": str(e)},
        )
    try:
        if path == "/health" and method == "GET":
            return _json_response(
                start_response, "200 OK", {"status": "ok", "banks": list_banks()}
            )
        if path == "/" and method == "GET":
            index = WEB_DIR / "index.html"
            if index.exists():
                return _file_response(start_response, index, "text/html; charset=utf-8")
            return _json_response(
                start_response,
                "404 Not Found",
                {"error": "not_found", "message": "landing page not found"},
            )
        if path == "/parse" and method == "POST":
            return _handle_parse(environ, start_response)
        if path == "/verify-income" and method == "POST":
            return _handle_verify_income(environ, start_response)
        return _json_response(
            start_response,
            "404 Not Found",
            {"error": "not_found", "message": f"unknown route {method} {path}"},
        )
    except Exception as e:  # noqa: BLE001 — a WSGI app must never leak a traceback
        return _json_response(
            start_response,
            "500 Internal Server Error",
            {"error": "internal_error", "message": f"{type(e).__name__}: {e}"},
        )