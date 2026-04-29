# Catatan Keputusan Arsitektur

Dokumen ini mencatat keputusan desain kunci beserta alasannya, untuk membantu pemelihara masa depan memahami *mengapa* sesuatu dibuat seperti ini.

---

## ADR-001: Pipeline dua tahap `extract → normalize`

**Keputusan:** Pisahkan ekstraksi PDF dan normalisasi teks menjadi dua subcommand dan dua set output file (`.raw.txt` + `.txt`).

**Alasan:** Jika normalisasi gagal atau menghasilkan output yang buruk, pengguna dapat memeriksa `.raw.txt` untuk memverifikasi apakah masalahnya ada di level ekstraksi atau di level aturan profile. Tanpa pemisahan ini, debugging memerlukan re-run penuh. Selain itu, `.raw.txt` dapat di-inspeksi secara manual untuk menulis aturan profile baru tanpa perlu mengulang ekstraksi.

**Konsekuensi:** Lebih banyak file intermediate di folder output. Diterima — pengguna dapat membersihkannya manual, atau perintah `run` menyembunyikan kompleksitas ini.

---

## ADR-002: Aturan normalisasi dalam YAML profile, bukan hardcoded

**Keputusan:** Semua aturan regex didefinisikan dalam file `.yaml` di direktori `profiles/`, bukan hardcoded dalam Python.

**Alasan:** Memungkinkan penambahan dukungan jenis dokumen baru (PBI, Permenkeu, Permenkominfo) tanpa mengubah kode inti. Kontributor non-programmer dapat berkontribusi profile baru melalui PR. Aturan dalam YAML lebih mudah di-review daripada regex tersebar dalam kode Python.

**Konsekuensi:** Sedikit overhead loading YAML + validasi Pydantic saat startup (~50ms). Dapat diabaikan untuk CLI yang berjalan sekali per invokasi.

---

## ADR-003: Profile di dalam package Python (`regulasi_id_corpus_prep/profiles/`)

**Keputusan:** File YAML profile disimpan di dalam direktori package (`regulasi_id_corpus_prep/profiles/`) dan disertakan sebagai `package_data`, bukan di root repo.

**Alasan:** Saat pengguna menginstal via `pip install`, hanya file di dalam package yang disertakan dalam distribusi. Profile di root repo tidak akan tersedia setelah instalasi. Menempatkan profile di dalam package memastikan mereka selalu dapat ditemukan via `Path(__file__).parent / "profiles"`.

**Konsekuensi:** Deviasi dari layout spec awal yang menunjukkan `profiles/` di root. Profile kustom tetap dapat digunakan via flag `--profiles-dir`. Pengembang yang meng-clone repo tetap melihat profile di lokasi yang intuitif (bagian dari package source).

---

## ADR-004: PyMuPDF sebagai library ekstraksi primer

**Keputusan:** Gunakan `PyMuPDF` (fitz) sebagai satu-satunya library ekstraksi PDF di v0.1.0.

**Alasan:** LexHarmoni (proyek hilir) telah memvalidasi output ekstraksi PyMuPDF pada corpus POJK/SEOJK yang sama. Menggunakan library yang sama memastikan konsistensi karakter-level antara output tool ini dan corpus yang sudah ada di LexHarmoni.

**Risiko diketahui:** PyMuPDF adalah AGPL. Didokumentasikan di NOTICE. Jika AGPL menimbulkan masalah lisensi bagi pengguna tertentu, `pypdf` (BSD) adalah alternatif yang terdokumentasi — diimplementasikan di v0.2.0+.

---

## ADR-005: Validasi Pydantic v2 untuk schema profile

**Keputusan:** Gunakan Pydantic v2 dengan discriminated union pada field `type` untuk validasi schema profile.

**Alasan:** Tangkap profile yang salah format saat load time dengan pesan error yang menunjuk field spesifik, bukan saat runtime ketika regex gagal dengan pesan yang membingungkan. Pydantic v2 lebih cepat dan memiliki error message yang lebih baik dari v1.

**Catatan:** Pydantic melaporkan error berdasarkan path field Python, bukan nomor baris YAML. Mendapatkan nomor baris YAML yang tepat memerlukan `ruamel.yaml` dengan position tracking — ditangguhkan ke v0.2.0+.

---

## ADR-006: Exit code validate subcommand (0/1/2)

**Keputusan:** `validate` mengembalikan exit code 0 (semua lulus), 1 (ada peringatan), 2 (kegagalan kritis).

**Alasan:** Memungkinkan integrasi dalam shell script dan CI. Exit code 2 hanya untuk kondisi yang benar-benar mengindikasikan output tidak dapat digunakan (tidak ada Pasal terdeteksi, encoding rusak). Peringatan (exit 1) membutuhkan inspeksi manual tapi tidak berarti output tidak bisa dipakai.
