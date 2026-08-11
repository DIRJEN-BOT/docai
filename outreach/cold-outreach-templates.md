# DocAI Verify — Cold Outreach Templates

> Siap pakai. Copy-paste, personalisasi, kirim.

---

## 1. LinkedIn Connection Request (maks 300 karakter)

### P2P Lending

```
Halo [Nama], saya lihat [Perusahaan] lagi scale lending operations. Kami punya API income verification dari PDF bank statement — bisa kurangi manual verification 90%. Boleh connect? Saya share demo singkat.
```

```
Hi [Nama] — saw [Perusahaan]'s growth in P2P lending. We built an API that turns bank statement PDFs into credit decision data in <150ms. Zero manual work. Would love to share a demo.
```

### BNPL

```
Halo [Nama], di [Perusahaan] pakai manual verification untuk limit kredit baru? Kami punya API yang auto-parse PDF statement + kasih income score. Bisa kurangi fraud risk & approve lebih cepat. Connect?
```

```
Hi [Nama] — BNPL approval friction? Our API extracts income data from bank statement PDFs instantly, with fraud detection built in. Happy to share how [competitor-like company] is using it.
```

### Digital Bank

```
Halo [Nama], untuk pinjaman digital di [Perusahaan], kami punya API income verification yang fully deterministic — zero LLM cost, 30-150ms. Bisa jadi fallback untuk borrower yang tidak mau connect bank. Boleh share lebih lanjut?
```

### Multifinance

```
Halo [Nama], tim credit di [Perusahaan] masih handle PDF statement manual? Kami build API yang auto-parse + kasih fraud signals. Bisa reduce analyst workload 95%. Boleh connect?
```

### Insurtech

```
Halo [Nama], untuk claims verification di [Perusahaan], kami punya API yang auto-verify bank statement — detect fraud pattern & validate balance. Boleh connect? Saya share contoh output.
```

---

## 2. LinkedIn Follow-up (setelah connect diterima)

### Template A: P2P Lending

```
Halo [Nama], makasih sudah connect! 👋

Saya founder DocAI — kami build income verification API khusus untuk fintech Indonesia.

Yang kami solve:
📄 Borrower upload PDF bank statement → kami extract income data, score konsistencias, & deteksi fraud
⚡ 30-150ms response time, zero manual work
🔒 Deterministic — bukan LLM, jadi hasilnya konsisten & biaya ~Rp0/doc

Sekarang support BCA. Mandiri coming soon.

Mau coba? Kami offer **100 free verifications** — cukup kirim 10 sample statement, kami proses & return hasilnya dalam 24 jam.

Interested? Saya share API docs & demo response.
```

### Template B: BNPL

```
Halo [Nama], makasih sudah connect!

Saya builder DocAI — income verification API untuk lending di Indonesia.

Pain point yang kami solve:
- Approve limit tanpa manual verification
- Fraud statement detection (balance mismatch, suspicious patterns)
- Income consistency scoring — langsung kasih angka untuk credit decision

Output-nya: JSON lengkap dengan verification score (0-100), monthly income breakdown, fraud flags.

Kami offer **100 free trial verifications** — mau coba? Cukup kirim sample statement, kami proses & kirim hasilnya.
```

### Template C: Digital Bank / Enterprise

```
Halo [Nama], thanks for connecting!

Saya founder DocAI, kami punya income verification API yang built untuk Indonesian banks & fintech.

Kenapa beda dari Perfios/Brick:
- **Indonesia-first** — built untuk format BCA/Mandiri
- **Zero user friction** — borrower cukup upload PDF, tidak perlu connect bank
- **10-50x lebih murah** dari manual verification
- **Deterministic** — zero LLM cost, consistent results

Production-ready untuk BCA, Mandiri in pipeline.

Boleh schedule 15-min call minggu depan? Saya demo langsung.
```

---

## 3. WhatsApp Message

### Bahasa Indonesia (untuk Indonesian B2B)

```
Halo Kak [Nama] 👋

Saya [Nama], founder DocAI. Kami punya API buat auto-parse PDF bank statement jadi data income verification — langsung kasih scoring, fraud detection, balance check.

Buat lending/credit process, ini bisa:
• Kurangi manual verification 90%
• Deteksi fraud statement (saldo tidak match, pola curiga)
• Kasih income score otomatis

Sekarang support BCA, Mandiri coming soon.

Mau coba gratis? 100 verifications free, 30 hari. Cukup kirim sample statement, saya proses & kirim hasilnya.

Boleh chat atau schedule demo call? 🙏
```

### English version

```
Hi [Nama] 👋

I'm [Nama], founder of DocAI. We built an income verification API for Indonesian fintech lenders.

What it does:
• Parse bank statement PDFs → structured income data
• Auto score income consistency (0-100)
• Detect fraud signals (balance mismatch, suspicious patterns)
• 30-150ms response, zero LLM cost

Currently support BCA. Mandiri coming soon.

Want to try? 100 free verifications, 30 days. Just send 10 sample statements, I'll process and return results within 24h.

Available for a quick call this week? 🙏
```

### Formal / Enterprise (untuk bank/multifinance)

```
Halo Bapak/Ibu [Nama],

Saya [Nama], founder DocAI — income verification API untuk fintech lending Indonesia.

Kami menawarkan pilot program gratis:
• 100 verifications tanpa komitmen
• Full API access
• Benchmark vs proses manual Anda

Produk kami sudah production-ready untuk bank statement BCA. Deterministik, zero LLM cost, 30-150ms latency.

Bila berkenan, saya bisa share proposal & demo response. Atau schedule 15-min call minggu depan?

Terima kasih 🙏
```

