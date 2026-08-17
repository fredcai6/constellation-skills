# Review Result

## Assigned Gate
`g2-review` — rework of PR #621's 6 net regressions (groups 1+2 only; epic #567 lane B)

## Result
`APPROVE`

## Handoff compliance
All Close Criteria met, verified against the diff and independently reproduced (not just
trusted from the pasted transcript):

- `tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_flat_work_id_finalizes_identically`
  — re-run myself: passes.
- `tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_nested_work_id_finalizes_its_own_registry`
  — re-run myself: passes.
- `tests/test_crew_delivery_addressing.py::JobAddressedDeliverySurvivesRelaunch::test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity`
  — re-run myself: passes.
- `tests/test_episode_observations.py::RealStoreTests::test_the_real_store_is_clean_under_strict`
  and `::test_the_real_store_scan_actually_examined_the_records` — re-run myself: both pass.
- `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
  — re-run myself: still **FAILED** (entity-count mismatch, 1227 vs 1226) — this is the
  required pass condition for this gate (group 3 explicitly withdrawn), not a defect.
- Full close-criteria suite `pytest tests/test_work_id_nesting.py tests/test_crew_delivery_addressing.py tests/test_episode_observations.py tests/test_crew_launcher.py -q`
  — re-run myself: **269 passed, 20 subtests passed, 0 failures.**
- Both group-1 call sites now pass `accept_mtime_only_risk="<honest reason>"` — verified
  each reason string against the actual test scenario it annotates (see Code/doc quality
  below), not a generic "no spine given."
- Episode fix: `episodes/active/epic-567-door_cmdr-b-003.md` assertion `a5` restated via
  `restate-assertion`, independently confirmed as the real write path (see Evidence
  verdict).
- No production code touched: `scripts/run_crew.py` absent from `git status --porcelain`.
- `verify_external_result` (`scripts/run_crew.py:1970`) confirmed read-only — a thin
  pass-through to `ExternalBackend().verify(...)`, its `accept_mtime_only_risk` kwarg
  (g1/PR #621) now exercised by two more callers, signature itself untouched.

## Scope drift
None. `git status --porcelain` shows exactly the Allowed Scope touched:
`tests/test_work_id_nesting.py`, `tests/test_crew_delivery_addressing.py`,
`episodes/active/epic-567-door_cmdr-b-003.md`, plus new
`.agent-work/567-b/triage-candidates/tc3-*.md`. All 6 named exclusion/stop-condition paths
independently confirmed untouched via `git status --porcelain` on each exact path (empty
output for all): `map/INDEX.md`, `scripts/run_crew.py`, `scripts/checklist_engine.py`,
`scripts/mcp_spine_server.py`, `tests/test_crew_launcher.py`, `tests/test_code_map.py`.

One pre-existing untracked file at the worktree root, `RETURN.md`, is the Commander's own
epic-level closing narrative (references PR #621 / g1's #432 fix, dated before this
gate) — not code, not part of this diff; noted below as an out-of-scope observation, not
scope drift.

## Evidence verdict
Required evidence present and independently reproduced, exceeding what was pasted:

- All 5 named tests re-run in isolation and together — all pass, matching the
  implementer's claimed counts exactly.
- Full close-criteria suite re-run — 269 passed / 20 subtests, 0 failures, matching.
- Map freshness test re-run — still red, matching the required (non-defect) outcome.
- **Episode fix — reproduced end to end, not just inspected:** seeded a scratch store
  with the pre-change episode file (`git show HEAD:episodes/active/epic-567-door_cmdr-b-003.md`),
  ran `python3 scripts/apply_episode_delta.py --delta .agent-work/epic-567-door/cmdr-b/episode-delta-g2.json --store-root <scratch>/episodes`
  — output `restated epic-567-door_cmdr-b-003.a5` — then diffed the scratch result against
  the actual working-tree file: **byte-identical**. This is stronger than checking the
  diff "looks like" the documented `restated — <reason> — original statement was: <original>`
  format; it proves the real write path produced this exact byte sequence, not a hand-edit
  dressed up to match it. `git diff --stat` on the episode file also confirms minimal
  footprint (2 insertions, 1 deletion in one file), consistent with "only `a5`'s statement
  line changed plus one appended history line."

## Code/doc quality
Minimal, honest, matches surrounding conventions:

- `tests/test_work_id_nesting.py`: `"test: exercising registry addressing (nested vs flat
  work_id), not spine-driving"` — read against `CrewRegistryAddressingTests`'s own
  docstring ("`--verify-result` must find the registry its own launch wrote") and both
  test docstrings: honest, specific, matches.
