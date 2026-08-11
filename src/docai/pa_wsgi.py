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
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        parser = get_parser(bank)
        result = parser.parse(tmp_path)
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
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
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


def application(environ, start_response):
    path = environ.get("PATH_INFO", "") or "/"
    method = environ.get("REQUEST_METHOD", "GET")
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