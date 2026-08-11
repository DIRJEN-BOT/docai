# DocAI Verify — Target Buyer List

> Daftar perusahaan Indonesia yang butuh income verification API untuk lending/credit decisions.
> Diurutkan berdasarkan kemungkinan closing: P2P lending → BNPL → digital bank → multifinance → insurtech.

---

## P2P Lending (Prioritas Tinggi)

### 1. Modalku / Funding Societies
- **Website:** modalku.co.id
- **Segment:** P2P lending (UMKM & personal)
- **Pain point:** Volume pinjaman besar, tim credit masih manually cross-check income dari PDF statement yang di-upload borrower. Fraud statement (edit manual) jadi red flag utama — balance mismatch tidak selalu terdeteksi.
- **Decision maker:** VP of Risk / Head of Credit Risk / CTO
- **LinkedIn search:** `"Modalku" "Head of Risk" OR "VP Risk" OR "CTO" site:linkedin.com`
- **Est. budget:** Rp 5-15 juta/bulan (high volume, needs automation at scale)

### 2. Amartha
- **Website:** amartha.com
- **Segment:** P2P lending (UMKM)
- **Pain point:** Fokus di segmentasi borrower dengan cash flow analysis. Saat ini andalkan data aggregator (Brick/Ayoconnect) yang butuh borrower connect bank — friction tinggi, banyak drop-off. DocAI bisa jadi fallback untuk borrower yang tidak mau connect.
- **Decision maker:** CTO / Head of Product / VP Engineering
- **LinkedIn search:** `"Amartha" "CTO" OR "Head of Credit" OR "VP Engineering" site:linkedin.com`
- **Est. budget:** Rp 5-10 juta/bulan

### 3. KoinWorks
- **Website:** koinworks.com
- **Segment:** P2P lending + digital bank (KoinGold, KoinBisnis)
- **Pain point:** Diversifikasi produk lending, butuh income verification yang scalable untuk personal loan & BNPL kredit. Tidak semua borrower mau link bank — PDF upload jadi alternatif.
- **Decision maker:** Head of Credit / CTO / VP Risk
- **LinkedIn search:** `"KoinWorks" "Head of Credit" OR "Risk" OR "CTO" site:linkedin.com`
- **Est. budget:** Rp 3-8 juta/bulan

### 4. Investree
- **Website:** investree.id
- **Segment:** P2P lending (invoice financing & personal)
- **Pain point:** Bisnis invoice financing butuh verifikasi cash flow borrower dari rekening bisnis. PDF statement BCA dari borrower sudah dikumpulkan tapi dianalisis manual.
- **Decision maker:** VP Risk / Head of Credit Operations
- **LinkedIn search:** `"Investree" "VP Risk" OR "Head of Credit" OR "Credit Manager" site:linkedin.com`
- **Est. budget:** Rp 3-8 juta/bulan

### 5. Akseleran
- **Website:** akseleran.co.id
- **Segment:** P2P lending (UMKM & working capital)
- **Pain point:** Proses credit scoring untuk UMKM masih banyak manual verification. Butuh automated income verification yang langsung kasih scoring — tidak cuma data mentah.
- **Decision maker:** Head of Credit / CTO
- **LinkedIn search:** `"Akseleran" "Head of Credit" OR "CTO" OR "Credit Risk" site:linkedin.com`
- **Est. budget:** Rp 2-5 juta/bulan

### 6. Danamon Social Finance (DSF)
- **Website:** dsf.co.id
- **Segment:** P2P lending (social impact)
- **Pain point:** Lending untuk underbanked — income verification dari PDF jadi satu-satunya cara untuk borrower yang tidak punya data digital bank. Butuh solusi murah & akurat.
- **Decision maker:** Head of Technology / VP Operations
- **LinkedIn search:** `"Danamon Social Finance" OR "DSF" "Technology" OR "Operations" site:linkedin.com`
- **Est. budget:** Rp 1-3 juta/bulan

### 7. Finmas
- **Website:** finmas.co.id
- **Segment:** P2P lending (personal loan)
- **Pain point:** Early-stage lending platform, butuh quick integration untuk income verification. Budget terbatas tapi butuh fitur yang bisa langsung compete dengan yang sudah established.
- **Decision maker:** CTO / Founder
- **LinkedIn search:** `"Finmas" "CTO" OR "Founder" OR "Credit" site:linkedin.com`
- **Est. budget:** Rp 500rb-2 juta/bulan (starter tier)

