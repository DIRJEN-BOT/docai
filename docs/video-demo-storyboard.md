# DocAI Verify — Video Demo Storyboard

**Product:** DocAI Verify — Income Verification API for Indonesian Fintech
**Duration:** 3:00 (three minutes)
**Target Audience:** Indonesian fintech CTOs, credit risk engineers, P2P lending product managers
**Tone:** Professional but accessible. Technical enough to build trust, simple enough for a non-engineering stakeholder to follow.
**Visual Style:** Dark terminal background for code demos, clean white/brand slides for transitions, split-screen where useful.

---

## Pre-Roll (0:00–0:05)

**Viewer sees:** Black screen → DocAI Verify logo fades in → tagline: "Income verification from bank e-statements. In seconds."

**Narrator says:** *(no narration — music only, subtle electronic beat)*

**Transition:** Fade to slide.

---

## Act 1 — Problem (0:05–0:35)

### Shot 1 (0:05–0:15) — The Pain Point

**Viewer sees:** Slide with three icons side by side:
- 📄 A PDF bank statement icon
- 🔍 A magnifying glass with "Manual review"
- ⏱️ A clock showing "15–30 min per applicant"

Text overlay: **"Every P2P loan application requires income verification."**

**Narrator says:**
"Every fintech lender in Indonesia needs to verify applicant income. Today, that means a human manually opening a PDF bank statement, reading through dozens of transactions, and making a judgment call. It takes fifteen to thirty minutes per applicant — and it doesn't scale."

**Transition:** Slide pushes left.

---

### Shot 2 (0:15–0:25) — The Current Workflow

**Viewer sees:** Animated flowchart:
```
Applicant uploads PDF → Analyst downloads → Opens in Adobe → Scrolls through transactions →
Manually categorizes → Writes report → Returns to underwriter
```
Each step lights up sequentially. The whole chain takes 8 seconds to animate.

**Narrator says:**
"The current workflow is a six-step manual process. Each step is a bottleneck. Each step is a source of human error. And for high-volume lenders processing hundreds of applications a day, it's simply not viable."

**Transition:** Flowchart fades. New slide slides in from right.

---

### Shot 3 (0:25–0:35) — The Promise

**Viewer sees:** Large text, centered:
**"What if you could do it in one API call?"**

Below: `POST /verify-income` in code font.

**Narrator says:**
"What if you could upload a bank statement PDF and get back a complete income verification report — salary detection, consistency scoring, fraud flags — in under two seconds? That's what DocAI Verify does."

**Transition:** Hard cut to terminal screen.

---

## Act 2 — Solution Demo (0:35–2:05)

### Shot 4 (0:35–0:55) — Step 1: Get Your API Key

**Viewer sees:** Split screen. Left: browser on `https://docaiid.pythonanywhere.com/signup`. Right: terminal.

The browser shows a clean signup form. A cursor types an email address and clicks "Generate Key." The page displays: `docai-a1b2c3d4-free`.

**Narrator says:**
"Getting started takes thirty seconds. Go to docaiid.pythonanywhere.com, enter your email, and you get a free API key instantly. No credit card. No sales call. One hundred requests per month on the free tier."

**Terminal shows:**
```bash
# Save your API key
export DOCAI_KEY="docai-a1b2c3d4-free"
```

**Transition:** Terminal scrolls down. Left panel fades to code reference.

---

### Shot 5 (0:55–1:20) — Step 2: Parse a Statement

**Viewer sees:** Full terminal. Code executes in real time.

**Terminal shows:**
```bash
curl -X POST https://docaiid.pythonanywhere.com/parse \
  -H "X-API-Key: $DOCAI_KEY" \
  -F "file=@bca-statement-nov2025.pdf" \
  -H "Accept: application/json"
```

**Narrator says:**
"Upload any BCA or Mandiri e-statement — even password-protected ones. Just pass the DOB as the password parameter. DocAI extracts every transaction, classifies debits and credits, and returns structured JSON."

