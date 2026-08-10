#!/usr/bin/env python3
"""Generate synthetic BCA-style e-statement PDFs for testing.

Produces PDFs that mimic BCA statement format with known transactions
and balances, so tests can assert exact parsing + balance-check results.

Usage:
    python tests/generate_fixtures.py
    → creates tests/fixtures/ with synthetic statement PDFs
"""

from __future__ import annotations

import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def fmt_idr(val: Decimal) -> str:
    """Format Decimal as Indonesian number: 1.234.567,89."""
    s = f"{val:,.2f}"  # 1,234,567.89
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def generate_bca_statement(
    filename: str,
    account_number: str,
    account_name: str,
    period: str,
    opening_balance: Decimal,
    transactions: list[dict],
    output_dir: Path | None = None,
    declared_closing_balance: Decimal | None = None,
) -> Path:
    """Generate a BCA-style e-statement PDF.

    Args:
        filename: output PDF filename (without .pdf)
        account_number: bank account number
        account_name: account holder name
        period: statement period string
        opening_balance: opening balance amount
        transactions: list of dicts with keys:
            - date: DD/MM/YYYY
            - description: transaction description
            - debit: amount (Decimal or str), 0 for credit-only
            - credit: amount (Decimal or str), 0 for debit-only
        output_dir: where to write (default: tests/fixtures/)
        declared_closing_balance: closing balance to write as "Saldo Akhir"
            instead of the computed value (for mismatch fixtures); None = computed

    Returns:
        Path to the generated PDF
    """
    try:
        from fpdf import FPDF
    except ImportError:
        print("ERROR: fpdf2 not installed. Run: pip install fpdf2", file=sys.stderr)
        sys.exit(1)

    out_dir = output_dir or FIXTURES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{filename}.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "BANK CENTRAL ASIA", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "BCA e-Statement", ln=True, align="C")
    pdf.ln(5)

    # Metadata — use Indonesian format (dots for thousands, comma for decimal)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, f"Rekening : {account_number}", ln=True)
    pdf.cell(0, 6, f"Nama Rekening : {account_name}", ln=True)
    pdf.cell(0, 6, f"Periode : {period}", ln=True)
    pdf.cell(0, 6, f"Saldo Awal : Rp {fmt_idr(opening_balance)}", ln=True)
    pdf.ln(3)

    # Compute closing balance
    running_balance = opening_balance
    for txn in transactions:
        debit = Decimal(str(txn.get("debit", 0)))
        credit = Decimal(str(txn.get("credit", 0)))
        running_balance = (running_balance - debit + credit).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    closing_balance = running_balance

    # Allow fixtures to declare a deliberately wrong closing balance
    # (e.g. to test balance-mismatch detection end-to-end).
    if declared_closing_balance is not None:
        closing_balance = declared_closing_balance

    pdf.cell(0, 6, f"Saldo Akhir : Rp {fmt_idr(closing_balance)}", ln=True)
    pdf.ln(3)

    # Table header
    pdf.set_font("Helvetica", "B", 8)
    col_widths = [25, 80, 30, 30, 30]
    headers = ["Tanggal", "Keterangan", "Debit", "Kredit", "Saldo"]
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 6, h, border=1, align="C")
    pdf.ln()

    # Transaction rows
    pdf.set_font("Helvetica", "", 8)
    running_balance = opening_balance
    for txn in transactions:
        debit = Decimal(str(txn.get("debit", 0)))
        credit = Decimal(str(txn.get("credit", 0)))
        running_balance = (running_balance - debit + credit).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        date_str = txn["date"]
        desc = txn["description"][:40]
        debit_str = fmt_idr(debit) if debit > 0 else ""
        credit_str = fmt_idr(credit) if credit > 0 else ""
        balance_str = fmt_idr(running_balance)

        pdf.cell(col_widths[0], 5, date_str, border=1, align="C")
        pdf.cell(col_widths[1], 5, desc, border=1)
        pdf.cell(col_widths[2], 5, debit_str, border=1, align="R")
        pdf.cell(col_widths[3], 5, credit_str, border=1, align="R")
        pdf.cell(col_widths[4], 5, balance_str, border=1, align="R")
        pdf.ln()

    pdf.output(str(pdf_path))
    return pdf_path


# ---------------------------------------------------------------------------
# Real BCA e-statement layout (as extracted from actual BCA PDFs)
# ---------------------------------------------------------------------------


def fmt_western(val: Decimal) -> str:
    """Format as BCA prints amounts in real statements: 1,234,567.89
    (commas = thousands, dot = decimal). f-string {:,.2f} does exactly this."""
    return f"{val:,.2f}"


