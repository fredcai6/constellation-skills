# Review Result

## Assigned Gate
g1

## Result
APPROVE

## Handoff compliance
Fully satisfied. `git show e11801972c63c969be88f904afe0fa9bbb6d8fad -- scripts/run_crew.py` shows `_crew_door_env`'s `spine is None` branch now does:

```python
env = crew_env(parent=resolved_parent, scratch_dir=scratch_dir)
env.pop("SPINE_FILE", None)
env.pop("SPINE_SESSION", None)
return env
```

— both vars cleared together, matching `decision:clear-both-or-neither` exactly (no path clears one alone). `crew_env`'s docstring drops the "(this is what lets the Admiral's own bootstrap...)" framing and states its own contract is unchanged while noting `_crew_door_env` no longer relies on it for `spine=None`. `_crew_door_env`'s docstring drops the "...exactly as `crew_env()`'s own contract already promises" claim and states the new "no `spine` means NO door at all" contract, naming `decision:clear-both-or-neither`. `crew_env` itself is textually unchanged in signature and body (only its own docstring gained one clarifying note); confirmed by diff — the second hunk touches only `_crew_door_env`'s docstring and body.

All named test edits are present verbatim:
- `test_dispatch_without_spine_leaves_ambient_pair_untouched` renamed to `test_dispatch_without_spine_gets_no_door`, rewritten to `assertNotIn("SPINE_FILE", env)` / `assertNotIn("SPINE_SESSION", env)` instead of equality against ambient values.
- The dangling cross-reference in `test_dispatch_without_spine_binds_neither_var`'s comment now names `test_dispatch_without_spine_gets_no_door`.
- New `test_resume_via_cli_backend_with_no_stored_spine_gets_no_door` exercises `CliBackend().resume(...)` directly with a real non-empty ambient pair (`/admiral/EPIC_SPINE.json` / `constellation/epic/admiral`) — not `no_ambient_spine_env()`-stripped — and asserts absence.
- `ParentLeaseHeartbeatTests::test_dispatch_skips_parent_heartbeat_in_shared_spine_case` → `test_dispatch_heartbeats_parent_lease_when_spine_is_none`, and the resume sibling likewise, both rewritten to assert the parent heartbeat now always advances (`assertGreater(self._last_heartbeat(spine), before)`), since a `spine=None` child structurally cannot share the parent's pair anymore.
- `_parent_lease_heartbeat`'s own comparison logic is untouched (no hunk touches it).

## Scope drift
None. `git show --stat` lists exactly the two allowed files: `scripts/run_crew.py` (25 changed lines) and `tests/test_crew_launcher.py` (106 changed lines). No hunk touches `crew_env`'s signature/behavior, `--spine`'s meaning, `SPINE_PARENT`, `CREW_SCRATCH_DIR`, the registry schema, or `_parent_lease_heartbeat`'s comparison logic.

## Evidence verdict
Independently reproduced everything the handoff and IMPLEMENTER_RESULT claimed, plus the real-child spot-check named by `decision:verify-against-a-real-child`:

- `py -m pytest -q tests/test_crew_launcher.py` → **262 passed** (matches claim).
- `py -m pytest -q` (full suite) → **3729 passed, 9 skipped, 1 failed** — the same single `MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build` failure, same `5724` vs `5723` mismatch.
- Bisected independently: since the worktree was already clean at the committed diff, used `git checkout 135c34eb -- scripts/run_crew.py tests/test_crew_launcher.py` (equivalent to the implementer's `git stash` bisection) to restore the pre-change file content, reran the map-freshness test alone → **1 passed**. Restored `git checkout HEAD -- scripts/run_crew.py tests/test_crew_launcher.py`, reran → **fails again**, with the tree confirmed clean afterward (`git status --short` shows only my own `.agent-work/w3-door/` scratch, untracked). This independently confirms the failure is caused by this diff (the new test method bumping the map's committed entity count) and is not a pre-existing, unrelated defect.
- Red/green proof on the four new/rewritten test methods: reverted only `scripts/run_crew.py` to the base commit (kept the fixed test file), reran the four tests by name — all four genuinely **FAIL** (`AssertionError: 'SPINE_FILE' unexpectedly found in {...}`) against the pre-fix implementation. Restored the fixed source; all 262 tests pass again. This proves the tests are not vacuous.
- **`decision:verify-against-a-real-child`**: built a throwaway fake `claude` launcher binary (`/tmp/g1review-realchild/bin/claude`) that dumps its own real process environment, set a genuinely non-empty ambient `SPINE_FILE=/tmp/g1review-realchild/AMBIENT_SPINE.json` / `SPINE_SESSION=constellation/ambient-fake/commander` in the dispatching shell, and ran `python3 scripts/run_crew.py --backend cli --command claude --work-id g1review-realchild --gate g1 --role reviewer --parent test-parent` (no `--spine`) as a real OS subprocess (`subprocess.run`, not a mock). Captured stdout from the actually-spawned child:
  ```
  SPINE_FILE=<UNSET>
  SPINE_SESSION=<UNSET>
  SPINE_PARENT=test-parent
  ```
  `SPINE_PARENT` correctly bound to `test-parent` proves the env dict reached the child intact (the launch machinery worked); `SPINE_FILE`/`SPINE_SESSION` being `<UNSET>` proves active clearing held for a genuinely spawned child process, not only a mocked unit-test env-dict assertion. Scratch dir removed after capture. This independently reproduces the Commander's own claimed real-dispatched-child spot-check.

