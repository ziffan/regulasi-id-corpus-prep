# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from __future__ import annotations

import re
from pathlib import Path

from rich import box
from rich.console import Console
from rich.table import Table

from .profile import Profile

_MAX_LINE_LENGTH = 2000
_MIN_TITLE_LEN = 30
_MAX_TITLE_LEN = 400


class ValidationResult:
    def __init__(self) -> None:
        self.checks: list[dict] = []

    def add(self, name: str, status: str, detail: str) -> None:
        """Add a check result. status: 'pass' | 'warn' | 'fail'."""
        self.checks.append({"name": name, "status": status, "detail": detail})

    @property
    def exit_code(self) -> int:
        statuses = {c["status"] for c in self.checks}
        if "fail" in statuses:
            return 2
        if "warn" in statuses:
            return 1
        return 0


def validate_corpus(txt_path: Path, profile: Profile) -> ValidationResult:
    text = txt_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    result = ValidationResult()

    # 1. Title detected — check first 5 non-empty lines (SEOJK starts with "Yth." header)
    first_lines = [line for line in lines if line.strip()][:5]
    title_line = next(
        (
            line for line in first_lines
            if _MIN_TITLE_LEN <= len(line) <= _MAX_TITLE_LEN
            and any(kw.lower() in line.lower() for kw in profile.validation.title_keywords)
        ),
        None,
    )
    if title_line:
        preview = title_line[:80] + ("..." if len(title_line) > 80 else "")
        result.add("title_detected", "pass", f"'{preview}'")
    else:
        first_nonempty = first_lines[0] if first_lines else ""
        preview = first_nonempty[:80] + ("..." if len(first_nonempty) > 80 else "")
        result.add(
            "title_detected",
            "warn",
            f"Tidak ada judul terdeteksi dalam 5 baris pertama: '{preview}'",
        )

    # 2. Content marker count (e.g., Pasal)
    label = profile.validation.content_marker_label
    markers = re.findall(profile.validation.content_marker_pattern, text)
    marker_count = len(markers)
    check_name = label.lower().replace(" ", "_") + "_count"
    if marker_count > 0:
        result.add(check_name, "pass", f"{marker_count} {label} ditemukan")
    else:
        result.add(
            check_name,
            "fail",
            f"Tidak ada {label} terdeteksi — kemungkinan kegagalan normalisasi kritis",
        )

    # 3. Suspiciously long lines
    long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > _MAX_LINE_LENGTH]
    if not long_lines:
        result.add("line_length", "pass", "Tidak ada baris melebihi 2000 karakter")
    else:
        sample = long_lines[:5]
        result.add(
            "line_length",
            "warn",
            f"Baris panjang mencurigakan di baris: {sample}"
            + (" ..." if len(long_lines) > 5 else ""),
        )

    # 4. Noise residue
    found_noise = [
        pat
        for pat in profile.validation.noise_check_patterns
        if re.search(pat, text, re.IGNORECASE)
    ]
    if not found_noise:
        result.add("noise_residue", "pass", "Tidak ada noise residual terdeteksi")
    else:
        result.add("noise_residue", "warn", f"Pola noise masih ditemukan: {found_noise}")

    # 5. Encoding sanity
    has_replacement_char = "�" in text
    has_hex_escape = bool(re.search(r"\\x[0-9a-fA-F]{2}", text))
    if not has_replacement_char and not has_hex_escape:
        result.add("encoding_sanity", "pass", "Tidak ada karakter pengganti encoding")
    else:
        issues = []
        if has_replacement_char:
            issues.append("karakter \\ufffd ditemukan")
        if has_hex_escape:
            issues.append("escape sequence \\xNN ditemukan")
        result.add("encoding_sanity", "fail", "; ".join(issues))

    return result


_STATUS_DISPLAY = {
    "pass": "[green]PASS[/green]",
    "warn": "[yellow]WARN[/yellow]",
    "fail": "[red]FAIL[/red]",
}


def print_validation_report(
    txt_path: Path, result: ValidationResult, console: Console | None = None
) -> None:
    if console is None:
        console = Console()

    console.print(f"\n[bold]Laporan Validasi:[/bold] {txt_path.name}\n")

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Pemeriksaan", style="cyan", min_width=22)
    table.add_column("Status", min_width=10)
    table.add_column("Detail")

    for check in result.checks:
        table.add_row(
            check["name"],
            _STATUS_DISPLAY.get(check["status"], check["status"]),
            check["detail"],
        )

    console.print(table)

    ec = result.exit_code
    if ec == 0:
        console.print("[green]Semua pemeriksaan lulus.[/green]\n")
    elif ec == 1:
        console.print("[yellow]Ada peringatan - silakan periksa secara manual (lihat docs/VALIDATION_GUIDE.md).[/yellow]\n")
    else:
        console.print("[red]Ada kegagalan kritis — output kemungkinan tidak siap pakai.[/red]\n")
