# Implementer Handoff — REWORK (attempt 2)

## Gate
`g1-implement` (reopened after REVIEW BLOCK)

## Task
Fix a real bug the reviewer found and reproduced live in
`scripts/race_week_stages.py`'s `explain_stage` (in the worktree
`C:/Programs/f1Brainz/.claude/worktrees/604-build`), then add regression coverage. This is a
targeted fix, not a redo of the whole gate — everything else from the original build (checkpoint
I/O, hash/skip, `discover_sessions_stage`, `predict_stage`, `optimize_stage`) was reviewed and
APPROVED-equivalent (no findings) and must NOT be touched or restructured.

## Protected Intent
`explain_stage`'s entire contract is "never blocks the hard gate" — it must not raise for ANY input,
including a malformed `explainer_path`.

## The bug (full original handoff + result at .agent-work/604-race-week-build/crew-handoffs/g1-implementer-handoff.md and g1-implementer-result.md; review at g1-review-result.md — read the Blockers section there in full)
At `scripts/race_week_stages.py:288-289`:
```python
explainer_path = Path(explainer_path)
stub_path = explainer_path.with_name(f"{explainer_path.stem}.STUB{explainer_path.suffix}")

try:
    ...
```
Both lines execute BEFORE the `try:` block starts (line 291). Reviewer's live reproduction:
```
>>> explain_stage('some/stem', None)
TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'
>>> explain_stage('some/stem', '')
ValueError: WindowsPath('.') has an empty name
```
Both propagate uncaught, defeating the documented "never raises" contract.

## Close Criteria
- Move the `Path(explainer_path)` / `with_name(...)` construction INSIDE the `try:` block (or wrap
  it in its own guard) so any exception raised by constructing the path — bad type, empty string,
  or anything else — is caught by the same broad `except Exception` that already handles copy
  failures.
- Because `stub_path` itself is derived FROM `explainer_path`, if `explainer_path` construction
  itself fails, you cannot derive a stub path from it. In that case, fall back to a fixed,
  hardcoded stub filename (e.g. write the stub content to a path you can always construct — your
  call on the exact fallback, but it must never itself be able to raise). Document the fallback
  choice in your IMPLEMENTER_RESULT.
- Add regression tests to `tests/unit/scripts/test_race_week_stages.py` covering at minimum:
  `explain_stage(<valid stem>, None)` and `explain_stage(<valid stem>, "")` — both must return
  cleanly (a dict, `status` field present) and must NOT raise.
- Re-run the FULL test file (not just the new tests) and paste the full output — confirm nothing
  else regressed.
- Re-run `py -m src.utils.simplification_limits --paths scripts/race_week_stages.py`.

## Allowed Scope
`scripts/race_week_stages.py` (ONLY the `explain_stage` function — do not touch
`discover_sessions_stage`/`predict_stage`/`optimize_stage`/the checkpoint I/O helpers/
`compute_stage_inputs_hash`/`should_skip_stage`, they were reviewed clean) and
`tests/unit/scripts/test_race_week_stages.py` (add tests only — do not delete or rewrite existing
passing tests).

## Specific Exclusions
No `scripts/race_week.py`. No `src/` changes. Do not restructure functions outside `explain_stage`.

## Constraints
Same as the original handoff (compound-prior XOR propagation, no `write_beam_search_report` import,
etc.) — unaffected by this fix, just don't regress them.

## Deliverable Path Check
Same two files as the original gate — both already `git check-ignore` exit 1 (not ignored),
verified at original dispatch; unchanged.

## Required Evidence
Full pytest output for the WHOLE test file (not just new tests) post-fix. A short before/after
snippet showing the two previously-raising calls now return cleanly.

## Verification Commands
```bash
cd C:/Programs/f1Brainz/.claude/worktrees/604-build
py -m pytest tests/unit/scripts/test_race_week_stages.py -q
py -m src.utils.simplification_limits --paths scripts/race_week_stages.py
```

## Suggested Model Tier
Sonnet — small, well-diagnosed, targeted bug fix.

## Authority
The bug diagnosis and required fix shape (move construction inside try / guard it) are already
decided by the reviewer's finding — do not relitigate whether it's a real bug.

## Stop Conditions
Stop and return if the fix requires touching a function outside `explain_stage`, or if fixing it
reveals a deeper design problem in the checkpoint I/O helpers.

## Return Format
Return IMPLEMENTER_RESULT (rework/attempt 2): what changed, full pytest output, the before/after
repro snippet, assumptions, workflow feedback.