---

## BNPL (Buy Now Pay Later)

### 8. Kredivo
- **Website:** kredivo.com
- **Segment:** BNPL + personal loan
- **Pain point:** Proses approve limit kredit untuk new user masih pakai data alternative (phone bill, e-commerce history). PDF bank statement sebagai secondary verification untuk limit upgrade — currently handled manually or not at all.
- **Decision maker:** VP Risk / Head of Data Science / CTO
- **LinkedIn search:** `"Kredivo" "VP Risk" OR "Data Science" OR "CTO" site:linkedin.com`
- **Est. budget:** Rp 10-20 juta/bulan (massive volume)

### 9. Akulaku
- **Website:** akulaku.com
- **Segment:** BNPL + fintech lending + bank
- **Pain point:** Sama dengan Kredivo, tapi lebih besar. Akulaku juga punya bank (Neo Commerce Bank) — dual use case: consumer BNPL + bank lending verification. Fraud statement detection sangat kritis.
- **Decision maker:** VP Risk / CTO / Head of Credit Policy
- **LinkedIn search:** `"Akulaku" "Risk" OR "CTO" OR "Credit Policy" site:linkedin.com`
- **Est. budget:** Rp 15-30 juta/bulan

### 10. Home Credit Indonesia
- **Website:** homecredit.co.id
- **Segment:** BNPL (merchant financing)
- **Pain point:** Verifikasi income untuk merchant partner dan end-consumer. Home Credit sudah punya data sharing agreements, tapi PDF statement verification jadi backup channel untuk edge cases.
- **Decision maker:** VP Operations / Head of Credit / CTO
- **LinkedIn search:** `"Home Credit Indonesia" "Risk" OR "Operations" OR "CTO" site:linkedin.com`
- **Est. budget:** Rp 10-20 juta/bulan

### 11. Atome
- **Website:** atome.co.id
- **Segment:** BNPL
- **Pain point:** Baru masuk Indonesia, butuh quick credit infrastructure. PDF bank statement verification untuk user yang tidak punya credit score tradisional.
- **Decision maker:** Head of Credit / Country Manager / CTO
- **LinkedIn search:** `"Atome" "Indonesia" "Credit" OR "Risk" OR "CTO" site:linkedin.com`
- **Est. budget:** Rp 5-10 juta/bulan

---

## Digital Banks

### 12. Bank Jago
- **Website:** bankjago.com
- **Segment:** Digital bank
- **Pain point:** Pinjaman digital butuh income verification yang fully digital. Banyak user Jago yang apply loan tapi tidak punya slip gaji — bank statement PDF jadi alternative income proof. Fraud detection kritis karena fully automated process.
- **Decision maker:** VP Lending / Head of Digital Banking / CTO
- **LinkedIn search:** `"Bank Jago" "Lending" OR "Digital Banking" OR "CTO" site:linkedin.com`
- **Est. budget:** Rp 15-30 juta/bulan

### 13. Blu by BCA
- **Website:** blubybca.com
- **Segment:** Digital bank (BCA subsidiary)
- **Pain point:** Sebagai produk BCA, blu punya akses ke BCA data secara internal. Tapi untuk user non-BCA atau cross-bank lending, butuh verifikasi dari bank lain — DocAI bisa handle parsing bank statement non-BCA yang masuk.
- **Decision maker:** Head of Innovation / VP Product
- **LinkedIn search:** `"Blu by BCA" OR "Bank BCA" "Innovation" OR "Product" OR "CTO" site:linkedin.com`
- **Est. budget:** Rp 10-20 juta/bulan

### 14. Neo Commerce Bank
- **Website:** neocommercebank.co.id
- **Segment:** Digital bank (Akulaku subsidiary)
- **Pain point:** Bank digital yang support lending untuk Akulaku ecosystem. Income verification cross-platform — borrower dari Akulaku tapi pakai statement bank lain.
- **Decision maker:** VP Risk / Head of Credit Technology
- **LinkedIn search:** `"Neo Commerce Bank" "Risk" OR "Credit" OR "Technology" site:linkedin.com`
- **Est. budget:** Rp 10-20 juta/bulan

