# Copyright 2026 Ziffany Firdinal
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .profile import MarkdownHeading, NoiseRemovalRule, Profile, StructureSplitRule, WhitespaceNormalizeRule


def _build_re_flags(flag_names: list[str]) -> int:
    flags = 0
    for name in flag_names:
        flags |= getattr(re, name.upper(), 0)
    return flags


def _apply_rule(text: str, rule: object, stats: dict) -> str:
    if isinstance(rule, NoiseRemovalRule):
        flags = _build_re_flags(rule.flags)
        new_text, count = re.subn(rule.pattern, rule.replacement, text, flags=flags)
        stats[rule.name] = {"type": rule.type, "match_count": count}
        return new_text

    if isinstance(rule, WhitespaceNormalizeRule):
        new_text, count = re.subn(r"\s+", " ", text)
        stats[rule.name] = {"type": rule.type, "match_count": count}
        return new_text.strip()

    if isinstance(rule, StructureSplitRule):
        flags = _build_re_flags(rule.flags)
        prefix = "\n" * rule.newlines_before

        if rule.requires_following:
            # Consume the following keyword and re-insert with a space
            pattern = r"\s+(" + rule.pattern + r")\s+(" + rule.requires_following + r")"
            replacement = prefix + r"\1 \2"
        elif rule.space_after:
            pattern = r"\s+(" + rule.pattern + r")\s+"
            replacement = prefix + r"\1 "
        else:
            pattern = r"\s+(" + rule.pattern + r")"
            replacement = prefix + r"\1"

        new_text, count = re.subn(pattern, replacement, text, flags=flags)
        stats[rule.name] = {"type": rule.type, "match_count": count}
        return new_text

    return text


def _apply_markdown_headings(text: str, headings: list[MarkdownHeading]) -> str:
    if not headings:
        return text
    compiled = [
        (re.compile(h.pattern, _build_re_flags(h.flags)), h.level)
        for h in headings
    ]
    lines = text.split("\n")
    result = []
    for line in lines:
        for pattern, level in compiled:
            if pattern.match(line):
                line = "#" * level + " " + line
                break
        result.append(line)
    return "\n".join(result)


def normalize(
    raw_txt_path: Path,
    profile: Profile,
    output_dir: Path | None = None,
    fmt: str = "txt",
) -> tuple[Path, Path]:
    """Apply profile rules to a .raw.txt file, producing a corpus-ready .txt.

    Returns (txt_path, meta_json_path).
    """
    if output_dir is None:
        output_dir = raw_txt_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    name = raw_txt_path.name
    stem = name[:-8] if name.endswith(".raw.txt") else raw_txt_path.stem

    ext = ".md" if fmt == "md" else ".txt"
    out_path = output_dir / f"{stem}{ext}"
    meta_path = output_dir / f"{stem}.meta.json"

    text = raw_txt_path.read_text(encoding="utf-8")

    rule_stats: dict = {}
    for rule in profile.rules:
        text = _apply_rule(text, rule, rule_stats)

    # Strip each line and drop empty lines
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(line for line in lines if line).strip()

    if fmt == "md":
        text = _apply_markdown_headings(text, profile.markdown_headings)

    out_path.write_text(text, encoding="utf-8")

    meta = {
        "source_raw": raw_txt_path.name,
        "profile_name": profile.metadata.name,
        "profile_version": profile.metadata.version,
        "output_format": fmt,
        "rules_applied": rule_stats,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return out_path, meta_path
