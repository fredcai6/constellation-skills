# Implementation Result

## Assigned gate
`g2-implement` (issue #328/#422, workstream D of epic #418)

## Completed slice
`record()` (the survey verb in `scripts/checklist_engine.py`) now evaluates `command`-kind postconditions when `result == 'pass'` is requested, mirroring `advance()`'s existing pattern via the same `_check_condition` helper and the same `EngineError` refusal shape. `result == 'fail'` is never gated by the check. `null`-kind and `artifact`-kind postconditions on a survey item remain unevaluated, with a comment at the site naming the limit as an explicit scope decision. Two templates — `INTERROGATION.template.json`'s `zc-consolidate` and `REVIEW_SURVEY.template.json`'s `r6-fowler` — now each carry a real command postcondition wired to their existing verify script, with the hand-fill-placeholder convention spelled out in the imperative text. `tests/test_record_postcondition_wiring.py` lands 10 tests including two REAL, unmocked deliberate-breakage tests that invoke the actual `verify_interrogation.py`/`verify_fowler_pass.py` scripts against bad scratch records in a temp dir.

## Scope
**Files changed:**
- `scripts/checklist_engine.py` — `record()` gained a `base_dir` parameter (mirroring `advance()`'s signature) and, on `result == 'pass'`, runs each `command`-kind postcondition via `_check_condition` and raises `EngineError` naming the unmet ones if any fail. `main()`'s CLI dispatch for `record` now passes `base_dir` through. No other function touched.
- `skills/interrogator/templates/INTERROGATION.template.json` — `zc-consolidate`'s `postconditions` array (was `[]`) now carries one `command` postcondition calling `verify_interrogation.py <interrogation-record-path>`; one sentence added to its `imperative` making the hand-fill convention explicit. No other item touched.
- `skills/reviewer/templates/REVIEW_SURVEY.template.json` — `r6-fowler`'s `postconditions` array (was `[]`) now carries one `command` postcondition calling `verify_fowler_pass.py <fowler-pass-record-path>`; same one-sentence addition. No other item touched.
- `tests/test_record_postcondition_wiring.py` — new file.

**Specific exclusions touched:** no — `verify_interrogation.py` and `verify_fowler_pass.py` were read but not modified; `render_human`, `_why_suffix`, and `current()` (workstream B/#420's fence) were not touched; issue #315 (command-check `cwd` inheritance) was not fixed — see Assumptions below for the residual fragility noted at the code site instead.

## Behavior changed
Yes. `record(iid, result='pass', ...)` on a survey item carrying a `command`-kind postcondition now actually runs that check and refuses the request (raising `EngineError`, item stays `in-progress`, `result`/`status` untouched) if the command fails — previously it stored `pass` unconditionally regardless of what the postcondition said. `record(iid, result='fail', ...)` is unaffected — it always succeeds, even when the same command would fail. Items with no command postcondition (the vast majority of survey items today, and any item with only `null`/`artifact`-kind postconditions) are byte-for-byte unchanged.

## Map Impact
- **Structural anchors touched:** `scripts/checklist_engine.py:1731` `record()` (now ~28 lines, was 9) and `scripts/checklist_engine.py:2479` (`main()`'s CLI dispatch for `record`) — both inside the invariant-check path named in the inbound Structural anchors; `advance()` (`:1668`) and `_check_condition` (`:746`) read but not modified, reused exactly as the inbound anchor named.
- **Capabilities added/changed/affected:** Survey `record()` verb — moved from "ignores postconditions entirely" (inbound Capability anchor) to "a `pass` result on a command-backed item is provably checked," matching the anchor's stated target exactly.
- **Constraints/assumptions touched:** the inbound Constraints anchor ("all 7 existing `kind: command` postcondition examples in the corpus live on GATED spines only") is now stale in one respect — two SURVEY items (`zc-consolidate`, `r6-fowler`) carry `command`-kind postconditions as of this change. Worth a Cartographer reconcile note.
- **Decision candidates / resolved decisions:** `decision:survey-record-check-scope` (inbound, `@grade: settled/human`) — implemented exactly as specified: `command`-kind only, `null`/`artifact`-kind explicitly out of scope and commented at the site, not silently generalized.
- **Claims/evidence produced:** `claim:record-ignores-postconditions` re-confirmed via red-before/green-after test (see TDD evidence below), not a second source read — matches the inbound Evidence expectation.
- **Trust limitations / drift found:** none found beyond the Constraints anchor staleness noted above.
- **Triage candidates:**
  1. `scripts/checklist_engine.py`'s `_next_verbs` (~line 1536) carries a comment/behavior note: "`record()` carries no precondition/postcondition gate at all (see `record()`) -- unlike `advance()`, it is ALWAYS legal from in-progress, so it is never suppressed by open conditions." That statement is now partially stale: `record()` does gate `command`-kind postconditions on `result == 'pass'`. The `_next_verbs` hint-suppression behavior itself is unaffected (the `record` verb hint is still always offered — the refusal happens inside `record()` when actually invoked, not by suppressing the hint), so no functional bug, but the comment's premise is now inaccurate. `_next_verbs` is in the rendering path (workstream B/#420's fence this wave) — not touched, flagged for that workstream or a follow-up.

## Test mode
**Required:** `test-after` (wiring existing, already-tested rail scripts into the engine — but the deliberate-breakage tests are the acceptance criteria themselves)
**Satisfied:** yes — all tests pass on the fixed tree, and the refusal-dependent tests were independently proven to fail red on the pre-fix state (see "TDD evidence" below).

## Evidence

```bash
python -c "import json; json.load(open('skills/interrogator/templates/INTERROGATION.template.json', encoding='utf-8')); json.load(open('skills/reviewer/templates/REVIEW_SURVEY.template.json', encoding='utf-8'))"
```
**Result:** no output, exit 0 — both templates valid JSON.

```bash
python -m pytest tests/test_record_postcondition_wiring.py -q
```
```
..........                                                               [100%]
10 passed in 1.62s
```
**Result:** pass, all 10 tests green.

```bash
python -m pytest tests/test_checklist_engine.py -q
```
```
........................................................................ [ 21%]
...................................................... [ 38%]
........................................................................ [ 60%]
.................................................................. [ 80%]
..................................................................       [100%]
330 passed, 24 subtests passed in 13.13s
```
**Result:** pass, regression floor for `record()`'s unchanged no-command-postcondition behavior holds.

```bash
python -m pytest tests/ -q
```
```
1633 passed, 2 skipped, 549 subtests passed in 445.96s (0:07:25)
```
**Result:** pass, full suite green (1623 baseline + 10 new, per g1's own last full-suite run on this branch — no regressions).

```bash
grep -rn "interrogation-record-path\|fowler-pass-record-path" --include=*.json --include=*.md .
```
**Result:** 5 distinct files matched: the two committed templates (`skills/interrogator/templates/INTERROGATION.template.json`, `skills/reviewer/templates/REVIEW_SURVEY.template.json` — the required wiring), plus three `.agent-work/` artifacts of this run itself (`g2-implement-handoff.md`, `g2-implement-plan.json`, `execute.json`, all referencing the same placeholder text as part of driving this gate) — no unexpected third-party reference found.

## TDD evidence, if required
Test-after mode, so no red-step-first TDD cycle — instead, the required "prove the deliberate-breakage tests genuinely fail without the fix" evidence, produced by reverting the real `record()` change via `git stash`, not a synthetic before-state fixture:

1. `git stash push --quiet -- scripts/checklist_engine.py` — reverted the file to its last-committed (pre-fix) state; `git diff --stat scripts/checklist_engine.py` showed empty, confirming the mutation applied.
2. `python -m pytest tests/test_record_postcondition_wiring.py -q` against that reverted state:
   ```
   ...F..F..F                                                               [100%]
   FAILED tests/test_record_postcondition_wiring.py::RecordCommandPostconditionTests::test_pass_with_failing_command_postcondition_refused
   FAILED tests/test_record_postcondition_wiring.py::InterrogationDeliberateBreakageTests::test_self_answered_decision_refuses_record_pass
   FAILED tests/test_record_postcondition_wiring.py::FowlerDeliberateBreakageTests::test_skipped_smell_refuses_record_pass
   3 failed, 7 passed in 0.42s
   ```
   All three failures are `AssertionError: EngineError not raised` — exactly the three refusal-dependent tests (the generic failing-command case, and the two real-script deliberate-breakage cases), each caught by the missing fix. The other 7 tests (record-fail-never-blocked, no-command-postcondition-unaffected, null-kind-unevaluated, the gated-type guard, and the two "valid record still passes" cases) stayed green, confirming they exercise something else and are not accidentally coupled to the fix.
3. `git stash pop --quiet` — restored the fix; `git diff --stat scripts/checklist_engine.py` showed `22 insertions(+), 2 deletions(-)`, confirming the restore applied; re-validated with `python -c "import ast; ast.parse(...)"` (syntax ok).
4. Re-ran `python -m pytest tests/test_record_postcondition_wiring.py -q` → `10 passed in 1.66s` — confirmed green again.
- Refactor while green: no refactor needed.

## Docs/contracts touched
- none beyond the two templates named in scope — both are additive (`postconditions: []` → one `command` postcondition plus one imperative sentence); no existing doc needed updating.

## Assumptions
- `base_dir` threaded through `record()`'s signature (mirroring `advance()`'s) does not actually change a `command`-kind check's working directory — `_check_condition`'s command branch calls `_run_check_command(chk["command"])` with no `cwd`, exactly as `advance()`'s own command-kind checks already work; `base_dir` is only consumed by the `artifact`/`git-change-policy` branches. This is consistent with existing behavior (issue #315, explicitly out of scope) and is why the templates' hand-fill commands (`python scripts/verify_interrogation.py <path>`) assume the engine runs from the repo root, same as every other `command`-kind postcondition in the corpus today.
- The deliberate-breakage tests invoke the real verify scripts via a real `command`-kind postcondition (subprocess through the engine's own POSIX-shell command runner), not a direct Python import — this exercises the actual code path (`record()` → `_check_condition` → `_run_check_command` → `bash -c "python scripts/verify_....py <path>"`) end to end, documented in the test file's module docstring.
- Minimal invalid fixtures were built by reading `tests/test_interrogation.py`'s `_decision(human_answer="")` (`DecisionBlockTests::test_decision_resolved_without_human_answer_refused`) and `tests/test_fowler_pass.py`'s `_all_absent()` with one smell dropped (`VisitEverySmellTests::test_missing_smell_refused`) rather than guessing the schema, per the handoff's instruction — confirmed both shapes are the exact ones each rail's own test suite treats as minimal-invalid.
- Scratch records use `tempfile.TemporaryDirectory` (cleaned up in `tearDown`), matching the idiom already used by `tests/test_worktree_precondition_wiring.py` (g1's own precedent) rather than pytest's `tmp_path` fixture — this codebase's existing tests are `unittest.TestCase`-based, and `tmp_path` is a pytest-native fixture not directly available inside `unittest.TestCase` methods without extra plumgin machinery.

## Stop conditions hit
- none — no rendering-path (`render_human`/`_why_suffix`/`current()`) change was needed, `record()`'s existing no-command-postcondition behavior stayed intact (regression floor green), both deliberate-breakage tests were provably made to fail without the fix using temp-only fixtures, and all required evidence was producible.

## Out-of-scope observations
- **Triage candidate:** the stale `_next_verbs` comment/premise at `scripts/checklist_engine.py:~1536-1538` — see Map Impact above. Not fixed here (rendering-path fence).
- Both templates' new command postcondition is unmet by default (`satisfied: false`, hand-fill placeholder unresolved) — this is intentional and matches the `EXECUTE_PLAN.template.json` precedent exactly; a driving interrogator/reviewer agent must edit the check's `command` string with the real per-run record path before it can ever pass. No mechanism auto-resolves it (matching `init_work_area.py`'s scope, which only ever writes `spine.json` for gated spines, per the handoff's own framing).

## Workflow Feedback
- **Handoff gaps:** none — the handoff's exact postcondition JSON shape, the `base_dir` plumbing instruction, the fence boundary, and the four required test behaviors were all specified precisely enough to implement without guessing.
- **Context rediscovered:** had to read `tests/test_checklist_engine.py`'s `gate()`/`gated()`/`survey_item()`/`survey()` helpers and `_run_check_command`'s POSIX-shell routing directly to confirm `base_dir` is a no-op for `command`-kind checks (only `artifact`/`git-change-policy` consume it) — this shaped both the implementation (thread the param for signature parity, as asked, without expecting it to affect command execution) and the Assumptions note above. The handoff's own framing ("cwd-independent-in-spirit... note any residual fragility at the code site rather than fixing #315 wholesale") was accurate and anticipated this — a "had to look," not a handoff gap.
- **Instructions improvised around:** none — no skill/template/engine instruction failed to cover the situation.
- **What would have made this easier:** none concrete — this handoff's precision (exact postcondition JSON shape for both templates, the exact fence boundary with a named escalation path, and the four required test behaviors spelled out with pointers to the minimal-invalid fixture sources) was close to ideal for a bounded wiring task.

## Return status
`complete`
