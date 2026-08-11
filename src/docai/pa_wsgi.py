"""Pure-WSGI adapter for PythonAnywhere.

Serves the same endpoints as the FastAPI app in ``docai.api`` but with zero
framework dependencies (no fastapi / a2wsgi / anyio), so it runs reliably
under PythonAnywhere's uWSGI worker:

    GET  /health        → {"status": "ok", "banks": [...]}
    GET  /              → static demo page (web/index.html)
    GET  /docs          → Swagger UI HTML
    GET  /openapi.json  → OpenAPI 3.0 spec
    POST /parse         → multipart PDF upload, JSON or CSV response
    POST /verify-income → parse + income verification report

The FastAPI app remains the canonical API for local development; this module
is a thin, synchronous WSGI mirror used only for PA hosting.
"""

from __future__ import annotations

import calendar
import io
import json
import os
import tempfile
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

from python_multipart import parse_form

from docai.base import ParseError, PasswordProtectedError
from docai.parsers.registry import get_parser, list_banks
from docai.serialization import result_to_csv, result_to_dict
from docai.validation import ValidationError, validate_statement

WEB_DIR = Path(__file__).resolve().parent.parent.parent / "web"
_USAGE_FILE = Path(__file__).resolve().parent / "usage.json"

# --- Tier limits --------------------------------------------------------------

TIER_LIMITS = {
    "free": 100,
    "starter": 500,
    "growth": 5000,
    "scale": 50000,
    "enterprise": 0,  # 0 = unlimited
}

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


def _get_api_key(environ) -> str:
    """Get API key from environ."""
    return environ.get("HTTP_X_API_KEY", "")


# --- Usage tracking ----------------------------------------------------------

