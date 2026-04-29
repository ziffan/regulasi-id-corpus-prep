# Changelog

Semua perubahan penting pada proyek ini didokumentasikan di sini.
Format mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
dan proyek ini mengikuti [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-29

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
