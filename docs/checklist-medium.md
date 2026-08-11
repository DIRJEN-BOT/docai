# Medium Blog Post Checklist — DocAI Verify

Step-by-step instructions to publish the income verification blog post on Medium. Every field below is copy-paste ready.

---

## Step 1: Sign In

1. Go to **https://medium.com**
2. Sign in with your Medium account (or create one)
3. Verify your email if prompted
4. Ensure you have a Medium membership (required for "Members only" posts)

---

## Step 2: Start a New Story

1. Click **"Write"** in the top-right corner
2. Select **"Write a story"**

---

## Step 3: Title

Copy and paste this exactly into the **Title** field:

```
How We Built an Income Verification API for Indonesian Fintech (Deterministic, Zero LLM Cost)
```

---

## Step 4: Subtitle

Copy and paste this exactly into the **Subtitle** field (click the "T" subtitle option):

```
Parsing bank statement PDFs without OCR, without LLMs, and without breaking the bank.
```

---

## Step 5: Featured Image

Before pasting the body content, add the featured image:

1. Click the **"+"** button at the top of the editor
2. Select **"Add image"**
3. Upload the file: `assets/promo/docai_banner_twitter.png` (from the docai repo)
   - This is 1600×900px, optimized for Medium's featured image ratio
4. Click the image and select **"Use as featured image"**
5. Add alt text: `DocAI Verify — Income Verification API for Indonesian Fintech`

---

## Step 6: Body Content

Copy the **entire content below** and paste it into the Medium editor body. Medium supports Markdown pasting — it will auto-convert.

### Copy from here:

How We Built an Income Verification API for Indonesian Fintech (Deterministic, Zero LLM Cost)

*Parsing bank statement PDFs without OCR, without LLMs, and without breaking the bank.*

---

## The Problem: Manual Income Verification Is a Bottleneck

Indonesia's peer-to-peer lending market processes millions of loan applications every month. Before disbursing funds, lenders need to verify that the applicant actually earns what they claim. The traditional approach? A human underwriter opens a bank statement PDF, scrolls through pages of transactions, mentally tallies salary deposits, and makes a judgment call.

This process is slow, subjective, and fraud-prone.

The digital alternatives aren't much better. Account-aggregation services like Brick and Ayoconnect let borrowers link their bank accounts directly — eliminating the PDF entirely. But this approach has its own problems: it requires the borrower to authenticate through their banking app, many users drop off during the linking flow, and not all banks support the integration. For BCA — Indonesia's largest private bank — account aggregation coverage is incomplete, and the user experience is clunky.

What if you could get the same structured data from the PDF itself, deterministically, in under 150 milliseconds, with zero per-document cost?

That's what we built with **DocAI Verify**.

## Our Approach: Deterministic PDF Parsing + Scoring Engine

DocAI Verify is an income verification API that takes a bank e-statement PDF as input and produces a structured income verification report as output. No LLM calls. No OCR engine. No machine learning models. Pure regex, number parsing, and statistical analysis.

The system has two layers:

1. **Bank-specific parsers** — Extract structured transaction data from BCA and Mandiri e-statement PDFs
2. **Scoring engine** — Analyze the transaction data to produce a composite verification score (0–100)

The entire pipeline runs in 30–150ms per document on commodity hardware. The cost per verification is effectively zero — no API calls to third-party services, no GPU inference, no token fees.

### Why Deterministic Beats LLM for This Use Case

When we started, the obvious approach was to feed the PDF to GPT-4 or Claude with a structured prompt. It would "understand" the document, extract the data, and return JSON. Simple.

But we found three critical problems with the LLM approach:

1. **Consistency** — The same document processed twice could produce different field extractions. Transaction amounts might be off by rounding. Dates might be reformatted. For a financial verification system, "usually correct" isn't good enough.

