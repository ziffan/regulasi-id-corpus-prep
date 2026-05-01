# Changelog

Semua perubahan penting pada proyek ini didokumentasikan di sini.
Format mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
dan proyek ini mengikuti [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-01

### Added
- Profile `ri-pp` (PP Peraturan Pemerintah RI) — sumber PDF peraturan.go.id;
  noise removal: SK marker, kop garbled, nomor halaman, continuation marker, LAMPIRAN, LEMBARAN NEGARA.
- Profile `ri-uu` (UU Undang-Undang RI) — sumber PDF peraturan.go.id (SALINAN);
  nomor halaman satu-sisi, kop PRESIDEN/REPUBLIK INDONESIA garbled, Pasal Romawi dan Arab.
- Flag `--format [txt|md]` pada subcommand `normalize` dan `run` (default: `txt`).
  Saat `--format md` dipilih, output ditulis ke `.md` dengan heading Markdown sesuai profil.
- Field `markdown_headings` (opsional) pada schema Profile: list `{pattern, level, flags}`
  yang memetakan pola baris ke heading Markdown (`##`, `###`, dst).
  Semua 5 profile bawaan sudah dilengkapi `markdown_headings`.
- Field `output_format` di `.meta.json` mencatat format yang dipakai (`txt` atau `md`).

### Notes
- Profile RI (ri-pp, ri-uu) menghapus LAMPIRAN dan LEMBARAN NEGARA secara otomatis.
- 79/79 tests pass (naik dari 40 di v0.1.0).

## [0.1.0] - 2026-04-29 — PyPI: `pip install regulasi-id-corpus-prep`

### Added
- Subcommand `extract`: ekstrak teks dari PDF born-digital ke `.raw.txt` + `.raw.meta.json` via PyMuPDF (`sort=True`).
- Subcommand `normalize`: terapkan profile YAML ke `.raw.txt`, hasilkan `.txt` + `.meta.json` dengan audit trail transformasi.
- Subcommand `validate`: 5 pemeriksaan otomatis (judul, penanda konten, panjang baris, noise residual, encoding) dengan output rich-formatted dan exit code 0/1/2.
- Subcommand `run`: pipeline penuh `extract → normalize → validate` dalam satu perintah.
- Subcommand `list-profiles`: tampilkan semua profile yang tersedia.
- Profile `ojk-pojk` (POJK dari JDIH OJK) — port dari `convert_pdf_to_txt.py`.
- Profile `ojk-seojk` (SEOJK dari JDIH OJK) — dengan penanganan bagian bernomor Romawi dan artefak header.
- Template profile `_template.yaml` dengan anotasi lengkap.
- Validasi schema profile via Pydantic v2 dengan pesan error yang menunjuk field bermasalah.
- Deteksi PDF scan (tanpa text layer) dengan pesan error yang ramah pengguna non-teknis.
- Semua transformasi dicatat ke `.meta.json` (tidak ada transformasi diam).
- Dokumentasi: `docs/DECISION_TREE.md`, `docs/VALIDATION_GUIDE.md`, `docs/PROFILE_GUIDE.md`.
- Sample input/output di `examples/` untuk regression testing.
- Apache 2.0 license + NOTICE untuk PyMuPDF (AGPL).

### Notes
- Round-trip match 100.00% (SequenceMatcher) terhadap 4 PDF corpus LexHarmoni: POJK 22-2023, POJK 40-2024, SEOJK 19-2025, POJK 10-2022.
- Stage 0 corpus preparation didokumentasikan di LexHarmoni `docs/REPLICATION_GUIDEv1.md`.
