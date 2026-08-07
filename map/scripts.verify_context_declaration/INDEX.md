# scripts.verify_context_declaration
scripts/verify_context_declaration.py, 207 lines, 1 holes

Lint: every declared `context_refs` path must appear verbatim in its own

task's `imperative` prose.

`scripts/context_manifest.py` (the authority on the `context_refs` shape) is
committed and approved, and its module docstring explains the design: a
declaration entry is `{"root", "path", "required"}`, and the task's
`imperative` prose is deliberately kept alongside it rather than replaced,
because the prose carries rules a path list cannot express -- e.g. the
COMMANDER_SPINE `context` step's substitute-and-record rule, and "a missing
engine-config is a sanctioned degradation, do NOT create the overlay file."

This script is the mechanical guard that keeps the two from drifting apart:
for every task that declares `context_refs`, every declared `path` string
must occur verbatim inside that same task's `imperative` string, as a whole
path token -- a match is not accepted when it is merely a suffix of a longer,
different path in the prose (see `_appears_at_path_boundary`).

**Direction, stated honestly.** This catches exactly one failure shape: the
declaration naming a path its own prose never mentions -- a declaration that
has been retargeted, mistyped, or extended past the prose that justifies it.
It CANNOT catch the reverse -- a path quietly dropped from `context_refs`
while the prose still names it (the declaration silently *narrowing away*
from what the prose describes) -- because the imperative is free-form prose,
not a parseable list, and there is no reliable way to extract "the paths this
sentence claims to read" from it. The declaration is authoritative; the prose
is the human-readable explanation of it. This lint does not claim to
guarantee agreement in both directions: it only guarantees that no declared
path points somewhere its own prose is silent about.

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, re, sys
imported by: none found

```python
DECLARATION_KEY = 'context_refs'
DEFAULT_GLOB = 'skills/*/templates/*.json'
_PATH_CHAR = re.compile('[A-Za-z0-9_./\\\\-]')
_TRAILING_CONTINUATION_CHAR = re.compile('[A-Za-z0-9_/\\\\-]')
```

- [_bounded_after](_bounded_after.md) function: True when nothing immediately after `prose[:end]` continues the path
- [_appears_at_path_boundary](_appears_at_path_boundary.md) function: True when `path` occurs in `prose` as a whole path token, not merely as
- [_is_checklist](_is_checklist.md) function: True for anything shaped like a checklist (`gated` or `survey`) this
- [offenders_in_task](offenders_in_task.md) function: Declared paths in `task` that do not appear verbatim in its own
- [check_checklist](check_checklist.md) function: One human-readable problem string per (task, offending path). Empty
- [discover_templates](discover_templates.md) function: Every real, committed checklist template under `root` -- never sorted
- [main](main.md) function: HOLE: no docstring
