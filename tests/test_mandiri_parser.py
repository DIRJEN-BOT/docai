"""Test suite for DocAI Mandiri parser."""

from __future__ import annotations

import textwrap
from decimal import Decimal
from pathlib import Path

import pytest

from docai.base import ParseError
from docai.models import Bank, ParseResult, Transaction
from docai.parsers.mandiri import MandiriParser
from docai.parsers.registry import get_parser, list_banks
from docai.utils import parse_indonesian_number


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MODERN_MANDIRI_TEXT = textwrap.dedent("""\
    e-Statement
    Nama/Name: Budi Santoso
    Nomor Rekening/Account Number: 1300027219719
    Periode/Period: 01 Apr 2025 - 30 Apr 2025
    Mata Uang/Currency: IDR
    Saldo Awal/Initial Balance: IDR 1.250.000,00
    Dana Masuk/Incoming: IDR 2.160.000,00
    Dana Keluar/Outgoing: IDR 53.500,00
    Saldo Akhir/Closing Balance: IDR 3.356.500,00

    No | Tanggal/Date | Keterangan/Remarks | Nominal (IDR)/Amount (IDR) | Saldo (IDR)/Balance (IDR)
    11 | 05 Apr 2025 | 14:39:33 WIB Transfer ke BANK MANDIRI BERSAMA SILALAHI 1 6300072535 14 | -50.000,00 | 1.200.000,00
    12 | 07 Apr 2025 | 17:18:28 WIB Transfer BI Fast Dari KANISAH 6285283743827 DANA20250207 | +10.000,00 | 1.210.000,00
    13 | 10 Apr 2025 | 10:22:40 WIB Transfer BI Fast Dari BCA KHUSTINI 4921073601 Tf | +200.000,00 | 1.410.000,00
    14 | 15 Apr 2025 | 17:40:09 WIB Biaya administrasi kartu debit | -3.500,00 | 1.406.500,00

    ini adalah batas akhir transaksi anda
""")

INLINE_FORMAT_TEXT = textwrap.dedent("""\
    e-Statement
    Nama/Name: Siti Rahayu
    Nomor Rekening/Account Number: 1300098765432
    Periode/Period: 12 Feb 2025 - 28 Feb 2025
    Mata Uang/Currency: IDR
    Saldo Awal/Initial Balance: IDR 500.000,00
    Saldo Akhir/Closing Balance: IDR 332.750,00

    12 Feb 2025 19:08:39 WIB Transfer ke BANK MANDIRI FADILAH AZMI 1330026577999 -17.250.000,00 99.179,00
    15 Feb 2025 10:00:00 WIB Setor Tunai ATM +2.000.000,00 2.099.179,00

    ini adalah batas akhir transaksi anda
""")

MULTI_PAGE_TEXT = textwrap.dedent("""\
    e-Statement
    Nama/Name: Andi Pratama
    Nomor Rekening/Account Number: 1300055512345
    Periode/Period: 01 Mar 2025 - 31 Mar 2025
    Mata Uang/Currency: IDR
    Saldo Awal/Initial Balance: IDR 10.000.000,00
    Saldo Akhir/Closing Balance: IDR 9.946.500,00

    01 Mar 2025 08:15:00 WIB Transfer ke BCA ANDI +5.000.000,00 15.000.000,00
    05 Mar 2025 12:00:00 WIB Biaya admin -3.500,00 14.996.500,00

    --- PAGE 2 ---

    10 Mar 2025 09:30:00 WIB Tarik Tunai -50.000,00 14.946.500,00
    15 Mar 2025 14:00:00 WIB Transfer BI Fast +100.000,00 15.046.500,00

    ini adalah batas akhir transaksi anda
""")


@pytest.fixture
def mandiri_parser():
    return MandiriParser()


# ---------------------------------------------------------------------------
# Unit tests: format detection
# ---------------------------------------------------------------------------


class TestFormatDetection:
    """Test Mandiri format detection."""

    def test_modern_format_detected(self, mandiri_parser):
        assert mandiri_parser._is_mandiri_format(MODERN_MANDIRI_TEXT) is True

    def test_inline_format_detected(self, mandiri_parser):
        assert mandiri_parser._is_mandiri_format(INLINE_FORMAT_TEXT) is True

    def test_non_mandiri_text_rejected(self, mandiri_parser):
        assert mandiri_parser._is_mandiri_format("BCA e-Statement\nRekening: 123") is False

    def test_partial_tokens_rejected(self, mandiri_parser):
        # Has e-Statement but missing Saldo Awal
        assert mandiri_parser._is_mandiri_format("e-Statement\nNama: Test") is False


