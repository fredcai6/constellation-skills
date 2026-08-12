# Implementation Result

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement`, REWORK attempt 2 — remove `scripts/gen_mcp_config.py` and leave the door's tests
exercising the mechanism that actually ships (the committed project-scope `.mcp.json` with `${VAR}`
expansion from the caller's environment).

## Completed slice
`scripts/gen_mcp_config.py` deleted. `tests/test_mcp_spine_server.py` and `tests/test_mcp_identity.py`
rewired off it with no coverage silently dropped. `scripts/mcp_spine_server.py`'s dangling docstring
reference corrected. Code map rebuilt. Full suite green, committed to `epic-418/f-424-mcp-door`.

## Scope
**Files changed:**
- `scripts/gen_mcp_config.py` (deleted, `git rm`)
- `scripts/mcp_spine_server.py` (docstring: `SPINE_SESSION` line re-pointed to the caller's environment)
- `tests/test_mcp_spine_server.py` (`GenMcpConfigTests` + `load_module` dropped; module docstring
  updated; new `McpJsonVarExpansionLaunchTests` added)
- `tests/test_mcp_identity.py` (`DC3InheritanceMechanismTests.setUp` rewired; docstrings updated)
- `map/INDEX.md` (rebuilt)

**Specific exclusions touched:** no — `scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
`tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py`,
`scripts/checklist_engine.py` were not touched. Confirmed: `git diff -- scripts/checklist_engine.py`
is empty (0 lines, both staged and unstaged).

## Behavior changed
Yes — `scripts/gen_mcp_config.py` no longer exists; nothing in the shipped repo generates a
per-dispatch MCP config file. The delivery mechanism for per-dispatch identity is now solely the
committed `.mcp.json` plus caller-set `SPINE_FILE`/`SPINE_ENGINE`/`SPINE_SESSION` environment
variables (this was already the case in practice per M1/M2 in the handoff; this change removes the
now-redundant alternate path and its own tests).

## Map Impact
- **Structural anchors touched:** `scripts.gen_mcp_config` (removed from the corpus entirely — module,
  3 entities, 2 holes, gone). `scripts.mcp_spine_server` (docstring only, no structural/behavioral
  change to its module-level entities). `tests.test_mcp_spine_server` and `tests.test_mcp_identity`
  (entity counts shift with the test rewiring: `test_mcp_spine_server` went from having a
  `GenMcpConfigTests` class + `load_module` helper to a `McpJsonVarExpansionLaunchTests` class instead;
  `test_mcp_identity`'s `DC3InheritanceMechanismTests` entity shape is unchanged — same test methods,
  different `setUp` body).
- **Capabilities added/changed/affected:** the "per-dispatch MCP config generation" capability is
  removed. The "committed project-scope `.mcp.json` with `${VAR}` expansion" capability (already
  shipping) is now the sole delivery path and gains direct end-to-end test coverage
  (`McpJsonVarExpansionLaunchTests`) that launches the real server through `.mcp.json`'s own
  `command`/`args` with caller-set env vars.
- **Decision candidates / resolved decisions:** the g1-integrate blocker's underlying question — "is
  per-dispatch config generation load-bearing?" — is now resolved by removal, per the Commander's
  measured M1/M2 evidence in the rework handoff. This implementer did not find contrary evidence
  during the rewiring; nothing in the removal required improvising a fallback capability.
- **Trust limitations / drift found:** `map/INDEX.md` was rebuilt and confirmed to carry no
  `gen_mcp_config` reference; the per-module map pages (`map/scripts.gen_mcp_config/...`) are
  untracked-generated (`.gitignore`: `map/* / !map/INDEX.md / !map/ids.jsonl`) so their disappearance
  from disk is not itself a git change — only `map/INDEX.md`'s content change is committed.
