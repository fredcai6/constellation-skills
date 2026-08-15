# Implementation Result

> Written per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Assigned gate
`g1`

## Completed slice
`finalize_from_exit_code` in `scripts/run_crew.py` no longer inverts the archive verdict when a dispatch
is given both `--spine` and `--result`: if the result artifact is missing or stale, and the bound spine is
terminal, the verdict is rescued into `completed` instead of unconditionally reading `failed`. When the
spine is not terminal (or absent), the crew still reads `failed` — the fix is not a rubber stamp. A new
`entry["verdict_source"]` field, set on every call to exactly `"blocked_gate"` | `"result"` |
`"spine_terminal"` | `"none"`, records which path decided the verdict. `blocked_gate` is still checked
first and unconditionally wins, overriding `verdict_source` too.

## Scope
**Files changed:**
- `scripts/run_crew.py` — `finalize_from_exit_code` function body and docstring only (lines ~954-1046 after
  the edit).
- `tests/test_crew_launcher.py` — three new test methods added to `FinalizeFromExitCodeTests`.

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
`.mcp.json` untouched. `result_exists`, `result_fresh`, `spine_terminal`, `spine_blocked_id` untouched
(confirmed by diff — only `finalize_from_exit_code` changed in `run_crew.py`).

## Behavior changed
Yes. `finalize_from_exit_code(result=<given>, spine=<given>)`: when the result artifact is missing/stale
AND the bound spine is terminal, status is now `completed` (was `failed`). When the result is
missing/stale and the spine is NOT terminal (or no spine), status is unchanged (`failed`). `blocked_gate`
precedence is unchanged. Every call now also sets `entry["verdict_source"]`, a new field.

## Test mode
**Required:** test-first (TDD, red before green)
**Satisfied:** yes — see TDD evidence below.

## Evidence

```bash
$ git check-ignore scripts/run_crew.py tests/test_crew_launcher.py; echo "exit:$?"
exit:1
```

```bash
$ python -m pytest -q tests/test_crew_launcher.py::FinalizeFromExitCodeTests
........                                                                 [100%]
8 passed in 0.02s
```

```bash
$ python -m pytest -q -k "test_finalize_terminal_spine_rescues_missing_result or test_finalize_still_fails_when_spine_not_terminal or test_finalize_blocked_wins_regardless_of_result_or_spine"
...                                                                      [100%]
3 passed, 3009 deselected in 0.78s
```

**Result:** pass — all commands run foreground to completion, output pasted verbatim (not summarized).

## TDD evidence, if required

**Failing test observed (RED), run against the UNCHANGED `finalize_from_exit_code`:**

```
$ python -m pytest -q -k "test_finalize_terminal_spine_rescues_missing_result or test_finalize_still_fails_when_spine_not_terminal or test_finalize_blocked_wins_regardless_of_result_or_spine"
FFF                                                                      [100%]
=================================== FAILURES ===================================
_ FinalizeFromExitCodeTests.test_finalize_blocked_wins_regardless_of_result_or_spine _
...
>           self.assertEqual("blocked_gate", entry["verdict_source"])
E           KeyError: 'verdict_source'
_ FinalizeFromExitCodeTests.test_finalize_still_fails_when_spine_not_terminal __
...
>           self.assertNotEqual("spine_terminal", entry["verdict_source"])
E           KeyError: 'verdict_source'
_ FinalizeFromExitCodeTests.test_finalize_terminal_spine_rescues_missing_result _
...
>           self.assertEqual(0, final)
E           AssertionError: 0 != 1
=========================== short test summary info ============================
FAILED tests/test_crew_launcher.py::FinalizeFromExitCodeTests::test_finalize_blocked_wins_regardless_of_result_or_spine
FAILED tests/test_crew_launcher.py::FinalizeFromExitCodeTests::test_finalize_still_fails_when_spine_not_terminal
FAILED tests/test_crew_launcher.py::FinalizeFromExitCodeTests::test_finalize_terminal_spine_rescues_missing_result
3 failed, 3009 deselected in 0.82s
```

**Actual baseline distribution was 3 failed, not the handoff's predicted "exactly the rescue test failing,
the other two passing."** Derived mechanically, not summarized from a glance — see Assumptions below for
why this is not a design problem: `test_finalize_terminal_spine_rescues_missing_result` fails on the
genuine behavioral bug this gate fixes (`final == 1`, not `0` — the rescue never happens pre-fix). The
other two fail only via `KeyError` at the `entry["verdict_source"]` line, reached AFTER their pre-existing
status/blocked_gate assertions already passed — because `verdict_source` is a brand-new field this same fix
introduces and does not exist at all pre-fix. The underlying behavior those two protect (status stays
`failed` when the spine is not terminal; `blocked` wins regardless of a fresh result) was independently
confirmed correct pre-fix; only the new-field reference turns them red too.

**Passing test observed (GREEN), run against the FIXED `finalize_from_exit_code`:**