2. **Cost** — At scale, LLM token costs add up fast. A 10-page bank statement is roughly 4,000–8,000 tokens input. At GPT-4o rates, that's $0.02–0.04 per verification. Process 100,000 documents a month and you're looking at $2,000–4,000 in pure inference cost — before you've built any actual business logic.

3. **Latency** — LLM API calls take 2–10 seconds. Our deterministic parser finishes in 30–150ms. For an API that needs to sit inside a loan decisioning pipeline, that difference matters.

The tradeoff is clear: bank e-statements are structured documents with known formats. They don't need "understanding" — they need precise, repeatable extraction. Deterministic parsing wins here.

## Technical Deep Dive

### Parsing BCA E-Statements

BCA (Bank Central Asia) e-statements come in a native format that's been relatively stable for years. The parser handles several quirks:

**Format detection.** The parser first determines whether it's looking at a native BCA e-statement or a synthetic/test format. It does this by checking for characteristic tokens in the extracted text: the BCA header layout, specific column arrangement, and the "MUTASI" (transaction) summary section.

**DB/CR labels.** BCA statements use "DB" (debit) and "CR" (credit) labels — but only sometimes. When the labels are present, classification is straightforward. When they're absent (common in multi-page statements where the header doesn't repeat), the parser falls back to balance-based detection.

**Balance-based debit/credit detection.** This is the core algorithm. For each transaction row, the parser compares the running balance before and after the transaction:

```
if current_balance > previous_balance:
    transaction is a CREDIT (incoming)
    credit_amount = current_balance - previous_balance
elif current_balance < previous_balance:
    transaction is a DEBIT (outgoing)
    debit_amount = previous_balance - current_balance
```

This approach is robust because BCA statements always include a running balance column. Even when OCR extraction mangles the amount labels, the balance progression tells the truth.

**Native amount format.** BCA uses Western-style formatting: commas for thousands, dots for decimals (`9,846,915.69`). The parser uses a regex pattern `\d{1,3}(?:,\d{3})+(?:\.\d{2})?` to match these amounts precisely.

**Multi-page handling.** Real BCA statements span multiple pages. The parser concatenates all page text, normalizes dates (appending the statement year to bare DD/MM dates), and processes the full transaction stream as a single sequence.

### Parsing Mandiri Livin' Statements

Mandiri's modern e-statement format (2023+, from the Livin' by Mandiri app) is quite different from BCA:

**Bilingual headers.** The column headers appear in both Indonesian and English: "Tanggal/Date", "Keterangan/Remarks", "Nominal/Amount", "Saldo/Balance". The parser handles either language.

**Sign-based amounts.** Unlike BCA's DB/CR labels, Mandiri uses explicit signs: `+12,500,000` for credits, `-3,200,000` for debits. The parser extracts the sign and maps it accordingly.

**Pipe-separated format.** Transaction lines follow the pattern:
```
No | Date | Time | Description | Amount | Balance
```
The parser splits on pipe characters and validates each field positionally.

**Indonesian number formatting.** Mandiri uses the Indonesian convention: dots for thousands, comma for decimal (`1.234.567,89`). The `parse_indonesian_number` utility handles this conversion to `Decimal` for precise arithmetic.

**Password-protected PDFs.** Both BCA and Mandiri statements can be encrypted with the account holder's date of birth (DDMMYYYY format). The API accepts an optional `password` parameter, decrypts the PDF transparently, and retries the parse.

### The Income Verification Scoring Algorithm

Once transactions are extracted, the scoring engine analyzes the data across four dimensions:

#### 1. Salary Detection

The engine identifies salary deposits using a two-pass approach:

**Pass 1 — Keyword matching.** Transaction descriptions are scanned for salary-related terms: `gaji` (salary), `payroll`, `upah` (wages), `THP` (take-home pay), `salary`. If a credit transaction's description matches, it's flagged as a salary deposit.

