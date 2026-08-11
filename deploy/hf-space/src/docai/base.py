"""Abstract base parser for bank e-statement PDFs."""

from __future__ import annotations

import abc
from pathlib import Path
from typing import Union

from docai.models import ParseResult


class ParseError(Exception):
    """Raised when a statement cannot be parsed."""

    pass


class PasswordProtectedError(ParseError):
    """Raised when the PDF is password-protected (e.g. DOB-locked)."""

    pass


class BaseParser(abc.ABC):
    """Interface that all bank parsers implement."""

    @property
    @abc.abstractmethod
    def bank_name(self) -> str:
        """Canonical bank identifier, e.g. 'bca'."""
        ...

    @abc.abstractmethod
    def parse(self, pdf_path: Union[str, Path]) -> ParseResult:
        """Parse the given PDF and return structured result.

        Raises ParseError or subclass on failure.
        """
        ...

    def _open_pdf(self, pdf_path: Union[str, Path]) -> Path:
        """Validate that the file exists and is a PDF."""
        p = Path(pdf_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")
        if not p.suffix.lower() == ".pdf":
            raise ValueError(f"Not a PDF file: {p}")
        return p
