# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ziffany Firdinal

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich import box
from rich.console import Console
from rich.table import Table

from . import __version__
from .extract import extract_pdf
from .normalize import normalize
from .profile import load_profile, list_profiles
from .validate import print_validation_report, validate_corpus

_console = Console(highlight=False)
_err = Console(stderr=True, highlight=False)


def _error(msg: str) -> None:
    _err.print(f"[red]Error:[/red] {msg}")


@click.group()
@click.version_option(version=__version__, prog_name="regulasi-id-corpus-prep")
def main() -> None:
    """regulasi-id-corpus-prep: Konversi PDF regulasi OJK ke teks corpus bersih."""


@main.command("extract")
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Direktori output (default: direktori yang sama dengan input).",
)
def extract_cmd(input_path: Path, output_dir: Path | None) -> None:
    """Ekstrak teks dari PDF ke file .raw.txt.

    INPUT_PATH bisa berupa satu file .pdf atau direktori berisi file .pdf.
    """
    if input_path.is_dir():
        pdf_files = sorted(input_path.glob("*.pdf"))
        if not pdf_files:
            _error(f"Tidak ada file PDF ditemukan di '{input_path}'")
            sys.exit(1)
        target_dir = output_dir or input_path
    else:
        pdf_files = [input_path]
        target_dir = output_dir or input_path.parent

    success = 0
    for pdf in pdf_files:
        try:
            raw_txt, _ = extract_pdf(pdf, output_dir=target_dir)
            _console.print(f"[green]OK[/green] {pdf.name} -> {raw_txt.name}")
            success += 1
        except ValueError as exc:
            _error(str(exc))
            sys.exit(1)
        except Exception as exc:
            _error(f"Gagal mengekstrak '{pdf.name}': {exc}")
            sys.exit(1)

    _console.print(f"\n[bold]{success}/{len(pdf_files)} file berhasil diekstrak.[/bold]")


@main.command("normalize")
@click.argument("raw_txt_path", type=click.Path(exists=True, path_type=Path))
@click.option("--profile", "-p", required=True, help="Nama profile (contoh: ojk-pojk).")
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Direktori output (default: direktori yang sama dengan input).",
)
@click.option(
    "--profiles-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Direktori profile kustom.",
)
@click.option(
    "--format", "-f", "fmt",
    type=click.Choice(["txt", "md"]),
    default="txt",
    show_default=True,
    help="Format output: txt (plain text) atau md (Markdown dengan heading).",
)
def normalize_cmd(
    raw_txt_path: Path,
    profile: str,
    output_dir: Path | None,
    profiles_dir: Path | None,
    fmt: str,
) -> None:
    """Normalisasi file .raw.txt menjadi corpus .txt menggunakan profile.

    RAW_TXT_PATH adalah file .raw.txt hasil perintah 'extract'.
    """
    try:
        prof = load_profile(profile, profiles_dir=profiles_dir)
    except (FileNotFoundError, ValueError) as exc:
        _error(str(exc))
        sys.exit(1)

    target_dir = output_dir or raw_txt_path.parent

    try:
        out_path, _ = normalize(raw_txt_path, prof, output_dir=target_dir, fmt=fmt)
        _console.print(f"[green]OK[/green] {raw_txt_path.name} -> {out_path.name}")
    except Exception as exc:
        _error(f"Normalisasi gagal: {exc}")
        sys.exit(1)


@main.command("validate")
@click.argument("txt_path", type=click.Path(exists=True, path_type=Path))
@click.option("--profile", "-p", required=True, help="Nama profile (contoh: ojk-pojk).")
@click.option(
    "--profiles-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Direktori profile kustom.",
)
def validate_cmd(txt_path: Path, profile: str, profiles_dir: Path | None) -> None:
    """Jalankan pemeriksaan otomatis pada file .txt hasil normalisasi.

    TXT_PATH adalah file .txt hasil perintah 'normalize'.
    Exit code: 0=semua lulus, 1=ada peringatan, 2=kegagalan kritis.
    """
    try:
        prof = load_profile(profile, profiles_dir=profiles_dir)
    except (FileNotFoundError, ValueError) as exc:
        _error(str(exc))
        sys.exit(1)

    try:
        result = validate_corpus(txt_path, prof)
        print_validation_report(txt_path, result, console=_console)
        sys.exit(result.exit_code)
    except Exception as exc:
        _error(f"Validasi gagal: {exc}")
        sys.exit(2)


@main.command("run")
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--profile", "-p", required=True, help="Nama profile (contoh: ojk-pojk).")
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Direktori output.",
)
@click.option(
    "--profiles-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Direktori profile kustom.",
)
@click.option(
    "--format", "-f", "fmt",
    type=click.Choice(["txt", "md"]),
    default="txt",
    show_default=True,
    help="Format output: txt (plain text) atau md (Markdown dengan heading).",
)
def run_cmd(
    input_path: Path,
    profile: str,
    output_dir: Path | None,
    profiles_dir: Path | None,
    fmt: str,
) -> None:
    """Jalankan pipeline penuh: extract → normalize → validate.

    INPUT_PATH bisa berupa satu file .pdf atau direktori berisi file .pdf.
    Ini adalah perintah utama untuk pengguna non-teknis.
    """
    try:
        prof = load_profile(profile, profiles_dir=profiles_dir)
    except (FileNotFoundError, ValueError) as exc:
        _error(str(exc))
        sys.exit(1)

    if input_path.is_dir():
        pdf_files = sorted(input_path.glob("*.pdf"))
        if not pdf_files:
            _error(f"Tidak ada file PDF ditemukan di '{input_path}'")
            sys.exit(1)
        target_dir = output_dir or input_path
    else:
        pdf_files = [input_path]
        target_dir = output_dir or input_path.parent

    has_critical_failure = False

    for pdf in pdf_files:
        _console.print(f"\n[bold]Memproses:[/bold] {pdf.name}")

        try:
            raw_txt, _ = extract_pdf(pdf, output_dir=target_dir)
            _console.print(f"  [green]OK[/green] extract -> {raw_txt.name}")
        except ValueError as exc:
            _error(str(exc))
            sys.exit(1)
        except Exception as exc:
            _error(f"Extract gagal untuk '{pdf.name}': {exc}")
            sys.exit(1)

        try:
            out_path, _ = normalize(raw_txt, prof, output_dir=target_dir, fmt=fmt)
            _console.print(f"  [green]OK[/green] normalize -> {out_path.name}")
        except Exception as exc:
            _error(f"Normalize gagal untuk '{raw_txt.name}': {exc}")
            sys.exit(1)

        try:
            result = validate_corpus(out_path, prof)
            print_validation_report(txt_path, result, console=_console)
            if result.exit_code == 2:
                has_critical_failure = True
        except Exception as exc:
            _error(f"Validate gagal untuk '{out_path.name}': {exc}")
            sys.exit(2)

    if has_critical_failure:
        sys.exit(2)


@main.command("list-profiles")
@click.option(
    "--profiles-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Direktori profile kustom.",
)
def list_profiles_cmd(profiles_dir: Path | None) -> None:
    """Tampilkan semua profile yang tersedia."""
    profiles = list_profiles(profiles_dir=profiles_dir)
    if not profiles:
        _console.print("Tidak ada profile ditemukan.")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Profile", style="cyan", min_width=20)
    table.add_column("Deskripsi")

    for name, description in profiles:
        table.add_row(name, description)

    _console.print(table)
