# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

import json
from pathlib import Path

import fitz
import pytest

from regulasi_id_corpus_prep.extract import extract_pdf


@pytest.fixture
def small_born_digital_pdf(tmp_path: Path) -> Path:
    """PDF born-digital kecil dengan text layer."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), "PERATURAN OTORITAS JASA KEUANGAN NOMOR 1 TAHUN 2099")
    page.insert_text((72, 130), "Pasal 1 Ketentuan ini berlaku sejak ditetapkan.")
    path = tmp_path / "test_born_digital.pdf"
    doc.save(str(path))
    doc.close()
    return path


def test_extract_produces_raw_txt(small_born_digital_pdf: Path, tmp_path: Path) -> None:
    raw_txt, _ = extract_pdf(small_born_digital_pdf, output_dir=tmp_path)
    assert raw_txt.exists()
    assert raw_txt.suffix == ".txt"
    assert raw_txt.name.endswith(".raw.txt")
    content = raw_txt.read_text(encoding="utf-8")
    assert len(content) > 0


def test_extract_produces_meta_json(small_born_digital_pdf: Path, tmp_path: Path) -> None:
    _, meta_path = extract_pdf(small_born_digital_pdf, output_dir=tmp_path)
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["page_count"] == 1
    assert meta["extraction_method"] == "PyMuPDF"
    assert "pymupdf_version" in meta
    assert "timestamp" in meta
    assert "page_text_lengths" in meta


def test_extract_meta_contains_source_filename(small_born_digital_pdf: Path, tmp_path: Path) -> None:
    _, meta_path = extract_pdf(small_born_digital_pdf, output_dir=tmp_path)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["source_file"] == small_born_digital_pdf.name


def test_extract_scanned_pdf_raises_value_error(empty_pdf: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No text layer detected"):
        extract_pdf(empty_pdf, output_dir=tmp_path)


def test_extract_scanned_pdf_does_not_write_output(empty_pdf: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        extract_pdf(empty_pdf, output_dir=tmp_path)
    raw_files = list(tmp_path.glob("*.raw.txt"))
    assert len(raw_files) == 0


def test_extract_default_output_dir(tmp_path: Path) -> None:
    # Create a fresh PDF in a subdir so default output goes to the same subdir
    import fitz
    subdir = tmp_path / "input"
    subdir.mkdir()
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), "PERATURAN OTORITAS JASA KEUANGAN NOMOR 2 TAHUN 2099")
    pdf_path = subdir / "test2.pdf"
    doc.save(str(pdf_path))
    doc.close()
    raw_txt, meta = extract_pdf(pdf_path)
    assert raw_txt.parent == subdir
    assert meta.parent == subdir


def test_extract_sample_pdf(sample_pdf: Path, tmp_path: Path) -> None:
    pytest.importorskip("fitz")
    if not sample_pdf.exists():
        pytest.skip("Sample PDF belum tersedia di examples/sample-input/")
    raw_txt, meta_path = extract_pdf(sample_pdf, output_dir=tmp_path)
    assert raw_txt.exists()
    content = raw_txt.read_text(encoding="utf-8")
    assert len(content) > 1000
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["page_count"] > 0
