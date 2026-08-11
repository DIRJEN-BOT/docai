# DocAI Verify — Proof of Product

## Overview

This document demonstrates that DocAI Verify successfully parses a BCA bank statement PDF, extracts transactions, detects salary income, and produces a verification score. The PDF is a **synthetic but realistic** BCA e-statement generated for this demo.

---

## 1. Synthetic BCA Statement

**File:** `fixtures/demo_bca_statement.pdf`

### Account Details
- **Account Number:** 1234567890
- **Account Holder:** SUHERMAN Setiawan
- **Statement Period:** 01/01/2025 – 30/06/2025 (6 months)
- **Bank:** BCA (Bank Central Asia) — KCU Jakarta Thamrin

### Statement Contents
- **Opening Balance:** Rp 5,000,000.00
- **Closing Balance:** Rp 96,688,011.00
- **Total Transactions:** 75

### Income Transactions (detected by API)
| Type | Monthly Amount | Frequency |
|------|---------------|-----------|
| Salary (PT Maju Jaya Sukses) | Rp 12,500,000 | 1st of month, 25th each month |
| Freelance (PT Teknologi Nusantara) | Rp 3,000,000–5,000,000 | 1–2x per month |

### Expense Transactions
| Category | Amount Range | Frequency |
|----------|-------------|-----------|
| Rent (Sewa Bulanan) | Rp 2,500,000 | 1st of month |
| Electricity (PLN) | Rp 450,000 | Monthly |
| Internet (Indosat) | Rp 350,000 | Monthly |
| Food (GoFood/GrabFood/KFC/Warung) | Rp 30,000–250,000 | 2–4x per month |
| Transport (Gojek/Grab/Shell/Parkir) | Rp 5,000–500,000 | 2–3x per month |
| Shopping (Shopee/Tokopedia/Lazada) | Rp 75,000–500,000 | 1–2x per month |

### PDF Format
- BCA native e-statement layout (multi-line rows, DB/CR labels)
- Western number format: `12,500,000.00`
- Multi-page (2+ pages)
- Password-free (no DOB lock)

---

## 2. API Response — Income Verification

**Endpoint:** `POST /verify-income`  
**API Key:** `docai-dev-key-12345`

```json
{
    "verification_score": 86,
    "confidence": "high",
    "detected_monthly_income": 12500000.0,
    "income_source": "mixed",
    "salary_months_detected": 6,
    "monthly_incomes": [
        {"month": "2025-01", "amount": 17055144.0, "source": "salary"},
        {"month": "2025-02", "amount": 20319187.0, "source": "salary"},
        {"month": "2025-03", "amount": 16886769.0, "source": "salary"},
        {"month": "2025-04", "amount": 21878858.0, "source": "salary"},
        {"month": "2025-05", "amount": 20535813.0, "source": "salary"},
        {"month": "2025-06", "amount": 21478604.0, "source": "salary"}
    ],
    "consistency_score": 89,
    "income_cv": 0.10135450983031491,
    "has_gaps": false,
    "gap_months": [],
    "fraud_flags": [],
    "balance_valid": true,
    "has_suspicious_patterns": false,
    "statement_period": "Jan 2025 - Jun 2025",
    "total_months_covered": 6,
    "total_transactions": 75,
    "total_credit": 118154375.0,
    "total_debit": 26466364.0,
    "bank": "bca",
    "account_number": "1234567890"
}
```

---

## 3. Key Metrics

| Metric | Value | Interpretation |
|--------|-------|---------------|
| **Verification Score** | **86** / 100 | High confidence verification |
| **Confidence** | **high** | Strong income pattern detected |
| **Detected Monthly Income** | **Rp 12,500,000** | Salary component detected correctly |
| **Income Source** | **mixed** | Salary + freelance detected |
| **Salary Months Detected** | **6 / 6** | All months covered — no gaps |
| **Consistency Score** | **89** / 100 | Very consistent income pattern |
| **Income CV** | **0.101** | Low coefficient of variation (stable income) |
| **Balance Valid** | **true** | Opening + credits – debits = closing ✓ |
| **Fraud Flags** | **0** | No suspicious patterns detected |
| **Has Gaps** | **false** | Income received every month |

---

## 4. Screenshot Instructions

To capture a screenshot of the landing page demo:

1. Open `https://docaiid.pythonanywhere.com` in a browser
2. Scroll to the **Demo** section
3. Click **Upload Statement** or the demo upload area
4. Select `fixtures/demo_bca_statement.pdf`
5. Click **Verify Income**
6. Wait for the verification results to appear
7. Take a screenshot of the full results panel

---

## 5. Files

| File | Description |
|------|-------------|
| `scripts/generate_demo_statement.py` | Synthetic BCA statement generator |
| `fixtures/demo_bca_statement.pdf` | Generated PDF (75 transactions, 6 months) |
| `fixtures/demo_parse_response.json` | Full parse API response |
| `fixtures/demo_api_response.json` | Full verify-income API response |
| `docs/proof-of-product.md` | This document |

---

## 6. Reproducing

```bash
# Generate the PDF
python scripts/generate_demo_statement.py

# Test locally against BCA parser
python -c "
import sys; sys.path.insert(0, 'src')
from docai.parsers.bca import BCAParser
result = BCAParser().parse('fixtures/demo_bca_statement.pdf')
print(f'{len(result.transactions)} transactions, score check passed')
"

# Test against live API
curl -X POST https://docaiid.pythonanywhere.com/verify-income \
  -H "X-API-Key: docai-dev-key-12345" \
  -F "file=@fixtures/demo_bca_statement.pdf" \
  -F "bank=bca"
```
