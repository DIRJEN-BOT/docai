"""BNI e-statement PDF parser — modern Wondr (2023+) and legacy formats.

Handles two BNI statement generations:

Modern (Wondr / BNI Mobile 2023+):
    Columns: Tanggal & Waktu | Rincian Transaksi | Nominal (IDR) | Saldo (IDR)
    - Comma thousands, NO decimal (e.g. "+50,000", "-2,210,784")
    - Explicit +/- sign on amounts; unsigned balance
    - Date format: "DD Mon YYYY HH:MM:SS WIB"
    - Title: "Laporan Mutasi Rekening"
    - Password: DOB ddmmyyyy

Legacy (BNI Internet Banking / Corporate ~2020-2023):
    Columns: Tgl. | Keterangan | Cab. | Mutasi | Saldo
    - DB/CR suffix on debit/credit amounts (e.g. "4,200,000.00 DB")
    - Date format: "DD/MM"
    - Title: "Laporan Mutasi Rekening" or "ACCOUNT STATEMENT"
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Union

from docai.base import BaseParser, PasswordProtectedError, ParseError
from docai.models import Bank, ParseResult, Transaction
from docai.utils import clean_text, parse_indonesian_number


class BNIStatementParser(BaseParser):
    """Parser for BNI (Bank Negara Indonesia) e-statement PDFs.

    Supports both modern Wondr format (2023+) and legacy IB format.
    Auto-detects format based on header keywords.
    """

    @property
    def bank_name(self) -> str:
        return "bni"

    # --- Format detection tokens ---

    # Modern Wondr markers
    _MODERN_TOKENS = ("Tanggal & Waktu", "Rincian Transaksi")
    # Legacy markers (IB / Corporate)
    _LEGACY_TOKENS = ("Tgl.", "Mutasi", "Saldo")
    # Corporate uses "ACCOUNT STATEMENT" + Account No
    _LEGACY_CORP_TOKENS = ("ACCOUNT STATEMENT", "Account No")

    def parse(self, pdf_path: Union[str, Path]) -> ParseResult:
        path = self._open_pdf(pdf_path)
        text = self._extract_text(path)

        if not text.strip():
            raise ParseError(f"Could not extract text from {path}")

        result = ParseResult(bank=Bank.BNI)

        if self._is_modern_format(text):
            self._extract_metadata_modern(text, result)
            self._extract_transactions_modern(text, result)
        elif self._is_legacy_format(text):
            self._extract_metadata_legacy(text, result)
            self._extract_transactions_legacy(text, result)
        else:
            raise ParseError(
                "Unable to detect BNI format. "
                "Expected 'Tanggal & Waktu' (modern) or 'Tgl.' + 'Mutasi' (legacy)."
            )

        return result

    # ------------------------------------------------------------------
    # Format detection
    # ------------------------------------------------------------------

    def _is_modern_format(self, text: str) -> bool:
        """Detect modern Wondr format via unique header tokens."""
        return all(tok in text for tok in self._MODERN_TOKENS)

    def _is_legacy_format(self, text: str) -> bool:
        """Detect legacy IB/Corporate format."""
        # Corporate uses "ACCOUNT STATEMENT" + "DB/CR"
        if all(tok in text for tok in self._LEGACY_CORP_TOKENS):
            return True
        # Standard legacy IB
        return all(tok in text for tok in self._LEGACY_TOKENS)

    # ------------------------------------------------------------------
    # Text extraction
    # ------------------------------------------------------------------

    def _extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF. Raises PasswordProtectedError if encrypted."""
        try:
            import pdfplumber
        except ImportError:
            raise ParseError("pdfplumber is required for BNI parsing")

        try:
            pdf = pdfplumber.open(str(pdf_path))
        except Exception as e:
            msg = str(e).lower()
            if "password" in msg or "encrypted" in msg:
                raise PasswordProtectedError(
                    "PDF is password-protected. "
                    "Provide the password (DOB in DDMMYYYY format)."
                ) from e
            raise ParseError(f"Failed to open PDF {pdf_path}: {e}") from e

        pages_text: List[str] = []
        for page in pdf.pages:
            txt = page.extract_text() or ""
            pages_text.append(txt)
        pdf.close()
        return "\n".join(pages_text)

    # ------------------------------------------------------------------
    # Modern format (Wondr 2023+)
    # ------------------------------------------------------------------

    # Modern BNI amount: comma thousands, NO decimal, with sign
    # e.g. "+50,000", "-2,210,784", "1,551,141"
    _MODERN_AMOUNT = r"[+-]?\d{1,3}(?:,\d{3})*"
    # Modern date: DD Mon YYYY HH:MM:SS WIB
    _MODERN_DATE_RE = re.compile(
        r"(\d{2}\s+[A-Z][a-z]{2}\s+\d{4})\s+(\d{2}:\d{2}:\d{2}\s+WIB)"
    )
    # Modern transaction line: date + time + description + amount + balance
    _MODERN_TX_RE = re.compile(
        r"^(\d{2}\s+[A-Z][a-z]{2}\s+\d{4})\s+"  # date
        r"(\d{2}:\d{2}:\d{2}\s+WIB)\s+"          # time
        r"(.+?)\s+"                                 # description (greedy but bounded)
        r"([+-]?\d{1,3}(?:,\d{3})*)\s+"           # signed amount
        r"(\d{1,3}(?:,\d{3})*)$",                  # unsigned balance
        re.MULTILINE,
    )
    # Pipe-separated variant (some PDFs): No | Date | Time | Description | Amount | Balance
    _MODERN_PIPE_RE = re.compile(
        r"(\d+)\s*\|\s*"
        r"(\d{2}\s+[A-Z][a-z]{2}\s+\d{4})\s*\|\s*"
        r"(\d{2}:\d{2}:\d{2}\s+WIB)\s*\|\s*"
        r"(.+?)\s*\|\s*"
        r"([+-]?\d{1,3}(?:,\d{3})*)\s*\|\s*"
        r"(\d{1,3}(?:,\d{3})*)",
        re.MULTILINE,
    )

    def _parse_modern_amount(self, s: str) -> Decimal:
        """Parse modern BNI amount: comma thousands, no decimal, with optional sign.

        "+50,000" → Decimal("50000.00")
        "-2,210,784" → Decimal("2210784.00")
        "1,551,141" → Decimal("1551141.00")
        """
        s = s.strip()
        # Remove sign for now; handle debit/credit separately
        is_negative = s.startswith("-")
        numeric = s.lstrip("+-").replace(",", "")
        try:
            val = Decimal(numeric)
        except Exception:
            return Decimal("0")
        return val.quantize(Decimal("0.01"))

    def _normalize_modern_date(self, date_str: str) -> str:
        """Normalize 'DD Mon YYYY' to 'DD/MM/YYYY'."""
        _MONTH_MAP = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
        }
        parts = date_str.strip().split()
        if len(parts) == 3:
            day, mon, year = parts
            mon_num = _MONTH_MAP.get(mon, "01")
            return f"{day}/{mon_num}/{year}"
        return date_str

    def _extract_metadata_modern(self, text: str, result: ParseResult) -> None:
        """Extract account info and balances from modern BNI statement."""
        # Account: "TAPLUS - 327872529" or "TAPLUS MUDA - 399105645"
        acct_match = re.search(
            r"(?:TAPLUS(?:\s+MUDA)?)\s*-\s*(\d{8,12})", text
        )
        if acct_match:
            result.account_number = acct_match.group(1)

        # Account name (typically on same line or nearby)
        name_match = re.search(
            r"Nama(?:\s+Pemegang)?\s*[:\s]+(.+?)(?:\n|$)", text
        )
        if name_match:
            result.account_name = clean_text(name_match.group(1))

        # Period: "Periode: 1 - 30 November 2024"
        period_match = re.search(
            r"Periode:\s*(.+?)(?:\n|$)", text
        )
        if period_match:
            result.statement_period = clean_text(period_match.group(1))

        # Opening balance: "Saldo Awal" ... amount
        opening_match = re.search(
            r"Saldo\s+Awal[:\s]+([\d,.]+)", text
        )
        if opening_match:
            result.opening_balance = self._parse_modern_amount(opening_match.group(1))

        # Closing balance: "Saldo Akhir" ... amount
        closing_match = re.search(
            r"Saldo\s+Akhir[:\s]+([\d,.]+)", text
        )
        if closing_match:
            result.closing_balance = self._parse_modern_amount(closing_match.group(1))

    def _extract_transactions_modern(self, text: str, result: ParseResult) -> None:
        """Extract transactions from modern BNI format."""
        transactions: List[Transaction] = []

        # Try pipe-separated format first
        pipe_matches = list(self._MODERN_PIPE_RE.finditer(text))
        if pipe_matches:
            for m in pipe_matches:
                txn = self._build_modern_txn(
                    date_str=m.group(2),
                    description=m.group(4),
                    amount_str=m.group(5),
                    balance_str=m.group(6),
                    prev_balance=transactions[-1].balance if transactions else result.opening_balance,
                )
                if txn:
                    transactions.append(txn)
        else:
            # Try standard tab/space-separated format
            for m in self._MODERN_TX_RE.finditer(text):
                txn = self._build_modern_txn(
                    date_str=m.group(1),
                    description=m.group(3),
                    amount_str=m.group(4),
                    balance_str=m.group(5),
                    prev_balance=transactions[-1].balance if transactions else result.opening_balance,
                )
                if txn:
                    transactions.append(txn)

        result.transactions = transactions

    def _build_modern_txn(
        self,
        date_str: str,
        description: str,
        amount_str: str,
        balance_str: str,
        prev_balance: Optional[Decimal],
    ) -> Optional[Transaction]:
        """Build a Transaction from modern BNI fields."""
        amount = self._parse_modern_amount(amount_str)
        balance = self._parse_modern_amount(balance_str)
        normalized_date = self._normalize_modern_date(date_str)
        desc = clean_text(description)

        if amount == 0:
            return None

        is_debit = amount_str.strip().startswith("-")

        if is_debit:
            debit = amount
            credit = Decimal("0.00")
        else:
            debit = Decimal("0.00")
            credit = amount

        return Transaction(
            date=normalized_date,
            description=desc,
            debit=debit,
            credit=credit,
            balance=balance,
        )

    # ------------------------------------------------------------------
    # Legacy format (BNI IB / Corporate)
    # ------------------------------------------------------------------

    # For legacy IB: detect lines starting with a date
    _LEGACY_DATE_LINE_RE = re.compile(
        r"^(\d{2}/\d{2}(?:/\d{2,4})?)\s+(.+)$",
        re.MULTILINE,
    )
    # Find all numeric amounts in a line (comma-separated or dot-separated)
    _LEGACY_AMOUNT_RE = re.compile(r"\d[\d,]*\.\d{2}")
    # Corporate format: Posting Date | ... | Amount | D/K | Balance
    _CORP_TX_RE = re.compile(
        r"(\d{2}/\d{2}(?:/\d{4})?)\s+"       # posting date
        r"(.+?)\s+"                             # description
        r"([\d,.]+)\s+"                         # amount
        r"(D|K)\s+"                             # D=debit, K=credit (corporate)
        r"([\d,.]+)",                            # balance
        re.MULTILINE,
    )

    def _parse_legacy_amount(self, s: str) -> Decimal:
        """Parse legacy BNI amount: comma thousands with optional decimal.

        "4,200,000.00" → Decimal("4200000.00")
        "153,460,000.00" → Decimal("153460000.00")
        "1,234,567.89" → Decimal("1234567.89")
        """
        s = s.strip().replace(" ", "")
        # Remove commas (thousands separators)
        s = s.replace(",", "")
        try:
            return Decimal(s).quantize(Decimal("0.01"))
        except Exception:
            return Decimal("0")

    def _extract_metadata_legacy(self, text: str, result: ParseResult) -> None:
        """Extract account info and balances from legacy BNI statement."""
        # Account number: "No. Rekening: 001678340" or "Account No. : 0045206873"
        acct_match = re.search(
            r"(?:No\.?\s*Rekening|Account\s+No\.?\s*)[:\s]+(\d{8,15})", text
        )
        if acct_match:
            result.account_number = acct_match.group(1)

        # Account name
        name_match = re.search(
            r"Nama[:\s]+(.+?)(?:\n|$)", text
        )
        if name_match:
            result.account_name = clean_text(name_match.group(1))

        # Period
        period_match = re.search(
            r"(?:Periode\s+transaksi|Period)\s*[:\s]*(.+?)(?:\||$)", text
        )
        if period_match:
            result.statement_period = clean_text(period_match.group(1))

        # Opening balance: "Saldo Awal" or "Opening Balance" or "Ledger Balance"
        opening_match = re.search(
            r"(?:Saldo\s+Awal|Opening\s+Balance|Ledger\s+Balance)[:\s]+([\d,.]+)",
            text, re.IGNORECASE,
        )
        if opening_match:
            result.opening_balance = self._parse_legacy_amount(opening_match.group(1))

        # Closing balance: "Saldo Akhir" or "Closing Balance" or "Ending Balance"
        closing_match = re.search(
            r"(?:Saldo\s+Akhir|Closing\s+Balance|Ending\s+Balance)[:\s]+([\d,.]+)",
            text, re.IGNORECASE,
        )
        if closing_match:
            result.closing_balance = self._parse_legacy_amount(closing_match.group(1))

    def _extract_transactions_legacy(self, text: str, result: ParseResult) -> None:
        """Extract transactions from legacy BNI format.

        Handles both standard IB format and corporate format.
        Uses a line-by-line approach for robustness against varied layouts.
        """
        transactions: List[Transaction] = []

        # Try corporate format first (has explicit D/K column in structured layout)
        corp_matches = list(self._CORP_TX_RE.finditer(text))
        if corp_matches:
            for m in corp_matches:
                txn = self._build_legacy_txn(
                    date_str=m.group(1),
                    description=m.group(2),
                    amount_str=m.group(3),
                    dc_label=m.group(4),
                    balance_str=m.group(5),
                )
                if txn:
                    transactions.append(txn)
            result.transactions = transactions
            return

        # Robust line-by-line extraction for standard legacy format
        for m in self._LEGACY_DATE_LINE_RE.finditer(text):
            date_str = m.group(1)
            rest_of_line = m.group(2)

            # Skip metadata/summary lines
            if any(skip in rest_of_line.upper() for skip in (
                "SALDO AWAL", "SALDO AKHIR", "OPENING", "CLOSING",
                "ENDING", "LEDGER", "TOTAL", "KETERANGAN",
                "TGL.", "NO.", "NAMA",
            )):
                continue

            # Find all numeric amounts in the line
            amounts = list(self._LEGACY_AMOUNT_RE.finditer(rest_of_line))
            if len(amounts) < 2:
                # Need at least amount + balance
                continue

            # Last amount = balance, second-to-last = transaction amount
            balance_str = amounts[-1].group()
            amount_str = amounts[-2].group()

            # Determine DB/CR from the line
            # Check for DB/CR/D/K tokens (case-insensitive)
            upper_line = rest_of_line.upper()
            is_debit = False
            is_credit = False

            # Check for explicit D/K (corporate style)
            # Find the D or K that's standalone (not part of a word)
            dk_match = re.search(r'\b(D|K)\b', rest_of_line)
            if dk_match:
                is_debit = dk_match.group(1) == "D"
                is_credit = dk_match.group(1) == "K"

            # Check for DB/CR labels
            if not is_debit and not is_credit:
                if "DB" in upper_line:
                    is_debit = True
                elif "CR" in upper_line:
                    is_credit = True

            # If still ambiguous, skip (can't determine direction)
            if not is_debit and not is_credit:
                continue

            # Extract description: everything between date and first amount
            first_amount_pos = amounts[0].start()
            description = rest_of_line[:first_amount_pos].strip()
            # Remove trailing DB/CR/D/K labels from description
            description = re.sub(r'\s+(DB|CR|D|K)\s*$', '', description, flags=re.IGNORECASE)
            description = clean_text(description)

            txn = self._build_legacy_txn(
                date_str=date_str,
                description=description,
                amount_str=amount_str,
                dc_label="DB" if is_debit else "CR",
                balance_str=balance_str,
            )
            if txn:
                transactions.append(txn)

        result.transactions = transactions

    def _build_legacy_txn(
        self,
        date_str: str,
        description: str,
        amount_str: str,
        dc_label: str,
        balance_str: str,
    ) -> Optional[Transaction]:
        """Build a Transaction from legacy BNI fields."""
        amount = self._parse_legacy_amount(amount_str)
        balance = self._parse_legacy_amount(balance_str)
        desc = clean_text(description)

        if amount == 0:
            return None

        # DB = debit, CR/KR = credit
        is_debit = dc_label.upper() in ("DB", "D")

        if is_debit:
            debit = amount
            credit = Decimal("0.00")
        else:
            debit = Decimal("0.00")
            credit = amount

        # Normalize date: add year if missing
        normalized_date = self._normalize_legacy_date(date_str)

        return Transaction(
            date=normalized_date,
            description=desc,
            debit=debit,
            credit=credit,
            balance=balance,
        )

    def _normalize_legacy_date(self, date_str: str) -> str:
        """Normalize legacy date. If DD/MM, append statement year if available."""
        date_str = date_str.strip()
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 2:
                # DD/MM — try to get year from statement period
                # For now, return as-is; the caller can normalize
                return date_str
            elif len(parts) == 3:
                return date_str
        return date_str
