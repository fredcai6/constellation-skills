# Review Result

## Assigned Gate
`g1` — verify + close primitives (#574)

## Result
`APPROVE`

## Handoff compliance
Satisfied. `done_refusal`, `_engine_call`, `_advance_and_release` all exist in `scripts/spine_lifecycle.py` with the exact signatures the handoff fixes. The single most important close criterion — `done_refusal` does not call or reference `closeout_refusal` anywhere in its own source, docstring included, and takes no `archive_exists` parameter — is independently confirmed:

```
$ python3 -c "import sys; sys.path.insert(0,'scripts'); import spine_lifecycle as sl, inspect; print('closeout_refusal' in inspect.getsource(sl.done_refusal))"
False
```

I also red-proofed this guard rather than trusting it on its face: I mutated `done_refusal` to reintroduce a `closeout_refusal` reference, re-ran `test_does_not_call_closeout_refusal`, watched it fail with the injected string named in the diff output, then restored the file (`git diff --stat` back to the original 196-line insertion, full suite green again at 95). The check can fail, so its passing is real evidence.

Every other close criterion verified directly, not taken from the implementer's report:
- `done_refusal` is genuinely pure (no `Path(`/`open(`/`subprocess.` in its source).
- `_engine_call`'s only real call site of `checklist_engine.main` is inside its own definition (line 658, within `_engine_call`'s span 621–668) — confirmed via the test suite's own AST-based check (`test_is_the_only_place_this_module_calls_checklist_engine_main`), which is more rigorous than a plain-text grep (see Workflow Feedback — the handoff's suggested plain grep actually returns 5 lines, 4 of them docstring/comment prose).
- `_advance_and_release`'s refused `advance` never attempts `release` — `engine_session.status` stays `"active"` and the refusal text passes through byte-identical to a real separate-process engine run (`TestAdvanceAndReleaseHardBand`/unmet-postcondition tests, independently re-run).
- The HARD-band path is genuinely exercised — see Evidence verdict below.
- `closeout_refusal`/`close_work` are byte-for-byte unchanged: `git diff -U0` shows the only lines mentioning `closeout_refusal` are new prose in surrounding docstrings, and `closeout_refusal(` is still called from exactly one place (line 513, inside `close_work`).
- Fenced files empty diff: `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py` → empty, reproduced.
- Full suite green: 95 passed, reproduced. Pre-change count independently reproduced via `git stash push -u -- scripts/spine_lifecycle.py tests/test_spine_lifecycle.py` → 59 collected, matching the implementer's claim.

## Scope drift
None. `git status --porcelain` shows only `scripts/spine_lifecycle.py` and `tests/test_spine_lifecycle.py` modified — the two allowed-scope files. `.agent-work/*`, `RETURN.md`, `notes-g.md` are untracked workflow artifacts, not code. No forbidden functions (`force_reap`, `_release_child_plans`, `finish_work`, `open_pr`) were added. The wiring grep shows `done_refusal`/`_engine_call`/`_advance_and_release` have no callers outside their own definitions and the test file — matches the handoff's expectation that g3's `finish_work` is the future consumer.

## Evidence verdict
Required evidence present and independently reproduced, not merely trusted:
- Exact refusal strings match the handoff verbatim (`"close refused: the working tree has uncommitted changes"` / `"close refused: this run captured no episode"`), check order tested explicitly.
- `archive_exists` raises `TypeError` — confirms the signature has no such parameter.
- HARD-band test: I verified all four preconditions the stop condition names are genuinely satisfied by the fixture (gate `in-progress` by default, active lease, `observed_at >= claimed_at` — `claimed_ago=300`s vs. `observed_at=now`, model `claude-opus-5` present in `gauge_reader._PROFILES` with hard threshold 0.15 vs. fixture fill 0.92). The test class also carries its own negative-control test (`test_the_fixture_really_is_in_the_hard_band`) proving the fixture doesn't silently collapse to no reading — a stronger guarantee than the stop condition asked for. The why-less attempt is refused with the engine's own `"cannot be closed silently"` wording verbatim; the identical fixture then closes cleanly once `why` is supplied.
- `_engine_call` never raises on a malformed argv — `SystemExit(2)` from argparse is caught and returned as `(output, 2)`, confirmed for both an unparseable verb-args combination and an unknown flag.
- Test mode (test-after) matches the handoff's Test Mode section; not applicable to check TDD red-green.