---

## Multifinance

### 15. Sinar Mas Multiartha
- **Website:** simasdev.id
- **Segment:** Multifinance (auto, consumer, property)
- **Pain point:** Multifinance besar dengan volume pengajuan ribuan per bulan. Income verification masih banyak manual — analyst buka PDF, ketik ke sistem. Fraud statement jadi cost center.
- **Decision maker:** VP IT / Head of Credit Operations / CTO
- **LinkedIn search:** `"Sinar Mas" "Multiartha" OR "Simas" "IT" OR "Credit" OR "Operations" site:linkedin.com`
- **Est. budget:** Rp 15-25 juta/bulan

### 16. BCA Finance
- **Website:** bcafinance.co.id
- **Segment:** Multifinance (auto, consumer)
- **Pain point:** Sama seperti di atas, tapi karena afiliasi BCA — bisa jadi early adopter untuk parser BCA yang sudah mature. Cross-reference antara statement BCA internal dan yang di-submit borrower.
- **Decision maker:** VP Risk / Head of Credit / IT Director
- **LinkedIn search:** `"BCA Finance" "Risk" OR "Credit" OR "IT" site:linkedin.com`
- **Est. budget:** Rp 10-20 juta/bulan

### 17. Mandiri Tunas Finance
- **Website:** mandiritunas.co.id
- **Segment:** Multifinance (Mandiri subsidiary)
- **Pain point:** Saat ini support PDF parsing BCA belum ada — ketika parser Mandiri ready, ini jadi target utama. Multifinance dengan volume tinggi, butuh automation.
- **Decision maker:** VP Operations / Head of Credit / CTO
- **LinkedIn search:** `"Mandiri Tunas Finance" "Operations" OR "Credit" OR "Technology" site:linkedin.com`
- **Est. budget:** Rp 10-15 juta/bulan

---

## Insurtech

### 18. Qoala
- **Website:** qoala.app
- **Segment:** Insurtech (general insurance)
- **Pain point:** Claims verification untuk asuransi — borrower/claimant submit bank statement sebagai bukti transaksi. Butuh automated verification untuk detect fraud claim & speed up processing.
- **Decision maker:** VP Product / Head of Claims / CTO
- **LinkedIn search:** `"Qoala" "Claims" OR "Product" OR "CTO" site:linkedin.com`
- **Est. budget:** Rp 3-8 juta/bulan

### 19. Allianz Indonesia
- **Website:** allianz.co.id
- **Segment:** Insurance (traditional + digital)
- **Pain point:** Divisi digital lending (Allianz Multi Finance) butuh income verification. Divisi asuransi juga butuh untuk claims verification.
- **Decision maker:** VP Digital / Head of IT / Chief Data Officer
- **LinkedIn search:** `"Allianz Indonesia" "Digital" OR "IT" OR "Data" site:linkedin.com`
- **Est. budget:** Rp 10-20 juta/bulan

---

## Additional Targets (Wildcard)

### 20. Bank Rakyat Indonesia (BRI)
- **Website:** bri.co.id
- **Segment:** State-owned bank (UMKM lending)
- **Pain point:** BRILink dan pinjaman digital butuh verifikasi income dari bank statement. Volume UMKM BRI sangat besar — manual verification tidak scalable.
- **Decision maker:** VP Digital / VP Risk / CTO BRI Digital
- **LinkedIn search:** `"Bank BRI" "Digital" OR "Risk" OR "CTO" site:linkedin.com`
- **Est. budget:** Rp 20-50 juta/bulan (enterprise)

### 21. Bank Negara Indonesia (BNI)
- **Website:** bni.co.id
- **Segment:** State-owned bank
- **Pain point:** Sama seperti BRI — digital lending butuh automated income verification. BNI juga punya BNPL produk.
- **Decision maker:** VP Innovation / Head of Digital Banking
- **LinkedIn search:** `"Bank BNI" "Innovation" OR "Digital Banking" site:linkedin.com`
- **Est. budget:** Rp 20-50 juta/bulan (enterprise)

