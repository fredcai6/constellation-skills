# Launch Order: `cleanup-a-door — #604, #603, #605`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Commanders start cold. Everything you need is pasted below; nothing here requires you to open an issue to understand your mission.

## Mission

Make the MCP door usable by the session that needs it. Today an orchestrator cannot bind the door to a spine it is about to create, so every epic since #424 has driven its own spine through the CLI — which is the opposite of what #559 ruled. Three defects, in this order:

**1. #604 — the door dies on its own call log.** It appends to `<spine_dir>/mcp_calls.jsonl` with no guard. Bind it to a spine whose work area has been archived away and the first tool call raises `FileNotFoundError` inside `call_tool`, unhandled, so the process exits 1 and every tool on that server is gone for the session. Reproduced deterministically:

```
EXIT 1
FileNotFoundError: [Errno 2] No such file or directory:
  '/home/tommy/projects/constellation-skills/.agent-work/epic-418-followon/mcp_calls.jsonl'
```

The client is told only `MCP error -32000: Connection closed`, with no mention of a spine, a path, or a stale binding. Telemetry must never be able to kill a tool call, let alone the server; and a bound spine that does not exist should be a refusal that names the path.

**2. #603 — the door cannot be bound, and fails open when unbound.** `scripts/mcp_spine_server.py:146` reads `SPINE = Path(os.environ["SPINE_FILE"]).resolve()` at import. Every call builds `argv = ["--file", str(SPINE), verb, *rest]` (`:441`), and `_identity_violation` refuses any argv naming a different spine — deliberately. So the binding is fixed before Claude Code launches, which is before the spine exists. Worse, `.mcp.json` supplies `"SPINE_FILE": "${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}"`, so an unbound session gets a confident answer about a demo scratch gate instead of a refusal.

Two changes: **fail closed** (drop the demo default; an unset, missing or unreadable `SPINE_FILE` makes every tool return a refusal naming the path and how to bind), and **bind on open** (`spine_open` is already required never to touch `SPINE`/`SESSION` because it acts on a spine that does not exist yet, so it is already callable on an unbound door — let it bind the calling process to what it just minted, or add an explicit `spine_bind` running the same identity checks).

**3. #605 — the shipped demo spine is unusable.** `examples/mcp-interactive-demo/spine.json` is tracked and carries absolute paths into `constellation-skills-wt/f-424`, a worktree deleted during the epic-418-followon closeout, on one machine, which never existed anywhere else. Regenerate it with paths relative to the example directory, and add whatever check keeps a machine-specific absolute path out of a shipped example.

**Serves the epic intent:** goal 1 of this cleanup is "the door is usable". The exit criterion is a session started with no `SPINE_FILE` that calls `spine_open`, gets bound, and drives a real spine end to end without touching the CLI.

## Prior-Wave Verdicts (pasted)

From epic 568's ADMIRAL_LOG, standing corrections, 2026-08-15:

> **"MCP-only" is withdrawn as a blanket constraint.** The door binds at import from `.mcp.json`'s demo default and cannot be rebound, so out-of-band dispatch hands a child a door pointing at the demo spine. Dispatch through the `cli` backend with `--spine` when the child must mutate a spine; otherwise state plainly that the door may be unbound and authorize a disclosed CLI fallback.

From the same contract, pre-ruling `decision:door-unusable-this-session` (`settled/measured · leans all-waves`): the Admiral drove its own spine through `checklist_engine.py` with an explicit `--session-id` for the entire epic.

Measured 2026-08-15, this session: a probe driving the real server over stdio with `SPINE_FILE` set to a real spine returned a correct `spine_status` — lease state, digest, no stderr. **The mechanism is healthy. Only the binding handoff is broken.** Do not rewrite what works.

From #567's verified starting point, 2026-08-12: the verb gap is closed — 11 tools cover every engine verb. No tool work is needed there.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- `decision:one-spine-per-process-stands` — the door binds one spine per process, and `_identity_violation` continues to refuse any argv naming another. Bind-on-open changes *when* the binding is decided, never *how many* are live at once. A tool that takes a spine path per call is out of scope and would undo the guard that makes the door safe.
  `@grade: settled/human · leans all gates`
- `decision:fail-closed-beats-fail-open` — an unbound, missing or unreadable spine yields a refusal that names the path. Never a demo answer, never a crash, never silence.
  `@grade: settled/measured · leans g1-implement`
