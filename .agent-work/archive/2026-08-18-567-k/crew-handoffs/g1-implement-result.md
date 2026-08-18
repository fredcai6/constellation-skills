# Implementation Result

Return status: complete

## Assigned gate
g1-implement — the declared-bookend guard in `amend()` (#634)

## Completed slice
`amend()` now honors a per-gate `"bookend": true` declaration: `add` refuses inserting past the
last declared bookend; `drop`, `rescope`, and `retext-check` refuse acting on a bookend gate
regardless of status. `rescope`'s overwritable field list now includes `bookend`, which is the
engine-reachable retrofit path — and, because the new guard runs *before* the field overwrite,
setting the flag is a one-way latch (a later `rescope {bookend: false}` on that gate is refused
too). An undeclared plan (no `bookend` key anywhere) is unaffected — confirmed by dedicated
backward-compat tests and by the full pre-existing suite staying green.

## Scope
**Files changed:**
- `scripts/checklist_engine.py` — the guard implementation
- `scripts/mcp_spine_server.py` — one sentence added to `spine_amend`'s tool description
- `tests/test_checklist_engine.py` — new `AmendBookendGuard` test class

**Specific exclusions touched:** no — `run_crew.py`, `install_constellation.py`,
`LAUNCH_ORDER.template.md`, `map/INDEX.md`, `generate_spine.py`, `specs/*.spine.toml`,
`IMPLEMENTER_PLAN.template.json`, and every `*SPINE*.template.json` were not touched. No mutating
verb was ever run against a live spine — every amend in this run's tests and manual checks
targeted an in-memory or temp-file checklist built by the test helpers.

## Behavior changed
Yes. New refusal paths on `amend`'s four ops when a gate is declared `bookend: true`; zero change
to any gate with no `bookend` key.

## Map Impact
- **Structural anchors touched:** `amend()` in `scripts/checklist_engine.py` (`:2971` region) — the
  four op branches (`add`, `drop`, `rescope`, `retext-check`) each gained one guard call; one new
  nested helper `_is_bookend(tid)` added beside `_floor()`.
- **Capabilities added/changed/affected:** a plan/spine can now declare a gate frozen against
  `amend`, and can retrofit that freeze onto an already-running spine via `rescope {bookend: true}`
  (one-way latch — no engine verb can unset it once set).
- **Constraints/assumptions touched:** the schema-freedom assumption this design leans on —
  "no task-schema validator exists in `checklist_engine.py`, so an unrecognized key survives
  round-trip" — held; confirmed by grep, not just cited from the design doc.
- **Decision candidates / resolved decisions:** the `retext-check` guard was a contested design
  choice (candidate A left it open); implemented per the handoff's override — a freeze that only
  stops deletion is not a freeze.
- **Trust limitations / drift found:** `DESIGN_COMPARISON.md`/`design-B-result.md`'s literal
  `_bookend_ceiling()` formula (`max(marked_indices) + 1`) has an off-by-one that would let `add`
  append immediately after a bookend gate that is the *last* item in the checklist — exactly the
  "append after archive" case its own prose says must be refused. I implemented the corrected
  semantics (ceiling = the bookend's own index; refuse `insert_at > ceiling`) rather than the
  literal formula. See "Anything refused" below.
- **Triage candidates:** none raised — the existing `flag-candidate`/triage-worthy gaps
  (retrofitting live spines, the `execute.json` migration, template-lint for a forgotten
  declaration) are already tracked in `DESIGN_COMPARISON.md` and were not this gate's job to act on.

## Test mode
**Required:** test-first (TDD red→green)
**Satisfied:** yes — every new guard has a dedicated red→green pair; the all-or-nothing test and
the mcp-prose grep check were confirmation-only per their own item's imperative (no engine-logic
change was needed for either).

## Evidence

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py
```
**Result:** pass — `466 passed, 140 subtests passed`

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_identity.py
```
**Result:** pass — `62 passed, 14 subtests passed`

Both run in a fresh subprocess with the crew env vars unset, per #269 — never observed via this
session's own behavior.

## TDD evidence, if required

Per guard, red observed before green (all in `tests/test_checklist_engine.py::AmendBookendGuard`):

- `test_amend_add_refuses_after_last_bookend` — RED: `AssertionError: EngineError not raised` →
  GREEN after the `add()` ceiling guard.
- `test_amend_drop_refuses_bookend_gate_pending`,
  `test_amend_reproduces_measured_gap_refused_when_declared` — RED: `AssertionError: EngineError
  not raised` (both) → GREEN after the `drop()` guard. (`test_amend_drop_pending_gate_no_bookend_key_still_succeeds`
  — the backward-compat sibling — already passed before the change, as expected: it asserts
  unchanged behavior.)
- `test_amend_rescope_refuses_bookend_gate`, `test_amend_rescope_sets_bookend_flag_via_overwritable`,
  `test_amend_rescope_bookend_flag_is_one_way_latch` — RED: `EngineError: rescope g1: at least one
  overwritable field is required` (all three — `bookend` wasn't in the tuple yet, and the refusal
  guard didn't exist) → GREEN after adding the guard and `"bookend"` to `overwritable`.
- `test_amend_retext_check_refuses_bookend_gate` — RED: `AssertionError: EngineError not raised`
  (the command was silently retexted from FAIL to PASS) → GREEN after the guard.
- `test_amend_all_or_nothing_leaves_checklist_unmutated_with_bookend_violation` — confirmation only,
  passed on first run (the existing copy-then-commit structure at `:3031`/`:3177` already covers
  the new guards, since they raise before any of `new_items`/`new_tasks` is touched).

Refactor while green: no refactor pass beyond the implementation itself — each guard's shape
mirrors its neighbor's existing style (see `checklist_engine.py:3095-3163` for the four branches in
order).

## Docs/contracts touched
- `scripts/mcp_spine_server.py` — `spine_amend`'s tool `description` string gained one sentence
  naming the new refusal, so a calling agent learns of it without a failed call. No schema field,
  no handler logic changed.

## Assumptions
- None beyond what the handoff and design-B-result already established (no task-schema validator
  to update; `spine_amend` is a pure pass-through) — both were independently re-confirmed by
  reading the live source rather than trusting the citation.

## Stop conditions hit
- None. The door needed no schema change (confirmed by reading `scripts/mcp_spine_server.py:2404-2424`
  directly — `_write_amend_delta` + `run_engine("amend", *rest)`, no bookend-specific logic
  anywhere in the handler). No fenced file needed a change. Every required test could be made to
  fail before it passed. Backward compatibility held without conflicting with any guard.

## Out-of-scope observations
- `DESIGN_COMPARISON.md`/`design-B-result.md`'s `_bookend_ceiling()` formula has the off-by-one
  described above under Map Impact / Trust limitations. Worth a note back to whoever maintains
  those design artifacts, since a future reader implementing "the same way design B says" would
  reproduce a gate that fails to protect the *exact* case the design's own prose calls out
  (appending a new gate immediately after a bookend that is currently the last item). Not filing a
  separate triage entry — this result note is the record.

## Workflow Feedback

- **Handoff gaps:** none — task, intent, scope, exclusions, evidence, test mode, and stop
  conditions were all present and internally consistent. The handoff's own citation of design-B's
  formula (step 1: "One helper... answering 'is this gate a declared bookend?'") left me free to
  implement the ceiling arithmetic myself rather than copy design-B's formula verbatim, which
  turned out to matter (see above) — worth calling that latitude out explicitly in a future
  handoff, since a less careful reader might copy the formula instead of deriving it from the
  stated requirement ("an insert may not land after the last bookend-marked gate").
- **Context rediscovered:** none — the design-B-result.md worked example (§3) gave the exact
  Commander-spine index arithmetic needed to derive the off-by-one; no extra digging required.
- **Instructions improvised around:** none — no engine call or instruction failed to cover the
  actual situation. `IMPLEMENTER_PLAN.template.json`'s `constraints` field was used to record the
  "single source of truth" requirement on the helper (own plan item m1), not improvised around.
- **What would have made this easier:** the handoff cites design-B's helper and ceiling logic as
  the thing to implement; naming explicitly that the ceiling *formula* (not just the "one helper"
  shape) is open to correction against the stated requirement would have removed a moment of doubt
  about whether to follow the design doc literally or the requirement prose when the two disagreed.

## Session

Own `IMPLEMENTER_PLAN.json` claimed and driven through the engine (no spine was bound in this
process's environment — only `SPINE_PARENT` was set, so per `constellation-implementer`/global
doctrine this run authored and drove its own plan rather than a bound spine):
`.agent-work/567-k/crew-scratch/g1-implement-implementer-attempt-1-5d572aaaea17/IMPLEMENTER_PLAN.json`,
session id `g1-implement-implementer-attempt-1`. All 9 items (`m0-context` through `m8-result`)
advanced to `complete` through the CLI (`scripts/checklist_engine.py`, vendored copy — this repo
*is* the constellation-skills source). Lease released as the final action after this result was
written.