def generate_bca_native_statement(
    filename: str,
    account_number: str,
    account_name: str,
    period: str,
    opening_balance: Decimal,
    transactions: list[dict],
    output_dir: Path | None = None,
    declared_closing_balance: Decimal | None = None,
) -> Path:
    """Generate a PDF that mirrors the real BCA e-statement layout.

    Real BCA e-statements differ from the synthetic fixtures:
    - headers "NO. REKENING :", "PERIODE :", "MATA UANG : IDR"
    - rows start with "DD/MM" dates, descriptions span multiple lines, and the
      row closes with "[code] amount [DB/CR] [running balance]"
    - amounts use commas for thousands and a dot for decimals ("9,846,915.69")
    - a trailing summary block: SALDO AWAL / MUTASI CR / MUTASI DB / SALDO AKHIR
    """
    try:
        from fpdf import FPDF
    except ImportError:
        print("ERROR: fpdf2 not installed. Run: pip install fpdf2", file=sys.stderr)
        sys.exit(1)

    out_dir = output_dir or FIXTURES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{filename}.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Courier", "", 9)
    pdf.add_page()

    def line(text: str = "") -> None:
        pdf.cell(0, 5, text, ln=True)

    # --- page header (repeats on every page, like the real statement) ---
    def page_header(page_no: int, total_pages: int) -> None:
        line("REKENING GIRO")
        line("KCU JAKARTA THAMRIN")
        line(account_name)
        line("JAKARTA")
        line("JL. CONTOH NO. 1 RT 000 RW 000 RT000RW000")
        line("JAKARTA 10110")
        line("INDONESIA")
        line(f"NO. REKENING : {account_number}")
        line("HALAMAN :")
        line(f"PERIODE : {period}")
        line("MATA UANG : IDR")
        line()
        line("CATATAN:")
        line("Apabila nasabah tidak melakukan sanggahan atas Laporan Mutasi")
        line("Rekening ini sampai dengan akhir bulan berikutnya, nasabah")
        line("dianggap telah menyetujui segala data yang tercantum pada")
        line("Laporan Mutasi Rekening ini.")
        line()
        line("TANGGAL KETERANGAN CBG MUTASI SALDO")
        line(f"{page_no} /")
        line(f"{total_pages}")

    def emit_txn(t: dict, cumulative: Decimal) -> Decimal:
        """Print one multi-line row; returns the new running balance."""
        debit = Decimal(str(t.get("debit", 0)))
        credit = Decimal(str(t.get("credit", 0)))
        cumulative = (cumulative - debit + credit).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        code = t.get("code", "")
        if t.get("single_line"):
            # Single-line row like "15/01 BIAYA ADM 25,000.00 DB 9,929,972.00"
            label = " DB" if debit > 0 else " CR"
            line(
                f"{t['date']} {t['description']} "
                f"{fmt_western(debit if debit > 0 else credit)}{label} "
                f"{fmt_western(cumulative)}"
            )
            return cumulative
        desc_lines = [t["description"]] + list(t.get("extra_lines", []))
        show_balance = t.get("show_balance", True)
        show_label = t.get("show_label", False)
        raw_amt = t.get("raw_amount")
        for i, d in enumerate(desc_lines):
            line(f"{t['date']} {d}" if i == 0 else d)
        if raw_amt is not None:
            line(raw_amt)
        suffix = (" DB" if debit > 0 else " CR") if show_label else ""
        bal = f" {fmt_western(cumulative)}" if show_balance else ""
        line(f"{code} {fmt_western(debit if debit > 0 else credit)}{suffix}{bal}")
        return cumulative

    total_pages = 2
    running = opening_balance

    # --- page 1 ---
    page_header(1, total_pages)
    line(f"01/01 SALDO AWAL {fmt_western(opening_balance)}")
    page1 = list(transactions[:3])
    for t in page1:
        running = emit_txn(t, running)
    line("Bersambung ke halaman berikut")

    # --- page 2 ---
    pdf.add_page()
    page_header(2, total_pages)
    for t in transactions[3:]:
        running = emit_txn(t, running)

    # --- trailing summary block (last page) ---
    closing_balance = running
    if declared_closing_balance is not None:
        closing_balance = declared_closing_balance
    total_debit = sum(Decimal(str(t.get("debit", 0))) for t in transactions)
    total_credit = sum(Decimal(str(t.get("credit", 0))) for t in transactions)
    n_db = len([t for t in transactions if Decimal(str(t.get("debit", 0))) > 0])
    n_cr = len([t for t in transactions if Decimal(str(t.get("credit", 0))) > 0])
    line()
    line(f"SALDO AWAL : {fmt_western(opening_balance)}")
    line(f"MUTASI CR : {fmt_western(total_credit)} {n_cr}")
    line(f"MUTASI DB : {fmt_western(total_debit)} {n_db}")
    line(f"SALDO AKHIR : {fmt_western(closing_balance)}")

    pdf.output(str(pdf_path))
    return pdf_path


