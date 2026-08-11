# RapidAPI Submission Checklist — DocAI Verify

Step-by-step instructions to submit the DocAI Verify API to RapidAPI. Follow each step in order; every field below is copy-paste ready.

---

## Step 1: Sign In

1. Go to **https://rapidapi.com/hub**
2. Sign in with your RapidAPI account (or create one if you don't have one)
3. Verify your email if prompted

---

## Step 2: Create a New App

1. Click **"My Apps"** in the top-right menu
2. Click **"Add New App"**
3. App name: **DocAI Verify**

---

## Step 3: API Title

Copy and paste this exactly into the **API Title** field:

```
DocAI Verify — Income Verification API
```

---

## Step 4: Tagline

Copy and paste this exactly into the **Tagline** field:

```
Parse Indonesian bank e-statement PDFs → income verification score, salary detection, fraud signals. Zero LLM cost, 30–150ms.
```

---

## Step 5: Categories

Select these categories:

- **Finance / Banking**
- **Data Extraction / OCR**
- **Accounting**

---

## Step 6: Search Tags

Copy and paste this exactly into the **Search Tags** field:

```
bca, mandiri, e-statement, mutasi bank, rekening koran, bank statement parser, indonesia, ocr, accounting, income verification, credit scoring, fraud detection, jurnal, accurate, kledo
```

---

## Step 7: Description (Markdown)

Copy and paste this **entire block** into the **Description** field. The field supports Markdown.

```markdown
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
```

---

## Step 8: API Base URL

Enter this as the **Base URL**:

```
https://docaiid.pythonanywhere.com
```

---

## Step 9: Add Endpoints

Add the following 3 endpoints. For each endpoint, fill in the method, path, description, and parameters exactly as shown.

### Endpoint 1: GET /health

- **Method:** GET
- **Path:** `/health`
- **Description:**
  ```
  Health check. Returns status and list of supported banks. No authentication required.
  ```
- **Authentication:** None
- **Request Parameters:** None

**Sample Request:**
```bash
curl -X GET "https://docaiid.pythonanywhere.com/health"
```

**Sample Response:**
```json
{
  "status": "ok",
  "banks": ["bca", "mandiri"]
}
```

### Endpoint 2: POST /parse

- **Method:** POST
- **Path:** `/parse`
- **Description:**
  ```
  Parse a bank statement PDF into structured transaction data.
  ```
- **Authentication:** X-API-Key header required
- **Parameters (multipart/form-data):**

  | Name | Type | Required | Default | Description |
  |------|------|----------|---------|-------------|
  | `file` | file | ✅ | — | Bank statement PDF |
  | `bank` | string | ❌ | `"bca"` | Bank identifier: `bca` or `mandiri` |
  | `password` | string | ❌ | `null` | PDF password (DOB in DDMMYYYY format for BCA) |

- **Query Parameter:**

  | Name | Type | Default | Description |
  |------|------|---------|-------------|
  | `format` | string | `"json"` | Output format: `json` or `csv` |

- **Request Header:**

  | Header | Required | Description |
  |--------|----------|-------------|
  | `X-API-Key` | ✅ | Your RapidAPI key |

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

### Endpoint 3: POST /verify-income

- **Method:** POST
- **Path:** `/verify-income`
- **Description:**
  ```
  Verify income from a bank statement PDF. Returns structured income report with verification score, salary detection, consistency score, and fraud signals.
  ```
- **Authentication:** X-API-Key header required
- **Parameters (multipart/form-data):**

  | Name | Type | Required | Default | Description |
  |------|------|----------|---------|-------------|
  | `file` | file | ✅ | — | Bank statement PDF |
  | `bank` | string | ❌ | `"bca"` | Bank identifier: `bca` or `mandiri` |
  | `password` | string | ❌ | `null` | PDF password (DOB in DDMMYYYY format for BCA) |

- **Request Header:**

  | Header | Required | Description |
  |--------|----------|-------------|
  | `X-API-Key` | ✅ | Your RapidAPI key |

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
    {"month": "2025-02", "amount": 12500000.0, "source": "salary"},
    {"month": "2025-03", "amount": 12500000.0, "source": "salary"},
    {"month": "2025-04", "amount": 12500000.0, "source": "salary"},
    {"month": "2025-05", "amount": 13000000.0, "source": "salary"},
    {"month": "2025-06", "amount": 12500000.0, "source": "salary"}
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

## Step 10: Set Pricing Tiers

Configure the following pricing tiers in the **Pricing** section of the RapidAPI provider portal:

### Free Tier
- **Plan name:** Free
- **Price:** $0/month
- **Quota:** 100 requests/month

### Basic Tier
- **Plan name:** Basic
- **Price:** $9.99/month
- **Quota:** 1,000 requests/month

### Pro Tier
- **Plan name:** Pro
- **Price:** $49.99/month
- **Quota:** 10,000 requests/month

### Business Tier
- **Plan name:** Business
- **Price:** $199.99/month
- **Quota:** 100,000 requests/month

---

## Step 11: Add Sample Request/Response

For the **Sample Request** section, use the `curl` from the `/verify-income` endpoint above.

For the **Sample Response**, copy and paste this JSON (this is a verified demo response):

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

---

## Step 12: API Contact Information

Set the contact info in the provider portal:

- **Email:** hello@docai.id
- **Website:** https://docai.id
- **GitHub:** https://github.com/oyi77/docai

---

## Step 13: Submit for Review

1. Review all fields — ensure every section has content
2. Click **"Submit for Review"** (or equivalent button)
3. Wait for RapidAPI to review (typically 1–3 business days)
4. Check your email for approval notification

---

## Notes

- The RapidAPI hub URL after approval will be: `https://rapidapi.com/oyi77/api/docai`
- **DO NOT** expose your production API key in the listing — use placeholder `YOUR_RAPIDAPI_KEY` in sample requests
- Mandiri support is listed as "coming soon" in some contexts — the API supports it, but you may want to keep it as secondary in the listing to manage expectations
- After approval, the free tier is available immediately to anyone who subscribes to your API on RapidAPI
