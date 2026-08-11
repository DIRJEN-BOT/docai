"""Offline test for docai.pa_wsgi on PythonAnywhere.

Run from console:  python3 /home/docaiid/pa_wsgi_test.py
Writes results to /home/docaiid/pa_wsgi_test_out.txt (readable via files API).
"""

import io
import json
import sys
import traceback
import uuid
from pathlib import Path

sys.path.insert(0, "/home/docaiid")
sys.path.insert(0, "/home/docaiid/src")

lines = []


def log(msg):
    lines.append(str(msg))
    print(msg, flush=True)


class _SR:
    def __init__(self):
        self.status = None
        self.headers = []

    def __call__(self, status, headers):
        self.status = status
        self.headers = headers


def run(environ):
    sr = _SR()
    chunks = application(environ, sr)
    body = b"".join(chunks) if chunks else b""
    return sr.status, dict(sr.headers), body


def fake_environ(method, path, query="", body=b"", ctype=None):
    return {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "CONTENT_TYPE": ctype or "",
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }


def multipart_body(bank, pdf_bytes, boundary):
    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"bank\"\r\n\r\n{bank}\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"statement.pdf\"\r\nContent-Type: application/pdf\r\n\r\n".encode(),
        pdf_bytes,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts)


try:
    from docai.pa_wsgi import application

    pdf = Path("/home/docaiid/bca_native.pdf").read_bytes()

    status, headers, body = run(fake_environ("GET", "/health"))
    payload = json.loads(body)
    assert status == "200 OK" and payload == {"status": "ok", "banks": ["bca"]}
    log(f"[health] {status} {payload}")

    status, headers, body = run(fake_environ("GET", "/"))
    assert status == "200 OK" and headers["Content-Type"].startswith("text/html")
    log(f"[landing] {status} {len(body)} bytes")

    boundary = uuid.uuid4().hex
    raw = multipart_body("bca", pdf, boundary)
    status, headers, body = run(
        fake_environ("POST", "/parse", body=raw, ctype=f"multipart/form-data; boundary={boundary}")
    )
    assert status == "200 OK", status
    payload = json.loads(body)
    assert len(payload["transactions"]) == 6
    assert payload["closing_balance"] == 9929972.0
    assert payload["balance_check"] == "passed"
    log(f"[parse json] {status} {len(payload['transactions'])} txns closing={payload['closing_balance']} balance={payload['balance_check']}")

    boundary = uuid.uuid4().hex
    raw = multipart_body("bca", pdf, boundary)
    status, headers, body = run(
        fake_environ("POST", "/parse", query="format=csv", body=raw, ctype=f"multipart/form-data; boundary={boundary}")
    )
    assert status == "200 OK"
    csv_text = body.decode("utf-8")
    assert csv_text.splitlines()[0] == "tanggal;keterangan;debit;kredit;saldo"
    log(f"[parse csv] {status} rows={len(csv_text.strip().splitlines()) - 1}")

    log("ALL PA WSGI TESTS PASSED")
except Exception:
    log("FAILED:\n" + traceback.format_exc())

Path("/home/docaiid/pa_wsgi_test_out.txt").write_text("\n".join(lines))
