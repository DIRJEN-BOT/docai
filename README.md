# DocAI Verify — Income Verification API for Indonesian Fintech

[![CI](https://github.com/oyi77/docai/actions/workflows/ci.yml/badge.svg)](https://github.com/oyi77/docai/actions/workflows/ci.yml)
[![Site](https://img.shields.io/badge/site-docaiid.pythonanywhere.com-blue)](https://docaiid.pythonanywhere.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Parse bank e-statement PDFs → structured income data + verification score.
Deterministic (zero LLM cost), 30–150ms, BCA + Mandiri live.

## What It Does

POST a borrower's bank statement PDF → get:

- **Structured transaction data** — date, description, debit, credit, balance
- **Monthly income estimate** with salary detection (keyword + round-number heuristics)
- **Income consistency score** (0–100) — coefficient of variation across months
- **Fraud signals** — balance mismatch, suspicious patterns, short statements
- **Overall verification score** (0–100) — composite of parsing validity, consistency, and fraud checks

Zero LLM cost. Pure deterministic parsing + scoring. 30–150ms per document.

## Quick Start

### API (Live)

```bash
# Verify income from a BCA statement
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@statement.pdf" \
  -F "bank=bca"

# Response:
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

### Python

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
print(f"Score: {report.verification_score}, Income: Rp{report.detected_monthly_income:,.0f}/mo")
```

### CLI

```bash
# Parse to JSON
docai parse --bank bca statement.pdf
docai parse --bank mandiri statement.pdf

# Parse to CSV
docai parse --bank mandiri statement.pdf --format csv

# List supported banks
docai banks
```

## Supported Banks

| Bank | Status | Format |
|------|--------|--------|
| BCA | ✅ Live | Native e-statement (multi-page, DOB-locked) |
| Mandiri | ✅ Live | Modern Livin' (2023+, bilingual, sign-based) |
| BNI | 🔜 Coming Soon | Modern Wondr + legacy |
| BRI | 🔜 Coming Soon | Rekening koran + BRImo |

## API Reference

All endpoints require an `X-API-Key` header except `/health` and `/docs`.

### `POST /verify-income`

Main endpoint. Parses a bank statement and returns an income verification report.

- **Body:** `multipart/form-data` — `file` (PDF), `bank` (string), `password` (optional)
- **Auth:** `X-API-Key` header
- **Response:** `IncomeReport` JSON — verification score, monthly income estimate, consistency score, fraud flags, balance validity

```bash
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@statement.pdf" \
  -F "bank=mandiri"
```

### `POST /parse`

Parse a bank statement to structured transactions.

- **Body:** `multipart/form-data` — `file` (PDF), `bank` (string), `password` (optional)
- **Auth:** `X-API-Key` header
- **Response:** `ParseResult` JSON (or CSV with `?format=csv`)

```bash
curl -X POST https://docaiid.pythonanywhere.com/parse \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

### `GET /health`

Health check. Returns `{"status": "ok", "banks": ["bca", "mandiri"]}`. No auth required.

### Interactive Docs

When running locally (`python -m docai.api`), visit **http://localhost:8000/docs** for the Swagger UI with try-it-out support.

## Authentication

All API requests (except `/health`) require an `X-API-Key` header:

```bash
-H "X-API-Key: docai-dev-key-12345"
```

| Key | Tier | Limit |
|-----|------|-------|
| `docai-dev-key-12345` | Free | 100 verifications/month |

Keys are issued per-tier. Contact [hello@docai.id](mailto:hello@docai.id) for production keys.

## Pricing

| Tier | Price | Verifications/Month |
|------|-------|---------------------|
| **Free** | Rp 0 | 100 |
| **Starter** | Rp 500,000/bulan (~$30) | 500 |
| **Growth** | Rp 5,000,000/bulan (~$300) | 5,000 |
| **Scale** | Rp 30,000,000/bulan (~$1,800) | 50,000 |
| **Enterprise** | Custom | Unlimited |

All tiers include: full API access (parse + verify-income), dashboard usage stats, WhatsApp/email support, SLA 99.9% uptime, response time < 500ms.

Annual billing: 20% discount. See [outreach/pricing.md](outreach/pricing.md) for detailed ROI calculations and competitor comparison.

## Architecture

```
docai/
├── src/docai/
│   ├── models.py              # Transaction dataclass, ParseResult
│   ├── base.py                # BaseParser ABC, ParseError hierarchy
│   ├── scoring.py             # IncomeReport, analyze_income(), fraud detection
│   ├── validation.py          # Balance + running-balance validators
│   ├── serialization.py       # JSON/CSV serialization (shared CLI + API)
│   ├── api.py                 # FastAPI: /parse, /verify-income, /health
│   ├── cli.py                 # CLI: docai parse, docai banks
│   ├── pa_wsgi.py             # PythonAnywhere WSGI entry point
│   ├── utils.py               # Indonesian number parsing, text cleanup
│   └── parsers/
│       ├── bca.py             # BCA e-statement parser
│       ├── mandiri.py         # Mandiri Livin' e-statement parser (2023+)
│       └── registry.py        # Bank → parser registry
├── tests/
│   ├── test_parsers.py        # Parser integration tests (BCA + Mandiri)
│   ├── test_scoring.py        # Scoring engine unit tests
│   ├── test_validation.py     # Validation unit tests
│   ├── test_cli.py            # CLI end-to-end tests (batch/CSV/errors)
│   ├── test_api.py            # FastAPI endpoint tests
│   ├── test_api_enhanced.py   # Enhanced API tests (auth, /verify-income)
│   ├── test_mandiri_parser.py # Mandiri parser tests
│   ├── fixtures/              # Synthetic + real PDF fixtures
│   └── generate_fixtures.py
├── outreach/
│   ├── pricing.md             # Pricing tiers + ROI analysis
│   ├── buyer-list.md          # Target customer segments
│   ├── pilot-offer.md         # Pilot program details
│   └── cold-outreach-templates.md
├── docs/
│   ├── index.html             # Landing page
│   └── bank-formats-research.md
├── web/
│   └── index.html             # Interactive demo page
├── deploy/
│   ├── pythonanywhere/        # PythonAnywhere deploy config
│   ├── cloudflared/           # Cloudflare tunnel setup
│   └── hf-space/              # HuggingFace Spaces config
├── scripts/
│   └── generate_promo_banners.py
├── api/
│   └── index.py               # Vercel serverless entry point
├── pyproject.toml
├── vercel.json
├── requirements.txt
└── LICENSE
```

## Benchmark

| Metric | BCA | Mandiri | BNI | BRI |
|--------|-----|---------|-----|-----|
| Field accuracy | ~100% (3 real statements + 5 fixtures) | ~100% (limited test data) | — | — |
| COGS per doc | ~Rp 0 (deterministic) | ~Rp 0 (deterministic) | — | — |
| Balance-check pass | 100% (3 real + 6 fixtures; corrupted files rejected) | 100% (test set) | — | — |
| Latency per doc | ~30–150ms (pypdf) | ~50–200ms (pypdf) | — | — |

> **BCA:** Verified against real e-statement PDFs (Oct 2025: 50 txn, Apr 2026: 11 txn,
> May 2026: 8 txn): all parsed totals match the bank's own `MUTASI CR/DB` summary
> and balance-check passes. Deliberately modified/corrupted files are correctly
> rejected as mismatches. Latency measured locally on real statements.

> **Mandiri:** Verified against modern Livin' format e-statements (2023+). Parser
> handles bilingual headers, sign-based amounts (+/−), and pipe-separated line
> format. Limited test data — more real statements welcome for validation.

## For Developers

### Install

```bash
pip install -e ".[dev]"
```

### Run Locally

```bash
# Start the API server
python -m docai.api    # or: uvicorn docai.api:app --port 8000

# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
# Demo page at http://localhost:8000/
```

### Run Tests

```bash
pytest tests -q
```

### Project Conventions

- **Deterministic only** — no LLM calls in the parser or scoring pipeline
- **Balance validation** — every parse result is verified (aggregate + row-level running balances)
- **Indonesian number format** — `1.234.567,89` (dot thousands, comma decimal)
- **Frozen dataclasses** — `Transaction` is immutable; use `object.__setattr__` for Decimal coercion

### Contributing

1. Fork → branch → PR
2. Add tests for any new parser or scoring logic
3. Run `pytest tests -q` before submitting
4. Keep it deterministic — no API calls in core parsing

## License

MIT — see [LICENSE](LICENSE).
