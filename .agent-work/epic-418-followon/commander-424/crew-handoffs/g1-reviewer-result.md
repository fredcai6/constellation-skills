# Review Result

> Written per `constellation-how-to-talk`.

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` — the MCP front door: `scripts/mcp_spine_server.py`, `scripts/gen_mcp_config.py`, project-scope `.mcp.json`, `tests/test_mcp_spine_server.py` (issue #424, workstream F of epic #418).

## Result
`BLOCK`

Driven end to end through the checklist engine as a `survey`:
`/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/g1-review/review.json`
(claim → 7 items visited, r7 appended → consolidate). Fowler-pass record at
`.../g1-review/fowler-pass.json`. All commands below were re-run by me, not taken from the
implementer's report.

## Handoff compliance
The implementer built exactly what `g1-implement` asked: `scripts/mcp_spine_server.py` (7 tools
wrapping `checklist_engine.main()`), `scripts/gen_mcp_config.py`, `.mcp.json`, 24 tests in
`tests/test_mcp_spine_server.py`. Verified directly against `git diff a2ce8669..HEAD`. The
implementer faithfully executed the handoff; the BLOCK below is a defect in the handoff's own
inherited premise, not an implementer scope failure.

## Scope drift
None. Fenced files show an empty diff:
```
$ git diff a2ce8669..HEAD --stat -- scripts/install_constellation.py tests/test_feedback_tooling.py tests/test_install_constellation.py tests/test_run_skill_eval.py tests/test_spine_rail.py
(empty)
```
`episodes/` untouched. No hand-edited checklist JSON (the implementer's own plan carries a
`.journal` sidecar, proving engine-driven mutation). Engine bugs #439/#446/#427/#443 untouched
(`scripts/checklist_engine.py` diff is empty — see below).

## Evidence verdict

**Protected-intent item 1 — no engine logic duplicated.**
```
$ git diff a2ce8669..HEAD -- scripts/checklist_engine.py
(empty)
```
Read all of `scripts/mcp_spine_server.py`: every branch of `call_tool()` routes through
`run_engine()` → `checklist_engine.main(argv)`. No output-parsing-to-decide-behaviour found (the
subtle duplication form the handoff warned about).

**Protected-intent item 2 — imperative rides tool results verbatim, negative control genuinely fails.**
I did not accept the implementer's claim on inspection alone. I mutated the shipped code to break
the guarantee and confirmed the test suite catches it:
```
$ python3 - <<'EOF'
# appended a trailing space to as_result()'s returned text
EOF
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py::ToolsWrapEngineTests::test_spine_status_matches_real_engine_current_output -v
FAILED ... AssertionError: "...next: start g1" != "...next: start g1 "
$ git checkout -- scripts/mcp_spine_server.py   # revert
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
........................                                                 [100%]
24 passed in 0.70s
```
The check can fail, and did, on a real mutation. Not vacuous.

**Protected-intent item 3 — CLI door stays, uncovered-verb table complete against the real verb list.**
Enumerated the engine's own verb list directly (not from the implementer's count):
```
$ python scripts/checklist_engine.py --help
{current, claim, heartbeat, release, start, advance, record, consolidate, skip, block, resume,
 reopen, append, amend, attest, waive, attach, flag-candidate}   # 18 verbs
```
Covered by the 7 tools: `current, claim, heartbeat, release, start, advance, attest, attach,
waive, block, resume, record, consolidate` (13). Uncovered, documented in
`mcp_spine_server.py`'s module docstring with invocation shape + rationale:
`skip, reopen, append, amend, flag-candidate` (5). 13 + 5 = 18, disjoint, exhaustive. Matches the
handoff's claimed set exactly.

**Protected-intent item 4 — `settings.json` never written.**
```
$ grep -rn "settings.json" scripts/mcp_spine_server.py scripts/gen_mcp_config.py .mcp.json tests/test_mcp_spine_server.py
(no matches)
```

**Protected-intent item 5 — each agent gets its own server instance.**
Read `mcp_spine_server.py:112-114`: `SPINE_FILE`/`SPINE_ENGINE`/`SPINE_SESSION` are bound at
module-import time from the process environment — one OS process is one dedicated identity.
`gen_mcp_config.py` composes `SPINE_SESSION` as `session_id#agent_id` per dispatch (confirmed in
`build_config()` and its test `test_build_config_keys_session_id_and_agent_id`).