def generate_all_fixtures() -> dict:
    """Generate all test fixture PDFs. Returns dict of metadata for test assertions."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    fixtures = {}

    # ---- Fixture 1: Happy path ----
    txns_1 = [
        {"date": "02/01/2026", "description": "TRSF E-BANKING BCA", "debit": 0, "credit": 500000},
        {"date": "03/01/2026", "description": "ATM WD BCA KCP THAMRIN", "debit": 250000, "credit": 0},
        {"date": "05/01/2026", "description": "TRANSFER MASUK dari PT MAJU JAYA", "debit": 0, "credit": 3000000},
        {"date": "07/01/2026", "description": "PEMBAYARAN LISTRIK PLN", "debit": 750000, "credit": 0},
        {"date": "10/01/2026", "description": "SETORAN TUNAI", "debit": 0, "credit": 1500000},
        {"date": "15/01/2026", "description": "BIAYA ADM BULANAN", "debit": 25000, "credit": 0},
        {"date": "20/01/2026", "description": "TRANSFER dari PT SEJAHTERA", "debit": 0, "credit": 750000},
        {"date": "25/01/2026", "description": "ATM WD BCA GADING", "debit": 500000, "credit": 0},
    ]
    opening_1 = Decimal("1000000")
    closing_1 = opening_1
    for t in txns_1:
        closing_1 += Decimal(str(t.get("credit", 0))) - Decimal(str(t.get("debit", 0)))
    closing_1 = closing_1.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    f1_path = generate_bca_statement(
        filename="bca_happy_path",
        account_number="1234567890",
        account_name="BUDI SETIAWAN",
        period="01/01/2026 - 31/01/2026",
        opening_balance=opening_1,
        transactions=txns_1,
    )

    fixtures["happy_path"] = {
        "path": str(f1_path),
        "account_number": "1234567890",
        "account_name": "BUDI SETIAWAN",
        "period": "01/01/2026 - 31/01/2026",
        "opening_balance": str(opening_1),
        "closing_balance": str(closing_1),
        "num_transactions": len(txns_1),
        "total_debit": str(sum(Decimal(str(t.get("debit", 0))) for t in txns_1)),
        "total_credit": str(sum(Decimal(str(t.get("credit", 0))) for t in txns_1)),
        "transactions": txns_1,
    }

    # ---- Fixture 2: Balance mismatch (wrong declared closing) ----
    txns_2 = [
        {"date": "02/01/2026", "description": "SETORAN TUNAI", "debit": 0, "credit": 1000000},
    ]
    opening_2 = Decimal("500000")
    actual_closing_2 = opening_2 + Decimal("1000000")

    f2_path = generate_bca_statement(
        filename="bca_balance_mismatch",
        account_number="9876543210",
        account_name="SITI RAHMAWATI",
        period="01/01/2026 - 31/01/2026",
        opening_balance=opening_2,
        transactions=txns_2,
        # PDF deliberately declares the WRONG closing balance (2.000.000
        # instead of the computed 1.500.000) so validation rejects it E2E.
        declared_closing_balance=Decimal("2000000"),
    )

    fixtures["balance_mismatch"] = {
        "path": str(f2_path),
        "account_number": "9876543210",
        "account_name": "SITI RAHMAWATI",
        "period": "01/01/2026 - 31/01/2026",
        "opening_balance": str(opening_2),
        # PDF declares a wrong closing balance (2.000.000 vs computed 1.500.000)
        "declared_closing_balance": str(Decimal("2000000")),
        "actual_closing_balance": str(actual_closing_2),
        "num_transactions": 1,
    }

    # ---- Fixture 3: Credit-only (salary) ----
    txns_3 = [
        {"date": "01/01/2026", "description": "GAJI JANUARI 2026", "debit": 0, "credit": 8500000},
        {"date": "15/01/2026", "description": "BONUS PRODUKSI", "debit": 0, "credit": 2000000},
    ]
    opening_3 = Decimal("200000")
    closing_3 = opening_3
    for t in txns_3:
        closing_3 += Decimal(str(t.get("credit", 0))) - Decimal(str(t.get("debit", 0)))
    closing_3 = closing_3.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    f3_path = generate_bca_statement(
        filename="bca_credit_only",
        account_number="5555666677",
        account_name="DEWI KARTIKA",
        period="01/01/2026 - 31/01/2026",
        opening_balance=opening_3,
        transactions=txns_3,
    )

    fixtures["credit_only"] = {
        "path": str(f3_path),
        "account_number": "5555666677",
        "account_name": "DEWI KARTIKA",
        "opening_balance": str(opening_3),
        "closing_balance": str(closing_3),
        "num_transactions": 2,
        "transactions": txns_3,
    }

    # ---- Fixture 4: Large values ----
    txns_4 = [
        {"date": "05/01/2026", "description": "TRANSFER MASUK PT ABADI SENTOSA", "debit": 0, "credit": 50000000},
        {"date": "10/01/2026", "description": "PEMBAYARAN SUPPLIER CV BERSAMA", "debit": 35000000, "credit": 0},
        {"date": "15/01/2026", "description": "SETORAN TUNAI", "debit": 0, "credit": 10000000},
        {"date": "20/01/2026", "description": "BIAYA TRANSFER INTL", "debit": 250000, "credit": 0},
    ]
    opening_4 = Decimal("75000000")
    closing_4 = opening_4
    for t in txns_4:
        closing_4 += Decimal(str(t.get("credit", 0))) - Decimal(str(t.get("debit", 0)))
    closing_4 = closing_4.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    f4_path = generate_bca_statement(
        filename="bca_large_values",
        account_number="3333444455",
        account_name="PT MAKMUR JAYA",
        period="01/01/2026 - 31/01/2026",
        opening_balance=opening_4,
        transactions=txns_4,
    )

    fixtures["large_values"] = {
        "path": str(f4_path),
        "account_number": "3333444455",
        "account_name": "PT MAKMUR JAYA",
        "opening_balance": str(opening_4),
        "closing_balance": str(closing_4),
        "num_transactions": 4,
        "total_debit": str(sum(Decimal(str(t.get("debit", 0))) for t in txns_4)),
        "total_credit": str(sum(Decimal(str(t.get("credit", 0))) for t in txns_4)),
        "transactions": txns_4,
    }

    # ---- Fixture 5: Real BCA e-statement layout (native format) ----
    # Mirrors the multi-line rows, Western-style amounts and trailing summary
    # block found in actual BCA e-statement PDFs (see ESTATEMENT_* samples).
    native_txns = [
        {
            "date": "02/01", "description": "KR OTOMATIS MID : 885001061193",
            "extra_lines": ["BUDI MART", "QR :    5001000.00", "DDR:      35007.00"],
            "debit": 0, "credit": 4965993, "code": "0998",
        },
        {
            "date": "03/01", "description": "TRSF E-BANKING DB 0301/FTSCY/WS95051",
            "extra_lines": ["ATM THAMRIN", "250000.00"],
            "debit": 250000, "credit": 0,
            "raw_amount": "250000.00", "show_label": True, "show_balance": False,
        },
        {
            "date": "03/01", "description": "TRSF E-BANKING DB 0301/FTSCY/WS95051",
            "extra_lines": ["LISTRIK PLN", "750000.00"],
            "debit": 750000, "credit": 0,
            "raw_amount": "750000.00", "show_label": True,
        },
        {
            "date": "05/01", "description": "BI-FAST CR BIF TRANSFER DR",
            "extra_lines": ["535", "PT MAJU JAYA"],
            "debit": 0, "credit": 3000000,
        },
        {
            "date": "07/01", "description": "KR OTOMATIS MID : 885001061193",
            "extra_lines": ["BUDI MART", "QR :    2003000.00", "DDR:       14021.00"],
            "debit": 0, "credit": 1988979, "code": "0998",
        },
        {
            "date": "15/01", "description": "BIAYA ADM",
            "debit": 25000, "credit": 0, "single_line": True,
        },
    ]
    native_opening = Decimal("1000000")
    native_closing = native_opening
    for t in native_txns:
        native_closing += Decimal(str(t.get("credit", 0))) - Decimal(str(t.get("debit", 0)))
    native_closing = native_closing.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    f5_path = generate_bca_native_statement(
        filename="bca_native",
        account_number="1234567890",
        account_name="BUDI SETIAWAN",
        period="JANUARI 2026",
        opening_balance=native_opening,
        transactions=native_txns,
    )

    fixtures["native_format"] = {
        "path": str(f5_path),
        "account_number": "1234567890",
        "account_name": "BUDI SETIAWAN",
        "period": "JANUARI 2026",
        "opening_balance": str(native_opening),
        "closing_balance": str(native_closing),
        "num_transactions": len(native_txns),
        "total_debit": str(
            sum(Decimal(str(t.get("debit", 0))) for t in native_txns)
        ),
        "total_credit": str(
            sum(Decimal(str(t.get("credit", 0))) for t in native_txns)
        ),
        "transactions": native_txns,
    }

    # Save manifest
    manifest_path = FIXTURES_DIR / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(fixtures, f, indent=2)

    return fixtures


if __name__ == "__main__":
    fixtures = generate_all_fixtures()
    print(f"Generated {len(fixtures)} fixture PDFs in {FIXTURES_DIR}")
    for name, meta in fixtures.items():
        print(f"  {name}: {meta['path']}")
