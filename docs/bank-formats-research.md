# Riset Format E-Statement Bank Indonesia — untuk Ekstensi Parser DocAI

> Status: BCA (live) + Mandiri/BNI/BRI/OCBC (riset selesai, verified dari parser GitHub). BSI/CIMB Niaga/Permata/BTN: tidak ada parser publik ditemukan.
> Sumber: contoh PDF asli via Scribd + kode parser GitHub (fahminlb33/bank-statement-extractor, HariNurd/convert-estatement-BNI-pdf-to-excel, rzpelv01/rekap-rekening, Michael-dvs/FinExtract, ACC-TAX-REIGHTEEN/Mutasi-BRI-CSV-PDF-ke-Excel).
> **[VERIFIED]** = dikutip langsung dari teks PDF asli / sample parser asli. **[DESCRIBED]** = dari artikel/blog/kode kedua.

---

## Ringkasan penting lintas bank

| Bank | Title PDF | Header kolom | Format tanggal | Format nominal | Tanda arah | Password |
|---|---|---|---|---|---|---|
| BCA (live) | (estatement BCA) | `TANGGAL KETERANGAN CBG MUTASI SALDO` | `DD/MM` (+tahun di periode) | `9,846,915.69` (koma ribuan) | Label `DB`/`KR` | DOB `DDMMYYYY` |
| Mandiri (modern, Livin' 2023+) | `e-Statement` | `No Tanggal Keterangan Nominal (IDR) Saldo (IDR)` (bilingual 2 baris) | `DD Mon YYYY` + `HH:MM:SS WIB` | `1.234.567,89` (titik ribuan, koma desimal) | Sign `+`/`-` (minus = debit) | DOB `DDMMYYYY` |
| BNI (modern, Wondr 2023+) | `Laporan Mutasi Rekening` | `Tanggal & Waktu Rincian Transaksi Nominal (IDR) Saldo (IDR)` | `DD Mon YYYY` + `HH:MM:SS WIB` | `1,234,567` (koma ribuan, TANPA desimal) | Sign `+`/`-` (minus = debit) | DOB `ddmmyyyy` |
| BRI — rekening koran (IBBIZ/BRIIbiz) | `Rekening koran` / `Mutasi ... Rekening BRI` | tgl jam uraian + 3 kolom nominal (dua amount + saldo) | `DD/MM/YY` + `HH:MM:SS` | `1,234,567.89` (EN-US) | Kolom nominal terpisah: debit & kredit | ? |
| BRI — BRImo (mutasi mobile) | `Mutasi BRImo` | `Tanggal Transaksi ... Debet Kredit Saldo` | `DD/MM/YY` (+opsional jam) | `1,234,567` (koma ribuan) | Kolom Debet/Kredit terpisah | ? |
| OCBC (mutasi mobile/web) | — | `TGL TRANS TGL VALUTA URAIAN DEBET KREDIT SALDO` | `DD/MM` | `1,234,567` (koma ribuan) | Kolom DEBET/KREDIT terpisah | ya (pdfplumber `password=`) |

**Pelajaran lintas bank:**
- Semua bank modern pakai **sign `+`/`-`** di kolom nominal; bank legacy pakai kolom Debit/Credit terpisah atau label `DB`/`CR`. Parser harus deteksi dua gaya ini.
- **Ada 2 generasi format per bank** (modern app ~2023+ vs legacy web/IB/koran). Perlu detektor berbasis token unik: `e-Statement`+`Mandiri Call 14000`, `Account Statement`, `ACCOUNT STATEMENT`+`DB/CR`, `Tanggal & Waktu`.
- Konvensi angka beda-beda: Mandiri `1.234.567,89`, BNI modern `1,234,567` (no decimal), BNI legacy `4,200,000.00`. Parser tidak boleh hardcode satu konvensi.
- Seluruh PDF umumnya **password-protected dengan DOB `DDMMYYYY`** — endpoint perlu support password (parameter `password`).
- Batas akhir tabel Mandiri: `ini adalah batas akhir transaksi anda`; footer legal + `N dari M` di semua bank.

---

## BANK MANDIRI

### A. Format modern — Livin' by Mandiri e-Statement (2023+) [VERIFIED]
Sumber: scribd.com/document/867768871 (`e-Statement_…9719_01 Apr 2025-30 Apr 2025`), scribd.com/document/830356419 (e-Statement PT Avinto Sukses, Feb 2025).

**Kolom (header bilingual, 2 baris per label):**
```
No | Tanggal/Date | Keterangan/Remarks | Nominal (IDR)/Amount (IDR) | Saldo (IDR)/Balance (IDR)
```
Tidak ada kolom D/K.

**Metadata (atas halaman 1):**
- `e-Statement`, `Nama/Name`, `Cabang/Branch` (e.g. `KCP Serang Cikande`), `Dicetak pada/Issued on`, `Periode/Period` (e.g. `01 Apr 2025 - 30 Apr 2025`), `Nomor Rekening/Account Number` (e.g. `1300027219719`), `Mata Uang/Currency` (`IDR`)
- Blok ringkasan: `Saldo Awal/Initial Balance`, `Dana Masuk/Incoming Transactions`, `Dana Keluar/Outgoing Transactions`, `Saldo Akhir/Closing Balance`

**Format tanggal:** `DD Mon YYYY` (e.g. `05 Apr 2025`) + waktu terpisah `HH:MM:SS WIB`. Tanggal di baris sendiri — pattern aman untuk boundary baris: `^\d{2} [A-Z][a-z]{2} \d{4}$`.

**Format nominal:** `1.234.567,89` (titik=ribuan, koma=desimal), **semua nominal ada sign `+`/`-`**; minus = debit/keluar, plus = kredit/masuk. Saldo tanpa sign.

**Contoh baris asli [VERIFIED]:**
```
14:39:33 WIB Transfer ke BANK MANDIRI BERSAMA SILALAHI 1 6300072535 14    -50.000,00
17:18:28 WIB Transfer BI Fast Dari KANISAH 6285283743827 DANA20250207 ... +10.000,00
10:22:40 WIB Transfer BI Fast Dari BCA KHUSTINI 4921073601 Tf             +200.000,00
17:40:09 WIB Biaya administrasi kartu debit                               -3.500,00
11 | 12 Feb 2025 | 19:08:39 WIB | Transfer ke BANK MANDIRI FADILAH AZMI 1330026577999 | -17.250.000,00 | 99.179,00
```

**Password:** ya, DOB `DDMMYYYY` (ezmutasi.com + GitHub parser perlu flag `-p`).

**Quirk:**
- Penanda akhir tabel: `ini adalah batas akhir transaksi anda`
- Deskripsi mengandung ref/penerima: `Transfer BI Fast Dari KANISAH 6285283743827`, `Gaji PT PWI Prd Maret 2025`
- Disclaimer legal bilingual + `PT Bank Mandiri (Persero) Tbk. ... OJK ... LPS`, `Mandiri Call 14000`, `1 dari 2`

### B. Format legacy

**B1. Mandiri Online "Account Statement" (web/IB ~2021-2024) [VERIFIED]** — scribd.com/document/742899452:
- Meta satu baris: `Account No 1440025261188 IDR ARIS LINTAS RAYA Period 01 June 2024 - 08 June 2024 Currency IDR Branch Name KCP Malang Ahmad Yani Opening Balance 123,854.96`
- Headers: `Posting Date | Remarks | Reference Number | Debit | Credit | Balance`
- Baris: `03/06/2024 09:16:57 20240603BMRIIDJA010O9930760399 CENAIDJA/ARITA RACHMAWATI NINGRUM KAS KECIL 99102- 100,000.00 0.00 23,854.96`
- **Format angka EN-US** (`100,000.00`), tanggal `DD/MM/YYYY` + `HH:MM:SS`, summary `No of Debit 7 ... Total Amount Debited ... Closing Balance 24,354.96`

**B2. Mutasi tabungan lama (pre-2022) [VERIFIED-DESCRIBED]** — github.com/fahminlb33/bank-statement-extractor sample `mandiri_2022_07.pdf`:
- Baris mulai literal `-` (e.g. `-UBP60148870801800000…`, `-20220707BMRIIDJA01…`), tanggal `DD/MM` (`transaction_date` + `valuta_date`), kolom `D`/`K` flag, lalu saldo
- Summary: `SALDO AWAL : 1.234.567,89` / `Saldo Akhir : …` / `Mutasi Kredit : …` / `Mutasi Debit : …`
- Deteksi halaman 1: token `mandiri call 14000`

### C. Repo parser Mandiri [VERIFIED]
- github.com/fahminlb33/bank-statement-extractor (Python: `bca`, `mandiri`, `jago`, support password `-p`)
- github.com/rzpelv01/rekap-rekening (`_parse_pdf_mandiri`, format Account Statement)

---

## BANK BNI

### A. Format modern — Wondr/BNI Mobile "Laporan Mutasi Rekening" (2023+) [VERIFIED]
Sumber: scribd.com/document/1045998436 (BNI 327872529 Nov 2024), scribd.com/document/1052387326 (Feb 2026), scribd.com/document/1052387175 (Apr 2026).

**Kolom:**
```
Tanggal & Waktu | Rincian Transaksi | Nominal (IDR) | Saldo (IDR)
```

**Metadata (halaman 1):**
- Title `Laporan Mutasi Rekening`
- `Periode: 1 - 30 November 2024` (nama bulan Indonesia)
- Identitas: `TAPLUS - 327872529` / `TAPLUS MUDA - 399105645` (**label produk + ` - ` + nomor rekening 10 digit**), `Kantor Cabang: BOGOR`, `Mata Uang: IDR`
- Summary atas: `Saldo Awal`, `Total Pemasukan`, `Total Pengeluaran`, `Saldo Akhir`

**Format tanggal:** `DD Mon YYYY` + `HH:MM:SS WIB` (e.g. `25 Nov 2024 13:29:09 WIB`).

**Format nominal:** **koma ribuan, TANPA desimal**, dengan sign `+`/`-` (e.g. `+50,000`, `-2,210,784`). Minus = debit. Saldo unsigned (e.g. `1,551,141`).

**Contoh baris asli [VERIFIED]:**
```
25 Nov 2024 13:29:09 WIB Transfer BNI - PRIYO DWI CAHYONO              +50,000       1,551,141
25 Nov 2024 07:28:19 WIB Virtual Account TOKOPEDIA - PLSTOKOPEDIAANDI  -2,210,784     7,935,378
25 Nov 2024 12:40:13 WIB Pembayaran MARUGAME FX SUDIRMAN - JAKARTA PUSAT -126,000     7,809,378
25 Nov 2024 19:40:46 WIB Transfer BNI - PT FLIPTECH LENTERA INSPIRASI PERTIWI -4,020,301 3,789,077
27 Nov 2024 10:25:42 WIB Tarik Tunai ATM                               -1,500,000     2,289,077
30 Nov 2024 23:59:59 WIB Lainnya Bunga                                  +233          3,789,310
02 Feb 2026 16:37:17 WIB Transfer BANK SUMUT - SAIMA PUTRI   +10,000     36,876,186
04 Feb 2026 09:10:17 WIB Biaya Transfer BI-FAST             -2,500      30,356,686
```

**Password:** ya, DOB `ddmmyyyy` (ezmutasi.com). Catatan: beberapa salinan Scribd sudah di-unlock.

**Quirk:**
- Kredit kecil: `Lainnya Bunga +233`
- Baris sintetis tengah malam `23:59:59 WIB` (e.g. `Lainnya BV TRK TRF/STD ORD`)
- Keterangan kategori: `Transfer BNI - <name>`, `Transfer <BANK> - <name>`, `Virtual Account TOKOPEDIA - ...`, `Pembayaran Qris ...`, `Biaya Transfer BI-FAST`, `Tarik Tunai ATM`, `Lainnya ...`
- Quirk layout: suffix `ID` (dari IDR) bisa nempel di akhir keterangan (`…JAKARTA TIMURID`) — perlu stripping
- Blok akhir: `Informasi Lainnya: 1. Apabila terdapat kesalahan data ... 7 hari kerja ...` + `N dari M`

### B. Format legacy

**B1. BNI IB "Laporan Mutasi Rekening / Rekening Koran" (~2020-2023) [VERIFIED]** — scribd.com/document/650802232 (Apr 2020):
- Meta: `Tanggal Laporan: 2 Juli 2020 | Periode transaksi: 01/04/2020 – 18/04/2020 | Halaman: 4 | No. Rekening: 001678340 | No. Kartu: … | Nama: VERNANDYA VINNY | Valuta: IDR`
- Headers: `Tgl. | Keterangan | Cab. | Mutasi | Saldo` — suffix `DB`/`CR` di dalam sel Mutasi (`4,200,000.00 DB`)
- Baris: `01/04 TRSF E-BANKING DB 01/04 73283 FATMA AFIFATUL 03 72 4,200,000.00 0.00 DB 153,460,000.00` — **angka EN-US**, tanggal `DD/MM`

**B2. BNI corporate "ACCOUNT STATEMENT" (BNI Smart/BNI Direct) [DESCRIBED]** — github.com/rzpelv01/rekap-rekening `_parse_pdf_bni`:
- Deteksi: `ACCOUNT STATEMENT` + `DB/CR` + `Account No.`
- Headers: `Posting Date | Effective Date | Branch | Journal | Transaction Description | Amount | DB/CR | Balance`
- Meta: `Account No. : 0045206873`, `Period : 01-Jun-24 - 30-Jun-24`, `Ledger Balance`, `Ending Balance`, `Total Debet / Total Credit`
- Angka **Indonesia** `1.234.567,89`; kolom DB/CR bernilai `D`/`K`

### C. Repo parser BNI [VERIFIED]
- github.com/HariNurd/convert-estatement-BNI-pdf-to-excel (Python + tabula, format modern Wondr)
- github.com/rzpelv01/rekap-rekening (`_parse_pdf_bni`, format corporate)

---

---

## BANK BRI

### A. Format rekening koran (BRIIbiz / Created By IBBIZ) [VERIFIED]
Sumber: github.com/Michael-dvs/FinExtract `parser/BRI.py` (sample asli: `Mutasi Juli Rekening BRI 203901000446308.pdf`).

**Baris transaksi (regex asli parser):**
```
^(\d{2}/\d{2}/\d{2})\s+\d{2}:\d{2}:\d{2}\s+(.+?)\s+(\d{7,})?\s*([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})$
```
Struktur: `DD/MM/YY | HH:MM:SS | uraian | user_id (opsional, 7+ digit) | amount-kiri | amount-kanan | saldo`

- **Format angka EN-US** (`1,234,567.89`)
- **⚠ Urutan debit/kredit kontroversial:** parser FinExtract menetapkan `debit = amount-kanan`, `credit = amount-kiri` — kebalikan dari ekspektasi umum "DEBET kiri, KREDIT kanan". Perlu sampel PDF asli untuk memastikan arah kolom sebenarnya.
- Baris uraian lanjutan (tanpa tanggal) di-append ke uraian transaksi sebelumnya.
- **Footer/skip list:** `halaman N`, `saldo akhir`, `jumlah mutasi`, `rekening koran`, `Created By IBBIZ`, `saldo awal` / `opening balance`, `closing balance`, `total transaksi debet/kredit`, `terbilang`, `biaya materai`
- Nomor rekening contoh: `203901000446308` (15 digit, awalan `2039`)

### B. Format mutasi BRImo (mobile) [VERIFIED]
Sumber: github.com/ACC-TAX-REIGHTEEN/Mutasi-BRI-CSV-PDF-ke-Excel `bri_pdf2excel.py`.

- Baris mulai `^(\d{2}/\d{2}/\d{2})` (DD/MM/YY), opsional jam `HH:MM:SS` di posisi kedua.
- Struktur: `Tanggal [Jam] Uraian... [Teller_id?] Debet Kredit Saldo` — parser membaca dari belakang: `saldo = parts[-1]`, `kredit = parts[-2]`, `debet = parts[-3]`, `teller_id = parts[-4]` (jika numeric).
- **Format angka koma ribuan** (`1,234,567`), lalu koma di-strip, prefix `IDR`/`Rp` dibuang.
- Tabel mulai setelah baris `Tanggal Transaksi` / `Transaction Date`; berhenti saat `Saldo Awal` / `Opening Balance` / `Total Transaksi`.
- **Kesimpulan deteksi:** BRImo = kolom Debet/Kredit terpisah; rekening koran = 3 kolom nominal (amount+amount+saldo). Token pembeda: `Created By IBBIZ` + `rekening koran` (koran) vs `Tanggal Transaksi` + `Mutasi` (BRImo).

---

## BANK OCBC

### Format mutasi OCBC (mobile/web) [VERIFIED]
Sumber: github.com/Michael-dvs/FinExtract `parser/OCBC.py`.

**Kolom:**
```
TGL TRANS | TGL VALUTA | URAIAN | DEBET | KREDIT | SALDO
```
- Deteksi header: baris mengandung `TRANS` + (`URAIAN` atau `DESCRIPTION`) + `VALUTA` sekaligus.
- Baris transaksi baru: kolom pertama berisi tanggal (`DD/MM`) ATAU mengandung `BEGINNING BALANCE` / `SALDO AWAL` / `SALDO SEBELUMNYA` / `BROUGHT FORWARD`.
- Support password via `pdfplumber.open(path, password=password)`.
- ⚠ Quirk parser FinExtract: mereka menukar kolom DEBET ↔ KREDIT saat ekspor — kemungkinan koreksi atas layout PDF yang kebalik. Perlu sampel asli untuk konfirmasi.
- Format angka tidak di-normalisasi di parser (dibiarkan mentah dari PDF).

---

## BANK LAIN (BSI, CIMB Niaga, Permata, BTN, dll)

**Tidak ada parser publik yang ditemukan** di GitHub (search API: `cimb niaga mutasi parser`, `bsi mutasi statement parser`, `permata statement parser`, `btn mutasi rekening` → semua kosong). Parser komunitas yang ada hanya: BCA, Mandiri (2 generasi), BNI (modern + corporate), BRI (BRImo + rekening koran), Jago, OCBC.

**Implikasi:** bank-bank ini = peluang greenfield untuk DocAI, tapi juga **tanpa referensi format yang bisa diverifikasi** — implementasinya harus dimulai dari sampel PDF asli (minta user kirim / jadikan call-to-action di materi promo: "kirim e-statement bank X, kami support minggu ini").

---

## Implikasi implementasi untuk DocAI

1. **Endpoint `POST /parse` perlu parameter baru `password`** (opsional) — mayoritas PDF e-statement terkunci DOB.
2. **Detektor bank & format** harus berbasis token unik per generasi:
   - BCA native: `TANGGAL KETERANGAN CBG MUTASI SALDO` / `SALDO AWAL`
   - Mandiri modern: `e-Statement` + `Saldo Awal/Initial Balance` + `Mandiri Call 14000`
   - Mandiri legacy: `Account No` + `Posting Date`
   - BNI modern: `Tanggal & Waktu` + `Rincian Transaksi` + `Laporan Mutasi Rekening`
   - BNI legacy: `Tgl. Keterangan Cab. Mutasi Saldo` + `DB` suffix / `ACCOUNT STATEMENT`
   - BRI koran: `rekening koran` + `Created By IBBIZ` (3 kolom nominal)
   - BRI BRImo: `Tanggal Transaksi` + kolom `Debet Kredit Saldo`
   - OCBC: `TGL TRANS` + `VALUTA` + `URAIAN`
3. **Normalisasi angka** per format: detect dot-vs-comma convention (Mandiri: titik ribuan+koma desimal; BNI modern: koma ribuan no desimal; BRI koran/legacy: EN-US comma/dot; BRImo/OCBC: koma ribuan).
4. **CSV/serialization** tidak berubah — transaksi tetap `date, description, debit, credit, balance`.
5. Sampel berformat baru bisa diunduh dari Scribd (URL di atas) untuk fixture pengujian.