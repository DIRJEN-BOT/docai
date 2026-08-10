"""API tests — exercise the FastAPI wrapper with the TestClient."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from docai.api import app

FIXTURES_DIR = Path(__file__).parent / "fixtures"
NATIVE_PATH = FIXTURES_DIR / "bca_native.pdf"
MISMATCH_PATH = FIXTURES_DIR / "bca_balance_mismatch.pdf"
HAPPY_PATH = FIXTURES_DIR / "bca_happy_path.pdf"

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "bca" in data["banks"]


def test_landing_page_served():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "DocAI" in resp.text


def test_parse_native_happy_path():
    with open(NATIVE_PATH, "rb") as f:
        resp = client.post("/parse", files={"file": ("bca_native.pdf", f, "application/pdf")})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["bank"] == "bca"
    assert data["account_name"] == "BUDI SETIAWAN"
    assert data["opening_balance"] == 1000000.0
    assert data["closing_balance"] == 9929972.0
    assert data["total_debit"] == 1025000.0
    assert data["total_credit"] == 9954972.0
    assert data["balance_check"] == "passed"
    assert "validation_error" not in data
    assert len(data["transactions"]) == 6


def test_parse_balance_mismatch_flags_not_errors():
    """A mismatched statement is a valid parse — API flags it, does not 4xx."""
    with open(MISMATCH_PATH, "rb") as f:
        resp = client.post("/parse", files={"file": ("mismatch.pdf", f, "application/pdf")})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["balance_check"] == "failed"
    assert "Balance mismatch" in data["validation_error"]


def test_parse_csv_output():
    with open(NATIVE_PATH, "rb") as f:
        resp = client.post(
            "/parse?format=csv",
            files={"file": ("bca_native.pdf", f, "application/pdf")},
        )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/csv")
    lines = resp.text.strip().splitlines()
    assert lines[0] == "tanggal;keterangan;debit;kredit;saldo"
    assert len(lines) == 1 + 6  # header + 6 transactions
    # First native row: KR OTOMATIS credit 4965993.00
    assert "4965993.00" in lines[1]
    assert ";" in lines[1]


def test_parse_non_pdf_rejected():
    resp = client.post(
        "/parse",
        files={"file": ("not_a_pdf.txt", b"hello world", "text/plain")},
    )
    assert resp.status_code == 400
    assert "error" in resp.json()


def test_parse_missing_file_field():
    resp = client.post("/parse")
    assert resp.status_code == 422


def test_parse_unknown_bank_rejected():
    with open(NATIVE_PATH, "rb") as f:
        resp = client.post(
            "/parse",
            files={"file": ("bca_native.pdf", f, "application/pdf")},
            data={"bank": "mandiri"},
        )
    assert resp.status_code == 400
    assert "No parser registered" in resp.json()["message"]