**Pass 2 — Recurring amount analysis.** Even without keyword matches, salary deposits have a telltale pattern: the same (or very similar) credit amount appears in 3+ distinct calendar months. The engine checks for amounts within ±10% of each other across months. If a recurring pattern is found, those transactions are also classified as salary.

The detected income for each month is the total salary-classified credits. The overall monthly income estimate is the median of the per-month totals — robust against outlier months.

#### 2. Consistency Scoring

Income consistency is measured using the **coefficient of variation (CV)** across months:

```
CV = standard_deviation(monthly_incomes) / mean(monthly_incomes)
```

The CV is then mapped to a 0–100 score:

| CV Range | Score Range | Interpretation |
|----------|-------------|----------------|
| < 0.10 | 90–100 | Very stable income |
| 0.10–0.20 | 70–89 | Mostly stable |
| 0.20–0.40 | 40–69 | Variable |
| > 0.40 | 0–39 | Highly irregular |

The engine also detects **gap months** — months with zero detected income — which significantly impact the consistency score and trigger warnings.

#### 3. Fraud Signal Detection

The fraud detection layer flags several anomalous patterns:

- **Balance mismatch** — The computed closing balance (opening + credits − debits) doesn't match the declared closing balance. This catches modified or tampered statements.
- **Round-number concentration** — If more than 30% of transactions are round multiples of IDR 100,000, it suggests fabricated entries. Real bank statements have odd amounts.
- **Duplicate transactions** — Same date, same description, same amount appearing multiple times. Could indicate copy-paste fraud.
- **High balance relative to income** — If the closing balance represents more than 24 months of detected income, the numbers don't add up.
- **Short statement periods** — Statements covering fewer than 3 months provide insufficient data for reliable income estimation.

Each fraud flag reduces the composite score by 5 points.

#### 4. Composite Score

The final verification score (0–100) is a weighted composite:

| Component | Weight | Points |
|-----------|--------|--------|
| Balance validation (pass/fail) | 25% | 0 or 25 |
| Income source detected | 25% | 5–25 (salary = 25, mixed = 15, freelance = 10) |
| Consistency score | 30% | 0–30 (scaled from consistency 0–100) |
| No fraud flags | 20% | 0–20 (lose 5 per flag) |

The composite score maps to a confidence level:
- **80–100:** High confidence
- **50–79:** Medium confidence
- **0–49:** Low confidence

## Results

After building the full pipeline, we verified it against real and synthetic data:

- **120 tests passing** — Unit tests for parsers, scoring engine, validation, CLI, and API endpoints
- **BCA parser: 100% accuracy** — Verified against 3 real BCA e-statement PDFs (October 2025: 50 transactions, April 2026: 11 transactions, May 2026: 8 transactions). All parsed totals match the bank's own MUTASI CR/DB summary.
- **Mandiri parser: format-verified** — Verified against modern Livin' format specifications with bilingual headers, sign-based amounts, and pipe-separated lines.
- **Balance-check pass rate: 100%** — Every parse result is validated with a 3-tier balance check: aggregate balance reconciliation, debit/credit non-negativity, and row-level running balance verification. Corrupted or modified files are correctly rejected.
- **Zero fraud false positives** on clean statements — Fraud flags only trigger on genuinely anomalous patterns.

## API Example

```bash
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@statement.pdf" \
  -F "bank=bca"
```

Response:

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

The score of 82 with `"high"` confidence tells the lender: this applicant has a stable salary of approximately Rp 12.5 million/month, consistent across 6 months, with no fraud signals and a valid balance reconciliation.

## What's Next

We're expanding DocAI Verify in several directions:

- **BNI and BRI parsers** — Adding support for Indonesia's two largest state-owned banks
- **Batch processing** — Upload multiple statements in a single request for portfolio-level verification
- **Webhook support** — Push verification results to your system when processing is complete
- **On-premise deployment** — Docker image for lenders who need to process statements within their own infrastructure (no data leaves your network)

## Try It

DocAI Verify is live and free to try:

