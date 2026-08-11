#!/usr/bin/env python3
"""Generate a realistic synthetic BCA e-statement PDF for the DocAI Verify demo.

Uses reportlab to produce a native-format BCA statement that the BCAParser
can parse. The layout mirrors real BCA e-statements:
- Header block (REKENING GIRO, branch, account info)
- NO. REKENING, PERIODE, MATA UANG fields
- Transaction rows with DD/MM dates, DB/CR labels, running balance
- Trailing summary block (SALDO AWAL, MUTASI CR/DB, SALDO AKHIR)

Each line is a single drawString call to ensure pypdf text extraction works.

Usage:
    python scripts/generate_demo_statement.py
    -> fixtures/demo_bca_statement.pdf
"""

from __future__ import annotations

import random
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

FIXTURES_DIR = PROJECT_ROOT / "fixtures"
OUTPUT_PATH = FIXTURES_DIR / "demo_bca_statement.pdf"


def fmt(val: Decimal) -> str:
    """Format Decimal as BCA native amount: 12,500,000.00"""
    return f"{val:,.2f}"


random.seed(42)

SALARY = Decimal("12500000")
OPENING_BALANCE = Decimal("5000000")
RENT = Decimal("2500000")
ELECTRICITY = Decimal("450000")
INTERNET = Decimal("350000")

MONTHS = [("01", 31), ("02", 28), ("03", 31), ("04", 30), ("05", 31), ("06", 30)]

FOOD_OPTIONS = [
    ("PEMBAYARAN GOFOOD", (45000, 180000)),
    ("PEMBAYARAN GRABFOOD", (50000, 160000)),
    ("MERCHANT ABC RESTO", (60000, 250000)),
    ("POS DEBIT KFC", (55000, 120000)),
    ("QRIS WARUNG MAKAN", (30000, 85000)),
]

TRANSPORT_OPTIONS = [
    ("TOP UP GOJEK", (20000, 100000)),
    ("TOP UP GRAB", (25000, 90000)),
    ("SHELL ISTRA PEMBAYARAN", (150000, 500000)),
    ("SPBU PERTAMINA", (100000, 400000)),
    ("PARKIR IRAMA MASUK", (5000, 25000)),
]

SHOPPING_OPTIONS = [
    ("PEMBAYARAN SHOPEE", (75000, 500000)),
    ("TOKOPEDIA PEMBAYARAN", (100000, 350000)),
    ("LAZADA PEMBAYARAN", (80000, 300000)),
    ("ATM WD BCA KCP THAMRIN", (100000, 500000)),
    ("TRANSFER KELUAR BCA", (200000, 800000)),
]