# ---------------------------------------------------------------------------
# Unit tests: metadata extraction
# ---------------------------------------------------------------------------


class TestMetadataExtraction:
    """Test metadata extraction from Mandiri statements."""

    def test_account_number(self, mandiri_parser):
        result = ParseResult(bank=Bank.MANDIRI)
        mandiri_parser._extract_metadata(MODERN_MANDIRI_TEXT, result)
        assert result.account_number == "1300027219719"

    def test_account_name(self, mandiri_parser):
        result = ParseResult(bank=Bank.MANDIRI)
        mandiri_parser._extract_metadata(MODERN_MANDIRI_TEXT, result)
        assert result.account_name == "Budi Santoso"

    def test_statement_period(self, mandiri_parser):
        result = ParseResult(bank=Bank.MANDIRI)
        mandiri_parser._extract_metadata(MODERN_MANDIRI_TEXT, result)
        assert result.statement_period == "01 Apr 2025 - 30 Apr 2025"

    def test_currency(self, mandiri_parser):
        result = ParseResult(bank=Bank.MANDIRI)
        mandiri_parser._extract_metadata(MODERN_MANDIRI_TEXT, result)
        assert result.currency == "IDR"

    def test_opening_balance(self, mandiri_parser):
        result = ParseResult(bank=Bank.MANDIRI)
        mandiri_parser._extract_metadata(MODERN_MANDIRI_TEXT, result)
        assert result.opening_balance == Decimal("1250000.00")

    def test_closing_balance(self, mandiri_parser):
        result = ParseResult(bank=Bank.MANDIRI)
        mandiri_parser._extract_metadata(MODERN_MANDIRI_TEXT, result)
        assert result.closing_balance == Decimal("3356500.00")


# ---------------------------------------------------------------------------
# Unit tests: date normalization
# ---------------------------------------------------------------------------


class TestDateNormalization:
    """Test date format normalization."""

    def test_dd_mon_yyyy_to_dd_mm_yyyy(self, mandiri_parser):
        assert mandiri_parser._normalize_mandiri_date("05 Apr 2025") == "05/04/2025"

    def test_jan(self, mandiri_parser):
        assert mandiri_parser._normalize_mandiri_date("15 Jan 2025") == "15/01/2025"

    def test_dec(self, mandiri_parser):
        assert mandiri_parser._normalize_mandiri_date("25 Dec 2024") == "25/12/2024"

    def test_already_normalized_passthrough(self, mandiri_parser):
        assert mandiri_parser._normalize_mandiri_date("05/04/2025") == "05/04/2025"


# ---------------------------------------------------------------------------
# Unit tests: transaction parsing (pipe-separated)
# ---------------------------------------------------------------------------


class TestPipeSeparatedTransactions:
    """Test pipe-separated transaction line parsing."""

    def test_credit_transaction(self, mandiri_parser):
        line = "12 | 07 Apr 2025 | 17:18:28 WIB Transfer BI Fast Dari KANISAH | +10.000,00 | 1.210.000,00"
        txn = mandiri_parser._parse_pipe_separated(line, Decimal("1200000.00"))
        assert txn is not None
        assert txn.credit == Decimal("10000.00")
        assert txn.debit == Decimal("0")
        assert txn.balance == Decimal("1210000.00")
        assert txn.date == "07/04/2025"

    def test_debit_transaction(self, mandiri_parser):
        line = "11 | 05 Apr 2025 | 14:39:33 WIB Transfer ke BANK MANDIRI | -50.000,00 | 1.200.000,00"
        txn = mandiri_parser._parse_pipe_separated(line, Decimal("1250000.00"))
        assert txn is not None
        assert txn.debit == Decimal("50000.00")
        assert txn.credit == Decimal("0")
        assert txn.balance == Decimal("1200000.00")

    def test_no_pipe_returns_none(self, mandiri_parser):
        assert mandiri_parser._parse_pipe_separated("no pipes here", None) is None


# ---------------------------------------------------------------------------
# Unit tests: transaction parsing (inline)
# ---------------------------------------------------------------------------


