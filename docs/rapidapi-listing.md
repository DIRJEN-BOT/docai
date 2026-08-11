# RapidAPI Listing — DocAI Verify

Copy-paste ready for the RapidAPI provider portal.

---

## Title

**DocAI Verify — Income Verification API**

## Tagline

Parse Indonesian bank e-statement PDFs → income verification score, salary detection, fraud signals. Zero LLM cost, 30–150ms.

## Categories

- Finance / Banking
- Data Extraction / OCR
- Accounting

## Search Tags

`bca`, `mandiri`, `e-statement`, `mutasi bank`, `rekening koran`, `bank statement parser`, `indonesia`, `ocr`, `accounting`, `income verification`, `credit scoring`, `fraud detection`, `jurnal`, `accurate`, `kledo`

## Description (Markdown for listing page)

DocAI Verify is an income verification API purpose-built for Indonesian fintech lenders.

Upload a borrower's bank statement PDF (BCA or Mandiri), and get:

- ✅ Structured transaction data (date, description, debit, credit, balance)
- ✅ Monthly income estimate with salary detection
- ✅ Income consistency score (0–100)
- ✅ Fraud signals (balance mismatch, suspicious patterns, round-number anomalies)
- ✅ Overall verification score (0–100)

### Why DocAI Verify?

- **Deterministic** — no LLM calls, so results are consistent and COGS ~Rp0/doc
- **Indonesia-first** — built for BCA and Mandiri e-statement formats
- **Balance validation** — every result is verified against the bank's own balance
- **Fast** — 30–150ms response time
- **Privacy-first** — stateless processing, no data stored

### Perfect for

- P2P lending income verification
- BNPL credit limit decisions
- Mortgage (KPR) application processing
- Tenant screening
- Any use case requiring structured bank transaction data

Try the free tier: 100 verifications/month at no cost.

## Endpoints

### POST /verify-income

**Description:** Verify income from a bank statement PDF.

**Parameters (multipart/form-data):**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file` | file | ✅ | — | Bank statement PDF |
| `bank` | string | ❌ | `"bca"` | Bank identifier: `bca` or `mandiri` |
| `password` | string | ❌ | `null` | PDF password (DOB in DDMMYYYY format for BCA) |

**Request Header:**

| Header | Required | Description |
|--------|----------|-------------|
| `X-API-Key` | ✅ | Your RapidAPI key |

**Response (200):** `IncomeReport` JSON — see [Data Models](#data-models) section below.

**Sample Request:**

```bash
curl -X POST "https://docaiid.pythonanywhere.com/verify-income" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

**Sample Response:**

```json
{
  "verification_score": 82,
  "confidence": "high",
  "detected_monthly_income": 12500000.0,
  "income_source": "salary",
  "salary_months_detected": 6,
  "monthly_incomes": [
    {"month": "2025-01", "amount": 12500000.0, "source": "salary"},
    {"month": "2025-02", "amount": 12500000.0, "source": "salary"}
  ],
  "consistency_score": 95,
  "income_cv": 0.02,
  "has_gaps": false,
  "gap_months": [],
  "fraud_flags": [],
  "balance_valid": true,
  "has_suspicious_patterns": false,
  "statement_period": "01 Jan 2025 - 30 Jun 2025",
  "total_months_covered": 6,
  "total_transactions": 186,
  "total_credit": 75500000.0,
  "total_debit": 52300000.0,
  "bank": "bca",
  "account_number": "1234567890"
}
```

---

### POST /parse

**Description:** Parse a bank statement PDF into structured transaction data.

**Parameters (multipart/form-data):**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file` | file | ✅ | — | Bank statement PDF |
| `bank` | string | ❌ | `"bca"` | Bank identifier: `bca` or `mandiri` |
| `password` | string | ❌ | `null` | PDF password (DOB in DDMMYYYY format for BCA) |

**Query Parameter:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `format` | string | `"json"` | Output format: `json` or `csv` |

**Request Header:**

| Header | Required | Description |
|--------|----------|-------------|
| `X-API-Key` | ✅ | Your RapidAPI key |

**Response (200):** `ParseResult` JSON (or CSV when `?format=csv`).

**Sample Request:**

```bash
curl -X POST "https://docaiid.pythonanywhere.com/parse?format=json" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

**Sample Response:**

```json
{
  "bank": "bca",
  "account_number": "1234567890",
  "account_name": "BUDI SETIAWAN",
  "statement_period": "01/01/2025 - 31/01/2025",
  "opening_balance": 1000000.00,
  "closing_balance": 5225000.00,
  "currency": "IDR",
  "total_debit": 1525000.00,
  "total_credit": 5750000.00,
  "balance_check": "passed",
  "transactions": [
    {
      "date": "02/01/2025",
      "description": "TRSF E-BANKING BCA",
      "debit": 0.00,
      "credit": 500000.00,
      "balance": 1500000.00,
      "reference": ""
    },
    {
      "date": "03/01/2025",
      "description": "ATM WD BCA KCP THAMRIN",
      "debit": 250000.00,
      "credit": 0.00,
      "balance": 1250000.00,
      "reference": ""
    }
  ]
}
```

---

### GET /health

**Description:** Health check. Returns status and list of supported banks.

**Authentication:** None required.

**Response (200):**

```json
{
  "status": "ok",
  "banks": ["bca", "mandiri"]
}
```

---

## Pricing Tiers

| Plan | Price | Quota |
|------|-------|-------|
| Free | $0/month | 100 requests/month |
| Basic | $9.99/month | 1,000 requests/month |
| Pro | $49.99/month | 10,000 requests/month |
| Business | $199.99/month | 100,000 requests/month |

## Sample cURL Request

```bash
curl -X POST "https://docai.p.rapidapi.com/verify-income" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "X-RapidAPI-Host: docai.p.rapidapi.com" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

## Sample Response (verify-income)

```json
{
  "verification_score": 82,
  "confidence": "high",
  "detected_monthly_income": 12500000,
  "income_source": "salary",
  "salary_months_detected": 6,
  "monthly_incomes": [
    {"month": "2025-01", "amount": 12500000, "source": "salary"},
    {"month": "2025-02", "amount": 12500000, "source": "salary"}
  ],
  "consistency_score": 95,
  "income_cv": 0.02,
  "has_gaps": false,
  "gap_months": [],
  "fraud_flags": [],
  "balance_valid": true,
  "has_suspicious_patterns": false,
  "statement_period": "01 Jan 2025 - 30 Jun 2025",
  "total_months_covered": 6,
  "total_transactions": 186,
  "total_credit": 75500000,
  "total_debit": 52300000,
  "bank": "bca",
  "account_number": "1234567890"
}
```

## API Contact

- **Email:** hello@docai.id
- **Website:** https://docai.id
- **GitHub:** https://github.com/oyi77/docai
