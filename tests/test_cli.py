"""CLI tests — run docai.cli as a subprocess against fixture PDFs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
HAPPY_PATH = FIXTURES_DIR / "bca_happy_path.pdf"
MISMATCH = FIXTURES_DIR / "bca_balance_mismatch.pdf"
NATIVE_PATH = FIXTURES_DIR / "bca_native.pdf"


def run_cli(*args: str):
    return subprocess.run(
        [sys.executable, "-m", "docai.cli", *args],
        capture_output=True,
        text=True,
    )


def test_parse_happy_path_to_json():
    proc = run_cli("parse", "--bank", "bca", str(HAPPY_PATH))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["bank"] == "bca"
    assert data["account_name"] == "BUDI SETIAWAN"
    assert data["closing_balance"] == 5225000.00
    assert data["total_debit"] == 1525000.00
    assert data["total_credit"] == 5750000.00
    assert data["balance_check"] == "passed"
    assert len(data["transactions"]) == 8


def test_parse_balance_mismatch_fails():
    proc = run_cli("parse", "--bank", "bca", str(MISMATCH))
    data = json.loads(proc.stdout)
    assert data["balance_check"] == "failed"
    assert "Balance mismatch" in data["validation_error"]
    assert proc.returncode == 1


def test_parse_no_validate_skips_check():
    proc = run_cli("parse", "--bank", "bca", "--no-validate", str(MISMATCH))
    data = json.loads(proc.stdout)
    assert data["balance_check"] == "passed"  # not run
    assert "validation_error" not in data
    assert proc.returncode == 0


def test_parse_real_layout_happy_path():
    """Real BCA e-statement layout (multi-line rows, SALDO AWAL/MUTASI/SALDO
    AKHIR summary) is parsed and passes the balance check end-to-end."""
    proc = run_cli("parse", "--bank", "bca", str(NATIVE_PATH))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["account_number"] == "1234567890"
    assert data["account_name"] == "BUDI SETIAWAN"
    assert data["opening_balance"] == 1000000.00
    assert data["closing_balance"] == 9929972.00
    assert data["balance_check"] == "passed"
    assert len(data["transactions"]) == 6


def test_banks_command():
    proc = run_cli("banks")
    assert proc.returncode == 0
    assert "bca" in proc.stdout.split()


def test_missing_file_errors():
    proc = run_cli("parse", "--bank", "bca", "/nonexistent/file.pdf")
    assert proc.returncode == 1
    assert "Error" in proc.stderr
