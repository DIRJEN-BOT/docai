# DocAI Verify — API Reference

**Base URL:** `https://docaiid.pythonanywhere.com`

**Authentication:** All endpoints except `/health` require the `X-API-Key` header. Obtain your key from [RapidAPI](https://rapidapi.com/oyi77/api/docai) or by contacting hello@docai.id.

---

## Endpoints

### POST `/verify-income`

Parse a bank statement PDF and return a comprehensive income verification report. This is the primary endpoint for fintech lending use cases.

**Request:**

| Component | Name | Type | Required | Default | Description |
|-----------|------|------|----------|---------|-------------|
| Header | `X-API-Key` | string | ✅ | — | Your API key |
| Form field | `file` | binary | ✅ | — | Bank statement PDF file |
| Form field | `bank` | string | ❌ | `"bca"` | Bank identifier: `bca` or `mandiri` |
| Form field | `password` | string | ❌ | `null` | PDF password (BCA DOB in DDMMYYYY format) |

**Response (200):** `IncomeReport` JSON — see [IncomeReport Schema](#incomereport-schema).

**cURL Example:**

```bash
curl -X POST "https://docaiid.pythonanywhere.com/verify-income" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

**Python Example:**

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

---

### POST `/parse`

Parse a bank statement PDF into structured transaction rows. Useful when you need raw transaction data without the income verification scoring.

**Request:**

| Component | Name | Type | Required | Default | Description |
|-----------|------|------|----------|---------|-------------|
| Header | `X-API-Key` | string | ✅ | — | Your API key |
| Form field | `file` | binary | ✅ | — | Bank statement PDF file |
| Form field | `bank` | string | ❌ | `"bca"` | Bank identifier: `bca` or `mandiri` |
| Form field | `password` | string | ❌ | `null` | PDF password (BCA DOB in DDMMYYYY format) |
| Query param | `format` | string | ❌ | `"json"` | Output format: `json` or `csv` |

**Response (200):** `ParseResult` JSON — see [ParseResult Schema](#parseresult-schema).

When `?format=csv`, returns `text/csv` (semicolon-delimited, header: `tanggal;keterangan;debit;kredit;saldo`).

**cURL Example:**

```bash
# JSON output
curl -X POST "https://docaiid.pythonanywhere.com/parse" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"

# CSV output
curl -X POST "https://docaiid.pythonanywhere.com/parse?format=csv" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

---

### GET `/health`

Health check endpoint. Returns the service status and list of supported banks. No authentication required.

**Response (200):**

```json
{
  "status": "ok",
  "banks": ["bca", "mandiri"]
}
```

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
| `500` | `error` | Unexpected server error |

**Example Error:**

```json
{
  "error": "password_protected",
  "message": "This BCA statement PDF is password-protected (likely locked with date of birth: DDMMYYYY format)."
}
```

---

## Data Models

### IncomeReport Schema

Returned by `POST /verify-income`.

| Field | Type | Description |
|-------|------|-------------|
| `verification_score` | integer | Overall score 0–100 (composite of parsing validity, consistency, fraud) |
| `confidence` | string | `"high"`, `"medium"`, or `"low"` |
| `detected_monthly_income` | number | Best estimate of monthly income (IDR) |
| `income_source` | string | `"salary"`, `"mixed"`, `"freelance"`, `"business"`, or `"undetected"` |
| `salary_months_detected` | integer | Number of months with salary-like credits found |
| `monthly_incomes` | array | Monthly breakdown (see below) |
| `consistency_score` | integer | Income stability score 0–100 |
| `income_cv` | number | Coefficient of variation (lower = more consistent) |
| `has_gaps` | boolean | Whether any months have zero detected income |
| `gap_months` | array[string] | List of `YYYY-MM` strings with no income detected |
| `fraud_flags` | array[string] | Human-readable fraud/anomaly descriptions (empty = clean) |
| `balance_valid` | boolean | Whether the statement's closing balance reconciles |
| `has_suspicious_patterns` | boolean | Whether unusual patterns were detected |
| `statement_period` | string | Human-readable date range, e.g. `"01 Jan 2025 - 30 Jun 2025"` |
| `total_months_covered` | integer | Number of calendar months spanned by transactions |
| `total_transactions` | integer | Total number of transaction rows parsed |
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

---

### ParseResult Schema

Returned by `POST /parse`.

| Field | Type | Description |
|-------|------|-------------|
| `bank` | string | Detected/specified bank: `"bca"` or `"mandiri"` |
| `account_number` | string | Account number from the statement header |
| `account_name` | string | Account holder name |
| `statement_period` | string | Date range, e.g. `"01/01/2025 - 31/01/2025"` |
| `opening_balance` | number | Balance at start of statement period (IDR) |
| `closing_balance` | number | Balance at end of statement period (IDR) |
| `currency` | string | Always `"IDR"` |
| `total_debit` | number | Sum of all debit transactions |
| `total_credit` | number | Sum of all credit transactions |
| `balance_check` | string | `"passed"` or `"failed"` (3-tier validation: aggregate + debit/credit non-negative + running balance) |
| `validation_error` | string | Balance-check error message (only present when `balance_check` is `"failed"`) |
| `transactions` | array[Transaction] | List of parsed transactions (see below) |

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

## Rate Limits

Rate limits are enforced per API key and reset monthly.

| Plan | Requests/Month |
|------|----------------|
| Free | 100 |
| Starter | 500 |
| Growth | 5,000 |
| Scale | 50,000 |
| Enterprise | Unlimited (custom) |

---

## Supported Banks

| Bank | Parser Status | Notes |
|------|---------------|-------|
| BCA | ✅ Stable | Native e-statement, multi-page, DOB-locked PDFs, synthetic + real formats |
| Mandiri | ✅ Stable | Modern Livin' format (2023+), bilingual headers, sign-based amounts |
| BNI | 🔜 Coming soon | — |
| BRI | 🔜 Coming soon | — |

---

## FAQ

**Q: Do I need to provide a password for BCA statements?**
A: BCA e-statement PDFs are typically locked with the account holder's date of birth (DDMMYYYY format). Pass the `password` parameter with the DOB string. Without it, encrypted PDFs will return a `400 password_protected` error.

**Q: What bank formats are supported?**
A: Currently BCA and Mandiri. Pass `bank=bca` or `bank=mandiri` explicitly for best results. The default is `bank=bca`.

**Q: What does `balance_check: "failed"` mean?**
A: It means the transaction totals don't reconcile with the declared closing balance. This is informational, not an error — the parsing succeeded. A `validation_error` field in the response explains the discrepancy. This could indicate the source PDF was modified or the parser misread a transaction.

**Q: Is the API stateless?**
A: Yes. No uploaded files or parsed data are stored. PDFs are processed in memory and immediately discarded.

**Q: How fast is the API?**
A: Typically 30–150ms for BCA, 50–200ms for Mandiri. The scoring engine adds negligible overhead since it operates on already-parsed data.

**Q: Can I use this for CSV export?**
A: Yes. Add `?format=csv` to `POST /parse` to get semicolon-delimited CSV output (`tanggal;keterangan;debit;kredit;saldo`).

**Q: What is the `verification_score`?**
A: A composite 0–100 score combining three factors: parsing validity (balance reconciliation), income consistency (coefficient of variation across months), and fraud risk (suspicious patterns, round-number anomalies). A score of 80+ with `"high"` confidence indicates a reliable income profile.

---

## Contact

- **Email:** hello@docai.id
- **GitHub:** https://github.com/oyi77/docai (MIT licensed)
- **RapidAPI:** https://rapidapi.com/oyi77/api/docai
- **Live API:** https://docaiid.pythonanywhere.com/docs
