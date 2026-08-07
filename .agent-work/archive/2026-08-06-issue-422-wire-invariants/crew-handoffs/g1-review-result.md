# Review Result

## Assigned Gate
`g1` (issue #329/#422, workstream D of epic #418)

## Result
`APPROVE`

## Handoff compliance
All four close criteria met and independently reproduced (not just read from the implementer's report):

- `COMMANDER_SPINE.template.json`'s `init` gate carries a new `c0` precondition whose `check.command` is `python scripts/verify_worktree_isolation.py --here <repo-root>` — confirmed by diff; valid JSON re-validated; no other gate touched.
- `scripts/verify_worktree_precondition_coverage.py` exists, exits 0 against the real tree (`worktree-precondition coverage OK: 1 worktree-entering template(s) checked`), and its membership list (`WORKTREE_ENTERING_GATES`) plus rationale are documented in the module docstring.
- `tests/test_worktree_precondition_wiring.py` exists and passes (`2 passed`). I independently re-ran the deliberate-breakage claim myself rather than trusting the report: `git stash push --quiet -- skills/commander/templates/COMMANDER_SPINE.template.json`, re-ran the coverage script (FAILED, naming `init` and `COMMANDER_SPINE.template.json`) and the test suite (`EnumerationDeliberateBreakage` failed with `AssertionError: real template unexpectedly missing the precondition before stripping` — the identical failure text the implementer reported), then `git stash pop --quiet` and confirmed `git diff --stat` matched the pre-stash state exactly (`3 insertions(+), 1 deletion(-)`) and the tests passed again.
- Full suite green: `python -m pytest tests/ -q` → `1623 passed, 2 skipped, 549 subtests passed` — matches the implementer's reported numbers exactly, independently re-run (not copied).

## Scope drift
None. `git diff --stat` shows exactly one modified file (`COMMANDER_SPINE.template.json`, 3 insertions/1 deletion, only the `init` gate's `preconditions` array) plus the two new files named in Allowed Scope. Both Specific Exclusions confirmed untouched: `git diff scripts/checklist_engine.py` and `git diff scripts/verify_worktree_isolation.py` both show nothing. No other gate in the template touched. No PreToolUse-hook code anywhere in the diff.

## Evidence verdict
Test-after mode is satisfied. Every piece of required evidence was independently reproduced: JSON validity, coverage-script run (stated count), targeted test run, full suite run, the `grep -rln verify_worktree_isolation skills/*/templates/*.json` call-site check (exactly one match), the `grep -rn verify_worktree_precondition_coverage` call-site check (2 sites, both in the new test file), and the git-stash red/green deliberate-breakage demonstration. None of the evidence rests on an unreproduced claim.

## Code/doc quality
Minimal, maintainable, matches project conventions. Ran the full Fowler baseline pass (`.agent-work/issue-422-wire-invariants/g1-review/fowler-pass.json`, cleared `scripts/verify_fowler_pass.py`'s rail: `smells=12, flagged=[], overridden=[primitive-obsession]`). The one override (`WORKTREE_ENTERING_GATES` as a plain tuple rather than a small `NamedTuple`/dataclass) is subordinated to `references/global-crew.md`'s "minimal change, no speculative abstraction" doctrine — wrapping a single-entry maintained list in a bespoke type ahead of a real second case would itself be the speculative-generality smell. Also checked against `docs/agents/CREW_CONTEXT.md`'s "Verification Discipline" rules: the coverage script asserts behaviour (the actual command string) not description text; the enumeration loop states the count it checked, not a bare pass; and the hand-maintained-list rule that CREW_CONTEXT.md generally discourages is a documented, justified exception here — the membership fact (which roles get dispatched into an isolated worktree) is a deployment/architectural fact, not something recoverable by scanning template JSON, and the handoff's own Map Anchors already name this as `decision:worktree-entering-membership`, graded `guess` with a `settle:` experiment.

## Map impact verdict
- **Evidence supports claimed change:** Yes — `claim:no-template-wires-isolation` re-confirmed independently (one grep match, the Commander spine).
- **Constraints not violated:** Yes — `<repo-root>` reuses the existing `resolve_spine()`-owned placeholder (confirmed via `grep -n repo-root scripts/init_work_area.py`, no new placeholder syntax introduced); `constraint:only-COMMANDER_SPINE-worktree-entering` honored (enumeration list carries exactly one entry).
- **Notes match the diff:** Yes — structural anchor (`init` gate `c0`, riding the unmodified `checklist_engine.py:1635 start()`), capability change (init gate now mechanically proves worktree isolation), both match the diff exactly.
- **Decision candidates surfaced:** Yes — `decision:worktree-entering-membership` implemented as specified; the implementer honestly flagged that its `settle:` experiment is only half-exercised (proven for a stripped copy of the one existing entry, not for a genuinely new second template, since none exists). This is not a cover for weak evidence — the two deliberate-breakage tests are otherwise fully proven.
- **Durable context routed:** Yes — routed forward as triage candidate `tc1` rather than dropped (see below).

## Reconciliation check
No divergence from recorded architecture. This is exactly the planned wiring for #329/#422: a prose-only invariant converted into a real engine precondition plus an enumeration check, matching the confirmed spec and the inbound map anchors.

## Blockers
- none

## Out-of-scope observations
- Triage candidate `tc1` (flagged in the survey): `decision:worktree-entering-membership`'s `settle:` experiment is only half-exercised — `EnumerationDeliberateBreakage` proves refusal-on-omission for a stripped copy of the existing single entry, not for a genuinely new second worktree-entering template, since none exists yet. Re-confirm the enumeration check's refusal actually fires when a second worktree-entering role/spine is added and left unwired, before regrading the decision from `guess` to `settled/measured`.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: the handoff's exact `c0` JSON shape, the coverage-script contract (`--root`, stated count, docstring rationale), and the two deliberate-breakage test shapes (enumeration + engine) were all specified precisely enough to verify without guessing.
- **Context rediscovered:** none beyond what the handoff pointed at directly — the handoff's own commands (stash/pop sequence, exact grep invocations) were sufficient to independently reproduce every claim without hunting for undocumented context.
- **Instructions improvised around:** The `templates/FOWLER_PASS.template.json` example record has an `override.reason` field with an embedded apostrophe-quoted phrase; hand-authoring the analogous JSON by literal string content produced a `\'`-escaped file that failed strict JSON parsing (`Expecting property name enclosed in double quotes`) even though it looked correct on read-back. Worked around it by generating the record via `json.dump()` in Python instead of hand-writing the JSON text, which guarantees correct escaping. Not a handoff gap — a general hazard of hand-authoring JSON with nested quoted phrases worth naming for future reviewers doing the Fowler pass.
- **What would have made this easier:** none — this handoff's precision (exact stash/pop commands, exact expected diff-stat delta, exact grep invocations) was close to the ideal shape for independently reproducing every claim rather than trusting the report.

## Return status
`complete`
