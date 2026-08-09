# Review Result

> Written per `constellation-how-to-talk`.

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review`, REWORK attempt 2 — review of commit `fda35ec0` (remove `scripts/gen_mcp_config.py`,
rewire tests onto the shipped `${VAR}` path), issue #424, workstream F of epic #418.

## Result
APPROVE

Driven end to end through the checklist engine as a `survey`:
`/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/g1-review/review-rework.json`
(claim → r0-context..r6-fowler visited, r4a-r4d appended and visited → consolidate, 0 fails,
0 override needed). Fowler-pass record at
`.../g1-review/fowler-pass-rework.json` (`verify_fowler_pass.py` exits 0). Every command below
was re-run by me independently — none of it is taken from the implementer's or Commander's
report.

## Handoff compliance
All 5 numbered tasks in the rework handoff are done, verified directly against `git show fda35ec0`:
1. `scripts/gen_mcp_config.py` deleted (`git rm`).
2. `tests/test_mcp_spine_server.py` rewired: `GenMcpConfigTests` + `load_module` dropped,
   `McpJsonVarExpansionLaunchTests` added.
3. `tests/test_mcp_identity.py`'s `DC3InheritanceMechanismTests.setUp` rewired onto `ServerInstance`.
4. `scripts/mcp_spine_server.py`'s `SPINE_SESSION` docstring re-pointed to the caller's environment.
5. `map/INDEX.md` rebuilt; `grep -rn gen_mcp_config scripts/ tests/ map/ .mcp.json` returns no
   matches (exit 1, confirmed by me).

## Scope drift
None. `git diff HEAD~1 HEAD --name-only` shows exactly the 5 files the handoff named: `map/INDEX.md`,
`scripts/gen_mcp_config.py`, `scripts/mcp_spine_server.py`, `tests/test_mcp_identity.py`,
`tests/test_mcp_spine_server.py`. Every fenced exclusion (`scripts/install_constellation.py`,
`tests/test_feedback_tooling.py`, `tests/test_install_constellation.py`,
`tests/test_run_skill_eval.py`, `tests/test_spine_rail.py`, `scripts/checklist_engine.py`,
`episodes/`) shows an empty diff, confirmed directly:
```
$ git diff HEAD~1 HEAD --stat -- scripts/install_constellation.py tests/test_feedback_tooling.py \
    tests/test_install_constellation.py tests/test_run_skill_eval.py tests/test_spine_rail.py \
    scripts/checklist_engine.py episodes/
