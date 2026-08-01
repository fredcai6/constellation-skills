#!/usr/bin/env python
"""Fingerprint the GLOBAL constellation corpus — the copy that actually SERVES (#332).

PRE-B does NOT install a pinned corpus. Issue #332 established that `~/.claude/skills`
shadows any `<worktree>/.claude/skills` install: both copies register in `system/init`
(every constellation name appears twice) but the global one is what loads. So installing
a pin does not deliver it, and PRE-B measures the corpus AS ACTUALLY INSTALLED.

That makes the global corpus an uncontrolled input rather than a pinned one, so it has to
be WITNESSED instead: fingerprint before the first run and after the last. If the two
differ, runs from either side of the change are not poolable and the arm is compromised.

Method, stated so it is reproducible rather than trusted: sort the `constellation-*`
directories by name, concatenate each one's `SKILL.md` RAW BYTES in that order, sha256.
Raw bytes, not decoded text — a line-ending or encoding change is a corpus change and
decoding would hide it.

This covers the trigger surface and the skill bodies. It does NOT cover `references/`,
`templates/`, or `scripts/` under each skill; `--deep` adds those. The shallow digest is
the one the launch order quotes, so it is the primary and `--deep` is a second witness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

GLOBAL_SKILLS = Path.home() / ".claude" / "skills"


def _skill_dirs(root: Path) -> list[Path]:
    return sorted((d for d in root.iterdir() if d.is_dir() and d.name.startswith("constellation-")),
                  key=lambda p: p.name)


def fingerprint(root: Path = GLOBAL_SKILLS) -> dict:
    dirs = _skill_dirs(root)

    shallow = hashlib.sha256()
    per_skill: dict[str, str] = {}
    for d in dirs:
        raw = (d / "SKILL.md").read_bytes()
        shallow.update(raw)
        per_skill[d.name] = hashlib.sha256(raw).hexdigest()[:16]

    # Deep: every file under every constellation skill, path-relative so it is
    # install-path-invariant. __pycache__ excluded — it is generated, not corpus.
    deep = hashlib.sha256()
    deep_files = 0
    for d in dirs:
        for f in sorted(d.rglob("*"), key=lambda p: str(p.relative_to(root)).replace("\\", "/")):
            if not f.is_file() or "__pycache__" in f.parts or f.suffix == ".pyc":
                continue
            deep.update(str(f.relative_to(root)).replace("\\", "/").encode("utf-8"))
            deep.update(f.read_bytes())
            deep_files += 1

    marker = root / "CORPUS.json"
    marker_data = json.loads(marker.read_text(encoding="utf-8")) if marker.is_file() else None

    return {
        "taken_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "root": str(root),
        "constellation_skill_count": len(dirs),
        "skill_names": [d.name for d in dirs],
        "skillmd_concat_sha256": shallow.hexdigest(),
        "deep_tree_sha256": deep.hexdigest(),
        "deep_file_count": deep_files,
        "per_skill_skillmd_sha256_prefix": per_skill,
        "corpus_marker": marker_data,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--expect-shallow", default=None,
                   help="prefix the digest must start with; mismatch exits 2")
    args = p.parse_args()

    fp = fingerprint()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(fp, indent=2) + "\n", encoding="utf-8", newline="\n")

    print(f"constellation skills : {fp['constellation_skill_count']}")
    print(f"SKILL.md concat      : {fp['skillmd_concat_sha256']}")
    print(f"deep tree            : {fp['deep_tree_sha256']}  ({fp['deep_file_count']} files)")
    print(f"marker source_commit : {(fp['corpus_marker'] or {}).get('source_commit')}")
    print(f"written              : {args.out}")

    if args.expect_shallow and not fp["skillmd_concat_sha256"].startswith(args.expect_shallow):
        print(f"MISMATCH: expected shallow digest to start {args.expect_shallow}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