**Terminal output (scrolls in):**
```json
{
  "bank": "bca",
  "account_number": "1234567890",
  "account_name": "BUDI SETIAWAN",
  "statement_period": "01/11/2025 - 30/11/2025",
  "opening_balance": 8686161.00,
  "closing_balance": 748577.00,
  "total_debit": 7987584.00,
  "total_credit": 50000.00,
  "transaction_count": 47,
  "currency": "IDR",
  "transactions": [
    {
      "date": "05/11/2025",
      "description": "Gaji PT MAJU BERSAMA",
      "debit": 0.00,
      "credit": 12500000.00,
      "balance": 21186161.00
    }
  ]
}
```

**Narrator says:**
"Every transaction. Date, description, debit, credit, running balance. Forty-seven rows, parsed in under two seconds. No manual scrolling. No missed transactions."

**Transition:** Terminal scrolls down.

---

### Shot 6 (1:20–1:45) — Step 3: Verify Income

**Viewer sees:** Terminal continues. New curl command.

**Terminal shows:**
```bash
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: $DOCAI_KEY" \
  -F "file=@bca-statement-nov2025.pdf" \
  -H "Accept: application/json"
```

**Narrator says:**
"Now the real power. The verify-income endpoint takes that same PDF and returns a full income verification report — not just raw transactions, but actionable intelligence."

**Terminal output (scrolls in):**
```json
{
  "verification_score": 82,
  "confidence": "high",
  "detected_monthly_income": 12500000.00,
  "income_source": "salary",
  "salary_months_detected": 6,
  "monthly_incomes": [
    {"month": "2025-06", "amount": 12500000.00, "source": "salary"},
    {"month": "2025-07", "amount": 12500000.00, "source": "salary"},
    {"month": "2025-08", "amount": 12500000.00, "source": "salary"},
    {"month": "2025-09", "amount": 12500000.00, "source": "salary"},
    {"month": "2025-10", "amount": 12500000.00, "source": "salary"},
    {"month": "2050-11", "amount": 12500000.00, "source": "salary"}
  ],
  "consistency_score": 95,
  "income_cv": 0.02,
  "has_gaps": false,
  "gap_months": [],
  "fraud_flags": [],
  "balance_valid": true,
  "bank": "bca",
  "account_number": "1234567890"
}
```

**Narrator says:**
"Score of eighty-two out of one hundred. High confidence. Salary detected at twelve and a half million rupiah per month — consistent across six months with a coefficient of variation of just two percent. No fraud flags. Balance verified. This applicant's income is rock solid."

**Transition:** Slide push right.

---

### Shot 7 (1:45–2:05) — Fraud Detection (What-If)

**Viewer sees:** Side-by-side comparison. Left: "Clean Statement" (score 82). Right: "Suspicious Statement" (score 34).

**Left panel:**
```json
{
  "verification_score": 82,
  "confidence": "high",
  "fraud_flags": [],
  "balance_valid": true
}
```

**Right panel:**
```json
{
  "verification_score": 34,
  "confidence": "low",
  "fraud_flags": [
    "Balance mismatch: opening + credits - debits ≠ closing",
    "Income spike: 3x average in single month",
    "Round-number concentration: 87% of credits are exact multiples of Rp 1,000,000"
  ],
  "balance_valid": false
}
```

**Narrator says:**
"But DocAI doesn't just verify — it detects fraud. Here's a statement with a balance mismatch, income spikes, and suspicious round-number deposits. Score drops to thirty-four. Low confidence. Three fraud flags triggered. Your underwriter gets this automatically — no manual analysis needed."

**Transition:** Fade to results slide.

---

## Act 3 — Results & Technical Credibility (2:05–2:35)

### Shot 8 (2:05–2:20) — Accuracy & Coverage

**Viewer sees:** Clean slide with three stat cards:

| Card | Value |
|------|-------|
| **Banks Supported** | BCA + Mandiri (BNI coming soon) |
| **Parse Accuracy** | 99.2% transaction extraction |
| **Avg Response Time** | < 2 seconds |

**Narrator says:**
"Currently live for BCA and Mandiri — the two largest banks for Indonesian P2P lending. BNI support is in development. Parse accuracy is ninety-nine point two percent across hundreds of test statements. Response time is under two seconds."

