---
title: "I Built a Bank Statement Parser for Indonesian Fintech — No LLM, No OCR, 150ms"
published: true
tags: python, api, fintech, indonesia, open source
description: "Parse BCA & Mandiri bank statement PDFs into structured income data with fraud detection. Deterministic, zero LLM cost, 120 tests."
canonical_url: https://medium.com/@yourusername/docai-verify-indonesian-fintech
cover_image: https://raw.githubusercontent.com/DIRJEN-BOT/docai/main/assets/promo/docai_banner_linkedin.png
---

# I Built a Bank Statement Parser for Indonesian Fintech — No LLM, No OCR, 150ms

*Parsing bank statement PDFs without OCR, without LLMs, and without breaking the bank.*

---

## The Problem: Manual Income Verification Is a Bottleneck

Indonesia's peer-to-peer lending market processes millions of loan applications every month.

Before disbursing funds, lenders need to verify that the applicant actually earns what they claim. The traditional approach? A human underwriter opens a bank statement PDF, scrolls through pages of transactions, mentally tallies salary deposits, and makes a judgment call.

**This process is slow, subjective, and fraud-prone.**

The digital alternatives aren't much better. Account-aggregation services like Brick and Ayoconnect let borrowers link their bank accounts directly — eliminating the PDF entirely. But this approach has its own problems: it requires the borrower to authenticate through their banking app, many users drop off during the linking flow, and not all banks support the integration.

For BCA — Indonesia's largest private bank — account aggregation coverage is incomplete, and the user experience is clunky.

**What if you could get the same structured data from the PDF itself, deterministically, in under 150 milliseconds, with zero per-document cost?**

That's what we built with **DocAI Verify**.

## What DocAI Verify Does

DocAI Verify is an income verification API that takes a bank e-statement PDF as input and produces a structured income verification report as output.

**No LLM calls. No OCR engine. No machine learning models. Pure regex, number parsing, and statistical analysis.**

Here's the quickstart:

```bash
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

Response:

```json
{
  "verification_score": 82,
  "confidence": "high",
  "detected_monthly_income": 12500000,
  "income_source": "salary",
  "consistency_score": 95,
  "balance_valid": true,
  "fraud_flags": []
}
```

The score of 82 with `"high"` confidence tells the lender: this applicant has a stable salary of approximately Rp 12.5 million/month, consistent across 6 months, with no fraud signals and a valid balance reconciliation.

## The Architecture: Two Layers

The system has two layers:

1. **Bank-specific parsers** — Extract structured transaction data from BCA and Mandiri e-statement PDFs
2. **Scoring engine** — Analyze the transaction data to produce a composite verification score (0–100)

The entire pipeline runs in **30–150ms per document** on commodity hardware. The cost per verification is effectively zero — no API calls to third-party services, no GPU inference, no token fees.

```python
from docai.parsers import get_parser
from docai.scoring import analyze_income
from docai.validation import validate_statement

# Parse
result = get_parser("bca").parse("statement.pdf")

# Validate
validate_statement(result)

# Score
report = analyze_income(result)
print(f"Score: {report.verification_score}")
print(f"Income: Rp{report.detected_monthly_income:,.0f}/mo")
```

## Why Deterministic Beats LLM for This Use Case

When we started, the obvious approach was to feed the PDF to GPT-4 or Claude with a structured prompt. It would "understand" the document, extract the data, and return JSON.

But we found three critical problems:

### 1. Consistency

The same document processed twice could produce different field extractions. Transaction amounts might be off by rounding. Dates might be reformatted.

**For a financial verification system, "usually correct" isn't good enough.**

Our deterministic parser produces byte-identical output for the same input, every time.

### 2. Cost

At scale, LLM token costs add up fast:

| Approach | Cost per doc | 100K docs/month |
|----------|-------------|-----------------|
| GPT-4o | ~$0.03 | ~$3,000 |
| Claude Sonnet | ~$0.02 | ~$2,000 |
| **DocAI Verify** | **~Rp0** | **~Rp0** |

For an API that needs to sit inside a loan decisioning pipeline, that cost difference is the difference between viable and not.

### 3. Latency

LLM API calls take 2–10 seconds. Our deterministic parser finishes in 30–150ms.

**That's a 20–60x speedup.**

## How the Parsers Work

### BCA E-Statements

BCA statements come in a native format with some quirks:

**Balance-based debit/credit detection.** When DB/CR labels are missing (common in multi-page statements), the parser compares running balances:

```python
if current_balance > previous_balance:
    transaction = CREDIT
    credit_amount = current_balance - previous_balance
