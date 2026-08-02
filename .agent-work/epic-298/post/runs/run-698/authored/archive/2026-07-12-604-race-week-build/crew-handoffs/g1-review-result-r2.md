# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` (re-run after g1-implement rework, attempt 2 — issue #604, race-week staged
pipeline, Candidate C, gate G1)

## Result
`APPROVE`

## Handoff compliance
All Close Criteria independently re-verified true, using my own live reproduction, not the
implementer's pasted transcript:

- **Fix holds.** Ran, live, in a fresh Python process against the current worktree
  (`C:/Programs/f1Brainz/.claude/worktrees/604-build`):
  ```
  >>> rws.explain_stage('some/stem', None)
  {'status': 'stub', 'path': 'C:\\Users\\fredc\\AppData\\Local\\Temp\\race_week_explainer.STUB.md',
   'reason': "TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'"}
  >>> rws.explain_stage('some/stem', '')
  {'status': 'stub', 'path': 'C:\\Users\\fredc\\AppData\\Local\\Temp\\race_week_explainer.STUB.md',
   'reason': "ValueError: WindowsPath('.') has an empty name"}
  ```
  Both return cleanly — a `dict` with a `status` field, no exception propagates. Also confirmed
  the actual side effect: `race_week_explainer.STUB.md` was physically written at
  `tempfile.gettempdir()` with the expected reason text (`ls`/`cat` on the real file, not the
  reported path string).
- **Fallback stub path sanity.** `tempfile.gettempdir()` resolves to
  `C:\Users\fredc\AppData\Local\Temp` (checked live) — a per-user OS temp dir, writable, never
  the repo/cwd. Reasonable choice; not silently broken.
- **The new tests genuinely exercise the failure mode, not just superficially named.** Went
  beyond reading the test bodies: temporarily reverted `explain_stage` in the worktree to the
  exact pre-fix shape (`Path(...)`/`with_name(...)` moved back before the `try:` block,
  restoring the original bug), re-ran only `test_explain_stage_none_explainer_path_does_not_raise`
  and `test_explain_stage_empty_string_explainer_path_does_not_raise`, and confirmed **both fail**
  with the identical uncaught `TypeError`/`ValueError` the original BLOCK finding reported. This
  proves the tests would have caught the original bug — they are not vacuous. Restored the fixed
  file and re-ran the full suite to confirm 33/33 green again before moving on.
- **Full test suite** (`tests/unit/scripts/test_race_week_stages.py`) — re-ran myself, twice
  (once standalone, once after the revert-and-restore probe): **33 passed in 0.20s** both times,
  same test names/order as the implementer's pasted output (31 original + 2 new).
- **`py -m src.utils.simplification_limits --paths scripts/race_week_stages.py`** — re-ran myself:
  `PASS (1 files checked)`.

## Scope drift
None beyond what was already sanctioned. `git status --porcelain` in the worktree (run by me)
shows exactly the two sanctioned untracked additions: `scripts/race_week_stages.py`,
`tests/unit/scripts/test_race_week_stages.py`. No `scripts/race_week.py`, no `src/` changes.

Read the full current `scripts/race_week_stages.py` (319 lines) and confirmed
`discover_sessions_stage`, `predict_stage`, `optimize_stage`, checkpoint I/O helpers,
`compute_stage_inputs_hash`, `should_skip_stage` structurally match the exact quotes/line-behavior
the first review confirmed (`db_path=db_path` verbatim at line 187, no `or` fallback;
`VALID_LANES` check raises before `generate_report` is called; `generate_report` called exactly
once, `write_beam_search_report` never imported/called directly). Only `explain_stage`'s body
changed (`Path`/`with_name` construction moved inside `try`, `stub_path: Path | None = None` init
+ tempdir fallback) plus one new top-level `import tempfile` — matches the implementer's claimed
diff shape exactly.

## Evidence verdict
Evidence is solid and independently reproduced, including the side-effect (stub file on disk) and
the negative-control probe (tests genuinely fail pre-fix). The implementer's before/after repro,
33/33 test run, and `simplification_limits` PASS all check out live.