---

## 4. Email Template

### Subject Line Options

1. `Income verification API — 100 free verifications untuk [Perusahaan]`
2. `Auto-verify bank statement PDFs — 90% faster, 95% cheaper`
3. `DocAI Verify: income scoring dari PDF bank statement`
4. `Free trial: income verification API untuk fintech lending`
5. `[Perusahaan] x DocAI: pilot program 100 verifications`

### Body — P2P Lending

```
Subject: Income verification API — 100 free verifications untuk [Perusahaan]

Halo [Nama],

Saya [Nama], founder DocAI.

**Masalah:**
Tim credit di [Perusahaan] masih manually verify income dari PDF bank statement yang di-upload borrower. Proses ini:
- Butuh 30-60 menit per statement
- Rawan human error
- Tidak scalable saat volume naik

**Solusi:**
DocAI Verify — POST bank statement PDF, dapat:
- Structured transaction data (date, description, debit, credit, balance)
- Monthly income estimate + source detection
- Income consistency score (0-100)
- Fraud signals (balance mismatch, suspicious patterns)
- Overall verification score (0-100)

**Bukan LLM.** Deterministik — hasil konsisten, biaya ~Rp0/doc. Latency 30-150ms.

**Bukti:**
Contoh output (bank statement 6 bulan, 186 transaksi):
{
  "verification_score": 82,
  "detected_monthly_income": 12500000,
  "income_source": "salary",
  "consistency_score": 95,
  "balance_valid": true,
  "fraud_flags": []
}

Full response: [link ke demo-response.json]

**Tawaran:**
100 verifications gratis. 30 hari. Tanpa komitmen.
Cukup kirim 10 sample statement, kami proses & kirim hasilnya dalam 24 jam.

**Cara mulai:**
Balas email ini atau WhatsApp: [nomor]

Salam,
[Nama]
Founder, DocAI
hello@docai.id | docaiid.pythonanywhere.com
```

### Body — BNPL / Digital Bank

```
Subject: Auto-verify bank statement PDFs — fraud detection built in

Halo [Nama],

Saya [Nama], founder DocAI.

**Context:**
Di BNPL/digital banking, approve limit kredit butuh income verification. Saat ini:
- User harus connect bank account (friction tinggi, banyak drop-off)
- Atau analyst manual review PDF (slow, expensive)
- Fraud statement sulit dideteksi secara manual

**What DocAI Verify does:**
POST bank statement PDF → get:
✓ Structured transaction data
✓ Monthly income estimate with source detection
✓ Income consistency score
✓ Fraud detection (balance mismatch, suspicious patterns)
✓ Overall verification score (0-100)

**Why it's different:**
- Zero user friction — borrower cukup upload PDF, tidak perlu connect bank
- Indonesia-first — built untuk format BCA/Mandiri
- 10-50x cheaper than manual verification
- Deterministic — zero LLM cost, consistent results

**Offer:**
100 free verifications, 30 days, no commitment.
Send 10 sample statements → results within 24h.

Reply or WhatsApp: [nomor]

[Nama]
Founder, DocAI | hello@docai.id
```

---

## 5. Telegram Message (Dev Community)

```
🔧 DocAI Verify — Income Verification API untuk Indonesian Fintech

POST bank statement PDF → structured income data + scoring

Contoh output:
{
  "verification_score": 82,
  "detected_monthly_income": 12500000,
  "income_source": "salary",
  "consistency_score": 95,
  "balance_valid": true,
  "fraud_flags": []
}

Fitur:
• Parse bank statement PDF → JSON transactions
• Auto income estimation + source detection (salary/freelance/business)
• Income consistency scoring (0-100)
• Fraud detection (balance mismatch, suspicious patterns)
• 30-150ms latency, zero LLM cost

Tech stack:
• Python (FastAPI)
• Deterministic (regex-based, bukan LLM)
• Stateless — file tidak disimpan

API endpoint: POST /verify-income
Docs: docaiid.pythonanywhere.com/docs
RapidAPI: rapidapi.com/oyi77/api/docai

Saat ini: BCA ✅, Mandiri coming soon
Open for feedback & collaboration 🚀
```

---

## Personalization Checklist

Sebelum kirim, pastikan:
- [ ] Nama decision maker benar (cek LinkedIn)
- [ ] Nama perusahaan benar
- [ ] Pain point spesifik untuk segment mereka
- [ ] Tidak ada typo
- [ ] Link demo-response.json atau API docs aktif
- [ ] WhatsApp number / email benar
- [ ] Bahasa sesuai konteks (Indonesia untuk local, English untuk enterprise)

---

## Follow-up Cadence

| Day | Action | Channel |
|-----|--------|---------|
| Day 1 | Connection request / initial message | LinkedIn |
| Day 2 | Follow-up if connected | LinkedIn DM |
| Day 4 | WhatsApp (if phone available) | WhatsApp |
| Day 7 | Email (if no response) | Email |
| Day 14 | Final follow-up | LinkedIn + Email |
| Day 30 | Re-engage with update (new bank support, etc.) | LinkedIn |

**Tips:**
- Jangan spam — max 3 touchpoints per minggu
- Selalu kasih value (bukan cuma "lagi apa?")
- Track response di spreadsheet
- Kalau tidak response setelah 3 follow-up, skip & move on

---

*Templates ini continuously updated berdasarkan response rate. Update terakhir: Agustus 2026.*
