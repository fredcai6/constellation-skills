# Implementation Result

## Assigned gate
`g1` — open Constellation work in one call (`scripts/spine_lifecycle.py`)

## Completed slice
Added `scripts/spine_lifecycle.py`: the pure helpers (`worktree_path_for`, `branch_name_for`,
`archive_name_for`, `build_origin`) and `open_work(work_id, spec, *, root, base, parent,
wt_root=None)` per `LIFECYCLE_CONTRACT.md` sections 2–3. `open_work` validates the work id (reusing
`run_crew.validate_work_id`), refuses an occupied worktree path and a work id with an already-active
`engine_session`, runs `git worktree add`, scaffolds the work area (`init_work_area.init_work_area`),
compiles the spine (`generate_spine.spec_shape_faults`/`compile_spec`/`probe_spec`, imported, never
re-implemented), injects the `origin` block, re-validates (`validate_spine.validate`), self-verifies
isolation in-process (`verify_worktree_isolation.check_distinct_real`), and returns the crew-binding
values. Any failure at or after `git worktree add` rolls back the worktree and branch this call
created and re-raises. `close_work` and MCP door wiring are **not** included — g2/g3 scope.

## Scope
**Files changed:**
- `scripts/spine_lifecycle.py` (new)
- `tests/test_spine_lifecycle.py` (new, 28 tests)
- `map/INDEX.md` (regenerated via `python -m scripts.code_map build`, never hand-edited)

**Specific exclusions touched:** no — `checklist_engine.py`, `validate_spine.py`,
`mcp_spine_server.py`, `generate_spine.py`, `settings.json`, `.mcp.json`, `docs/agents/*`, and
`skills/**` are all untouched. `close_work` was not implemented; only the pure `archive_name_for`
ships, per the handoff's specific exclusion.

## Behavior changed
Yes — a new capability exists (`open_work`), but nothing else in the corpus calls it yet (no door
wiring in this gate), so no existing behavior changed.

## Map Impact
- **Structural anchors touched:** none pre-existing; `scripts.spine_lifecycle` is a new module,
  now indexed at `map/scripts.spine_lifecycle/INDEX.md` (13 entities, 3 holes) alongside its sibling
  seams `generate_spine.py`, `validate_spine.py`, `checklist_engine.py`.
- **Capabilities added:** "open Constellation work in one call" — `open_work`, the module's own
  interface, ships with no production caller yet; the MCP door (`spine_open`) is g3.
- **Decision candidates:** `SPINE_SESSION`'s exact derivation was left silent by both
  `LIFECYCLE_CONTRACT.md` and this handoff (neither states a formula, and it is untested by any close
  criterion). I judged it as `f"constellation/{work_id}"` — a work-id-scoped identity, deliberately
  **not** run through `run_crew.assignment_session_name`'s gate/role grammar, since `open_work` has no
  gate/role parameter to supply one. Flagged here per `LIFECYCLE_CONTRACT.md`'s own "where it is
  silent, the crew decides and says so" — g3/g4 should confirm or revise this before the door or
  declared-dispatch wiring depends on its exact shape.
- **Trust limitations:** none newly found; the repo already reads DEGRADED-UNPARSEABLE for map
  orientation (no `docs/architecture/` packet map), consistent with this run's own `context` gate
  evidence.

## Test mode
**Required:** test-after (per handoff)
**Satisfied:** yes — every guard has a VIOLATING and INNOCENT fixture (`tests/test_spine_lifecycle.py`).

## Evidence

### 1. Rollback fixtures — real `git worktree list --porcelain` before/after

**Late failure at step 6** (spec-shape refusal after `git worktree add` succeeded):

```
=== EVIDENCE 1: late failure at step 6 (spec-shape refusal after worktree add) ===
--- before ---
worktree /tmp/sl_evidence/repo
HEAD f87e4f1ddc3b56f1f3cb1c72d4131d47bcc1daa4
branch refs/heads/main

* main

refused: spec-shape refused: [spec-all-qualitative-postconditions] m1: every postcondition is
qualitative -- quoting validate_spine's own falsifiable-all-null wording: nothing here can ever
refuse this gate; failing at the spec is a better error than failing at the spine
--- after ---
worktree /tmp/sl_evidence/repo
HEAD f87e4f1ddc3b56f1f3cb1c72d4131d47bcc1daa4
branch refs/heads/main

* main
```

Before and after are identical: no `evwork` worktree entry, no `evwork` branch. The equivalent test
(`TestOpenWorkRollback::test_violating_late_failure_at_compile_leaves_no_worktree_or_branch`) also
covers a step-7 variant (`test_violating_late_failure_after_origin_injection_leaves_no_worktree_or_branch`)
that forces the failure specifically on the **second** `validate_spine.validate` call (the post-origin
re-validate), not the first.

### 2. `check_distinct_real` says no despite `git worktree add` exit 0 (load-bearing)

```
=== EVIDENCE 2: check_distinct_real says no despite git worktree add exit 0 ===
--- before ---
worktree /tmp/sl_evidence/repo
HEAD f87e4f1ddc3b56f1f3cb1c72d4131d47bcc1daa4
branch refs/heads/main

* main

refused: worktree isolation self-verify failed: faked: git exit 0 is not evidence
--- after ---
worktree /tmp/sl_evidence/repo
HEAD f87e4f1ddc3b56f1f3cb1c72d4131d47bcc1daa4
branch refs/heads/main

* main
```

`git worktree add` ran for real and exited 0; only `verify_worktree_isolation.check_distinct_real`
was monkeypatched to return `(False, ...)`. The worktree was still rolled back — the code does not
trust `git`'s own exit code as evidence. Test:
`TestOpenWorkSelfVerifyForcesRollback::test_violating_check_distinct_real_says_no_forces_rollback`.