## Code/doc quality
Meets project rules. Constraints checked individually against the diff:
- Never run against a live spine file — all 36 new tests build fixtures exclusively under `tmp_path`; no live `.agent-work/epic-567-door/{,cmdr-g/}{spine,execute}.json` path appears anywhere in the new test code. `validate_spine.py` against `cmdr-g/execute.json` is read-only (sha256 identical before/after my own re-run).
- Pure/impure split at function granularity — `done_refusal` pure (red-proofed above); `_engine_call`/`_advance_and_release` impure, routed through `_engine_call` only (`test_advance_and_release_goes_through_the_choke_point_only` asserts no `subprocess`/no direct `checklist_engine.main(` in `_advance_and_release`'s body).
- POSIX-form / `PYTHONIOENCODING=utf-8` — no new subprocess call path was added (all three new functions are in-process only); my own verification commands ran under `PYTHONIOENCODING=utf-8`.

**Fowler refactoring pass** (`r6-fowler`, recorded to `.agent-work/epic-567-door/cmdr-g/g1-review/FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0): 12/12 baseline smells rendered a verdict. 10 absent. 1 **flagged** (non-blocking): `_advance_and_release` repeats the same call/check-code/return-refusal shape three times (start/advance/release) — a `_call_stage(argv, stage)` helper would remove it; carried forward below as a triage candidate, not a blocker. 1 **overridden**: the plain-`dict` return shape (primitive-obsession candidate) is subordinate to the handoff's own Authority section, which fixes `-> dict` as the ratified signature, and matches `close_work`'s own pre-existing dict-return convention in the same module.

## Map impact verdict
- **Evidence supports claimed change:** yes — every capability/behavior claim in the implementer's Map Impact section is backed by independently-reproduced evidence above.
- **Constraints not violated:** yes — file-ownership fence honored (fenced files empty diff), never-test-on-a-live-lease honored (tmp_path fixtures only, read-only validate_spine.py check).
- **Notes match the diff:** yes, with one minor imprecision — line numbers given for `_engine_call` (~623 vs. actual 621) and `_advance_and_release` (~665 vs. actual 670) are close approximations, not materially wrong. `closeout_refusal`(:141) and `close_work`(:444) are exact.
- **Decision candidates surfaced:** none needed beyond what the REWORK NOTE already resolved (that resolution is itself confirmed correct by the load-bearing check above).
- **Durable context routed:** yes — the implementer's out-of-scope observation about the abandoned `g1-implementer-plan.json` "stand down" collision is carried forward as a triage candidate below rather than silently dropped or resolved by this review.

## Reconciliation check
No divergence from the recorded architecture needing Commander reconciliation. `decision:library-reuse-over-file-edit` honored throughout — no edits to fenced files, all engine calls in-process via `checklist_engine.main(argv)`.

## Blockers
- none

## Out-of-scope observations
- **Duplicated-code (Fowler, non-blocking):** `_advance_and_release`'s three-stage call/check/return pattern (start/advance/release) is a rule-of-three candidate for a small private helper. Does not affect correctness. Flagged as a triage candidate (`tc1` in the review survey).
- **Unresolved prior-attempt collision:** the abandoned earlier implementer attempt's `.agent-work/epic-567-door/cmdr-g/g1-implementer-plan.json` records a "STAND DOWN" blocker (a dispatching-fork-identity vs. real-`cmdr-g` collision on this same work-id) that was never adjudicated. This reviewer did not adjudicate it — outside `g1-review`'s authority. Commander/Admiral should reconcile `g1-implementer-plan.json` against `g1-implementer-plan-attempt2.json` before archiving g1's work area. Flagged as a triage candidate (`tc2` in the review survey).

## Workflow Feedback
- **Handoff gaps:** the reviewer handoff's suggested confirmation command — `grep -n "checklist_engine.main" scripts/spine_lifecycle.py` shows exactly one line — does not literally hold: the module's own docstring and `_engine_call`'s docstring legitimately *discuss* the pattern in prose (as the implementer handoff's REWORK-adjacent instructions asked them to document), so the plain grep returns 5 lines, 4 of them prose. The substantive claim (one real call site, inside `_engine_call`) is true and is what actually matters; I verified it with an AST-scoped check instead (the test file already does this itself, more rigorously than the suggested grep). Future handoffs authoring this kind of confirmation command should either scope the grep to exclude backtick-quoted docstring mentions or point at the AST-based test the implementer already wrote, rather than a plain-text grep that a compliant, well-documented implementation will fail.
- **Context rediscovered:** the survey template's `r6-fowler` postcondition (`REVIEW_SURVEY.template.json`) ships with a literal, unsubstituted `<work-id>` placeholder in its `command` check text (`python scripts/verify_fowler_pass.py .agent-work/<work-id>/FOWLER_PASS.json`). The item's own imperative text asserts this "resolves ... alone, so no separate placeholder to fill" but the template as copied does not actually substitute it — I had to discover this by inspecting the unmet postcondition and then repair it through `amend --delta <file>` (`retext-check` on `r6-fowler.c1`) per the item's own stated repair path, naming `cmdr-g` (the dispatching Commander from the directory structure) as `--authority` since the handoff does not name one explicitly.
- **Instructions improvised around:** the reviewer handoff never names a Commander session/identity to use as `--authority` for an `amend`. I inferred `cmdr-g` from the work-area path (`.agent-work/epic-567-door/cmdr-g/...`) rather than inventing a string — this happened to be unambiguous here, but a handoff that names the dispatching Commander's identity explicitly (as it already does for other authority-requiring situations) would remove the inference.
- **What would have made this easier:** either fix `REVIEW_SURVEY.template.json` so `r6-fowler`'s postcondition command is substituted at template-copy time along with the top-level `work_id` field (so the "no separate placeholder to fill" claim in its own imperative is actually true), or have the reviewer handoff name the dispatching Commander's identity for use as amend authority.

## Return status
`complete`
