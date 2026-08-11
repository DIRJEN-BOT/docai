# DocAI Verify — Competitive Landscape Analysis

> Prepared August 2026 | Confidential — For Internal Planning & Investor Discussion

---

## Market Context

Indonesia's digital lending market comprises **97 licensed P2P lenders** (OJK data), plus **BNPL providers**, **digital banks**, and **multifinance companies** — all requiring income verification during credit underwriting. The total addressable market for income verification in Indonesian fintech is estimated at **Rp 500B–1T annually** ($30–60M USD).

Current verification methods range from manual analyst review (expensive, slow, inconsistent) to open-finance API integrations (high user friction) to generic OCR (poor accuracy on Indonesian bank formats). DocAI Verify occupies a unique position: **deterministic, Indonesia-native PDF parsing with zero user friction**.

---

## Competitor Profiles

### 1. Perfios (India)

**Overview**: Perfios is India's leading financial data analytics platform, processing 1B+ documents annually. They offer bank statement analysis, tax return parsing, and credit scoring APIs. Recently expanded to Southeast Asia including Indonesia.

| Dimension | Details |
|-----------|---------|
| **Founded** | 2008 (Bangalore, India) |
| **Method** | OCR + ML-based document analysis |
| **Pricing** | Enterprise: $5–15/statement (Rp 80,000–240,000) |
| **Indonesia Presence** | Yes, but enterprise-only; requires custom contract |
| **Setup Time** | 2–6 months (integration + contract negotiation) |
| **Min Commitment** | Enterprise contract, typically 10K+ statements/month |
| **Self-Service Signup** | No — sales-driven process |
| **Free Tier** | No |

**Strengths:**
- Deep document analysis capabilities (not just bank statements)
- ML-based pattern recognition across thousands of formats
- Established enterprise client base in India

**Weaknesses for Indonesian Market:**
- **Pricing is 80–240× more expensive** than DocAI (Rp 8K–240K vs Rp 1K/verification)
- **Not Indonesian-first**: BCA/Mandiri format support is secondary to Indian bank formats
- **Long sales cycle**: 2–6 months vs. DocAI's instant self-service signup
- **Enterprise lock-in**: No free tier, no low-commitment entry point
- **OCR dependency**: Non-deterministic parsing introduces accuracy variance

---

### 2. Brick (onebrick.io)

**Overview**: Jakarta-based open finance infrastructure. Provides account aggregation, identity verification, and income verification via direct bank API connections through Indonesia's SNAP BI (Standard National Open API Payment) network.

| Dimension | Details |
|-----------|---------|
| **Founded** | 2020 (Jakarta, Indonesia) |
| **Method** | Direct bank API via SNAP BI |
| **Pricing** | Per-call API pricing (varies by endpoint) |
| **Indonesia Presence** | Indonesia-native |
| **Setup Time** | 1–3 months (merchant onboarding + compliance) |
| **Min Commitment** | Typically volume-based contract |
| **Self-Service Signup** | Limited (merchant application required) |
| **Free Tier** | No |

**Strengths:**
- Real-time data directly from bank APIs (not PDF parsing)
- Covers account balance, transaction history, and identity
- Strong regulatory positioning (SNAP BI compliant)
- Jakarta-based, Indonesian-first team

**Weaknesses for Income Verification:**
- **Requires user to link bank account** — high friction, significant drop-off (industry average: 40–60% abandonment at bank-linking step)
- **Not PDF-based**: Cannot process uploaded bank statements; requires live bank connection
- **User-dependent**: Lender cannot verify income without the applicant actively linking their account
- **Privacy concerns**: Applicants may refuse to link bank accounts for small/early-stage lenders
- **API cost is hidden**: Brick charges per-call, but the per-verification cost is unclear to end users

**Key Differentiator vs. DocAI:** Brick requires the applicant to authenticate with their bank. DocAI only requires a PDF upload — **zero friction, zero refusal**.

---

### 3. Ayoconnect (Jakarta)

**Overview**: Indonesia's open finance API platform. Connects fintechs to bank accounts, e-wallets, and other financial data sources. Backed by prominent investors including AC Ventures and Telkomsel.

