# Launch Order: `cleanup-b-context-identity — #600, #500`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Commanders start cold. Everything you need is pasted below.

## Mission

Make a context reading, and a refresh-request, belong to an **agent** instead of to a **folder**.

**1. #600 — the gauge identifies a directory.** `checklist_engine.py:1348`:

```python
def _gauge_path(base_dir: Path | None) -> Path | None:
    """The gauge file for this checklist: `.agent-work/<work_id>/gauge.json`..."""
    return Path(base_dir) / "gauge.json"
```

One file per work directory, no agent identity in the path, and none among the four fields the reader requires (`gauge_reader.py:24`). `resolve_gauge_path` in `gauge_writer_hook.py:233` was made key-aware under #419/#477 — it looks up bindings under `session_id#agent_id` — but still resolves every binding to that same per-folder file. The *lookup* is per-agent; the *file* is not. That is the ground #477 was closed on, and the symptom is back.

Measured on another fleet, 2026-08-15: leg 2 of a relaunched Commander was told `CONTEXT 18% (>= hard)` and instructed to stop. The number was leg 1's. Leg 2 had done almost nothing.

**2. The workaround does not exist either.** Moving the stale file aside fails, because the writer runs on PostToolUse for every Bash call and re-creates it before the next engine command reads it. Only deleting it immediately before each blocked call worked, which the Commander discovered on its own.

**3. #500 — a refresh-request has no consume path.** An agent that stops early leaves a `refresh-request`. The successor — the agent that *is* the refresh — reads it and is told to close its gate and stop. Nothing removes it. Every relaunch had to be briefed by hand to disregard it, which means the tooling's instruction and the doctrine's instruction were in direct contradiction and a human's note broke the tie.

**Your first task is a measurement, not a change.** #600 records an open question: whose reading the re-created file carries at the moment of a trip. Two candidates, both consistent with the code — the write is skipped on an ambiguous or unresolvable binding and the stale file survives, or another agent's key resolves into the same directory and writes its own fill. Capture `gauge.json` plus `.agent-work/.spine-rail-binding.json` at the instant of a refusal and settle it. Design after you know.

## Prior-Wave Verdicts (pasted)

Already landed on `main` at `a69bbac4`, and you inherit it — **#601**, from `checklist_engine.py`'s claim path:

> A relaunched agent reuses its predecessor's session name, so `claim` took the idempotent same-session branch, which refreshed `last_heartbeat` and returned — leaving `claimed_at` pinned at the first leg's claim. The successor's inherited reading was therefore `observed_at > claimed_at`, read as owned, and #477's guard sat there doing nothing on precisely the case it exists for. `claim` now re-stamps `claimed_at`, and the guard fires.

Its residual is your mission's core, stated in the code at the fix site:

