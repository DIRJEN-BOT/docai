# DocAI — Indonesian Bank E-Statement Parser

[![CI](https://github.com/oyi77/docai/actions/workflows/ci.yml/badge.svg)](https://github.com/oyi77/docai/actions/workflows/ci.yml)
[![Site](https://img.shields.io/badge/site-oyi77.is--a.dev%2Fdocai-blue)](https://oyi77.is-a.dev/docai/)

Extract structured transaction data from Indonesian bank e-statement PDFs (BCA, Mandiri, BNI, BRI) into clean JSON/CSV.

**Target users:** Accountants, bookkeepers, fintech developers working with Indonesian financial documents.

## Features

- Parse BCA e-statement PDFs → structured `Transaction` objects
- **Balance-check validation** — every parsed result is verified; mismatches are rejected
- **Row-level running-balance validation** — each transaction's printed balance is checked against opening + net amounts, catching misparses that a closing-balance-only check would miss
- **Date normalization** — bare `DD/MM` dates in real BCA statements get the year from the statement period (`02/01` → `02/01/2026`), ready for accounting imports
- **Batch parsing + CSV export on the CLI** — `docai parse a.pdf b.pdf --format csv` for pipeline use
- Handles BCA quirks: DOB-locked PDFs (clear error), "DB"/"CR" label convention, both number conventions — synthetic fixtures (`1.234.567,89`) and the real BCA e-statement style (`54,291,427.59`)
- Deterministic, zero-API-cost parsing — no LLM calls for known formats
- MIT licensed, open source

## Quickstart

```bash
# Install
pip install -e ".[dev]"

# Python usage
from docai import BCAParser, validate_statement

result = BCAParser().parse("my_statement.pdf")
validate_statement(result)  # full suite: balance + amounts + running balances

for txn in result.transactions:
    print(f"{txn.date}  {txn.description:40s}  Dr {txn.debit:>15}  Cr {txn.credit:>15}  Bal {txn.balance:>15}")
```

`validate_statement` runs the full validation pass (aggregate balance check → non-negative amounts → per-row running balances). Individual checks are also exported: `validate_balance`, `validate_debit_credit_non_negative`, `validate_running_balances`.

## CLI

```bash
# Satu file → JSON ke stdout
docai parse --bank bca statement.pdf

# Banyak file → array JSON [{"file": ..., "result": ...}]
docai parse --bank bca jan.pdf feb.pdf mar.pdf

# Ekspor CSV (semicolon; header: tanggal;keterangan;debit;kredit;saldo)
docai parse --bank bca statement.pdf --format csv

# Batch CSV — tiap blok diawali komentar "# file: <path>"
docai parse --bank bca jan.pdf feb.pdf --format csv > mutasi.csv

# Skip validasi (hanya parse)
docai parse --bank bca statement.pdf --no-validate

# Ganti bank / daftar bank didukung
docai banks
```

Exit code 0 = semua file ter-parse **dan** lolos validasi; non-zero = ada yang gagal parse atau gagal validation (detail di stderr) — aman dipakai di pipeline.

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
│   ├── validation.py      # Balance + running-balance validators
│   ├── serialization.py   # JSON/CSV serialization (shared CLI + API)
│   ├── api.py             # FastAPI wrapper (JSON + CSV + demo page)
│   ├── utils.py           # Indonesian number parsing, text cleanup
│   └── parsers/
│       ├── bca.py         # BCA e-statement parser
│       └── registry.py    # Bank → parser registry
├── tests/
│   ├── test_parsers.py    # Parser integration tests
│   ├── test_validation.py # Validation unit tests
│   ├── test_cli.py        # CLI end-to-end tests (batch/CSV/errors)
│   ├── test_api.py        # FastAPI endpoint tests
│   └── generate_fixtures.py
├── docs/
│   └── index.html         # Landing page v1
├── web/
│   └── index.html         # Demo interaktif (di-serve API di GET /)
├── pyproject.toml
└── README.md
```

## Benchmark (terukur)

| Metric | BCA | Mandiri | BNI | BRI |
|--------|-----|---------|-----|-----|
| Field accuracy | ~100% (3 statement asli + 5 fixture) | — | — | — |
| COGS per doc | ~Rp0 (deterministic) | — | — | — |
| Balance-check pass | 100% (3 asli + 6 fixture pass; file korup ditolak) | — | — | — |
| Latency per doc | ~30–150 ms (pypdf) | — | — | — |

> Verified against real BCA e-statement PDFs (Okt 2025: 50 txn, Apr 2026: 11 txn,
> Mei 2026: 8 txn): all parsed totals match the bank's own `MUTASI CR/DB` summary
> and balance-check passes. Deliberately modified/corrupted files are correctly
> rejected as mismatches. Latency measured locally on the real statements.

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
- **Week 3:** Balance-check hardening ✅ (row-level running balances, batch CLI, date normalization) · KTP/NPWP extraction
- **Week 4:** Billing + SEO pages + accountant beta launch

## Need Production / API?

The open-source parser covers the happy path. For production use:

- **REST API** with auth, rate limiting, and 99.9% uptime → [docai.id](https://docai.id) *(coming soon)*
- **Batch processing** for accounting firms (1000+ docs/month)
- **Accounting software integration** (Jurnal, Accurate, Kledo templates)

→ [Contact us](mailto:hello@docai.id) for enterprise pricing.

## License

MIT — see [LICENSE](LICENSE).
