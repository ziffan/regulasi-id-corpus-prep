# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from pathlib import Path

import pytest

from regulasi_id_corpus_prep.profile import (
    Profile,
    load_profile,
    list_profiles,
)


def test_load_valid_profile(minimal_profile_dir: Path) -> None:
    profile = load_profile("test-minimal", profiles_dir=minimal_profile_dir)
    assert profile.metadata.name == "test-minimal"
    assert len(profile.rules) == 5
    assert profile.validation.content_marker_label == "Section"


def test_load_builtin_ojk_pojk() -> None:
    profile = load_profile("ojk-pojk")
    assert profile.metadata.name == "ojk-pojk"
    assert any(r.type == "whitespace_normalize" for r in profile.rules)


def test_load_builtin_ojk_seojk() -> None:
    profile = load_profile("ojk-seojk")
    assert profile.metadata.name == "ojk-seojk"
    assert profile.validation.content_marker_label == "Bagian"


def test_missing_profile_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        load_profile("profile-tidak-ada", profiles_dir=tmp_path)


def test_malformed_profile_raises_value_error(minimal_profile_dir: Path) -> None:
    with pytest.raises(ValueError, match="validation error"):
        load_profile("malformed_profile", profiles_dir=minimal_profile_dir)


def test_duplicate_rule_names_raises_error() -> None:
    data = {
        "metadata": {
            "name": "test",
            "description": "test",
            "version": "1.0.0",
            "document_types": ["TEST"],
        },
        "rules": [
            {"name": "sama", "type": "whitespace_normalize"},
            {"name": "sama", "type": "whitespace_normalize"},
        ],
        "validation": {
            "title_keywords": ["TEST"],
            "content_marker_pattern": "test",
            "content_marker_label": "Test",
        },
    }
    with pytest.raises(Exception, match="[Dd]uplicate"):
        Profile.model_validate(data)


def test_list_profiles_returns_builtin() -> None:
    profiles = list_profiles()
    names = [name for name, _ in profiles]
    assert "ojk-pojk" in names
    assert "ojk-seojk" in names


def test_list_profiles_excludes_template() -> None:
    profiles = list_profiles()
    names = [name for name, _ in profiles]
    assert "_template" not in names
