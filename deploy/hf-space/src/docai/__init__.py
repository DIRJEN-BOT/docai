"""DocAI — Indonesian bank e-statement parser.

Parse Indonesian bank e-statement PDFs (BCA, and soon Mandiri/BNI/BRI) into
structured transaction data, with built-in balance validation.

Quickstart:
    from docai import BCAParser, validate_statement

    result = BCAParser().parse("my_statement.pdf")
    validate_statement(result)
"""

from docai.base import ParseError, PasswordProtectedError
from docai.models import Bank, ParseResult, Transaction
from docai.parsers.bca import BCAParser
from docai.parsers.registry import get_parser, list_banks
from docai.utils import parse_indonesian_number
from docai.validation import (
    ValidationError,
    validate_balance,
    validate_debit_credit_non_negative,
    validate_running_balances,
    validate_statement,
)

__version__ = "0.1.0"

__all__ = [
    "BCAParser",
    "Bank",
    "ParseError",
    "ParseResult",
    "PasswordProtectedError",
    "Transaction",
    "ValidationError",
    "get_parser",
    "list_banks",
    "parse_indonesian_number",
    "validate_balance",
    "validate_debit_credit_non_negative",
    "validate_running_balances",
    "validate_statement",
]