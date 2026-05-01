# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from pathlib import Path

import pytest

from regulasi_id_corpus_prep.normalize import normalize
from regulasi_id_corpus_prep.profile import load_profile


RAW_POJK = (
    "SALINAN PERATURAN OTORITAS JASA KEUANGAN REPUBLIK INDONESIA NOMOR 99 TAHUN 2099 "
    "TENTANG SESUATU https://jdih.ojk.go.id/ DENGAN RAHMAT TUHAN YANG MAHA ESA "
    "DEWAN KOMISIONER OTORITAS JASA KEUANGAN, Menimbang: Bahwa hal ini penting. "
    "Mengingat: 1. Undang-Undang Nomor 1 Tahun 2000. MEMUTUSKAN: Menetapkan: PERATURAN INI. "
    "BAB I KETENTUAN UMUM Pasal 1 (1) Definisi pertama adalah ini. "
    "(2) Definisi kedua adalah itu. a. bahwa hal ini benar. Pasal 2 Ketentuan lain. "
    "- 3 - BAB II PENUTUP Pasal 3 Peraturan ini berlaku."
)


@pytest.fixture
def pojk_profile():
    return load_profile("ojk-pojk")


@pytest.fixture
def raw_pojk_file(tmp_path: Path) -> Path:
    p = tmp_path / "test.raw.txt"
    p.write_text(RAW_POJK, encoding="utf-8")
    return p