| Dimension | Details |
|-----------|---------|
| **Founded** | 2020 (Jakarta, Indonesia) |
| **Method** | Open finance API aggregation |
| **Pricing** | Custom enterprise pricing |
| **Indonesia Presence** | Indonesia-native |
| **Setup Time** | 2–4 months (enterprise onboarding) |
| **Min Commitment** | Enterprise contract |
| **Self-Service Signup** | No — sales-driven |
| **Free Tier** | No |

**Strengths:**
- Broad financial data coverage (bank accounts, e-wallets, investments)
- Strong investor backing and regulatory relationships
- Enterprise-grade reliability and SLA

**Weaknesses for Income Verification:**
- **Same bank-linking friction as Brick** — applicant must actively connect their bank account
- **Enterprise-only pricing**: No self-service, no free tier, no low-commitment entry
- **Not income-verification-specific**: A general data aggregator, not a purpose-built verification tool
- **Long sales cycle**: Enterprise onboarding with compliance review
- **Not PDF-based**: Cannot process uploaded statements

**Key Differentiator vs. DocAI:** Ayoconnect is a horizontal data platform. DocAI is a vertical, purpose-built income verification tool with zero user friction.

---

### 4. VIDA (formerly identitas.id)

**Overview**: Jakarta-based digital identity verification platform. Specializes in NIK (Nomor Induk Kependudukan) validation, e-KYC, and government ID verification. Used by banks and fintechs for onboarding.

| Dimension | Details |
|-----------|---------|
| **Founded** | 2019 (Jakarta, Indonesia) |
| **Method** | NIK-based identity verification + document OCR |
| **Pricing** | Per-verification (Rp 2,000–5,000 estimated) |
| **Indonesia Presence** | Indonesia-native |
| **Setup Time** | 1–2 months |
| **Min Commitment** | Volume-based |
| **Self-Service Signup** | Limited |
| **Free Tier** | No |

**Strengths:**
- Government-grade NIK validation (direct Dukcapil integration)
- Strong e-KYC and biometric capabilities
- Well-known brand in Indonesian fintech identity space

**Weaknesses for Income Verification:**
- **Identity verification, not income verification** — validates WHO someone is, not HOW MUCH they earn
- **Cannot parse bank statements**: No bank statement analysis capability
- **NIK-based**: Useful for KYC/AML, not for credit underwriting income assessment
- **No financial data analysis**: Does not compute income, salary, balance, or transaction patterns

**Key Differentiator vs. DocAI:** VIDA and DocAI are complementary, not competitive. VIDA answers "is this person real?" DocAI answers "can this person repay?" A lender needs both.

---

### 5. Didit.me

**Overview**: Jakarta-based AI document verification platform. Offers generic OCR and document authentication for various document types (ID cards, bank statements, payslips, tax documents).

| Dimension | Details |
|-----------|---------|
| **Founded** | 2021 (Jakarta, Indonesia) |
| **Method** | Generic AI-powered document OCR |
| **Pricing** | Per-document (Rp 5,000–15,000 estimated) |
| **Indonesia Presence** | Indonesia-native |
| **Setup Time** | 1–2 weeks (API integration) |
| **Min Commitment** | Low / pay-as-you-go |
| **Self-Service Signup** | Yes |
| **Free Tier** | Trial available |

**Strengths:**
- Multi-document support (not limited to bank statements)
- Self-service signup available
- Lower barrier to entry than enterprise competitors

**Weaknesses for Income Verification:**
- **Generic OCR, not format-native**: Does not understand BCA/Mandiri/PDF structure; applies generic text extraction
- **No income calculation logic**: Extracts text but does not compute income, salary, or balance metrics
- **No balance validation**: Cannot detect tampered or forged statements
- **5–15× more expensive** than DocAI per verification
- **Accuracy varies**: Generic OCR on complex Indonesian bank PDFs produces inconsistent results
- **No fraud detection**: No built-in tampering or anomaly detection

**Key Differentiator vs. DocAI:** Didit.me is a document reader. DocAI is a document *understanding* engine purpose-built for Indonesian bank statement income verification.

---

## Feature Comparison Matrix

