"""Test suite for DocAI BCA parser and validation."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from docai.base import PasswordProtectedError
from docai.models import Bank, ParseResult, Transaction
from docai.parsers.bca import BCAParser
from docai.parsers.registry import get_parser, list_banks
from docai.utils import parse_indonesian_number
from docai.validation import ValidationError, validate_balance

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURE_MANIFEST = FIXTURES_DIR / "manifest.json"


@pytest.fixture(scope="session", autouse=True)
def generate_fixtures():
    """Generate synthetic fixture PDFs before tests run."""
    from tests.generate_fixtures import generate_all_fixtures

    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    if not FIXTURE_MANIFEST.exists():
        fixtures = generate_all_fixtures()
        # Save manifest for test assertions
        with open(FIXTURE_MANIFEST, "w") as f:
            json.dump(fixtures, f, indent=2)
    else:
        with open(FIXTURE_MANIFEST) as f:
            fixtures = json.load(f)
    return fixtures


@pytest.fixture
def manifest():
    """Load fixture manifest with expected values."""
    with open(FIXTURE_MANIFEST) as f:
        return json.load(f)


@pytest.fixture
def bca_parser():
    return BCAParser()


# ---------------------------------------------------------------------------
# Unit tests: utils
# ---------------------------------------------------------------------------


class TestParseIndonesianNumber:
    """Test the Indonesian number parser."""

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("1.234.567,89", "1234567.89"),
            ("500.000", "500000.00"),
            ("1.000.000,00", "1000000.00"),
            ("0", "0.00"),
            ("", "0.00"),
            ("25.000", "25000.00"),
            ("8.500.000,00", "8500000.00"),
            ("75.000.000,00", "75000000.00"),
        ],
    )
    def test_parse_id_number(self, input_str: str, expected: str):
        result = parse_indonesian_number(input_str)
        assert result == Decimal(expected), f"parse_indonesian_number({input_str!r}) = {result}, expected {expected}"


# ---------------------------------------------------------------------------
# Unit tests: models
# ---------------------------------------------------------------------------


class TestTransaction:
    """Test Transaction dataclass."""

    def test_creation(self):
        t = Transaction(
            date="02/01/2026",
            description="SETORAN TUNAI",
            debit=Decimal("0"),
            credit=Decimal("1000000"),
            balance=Decimal("2000000"),
        )
        assert t.date == "02/01/2026"
        assert t.credit == Decimal("1000000")
        assert t.balance == Decimal("2000000")

    def test_string_to_decimal_coercion(self):
        t = Transaction(
            date="02/01/2026",
            description="TEST",
            debit="50000",
            credit="0",
            balance="950000",
        )
        assert t.debit == Decimal("50000")


class TestParseResult:
    """Test ParseResult computed properties."""

    def test_computed_closing(self):
        r = ParseResult(bank=Bank.BCA)
        r.opening_balance = Decimal("1000000")
        r.closing_balance = Decimal("1700000")
        r.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("1000000"), Decimal("2000000")),
            Transaction("03/01/2026", "OUT", Decimal("300000"), Decimal("0"), Decimal("1700000")),
        ]
        assert r.computed_closing() == Decimal("1700000.00")


# ---------------------------------------------------------------------------
# Integration tests: BCA parser
# ---------------------------------------------------------------------------


class TestBCAParser:
    """Integration tests against generated fixture PDFs."""

    def test_happy_path_parse(self, bca_parser: BCAParser, manifest: dict):
        """Happy path: parse matches generated truth."""
        meta = manifest["happy_path"]
        result = bca_parser.parse(meta["path"])

        assert result.bank == Bank.BCA
        assert result.account_number == meta["account_number"]
        assert result.account_name == meta["account_name"]
        assert result.opening_balance == Decimal(meta["opening_balance"])
        assert result.closing_balance == Decimal(meta["closing_balance"])
        assert len(result.transactions) == meta["num_transactions"]

    def test_happy_path_balances(self, bca_parser: BCAParser, manifest: dict):
        """Each transaction balance should be consistent."""
        meta = manifest["happy_path"]
        result = bca_parser.parse(meta["path"])

        running = result.opening_balance
        for txn in result.transactions:
            expected_balance = running - txn.debit + txn.credit
            assert txn.balance == expected_balance, (
                f"Transaction {txn.date} balance mismatch: "
                f"expected {expected_balance}, got {txn.balance}"
            )
            running = txn.balance

    def test_happy_path_total_debit_credit(self, bca_parser: BCAParser, manifest: dict):
        """Sum of debits and credits match expected totals."""
        meta = manifest["happy_path"]
        result = bca_parser.parse(meta["path"])
        assert result.total_debit == Decimal(meta["total_debit"])
        assert result.total_credit == Decimal(meta["total_credit"])

    def test_balance_check_passes(self, bca_parser: BCAParser, manifest: dict):
        """Balance-check validation passes for happy path."""
        meta = manifest["happy_path"]
        result = bca_parser.parse(meta["path"])
        # Should not raise
        validate_balance(result)

    def test_balance_mismatch_detected(self, bca_parser: BCAParser, manifest: dict):
        """Balance-check catches a wrong closing balance declared in the PDF."""
        meta = manifest["balance_mismatch"]
        result = bca_parser.parse(meta["path"])
        # The PDF itself declares a wrong closing balance (2.000.000 instead of
        # the computed 1.500.000) — validation must reject it end-to-end.
        with pytest.raises(ValidationError, match="Balance mismatch"):
            validate_balance(result)

    def test_credit_only_statement(self, bca_parser: BCAParser, manifest: dict):
        """Credit-only statement (salary deposits) parses correctly."""
        meta = manifest["credit_only"]
        result = bca_parser.parse(meta["path"])

        assert result.account_number == meta["account_number"]
        assert len(result.transactions) == meta["num_transactions"]
        assert result.total_debit == Decimal("0")
        assert result.total_credit == (
            Decimal(meta["closing_balance"]) - Decimal(meta["opening_balance"])
        )

    def test_large_values(self, bca_parser: BCAParser, manifest: dict):
        """Large Indonesian business amounts parse correctly."""
        meta = manifest["large_values"]
        result = bca_parser.parse(meta["path"])

        assert result.account_number == meta["account_number"]
        assert len(result.transactions) == meta["num_transactions"]
        assert result.total_debit == Decimal(meta["total_debit"])
        assert result.total_credit == Decimal(meta["total_credit"])

    def test_parse_result_has_correct_bank(self, bca_parser: BCAParser, manifest: dict):
        """Parsed result always identifies as BCA."""
        result = bca_parser.parse(manifest["happy_path"]["path"])
        assert result.bank == Bank.BCA
        assert result.currency == "IDR"


# ---------------------------------------------------------------------------
# Native (real BCA e-statement) format tests
# ---------------------------------------------------------------------------


class TestNativeFormat:
    """Tests for the real BCA e-statement layout (multi-line rows, Western
    amounts like 9,846,915.69, trailing SALDO AWAL/MUTASI/SALDO AKHIR block)."""

    def test_native_metadata(self, bca_parser: BCAParser, manifest: dict):
        meta = manifest["native_format"]
        result = bca_parser.parse(meta["path"])

        assert result.account_number == meta["account_number"]
        assert result.account_name == meta["account_name"]
        assert result.statement_period == meta["period"]
        assert result.opening_balance == Decimal(meta["opening_balance"])
        assert result.closing_balance == Decimal(meta["closing_balance"])
        assert result.currency == "IDR"

    def test_native_transactions(self, bca_parser: BCAParser, manifest: dict):
        meta = manifest["native_format"]
        result = bca_parser.parse(meta["path"])

        assert len(result.transactions) == meta["num_transactions"]
        assert result.total_debit == Decimal(meta["total_debit"])
        assert result.total_credit == Decimal(meta["total_credit"])

        # Debit/credit direction resolved correctly for each row type:
        # labelled closing line, description label, balance comparison.
        qr_credit = [t for t in result.transactions if t.date == "02/01" and t.credit == Decimal("4965993")]
        assert len(qr_credit) == 1
        assert "KR OTOMATIS" in qr_credit[0].description

        atm_debit = [t for t in result.transactions if t.date == "03/01" and t.debit == Decimal("250000.00")]
        assert len(atm_debit) == 1
        assert atm_debit[0].debit == Decimal("250000.00")

        # No-label row resolved via description hint / balance comparison
        bfast = [t for t in result.transactions if t.date == "05/01" and t.credit == Decimal("3000000.00")]
        assert len(bfast) == 1
        assert "BI-FAST" in bfast[0].description

        # Single-line row "15/01 BIAYA ADM 25,000.00 DB 9,929,972.00"
        adm = [t for t in result.transactions if t.date == "15/01" and t.debit == Decimal("25000.00")]
        assert len(adm) == 1
        assert adm[0].description == "BIAYA ADM"

    def test_native_running_balances(self, bca_parser: BCAParser, manifest: dict):
        """Rows without a printed running balance must still reconcile."""
        meta = manifest["native_format"]
        result = bca_parser.parse(meta["path"])

        running = result.opening_balance
        for txn in result.transactions:
            expected_balance = running - txn.debit + txn.credit
            assert txn.balance == expected_balance, (
                f"Transaction {txn.date} balance mismatch: "
                f"expected {expected_balance}, got {txn.balance}"
            )
            running = txn.balance

    def test_native_balance_check_passes(self, bca_parser: BCAParser, manifest: dict):
        """End-to-end: balance-check passes for the native layout fixture."""
        meta = manifest["native_format"]
        result = bca_parser.parse(meta["path"])
        validate_balance(result)  # must not raise


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Test error conditions."""

    def test_file_not_found(self, bca_parser: BCAParser):
        with pytest.raises(FileNotFoundError):
            bca_parser.parse("/nonexistent/file.pdf")

    def test_not_a_pdf(self, bca_parser: BCAParser, tmp_path):
        txt_file = tmp_path / "not_a_pdf.txt"
        txt_file.write_text("hello")
        with pytest.raises(ValueError, match="Not a PDF"):
            bca_parser.parse(txt_file)

    def test_password_protected_pdf(self, bca_parser: BCAParser, tmp_path):
        """DOB-locked (encrypted) BCA PDF raises PasswordProtectedError."""
        from pypdf import PdfWriter

        locked_path = tmp_path / "locked.pdf"
        writer = PdfWriter()
        writer.append(str(FIXTURES_DIR / "bca_happy_path.pdf"))
        writer.encrypt("01011990")
        with open(locked_path, "wb") as f:
            writer.write(f)

        with pytest.raises(PasswordProtectedError, match="password-protected"):
            bca_parser.parse(locked_path)


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestRegistry:
    """Test parser registry."""

    def test_list_banks(self):
        banks = list_banks()
        assert "bca" in banks

    def test_get_bca_parser(self):
        parser = get_parser("bca")
        assert isinstance(parser, BCAParser)

    def test_unknown_bank_raises(self):
        with pytest.raises(ValueError, match="No parser registered"):
            get_parser("unknown_bank")
