#!/usr/bin/env python3
"""Validate the source tree or the exact public GitHub Pages artifact."""

from __future__ import annotations

import argparse
import html
import re
import struct
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote, urlsplit


CANONICAL_URL = "https://ghandyp.github.io/GhandyP/"
CANONICAL_IMAGE_URL = f"{CANONICAL_URL}assets/og-image.png"
IMAGE_DIMENSIONS = (1200, 630)

SOURCE_FILES = (
    Path("index.html"),
    Path("style.css"),
    Path("script.js"),
    Path("robots.txt"),
    Path("sitemap.xml"),
    Path("README.md"),
    Path("assets/og-image.png"),
    Path("assets/ghandyit-logo.svg"),
    Path("scripts/build-public-artifact.py"),
    Path("scripts/validate_site.py"),
)

ARTIFACT_FILES = frozenset(
    {
        "index.html",
        "style.css",
        "script.js",
        "robots.txt",
        "sitemap.xml",
        "assets/og-image.png",
        "assets/ghandyit-logo.svg",
        ".nojekyll",
    }
)
ARTIFACT_DIRECTORIES = frozenset({"assets"})

REQUIRED_IDS = (
    "main-content",
    "top",
    "about",
    "capabilities",
    "services",
    "experience",
    "methods",
    "learning",
    "work",
    "contact",
)

REQUIRED_META = (
    ("name", "description"),
    ("property", "og:title"),
    ("property", "og:description"),
    ("property", "og:type"),
    ("property", "og:url"),
    ("property", "og:site_name"),
    ("property", "og:image"),
    ("property", "og:image:width"),
    ("property", "og:image:height"),
    ("property", "og:image:alt"),
    ("name", "twitter:card"),
    ("name", "twitter:title"),
    ("name", "twitter:description"),
    ("name", "twitter:image"),
    ("name", "twitter:image:alt"),
)

# Keep privacy-sensitive checks in one small, configurable list. Split values
# which are also likely to occur in validator-oriented documentation or tests.
LEAKAGE_TERMS = (
    "mail" + "to:",
    "tel" + ":",
    "info@" + "gandyit" + ".com",
    "+" + "58 " + "424",
    "Maracay" + ", " + "Venezuela",
    "available for " + "remote work",
    "on-site opportunities " + "in Caracas",
    "Remote / " + "Caracas",
    "Available: " + "Remote, Caracas",
    "Remote, " + "Caracas",
    "open to full-time and contract " + "opportunities",
    "open to full-time and contract " + "roles",
    "two-week notice " + "period",
    "Martin " + "Ghandy " + "Prieto",
    "Martin " + "Ghandy " + "Prieto " + "Rodriguez",
)

PROFILE_URLS = (
    "https://github.com/GhandyP",
    "https://linkedin.com/in/martin-prieto-564253a9",
)

