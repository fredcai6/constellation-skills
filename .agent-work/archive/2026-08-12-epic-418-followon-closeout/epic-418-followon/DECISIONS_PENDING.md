# Decisions queued for Tommy — epic-418-followon

The refreshed latitude contract (2026-08-10, AFK mode) says a surfaced decision **queues** here and
the work routes around it, rather than halting the run. Present these on his return.

## 1. PR #555 — Windows launch: resume, close, or leave parked?

**Status:** parked, carried verbatim through the `w3x-door-binding` replan as a launched identity
that may not be silently dropped. No spend authorized against it this wave.

**What is true:** the branch head is `6b947546` (*not* `3f8f693c`), CI-green on `windows-latest`
(run 31405772388, no failed steps). The repair agent was stopped mid-run, so the full suite never
completed under supervision and **no cold reviewer has seen that commit.** Two prior review rounds
each found a real user-scope write that CI was green through.

**Why it is not obviously worth resuming:** it was launched against the belief that Windows launch
gated adoption. That belief is now falsified — the door launches correctly here and was still
unusable. Windows remains a genuine defect, just not this round's blocker, and he already accepted
being broken on Windows for now.

**Recommendation:** leave parked until the adoption work lands, then resume it *together with*
`--wire-hooks` (#560), which has the same flag-not-path shape. Designing the write location once for
both beats repairing them separately — the last two rounds each fixed one guess and invited the next.

## 2. `docs/agents/CREW_CONTEXT.md` is wrong about Python on this host (#561)

**Surfaced because** promoting anything into `docs/agents/*` is a human's call, always.

**Measured 2026-08-10:** `py` and `python` are the same install at `~/.local/bin`, both carrying
pytest 9.1.1. `/usr/bin/python3` is the one **without** pytest. The committed section names `py` as
the broken interpreter, never mentions `python3`, and its version claims (3.12.13, 3.14.x) are both
wrong here — everything measures 3.12.3.

**Cost of leaving it:** every crew reads it. This dispatch had to carry a correction inline in both
the handoff and the spine imperative to stop the implementer following it into a misleading
`No module named pytest`.

**Recommendation:** patch it. Filed rather than patched only because the file is his call.

## 3. `run_crew.py`'s `cli` backend grants no permissions — should that be fixed in the launcher?

**Found 2026-08-10:** `build_crew_argv` builds `[claude, -p, prompt] (+ --model)` with **no
`--allowedTools` and no `--permission-mode`**. Every prior crew in this epic went out on the
`external` backend instead; all 7 registry entries are `backend: external` with null session and pid.

This dispatch worked around it with a per-dispatch, **gitignored** `.claude/settings.local.json` in
the worktree. That is legitimate and touches no tracked file, but it means the sanctioned launcher's
own spawn path only works if the caller remembers to write a settings file first.

**Why it matters to the goal:** a spawned process is the only dispatch shape that can own its own
door binding. The adoption path runs straight through the backend nobody uses.

**Recommendation:** fold the grant into `run_crew.py` so the launcher is self-sufficient. Not done
in M1 — it is a separate change and M1 is deliberately one wire.

## 4. Merge authority for M1

The contract's hard floor keeps **merge or push to `main`** surfaced even under the AFK grant. M1
will land reviewed and green on `epic-418/m1-door-binding` and then wait for him.