elif current_balance < previous_balance:
    transaction = DEBIT
    debit_amount = previous_balance - current_balance
```

This approach is robust because BCA statements always include a running balance column. Even when extraction mangles the amount labels, the balance progression tells the truth.

**Multi-page handling.** Real BCA statements span multiple pages. The parser concatenates all page text, normalizes dates, and processes the full transaction stream as a single sequence.

### Mandiri Livin' Statements

Mandiri's modern format (2023+) is quite different:

- **Bilingual headers** — "Tanggal/Date", "Keterangan/Remarks"
- **Sign-based amounts** — `+12,500,000` for credits, `-3,200,000` for debits
- **Pipe-separated format** — `No | Date | Time | Description | Amount | Balance`
- **Indonesian number formatting** — dots for thousands, comma for decimal (`1.234.567,89`)

## The Scoring Algorithm

Once transactions are extracted, the scoring engine analyzes four dimensions:

### 1. Salary Detection

Two-pass approach:

- **Pass 1 — Keyword matching:** Scans for `gaji`, `payroll`, `upah`, `THP`, `salary`
- **Pass 2 — Recurring amount analysis:** Same credit amount in 3+ distinct months → classified as salary

The monthly income estimate is the **median** of per-month totals — robust against outlier months.

### 2. Consistency Scoring

Uses **coefficient of variation (CV)** across months:

```python
CV = std_dev(monthly_incomes) / mean(monthly_incomes)
```

| CV Range | Score | Interpretation |
|----------|-------|----------------|
| < 0.10 | 90–100 | Very stable |
| 0.10–0.20 | 70–89 | Mostly stable |
| 0.20–0.40 | 40–69 | Variable |
| > 0.40 | 0–39 | Highly irregular |

### 3. Fraud Detection

Flags anomalous patterns:

- **Balance mismatch** — computed closing balance ≠ declared closing balance
- **Round-number concentration** — >30% of transactions are multiples of IDR 100K
- **Duplicate transactions** — same date + description + amount
- **High balance relative to income** — closing balance > 24 months of income
- **Short statement periods** — < 3 months of data

### 4. Composite Score

| Component | Weight | Points |
|-----------|--------|--------|
| Balance validation | 25% | 0 or 25 |
| Income source detected | 25% | 5–25 |
| Consistency score | 30% | 0–30 |
| No fraud flags | 20% | 0–20 |

Maps to confidence: **80–100** = high, **50–79** = medium, **0–49** = low.

## Results

After building the full pipeline:

- **120 tests passing** — parsers, scoring, validation, CLI, API
- **BCA parser: 100% accuracy** — verified against 3 real e-statement PDFs
- **Balance-check pass rate: 100%** — 3-tier validation catches corrupted files
- **Zero fraud false positives** on clean statements

## Try It

DocAI Verify is live and free to try:

- **100 verifications/month** — no credit card required
- **API:** [docaiid.pythonanywhere.com](https://docaiid.pythonanywhere.com)
- **Source code:** [github.com/DIRJEN-BOT/docai](https://github.com/DIRJEN-BOT/docai) (MIT licensed)
- **Postman collection:** Import `docs/postman-collection.json` from the repo

```bash
# Quick test
curl -X GET https://docaiid.pythonanywhere.com/health
# → {"status": "ok", "banks": ["bca", "mandiri"]}
```

## What's Next

- **BNI and BRI parsers** — Indonesia's two largest state-owned banks
- **Batch processing** — Multiple statements in one request
- **Webhook support** — Push results to your system
- **On-premise deployment** — Docker image for data-sensitive lenders

---

*DocAI Verify — Income verification for Indonesian fintech. Deterministic. Fast. Free to start.*

*Originally published on [Medium](https://medium.com/@yourusername/docai-verify-indonesian-fintech).*