```
$ python -m pytest -q -k "test_finalize_terminal_spine_rescues_missing_result or test_finalize_still_fails_when_spine_not_terminal or test_finalize_blocked_wins_regardless_of_result_or_spine"
...                                                                      [100%]
3 passed, 3009 deselected in 0.78s
```

**Refactor while green:** no — the change was minimal (branch + one new field); no refactor pass needed.

## Docs/contracts touched
- `scripts/run_crew.py` — `finalize_from_exit_code`'s docstring, updated in the same edit to describe the
  rescue path and the `verdict_source` field's four values.

## Assumptions
- The handoff's predicted baseline distribution ("exactly the rescue test failing, the other two passing")
  does not hold literally once `verdict_source` assertions (specified by the handoff itself, using bracket
  access `entry["verdict_source"]`) are included in the pinned test bodies, because that field does not
  exist at all before this fix. I did not rewrite the two "should already pass" tests to use `.get(...)` to
  force a literal pass at baseline — the handoff pins the exact assertion shapes (`entry["verdict_source"]
  == "blocked_gate"`, `entry["verdict_source"] != "spine_terminal"`), and changing them to swallow the
  KeyError would hide the field's newness rather than reflect it honestly. I treated the mechanically
  measured 3-failed baseline, with cause attributed per-test, as satisfying the spirit of "red before
  green" (the one behavioral bug this gate fixes is isolated and shown red; the two regression-proof tests'
  pre-existing behavior is independently confirmed unchanged pre-fix, and both plus the fix land green
  together after).
- `verdict_source` for the `result is None` branch (unchanged by this fix, not exercised by the three pinned
  tests) is set to `"spine_terminal"` whenever a `spine` is given at all — win or lose on terminality — and
  `"none"` only when both `result` and `spine` are `None`. This reads the field as naming *which check
  decided the verdict* (the spine-terminal check was consulted and is dispositive in that branch), not as a
  synonym for "the spine was in fact terminal." Not one of the three required tests exercises this branch,
  so it's an inference from the pinned mapping's stated cases, not itself pinned — flagging in case the
  Commander wants a different reading.

## Stop conditions hit
None. The fix does not let a genuinely failed crew (spine not terminal, no result) read as completed
(`test_finalize_still_fails_when_spine_not_terminal` proves it); scope was not exceeded; all required
evidence was produced.

## Out-of-scope observations
- `spine_terminal` (untouched, out of scope for this gate) takes no `since`/dispatch-time parameter, unlike
  `result_fresh`. A terminal spine left over from an EARLIER attempt at the same path could rescue a LATER
  attempt's missing/stale result into `completed`, as long as that later attempt's `exit_code` happens to be
  `0` — the `exit_code == 0 and done` gate still catches a crashing child, but not a child that exits 0
  having done nothing new while an old terminal spine sits at the path. Worth a triage candidate: a
  dispatch-time-aware `spine_terminal` (or a caller-side staleness check mirroring `result_fresh`) if this
  edge matters in practice; not raised as a blocker for this gate, which was scoped not to touch
  `spine_terminal`.
- Both open questions answered below are themselves candidates for a follow-on doc note if the answers
  should be recorded closer to the code (e.g. as a `spine_lifecycle.close_work` docstring note referencing
  this fix) — not acted on here, out of this gate's file-ownership fence.

## Open questions (from Constraints)

**(a) Does any gate OTHER than `archive` relocate artifacts the launcher watches?**
No, and more specifically: `scripts/checklist_engine.py` itself contains **zero** relocation/move code —
grepped for `shutil.move`, `shutil.copy`, `.rename(`, `os.replace`, and `relocat` across the whole file;
the only three hits are in docstrings/comments *referencing* `spine_lifecycle` by name, not moving anything
themselves. The actual mover is `scripts/spine_lifecycle.py`'s `close_work` (~line 365-520), which relocates
the **entire work-area directory** — every top-level entry (any `--result` artifact included, since it
typically lives inside the work area), plus the spine and its journal last — into
`.agent-work/archive/<archive_name>` as one atomic, all-or-nothing operation (a failure partway rolls the
whole batch back via `_undo_moved`). It is invoked once, at closeout, not per-gate: there is exactly one
relocation code path in the repo, not one-per-gate, so "the archive gate relocates" is really "closeout
(spine_lifecycle.close_work) relocates, and closeout is what the archive gate's imperative names as its
job" — checklist_engine.py's gates are a plan/state machine with no filesystem-move verb of their own.

**(b) Should a `failed` verdict ever be recordable while the bound spine is terminal?**
Yes, and this fix deliberately preserves that case rather than closing it: `elif exit_code == 0 and done:`
still requires BOTH a zero exit code AND `done` (fresh result or spine rescue) for `completed` — if the
child process itself exits nonzero, the entry reads `failed` (`final = exit_code`) even when `done` is
`True` because the spine happens to be terminal. This is correct, not a gap: a nonzero exit code is the
process's own signal that something went wrong (crash, uncaught exception, launcher-level failure) and
must not be silently overridden by a spine state — which, per the out-of-scope note above, is not even
required to be fresh relative to this dispatch. Conflating "spine terminal" with "process succeeded" would
let a crashing child that happens to run against a leftover terminal spine from a prior attempt read as
`completed`. So: `failed`-while-terminal-spine is possible and intentional in the current design, gated on
`exit_code`, not something this fix needed to resolve — stated as my read, not re-litigated.

