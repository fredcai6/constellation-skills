# Review Result

## Assigned Gate
`g2` (issue #328/#422, workstream D of epic #418)

## Result
`APPROVE`

## Handoff compliance
All 5 close criteria independently reproduced, not trusted from the report:
1. `record()` refuses `result='pass'` when a `command`-kind postcondition fails; never blocks `result='fail'`; items with no command postcondition are byte-for-byte unaffected — confirmed by reading the diff, `tests/test_checklist_engine.py` re-run (330 passed, 24 subtests, unchanged behavior).
2. `zc-consolidate`/`r6-fowler` each carry exactly one new command postcondition; both templates valid JSON; no other item touched — confirmed by diff (single-item hunk per template) and re-validated JSON parse.
3. `tests/test_record_postcondition_wiring.py` passes (10/10) AND the deliberate-breakage claim was independently re-proven via `git stash push -- scripts/checklist_engine.py` → re-run (exactly the 3 named tests fail with `AssertionError: EngineError not raised`, 7 others green) → `git stash pop` (diff --stat back to 22 insertions/2 deletions) → re-run (10/10 passed).
4. **Fence check**: full-file diff shows only 2 hunks total (record() at line 1728, CLI dispatch at 2477/2497). Independently confirmed a second way — extracted `render_human`, `_why_suffix`, `current()` from HEAD and the working tree by function boundary and diffed them directly: all three **byte-identical**.
5. Full suite green, independently re-run: `1633 passed, 2 skipped, 549 subtests passed` — exact match to the implementer's reported numbers.

## Scope drift
None. `git status --porcelain` shows exactly the allowed set: `scripts/checklist_engine.py` (record() + CLI dispatch only), both templates (one item each), the new test file. Both specific exclusions (`scripts/verify_interrogation.py`, `scripts/verify_fowler_pass.py`) confirmed byte-identical via `git diff --stat` (empty). Issue #315 (cwd inheritance) correctly left unfixed, documented in Assumptions rather than silently expanded.

## Evidence verdict
Every required piece of evidence independently reproduced at its source: JSON validity, targeted test (10/10), regression floor (330 passed/24 subtests), full suite (1633 passed/2 skipped/549 subtests), and the git-stash red/green deliberate-breakage demonstration. Test mode is test-after (wiring an existing rail into the engine); the deliberate-breakage tests are the acceptance criteria, and both were proven to fail without the fix.

One minor non-blocking discrepancy: re-running `grep -rn "interrogation-record-path\|fowler-pass-record-path" --include=*.json --include=*.md .` today returns **6** distinct files, not the reported 5 — the implementer's own `g2-implement-result.md` now also matches, because its Evidence section quotes the wired command strings in prose. This is self-referential growth from writing the evidence doc after running the grep, not an unexpected third-party reference; the substantive claim (only the two committed templates are wired, no stray reference) still holds.

## Code/doc quality
- Constraint "reuses `_check_condition`, no reimplementation" — confirmed: `record()`'s new line calls `_check_condition(c, t, base_dir)` verbatim, identical to `advance()`'s two call sites.
- Constraint "null/artifact-kind postconditions remain unevaluated by `record()`, commented at the site" — confirmed: the filter (`_condition_kind(c) == "command"`) structurally excludes null/artifact kinds, and a 7-line comment names the limit explicitly, citing `decision:survey-record-check-scope`.
- Constraint "deliberate-breakage fixtures are real, unmocked" — confirmed: no `mock`/`monkeypatch`/`patch(` anywhere in the new test file; both breakage tests write real JSON to `tempfile.TemporaryDirectory` and invoke the real verify scripts as a subprocess through `record()`'s real command-check path.
- Fowler pass: ran the required baseline pass (`.agent-work/issue-422-wire-invariants/g2-review/fowler-pass.json`, verified by `verify_fowler_pass.py`, exit 0, 12/12 smells visited). 11 absent, 1 overridden: **duplicated-code** — `record()`'s new unmet-computation/raise-`EngineError` block structurally echoes `advance()`'s existing one. Subordinated to `references/global-crew.md`'s minimal-change/no-speculative-abstraction doctrine: the handoff explicitly required mirroring `advance()`'s exact pattern, and extracting a shared helper for exactly 2 call sites in a bounded wiring gate would itself be premature abstraction. No blocking code-smell findings.

## Map impact verdict
- **Evidence supports claimed change:** yes — the capability change ("survey `record()`'s `pass` result on a command-backed item is provably checked") is backed by the red/green demonstration, independently reproduced.
- **Constraints not violated:** yes — the inbound constraint ("all 7 existing `kind: command` examples live on GATED spines only") is now accurately flagged stale by the implementer (two SURVEY items now carry command postconditions), correctly routed as a Cartographer reconcile note rather than silently left wrong.
- **Notes match the diff:** yes — structural anchors (`record()` ~28 lines was 9, CLI dispatch) match the 2-hunk diff exactly; `advance()`/`_check_condition` correctly noted as read-not-modified.
- **Decision candidates surfaced:** `decision:survey-record-check-scope` (settled/human, not this gate's to unsettle) implemented exactly as graded — command-kind only, null/artifact explicitly out and commented, not silently generalized. No new decision needed authority beyond the implementer's latitude.
- **Durable context routed:** yes — the Constraints-anchor staleness is flagged for Cartographer reconcile; one triage candidate (stale `_next_verbs` comment) routed forward rather than fixed silently (it sits outside this gate's allowed scope) or dropped.

## Reconciliation check
No divergence from recorded architecture beyond the already-flagged, correctly-routed Constraints-anchor staleness (two SURVEY items now carry `command`-kind postconditions, where the anchor said only GATED spines did). No other concerns.

## Blockers
- none

## Out-of-scope observations
- **tc1** (flagged to the survey's `triage_candidates`): `scripts/checklist_engine.py`'s `_next_verbs` (~line 1536–1538) carries a comment stating `record()` "carries no precondition/postcondition gate at all" and is "ALWAYS legal from in-progress" — now partially stale, since `record()` does gate `command`-kind postconditions on `result == 'pass'` as of this change. No functional bug (the `record` verb hint is still always offered; the refusal happens inside `record()` itself, not by hint-suppression), but the comment's premise is inaccurate and should be updated. Independently confirmed by reading the function. Outside this gate's allowed scope (`record()`/CLI dispatch only) and outside the three fenced rendering functions — correctly left untouched by the implementer and flagged rather than fixed.
- Minor evidence-count discrepancy in the wiring grep (5 vs 6 files) — see Evidence verdict above. Not a defect, just worth noting for anyone re-running that exact command later.

## Workflow Feedback
- **Handoff gaps:** none — the exact fence boundary (three named functions), the exact deliberate-breakage reproduction recipe, the `python` vs `py` pytest gotcha, and the required constraint list were all precise enough to drive the review without guessing.
- **Context rediscovered:** none beyond the ordinary — the g1-review precedent (`.agent-work/issue-422-wire-invariants/g1-review/review.json`) was a useful pattern to confirm the append-siblings-for-per-rule-checks convention and the `session_id` naming convention (`g{n}-review-cmdr{issue}`), but this was a "had to look," not a gap.
- **Instructions improvised around:** none.
- **What would have made this easier:** none concrete. One small note: the handoff's evidence-reproduction instruction for the wiring grep did not warn that the grep's own target string set would grow to include the implementer's own result doc once it quotes the wired command — a trivial, self-resolving discrepancy, but a future handoff author could note that a grep over `.agent-work/` artifacts is not a stable count across time.

## Return status
`complete`