(empty)
```
`settings.json` untouched at every scope (not in the commit's diff; the pre-existing
`.claude/settings.json` on disk is unmodified). No issue closed. Nothing promoted into
`docs/agents/*` (`git diff HEAD~1 HEAD --stat -- docs/agents/` is empty).

## Evidence verdict

**The delivery-path claim that overturns attempt 1's own reasoning — checked hardest, per
instruction.** Attempt 1 blocked, was not overridden, and stands corrected here on the merits, not
on authority. Attempt 1 additionally argued generation should survive anyway because a single
shared `.mcp.json` cannot key identity per `session_id#agentId` (protected-intent item 5) — that
specific argument assumed `.mcp.json`'s env values are static literals. They are not:
```
$ cat .mcp.json
...
"SPINE_FILE": "${SPINE_FILE:-.../interactive-demo/spine.json}",
"SPINE_ENGINE": "${SPINE_ENGINE:-scripts/checklist_engine.py}",
"SPINE_SESSION": "${SPINE_SESSION:-}"
```
These are shell `${VAR:-default}` templates, expanded by Claude Code from the *caller's own*
environment at server-launch time, per dispatch — not a single fixed value shared by every
dispatch of the one committed file. That was the gap in my attempt-1 reasoning.

**M1, independently reproduced by me — third reproduction (attempt-1 reviewer, then Commander,
now me):**
```
$ cd /home/tommy/projects/constellation-skills-wt/f-424
$ SPINE_FILE=.../g1-m1-repro/a/spine.json SPINE_SESSION="reviewer-verify-sess-a#reviewer-agent" \
    claude -p "Call the mcp tool spine__spine_status ..." \
    --allowedTools "mcp__spine__spine_status" --output-format json
RESULT: ... ACTIVE g1 [pending] — RVWR-A::1a2a60addbac8c8b ...

$ SPINE_FILE=.../g1-m1-repro/b/spine.json SPINE_SESSION="reviewer-verify-sess-b#reviewer-agent" \
    claude -p "Call the mcp tool spine__spine_status ..." \
    --allowedTools "mcp__spine__spine_status" --output-format json
RESULT: ... ACTIVE g1 [pending] — RVWR-B::aec2980a053d8e8d ...
```
Same directory (this worktree), no `--mcp-config`, no generated file, plain committed `.mcp.json`,
differing only in the caller's `SPINE_FILE`/`SPINE_SESSION`. Each dispatch returned its own fresh,
unguessable nonce. Corroborated server-side, independent of the model's report:
```
$ cat .../g1-m1-repro/a/mcp_calls.jsonl
{"verb": "current", "argv": ["--file", ".../a/spine.json", "current"], ... "ACTIVE g1 [pending] — RVWR-A::1a2a60addbac8c8b" ...}
$ cat .../g1-m1-repro/b/mcp_calls.jsonl
{"verb": "current", "argv": ["--file", ".../b/spine.json", "current"], ... "ACTIVE g1 [pending] — RVWR-B::aec2980a053d8e8d" ...}
```
Each spine directory's own call log recorded exactly one `current` call against its own `--file`.
M1 holds. **A single shared `.mcp.json` does give per-dispatch identity — item 5 is satisfied
without generation, and my attempt-1 objection to removal does not survive.**

**M2 (checked by reading the evidence, not re-run — the handoff did not ask for re-measurement):**
`crew-handoffs/g3-implementer-result.md`'s DC3 verdict measured, twice, with independent nonces,
that a Task-tool subagent inherits its dispatching process's *entire* already-connected MCP
server/scope — it does not spawn a fresh top-level process with its own `--mcp-config`. Since
per-dispatch generation only differentiates identity *between* top-level `claude -p` processes
(one generated config per process), and a Task-tool subagent is not a new top-level process, a
generated config could no more give that subagent its own identity than `${VAR}` can. The
reasoning holds: M2 does not distinguish the two mechanisms.

**Coverage — dropped/carried split checked against the actual diff (`git show fda35ec0`), not the
report:**
- `test_build_config_keys_session_id_and_agent_id` — tested the deleted generator's own compose
  logic. No code left to test. Correctly dropped.
- `test_build_config_rejects_hash_in_identity_components` — a generator-input validation guard.
  Confirmed it was never on the actual delivery path (`run_crew.py` has no MCP wiring; nothing
  else called `build_config`). Correctly dropped, no functional regression.
- `test_cli_writes_a_valid_config_file` — the CLI `--out` flag. No CLI left. Correctly dropped.
- `test_generated_config_server_actually_answers_a_real_tool_call` — e2e proof of a launchable
  config. Superseded by `McpJsonVarExpansionLaunchTests`, which does strictly more: the old test
  only asserted `"ACTIVE g1" in text`; the new one additionally asserts
  `"LEASE active: varexp-sess#varexp-agent (by varexp-tester"` — proving `SPINE_SESSION` reaches
  the engine verbatim, a claim the old e2e test never made at all.
- Net: -4 dropped, +1 added, matching the implementer's own accounting exactly, and each drop
  independently justified as generation-only.

**DC2/DC3 — diffed `DC3InheritanceMechanismTests.setUp` against attempt 1's version directly.**
Only the parent-construction line changed: a `gen_mcp_config.py` subprocess call + hand-read
`parent_entry` dict, replaced by `ServerInstance(self.parent_spine, "parent-session#parent-agent",
self.root / "parent")` — the exact pattern every other class in the file already uses. This is not
merely equivalent, it is a more faithful fixture: the old generated-config parent replaced the
environment wholesale with only the generator's 3 keys; the new parent inherits the real process
environment with only `SPINE_*` stripped and re-set — which is what a real `.mcp.json` `${VAR}`
launch actually does (inherit environment, override named vars). The DC3 positive control
(`assert_door_is_up_and_serving`, called in `setUp` before any "no identity" assertion elsewhere in
the class) is untouched — still in the assertion path.

I did not accept "still demonstrated red and green" on inspection alone. I mutated the shipped
code and reran:
```
$ sed -i 's/SESSION = os.environ.get("SPINE_SESSION", "")/SESSION = "MUTATED-IGNORES-ENV"/' scripts/mcp_spine_server.py
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py tests/test_mcp_spine_server.py
FAILED tests/test_mcp_identity.py::DC2SeparateReadingsTests::...
FAILED tests/test_mcp_identity.py::DC2ConcurrencyAndCollisionControlTests::...
FAILED tests/test_mcp_identity.py::DC3InheritanceMechanismTests::test_ambient_leak_counterfactual_would_have_been_caught
FAILED tests/test_mcp_identity.py::DC3InheritanceMechanismTests::test_subagent_with_no_special_configuration_gets_no_identity_never_the_parents
FAILED tests/test_mcp_spine_server.py::RefusalSurfacesAsIsErrorTests::...
FAILED tests/test_mcp_spine_server.py::McpJsonVarExpansionLaunchTests::...
6 failed, 27 passed in 1.28s
$ cp <backup> scripts/mcp_spine_server.py   # revert
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py tests/test_mcp_spine_server.py
33 passed in 1.30s
```
Both DC3 tests and the new `McpJsonVarExpansionLaunchTests` went genuinely red on a real mutation
and green on revert. Not vacuous. The ambient-leak counterfactual's only change from attempt 1 is
reading `self.parent.env[...]` instead of `self.parent_entry["env"][...]` — the same real env dict
`Popen` actually used to launch the parent, not a weaker substitute.

**New test exercises the real `.mcp.json`, not a hand-rolled copy — read directly:**
```python
config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
entry = config["mcpServers"]["spine"]
...
proc = subprocess.Popen([entry["command"], *entry["args"]], ..., cwd=str(ROOT))
```
`command`/`args` are read live off the committed file; a corruption of `.mcp.json` (wrong command,
wrong args) would break this test. `env` values (`SPINE_FILE`/`SPINE_ENGINE`/`SPINE_SESSION`) are
necessarily hand-supplied — `.mcp.json` stores them as `${VAR:-default}` shell templates, and
Python has no shell to expand that syntax. The test's own docstring says so plainly, and this
substitution is not a coverage gap: the actual `${VAR}` expansion mechanism was independently
verified via the real `claude -p` dispatches in M1 above, which is the only place that expansion
can actually be exercised.

**Test suite, all three handoff commands, reproduced independently:**
```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
21 passed in 0.70s
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
12 passed in 0.64s
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2172 passed, 1 skipped, 1061 subtests passed in 96.64s (0:01:36)
$ echo $?
0
```
Exit code 0 confirmed explicitly (not inferred from the summary line). `2175 -> 2172` = exactly
`-4 + 1` in `test_mcp_spine_server.py` (`24 -> 21`); `test_mcp_identity.py` flat at `12 -> 12`
(confirmed by running it alone, matching the diff's own scope). The one skip is pre-existing and
platform-conditional:
```
$ python -m pytest -q tests -rs | grep SKIPPED
SKIPPED [1] tests/test_spine_rail.py:649: ntpath's normcase ... only applies on Windows
```
Grepped the full commit diff for `skip`/`xfail`/`SkipTest` markers: none found (the only `skip`
string match is the pre-existing `UNCOVERED_VERBS` list entry, unrelated to test collection). No
padding.

**Scoped null:** M1 re-tested on Claude Code 2.1.226-class behavior, this Linux host, one server /
one tool in `--allowedTools`, print-mode with `--output-format json`, two sequential dispatches.
Not re-tested here: genuinely concurrent dispatch, other CLI versions, or the `--strict-mcp-config`
boundary M2 names (that boundary was read from `g3-implementer-result.md`'s own twice-reproduced
measurement, not re-run by me).

## Code/doc quality
Fowler baseline pass rendered on all 12 smells
(`.agent-work/.../g1-review/fowler-pass-rework.json`, `verify_fowler_pass.py` exits 0). 11 absent.
One overridden, logged: `McpJsonVarExpansionLaunchTests` hand-rolls its own JSON-RPC read/write
loop instead of reusing the file's existing `McpRpcClient` helper — justified because (a) the test
this one replaces used the identical hand-rolled shape for the identical structural reason
(`McpRpcClient`'s launch command is hardcoded to `[sys.executable, SERVER]`, which would defeat
this test's whole point of exercising `.mcp.json`'s own `command`/`args`), and (b) `global-crew.md`
directs matching the surrounding code's established local convention. No other smell present. No
comments-as-deodorant: the new test's docstring records durable design rationale (why the env
substitution stands in for shell expansion, what it carries forward from the deleted test),
matching this repo's existing decision-anchor convention; the code does not depend on it to be
understood.

## Map impact verdict
- **Evidence supports claimed change:** yes — `map/INDEX.md` genuinely rebuilt, `gen_mcp_config`
  absent from it (grepped directly), matches the implementer's stated entity-count shifts.
- **Constraints not violated:** yes — `git diff -- scripts/checklist_engine.py` is empty (0
  lines), engine bugs #439/#446/#427/#443 untouched, `settings.json` untouched, `episodes/`
  untouched, no issue closed.
- **Notes match the diff:** yes — the implementer's Map Impact notes (module removed, docstring-
  only changes elsewhere, entity-count shifts in the two test files) match `git show fda35ec0`
  exactly.
- **Decision candidates surfaced:** yes — the implementer correctly did not relitigate the removal
  decision (it was the Commander's, made on M1/M2) and surfaced no new contrary evidence.
- **Durable context routed:** yes — two triage candidates flagged into the survey (`tc1`, `tc2`
  below), not fixed, not dropped.

## Reconciliation check
No divergence beyond the two triage candidates below. This change *resolves* an architecture
divergence (attempt 1's falsified justification) rather than creating one; `map/INDEX.md`
reconciles cleanly with the reduced surface.

## Blockers
None.

## Out-of-scope observations
- **triage (tc1):** `MISSION_FRAME.md` and `crew-plans/scratch-mcp/prove_headless_dispatch.py`
  still narrate the old per-dispatch generation mechanism and read as living documents, not
  point-in-time history (unlike the historical handoffs/results, which should stay as-authored).
  Independently confirmed present; flagged by the implementer, not fixed here — the handoff's task
  list scoped this gate to exactly 5 files, and neither of these is one of them. Might warrant a
  Commander-level pass to note the mechanism change.
- **triage (tc2):** `tests/test_mcp_spine_server.py` has a pre-existing unused `import shutil` (no
  `shutil.` call anywhere in the file), predating this change. Independently confirmed. Unrelated
  cleanup, not fixed here to avoid scope creep.

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff named the exact prior reasoning to check hardest
  (my own attempt-1 item-5 objection), the exact evidence directory to inspect, and the exact
  verification commands — that specificity is why the M1 re-reproduction, the mutation test, and
  the diff-against-attempt-1 checks all landed in one pass. One small thing: the handoff's close
  criterion 4 says the new test must exercise the `.mcp.json`'s own "`command`/`args`/`env`" — the
  test can only genuinely exercise `command`/`args` that way (`env` values are shell-template
  strings Python cannot expand, so they are necessarily hand-supplied); a handoff that names this
  distinction explicitly (rather than leaving it for the reviewer to work out from the test's own
  docstring) would remove one judgment call.
- **Context rediscovered:** none of substance — `docs/agents/CREW_CONTEXT.md`'s "Verification
  Discipline" section ("a check that cannot fail is indistinguishable from one that passed")
  directly motivated the mutation test on `SESSION`, and I had already internalized that from
  attempt 1's own review.
- **Instructions improvised around:** the "Survey State Location" field was not given a literal
  value in this rework handoff (as in attempt 1). I resolved it to
  `.agent-work/epic-418-followon/commander-424/g1-review/review-rework.json`, deliberately distinct
  from attempt 1's now-consolidated `g1-review/review.json`, so the two survey files (BLOCK, then
  APPROVE) both stay intact and auditable rather than one overwriting the other's provenance. A
  rework handoff that names the survey path explicitly the way it names the result path would
  remove this judgment call, and would also settle whether a rework review should reuse or
  fork the prior survey file — I chose fork, since the prior one is a closed, correct BLOCK record
  that should not be reopened or overwritten.
- **What would have made this easier:** nothing structural — this was the cleanest handoff of the
  two attempts on this gate precisely because it named the exact prior claim to re-examine and the
  exact evidence directory backing the new one.

## Return status
`complete`
