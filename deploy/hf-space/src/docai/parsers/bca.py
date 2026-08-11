"""BCA e-statement PDF parser.

Handles known BCA quirks:
- Password/DOB-locked PDFs → PasswordProtectedError with clear message
- "DB" label convention (when present in extracted text)
- Rows: date | description | debit | credit | balance
- When columns are merged (amount + balance), uses balance comparison
- Multi-page statements
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Union

from docai.base import BaseParser, PasswordProtectedError, ParseError
from docai.models import Bank, ParseResult, Transaction
from docai.utils import clean_text, parse_indonesian_number


class BCAParser(BaseParser):
    """Parser for BCA (Bank Central Asia) e-statement PDFs."""

    @property
    def bank_name(self) -> str:
        return "bca"

    # Native (real) BCA e-statement amount format: "9,846,915.69", "60,000,000.00",
    # "30,000.00" — commas are thousands separators, dot is the decimal separator.
    NATIVE_AMOUNT = r"\d{1,3}(?:,\d{3})+(?:\.\d{2})?"
    NATIVE_DATE = r"(\d{2}/\d{2}(?:/\d{2,4})?)"
    DC_LABELS = {"DB": "debit", "CR": "credit", "KR": "credit"}

    def parse(self, pdf_path: Union[str, Path]) -> ParseResult:
        path = self._open_pdf(pdf_path)
        text = self._extract_text(path)

        result = ParseResult(bank=Bank.BCA)
        if self._is_native_format(text):
            # Real BCA e-statement layout (multi-line rows, uppercase headers,
            # "NO. REKENING", trailing summary block SALDO AWAL/MUTASI/SALDO AKHIR).
            self._extract_metadata_native(text, result)
            self._extract_transactions_native(text, result)
        else:
            # Synthetic/older-style layout ("Rekening :", "Nama Rekening :",
            # "Saldo Awal : Rp …", one line per transaction).
            self._extract_metadata(text, result)
            self._extract_transactions(text, result)
        self._normalize_dates(result)
        return result

    def _normalize_dates(self, result: ParseResult) -> None:
        """Append the statement year to bare DD/MM dates.

        Real BCA e-statements print dates as "DD/MM" (no year). Accounting
        imports need a full date, so we inherit the year from the statement
        period (e.g. "JANUARI 2026" → 2026). Dates that already carry a year
        are left untouched. Limitation: for a cross-year period
        ("31/12/2025 - 02/01/2026") the FIRST year in the period is used.
        """
        m = re.search(r"(?:19|20)\d{2}", result.statement_period)
        if not m:
            return
        year = m.group(0)
        for t in result.transactions:
            if re.fullmatch(r"\d{2}/\d{2}", t.date):
                object.__setattr__(t, "date", f"{t.date}/{year}")

    def _is_native_format(self, text: str) -> bool:
        """Detect the real BCA e-statement layout vs the synthetic one."""
        return bool(
            re.search(
                r"TANGGAL\s+KETERANGAN\s+CBG\s+MUTASI\s+SALDO|"
                r"SALDO AWAL\s*:|"
                r"MUTASI\s+(?:CR|DB)\s*:",
                text,
            )
        )

    def _extract_metadata_native(self, text: str, result: ParseResult) -> None:
        """Extract header + trailing summary from a real BCA e-statement."""
        m = re.search(r"NO\.?\s*REKENING\s*:\s*(\d+)", text)
        if m:
            result.account_number = m.group(1)

        # Header block: "REKENING GIRO\nKCU JOMBANG\n<account name>\n..."
        m = re.search(r"(?:REKENING GIRO|TABUNGAN)[^\n]*\n\s*[^\n]*\n\s*([^\n]+)", text)
        if m:
            result.account_name = clean_text(m.group(1))

        m = re.search(r"PERIODE\s*:\s*(.+?)(?:\n|$)", text)
        if m:
            result.statement_period = clean_text(m.group(1))

        m = re.search(r"MATA UANG\s*:\s*(\w+)", text)
        if m:
            result.currency = m.group(1)

        # Trailing summary block (last page):
        #   SALDO AWAL : 54,291,427.59
        #   MUTASI CR : 179,269,600.12 21
        #   MUTASI DB : 204,050,000.00 29
        #   SALDO AKHIR : 29,511,027.71
        m = re.search(r"SALDO AWAL\s*:\s*([\d.,]+)", text)
        if m:
            result.opening_balance = parse_indonesian_number(m.group(1))

        m = re.search(r"SALDO AKHIR\s*:\s*([\d.,]+)", text)
        if m:
            result.closing_balance = parse_indonesian_number(m.group(1))

    def _extract_transactions_native(self, text: str, result: ParseResult) -> None:
        """Extract transactions from a real BCA e-statement (multi-line rows).

        Each row starts with a "DD/MM" line, continues with description lines,
        and ends with a closing line that holds the mutation amount (and optionally
        a DB/CR label and the running balance). A row may also be a single line
        ("31/10 BIAYA ADM 30,000.00 DB 29,511,027.71"). The printed running
        balance is missing from many closing lines, so debit/credit is resolved
        by: explicit DB/CR/KR label on the closing line → label embedded in the
        description → comparison of the printed balance with the computed
        running balance → default credit.
        """
        transactions: List[Transaction] = []
        running: Optional[Decimal] = result.opening_balance or None
        current: Optional[dict] = None  # {"date": ..., "desc_parts": [...]}
        in_table = False

        for raw in text.split("\n"):
            line = raw.strip()
            if not line:
                continue

            # Column header marks the start of the transaction table.
            if re.fullmatch(r"TANGGAL\s+KETERANGAN\s+CBG\s+MUTASI\s+SALDO", line):
                in_table = True
                continue

            # Page header repeats on every page → leave table mode.
            if line.startswith(("REKENING GIRO", "TABUNGAN")):
                in_table = False
                current = None
                continue

            if not in_table:
                continue

            if (
                "Bersambung" in line
                or re.match(r"^\d+\s*/\s*$", line)  # "1 /"
                or line.startswith(("SALDO AWAL :", "SALDO AKHIR :", "MUTASI CR :", "MUTASI DB :"))
            ):
                continue

            date_m = re.match(rf"^{self.NATIVE_DATE}\s*(.*)$", line)
            if date_m:
                # A new row starts — any previously open row without a closing
                # amount is incomplete and gets dropped.
                current = None
                date_str = date_m.group(1)
                rest = date_m.group(2).strip()

                # Row "01/10 SALDO AWAL 54,291,427.59" → opening balance, not a txn
                if re.match(r"SALDO AWAL\b", rest, re.IGNORECASE):
                    amt_m = re.search(r"([\d.,]+)\s*$", rest)
                    if amt_m:
                        opening_val = parse_indonesian_number(amt_m.group(1))
                        if not result.opening_balance:
                            result.opening_balance = opening_val
                            running = opening_val
                    continue

                inline = self._parse_native_inline(rest)
                if inline is not None:
                    desc, amt, label, bal = inline
                    running = self._build_native_txn(
                        date_str, desc, amt, label, bal, running, transactions
                    )
                else:
                    current = {"date": date_str, "desc_parts": [rest] if rest else []}
                continue

            # Non-date line: either a continuation of the description or the
            # closing line with the mutation amount.
            closing = self._parse_native_closing(line)
            if closing is not None and current is not None:
                amt, label, bal = closing
                desc = clean_text(" ".join(current["desc_parts"]))
                running = self._build_native_txn(
                    current["date"],
                    desc,
                    amt,
                    label,
                    bal,
                    running,
                    transactions,
                    desc_hint=desc,
                )
                current = None
            elif closing is None and current is not None:
                current["desc_parts"].append(line)
            # closing line with no open row → ignore

        result.transactions = transactions

    def _parse_native_inline(
        self, rest: str
    ) -> Optional[tuple]:
        """Parse a single-line native row: desc + amount [+ label [+ balance]]."""
        m = re.match(
            rf"^(.+?)\s+({self.NATIVE_AMOUNT})\s*(DB|CR|KR)?\s*"
            rf"({self.NATIVE_AMOUNT})?\s*$",
            rest,
            re.IGNORECASE,
        )
        if not m:
            return None
        label = m.group(3).upper() if m.group(3) else None
        bal = (
            parse_indonesian_number(m.group(4))
            if m.group(4)
            else None
        )
        return (
            clean_text(m.group(1)),
            parse_indonesian_number(m.group(2)),
            label,
            bal,
        )

    def _parse_native_closing(self, line: str) -> Optional[tuple]:
        """Parse a closing line: [code] amount [+ label] [+ running balance]."""
        amounts = re.findall(self.NATIVE_AMOUNT, line)
        if not amounts:
            return None
        labels = re.findall(r"\b(DB|CR|KR)\b", line, re.IGNORECASE)
        amt = parse_indonesian_number(amounts[0])
        bal = (
            parse_indonesian_number(amounts[1])
            if len(amounts) > 1
            else None
        )
        label = labels[0].upper() if labels else None
        return amt, label, bal

    def _build_native_txn(
        self,
        date_str: str,
        desc: str,
        amt: Decimal,
        label: Optional[str],
        bal: Optional[Decimal],
        running: Optional[Decimal],
        transactions: List[Transaction],
        desc_hint: Optional[str] = None,
    ) -> Optional[Decimal]:
        """Determine debit/credit, build the Transaction, return new running balance."""
        dc = self.DC_LABELS.get(label)
        if dc is None and desc_hint is None:
            desc_hint = desc
        if dc is None and desc_hint:
            m = re.search(r"\b(DB|CR|KR)\b", desc_hint, re.IGNORECASE)
            if m:
                dc = self.DC_LABELS.get(m.group(1).upper())
        if dc is None and bal is not None and running is not None:
            dc = "credit" if bal >= running else "debit"
        if dc is None:
            dc = "credit"

        if dc == "debit":
            expected = running - amt if running is not None else None
            txn_bal = bal if bal is not None else (expected if expected is not None else Decimal("0"))
            transactions.append(
                Transaction(
                    date=date_str, description=desc,
                    debit=amt, credit=Decimal("0"), balance=txn_bal,
                )
            )
            return txn_bal if bal is not None else expected
        else:
            expected = running + amt if running is not None else None
            txn_bal = bal if bal is not None else (expected if expected is not None else Decimal("0"))
            transactions.append(
                Transaction(
                    date=date_str, description=desc,
                    debit=Decimal("0"), credit=amt, balance=txn_bal,
                )
            )
            return txn_bal if bal is not None else expected

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
                            f"This BCA statement PDF is password-protected "
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
                        f"This BCA statement PDF is password-protected "
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

    def _extract_metadata(self, text: str, result: ParseResult) -> None:
        """Extract account number, name, period, opening/closing balance."""
        m = re.search(r"Rekening\s*:\s*(\d+)", text)
        if m:
            result.account_number = m.group(1)

        m = re.search(r"Nama Rekening\s*:\s*(.+?)(?:\n|$)", text)
        if m:
            result.account_name = clean_text(m.group(1))

        m = re.search(r"Periode\s*:\s*(.+?)(?:\n|$)", text)
        if m:
            result.statement_period = clean_text(m.group(1))

        # Saldo Awal: "Rp 1.000.000,00" or "Rp 1.000.000.00"
        m = re.search(r"Saldo Awal\s*[:\s]*Rp\.?\s*([\d.,]+)", text)
        if m:
            result.opening_balance = parse_indonesian_number(m.group(1))

        m = re.search(r"Saldo Akhir\s*[:\s]*Rp\.?\s*([\d.,]+)", text)
        if m:
            result.closing_balance = parse_indonesian_number(m.group(1))

    def _extract_transactions(self, text: str, result: ParseResult) -> None:
        """Extract transaction rows using balance-based debit/credit detection.

        The extracted text from BCA PDFs typically shows:
            date  description  [amount]  balance

        Where [amount] may be:
        - Two numbers (debit/credit columns separate): "500.000,00  1.500.000,00"
        - One number + balance: "500.000,00 1.500.000,00"
        - Amount with DB/CR label: "500.000,00 DB 1.500.000,00"

        We detect debit vs credit by comparing balance with previous balance.
        """
        lines = text.split("\n")
        transactions: List[Transaction] = []

        # Skip metadata/header lines
        skip_patterns = [
            r"^\s*$",
            r"Rekening\s*:",
            r"Nama Rekening",
            r"Periode\s*:",
            r"Saldo Awal",
            r"Saldo Akhir",
            r"^\s*Tanggal\s*$",
            r"^\s*Tanggal\s+Transaksi",
            r"^\s*Description",
            r"^\s*Ket",
            r"^\s*Debit\s+Kredit",
            r"^\s*DEBIT\s+KREDIT",
            r"^\s*Berita",
            r"^BCA\s",
            r"^Bank Central Asia",
            r"^BCA e-Statement",
            r"Cetak\s*:",
            r"Lembar\s*:",
            r"^\s*No\s*$",
        ]

        prev_balance: Optional[Decimal] = None

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

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
        """Parse a single line as a transaction.

        Returns Transaction or None if line doesn't match.
        Uses balance comparison to determine debit vs credit.
        """
        date_pattern = r"(\d{2}/\d{2}/\d{2,4})"

        # Amount pattern: must have at least one dot or comma (real IDR amounts always do)
        # This prevents matching years like "2026" or plain integers in descriptions
        AMT = r"[\d]*[.,][\d.,]+"  # e.g. "500.000,00" or "8.500.000,00" or "500.000"

        # Pattern A: has DB/CR label — easiest to parse
        m = re.match(
            rf"{date_pattern}\s+(.+?)\s+({AMT})\s*(DB|CR|db|cr)\s+({AMT})\s*$",
            line,
        )
        if m:
            amount = parse_indonesian_number(m.group(3))
            balance = parse_indonesian_number(m.group(5))
            dc = m.group(4).upper()
            if dc == "DB":
                return Transaction(
                    date=m.group(1),
                    description=clean_text(m.group(2)),
                    debit=amount,
                    credit=Decimal("0"),
                    balance=balance,
                )
            else:
                return Transaction(
                    date=m.group(1),
                    description=clean_text(m.group(2)),
                    debit=Decimal("0"),
                    credit=amount,
                    balance=balance,
                )

        # Pattern B: three amounts (debit_col credit_col balance)
        m = re.match(
            rf"{date_pattern}\s+(.+?)\s+({AMT})\s+({AMT})\s+({AMT})\s*$",
            line,
        )
        if m:
            col3 = parse_indonesian_number(m.group(3))
            col4 = parse_indonesian_number(m.group(4))
            balance = parse_indonesian_number(m.group(5))
            desc = clean_text(m.group(2))
            date_str = m.group(1)

            if col3 == Decimal("0") and col4 > Decimal("0"):
                return Transaction(date=date_str, description=desc,
                                   debit=Decimal("0"), credit=col4, balance=balance)
            elif col4 == Decimal("0") and col3 > Decimal("0"):
                return Transaction(date=date_str, description=desc,
                                   debit=col3, credit=Decimal("0"), balance=balance)
            else:
                # Ambiguous — use balance comparison
                return self._balance_based_txn(date_str, desc, col3, balance, prev_balance)

        # Pattern C: two amounts (amount + balance) — most common from PDF extraction
        m = re.match(
            rf"{date_pattern}\s+(.+?)\s+({AMT})\s+({AMT})\s*$",
            line,
        )
        if m:
            amount = parse_indonesian_number(m.group(3))
            balance = parse_indonesian_number(m.group(4))
            desc = clean_text(m.group(2))
            date_str = m.group(1)

            return self._balance_based_txn(date_str, desc, amount, balance, prev_balance)

        return None

    def _balance_based_txn(
        self,
        date_str: str,
        description: str,
        amount: Decimal,
        balance: Decimal,
        prev_balance: Optional[Decimal],
    ) -> Transaction:
        """Determine debit vs credit from balance change.

        If prev_balance is known:
        - balance > prev_balance → credit (deposit)
        - balance < prev_balance → debit (withdrawal)
        - balance == prev_balance → credit (no change, treat as zero-amount)
        """
        if prev_balance is not None and prev_balance != Decimal("0"):
            if balance < prev_balance:
                # Balance went down → debit
                return Transaction(
                    date=date_str, description=description,
                    debit=amount, credit=Decimal("0"), balance=balance,
                )
            else:
                # Balance went up or same → credit
                return Transaction(
                    date=date_str, description=description,
                    debit=Decimal("0"), credit=amount, balance=balance,
                )
        else:
            # No previous balance — default to credit (first transaction)
            return Transaction(
                date=date_str, description=description,
                debit=Decimal("0"), credit=amount, balance=balance,
            )
