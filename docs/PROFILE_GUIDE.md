# Panduan Membuat Profile Baru

Dokumen ini menjelaskan cara membuat profile untuk jenis dokumen regulasi Indonesia yang belum didukung (misalnya PBI dari Bank Indonesia, Permenkeu dari Kementerian Keuangan, dll.).

---

## Apa Itu Profile?

Profile adalah file YAML yang mendefinisikan aturan pembersihan teks untuk satu jenis dokumen regulasi. Setiap profile berisi:
1. **Metadata** — nama, deskripsi, versi
2. **Rules** — daftar aturan transformasi yang dijalankan berurutan
3. **Validation** — konfigurasi untuk pemeriksaan otomatis
4. **Markdown Headings** *(opsional)* — pemetaan pola baris ke heading Markdown

Profile disimpan di `regulasi_id_corpus_prep/profiles/`. Setiap file `.yaml` (kecuali `_template.yaml`) otomatis tersedia via `--profile=nama-file`.

---

## Tiga Tipe Rule

### 1. `noise_removal` — Hapus atau ganti pola tidak diinginkan

```yaml
- name: hapus_footer_jdih
  type: noise_removal
  pattern: 'https?://jdih\.ojk\.go\.id/\s*'   # Python regex
  replacement: ' '                              # Ganti dengan spasi (default)
  flags:
    - IGNORECASE                                # Opsional
```

Gunakan untuk: footer halaman, URL, watermark, nomor halaman, header berulang.

### 2. `whitespace_normalize` — Gabungkan semua whitespace

```yaml
- name: normalize_whitespace
  type: whitespace_normalize
```

Tidak ada parameter tambahan. Rule ini:
- Mengganti semua `\n`, `\t`, spasi ganda (dll.) menjadi satu spasi tunggal
- Menyatukan kalimat yang terpotong antar-baris dalam PDF
- **Wajib dijalankan SEBELUM semua rule `structure_split`**

### 3. `structure_split` — Sisipkan baris baru sebelum elemen struktural

```yaml
- name: split_sebelum_pasal
  type: structure_split
  pattern: 'Pasal\s+\d+'   # Elemen yang akan diawali baris baru
  newlines_before: 2        # 1–4 baris baru (default: 2)
  space_after: false        # Spasi setelah elemen (default: false)
  requires_following: null  # Hanya split jika diikuti pola ini
  flags: []
```

**`requires_following`:** Jika diisi, split hanya dilakukan ketika pola diikuti oleh pola ini. Teks yang mengikuti **dikonsumsi dan disisipkan kembali** dengan spasi. Berguna untuk poin huruf yang ambigu:

```yaml
- name: split_poin_huruf
  type: structure_split
  pattern: '[a-z]\.'
  newlines_before: 1
  requires_following: 'bahwa|dalam|berdasarkan|pada|meliputi'
  # Hanya split "a. bahwa..." bukan "e.g.", "a. b.", dll.
```

> **Perhatian — engine menambahkan `\s+` di depan setiap pola `structure_split` secara otomatis.**
> Ini berarti pola `Pasal\s+\d+` sebenarnya dicocokkan sebagai `\s+(Pasal\s+\d+)`.
> Konsekuensinya: jika ada dua pola di mana pola A adalah suffix dari pola B
> (contoh: `Pasal \d+` dan `Penjelasan Pasal \d+`), pola A akan ikut memotong
> spasi di dalam pola B. Solusi: gunakan negative lookbehind pada pola A.
> ```yaml
> # Cegah split "Pasal N" di dalam "Penjelasan Pasal N"
> pattern: '(?<!Penjelasan )Pasal\s+\d+[A-Z]?'
> ```

---

## Urutan Rule yang Direkomendasikan

```
1. noise_removal (hapus semua noise terlebih dahulu)
2. whitespace_normalize (WAJIB sebelum structure_split)
3. structure_split untuk bagian besar (BAB, Pasal, Bagian Romawi)
4. structure_split untuk sub-elemen (ayat, poin angka, poin huruf)
5. structure_split untuk kata kunci struktural (Menimbang, Mengingat, dll.)
```

---

## Markdown Headings (Opsional)

Field `markdown_headings` memungkinkan output `--format md` memberi heading Markdown pada baris-baris tertentu. Jika tidak diisi, `--format md` tetap menghasilkan `.md` tapi tanpa heading markup.

```yaml
markdown_headings:
  - pattern: 'BAB\s+[IVXLCDM]+'   # Python regex, dicocokkan dari awal baris (re.match)
    level: 2                        # Level heading: 1–6 (# sampai ######)
  - pattern: 'Pasal\s+\d+'
    level: 3
  - pattern: 'PENJELASAN'
    level: 2
    flags: []                       # Opsional: IGNORECASE, MULTILINE, dll.
```

