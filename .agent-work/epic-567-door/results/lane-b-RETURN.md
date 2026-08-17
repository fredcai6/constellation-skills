# RETURN — cmdr-567-b (#432 ExternalBackend refuses a spineless success)

## 0. Post-return rework (Admiral-diagnosed, addressed before this return stands)

After this return was first sent, the Admiral diagnosed 6 net regressions in PR #621
against `main` (all reproduced locally, 2.65s, not a Windows artifact) and instructed a
3-group fix, then withdrew group 3 in a follow-up correction. Addressed through the engine
via a reopen + amend (new gate `g2`, implement + review + integrate), not by editing
outside it. Final state:

- **Groups 1+2 (this lane's to fix): DONE.**
  - 3 tests that encoded the deleted mtime-only contract
    (`test_work_id_nesting.py::CrewRegistryAddressingTests::test_flat_work_id_finalizes_identically`,
    `::test_nested_work_id_finalizes_its_own_registry`,
    `test_crew_delivery_addressing.py::JobAddressedDeliverySurvivesRelaunch::test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity`)
    now pass the explicit, honest `accept_mtime_only_risk="<reason>"` naming what each
    scenario actually proves (registry addressing; identity-free delivery discovery — neither
    has a spine concept in scope) — never a fictitious `--spine`, never a weakened refusal.
  - Episode `epic-567-door_cmdr-b-003` assertion `a5` tripped the strict imperative-detector
    guard on a past-tense/imperative homograph ("read"). Fixed via `restate-assertion`
    (rephrase "read" → "reading"), not by adding a 12th entry to the guard's already-11-entry
    exception list, per the Admiral's explicit instruction. Recorded as triage candidate
    `tc3-imperative-detector-homograph-allowlist-growth.md` — the same "check that cannot
    fail" family, wearing the opposite face: a check whose *failures* are absorbed into a
    growing allowlist rather than diagnosed at the root.
  - Local, this session:
    ```
    $ python -m pytest tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_flat_work_id_finalizes_identically \
        tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_nested_work_id_finalizes_its_own_registry \
        tests/test_crew_delivery_addressing.py::JobAddressedDeliverySurvivesRelaunch::test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity \
        tests/test_episode_observations.py::RealStoreTests::test_the_real_store_is_clean_under_strict \
        tests/test_episode_observations.py::RealStoreTests::test_the_real_store_scan_actually_examined_the_records \
        tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build -v
    ...
    FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
    1 failed, 5 passed in 2.55s
    ```
    5/6 green; the 6th is group 3, left red by design (below).
  - Full close-criteria suite: `python -m pytest tests/test_work_id_nesting.py
    tests/test_crew_delivery_addressing.py tests/test_episode_observations.py
    tests/test_crew_launcher.py -q` → **269 passed, 20 subtests passed**.
- **Group 3 (map/INDEX.md staleness): WITHDRAWN by the Admiral, left red.** The Admiral's
  first message instructed regenerating `map/INDEX.md`; a follow-up correction withdrew it
  after lane C's PR hit the **identical** staleness on the **identical** generated file in
  the same wave — two independent PRs racing to regenerate one committed generated artifact,
  exactly the failure open issue **#544** predicts ("map/INDEX.md is generated, committed
  and freshness-tested — so it conflicts on every parallel branch"). I regenerated it once
  locally, then reverted (`git checkout -- map/INDEX.md`) per the correction. `git diff
  --stat -- map/INDEX.md` on this branch is empty — untouched.
  `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
  is confirmed still red above, by design. **Recorded per the Admiral's request:** #544 is
  now evidenced by two simultaneous, independent wave-lane collisions on the same generated
  artifact — stronger than the issue's own original filing. The Admiral regenerates
  `map/INDEX.md` once, centrally, post-merge.
- `git diff --stat main..feat/567-b-external-backend -- scripts/run_crew.py tests/test_crew_launcher.py tests/test_work_id_nesting.py tests/test_crew_delivery_addressing.py episodes/active/epic-567-door_cmdr-b-003.md`:
  ```
  episodes/active/epic-567-door_cmdr-b-003.md |  55 +++++
  scripts/run_crew.py                         | 222 +++++++++++++++---
  tests/test_crew_delivery_addressing.py      |   1 +
  tests/test_crew_launcher.py                 | 334 +++++++++++++++++++++++++---
  tests/test_work_id_nesting.py               |   5 +-
  5 files changed, 558 insertions(+), 59 deletions(-)
  ```
  (`scripts/run_crew.py`/`test_crew_launcher.py` are g1's original diff, unchanged by this
  rework; `test_work_id_nesting.py`, `test_crew_delivery_addressing.py`, and the episode file
  are g2's rework diff. `checklist_engine.py`/`mcp_spine_server.py` remain untouched
  throughout — confirmed absent from every commit.)
- Driven through the engine: reopened the archived spine's `execute` step (cascaded
  reconcile/triage/review/feedback/archive back to pending), amended `execute.json` with a
  new `g2` gate (implement + review + integrate), dispatched fresh implementer/reviewer
  crews, re-verified independently, re-ran reconcile/triage/review/feedback, re-archived,
  released the lease. `g2-integrate.c1`'s check-text (authored before the Admiral's
  mid-flight correction, so it still bundled `test_code_map.py` into one command) could not
  be rescoped in place — the gate was already `in-progress`, and `rescope`/`amend` both
  require `pending`. Waived (authority `admiral`) with the real, correct 4-file verification
  pasted into the waiver reason, rather than forcing a status transition the engine does not
  offer mid-gate. Recorded as an episode (`epic-567-door_cmdr-b-004`).
- Not merged. Pushed to `feat/567-b-external-backend` (commits `710c340d..2ac82664`).
  `checklist_engine.py`/`mcp_spine_server.py` untouched throughout, per the standing fence
  (lane A live in them, confirmed still respected).

## 1. Verdict

Delivered. `ExternalBackend`'s verification path on `scripts/run_crew.py` no longer
verifies completion on result-artifact mtime alone. It now **default-refuses** without
spine evidence or an explicit, reasoned override — a spineless-but-fresh dispatch can no
longer read as a clean success by default. Not an honest null: this is a working,
independently-verified fix, reviewed and APPROVEd, PR open.

## 2. Isolation evidence

```
$ py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend
```
(exit 0, run at bootstrap before any git operation)

## 3. Refuse or report — settled from the code, both built

Read `ExternalBackend.dispatch()`/`.verify()` before designing (see `PROBLEM_STATEMENT.md`
for the full trace). Conclusion: **refusal is possible only when the caller can name a
verification target; report is the honest fallback when it cannot.** Both are built:

- **Refuse** — real and exercised. When a caller names `--spine` (dispatch-time) or
  `--verify-spine` (verify-time, checked independently — the dispatcher usually only
  learns the crew's real plan path *after* it returns), `ExternalBackend.verify()` requires
  `spine_terminal(spine, root)` (AND, never rescue/OR, with any result also given) —
  `scripts/run_crew.py` `ExternalBackend.verify()`, new method, ~L1740.
- **Report** — the honest fallback. When no spine target is nameable at all, mtime-only
  completion is still *reachable*, but never the silent default: it requires an explicit,
  reasoned `--accept-mtime-only-risk "<reason>"`, recorded on the entry
  (`mtime_only_risk_accepted`) and printed to **both** stdout and stderr — never a quiet
  pass. Absent both spine evidence and that override, the default is REFUSE (exit 1), not
  a warned-through pass — this is the fix's core behavior change (see §4).

The wrapper genuinely cannot refuse unconditionally: the crew's own plan/spine path is
chosen by the crew when it starts, not known to the dispatcher at dispatch time in the
common case (this is exactly why `--spine` was refused outright before this fix — see
`PLAN_ALTERNATIVES.md` Candidate B, the untaken road). Making `--spine` *mandatory* at
dispatch time would need a coordinated handoff/doctrine change across skills this lane
does not own this wave — floated as triage candidate `tc2`, not built.

## 4. The red-proof, against the shipped path, with count

**Pre-fix, reproduced against the shipped `RC.main` CLI entrypoint** (no fixture):
`tests/test_crew_launcher.py::test_verify_result_absent_then_present_marks_completed`
dispatched an external crew, wrote **only** a fresh result artifact (zero spine evidence,
matching #432's actual evidence exactly), and `--verify-result` returned exit 0 /
`completed`. Confirmed once at `understand` (before any edit) and again independently by
the implementer, the Commander, and the reviewer (three separate re-runs, same result).
One test enumerated, one item found red — the whole point of this lane. Then an
independent, non-pytest, fresh-process reproduction (Commander, this session):

```
$ py scripts/run_crew.py --root $TMP --work-id demo --gate g1 --role implementer \
    --handoff .../g1-implementer.md --result .../g1-implementer-result.md \
    --backend external --model sonnet
$ echo RETURN > .../g1-implementer-result.md   # crew drives no spine at all
$ py scripts/run_crew.py --root $TMP --verify-result constellation/demo/g1/implementer/attempt-1
REFUSED: no spine evidence and no --accept-mtime-only-risk given for ... see #432
exit=1
```

**Green**, same scenario, explicit override:
```
$ py scripts/run_crew.py --root $TMP --verify-result ... --accept-mtime-only-risk "demo: no spine target known"
RISK ACCEPTED: ... marked completed on a fresh result artifact alone ... (see #432)
[printed to stdout AND stderr]
verify ... -> fresh (completed)
exit=0
```

Full suite after the fix: **217 passed** (re-run independently 3 times: implementer,
Commander, reviewer — identical count each time).

## 5. Fresh-process validation

Both demonstrations in §4 were run as real subprocesses (`py scripts/run_crew.py ...`,
new Python interpreter per invocation, explicit `--root` pointing at a scratch tmp dir) —
not an in-session import or a monkeypatched call. This also holds for the pytest run:
each `python -m pytest tests/test_crew_launcher.py -q` invocation is itself a fresh
process reading `scripts/run_crew.py` from disk. Per `decision:in-session-observation-is-
not-evidence`: this fix lives in `scripts/run_crew.py`, a standalone script with no
installed-vs-worktree hook-binding hazard (unlike `checklist_engine.py`/
`mcp_spine_server.py`, which I did not touch) — the worktree copy is the one under test in
every command above.

## 6. What was deleted

Deleted: `ExternalBackend.dispatch()`'s blanket refusal of `--spine` (the mechanism that
made a refuse-capable check impossible to build at all). Deleted as a **silent** path:
mtime-only completion no longer passes unqualified — every path to a `completed` verdict
either passed a real `spine_terminal` check or required an explicit, loud, recorded
`--accept-mtime-only-risk`. What survives, by design and stated in `PLAN_ALTERNATIVES.md`:
mtime-only-with-an-override remains *reachable*, because a caller genuinely without any
spine target to name cannot be forced through a refusal without inventing evidence — that
survival is a finding (see §3), not a shortfall.

## 7. Touched paths

- `scripts/run_crew.py` (the fix)
- `tests/test_crew_launcher.py` (new tests; 4 existing test scenarios intentionally
  rewritten and named: `test_external_dispatch_refuses_spine`,
  `test_verify_result_absent_then_present_marks_completed`,
  `test_verify_is_uniform_across_backends`,
  `test_both_backends_verify_exists_and_fresh_identically`)
- `.agent-work/archive/2026-08-16-epic-567-door-cmdr-b/` (this run's archived work area —
  spine, execute plan, crew handoffs/results, mission frame, plan alternatives, problem
  statement, reconcile note, REPLAN_INPUT.json)
- `.agent-work/567-b/triage-candidates/tc1-*.md`, `tc2-*.md`, `tc3-*.md` (not filed)
- `episodes/active/epic-567-door_cmdr-b-{001,002,003,004}.md` (4 episodes)
- Rework only (g2, post-return): `tests/test_work_id_nesting.py`,
  `tests/test_crew_delivery_addressing.py` (one `accept_mtime_only_risk=` call site added
  each), `episodes/active/epic-567-door_cmdr-b-003.md` (via `restate-assertion` only).
  `map/INDEX.md` touched locally then reverted — final diff on this branch is empty.
- No edits to `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py` (lane A's
  fence, respected throughout — confirmed absent from every commit's diff).

## 8. The lane-A interaction

Lane A's measured ground truth (pasted in the launch order): "a role agent reaching its
**own** spine through the door is impossible — no verb binds an existing spine;
`spine_open` only mints." This lane's own dispatched crews hit exactly that: both the
implementer and reviewer subagents found `spine_status` reporting "no spine is bound to
this door" (expected — `ExternalBackend` spawns nothing, binds nothing) and correctly
built their own plan/survey files driven via the CLI fallback, per their skills' own
documented instructions for the unbound case. **My check would NOT have refused either of
them**: both drove a real, engine-gated plan/survey to completion (visible in their own
`IMPLEMENTER_PLAN.json`/`review.json` journals, now archived), so `spine_terminal` on
those files reads genuinely terminal — the fix correctly distinguishes "structurally
unable to bind, but drove its own plan anyway" (this run's actual crews) from "drove
nothing at all" (#432's crew). The one place the two lanes touch: my fix's refuse-path
depends on a caller (a Commander) being able to *name* the crew's plan/spine path at
verify time; lane A's finding that no verb binds an existing spine is exactly why that
path can only ever be named after the fact by convention, not bound automatically by the
door — this is the same structural gap from two different angles, not a collision. No
architecture/structural change was needed on my side to accommodate it.

## 9. PR

**#621** — https://github.com/fredcai6/constellation-skills/pull/621 (OPEN, not merged —
per the launch order, this Commander does not merge).

## 10. Triage candidates (not filed)

- `.agent-work/567-b/triage-candidates/tc1-crew-backend-design-doc-drift.md` —
  `docs/superpowers/specs/2026-07-07-crew-backend-design.md` Decision 2's "never forked"
  prose is now stale (intentionally narrowed for `ExternalBackend` only, evidence-backed).
  Doc-only, small, out of this lane's stated file ownership.
- `.agent-work/567-b/triage-candidates/tc2-mandatory-spine-at-dispatch.md` — whether a
  future wave should make `--spine` mandatory at dispatch time, closing the remaining gap
  structurally rather than by convention. Contingent on observing real
  `mtime_only_risk_accepted` frequency after this lands.
- `.agent-work/567-b/triage-candidates/tc3-imperative-detector-homograph-allowlist-growth.md`
  (new, post-return rework) — the episode store's strict imperative-detector guard cannot
  tell a past-tense/imperative homograph ("read", "run", "write", ...) from an actual
  instruction; its remedy channel is a hand-maintained exception list already 11 entries
  long across 4 prior runs before this one's own near-miss. Worth a future pass at the
  detector itself, or at least treating the allowlist's own growth rate as a signal.

## 11. Workflow feedback

- The cold plan critic (bias-to-yes, fresh agent, no authoring context) earned its keep
  here: it caught a genuine design bug (a `result=None` crash the first draft would have
  shipped) and a genuine intent-fit gap (the first draft left the mission's own bar unmet
  for the dominant case) *before* any implementer was dispatched. Both are recorded as
  episodes.
- `REPLAN_INPUT.json`'s schema (`../constellation-replan/templates/REPLAN_INPUT.template.json`)
  ships `completed_outcomes: []` with no worked example of a member's shape, and its
  sibling arrays are inconsistent about the id field name (`id` elsewhere, `issue_id`
  here) — cost three refusal/fix/retry cycles at the very end of `execute`, recorded as an
  episode. A one-entry worked example in the template would remove this friction entirely.
- Everything else — the engine CLI fallback pattern (installed copy for my own spine,
  worktree copy broken for red-proofs), crew dispatch via `run_crew.py --backend external`
  + Agent-tool subagents + `--verify-result`, the archive gate's advance-then-release
  ordering — worked exactly as documented once the sequencing was followed literally.
