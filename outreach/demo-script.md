# DocAI Verify — Demo Script

> 15-minute sales call walkthrough. Ready for live demos with fintech lending prospects.

---

## Pre-Demo Setup (Before the Call)

1. Have these files ready on your machine:
   - `demo_bca_statement.pdf` — sample BCA statement (good profile, verification_score ~82)
   - `demo_bca_statement_bad.pdf` — sample with balance mismatch (fraud detection demo)
2. Terminal open with curl ready
3. Browser tab open to `https://docaiid.pythonanywhere.com/health` (warm the endpoint)
4. Your API key on clipboard (demo key: `docai-dev-key-12345`)

---

## Section 1: Opening — Problem Statement (1 minute)

**Say:**

> "Every time someone applies for a loan at your platform, your team has to verify their income. Right now, that means either:
>
> 1. An analyst opens the PDF, manually reads each transaction, and calculates monthly income — 30 to 60 minutes per statement. Or,
> 2. You pay an enterprise provider like Perfios — $0.50 to $2 per verification, which adds up fast at scale.
>
> At 1,000 loan applications per month, that's either 500 analyst-hours or Rp 32 million in vendor fees.
>
> DocAI Verify replaces both of those with a single API call."

**Transition:** "Let me show you exactly how it works."

---

## Section 2: Live Demo — API Call with Real PDF (5 minutes)

### Step 2a: Health Check (30 seconds)

**Run in terminal:**

```bash
curl -s https://docaiid.pythonanywhere.com/health | python -m json.tool
```

**Expected output:**

```json
{
    "status": "ok",
    "banks": ["bca", "mandiri"]
}
```

**Say:**

> "The API is live. It supports BCA and Mandiri today, with BNI and BRI coming soon. No authentication needed for this check."

### Step 2b: Parse Endpoint — Raw Transaction Extraction (1.5 minutes)

**Run in terminal:**

```bash
curl -s -X POST "https://docaiid.pythonanywhere.com/parse" \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@demo_bca_statement.pdf" \
  -F "bank=bca" | python -m json.tool
```

**Walk through the output:**

> "This is the raw parse. Every transaction is extracted: date, description, debit, credit, running balance. Notice the balance_check at the bottom — it validates that the opening balance plus credits minus debits equals the closing balance. This is built-in integrity checking."

**Point out key fields:**
- `account_number` — extracted from the PDF
- `statement_period` — date range detected
- `opening_balance` / `closing_balance` — with validation
- `balance_check: "passed"` — integrity verified
- `transactions` array — all rows extracted

### Step 2c: Verify-Income Endpoint — The Main Event (3 minutes)

**Run in terminal:**

```bash
curl -s -X POST "https://docaiid.pythonanywhere.com/verify-income" \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@demo_bca_statement.pdf" \
  -F "bank=bca" | python -m json.tool
```

**Expected output:**

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

**Say:**

> "One call. In under 100 milliseconds, we get a complete income verification report. Let me walk you through what matters for your underwriting."

---

## Section 3: Results Walkthrough (3 minutes)

**Go field by field:**

### Verification Score (0–100)

> "The `verification_score` is 82. This is a composite of three things: whether the statement parsed correctly, how consistent the income is, and whether there are fraud signals. 80+ with `confidence: "high"` is a reliable income profile."

### Detected Monthly Income

> "`detected_monthly_income` is Rp 12.5 juta. This is the system's best estimate — it detected 6 months of salary credits at that amount. The `income_source` tells you it's salary, not freelance or mixed."

### Monthly Breakdown

> "`monthly_incomes` gives you a month-by-month breakdown. In this case, 5 of 6 months are exactly Rp 12.5 juta — one month was Rp 13 juta. Your underwriters can use this to see stability month over month."

### Consistency Score

> "`consistency_score` is 95 out of 100. The `income_cv` (coefficient of variation) is 0.02 — that means income varies by only 2%. Very stable. A gig worker might have a CV of 0.4 or higher."

### Balance Validation

> "`balance_valid: true` means the statement's closing balance matches the math. This is your first fraud check — if someone edited the PDF to inflate their balance, this would be `false`."

---

## Section 4: Fraud Detection Demo (2 minutes)

**Run in terminal:**

```bash
curl -s -X POST "https://docaiid.pythonanywhere.com/verify-income" \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@demo_bca_statement_bad.pdf" \
  -F "bank=bca" | python -m json.tool
```

**Walk through the differences:**

> "Now look at this statement. Same format, but:
>
> - `balance_valid: false` — the closing balance doesn't reconcile
> - `has_suspicious_patterns: true` — the system detected anomalies
> - `fraud_flags` — contains specific descriptions of what's wrong
> - `verification_score` is lower because of the balance mismatch
>
> This is what catches fabricated statements before they reach your underwriters. A manual analyst might miss a Rp 2 juta discrepancy in a 200-row statement. The API catches it instantly."