- `tests/test_crew_delivery_addressing.py`: `"test: {asking_instance} proving
  identity-free delivery discovery (job-file-not-agent-file), not spine-driving"` — read
  against `JobAddressedDeliverySurvivesRelaunch`'s own docstring ("the WRITE to the
  job/gate-addressed result path is the delivery... no agent name involved") and the test
  body's own comment (`asking_instance` deliberately never passed into the production
  call): honest, specific, matches.
- Neither reason string is the generic "no spine given" the constraint warns against;
  neither test scenario has any spine concept in scope.

### Refactoring pass (Fowler code smells)
Recorded to `.agent-work/epic-567-door/cmdr-b/g2-review/FOWLER_PASS.json`;
`scripts/verify_fowler_pass.py` exits 0 (`smells=12, flagged=[], overridden=[]`). All 12
baseline smells visited, none silently skipped — all 12 verdict `absent`, an honest outcome
for a diff this small (two one-line keyword-arg additions plus one `restate-assertion` op,
no production code). Two worth naming: **duplicated-code** — both call sites add a
similarly-shaped `accept_mtime_only_risk="test: ... not spine-driving"` keyword, but the
two reason strings are independently authored and scenario-specific, a phrasing
convention rather than copy-pasted logic, so `absent` not `flagged`. **comments-as-deodorant**
— the reason strings are load-bearing function arguments (recorded on the entry, printed
to stdout+stderr per `decision:default-refuse-not-default-warn`), not comments masking
confusing code.

## Map impact verdict
- **Evidence supports claimed change:** yes — see Evidence verdict above.
- **Constraints not violated:** yes — `decision:and-not-rescue-semantics` and
  `decision:default-refuse-not-default-warn` (both g1 `MISSION_FRAME.md`) are exercised,
  not relitigated: both fixes reach `completed` only via the explicit, loud override, and
  `ExternalBackend.verify()`'s refusal logic itself is byte-for-byte unchanged.
- **Notes match the diff:** yes — the implementer's structural anchor
  (`verify_external_result`, read-only) and capability/constraint notes match what the
  diff actually touches; no missing or overstated impact.
- **Decision candidates surfaced:** n/a — no new decision required; both fixes were fully
  specified by the Admiral's diagnosis.
- **Durable context routed:** yes — `tc3-imperative-detector-homograph-allowlist-growth.md`
  is correctly recorded as an unfiled triage candidate per this lane's
  `decision:no-issue-filing`, not silently fixed (confirmed: `scripts/verify_episode_observations.py`
  and its `EXCEPTIONS` allowlist are untouched by `git status`) or dropped.

## Reconciliation check
No `docs/architecture` map exists in this repo (confirmed: directory absent), so there is
nothing structural to reconcile against.

## Blockers
- none

## Out-of-scope observations
- `RETURN.md` (untracked, worktree root) — the Commander's own epic-level closing
  narrative, predates and is unrelated to this gate's diff. Workflow artifact, not code
  scope creep.
- `tc3-imperative-detector-homograph-allowlist-growth.md` — already correctly routed as an
  unfiled triage candidate by the implementer/Commander (confirmed accurate by me — see
  Map impact verdict).

## Workflow Feedback
- **Handoff gaps:** none — the handoff's Close Criteria, Specific Exclusions, and Stop
  Conditions translated directly into checkable survey items; no field was missing or
  ambiguous. The explicit instruction to treat the map-freshness test's continued redness
  as a *pass* condition rather than a defect was unusually clear and prevented a
  reflexive "test is failing → BLOCK" mistake.
- **Context rediscovered:** none beyond what the Map Anchors pointed at directly — the
  handoff's file/line references and the g1 `MISSION_FRAME.md` decision anchors were
  sufficient without extra digging.
- **Instructions improvised around:** the `r6-fowler` Fowler pass on a diff this small
  (two one-line keyword-arg additions, no production code) produced an all-`absent`
  record; I ran the full 12-smell walk anyway rather than treating the pass as
  self-evidently skippable, per the skill's "do NOT silently skip this item" — this
  worked cleanly and cost little, but a future reviewer facing an equally trivial diff
  might be tempted to shortcut it, so naming it here as expected friction rather than a
  gap.
- **What would have made this easier:** none — the implementer's evidence writeup and the
  episode-delta JSON being available as a structured, replayable artifact (rather than
  only a prose description) made the strongest piece of independent verification in this
  review — the byte-identical replay — straightforward to construct.

## Return status
`complete`
