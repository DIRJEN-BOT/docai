"""Data models for parsed bank statements."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import List


class Bank(str, Enum):
    BCA = "bca"
    MANDIRI = "mandiri"
    BNI = "bni"
    BRI = "bri"


@dataclass(frozen=True)
class Transaction:
    """A single bank statement row."""

    date: str  # DD/MM/YYYY or DD/MM/YY — kept as string for fidelity
    description: str
    debit: Decimal  # money out (0 if credit)
    credit: Decimal  # money in (0 if debit)
    balance: Decimal  # running balance after this transaction
    reference: str = ""  # optional transaction reference / number

    def __post_init__(self) -> None:
        # Ensure Decimal types on frozen dataclass — use object.__setattr__
        for fld in ("debit", "credit", "balance"):
            val = getattr(self, fld)
            if not isinstance(val, Decimal):
                object.__setattr__(self, fld, Decimal(str(val)))


@dataclass
class ParseResult:
    """Result of parsing a bank statement PDF."""

    bank: Bank
    account_number: str = ""
    account_name: str = ""
    statement_period: str = ""  # e.g. "01/01/2026 - 31/01/2026"
    opening_balance: Decimal = Decimal("0")
    closing_balance: Decimal = Decimal("0")
    currency: str = "IDR"
    transactions: List[Transaction] = field(default_factory=list)

    @property
    def total_debit(self) -> Decimal:
        return sum((t.debit for t in self.transactions), Decimal("0"))

    @property
    def total_credit(self) -> Decimal:
        return sum((t.credit for t in self.transactions), Decimal("0"))

    def computed_closing(self) -> Decimal:
        """Compute closing balance from opening + net transactions."""
        net = self.total_credit - self.total_debit
        return (self.opening_balance + net).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