**If fraud_flags is non-empty, read them out:**

> "See this flag? [read the specific flag]. That's the kind of pattern that costs lenders money when it slips through."

---

## Section 5: Integration Overview (2 minutes)

**Say:**

> "Integration is straightforward. Here's what it looks like in Python."

**Show on screen (or paste in chat):**

```python
import requests

def verify_income(pdf_path: str, api_key: str) -> dict:
    """Verify income from a bank statement PDF."""
    response = requests.post(
        "https://docaiid.pythonanywhere.com/verify-income",
        headers={"X-API-Key": api_key},
        files={"file": open(pdf_path, "rb")},
        data={"bank": "bca"},
    )
    response.raise_for_status()
    return response.json()

# Usage in your loan flow
report = verify_income("applicant_statement.pdf", "your-api-key")

if report["verification_score"] >= 80:
    print(f"Income verified: Rp {report['detected_monthly_income']:,.0f}/month")
    print(f"Confidence: {report['confidence']}")
    # Proceed with loan decision
elif report["fraud_flags"]:
    print(f"Fraud detected: {report['fraud_flags']}")
    # Flag for manual review
else:
    print(f"Low confidence score: {report['verification_score']}")
    # Request additional documents
```

**Say:**

> "That's it. Three lines to make the call. The response gives you everything you need for an automated underwriting decision. It works the same way in any language — Java, Go, Node.js — it's just a REST API with multipart file upload."

**Mention:**

> "The API is also available on RapidAPI, so if your team already uses RapidAPI for other services, you can add DocAI Verify in minutes with billing through your existing RapidAPI account."

---

## Section 6: Pricing + Next Steps (2 minutes)

### Pricing Summary

**Show this table (or paste in chat):**

| Plan | Price | Verifications/Month | Best For |
|------|-------|--------------------|---------|
| Free | $0 | 100 | Test with your own statements |
| Pro | $35/mo | 500 | Small P2P lender |
| Business | $250/mo | 5,000 | Mid-size fintech |
| Enterprise | Contact Us | Custom | Banks, large fintech |

**Say:**

> "Free tier — 100 verifications a month, no credit card, no commitment. That's enough to test with real statements from your portfolio and see the output quality.
>
> The Business plan at $250 a month handles 5,000 verifications — that's Rp 700 per verification. Compare that to Rp 50 to 100K for a manual analyst, or $0.50 to $2 for enterprise tools.
>
> Annual billing gets you 20% off."

### ROI Quick Math

> "Quick math: if you process 1,000 loan applications a month, manual verification costs you roughly Rp 75 juta in analyst time. DocAI Verify on the Business plan costs Rp 3.5 juta. That's a 95% cost reduction with instant turnaround instead of 30–60 minute waits."

### Next Steps

**Close with:**

> "Here's what I'd suggest:
>
> 1. **Sign up for the free tier** — I'll send you the link. Test with 3–5 real statements from your existing portfolio.
> 2. **Compare the output** to what your analysts currently produce. Check the score, the monthly breakdown, the fraud flags.
> 3. **If it fits**, we can discuss the Pro or Business plan, or a pilot program at volume pricing.
>
> Want me to send the RapidAPI link now, or would you prefer to schedule a follow-up after you've tested it?"

---

## Appendix: Quick Reference

### API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/verify-income` | X-API-Key | Income verification report |
| POST | `/parse` | X-API-Key | Raw transaction extraction |
| GET | `/health` | None | Service status |

### Key cURL Commands

```bash
# Health check
curl https://docaiid.pythonanywhere.com/health

# Parse transactions (JSON)
curl -X POST "https://docaiid.pythonanywhere.com/parse" \
  -H "X-API-Key: YOUR_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"

# Parse transactions (CSV)
curl -X POST "https://docaiid.pythonanywhere.com/parse?format=csv" \
  -H "X-API-Key: YOUR_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"

# Verify income
curl -X POST "https://docaiid.pythonanywhere.com/verify-income" \
  -H "X-API-Key: YOUR_KEY" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

### Objection Handling

| Objection | Response |
|-----------|----------|
| "We already use Perfios" | "Perfios costs $0.50–$2/verification. We're Rp 1,000 (~$0.06). Use us for high-volume, low-risk tiers; keep Perfios for premium products." |
| "What about data privacy?" | "Stateless API — no files stored, no data retained. PDFs are processed in memory and immediately discarded." |
| "BCA only isn't enough" | "Mandiri is live today. BNI and BRI are on our roadmap. For P2P lending, BCA + Mandiri covers ~60% of applicant bank statements." |
| "Can we run it on-premise?" | "Enterprise tier includes on-premise deployment. Same deterministic parser, no LLM dependencies, runs in a Docker container." |
| "How accurate is it?" | "Deterministic parsing — same input, same output, every time. Balance validation catches structural errors. 82/100 on the demo statement, all signals verified." |
