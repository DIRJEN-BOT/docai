# DocAI Verify — 12-Month Revenue Projections

> Prepared August 2026 | Confidential — For Internal Planning & Investor Discussion

---

## Executive Summary

DocAI Verify is an income verification API for the Indonesian fintech lending market. With a deterministic PDF parser (no LLM costs), near-zero marginal cost per verification, and a total addressable market of 97+ licensed P2P lenders plus BNPL, digital banks, and multifinance companies, the path to profitability is rapid.

This document models three scenarios over 12 months, projecting Monthly Recurring Revenue (MRR), cumulative revenue, customer acquisition, and churn dynamics.

---

## Key Assumptions

### Pricing (Monthly Subscription)

| Tier | Monthly Price | Verifications Included | Per-Verification Cost |
|------|--------------|----------------------|----------------------|
| Free | Rp 0 | 100 | Rp 0 |
| Starter | Rp 500,000 | 500 | Rp 1,000 |
| Growth | Rp 3,500,000 | 5,000 | Rp 700 |
| Scale | Rp 15,000,000 | 50,000 | Rp 300 |
| Enterprise | Custom (est. Rp 25M+) | Unlimited | Negotiable |

### Cost Structure

| Cost Item | Monthly | Notes |
|-----------|---------|-------|
| Infrastructure (PythonAnywhere) | Rp 75,000 | ~$5/mo, scales to millions of calls |
| Domain & SSL | Rp 10,000 | Amortized annually |
| Customer acquisition (blended) | Rp 800,000/customer | 60% organic (Rp 0) + 40% paid (Rp 2M) |
| Founder time (opportunity cost) | Rp 5,000,000 | Full-time equivalent |
| **Total fixed overhead** | **~Rp 5,100,000/mo** | |

### Unit Economics Definitions

- **Churn rate**: Applied monthly to total MRR (net revenue retention).
- **CAC (Customer Acquisition Cost)**: Blended average Rp 800K/customer (60% organic, 40% paid at Rp 2M).
- **LTV (Lifetime Value)**: MRR per tier × (1 ÷ churn rate).
- **Payback period**: CAC ÷ monthly MRR per customer.

---

## Scenario 1: Conservative

> Slow pipeline build, high early churn. Proves unit economics under pressure.

**Assumptions:** 15% monthly churn, no paying customers in Months 1–2, mix of Starter/Growth from Month 3, adding 2–3 customers/month in second half.

| Month | New Customers | Churned | Active Customers | Net New MRR | MRR (Rp) | Cumulative Revenue (Rp) |
|-------|:------------:|:-------:|:----------------:|:-----------:|----------:|------------------------:|
| 1 | 0 | 0 | 0 | — | 0 | 0 |
| 2 | 0 | 0 | 0 | — | 0 | 0 |
| 3 | 2S | 0 | 2 | +1,000,000 | 1,000,000 | 1,000,000 |
| 4 | 1S | 0 | 3 | +500,000 | 1,350,000 | 2,350,000 |
| 5 | 1S + 1G | 0 | 5 | +4,000,000 | 5,148,000 | 7,498,000 |
| 6 | 1S | 1 | 5 | +500,000 | 4,876,000 | 12,374,000 |
| 7 | 1S + 1G | 1 | 6 | +4,000,000 | 8,145,000 | 20,519,000 |
| 8 | 1S + 1G | 1 | 7 | +4,000,000 | 10,923,000 | 31,442,000 |
| 9 | 2S + 1G | 2 | 8 | +4,500,000 | 13,785,000 | 45,227,000 |
| 10 | 1S + 1G | 2 | 8 | +4,000,000 | 15,717,000 | 60,944,000 |
| 11 | 2S + 1G | 2 | 9 | +4,500,000 | 17,859,000 | 78,803,000 |
| 12 | 1S + 1G | 3 | 8 | +4,000,000 | 19,180,000 | 97,983,000 |

**Conservative 12-Month Totals:**

| Metric | Value |
|--------|-------|
| Month 12 MRR | Rp 19,180,000 (~$1,150) |
| 12-Month Cumulative Revenue | Rp 97,983,000 (~$5,900) |
| Total Customers Acquired | 20 |
| Total Customers Churned | 12 |
| Net Active Customers (Month 12) | 8 |
| Infra Cost Covered By | Month 1 (first paying customer) |
| Overhead Cost Covered By | Month 5 |

