"""Command-line interface for docai.

Usage:
    docai parse --bank bca statement.pdf
    → structured JSON to stdout; exit 0 on success.

    docai parse --bank bca a.pdf b.pdf c.pdf
    → JSON array of per-file results (each with "file" and "result").

    docai parse --bank bca statement.pdf --format csv
    → semicolon-delimited CSV to stdout (header: tanggal;keterangan;debit;kredit;saldo).

Exits non-zero if any file fails to parse or fails validation (balance-check,
non-negative amounts, or row-level running-balance consistency).
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional, Tuple

from docai.base import ParseError, PasswordProtectedError
from docai.models import ParseResult
from docai.parsers.registry import get_parser, list_banks
from docai.serialization import result_to_csv, result_to_dict
from docai.validation import ValidationError, validate_statement


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docai",
        description="Parse Indonesian bank e-statement PDFs into structured JSON.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    parse_p = sub.add_parser("parse", help="Parse statement PDF(s) to JSON/CSV")
    parse_p.add_argument(
        "pdf",
        nargs="+",
        help="Path(s) to the e-statement PDF file(s)",
    )
    parse_p.add_argument(
        "--bank",
        required=True,
        choices=list_banks(),
        help="Bank identifier (see: docai banks)",
    )
    parse_p.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parse_p.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip the validation pass (balance-check + running balances)",
    )
    parse_p.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output",
    )

    banks_p = sub.add_parser("banks", help="List supported banks")
    return parser


def _parse_one(
    pdf_path: str, bank: str, do_validate: bool
) -> Tuple[ParseResult, str, Optional[str], Optional[str]]:
    """Parse one file. Returns (result, balance_status, validation_error, error)."""
    parser_instance = get_parser(bank)
    try:
        result = parser_instance.parse(pdf_path)
    except PasswordProtectedError as e:
        return None, None, None, str(e)
    except (ParseError, FileNotFoundError, ValueError) as e:
        return None, None, None, str(e)

    balance_status = "passed"
    validation_error: Optional[str] = None
    if do_validate:
        try:
            validate_statement(result)
        except ValidationError as e:
            balance_status = "failed"
            validation_error = str(e)
    return result, balance_status, validation_error, None


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "banks":
        for bank in list_banks():
            print(bank)
        return 0

    # command == "parse"
    do_validate = not args.no_validate
    parsed: List[Tuple[str, ParseResult, str, Optional[str]]] = []  # (file, result, status, verr)
    errors: List[Tuple[str, str]] = []  # (file, error message)
    failed = False

    for pdf_path in args.pdf:
        result, balance_status, validation_error, error = _parse_one(
            pdf_path, args.bank, do_validate
        )
        if error is not None:
            errors.append((pdf_path, error))
            failed = True
            continue
        if balance_status == "failed":
            failed = True
        parsed.append((pdf_path, result, balance_status, validation_error))

    for pdf_path, error in errors:
        print(f"Error parsing {pdf_path}: {error}", file=sys.stderr)

    if args.format == "csv":
        for pdf_path, result, balance_status, validation_error in parsed:
            if len(args.pdf) > 1:
                print(f"# file: {pdf_path}")
            print(result_to_csv(result), end="")
            if balance_status == "failed":
                print(f"# validation: {validation_error}", file=sys.stderr)
        return 1 if failed else 0

    # JSON output. Single input file → one result object (same shape as
    # before); multiple input files → list of {"file": ..., "result": ...},
    # keyed off the INPUT count so a failed file in a batch cannot silently
    # change the output shape.
    def _payload(result: ParseResult, status: str, verr: Optional[str]) -> dict:
        payload = result_to_dict(result, status)
        if verr is not None:
            payload["validation_error"] = verr
        return payload

    if len(args.pdf) > 1:
        out = [
            {"file": pdf_path, "result": _payload(result, status, verr)}
            for pdf_path, result, status, verr in parsed
        ]
        if not out and errors:
            out = {"error": "no files could be parsed"}
    else:
        if not parsed:
            out = {"error": "no files could be parsed"}
        else:
            _, result, status, verr = parsed[0]
            out = _payload(result, status, verr)

    indent = 2 if args.pretty else None
    print(json.dumps(out, indent=indent))
    # Exit non-zero when any statement fails parse or validation (pipeline-friendly).
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())