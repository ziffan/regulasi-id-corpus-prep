# CLAUDE.md — regulasi-id-corpus-prep

Panduan untuk coding agent yang bekerja di repositori ini.

## Ringkasan Proyek

CLI dua-tahap (`extract` → `normalize`) untuk konversi PDF regulasi Indonesia ke teks corpus bersih. Companion tool untuk [LexHarmoni](https://github.com/ziffan/lexharmoni).

## Struktur Utama

```
regulasi_id_corpus_prep/
  cli.py          # Click entry point, semua subcommands
  extract.py      # PyMuPDF → .raw.txt + .raw.meta.json
  normalize.py    # profile rules → .txt + .meta.json
  validate.py     # 5 sanity checks, exit code 0/1/2
  profile.py      # Pydantic v2 schema + YAML loader
  profiles/       # Built-in profiles
    ojk-pojk.yaml, ojk-seojk.yaml
    ri-pp.yaml, ri-uu.yaml
    uu-konsolidasi.yaml
    _template.yaml
tests/
  conftest.py     # Fixtures: sample PDF path, empty PDF generator
  fixtures/profiles/  # Test profiles (terisolasi dari production)
examples/
  sample-input/   # SEOJK-19-2023.pdf (fixture untuk regression test)
  sample-output/  # Golden files — jangan diedit manual, generate ulang jika perlu
```

## Perintah Penting

```bash
# Install dalam mode development
pip install -e ".[dev]"

# Jalankan semua test
python -m pytest tests/ -v

# Jalankan pipeline pada sample
regulasi-id-corpus-prep run examples/sample-input/SEOJK-19-2023.pdf \
  --profile ojk-seojk --output-dir /tmp/test-out/

# Lihat profile tersedia
regulasi-id-corpus-prep list-profiles
```

## Status v0.2.0 — SELESAI (2026-05-01)

### Profile RI

- **`ri-pp`**: Peraturan Pemerintah RI (peraturan.go.id, hukumonline.com) ✓
- **`ri-uu`**: Undang-Undang RI (peraturan.go.id, hukumonline.com SALINAN) ✓  
  Referensi PDF: `examples/sample-input/UU_NO_1_2026.pdf`, `uu-no-1-tahun-2026.pdf`
- **`uu-konsolidasi`**: UU Konsolidasi hukumonline (teks terintegrasi + perubahan + anotasi Putusan MK) ✓  
  Referensi PDF: `examples/sample-input/UU_NO_1_2023_KNS.pdf`, `UU_NO_13_2003_REV-JAN26_KNSUM.pdf`

### Fitur Markdown output (`--format md`) ✓

Flag `--format [txt|md]` di `normalize` dan `run` (default: `txt`). Saat `md` dipilih:
- Output: `.md` + `.meta.json`, field `output_format` dicatat di meta
- `profile.py`: model `MarkdownHeading` baru (`pattern`, `level` 1–6, `flags`); field `markdown_headings` di `Profile` (default kosong — backward compatible)
- `normalize.py`: `_apply_markdown_headings()` dijalankan per-baris setelah semua rules selesai dan empty lines dihapus; menggunakan `re.match` (bukan fullmatch) agar pola partial-line seperti `BAB\s+[IVX]+` cocok dengan `BAB I KETENTUAN UMUM`
- Semua 5 profile sudah punya `markdown_headings`: BAB→`##`, Pasal→`###`, Penjelasan Pasal (uu-konsolidasi)→`####`, bagian Romawi SEOJK→`##`, PENJELASAN (ri-pp/ri-uu)→`##`

### Totals v0.2.0

- 105/105 tests pass

## Aturan Penting

### Jangan Lakukan

- **Jangan ubah golden files** di `examples/sample-output/` secara manual. Jika perlu update (karena perubahan profile yang disengaja), generate ulang dengan `run` lalu commit hasilnya.
- **Jangan collapse pipeline** menjadi satu command. Pemisahan `extract` → `normalize` adalah keputusan arsitektur yang non-negotiable (lihat `DECISIONS.md` ADR-001).
- **Jangan tambah OCR, scraping JDIH, atau network calls** dalam bentuk apapun.

### Harus Dilakukan

- Semua transformasi wajib tercatat di `.meta.json` — tidak ada transformasi diam-diam.
- Error messages harus dapat dibaca oleh non-engineer. Gunakan `rich`, jangan biarkan Python traceback muncul ke user.
- Setiap file Python baru harus punya header `# SPDX-License-Identifier: Apache-2.0`.
- Setelah mengubah profile YAML, jalankan round-trip test terhadap reference PDFs (lihat section bawah).

## Profile System

Tiga tipe rule: `noise_removal`, `whitespace_normalize`, `structure_split`. Urutan eksekusi penting: selalu normalisasi whitespace sebelum structure_split.

Untuk menambah profile baru: copy `regulasi_id_corpus_prep/profiles/_template.yaml`, isi, lalu jalankan `regulasi-id-corpus-prep list-profiles` untuk verifikasi.

Profile divalidasi via Pydantic v2 saat load. Jika ada rule dengan `type` tidak dikenal, akan gagal dengan error yang menunjuk field bermasalah.

---

## Engine Internals — WAJIB DIBACA SEBELUM MEMBUAT PROFILE BARU

### Cara `structure_split` bekerja di `normalize.py`

Engine membangun regex dari `pattern` di YAML dengan **selalu menambahkan `\s+` di depan**:

```python
# normalize.py — logika inti structure_split
if rule.requires_following:
    pattern = r"\s+(" + rule.pattern + r")\s+(" + rule.requires_following + r")"
    replacement = prefix + r"\1 \2"
elif rule.space_after:
    pattern = r"\s+(" + rule.pattern + r")\s+"
    replacement = prefix + r"\1 "
else:
    pattern = r"\s+(" + rule.pattern + r")"
    replacement = prefix + r"\1"
```

**Konsekuensi kritis:** Prefix `\s+` mengkonsumsi whitespace *sebelum* pola. Artinya pola `Pasal\s+\d+` akan cocok dengan spasi antara `Penjelasan` dan `Pasal` dalam teks `Penjelasan Pasal 1` — dan menghasilkan split yang tidak diinginkan.

### `newlines_before` tidak menghasilkan baris kosong di output

`normalize.py` (baris 78–79) menghapus semua baris kosong setelah semua rule selesai. Sehingga `newlines_before: 4` dan `newlines_before: 2` menghasilkan output yang **identik** — hanya 1 baris baru di antara dua blok konten.

### Rules berjalan secara sekuensial

Output rule N menjadi input rule N+1. Urutan rule dalam YAML menentukan hasil. `whitespace_normalize` harus selalu diletakkan **setelah** semua `noise_removal` dan **sebelum** semua `structure_split`.

---

## Pitfalls Profil — Pelajaran dari Pengerjaan ri-uu & uu-konsolidasi

### 1. Pola split yang saling tumpang-tindih → pakai negative lookbehind

Jika pola split A adalah suffix dari pola split B (contoh: `Pasal \d+` adalah suffix dari `Penjelasan Pasal \d+`), maka rule untuk A akan memotong spasi di dalam B.

**Solusi:** Gunakan negative lookbehind fixed-width pada pola A:

```yaml
# SALAH — memotong "Penjelasan Pasal 1" menjadi dua baris
- name: split_before_pasal
  pattern: 'Pasal\s+\d+[A-Z]?'

# BENAR — lookbehind mencegah split jika didahului "Penjelasan "
- name: split_before_pasal
  pattern: '(?<!Penjelasan )Pasal\s+\d+[A-Z]?'
```

Python lookbehind harus fixed-width. `(?<!Penjelasan )` = 11 karakter (termasuk spasi trailing). Jika prefix lebih panjang atau variatif, pertimbangkan pendekatan lain (misal: ganti urutan rule, atau tambahkan `requires_following`).

### 2. `split_before_numbered_points` (`\d+\.`) memotong tahun di akhir kalimat

Pola `\d+\.` cocok dengan `1945.`, `2022.`, `2011.` di akhir kalimat. Ini adalah known limitation. Jangan menulis test yang mengassert string penuh yang mengandung `<tahun>.`:

```python
# SALAH — "1945." di-split, jadi "UUD\n1945. Catatan"
assert "bertentangan dengan UUD 1945" in content

# BENAR — pisah assertion
assert "bertentangan dengan UUD" in content
assert "1945" in content
```

### 3. Jangan assert `"\n\nKEYWORD"` — normalize.py menghapus baris kosong

Setelah normalize, tidak ada baris kosong. Untuk memverifikasi keyword muncul pada barisnya sendiri:

```python
# SALAH — normalize.py menghapus empty lines
assert "\n\n\n\nPENJELASAN" in content

# BENAR — cek line-level
lines = content.splitlines()
assert any(l == "PENJELASAN" or l.startswith("PENJELASAN ") for l in lines)
```

### 4. Substring ambigu di string assertion

Jika test mengecek absence substring, pastikan substring itu tidak valid dalam konteks lain:

```python
# SALAH — "K INDONESIA" adalah substring dari "REPUBLIK INDONESIA" yang valid
assert "K INDONESIA" not in content

# BENAR — cek pada level baris
assert not any(l.strip() == "K INDONESIA" for l in content.splitlines())
```

### 5. PyMuPDF menyatukan superscript footnote ke angka sebelumnya

Nomor catatan kaki superscript digabung langsung ke angka terakhir teks (misal: `20261` = `2026` + catatan kaki `1`, `20117` = `2011` + catatan kaki `7`). Jangan coba strip ini — biarkan apa adanya. Jika test mengassert tahun, gunakan `str(year)` saja, bukan string penuh:

```python
# Aman — "2026" tetap ada walau ada "20261"
assert "2026" in content
```

### 6. Edit tool gagal jika search string mengandung em-dash atau karakter Unicode non-ASCII

YAML profile menggunakan em-dash (`—`) di komentar. Jika Edit tool gagal dengan "String to replace not found", coba dua hal:
1. Gunakan substring yang lebih pendek dan tidak mengandung karakter khusus
2. Read ulang file terlebih dahulu untuk memastikan encoding sesuai

---

## Pola Noise per Jenis Dokumen

### peraturan.go.id — SALINAN UU/PP (kop surat bergambar)

Noise khas:
- **Garbled kop — family EIEtrN**: `iIitrEIEtrN`, `;*trEIEtrN`, `LIrtrEIEtrN`, `EEI-iEIEtrN`  
  Pattern: `[^\n]*EIEtrN[^\n]*`
- **Garbled kop — family brace**: `T{Irr;IriilTlr.I,IrEF{a` dan variannya  
  Pattern: `^\s*\w+\{[^\n]*` (MULTILINE)
- **Garbled header halaman**: `REPUEUK INDONESIA`, `K INDONESIA`  
  Pattern: `^\s*(?:[A-Z]{1,6}\s+)?INDONESIA\s*$` (MULTILINE)
- **Nomor halaman dua sisi**: `- 3 -`, `- 12 -`  
  Pattern: `\s*-\s*[lt\d]+\s*-\s*` (OCR: `t`/`l` bisa menggantikan `1`)
- **Nomor halaman satu sisi leading**: `-3`, `-12`  
  Pattern: `^\s*-\s*[lt\d]+\s*$` (MULTILINE)
- **Nomor halaman satu sisi trailing**: `3-`, `12-`  
  Pattern: `^\s*[lt\d]+\s*-\s*$` (MULTILINE)
- **SK marker**: `SK No XXXXXX A`  
  Pattern: `SK\s+No\s+\w+`
- **Continuation marker**: `. .  .`

### hukumonline.com — UU/PP reguler & konsolidasi

Noise khas:
- **Personal footer**: `ZIFFANY FIRDINAL | DIUNDUH PADA 01 MEI 2026`  
  Pattern: `[A-Z][A-Z ]{2,}\|\s*DIUNDUH PADA[^\n]*`
- **Header domain**: `www.hukumonline.com`  
  Pattern: `^\s*www\.hukumonline\.com[^\n]*$` (MULTILINE)
- **Banner laporan typo**: `Menemukan kesalahan ketik dalam dokumen? Klik di sini...`  
  Pattern: `Menemukan kesalahan ketik[^\n]*` (IGNORECASE)

---

## Keputusan Desain per Format Dokumen

### ri-pp dan ri-uu
- Section **LAMPIRAN** dihapus (isi umumnya tabel/formulir, tidak membawa makna normatif dalam teks biasa)
- Section **LEMBARAN NEGARA** dihapus
- Pasal menggunakan angka Romawi (Pasal I, II) untuk UU Omnibus; angka Arab untuk UU biasa  
  Pattern aman: `Pasal\s+(?:[IVX][IVXLCDM]*|\d+[A-Z]?)`

### uu-konsolidasi
- **LAMPIRAN dan LEMBARAN NEGARA DIPERTAHANKAN** — informasi provenance dokumen sumber
- **Penjelasan terintegrasi per Pasal** (`Penjelasan Pasal N` langsung setelah isi Pasal) — JANGAN tambah split untuk `PENJELASAN` generik karena tidak ada section PENJELASAN terpisah di akhir
- Anotasi Putusan MK dan referensi UU/PERPU pengubah di bawah Pasal harus dipertahankan
- Gunakan `(?<!Penjelasan )` lookbehind pada `split_before_pasal` untuk mencegah `Penjelasan Pasal N` terpecah

---

## Round-Trip Test (DoD item 3)

Reference PDFs ada di `D:\HackathonOpus4.7\pdf-aturan\`. Untuk verifikasi setelah mengubah profile:

```python
# Lihat tests/test_integration.py untuk pola yang benar
# Target: ≥99% character-level match (whitespace-collapsed) terhadap reference .txt
# Baseline saat ini (SequenceMatcher ratio, 2026-04-29):
#   POJK 22-2023: 100.00%
#   POJK 40-2024: 100.00%
#   SEOJK 19-2025: 100.00%
#   POJK 10-2022: 100.00%
```

## Dependensi Kritis

- **PyMuPDF (AGPL)**: library ekstraksi PDF. Harus selalu disebut di NOTICE jika distribusi tool berubah. Fallback ke `pypdf` (BSD) direncanakan di versi mendatang.
- **Pydantic v2**: bukan v1. API berbeda signifikan.

## Status Terkini — v0.2.0 SELESAI (2026-05-01)

- 105/105 tests pass
- 5 built-in profiles: `ojk-pojk`, `ojk-seojk`, `ri-pp`, `ri-uu`, `uu-konsolidasi`
- `--format md` tersedia di `normalize` dan `run`
- POJK/SEOJK diverifikasi 100.00% terhadap 4 PDF LexHarmoni corpus
- PyPI: `pip install regulasi-id-corpus-prep` (latest release: v0.1.0; v0.2.0 belum di-tag)