---

## Scenario 2: Base

> Steady growth with strong second half. One Scale deal closes in H2.

**Assumptions:** 10% monthly churn, 3 Starter + 1 Growth at Month 3, 3–4 new customers/month in M4–6, 4–6/month in M7–12 plus 1 Scale deal.

| Month | New Customers | Churned | Active Customers | Net New MRR | MRR (Rp) | Cumulative Revenue (Rp) |
|-------|:------------:|:-------:|:----------------:|:-----------:|----------:|------------------------:|
| 1 | 0 | 0 | 0 | — | 0 | 0 |
| 2 | 0 | 0 | 0 | — | 0 | 0 |
| 3 | 3S + 1G | 0 | 4 | +5,000,000 | 5,000,000 | 5,000,000 |
| 4 | 2S + 2G | 0 | 8 | +8,000,000 | 12,500,000 | 17,500,000 |
| 5 | 2S + 2G | 1 | 9 | +8,000,000 | 19,250,000 | 36,750,000 |
| 6 | 1S + 3G | 2 | 10 | +11,000,000 | 28,325,000 | 65,075,000 |
| 7 | 2S + 3G | 3 | 11 | +11,500,000 | 36,993,000 | 102,068,000 |
| 8 | 1S + 2G + 1Sc | 4 | 12 | +22,000,000 | 55,293,000 | 157,361,000 |
| 9 | 2S + 3G | 5 | 13 | +11,500,000 | 61,264,000 | 218,625,000 |
| 10 | 1S + 3G | 6 | 13 | +11,000,000 | 66,137,000 | 284,762,000 |
| 11 | 2S + 3G + 1Sc | 7 | 14 | +26,500,000 | 86,024,000 | 370,786,000 |
| 12 | 2S + 4G | 9 | 13 | +15,000,000 | 92,421,000 | 463,207,000 |

**Base 12-Month Totals:**

| Metric | Value |
|--------|-------|
| Month 12 MRR | Rp 92,421,000 (~$5,550) |
| 12-Month Cumulative Revenue | Rp 463,207,000 (~$27,800) |
| Total Customers Acquired | 34 |
| Total Customers Churned | 21 |
| Net Active Customers (Month 13) | 13 |
| Infra Cost Covered By | Month 1 (first paying customer) |
| Overhead Cost Covered By | Month 3 |

---

## Scenario 3: Aggressive

> Early Enterprise traction, fast market capture. Multiple Scale + Enterprise deals in H2.

**Assumptions:** 8% monthly churn, 1 Growth customer in Month 1, rapid ramp to 8–12 customers/month in M7–12, Enterprise pilots from M4, multiple Scale deals in H2.

| Month | New Customers | Churned | Active Customers | Net New MRR | MRR (Rp) | Cumulative Revenue (Rp) |
|-------|:------------:|:-------:|:----------------:|:-----------:|----------:|------------------------:|
| 1 | 1G | 0 | 1 | +3,500,000 | 3,500,000 | 3,500,000 |
| 2 | 3S + 2G | 0 | 6 | +8,500,000 | 11,720,000 | 15,220,000 |
| 3 | 4S + 2G | 1 | 9 | +9,000,000 | 19,782,000 | 35,002,000 |
| 4 | 3S + 3G + 1E | 2 | 13 | +19,000,000 | 37,200,000 | 72,202,000 |
| 5 | 4S + 3G | 3 | 16 | +12,500,000 | 46,724,000 | 118,926,000 |
| 6 | 3S + 3G + 1E | 4 | 18 | +19,000,000 | 61,986,000 | 180,912,000 |
| 7 | 4S + 4G + 1E | 5 | 20 | +33,500,000 | 90,527,000 | 271,439,000 |
| 8 | 4S + 4G + 1E | 9 | 22 | +33,500,000 | 116,785,000 | 388,224,000 |
| 9 | 4S + 4G + 1Sc | 12 | 23 | +39,000,000 | 146,443,000 | 534,667,000 |
| 10 | 3S + 5G + 1E | 13 | 25 | +31,000,000 | 165,727,000 | 700,394,000 |
| 11 | 4S + 5G + 1Sc | 14 | 27 | +44,000,000 | 196,469,000 | 896,863,000 |
| 12 | 4S + 5G + 1E | 16 | 28 | +31,000,000 | 211,752,000 | 1,108,615,000 |

