# Promo Kit — DocAI (Indonesian Bank Statement Parser)

**Hub:** https://rapidapi.com/oyi77/api/docai
**Backend:** https://docaiid.pythonanywhere.com
**Aset gambar:** `assets/promo/docai_banner_linkedin.png` (1200x630), `docai_banner_twitter.png` (1600x900), `docai_banner_square.png` (1080x1080), `assets/logo_docai_400.png`

**Claim yang BOLEH dipakai (terverifikasi):**
- Parse PDF e-statement **BCA** -> JSON/CSV, deterministik, zero LLM cost
- `balance_check` otomatis (saldo awal + kredit - debit == saldo akhir)
- API production, Public di RapidAPI, Free tier, docs lengkap
- 200 OK terverifikasi lewat proxy RapidAPI (health + parse)

**Claim yang BELUM boleh:**
- Mandiri/BNI/BRI = "coming soon" (masih riset format — jangan klaim sudah jalan)
- Multi-bank, tanpa watermark, batch — semua belum ada di versi live

---

## 1. LinkedIn — Post utama (Bahasa Indonesia)

```
🟦 DocAI — parse e-statement bank jadi JSON, tanpa manual entry

Masih input mutasi bank satu-satu ke Excel/Jurnal/Accurate?
Ini API yang saya buat sendiri: upload PDF e-statement BCA, dapat
struktur JSON + CSV dalam hitungan detik.

Yang bikin beda:
✔ Deterministik — bukan LLM, jadi hasilnya konsisten & biaya ~Rp0/doc
✔ Balance check otomatis — saldo awal + mutasi vs saldo akhir divalidasi sistem
✔ Siap integrasi — output dipetakan untuk jurnal & laporan keuangan

Kalau kamu akuntan, pembuku, founder fintech, atau dev yang butuh
data transaksi bank terstruktur — coba gratis di RapidAPI:

🔗 https://rapidapi.com/oyi77/api/docai

(Mandiri · BNI · BRI menyusul 🚀)
```

**Versi English (untuk audience global):**

```
🟦 DocAI — parse Indonesian bank e-statements into JSON, no manual entry

Still typing bank statement rows into Excel one by one?
I built an API that turns a BCA e-statement PDF into structured
JSON + CSV in seconds.

Why it's different:
✔ Deterministic — no LLM calls, so results are consistent & COGS ~$0/doc
✔ Balance check built-in — opening + flows vs closing balance validated
✔ Integrator-friendly — fields mapped for journals & financial reports

If you're an accountant, bookkeeper, fintech founder, or dev needing
structured bank transactions — try the free tier:

🔗 https://rapidapi.com/oyi77/api/docai

(Mandiri · BNI · BRI coming soon 🚀)
```

---

## 2. Facebook — grup akuntan & pembukuan (Bahasa Indonesia)

```
[FREE] Tools buat akuntan/pembuku: e-statement bank langsung jadi data

Siapa di sini yang masih input mutasi rekening bank manual ke Excel
atau Jurnal? 😅 Satu statement bisa puluhan baris, salah satu angka
saja saldo tidak balance, dan cek-ulang makan waktu sejam.

Saya buat DocAI:
📄 Upload PDF e-statement (BCA dulu, Mandiri/BNI/BRI menyusul)
⚙️ Output: tabel transaksi (tanggal, keterangan, debet, kredit, saldo)
✅ Auto balance check — sistem langsung bilang kalau saldo tidak nyambung
💾 Export JSON atau CSV, siap dipindah ke aplikasi akuntansi

Gratis untuk dicoba, tidak perlu daftar kartu kredit:
🔗 https://rapidapi.com/oyi77/api/docai

Kalau kalian pakai Jurnal/Accurate/Kledo dan butuh template import
yang sesuai, tinggalkan komentar — saya prioritaskan fitur itu. 🙌
```

---

## 3. Twitter/X (Bahasa Indonesia, thread pendek)

