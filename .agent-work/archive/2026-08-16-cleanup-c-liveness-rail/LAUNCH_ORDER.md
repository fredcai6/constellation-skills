# Launch Order: `cleanup-c-liveness-rail — #599, #549`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Commanders start cold. Everything you need is pasted below.

## Mission

Two questions the fleet asks constantly and gets wrong answers to: **is anything already running?** and **whose gate is this?**

**1. #599 — the registry answers from a status string.** `run_crew.py:252`, `active_duplicate()` — the predicate both the launch refusal and `recover_crews` consult:

```python
if is_abandoned(entry): continue
if entry.get("status") not in ACTIVE_STATUSES: continue
if entry.get("work_id") == work_id and ... : return entry
```

No PID check, no heartbeat-freshness check. A crew that dies, is killed, or never starts keeps `status: running` forever, because only an explicit `abandoned` mark clears it — so it reads as alive and holds the lock. A crew that is working but whose entry was never written reads as absent. `process_alive(pid)` **already exists** at `:864`, with `os.kill(pid, 0)` semantics and an injectable seam for tests; the guard simply never calls it. The `external` backend makes the first direction structural: those entries are recorded `pid=None` by design (`:1393`), so a killed external run is indistinguishable from a working one.

Observed on another fleet, 2026-08-15/16: three occurrences on one Commander in one night — `running` for a helper that never started, dead for one that was working. The Commander stopped believing the registry and read heartbeat files on disk instead. A phantom entry held a job's lock and another agent had to force it away. The next wave dispatches four Commanders concurrently, and doctrine requires asking the registry before every dispatch.

**2. #549 — the Stop hook hands an orchestrator its subordinate's gates.** `session_view` (`spine_rail.py:515`) merges every per-agent key `sid#agent_id` back into the parent's view, so a subordinate's spine is visible to the parent's Stop. The only thing normally suppressing it is `_foreign_worktree` (`:639`), which skips an entry when the stopping session's cwd differs from the binding's recorded worktree — so an orchestrator whose shell sits in a subordinate's worktree, the normal state right after provisioning or inspecting one, looks like the legitimate driver.

Twice in one night an Admiral was instructed to author its Commander's mission frame and drive its gates while that Commander was alive and holding the lease. It refused both times. Complying would have broken the single hard prohibition in its own active imperative and raced a live agent on state whose lease it holds.

**The fix is to separate the two halves.** The block is the safe half. Rendering someone else's imperative into an orchestrator's turn is the unsafe half. Keep blocking; stop instructing. An entry reachable only through a per-agent key should say *"spine X belongs to session Y; it is not yours to drive"* instead of that spine's next imperative.

## Prior-Wave Verdicts (pasted)

From an archived triage candidate written during the post-epic-568 wave and never filed until now (`.agent-work/archive/2026-08-15-triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md`) — the same registry failure, seen twice, described in the Commanders' own words:

> `epic-568-441` attempt 1: *"I'll pause here and resume automatically once the background implementer crew finishes."* No such crew existed; it had read a **stale `external` registry entry** left by a Codex run killed a day earlier (`status: running`, `pid: null`, `last_heartbeat == started_at`).
>
> `tc1-windows-path-form` attempt 1: *"The implementer crew (background task `bds4xeqiq`, PID 3033423) is running..."* PID gone at inspection; **no implementer entry in the registry at all**.

And its third observation, which tells you the shape of the bug:

> `crew-verdict-and-door` dispatched implementer **and** reviewer crews on the same machine, in the same wave, and finished cleanly. Its children returned inside the foreground window and were never auto-backgrounded. So the defect does not fire on short dispatches. It fires on **long** ones — which are precisely the substantial implementation tasks where losing the run is most expensive.

From #591, which declined the adjacent Stop-hook check and recorded why: `decide_stop` already refuses a mid-flight turn-end, and its binding precondition engaged only for a Bash-matcher `checklist_engine.py claim`, never for an MCP-door `spine_lease` claim. That gap was closed in #593. The rail is otherwise sound — you are changing what it *says*, not whether it fires.

## Pre-Rulings