def test_noise_removal_jdih_link(tmp_path: Path, pojk_profile) -> None:
    p = tmp_path / "noise.raw.txt"
    p.write_text("teks https://jdih.ojk.go.id/ lanjut", encoding="utf-8")
    txt, _ = normalize(p, pojk_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "jdih.ojk.go.id" not in content


def test_noise_removal_page_numbers(tmp_path: Path, pojk_profile) -> None:
    p = tmp_path / "pagenum.raw.txt"
    p.write_text("akhir kalimat - 12 - awal kalimat baru", encoding="utf-8")
    txt, _ = normalize(p, pojk_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "- 12 -" not in content


def test_whitespace_normalize_collapses_spaces(tmp_path: Path, pojk_profile) -> None:
    p = tmp_path / "ws.raw.txt"
    p.write_text("kata   banyak\n\n\nspasi\t\ttab", encoding="utf-8")
    txt, _ = normalize(p, pojk_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "   " not in content
    assert "\t" not in content


def test_structure_split_bab(tmp_path: Path, pojk_profile) -> None:
    p = tmp_path / "bab.raw.txt"
    p.write_text("teks awal BAB I KETENTUAN Pasal 1 isi", encoding="utf-8")
    txt, _ = normalize(p, pojk_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    bab_line = next((l for l in lines if l.startswith("BAB I")), None)
    assert bab_line is not None


def test_structure_split_pasal(tmp_path: Path, pojk_profile) -> None:
    p = tmp_path / "pasal.raw.txt"
    p.write_text("teks BAB I UMUM Pasal 1 isi ayat satu Pasal 2 isi ayat dua", encoding="utf-8")
    txt, _ = normalize(p, pojk_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    pasal_lines = [l for l in lines if l.startswith("Pasal ")]
    assert len(pasal_lines) == 2


def test_structure_split_ayat(tmp_path: Path, pojk_profile) -> None:
    p = tmp_path / "ayat.raw.txt"
    p.write_text("Pasal 1 (1) Ayat pertama. (2) Ayat kedua.", encoding="utf-8")
    txt, _ = normalize(p, pojk_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    ayat_lines = [l for l in lines if l.startswith("(")]
    assert len(ayat_lines) == 2


def test_structure_split_letter_points(tmp_path: Path, pojk_profile) -> None:
    p = tmp_path / "letter.raw.txt"
    p.write_text("Pasal 1 meliputi: a. bahwa ini benar b. dalam hal lain", encoding="utf-8")
    txt, _ = normalize(p, pojk_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    letter_lines = [l for l in lines if l.startswith("a.") or l.startswith("b.")]
    assert len(letter_lines) == 2


def test_meta_json_written(raw_pojk_file: Path, tmp_path: Path, pojk_profile) -> None:
    _, meta_path = normalize(raw_pojk_file, pojk_profile, output_dir=tmp_path)
    assert meta_path.exists()

    import json
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["profile_name"] == "ojk-pojk"
    assert "rules_applied" in meta
    assert "timestamp" in meta


def test_determinism(raw_pojk_file: Path, tmp_path: Path, pojk_profile) -> None:
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    txt1, _ = normalize(raw_pojk_file, pojk_profile, output_dir=out1)
    txt2, _ = normalize(raw_pojk_file, pojk_profile, output_dir=out2)
    assert txt1.read_text(encoding="utf-8") == txt2.read_text(encoding="utf-8")


def test_output_filename_derived_from_raw_txt(raw_pojk_file: Path, tmp_path: Path, pojk_profile) -> None:
    txt, _ = normalize(raw_pojk_file, pojk_profile, output_dir=tmp_path)
    assert txt.name == "test.txt"


# ---------------------------------------------------------------------------
# ri-pp profile tests
# ---------------------------------------------------------------------------

RAW_PP_PGI = (
    "Menemukan kesalahan ketik dalam dokumen? Klik di sini untuk perbaikan.\n"
    "SALINAN    ★\n"
    "PRESIDEN\n"
    "REPUBLIK INDONESIA\n"
    "PERATURAN PEMERINTAH REPUBLIK INDONESIA NOMOR 22 TAHUN 2025 TENTANG SESUATU\n"
    "DENGAN RAHMAT TUHAN YANG MAHA ESA\n"
    "PRESIDEN REPUBLIK INDONESIA,\n"
    "Menimbang : a. bahwa hal ini penting.\n"
    "ZIFFANY FIRDINAL | DIUNDUH PADA 01 MEI 2026\n"
    "SK No 255843 A\n"
    "PRESIDEN\n"
    "REPUBLIK INDONESIA\n"
    "- 2 -\n"
    "Mengingat : 1. Pasal 5 ayat (2) UUD 1945.\n"
    "MEMUTUSKAN :\n"
    "Menetapkan : PERATURAN PEMERINTAH TENTANG SESUATU.\n"
    "BAB I KETENTUAN UMUM\n"
    "Pasal 1 (1) Definisi. (2) Definisi kedua.\n"
    "Pasal 2 Aturan lain berlaku."
)

RAW_PP_HO = (
    "l\n"
    "SALINAN\n"
    "FNESIDEN\n"
    "REPUEUK INDONESIA\n"
    "PERATURAN PEMERINTAH REPUBLIK INDONESIA NOMOR 22 TAHUN 2025 TENTANG SESUATU\n"
    "DENGAN RAHMAT TUHAN YANG MAHA ESA\n"
    "PRESIDEN REPUBLIK INDONESIA,\n"
    "Menimbang : a. bahwa hal ini penting. . . .\n"
    "SK No255&43A\n"
    "FNESIDEN\n"
    "REPUEUK INDONESIA\n"
    "-2-\n"
    "Menimbang : a. bahwa hal ini penting.\n"
    "Mengingat : 1. Pasal 5 ayat (2) UUD 1945.\n"
    "MEMUTUSKAN:\n"
    "Menetapkan : PERATURAN PEMERINTAH TENTANG SESUATU.\n"
    "BAB I KETENTUAN UMUM\n"
    "Pasal 1 (1) Definisi. (2) Definisi kedua.\n"
    "Pasal 2 Aturan lain berlaku.\n"
    "PENJELASAN\n"
    "I. UMUM\n"
    "LAMPIRAN I\n"
    "Tabel lampiran yang dikecualikan.\n"
    "TAMBAHAN LEMBARAN NEGARA REPUBLIK INDONESIA NOMOR 7094\n"
)


@pytest.fixture
def ripp_profile():
    return load_profile("ri-pp")


@pytest.fixture
def raw_pp_pgi_file(tmp_path: Path) -> Path:
    p = tmp_path / "pp_pgi.raw.txt"
    p.write_text(RAW_PP_PGI, encoding="utf-8")
    return p


@pytest.fixture
def raw_pp_ho_file(tmp_path: Path) -> Path:
    p = tmp_path / "pp_ho.raw.txt"
    p.write_text(RAW_PP_HO, encoding="utf-8")
    return p


def test_ri_pp_removes_personal_footer(tmp_path: Path, raw_pp_pgi_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "DIUNDUH PADA" not in content


def test_ri_pp_removes_menemukan_kesalahan(tmp_path: Path, raw_pp_pgi_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "Menemukan kesalahan ketik" not in content


def test_ri_pp_removes_sk_markers_pgi(tmp_path: Path, raw_pp_pgi_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "SK No" not in content


def test_ri_pp_removes_sk_markers_ho(tmp_path: Path, raw_pp_ho_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_ho_file, ripp_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "SK No" not in content


def test_ri_pp_removes_salinan(tmp_path: Path, raw_pp_pgi_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "SALINAN" not in content


def test_ri_pp_removes_page_numbers(tmp_path: Path, raw_pp_pgi_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "- 2 -" not in content


def test_ri_pp_removes_page_header_garbled_ho(tmp_path: Path, raw_pp_ho_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_ho_file, ripp_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "FNESIDEN" not in content
    assert "REPUEUK" not in content


def test_ri_pp_removes_lampiran(tmp_path: Path, raw_pp_ho_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_ho_file, ripp_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "Tabel lampiran" not in content
    assert "LAMPIRAN" not in content


def test_ri_pp_removes_tambahan_lembaran_negara(tmp_path: Path, raw_pp_ho_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_ho_file, ripp_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "TAMBAHAN LEMBARAN NEGARA" not in content


def test_ri_pp_split_bab(tmp_path: Path, raw_pp_pgi_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    assert any(l.startswith("BAB I") for l in lines)


def test_ri_pp_split_pasal(tmp_path: Path, raw_pp_pgi_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    pasal_lines = [l for l in lines if l.startswith("Pasal ")]
    assert len(pasal_lines) >= 2


def test_ri_pp_split_ayat(tmp_path: Path, raw_pp_pgi_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    ayat_lines = [l for l in lines if l.startswith("(")]
    assert len(ayat_lines) >= 1


def test_ri_pp_penjelasan_separated(tmp_path: Path, raw_pp_ho_file: Path, ripp_profile) -> None:
    txt, _ = normalize(raw_pp_ho_file, ripp_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    assert any(l == "PENJELASAN" or l.startswith("PENJELASAN ") for l in lines)


def test_ri_pp_meta_json_written(raw_pp_pgi_file: Path, tmp_path: Path, ripp_profile) -> None:
    import json
    _, meta_path = normalize(raw_pp_pgi_file, ripp_profile, output_dir=tmp_path)
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["profile_name"] == "ri-pp"
    assert "rules_applied" in meta


def test_ri_pp_determinism(raw_pp_pgi_file: Path, tmp_path: Path, ripp_profile) -> None:
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    txt1, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=out1)
    txt2, _ = normalize(raw_pp_pgi_file, ripp_profile, output_dir=out2)
    assert txt1.read_text(encoding="utf-8") == txt2.read_text(encoding="utf-8")