## Code/doc quality
Minimal, behavior-focused diff: the fix is a 3-line branch-local change (`crew_env(...)` call unchanged, two `env.pop` calls added). Both docstrings correctly state the new contract and drop the specific contradictory clauses the close criteria named. Naming and structure match the surrounding file's conventions.

**Fowler refactoring pass** (recorded to `.agent-work/w3-door/FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0 — `smells=12, flagged=[], overridden=['comments-as-deodorant']`): 11 of 12 baseline smells are absent. One is `overridden`: **comments-as-deodorant** — both docstrings are dense and rationale-heavy, but this matches this file's own established, repo-wide documentation convention (every function in `scripts/run_crew.py` carries an equally dense rationale-bearing docstring) and `docs/agents/CREW_CONTEXT.md`'s "Evidence You Owe Back" / `@grade:` decision-recording doctrine — the prose documents a subtle historical bug (a mismatched file/identity pair) that is not recoverable from the code alone, not a cover for unclear code (the code itself is a trivially readable 3-line branch).

## Map impact verdict
- **Evidence supports claimed change:** yes — reproduced directly (see Evidence verdict above), including the real-child spot-check.
- **Constraints not violated:** yes — `decision:clear-both-or-neither` (both cleared together) and `decision:verify-against-a-real-child` (both the implementer's and my own independent real-subprocess evidence) both honored.
- **Notes match the diff:** yes — the implementer's Map Impact notes name exactly the two structural anchors the diff actually touches (`_crew_door_env`'s body, `crew_env`'s docstring only) and correctly note the map is DEGRADED-UNPARSEABLE with no citable baseline.
- **Decision candidates surfaced:** n/a — both decisions were already fixed/settled going in (`@grade: settled/admiral` and `settled/human`), nothing new required authority.
- **Durable context routed:** yes — the map/INDEX.md staleness (5723→5724) is correctly routed as an out-of-scope observation for Commander/Cartographer at wave closeout, not fixed mid-wave against three concurrent sibling lanes. I additionally recorded this as a formal triage candidate (`tc1`) in my own survey.

## Reconciliation check
None. Map is DEGRADED-UNPARSEABLE per `.agent-work/w3-door/map-orientation.json` — no citable structural baseline exists to reconcile against. The change is architecturally narrow (one internal branch of one already-existing function, plus its own test file) and introduces no new module, seam, or public contract.

## Blockers
- none

## Out-of-scope observations
- `map/INDEX.md`'s committed entity count is stale by exactly one (5723 → 5724), purely because this gate's one new test method (`test_resume_via_cli_backend_with_no_stored_spine_gets_no_door`) bumps the map's tracked entity count. This is the one expected pre-existing failure named in the handoff's Close Criteria and is correctly out of this lane's file ownership this wave. Recommend a single `python -m scripts.code_map build --root .` regen at wave closeout after all sibling lanes land, rather than per-lane (echoing the implementer's own recommendation). Flagged as triage candidate `tc1` in my survey (`.agent-work/w3-door/g1-review/review.json`).

## Workflow Feedback
- **Handoff gaps:** none of substance. One minor ambiguity: the handoff's "Survey State Location" is `.agent-work/w3-door/g1-review/review.json`, but I am a Task-tool subagent with no `mcp__spine__*` tool and no MCP door bound to my own process (my dispatcher's `SPINE_FILE`/`SPINE_SESSION` env vars resolve to the Commander's own spine, not mine, per this dispatch's explicit instruction not to touch `mcp__spine__*`). The constellation-reviewer skill's default instruction ("spine_status is your first call... do not author a survey of your own when a spine is already bound") reads as if it conflicts with that instruction, since env vars for a bound spine WERE present. I resolved this by treating "bound for you" as meaning reachable through my own tool surface, which it was not — so I authored my own survey and drove it entirely through `checklist_engine.py`'s plain `--file` CLI mode (never the MCP door), which is a mechanism distinct from the door and does not touch the dispatcher's spine. This worked cleanly but the skill text does not explicitly name this exact case (dispatched subagent, no MCP tool present, spine env vars visible but not yours) — a one-line clarification in the skill ("if the spine's env vars are visible but no mcp__spine__* tool is on your surface, that spine is not reachable and not yours: build your own survey via the CLI, never the door") would remove the ambiguity for the next reviewer subagent.
- **Context rediscovered:** had to read `scripts/run_crew.py`'s `CliBackend.dispatch`/`build_parser`/`launch_process` to work out how to construct a real, genuinely-spawned dispatch for the `decision:verify-against-a-real-child` check (required flags, that `env=` fully replaces rather than merges into the child's environment via `subprocess.run`, and that `crew_env` seeds from `dict(os.environ)` so `PATH` still reaches the fake launcher). None of this was named in the handoff's Map Anchors (map is DEGRADED-UNPARSEABLE, as noted there) — this was source-reading, same as the implementer's own experience.
- **Instructions improvised around:** the constellation-reviewer skill's default first move ("spine_status is your first call... claim the checklist lease with the engine [via MCP]") does not fit a Task-tool subagent with no `mcp__spine__*` tool on its surface. Followed the dispatching harness's explicit instruction instead: built my own survey from `templates/REVIEW_SURVEY.template.json` at the handoff-named path and drove it entirely through `checklist_engine.py --file <path> <verb>` (its own plain CLI mode, distinct from the MCP door), never touching the dispatcher's bound spine.
- **What would have made this easier:** nothing concrete beyond the handoff-gap note above — the handoff itself was precise and the Close Criteria named every test by exact string, which made independent verification fast.

## Return status
complete