**Test suite:**
```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
........................                                                 [100%]
24 passed in 0.70s

$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
...
FAILED tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_installed_path_rewritten_template_is_up_to_date
FAILED tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_token_working_copy_up_to_date_against_promoted_baseline
FAILED tests/test_install_constellation.py::InterpreterProbeTests::test_sidecar_records_resolved_via_for_probe_success_and_fallback
FAILED tests/test_install_constellation.py::TemplateBaselineTests::test_seeded_working_copy_reads_up_to_date_against_baseline
FAILED tests/test_run_skill_eval.py::test_real_runner_process_death_leaves_resumable_state
FAILED tests/test_spine_rail.py::test_same_path_windows_normcase_sep_equivalence
6 failed, 2157 passed, 1061 subtests passed in 93.87s (0:01:33)
```
Exactly the pinned red set from the handoff — names match verbatim, no growth, no shrink.
Tests are behavioral: real subprocess spawns the server and drives real newline-delimited
JSON-RPC over stdio (`McpRpcClient`); the refusal test cross-checks the tool's `isError` text
against the CLI's real stderr for the identical illegal call, not a string fixture.

## The delivery-path decision — re-verified, and it does not hold

**This is the BLOCK.** The handoff named this the highest-value part of the review: all of
`gen_mcp_config.py` and the per-dispatch delivery architecture rest on one unreviewed Commander
observation — that project-scope `.mcp.json` lands in `⏸ Pending approval` and "cannot serve a
cold or headless agent at all."

I re-ran the probe independently, on Claude Code 2.1.226, against a genuinely cold project (no
entry at all for this worktree in `~/.claude.json` before this review):

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424
$ claude mcp list
spine: python3 scripts/mcp_spine_server.py - ⏸ Pending approval (run `claude` to approve)