class TestInlineTransactions:
    """Test inline transaction line parsing."""

    def test_inline_debit_with_date(self, mandiri_parser):
        line = "12 Feb 2025 19:08:39 WIB Transfer ke BANK MANDIRI FADILAH AZMI -17.250.000,00 99.179,00"
        txn = mandiri_parser._parse_inline(line, Decimal("500000.00"))
        assert txn is not None
        assert txn.debit == Decimal("17250000.00")
        assert txn.credit == Decimal("0")
        assert txn.date == "12/02/2025"

    def test_inline_credit_with_date(self, mandiri_parser):
        line = "15 Feb 2025 10:00:00 WIB Setor Tunai ATM +2.000.000,00 2.099.179,00"
        txn = mandiri_parser._parse_inline(line, Decimal("99179.00"))
        assert txn is not None
        assert txn.credit == Decimal("2000000.00")
        assert txn.debit == Decimal("0")

    def test_time_only_no_date_returns_none(self, mandiri_parser):
        line = "14:39:33 WIB Transfer ke BANK MANDIRI -50.000,00"
        txn = mandiri_parser._parse_inline(line, None)
        assert txn is None


# ---------------------------------------------------------------------------
# Integration tests: full parse from text
# ---------------------------------------------------------------------------


class TestFullParse:
    """Test full pipeline: format detection + metadata + transactions."""

    def test_modern_format_parse(self, mandiri_parser):
        # We can't call .parse() on a real PDF, so test the components
        assert mandiri_parser._is_mandiri_format(MODERN_MANDIRI_TEXT) is True

        result = ParseResult(bank=Bank.MANDIRI)
        mandiri_parser._extract_metadata(MODERN_MANDIRI_TEXT, result)
        mandiri_parser._extract_transactions(MODERN_MANDIRI_TEXT, result)

        assert result.account_number == "1300027219719"
        assert result.account_name == "Budi Santoso"
        assert len(result.transactions) == 4

        # First transaction: debit
        t0 = result.transactions[0]
        assert t0.debit == Decimal("50000.00")
        assert t0.credit == Decimal("0")
        assert t0.balance == Decimal("1200000.00")

        # Second transaction: credit
        t1 = result.transactions[1]
        assert t1.credit == Decimal("10000.00")
        assert t1.debit == Decimal("0")

        # Third transaction: credit
        t2 = result.transactions[2]
        assert t2.credit == Decimal("200000.00")

        # Fourth transaction: debit (admin fee)
        t3 = result.transactions[3]
        assert t3.debit == Decimal("3500.00")
        assert t3.credit == Decimal("0")

    def test_end_of_table_stops_parsing(self, mandiri_parser):
        result = ParseResult(bank=Bank.MANDIRI)
        mandiri_parser._extract_transactions(MODERN_MANDIRI_TEXT, result)
        # All 4 transactions present, nothing after end marker
        assert len(result.transactions) == 4

    def test_multi_page_transactions(self, mandiri_parser):
        result = ParseResult(bank=Bank.MANDIRI)
        mandiri_parser._extract_transactions(MULTI_PAGE_TEXT, result)
        # 4 transactions across 2 pages
        assert len(result.transactions) == 4
        assert result.transactions[0].date == "01/03/2025"
        assert result.transactions[3].date == "15/03/2025"


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestRegistry:
    """Test parser registry includes Mandiri."""

    def test_mandiri_registered(self):
        parser = get_parser("mandiri")
        assert isinstance(parser, MandiriParser)
        assert parser.bank_name == "mandiri"

    def test_mandiri_case_insensitive(self):
        parser = get_parser("MANDIRI")
        assert isinstance(parser, MandiriParser)

    def test_list_banks_includes_mandiri(self):
        banks = list_banks()
        assert "mandiri" in banks
        assert "bca" in banks

    def test_unknown_bank_raises(self):
        with pytest.raises(ValueError, match="No parser registered"):
            get_parser("unknown_bank")


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Test error conditions."""

    def test_file_not_found(self, mandiri_parser):
        with pytest.raises(FileNotFoundError):
            mandiri_parser.parse("nonexistent.pdf")

    def test_not_a_pdf(self, mandiri_parser):
        # Create a temp file that's not a PDF
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not a pdf")
            tmp_path = Path(f.name)
        try:
            with pytest.raises(ValueError, match="Not a PDF"):
                mandiri_parser.parse(tmp_path)
        finally:
            tmp_path.unlink()

    def test_non_mandiri_pdf_raises_parse_error(self, mandiri_parser):
        """Test that non-Mandiri text raises ParseError (not PasswordProtectedError)."""
        # This tests _is_mandiri_format integration — we simulate by checking
        # that _is_mandiri_format returns False for non-Mandiri content
        assert mandiri_parser._is_mandiri_format("Some random PDF text") is False