def generate_transactions() -> list[dict]:
    """Generate 6 months of realistic transaction data."""
    txns = []
    balance = OPENING_BALANCE

    for month_num, days in MONTHS:
        # Salary on 25th
        balance += SALARY
        txns.append({
            "date": f"25/{month_num}",
            "description": "Transfer BI Fast Dari PT MAJU JAYA SUKSES Gaji Bulanan",
            "credit": SALARY, "debit": Decimal("0"), "balance": balance,
        })

        # Freelance income (1-2x per month)
        for fd in sorted(random.sample(range(5, 22), random.choice([1, 2]))):
            amt = Decimal(str(random.randint(3000000, 5000000)))
            balance += amt
            txns.append({
                "date": f"{fd:02d}/{month_num}",
                "description": "Transfer BI Fast Dari PT TEKNOLOGI NUSANTARA Proyek Freelance",
                "credit": amt, "debit": Decimal("0"), "balance": balance,
            })

        # Rent on 1st
        balance -= RENT
        txns.append({
            "date": f"01/{month_num}",
            "description": "TRANSFER KELUAR BCA Sewa Bulanan",
            "debit": RENT, "credit": Decimal("0"), "balance": balance,
        })

        # Electricity
        balance -= ELECTRICITY
        txns.append({
            "date": f"{random.randint(5, 15):02d}/{month_num}",
            "description": "PEMBAYARAN LISTRIK PLN",
            "debit": ELECTRICITY, "credit": Decimal("0"), "balance": balance,
        })

        # Internet
        balance -= INTERNET
        txns.append({
            "date": f"{random.randint(8, 18):02d}/{month_num}",
            "description": "PEMBAYARAN INDOSAT FREEDOM INTERNET",
            "debit": INTERNET, "credit": Decimal("0"), "balance": balance,
        })

        # Food (2-4x/month)
        for fd in sorted(random.sample(range(2, days - 2), random.randint(2, 4))):
            name, (lo, hi) = random.choice(FOOD_OPTIONS)
            amt = Decimal(str(random.randint(lo, hi)))
            balance -= amt
            txns.append({
                "date": f"{fd:02d}/{month_num}",
                "description": name,
                "debit": amt, "credit": Decimal("0"), "balance": balance,
            })

        # Transport (2-3x/month)
        for td in sorted(random.sample(range(3, days - 1), random.randint(2, 3))):
            name, (lo, hi) = random.choice(TRANSPORT_OPTIONS)
            amt = Decimal(str(random.randint(lo, hi)))
            balance -= amt
            txns.append({
                "date": f"{td:02d}/{month_num}",
                "description": name,
                "debit": amt, "credit": Decimal("0"), "balance": balance,
            })

        # Shopping (1-2x/month)
        for sd in sorted(random.sample(range(10, days - 3), random.randint(1, 2))):
            name, (lo, hi) = random.choice(SHOPPING_OPTIONS)
            amt = Decimal(str(random.randint(lo, hi)))
            balance -= amt
            txns.append({
                "date": f"{sd:02d}/{month_num}",
                "description": name,
                "debit": amt, "credit": Decimal("0"), "balance": balance,
            })

    # Sort by date then recompute running balance
    txns.sort(key=lambda t: (int(t["date"].split("/")[1]), int(t["date"].split("/")[0])))
    running = OPENING_BALANCE
    for t in txns:
        running = (running - t["debit"] + t["credit"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        t["balance"] = running

    return txns


# ─── PDF generation ─────────────────────────────────────────────────────

ACCOUNT_NUMBER = "1234567890"
ACCOUNT_NAME = "SUHERMAN Setiawan"
PERIOD = "01/01/2025 - 30/06/2025"
BRANCH = "KCU JAKARTA THAMRIN"
CITY = "JAKARTA"
ADDRESS = "JL. CONTOH NO. 1 RT 000 RW 000 RT000RW000"
POSTCODE = "JAKARTA 10110"
COUNTRY = "INDONESIA"
CURRENCY = "IDR"

PAGE_W, PAGE_H = A4
MARGIN_L = 25 * mm
MARGIN_T = 20 * mm
MARGIN_B = 20 * mm
LINE_H = 10
LINE_H_SM = 8
LINE_H_HDR = 11


def draw_line(c: canvas.Canvas, y: float, text: str,
              font: str = "Courier", size: int = 8) -> float:
    """Draw one line of text. Returns new y position."""
    c.setFont(font, size)
    c.drawString(MARGIN_L, y, text)
    return y - (LINE_H_SM if size == 7 else LINE_H)


def draw_page_header(c: canvas.Canvas, y: float) -> float:
    """Draw the BCA statement header block."""
    header_lines = [
        ("REKENING GIRO", "Courier-Bold", 10),
        (BRANCH, "Courier", 9),
        (ACCOUNT_NAME, "Courier", 9),
        (CITY, "Courier", 9),
        (ADDRESS, "Courier", 9),
        (POSTCODE, "Courier", 9),
        (COUNTRY, "Courier", 9),
        (f"NO. REKENING : {ACCOUNT_NUMBER}", "Courier", 9),
        ("HALAMAN :", "Courier", 9),
        (f"PERIODE : {PERIOD}", "Courier", 9),
        (f"MATA UANG : {CURRENCY}", "Courier", 9),
        ("", "Courier", 9),
        ("CATATAN:", "Courier", 7),
        ("Apabila nasabah tidak melakukan sanggahan atas Laporan Mutasi", "Courier", 7),
        ("Rekening ini sampai dengan akhir bulan berikutnya, nasabah", "Courier", 7),
        ("dianggap telah menyetujui segala data yang tercantum pada", "Courier", 7),
        ("Laporan Mutasi Rekening ini.", "Courier", 7),
        ("", "Courier", 7),
        ("TANGGAL KETERANGAN CBG MUTASI SALDO", "Courier-Bold", 8),
    ]
    for text, font, size in header_lines:
        if text:
            c.setFont(font, size)
            c.drawString(MARGIN_L, y, text)
        y -= LINE_H_HDR if size >= 9 else (LINE_H_SM if size == 7 else LINE_H)
    return y


def fmt_txn_lines(txn: dict) -> list[str]:
    """Format a transaction as text lines.

    Multi-line rows: desc on line 1, amount+label+balance on line 2.
    Single-line rows: everything concatenated.
    """
    date_str = txn["date"]
    desc = txn["description"]
    amt = txn["debit"] if txn["debit"] > 0 else txn["credit"]
    label = "DB" if txn["debit"] > 0 else "CR"
    bal = txn["balance"]

    # Use the same right-aligned format as the parser expects
    amt_str = fmt(amt)
    bal_str = fmt(bal)

    if len(desc) <= 45:
        # Single line: DD/MM description AMOUNT DB/CR BALANCE
        return [f"{date_str} {desc} {amt_str} {label} {bal_str}"]
    else:
        # Multi-line: line 1 = date + truncated desc, line 2 = closing with amount
        line1 = f"{date_str} {desc[:45]}"
        # Closing line padded to align amount after the description area
        line2 = f"{'':50}{amt_str} {label} {bal_str}"
        return [line1, line2]


def generate_pdf(transactions: list[dict]) -> Path:
    """Generate the multi-page BCA e-statement PDF."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    opening = OPENING_BALANCE
    closing = transactions[-1]["balance"] if transactions else opening
    total_credit = sum(t["credit"] for t in transactions)
    total_debit = sum(t["debit"] for t in transactions)
    n_credit = sum(1 for t in transactions if t["credit"] > 0)
    n_debit = sum(1 for t in transactions if t["debit"] > 0)

    # Page planning
    HEADER_LINES = 19
    HEADER_HEIGHT = HEADER_LINES * LINE_H_HDR + 20
    USABLE_H = PAGE_H - MARGIN_T - MARGIN_B

    # Pre-compute lines per transaction
    txn_line_lists = [fmt_txn_lines(t) for t in transactions]

    # Split into pages
    pages: list[list[int]] = []
    current_page: list[int] = []
    y_remaining = USABLE_H - HEADER_HEIGHT

    for i, lines in enumerate(txn_line_lists):
        needed = len(lines) * LINE_H
        if y_remaining < needed:
            pages.append(current_page)
            current_page = []
            y_remaining = USABLE_H - HEADER_HEIGHT
        current_page.append(i)
        y_remaining -= needed
    if current_page:
        pages.append(current_page)

    # Summary block height
    summary_height = 6 * LINE_H + 20
    last_page_used = USABLE_H - HEADER_HEIGHT
    for i in pages[-1]:
        last_page_used -= len(txn_line_lists[i]) * LINE_H
    need_summary_page = last_page_used < summary_height
    total_pages = len(pages) + (1 if need_summary_page else 0)

    c = canvas.Canvas(str(OUTPUT_PATH), pagesize=A4)

    for page_idx, page_txn_indices in enumerate(pages):
        if page_idx > 0:
            c.showPage()

        y = PAGE_H - MARGIN_T
        y = draw_page_header(c, y)

        for txn_idx in page_txn_indices:
            for line in txn_line_lists[txn_idx]:
                y = draw_line(c, y, line)

        if page_idx < len(pages) - 1:
            y -= 8
            c.setFont("Courier", 8)
            c.drawString(MARGIN_L, y, "Bersambung ke halaman berikut")

    # Summary page
    if need_summary_page:
        c.showPage()
        y = PAGE_H - MARGIN_T
        y = draw_page_header(c, y)
    else:
        y -= 14

    # Summary block
    c.setFont("Courier", 9)
    c.drawString(MARGIN_L, y, f"SALDO AWAL : {fmt(opening)}"); y -= LINE_H
    c.drawString(MARGIN_L, y, f"MUTASI CR : {fmt(total_credit)} {n_credit}"); y -= LINE_H
    c.drawString(MARGIN_L, y, f"MUTASI DB : {fmt(total_debit)} {n_debit}"); y -= LINE_H
    c.drawString(MARGIN_L, y, f"SALDO AKHIR : {fmt(closing)}"); y -= LINE_H

    c.save()
    return OUTPUT_PATH


def main():
    print("Generating synthetic BCA e-statement...")
    transactions = generate_transactions()
    print(f"  {len(transactions)} transactions over 6 months")

    total_credit = sum(t["credit"] for t in transactions)
    total_debit = sum(t["debit"] for t in transactions)
    closing = transactions[-1]["balance"]

    print(f"  Opening balance:  Rp {fmt(OPENING_BALANCE)}")
    print(f"  Total credits:    Rp {fmt(total_credit)} ({sum(1 for t in transactions if t['credit'] > 0)} txns)")
    print(f"  Total debits:     Rp {fmt(total_debit)} ({sum(1 for t in transactions if t['debit'] > 0)} txns)")
    print(f"  Closing balance:  Rp {fmt(closing)}")

    pdf_path = generate_pdf(transactions)
    print(f"\n  PDF generated: {pdf_path}")
    print(f"  File size: {pdf_path.stat().st_size:,} bytes")
    return pdf_path


if __name__ == "__main__":
    main()