- `decision:telemetry-never-fatal` — the call log is diagnostic. If it cannot be written, drop the record and continue; do not fail the call.
  `@grade: settled/measured · leans g1-implement`
- `decision:bind-on-open-over-new-verb` — prefer binding inside `spine_open` to adding a `spine_bind` tool, because `spine_open` already has the unbound-safe contract and a new verb is a new thing to teach. Overridable: if the identity checks cannot be expressed inside `spine_open` without weakening them, add the explicit verb and say why.
  `@grade: guess · leans g1-implement · settle: attempt the `spine_open` binding first and report what it costs`
- `decision:demo-spine-is-generated-not-hand-fixed` — do not hand-edit paths in the demo spine. Produce it from the example's own directory so it cannot drift back.
  `@grade: guess · leans g2 · settle: whichever is smaller once you have read how the example is built`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win. Specifically: if bind-on-open turns out to be unreachable without weakening `_identity_violation`, that finding, measured, is the deliverable — say so and stop rather than shipping a weakened guard.

## Inherited Latitude

**You may decide:** the shape of the refusal messages, where the fail-closed check sits, how the demo spine is generated, test structure, and whether `spine_open` or a new verb carries the binding (see the pre-ruling).

**You must float to the Admiral:** any change to `_identity_violation`'s semantics; any change to the engine (`checklist_engine.py`); any change that makes an agent-facing skill teach the CLI as a default; publication. Commanders park at `archive` — merge to `main` is the Admiral's class.

## File Ownership

Your working-notes file is `notes-a.md`, in your worktree, and you are its sole writer this wave.

> Name it `notes-<n>.md`, **never** `findings-<n>.md`. The harness `Write` tool refuses any path whose basename contains "findings" — a guard aimed at unprompted report-dumping, which cannot tell that this file was deliberately assigned. The guard is not ours to change; the word is.

**Files you own this wave:** `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/mcp-interactive-demo/**`, `tests/test_mcp_spine_server.py`, and any new test file you add for the door. Also `scripts/install_constellation.py` and `skills/commander/templates/COMMANDER_SPINE.template.json` **for the door-detection change only**, which lands last.

