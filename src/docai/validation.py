"""Balance-check validation for parsed statements."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from docai.models import ParseResult


class ValidationError(Exception):
    """Raised when statement data fails validation."""

    pass


def validate_balance(result: ParseResult) -> None:
    """Verify that transaction rows reconcile to the closing balance.

    Checks:
    1. Sum of all credits - sum of all debits + opening_balance == closing_balance
    2. The result has at least one transaction

    Raises ValidationError on failure with a human-readable message.
    """
    if not result.transactions:
        raise ValidationError(
            "No transactions found in statement — cannot validate balance."
        )

    computed = result.computed_closing()
    declared = result.closing_balance

    if computed != declared:
        total_debit = result.total_debit
        total_credit = result.total_credit
        raise ValidationError(
            f"Balance mismatch: opening={result.opening_balance}, "
            f"credit={total_credit}, debit={total_debit}, "
            f"computed_closing={computed}, declared_closing={declared}. "
            f"Difference = {computed - declared}"
        )


def validate_debit_credit_non_negative(result: ParseResult) -> None:
    """Ensure no negative debit/credit values."""
    for i, t in enumerate(result.transactions):
        if t.debit < 0:
            raise ValidationError(
                f"Transaction {i} has negative debit: {t.debit}"
            )
        if t.credit < 0:
            raise ValidationError(
                f"Transaction {i} has negative credit: {t.credit}"
            )


def validate_running_balances(result: ParseResult) -> None:
    """Verify each row's running balance matches opening + net transactions.

    Catches parser artifacts that a closing-balance-only check would miss —
    e.g. an amount attached to the wrong row, or a skipped row that still
    happens to reconcile to the closing balance.
    """
    running = result.opening_balance
    for i, t in enumerate(result.transactions):
        expected = (running - t.debit + t.credit).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if t.balance != expected:
            raise ValidationError(
                f"Transaction {i} ({t.date}) running-balance mismatch: "
                f"row_balance={t.balance}, expected={expected}. "
                f"Possible misparse — the amount may be attached to the "
                f"wrong description."
            )
        running = t.balance


def validate_statement(result: ParseResult) -> None:
    """Run the full validation suite in one pass.

    Order matters: the aggregate balance check fails fast on empty/aggregate
    mismatches, then amount sanity, then row-level running-balance consistency.

    Raises ValidationError on the first failure.
    """
    validate_balance(result)
    validate_debit_credit_non_negative(result)
    validate_running_balances(result)