$ claude -p "Call the mcp tool spine__spine_status if it is available, and tell me its output
             verbatim." --output-format json --allowedTools "mcp__spine__spine_status"
{"is_error":false, ... "result":"Here's the verbatim output from `spine__spine_status`:\n\n```\n
RAIL: ...\nACTIVE g1 [pending] — Create .../interactive-demo/workspace/notes.txt ...\n
postconditions:\n  c1 [unmet] command — notes.txt exists\n  c2 [unmet] null — gates understood\n
0/2 met\nnext: start g1\n```"}
```
No `--mcp-config`, no `--strict-mcp-config` — the plain, committed, project-scope `.mcp.json`.
Verified this is not a hallucinated transcript by checking server-side ground truth independent of
the model's claim:
```
$ wc -l .../interactive-demo/mcp_calls.jsonl   # before: 2
$ <repeat the -p call>
$ wc -l .../interactive-demo/mcp_calls.jsonl   # after: 3, fresh matching timestamp
```
Repeated once more: line count grew 2→3 again, same result both times. `~/.claude.json` shows no
entry for this project after either call — no approval was ever recorded or required.

I then isolated why the Commander's original probe likely saw a block — reran the identical `-p`
call **without** `--allowedTools`:
```
$ claude -p "Call the mcp tool spine__spine_status..." --output-format json
{"permission_denials":[{"tool_name":"mcp__spine__spine_status", ...}],
 "result":"The tool exists but I don't have permission to call it — you'd need to grant that in a
           permission prompt. ..."}
```
That is the **ordinary per-tool-call permission gate** every tool has in headless mode absent an
explicit grant — not the MCP-server "Pending approval" connection gate. They are two different
mechanisms, and the implementer's own headless proof (`prove_headless_dispatch.py`) already passes
`--allowedTools "mcp__spine__spine_status"` — so this friction is identical on both the
plain-`.mcp.json` path and the per-dispatch-config path.

**Answer to the handoff's question:** `Pending approval` is not permanent for a cold/headless
agent, and it is not even a one-time-clearing state — headless `-p` dispatch does not appear to
hit that gate at all on this host/version. Project-scope `.mcp.json` serves a headless agent
today, out of the box, with the same `--allowedTools` requirement any tool call needs. The premise
recorded in `MISSION_FRAME.md`, the `g1-implementer-handoff.md`, and `execute.json`'s
`decision:mcp-probe-is-the-commanders` (graded `settled/measured`) does not reproduce as measured
here. Per the repo's own `@grade` doctrine, a `settled/measured` decision is revisable by a
contradicting new measurement — this is that measurement.

This does **not** mean `gen_mcp_config.py` should be deleted. Protected-intent item 5 (each agent
gets its own server instance, keyed `session_id#agentId`) is a real, independent requirement a
single shared project `.mcp.json` cannot satisfy: `SPINE_FILE`/`SPINE_SESSION` are bound once at
server-launch from one static `.mcp.json` entry, so N concurrently-dispatched agents sharing that
one project config would all bind the same spine file and session identity. That is a genuine,
different justification for per-dispatch config generation — but it is not the justification the
plan actually recorded, and the plan graded a decision `settled/measured` on a measurement that
does not reproduce. This is the reviewer surfacing a decision for Commander, not making it.

**Scoped null:** tested on Claude Code 2.1.226, Linux host, one server / one tool named in
`--allowedTools`, print-mode with `--output-format json`. Not tested: other CLI versions,
`--dangerously-skip-permissions`, or genuinely concurrent multi-agent dispatch racing the same
project `.mcp.json` (where the real, different per-identity justification above would need its own
re-verification before the architecture can be re-grounded on it).

## Code/doc quality
Fowler baseline pass rendered on all 12 smells (`.agent-work/.../g1-review/fowler-pass.json`,
`verify_fowler_pass.py` exits 0). One flagged, non-blocking: `mcp_spine_server.py:call_tool()` is
a ~130-line flat dispatcher across all 7 tools — readable, each branch a short argv builder, but a
candidate to split into one handler per tool name dispatched from a dict. Eleven smells absent,
each with a logged reason (primitive-obsession and speculative-generality both have specific
counter-reasons recorded, not just "not applicable"). No comments-as-deodorant: the long module
docstrings record durable design rationale (tool-grouping decision, CLI-fallback table), matching
this repo's decision-anchor convention, and the code does not depend on them to be understood.

## Map impact verdict
- **Evidence supports claimed change:** yes — `map/INDEX.md` was genuinely rebuilt (`scripts` 53→55
  modules, `tests` 60→61), lists `scripts.gen_mcp_config`, `scripts.mcp_spine_server`,
  `tests.test_mcp_spine_server` with real entity/hole counts, and `tests/test_code_map.py`'s
  freshness check is green (148 passed, 63 subtests) — not stale.
- **Constraints not violated:** yes, per the protected-intent verification above.
- **Notes match the diff:** yes, with the one exception above (the delivery-path decision claim).
- **Decision candidates surfaced:** yes — the delivery-path re-grounding (identity-isolation vs.
  the disproven approval-gate claim) is surfaced to Commander, not resolved here.
- **Durable context routed:** yes — two triage candidates flagged into the survey
  (`triage_candidates: tc1, tc2`), not fixed, not dropped.

## Reconciliation check
No divergence beyond the two triage candidates below. `map/INDEX.md` reconciles cleanly with the
new structural surface.

## Blockers
- **r7-delivery-path (survey item, recorded `fail`):** the per-dispatch config-generation
  architecture's stated justification ("project-scope `.mcp.json` cannot serve a cold/headless
  agent") does not reproduce on independent re-measurement. See "The delivery-path decision" above
  for full evidence and the scoped null. This blocks APPROVE until Commander either (a) re-grounds
  the decision on the real justification (per-agent identity isolation) and regrades it, or (b)
  produces a reproduction of the original failure mode I could not reproduce.

## Out-of-scope observations
- **triage (tc1):** `map_orient.py` reports `DEGRADED-NO-MAP` on this repo despite a real,
  enforced, current code map at `map/INDEX.md` — it only probes `docs/architecture/generated/map.json`,
  `docs/architecture/index.md`, `docs/architecture/`, then falls back to README/AGENTS/CLAUDE.md/a
  docs index; `map/` is in neither list. First observed by the implementer/Commander this run,
  independently confirmed here.
- **triage (tc2):** a duplicated-path artifact tree at
  `.agent-work/epic-418-followon/epic-418-followon/commander-424/{context,mechanical}/*.json`
  pre-dates this gate and looks like a path-construction defect (a work-id-qualified path composed
  with a redundant work-id prefix) in whatever hook wrote it. I independently reproduced a fresh
  instance of the same bug on my own `g1-review` context/mechanical files, generated at the same
  timestamp as the Commander's own `start r1-handoff`-equivalent step — this is a live, reproducible
  defect, not a one-off.
- **Minor, not blocking:** the "byte-identical" claim for imperative-verbatim is, precisely, "identical
  after both sides are whitespace-stripped" (`as_result()` calls `.strip()`, and the test's CLI
  capture uses `.rstrip("\n")`) — substantively the same guarantee since both sides normalize the
  same way, but a hair narrower than the literal word "byte-identical." Worth a one-word precision
  fix in the docstring/handoff language, not a functional defect.

