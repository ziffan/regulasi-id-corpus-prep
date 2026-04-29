# Decision Tree: Apakah PDF Saya Bisa Diproses?

Panduan ini membantu Anda menentukan apakah file PDF regulasi Anda dapat diproses oleh `regulasi-id-corpus-prep` **tanpa memerlukan kemampuan pemrograman**.

---

## Langkah 1: Buka PDF di browser atau Adobe Reader

Buka file `.pdf` Anda menggunakan salah satu:
- Google Chrome / Microsoft Edge / Firefox (drag & drop file ke browser)
- Adobe Acrobat Reader

---

## Langkah 2: Coba seleksi teks

1. Klik di area teks di dalam PDF (misalnya di bagian isi Pasal pertama)
2. Tekan **Ctrl+A** (Windows/Linux) atau **Cmd+A** (Mac) untuk pilih semua teks
3. Tekan **Ctrl+C** untuk menyalin

---

## Langkah 3: Tempel ke Notepad / TextEdit

1. Buka Notepad (Windows) atau TextEdit (Mac)
2. Tekan **Ctrl+V** untuk menempel

---

## Interpretasi hasil:

### ✅ JALUR A — Teks tempel terbaca (born-digital PDF)

Teks yang ditempel terlihat seperti teks normal (meski mungkin berantakan):

```
PERATURAN OTORITAS JASA KEUANGAN NOMOR 40 TAHUN 2024 TENTANG LAYANAN
PENDANAAN BERSAMA BERBASIS TEKNOLOGI INFORMASI...
```

**→ PDF Anda dapat diproses oleh tool ini.**

Jalankan:
```bash
regulasi-id-corpus-prep run dokumen.pdf --profile ojk-pojk
```

---

### ❌ JALUR B — Teks tidak bisa diseleksi / hasil tempel kosong (PDF scan)

Saat Anda mencoba menyeleksi teks:
- Kursor berubah menjadi ikon tangan atau salib (bukan kursor teks)
- Tidak ada teks yang ter-highlight
- Hasil tempel di Notepad kosong

**→ PDF Anda adalah hasil scan (gambar/foto dokumen).**

Tool ini **tidak dapat** memproses PDF scan. Alternatif:
- Gunakan layanan OCR seperti Adobe Acrobat Pro (menu Tools → Recognize Text)
- Gunakan Google Drive: upload PDF → klik kanan → "Buka dengan Google Docs" (OCR otomatis)
- Gunakan alat OCR open-source seperti [Tesseract](https://github.com/tesseract-ocr/tesseract)

Setelah OCR selesai dan teks dapat diseleksi, kembalilah ke Langkah 1.

---

### ⚠️ JALUR C — Teks tempel ada tapi penuh karakter aneh

Hasil tempel seperti:
```
炉瀥瀭畬愭瀱潲湩琱㔱椱最桴楮稱湩楯湲浳獥楳潮攱❮
```

**→ PDF Anda menggunakan font khusus dengan encoding non-standar.**

Tool ini akan mengekstrak teks, tapi hasil kemungkinan tidak bisa dibaca. Coba langkah:
1. Cek apakah ada versi lain PDF ini yang bisa diunduh dari sumber resmi
2. Laporkan sebagai bug di [GitHub Issues](https://github.com/ziffan/regulasi-id-corpus-prep/issues) dengan menyertakan nama file (tanpa konten sensitif)

---

## Unduh PDF dari JDIH OJK

Tool ini tidak mengunduh PDF secara otomatis. Unduh manual dari:
- **POJK:** https://ojk.go.id/id/regulasi/Pages/POJK.aspx
- **SEOJK:** https://ojk.go.id/id/regulasi/Pages/SE-OJK.aspx
- **JDIH OJK:** https://jdih.ojk.go.id/
