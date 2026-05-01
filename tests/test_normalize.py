# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

import re
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


# ---------------------------------------------------------------------------
# ri-uu profile tests
# ---------------------------------------------------------------------------

RAW_UU_PGI = (
    "Menemukan kesalahan ketik dalam dokumen? Klik di sini untuk perbaikan.\n"
    "SALINAN    ★\n"
    "PRESIDEN\n"
    "REPUBUK INDONESIA\n"
    "UNDANG-UNDANG REPUBLIK INDONESIA NOMOR 1 TAHUN 2026 TENTANG PENYESUAIAN PIDANA\n"
    "DENGAN RAHMAT TUHAN YANG MAHA ESA\n"
    "PRESIDEN REPUBLIK INDONESIA,\n"
    "Menimbang : a. bahwa hal ini penting.\n"
    "ZIFFANY FIRDINAL | DIUNDUH PADA 01 MEI 2026                                1/47\n"
    "SK No 273836 A\n"
    "PRESIDEN\n"
    "REPUBLIK INDONESIA\n"
    "- 2 -\n"
    "Mengingat : 1. Pasal 5 ayat (1) UUD 1945.\n"
    "Dengan Persetujuan Bersama\n"
    "DEWAN PERWAKILAN RAKYAT REPUBLIK INDONESIA\n"
    "dan\n"
    "PRESIDEN REPUBLIK INDONESIA\n"
    "MEMUTUSKAN:\n"
    "Menetapkan : UNDANG-UNDANG TENTANG PENYESUAIAN PIDANA.\n"
    "BAB I KETENTUAN UMUM\n"
    "Pasal I (1) Definisi pertama. (2) Definisi kedua.\n"
    "Pasal II Aturan lain berlaku.\n"
    "PENJELASAN ATAS\n"
    "UNDANG-UNDANG NOMOR 1 TAHUN 2026\n"
    "LEMBARAN NEGARA REPUBLIK INDONESIA TAHUN 2026 NOMOR 1\n"
)

RAW_UU_HO = (
    "T{Irr;IriilTlr.I,IrEF{a\n"
    "UNDANG-UNDANG REPUBLIK INDONESIA NOMOR 1 TAHUN 2026 TENTANG PENYESUAIAN PIDANA\n"
    "DENGAN RAHMATTUHAN YANG MAHA ESA\n"
    "PRESIDEN REPUBLIK INDONESIA,\n"
    "Menimbang : a. bahwa hal ini penting. . . .\n"
    "SK No273836A\n"
    "iIitrEIEtrN\n"
    "REPUEUK INDONESIA\n"
    "-3-\n"
    "Mengingat : 1. Pasal 5 ayat (1) UUD 1945.\n"
    "Dengan Persetujuan Bersama\n"
    "DEWAN PERWAKILAN RAKYAT REPUBLIK INDONESIA\n"
    "dan\n"
    "PRESIDEN REPUBLIK INDONESIA\n"
    "MEMUTUSKAN:\n"
    "Menetapkan : UNDANG-UNDANG TENTANG PENYESUAIAN PIDANA.\n"
    "SK No273837A\n"
    "K INDONESIA\n"
    "4-\n"
    "BAB I KETENTUAN UMUM\n"
    "Pasal I (1) Definisi pertama. (l) OCR error. (2) Definisi kedua.\n"
    "Pasal II Aturan lain berlaku.\n"
    "PENJELASAN ATAS\n"
    "UNDANG-UNDANG NOMOR 1 TAHUN 2026\n"
    "TAMBAHAN LEMBARAN NEGARA REPUBLIK INDONESIA NOMOR 7153\n"
    "LAMPIRAN I\n"
    "Tabel lampiran yang dikecualikan.\n"
)


@pytest.fixture
def riuu_profile():
    return load_profile("ri-uu")


@pytest.fixture
def raw_uu_pgi_file(tmp_path: Path) -> Path:
    p = tmp_path / "uu_pgi.raw.txt"
    p.write_text(RAW_UU_PGI, encoding="utf-8")
    return p


@pytest.fixture
def raw_uu_ho_file(tmp_path: Path) -> Path:
    p = tmp_path / "uu_ho.raw.txt"
    p.write_text(RAW_UU_HO, encoding="utf-8")
    return p