## Workflow Feedback
- **Handoff gaps:** none of substance — the handoff named the exact probe to re-run, the exact
  question the Commander did not answer, and the exact BLOCK condition. That specificity is why
  the delivery-path finding above was possible in one pass rather than several.
- **Context rediscovered:** the distinction between the MCP-server "Pending approval" connection
  gate (`claude mcp list`/`get`, interactive-session-scoped, persisted in `~/.claude.json`'s
  `enabledMcpjsonServers`) and the ordinary per-tool-call permission gate (`--allowedTools`,
  applies identically to every tool, MCP or built-in) is not documented anywhere in this repo's
  doctrine or in Claude Code's own `--help`. I had to discover it by running the probe four
  different ways (`claude mcp list`, `-p` with `--allowedTools`, `-p` without it, checking
  `~/.claude.json` state before/after). A future MISSION_FRAME citing an MCP-approval measurement
  should name which of these two gates it tested, because they produce visually similar-looking
  friction ("the tool didn't work") for completely different reasons with completely different
  fixes.
- **Instructions improvised around:** the Fowler-pass template's `<fowler-pass-record-path>`
  placeholder resolution and the survey's `Survey State Location` are both described only by
  example in the skill prose, not given a literal value in this handoff — I resolved both to
  `.agent-work/epic-418-followon/commander-424/g1-review/{review.json,fowler-pass.json}` by
  analogy with the gate id (`g1-review`) and the existing `g1-implement-mcp-door-424/` sibling
  directory naming. This worked, but a handoff that states the survey path explicitly (the way it
  already states the result path) would remove one judgment call per reviewer run.
- **Self-inflicted, worth naming anyway:** one of my `record` finding strings used backticks around
  a shell command inside a double-quoted Bash `--finding` argument; bash command-substituted them,
  so the r4-quality finding text now has a large verbatim dump of `checklist_engine.py --help`'s
  output pasted inline. The content is still factually accurate, just visually noisy — worth a
  reviewer-side habit note (use single-quoted heredocs for any finding text containing backticks),
  not an engine or handoff defect.
- **What would have made this easier:** a one-line doctrine note (in `global-everyone.md` or
  `checklist-engine.md`) distinguishing MCP server-connection approval from ordinary tool-call
  permission would have saved the two extra probe variants I ran to separate them.

## Return status
`complete`