### 3. `origin` round-trip through a real `claim → start → attest → advance` drive

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q -v \
    tests/test_spine_lifecycle.py::TestOriginRoundTrip
collected 1 item
tests/test_spine_lifecycle.py .                                          [100%]
1 passed in 0.05s
```

`TestOriginRoundTrip::test_origin_survives_claim_start_attest_advance` opens real work, deep-copies
`cl["origin"]`, then drives `checklist_engine.claim` → `start` → `attest` (qualitative) → `attach` +
`attest` (artifact, by evidence reference) → `advance(mechanical=True)` to `complete`, and asserts
`cl["origin"] == origin_before` byte-for-byte (dict equality) afterward. It also asserts `origin.base`
is a real 40-character commit SHA, not the literal `"HEAD"` ref the caller passed.

### Confirmatory (spot-checked)

```
$ cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_spine_lifecycle.py
............................                                             [100%]
28 passed in 0.19s

$ cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2852 passed, 3 skipped, 1121 subtests passed in 114.90s (0:01:54)
```
(Baseline was 2824 passed, 3 skipped, 1121 subtests — 2852 = 2824 + 28 new tests, exactly.)

```
$ cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
23
```
Matches the required exact baseline.

Pure helpers, spot-checked directly (`today`/`wt_root` passed in, never read internally):
```python
>>> sl.worktree_path_for("epic-559/c3-lifecycle", wt_root="/home/tommy/projects/constellation-skills-wt")
'/home/tommy/projects/constellation-skills-wt/c3-lifecycle'
>>> sl.archive_name_for("epic-559/c3-lifecycle", today="2026-08-12")
'2026-08-12-epic-559-c3-lifecycle'
```
`TestWorktreePathForRealWorktree::test_reproduces_this_runs_real_worktree` confirms
`worktree_path_for("epic-559/c3-lifecycle", wt_root=<default derived from primary_checkout()>)`
resolves to this run's own real worktree path, without hardcoding a host-specific string.

Code map regenerated (`python -m scripts.code_map build`) after staging the two new files (the
discoverer enumerates via `git ls-files`, so it only sees tracked files — the files had to be
staged **before** the rebuild for it to pick them up; see Workflow Feedback). `map/INDEX.md` now
lists `scripts.spine_lifecycle` (13 entities, 3 holes) and `tests.test_spine_lifecycle` (52 entities,
50 holes); not hand-edited.

## Docs/contracts touched
- none — `LIFECYCLE_CONTRACT.md` is read-only input to this gate, not touched.

## Assumptions
- `SPINE_SESSION`'s derivation (`f"constellation/{work_id}"`) — see Map Impact / Decision candidates
  above; the contract and handoff are both silent on the exact formula and no close criterion tests it.
- `origin.base` is resolved to the real commit SHA the new worktree's `HEAD` actually points at
  (`git rev-parse HEAD` inside the fresh worktree) rather than the raw `base` ref string the caller
  passed — matching the contract's own example (`"base": "<sha>"`) and candidate A's draft
  (`base_commit = git rev-parse <base>`).
- The active-engine-session scan (step 3) is **structural**, not filename-based: it globs
  `root/.agent-work/<work_id>/**/*.json` and inspects any dict carrying `engine_session`, rather than
  looking only for a file literally named `spine.json` — this epic's own driving spine is
  `execute.json`, and the contract's §4 close-work discussion explicitly warns against literal-name
  assumptions for the sibling problem.

## Stop conditions hit
- None. All required and confirmatory evidence passed on the first real run (no repeated-failure
  stop condition was triggered).

## Out-of-scope observations
- None beyond the `SPINE_SESSION` derivation question already recorded above.

## Workflow Feedback

- **Handoff gaps:** `open_work`'s step 9 says "Return the crew-binding values: `SPINE_FILE`,
  `SPINE_SESSION`, `SPINE_PARENT`, branch, worktree" but neither the handoff nor
  `LIFECYCLE_CONTRACT.md` states how `SPINE_SESSION` is derived from `open_work`'s actual parameters
  (`work_id`, `spec`, `root`, `base`, `parent` — no `gate`/`role`). I checked both plan-alternative
  drafts (`plan-alt-a-result.md`, `plan-alt-b-result.md`) and the critic's result for a formula; none
  gives one either, so this was genuinely open, not something I missed. I made a documented judgment
  call (see Assumptions) rather than blocking, since no close criterion in this gate tests the exact
  value and the contract explicitly authorizes crew judgment where it is silent.
- **Context rediscovered:** the bound `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` env vars in my own
  process pointed at the Commander's own top-level `execute.json` run tracker (its `execute` gate
  covers all five crew gates, not a dedicated g1 spine) — there is no per-gate MCP door binding yet
  because building that door is this same epic's g3. I did not drive or advance that spine; I tracked
  my own steps with `TaskCreate` instead and worked the handoff directly. Worth naming explicitly in a
  future handoff so the next crew doesn't spend time on the same disambiguation.
- **Instructions improvised around:** `python -m scripts.code_map build` discovers modules via
  `git ls-files`, so it silently ignores brand-new untracked files. I had to `git add` the two new
  source files *before* the rebuild for `map/INDEX.md` to pick up `scripts.spine_lifecycle` at all —
  otherwise the close criterion "the code map is regenerated because this gate adds a module" would
  have passed mechanically (`build` exits 0) while the map stayed silently stale.
- **What would have made this easier:** naming the staging-before-code-map-build ordering explicitly
  in the close criteria (or in the workbench's code-map reference) for any gate that adds a new
  tracked file — it's a real trap: the command that would appear to "regenerate the map" can succeed
  and still not include your own new module.

## Return status
`complete`
