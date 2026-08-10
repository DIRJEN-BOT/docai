"""Dedicated validation tests."""

from __future__ import annotations

from decimal import Decimal

import pytest

from docai.models import Bank, ParseResult, Transaction
from docai.validation import (
    ValidationError,
    validate_balance,
    validate_debit_credit_non_negative,
    validate_running_balances,
    validate_statement,
)


class TestValidateBalance:
    def test_passes_when_balances_match(self):
        result = ParseResult(bank=Bank.BCA)
        result.opening_balance = Decimal("1000000")
        result.closing_balance = Decimal("1700000")
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("1000000"), Decimal("2000000")),
            Transaction("03/01/2026", "OUT", Decimal("300000"), Decimal("0"), Decimal("1700000")),
        ]
        validate_balance(result)  # should not raise

    def test_fails_when_closing_mismatch(self):
        result = ParseResult(bank=Bank.BCA)
        result.opening_balance = Decimal("1000000")
        result.closing_balance = Decimal("999999")  # wrong
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("1000000"), Decimal("2000000")),
        ]
        with pytest.raises(ValidationError, match="Balance mismatch"):
            validate_balance(result)

    def test_fails_when_no_transactions(self):
        result = ParseResult(bank=Bank.BCA)
        result.opening_balance = Decimal("1000000")
        result.closing_balance = Decimal("1000000")
        result.transactions = []
        with pytest.raises(ValidationError, match="No transactions"):
            validate_balance(result)


class TestValidateDebitCreditNonNegative:
    def test_passes_for_valid_data(self):
        result = ParseResult(bank=Bank.BCA)
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("500000"), Decimal("1500000")),
        ]
        validate_debit_credit_non_negative(result)  # should not raise

    def test_fails_for_negative_debit(self):
        result = ParseResult(bank=Bank.BCA)
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("-100"), Decimal("0"), Decimal("1500000")),
        ]
        with pytest.raises(ValidationError, match="negative debit"):
            validate_debit_credit_non_negative(result)

    def test_fails_for_negative_credit(self):
        result = ParseResult(bank=Bank.BCA)
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("-100"), Decimal("1500000")),
        ]
        with pytest.raises(ValidationError, match="negative credit"):
            validate_debit_credit_non_negative(result)


class TestValidateRunningBalances:
    """Row-level running-balance consistency check."""

    def test_passes_when_rows_reconcile(self):
        result = ParseResult(bank=Bank.BCA)
        result.opening_balance = Decimal("1000000")
        result.closing_balance = Decimal("1700000")
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("1000000"), Decimal("2000000")),
            Transaction("03/01/2026", "OUT", Decimal("300000"), Decimal("0"), Decimal("1700000")),
        ]
        validate_running_balances(result)  # should not raise

    def test_fails_on_mismatched_row(self):
        result = ParseResult(bank=Bank.BCA)
        result.opening_balance = Decimal("1000000")
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("1000000"), Decimal("2000000")),
            Transaction("03/01/2026", "OUT", Decimal("300000"), Decimal("0"), Decimal("999999")),
        ]
        with pytest.raises(ValidationError, match="running-balance mismatch"):
            validate_running_balances(result)

    def test_fails_on_first_row_mismatch(self):
        """Opening balance is the starting point for row 0."""
        result = ParseResult(bank=Bank.BCA)
        result.opening_balance = Decimal("1000000")
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("1000000"), Decimal("1500000")),
        ]
        with pytest.raises(ValidationError, match="running-balance mismatch"):
            validate_running_balances(result)


class TestValidateStatement:
    """Full validation suite: aggregate balance → amounts → running balances."""

    def test_passes_for_consistent_statement(self):
        result = ParseResult(bank=Bank.BCA)
        result.opening_balance = Decimal("1000000")
        result.closing_balance = Decimal("1700000")
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("1000000"), Decimal("2000000")),
            Transaction("03/01/2026", "OUT", Decimal("300000"), Decimal("0"), Decimal("1700000")),
        ]
        validate_statement(result)  # should not raise

    def test_raises_on_negative_debit(self):
        result = ParseResult(bank=Bank.BCA)
        result.opening_balance = Decimal("1000000")
        # Aggregate still reconciles (closing = opening - debit + credit):
        # debit is -100 → net effect is +100 → closing 1000100.00
        result.closing_balance = Decimal("1000100")
        result.transactions = [
            Transaction("02/01/2026", "BAD", Decimal("-100"), Decimal("0"), Decimal("1000100")),
        ]
        with pytest.raises(ValidationError, match="negative debit"):
            validate_statement(result)

    def test_raises_on_balance_mismatch(self):
        result = ParseResult(bank=Bank.BCA)
        result.opening_balance = Decimal("1000000")
        result.closing_balance = Decimal("999999")  # wrong
        result.transactions = [
            Transaction("02/01/2026", "IN", Decimal("0"), Decimal("1000000"), Decimal("2000000")),
        ]
        with pytest.raises(ValidationError, match="Balance mismatch"):
            validate_statement(result)
