# Panduan Validasi Manual Output Corpus

Dokumen ini adalah **checklist untuk validator manusia** — tidak memerlukan kemampuan pemrograman. Gunakan setelah menjalankan perintah `validate` atau `run` untuk memverifikasi bahwa output `.txt` layak digunakan sebagai corpus.

Alat `validate` melakukan pemeriksaan teknis otomatis. Panduan ini melengkapinya dengan pemeriksaan **substansi** yang hanya bisa dilakukan oleh manusia.

---

## Alat yang Diperlukan

- Teks editor sederhana (Notepad, TextEdit, VS Code, Notepad++)
- Fungsi "Find" / pencarian di teks editor (biasanya **Ctrl+F**)
- Salinan PDF asli untuk perbandingan

---

## Checklist Validasi (6 Langkah)

---

### ✅ Langkah 1: Cek Judul Dokumen

**Yang diperiksa:** Apakah baris pertama file `.txt` berisi judul dokumen yang benar?

**Cara:**
1. Buka file `.txt` di teks editor
2. Lihat baris paling atas

**Yang diharapkan:**
```
SALINAN PERATURAN OTORITAS JASA KEUANGAN REPUBLIK INDONESIA NOMOR 40 TAHUN 2024 TENTANG LAYANAN PENDANAAN BERSAMA BERBASIS TEKNOLOGI INFORMASI...
```

**Tanda masalah:**
- Baris pertama kosong atau hanya berisi karakter aneh
- Judul terpotong di tengah
- Nomor halaman atau URL JDIH muncul di awal

---

### ✅ Langkah 2: Hitung Pasal (atau Bagian untuk SEOJK)

**Yang diperiksa:** Apakah jumlah Pasal di output `.txt` cocok dengan PDF asli?

**Cara:**
1. Di teks editor, tekan **Ctrl+F**
2. Ketik `Pasal ` (dengan spasi) — untuk POJK
   - Untuk SEOJK, cari pola bagian seperti `I.`, `II.`, dll.
3. Catat jumlah hasil yang ditemukan
4. Bandingkan dengan jumlah Pasal di PDF asli (lihat di halaman terakhir atau daftar isi)

**Yang diharapkan:** Jumlah cocok ± 1 (perbedaan kecil bisa terjadi karena referensi lintas-Pasal).

**Tanda masalah:** Lebih dari 5% Pasal hilang → kemungkinan halaman atau bagian tidak terekstrak.

---

### ✅ Langkah 3: Cek Blok Hilang (Spot-Check)

**Yang diperiksa:** Apakah isi Pasal/bagian penting tidak ada?

**Cara:**
1. Pilih **3 Pasal secara acak** dari PDF asli
2. Cari kalimat pertama masing-masing Pasal di file `.txt` menggunakan Ctrl+F
3. Pastikan teksnya ada dan tidak terpotong

**Tanda masalah:**
- Kalimat yang ada di PDF tidak ditemukan di `.txt`
- Teks terpotong di tengah kalimat tanpa lanjutan

---

### ✅ Langkah 4: Cek Lampiran (Jika Ada)

**Yang diperiksa:** Apakah lampiran dokumen (jika ada) ikut terekstrak?

**Cara:**
1. Cari kata `LAMPIRAN` di file `.txt` menggunakan Ctrl+F
2. Jika PDF memiliki lampiran, pastikan kontennya ada

**Catatan:** Lampiran berupa tabel atau gambar tidak akan terekstrak (normal). Hanya teks dalam lampiran yang terekstrak.

---

### ✅ Langkah 5: Cek Sisa Noise

**Yang diperiksa:** Apakah ada sisa noise yang lolos dari normalisasi?

**Cara:** Di teks editor, cari (Ctrl+F) masing-masing pola berikut:

| Pola yang dicari | Yang seharusnya tidak ada |
|-----------------|--------------------------|
| `jdih.ojk.go.id` | Link footer JDIH |
| ` - 1 -` atau ` - 12 -` | Nomor halaman format lama |
| `https://` | URL apapun |

**Yang diharapkan:** Tidak ada hasil ditemukan untuk semua pola di atas.

---

### ✅ Langkah 6: Baca Cepat 3 Paragraf Acak

**Yang diperiksa:** Apakah teks mengalir dengan natural (tidak ada kata-kata yang "menyatu" atau terpotong aneh)?

**Cara:** Pilih 3 paragraf acak dari file `.txt` dan baca sekilas.

**Tanda masalah:**
- Kata-kata menyatu tanpa spasi: `BabIKetentuan` atau `Pasal1Dalam`
- Kalimat terpotong tiba-tiba tanpa lanjutan
- Karakter aneh seperti `???` atau kotak hitam (`■`)

---

## Skala Keputusan

| Temuan | Tindakan |
|--------|----------|
| Semua 6 langkah lulus | Output siap digunakan sebagai corpus |
| 1–2 masalah minor (sisa noise, 1-2 Pasal hilang) | Gunakan dengan catatan; laporkan sebagai issue |
| Lebih dari 5% Pasal hilang atau teks tidak terbaca | Jangan gunakan; laporkan ke pengembang |

---

## Melaporkan Masalah

Jika output tidak sesuai harapan, buka issue di GitHub dengan menyertakan:
- Nama file PDF (tanpa mengunggah konten dokumen)
- Profile yang digunakan (`ojk-pojk` atau `ojk-seojk`)
- Screenshot atau kutipan teks yang bermasalah
- Nomor Pasal atau bagian spesifik yang bermasalah

GitHub Issues: https://github.com/ziffan/regulasi-id-corpus-prep/issues
