# Verification — g3 rework 2

Every number below re-measured at this working tree over `HEAD = b9709cfe`,
whose `scripts/hooks/spine_rail.py` is byte-identical to `6bba3fd2` (confirmed
by `git diff` against HEAD before I edited it).

## Suite

```
3187 passed, 5 skipped, 1208 subtests passed in 128.06s   (exit 0)
```

`__pycache__` cleared repo-wide first;
`SPINE_FILE` / `SPINE_SESSION` / `SPINE_PARENT` / `CREW_SCRATCH_DIR` scrubbed.

Failure distribution derived mechanically even though empty:
`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c` → **0 lines**.

**Arithmetic against the diff.** Floor 3183 → 3187 = **+4**, which is exactly
the four test methods added. Subtests 1204 → 1208 = **+4** = 2 arms
(`..._does_not_change_what_the_next_stop_is_told`) + 2 rows
(`..._withheld_only_when_the_session_owns_nothing_visible`). No test was
deleted; one pre-existing test was rewritten in place (below).

One intermediate red is on the record and is not a defect:
`tests/test_code_map.py::MapTreeFreshnessTests` failed on the first post-change
run because `map/INDEX.md` had not been regenerated yet. Regenerated with
`py -m scripts.code_map build` (never hand-edited, #544) and green on the rerun.

## The Stop path did not move

The pinned three-arm differential
(`crew-handoffs/g3-implement/m4_differential.py`, rework 1's harness, run
unmodified) exits 0 and its arm guard still accepts.

To compare rework 1 against this tree honestly I ran the **same harness twice**
with only its AFTER arm swapped — once with `6bba3fd2`'s hook in the working
tree, once with mine — and diffed:

- **all 13 Stop rows (sections 1–4): IDENTICAL.**
- **S9–S12 (SessionStart selection): IDENTICAL.** Expected: every one of those
  fixtures places its spines outside the scan's glob, which is precisely why
  none of them could see B4.

The swapped hook was restored and `cmp` confirms the working copy is
byte-identical to what I had before the swap.

## Rework 1's approved behaviour is unchanged

- Selection is still ownership-based at both sites (S9–S12 unmoved; `_own_entries`
  still the single shared comparison, still exactly 2 call sites).
- The differential's guard still refuses every degenerate direction — it is
  unmodified and its arm pins are untouched.
- `_entry_mid_flight_view` and `decide_stop` are **not edited at all** in this
  rework; the whole diff to production code is inside `decide_session_start`.
- `_foreign_worktree` stays deleted (`test_foreign_worktree_is_gone_and_stays_gone`).
- Nudges still keyed by `sid` alone — untouched.

## Import block

Unchanged and stdlib-only, printed by the differential's own final section:

```
['import errno', 'import json', 'import os', 'import re', 'import shlex',
 'import subprocess', 'import sys', 'import tempfile', 'import time',
 'from datetime import datetime, timezone', 'from pathlib import Path']
identical: True
```

## Fences

- `tests/test_worktree_derivation.py` — `git diff --name-only 999b7663..HEAD`
  returns **0 lines** for it, and it is clean in the working tree. Unedited
  across the whole gate, and green.
- Files changed by this rework: `scripts/hooks/spine_rail.py`,
  `tests/test_spine_rail.py`, `map/INDEX.md` (regenerated). Nothing else.
- `map/INDEX.md` arithmetic: `tests` 4850 → **4855** = 4 new test methods + 1
  new helper (`_in_tree_crew_only`); `tests.test_spine_rail` 208 → **213**, the
  same +5. `scripts` **unchanged at 1225** — this rework adds no symbol to the
  hook, only a local name (`owned`) and a condition.

## Windows

One line, as the handoff predicted: **the change involves no path comparison at
all.** It reads the truthiness of `sid_bindings` and of `_own_entries`' result —
a dict and a list — and `normcase` being the identity function on this Linux
host cannot affect either. The pre-existing constructed case expectation in
`test_ownership_no_longer_folds_case_or_separators` is untouched and green.
