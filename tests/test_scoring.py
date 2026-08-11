"""Tests for the income verification scoring engine."""

from __future__ import annotations

from decimal import Decimal

import pytest

from docai.models import Bank, ParseResult, Transaction
from docai.scoring import IncomeReport, analyze_income


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tx(
    date: str,
    desc: str,
    debit: str = "0",
    credit: str = "0",
    balance: str = "0",
) -> Transaction:
    """Shorthand for building test transactions."""
    return Transaction(
        date=date,
        description=desc,
        debit=Decimal(debit),
        credit=Decimal(credit),
        balance=Decimal(balance),
    )


def _result(
    transactions: list[Transaction],
    opening: str = "0",
    closing: str = "0",
) -> ParseResult:
    """Build a ParseResult with the given transactions."""
    return ParseResult(
        bank=Bank.BCA,
        opening_balance=Decimal(opening),
        closing_balance=Decimal(closing),
        transactions=transactions,
    )


# ---------------------------------------------------------------------------
# Salary detection: keyword-based
# ---------------------------------------------------------------------------

class TestSalaryDetectionKeyword:
    def test_salary_keyword_detected(self):
        """Transactions with 'Gaji' in the description are recognised as salary."""
        txns = [
            _tx("01/01/2025", "Transfer Gaji PT Maju Jaya", credit="8500000", balance="8500000"),
            _tx("01/02/2025", "Transfer Gaji PT Maju Jaya", credit="8500000", balance="17000000"),
            _tx("01/03/2025", "Transfer Gaji PT Maju Jaya", credit="8500000", balance="25500000"),
            _tx("10/03/2025", "BELANJA WARUNG", debit="150000", balance="25350000"),
        ]
        result = _result(txns, opening="0", closing="25350000")
        report = analyze_income(result)

        assert report.income_source == "salary"
        assert report.salary_months_detected == 3
        assert report.detected_monthly_income == Decimal("8500000.00")

    def test_salary_keyword_upah(self):
        """'Upah' is also a salary keyword."""
        txns = [
            _tx("05/01/2025", "Upah Bulanan", credit="3000000", balance="3000000"),
            _tx("05/02/2025", "Upah Bulanan", credit="3000000", balance="6000000"),
            _tx("05/03/2025", "Upah Bulanan", credit="3000000", balance="9000000"),
        ]
        result = _result(txns, opening="0", closing="9000000")
        report = analyze_income(result)

        assert report.income_source == "salary"
        assert report.salary_months_detected >= 2


# ---------------------------------------------------------------------------
# Salary detection: recurring amount
# ---------------------------------------------------------------------------

class TestSalaryDetectionRecurring:
    def test_recurring_amount_without_keyword(self):
        """A similar credit amount across 3+ months is detected as salary."""
        # All different descriptions but same amount
        txns = [
            _tx("03/01/2025", "Transfer BI Fast Dari Budi", credit="7500000", balance="7500000"),
            _tx("03/02/2025", "Transfer BCA Dari Andi", credit="7500000", balance="15000000"),
            _tx("03/03/2025", "Transfer Mandiri Dari Sari", credit="7500000", balance="22500000"),
            _tx("15/03/2025", "Pembayaran Listrik", debit="500000", balance="22000000"),
        ]
        result = _result(txns, opening="0", closing="22000000")
        report = analyze_income(result)

        assert report.income_source in ("salary", "mixed")
        assert report.salary_months_detected >= 3

    def test_recurring_amount_within_tolerance(self):
        """Amounts within ±10% are considered the same recurring income."""
        txns = [
            _tx("01/01/2025", "Transfer Dari Kantor", credit="5000000", balance="5000000"),
            _tx("01/02/2025", "Transfer Dari Kantor", credit="5200000", balance="10200000"),
            _tx("01/03/2025", "Transfer Dari Kantor", credit="4900000", balance="15100000"),
        ]
        result = _result(txns, opening="0", closing="15100000")
        report = analyze_income(result)

        # Should detect recurring income despite variation
        assert report.income_source in ("salary", "mixed")