def _load_usage() -> dict:
    """Load usage data from usage.json."""
    try:
        return json.loads(_USAGE_FILE.read_text("utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_usage(data: dict) -> None:
    """Write usage data to usage.json."""
    _USAGE_FILE.write_text(json.dumps(data, indent=2), "utf-8")


def _track_usage(api_key: str) -> Tuple[bool, int, int]:
    """Increment counter for the key and check limits.

    Returns (allowed, remaining, limit).
    """
    usage = _load_usage()
    key_data = usage.get(api_key, {
        "tier": "free",
        "calls_this_month": 0,
        "last_call": None,
        "total_calls": 0,
    })

    # Check current month
    now = datetime.now(timezone.utc)
    current_month = now.strftime("%Y-%m")

    # If the key has never been used, initialize
    if key_data.get("last_call") is None:
        key_data["calls_this_month"] = 0
    else:
        # Check if we're in a new month
        last_call_month = key_data["last_call"][:7]
        if last_call_month != current_month:
            key_data["calls_this_month"] = 0

    tier = key_data.get("tier", "free")
    limit = TIER_LIMITS.get(tier, 100)

    # Check if limit is exceeded
    if limit != 0 and key_data["calls_this_month"] >= limit:
        return (False, 0, limit)

    # Increment counter
    key_data["calls_this_month"] += 1
    key_data["total_calls"] += 1
    key_data["last_call"] = now.isoformat()

    usage[api_key] = key_data
    _save_usage(usage)

    remaining = max(0, limit - key_data["calls_this_month"]) if limit != 0 else 999999
    return (True, remaining, limit)


def _check_rate_limit(api_key: str) -> Tuple[bool, int, int]:
    """Check rate limit without incrementing.

    Returns (allowed, remaining, limit).
    """
    usage = _load_usage()
    key_data = usage.get(api_key, {
        "tier": "free",
        "calls_this_month": 0,
        "last_call": None,
        "total_calls": 0,
    })

    now = datetime.now(timezone.utc)
    current_month = now.strftime("%Y-%m")

    if key_data.get("last_call") is not None:
        last_call_month = key_data["last_call"][:7]
        if last_call_month != current_month:
            key_data["calls_this_month"] = 0

    tier = key_data.get("tier", "free")
    limit = TIER_LIMITS.get(tier, 100)

    if limit != 0 and key_data["calls_this_month"] >= limit:
        return (False, 0, limit)

    remaining = max(0, limit - key_data["calls_this_month"]) if limit != 0 else 999999
    return (True, remaining, limit)


def _get_reset_timestamp() -> int:
    """Get unix timestamp of end of current month (UTC)."""
    now = datetime.now(timezone.utc)
    _, last_day = calendar.monthrange(now.year, now.month)
    reset = datetime(now.year, now.month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    return int(reset.timestamp())


def _rate_limit_headers(api_key: str) -> List[Tuple[str, str]]:
    """Generate rate limit headers for a response."""
    allowed, remaining, limit = _check_rate_limit(api_key)
    reset = _get_reset_timestamp()
    limit_str = str(limit) if limit != 0 else "unlimited"
    return [
        ("X-RateLimit-Limit", limit_str),
        ("X-RateLimit-Remaining", str(remaining)),
        ("X-RateLimit-Reset", str(reset)),
    ]


def _rate_limit_start_response(start_response, api_key: str):
    """Create a wrapper around start_response that adds rate limit headers."""
    def wrapper(status, headers):
        allowed, remaining, limit = _check_rate_limit(api_key)
        reset = _get_reset_timestamp()
        limit_str = str(limit) if limit != 0 else "unlimited"
        headers = list(headers)
        headers.extend([
            ("X-RateLimit-Limit", limit_str),
            ("X-RateLimit-Remaining", str(remaining)),
            ("X-RateLimit-Reset", str(reset)),
        ])
        return start_response(status, headers)
    return wrapper


# --- PDF decryption ----------------------------------------------------------

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


# --- Response helpers --------------------------------------------------------

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


# --- Rate limit response ----------------------------------------------------

def _rate_limit_exceeded(start_response, api_key: str):
    """Return 429 Too Many Requests."""
    usage = _load_usage()
    key_data = usage.get(api_key, {})
    tier = key_data.get("tier", "free")
    limit = TIER_LIMITS.get(tier, 100)
    reset_ts = _get_reset_timestamp()
    reset_iso = datetime.fromtimestamp(reset_ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "error": "rate_limit_exceeded",
        "message": f"You have exceeded your monthly limit of {limit} API calls. Upgrade your plan at docaiid.pythonanywhere.com/pricing",
        "limit": limit,
        "remaining": 0,
        "reset": reset_iso,
    }

    rate_headers = [
        ("X-RateLimit-Limit", str(limit)),
        ("X-RateLimit-Remaining", "0"),
        ("X-RateLimit-Reset", str(reset_ts)),
    ]

    return _json_response(start_response, "429 Too Many Requests", payload, rate_headers)


# --- Request handlers --------------------------------------------------------

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


# --- Static HTML serving -----------------------------------------------------

def _serve_static_html(environ, start_response, path: str):
    """Serve a static HTML file from WEB_DIR if it exists."""
    if path.endswith(".html"):
        candidate = WEB_DIR / path.lstrip("/")
        if candidate.exists():
            return _file_response(start_response, candidate, "text/html; charset=utf-8")
    return None


# --- OpenAPI / Swagger docs --------------------------------------------------

def _openapi_spec() -> dict:
    """Return the OpenAPI 3.0 specification."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "DocAI Verify",
            "description": "Income verification API for Indonesian fintech",
            "version": "2.0.0",
        },
        "servers": [{"url": "https://docaiid.pythonanywhere.com"}],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "description": "Returns service status and supported banks.",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "ok"},
                                            "banks": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                                "example": ["bca", "mandiri"],
                                            },
                                        },
                                    }
                                }
                            },
                        },
                    },
                }
            },
            "/parse": {
                "post": {
                    "summary": "Parse bank statement PDF",
                    "description": "Upload a bank statement PDF and receive structured data in JSON or CSV format.",
                    "security": [{"ApiKeyAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["file"],
                                    "properties": {
                                        "file": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "Bank statement PDF file",
                                        },
                                        "bank": {
                                            "type": "string",
                                            "default": "bca",
                                            "description": "Bank identifier (bca, mandiri, etc.)",
                                        },
                                        "password": {
                                            "type": "string",
                                            "description": "PDF password (DOB DDMMYYYY) for encrypted statements",
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "parameters": [
                        {
                            "name": "format",
                            "in": "query",
                            "schema": {"type": "string", "enum": ["json", "csv"], "default": "json"},
                            "description": "Response format",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Parsed statement data",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ParseResponse"}
                                },
                                "text/csv": {
                                    "schema": {"type": "string"}
                                },
                            },
                        },
                        "400": {
                            "description": "Invalid request (bad format, missing file, password error, parse error)",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "401": {
                            "description": "Missing or invalid API key",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "429": {
                            "description": "Rate limit exceeded",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/RateLimitError"}
                                }
                            },
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                }
            },
            "/verify-income": {
                "post": {
                    "summary": "Verify income from bank statement",
                    "description": "Parse a bank statement and return an income verification report.",
                    "security": [{"ApiKeyAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["file"],
                                    "properties": {
                                        "file": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "Bank statement PDF file",
                                        },
                                        "bank": {
                                            "type": "string",
                                            "default": "bca",
                                            "description": "Bank identifier (bca, mandiri, etc.)",
                                        },
                                        "password": {
                                            "type": "string",
                                            "description": "PDF password (DOB DDMMYYYY) for encrypted statements",
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Income verification report",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/VerifyIncomeResponse"}
                                }
                            },
                        },
                        "400": {
                            "description": "Invalid request (bad format, missing file, password error, parse error)",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "401": {
                            "description": "Missing or invalid API key",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "429": {
                            "description": "Rate limit exceeded",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/RateLimitError"}
                                }
                            },
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                }
            },
        },
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                }
            },
            "schemas": {
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "unauthorized"},
                        "message": {"type": "string", "example": "Missing or invalid X-API-Key header"},
                    },
                },
                "RateLimitError": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "rate_limit_exceeded"},
                        "message": {"type": "string"},
                        "limit": {"type": "integer", "example": 100},
                        "remaining": {"type": "integer", "example": 0},
                        "reset": {"type": "string", "format": "date-time", "example": "2026-09-01T00:00:00Z"},
                    },
                },
                "ParseResponse": {
                    "type": "object",
                    "properties": {
                        "bank": {"type": "string", "example": "bca"},
                        "account_number": {"type": "string", "example": "1234567890"},
                        "account_name": {"type": "string", "example": "John Doe"},
                        "statement_period": {"type": "string", "example": "01/01/2026 - 31/01/2026"},
                        "opening_balance": {"type": "number", "example": 5000000.0},
                        "closing_balance": {"type": "number", "example": 9929972.0},
                        "currency": {"type": "string", "example": "IDR"},
                        "balance_check": {"type": "string", "example": "passed"},
                        "validation_error": {"type": "string"},
                        "transactions": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Transaction"},
                        },
                    },
                },
                "Transaction": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "example": "02/01/2026"},
                        "description": {"type": "string", "example": "TRANSFER DARI BCA"},
                        "debit": {"type": "number", "example": 0},
                        "credit": {"type": "number", "example": 1500000},
                        "balance": {"type": "number", "example": 5150000},
                        "reference": {"type": "string", "example": "TRX12345"},
                    },
                },
                "VerifyIncomeResponse": {
                    "type": "object",
                    "properties": {
                        "verification_score": {"type": "number", "example": 85},
                        "confidence": {"type": "string", "example": "high"},
                        "detected_monthly_income": {"type": "number", "example": 15000000},
                        "income_source": {"type": "string", "example": "salary"},
                        "salary_months_detected": {"type": "integer", "example": 6},
                        "monthly_incomes": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/MonthlyIncome"},
                        },
                        "consistency_score": {"type": "number", "example": 0.92},
                        "income_cv": {"type": "number", "example": 0.15},
                        "has_gaps": {"type": "boolean", "example": False},
                        "gap_months": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "fraud_flags": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "balance_valid": {"type": "boolean", "example": True},
                        "has_suspicious_patterns": {"type": "boolean", "example": False},
                        "statement_period": {"type": "string", "example": "01/01/2026 - 31/01/2026"},
                        "total_months_covered": {"type": "integer", "example": 6},
                        "total_transactions": {"type": "integer", "example": 120},
                        "total_credit": {"type": "number", "example": 90000000},
                        "total_debit": {"type": "number", "example": 45000000},
                        "bank": {"type": "string", "example": "bca"},
                        "account_number": {"type": "string", "example": "1234567890"},
                    },
                },
                "MonthlyIncome": {
                    "type": "object",
                    "properties": {
                        "month": {"type": "string", "example": "2026-01"},
                        "amount": {"type": "number", "example": 15000000},
                        "source": {"type": "string", "example": "salary"},
                        "confidence": {"type": "string", "example": "high"},
                    },
                },
            },
        },
    }


_SWAGGER_UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocAI Verify — API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui.css" />
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #f8f9fa;
        }
        .topbar {
            background: #1a1a2e;
            padding: 12px 24px;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .topbar img {
            height: 32px;
        }
        .topbar h1 {
            color: #fff;
            font-size: 18px;
            margin: 0;
        }
        .topbar a {
            color: #4fc3f7;
            text-decoration: none;
            font-size: 14px;
            margin-left: auto;
        }
        #swagger-ui {
            max-width: 960px;
            margin: 0 auto;
            padding: 16px;
        }
    </style>
</head>
<body>
    <div class="topbar">
        <img src="https://docaiid.pythonanywhere.com/assets/logo_docai_400.png" alt="DocAI" onerror="this.style.display='none'">
        <h1>DocAI Verify API</h1>
        <a href="/openapi.json">OpenAPI Spec</a>
    </div>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
            layout: "BaseLayout"
        });
    </script>
</body>
</html>"""


def _handle_docs(environ, start_response):
    """GET /docs — Swagger UI HTML page."""
    body = _SWAGGER_UI_HTML.encode("utf-8")
    start_response(
        "200 OK",
        [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


def _handle_openapi_json(environ, start_response):
    """GET /openapi.json — OpenAPI 3.0 specification."""
    spec = _openapi_spec()
    body = json.dumps(spec, indent=2).encode("utf-8")
    start_response(
        "200 OK",
        [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


# --- WSGI application --------------------------------------------------------

def application(environ, start_response):
    path = environ.get("PATH_INFO", "") or "/"
    method = environ.get("REQUEST_METHOD", "GET")

    # Serve public static HTML pages without auth
    if method == "GET":
        static_result = _serve_static_html(environ, start_response, path)
        if static_result is not None:
            return static_result

    try:
        _check_api_key(environ)
    except PermissionError as e:
        return _json_response(
            start_response,
            "401 Unauthorized",
            {"error": "unauthorized", "message": str(e)},
        )

    # Wrap start_response to add rate limit headers for API endpoints
    api_key = _get_api_key(environ)
    is_api_endpoint = path in ("/parse", "/verify-income")

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
        if path == "/docs" and method == "GET":
            return _handle_docs(environ, start_response)
        if path == "/openapi.json" and method == "GET":
            return _handle_openapi_json(environ, start_response)
        if path == "/parse" and method == "POST":
            # Check rate limit
            allowed, remaining, limit = _check_rate_limit(api_key)
            if not allowed:
                return _rate_limit_exceeded(start_response, api_key)
            # Track usage and get headers
            allowed_after_track, remaining_after_track, limit_after_track = _track_usage(api_key)
            sr = _rate_limit_start_response(start_response, api_key)
            return _handle_parse(environ, sr)
        if path == "/verify-income" and method == "POST":
            # Check rate limit
            allowed, remaining, limit = _check_rate_limit(api_key)
            if not allowed:
                return _rate_limit_exceeded(start_response, api_key)
            # Track usage and get headers
            allowed_after_track, remaining_after_track, limit_after_track = _track_usage(api_key)
            sr = _rate_limit_start_response(start_response, api_key)
            return _handle_verify_income(environ, sr)
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