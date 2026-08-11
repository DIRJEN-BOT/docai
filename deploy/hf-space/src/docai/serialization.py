"""Serialization helpers shared by the CLI and the API."""

from __future__ import annotations

import csv
import io

from docai.models import ParseResult


def result_to_dict(result: ParseResult, balance_status: str) -> dict:
    """Serialize a ParseResult to a JSON-friendly dict."""
    return {
        "bank": result.bank.value,
        "account_number": result.account_number,
        "account_name": result.account_name,
        "statement_period": result.statement_period,
        "opening_balance": float(result.opening_balance),
        "closing_balance": float(result.closing_balance),
        "currency": result.currency,
        "total_debit": float(result.total_debit),
        "total_credit": float(result.total_credit),
        "balance_check": balance_status,
        "transactions": [
            {
                "date": t.date,
                "description": t.description,
                "debit": float(t.debit),
                "credit": float(t.credit),
                "balance": float(t.balance),
                "reference": t.reference,
            }
            for t in result.transactions
        ],
    }


def result_to_csv(result: ParseResult, delimiter: str = ";") -> str:
    """Serialize transactions to CSV text (semicolon-separated by default).

    Header: tanggal;keterangan;debit;kredit;saldo
    Amounts use the plain Decimal string form (e.g. "4965993.00").
    """
    out = io.StringIO()
    writer = csv.writer(out, delimiter=delimiter, lineterminator="\n")
    writer.writerow(["tanggal", "keterangan", "debit", "kredit", "saldo"])
    for t in result.transactions:
        writer.writerow(
            [t.date, t.description, str(t.debit), str(t.credit), str(t.balance)]
        )
    return out.getvalue()