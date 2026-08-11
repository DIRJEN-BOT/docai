"""Mandiri e-statement PDF parser — modern Livin' format (2023+).

Handles the bilingual Mandiri e-statement layout:
- Password/DOB-locked PDFs → PasswordProtectedError with clear message
- Detection via 'e-Statement' + 'Saldo Awal'/'Initial Balance' tokens
- Bilingual column headers: Tanggal/Date, Keterangan/Remarks, Nominal/Amount, Saldo/Balance
- Two transaction line formats:
  a) Pipe-separated: No | Date | Time | Description | Amount | Balance
  b) Inline: HH:MM:SS WIB Description +/-Amount
- Indonesian number formatting: 1.234.567,89 (dot thousands, comma decimal)
- Explicit sign: + = credit (incoming), - = debit (outgoing)
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Tuple, Union

from docai.base import BaseParser, PasswordProtectedError, ParseError
from docai.models import Bank, ParseResult, Transaction
from docai.utils import clean_text, parse_indonesian_number


class MandiriParser(BaseParser):
    """Parser for Mandiri (Bank Mandiri) e-statement PDFs — modern Livin' format (2023+)."""

    @property
    def bank_name(self) -> str:
        return "mandiri"

    # Mandiri amount pattern (Indonesian format): "1.234.567,89" or "50.000"
    IDR_AMOUNT = r"\d{1,3}(?:\.\d{3})+(?:,\d{2})?"
    IDR_AMOUNT_SHORT = r"\d+(?:,\d{2})"

    # Mandiri date pattern: DD Mon YYYY (e.g. "05 Apr 2025")
    MANDIRI_DATE = r"(\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})"

    # Month name to number mapping
    MONTH_MAP = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
    }

    # End-of-table marker
    END_MARKER = "ini adalah batas akhir transaksi anda"

    def parse(self, pdf_path: Union[str, Path]) -> ParseResult:
        """Parse a Mandiri e-statement PDF and return structured result.

        Raises ParseError or PasswordProtectedError on failure.
        """
        path = self._open_pdf(pdf_path)
        text = self._extract_text(path)

        if not text.strip():
            raise ParseError(f"Could not extract text from {path}")

        if not self._is_mandiri_format(text):
            raise ParseError(
                f"This does not appear to be a Mandiri e-statement. "
                f"Expected tokens: 'e-Statement' + 'Saldo Awal'/'Initial Balance'. "
                f"File: {path}"
            )

        result = ParseResult(bank=Bank.MANDIRI)
        self._extract_metadata(text, result)
        self._extract_transactions(text, result)
        return result

    # ------------------------------------------------------------------
    # Format detection
    # ------------------------------------------------------------------

    def _is_mandiri_format(self, text: str) -> bool:
        """Detect the modern Mandiri e-statement layout.

        Requires 'e-Statement' AND ('Saldo Awal' or 'Initial Balance').
        """
        has_estatement = "e-Statement" in text or "e-statement" in text
        has_saldo_awal = "Saldo Awal" in text or "Initial Balance" in text
        return has_estatement and has_saldo_awal

    # ------------------------------------------------------------------
    # Metadata extraction
    # ------------------------------------------------------------------

    def _extract_metadata(self, text: str, result: ParseResult) -> None:
        """Extract account number, name, period, balances from the statement header."""
        # Account number: "Nomor Rekening/Account Number" followed by digits
        m = re.search(
            r"(?:Nomor Rekening|Account\s*Number)\s*/?\s*(?:Nomor\s*)?:?\s*(\d+)",
            text,
            re.IGNORECASE,
        )
        if m:
            result.account_number = m.group(1)

        # Account name: "Nama/Name: <value>"
        m = re.search(
            r"Nama/Name\s*:\s*(.+?)(?:\n|$)",
            text,
        )
        if m:
            result.account_name = clean_text(m.group(1))

        # Statement period: "Periode/Period: <date range>"
        m = re.search(
            r"(?:Periode/Period)\s*:\s*(.+?)(?:\n|$)",
            text,
            re.IGNORECASE,
        )
        if m:
            result.statement_period = clean_text(m.group(1))

        # Currency: "Mata Uang/Currency: IDR"
        m = re.search(
            r"Mata Uang/Currency\s*:\s*(\w+)",
            text,
            re.IGNORECASE,
        )
        if m:
            result.currency = m.group(1)

        # Opening balance: "Saldo Awal/Initial Balance" + amount
        m = re.search(
            r"(?:Saldo\s*Awal|Initial\s*Balance)\s*/?\s*(?:Saldo\s*Awal\s*)?:?\s*"
            r"(?:IDR|Rp\.?)?\s*([\d.,]+)",
            text,
            re.IGNORECASE,
        )
        if m:
            result.opening_balance = parse_indonesian_number(m.group(1))

        # Closing balance: "Saldo Akhir/Closing Balance" + amount
        m = re.search(
            r"(?:Saldo\s*Akhir|Closing\s*Balance)\s*/?\s*(?:Saldo\s*Akhir\s*)?:?\s*"
            r"(?:IDR|Rp\.?)?\s*([\d.,]+)",
            text,
            re.IGNORECASE,
        )
        if m:
            result.closing_balance = parse_indonesian_number(m.group(1))

        # Dana masuk (incoming) and Dana keluar (outgoing) — optional summary
        m = re.search(
            r"(?:Dana\s*Masuk|Incoming)\s*/?\s*(?:Dana\s*Masuk\s*)?:?\s*"
            r"(?:IDR|Rp\.?)?\s*([\d.,]+)",
            text,
            re.IGNORECASE,
        )
        # (total_credit/total_debit not stored in ParseResult directly;
        # they're computed from transactions)

    # ------------------------------------------------------------------
    # Transaction extraction
    # ------------------------------------------------------------------

    def _extract_transactions(self, text: str, result: ParseResult) -> None:
        """Extract transaction rows from the statement body.

        Handles two line formats:
        a) Pipe-separated: No | Date | Time? | Description | Amount | Balance
        b) Inline: HH:MM:SS WIB Description +/-Amount [Balance]
        """
        transactions: List[Transaction] = []

        # Trim text to end marker if present
        end_idx = text.lower().find(self.END_MARKER)
        if end_idx != -1:
            text = text[:end_idx]

        lines = text.split("\n")

        # Skip patterns for metadata/header lines
        skip_patterns = [
            r"^\s*$",
            r"e-Statement",
            r"(?:Nomor Rekening|Account\s*Number)",
            r"(?:Nama|Name)\s*/",
            r"(?:Periode|Period)\s*/",
            r"(?:Mata Uang|Currency)",
            r"(?:Saldo\s*Awal|Initial\s*Balance)",
            r"(?:Saldo\s*Akhir|Closing\s*Balance)",
            r"(?:Dana\s*Masuk|Incoming)",
            r"(?:Dana\s*Keluar|Outgoing)",
            r"No\s*\|\s*Tanggal",
            r"Tanggal/Date",
            r"Keterangan/Remarks",
            r"Nominal.*IDR.*Amount",
            r"Saldo.*IDR.*Balance",
            r"^No\s*$",
            r"Mandiri Call",
            r"PT Bank Mandiri",
            r"yang ditandai",
        ]

        prev_balance: Optional[Decimal] = None

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Stop at end marker (already trimmed text, but check line-level too)
            if self.END_MARKER in line_stripped.lower():
                break

            if any(re.search(p, line_stripped, re.IGNORECASE) for p in skip_patterns):
                continue

            txn = self._parse_transaction_line(line_stripped, prev_balance)
            if txn is not None:
                prev_balance = txn.balance
                transactions.append(txn)

        result.transactions = transactions

    def _parse_transaction_line(
        self, line: str, prev_balance: Optional[Decimal]
    ) -> Optional[Transaction]:
        """Parse a single line as a Mandiri transaction.

        Tries pipe-separated format first, then inline format.
        Returns Transaction or None if line doesn't match.
        """
        # Try pipe-separated format first
        txn = self._parse_pipe_separated(line, prev_balance)
        if txn is not None:
            return txn

        # Try inline format
        return self._parse_inline(line, prev_balance)

    def _parse_pipe_separated(
        self, line: str, prev_balance: Optional[Decimal]
    ) -> Optional[Transaction]:
        """Parse pipe-separated transaction line.

        Format: No | Date | Description | Amount | Balance
        Or:     No | Date | Time | Description | Amount | Balance
        """
        if "|" not in line:
            return None

        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]  # remove empty parts

        if len(parts) < 4:
            return None

        # Find the date part (DD Mon YYYY)
        date_str = None
        desc_parts = []
        amount_str = None
        balance_str = None

        for i, part in enumerate(parts):
            date_m = re.match(
                r"^(\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})\s*$",
                part,
            )
            if date_m:
                date_str = date_m.group(1)
                # Everything after date until the last two numeric parts
                remaining = parts[i + 1:]
                break
        else:
            return None

        if not date_str:
            return None

        if len(remaining) < 2:
            return None

        # Last part is always balance, second-to-last is amount
        balance_str = remaining[-1]
        amount_str = remaining[-2]
        # Everything between date and amount is description (may include time)
        desc_parts = remaining[:-2]
        description = clean_text(" ".join(desc_parts))

        # Parse amount — must have explicit sign (+/-)
        amount_m = re.match(r"^([+-])(" + self.IDR_AMOUNT + r")$", amount_str)
        if not amount_m:
            # Try short amount (no thousands separator)
            amount_m = re.match(r"^([+-])(\d+(?:,\d{2})?)$", amount_str)
        if not amount_m:
            return None

        sign = amount_m.group(1)
        amount = parse_indonesian_number(amount_m.group(2))
        balance = parse_indonesian_number(balance_str)

        # Normalize date to DD/MM/YYYY for consistency
        normalized_date = self._normalize_mandiri_date(date_str)

        if sign == "-":
            return Transaction(
                date=normalized_date,
                description=description,
                debit=amount,
                credit=Decimal("0"),
                balance=balance,
            )
        else:  # sign == "+"
            return Transaction(
                date=normalized_date,
                description=description,
                debit=Decimal("0"),
                credit=amount,
                balance=balance,
            )

    def _parse_inline(
        self, line: str, prev_balance: Optional[Decimal]
    ) -> Optional[Transaction]:
        """Parse inline transaction line.

        Format: HH:MM:SS WIB Description +/-Amount [Balance]
        Or:     DD Mon YYYY HH:MM:SS WIB Description +/-Amount [Balance]

        The date may appear at the start (pipe-separated with spaces instead of pipes)
        or the line may start directly with time.
        """
        # Pattern: optional date + time + description + signed amount + optional balance
        # The key indicator is the time pattern HH:MM:SS WIB followed by description
        # and ending with signed amount

        # Match the signed amount at the end (with optional trailing balance)
        # Amount must be the last or second-to-last number
        AMT = self.IDR_AMOUNT

        # Try to find date at the beginning
        date_str = None
        rest = line

        date_m = re.match(
            r"(\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})\s+(.*)",
            line,
        )
        if date_m:
            date_str = date_m.group(1)
            rest = date_m.group(2)

        # Now rest should be: [HH:MM:SS WIB] Description +/-Amount [Balance]
        # Find the signed amount pattern: +/- followed by Indonesian number
        # The signed amount may be followed by an unsigned balance at the end.
        SHORT_AMT = r"\d+(?:,\d{2})?"
        signed_amt_m = re.search(
            r"([+-](" + AMT + r"))\s+(" + AMT + r")\s*$",
            rest,
        )
        if not signed_amt_m:
            signed_amt_m = re.search(
                r"([+-](" + SHORT_AMT + r"))\s+(" + SHORT_AMT + r")\s*$",
                rest,
            )
        if not signed_amt_m:
            # Try signed amount at end (no trailing balance)
            signed_amt_m = re.search(
                r"([+-](" + AMT + r"))\s*$",
                rest,
            )
        if not signed_amt_m:
            signed_amt_m = re.search(
                r"([+-](" + SHORT_AMT + r"))\s*$",
                rest,
            )
        if not signed_amt_m:
            return None

        sign = signed_amt_m.group(1)[0]
        amount = parse_indonesian_number(signed_amt_m.group(2))
        description_part = rest[: signed_amt_m.start()].strip()

        # If no date found, try to extract from the beginning of the line
        if not date_str:
            # Look for time-only pattern at start (no date)
            time_m = re.match(
                r"(\d{2}:\d{2}:\d{2}\s+WIB)\s+(.*)",
                description_part,
            )
            if time_m:
                # Time-only line with no date — skip (no date to record)
                return None
            # Might have date embedded differently
            return None

        # Normalize time from description if present (keep it in description)
        normalized_date = self._normalize_mandiri_date(date_str)

        if sign == "-":
            return Transaction(
                date=normalized_date,
                description=clean_text(description_part),
                debit=amount,
                credit=Decimal("0"),
                balance=prev_balance - amount if prev_balance is not None else Decimal("0"),
            )
        else:  # sign == "+"
            return Transaction(
                date=normalized_date,
                description=clean_text(description_part),
                debit=Decimal("0"),
                credit=amount,
                balance=prev_balance + amount if prev_balance is not None else Decimal("0"),
            )

    # ------------------------------------------------------------------
    # Date normalization
    # ------------------------------------------------------------------

    def _normalize_mandiri_date(self, date_str: str) -> str:
        """Convert 'DD Mon YYYY' to 'DD/MM/YYYY' for consistency with BCA format."""
        m = re.match(r"(\d{2})\s+(\w{3})\s+(\d{4})", date_str)
        if not m:
            return date_str

        day = m.group(1)
        mon_name = m.group(2)
        year = m.group(3)
        mon_num = self.MONTH_MAP.get(mon_name)
        if mon_num is None:
            return date_str

        return f"{day}/{mon_num}/{year}"

    # ------------------------------------------------------------------
    # PDF text extraction
    # ------------------------------------------------------------------

    def _extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF. Raises PasswordProtectedError if encrypted."""
        try:
            import pypdf

            reader = pypdf.PdfReader(str(pdf_path))

            if reader.is_encrypted:
                try:
                    decrypt_result = reader.decrypt("")
                    if decrypt_result == 0:
                        raise PasswordProtectedError(
                            f"This Mandiri statement PDF is password-protected "
                            f"(likely locked with date of birth: DDMMYYYY format). "
                            f"Please unlock it first:\n"
                            f"  1. Open the PDF in a PDF reader (e.g. Adobe Acrobat)\n"
                            f"  2. Enter your DOB as password (DDMMYYYY)\n"
                            f"  3. Save the unlocked PDF\n"
                            f"  4. Re-run this parser on the unlocked file.\n"
                            f"File: {pdf_path}"
                        )
                except Exception:
                    raise PasswordProtectedError(
                        f"This Mandiri statement PDF is password-protected "
                        f"(likely locked with date of birth: DDMMYYYY format). "
                        f"Please unlock it first:\n"
                        f"  1. Open the PDF in a PDF reader (e.g. Adobe Acrobat)\n"
                        f"  2. Enter your DOB as password (DDMMYYYY)\n"
                        f"  3. Save the unlocked PDF\n"
                        f"  4. Re-run this parser on the unlocked file.\n"
                        f"File: {pdf_path}"
                    )

            pages_text = []
            for page in reader.pages:
                pages_text.append(page.extract_text() or "")
            return "\n".join(pages_text)

        except PasswordProtectedError:
            raise
        except ImportError:
            return self._extract_text_pdfplumber(pdf_path)
        except Exception as e:
            raise ParseError(f"Failed to read PDF {pdf_path}: {e}")

    def _extract_text_pdfplumber(self, pdf_path: Path) -> str:
        """Fallback text extraction via pdfplumber."""
        try:
            import pdfplumber

            pages_text = []
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
            return "\n".join(pages_text)
        except ImportError:
            raise ParseError(
                "Neither pypdf nor pdfplumber is installed. "
                "Install one: pip install pypdf pdfplumber"
            )
