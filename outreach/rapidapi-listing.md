# RapidAPI Listing — DocAI Verify

Copy-paste ready for RapidAPI provider portal.

---

## API Name

**DocAI Verify - Indonesian Bank Statement Income Verification API**

---

## Short Description (150 chars)

Verify income from Indonesian bank e-statements (BCA, Mandiri). Instant JSON/CSV extraction + credit scoring. 50-100ms response.

---

## Category

Finance / Financial Data

---

## Search Tags

`income verification`, `bank statement`, `BCA`, `Mandiri`, `fintech`, `credit scoring`, `Indonesia`, `P2P lending`, `loan underwriting`, `fraud detection`, `rekening koran`, `mutasi bank`, `e-statement`, `income check`, `financial data`

---

## Long Description (paste into RapidAPI description field)

### What It Does

DocAI Verify is an income verification API purpose-built for Indonesian fintech. Upload a BCA or Mandiri e-statement PDF and get back a complete income verification report in under 100ms — detected monthly income, salary consistency score, fraud flags, and a composite verification score (0–100). No LLM calls, no per-token fees, no human analysts. Just deterministic parsing that works at scale.

### Key Features

- **Instant income detection** — automatically identifies salary credits, freelance income, and mixed sources from raw bank statements
- **Verification scoring** — composite 0–100 score combining balance reconciliation, income consistency, and fraud risk signals
- **Fraud detection built-in** — flags balance mismatches, suspicious round-number patterns, and income inconsistencies
- **BCA + Mandiri live** — the two largest Indonesian banks, with BNI and BRI coming soon
- **50–100ms response time** — deterministic parsing, no LLM dependencies
- **JSON + CSV export** — structured output ready for your loan management system
- **Zero user friction** — no bank account linking required, just upload a PDF
- **Stateless & private** — no files stored, no data retained

### How It Works

**Step 1:** Sign up on RapidAPI and get your API key (2 minutes).

**Step 2:** Upload a bank statement PDF via a single API call:

```bash
curl -X POST "https://docaiid.pythonanywhere.com/verify-income" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

**Step 3:** Receive a structured JSON response with verification score, monthly income breakdown, consistency metrics, and fraud flags.

### Use Cases

**Fintech Lending & Underwriting**
Automate income verification in your loan application flow. Replace 30–60 minute manual analyst reviews with instant API calls. DocAI Verify detects salary amounts, calculates consistency, and flags anomalies — all in one endpoint.

**Credit Scoring Enhancement**
Feed verified income data into your credit scoring model. Get monthly income breakdown, coefficient of variation, and income stability metrics — fields that traditional bureau data doesn't provide.

**Fraud Detection**
Catch fraudulent statements before they cost you money. DocAI Verify detects balance mismatches, suspicious round-number patterns, and income fabrication signals that manual review often misses.

**BNPL & Digital Banking**
Scale income checks to thousands of applications per day without proportional headcount growth. Process 50,000+ statements per month on the Scale plan.

### Getting Started

1. **Subscribe** to a plan on RapidAPI (Free tier: 100 calls/month, no credit card)
2. **Copy** your `X-RapidAPI-Key` from the dashboard
3. **Make your first call** — upload any BCA or Mandiri statement PDF and get results in < 100ms

```python
import requests

response = requests.post(
    "https://docaiid.pythonanywhere.com/verify-income",
    headers={"X-API-Key": "YOUR_API_KEY"},
    files={"file": open("statement.pdf", "rb")},
    data={"bank": "bca"},
)
report = response.json()
print(f"Score: {report['verification_score']}")
print(f"Monthly income: Rp{report['detected_monthly_income']:,.0f}")
```

### Supported Banks

| Bank | Status | Notes |
|------|--------|-------|
| BCA (Bank Central Asia) | ✅ Live | Full e-statement support, DOB-locked PDFs |
| Mandiri (Bank Mandiri) | ✅ Live | Livin' format (2023+), bilingual headers |
| BNI | 🔜 Coming Soon | — |
| BRI | 🔜 Coming Soon | — |

### Pricing

| Plan | Price | Verifications/Month | Best For |
|------|-------|--------------------|----|
| **Basic** (Free) | $0/mo | 100 | Evaluation & testing |
| **Pro** | $35/mo | 500 | Small P2P lenders |
| **Business** | $250/mo | 5,000 | Mid-size fintech |
| **Enterprise** | Contact Us | Custom | Banks, large fintech |

All plans include full API access (parse + verify-income), JSON + CSV output, and email support. No per-call overage fees — upgrade when ready.

---

## Endpoint 1: POST `/verify-income`

**Description:** Upload a bank statement PDF and receive a complete income verification report with scoring, monthly breakdown, and fraud detection.

**Headers:**
| Header | Required | Value |
|--------|----------|-------|
| `X-API-Key` | Yes | Your RapidAPI key |
| `Content-Type` | No | Auto-set by multipart/form-data |

**Request Body (multipart/form-data):**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file` | binary | Yes | — | Bank statement PDF |
| `bank` | string | No | `"bca"` | `"bca"` or `"mandiri"` |
| `password` | string | No | `null` | PDF password (BCA DOB: DDMMYYYY) |