```
Saya capek manual entry e-statement bank, jadi saya bikin API-nya. 🧵

1/ Masalah tiap akhir bulan: mutasi BCA di PDF, harus diketik ulang
ke spreadsheet. Typo = saldo tidak balance = jam terbuang.

2/ Solusi: DocAI. Upload PDF e-statement, dapat JSON/CSV terstruktur
dalam detik. Deterministik (bukan LLM) = hasil konsisten + murah.

3/ Bonus: balance check otomatis. Sistem validasi saldo awal + mutasi
= saldo akhir. Menolak diam-diam? Tidak, bilang jelas bedanya.

4/ Sekarang support BCA. Mandiri/BNI/BRI di pipeline.

Coba gratis: https://rapidapi.com/oyi77/api/docai
```

---

## 4. Telegram — grup developer Indonesia

```
[POC / Open] DocAI — API parser e-statement bank Indonesia

Udah punya produk yang butuh data transaksi bank tapi malas parse
PDF? Cek ini:

POST /parse  (multipart: file=statement.pdf, bank=bca)
-> JSON: account_number, account_name, period, opening/closing
   balance, transactions[], balance_check

- Deterministic (regex-based, bukan LLM) — cocok untuk pipeline
  yang butuh hasil konsisten & biaya prediktif
- CSV mode: ?format=csv
- Error handling jelas: password_protected (PDF e-statement BCA
  sering dikunci DOB), parse_error, invalid_request
- Free tier di RapidAPI, docs lengkap: https://rapidapi.com/oyi77/api/docai

Contoh:
curl -X POST "https://docai.p.rapidapi.com/parse" \
  -F "file=@statement.pdf" -F "bank=bca" \
  -H "X-RapidAPI-Host: docai.p.rapidapi.com" \
  -H "X-RapidAPI-Key: YOUR_KEY"

Feedback / permintaan bank baru diterima. 🚀
```

---

## 5. Posting forum / komunitas (mis. rindoku, forum dev)

```
Halo semua, saya mau share API yang baru saya launch di RapidAPI:
DocAI — parser e-statement bank Indonesia (PDF -> JSON/CSV).

Latar belakang: kerjaan freelance saya banyak berkutat di laporan
keuangan UMKM, dan manual entry mutasi bank itu menyebalkan + rawan
salah. Jadi saya bangun parser yang deterministik (tanpa LLM, biaya
per dokumen ~Rp0), lengkap dengan balance check otomatis supaya
hasilnya teraudit sendiri.

Status sekarang: BCA stable. Mandiri/BNI/BRI sedang dikerjakan —
kalau di sini ada yang punya sampel e-statement bank tersebut
(anonymized, boleh), DM saya, bakal sangat membantu percepatan.

Free tier: https://rapidapi.com/oyi77/api/docai
Semua masukan diterima dengan senang hati. Terima kasih.
```

---

## 6. Artikel Medium/Dev.to (SEO play) — judul & outline

**Judul pilihan:**
- "Automate Your Bookkeeping: Parse Indonesian Bank e-Statements to JSON"
- "Cara Parse E-Statement BCA ke JSON Tanpa LLM (Deterministic, Rp0/doc)"

**Outline:**
```
1. Masalah: manual entry mutasi bank, typo, saldo tidak balance
2. Kenapa bukan LLM: konsistensi & biaya untuk batch besar
3. Studi kasus: PDF e-statement BCA nyata — apa yang terlihat di teks
4. Pipeline: extract text -> regex kolom -> validasi balance
5. Contoh kode (requests multipart ke RapidAPI, output JSON)
6. Gotcha: password-protected PDF (DOB), format angka 1.234.567,89,
   label DB/CR, tahun di DD/MM
7. Roadmap: Mandiri/BNI/BRI, template import Jurnal/Accurate
8. CTA: rapidapi.com/oyi77/api/docai
```

---

## 7. Sticky notes buat screenshots/thumbnail

- Screenshot response JSON parse (sudah ada dari test live) + arrow ke
  field `balance_check: "passed"` — ini bukti terkuat
- GIF demo: upload PDF -> JSON keluar (bisa pakai Loom/LICEcap)
- Kalau mau, generate ulang banner dengan warna brand sendiri —
  font/posisi ada di `scripts/generate_promo_banners.py`

---

## Checklist publish

- [ ] Ganti `YOUR_KEY` di contoh kode sesuai audience (jangan expose key produksi)
- [ ] Sertakan screenshot response JSON asli sebagai bukti
- [ ] Posting di 2-3 channel dulu, ukur komentar/klik, baru scale
- [ ] Pantau RapidAPI Analytics setelah 3-7 hari (hub: oyi77)