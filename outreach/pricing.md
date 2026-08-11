# DocAI Verify — Pricing

> Income verification API untuk fintech lending Indonesia.

---

## Pricing Tiers

| Tier | Harga/bulan | Verifications/bulan | Per-verifikasi | Target |
|------|-------------|---------------------|----------------|--------|
| **Free** | Rp 0 | 100 | Rp 0 | Trial & evaluasi |
| **Starter** | Rp 500.000 (~$30) | 500 | Rp 1.000 | P2P lender kecil |
| **Growth** | Rp 5.000.000 (~$300) | 5.000 | Rp 1.000 | Fintech menengah |
| **Scale** | Rp 30.000.000 (~$1.800) | 50.000 | Rp 600 | Lender besar / multifinance |
| **Enterprise** | Custom | Unlimited | Negotiable | Bank, fintech besar |

**Semua tier termasuk:**
- Akses API penuh (parse + verify-income)
- Dashboard usage stats
- WhatsApp/email support
- SLA 99.9% uptime
- Response time < 500ms

---

## Perbandingan dengan Alternatives

| Metode | Biaya per verifikasi | Akurasi | Kecepatan | Skalabilitas |
|--------|---------------------|---------|-----------|--------------|
| **Manual verification (analyst)** | Rp 50.000 - 100.000 | Tergantung skill | 30-60 menit/statement | Terbatas (butuh SDM) |
| **DocAI Verify (Starter)** | **Rp 1.000** | 98%+ (deterministic) | 30-150ms | Unlimited |
| **Perfios (enterprise)** | $0.50 - 2.000 (~Rp 8.000-32.000) | 95%+ | Instant | Unlimited, tapi mahal |
| **Brick / Ayoconnect** | Gratis untuk user (api cost hidden) | High | Instant | Bergantung user mau connect |
| **OpenFinance** | Custom pricing | High | Instant | Bergantung user mau connect |

### Kenapa DocAI Verify?

1. **10-50x lebih murah dari manual** — Rp 1.000 vs Rp 50.000-100.000
2. **2-30x lebih murah dari Perfios** — Rp 1.000 vs Rp 8.000-32.000
3. **Zero user friction** — tidak perlu user connect bank account, cukup upload PDF
4. **Indonesia-first** — built untuk format BCA/Mandiri, bukan generic parser
5. **Deterministic** — biaya ~Rp0 per dokumen, bukan LLM yang biayanya fluktuatif
6. **Fraud detection built-in** — balance mismatch & suspicious pattern detection

---

## Use Case → Tier Mapping

| Use case | Volume/bulan | Recommended tier | Monthly cost |
|----------|-------------|-----------------|--------------|
| P2P lender kecil (100-500 loan apps/bulan) | 200-500 | Starter | Rp 500.000 |
| P2P lender menengah (1.000-5.000 loan apps/bulan) | 1.000-5.000 | Growth | Rp 5.000.000 |
| BNPL (10.000-50.000 transaction/bulan) | 10.000-50.000 | Scale | Rp 30.000.000 |
| Bank digital (100.000+ loan apps/bulan) | 100.000+ | Enterprise | Custom |

---

## ROI Calculation

### Contoh: P2P Lender dengan 500 loan apps/bulan

| | Manual | DocAI Verify (Starter) |
|---|--------|------------------------|
| **Biaya verifikasi** | 500 × Rp 75.000 = Rp 37.500.000/bulan | Rp 500.000/bulan |
| **Biaya SDM (2 analyst)** | Rp 8.000.000/bulan (gaji + overhead) | Rp 0 (otomatis) |
| **Total biaya/bulan** | **Rp 45.500.000** | **Rp 500.000** |
| **Penghematan** | — | **Rp 45.000.000/bulan (99%)** |
| **Payback period** | — | Immediate |

### Contoh: Mid-size Fintech (3.000 verifications/bulan)

| | Manual | DocAI Verify (Growth) | Perfios |
|---|--------|----------------------|---------|
| **Biaya/bulan** | Rp 225.000.000 | Rp 5.000.000 | Rp 24.000.000 |
| **Penghematan vs manual** | — | **98%** | **89%** |
| **Penghematan vs Perfios** | — | **Rp 19.000.000 (79%)** | — |

---

## Enterprise Pricing

Untuk volume > 50.000 verifikasi/bulan:

- **Custom SLA** — 99.99% uptime, dedicated support
- **On-premise deployment** — jalankan di infrastruktur Anda
- **Custom integrasi** — connect ke loan management system Anda
- **Batch processing** — upload ribuan statement sekaligus
- **Custom scoring model** — adjust verification scoring sesuai risk policy

Hubungi kami untuk pricing: hello@docai.id

---

## FAQ Pricing

**Q: Ada biaya setup?**
A: Tidak ada. Daftar, dapat API key, langsung pakai.

**Q: Bagaimana kalau melebihi limit bulanan?**
A: Kami notifikasi di 80% usage. Kalau melebihi, overage charge sesuai tier di atas (Rp 1.000/verifikasi untuk Starter, Rp 1.000 untuk Growth).

**Q: Bisa bayar per verifikasi (pay-as-you-go)?**
A: Untuk sekarang, subscription bulanan. Enterprise bisa negosiasi per-verification pricing.

**Q: Ada diskon untuk annual commitment?**
A: Ya — diskon 20% untuk annual billing. Growth tier: Rp 48.000.000/tahun (hemat Rp 12.000.000).

**Q: Statement bank apa yang didukung?**
A: BCA (production-ready). Mandiri dalam pipeline. BNI & BRI menyusul.

---

## Contact

Untuk demo, pilot, atau pertanyaan pricing:

- **WhatsApp:** [nomor]
- **Email:** hello@docai.id
- **LinkedIn:** [profile]
- **API Docs:** docaiid.pythonanywhere.com/docs
- **Try Free:** rapidapi.com/oyi77/api/docai

---

*Harga dalam Rupiah (IDR). Konversi USD bersifat estimasi. Harga dapat berubah tanpa pemberitahuan.*