**Aggressive 12-Month Totals:**

| Metric | Value |
|--------|-------|
| Month 12 MRR | Rp 211,752,000 (~$12,700) |
| 12-Month Cumulative Revenue | Rp 1,108,615,000 (~$66,500) |
| Total Customers Acquired | 50 |
| Total Customers Churned | 22 |
| Net Active Customers (Month 13) | 28 |
| Infra Cost Covered By | Month 1 |
| Overhead Cost Covered By | Month 1 |

---

## Scenario Comparison

| Metric | Conservative | Base | Aggressive |
|--------|:----------:|:----:|:----------:|
| **Month 12 MRR** | Rp 19.2M | Rp 92.4M | Rp 211.8M |
| **12-Month Cumulative** | Rp 98.0M | Rp 463.2M | Rp 1,108.6M |
| **Total Customers Acquired** | 20 | 34 | 50 |
| **Net Active (Month 12)** | 8 | 13 | 28 |
| **Monthly Churn Rate** | 15% | 10% | 8% |
| **Year-End ARR (est.)** | Rp 230M | Rp 1,109M | Rp 2,541M |
| **Avg Revenue/Customer** | Rp 2.4M | Rp 7.1M | Rp 7.6M |

---

## Unit Economics

### Lifetime Value (LTV) by Tier

| Tier | MRR | Conservative (15% churn) | Base (10% churn) | Aggressive (8% churn) |
|------|-----|:------------------------:|:-----------------:|:---------------------:|
| Starter | Rp 500,000 | Rp 3,333,333 | Rp 5,000,000 | Rp 6,250,000 |
| Growth | Rp 3,500,000 | Rp 23,333,333 | Rp 35,000,000 | Rp 43,750,000 |
| Scale | Rp 15,000,000 | Rp 100,000,000 | Rp 150,000,000 | Rp 187,500,000 |
| Enterprise (est.) | Rp 25,000,000 | Rp 166,666,667 | Rp 250,000,000 | Rp 312,500,000 |

### Customer Acquisition Cost (CAC)

| Acquisition Channel | Cost/Customer | % of Mix | Blended CAC |
|-------------------:|:-------------:|:--------:|:-----------:|
| Organic (outbound DM, referral, content) | Rp 0 | 60% | — |
| Paid (LinkedIn Ads, SEM, events) | Rp 2,000,000 | 40% | — |
| **Blended CAC** | — | — | **Rp 800,000** |

### LTV:CAC Ratio

| Tier | Conservative | Base | Aggressive |
|------|:----------:|:----:|:----------:|
| Starter | 4.2x | 6.3x | 7.8x |
| Growth | 29.2x | 43.8x | 54.7x |
| Scale | 125.0x | 187.5x | 234.4x |
| Enterprise | 208.3x | 312.5x | 390.6x |

> **Benchmark**: LTV:CAC > 3x is healthy; > 5x is excellent. Every tier exceeds 3x under all scenarios. Growth and above exceed 20x — indicating the business is highly capital-efficient.

### Payback Period (CAC ÷ Monthly Revenue per Customer)

| Tier | Monthly Revenue | Payback Period |
|------|:--------------:|:--------------:|
| Starter | Rp 500,000 | 1.6 months |
| Growth | Rp 3,500,000 | < 1 month (immediate) |
| Scale | Rp 15,000,000 | < 1 month (immediate) |
| Enterprise | Rp 25,000,000 | < 1 month (immediate) |

> All non-Free tiers pay back CAC within 2 months. Growth+ tiers are profitable from Month 1 of the customer relationship.

---

## Break-Even Analysis

### Monthly Cost Base

| Category | Monthly (Rp) | Notes |
|----------|-------------|-------|
| Infrastructure | 75,000 | PythonAnywhere free-to-paid tier |
| Domain + SSL | 10,000 | Amortized |
| **Total fixed cost** | **85,000** | Excluding founder salary |
| Founder opportunity cost | 5,000,000 | Market-rate salary equivalent |

