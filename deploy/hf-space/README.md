---
title: DocAI — Indonesian Bank Statement Parser
emoji: 🏦
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# DocAI — Indonesian Bank Statement Parser

Parse Indonesian bank e-statement PDFs (BCA) into structured JSON or CSV, with
built-in balance validation. Deterministic, zero-LLM-cost.

## Endpoints

- `GET /health` — status + supported banks
- `POST /parse` — multipart `file` (PDF) + `bank` (default `bca`); query `format=json|csv`
- `GET /` — demo page (upload → parse → CSV)

## Example

```bash
curl -X POST https://<user>-docai-api.hf.space/parse \
     -F "file=@statement.pdf" -F "bank=bca"
```
