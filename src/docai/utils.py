"""Shared utilities for DocAI parsers."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


def parse_indonesian_number(s: str) -> Decimal:
    """Parse a number string that may use Indonesian formatting.

    Handles: "1.234.567,89" → 1234567.89
             "500.000"      → 500000.00
             "1234567.89"   → 1234567.89
             ""             → 0.00
    """
    s = s.strip().replace(" ", "")
    if not s:
        return Decimal("0")

    # BCA e-statements (real PDFs) print amounts like "54,291,427.59"
    # (commas = thousands, dot = decimal), while the synthetic fixtures use
    # the classic Indonesian style "1.000.000,00" (dots = thousands,
    # comma = decimal). Support both by looking at the LAST separator:
    #   "1.234.567,89" → comma is last → dots thousands, comma decimal
    #   "54,291,427.59" → dot is last → commas thousands, dot decimal
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            # Indonesian: 1.234.567,89 → remove dots, replace comma with dot
            s = s.replace(".", "").replace(",", ".")
        else:
            # Western/BCA: 54,291,427.59 → commas are thousands separators
            s = s.replace(",", "")
    elif "," in s:
        # No dot at all → commas are thousands separators ("60,000,000")
        s = s.replace(",", "")
    elif "." in s:
        # Could be "1.234" (Indonesian thousands) or "1234.56" (Western decimal)
        # Heuristic: if exactly 3 digits after the dot → thousands separator
        parts = s.split(".")
        if len(parts) == 2 and len(parts[1]) == 3:
            # "500.000" → 500000 (Indonesian thousands, no decimal)
            s = s.replace(".", "")
        elif len(parts) > 2:
            # Multiple dots → all are thousands separators
            s = s.replace(".", "")
        # else: single dot with 1-2 digits after → Western decimal, keep as-is

    try:
        return Decimal(s).quantize(Decimal("0.01"))
    except InvalidOperation:
        return Decimal("0")


def clean_text(s: str) -> str:
    """Normalize whitespace and common PDF artifacts."""
    s = s.replace("\xa0", " ")  # non-breaking space
    s = re.sub(r"\s+", " ", s)
    return s.strip()
