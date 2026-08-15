# Mission Frame

Context oriented DEGRADED-UNPARSEABLE (`map_orient.py`'s code-map-index parser finds no
citable anchor id in `map/INDEX.md`, though the file has grep-discoverable content).
Substitutes hash-pinned at the context step: `map/INDEX.md`,
`map/tests.test_spine_origin_isolation/INDEX.md`,
`.agent-work/tc1-windows-path-form/LAUNCH_ORDER.md`. This frame is shrunk: the run is a
single, precisely-scoped test-assertion fix the launch order (admiral-post-568) already
diagnoses down to the exact line, so full capability/decision anchor authoring would
restate the order rather than add planning value. Anchor-shaped tokens (`struct:`,
`capability:`, `decision:`, etc.) are deliberately omitted throughout, since this run's
context is DEGRADED and citing them would be citing a map that was never actually read.

## Intent
Make `tests/test_spine_origin_isolation.py::RefusesAGuardedVerbFromAForeignTree::test_the_refusal_names_both_trees_on_stderr`
pass on Windows CI without weakening what it proves (the refusal names both trees) and
without touching the refusal predicate's comparison logic or purity, per
`.agent-work/tc1-windows-path-form/LAUNCH_ORDER.md` ("The judgment call").

## Affected Capabilities (prose, DEGRADED — no anchor ids)
Only the test-side assertion of the worktree-identity refusal message in
`tests/test_spine_origin_isolation.py` (substitute: `map/tests.test_spine_origin_isolation/INDEX.md`).
`scripts/checklist_engine.py`'s `origin_worktree_refusal` predicate and its one call site
in `main()` are read-only reference for this run — confirmed correct, not touched.

## Structural Anchors (prose, DEGRADED)
- `tests/test_spine_origin_isolation.py`, class `RefusesAGuardedVerbFromAForeignTree`,
  method `test_the_refusal_names_both_trees_on_stderr` (line ~507-517) — the file this
  run owns.
- `scripts/checklist_engine.py`, function `origin_worktree_refusal` (~line 102-178) and
  its one call site in `main()` (~line 3439-3441) — read for verification only; NOT
  yours per the launch order's File Ownership.

## Governing Constraints / Assumptions
- The predicate's comparison (`os.path.normcase` on both `stored` and `cwd`) is
  separator-agnostic on Windows and identity on POSIX — verified directly against
  `scripts/checklist_engine.py:170-174` at the understand step, not taken on trust.
  Confirms the launch order's "not a bug" claim.
- `main()`'s call site feeds `cwd` from `git rev-parse --show-toplevel` output
  (`scripts/checklist_engine.py:3439-3441`), which is posix-form on Windows — confirms
  the launch order's diagnosis of why the cwd-side assertion broke.
- File ownership fence (LAUNCH_ORDER §"File Ownership"): only
  `tests/test_spine_origin_isolation.py`, and only if choosing (b),
  `scripts/checklist_engine.py::origin_worktree_refusal`'s rendering — never its
  comparison logic. `scripts/hooks/spine_rail.py`, `scripts/run_crew.py`, `.mcp.json`
  are explicitly not this run's.
- `test_it_is_pure` (in the same test file) must stay green and unmodified
  (LAUNCH_ORDER Pre-Ruling 1, "predicate-untouched").

## Decision Anchors & Decision Pressure
- Judgment call (a) vs (b) from LAUNCH_ORDER §"The judgment call": accept option (a) —
  update the test's cwd-side assertion to posix form (`self.foreign.as_posix()`), matching
  the stored side's existing `self.worktree.as_posix()` (line 516) and the order's own
  leaning. Rationale: the message is internally consistent (both halves posix on
  Windows) after the 2026-08-15 worktree-identity ruling switched the cwd source from
  `str(Path.cwd().resolve())` to git's toplevel output; (b) would add formatting work in
  a refusal path purely for cosmetic native-form display, and would touch
  `origin_worktree_refusal`'s rendering (higher blast radius: every future reader of that
  message) for a benefit (native separators in a refusal string) the launch order itself
  treats as secondary to internal consistency. This is a plan-time decision already
  authorized by the launch order's explicit "I lean (a)" plus Pre-Ruling framing; not
  reopened here as a fresh candidate.
  `@grade: settled/human · leans g1-implement · settle: n/a — ratified by LAUNCH_ORDER`

## Claims / Evidence Surfaces
- Claim: the fixed assertion holds on Windows AND POSIX by construction. Evidence: the
  cwd side of the refusal message is always literally `engine_cwd`, which is always
  `toplevel.stdout.strip()` from `git rev-parse --show-toplevel` — git emits posix-form
  path output on every platform including Windows (documented git behavior, not
  Windows-native backslash form), so `self.foreign.as_posix()` matches on Windows and
  `self.foreign.as_posix() == str(self.foreign)` already holds on POSIX (no separator
  difference there). No platform-conditional branching needed in the test.
- Claim: `test_it_is_pure` is unaffected — it tests the predicate function directly, not
  `main()`'s message construction, and this run does not touch the predicate.
- Re-confirm: full Linux suite cache-clean, matching the launch order's stated baseline
  (3010 passed, 6 skipped, 0 failed, 1136 subtests from this worktree).

## Map Confidence / Staleness / Disputes
- `map/INDEX.md` reads DEGRADED-UNPARSEABLE from `map_orient.py`'s own parser (no
  citable anchor id), despite having grep-discoverable, human-readable content —
  recorded as `unmapped` in the context step's orientation receipt. This is a tooling
  gap in `map_orient`/the code-map format for this skill-source repo, not something this
  ticket's one-assertion budget can or should fix. No plan alteration needed: the exact
  affected file and lines were located directly via `grep` and cross-checked against the
  launch order, which independently names the same file, class, and method.

## Out of Scope
- The refusal predicate's comparison logic and purity (`origin_worktree_refusal` itself)
  — confirmed correct, explicitly NOT this run's per LAUNCH_ORDER Pre-Ruling 1
  ("predicate-untouched").
- The worktree-identity ruling itself (LAUNCH_ORDER Pre-Ruling 2, "ruling-stands") — not reopened.
- `scripts/hooks/spine_rail.py`, `scripts/run_crew.py`, `.mcp.json` — owned by other open PRs.
- Design-it-twice plan-alternatives and a cold plan critic — **named untaken road**.
  Skipped because the fix is a single, already-fully-specified line (option (a), ratified
  by the launch order itself with explicit reasoning for (a) over (b)); generating
  parallel gate-plan candidates or a critic panel for a one-line, pre-decided test
  assertion would manufacture planning ceremony without a real alternative to weigh —
  the launch order's Budget section ("One assertion... if this grows past a handful of
  lines, stop and report") is itself the scope constraint that makes alternatives moot.
