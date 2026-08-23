# Implementation Result

## Assigned gate
`g1-implement` (569 w3-basis)

## Completed slice
In `tests/test_checklist_engine.py`, class `CommanderSpineBasisFields` (~line 8543):
replaced the whole-repo `HEAD` pin (`PINNED_HEAD` / `_skip_if_head_moved`) with a
blob-OID pin on `skills/commander/templates/COMMANDER_SPINE.template.json`
(`PINNED_BLOB` / `_fail_if_template_drifted`); on drift the helper now calls
`self.fail(...)` (never `self.skipTest(...)`), naming the proof as "stale", both
blob OIDs, the exact re-run command, and the paste-target. All 3 existing test
methods' first line was updated to call the renamed helper; `EXPECTED_BASIS` and
`_load_spine` are byte-identical. The class docstring's second paragraph now
describes blob-OID pinning and fail-on-drift instead of the retired
whole-repo-HEAD + skip design. Added two new mutation-battery test methods
(`test_mutation_battery_template_edit_fails_not_skips`,
`test_mutation_battery_unrelated_commit_stays_green`) that each clone the repo
into an isolated `/tmp` scratch dir via `git clone --local`, plant one of the two
opposite mutations there, and assert the 3 protected-intent tests FAIL (RED,
template mutated) or PASS (GREEN, unrelated commit) — never touching the shared
worktree. `PINNED_BLOB` was computed via
`git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json`
and re-checked immediately before writing this result; unchanged both times.

## Scope
**Files changed:**
- `tests/test_checklist_engine.py`

**Specific exclusions touched:** no — `skills/commander/templates/COMMANDER_SPINE.template.json`
and `scripts/checklist_engine.py` were read-only (read once each, for the blob-OID
computation and to confirm the `subprocess`/`git` idiom already used by the file);
neither was edited. No qualitative-condition population and no rollout of `basis`
beyond `plan.c2/c4/c5`.

## Behavior changed
Yes. `CommanderSpineBasisFields`'s staleness gate now (a) tracks the template
file's content (blob OID), not repo-wide `HEAD`, so unrelated commits elsewhere no
longer perturb it, and (b) FAILs loudly on drift instead of silently skipping.
Both directions are proven by the new mutation-battery tests. No other test file,
production module, or the template itself changed.

## Map Impact
- **Structural anchors touched:** `tests/test_checklist_engine.py::CommanderSpineBasisFields`
  — `PINNED_HEAD`/`_skip_if_head_moved` retired; `PINNED_BLOB`/`_fail_if_template_drifted`
  added; two new test methods added (`test_mutation_battery_template_edit_fails_not_skips`,
  `test_mutation_battery_unrelated_commit_stays_green`) plus a shared
  `BASIS_TEST_NODE_IDS` tuple.
- **Capabilities added/changed/affected:** red-proof pinning for the commander
  spine template's basis-field shape — pin granularity changed from whole-repo
  `HEAD` to the template's blob OID; drift behavior changed from skip to fail.
- **Constraints/assumptions touched:** `constraint:file-ownership` (honored — only
  this file edited), `constraint:no-skip-on-drift` (honored — `self.fail` only,
  `grep` confirms no `skipTest` remains in the class), `constraint:blob-oid-granularity`
  (honored — pin is `git rev-parse HEAD:<path>`), `constraint:cheap-re-verify`
  (honored — the re-verify path is the one-liner already printed in the fail
  message), `constraint:prove-both-directions` (honored — see mutation battery
  evidence below).
- **Decision candidates / resolved decisions:** `decision:blob-oid-not-head`,
  `decision:drift-fails`, `decision:ship-the-re-verify-path`,
  `decision:prove-both-directions` — all four applied as specified in the
  handoff; none re-litigated.
- **Claims/evidence produced:** `claim:pin-tracks-file-not-repo` (mutation-battery
  GREEN direction), `claim:drift-fails-not-skips` (mutation-battery RED direction),
  `claim:re-verify-is-cheap` (the re-verify command is a single `git rev-parse`
  invocation, exercised live in the RED-direction evidence probe below, which
  prints the exact new blob it would need pasted in).
- **Trust limitations / drift found:** none new. The repo map was already flagged
  DEGRADED-UNPARSEABLE for this run (per `MISSION_FRAME.md`); this slice did not
  touch anything that would resolve or worsen that.
- **Triage candidates:** none from this slice.

## Test mode
**Required:** test-after (this gate IS the test file; the new mutation-battery
tests are the TDD-style proof, per the handoff).
**Satisfied:** yes — both directions of the mutation battery were run and their
raw output inspected (below) before this result was written.

## Evidence

```bash
$ python3 -m pytest tests/test_checklist_engine.py::CommanderSpineBasisFields -q -rs
.....                                                                 [100%]
5 passed, 3 subtests passed in 2.82s
```

**Result:** pass — 5 tests (the original 3 plus the 2 new mutation-battery
methods), zero skipped, zero failed, at commit `8691a40e` (this gate's final
commit — working tree is clean at hand-back).

Whole-file regression check (not required by the handoff, run as an extra
sanity check since only this file changed):

```bash
$ python3 -m pytest tests/test_checklist_engine.py -q -rs
538 passed, 150 subtests passed in 8.77s
```

**Result:** pass — no other test in the file was disturbed.

## TDD evidence, if required

Mutation-battery run, both directions, output captured directly from the
isolated-clone subprocess calls (same mechanism the two new test methods use
internally):

