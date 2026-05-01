# Panduan Validasi Manual Output Corpus

Dokumen ini adalah **checklist untuk validator manusia** — tidak memerlukan kemampuan pemrograman. Gunakan setelah menjalankan perintah `validate` atau `run` untuk memverifikasi bahwa output `.txt` (atau `.md`) layak digunakan sebagai corpus.

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

**Yang diperiksa:** Apakah baris pertama file output berisi judul dokumen yang benar?

**Cara:**
1. Buka file output di teks editor
2. Lihat baris paling atas

**Yang diharapkan** (contoh per jenis dokumen):

| Profile | Contoh baris pertama |
|---------|---------------------|
| `ojk-pojk` | `SALINAN PERATURAN OTORITAS JASA KEUANGAN REPUBLIK INDONESIA NOMOR 40 TAHUN 2024 TENTANG...` |
| `ojk-seojk` | `SALINAN SURAT EDARAN OTORITAS JASA KEUANGAN NOMOR...` |
| `ri-pp` | `PERATURAN PEMERINTAH REPUBLIK INDONESIA NOMOR...` |
| `ri-uu` | `UNDANG-UNDANG REPUBLIK INDONESIA NOMOR...` |

**Tanda masalah:**
- Baris pertama kosong atau hanya berisi karakter aneh
- Judul terpotong di tengah
- Nomor halaman atau URL muncul di awal

---

### ✅ Langkah 2: Hitung Penanda Struktur Utama

**Yang diperiksa:** Apakah jumlah penanda struktur di output cocok dengan PDF asli?

**Cara:**
1. Di teks editor, tekan **Ctrl+F**
2. Cari pola sesuai jenis dokumen:

| Profile | Yang dicari | Catatan |
|---------|-------------|---------|
| `ojk-pojk` | `Pasal ` (dengan spasi) | |
| `ojk-seojk` | `I. `, `II. `, `III. ` | Bagian bernomor Romawi |
| `ri-pp` | `Pasal ` (dengan spasi) | |
| `ri-uu` | `Pasal ` (dengan spasi) | Bisa Pasal I/II (Romawi) atau Pasal 1/2 (Arab) |

3. Catat jumlah hasil yang ditemukan
4. Bandingkan dengan PDF asli

**Yang diharapkan:** Jumlah cocok ± 1 (perbedaan kecil bisa terjadi karena referensi lintas-Pasal).

**Tanda masalah:** Lebih dari 5% Pasal/bagian hilang → kemungkinan halaman tidak terekstrak.

---

### ✅ Langkah 3: Cek Blok Hilang (Spot-Check)

**Yang diperiksa:** Apakah isi Pasal/bagian penting tidak ada?

**Cara:**
1. Pilih **3 Pasal secara acak** dari PDF asli
2. Cari kalimat pertama masing-masing Pasal di file output menggunakan Ctrl+F
3. Pastikan teksnya ada dan tidak terpotong

**Tanda masalah:**
- Kalimat yang ada di PDF tidak ditemukan di output
- Teks terpotong di tengah kalimat tanpa lanjutan

---

### ✅ Langkah 4: Cek Lampiran

**Yang diperiksa:** Apakah perlakuan LAMPIRAN sesuai dengan profile yang digunakan?

Perlakuan berbeda tergantung profile:

| Profile | Perlakuan LAMPIRAN |
|---------|--------------------|
| `ojk-pojk` | Dipertahankan — cari `LAMPIRAN` di output, pastikan ada |
| `ojk-seojk` | Dipertahankan |
| `ri-pp` | **Dihapus secara sengaja** — jangan heran jika tidak ada |
| `ri-uu` | **Dihapus secara sengaja** — jangan heran jika tidak ada |

**Untuk `ri-pp` dan `ri-uu`:** Lampiran umumnya berisi tabel/formulir yang tidak membawa makna hukum normatif dalam format teks. Jika isi lampiran diperlukan, gunakan file `.raw.txt` (output tahap `extract`) sebagai sumber lengkap.

**Catatan:** Lampiran berupa gambar tidak akan terekstrak pada profil manapun (normal).

---

### ✅ Langkah 5: Cek Sisa Noise

**Yang diperiksa:** Apakah ada sisa noise yang lolos dari normalisasi?

**Cara:** Di teks editor, cari (Ctrl+F) pola berikut sesuai sumber PDF:

**Untuk semua profil OJK:**

| Pola yang dicari | Yang seharusnya tidak ada |
|-----------------|--------------------------|
| `jdih.ojk.go.id` | Link footer JDIH |
| ` - 1 -` | Nomor halaman |
| `https://` | URL apapun |

**Untuk profil RI (ri-pp, ri-uu):**

| Pola yang dicari | Yang seharusnya tidak ada |
|-----------------|--------------------------|
| `Menemukan kesalahan ketik` | Banner laporan typo |
| `SK No` | Penanda dokumen per halaman (SALINAN) |

**Yang diharapkan:** Tidak ada hasil ditemukan untuk semua pola di atas.

---

### ✅ Langkah 6: Baca Cepat 3 Paragraf Acak

**Yang diperiksa:** Apakah teks mengalir dengan natural (tidak ada kata-kata yang "menyatu" atau terpotong aneh)?

**Cara:** Pilih 3 paragraf acak dari file output dan baca sekilas.

**Tanda masalah:**
- Kata-kata menyatu tanpa spasi: `BabIKetentuan` atau `Pasal1Dalam`
- Kalimat terpotong tiba-tiba tanpa lanjutan
- Karakter aneh seperti `???` atau kotak hitam (`■`)

**Catatan untuk output `--format md`:** Baris heading Markdown (`##`, `###`) adalah normal — bukan noise.

---

## Skala Keputusan

| Temuan | Tindakan |
|--------|----------|
| Semua langkah lulus | Output siap digunakan sebagai corpus |
| 1–2 masalah minor (sisa noise, 1-2 Pasal hilang) | Gunakan dengan catatan; laporkan sebagai issue |
| Lebih dari 5% Pasal hilang atau teks tidak terbaca | Jangan gunakan; laporkan ke pengembang |

---

## Melaporkan Masalah

Jika output tidak sesuai harapan, buka issue di GitHub dengan menyertakan:
- Nama file PDF (tanpa mengunggah konten dokumen)
- Profile yang digunakan (`ojk-pojk`, `ojk-seojk`, `ri-pp`, atau `ri-uu`)
- Screenshot atau kutipan teks yang bermasalah
- Nomor Pasal atau bagian spesifik yang bermasalah

GitHub Issues: https://github.com/ziffan/regulasi-id-corpus-prep/issues