**Fenced — do not touch:** `scripts/checklist_engine.py`, `scripts/hooks/**`, `scripts/run_crew.py`, `scripts/gauge_reader.py`. Lanes B and C own those and are running concurrently.

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door`, branch `cleanup/a-door`, base commit `a69bbac4`, created from the main checkout with:

```
git worktree add .worktrees/cleanup-a-door -b cleanup/a-door a69bbac4
```

`main` was verified fresh at dispatch: `a69bbac4`, working tree clean, suite 3057 passed / 0 failed.

First step, before any git operation: **`cd` into that worktree**, then run `py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door` — it must exit 0. Paste its output into your return report.

> **Order matters.** `--here` asserts about the directory you are *standing in*. Run it before `cd` and you get `fatal: not a git repository`, which reads as "you are not isolated" when the truth is "you have not arrived yet". Do **not** resolve this by passing the path to git (`git -C <path>`): that compares the worktree to itself, is true for any valid worktree, and disarms the check. Measured in #315 / PR #576.

NOTE: PR integration defaults to **server-side merge**, and publication is the Admiral's anyway.

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` is resolved once at session launch and inherited unchanged by every subagent, so a Commander in a worktree still runs the **main checkout's** hook code against the **main checkout's** state (#269). This lane does not change hook code, but it does change a **server process**: validate the door by launching the server yourself as a subprocess with the environment you intend to test, never by reasoning about the door your own session is connected to. A working stdio probe already exists in this order's Data Locations.

## Inherited Context

- **Platform:** Linux, Python 3.12, invoked as `py`. Suite: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`.
- **Clear `__pycache__` before every measurement** (`find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +`). Stale bytecode from a relocated worktree fabricates failures that look exactly like defects and cost epic 568 hours twice (#597).
- **Merge gate, as epic 568 settled it:** local Linux green, an independent APPROVE, and a failure-set difference against a `main` baseline **re-measured at gate time**, not reused.
- **CI is one `windows-latest` job** and is red from pre-existing breakage. There is no Linux CI. Local measurement is the only Linux signal.
- **The door in your own session is bound to the demo spine.** That is the defect you are fixing; do not use your own connection as evidence about anything.
- **Drive your spine through the engine CLI this wave** with an explicit `--session-id`. The door cannot be trusted to be pointed at your spine until your own change lands.
- **`map/INDEX.md` is generated and freshness-tested.** If you add or rename an entity, run `py -m scripts.code_map build --root .` and commit the result, or the suite fails on a file you did not think you touched.
- **Relaunch is fixed as of `a69bbac4`** (#601): re-claiming your own lease now re-stamps `claimed_at`, so a relaunched leg is no longer refused by its predecessor's context reading. You do **not** need `claim --force` for a routine relaunch.

**Charter-lite carrier:** this repo has no `docs/agents/` overlay. `docs/CHECKLIST_SCHEMA.md` and `skills/workbench/references/checklist-engine.md` are the engine's own reference; `skills/admiral/references/fleet-doctrine.md` carries fleet doctrine.

## Pre-empted Steps

- **Context is established by this order.** Cite it rather than re-deriving the door's state; the measurements in Mission and Prior-Wave Verdicts were taken 2026-08-15/16 against `a69bbac4`.
- **The worktree is provisioned and gate-verified.** `verify_worktree_isolation.py` over all three lane paths exited 0 at dispatch.
- **Triage is done.** #603, #604 and #605 are filed with mechanisms and file:line citations. Do not re-triage; implement.

## Data Locations

- A working stdio probe for the door, written 2026-08-15, at `/tmp/claude-1000/-home-tommy-projects-constellation-skills/2fe45059-0786-403a-9bd3-f2214c06c443/scratchpad/door_probe.py`. It sends `initialize`, `notifications/initialized`, then a `tools/call`, and prints the result. Copy it into your worktree and adapt it; do not depend on that path surviving.
- The stale binding that produced #604's crash was `~/.claude.json`'s `spine-epic` entry, pinned to `.agent-work/epic-418-followon/spine.json`. It has been **removed**, so reproduce the crash by pointing a server at any nonexistent spine directory rather than expecting that entry to still be there.
- Epic 568's full record, including every door incident: `.agent-work/archive/2026-08-15-epic-568/ADMIRAL_LOG.md`.

## Budget

- **Model tier (required):** Opus 5. This is a design change to how a long-lived server acquires its identity, with a guard that must not be weakened while it is made reachable. Float to the Admiral if you believe a lower tier suffices.
- **Compute/time, session-window:** one working session. If you need a second, hand off at a gate boundary with a digest rather than running long.

## Stop Conditions

Stop and return when: the mission's scope is exceeded, a decision outside your inherited latitude is needed, the budget is crossed, evidence is impossible, or you need context this order does not cover and cannot safely proceed without — return-and-query the Admiral. Asking up is always sanctioned.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap (150K on a 1M-window model), so a Commander that has loaded its skill, references, templates and this order can be over it on turn one having done no work. The engine refuses only `start` and `reopen`, and only until a refresh-request exists for that gate. The legal sequence is: **attach the refresh-request against the current why-record, then `start`, then work.** Attaching first sends the guard down its release path; starting first is what gets refused.

Do not read a HARD advisory, or a `REFRESH REQUESTED:` line inherited from a predecessor, as an instruction to `advance --why` and hand off on turn one. That produces an infinite handoff chain with no deliverable ever written. Hand off when you have actually spent the context, not when you inherit the reading.

## Return Shape

A verdict — shipped, blocked with a measured reason, or an honest null — plus:

1. **Evidence per defect:** for #604, the crash reproduced and then not reproduced, with the process exit code both times. For #603, a probe transcript showing an unbound door refusing by name, then `spine_open` binding it, then a real verb succeeding. For #605, the demo spine driven from a directory that is not the one it was generated in.
2. **Full clean-env, cache-cleared Linux suite** at your exact published head, with the count, and the `main` baseline **re-measured at gate time**.
3. **Map impact:** whether `map/INDEX.md` changed and that you rebuilt it.
4. **Triage candidates** for anything you find outside this scope — filed as recommendations in your notes, not implemented.
5. **Workflow feedback** on the tooling itself. If you are fenced from writing `.agent-work/CONSTELLATION_FEEDBACK.md`, stage the export in your work area and leave a `FENCE.md` citing this order — and know that the harvest has failed before, so name the staged path explicitly in your return report rather than trusting the sweep.
6. Your `verify_worktree_isolation.py --here` output, as evidence you worked in isolation.

Park at `archive`. **Do not merge.** Publication is the Admiral's delegated class; open the PR, push the branch, and report.

Write your result artifact and send your verdict **before** going idle: an idle notification with no artifact reads as stalled, not done.
