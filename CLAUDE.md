# CLAUDE.md — regulasi-id-corpus-prep

Panduan untuk coding agent yang bekerja di repositori ini.

## Ringkasan Proyek

CLI dua-tahap (`extract` → `normalize`) untuk konversi PDF regulasi OJK (POJK/SEOJK) ke teks corpus bersih. Companion tool untuk [LexHarmoni](https://github.com/ziffan/lexharmoni).

## Struktur Utama

```
regulasi_id_corpus_prep/
  cli.py          # Click entry point, semua subcommands
  extract.py      # PyMuPDF → .raw.txt + .raw.meta.json
  normalize.py    # profile rules → .txt + .meta.json
  validate.py     # 5 sanity checks, exit code 0/1/2
  profile.py      # Pydantic v2 schema + YAML loader
  profiles/       # Built-in profiles (ojk-pojk, ojk-seojk, _template)
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

## Aturan Penting

### Jangan Lakukan

- **Jangan ubah golden files** di `examples/sample-output/` secara manual. Jika perlu update (karena perubahan profile yang disengaja), generate ulang dengan `run` lalu commit hasilnya.
- **Jangan collapse pipeline** menjadi satu command. Pemisahan `extract` → `normalize` adalah keputusan arsitektur yang non-negotiable (lihat `DECISIONS.md` ADR-001).
- **Jangan tambah profile non-OJK** di v0.1.0. Arsitektur sudah siap; profile-nya belum.
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

## Round-Trip Test (DoD item 3)

Reference PDFs ada di `D:\HackathonOpus4.7\pdf-aturan\`. Untuk verifikasi setelah mengubah profile:

```python
# Lihat tests/test_integration.py untuk pola yang benar
# Target: ≥99% character-level match (whitespace-collapsed) terhadap reference .txt
# POJK profiles: 100.00% match saat ini
# SEOJK profiles: 99.97% (2-char diff = artefak 'r ' dihapus, ini perbaikan)
```

## Dependensi Kritis

- **PyMuPDF (AGPL)**: library ekstraksi PDF. Harus selalu disebut di NOTICE jika distribusi tool berubah. Fallback ke `pypdf` (BSD) direncanakan di v0.2.0.
- **Pydantic v2**: bukan v1. API berbeda signifikan.

## Status v0.1.0

- 40/40 tests pass
- POJK/SEOJK profiles diverifikasi terhadap 4 PDF LexHarmoni corpus
- Fresh install dari GitHub berfungsi
- PyPI publish direncanakan setelah review pengguna non-teknis
