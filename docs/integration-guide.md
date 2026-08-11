# DocAI Verify — Integration Guide

**Base URL:** `https://docaiid.pythonanywhere.com`
**Authentication:** `X-API-Key` header (all endpoints except `/health`)
**Supported Banks:** BCA, Mandiri

---

## Quick Start (5 minutes)

### Step 1: Get Your API Key

Sign up at **https://docaiid.pythonanywhere.com/signup** and copy your API key from the confirmation screen.

### Step 2: Make Your First Call

```bash
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

### Step 3: Parse the Response

```json
{
  "verification_score": 86,
  "confidence": "high",
  "detected_monthly_income": 12500000,
  "income_source": "salary",
  "salary_months_detected": 6,
  "consistency_score": 88,
  "income_cv": 0.12,
  "has_gaps": false,
  "fraud_flags": [],
  "balance_valid": true,
  "has_suspicious_patterns": false,
  "statement_period": "01 Jan 2025 - 30 Jun 2025",
  "total_months_covered": 6,
  "total_transactions": 142,
  "monthly_incomes": [
    {"month": "2025-01", "amount": 12500000, "source": "salary"},
    {"month": "2025-02", "amount": 12500000, "source": "salary"}
  ]
}
```

---

## Python Integration

### Basic Usage

```python
import requests


def verify_income(pdf_path: str, api_key: str, bank: str = "bca") -> dict:
    """Verify income from a bank statement PDF.

    Args:
        pdf_path: Path to the bank statement PDF file.
        api_key: Your DocAI Verify API key.
        bank: Bank identifier — "bca" or "mandiri".

    Returns:
        Parsed income verification report.

    Raises:
        requests.HTTPError: On 4xx/5xx responses.
    """
    with open(pdf_path, "rb") as f:
        response = requests.post(
            "https://docaiid.pythonanywhere.com/verify-income",
            headers={"X-API-Key": api_key},
            files={"file": f},
            data={"bank": bank},
        )
    response.raise_for_status()
    return response.json()


# Usage
result = verify_income("statement.pdf", "your-api-key")
print(f"Score: {result['verification_score']}")
print(f"Monthly Income: Rp {result['detected_monthly_income']:,.0f}")
print(f"Confidence: {result['confidence']}")
```

### Error Handling

```python
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout


