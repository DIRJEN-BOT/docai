# DocAI Verify — 2-Minute Demo Script

**Total runtime:** 2:00 (120 seconds)
**Recording method:** Screen capture + voiceover (no editing required — each scene is one continuous take)
**Pre-requisites before recording:**
- Terminal window open at `docaiid.pythonanywhere.com`
- API key visible: `docai-dev-key-12345`
- BCA demo PDF at `fixtures/demo_bca_statement.pdf`
- Mandiri demo PDF at `fixtures/demo_mandiri_statement.pdf`
- Landing page tab open: `https://docaiid.pythonanywhere.com`

---

## Scene 1: Hook (0:00 – 0:15)

**Duration:** 15 seconds
**Screen:** Split layout — left half shows a BCA bank statement PDF scrolling slowly (zoomed to transactions), right half shows a stopwatch counting up from 0:00. Timer pauses at 0:28 when narration says "30 minutes." Dark overlay with white text appears: *"Your credit analysts spend 30 minutes per bank statement."*

**Narration:**
> "Your credit analysts spend thirty minutes on every bank statement. Opening the PDF, scanning transactions, reconciling balances, checking for fraud. Every single time. That's six hours a day — just on paperwork."

**Transition:** Timer and PDF fade out. Screen wipes to landing page.

---

## Scene 2: Solution Intro (0:15 – 0:30)

**Duration:** 15 seconds
**Screen:** Browser navigates to `https://docaiid.pythonanywhere.com`. Show the landing page hero section full-screen. Mouse hovers over "BCA + Mandiri" badge. Then scroll down to the "How it works" section showing the three steps: Upload → Parse → Verify.

**Narration:**
> "DocAI Verify does it in one hundred fifty milliseconds. Drop in a BCA or Mandiri bank e-statement — PDF or password-protected — and get structured income data. Zero LLM cost, deterministic results, built for Indonesian fintech."

**Transition:** Click on the terminal app or switch to terminal window.

---

## Scene 3: Live Demo — Parse (0:30 – 1:00)

**Duration:** 30 seconds
**Screen:** Full-screen terminal. Type and run the commands live — do not paste pre-written blocks. The typing speed should be natural, not sped up.

**Command block 1 — BCA Parse:**
```bash
curl -s -X POST https://docaiid.pythonanywhere.com/parse \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@fixtures/demo_bca_statement.pdf" \
  -F "bank=bca" | python -m json.tool
```

**On screen (JSON response appears):**
```json
{
    "bank": "bca",
    "account_number": "1234567890",
    "account_name": "SUHERMAN Setiawan",
    "statement_period": "01/01/2025 - 30/06/2025",
    "opening_balance": 5000000.0,
    "closing_balance": 96688011.0,
    "currency": "IDR",
    "total_debit": 26466364.0,
    "total_credit": 118154375.0,
    "balance_check": "passed",
    "transactions": [
        {
            "date": "01/01/2025",
            "description": "TRANSFER KELUAR BCA Sewa Bulanan",
            "debit": 2500000.0,
            "credit": 0.0,
            "balance": 2500000.0,
            "reference": ""
        },
        {
            "date": "05/01/2025",
            "description": "Transfer BI Fast Dari PT TEKNOLOGI NUSANTARA",
            "debit": 0.0,
            "credit": 4555144.0,
            "balance": 7014897.0,
            "reference": ""
        }
    ]
}
```

**Narration:**
> "Here's a BCA statement. One curl command — the API returns every transaction, account details, and a balance check. See 'balance_check passed'? The API reconciled opening balance plus credits minus debits against closing balance. If the math doesn't add up, you'd see 'mismatch' here."

**Command block 2 — Quick Mandiri parse (optional, runs while narrating):**
```bash
curl -s -X POST https://docaiid.pythonanywhere.com/parse \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@fixtures/demo_mandiri_statement.pdf" \
  -F "bank=mandiri" | python -m json.tool
```

**Narration (continues):**
> "Same endpoint works for Mandiri statements. Upload the PDF, specify the bank, get structured data. The API handles both PDF formats natively — no conversion, no OCR."

**Transition:** Clear screen or scroll down to a fresh prompt.

---

## Scene 4: Live Demo — Verify Income (1:00 – 1:30)

