# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g4-review` (issue #104, constellation-curator)

## Result
`APPROVE`

## Handoff compliance
Yes. The handoff asked for `SKILL_SCRIPT_BUNDLES["curator"]`, `SKILL_REFERENCE_BUNDLES["curator"]`,
one `SKILL_INDEX.md` entry, and 3 per-skill install tests. `git diff --stat` shows exactly:
`SKILL_INDEX.md | 5 ++`, `scripts/install_constellation.py | 2 ++`,
`tests/test_install_constellation.py | 60 ++` — nothing else. Read line-by-line, this is precisely
the wiring described, no more.

## Scope drift
None. `git status --short` shows exactly the three named files, no untracked files. Confirmed with
`git diff --unified=0 scripts/install_constellation.py`: only two `+` lines exist in the whole file,
zero `-` lines — a pure addition, no other skill's `SKILL_SCRIPT_BUNDLES`/`SKILL_REFERENCE_BUNDLES`
entry was touched or reformatted.

## Evidence verdict
Reproduced independently, not trusted from the report:
- `py -m pytest tests/test_install_constellation.py -v -k curator` → 3 passed, 2 subtests passed.
- `py -m pytest tests/ -q` → 467 passed, 2 skipped, 152 subtests passed (matches the claimed count).
- `py -m pytest tests/ -k test_bundled_scripts_carry_their_sibling_imports` → 1 passed (curator's
  script is stdlib-only, no sibling-import obligation, criterion 5 satisfied).
- Test mode `evidence-only` fits the suggested "simple bounded" tier; each new test is individually
  falsifiable (see falsification below), which is stronger than a bare green claim.

## Code/doc quality
Minimal, matches surrounding conventions exactly: dict key is the source-dir name (`"curator"`,
consistent with `"explorer"`, `"prototyper"`, etc.), `SKILL_INDEX.md` entry uses the same
`## <Name>` / `Path:` / description format as every preceding entry. No speculative abstraction, no
new bucket constant, no new `global-*.md` filename anywhere in the diff or git status.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the three new tests exercise exactly the claimed
  behavior (script bundling, everyone-tier reference bucket, install/discovery), and I reproduced
  all three green plus the full suite green.
- **Constraints not violated:** Yes — no new `global-*.md` filename was introduced (checked `git
  diff`/`git status` repo-wide for any `global*` path), no new bucket constant, `skills/curator/
  SKILL.md` and `scripts/curate_corpus.py` were not touched by this diff.
- **Notes match the diff:** Yes — the implementer's Map Impact notes (2 dict entries, 1 index entry,
  3 test methods; curator ships script + everyone-tier refs same as interrogator/lessons-auditor)
  match the diff exactly; nothing overstated or missing.
- **Decision candidates surfaced:** N/A — DC1 (curator carries `_GLOBAL_EVERYONE`) was already
  ratified upstream; correctly treated as implemented-not-revisited, no new authority needed.
- **Durable context routed:** Yes — the pre-existing `SKILL_INDEX.md` gap (docent/explorer/
  prototyper missing entries) is routed as a triage candidate rather than silently dropped or
  fixed out-of-scope. I independently verified the gap via `grep -n '^##' SKILL_INDEX.md` against
  the discovered-skill set and confirmed it predates this change (this diff only adds curator).

## Reconciliation check
No architecture-baseline concerns. This is additive, mechanical wiring following an established
per-skill dict pattern; no reconciliation needed beyond the already-flagged triage candidate.

## Falsification performed (criterion 4)
Reproduced the implementer's falsification myself, independent of their report:
1. Edited `scripts/install_constellation.py`, removing the line
   `"curator": ("curate_corpus.py",),` from `SKILL_SCRIPT_BUNDLES`.
2. Ran `py -m pytest tests/test_install_constellation.py -v -k curator` →
   `test_curator_script_bundle_lands_in_installed_skill` FAILED
   (`AssertionError: False is not true`); the other 2 curator tests still passed (as expected —
   they depend on different dict entries).
3. Restored the exact line via Edit.
4. Verified restore: `git diff scripts/install_constellation.py` matches the original two-line
   addition exactly; `git status --short` shows the same three files as before the falsification
   (`SKILL_INDEX.md`, `scripts/install_constellation.py`, `tests/test_install_constellation.py`),
   no leftover diff, no untracked files.
5. Re-ran `py -m pytest tests/test_install_constellation.py -v -k curator` → 3 passed, 2 subtests
   passed again.

Tree confirmed clean after restore — round-trip left no trace.

## Blockers
- none

## Out-of-scope observations
- `SKILL_INDEX.md` is missing entries for `docent`, `explorer`, and `prototyper` — pre-existing gap,
  not introduced by this gate. Independently confirmed via `grep -n '^##' SKILL_INDEX.md`. Flagged
  as triage candidate `tc1` in the survey checklist (`.agent-work/issue-104/g4-review/review.json`);
  worth a follow-up issue to backfill the index against the full discovered-skill set.

## Workflow Feedback
- **Handoff gaps:** none — the handoff named exact expected dict values, the exact reused constant
  (`_GLOBAL_EVERYONE`), and the exact falsification method (delete a dict line, observe red,
  restore). Nothing was ambiguous or missing.
- **Context rediscovered:** none beyond what the handoff and implementer result already carried —
  the implementer's report was thorough enough that I only needed to independently re-run/re-derive
  each claim rather than dig anything up myself.
- **Instructions improvised around:** the checklist_engine survey template's `r4-quality` item asks
  to "append a check per rule," which I interpreted as one umbrella pass/fail referencing the
  already-recorded per-criterion checks (r6-r12) rather than re-deriving separate constraint rules —
  the seven close criteria from the handoff already served as the per-rule breakdown, so a second,
  parallel decomposition would have been redundant ceremony.
- **What would have made this easier:** nothing concrete — the handoff was complete and the
  implementer's result gave exact line numbers/diffs, making reproduction fast and unambiguous.

## Return status
`complete`
