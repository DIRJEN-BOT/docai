# LinkedIn Announcement Checklist — DocAI Verify

Step-by-step instructions to post 3 LinkedIn announcements. All posts below are copy-paste ready. Post them in the order listed, spaced 1–3 days apart.

---

## Pre-Post Setup

Before posting, ensure:

1. You are signed in to LinkedIn
2. Your LinkedIn profile has a professional headline (e.g., "Founder @ DocAI | Building income verification APIs for Indonesian fintech")
3. You have at least 50+ connections (for initial visibility)
4. Your profile photo is current and professional

---

## Post 1: Personal Announcement (Product Launch)

### Timing
- Post on a **Tuesday–Thursday** morning (9–11 AM WIB / Jakarta time)
- Best for: your personal network, fintech contacts, developer connections

### Post Text

Copy and paste this **entire block** into the LinkedIn composer:

---

I just built an income verification API for Indonesian fintech lenders. 🇮🇩

The problem: P2P lenders manually verify bank statements. It's slow, inconsistent, and fraud-prone.

What it does: Upload a BCA/Mandiri statement PDF → get structured income data + verification score in 150ms.

Tech: Deterministic parsing (no LLM), Python, 120 tests, zero cost per document.

Try it free: docaiid.pythonanywhere.com
Source: github.com/oyi77/docai

#fintech #indonesia #api #banking #open-source

---

### Hashtags (included in the post above)
- `#fintech`
- `#indonesia`
- `#api`
- `#banking`
- `#open-source`

### Image
- Use the LinkedIn banner image: `assets/promo/docai_banner_linkedin.png`
- Upload as an image attachment to the post (not as a link preview)
- Image dimensions: 1200×630px

### Notes
- This is a short, punchy post. Do NOT add more text — brevity works on LinkedIn.
- The 🇮🇩 emoji helps with visibility in Indonesian fintech circles.
- After posting, comment on your own post with a follow-up to boost engagement:

  ```
  "100 free verifications/month. No credit card required. Happy to walk anyone through the API docs."
  ```

---

## Post 2: Technical Deep-Dive (Developer Audience)

### Timing
- Post 1–3 days after Post 1
- Post on a **Wednesday–Friday** morning (9–11 AM WIB / Jakarta time)
- Best for: developer communities, tech recruiters, open-source enthusiasts

### Post Text

Copy and paste this **entire block** into the LinkedIn composer:

---

I wrote up the technical details behind the income verification API I built for Indonesian fintech lenders.

Key decisions:
- Deterministic parsing (regex, not LLM) for consistency and zero COGS
- Balance-based debit/credit detection — the bank's own running balance tells the truth
- Salary detection via keyword matching + recurring amount analysis
- Fraud detection built in: balance mismatch, round-number anomalies, duplicate transactions

The scoring engine weighs 4 dimensions: balance validation, income source, consistency, and fraud signals → composite score 0–100.

Full write-up: [paste the Medium article URL here after publishing]

API: docaiid.pythonanywhere.com
Source: github.com/oyi77/docai

#python #fintech #api #indonesia #open-source

---

### Hashtags (included in the post above)
- `#python`
- `#fintech`
- `#api`
- `#indonesia`
- `#open-source`

### Before Posting
- **IMPORTANT:** Replace `[paste the Medium article URL here after publishing]` with the actual URL of the Medium article from `checklist-medium.md`
- The Medium article URL format: `https://medium.com/@yourname/how-we-built-an-income-verification-api-...`

### Image
- Use the LinkedIn banner image: `assets/promo/docai_banner_linkedin.png`
- Or use the social preview image if available: `docai-social-preview.png`

### Notes
- This post targets developers who care about the "how" — not just the "what"
- The bullet points in the post are copy-paste ready and explain the technical approach
- After posting, add a follow-up comment with the API response JSON (from `outreach/demo-response.json`):

  ```
  "Here's what the API returns from a BCA e-statement:

  {
    \"verification_score\": 82,
    \"confidence\": \"high\",
    \"detected_monthly_income\": 12500000,
    \"income_source\": \"salary\",
    \"consistency_score\": 95,
    \"balance_valid\": true
  }

  120 tests. 30–150ms. Zero LLM cost."
  ```

---

## Post 3: Targeted Post for P2P Lending Audience

