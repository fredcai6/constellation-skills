# Crash-resume state note — epic-568

- **step:** execute · final archive · all three wave-2 lanes merged; only #510's archive stands between here and epic closeout
- **slug:** epic-568 · `main` at `addf98c6` (#579 `e0c998b6`, #580 `c23c3d0f`, #581 `addf98c6`) · last open lane `.worktrees/epic-568-510`
- **next command:** dispatch the #510 archive Commander (`--backend cli --spine .worktrees/epic-568-510/.agent-work/epic-568-510/spine.json`), then drive the epic's own `closeout` via `python scripts/checklist_engine.py --file .agent-work/epic-568/spine.json <verb> --session-id admiral-epic-568`
- **pid:** #510 archive Commander launching now via backend `cli`; record its launcher PID here at spawn. Nothing else in flight.
- **expected artifact:** `archive` complete and lease **released** on `epic-568-510`, then the epic retrospective and architecture audits, then release of the epic lease **last**

## Ground truth at 2026-08-15T00:20Z

| Lane | State | Next |
|---|---|---|
| Codex tier | **MERGED** → `main` at `e0c998b6` | archive attempt 2 in flight (attempt 1 abandoned via registry) |
| #530 | **MERGED** → `main` at `c23c3d0f` | done; lease still held pending its own archive |
| #510 | engine change in flight, base `23ed6b70` | re-measure, then publish under the delegated class |
| #441 | `execute` blocked, external Codex quota | resumes after 2026-08-20T06:19Z |

## Gate procedure — do not skip

1. Clear `__pycache__` before **every** measurement. Stale `.pyc` from the wave-1 relocation
   fabricates failures that look exactly like defects.
2. Re-measure the `main` baseline at gate time. It has moved twice today (`0448275e` → `e0c998b6` →
   `c23c3d0f`) and the CI baseline moved 84 → 89 failures with it.
3. Merge gate, as amended three times: local Linux green, independent APPROVE, and a set difference
   that is empty **or** whose additions all carry an error signature already on the baseline
   (the human's cause-based amendment, 2026-08-14).
4. CI is one `windows-latest` job. There is no Linux CI. Local measurement is the only Linux signal.

## Standing corrections to my own orders

- Publication is the Admiral's delegated `merge-to-main` class. Commanders park at `archive` by design.
- **"MCP-only" is withdrawn as a blanket constraint.** The door binds at import from `.mcp.json`'s
  demo default and cannot be rebound, so out-of-band dispatch hands a child a door pointing at the
  demo spine. Dispatch through the `cli` backend with `--spine` when the child must mutate a spine;
  otherwise state plainly that the door may be unbound and authorize a disclosed CLI fallback.
- A frozen order freezes what was *true when written*. Two orders this run carried facts that went
  stale before the Commander read them. Re-check PR and `main` state at dispatch time.

## Open Admiral obligations

1. Adjudicate both in-flight returns; re-measure #510 at its exact head rather than trusting its numbers.
2. #510 may still come back with an honest null — its order permits stopping if the `_trip_hard_gate`
   refusal proves load-bearing. That would revise the human's ruling, not violate it.
3. The epic spine door is down and `mcp__spine__` binds to the demo spine, **but the epic spine is
   still drivable and closeout is reachable.** The contract's pre-ruling
   `decision:door-unusable-this-session` (`settled/measured · leans all-waves`) authorizes the
   Admiral to drive its own spine through the engine CLI with an explicit `--session-id`:
   `python scripts/checklist_engine.py --file .agent-work/epic-568/spine.json <verb> --session-id admiral-epic-568`.
   Lease heartbeated at `2026-08-15T00:48:23Z` by that path. The MCP-only rule in the replan packet
   binds **Commanders**, not the Admiral — do not over-apply it as I initially did.
4. Two triage candidates are filed and unimplemented; neither is authorized under the current contract.
5. **The contract expires when the wave-2 items are dispositioned.** A refresh is due before any work
   beyond them — including the two filed defects.
6. Commander leases (#510, #530, Codex) stay live by design. Release is last, after a terminal archive.
   The epic lease is released last of all.

_Updated: 2026-08-15T00:20:00Z_
