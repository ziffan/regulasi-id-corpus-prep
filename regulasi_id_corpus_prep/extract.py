# Copyright 2026 Ziffany Firdinal
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import fitz  # PyMuPDF

_PYMUPDF_VERSION = fitz.version[0]

# Average characters per page below this threshold → likely scanned PDF
_MIN_AVG_CHARS_PER_PAGE = 50


def extract_pdf(pdf_path: Path, output_dir: Path | None = None) -> tuple[Path, Path]:
    """Extract text from a born-digital PDF.

    Returns (raw_txt_path, raw_meta_json_path).
    Raises ValueError if the PDF appears to have no text layer (likely scanned).
    """
    if output_dir is None:
        output_dir = pdf_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = pdf_path.stem
    raw_txt_path = output_dir / f"{stem}.raw.txt"
    meta_path = output_dir / f"{stem}.raw.meta.json"

    doc = fitz.open(str(pdf_path))
    page_count = len(doc)

    pages_text: list[str] = []
    page_lengths: list[int] = []

    for page in doc:
        text = page.get_text("text", sort=True)
        pages_text.append(text)
        page_lengths.append(len(text))

    doc.close()

    total_chars = sum(page_lengths)
    avg_chars = total_chars / page_count if page_count > 0 else 0

    if avg_chars < _MIN_AVG_CHARS_PER_PAGE:
        raise ValueError(
            f"No text layer detected in '{pdf_path.name}'. "
            f"This tool does not handle scanned PDFs. "
            f"See docs/DECISION_TREE.md."
        )

    raw_text = "\n".join(pages_text)
    raw_txt_path.write_text(raw_text, encoding="utf-8")

    meta = {
        "source_file": pdf_path.name,
        "page_count": page_count,
        "page_text_lengths": page_lengths,
        "total_chars": total_chars,
        "extraction_method": "PyMuPDF",
        "pymupdf_version": _PYMUPDF_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return raw_txt_path, meta_path