**Cara kerja:** Setelah semua rules selesai dan baris kosong dihapus, setiap baris yang cocok dengan salah satu pola akan diberi prefix `##` / `###` / dst. Pencocokan menggunakan `re.match` (dari awal baris, tidak harus seluruh baris) sehingga pola `BAB\s+[IVX]+` cocok dengan baris `BAB I KETENTUAN UMUM`.

**Level yang direkomendasikan:**
- Level 2 (`##`) — BAB, PENJELASAN
- Level 3 (`###`) — Pasal
- Level 4 (`####`) — Penjelasan Pasal (khusus konsolidasi)
- Level 2 (`##`) — Bagian Romawi (I., II.) untuk SEOJK

---

## Contoh: Membuat Profile untuk PBI (Bank Indonesia)

PBI (Peraturan Bank Indonesia) memiliki struktur serupa POJK dengan beberapa perbedaan:
- Penerbit: "GUBERNUR BANK INDONESIA" (bukan "DEWAN KOMISIONER OJK")
- Footer: URL `peraturan.bi.go.id` (bukan `jdih.ojk.go.id`)
- Nomor: "PERATURAN BANK INDONESIA NOMOR ..."

Langkah-langkah:

### 1. Salin template

```bash
cp regulasi_id_corpus_prep/profiles/_template.yaml regulasi_id_corpus_prep/profiles/bi-pbi.yaml
```

### 2. Isi metadata

```yaml
metadata:
  name: bi-pbi
  description: "PBI (Peraturan Bank Indonesia) dari situs resmi Bank Indonesia"
  version: "1.0.0"
  document_types:
    - PBI
```

### 3. Periksa noise di file `.raw.txt`

Jalankan `extract` pada beberapa PDF PBI, lalu buka `.raw.txt` dan cari pola noise yang muncul berulang. Contoh yang mungkin ditemukan:

```
https://peraturan.bi.go.id/
- 5 -
BANK INDONESIA
```

Tambahkan sebagai `noise_removal` rules.

### 4. Identifikasi elemen struktural

Buka `.raw.txt` dan cari pola yang menandai awal bagian dokumen:
- `BAB I`, `BAB II`, dll.
- `Pasal 1`, `Pasal 2`, dll.
- `GUBERNUR BANK INDONESIA,`

Tambahkan sebagai `structure_split` rules.

### 5. Tambah markdown_headings (opsional)

```yaml
markdown_headings:
  - pattern: 'BAB\s+[IVXLCDM]+'
    level: 2
  - pattern: 'Pasal\s+\d+'
    level: 3
```

### 6. Isi bagian `validation`

```yaml
validation:
  title_keywords:
    - "PERATURAN BANK INDONESIA"
    - "PBI"
  content_marker_pattern: 'Pasal\s+\d+'
  content_marker_label: "Pasal"
  noise_check_patterns:
    - 'peraturan\.bi\.go\.id'
    - '-\s*\d+\s*-'
```

### 7. Uji profile

```bash
regulasi-id-corpus-prep run contoh.pdf --profile bi-pbi --output-dir /tmp/test/
regulasi-id-corpus-prep validate /tmp/test/contoh.txt --profile bi-pbi

# Uji output Markdown
regulasi-id-corpus-prep run contoh.pdf --profile bi-pbi --format md --output-dir /tmp/test/
```

Bandingkan output manual dengan PDF asli menggunakan [docs/VALIDATION_GUIDE.md](VALIDATION_GUIDE.md).

### 8. Kontribusi

Jika profile Anda bekerja dengan baik, kontribusikan melalui Pull Request ke repositori utama!

---

## Schema Lengkap Profile (Referensi Cepat)

```yaml
metadata:
  name: string                    # Unik, digunakan dengan --profile
  description: string             # Satu baris
  version: string                 # Semver, misal "1.0.0"
  document_types: list[string]    # Informatif, misal [POJK, SEOJK]

rules:
  - name: string                  # Unik dalam profile
    type: noise_removal | whitespace_normalize | structure_split
    # noise_removal:
    pattern: string               # Python regex
    replacement: string           # Default: " "
    flags: list[string]           # Opsional: IGNORECASE, MULTILINE, DOTALL
    # whitespace_normalize: tidak ada field tambahan
    # structure_split:
    pattern: string               # Python regex (engine menambahkan \s+ di depan otomatis)
    newlines_before: int          # 1–4, default: 2
    space_after: bool             # Default: false
    requires_following: string    # Opsional: pola yang harus mengikuti
    flags: list[string]           # Opsional

markdown_headings:                # Opsional — untuk output --format md
  - pattern: string               # Python regex, dicocokkan dari awal baris (re.match)
    level: int                    # 1–6 (# sampai ######)
    flags: list[string]           # Opsional

validation:
  title_keywords: list[string]    # Kata kunci yang harus ada di baris pertama
  content_marker_pattern: string  # Regex untuk menghitung elemen struktural
  content_marker_label: string    # Label manusiawi (misal: "Pasal", "Bagian")
  noise_check_patterns: list[string]  # Pola yang tidak boleh ada di output
```