def safe_verify(pdf_path: str, api_key: str, bank: str = "bca") -> dict | None:
    """Verify income with full error handling.

    Returns None on any failure with a user-facing message.
    """
    try:
        with open(pdf_path, "rb") as f:
            response = requests.post(
                "https://docaiid.pythonanywhere.com/verify-income",
                headers={"X-API-Key": api_key},
                files={"file": f},
                data={"bank": bank},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

    except HTTPError as e:
        status = e.response.status_code
        if status == 401:
            print("Invalid API key. Sign up at https://docaiid.pythonanywhere.com/signup")
        elif status == 400:
            body = e.response.json()
            error = body.get("error", "")
            if error == "password_protected":
                print("PDF is password-protected. Provide the password (BCA: DOB in DDMMYYYY).")
            elif error == "parse_error":
                print("Could not parse PDF. Check the file is a valid bank statement.")
            else:
                print(f"Bad request: {body.get('message', error)}")
        elif status == 413:
            print("File too large. Maximum size is 10 MB.")
        elif status == 429:
            print("Rate limit exceeded. Check your plan at https://docaiid.pythonanywhere.com/signup")
        else:
            print(f"HTTP {status}: {e}")
        return None

    except Timeout:
        print("Request timed out. Try again.")
        return None
    except ConnectionError:
        print("Cannot reach DocAI Verify. Check your network.")
        return None
```

### Two-Step: Parse + Verify Separately

```python
import requests


def parse_statement(pdf_path: str, api_key: str, bank: str = "bca") -> dict:
    """Parse a bank statement into structured transactions (no scoring)."""
    with open(pdf_path, "rb") as f:
        response = requests.post(
            "https://docaiid.pythonanywhere.com/parse",
            headers={"X-API-Key": api_key},
            files={"file": f},
            data={"bank": bank},
        )
    response.raise_for_status()
    return response.json()


# Parse to get raw transactions
parsed = parse_statement("statement.pdf", "your-api-key")
print(f"Account: {parsed['account_name']}")
print(f"Period: {parsed['statement_period']}")
print(f"Transactions: {len(parsed['transactions'])}")
print(f"Balance check: {parsed['balance_check']}")
```

---

## Node.js Integration

### Basic Usage

```javascript
const FormData = require("form-data");
const fs = require("fs");
const axios = require("axios");

async function verifyIncome(pdfPath, apiKey, bank = "bca") {
  const form = new FormData();
  form.append("file", fs.createReadStream(pdfPath));
  form.append("bank", bank);

  const response = await axios.post(
    "https://docaiid.pythonanywhere.com/verify-income",
    form,
    {
      headers: {
        "X-API-Key": apiKey,
        ...form.getHeaders(),
      },
      timeout: 30000,
    }
  );

  return response.data;
}

// Usage
verifyIncome("statement.pdf", "your-api-key")
  .then((result) => {
    console.log(`Score: ${result.verification_score}`);
    console.log(
      `Monthly Income: Rp ${result.detected_monthly_income.toLocaleString()}`
    );
    console.log(`Confidence: ${result.confidence}`);
  })
  .catch((err) => {
    if (err.response) {
      console.error(
        `HTTP ${err.response.status}: ${err.response.data.error}`
      );
    } else {
      console.error(`Request failed: ${err.message}`);
    }
  });
```

### With Error Handling

```javascript
async function safeVerify(pdfPath, apiKey, bank = "bca") {
  try {
    const form = new FormData();
    form.append("file", fs.createReadStream(pdfPath));
    form.append("bank", bank);

    const { data } = await axios.post(
      "https://docaiid.pythonanywhere.com/verify-income",
      form,
      {
        headers: { "X-API-Key": apiKey, ...form.getHeaders() },
        timeout: 30000,
      }
    );

    return data;
  } catch (err) {
    if (err.response) {
      const { status, data } = err.response;
      const messages = {
        401: "Invalid API key.",
        400: `Bad request: ${data.message || data.error}`,
        429: "Rate limit exceeded. Upgrade your plan.",
      };
      console.error(messages[status] || `HTTP ${status}`);
    } else {
      console.error(`Network error: ${err.message}`);
    }
    return null;
  }
}
```

---

## cURL Examples

### Verify Income

```bash
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: YOUR_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

### Verify Mandiri Statement

```bash
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: YOUR_KEY" \
  -F "file=@mandiri_statement.pdf" \
  -F "bank=mandiri"
```

### Parse Transactions Only

```bash
curl -X POST https://docaiid.pythonanywhere.com/parse \
  -H "X-API-Key: YOUR_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

### Parse to CSV

```bash
curl -X POST "https://docaiid.pythonanywhere.com/parse?format=csv" \
  -H "X-API-Key: YOUR_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

### Password-Protected BCA PDF

BCA e-statement PDFs are locked with the account holder's date of birth in DDMMYYYY format.

```bash
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: YOUR_KEY" \
  -F "file=@locked_statement.pdf" \
  -F "bank=bca" \
  -F "password=01011990"
```

### Health Check

```bash
curl https://docaiid.pythonanywhere.com/health
```

Response:

```json
{
  "status": "ok",
  "banks": ["bca", "mandiri"]
}
```

---

## Response Fields

### `POST /verify-income` — IncomeReport

| Field | Type | Description |
|-------|------|-------------|
| `verification_score` | integer | Overall score 0–100 (composite of parsing validity, income consistency, fraud risk) |
| `confidence` | string | `"high"`, `"medium"`, or `"low"` |
| `detected_monthly_income` | number | Best estimate of monthly income (IDR) |
| `income_source` | string | `"salary"`, `"mixed"`, `"freelance"`, `"business"`, or `"undetected"` |
| `salary_months_detected` | integer | Number of months with salary-like credits |
| `consistency_score` | integer | Income stability score 0–100 |
| `income_cv` | number | Coefficient of variation (lower = more consistent) |
| `has_gaps` | boolean | Whether any months have zero detected income |
| `gap_months` | array | List of `YYYY-MM` strings with no income detected |
| `monthly_incomes` | array | Monthly breakdown (see below) |
| `fraud_flags` | array | Human-readable fraud/anomaly descriptions (empty = clean) |
| `has_suspicious_patterns` | boolean | Whether unusual patterns were detected |
| `balance_valid` | boolean | Whether the statement's closing balance reconciles |
| `statement_period` | string | Human-readable date range, e.g. `"01 Jan 2025 - 30 Jun 2025"` |
| `total_months_covered` | integer | Calendar months spanned by transactions |
| `total_transactions` | integer | Total transaction rows parsed |
| `total_credit` | number | Sum of all credits (money in) |
| `total_debit` | number | Sum of all debits (money out) |
| `bank` | string | Detected bank: `"bca"` or `"mandiri"` |
| `account_number` | string | Account number extracted from the statement |

**Monthly income breakdown item:**

| Field | Type | Description |
|-------|------|-------------|
| `month` | string | `YYYY-MM` format |
| `amount` | number | Total detected income for the month (IDR) |
| `source` | string | `"salary"`, `"freelance"`, `"business"`, or `"mixed"` |

### `POST /parse` — ParseResult

| Field | Type | Description |
|-------|------|-------------|
| `bank` | string | Detected/specified bank |
| `account_number` | string | Account number from statement header |
| `account_name` | string | Account holder name |
| `statement_period` | string | Date range, e.g. `"01/01/2025 - 31/01/2025"` |
| `opening_balance` | number | Balance at start of statement period (IDR) |
| `closing_balance` | number | Balance at end of statement period (IDR) |
| `currency` | string | Always `"IDR"` |
| `total_debit` | number | Sum of all debit transactions |
| `total_credit` | number | Sum of all credit transactions |
| `balance_check` | string | `"passed"` or `"failed"` (3-tier validation) |
| `validation_error` | string | Error message (only present when `balance_check` is `"failed"`) |
| `transactions` | array | Parsed transactions (see below) |

**Transaction item:**

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Transaction date (`DD/MM/YYYY` or `DD/MM/YY`) |
| `description` | string | Transaction description / narration |
| `debit` | number | Money out (0 if credit) |
| `credit` | number | Money in (0 if debit) |
| `balance` | number | Running balance after this transaction |
| `reference` | string | Transaction reference number (may be empty) |

---

## Error Responses

All errors return a JSON body with `error` (code) and `message` (human-readable) fields.

| HTTP Status | Error Code | When |
|-------------|------------|------|
| `401` | `unauthorized` | Missing or invalid `X-API-Key` header |
| `400` | `password_protected` | PDF is encrypted and no password (or wrong password) provided |
| `400` | `parse_error` | PDF is unreadable or corrupt |
| `400` | `invalid_request` | Unknown bank identifier |
| `422` | `validation_error` | Invalid request shape (e.g., missing required `file` field) |
| `429` | `rate_limit_exceeded` | Monthly quota or per-minute rate limit exceeded |
| `500` | `error` | Unexpected server error |

**Example error:**

```json
{
  "error": "password_protected",
  "message": "This BCA statement PDF is password-protected (likely locked with date of birth: DDMMYYYY format)."
}
```

---

## Rate Limits

Rate limits are enforced per API key and reset monthly.

| Plan | Requests/Month | Requests/Minute |
|------|----------------|-----------------|
| Free | 100 | 10 |
| Starter | 500 | 50 |
| Growth | 5,000 | 200 |
| Scale | 50,000 | 1,000 |
| Enterprise | Unlimited | Custom |

Rate limit headers are included in every response:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Remaining` | Calls remaining this month |
| `X-RateLimit-Limit` | Monthly quota |
| `X-RateLimit-Reset` | Unix timestamp when the quota resets |

---

## Supported Banks

| Bank | Status | Notes |
|------|--------|-------|
| BCA | ✅ Production | Native e-statement PDF, multi-page, DOB-locked PDFs |
| Mandiri | ✅ Production | Modern Livin' format (2023+), bilingual headers, sign-based amounts |
| BNI | 🔜 Coming soon | — |
| BRI | 🔜 Coming soon | — |

---

## Integration Patterns

### Decision Engine (Recommended)

Use `verify-income` to make lending decisions. The `verification_score` and `confidence` fields give you a risk-ranked result:

```python
import requests


def lending_decision(pdf_path: str, api_key: str) -> dict:
    """Make a lending decision from a bank statement."""
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            "https://docaiid.pythonanywhere.com/verify-income",
            headers={"X-API-Key": api_key},
            files={"file": f},
            data={"bank": "bca"},
            timeout=30,
        )
    resp.raise_for_status()
    r = resp.json()

    # Decision logic
    if r["verification_score"] >= 80 and r["confidence"] == "high":
        decision = "approve"
    elif r["verification_score"] >= 60 and r["confidence"] != "low":
        decision = "review"
    else:
        decision = "decline"

    return {
        "decision": decision,
        "score": r["verification_score"],
        "income": r["detected_monthly_income"],
        "flags": r["fraud_flags"],
    }
