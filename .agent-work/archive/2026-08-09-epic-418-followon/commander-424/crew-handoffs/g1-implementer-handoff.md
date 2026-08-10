# Implementer handoff — gate g1: the MCP front door

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g1-implement`
**Worktree (work only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch
order. Governing spec: `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md` section F.

## Task

Build a second front door on the checklist engine: an MCP stdio server exposing the spine drive loop
as **roughly seven typed tools** that wrap the engine's own dispatch function, plus the per-dispatch
config generation that delivers it to a cold agent.

Deliverables, all inside the worktree above:

1. **`scripts/mcp_spine_server.py`** — zero-dependency, newline-delimited JSON-RPC 2.0 over stdio
   (that is what the MCP stdio transport is; do not add an SDK dependency). Roughly seven typed
   tools. Every tool builds an `argv` and calls `checklist_engine.main(argv)`, capturing stdout,
   stderr and the exit code.
2. **`scripts/gen_mcp_config.py`** — generates a per-dispatch MCP config JSON for one agent, keyed by
   `session_id#agentId`, binding that agent's `SPINE_FILE`, `SPINE_ENGINE` and `SPINE_SESSION` into
   the server's environment. This is the delivery path (see "Why per-dispatch" below).
3. **`.mcp.json`** at the worktree root — project scope, for the interactive convenience path only.
4. **`tests/test_mcp_spine_server.py`** — the gate's closing check.
5. A short **CLI-fallback table** documenting every engine verb the tool surface does *not* cover.
   Put it in the server module's docstring or a sibling markdown file; do not put it in
   `docs/agents/*` (promoting anything there is a human's call and is out of scope).

## Protected intent — what must survive, non-negotiable

These come from the spec's "Fixed" list. A change that breaks one of these is a failed gate even if
everything else works.

1. **No engine logic is duplicated.** The server *wraps* `checklist_engine.main()`. Refusals,
   recovery hints, rails, the trip ledger, the journal sidecar and lease enforcement must ride
   through unchanged because they are never reimplemented. If you find yourself parsing engine output
   to decide behaviour, stop — that is duplication in disguise.
2. **The gate imperative rides tool results verbatim.** Spine templates are the single source of
   instruction text. No second rendering path, no summarizing, no truncation, no reflowing.
3. **The CLI door stays.** F is additive. Every verb not covered by a tool keeps a documented CLI
   fallback.
4. **`settings.json` is never written, at any scope.** Project-scope `.mcp.json` only. This is an
   explicit pre-ruling.
5. **Each agent gets its own server instance**, keyed by `session_id#agentId`.

## Why per-dispatch config generation — already measured, do not re-litigate

I probed this before planning, with a control on each side:

- A fresh project-scope `.mcp.json` is **not** picked up by a live session (the tool was absent from
  the session's tool list, while a tool known to exist *was* found — so the search was working).
- On a fresh process, `claude mcp list` shows the server as **`⏸ Pending approval`**, and the
  server's start-marker file was never written. So the config is valid and seen, but the server does
  **not** run until a human approves it interactively. Project-scope `.mcp.json` therefore cannot
  deliver the door to a cold or headless agent at all.
- The path that works, verified end to end against a real server (it returned its tool's output and
  wrote its start marker):

  ```
  claude -p "<task>" --mcp-config <generated>.json --strict-mcp-config --allowedTools "mcp__<server>__<tool>"
  ```

  `--strict-mcp-config` ignores all other MCP configuration, which is exactly what gives each agent
  its own instance rather than a shared ambient one.

`gen_mcp_config.py` exists to emit that `<generated>.json`.

## Lift source — recoverable from git, NOT from any filesystem path

The prototype is at git object `de6a0844` **in this repo**. The path #424 names
(`C:/Programs/.proto-exc9-mcp-front-door`) does not exist; this is a Linux host and that text is
stale.

```
git show de6a0844:proto/mcp_spine_server.py     # 308 lines — the server
git show de6a0844:proto/drive_via_mcp.py        # 82
git show de6a0844:proto/run_arm.py              # 92  — tracer (later gate)
git show de6a0844:proto/score.py                # 98  — scorer (later gate)
git show de6a0844:proto/engine_cli.py           # 42
git show de6a0844:proto/make_toy_spine.py       # 123
```

**It is a throwaway prototype against a four-gate toy spine. Lift what earns its place; do not treat
it as a design.** Its tool grouping in particular is a placeholder, and its `run_engine()` binds
ambient state from env vars — that idea is good and worth keeping; the specific seven tools are not
sacred.

## The grouping decision is yours, and here is where it actually bites

The engine has **18 verbs**:

```
current  claim  heartbeat  release  start  advance  record  consolidate  skip
block    resume reopen     append   amend  attest   waive   attach       flag-candidate
```

The prototype's seven tools reach eleven of them and leave uncovered: `heartbeat, skip, reopen,
append, amend, waive, attach, flag-candidate`.

**That uncovered set is wrong for a real role spine, and this is the one judgement I most want you to
exercise.** Driving *this very run's* commander spine required `attest`, `attach` and `waive` — a
door missing `attach` cannot satisfy any `user-decision` checkpoint, and a door missing `waive`
cannot close a gate whose check the principal accepted as non-blocking. By contrast `skip`, `amend`,
`append` and `flag-candidate` are genuinely rarer. Weight coverage toward what a real role spine
needs, keep the tool count near seven, and put everything else in the CLI-fallback table.

Do **not** expand to eighteen tools to be safe. The spec calls the seven-over-eighteen split a
placeholder and explicitly forbids gold-plating: MCP is the current vehicle, not the destination, and
Tommy expects this to become a different kind of tool call later.

## Constraints

- Work only in the worktree named above. Do not create another worktree.
- **Do not edit** `scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
  `tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py` —
  a concurrent agent owns them. If your work genuinely requires one, stop and report it; do not
  negotiate directly with that agent.
- **Do not fix engine bugs #439, #446, #427 or #443.** They must be held constant across both
  measurement arms of a later gate. Fixing one here corrupts the measurement.
- Do not hand-edit any checklist JSON (`spine.json`, `execute.json`, survey files). The engine owns
  that state. Same for anything under `episodes/`.
- Host is **Linux**. Corpus text assuming Windows (`.cmd` wrappers, PowerShell here-strings,
  `C:/...` paths, "`py` has no pytest") is stale. Both `python` and `py` resolve to one venv here
  (3.12.3, pytest 9.1.1).

## Test mode and verification commands

Settled repo invocation — do not re-derive it:

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

The gate's closing check is:

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
```

**Six tests are already red on this host and are not yours** (a concurrent agent is fixing them, so
the set may shrink under you, which is fine — it must not grow):

```
tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_installed_path_rewritten_template_is_up_to_date
tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_token_working_copy_up_to_date_against_promoted_baseline
tests/test_install_constellation.py::InterpreterProbeTests::test_sidecar_records_resolved_via_for_probe_success_and_fallback
tests/test_install_constellation.py::TemplateBaselineTests::test_seeded_working_copy_reads_up_to_date_against_baseline
tests/test_run_skill_eval.py::test_real_runner_process_death_leaves_resumable_state
tests/test_spine_rail.py::test_same_path_windows_normcase_sep_equivalence
```

## Close criteria

1. The server starts, answers `initialize` and `tools/list`, and every tool executes a real engine
   call. **Prove it by driving a throwaway spine to completion through the tools** — not by unit
   tests alone.
2. **The door is demonstrably up and serving**, evidenced by a live tool call returning genuine
   engine output. This is load-bearing for a later gate's positive control, so make it reproducible.
3. A refusal from the engine surfaces as a **failed** tool result (`isError: true`) carrying the
   engine's own refusal text and recovery hint, not as prose the model must parse to notice it
   failed.
4. `gen_mcp_config.py` emits a config that a real `claude -p --mcp-config ... --strict-mcp-config`
   dispatch can use, and that binds `session_id#agentId`. Prove it with an actual headless dispatch,
   not a hand-inspected file.
5. Imperative text returned through a tool is **byte-identical** to the CLI projection's.
6. `tests/test_mcp_spine_server.py` passes; the pinned red set above has not grown.
7. The CLI-fallback table covers every uncovered verb.

## Required evidence to return

- The exact commands you ran and their real output, including exit codes.
- The transcript (or log) of the throwaway spine driven end to end through the tools.
- The headless dispatch that used a generated config, and what it returned.
- Your byte-identity check for imperative text, and how you know it can fail.
- Your tool-grouping decision: which verbs you covered, which you did not, and why.
- The full pytest tail for `tests/`, and whether the pinned red set grew.

## Specific exclusions — out of scope

Measurement or tracer work (a later gate). Same-gate equivalence as a property (a later gate). The
DC2/DC3 identity tests (a later gate). Fixing the six pinned red tests. Touching `settings.json`.
Closing any issue. Promoting anything into `docs/agents/*`.

## Reporting

Write your `IMPLEMENTER_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g1-implementer-result.md
```

**Write that file before ending your turn — the write is the delivery.** Include a
`## Workflow Feedback` section: where the skills, this handoff, or the engine cost you attention. Be
specific and blunt; this epic exists because that cost is real and your run is evidence.

Report a measured negative as a complete result. "This specific check failed" is a finding; "this
approach is impossible" is not a report a crew is positioned to make. Anything real but outside this
task goes back as a triage candidate rather than being fixed silently or dropped.