> Because ownership is measured in TIME, `claim` is now a one-call governor deferral — an agent over the line can re-claim and get one unguarded verb before the next sample lands. It is journaled, so it is auditable rather than silent, and the real fix is to measure ownership by IDENTITY (#600), which retires this whole timestamp comparison.

From #500's own history: the cheap display-side stopgap **does not work**, and this was checked rather than assumed. Passing the current why-record id into `has_pending_refresh_request` from `_why_suffix` (`:1297`) so the display uses #190's identity filter sounds right, but the successor's latest why-record on turn one is still the one the request was raised against, so it matches and renders anyway. It stops rendering only after the successor advances, by which point the gate is closed.

From `has_pending_refresh_request`'s own docstring: *"It is pending while present and not superseded (the reopen cascade supersedes evidence; the flow that consumes/fulfils it is #183)."* #183 is closed as skill and doctrine wiring only. The mechanism was never built.

## Pre-Rulings

- `decision:identity-not-time` — ownership of a reading is decided by the binding key that produced it, not by comparing timestamps. #601's timestamp comparison is a bridge and should end up unnecessary, though you are not required to delete it in this wave.
  `@grade: settled/human · leans g1-implement`
- `decision:unattributable-means-no-reading` — a reading the caller cannot be shown to own yields `None`, and `None` means no trip. The governor fails **open** on uncertainty, exactly as it does today for a stale or malformed record. Do not invent a new refusal here.
  `@grade: settled/measured · leans g1-implement`
- `decision:consume-on-lease-change` — a refresh-request is served when a **different process takes the lease**, because that event *is* the refresh. Same-session heartbeat is not consumption.
  `@grade: guess · leans g2 · settle: enumerate what distinguishes a relaunch from an idempotent re-claim now that #601 re-stamps claimed_at, and say whether it is sufficient`
- `decision:no-new-state-file` — attribution rides in the record or the filename, not in a new sidecar with its own lifecycle. This subsystem already has a binding store, a nudge store, a gauge and a lease; a fifth is a cost, not a fix.
  `@grade: guess · leans g1-implement · settle: if per-agent filenames prove unworkable, float rather than adding a store`
- `decision:measure-before-design` — the #600 open question is settled by captured artifacts before any design is frozen.
  `@grade: settled/human · leans g0-measure`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. If the measurement shows the stale reading survives for a reason neither candidate predicts, that finding is the deliverable — report it and stop rather than shipping a fix aimed at the wrong mechanism.

## Inherited Latitude

**You may decide:** the attribution scheme (per-agent filename versus an owner field in the record), where consumption is triggered, test structure, and whether #500's fix ships in this wave or is handed back as a settled design with #600 shipped alone.

**You must float to the Admiral:** anything that makes the governor refuse where it currently permits; any change to `claim`'s semantics beyond what #601 landed; any change to `spine_rail.py` or `run_crew.py` (lane C owns both); publication.

## File Ownership

Your working-notes file is `notes-b.md`, sole writer this wave.

> Name it `notes-<n>.md`, **never** `findings-<n>.md` — the harness `Write` tool refuses any path whose basename contains "findings".

**Files you own:** `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/checklist_engine.py` **in the gauge, trip and refresh regions only** (roughly `_gauge_path` through `_why_suffix` and the trip block), plus their tests.

**Fenced — do not touch:** `scripts/hooks/spine_rail.py`, `scripts/run_crew.py` (lane C), `scripts/mcp_spine_server.py`, `.mcp.json` (lane A). `checklist_engine.py`'s claim path was changed on `main` this morning; leave it alone unless your design requires it, and say so if it does.

**One interaction you must know about:** lane C is fixing #549 concurrently — an orchestrator's Stop hook seeing a subordinate's spine through `session_view`'s per-agent merge. That is candidate 2 of your open question. If C lands first, **re-measure**; your first measurement may describe a world that no longer exists.

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`, branch `cleanup/b-context-identity`, base commit `a69bbac4`, created with:

```
git worktree add .worktrees/cleanup-b-context-identity -b cleanup/b-context-identity a69bbac4
```

`main` verified fresh at dispatch: `a69bbac4`, clean tree, suite 3057 passed / 0 failed.

First step, before any git operation: **`cd` into that worktree**, then run `py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity` — must exit 0, pasted into your report.

> **Order matters.** `--here` asserts about where you are standing. Before `cd` you get `fatal: not a git repository`, which reads as "not isolated" when the truth is "not arrived". Do **not** pass the path to git (`git -C`): that compares the worktree to itself and disarms the check (#315 / PR #576).

**Isolation is git-only — hook code is not fenced by it.** This lane changes `gauge_writer_hook.py`, which is **hook code**, so this paragraph is load-bearing for you specifically. `CLAUDE_PROJECT_DIR` is resolved once at session launch and inherited unchanged by every subagent, so your worktree still runs the **main checkout's** hook against the **main checkout's** state (#269). You cannot validate your change from inside the session that contains it. Validate with a **fresh process** whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree — a headless `claude -p` launched with that value, or a plain subprocess with the variable set — never a fixture that hand-injects the value you are trying to prove the harness delivers.

## Inherited Context

- **Platform:** Linux, Python 3.12 as `py`. Suite: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`.
- **Clear `__pycache__` before every measurement.** Stale bytecode fabricates failures that look like defects (#597); it cost epic 568 hours twice, and your lane's tests are exactly the kind that get misattributed.
- **Merge gate:** local Linux green, independent APPROVE, failure-set difference against a `main` baseline **re-measured at gate time**.
- **CI is one `windows-latest` job**, red at baseline. Local Linux is the only real signal.
- **Drive your spine through the engine CLI** with an explicit `--session-id`. The door is bound to a demo spine until lane A lands.
- **`map/INDEX.md` is generated and freshness-tested** — rebuild and commit if you add or rename entities.
- **Relaunch works now** (#601): re-claiming your own lease re-stamps `claimed_at`. You do not need `claim --force` for a routine relaunch, and you should not use it — it is a takeover of someone else's lease.

**Charter-lite carrier:** no `docs/agents/` overlay in this repo. The governor's design intent is written at length in `checklist_engine.py`'s trip block comment (from `:1304`) and in `gauge_reader.py`'s `_PROFILES` note — read both before changing either.

## Pre-empted Steps

- **Context is established by this order**; the measurements cited were taken 2026-08-15/16 against `a69bbac4`.
- **The worktree is provisioned and gate-verified** (all three lane paths, rc=0).
- **Triage is done**; #600 and #500 carry mechanisms and file:line citations. The display-side stopgap has already been checked and refuted — do not spend the wave rediscovering it.

## Data Locations

- The reader's model profiles and the absolute-cap reasoning: `scripts/gauge_reader.py:76`. A 1M-window model has a 150K hard cap, which is why a freshly briefed agent can be over the band on turn one — that is intended, and is not your defect to fix.
- #477's guard and its test class: `tests/test_checklist_engine.py::TripGaugeReadingOwnership`, which now also carries #601's two relaunch tests. Your changes belong in or beside that class.
- Epic 568's record: `.agent-work/archive/2026-08-15-epic-568/ADMIRAL_LOG.md`.

## Budget

- **Model tier (required):** Opus 5. This is a design wave with a live measurement in front of it and a governor that must not become either bypassable or trigger-happy.
- **Compute/time, session-window:** one working session for the measurement plus #600. #500 may hand back as a settled design if the session runs out; say which you are doing before you start it.

## Stop Conditions

Stop and return when scope is exceeded, a decision outside your latitude is needed, the budget is crossed, evidence is impossible, or you need context this order does not cover — return-and-query the Admiral. Asking up is always sanctioned.

**Arriving over the context HARD band is not a stop condition.** It is an absolute token cap, so you can be over it on turn one having done nothing. The engine refuses only `start` and `reopen`, and only until a refresh-request exists for the gate. The legal sequence is **attach the refresh-request against the current why-record, then `start`, then work.** Attaching first sends the guard down its release path.

Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as an instruction to hand off on turn one — that is the infinite chain you are here to end. You will be living inside your own bug this wave; note what it does to you, because that is the best evidence anyone will get.

## Return Shape

A verdict — shipped, blocked with a measured reason, or an honest null — plus:

1. **The settled measurement first:** which mechanism leaves the stale reading in place, with the captured `gauge.json` and binding store contents that prove it. This is a deliverable in its own right even if no code ships.
2. **Evidence per change:** red-before / green-after over behavior, driving the real reader and a real gauge file, never a patched `_read_gauge` — the existing class's own standard.
3. **Full clean-env, cache-cleared suite** at your published head, plus a `main` baseline re-measured at gate time.
4. **Whether #549 landed while you worked**, and if so your re-measurement.
5. **Map impact**, triage candidates, workflow feedback (stage it and cite the fence if you are blocked from the durable root; name the staged path in your report).
6. Your `--here` output.

Park at `archive`. **Do not merge** — publication is the Admiral's class. Deliver the artifact before going idle.