def test_ri_uu_removes_menemukan_kesalahan(tmp_path: Path, raw_uu_pgi_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    assert "Menemukan kesalahan ketik" not in txt.read_text(encoding="utf-8")


def test_ri_uu_removes_personal_footer(tmp_path: Path, raw_uu_pgi_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    assert "DIUNDUH PADA" not in txt.read_text(encoding="utf-8")


def test_ri_uu_removes_sk_markers_pgi(tmp_path: Path, raw_uu_pgi_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    assert "SK No" not in txt.read_text(encoding="utf-8")


def test_ri_uu_removes_sk_markers_ho(tmp_path: Path, raw_uu_ho_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_ho_file, riuu_profile, output_dir=tmp_path)
    assert "SK No" not in txt.read_text(encoding="utf-8")


def test_ri_uu_removes_salinan(tmp_path: Path, raw_uu_pgi_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    assert "SALINAN" not in txt.read_text(encoding="utf-8")


def test_ri_uu_removes_page_numbers_standard(tmp_path: Path, raw_uu_pgi_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    assert "- 2 -" not in txt.read_text(encoding="utf-8")


def test_ri_uu_removes_page_numbers_one_dash(tmp_path: Path, raw_uu_ho_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_ho_file, riuu_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "-3-" not in content
    lines = content.splitlines()
    assert not any(l.strip() in ("4-", "-2") for l in lines)


def test_ri_uu_removes_garbled_kop_eitrn(tmp_path: Path, raw_uu_ho_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_ho_file, riuu_profile, output_dir=tmp_path)
    assert "EIEtrN" not in txt.read_text(encoding="utf-8")


def test_ri_uu_removes_garbled_kop_brace(tmp_path: Path, raw_uu_ho_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_ho_file, riuu_profile, output_dir=tmp_path)
    assert "T{Irr" not in txt.read_text(encoding="utf-8")


def test_ri_uu_removes_page_header_garbled_ho(tmp_path: Path, raw_uu_ho_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_ho_file, riuu_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "REPUEUK" not in content
    # "K INDONESIA" berdiri sendiri harus hilang (bukan substring dari "REPUBLIK INDONESIA")
    lines = content.splitlines()
    assert not any(l.strip() == "K INDONESIA" for l in lines)


def test_ri_uu_removes_lampiran(tmp_path: Path, raw_uu_ho_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_ho_file, riuu_profile, output_dir=tmp_path)
    content = txt.read_text(encoding="utf-8")
    assert "Tabel lampiran" not in content
    assert "LAMPIRAN" not in content


def test_ri_uu_removes_lembaran_negara(tmp_path: Path, raw_uu_pgi_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    assert "LEMBARAN NEGARA" not in txt.read_text(encoding="utf-8")


def test_ri_uu_split_bab(tmp_path: Path, raw_uu_pgi_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    assert any(l.startswith("BAB I") for l in lines)


def test_ri_uu_split_pasal_roman(tmp_path: Path, raw_uu_pgi_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    pasal_lines = [l for l in lines if re.match(r"Pasal [IVX]", l)]
    assert len(pasal_lines) >= 2


def test_ri_uu_split_ayat(tmp_path: Path, raw_uu_pgi_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    ayat_lines = [l for l in lines if l.startswith("(")]
    assert len(ayat_lines) >= 1


def test_ri_uu_penjelasan_separated(tmp_path: Path, raw_uu_ho_file: Path, riuu_profile) -> None:
    txt, _ = normalize(raw_uu_ho_file, riuu_profile, output_dir=tmp_path)
    lines = txt.read_text(encoding="utf-8").splitlines()
    assert any(l == "PENJELASAN" or l.startswith("PENJELASAN ") for l in lines)


def test_ri_uu_meta_json_written(raw_uu_pgi_file: Path, tmp_path: Path, riuu_profile) -> None:
    import json
    _, meta_path = normalize(raw_uu_pgi_file, riuu_profile, output_dir=tmp_path)
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["profile_name"] == "ri-uu"
    assert "rules_applied" in meta


def test_ri_uu_determinism(raw_uu_pgi_file: Path, tmp_path: Path, riuu_profile) -> None:
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    txt1, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=out1)
    txt2, _ = normalize(raw_uu_pgi_file, riuu_profile, output_dir=out2)
    assert txt1.read_text(encoding="utf-8") == txt2.read_text(encoding="utf-8")



# ---------------------------------------------------------------------------
# --format md tests
# ---------------------------------------------------------------------------

RAW_MD = (
    "PERATURAN OTORITAS JASA KEUANGAN REPUBLIK INDONESIA NOMOR 1 TAHUN 2099 "
    "BAB I KETENTUAN UMUM Pasal 1 (1) Definisi ini. Pasal 2 Ketentuan lain. "
    "BAB II PENUTUP Pasal 3 Peraturan berlaku."
)


@pytest.fixture
def raw_md_file(tmp_path: Path) -> Path:
    p = tmp_path / "md_test.raw.txt"
    p.write_text(RAW_MD, encoding="utf-8")
    return p


def test_md_format_produces_md_extension(tmp_path: Path, pojk_profile, raw_md_file: Path) -> None:
    out, _ = normalize(raw_md_file, pojk_profile, output_dir=tmp_path, fmt="md")
    assert out.suffix == ".md"
    assert out.exists()


def test_txt_format_produces_txt_extension(tmp_path: Path, pojk_profile, raw_md_file: Path) -> None:
    out, _ = normalize(raw_md_file, pojk_profile, output_dir=tmp_path, fmt="txt")
    assert out.suffix == ".txt"


def test_md_format_default_is_txt(tmp_path: Path, pojk_profile, raw_md_file: Path) -> None:
    out, _ = normalize(raw_md_file, pojk_profile, output_dir=tmp_path)
    assert out.suffix == ".txt"


def test_md_format_bab_becomes_h2(tmp_path: Path, pojk_profile, raw_md_file: Path) -> None:
    out, _ = normalize(raw_md_file, pojk_profile, output_dir=tmp_path, fmt="md")
    lines = out.read_text(encoding="utf-8").splitlines()
    bab_lines = [l for l in lines if re.match(r"##\s+BAB\s+[IVX]", l)]
    assert len(bab_lines) >= 2


def test_md_format_pasal_becomes_h3(tmp_path: Path, pojk_profile, raw_md_file: Path) -> None:
    out, _ = normalize(raw_md_file, pojk_profile, output_dir=tmp_path, fmt="md")
    lines = out.read_text(encoding="utf-8").splitlines()
    pasal_lines = [l for l in lines if re.match(r"###\s+Pasal\s+\d+", l)]
    assert len(pasal_lines) >= 2


def test_txt_format_has_no_markdown_headings(tmp_path: Path, pojk_profile, raw_md_file: Path) -> None:
    out, _ = normalize(raw_md_file, pojk_profile, output_dir=tmp_path, fmt="txt")
    content = out.read_text(encoding="utf-8")
    assert "## " not in content
    assert "### " not in content


def test_md_format_meta_records_format(tmp_path: Path, pojk_profile, raw_md_file: Path) -> None:
    import json
    _, meta_path = normalize(raw_md_file, pojk_profile, output_dir=tmp_path, fmt="md")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["output_format"] == "md"


def test_txt_format_meta_records_format(tmp_path: Path, pojk_profile, raw_md_file: Path) -> None:
    import json
    _, meta_path = normalize(raw_md_file, pojk_profile, output_dir=tmp_path, fmt="txt")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["output_format"] == "txt"



def test_md_profile_without_headings_produces_plain_md(tmp_path: Path) -> None:
    from regulasi_id_corpus_prep.profile import Profile
    data = {
        "metadata": {"name": "bare", "description": "bare", "version": "1.0.0", "document_types": ["X"]},
        "rules": [{"name": "ws", "type": "whitespace_normalize"}],
        "validation": {"title_keywords": ["X"], "content_marker_pattern": "X", "content_marker_label": "X"},
    }
    prof = Profile.model_validate(data)
    p = tmp_path / "bare.raw.txt"
    p.write_text("BAB I Ketentuan Umum", encoding="utf-8")
    out, _ = normalize(p, prof, output_dir=tmp_path, fmt="md")
    content = out.read_text(encoding="utf-8")
    assert "## " not in content
    assert "BAB I" in content