- **Triage candidates:** see "Out-of-scope observations" below — `.agent-work/epic-418-followon/commander-424/`
  still contains ~20 files (historical handoffs, `MISSION_FRAME.md`, a demo script under
  `crew-plans/scratch-mcp/`) that name `gen_mcp_config.py`. None were in this handoff's scope (task
  list items 1–5 name exactly `scripts/gen_mcp_config.py`, the two test files, `scripts/mcp_spine_server.py`,
  and the map); left untouched as Commander-owned provenance/process artifacts, not source under this
  gate's remit.

## Test mode
**Required:** `test-after` (existing suites rewired to keep exercising the mechanism that ships; no
new-feature TDD red/green applies since nothing new is being built, only removed and re-pointed).
**Satisfied:** yes — every touched test file was run to green after each edit, and the full suite was
run to green before committing.

## Evidence

### Baseline (before any change), reproduced fresh on this tree

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_identity.py
....................................                                     [100%]
36 passed in 1.35s
```
(24 in `test_mcp_spine_server.py`, 12 in `test_mcp_identity.py`, confirmed separately.)

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2175 passed, 1 skipped, 1061 subtests passed in 96.15s (0:01:36)
```
Exit code 0. Matches the handoff's pinned baseline exactly.

### The change

```
$ git rm scripts/gen_mcp_config.py
rm 'scripts/gen_mcp_config.py'
$ git diff --cached --name-status
D	scripts/gen_mcp_config.py
```

`tests/test_mcp_spine_server.py`: dropped the `GenMcpConfigTests` class (4 tests) and the
`load_module` helper (only consumer was that class); added `McpJsonVarExpansionLaunchTests` (1 test)
that launches the real server through `.mcp.json`'s own `command`/`args`, resolved relative to the
repo root exactly as a real dispatch resolves them, with `SPINE_FILE`/`SPINE_ENGINE`/`SPINE_SESSION`
set directly in the caller's environment (the shell `${VAR:-default}` expansion performed by hand),
then claims a lease and asserts `spine_status` shows `LEASE active: varexp-sess#varexp-agent (by
varexp-tester` — proving both that the shipped delivery path genuinely launches a working server, and
that `SPINE_SESSION` reaches the engine as an opaque `#`-containing string with no server-side parsing.

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
.....................                                                    [100%]
21 passed in 0.70s
```
Exit code 0. **24 -> 21** (delta -3): -4 generation-only tests removed (`test_build_config_keys_session_id_and_agent_id`,
`test_build_config_rejects_hash_in_identity_components`, `test_cli_writes_a_valid_config_file`,
`test_generated_config_server_actually_answers_a_real_tool_call`), +1 replacement
(`test_var_expansion_path_launches_a_real_server_and_answers_a_tool_call`).

`tests/test_mcp_identity.py`: `DC3InheritanceMechanismTests.setUp` now builds its "parent" directly
via `ServerInstance(self.parent_spine, "parent-session#parent-agent", self.root / "parent")` — the
same pattern `DC2SeparateReadingsTests` and every other class in the file already use — instead of
shelling out to `gen_mcp_config.py` and reading its generated config back. Everything downstream
(the composed `SPINE_SESSION`, the assertions on `LEASE active: parent-session#parent-agent (by
parent-agent`) is byte-identical to before; `self.parent_entry["env"][...]` reads were replaced with
`self.parent.env[...]` (the actual env dict `ServerInstance` launched with).

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
............                                                             [100%]
12 passed in 0.65s
```
Exit code 0. **12 -> 12** (delta 0) — no coverage lost or gained; only the mechanism building the
fixture changed.

