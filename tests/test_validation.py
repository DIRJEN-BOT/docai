"""Dedicated validation tests."""

from __future__ import annotations

from decimal import Decimal

import pytest

from docai.models import Bank, ParseResult, Transaction
from docai.validation import ValidationError, validate_balance, validate_debit_credit_non_negative


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