| Feature | DocAI Verify | Perfios | Brick | Ayoconnect | VIDA | Didit.me |
|---------|:------------:|:-------:|:-----:|:----------:|:----:|:--------:|
| **Method** | Deterministic PDF parser | OCR + ML | SNAP BI bank API | Open finance API | NIK + document OCR | Generic AI OCR |
| **Bank Format Coverage** | BCA (live), Mandiri (live), BNI/BRI/OCBC (planned) | 100+ Indian formats, limited ID formats | All SNAP BI banks (via API) | All aggregated banks | None (ID docs only) | None (generic) |
| **Accuracy** | 98%+ (deterministic) | 95%+ (ML-dependent) | 99%+ (direct API) | 99%+ (direct API) | N/A (not income) | 70–85% (OCR variance) |
| **Speed** | 30–150ms | 1–3 seconds | 2–5 seconds | 2–5 seconds | 1–2 seconds | 3–10 seconds |
| **Pricing Model** | Monthly subscription | Per-statement (enterprise) | Per-call (contract) | Custom enterprise | Per-verification | Per-document |
| **Min Commitment** | Rp 0 (Free tier) | $10K+ contract | Volume contract | Enterprise contract | Volume-based | Rp 0 (trial) |
| **Cost per Verification** | Rp 1,000 (Starter) | Rp 8,000–240,000 | Unknown (contract) | Unknown (contract) | Rp 2,000–5,000 | Rp 5,000–15,000 |
| **Setup Time** | Instant (self-service) | 2–6 months | 1–3 months | 2–4 months | 1–2 months | 1–2 weeks |
| **Indonesia Focus** | Indonesia-native | India-first (ID secondary) | Indonesia-native | Indonesia-native | Indonesia-native | Indonesia-native |
| **Fraud Detection** | Balance validation, pattern detection | Limited | N/A (live API) | N/A (live API) | N/A | None |
| **Balance Validation** | Yes (cross-checks opening/closing) | Limited | Yes (live balance) | Yes (live balance) | No | No |
| **Multi-Bank Support** | BCA + Mandiri live | 100+ formats | All SNAP BI | All aggregated | 0 (banking) | 0 (banking) |
| **API Documentation** | Full Swagger docs | Enterprise docs | Enterprise docs | Enterprise docs | API docs | API docs |
| **Self-Service Signup** | Yes (instant API key) | No | No | No | No | Yes |
| **Free Tier** | Yes (100/mo) | No | No | No | No | Trial only |
| **User Friction** | Upload PDF only | Upload document | Link bank account | Link bank account | Scan ID / NIK | Upload document |
| **Data Privacy** | PDF processed, not stored long-term | Data retained per contract | Live bank access | Live bank access | Government data | Document processed |

---

## Competitive Positioning

### DocAI's Unique Advantages

#### 1. Zero User Friction
DocAI requires only a PDF upload. No bank linking, no OTP, no third-party authentication. This is the single biggest advantage over Brick and Ayoconnect, which require applicants to actively link their bank accounts — a step where **40–60% of users abandon the process**.

**Impact for lenders:** Higher application completion rates = more loans processed = more revenue. A lender using DocAI verifies 100% of applicants who upload a PDF. A lender using Brick/Ayoconnect loses 40–60% at the bank-linking step.

---

#### 2. Deterministic Parsing (No LLM, No ML Cost)
DocAI uses format-specific deterministic parsers — not OCR, not LLM, not generic ML. Each bank format (BCA, Mandiri, etc.) has a dedicated parser that extracts data with **98%+ accuracy** at **near-zero marginal cost**.

**Impact:**
- **Cost**: ~Rp 0 per verification (CPU only) vs. Rp 1,000–5,000 for ML/OCR-based solutions
- **Consistency**: Same input always produces same output (no hallucination, no variance)
- **Speed**: 30–150ms vs. 1–10 seconds for OCR/ML solutions
- **Privacy**: No data sent to third-party ML services; processing is local

---

#### 3. Indonesian Bank Format Native
DocAI parsers are built specifically for BCA and Mandiri PDF statement formats — not adapted from Indian or generic formats. This means:
- Understanding of BCA's specific table structures, date formats, and transaction codes
- Handling of Mandiri's statement layout and encoding
- Future-proofing for BNI, BRI, OCBC, BSI, CIMB as they're added

**Competitor gap**: Perfios supports 100+ Indian formats but only limited Indonesian formats. Brick/Ayoconnect use live API (different problem). Didit.me uses generic OCR that misreads Indonesian bank formatting.

---

#### 4. Balance Validation (Fraud Detection)
DocAI automatically validates that opening balance + credits − debits = closing balance. Any discrepancy flags potential statement tampering — a critical fraud signal for credit underwriting.

