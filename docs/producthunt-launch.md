# Product Hunt Launch — DocAI Verify

## Launch Metadata

- **Tagline:** Bank statement parser for Indonesian fintech
- **Description:** Parse BCA & Mandiri bank statement PDFs into structured income data with fraud detection. Built for Indonesian P2P lenders. 120 tests, deterministic parsing, zero LLM cost. Free tier: 100 verifications/month.
- **Website:** https://docaiid.pythonanywhere.com
- **GitHub:** https://github.com/DIRJEN-BOT/docai
- **Pricing:** Free (100/mo), Starter Rp500K/mo (500), Growth Rp5M/mo (5K), Scale Rp30M/mo (50K), Enterprise custom

## Topics

- `fintech`
- `developer-tools`
- `open-source`
- `python`
- `indonesia`

## First Comment (Maker Comment)

Hey PH! 👋

I built DocAI Verify because I was frustrated watching fintech credit teams manually verify bank statements. It's 2026 and tim credit still scrolls through PDF pages to tally salary deposits.

Here's what DocAI does:
- Upload a BCA or Mandiri bank statement PDF
- Get structured income data + verification score in 150ms
- Built-in fraud detection (balance mismatch, suspicious patterns)

Why it's different:
- 🇮🇩 Indonesia-first — built for BCA/Mandiri formats, not generic
- 🔍 Deterministic — no LLM calls, consistent results, ~Rp0 per doc
- 🧪 120 tests — we take accuracy seriously
- 🔓 Open source — MIT licensed

The free tier gives you 100 verifications/month. No credit card, no signup friction.

I'd love feedback on:
1. Would you use this in your lending workflow?
2. Which bank should I add next? (BNI, BRI, Mandiri legacy)
3. What's missing for you to integrate this?

Try it: docaiid.pythonanywhere.com
GitHub: github.com/DIRJEN-BOT/docai

**Image:** `assets/promo/docai_banner_linkedin.png` (attach to first comment)

## Visual Assets

- **Thumbnail/logo:** `assets/logo_docai_400.png`
- **Gallery image:** `assets/promo/docai_banner_linkedin.png`
- **Optional gallery:** Screenshot of the API response or landing page demo

## Topics Checklist

- [x] `fintech` — core use case
- [x] `developer-tools` — API-first, importable Postman collection
- [x] `open-source` — MIT licensed, GitHub public
- [x] `python` — pure Python, no external services
- [x] `indonesia` — built specifically for Indonesian banks

## Launch Day Checklist

### Pre-Launch (Day Before)

- [ ] Submit to Product Hunt with all fields above
- [ ] Upload visual assets (logo + banner)
- [ ] Schedule for midnight PT (Product Hunt resets daily)
- [ ] Prepare Twitter/X thread with demo GIF
- [ ] Notify 5–10 friends to upvote + comment early
- [ ] Post in relevant communities (Indonesian dev groups, fintech Slack/Discord)

### Launch Day (Day Of)

- [ ] Reply to every comment within 30 minutes
- [ ] Share on Twitter/X at 9 AM PT (peak engagement)
- [ ] Post on LinkedIn with the maker story
- [ ] Cross-post the blog to dev.to
- [ ] Update GitHub repo description with PH badge
- [ ] Monitor API for any spikes (free tier should handle it)

### Post-Launch (Day After)

- [ ] Write thank-you post summarizing feedback
- [ ] Create GitHub issue for "BNI parser" (most-requested bank)
- [ ] Follow up with anyone who commented about integration
- [ ] Track: signups, API calls, GitHub stars

## Twitter/X Thread Draft

**Tweet 1:**
We just launched DocAI Verify on @ProductHunt 🇮🇩

Parse BCA & Mandiri bank statement PDFs → structured income data + fraud score in 150ms.

No LLM. No OCR. No cost. 120 tests.

Free tier: 100 verifications/month

🔗 [PH link]

**Tweet 2:**
The problem: Indonesian P2P lenders still have tim credit manually scroll through PDF bank statements to verify income.

We built a deterministic parser that does it in 30–150ms for ~Rp0 per document.

[150ms response GIF/demo]

**Tweet 3:**
What makes it different:

🇮🇩 Built for BCA/Mandiri formats specifically
🔍 Deterministic — same input = same output, always
🧪 120 tests, 100% balance-check pass rate
🔓 MIT licensed, self-hostable

No API keys to manage. No per-document token fees.

**Tweet 4:**
Tech stack:
- Python (pure, no ML dependencies)
- pypdf for extraction
- Regex + number parsing (not OCR)
- Statistical scoring (CV-based consistency)

Zero GPU. Zero LLM. Zero COGS.

**Tweet 5:**
The scoring engine produces:
- Verification score (0–100)
- Detected monthly income + source
- Income consistency score
- Fraud flags (balance mismatch, round-number concentration, etc.)
- Monthly income breakdown

All deterministic. All auditable.

**Tweet 6:**
Try it now → docaiid.pythonanywhere.com

100 free verifications/month. No credit card.

GitHub: github.com/DIRJEN-BOT/docai

We're looking for feedback:
1. Which bank should we add next?
2. What's missing for integration?
3. Would you use this in your lending workflow?
