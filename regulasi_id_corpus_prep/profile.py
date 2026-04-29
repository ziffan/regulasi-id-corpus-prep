# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, Union

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator


class NoiseRemovalRule(BaseModel):
    name: str
    type: Literal["noise_removal"]
    pattern: str
    replacement: str = " "
    flags: list[str] = Field(default_factory=list)


class WhitespaceNormalizeRule(BaseModel):
    name: str
    type: Literal["whitespace_normalize"]


class StructureSplitRule(BaseModel):
    name: str
    type: Literal["structure_split"]
    pattern: str
    newlines_before: int = Field(default=2, ge=1, le=4)
    space_after: bool = False
    requires_following: str | None = None
    flags: list[str] = Field(default_factory=list)


Rule = Annotated[
    Union[NoiseRemovalRule, WhitespaceNormalizeRule, StructureSplitRule],
    Field(discriminator="type"),
]


class ProfileValidation(BaseModel):
    title_keywords: list[str]
    content_marker_pattern: str
    content_marker_label: str = "Pasal"
    noise_check_patterns: list[str] = Field(default_factory=list)


class ProfileMetadata(BaseModel):
    name: str
    description: str
    version: str
    document_types: list[str]


class Profile(BaseModel):
    metadata: ProfileMetadata
    rules: list[Rule]
    validation: ProfileValidation

    @model_validator(mode="after")
    def _check_unique_rule_names(self) -> "Profile":
        names = [r.name for r in self.rules]
        if len(names) != len(set(names)):
            dupes = [n for n in names if names.count(n) > 1]
            raise ValueError(f"Duplicate rule names: {list(set(dupes))}")
        return self


def load_profile(profile_name: str, profiles_dir: Path | None = None) -> Profile:
    if profiles_dir is None:
        profiles_dir = Path(__file__).parent / "profiles"

    profile_path = profiles_dir / f"{profile_name}.yaml"
    if not profile_path.exists():
        available = [p.stem for p in profiles_dir.glob("*.yaml") if not p.stem.startswith("_")]
        raise FileNotFoundError(
            f"Profile '{profile_name}' not found. "
            f"Available profiles: {available}. "
            f"Use 'list-profiles' to see all options."
        )

    with open(profile_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    try:
        return Profile.model_validate(data)
    except ValidationError as e:
        errors = e.errors()
        lines = []
        for err in errors:
            loc = " → ".join(str(part) for part in err["loc"])
            lines.append(f"  {loc}: {err['msg']}")
        raise ValueError(
            f"Profile '{profile_name}' has {len(errors)} validation error(s):\n"
            + "\n".join(lines)
        ) from e


def list_profiles(profiles_dir: Path | None = None) -> list[tuple[str, str]]:
    if profiles_dir is None:
        profiles_dir = Path(__file__).parent / "profiles"

    result = []
    for yaml_file in sorted(profiles_dir.glob("*.yaml")):
        if yaml_file.stem.startswith("_"):
            continue
        try:
            with open(yaml_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            name = data.get("metadata", {}).get("name", yaml_file.stem)
            description = data.get("metadata", {}).get("description", "")
            result.append((name, description))
        except Exception:
            result.append((yaml_file.stem, "(gagal dimuat)"))
    return result
