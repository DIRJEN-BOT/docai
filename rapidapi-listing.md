# RapidAPI Listing — DocAI Indonesian Bank Statement Parser

Copy-paste ready for RapidAPI provider portal.

---

## API Name

**DocAI — Indonesian Bank Statement Parser**

## Tagline

Parse BCA/Mandiri/BNI/BRI e-statement PDFs into structured JSON — zero LLM cost, deterministic, with built-in balance validation.

## Categories

- Finance / Banking
- Data Extraction / OCR
- Accounting

## Search Tags

`bca`, `e-statement`, `mutasi bank`, `rekening koran`, `bank statement parser`, `indonesia`, `ocr`, `accounting`, `jurnal`, `accurate`, `kledo`, `csv export`

---

## Endpoints

### POST /v1/statements/parse

Parse a bank e-statement PDF and return structured transaction rows.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file), `bank` (string: "bca" | "mandiri" | "bni" | "bri")

**Response (200):**
```json
{
  "bank": "bca",
  "account_number": "1234567890",
  "account_name": "BUDI SETIAWAN",
  "statement_period": "01/01/2026 - 31/01/2026",
  "opening_balance": 1000000.00,
  "closing_balance": 5225000.00,
  "currency": "IDR",
  "transactions": [
    {
      "date": "02/01/2026",
      "description": "TRSF E-BANKING BCA",
      "debit": 0.00,
      "credit": 500000.00,
      "balance": 1500000.00
    },
    {
      "date": "03/01/2026",
      "description": "ATM WD BCA KCP THAMRIN",
      "debit": 250000.00,
      "credit": 0.00,
      "balance": 1250000.00
    }
  ],
  "balance_check": "passed",
  "total_debit": 1525000.00,
  "total_credit": 5750000.00
}
```
*(transactions truncated for brevity — the real response includes all 8 rows; totals above match the full statement: opening 1.000.000 + credit 5.750.000 − debit 1.525.000 = closing 5.225.000)*

**Balance mismatch (200, not an error):** the parse succeeded, so the API returns
`200` with `"balance_check": "failed"` and a `validation_error` field. Mismatches
are data, not failures — clients can audit the statement instead of treating it
as a hard error.

**CSV output:** add `?format=csv` to the request → returns `text/csv`
(semicolon-delimited, header `tanggal;keterangan;debit;kredit;saldo`).

**Error (400):**
```json
{
  "error": "password_protected",
  "message": "This BCA statement PDF is password-protected (likely locked with date of birth: DDMMYYYY format). ..."
}
```
Error codes: `password_protected`, `parse_error` (unreadable/corrupt PDF),
`invalid_request` (unknown bank), `validation_error` (422, bad request shape).

### GET /v1/statements/supported-banks

List supported banks and parser versions.

**Response (200):**
```json
{
  "banks": [
    { "id": "bca", "name": "Bank Central Asia", "parser_version": "0.1.0", "status": "stable" },
    { "id": "mandiri", "name": "Bank Mandiri", "parser_version": null, "status": "coming_soon" }
  ]
}
```

---

## Pricing Tiers

| Tier | Price | Docs/Month | Features |
|------|-------|-----------|----------|
| Free | $0 | 20 | Basic parsing, JSON output, watermark |
| Starter | $6.9/mo | 500 | All Free + CSV export, no watermark, email support |
| Pro | $19.9/mo | 5,000 | All Starter + batch upload, KTP/NPWP extraction, Jurnal/Accurate templates |
| Enterprise | Custom | Unlimited | SLA, on-prem, custom bank formats, dedicated support |

## Free Tier Details

- 20 documents per month
- BCA parser only (Mandiri/BNI/BRI in Starter+)
- JSON output only (CSV in Starter+)
- Rate limit: 5 requests/minute
- Watermarked output (removable in paid tiers)

## Description (Markdown for listing page)

```
# DocAI — Indonesian Bank Statement Parser

Parse BCA (and soon Mandiri/BNI/BRI) e-statement PDFs into structured, machine-readable JSON with **zero API cost per document**.

## Why DocAI?

- **Deterministic parsing** — no LLM calls, no per-token fees, COGS ~Rp0/doc
- **Balance-check built in** — every result is validated; mismatches rejected with clear error
- **Indonesian-aware** — handles "DB"/"CR" labels, `1.234.567,89` formatting, DOB-locked PDFs
- **Accountant-ready output** — fields mapped for Jurnal, Accurate, Kledo import

## Quick Start

```python
import requests

response = requests.post(
    "https://docai-id.p.rapidapi.com/v1/statements/parse",
    files={"file": open("statement.pdf", "rb")},
    data={"bank": "bca"},
    headers={"X-RapidAPI-Key": "YOUR_KEY"}
)
print(response.json())
```

## Use Cases

- Accounting firms: batch-parse client bank statements for reconciliation
- Fintech: extract transaction data for credit scoring, cash-flow analysis
- Bookkeeping SaaS: auto-import bank transactions into accounting software
- Developers: build financial dashboards on top of structured bank data

## Limitations (Free Tier)

- 20 docs/month, BCA only, JSON only
- No batch processing (Pro tier)
- Rate limited to 5 req/min

## Links

- GitHub: https://github.com/oyi77/docai (MIT licensed)
- Docs: https://docai.id/docs
- Support: hello@docai.id
```

## API Contact

- **Email:** hello@docai.id
- **Website:** https://docai.id
- **GitHub:** https://github.com/oyi77/docai
