#!/usr/bin/env python3
"""Build the allowlisted, dependency-free GitHub Pages artifact."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import NoReturn


PUBLIC_FILES = (
    Path("index.html"),
    Path("style.css"),
    Path("script.js"),
    Path("robots.txt"),
    Path("sitemap.xml"),
    Path("assets/og-image.png"),
    Path("assets/ghandyit-logo.svg"),
)


def parse_args() -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="repository root containing the public source files (default: repository root)",
    )
    return parser.parse_args()


def fail(message: str) -> NoReturn:
    print(f"Build failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_source(root: Path, relative_path: Path) -> Path:
    source = root / relative_path
    if source.is_symlink():
        fail(f"source must not be a symlink: {relative_path}")
    if not source.is_file():
        fail(f"required source file is missing: {relative_path}")
    return source


def prepare_output(root: Path) -> Path:
    output = root / "_site"
    if output.is_symlink():
        fail("refusing to replace symlinked output directory: _site")
    if output.exists() and not output.is_dir():
        fail("refusing to replace non-directory output: _site")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    return output


def build(root: Path) -> None:
    root = root.expanduser().resolve()
    sources = [require_source(root, relative_path) for relative_path in PUBLIC_FILES]
    output = prepare_output(root)

    for source, relative_path in zip(sources, PUBLIC_FILES):
        destination = output / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    (output / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {output} with {len(PUBLIC_FILES)} public files and .nojekyll.")


def main() -> None:
    build(parse_args().root)


if __name__ == "__main__":
    main()