IMAGE_SUFFIXES = frozenset(
    {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
)
MARKDOWN_LINK_RE = re.compile(
    r"(!?)\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)\n]+))"
)


class PageParser(HTMLParser):
    """Collect the small set of HTML facts needed by this validator."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1_count = 0
        self.ids: List[Tuple[str, int]] = []
        self.fragment_links: List[Tuple[str, int]] = []
        self.metadata: Dict[Tuple[str, str], List[str]] = {}
        self.canonical_links: List[Tuple[str, int]] = []
        self.title_values: List[str] = []
        self._title_parts: Optional[List[str]] = None

    @staticmethod
    def _attributes(attrs: Sequence[Tuple[str, Optional[str]]]) -> Dict[str, str]:
        return {
            name.casefold(): value or ""
            for name, value in attrs
            if name is not None
        }

    def handle_starttag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        tag = tag.casefold()
        line, _ = self.getpos()
        attributes = self._attributes(attrs)

        if tag == "h1":
            self.h1_count += 1
        if "id" in attributes:
            self.ids.append((attributes["id"], line))
        if tag == "a" and "href" in attributes:
            self.fragment_links.append((attributes["href"], line))
        if tag == "meta":
            field_kind = ""
            field_name = ""
            if attributes.get("name"):
                field_kind = "name"
                field_name = attributes["name"].casefold()
            elif attributes.get("property"):
                field_kind = "property"
                field_name = attributes["property"].casefold()
            if field_kind and "content" in attributes:
                self.metadata.setdefault((field_kind, field_name), []).append(
                    attributes["content"].strip()
                )
        if tag == "link" and "canonical" in attributes.get("rel", "").casefold().split():
            self.canonical_links.append((attributes.get("href", "").strip(), line))
        if tag == "title" and self._title_parts is None:
            self._title_parts = []

    def handle_startendtag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "title" and self._title_parts is not None:
            self.title_values.append("".join(self._title_parts).strip())
            self._title_parts = None

    def handle_data(self, data: str) -> None:
        if self._title_parts is not None:
            self._title_parts.append(data)


class ReadmeMarkupParser(HTMLParser):
    """Collect relative asset references from inline HTML in the README."""

    ASSET_TAGS = frozenset({"audio", "img", "link", "script", "source", "video"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.asset_links: List[Tuple[str, int]] = []

    def handle_starttag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        if tag.casefold() not in self.ASSET_TAGS:
            return
        attributes = {name.casefold(): value or "" for name, value in attrs}
        attribute_name = "src" if "src" in attributes else "href"
        if attribute_name in attributes:
            self.asset_links.append((attributes[attribute_name], self.getpos()[0]))



def normalize_text(value: str) -> str:
    """Normalize case, entities, and whitespace for copy-policy checks."""
    return " ".join(html.unescape(value).casefold().split())



def add_error(errors: List[str], message: str) -> None:
    errors.append(message)



def require_directory(root: Path, errors: List[str]) -> bool:
    if not root.exists():
        add_error(errors, f"root directory is missing: {root}")
        return False
    if not root.is_dir():
        add_error(errors, f"root path is not a directory: {root}")
        return False
    return True



def validate_required_files(root: Path, errors: List[str]) -> None:
    for relative_path in SOURCE_FILES:
        path = root / relative_path
        if path.is_symlink():
            add_error(errors, f"required source file must not be a symlink: {relative_path}")
        elif not path.is_file():
            add_error(errors, f"required source file is missing: {relative_path}")



def validate_artifact_layout(root: Path, errors: List[str]) -> None:
    if not require_directory(root, errors):
        return

    for relative_path in sorted(ARTIFACT_FILES):
        path = root / relative_path
        if path.is_symlink():
            add_error(errors, f"artifact file must not be a symlink: {relative_path}")
        elif not path.is_file():
            add_error(errors, f"required artifact file is missing: {relative_path}")

    allowed_paths = set(ARTIFACT_FILES) | set(ARTIFACT_DIRECTORIES)
    for path in root.rglob("*"):
        relative_path = path.relative_to(root).as_posix()
        if relative_path not in allowed_paths:
            add_error(errors, f"artifact contains a path outside the public allowlist: {relative_path}")



def read_utf8(path: Path, errors: List[str]) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        add_error(errors, f"could not read {path}: {exc}")
    except UnicodeError as exc:
        add_error(errors, f"{path} is not valid UTF-8: {exc}")
    return None



def parse_page(path: Path, text: str, errors: List[str]) -> Optional[PageParser]:
    parser = PageParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:  # HTMLParser can surface malformed input errors.
        add_error(errors, f"could not parse {path} as HTML: {exc}")
        return None
    return parser



def metadata_values(parser: PageParser, kind: str, field: str) -> List[str]:
    return parser.metadata.get((kind, field), [])



def validate_metadata(parser: PageParser, errors: List[str]) -> None:
    nonempty_titles = [title for title in parser.title_values if title]
    if len(parser.title_values) != 1 or len(nonempty_titles) != 1:
        add_error(errors, "index.html: expected exactly one non-empty <title>")

    for kind, field in REQUIRED_META:
        values = metadata_values(parser, kind, field)
        if not values or not any(value for value in values):
            add_error(errors, f"index.html: missing non-empty meta field {kind}={field!r}")

    canonical_values = parser.canonical_links
    if len(canonical_values) != 1 or canonical_values[0][0] != CANONICAL_URL:
        observed = [value for value, _ in canonical_values]
        add_error(
            errors,
            f"index.html: expected one canonical link with href {CANONICAL_URL!r}; found {observed!r}",
        )

    image_fields = (("property", "og:image"), ("name", "twitter:image"))
    for kind, field in image_fields:
        values = metadata_values(parser, kind, field)
        if any(value != CANONICAL_IMAGE_URL for value in values) or not values:
            add_error(
                errors,
                f"index.html: every {kind}={field!r} image must be {CANONICAL_IMAGE_URL!r}; found {values!r}",
            )

    if any(value != CANONICAL_URL for value in metadata_values(parser, "property", "og:url")):
        add_error(errors, f"index.html: og:url must be {CANONICAL_URL!r}")

    dimensions = {
        "og:image:width": str(IMAGE_DIMENSIONS[0]),
        "og:image:height": str(IMAGE_DIMENSIONS[1]),
    }
    for field, expected in dimensions.items():
        values = metadata_values(parser, "property", field)
        if any(value != expected for value in values) or not values:
            add_error(
                errors,
                f"index.html: property={field!r} must be {expected!r}; found {values!r}",
            )



def page_ids(parser: PageParser) -> Set[str]:
    return {value for value, _ in parser.ids if value}



def local_fragment_target(path: str) -> bool:
    return path in {"", "/", ".", "./", "index.html", "./index.html", "/index.html"}



def validate_fragment_links(
    root: Path,
    links: Iterable[Tuple[str, int]],
    ids: Set[str],
    errors: List[str],
) -> None:
    canonical_host = urlsplit(CANONICAL_URL).netloc.casefold()
    for href, line in links:
        value = href.strip()
        if not value:
            continue
        try:
            parsed = urlsplit(value)
        except ValueError as exc:
            add_error(errors, f"index.html:{line}: invalid link {value!r}: {exc}")
            continue

        is_same_site_absolute = (
            parsed.scheme.casefold() in {"http", "https"}
            and parsed.netloc.casefold() == canonical_host
        )
        is_local = not parsed.scheme and not parsed.netloc
        if not parsed.fragment:
            if "#" in value and (is_local or is_same_site_absolute):
                add_error(errors, f"index.html:{line}: link has an empty fragment: {value!r}")
            continue
        if not is_local and not is_same_site_absolute:
            continue

        fragment = unquote(parsed.fragment)
        if local_fragment_target(parsed.path) or (
            is_same_site_absolute and local_fragment_target(parsed.path)
        ):
            if fragment not in ids:
                add_error(
                    errors,
                    f"index.html:{line}: local fragment {fragment!r} does not resolve in index.html",
                )
            continue

        target_text_path = parsed.path.lstrip("/")
        target_path = (root / target_text_path).resolve()
        root_path = root.resolve()
        try:
            target_path.relative_to(root_path)
        except ValueError:
            add_error(errors, f"index.html:{line}: fragment target escapes the site root: {value!r}")
            continue
        if not target_path.is_file():
            add_error(errors, f"index.html:{line}: local fragment target is missing: {target_text_path!r}")
        elif target_path.suffix.casefold() not in {".html", ".htm"}:
            add_error(errors, f"index.html:{line}: fragment target is not an HTML file: {value!r}")
        else:
            target_ids = ids
            if target_path != (root / "index.html").resolve():
                target_text = read_utf8(target_path, errors)
                target_parser = (
                    parse_page(target_path, target_text, errors)
                    if target_text is not None
                    else None
                )
                if target_parser is None:
                    continue
                target_ids = page_ids(target_parser)
            if fragment not in target_ids:
                add_error(
                    errors,
                    f"index.html:{line}: local fragment {fragment!r} does not resolve in {target_text_path!r}",
                )



def validate_html(root: Path, errors: List[str]) -> None:
    path = root / "index.html"
    if not path.is_file():
        return
    text = read_utf8(path, errors)
    if text is None:
        return
    parser = parse_page(path, text, errors)
    if parser is None:
        return

    if parser.h1_count != 1:
        add_error(errors, f"index.html: expected exactly one <h1>, found {parser.h1_count}")

    ids = page_ids(parser)
    for required_id in REQUIRED_IDS:
        if required_id not in ids:
            add_error(errors, f"index.html: required public anchor id is missing: #{required_id}")

    duplicate_ids = sorted(
        value for value in ids if sum(1 for candidate, _ in parser.ids if candidate == value) > 1
    )
    for duplicate_id in duplicate_ids:
        add_error(errors, f"index.html: public id is duplicated: #{duplicate_id}")

    validate_fragment_links(root, parser.fragment_links, ids, errors)
    validate_metadata(parser, errors)



def validate_png(path: Path, errors: List[str]) -> None:
    try:
        data = path.read_bytes()
    except OSError as exc:
        add_error(errors, f"could not read {path}: {exc}")
        return

    signature = b"\x89PNG\r\n\x1a\n"
    if len(data) < 33 or data[:8] != signature:
        add_error(errors, f"{path}: expected a PNG with an IHDR chunk")
        return

    ihdr_length = struct.unpack_from(">I", data, 8)[0]
    if data[12:16] != b"IHDR" or ihdr_length != 13 or len(data) < 16 + ihdr_length:
        add_error(errors, f"{path}: malformed PNG IHDR chunk")
        return

    ihdr = data[16 : 16 + ihdr_length]
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
        ">IIBBBBB", ihdr
    )
    if (width, height) != IMAGE_DIMENSIONS:
        add_error(
            errors,
            f"{path}: expected dimensions {IMAGE_DIMENSIONS[0]}x{IMAGE_DIMENSIONS[1]}, found {width}x{height}",
        )
    if bit_depth != 8 or color_type not in {2, 6}:
        add_error(errors, f"{path}: expected an 8-bit RGB or RGBA PNG")
    if (compression, filter_method, interlace) != (0, 0, 0):
        add_error(errors, f"{path}: unsupported PNG compression, filter, or interlace metadata")
    if b"IEND" not in data:
        add_error(errors, f"{path}: PNG is missing its IEND chunk")



def validate_leakage(root: Path, relative_paths: Iterable[Path], errors: List[str]) -> None:
    normalized_terms = [(term, normalize_text(term)) for term in LEAKAGE_TERMS]
    for relative_path in relative_paths:
        path = root / relative_path
        if not path.is_file():
            continue
        text = read_utf8(path, errors)
        if text is None:
            continue
        normalized_text = normalize_text(text)
        for display_term, normalized_term in normalized_terms:
            if normalized_term in normalized_text:
                add_error(
                    errors,
                    f"{relative_path}: disallowed private/contact/identity text found: {display_term!r}",
                )



def parse_readme_markup(text: str, errors: List[str]) -> List[Tuple[str, int]]:
    links: List[Tuple[str, int]] = []
    parser = ReadmeMarkupParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        add_error(errors, f"README.md: could not parse inline HTML: {exc}")
    links.extend(parser.asset_links)

    for match in MARKDOWN_LINK_RE.finditer(text):
        image_marker, angle_destination, bare_destination = match.groups()
        destination = angle_destination or bare_destination or ""
        try:
            path = urlsplit(destination).path
        except ValueError:
            path = destination
        is_image = bool(image_marker)
        is_asset_path = path.casefold().startswith(("assets/", "./assets/"))
        is_image_path = Path(path).suffix.casefold() in IMAGE_SUFFIXES
        if is_image or is_asset_path or is_image_path:
            line = text.count("\n", 0, match.start()) + 1
            links.append((destination, line))
    return links



def validate_readme(root: Path, errors: List[str]) -> None:
    path = root / "README.md"
    if not path.is_file():
        return
    text = read_utf8(path, errors)
    if text is None:
        return

    for profile_url in PROFILE_URLS:
        if profile_url not in text:
            add_error(errors, f"README.md: required HTTPS profile link is missing: {profile_url}")

    for destination, line in parse_readme_markup(text, errors):
        try:
            parsed = urlsplit(destination.strip())
        except ValueError as exc:
            add_error(errors, f"README.md:{line}: invalid asset link {destination!r}: {exc}")
            continue
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        if parsed.path.startswith("#"):
            continue

        relative_path = unquote(parsed.path).lstrip("/")
        candidate = (root / relative_path).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            add_error(errors, f"README.md:{line}: asset link escapes the repository: {destination!r}")
            continue
        if not candidate.is_file():
            add_error(errors, f"README.md:{line}: local asset link does not exist: {destination!r}")



def xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]



def validate_sitemap(root: Path, errors: List[str]) -> None:
    path = root / "sitemap.xml"
    if not path.is_file():
        return
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError) as exc:
        add_error(errors, f"sitemap.xml: could not parse XML: {exc}")
        return

    locations = [
        (element.text or "").strip()
        for element in tree.getroot().iter()
        if xml_local_name(element.tag) == "loc"
    ]
    if not locations:
        add_error(errors, "sitemap.xml: expected at least one <loc> element")
        return

    for location in locations:
        try:
            has_fragment = bool(urlsplit(location).fragment)
        except ValueError:
            has_fragment = True
        if has_fragment:
            add_error(errors, f"sitemap.xml: location must not contain a fragment: {location!r}")

    root_count = locations.count(CANONICAL_URL)
    if root_count != 1:
        add_error(
            errors,
            f"sitemap.xml: expected exactly one root location {CANONICAL_URL!r}; found {root_count}",
        )



def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="site root to validate (default: repository root)",
    )
    parser.add_argument(
        "--artifact",
        action="store_true",
        help="validate the exact public artifact allowlist instead of source files",
    )
    return parser.parse_args(argv)



def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.expanduser().resolve()
    errors: List[str] = []

    if args.artifact:
        validate_artifact_layout(root, errors)
    elif require_directory(root, errors):
        validate_required_files(root, errors)

    if not root.is_dir():
        print_validation_result(root, args.artifact, errors)
        return 1

    validate_html(root, errors)
    validate_png(root / "assets/og-image.png", errors)
    validate_sitemap(root, errors)
    validate_leakage(root, (Path("index.html"), Path("README.md")), errors)
    if not args.artifact:
        validate_readme(root, errors)

    print_validation_result(root, args.artifact, errors)
    return 1 if errors else 0



def print_validation_result(root: Path, artifact: bool, errors: Sequence[str]) -> None:
    mode = "artifact" if artifact else "source"
    if errors:
        print(f"Site validation failed ({mode}): {root}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return
    print(f"Site validation passed ({mode}): {root}")


if __name__ == "__main__":
    raise SystemExit(main())