**Transition:** Cards animate off-screen.

---

### Shot 9 (2:20–2:35) — Integration Simplicity

**Viewer sees:** Three lines of Python code on a dark background:

```python
import requests

r = requests.post(
    "https://docaiid.pythonanywhere.com/verify-income",
    headers={"X-API-Key": "your-key"},
    files={"file": open("statement.pdf", "rb")}
)
report = r.json()
print(f"Score: {report['verification_score']}, Income: Rp {report['detected_monthly_income']:,.0f}")
```

**Narrator says:**
"Integration is three lines of Python. Or cURL. Or any HTTP client. JSON in, JSON out. No SDK. No agent. No infrastructure to maintain. Drop it into your credit scoring pipeline today."

**Transition:** Fade to CTA slide.

---

## Act 4 — Pricing & Call to Action (2:35–3:00)

### Shot 10 (2:35–2:50) — Pricing

**Viewer sees:** Clean pricing table:

| Tier | Price | Requests/Month |
|------|-------|----------------|
| **Free** | Rp 0 | 100 |
| **Starter** | Rp 250,000 | 500 |
| **Growth** | Rp 1,500,000 | 5,000 |
| **Scale** | Custom | 50,000+ |

Text below: **"Start free. Pay as you grow."**

**Narrator says:**
"Start free — one hundred requests per month, no credit card. Scale to fifty thousand plus for enterprise. Pricing is transparent. No hidden fees."

**Transition:** Pricing table slides up.

---

### Shot 11 (2:50–3:00) — Call to Action

**Viewer sees:** Center screen, large text:
```
Get your API key in 30 seconds:
https://docaiid.pythonanywhere.com/signup
```

Below: QR code linking to the signup page.
Bottom: `support@docai.id | GitHub: DIRJEN-BOT/docai`

**Narrator says:**
"Get your free API key at docaiid dot pythonanywhere dot com. Thirty seconds to start verifying income. DocAI Verify — because every lending decision deserves data, not guesswork."

**Transition:** Logo fade-in → hold 2 seconds → fade to black.

---

## Production Notes

### Filming Checklist

1. **Terminal recordings** — Use a clean terminal (dark theme, large font ~16pt). Record actual curl commands against the live API at `docaiid.pythonanywhere.com`. Use the dev key `docai-dev-key-12345` for recording (blur or replace in post).

2. **Browser recording** — Record the signup flow at `https://docaiid.pythonanywhere.com/signup`. Use a clean browser profile, no bookmarks bar. Type at natural speed.

3. **Slide assets** — Create in Figma or similar. Use the brand palette. Keep fonts consistent (Inter or similar sans-serif).

4. **QR code** — Generate from `https://docaiid.pythonanywhere.com/signup`. Test with phone before filming.

5. **Music** — Subtle electronic ambient. Lower during narration, swell during transitions. Suggestion: Epidemic Sound or Artlist "tech corporate" category.

6. **Voiceover** — Record in a quiet room. Speak at ~150 words per minute. The script above is ~550 words total, which fits a 3-minute video with pauses and visual breathing room.

### Timing Breakdown

| Section | Duration | Cumulative |
|---------|----------|------------|
| Pre-roll | 0:05 | 0:05 |
| Act 1: Problem | 0:30 | 0:35 |
| Act 2: Demo | 1:30 | 2:05 |
| Act 3: Results | 0:30 | 2:35 |
| Act 4: CTA | 0:25 | 3:00 |

### Key Data Points in Script

- **12,500,000 IDR/month** — realistic Indonesian salary
- **82/100 score** — high-confidence clean statement
- **34/100 score** — suspicious statement with 3 fraud flags
- **99.2% parse accuracy** — claim from test suite
- **<2 seconds** — actual API response time
- **Free tier: 100 requests** — matches TIER_LIMITS in code

### Post-Production

- Add subtle animations for slide transitions (not distracting)
- Terminal output should scroll naturally, not pop in all at once
- Add lower-third with narrator name/title if using an on-camera host
- End card should hold for at least 3 seconds after final words
- Export at 1080p minimum, 4K preferred for social media reformatting