# ---------------------------------------------------------------------------
# Income consistency scoring
# ---------------------------------------------------------------------------

class TestConsistencyScoring:
    def test_stable_income_high_score(self):
        """Identical monthly income → high consistency score (≥90)."""
        txns = []
        bal = Decimal("0")
        for month in range(1, 7):
            credit = Decimal("5000000")
            bal += credit
            txns.append(_tx(
                f"01/{month:02d}/2025",
                f"Salary Month {month}",
                credit=str(credit),
                balance=str(bal),
            ))
        result = _result(txns, opening="0", closing=str(bal))
        report = analyze_income(result)

        assert report.consistency_score >= 90
        assert report.income_cv < 0.05

    def test_variable_income_low_score(self):
        """Highly variable income → low consistency score."""
        amounts = ["1000000", "5000000", "2000000", "8000000", "500000", "9000000"]
        txns = []
        bal = Decimal("0")
        for i, amt in enumerate(amounts, 1):
            credit = Decimal(amt)
            bal += credit
            txns.append(_tx(
                f"01/{i:02d}/2025",
                f"Income {i}",
                credit=str(credit),
                balance=str(bal),
            ))
        result = _result(txns, opening="0", closing=str(bal))
        report = analyze_income(result)

        assert report.consistency_score < 50
        assert report.income_cv > 0.3


# ---------------------------------------------------------------------------
# Gap detection
# ---------------------------------------------------------------------------

class TestGapDetection:
    def test_gap_months_detected(self):
        """Months with zero credit income should be flagged as gaps."""
        # Jan, Mar, May have income; Feb and Apr do not.
        txns = [
            _tx("01/01/2025", "Income", credit="5000000", balance="5000000"),
            _tx("01/03/2025", "Income", credit="5000000", balance="10000000"),
            _tx("01/05/2025", "Income", credit="5000000", balance="15000000"),
        ]
        result = _result(txns, opening="0", closing="15000000")
        report = analyze_income(result)

        assert report.has_gaps is True
        assert len(report.gap_months) >= 1


# ---------------------------------------------------------------------------
# Fraud signals
# ---------------------------------------------------------------------------

class TestFraudSignals:
    def test_round_number_flag(self):
        """>30% round-number transactions trigger a flag."""
        # 4 round + 5 non-round → 4/9 ≈ 44% > 30%
        txns = [
            _tx("01/01/2025", "Round1", credit="1000000", balance="1000000"),
            _tx("02/01/2025", "Round2", credit="2000000", balance="3000000"),
            _tx("03/01/2025", "Round3", credit="3000000", balance="6000000"),
            _tx("04/01/2025", "Round4", credit="4000000", balance="10000000"),
            _tx("05/01/2025", "Odd1", credit="1234567", balance="11234567"),
            _tx("06/01/2025", "Odd2", credit="9876543", balance="21111110"),
            _tx("07/01/2025", "Odd3", credit="1111111", balance="22222221"),
            _tx("08/01/2025", "Odd4", credit="2345678", balance="24567899"),
            _tx("09/01/2025", "Odd5", credit="3456789", balance="28024688"),
        ]
        result = _result(txns, opening="0", closing="28024688")
        report = analyze_income(result)

        round_flags = [f for f in report.fraud_flags if "round" in f.lower()]
        assert len(round_flags) == 1

    def test_duplicate_transaction_flag(self):
        """Exact duplicates trigger a flag."""
        txns = [
            _tx("01/01/2025", "Transfer ke Budi", debit="500000", balance="9500000"),
            _tx("01/01/2025", "Transfer ke Budi", debit="500000", balance="9000000"),
            _tx("02/01/2025", "Belanja", debit="200000", balance="8800000"),
        ]
        result = _result(txns, opening="10000000", closing="8800000")
        report = analyze_income(result)

        dup_flags = [f for f in report.fraud_flags if "duplicate" in f.lower()]
        assert len(dup_flags) >= 1

    def test_balance_mismatch_flag(self):
        """Balance mismatch is flagged."""
        txns = [
            _tx("01/01/2025", "Credit", credit="1000000", balance="1000000"),
        ]
        result = _result(txns, opening="0", closing="999999")  # wrong closing
        report = analyze_income(result)

        assert report.balance_valid is False
        assert any("balance" in f.lower() for f in report.fraud_flags)