**Duration:** 30 seconds
**Screen:** Full-screen terminal. Type and run the command live.

**Command block:**
```bash
curl -s -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@fixtures/demo_bca_statement.pdf" \
  -F "bank=bca" | python -m json.tool
```

**On screen (JSON response appears):**
```json
{
    "verification_score": 86,
    "confidence": "high",
    "detected_monthly_income": 12500000.0,
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

**Narration:**
> "This is the income verification report. Verification score: eighty-six out of one hundred. The engine detected monthly salary of twelve point five million rupiah across six months. Consistency score ninety-five — very stable income, no gaps. Fraud flags: empty. That means no round-trip transactions, no suspicious patterns, balance is valid. All of this in one hundred fifty milliseconds. No LLM calls. No per-query token cost. Deterministic."

**Transition:** Terminal fades out, comparison table fades in.

---

## Scene 5: Results & CTA (1:30 – 2:00)

**Duration:** 30 seconds
**Screen:** Clean comparison table on dark background, left column "Manual Review" vs right column "DocAI Verify":

| | Manual Review | DocAI Verify |
|---|---|---|
| Time per statement | 30 minutes | 150 milliseconds |
| Output | Subjective notes | Structured JSON |
| Fraud detection | Manual checklist | Automated scoring |
| Cost | Analyst salary | Rp 1,000 / statement |
| Banks supported | Any (slow) | BCA + Mandiri (instant) |

After 5 seconds, the table shrinks and a CTA card slides in from the right:

```
100 free verifications per month
Sign up: docaiid.pythonanywhere.com
```

Below the CTA: placeholder for a QR code linking to the signup page.

**Narration:**
> "Thirty minutes becomes one hundred fifty milliseconds. Subjective judgment becomes a score from zero to one hundred. Your analysts focus on edge cases — the API handles the routine work. Start with one hundred free verifications every month. Sign up at docai id dot pythonanywhere dot com. Thank you."

**Transition:** Fade to black. End card holds for 3 seconds with logo, URL, and QR code placeholder.

---

## Production Notes

### Recording setup
1. **Screen recording:** OBS Studio or built-in screen recorder. Record at 1920x1080, 30fps.
2. **Voiceover:** Record separately with any microphone, then overlay in a basic editor. Or narrate live during screen recording for a more authentic feel.
3. **Terminal theme:** Use a dark terminal with large font (18pt minimum) so text is readable at 1080p.
4. **Font:** Use a monospace font (JetBrains Mono, Fira Code) in the terminal. The terminal background should be dark (#1e1e2e or similar).

### Before recording checklist
- [ ] Verify API is live: `curl https://docaiid.pythonanywhere.com/health`
- [ ] Test both curl commands produce expected output
- [ ] Open landing page in browser, confirm it loads
- [ ] Clear terminal history (clean prompt for recording)
- [ ] Set terminal to full-screen
- [ ] Close all notifications (Do Not Disturb mode)
- [ ] Test microphone levels

### Timing breakdown

| Scene | Start | End | Duration | Cumulative |
|---|---|---|---|---|
| 1: Hook | 0:00 | 0:15 | 15s | 15s |
| 2: Solution | 0:15 | 0:30 | 15s | 30s |
| 3: Parse demo | 0:30 | 1:00 | 30s | 60s |
| 4: Verify demo | 1:00 | 1:30 | 30s | 90s |
| 5: CTA | 1:30 | 2:00 | 30s | 120s |

### Narrator script (word count estimate)
- Scene 1: ~50 words → 15 sec at natural pace
- Scene 2: ~40 words → 15 sec
- Scene 3: ~80 words → 30 sec
- Scene 4: ~90 words → 30 sec
- Scene 5: ~60 words → 15 sec narration + 15 sec hold/end card
- **Total: ~320 words → 2:00**

### Key messages (must appear)
1. "30 minutes per statement" (pain)
2. "150 milliseconds" (speed)
3. "BCA + Mandiri" (coverage)
4. "Zero LLM cost" (economics)
5. "Balance check passed" (reliability)
6. "Fraud flags: empty" (trust)
7. "100 free verifications" (CTA)
8. "docaiid.pythonanywhere.com" (URL)
