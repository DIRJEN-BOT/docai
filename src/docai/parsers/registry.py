"""Parser registry — maps bank names to parser classes."""

from __future__ import annotations

from typing import Dict, Type

from docai.base import BaseParser
from docai.parsers.bca import BCAParser
from docai.parsers.bni import BNIStatementParser
from docai.parsers.mandiri import MandiriParser

_REGISTRY: Dict[str, Type[BaseParser]] = {
    "bca": BCAParser,
    "bni": BNIStatementParser,
    "mandiri": MandiriParser,
}


def get_parser(bank: str) -> BaseParser:
    """Get a parser instance for the given bank identifier."""
    bank_lower = bank.lower().strip()
    cls = _REGISTRY.get(bank_lower)
    if cls is None:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(
            f"No parser registered for bank '{bank}'. Available: {available}"
        )
    return cls()


def list_banks():
    """Return list of registered bank identifiers."""
    return list(_REGISTRY.keys())