# ---------------------------------------------------------------------------
# Composite score
# ---------------------------------------------------------------------------

class TestCompositeScore:
    def test_clean_statement_high_score(self):
        """Statement with salary, consistent income, no fraud → high score."""
        txns = []
        bal = Decimal("0")
        for month in range(1, 7):
            credit = Decimal("8000000")
            bal += credit
            txns.append(_tx(
                f"01/{month:02d}/2025",
                "Gaji PT Sejahtera",
                credit=str(credit),
                balance=str(bal),
            ))
        result = _result(txns, opening="0", closing=str(bal))
        report = analyze_income(result)

        assert report.verification_score >= 80
        assert report.confidence == "high"
        assert report.balance_valid is True

    def test_all_debits_no_income(self):
        """Statement with only debits → low score, undetected income."""
        txns = [
            _tx("01/01/2025", "Pembayaran", debit="500000", balance="9500000"),
            _tx("02/01/2025", "Pembayaran", debit="300000", balance="9200000"),
            _tx("03/01/2025", "Pembayaran", debit="200000", balance="9000000"),
        ]
        result = _result(txns, opening="10000000", closing="9000000")
        report = analyze_income(result)

        assert report.income_source == "undetected"
        assert report.detected_monthly_income == Decimal("0")
        assert report.verification_score < 60

    def test_score_range_clamped(self):
        """Score is always between 0 and 100."""
        # Worst case: balance mismatch, no income, fraud flags
        txns = [
            _tx("01/01/2025", "Transfer ke X", debit="1000000", balance="9000000"),
            _tx("01/01/2025", "Transfer ke X", debit="1000000", balance="8000000"),
        ]
        result = _result(txns, opening="10000000", closing="999999")
        report = analyze_income(result)

        assert 0 <= report.verification_score <= 100
        assert report.confidence in ("high", "medium", "low")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_transactions(self):
        """Empty transaction list → graceful handling."""
        result = ParseResult(bank=Bank.BCA)
        report = analyze_income(result)

        assert report.total_transactions == 0
        assert report.income_source == "undetected"
        assert report.detected_monthly_income == Decimal("0")
        assert report.statement_period == "N/A"
        assert report.total_months_covered == 0

    def test_single_month(self):
        """Single month of data → no gaps, reasonable consistency."""
        txns = [
            _tx("15/03/2025", "Gaji", credit="6000000", balance="6000000"),
            _tx("20/03/2025", "Belanja", debit="1000000", balance="5000000"),
        ]
        result = _result(txns, opening="0", closing="5000000")
        report = analyze_income(result)

        assert report.total_months_covered == 1
        assert report.salary_months_detected == 1
        assert report.has_gaps is False

    def test_metadata_populated(self):
        """Report metadata fields are correctly populated."""
        txns = [
            _tx("01/06/2025", "Income", credit="5000000", balance="5000000"),
            _tx("01/07/2025", "Income", credit="5000000", balance="10000000"),
            _tx("15/07/2025", "Expense", debit="2000000", balance="8000000"),
        ]
        result = _result(txns, opening="0", closing="8000000")
        report = analyze_income(result)

        assert report.statement_period == "Jun 2025 - Jul 2025"
        assert report.total_months_covered == 2
        assert report.total_transactions == 3
        assert report.total_credit == Decimal("10000000")
        assert report.total_debit == Decimal("2000000")
