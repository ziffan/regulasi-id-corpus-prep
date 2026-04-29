# regulasi-id-corpus-prep

Alat CLI untuk mengonversi PDF regulasi Indonesia yang *born-digital* (POJK, SEOJK dari JDIH OJK) menjadi file `.txt` bersih yang siap digunakan sebagai input corpus untuk aplikasi NLP hukum, termasuk [LexHarmoni](https://github.com/ziffan/lexharmoni).

---

## Syarat: PDF Born-Digital, Bukan Hasil Scan

Alat ini **hanya** bekerja pada PDF yang memiliki *text layer* (born-digital). PDF hasil scan (foto/gambar) **tidak didukung** dan akan ditolak dengan pesan jelas.

Tidak yakin PDF Anda termasuk jenis mana? Lihat [docs/DECISION_TREE.md](docs/DECISION_TREE.md).

---

## Quickstart

### Instalasi

Install dari GitHub (saat ini belum tersedia di PyPI):

```bash
pip install git+https://github.com/ziffan/regulasi-id-corpus-prep.git
```

Atau clone dan install dalam mode editable untuk development:

```bash
git clone https://github.com/ziffan/regulasi-id-corpus-prep.git
cd regulasi-id-corpus-prep
pip install -e .
```

> PyPI publish direncanakan setelah v0.1.0 mendapat review pengguna non-teknis.

### Jalankan Pipeline Penuh (untuk pengguna non-teknis)

```bash
regulasi-id-corpus-prep run dokumen-saya.pdf --profile ojk-pojk
```

Atau untuk seluruh folder:

```bash
regulasi-id-corpus-prep run ./folder-pdf/ --profile ojk-pojk --output-dir ./output/
```

Untuk dokumen SEOJK:

```bash
regulasi-id-corpus-prep run ./folder-pdf/ --profile ojk-seojk --output-dir ./output/
```

### Perintah Individual

```bash
# Langkah 1: Ekstrak teks dari PDF
regulasi-id-corpus-prep extract dokumen.pdf

# Langkah 2: Normalisasi teks
regulasi-id-corpus-prep normalize dokumen.raw.txt --profile ojk-pojk

# Langkah 3: Validasi otomatis
regulasi-id-corpus-prep validate dokumen.txt --profile ojk-pojk

# Lihat profile yang tersedia
regulasi-id-corpus-prep list-profiles
```

### Output yang Dihasilkan

Untuk setiap `<nama>.pdf`, alat ini menghasilkan:

| File | Isi |
|------|-----|
| `<nama>.raw.txt` | Teks mentah hasil ekstraksi PDF |
| `<nama>.raw.meta.json` | Metadata ekstraksi (jumlah halaman, timestamp, dll.) |
| `<nama>.txt` | Teks bersih siap corpus |
| `<nama>.meta.json` | Audit trail transformasi (rule apa yang diterapkan, berapa match) |

---

## Profile

Profile adalah file YAML yang mendefinisikan aturan pembersihan untuk jenis dokumen tertentu. Dua profile bawaan tersedia:

| Profile | Dokumen |
|---------|---------|
| `ojk-pojk` | POJK (Peraturan OJK) dari JDIH OJK |
| `ojk-seojk` | SEOJK (Surat Edaran OJK) dari JDIH OJK |

Untuk membuat profile baru (PBI, Permenkeu, dll.), lihat [docs/PROFILE_GUIDE.md](docs/PROFILE_GUIDE.md) dan gunakan `regulasi_id_corpus_prep/profiles/_template.yaml` sebagai titik awal.

---

## Validasi Manual

Validasi otomatis (`validate` subcommand) mengecek hal-hal teknis. Untuk memastikan **substansi** dokumen benar, ikuti checklist di [docs/VALIDATION_GUIDE.md](docs/VALIDATION_GUIDE.md) — tidak memerlukan kemampuan pemrograman.

---

## Keterbatasan (v0.1.0)

- **PDF born-digital saja.** PDF scan (foto regulasi) tidak dapat diproses.
- **Bahasa Indonesia.** Dokumen berbahasa lain tidak diuji.
- **Profile OJK saja.** Arsitektur mendukung PBI, Permenkeu, dll., tapi belum ada profile-nya.
- **Tidak mengunduh PDF.** Pengguna perlu mengunduh PDF secara manual dari JDIH OJK.
- **Tidak ada pemahaman semantik.** Output adalah teks biasa; hierarki Pasal tidak diurai.

---

## Lisensi

Apache 2.0. Lihat [LICENSE](LICENSE).

Alat ini menggunakan [PyMuPDF](https://github.com/pymupdf/PyMuPDF) (AGPL-3.0) sebagai dependensi ekstraksi PDF. Lihat [NOTICE](NOTICE) untuk detail.