**RED direction — template mutated in the isolated clone:**
```
=== RED direction (template mutated) ===
returncode: 1
FFF                                                                      [100%]
=================================== FAILURES ===================================
_ CommanderSpineBasisFields.test_plan_c2_c4_c5_each_carry_the_ratified_basis_shape _
...
E   AssertionError: CommanderSpineBasisFields' proof is stale: pinned to blob 6953ac90f2568890fddbe187ad5fc8dd095041dd of skills/commander/templates/COMMANDER_SPINE.template.json, current blob is 0ae37ea6d8487b0da415651606315d5cfdc9f0ef -- the template changed since this test's shape assumptions were verified (g1 dispatch). Re-verify EXPECTED_BASIS (and the rest of this class) against the new template content, then re-pin by running:
E       git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json
E   and pasting the result into PINNED_BLOB above.
[... same failure for test_no_condition_outside_plan_c2_c4_c5_carries_a_basis_key
     and test_live_checklist_from_the_template_renders_basis_lines_at_plan ...]
=========================== short test summary info ============================
FAILED tests/test_checklist_engine.py::CommanderSpineBasisFields::test_plan_c2_c4_c5_each_carry_the_ratified_basis_shape
FAILED tests/test_checklist_engine.py::CommanderSpineBasisFields::test_no_condition_outside_plan_c2_c4_c5_carries_a_basis_key
FAILED tests/test_checklist_engine.py::CommanderSpineBasisFields::test_live_checklist_from_the_template_renders_basis_lines_at_plan
3 failed in 0.39s
```
All 3 tests FAILED (not skipped, not errored); each failure names the proof as
"stale", states both blob OIDs, and gives the exact literal re-run command.

**GREEN direction — unrelated commit in the isolated clone, template untouched:**
```
=== GREEN direction (unrelated commit) ===
returncode: 0
...                                                                   [100%]
3 passed, 3 subtests passed in 0.12s
```
All 3 tests PASSED — `HEAD` moved in the scratch clone but the template's blob
did not, so `PINNED_BLOB` still matched.

- Failing test observed: RED-direction output above (mutation-battery template
  edit; observed both via the standalone probe and via the two new test methods'
  own assertions, which pass because they observe this same failure text).
- Passing test observed: GREEN-direction output above, plus the 5/5 pass at the
  final commit shown in Evidence.
- Refactor while green: n/a — no refactor step; this is a single surgical
  rename + behavior change plus two additive test methods, done in one pass.

## Final PINNED_BLOB
```
$ git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json
6953ac90f2568890fddbe187ad5fc8dd095041dd
```
Computed once to author the initial edit, then re-checked immediately before
writing this result (both at commit `8691a40e`, the gate's final commit) — the
template did not drift between the two checks, so `PINNED_BLOB` in the shipped
code (`6953ac90f2568890fddbe187ad5fc8dd095041dd`) is the value from the second,
final check.

## Docs/contracts touched
- none — `docs/CHECKLIST_SCHEMA.md`'s "Basis" subsection describes the `basis`
  field's shape, which this gate does not change; only the staleness-gate
  mechanism around it changed.

## Assumptions
- Interpreted "compute `PINNED_BLOB` as the last step" as "recompute and
  re-verify right before finishing," not "defer writing any value until the
  very end" — I set a real value early (needed for the mutation-battery clones
  to have a genuinely correct pin to test against) and re-checked it unchanged
  immediately before writing this result, per the close criterion's own
  rationale (a concurrent sibling lane might land on the template first).
- Committed the change locally on `epic-569/w3-basis` (commit `8691a40e`) as
  this gate's deliverable, rather than leaving it uncommitted, because (a) the
  handoff's Required Evidence literally asks for the pytest run "at your final
  commit's HEAD," (b) the Deliverable Path Check lists this file as
  "Committed," and (c) this epic just blocked a sibling PR (#657) specifically
  for shipping e2e tests that only passed while the work was uncommitted
  (`.agent-work/569/ADMIRAL_LOG.md`, 2026-08-22 ruling) — the mutation-battery
  tests here clone from `ROOT`'s committed `HEAD`, so if my own change weren't
  committed first, the clones would test the OLD (skip-based) class instead of
  the one this gate ships, silently defeating the whole proof. I did not push
  or open a PR; `g1-integrate` is a separate gate in `execute.json`.
  Only `tests/test_checklist_engine.py` was staged and committed.

## Stop conditions hit
- none — the file's actual shape matched `plan-candidate-smallest-diff.md`'s
  assumptions; no evidence item was unproducible; no need arose to touch
  `COMMANDER_SPINE.template.json` or `scripts/checklist_engine.py`.

## Out-of-scope observations
- none.

## Workflow Feedback

- **Handoff gaps:** none — task, protected intent, close criteria, allowed
  scope, exclusions, constraints, evidence, and verification command were all
  concrete and matched the actual file at ~line 8543 exactly as described.
- **Context rediscovered:** the handoff didn't say whether the gate's own
  deliverable commit should land on the branch now or be deferred to
  `g1-integrate`; I had to read `.agent-work/569/ADMIRAL_LOG.md`'s #657 ruling
  (found via git log on this same file) to see why "commit before testing the
  clone-based mutation battery" is the safe choice here — a future handoff for
  a similarly clone-based proof could name this explicitly and save that dig.
- **Instructions improvised around:** the handoff's Required Evidence phrase
  "at your final commit's HEAD" implies a commit but doesn't say so outright;
  I committed (`tests/test_checklist_engine.py` only) as the gate's deliverable,
  reasoning from the Deliverable Path Check ("Committed") and the #657
  precedent, since the mutation-battery tests clone from `ROOT`'s committed
  `HEAD` and would silently test stale code otherwise.
- **What would have made this easier:** an explicit line in the Close Criteria
  or Constraints saying "commit this file's change before running the
  mutation-battery clone probes, since the clone reads committed HEAD, not the
  working tree" would have removed the one real judgment call in this gate.

## Return status
`complete`
