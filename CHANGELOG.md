# Changelog

All notable changes to DocAI Verify will be documented in this file.

## [Unreleased] - 2026-08-11

### Added
- Revenue projections (3 scenarios, 12-month forecast)
- Competitor comparison (DocAI vs Perfios, Brick, Ayoconnect, VIDA, Didit.me)
- RapidAPI listing (copy-paste ready)
- Elevator pitch (LinkedIn, email, WhatsApp, meeting variants)
- Demo script (15-minute sales call walkthrough)
- 8 new outreach sequences (Kredivo, Akulaku, Home Credit, Bank Jago, DANA, BCA Finance, Mandiri Tunas, Qoala)
- Master outreach tracker (25 companies)

## [2.0.0] — 2026-08-11

### Added
- Income verification scoring engine (`scoring.py`): salary detection (keyword + round-number heuristics), income consistency scoring (coefficient of variation), fraud signal detection (balance mismatch, suspicious patterns, short statements)
- `POST /verify-income` endpoint — parse + score in one call, returns `IncomeReport`
- Mandiri modern Livin' parser (2023+ format): bilingual headers, sign-based amounts, pipe-separated lines
- API key authentication (`X-API-Key` header) with per-tier rate limiting
- `password` parameter for DOB-protected BCA PDFs (auto-decrypt and retry)
- 57 new tests: scoring engine (16), Mandiri parser (28), enhanced API with auth/verify-income (13)

### Changed
- Repositioned from "parser tool" to "Income Verification API"
- Updated landing page for DocAI Verify positioning
- Updated README with new endpoints, pricing, and architecture diagram
- RapidAPI listing rewritten for income verification use case

### Fixed
- N/A (first release of v2.0.0)

## [1.0.0] — 2026-08-10

### Added
- BCA e-statement parser (native + synthetic formats)
- Balance validation suite (3-tier: aggregate, debit/credit non-negative, running balance)
- `POST /parse` endpoint with JSON and CSV output
- `GET /health` endpoint
- CLI tool (`docai parse`, `docai banks`)
- PythonAnywhere deployment
- 59 initial tests (parsers, validation, CLI, API, fixtures)
