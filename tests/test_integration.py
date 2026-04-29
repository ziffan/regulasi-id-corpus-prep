# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from pathlib import Path

import pytest

from regulasi_id_corpus_prep.extract import extract_pdf
from regulasi_id_corpus_prep.normalize import normalize
from regulasi_id_corpus_prep.profile import load_profile
from regulasi_id_corpus_prep.validate import validate_corpus


@pytest.mark.skipif(
    not (Path(__file__).parent.parent / "examples" / "sample-input" / "SEOJK-19-2023.pdf").exists(),
    reason="Sample PDF belum tersedia di examples/sample-input/",
)
class TestFullPipeline:
    def test_extract_normalize_validate_succeeds(self, sample_pdf: Path, tmp_path: Path) -> None:
        profile = load_profile("ojk-seojk")

        raw_txt, raw_meta = extract_pdf(sample_pdf, output_dir=tmp_path)
        assert raw_txt.exists()
        assert raw_meta.exists()

        txt_path, meta_path = normalize(raw_txt, profile, output_dir=tmp_path)
        assert txt_path.exists()
        assert meta_path.exists()

        result = validate_corpus(txt_path, profile)
        # Pipeline sukses = exit code bukan 2 (kritis)
        assert result.exit_code < 2

    def test_normalized_output_not_empty(self, sample_pdf: Path, tmp_path: Path) -> None:
        profile = load_profile("ojk-seojk")
        raw_txt, _ = extract_pdf(sample_pdf, output_dir=tmp_path)
        txt_path, _ = normalize(raw_txt, profile, output_dir=tmp_path)
        content = txt_path.read_text(encoding="utf-8")
        assert len(content) > 500

    def test_normalized_output_has_no_jdih_links(self, sample_pdf: Path, tmp_path: Path) -> None:
        import re
        profile = load_profile("ojk-seojk")
        raw_txt, _ = extract_pdf(sample_pdf, output_dir=tmp_path)
        txt_path, _ = normalize(raw_txt, profile, output_dir=tmp_path)
        content = txt_path.read_text(encoding="utf-8")
        assert not re.search(r"jdih\.ojk\.go\.id", content, re.IGNORECASE)

    def test_golden_file_regression(self, sample_pdf: Path, sample_golden_txt: Path, tmp_path: Path) -> None:
        if not sample_golden_txt.exists():
            pytest.skip("Golden file belum di-commit di examples/sample-output/")

        profile = load_profile("ojk-seojk")
        raw_txt, _ = extract_pdf(sample_pdf, output_dir=tmp_path)
        txt_path, _ = normalize(raw_txt, profile, output_dir=tmp_path)

        actual = txt_path.read_text(encoding="utf-8")
        expected = sample_golden_txt.read_text(encoding="utf-8")
        assert actual == expected, (
            "Output normalisasi berbeda dari golden file.\n"
            "Jika perubahan ini disengaja, jalankan ulang generate_golden_files.py "
            "dan commit hasilnya."
        )