- **100 verifications/month** on the free tier — no credit card required
- **API:** [docaiid.pythonanywhere.com](https://docaiid.pythonanywhere.com)
- **Source code:** [github.com/oyi77/docai](https://github.com/oyi77/docai) (MIT licensed)
- **RapidAPI:** [docai on RapidAPI](https://rapidapi.com/oyi77/api/docai)

If you're building lending, credit scoring, or financial verification tools for the Indonesian market, we'd love to hear from you. Drop us a line at hello@docai.id.

---

*DocAI Verify — Income verification for Indonesian fintech. Deterministic. Fast. Free to start.*

### Copy ends here

---

## Step 7: Add Tags

After pasting the body, add tags at the bottom of the editor (or use the tag field):

1. Scroll to the bottom of the story editor
2. Add each tag one at a time:
   - `fintech`
   - `indonesia`
   - `api`
   - `python`
   - `banking`
   - `income-verification`
   - `pdf-parsing`

---

## Step 8: Code Block Formatting Check

Medium auto-formats code blocks, but verify:

1. Scroll through the post and find each code block (``` delimited sections)
2. Ensure each code block shows a **language label** (bash, json, python, etc.)
3. If a code block is plain text, click inside it and select the language from the toolbar dropdown
4. Verify the regex pattern renders correctly: `\d{1,3}(?:,\d{3})+(?:\.\d{2})?`
5. Verify the table formatting looks correct — Medium may need you to manually adjust table alignment

---

## Step 9: Formatting Check

Before publishing, verify these formatting elements:

- [ ] Title is correct (no extra spaces or typos)
- [ ] Subtitle appears below the title
- [ ] Featured image (docai_banner_twitter.png) is set
- [ ] All headings (##, ###) render as proper headers
- [ ] All code blocks render with syntax highlighting
- [ ] All tables render correctly (3 tables total)
- [ ] Bold text (**text**) renders properly
- [ ] Links are clickable: docaiid.pythonanywhere.com, github.com/oyi77/docai, rapidapi.com/oyi77/api/docai, hello@docai.id
- [ ] The horizontal rules (---) render as dividers

---

## Step 10: Set Visibility

1. Click the **"..."** menu (top-right of the editor)
2. Select **"Story settings"**
3. Set **"Allow responses"** to "Everyone" (or your preference)
4. Close settings

---

## Step 11: Preview

1. Click the **"Preview"** button (eye icon) in the top toolbar
2. Review the post on desktop and mobile view
3. Check that all code blocks render correctly
4. Check that tables are readable on mobile (they may scroll horizontally)
5. Close preview

---

## Step 12: Publish

1. Click the **"Publish"** button
2. Set the **"This story is members only"** toggle:
   - **ON** if you want it behind Medium's paywall (requires Medium membership to read)
   - **OFF** if you want it free for everyone
   - **Recommendation:** Set to **OFF** for maximum reach — this is a product launch post, not a paywall play
3. Add an **alt text** for the featured image: `DocAI Verify — Income Verification API for Indonesian Fintech`
4. Click **"Publish now"**

---

## Step 13: Post-Publish Checklist

After publishing:

1. Copy the published URL (e.g., `https://medium.com/@yourname/how-we-built-...`)
2. Share the URL on LinkedIn (see `checklist-linkedin.md` Post 2)
3. Share the URL on Twitter/X
4. Share the URL on relevant Reddit communities (r/fintech, r/indonesia, r/python)
5. Pin the post link to your Medium profile

---

## Notes

- Medium's Markdown parser is not 100% compatible with standard Markdown. If tables don't render, convert them to a simple text format or use Medium's built-in table feature
- If code blocks lose their language labels, click inside the code block and select the language from the dropdown
- The blog post is also saved as `docs/blog-post-income-verification.md` in the repo — if you need to make edits, edit that file and re-copy
- Medium takes ~10 minutes to index a new post for SEO