### Break-Even Points

| Scenario | Covers Infra (Rp 85K) | Covers Infra + Salary (Rp 5.085M) |
|----------|:---------------------:|:----------------------------------:|
| Conservative | Month 3 | Month 5 |
| Base | Month 3 | Month 3 |
| Aggressive | Month 1 | Month 1 |

> Even in the Conservative scenario, infrastructure costs are covered by the first paying customer. Full founder salary coverage is reached by Month 5.

---

## Revenue Sensitivity Analysis

### What If Churn Is Lower Than Projected?

| MRR at Month 12 | 8% churn | 10% churn | 15% churn | 20% churn |
|-----------------|:--------:|:---------:|:---------:|:---------:|
| Conservative (same acquisitions) | Rp 24.5M | Rp 19.2M | Rp 14.8M | Rp 11.2M |
| Base (same acquisitions) | Rp 115.0M | Rp 92.4M | Rp 63.0M | Rp 42.5M |
| Aggressive (same acquisitions) | Rp 260.0M | Rp 211.8M | Rp 140.0M | Rp 95.0M |

### What If Average Tier Mix Shifts?

If customer acquisition skews toward Growth tier (realistic with P2P lender pipeline):

| Mix (Starter:Growth) | Base Scenario MRR (M12) | Change vs. Base |
|:--------------------:|:-----------------------:|:--------------:|
| 70:30 (current model) | Rp 92.4M | — |
| 50:50 | Rp 118.6M | +28% |
| 30:70 | Rp 144.8M | +57% |

> Even modest shifts toward higher tiers dramatically impact MRR because Growth tier is 7× Starter pricing.

---

## Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **High churn in Starter tier** | Revenue volatility | Onboard with success team, show ROI in first 2 weeks |
| **Slow Enterprise sales cycle** | Aggressive scenario miss | Focus on Starter/Growth self-service; Enterprise as upside |
| **Bank format changes** | Parser breakage, accuracy drop | Version tracking, automated regression tests, fast hotfix pipeline |
| **Competitor enters with SNAP BI** | Brick/Ayoconnect undercut on friction | Emphasize PDF upload = zero friction (no bank linking required) |
| **Regulatory change (PSDKP/OJK)** | Potential mandate or restriction | Position as OJK-compliant; monitor regulatory pipeline |
| **Single-bank dependency (BCA only)** | TAM limitation | Mandiri live; BNI/BRI/OCBC in pipeline (see Roadmap) |

---

## Investment Ask (If Applicable)

| Use of Funds | Allocation | Purpose |
|-------------|:----------:|---------|
| Engineering (bank parsers) | 40% | BNI, BRI, OCBC, BSI, CIMB expansion |
| Sales & Marketing | 30% | Outbound team, events, content, LinkedIn Ads |
| Infrastructure | 15% | Dedicated hosting, SLA guarantees, monitoring |
| Legal & Compliance | 15% | OJK registration, data protection, contracts |

---

## Appendix: Monthly Detail (Base Scenario)

| Month | Starter (count) | Growth (count) | Scale (count) | Enterprise (count) | Total MRR (Rp) |
|-------|:---------------:|:--------------:|:-------------:|:------------------:|----------------:|
| 1 | 0 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 0 | 0 |
| 3 | 3 | 1 | 0 | 0 | 5,000,000 |
| 4 | 5 | 3 | 0 | 0 | 12,500,000 |
| 5 | 6 | 5 | 0 | 0 | 19,250,000 |
| 6 | 6 | 8 | 0 | 0 | 28,325,000 |
| 7 | 7 | 11 | 0 | 0 | 36,993,000 |
| 8 | 7 | 13 | 1 | 0 | 55,293,000 |
| 9 | 8 | 16 | 1 | 0 | 61,264,000 |
| 10 | 8 | 19 | 1 | 0 | 66,137,000 |
| 11 | 9 | 22 | 2 | 0 | 86,024,000 |
| 12 | 10 | 26 | 2 | 0 | 92,421,000 |

---

*Projections based on stated assumptions. Actual results will vary based on market conditions, execution quality, and competitive dynamics. Prepared August 2026.*