## Code/doc quality
Fix is minimal and correctly shaped: moving the two lines inside `try:` catches the construction
failure the same way as a copy failure, and the `stub_path: Path | None = None` + fixed-tempdir
fallback correctly handles the case where `stub_path` can't be *derived* from a broken
`explainer_path`. No speculative abstraction added.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the implementer's Map Impact note calls this a
  "trivial local edit ... no structural, capability, constraint, or decision impact beyond the bug
  fix itself," and that holds on independent inspection: the fix is confined to `explain_stage`'s
  internal exception-handling shape, no seam/interface signature changed.
- **Constraints not violated:** Re-verified live (not just re-read): `predict_stage`'s source has
  zero `db_path or ...` fallback occurrences (`inspect.getsource` scan) — db-path threading
  constraint intact. `hasattr(rws, 'write_beam_search_report')` is `False` — no-double-write
  constraint intact. Both are structurally unreachable from `explain_stage`'s diff surface.
- **Notes match the diff:** Yes.
- **Decision candidates surfaced:** N/A — no new architectural decision required.
- **Durable context routed:** N/A for this rework pass — the one durable item from the first
  review (`docs/design/race_week_seam.md` stale `best_max` claim) was already filed as Triage
  candidate `tc1` in the first review's survey (`.agent-work/604-race-week-build/g1-review/review.json`)
  and is unaffected by this rework.

## Reconciliation check
No architecture-significant divergence. Confirmed against `execute.json`'s `g1-implement` anchors
(unchanged by this rework, per the handoff). See Out-of-scope observations for one minor,
non-blocking worktree hygiene item.

## Blockers
None.

## Out-of-scope observations
- An untracked `out/04_explainer.STUB.md` exists in the worktree, dated before this review
  session — appears to be a stray artifact from an earlier manual/dev run using a relative
  `explainer_path` (predates the tempdir-fallback fix, or a dev probe that wrote relative to cwd).
  Not one of the two sanctioned files, not written by anything in this review session, and not a
  scope violation of this gate. Worth a glance/cleanup before the branch is committed so it
  doesn't ride along, same category as the previously-flagged `data/f1_data_2026.db`
  modified-binary item (still present, unchanged, already flagged in the first review).
- The doc-staleness Triage candidate (`tc1`, `docs/design/race_week_seam.md:26,218` stale
  `best_max` claim) from the first review's survey still stands; not re-litigated here since it's
  unaffected by the `explain_stage`-only rework.

## Workflow Feedback
Mandatory section.

- **Handoff gaps:** None — the rework handoff's Close Criteria gave an exact, falsifiable
  reproduction target (`explain_stage(<valid stem>, None)` / `""`) and an exact thing to check
  for the fallback path (`tempfile.gettempdir()` resolution), which made independent
  re-verification fast and unambiguous.
- **Context rediscovered:** None — every cited seam/line matched source on re-read; the
  implementer's own note about line numbers drifting by one (288-289 → 289-290) between the
  original handoff and the checked-out worktree state was accurate and harmless, and I found the
  same drift independently before reading their note.
- **Instructions improvised around:** None. One technique I used beyond the letter of the
  handoff, worth naming for future reviewer handoffs of this shape: I didn't just re-run the new
  tests against the fixed code (which only proves they pass, not that they'd have caught the
  bug) — I temporarily reverted the function to the pre-fix shape and re-ran just the two new
  tests to confirm they fail with the original exceptions, then restored the fix. This is a
  stronger form of "confirm the new tests actually exercise the failure mode" than reading test
  bodies alone, and it's the kind of check a rework re-review handoff could name explicitly next
  time (it fits naturally into this gate's Task Statement, which already asked for exactly this,
  just without prescribing the revert-and-reprove technique).
- **What would have made this easier:** None — the handoff was tightly scoped and gave a clear,
  reproducible target; nothing to improve here.

## Return status
`complete`
