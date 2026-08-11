#!/usr/bin/env python3
"""Generate a synthetic Mandiri e-statement PDF fixture.

Uses reportlab to create a realistic Mandiri-format PDF that the
MandiriParser can parse: pipe-separated transactions with explicit
signs, Indonesian number formatting, and required metadata tokens.

The key insight: pypdf text extraction flattens independently-placed
drawString calls into separate lines. We MUST draw each transaction
row as a SINGLE drawString call with pipe separators so the parser
can match them.
"""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent / "demo_mandiri_statement.pdf"

# Account metadata
ACCOUNT_NUMBER = "123456789012"
ACCOUNT_NAME = "BUDI SANTOSO"
STATEMENT_PERIOD = "01 Jan 2026 - 30 Jun 2026"
CURRENCY = "IDR"

# Transactions: (date, description, signed_amount, running_balance)
# Dates use DD Mon YYYY format. Amounts use Indonesian format.
OPENING = 5_250_000
transactions = [
    ("05 Jan 2026", "GAJI JANUARI 2026", "+12.500.000", 17_750_000),
    ("05 Jan 2026", "TF ke BCA XXXX1234", "-3.500.000", 14_250_000),
    ("10 Jan 2026", "LISTRIK PLN", "-850.000", 13_400_000),
    ("12 Jan 2026", "PULSA INDOSAT", "-100.000", 13_300_000),
    ("15 Jan 2026", "TF dari BCA XXXX5678", "+2.000.000", 15_300_000),
    ("20 Jan 2026", "ATM WD", "-1.500.000", 13_800_000),
    ("25 Jan 2026", "BUNGA BULANAN", "+65.000", 13_865_000),
    ("05 Feb 2026", "GAJI FEBRUARI 2026", "+12.500.000", 26_365_000),
    ("08 Feb 2026", "TF ke BCA XXXX1234", "-3.500.000", 22_865_000),
    ("12 Feb 2026", "LISTRIK PLN", "-900.000", 21_965_000),
    ("15 Feb 2026", "TF dari BCA XXXX5678", "+1.500.000", 23_465_000),
    ("20 Feb 2026", "ATM WD", "-2.000.000", 21_465_000),
    ("28 Feb 2026", "BUNGA BULANAN", "+75.000", 21_540_000),
    ("05 Mar 2026", "GAJI MARET 2026", "+12.500.000", 34_040_000),
    ("08 Mar 2026", "TF ke BCA XXXX1234", "-3.500.000", 30_540_000),
    ("10 Mar 2026", "LISTRIK PLN", "-875.000", 29_665_000),
    ("15 Mar 2026", "TF dari BCA XXXX5678", "+2.000.000", 31_665_000),
    ("20 Mar 2026", "ATM WD", "-1.000.000", 30_665_000),
    ("25 Mar 2026", "BUNGA BULANAN", "+85.000", 30_750_000),
    ("05 Apr 2026", "GAJI APRIL 2026", "+12.500.000", 43_250_000),
    ("08 Apr 2026", "TF ke BCA XXXX1234", "-3.500.000", 39_750_000),
    ("12 Apr 2026", "LISTRIK PLN", "-920.000", 38_830_000),
    ("15 Apr 2026", "TF dari BCA XXXX5678", "+1.500.000", 40_330_000),
    ("20 Apr 2026", "ATM WD", "-2.500.000", 37_830_000),
    ("30 Apr 2026", "BUNGA BULANAN", "+90.000", 37_920_000),
    ("05 May 2026", "GAJI MEI 2026", "+12.500.000", 50_420_000),
    ("08 May 2026", "TF ke BCA XXXX1234", "-3.500.000", 46_920_000),
    ("12 May 2026", "LISTRIK PLN", "-880.000", 46_040_000),
    ("15 May 2026", "TF dari BCA XXXX5678", "+2.000.000", 48_040_000),
    ("20 May 2026", "ATM WD", "-1.500.000", 46_540_000),
    ("31 May 2026", "BUNGA BULANAN", "+95.000", 46_635_000),
    ("05 Jun 2026", "GAJI JUNI 2026", "+12.500.000", 59_135_000),
    ("08 Jun 2026", "TF ke BCA XXXX1234", "-3.500.000", 55_635_000),
    ("12 Jun 2026", "LISTRIK PLN", "-910.000", 54_725_000),
    ("15 Jun 2026", "TF dari BCA XXXX5678", "+1.500.000", 56_225_000),
    ("20 Jun 2026", "ATM WD", "-2.000.000", 54_225_000),
    ("30 Jun 2026", "BUNGA BULANAN", "+100.000", 54_325_000),
]

CLOSING = transactions[-1][3]


def fmt_idr(n: int) -> str:
    """Format number as Indonesian: 1.234.567"""
    s = str(n)
    parts = []
    while len(s) > 3:
        parts.append(s[-3:])
        s = s[:-3]
    parts.append(s)
    return ".".join(reversed(parts))


def draw_pdf() -> None:
    c = canvas.Canvas(str(OUT), pagesize=A4)
    w, h = A4
    x_margin = 20 * mm
    y = h - 20 * mm
    line_h = 4.5 * mm

    def check_page():
        nonlocal y
        if y < 30 * mm:
            c.showPage()
            y = h - 20 * mm
            return True
        return False

    # Title — single line
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_margin, y, "e-Statement")
    y -= 8 * mm

    # Metadata — each on its own line (parser reads these as separate lines)
    c.setFont("Helvetica", 9)
    meta = [
        f"Nomor Rekening/Account Number: {ACCOUNT_NUMBER}",
        f"Nama/Name: {ACCOUNT_NAME}",
        f"Periode/Period: {STATEMENT_PERIOD}",
        f"Mata Uang/Currency: {CURRENCY}",
        f"Saldo Awal/Initial Balance: {fmt_idr(OPENING)}",
    ]
    for line in meta:
        check_page()
        c.drawString(x_margin, y, line)
        y -= line_h
    y -= 3 * mm

    # Column header — pipe-separated so parser skips it
    check_page()
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_margin, y, "No | Tanggal | Keterangan | Nominal (IDR) | Saldo (IDR)")
    y -= 2 * mm
    c.line(x_margin, y, w - x_margin, y)
    y -= 3 * mm

    # Transaction rows — each as a SINGLE drawString with pipes
    c.setFont("Helvetica", 8)
    for idx, (date, desc, amount, balance) in enumerate(transactions, 1):
        check_page()
        row = f"{idx} | {date} | {desc} | {amount} | {fmt_idr(balance)}"
        c.drawString(x_margin, y, row)
        y -= line_h

    # Closing balance
    y -= 3 * mm
    check_page()
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x_margin, y, f"Saldo Akhir/Closing Balance: {fmt_idr(CLOSING)}")
    y -= 5 * mm

    # End marker
    c.setFont("Helvetica", 7)
    c.drawString(x_margin, y, "Ini adalah batas akhir transaksi anda")
    y -= 4 * mm
    c.drawString(x_margin, y, "Mandiri Call 14000")
    y -= 4 * mm
    c.drawString(x_margin, y, "PT Bank Mandiri (Persero) Tbk.")

    c.save()
    print(f"Generated: {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    draw_pdf()