`scripts/mcp_spine_server.py`: the `SPINE_SESSION` docstring line changed from
`(gen_mcp_config.py composes this key; the server just uses whatever string it is handed)` to
`(the committed .mcp.json's ${VAR} expansion is what sets it on a real dispatch; the server just uses
whatever string it is handed)` — the true half (opaque string, no server-side parsing) kept verbatim,
the composition re-pointed to the caller's environment, no new unmeasured claim added.

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && grep -rn gen_mcp_config scripts/mcp_spine_server.py tests/test_mcp_spine_server.py tests/test_mcp_identity.py map/INDEX.md
(no output, exit code 1 on every file)
```

### Map rebuild

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && python -m scripts.code_map build --root .
pass1: 129 modules indexed
statements: 120733 over 129 files (0 failures)
{ "modules": 129, "entities": 4651, "pages": 4781, ... "stale_tags": [] }
```
Exit code 0. `scripts.gen_mcp_config` no longer appears anywhere in `map/INDEX.md`; only
`map/INDEX.md` and `map/ids.jsonl` are git-tracked (`.gitignore`: `map/* / !map/INDEX.md /
!map/ids.jsonl`) — `ids.jsonl` was unchanged, `INDEX.md` restaged.

### Full suite after all changes

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
.................................................................... [ 57%]
........................................................................ [ 60%]
............................................................................................................................................................... [ 67%]
........................................................................ [ 71%]
................................................................................ [ 74%]
........................................ [ 76%]
................................................................. [ 79%]
..................................................... [ 82%]
........................................ [ 83%]
........................................................................ [ 87%]
........................................................................ [ 90%]
..............s......................................................... [ 93%]
.................................................................... [ 96%]
..................................................................       [100%]
2172 passed, 1 skipped, 1061 subtests passed in 96.24s (0:01:36)
```
Exit code 0. **0 failed.** Pass-count delta: **2175 -> 2172 (-3)**, exactly the `test_mcp_spine_server.py`
delta above (`test_mcp_identity.py` contributed 0 to the delta). No filler tests added to mask the
drop — the one new test (`McpJsonVarExpansionLaunchTests`) is a genuine replacement carrying forward
real coverage, not padding.

### Checklist-engine isolation and commit

```
$ git diff -- scripts/checklist_engine.py | wc -l
0
$ git diff --cached -- scripts/checklist_engine.py | wc -l
0
$ git commit -m "fix(424): remove scripts/gen_mcp_config.py, rewire tests onto the shipped ${VAR} path (g1 rework)" ...
[epic-418/f-424-mcp-door fda35ec0] fix(424): remove scripts/gen_mcp_config.py, rewire tests onto the shipped ${VAR} path (g1 rework)
 5 files changed, 124 insertions(+), 228 deletions(-)
 delete mode 100644 scripts/gen_mcp_config.py
$ git diff --stat HEAD~1 HEAD
 map/INDEX.md                   |  11 ++-
 scripts/gen_mcp_config.py      | 107 ------------------------
 scripts/mcp_spine_server.py    |   5 +-
 tests/test_mcp_identity.py     |  48 ++++++-----
 tests/test_mcp_spine_server.py | 181 +++++++++++++++++++++--------------------
 5 files changed, 124 insertions(+), 228 deletions(-)
