"""Command-line interface for docai.

Usage:
    docai parse --bank bca statement.pdf
    → structured JSON to stdout; exit 0 on success.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from docai.base import ParseError, PasswordProtectedError
from docai.models import ParseResult
from docai.parsers.registry import get_parser, list_banks
from docai.serialization import result_to_dict
from docai.validation import ValidationError, validate_balance


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docai",
        description="Parse Indonesian bank e-statement PDFs into structured JSON.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    parse_p = sub.add_parser("parse", help="Parse a statement PDF to JSON")
    parse_p.add_argument("pdf", help="Path to the e-statement PDF file")
    parse_p.add_argument(
        "--bank",
        required=True,
        choices=list_banks(),
        help="Bank identifier (see: docai banks)",
    )
    parse_p.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip the balance-check validation pass",
    )
    parse_p.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output",
    )

    banks_p = sub.add_parser("banks", help="List supported banks")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "banks":
        for bank in list_banks():
            print(bank)
        return 0

    # command == "parse"
    try:
        parser_instance = get_parser(args.bank)
        result = parser_instance.parse(args.pdf)
    except PasswordProtectedError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except (ParseError, FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    balance_status = "passed"
    validation_error: Optional[str] = None
    if not args.no_validate:
        try:
            validate_balance(result)
        except ValidationError as e:
            balance_status = "failed"
            validation_error = str(e)

    payload = result_to_dict(result, balance_status)
    if validation_error is not None:
        payload["validation_error"] = validation_error

    indent = 2 if args.pretty else None
    print(json.dumps(payload, indent=indent))
    # Exit non-zero when a statement fails balance-check (useful in pipelines).
    return 1 if balance_status == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
