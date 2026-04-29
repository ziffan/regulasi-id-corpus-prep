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
