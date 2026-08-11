# DocAI Verify — Program Pilot Gratis

> 100 verifikasi income gratis. 30 hari. Tanpa komitmen.

---

## Apa itu DocAI Verify?

DocAI Verify adalah API income verification untuk fintech lending Indonesia.

**POST** satu PDF bank statement, dapat:
- Data transaksi terstruktur (tanggal, deskripsi, debit, kredit, saldo)
- Estimasi income bulanan dengan deteksi sumber (gaji, freelance, bisnis)
- Skor konsistensi income (0-100)
- Sinyal fraud (saldo tidak match, pola mencurigakan)
- Skor verifikasi keseluruhan (0-100)

**Bukan LLM.** Deterministik — hasil konsisten, biaya ~Rp0 per dokumen. Latency 30-150ms.

---

## Apa yang Anda Dapatkan?

| Item | Detail |
|------|--------|
| **Free verifications** | 100 statement |
| **Durasi** | 30 hari sejak aktivasi |
| **API access** | Full — endpoint `/verify-income`, rate limit normal |
| **Laporan verifikasi** | JSON lengkap (lihat `demo-response.json` di repo ini) |
| **Support** | WhatsApp/chat langsung ke founder |
| **Commitment** | Tidak ada. Kalau tidak cocok, ya sudah. |

---

## Kenapa Pilot Gratis?

Kami yakin produk ini的价值 (value) — tapi lebih baik kalau Anda buktikan sendiri.

Yang kami butuh dari pilot:
1. **Feedback jujur** — apakah output relevan untuk credit decision Anda?
2. **Edge cases** — kirim statement yang tricky (fraud, tidak jelas, format aneh)
3. **Case study** — kalau hasilnya bagus, boleh kami publish (tanpa data borrower)

Tidak ada upsell setelah pilot. Kalau cocok, kami tawarkan pricing. Kalau tidak, kami terima feedback.

---

## Cara Mulai

### Langkah 1: Kirim sample statement
Kirim 10 PDF bank statement (bisa anonymized/dummy) ke:
- **WhatsApp:** [nomor WhatsApp]
- **Email:** hello@docai.id

### Langkah 2: Kami proses & kirim hasil
Dalam 24 jam, kami kirim:
- JSON response untuk masing-masing statement
- Summary perbandingan: DocAI Verify output vs apa yang analyst Anda lihat
- Rekomendasi integrasi

### Langkah 3: Mulai API trial
Kalau hasilnya bagus, kami aktifkan API key dengan 100 free verifications.
Integrasi ke sistem Anda pakai API docs yang tersedia.

---

## Contoh Output

```json
{
  "verification_score": 82,
  "confidence": "high",
  "detected_monthly_income": 12500000,
  "income_source": "salary",
  "consistency_score": 95,
  "balance_valid": true,
  "fraud_flags": [],
  "statement_period": "01 Jan 2025 - 30 Jun 2025",
  "total_transactions": 186
}
```

Full response: `demo-response.json`

---

## Pertanyaan Umum

**Q: Statement bank apa yang didukung?**
A: Sekarang BCA (production-ready). Mandiri dalam pipeline. BNI & BRI menyusul.

**Q: Bagaimana kalau statement saya password-protected (DOB)?**
A: API kami tahu — langsung return error `password_protected` dengan instruksi cara unlock.

**Q: Apakah data statement kami disimpan?**
A: Tidak. Stateless processing — PDF diproses, hasil dikirim, file tidak disimpan di server kami.

**Q: Bisa dipakai untuk non-lending use case?**
A: Bisa — accounting automation, bookkeeping, audit trail, cash flow analysis.

**Q: Berapa lama integrasi?**
A: REST API standar. 1-2 hari untuk dev yang familiar dengan API integration. Contoh kode Python/Node/PHP tersedia.

---

## Hubungi Kami

- **WhatsApp:** [nomor]
- **Email:** hello@docai.id
- **LinkedIn:** [profile]
- **API Docs:** docaiid.pythonanywhere.com/docs
- **RapidAPI:** rapidapi.com/oyi77/api/docai

---

*DocAI Verify — income verification yang dibuat untuk fintech Indonesia, oleh developer Indonesia.*
