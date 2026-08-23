# Implementer Handoff

## Gate
g1 (g1-implement)

## Task
In `tests/test_checklist_engine.py`, class `CommanderSpineBasisFields` (~line 8543), replace the
whole-repo-`HEAD` pin with a **blob-OID pin** on `skills/commander/templates/COMMANDER_SPINE.template.json`,
and replace **skip-on-drift** with **FAIL-on-drift**.

## Protected Intent
The 3 test methods on `CommanderSpineBasisFields` must keep asserting exactly what they assert
today (`EXPECTED_BASIS`'s shape on `plan.c2/c4/c5`) when the template is unchanged. Only the
*staleness gate* they share changes: what it pins to, and what it does on drift.

## Test Mode
Test-after allowed — this gate IS the test file; there is no separate production code to drive
with a red-first cycle. The new mutation-battery tests you add ARE the TDD-style proof: write them
to demonstrate RED (template mutated) and GREEN (unrelated commit) before calling the gate done.

## Close Criteria
- `PINNED_HEAD` (whole-repo `git rev-parse HEAD`) is replaced by `PINNED_BLOB`, the blob OID of
  `skills/commander/templates/COMMANDER_SPINE.template.json` via
  `git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json`.
- `PINNED_BLOB` is computed and set as the **last** implementation step, immediately before you
  hand back — not at the start of your dispatch — because a sibling wave-3 lane (`w3-promote`)
  owns edits to that exact template this wave and may land on the shared branch first; recompute
  right before finishing so the pin reflects the template's actual current content.
- `_skip_if_head_moved` is replaced by `_fail_if_template_drifted`: on mismatch it calls
  `self.fail(...)` — never `self.skipTest(...)`. Keep the existing
  `self.assertEqual(out.returncode, 0, out.stderr)` guard so a `git rev-parse` failure stays
  distinct from a genuine drift failure (they must not be conflated into the same `self.fail`
  call).
- The fail message contains, verbatim-checkable: the word "stale" (as in "proof is stale"), the
  pinned blob OID, the current blob OID, and the exact literal re-run command
  `git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json`, plus an
  instruction to paste the result into `PINNED_BLOB`.
- All 3 existing test methods' first line changes from `self._skip_if_head_moved()` to
  `self._fail_if_template_drifted()`. `EXPECTED_BASIS` and `_load_spine` are untouched.
- The class docstring's second paragraph (currently "Pinned to this gate's shipped git HEAD ...
  If HEAD has moved past the pinned commit, skip rather than assert against a template shape this
  test was never written against.") is rewritten to describe blob-OID pinning to the template
  file and fail-on-drift — it must not describe the retired whole-repo-HEAD + skip design after
  this change ships.
- Any inline comment near `PINNED_BLOB` says "g1 dispatch" (this gate's own id), never "g2" — this
  execute.json has only one gate.
- Two new test methods (or equivalent) proving both directions, run against an **isolated clone**
  (`git clone --local . /tmp/<scratch-name>`), never the shared worktree in place:
  1. **Template-edit → RED**: in the scratch clone, mutate one byte of
     `skills/commander/templates/COMMANDER_SPINE.template.json` and commit; run
     `CommanderSpineBasisFields` against the scratch clone (e.g. via `subprocess` invoking pytest
     with `cwd=<scratch>`); assert all 3 tests **FAIL** (not skip, not error), each failure message
     containing the substring `"proof is stale"` and the literal command string
     `"git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json"`.
  2. **Unrelated commit → GREEN**: in the scratch clone, commit a change to a file OUTSIDE
     `skills/commander/templates/` (never touch the template); run `CommanderSpineBasisFields`
     against the scratch clone; assert all 3 tests **PASS**.
  Tear down the scratch clone when done (e.g. `shutil.rmtree`).
- `python3 -m pytest tests/test_checklist_engine.py::CommanderSpineBasisFields -q -rs` passes
  (GREEN, no skips) at your final commit's HEAD.

## Allowed Scope
- `tests/test_checklist_engine.py` only.
- The isolated scratch clone your new mutation-battery tests create/destroy under `/tmp` at test
  run time is fine — it is not a repo artifact.

## Specific Exclusions
- Do **not** edit `skills/commander/templates/COMMANDER_SPINE.template.json` — read-mostly this
  wave, owned by the sibling lane `w3-promote`.
- Do **not** edit `scripts/checklist_engine.py`.
- Do **not** touch any qualitative-condition population or roll the `basis` field out beyond
  `plan.c2/c4/c5` — out of this lane's scope entirely.
- Do **not** run your mutation-battery tests' mutating `git commit` calls against the live shared
  worktree (`/home/tommy/projects/569-w3-basis`, branch `epic-569/w3-basis`) — other lanes are
  concurrently active there. Isolated `/tmp` clone only.

## Constraints
- No `self.skipTest` anywhere in the new drift path.
- `PINNED_BLOB` is a plain string blob OID (40 hex chars), computed last, right before you finish.
- Keep the file's existing `subprocess` + `git` idiom (as `_skip_if_head_moved` already uses) —
  don't introduce a new dependency or module-level helper for this single caller.

## Map Anchors (inbound)
- **Map entry point:** repo map is DEGRADED-UNPARSEABLE this run; start instead at
  `tests/test_checklist_engine.py:8543` (the class itself) — see
  `.agent-work/w3-basis/MISSION_FRAME.md` for the full substitute-pinned frame.
- **Structural:** `tests/test_checklist_engine.py::CommanderSpineBasisFields`.
- **Capability:** red-proof pinning for the commander spine template's basis-field shape.
- **Constraints/assumptions:** file-ownership (this file only), no-skip-on-drift, blob-oid-granularity,
  cheap-re-verify, prove-both-directions.
- **Decision anchors:**
  - `decision:blob-oid-not-head` — pin the blob OID, not repo HEAD.
    `@grade: settled/human · leans g1-implement`
  - `decision:drift-fails` — FAIL, never skip, on divergence.
    `@grade: settled/human · leans g1-implement`
  - `decision:ship-the-re-verify-path` — the re-verify path must be cheap and documented.
    `@grade: settled/human · leans g1-implement`
  - `decision:prove-both-directions` — both directions of the granularity fix must be demonstrated.
    `@grade: settled/admiral · leans g1-implement`
- **Evidence expectations:** the pin tracks file content not repo HEAD; drift fails not skips; the
  re-verify path is genuinely cheap (one `git rev-parse` invocation).
- **Map confidence flags:** none beyond the DEGRADED map noted above (not blocking — this gate's
  frame is cut from direct file reads, not the map).

## Deliverable Path Check
- **Committed** — `tests/test_checklist_engine.py`; verified via `git check-ignore tests/test_checklist_engine.py` exiting 1 (not ignored) before dispatch.

## Required Evidence
- Full diff of `tests/test_checklist_engine.py` (and nothing else).
- `python3 -m pytest tests/test_checklist_engine.py::CommanderSpineBasisFields -q -rs` output,
  pasted verbatim, showing 3 passed (or however many tests you end with, but zero skipped).
- The mutation-battery run's own output (both directions), pasted verbatim, showing the RED case's
  exact failure message text and the GREEN case's pass.
- The final computed `PINNED_BLOB` value and the exact command used to compute it.

## Wiring Grep
`none — this slice adds no new production symbol; it only changes a test class's internal
mechanism and adds test methods, which are called by the test runner itself, not by other code.`

## Verification Commands
```bash
python3 -m pytest tests/test_checklist_engine.py::CommanderSpineBasisFields -q -rs
```

## Suggested Model Tier
simple bounded — one test class, ~15-40 line change, fully specified mechanism (smallest-diff
candidate, converged and critic-cleared).

## Authority
The mechanism's shape (blob-OID pin, fail-not-skip, inline re-verify command) is decided —
smallest-diff candidate, converged in `.agent-work/w3-basis/PLAN_ALTERNATIVES.md`, critic-cleared
in `.agent-work/w3-basis/PLAN_CRITIC.md`. Do not re-litigate that choice; if you find it doesn't
fit the actual code, stop and report why rather than substituting your own mechanism.

## Stop Conditions
Stop and return if: the file's actual current shape differs materially from what
`plan-candidate-smallest-diff.md` assumed in a way that invalidates the mechanism; a required
evidence item cannot be produced; you would need to touch `COMMANDER_SPINE.template.json` or
`scripts/checklist_engine.py` to satisfy a close criterion.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/w3-basis/crew-handoffs/g1-implement-implementer-result.md` before ending your turn.