```

### Batch Processing

Process multiple statements efficiently:

```python
import requests
from pathlib import Path


def batch_verify(pdf_dir: str, api_key: str) -> list[dict]:
    """Verify all PDFs in a directory."""
    results = []
    for pdf_path in Path(pdf_dir).glob("*.pdf"):
        try:
            with open(pdf_path, "rb") as f:
                resp = requests.post(
                    "https://docaiid.pythonanywhere.com/verify-income",
                    headers={"X-API-Key": api_key},
                    files={"file": f},
                    data={"bank": "bca"},
                    timeout=30,
                )
            resp.raise_for_status()
            result = resp.json()
            result["file"] = pdf_path.name
            results.append(result)
        except requests.HTTPError as e:
            results.append({
                "file": pdf_path.name,
                "error": str(e),
            })
    return results
```

---

## FAQ

**Q: Do I need to provide a password for BCA statements?**
A: BCA e-statement PDFs are typically locked with the account holder's date of birth (DDMMYYYY format). Pass the `password` form field with the DOB string. Without it, encrypted PDFs return `400 password_protected`.

**Q: What does `balance_valid: false` mean?**
A: The transaction totals don't reconcile with the declared closing balance. The parsing still succeeded — this is informational. A `validation_error` field explains the discrepancy. Could indicate the source PDF was modified or the parser misread a transaction.

**Q: Is the API stateless?**
A: Yes. No uploaded files or parsed data are stored. PDFs are processed in memory and immediately discarded.

**Q: How fast is the API?**
A: Typically 30–150 ms for BCA, 50–200 ms for Mandiri. The scoring engine adds negligible overhead.

**Q: Can I export transactions as CSV?**
A: Yes. Add `?format=csv` to `POST /parse` for semicolon-delimited output: `tanggal;keterangan;debit;kredit;saldo`.

**Q: What is the `verification_score`?**
A: A composite 0–100 score combining parsing validity (balance reconciliation), income consistency (coefficient of variation across months), and fraud risk (suspicious patterns, round-number anomalies). A score of 80+ with `"high"` confidence indicates a reliable income profile.

**Q: What bank formats are supported?**
A: Currently BCA and Mandiri. Pass `bank=bca` or `bank=mandiri` explicitly for best results. Default is `bank=bca`.

---

## Support

- **Sign up:** https://docaiid.pythonanywhere.com/signup
- **Health check:** https://docaiid.pythonanywhere.com/health
- **API docs:** https://docaiid.pythonanywhere.com/docs
- **GitHub:** https://github.com/oyi77/docai (MIT licensed)
- **Email:** hello@docai.id
