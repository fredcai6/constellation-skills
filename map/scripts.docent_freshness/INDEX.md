# scripts.docent_freshness
scripts/docent_freshness.py, 193 lines, 5 holes

docent_freshness — deterministic staleness check for a docent explainer site.

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

    "<map-root-relative POSIX path>\0<file sha256 hex>\n"

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

imports stdlib: __future__.annotations, argparse, hashlib, pathlib.Path, re, sys, typing.Iterable
imported by: none found

```python
STAMP_META_NAME = 'docent-map-stamp'
_STAMP_RE = re.compile('<meta\\s+name=["\\\']' + re.escape(STAMP_META_NAME) + '["\\\']\\s+content=[...
```

- [_iter_source_files](_iter_source_files.md) function: Yield the source-map files that define the digest, in no particular order.
- [_file_sha256](_file_sha256.md) function: HOLE: no docstring
- [compute_stamp](compute_stamp.md) function: Return the canonical SHA-256 digest over the sorted source-map file set.
- [_resolve_site_html](_resolve_site_html.md) function: Return the HTML file to read the stamp from (site dir -> index.html).
- [read_embedded_stamp](read_embedded_stamp.md) function: Return the digest embedded in the site's HTML, or None if absent/missing.
- [_cmd_stamp](_cmd_stamp.md) function: HOLE: no docstring
- [_cmd_check](_cmd_check.md) function: HOLE: no docstring
- [build_parser](build_parser.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
