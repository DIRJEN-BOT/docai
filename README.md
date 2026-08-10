# DocAI — Indonesian Bank E-Statement Parser

[![CI](https://github.com/oyi77/docai/actions/workflows/ci.yml/badge.svg)](https://github.com/oyi77/docai/actions/workflows/ci.yml)

Extract structured transaction data from Indonesian bank e-statement PDFs (BCA, Mandiri, BNI, BRI) into clean JSON/CSV.

**Target users:** Accountants, bookkeepers, fintech developers working with Indonesian financial documents.

## Features

- Parse BCA e-statement PDFs → structured `Transaction` objects
- **Balance-check validation** — every parsed result is verified; mismatches are rejected
- Handles BCA quirks: DOB-locked PDFs (clear error), "DB"/"CR" label convention, both number conventions — synthetic fixtures (`1.234.567,89`) and the real BCA e-statement style (`54,291,427.59`)
- Deterministic, zero-API-cost parsing — no LLM calls for known formats
- MIT licensed, open source

## Quickstart

```bash
# Install
pip install -e ".[dev]"

# Python usage
from docai.parsers.bca import BCAParser
from docai.validation import validate_balance

parser = BCAParser()
result = parser.parse("my_statement.pdf")
validate_balance(result)  # raises ValidationError if balance mismatch

for txn in result.transactions:
    print(f"{txn.date}  {txn.description:40s}  Dr {txn.debit:>15}  Cr {txn.credit:>15}  Bal {txn.balance:>15}")
```

## CLI

```bash
docai parse --bank bca statement.pdf
# → JSON output to stdout
```

## REST API (lokal / self-host)

```bash
# Jalankan server (dev):
python -m docai.api            # atau: uvicorn docai.api:app --port 8000

# Health check:
curl http://localhost:8000/health
# → {"status":"ok","banks":["bca"]}

# Parse PDF → JSON:
curl -X POST http://localhost:8000/parse \
     -F "file=@statement.pdf" \
     -F "bank=bca"

# Parse PDF → CSV:
curl -X POST "http://localhost:8000/parse?format=csv" \
     -F "file=@statement.pdf" -F "bank=bca"

# Demo halaman (upload → parse → CSV): buka http://localhost:8000/
# Dokumentasi interaktif (Swagger): buka http://localhost:8000/docs
```

**Catatan respons:**
- Balance-check mismatch **bukan error** — hasil parse tetap 200 dengan `balance_check: "failed"` + `validation_error`, karena itu output yang sah untuk audit.
- Error API dikembalikan sebagai `{"error": <code>, "message": <teks>}`; kode: `password_protected`, `parse_error`, `invalid_request`, `validation_error`.

## Project Structure

```
docai/
├── src/docai/
│   ├── models.py          # Transaction dataclass, ParseResult
│   ├── base.py            # BaseParser ABC, ParseError hierarchy
│   ├── validation.py      # Balance-check validator
│   ├── serialization.py   # JSON/CSV serialization (shared CLI + API)
│   ├── api.py             # FastAPI wrapper (JSON + CSV + demo page)
│   ├── utils.py           # Indonesian number parsing, text cleanup
│   └── parsers/
│       ├── bca.py         # BCA e-statement parser
│       └── registry.py    # Bank → parser registry
├── tests/
│   ├── test_parsers.py    # Parser integration tests
│   ├── test_validation.py # Validation unit tests
│   ├── test_api.py        # FastAPI endpoint tests
│   └── generate_fixtures.py
├── docs/
│   └── index.html         # Landing page v1
├── web/
│   └── index.html         # Demo interaktif (di-serve API di GET /)
├── pyproject.toml
└── README.md
```

## Benchmark (placeholder)

| Metric | BCA | Mandiri | BNI | BRI |
|--------|-----|---------|-----|-----|
| Field accuracy | ~95% TODO | — | — | — |
| COGS per doc | ~Rp0 (deterministic) | — | — | — |
| Balance-check pass | 100% (fixtures + real samples) | — | — | — |

> Verified against real BCA e-statement PDFs (Okt 2025, Apr 2026, Mei 2026): all parsed
> totals match the bank's own `MUTASI CR/DB` summary and balance-check passes.
> Deliberately modified/corrupted files are correctly rejected as mismatches.

## Supported Banks

| Bank | Status | Parser |
|------|--------|--------|
| BCA | ✅ Implemented | `docai.parsers.bca.BCAParser` |
| Mandiri | 🔜 Week 2–3 | — |
| BNI | 🔜 Week 2–3 | — |
| BRI | 🔜 Week 2–3 | — |

## Roadmap

- **Week 1:** BCA parser + tests + landing page ✅
- **Week 2:** FastAPI wrapper ✅ + CSV export ✅ + demo page ✅ · RapidAPI listing · Mandiri/BNI/BRI parsers
- **Week 3:** Balance-check hardening + KTP/NPWP extraction
- **Week 4:** Billing + SEO pages + accountant beta launch

## Need Production / API?

The open-source parser covers the happy path. For production use:

- **REST API** with auth, rate limiting, and 99.9% uptime → [docai.id](https://docai.id) *(coming soon)*
- **Batch processing** for accounting firms (1000+ docs/month)
- **Accounting software integration** (Jurnal, Accurate, Kledo templates)

→ [Contact us](mailto:hello@docai.id) for enterprise pricing.

## License

MIT — see [LICENSE](LICENSE).