### 22. Bank Mandiri
- **Website:** bankmandiri.co.id
- **Segment:** State-owned bank
- **Pain point:** Mandiri Kredit dan Livin' by Mandiri butuh income verification. Parser Mandiri jadi value prop kuat — "kami support bank Anda".
- **Decision maker:** VP Digital / Head of Credit Risk
- **LinkedIn search:** `"Bank Mandiri" "Digital" OR "Credit Risk" site:linkedin.com`
- **Est. budget:** Rp 20-50 juta/bulan (enterprise)

### 23. Bank Central Asia (BCA)
- **Website:** bca.co.id
- **Segment:** Largest private bank
- **Pain point:** BCA Finance & BCA digital lending butuh cross-verification. Parser BCA yang sudah mature jadi entry point — "kami sudah paham format BCA".
- **Decision maker:** VP Digital / IT Director
- **LinkedIn search:** `"Bank BCA" "Digital" OR "IT Director" site:linkedin.com`
- **Est. budget:** Rp 30-50 juta/bulan (enterprise)

### 24. DANA
- **Website:** Dana.id
- **Segment:** Digital wallet + lending
- **Pain point:** DANA Modal (peminjaman untuk merchant) butuh income verification dari bank statement — DANA sendiri tidak punya data cash flow merchant secara lengkap.
- **Decision maker:** VP Risk / Head of Lending
- **LinkedIn search:** `"DANA" "Lending" OR "Risk" OR "Merchant" site:linkedin.com`
- **Est. budget:** Rp 10-20 juta/bulan

### 25. OVO / Grab
- **Website:** ovo.id / grab.com/id
- **Segment:** Digital wallet + fintech
- **Pain point:** GrabFinance (lending untuk driver & merchant) butuh income verification — bank statement jadi data source untuk driver income assessment.
- **Decision manager:** VP Risk / Head of GrabFinance
- **LinkedIn search:** `"GrabFinance" OR "Grab" "Indonesia" "Lending" OR "Risk" site:linkedin.com`
- **Est. budget:** Rp 10-20 juta/bulan

---

## Prioritization Matrix

| Priority | Segment | Why | First 5 to contact |
|----------|---------|-----|---------------------|
| **P0** | P2P Lending | Highest pain, most willing to adopt, fastest decision cycle | Modalku, KoinWorks, Amartha, Investree, Akseleran |
| **P1** | BNPL | Large volume, fraud-sensitive, budget available | Kredivo, Akulaku, Home Credit, Atome |
| **P2** | Digital Banks | High budget, but longer procurement cycle | Bank Jago, Blu, Neo Commerce |
| **P3** | Multifinance | Slow adoption, but high volume if signed | Sinar Mas, BCA Finance, Mandiri Tunas |
| **P4** | Enterprise Banks | Huge budget, very long sales cycle (6-12 months) | BRI, BNI, BCA, Mandiri |
| **P5** | Insurtech | Smaller market fit, but unique use case | Qoala, Allianz |

---

## Outreach Strategy

### Week 1-2: P2P Lending (cold outreach ke 5 perusahaan P0)
- LinkedIn DM ke decision makers
- Offer: free pilot 100 verifications
- KPI: 3 demo calls scheduled

### Week 3-4: BNPL (cold outreach ke 4 perusahaan P1)
- Same playbook, emphasize fraud detection angle
- KPI: 2 demo calls scheduled

### Week 5-6: Digital Banks (warm intro via existing P2P clients)
- Leverage social proof dari P2P yang sudah trial
- KPI: 1 pilot agreement

### Week 7-8: Multifinance (formal proposal)
- Send pilot-offer.md + pricing.md
- KPI: 1 pilot agreement

### Ongoing: Enterprise Banks
- Start conversations now, expect 6-12 month close cycle
- Build case studies from P2P/BNPL pilots

---

## Notes

- **BCA parser sudah production-ready** → gunakan ini sebagai differentiator ("kami sudah solve BCA, bank paling banyak dipakai untuk lending di Indonesia")
- **Mandiri coming soon** → jangan promise, tapi mention di roadmap
- **Indonesian B2B prefers WhatsApp** → prioritaskan WhatsApp over email
- **Budget ranges are estimates** based on company size and industry benchmarks for Indonesian fintech tooling spend
- **LinkedIn search queries** are designed to find actual decision makers — adjust based on current results