### Timing
- Post 3–5 days after Post 2 (or 5–8 days after Post 1)
- Post on a **Monday–Wednesday** morning (9–11 AM WIB / Jakarta time)
- Best for: P2P lending professionals, fintech founders, credit analysts

### Post Text

Copy and paste this **entire block** into the LinkedIn composer:

---

Building credit scoring tools for Indonesian lenders. If you're in P2P lending and still manually verifying bank statements, I built something for you.

100 free verifications/month. API at docaiid.pythonanywhere.com

---

### Hashtags (included in the post above)
- `#fintech`
- `#indonesia`
- `#p2p-lending`
- `#credit-scoring`

### Image
- Use the LinkedIn banner image: `assets/promo/docai_banner_linkedin.png`

### Notes
- This post is intentionally short and direct — it targets P2P lending professionals who need a solution, not a tech breakdown
- The "100 free verifications/month" is the key hook — it removes the barrier to entry
- After posting, add a follow-up comment with a brief use case:

  ```
  "Use case: A P2P lender in Jakarta processes 500 loan applications/month. Each requires manual bank statement verification. With DocAI Verify, they upload the PDF and get a structured income report in 150ms — including salary detection, consistency scoring, and fraud flags. 100/month free, then $9.99/month for 1,000."
  ```

---

## Post 4 (Optional): Social Proof Post

### Timing
- Post 1–2 weeks after Post 3
- Post when you have any user feedback or test results

### Post Text

Copy and paste this **entire block** into the LinkedIn composer:

---

DocAI Verify — one month in.

Quick stats:
- 120 tests passing
- 30–150ms response time
- Zero LLM cost per document
- 100% balance-check pass rate

If you're building lending or credit scoring tools for the Indonesian market, the API is free to try:

docaiid.pythonanywhere.com

#fintech #indonesia #api #open-source

---

### Notes
- This post reinforces the product's reliability and performance
- Update with real metrics as they come in (e.g., number of API calls, user count)
- If you get any user testimonials or feedback, add a quote to this post

---

## Cross-Posting Checklist

After posting on LinkedIn, share the posts on:

1. **Twitter/X** — Repurpose Post 1 as a tweet (keep it under 280 characters):
   ```
   Built an income verification API for Indonesian fintech lenders.

   Upload BCA/Mandiri statement PDF → structured income data + verification score in 150ms.

   Deterministic (no LLM). Zero cost/doc. 100 free/month.

   docaiid.pythonanywhere.com
   github.com/oyi77/docai

   #fintech #indonesia #api
   ```

2. **Reddit** — Post in r/fintech, r/indonesia, r/python (if relevant)
3. **Dev.to** — Republish the blog post (Medium cross-post) with a note that it's a republish
4. **Hacker News** — Submit as "Show HN" (only if you have traction)

---

## Engagement Strategy

After each post:

1. **Reply to every comment** within 24 hours (even if it's just "Thanks!")
2. **Like and comment** on 5–10 related posts in the fintech/developer space (build visibility)
3. **Share to relevant LinkedIn groups** (e.g., "Indonesian Fintech", "Open Source Indonesia", "Python Developers")
4. **Pin the post** to your LinkedIn profile if it gets good engagement

---

## Image Assets Reference

| Image | Path | Dimensions | Use |
|-------|------|-----------|-----|
| LinkedIn banner | `assets/promo/docai_banner_linkedin.png` | 1200×630 | Post 1, 2, 3 image |
| Twitter banner | `assets/promo/docai_banner_twitter.png` | 1600×900 | Twitter/X post image |
| Square banner | `assets/promo/docai_banner_square.png` | 1080×1080 | Instagram/Telegram |
| Social preview | `docai-social-preview.png` (from docs) | 1280×640 | GitHub, Open Graph |

---

## Notes

- LinkedIn posts get 2–3x more reach on weekday mornings (Tuesday–Thursday)
- The 3-post sequence is designed to cover: (1) product launch, (2) technical credibility, (3) targeted audience
- The optional Post 4 reinforces reliability with metrics
- **DO NOT** post all 3 at once — space them 1–5 days apart for maximum algorithmic reach
- After posting, track engagement (likes, comments, profile views) to see which post resonates most
- If Post 1 gets strong engagement, boost it with a LinkedIn paid promotion (optional)