**Response Example (200):**
```json
{
  "verification_score": 82,
  "confidence": "high",
  "detected_monthly_income": 12500000,
  "income_source": "salary",
  "salary_months_detected": 6,
  "monthly_incomes": [
    {"month": "2025-01", "amount": 12500000, "source": "salary"},
    {"month": "2025-02", "amount": 12500000, "source": "salary"},
    {"month": "2025-03", "amount": 12500000, "source": "salary"},
    {"month": "2025-04", "amount": 12500000, "source": "salary"},
    {"month": "2025-05", "amount": 13000000, "source": "salary"},
    {"month": "2025-06", "amount": 12500000, "source": "salary"}
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

**cURL:**
```bash
curl -X POST "https://docaiid.pythonanywhere.com/verify-income" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

**Error Responses:**
| Status | Code | Meaning |
|--------|------|---------|
| 401 | `unauthorized` | Missing or invalid API key |
| 400 | `password_protected` | PDF is encrypted and no password provided |
| 400 | `parse_error` | PDF is unreadable or corrupt |
| 400 | `invalid_request` | Unknown bank identifier |
| 422 | `validation_error` | Missing required `file` field |
| 500 | `error` | Unexpected server error |

---

## Endpoint 2: POST `/parse`

**Description:** Extract structured transaction data from a bank statement PDF. Use this when you need raw transactions without income scoring.

**Headers:**
| Header | Required | Value |
|--------|----------|-------|
| `X-API-Key` | Yes | Your RapidAPI key |

**Request Body (multipart/form-data):**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file` | binary | Yes | — | Bank statement PDF |
| `bank` | string | No | `"bca"` | `"bca"` or `"mandiri"` |
| `password` | string | No | `null` | PDF password (BCA DOB: DDMMYYYY) |

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `format` | string | `"json"` | Output format: `"json"` or `"csv"` |

**Response Example (200):**
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
      "reference": "TRF202501020001"
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

**CSV Output:** Add `?format=csv` to get semicolon-delimited CSV:
```
tanggal;keterangan;debit;kredit;saldo
02/01/2025;TRSF E-BANKING BCA;0;500000;1500000
03/01/2025;ATM WD BCA KCP THAMRIN;250000;0;1250000
```

**cURL:**
```bash
curl -X POST "https://docaiid.pythonanywhere.com/parse" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

**Error Responses:** Same as `/verify-income`.

---

## Endpoint 3: GET `/health`

**Description:** Check service status and supported banks. No authentication required.

**Response Example (200):**
```json
{
  "status": "ok",
  "banks": ["bca", "mandiri"]
}
```

**cURL:**
```bash
curl "https://docaiid.pythonanywhere.com/health"
```

---

## Response Field Reference

### verify-income Fields

| Field | Type | Description |
|-------|------|-------------|
| `verification_score` | int | Overall score 0–100 (composite) |
| `confidence` | string | `"high"`, `"medium"`, or `"low"` |
| `detected_monthly_income` | float | Best monthly income estimate (IDR) |
| `income_source` | string | `"salary"`, `"mixed"`, `"freelance"`, `"business"`, `"undetected"` |
| `salary_months_detected` | int | Months with salary-like credits |
| `monthly_incomes` | array | Per-month income breakdown |
| `consistency_score` | int | Income stability 0–100 |
| `income_cv` | float | Coefficient of variation (lower = more stable) |
| `has_gaps` | bool | Whether any months have zero income |
| `gap_months` | array | `YYYY-MM` strings with no income |
| `fraud_flags` | array | Human-readable fraud/anomaly descriptions |
| `balance_valid` | bool | Whether closing balance reconciles |
| `has_suspicious_patterns` | bool | Whether unusual patterns detected |
| `statement_period` | string | Date range, e.g. `"01 Jan 2025 - 30 Jun 2025"` |
| `total_months_covered` | int | Calendar months spanned |
| `total_transactions` | int | Total transaction rows |
| `total_credit` | float | Sum of all credits (IDR) |
| `total_debit` | float | Sum of all debits (IDR) |
| `bank` | string | `"bca"` or `"mandiri"` |
| `account_number` | string | Extracted account number |

### parse Fields

| Field | Type | Description |
|-------|------|-------------|
| `bank` | string | Detected bank |
| `account_number` | string | Account number |
| `account_name` | string | Account holder name |
| `statement_period` | string | Date range |
| `opening_balance` | float | Starting balance (IDR) |
| `closing_balance` | float | Ending balance (IDR) |
| `currency` | string | Always `"IDR"` |
| `total_debit` | float | Sum of debits |
| `total_credit` | float | Sum of credits |
| `balance_check` | string | `"passed"` or `"failed"` |
| `validation_error` | string | Error detail (only when failed) |
| `transactions` | array | Parsed transaction rows |

---

## Pricing for RapidAPI

| Plan | RapidAPI Price | Verifications/Month | Per-Call Cost | Target |
|------|---------------|--------------------|--------------|----|
| **Basic** | Free ($0) | 100 | $0 | Evaluation & testing |
| **Pro** | $35/mo | 500 | $0.07 | Small P2P lenders, startups |
| **Business** | $250/mo | 5,000 | $0.05 | Mid-size fintech, BNPL |
| **Enterprise** | Contact Us | Custom | Negotiable | Banks, large fintech |

**Notes:**
- All plans include full API access (parse + verify-income)
- No per-call overage charges — upgrade your plan when you need more volume
- Annual billing: 20% discount (Pro = $28/mo, Business = $200/mo)
- Enterprise: on-premise deployment, custom SLA, dedicated support available

---

## API Contact

- **Email:** hello@docai.id
- **Website:** https://docaiid.pythonanywhere.com
- **GitHub:** https://github.com/oyi77/docai (MIT licensed)
- **RapidAPI:** https://rapidapi.com/oyi77/api/docai