```
Commit: `fda35ec0a62c72d4cb66a675da02de5fd35e3b7e` on `epic-418/f-424-mcp-door`. Only the five files
above were staged/committed — the pre-existing unstaged modifications to `.agent-work/epic-418-followon/commander-424/{STATE_NOTE.md,crew-runs.json,execute.json,spine.json,crew-handoffs/g3-implementer-handoff.md}`
(present before this run started, owned by Commander/a concurrent process) were left untouched and
unstaged.

**Result:** pass — every command above ran with exit code 0 and the stated output.

## TDD evidence, if required
Not applicable — this is a removal-and-rewire, not a new-feature TDD slice. Each rewired test file
was run to green immediately after its edit (red/green here means "file still references the deleted
module" -> fails the grep half of the postcondition -> fixed -> both grep and pytest pass), not a
red-test-first cycle.

## Docs/contracts touched
- `scripts/mcp_spine_server.py` docstring (not a contract change — the tool surface, env-var seam,
  and CLI-fallback table are all unchanged; only the SPINE_SESSION composer attribution was corrected).

## Assumptions
- The Commander's M1/M2 evidence in the rework handoff is accepted as the basis for removal per
  instruction #1 ("The removal decision is mine and is made"). No contrary hard evidence surfaced
  during the rewiring.
- `.agent-work/epic-418-followon/commander-424/` files naming `gen_mcp_config.py` (historical
  handoffs, `MISSION_FRAME.md`, the `crew-plans/scratch-mcp/` demo script) are Commander-owned
  provenance/working artifacts, not source under this gate's remit — treated as out of scope per the
  handoff's five-item task list, not silently edited.

## Stop conditions hit
None. No hard evidence surfaced against the removal; the removal decision was not relitigated.

## Out-of-scope observations
- `.agent-work/epic-418-followon/commander-424/` still contains references to the deleted
  `scripts/gen_mcp_config.py` in: `crew-handoffs/g1-implementer-handoff.md`,
  `crew-handoffs/g1-implementer-result.md`, `crew-handoffs/g1-reviewer-handoff.md`,
  `crew-handoffs/g1-reviewer-result.md`, `crew-handoffs/g3-implementer-handoff.md`,
  `crew-handoffs/g3-implementer-result.md`, `crew-plans/g1-implementer-plan.json`,
  `crew-plans/g3-implementer-plan.json`, `crew-plans/scratch-mcp/interactive-demo/README.md`,
  `crew-plans/scratch-mcp/prove_headless_dispatch.py`, `execute.json`, `g1-review/fowler-pass.json`,
  `g1-review/review.json`, `MISSION_FRAME.md`, `REPLAN_INPUT.json`, `STATE_NOTE.md`. Most are
  point-in-time historical records (handoffs, results, review verdicts, past plan journals) that
  should stay as-authored, not be retroactively edited. `MISSION_FRAME.md` and
  `crew-plans/scratch-mcp/prove_headless_dispatch.py` (a demo script) are the two that read as living
  documents rather than history and might warrant a Commander-level pass to note the mechanism
  change — flagged as a triage candidate, not fixed here, since the handoff's task list scoped this
  gate to exactly five items (`scripts/gen_mcp_config.py`, both test files, `scripts/mcp_spine_server.py`,
  the map) and none of them.
- `tests/test_mcp_spine_server.py` had a pre-existing unused `import shutil` (no `shutil.` call
  anywhere in the file) before this run started; left as-is since it predates and is unrelated to
  this change — noted, not fixed, to avoid scope creep into an unrelated cleanup.

## Workflow Feedback

- **Handoff gaps:** none material. The handoff's M1/M2 evidence and the four numbered "loud" points
  were unambiguous enough to execute without needing a clarifying stop. One small thing: the handoff
  says "Carry the composition being an opaque string to the server" as a thing to preserve, but didn't
  say where — I judged `tests/test_mcp_spine_server.py` was the right home (the file that used to hold
  `GenMcpConfigTests`) rather than `test_mcp_identity.py` (which already exercises the opaque-string
  property incidentally via its `parent-session#parent-agent` assertions, but never as its own focused
  claim). Worth stating explicitly in a future handoff which file should own which carried-over
  assertion, since two plausible homes existed.
- **Context rediscovered:** had to independently work out that `map/*` is gitignored except
  `map/INDEX.md` and `map/ids.jsonl` (`.gitignore` line ~51) before understanding why `git add map/`
  only staged one file — the handoff's map-rebuild instruction didn't mention this, and it's easy to
  read "stage the regenerated map/ output" as needing more than the two tracked files.
- **Instructions improvised around:** none — the engine's rail table and the handoff's task list
  covered every step cleanly; no gap needed a judgment call outside what was already specified.
- **What would have made this easier:** a one-line pointer in the handoff to the `map/*` gitignore
  shape (only `INDEX.md` + `ids.jsonl` are tracked) would have saved one round of investigation. Not
  a defect, just a small friction point future rework handoffs touching the map could shave off.

## Return status
`complete`
