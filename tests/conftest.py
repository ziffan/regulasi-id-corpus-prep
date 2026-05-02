# Copyright 2026 Ziffany Firdinal
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from pathlib import Path

import fitz
import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"
PROFILES_FIXTURE_DIR = FIXTURES_DIR / "profiles"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
SAMPLE_PDF = EXAMPLES_DIR / "sample-input" / "SEOJK-19-2023.pdf"
SAMPLE_GOLDEN_TXT = EXAMPLES_DIR / "sample-output" / "SEOJK-19-2023.txt"


@pytest.fixture
def minimal_profile_dir() -> Path:
    return PROFILES_FIXTURE_DIR


@pytest.fixture
def empty_pdf(tmp_path: Path) -> Path:
    """PDF tanpa text layer (simulasi PDF hasil scan)."""
    doc = fitz.open()
    doc.new_page()
    path = tmp_path / "empty.pdf"
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture
def sample_pdf() -> Path:
    return SAMPLE_PDF


@pytest.fixture
def sample_golden_txt() -> Path:
    return SAMPLE_GOLDEN_TXT