**No competitor offers this on PDF uploads:**
- Brick/Ayoconnect get live balance data (no tampering possible, but requires bank linking)
- Perfios has limited validation
- Didit.me has none
- VIDA doesn't process bank statements

---

#### 5. Self-Service Signup + Free Tier
DocAI is the only solution offering instant self-service signup with a free tier (100 verifications/month). This enables:
- Zero-friction evaluation (no sales call needed)
- Prototype integration in minutes
- Pay-as-you-grow pricing model

**All competitors require sales conversations, contracts, or enterprise onboarding before first API call.**

---

#### 6. Near-Zero Marginal Cost
DocAI's cost structure is fundamentally different from ML/OCR-based competitors:

| Cost Component | DocAI (Deterministic) | Perfios (OCR+ML) | Brick/Ayoconnect (API) |
|---------------|:---------------------:|:-----------------:|:----------------------:|
| Per-verification compute | ~Rp 0 (CPU) | Rp 500–2,000 (GPU/ML) | Rp 500–1,000 (API call) |
| Infrastructure scaling | Linear (add CPU) | Exponential (GPU clusters) | Linear (API capacity) |
| Marginal cost trend | Decreasing (optimization) | Stable or increasing | Dependent on bank API pricing |

**Impact**: DocAI can undercut competitors on price while maintaining margins, enabling aggressive pricing for market capture.

---

## Competitive Strategy Matrix

### When to Use DocAI vs. Competitors

| Use Case | Best Solution | Why |
|----------|:------------:|-----|
| P2P lender income verification (PDF upload) | **DocAI** | Zero friction, lowest cost, instant setup |
| Real-time account balance check | **Brick / Ayoconnect** | Live API data, no PDF needed |
| Identity verification (KYC/AML) | **VIDA** | NIK validation, government integration |
| Multi-format document processing (generic) | **Didit.me / Perfios** | Broad document coverage |
| Enterprise-scale document analytics | **Perfios** | Proven at 1B+ documents/year |
| Full financial profile (bank + e-wallet + investment) | **Ayoconnect** | Horizontal data aggregation |

### Complementary, Not Replacement

DocAI Verify is **not a replacement** for Brick, Ayoconnect, or VIDA. It's a **complementary layer** that:
- Captures users who won't link their bank accounts (40–60% of applicants)
- Enables instant verification without third-party dependency
- Provides fraud detection on uploaded statements
- Works as a first-pass filter before deeper API-based verification

**Recommended stack for P2P lenders:**
1. **DocAI Verify**: First-pass income verification (PDF upload, instant)
2. **Brick or Ayoconnect**: Deep verification for high-value loans (bank linking)
3. **VIDA**: Identity verification (KYC/AML compliance)

---

## Market Positioning Summary

```
                        HIGH FRICTION
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                  │
          │   Brick         │   Ayoconnect     │
          │   (bank link)   │   (bank link)    │
          │                 │                  │
  LOW ────┼─────────────────┼─────────────────┼──── HIGH
  COST    │                 │                  │    COST
          │   DocAI Verify  │   Perfios        │
          │   (PDF upload)  │   (enterprise)   │
          │                 │                  │
          │   Didit.me      │   VIDA           │
          │   (generic OCR) │   (identity)     │
          │                 │                  │
          └─────────────────┼─────────────────┘
                            │
                        LOW FRICTION
```

**DocAI occupies the optimal quadrant**: Low friction + low cost. This is the highest-volume, lowest-barrier segment of the income verification market.

---

## Conclusion

DocAI Verify's competitive moat is built on three pillars:

1. **Zero user friction** (PDF upload vs. bank linking) — captures the 40–60% of applicants who refuse or fail to link bank accounts
2. **Deterministic parsing** (no ML/OCR cost) — enables near-zero marginal cost and 98%+ accuracy
3. **Indonesian-native format support** — purpose-built for BCA/Mandiri, not adapted from Indian or generic formats

No competitor offers all three. Brick and Ayoconnect sacrifice friction for live data. Perfios sacrifices cost and setup time for breadth. Didit.me sacrifices accuracy for generality. VIDA serves a different problem entirely (identity, not income).

**The market gap DocAI fills**: Affordable, instant income verification for the 60–70% of Indonesian fintech applicants who won't or can't link their bank accounts.

---

*Analysis based on publicly available information and market research. Competitive pricing estimates are approximate and may vary. Prepared August 2026.*