# scripts.check_skill_freshness
scripts/check_skill_freshness.py, 196 lines, 5 holes

Report template drift for a project against its installed-skill baseline.

Three-way status per template:
  baseline (pristine copy at install)  vs  upstream (installed skill source)
  baseline                             vs  local (project working copy)

Statuses: up-to-date | upstream-changed | project-customized | both-changed
(reconcile!) | upstream-removed. The script never merges; conflicts are for a
human (or Charter) to adjudicate — `git merge-file local baseline upstream` is
the suggested tool. --update-baseline promotes the current upstream to the new
baseline AFTER reconciliation.

imports stdlib: __future__.annotations, argparse, hashlib, json, os, pathlib.Path, shutil, sys
imported by: none found

- [_utf8_stdio](_utf8_stdio.md) function: Per field feedback: don't make every call site set PYTHONIOENCODING.
- [FreshnessError](FreshnessError.md) class: HOLE: no docstring
- [_platform_interpreter](_platform_interpreter.md) function: Mirror of install_constellation._platform_interpreter: `py` on Windows,
- [_hash](_hash.md) function: Line-ending-insensitive content hash (CRLF checkouts vs LF writes).
- [_normalized_hash](_normalized_hash.md) function: Content hash after resolving <skill-dir> / <name-skill-dir> tokens to the
- [_load_manifest](_load_manifest.md) function: HOLE: no docstring
- [check](check.md) function: HOLE: no docstring
- [update_baseline](update_baseline.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
