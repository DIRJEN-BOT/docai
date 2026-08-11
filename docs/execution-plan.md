# DocAI Verify — Revenue Execution Plan (Start Today)

**Last updated:** 2026-08-11  
**Live at:** [docaiid.pythonanywhere.com](https://docaiid.pythonanywhere.com)  
**Demo API Key:** `docai-dev-key-12345`

---

## What's Built

DocAI Verify is a live income verification API at docaiid.pythonanywhere.com that parses BCA and Mandiri bank statement PDFs into structured income data with fraud detection, returning scores in 30–150ms at near-zero cost. 120 tests passing, two bank parsers, a scoring engine, and a WSGI app deployed on PythonAnywhere — ready for production traffic.

---

## Your 45-Minute Launch

### Minute 0–15: RapidAPI Listing

1. Go to [https://rapidapi.com/hub](https://rapidapi.com/hub)
2. Click **My Apps** → **Add New App**
3. Copy-paste the content from [`docs/rapidapi-listing.md`](rapidapi-listing.md) — it contains the title, tagline, description, endpoints, pricing, and sample responses ready to paste
4. Set pricing tiers:
   - **Free** — $0/month — 100 requests/month
   - **Basic** — $9.99/month — 1,000 requests/month
   - **Pro** — $49.99/month — 10,000 requests/month
   - **Business** — $199.99/month — 100,000 requests/month
5. Point the endpoint base URL to `https://docaiid.pythonanywhere.com`
6. Submit for review

---

### Minute 15–25: Medium Blog Post

1. Go to [https://medium.com](https://medium.com)
2. Click **Write** → paste from [`docs/blog-post-income-verification.md`](blog-post-income-verification.md)
3. Add tags: `fintech`, `indonesia`, `api`, `python`, `banking`
4. Set the image to [`assets/promo/docai_banner_linkedin.png`](../assets/promo/docai_banner_linkedin.png)
5. Publish

---

### Minute 25–30: LinkedIn Post 1

Copy-paste this exact text:

```
I just built an income verification API for Indonesian fintech lenders. 🇮🇩

The problem: P2P lenders manually verify bank statements. It's slow, inconsistent, and fraud-prone.

What it does: Upload a BCA/Mandiri statement PDF → get structured income data + verification score in 150ms.

Tech: Deterministic parsing (no LLM), Python, 120 tests, zero cost per document.

Try it free: docaiid.pythonanywhere.com
Source: github.com/DIRJEN-BOT/docai

#fintech #indonesia #api #banking #open-source
```

---

### Minute 30–35: LinkedIn DM #1 — Modalku (Pintar)

1. Go to [https://www.linkedin.com](https://www.linkedin.com)
2. Search for Modalku / Pintar credit risk team members
3. Open [`outreach/sequence-modalku.md`](../outreach/sequence-modalku.md) → copy from **Section 3: LinkedIn Connection Request**:

```
Hi [Name], I noticed Modalku's impressive growth in MSME lending. We've built a tool that turns bank statement PDFs into structured income data in under 150ms — with built-in fraud detection. Would love to share how it fits into Modalku's risk workflow. Happy to connect?
```

4. Send as LinkedIn connection request message

---

### Minute 35–40: LinkedIn DM #2 — KoinWorks

1. Search for KoinWorks risk/credit team members on LinkedIn
2. Open [`outreach/sequence-koinworks.md`](../outreach/sequence-koinworks.md) → copy from **Section 3: LinkedIn Connection Request**:

```
Hi [Name], I saw KoinWorks' journey through OJK's regulatory process — impressive how you've stayed focused on MSME lending. We built a tool that turns bank statement PDFs into structured income data with fraud detection. Would love to share how it fits your risk controls. Happy to connect?
```

3. Send as LinkedIn connection request message

---

### Minute 40–45: GitHub Profile

1. Go to [https://github.com/DIRJEN-BOT/docai](https://github.com/DIRJEN-BOT/docai)
2. Edit the org/repo profile README
3. Paste the content from [`docs/github-profile-section.md`](github-profile-section.md):

```
## 🏦 DocAI Verify — Income Verification API

[![CI](https://github.com/DIRJEN-BOT/docai/actions/workflows/ci.yml/badge.svg)](https://github.com/DIRJEN-BOT/docai/actions)
[![Tests](https://img.shields.io/badge/tests-120%20passing-brightgreen)](https://github.com/DIRJEN-BOT/docai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Parse Indonesian bank e-statement PDFs → income verification score.
BCA + Mandiri live. Zero LLM cost. 30–150ms.

**Try it:** [docaiid.pythonanywhere.com](https://docaiid.pythonanywhere.com)
**API:** POST /verify-income — 100 free verifications/month
**Source:** [github.com/DIRJEN-BOT/docai](https://github.com/DIRJEN-BOT/docai)
```

---

## Week 1 Follow-up Cadence

| Day | Action | Source |
|-----|--------|--------|
| **Day 1** | Send LinkedIn connection requests (Modalku + KoinWorks) | Done above |
| **Day 2** | If connected, send follow-up from sequence files | `outreach/sequence-modalku.md` Section 4, `outreach/sequence-koinworks.md` Section 4 |
| **Day 3** | Post LinkedIn Post 2 — technical deep-dive (pull the first 3 paragraphs from `docs/blog-post-income-verification.md` as a short post) | `docs/blog-post-income-verification.md` |
| **Day 5** | Send WhatsApp to any who connected | `outreach/sequence-modalku.md` Section 5, `outreach/sequence-koinworks.md` Section 5 |
| **Day 7** | Post LinkedIn Post 3 — targeted at P2P lenders (adapt the Medium post intro) | `docs/blog-post-income-verification.md` |
| **Day 10** | Email follow-up | `outreach/sequence-modalku.md` Section 6, `outreach/sequence-koinworks.md` Section 6 |

---

## Week 2–4 Pipeline

1. **Reply to any inbound interest** — respond within 24 hours
2. **Offer 100 free verifications pilot** — reference `outreach/pilot-offer.md` for the exact terms
3. **Set up 1–2 demo calls** — use `fixtures/demo_api_response.json` to show a real API response
4. **Close first paid pilot** — target Rp 5M/month Growth tier (see `outreach/pricing.md` for tier structure)

---

## Success Metrics

| Week | Metric | Target |
|------|--------|--------|
| Week 1 | Connection requests sent | 5 |
| Week 1 | LinkedIn posts published | 1 |
| Week 1 | RapidAPI listing submitted | 1 |
| Week 2 | Conversations started | 2 |
| Week 2 | Demo calls scheduled | 1 |
| Week 4 | Pilot offers accepted | 1 |
| Week 8 | Paid customers | 1 |

---

## If Nothing Happens

1. **Check RapidAPI listing status** — go to [rapidapi.com/hub](https://rapidapi.com/hub) → "My Apps" → check if review is pending or rejected
2. **Post in Indonesian fintech Telegram groups** — search for `P2P lending Indonesia`, `fintech Indonesia` groups, share the LinkedIn post text above
3. **Try Reddit** — cross-post to r/fintech and r/indonesia with the technical blog angle
4. **Try Dev.to cross-post** — paste the Medium post on Dev.to for additional reach
5. **Consider Product Hunt launch** — prepare a Product Hunt listing using the banner assets in `assets/promo/`
6. **Reach out to additional targets** — see `outreach/buyer-list.md` for the full list of 25+ Indonesian lenders, and `outreach/sequence-amartha.md`, `outreach/sequence-akseleran.md`, `outreach/sequence-investree.md` for pre-built outreach sequences

---

## Quick Reference

| Item | Value |
|------|-------|
| Live URL | `https://docaiid.pythonanywhere.com` |
| API Key (dev/demo) | `docai-dev-key-12345` |
| GitHub repo | `https://github.com/DIRJEN-BOT/docai` |
| Test endpoint | `POST /verify-income` |
| Parse endpoint | `POST /parse` |
| Health check | `GET /health` |
| Test suite | `cd C:/Users/MSI/business-exploration/docai && .venv/Scripts/python.exe -m pytest tests/ -q` |
| PA deploy token | `990c5f8cdef64b7ef6ff4f1b6c0d2a0bb72db075` |
| PA reload | `curl -X POST -H "Authorization: Token 990c5f8cdef64b7ef6ff4f1b6c0d2a0bb72db075" https://www.pythonanywhere.com/api/v0/user/docaiid/webapps/docaiid.pythonanywhere.com/reload` |

---

*This plan is a checklist. No research. No strategy. Just do it.*
