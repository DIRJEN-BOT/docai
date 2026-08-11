# Outreach Sequence: Kredivo

## 1. LinkedIn DM (Indonesian Bahasa)

Halo [Name], saya lihat Kredivo lagi scale BNPL & limit kredit — keren banget.

Quick question: untuk limit upgrade, banyak user yang submit PDF rekening bank tapi diverifikasi manual kan?

Kami built API yang extract data dari struk BCA/Mandiri otomatis — 150ms, fraud detection built-in. Cocok buat secondary verification tanpa tambah headcount.

Boleh connect? Saya share demo singkat. 🙏

## 2. Email Day 1 — Problem-Focused

**Subject:** Kredivo × DocAI Verify — Otomasi Verifikasi PDF Statement untuk Limit Upgrade

Dear [Name],

Saya [Your Name] dari DocAI Verify.

Saya perhatikan Kredivo punya sistem alternatif data yang kuat untuk approve limit — phone bill, e-commerce history, dll. Tapi untuk limit upgrade, banyak user yang submit PDF rekening bank sebagai secondary verification.

**Masalahnya:**
- Tim credit harus manual review setiap PDF — lambat, inconsistent
- Fraud statement (edit manual, balance mismatch) sulit dideteksi secara konsisten
- Scale limit upgrade jadi bottleneck tanpa tambah analyst

**Solusi kami:**
- User upload PDF rekening BCA/Mandiri → kami return structured income data dalam 150ms
- Fraud detection built-in: balance validation, suspicious pattern detection, anomaly flagging
- Deterministic, no LLM — hasil konsisten, ~Rp0 per dokumen
- Tinggal plug ke existing approval workflow Kredivo

Kami lagi offer **100 free verifications selama 30 hari** — tanpa komitmen.

Mau saya kasih live demo dengan BCA statement asli?

Best regards,
[Your Name]
DocAI Verify

## 3. Email Day 3 — Follow-up with Demo

**Subject:** Re: Kredivo × DocAI Verify — Live Demo Ready

Hi [Name],

Follow-up dari email kemarin. Saya sudah siapkan demo live yang bisa dilihat langsung:

**🔗 Live API:** https://docaiid.pythonanywhere.com
**📖 API Docs:** https://docaiid.pythonanywhere.com/docs
**🔑 Free Signup:** https://docaiid.pythonanywhere.com/signup

Cukup upload BCA statement PDF ke API, dalam 150ms langsung keluar:
- Struktur transaksi lengkap (amount, date, description, balance)
- Income verification score
- Fraud flags (balance mismatch, suspicious patterns)
- Salary detection otomatis

**Use case untuk Kredivo:**
Borrower apply limit upgrade → upload PDF → API return structured data + fraud score → credit system decide otomatis atau escalate ke analyst.

Tanpa tambah headcount, limit upgrade bisa 10x lebih cepat.

Mau saya schedule 15 menit call untuk walk through integration? Tinggal bilang tanggal yang cocok.

Best,
[Your Name]

## 4. Email Day 7 — Social Proof + Urgency

**Subject:** 100 Free Verifications Expire Soon — Kredivo's Limit Upgrade Pipeline

Hi [Name],

Update singkat: kami sudah handle ribuan verifications untuk beberapa fintech lending di Indonesia.

**Yang sudah live:**
- BCA parser production-ready (format statement terbaru 2024)
- Mandiri parser live
- Fraud detection rate >95% untuk edited statements
- Response time consistently <150ms

**Kenapa ini urgent untuk Kredivo:**
Volume limit upgrade naik terus — tanpa otomasi, tim credit makin terbebani. Dengan DocAI Verify, borrower submit PDF → otomatis diproses → analyst hanya handle edge cases.

Free trial: **100 verifications, 30 hari, tanpa komitmen.**

Kalau tidak cocok, no worries — tapi kalau cocok, ini bisa transform limit upgrade workflow Kredivo.

Mau saya demo langsung? Reply email ini atau WhatsApp saya.

Best regards,
[Your Name]
DocAI Verify
[Email] | [Phone]

## 5. WhatsApp Message (Indonesian Bahasa)

Halo [Name]! 👋

Saya [Nama] dari DocAI Verify. Kami built API buat extract data dari struk rekening bank (BCA/Mandiri) otomatis — 150ms, fraud detection built-in.

Cocok buat Kredivo: borrower submit PDF untuk limit upgrade → langsung diproses → nggak perlu manual review.

Sekarang free trial: 100 verifikasi, 30 hari. Mau saya kasih demo? 🙏
