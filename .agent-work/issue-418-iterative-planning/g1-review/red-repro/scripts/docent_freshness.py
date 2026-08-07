#!/usr/bin/env python3
"""docent_freshness — deterministic staleness check for a docent explainer site.

A docent explainer site is generated from Cartographer map truth
(`docs/architecture/`). A *stale* pretty site is worse than none, so the site
embeds a stamp: a SHA-256 digest over the exact source-map file set it was built
from. This tool computes that stamp and checks a published site against the live
source, so staleness is proven by an exit code, never eyeballed from prose.

Stdlib-only, deterministic, cross-platform (no shell `sha256sum`).

Subcommands
-----------
  stamp --map-root <dir>
      Print the current source-map digest (the generator embeds this in the site).

  check <site> --map-root <dir>
      Read the digest embedded in <site> (a directory containing index.html, or an
      HTML file directly), recompute it from <map-root>, print `fresh` or `stale`,
      and exit 0 when they match, nonzero when they diverge (or on error).

Canonical digest serialization (documented so it is reproducible)
-----------------------------------------------------------------
The source-map file set is every file under <map-root> in these groups:
  - `index.md` (at the map root)
  - everything under `packets/`   (recursively)
  - everything under `overlays/`  (recursively)
  - everything under `decisions/` (recursively)
  - `generated/map.json`          (only when it exists)
For each file we form the pair line

    "<map-root-relative POSIX path>\\0<file sha256 hex>\\n"

sort the pair lines by path (ascending, byte order), concatenate them, UTF-8
encode, and take the SHA-256 of the whole. Paths are made relative to the map
root and normalized to POSIX separators so the digest is identical regardless of
the map's absolute location or the host OS.

Embedding convention
--------------------
The generator writes the digest into the site's `index.html` as

    <meta name="docent-map-stamp" content="<64-hex-digest>">

An HTML comment marker `<!-- docent-map-stamp: <digest> -->` is also accepted as
a fallback so a generator that cannot place a <meta> still has a home for it.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Iterable


STAMP_META_NAME = "docent-map-stamp"
# Matches either the canonical <meta> tag or the comment fallback; captures 64 hex.
_STAMP_RE = re.compile(
    r'<meta\s+name=["\']' + re.escape(STAMP_META_NAME) + r'["\']\s+content=["\']([0-9a-fA-F]{64})["\']'
    r'|<!--\s*' + re.escape(STAMP_META_NAME) + r'\s*:\s*([0-9a-fA-F]{64})\s*-->'
)


def _iter_source_files(map_root: Path) -> Iterable[Path]:
    """Yield the source-map files that define the digest, in no particular order.

    Deterministic ordering is imposed later by sorting on the relative path, so
    the traversal order here does not matter."""
    index = map_root / "index.md"
    if index.is_file():
        yield index
    for group in ("packets", "overlays", "decisions"):
        base = map_root / group
        if base.is_dir():
            for path in base.rglob("*"):
                if path.is_file():
                    yield path
    generated = map_root / "generated" / "map.json"
    if generated.is_file():
        yield generated


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_stamp(map_root: Path) -> str:
    """Return the canonical SHA-256 digest over the sorted source-map file set."""
    map_root = Path(map_root)
    pairs: list[str] = []
    for path in _iter_source_files(map_root):
        rel = path.relative_to(map_root).as_posix()
        pairs.append(f"{rel}\0{_file_sha256(path)}\n")
    pairs.sort()
    combined = "".join(pairs).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


def _resolve_site_html(site: Path) -> Path:
    """Return the HTML file to read the stamp from (site dir -> index.html)."""
    site = Path(site)
    if site.is_dir():
        return site / "index.html"
    return site


def read_embedded_stamp(site: Path) -> str | None:
    """Return the digest embedded in the site's HTML, or None if absent/missing."""
    html_path = _resolve_site_html(site)
    if not html_path.is_file():
        return None
    text = html_path.read_text(encoding="utf-8", errors="replace")
    match = _STAMP_RE.search(text)
    if not match:
        return None
    return (match.group(1) or match.group(2)).lower()


def _cmd_stamp(args: argparse.Namespace) -> int:
    map_root = Path(args.map_root)
    if not map_root.is_dir():
        print(f"error: map-root is not a directory: {map_root}", file=sys.stderr)
        return 2
    print(compute_stamp(map_root))
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    map_root = Path(args.map_root)
    if not map_root.is_dir():
        print(f"error: map-root is not a directory: {map_root}", file=sys.stderr)
        return 2

    site = Path(args.site)
    html_path = _resolve_site_html(site)
    if not html_path.is_file():
        print(f"error: no site HTML to check at: {html_path}", file=sys.stderr)
        return 2

    embedded = read_embedded_stamp(site)
    if embedded is None:
        print(
            f"error: no docent-map-stamp embedded in {html_path}; cannot verify freshness",
            file=sys.stderr,
        )
        return 2

    current = compute_stamp(map_root)
    if embedded == current:
        print(f"fresh: site stamp matches map source ({current})")
        return 0
    print(
        "stale: site was generated from a different map source\n"
        f"  embedded (site): {embedded}\n"
        f"  current  (map):  {current}"
    )
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docent_freshness",
        description="Compute and verify the freshness stamp of a docent explainer site.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_stamp = sub.add_parser("stamp", help="print the current source-map digest")
    p_stamp.add_argument("--map-root", required=True, help="the docs/architecture map root")
    p_stamp.set_defaults(func=_cmd_stamp)

    p_check = sub.add_parser("check", help="check a site's embedded stamp against the map")
    p_check.add_argument("site", help="the explainer site dir (with index.html) or an HTML file")
    p_check.add_argument("--map-root", required=True, help="the docs/architecture map root")
    p_check.set_defaults(func=_cmd_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
