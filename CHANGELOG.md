# Changelog

All notable changes to DocAI Verify will be documented in this file.

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