## Wiring Grep
```
$ grep -rn "verdict_source" --include=*.py . | grep -v "def finalize_from_exit_code"
./scripts/run_crew.py:1002:    reality), `blocked_gate` when blocked, and `verdict_source` -- ALWAYS one
./scripts/run_crew.py:1018:            verdict_source = "result"
./scripts/run_crew.py:1022:            verdict_source = "spine_terminal" if rescued else "result"
./scripts/run_crew.py:1027:        verdict_source = "spine_terminal" if spine is not None else "none"
./scripts/run_crew.py:1035:        verdict_source = "blocked_gate"
./scripts/run_crew.py:1046:    entry["verdict_source"] = verdict_source
./tests/test_crew_launcher.py:2343:            self.assertEqual("spine_terminal", entry["verdict_source"])
./tests/test_crew_launcher.py:2359:            self.assertNotEqual("spine_terminal", entry["verdict_source"])
./tests/test_crew_launcher.py:2381:            self.assertEqual("blocked_gate", entry["verdict_source"])
```
Count: 9 lines (5 in `scripts/run_crew.py` — all within/about `finalize_from_exit_code` itself; 3 in the new
tests; the docstring line at 1002 is prose, not code). As expected per the handoff: nothing outside
`finalize_from_exit_code` and my three new tests reads `verdict_source` yet — it is a new observability
field the registry entry carries, not yet consumed by any caller (e.g. `crew-runs.json` readers, recovery
tooling). Not a defect for this gate.

## Map Impact
- **Structural anchors touched:** `scripts/run_crew.py:954-1046` — `finalize_from_exit_code` (grew by ~13
  lines to add the spine-rescue branch and `verdict_source`); no signature change (same params, same return
  type).
- **Capabilities added/changed/affected:** the launcher's completed/failed/blocked verdict for a
  both-`--spine`-and-`--result` dispatch now survives the `archive` gate's own relocation of the result
  artifact — a dispatch is no longer penalized for the exact filesystem move `spine_lifecycle.close_work`
  performs as its normal, correct behavior.
- **Events added/changed/affected:** none (no event/queue surface touched).
- **Constraints/assumptions touched:** the pre-existing invariant "`blocked_gate` decided first, ahead of
  both other paths" is stressed by the new branch and confirmed still holds (test 3;
  `verdict_source = "blocked_gate"` unconditionally overwrites whatever the earlier branch computed).
- **Decision candidates / resolved decisions:** none new — the fix's shape was pinned by the handoff/launch
  order, not decided here.
- **Claims/evidence produced:** `verdict_source` is a new claim surface (which of four paths decided a
  registry entry's status) with no external readers yet (see Wiring Grep) — a claim, not yet consumed.
- **Trust limitations / drift found:** `spine_terminal`'s lack of dispatch-time freshness (out-of-scope
  observation above) is a latent gap this fix's rescue path now leans on slightly more than before, since
  the rescue path is a NEW way for `spine_terminal`'s answer to flip a verdict from `failed` to `completed`.
- **Triage candidates:** dispatch-time-aware `spine_terminal` (or an equivalent caller-side staleness guard)
  — see Out-of-scope observations.

## Workflow Feedback

- **Handoff gaps:** the "Derive both distributions mechanically" instruction correctly anticipated that the
  predicted baseline ("exactly the rescue test failing, the other two passing") might not hold exactly —
  but the handoff's own pinned assertion shapes for the two "should already pass" tests
  (`entry["verdict_source"] != "spine_terminal"` / `== "blocked_gate"`, bracket access) make a literal
  3-failed baseline unavoidable, since `verdict_source` is new. Worth naming explicitly in a future handoff
  of this shape (new-field-plus-regression-tests) so the crew doesn't second-guess whether the mismatch
  signals a misread of the task.
- **Context rediscovered:** the handoff's Constraints section asked to grep `scripts/checklist_engine.py`
  for relocation/move behavior "across all gates," but the actual mover lives entirely in
  `scripts/spine_lifecycle.py` (`close_work`), invoked once at closeout, not per-gate inside the engine —
  I had to grep a level below the named file to find where relocation really happens. A pointer to
  `spine_lifecycle.py` alongside the `checklist_engine.py` grep instruction would have saved a hop.
- **Instructions improvised around:** none — the CLI checklist-engine path (no MCP door bound) matched the
  dispatch's explicit instruction exactly; the implementer skill's default MCP-door guidance was correctly
  superseded by the dispatch's explicit "no MCP spine door bound" statement.
- **What would have made this easier:** naming `scripts/spine_lifecycle.py` directly in the Constraints
  section's relocation question, since `checklist_engine.py` alone answers "none" and the interesting answer
  lives one file over.

## Return status
`complete`
