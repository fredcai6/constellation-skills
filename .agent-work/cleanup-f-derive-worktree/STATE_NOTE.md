# Crash-resume state note — cleanup-f-derive-worktree

- **step:** execute · leg 4 · g3: 5 reviews, 4 reworks. review4 BLOCK(B6/B7, both pre-existing) → **rework4 `539ff636`, both verified fixed by me**. **`g3` review 5 is dispatching.** `FLOAT_TO_ADMIRAL-3.md` written (3 scope questions, none blocking). Then `skip` g4 (R2), `skip` g5 (R3), reconcile → triage → review → feedback → archive. **Park at `archive`; do NOT merge.**
- **slug:** cleanup-f-derive-worktree · branch `cleanup/f-derive-worktree` · worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree` · HEAD `e3e50a69` (g3 implementation committed)
- **next command:** `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py --file .agent-work/cleanup-f-derive-worktree/execute.json current`
- **pid:** commander leg 4 is pid **1634189** (foreground). The g3 review-5 reviewer is dispatched through `run_crew.py`; its pid is recorded in `crew-runs.json` under `constellation/cleanup-f-derive-worktree/g3/reviewer/attempt-5`.
- **expected artifact:** `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-reviewer-rework4-result.md` for the crew; for this leg, `.agent-work/cleanup-f-derive-worktree/crew-handoffs/execute-commander-result.md`

**Read first on resume:** `LAUNCH_ORDER-4.md`, `ADMIRAL_RULING-3.md`,
`ADMIRAL_RULING-2.md`, `ADMIRAL_RULING-1.md`, then `LAUNCH_ORDER.md`,
`PROBLEM_STATEMENT.md`, `MISSION_FRAME.md`, `UNTAKEN_ROADS.md`.

## Lease

Held at `commander-cleanup-f-derive-worktree`, re-claimed by leg 4 without
`--force` (an owner is never blocked by its own staleness). If you resume, claim
under that **same** id and **never** `--force`. The stale-heartbeat cause is
named in `ADMIRAL_RULING-3.md` (the installed `run_crew.py` predates #607); it
is not yours to fix, and it goes in when this lane parks.

## Baselines re-measured by leg 4

| tree | result |
|---|---|
| this branch at `53c89ba1` (pre-g3) | **3170 passed / 5 skipped / 0 failed** |
| `main` at `17c2cee5`, isolated clone | **3171 / 7 / 0** |
| this branch at `e3e50a69` (g3 pass 1) | **3177 / 5 / 0** |
| this branch at `6bba3fd2` (g3 rework 1) | **3183 / 5 / 0** |
| this branch at `9b1a551e` (g3 rework 2) | **3187 / 5 / 0** |

Failure-set difference empty in every direction. The g3 targeted check
(`-k OwnershipIsBindingKeyNotWorktree`) exited **5** on the empty diff and now
collects **8 passed** — it was genuinely red before the work.

**A measurement hazard leg 4 hit and cost a re-run:** if you clone the repo to
measure a baseline, **name the clone directory `constellation-skills`**.
`tests/test_code_map.py::MapTreeFreshnessTests` compares `map/INDEX.md` against a
fresh build, and the map's title line derives from the checkout directory name,
so a clone at `/tmp/anything-else` reports a false red in an otherwise
byte-identical 29k file. That is the whole of the "1 failed" leg 4 first saw on
`main`; `main` is clean.

## What remains after g3

1. **`g3-review`**, then integrate.
2. **`skip` g4** with R2 as the recorded reason, **`skip` g5** with R3.
3. **reconcile** — three prose repairs, all this lane's own debt:
   - the door's stale `SPINE = Path(os.environ["SPINE_FILE"]).resolve()` contract
     citation in `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`.
     **Cite by the string to grep for, not by line** (ADMIRAL_RULING-3). Current
     truth is `mcp_spine_server._spine_from_env`, which collapses unset, empty and
     whitespace into `None` and refuses per call via `_unbound_refusal`.
   - **tc10**: `tests/test_explorer_templates.py` and
     `tests/test_mcp_door_engine_cwd.py` assert the engine still reads its ambient
     cwd and still enforces the `origin.worktree` comparison. Both were made false
     by this lane's g2, so this lane owns the repair (ADMIRAL_RULING-3). Where a
     repaired passage contradicts the 2026-08-15 worktree-identity ruling, cite
     that ruling and say plainly that this lane supersedes it.
4. **triage** — `tc1`–`tc12` are recorded in `execute.json`.
5. **review, feedback, archive.**

## Two hazards that cost measurable time on this lane

- **`CREW_SCRATCH_DIR`.** The engine's own gate-close suite command scrubs
  `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` but **not** `CREW_SCRATCH_DIR`, and
  a Commander is itself launched through `run_crew.py`. Close gates with
  `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py … advance …`. Recorded
  as `tc12`; the Admiral has taken it as an engine defect.
- **The registry clobber (#617, folded into #574).** `run_crew.py`'s parent
  writes a pre-launch snapshot back over `crew-runs.json` when the child exits,
  destroying what the child recorded. Git is the only durable store: **commit
  `crew-runs.json` as each gate closes**, and on resume check the working copy
  against `HEAD` before trusting `recover_crews.py`.

_Updated: 2026-08-16T20:05:00+00:00_
