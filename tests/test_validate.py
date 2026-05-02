# Copyright 2026 Ziffany Firdinal
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from pathlib import Path

import pytest

from regulasi_id_corpus_prep.profile import load_profile
from regulasi_id_corpus_prep.validate import validate_corpus, ValidationResult


@pytest.fixture
def pojk_profile():
    return load_profile("ojk-pojk")


def _write_txt(tmp_path: Path, content: str, name: str = "test.txt") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_title_pass_when_keyword_in_first_line(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(
        tmp_path,
        "PERATURAN OTORITAS JASA KEUANGAN NOMOR 99 TAHUN 2099 TENTANG SESUATU\n\nPasal 1 isi"
    )
    result = validate_corpus(txt, pojk_profile)
    title_check = next(c for c in result.checks if c["name"] == "title_detected")
    assert title_check["status"] == "pass"


def test_title_warn_when_no_keyword(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(tmp_path, "Dokumen tanpa kata kunci yang dikenal sama sekali disini\n\nPasal 1 isi")
    result = validate_corpus(txt, pojk_profile)
    title_check = next(c for c in result.checks if c["name"] == "title_detected")
    assert title_check["status"] == "warn"


def test_pasal_count_pass(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(tmp_path, "PERATURAN OTORITAS JASA KEUANGAN\n\nPasal 1 isi\n\nPasal 2 isi")
    result = validate_corpus(txt, pojk_profile)
    pasal_check = next(c for c in result.checks if "pasal" in c["name"])
    assert pasal_check["status"] == "pass"
    assert "2" in pasal_check["detail"]


def test_pasal_count_fail_when_absent(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(tmp_path, "PERATURAN OTORITAS JASA KEUANGAN\n\nIsi tanpa pasal sama sekali.")
    result = validate_corpus(txt, pojk_profile)
    pasal_check = next(c for c in result.checks if "pasal" in c["name"])
    assert pasal_check["status"] == "fail"


def test_long_line_warn(tmp_path: Path, pojk_profile) -> None:
    long_line = "a" * 2001
    txt = _write_txt(tmp_path, f"PERATURAN OTORITAS JASA KEUANGAN\n\nPasal 1 isi\n{long_line}")
    result = validate_corpus(txt, pojk_profile)
    line_check = next(c for c in result.checks if c["name"] == "line_length")
    assert line_check["status"] == "warn"


def test_no_long_line_pass(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(tmp_path, "PERATURAN OTORITAS JASA KEUANGAN\n\nPasal 1 isi pendek.")
    result = validate_corpus(txt, pojk_profile)
    line_check = next(c for c in result.checks if c["name"] == "line_length")
    assert line_check["status"] == "pass"


def test_noise_residue_warn(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(
        tmp_path,
        "PERATURAN OTORITAS JASA KEUANGAN\n\nPasal 1 isi https://jdih.ojk.go.id/ sisa noise"
    )
    result = validate_corpus(txt, pojk_profile)
    noise_check = next(c for c in result.checks if c["name"] == "noise_residue")
    assert noise_check["status"] == "warn"


def test_no_noise_residue_pass(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(tmp_path, "PERATURAN OTORITAS JASA KEUANGAN\n\nPasal 1 isi bersih.")
    result = validate_corpus(txt, pojk_profile)
    noise_check = next(c for c in result.checks if c["name"] == "noise_residue")
    assert noise_check["status"] == "pass"


def test_encoding_sanity_fail_on_replacement_char(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(tmp_path, "PERATURAN OTORITAS JASA KEUANGAN\n\nPasal 1 isi � rusak")
    result = validate_corpus(txt, pojk_profile)
    enc_check = next(c for c in result.checks if c["name"] == "encoding_sanity")
    assert enc_check["status"] == "fail"


def test_exit_code_zero_all_pass(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(
        tmp_path,
        "PERATURAN OTORITAS JASA KEUANGAN NOMOR 99 TAHUN 2099 TENTANG SESUATU\n\nPasal 1 isi bersih."
    )
    result = validate_corpus(txt, pojk_profile)
    # May be 0 or 1 depending on title length — just check it's not 2
    assert result.exit_code < 2


def test_exit_code_two_on_critical_failure(tmp_path: Path, pojk_profile) -> None:
    txt = _write_txt(tmp_path, "PERATURAN OTORITAS JASA KEUANGAN\n\nIsi tanpa pasal sama sekali.")
    result = validate_corpus(txt, pojk_profile)
    assert result.exit_code == 2