- `decision:fail-toward-active` — when liveness cannot be corroborated, report the entry as **active**, not free. A live crew wrongly declared dead means two agents on one gate; a phantom that blocks a dispatch is merely annoying and is visible. This direction is not negotiable without floating.
  `@grade: settled/human · leans g1-implement`
- `decision:three-states-not-two` — the query reports `active`, `stale`, or `unknown` rather than collapsing all three into a boolean drawn from a string nobody refreshes. The caller decides what to do with `stale`; the predicate's job is to stop lying.
  `@grade: settled/measured · leans g1-implement`
- `decision:pidless-means-heartbeat` — an `external` entry has no PID by design, so its corroboration is heartbeat age against a bound window. `last_heartbeat == started_at` after that window is the phantom signature seen twice already.
  `@grade: guess · leans g1-implement · settle: pick the window from the two observed phantoms and the one healthy run, and state the number you chose and why`
- `decision:keep-the-block-drop-the-imperative` — #549's fix does not weaken `decide_stop`. It changes the rendered reason for an entry reachable only through a per-agent key.
  `@grade: settled/human · leans g2`
- `decision:no-abandonment-by-inference` — do not auto-mark entries `abandoned` as a side effect of a liveness read. Reporting `stale` is the deliverable; reaping is a separate decision with its own blast radius (#552).
  `@grade: settled/human · leans g1-implement`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. In particular, if `session_view` cannot return provenance without a change wider than this lane's ownership, say so with the measurement and stop — a partial refactor of the binding readers is worse than a clear report that it needs its own wave.

## Inherited Latitude

**You may decide:** the corroboration window for pid-less entries, the shape of the three-state result, how provenance travels out of `session_view`, the refusal wording, and test structure.

**You must float to the Admiral:** anything that makes `decide_stop` allow a stop it currently blocks; any auto-reaping or auto-abandonment; any change to `checklist_engine.py` (lane B owns the engine this wave); publication.

## File Ownership

Your working-notes file is `notes-c.md`, sole writer this wave.

> Name it `notes-<n>.md`, **never** `findings-<n>.md` — the harness `Write` tool refuses any basename containing "findings".

**Files you own:** `scripts/run_crew.py`, `scripts/hooks/spine_rail.py`, `tests/test_crew_launcher.py`, `tests/test_spine_rail.py`, and any new test files for either.

**Fenced — do not touch:** `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py` (lane B), `scripts/mcp_spine_server.py`, `.mcp.json` (lane A).

**One interaction, and it runs your way:** lane B's #600 names "an orchestrator writing its own reading into a subordinate's gauge" as one of two candidate mechanisms for a defect it is measuring. Your #549 fix removes that possibility. **Tell the Admiral the moment #549 lands** so B can re-measure rather than reasoning about a world that has changed underneath it.

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/cleanup-c-liveness-rail`, branch `cleanup/c-liveness-rail`, base commit `a69bbac4`, created with:

```
git worktree add .worktrees/cleanup-c-liveness-rail -b cleanup/c-liveness-rail a69bbac4
```

`main` verified fresh at dispatch: `a69bbac4`, clean tree, suite 3057 passed / 0 failed.

First step, before any git operation: **`cd` into that worktree**, then run `py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/cleanup-c-liveness-rail` — must exit 0, pasted into your report.

> **Order matters.** `--here` asserts about where you are standing; run it before `cd` and you get `fatal: not a git repository`, which reads as "not isolated" when the truth is "not arrived". Do **not** pass the path to git (`git -C`) — that compares the worktree to itself and disarms the check (#315 / PR #576).

**Isolation is git-only — hook code is not fenced by it.** This is the load-bearing paragraph for your lane: `spine_rail.py` **is** the hook, and it fires on your own turns. `CLAUDE_PROJECT_DIR` is resolved once at session launch and inherited unchanged by every subagent, so your worktree runs the **main checkout's** hook against the **main checkout's** state (#269). You cannot validate this change from inside the session that contains it — that is the same process the harness would use to run the unchanged code. Validate with a **fresh process** whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree, or by calling `decide_stop` directly with constructed payloads and a constructed binding store. Never a fixture that hand-injects the value you are trying to prove the harness delivers.

You will also be **subject to the rail you are changing** for the whole wave. Keep your own shell in your worktree, not in a subordinate's, and do not read your own Stop behavior as evidence about the fix.

## Inherited Context

- **Platform:** Linux, Python 3.12 as `py`. Suite: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`.
- **Clear `__pycache__` before every measurement** (#597).
- **Merge gate:** local Linux green, independent APPROVE, failure-set difference against a `main` baseline re-measured at gate time.
- **CI is one `windows-latest` job**, red at baseline. `os.kill(pid, 0)` is POSIX; `process_alive` already carries the cross-platform seam — do not break it, and say what you did about Windows even though CI cannot tell you.
- **Drive your spine through the engine CLI** with an explicit `--session-id` until lane A lands the door fix.
- **`map/INDEX.md` is generated and freshness-tested** — rebuild and commit if entities change.
- **Relaunch works now** (#601): re-claiming your own lease re-stamps `claimed_at`. Do not use `claim --force` for a routine relaunch; it is a takeover.

**Charter-lite carrier:** no `docs/agents/` overlay. `skills/commander/references/crew-dispatch.md` carries the dispatch contract, including the auto-backgrounding hazard documented in #591 — read it before changing what "running" means.

## Pre-empted Steps

- **Context is established by this order.**
- **The worktree is provisioned and gate-verified.**
- **Triage is done** — #599 and #549 carry mechanisms and file:line citations, and #549 carries a written correction of the reporter's own theory (it is not proximity; it is the per-agent key merge). Implement; do not re-derive.

## Data Locations

- The two phantom signatures, in full, in the archived triage candidate quoted above: `.agent-work/archive/2026-08-15-triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md`.
- Live registry files to read for shape (not to mutate): `.agent-work/archive/*/crew-runs.json` and the `crew-runs.post-archive.json` variants swept in `adc4f668`.
- The binding store this repo actually carries, including entries from 2026-08-09 pointing at paths that no longer exist: `.agent-work/.spine-rail-binding.json`. Useful as a realistic fixture; #552 owns cleaning it up, you do not.

## Budget

- **Model tier (required):** Sonnet 5. Both changes have specified semantics and named seams; the judgement is concentrated in the fail-toward-active direction, which is pre-ruled. **Escalate to Opus 5 and tell the Admiral** if `session_view` provenance turns out to touch more readers than `decide_stop` and `decide_session_start`.
- **Compute/time, session-window:** one working session for both. #599 first — it is what makes a four-Commander wave safe.

## Stop Conditions

Stop and return when scope is exceeded, a decision outside your latitude is needed, the budget is crossed, evidence is impossible, or you need context this order does not cover — return-and-query the Admiral. Asking up is always sanctioned.

**Arriving over the context HARD band is not a stop condition.** Absolute token cap; you can be over it on turn one having done nothing. The engine refuses only `start` and `reopen`, and only until a refresh-request exists for the gate: **attach the refresh-request against the current why-record, then `start`, then work.**

Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as an instruction to hand off on turn one.

## Return Shape

A verdict — shipped, blocked with a measured reason, or an honest null — plus:

1. **Evidence per defect.** For #599: both directions, each shown wrong before and right after — a dead-PID entry that stops reading as active, and a live crew that keeps reading as active. Use the real `crew-runs.json` shape, not a hand-built dict, and state the corroboration window you chose for pid-less entries and why.
2. For #549: a constructed payload where an orchestrator's Stop meets a subordinate's per-agent-keyed binding, asserting that the stop is **still blocked** and that the rendered reason names the owning session instead of the subordinate's imperative. Both halves, or the test proves nothing.
3. **Full clean-env, cache-cleared suite** at your published head, plus a `main` baseline re-measured at gate time.
4. **A note to the Admiral the moment #549 lands**, for lane B's re-measurement.
5. **Map impact**, triage candidates, workflow feedback (stage and cite the fence if blocked from the durable root; name the staged path in your report).
6. Your `--here` output.

Park at `archive`. **Do not merge** — publication is the Admiral's class. Deliver the artifact before going idle.
