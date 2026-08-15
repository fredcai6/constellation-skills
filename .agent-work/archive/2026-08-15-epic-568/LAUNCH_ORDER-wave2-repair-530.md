# Launch Order: `epic-568-530 — repair — resolved worktree binding`

**Issued:** 2026-08-14 by `admiral-epic-568` · **Boundary:** `wave-2-gate-refusal` · **Launch:** `epic-568-wave-2-repair`
**Frozen.** Read it as written. Where it is wrong, say so and float rather than quietly working around it.

## Mission

Your lane's implementation is done and independently APPROVEd. It does not merge, because the lane
fails its own full Linux suite — and notably, not because of the production change. Make it green
without weakening what it proved, then take it to `archive`. You are repairing a launched issue: its
identity, intent, and desired outcome are unchanged and are not yours to revise.

## Prior-Wave Verdicts (pasted)

Verbatim from the wave-2 gate, measured by the Admiral at 2026-08-14T20:0xZ, cache-clean:

```
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
FAILED tests/test_episode_observations.py::RealStoreTests::test_the_real_store_is_clean_under_strict
FAILED tests/test_episode_observations.py::RealStoreTests::test_the_real_store_scan_actually_examined_the_records
3 failed, 2979 passed, 7 skipped, 1130 subtests passed in 120.94s
```

`main` baseline re-measured at the same gate: **2980 passed, 7 skipped, 0 failed** at `0448275e`.
Every failure above is therefore introduced by this lane. The guard names the offender exactly:

```
OFFENDER epic-568-530-001 a5 (workaround) imperative: 'Use'
episode-observation guard: 806 statements examined, offenders: 1 unlisted, 11 on the exception list
```

Your `spine_rail.py` fix and its 93 lines of tests are not implicated in any of this. The episode
record you wrote about your own run is.

## Pre-Rulings

1. **`decision:episode-guard-is-mechanical` — settled.** Reword the `a5 (workaround)` statement in
   `episodes/active/epic-568-530-001.md` so it reads as an observation rather than an instruction.
   The `apply_patch` incident it records is worth keeping; only its phrasing trips the guard. Prefer
   rewording over adding an exception entry — the exception list is for statements that genuinely
   must stay imperative, and this one does not.
2. **`decision:repro-before-and-after` — settled.** The issue still closes on its real-worktree
   red/green guard repro. Do not delete or weaken a failing test to reach green.
3. **`decision:map-refresh-is-mechanical` — settled.** Regenerate with
   `python -m scripts.code_map build --root .` and commit it. No judgement required.
4. **`decision:clear-caches-before-measuring` — settled.** `find . -name __pycache__ -type d -not
   -path './.git/*' -prune -exec rm -rf {} +` before **every** suite run. A stale `.pyc` carrying the
   pre-relocation path `constellation-skills-wt/` fabricated a failure elsewhere in this wave and
   cost four falsifications to attribute. Do not trust a gate measured without this.
5. **`decision:sandbox-workaround-stands` — settled.** Your predecessor hit
   `bwrap: loopback: Failed RTM_NEWADDR` behind `tools.apply_patch`, floated it, and was approved to
   use the direct `apply_patch` TTY path. That approval carries over. Do not substitute a shell or
   Python rewrite path.

## Honest-Null Clause

A measured negative is a complete, successful deliverable. If rewording the record does not clear
the guard, or the guard is itself wrong about this statement, report that plainly rather than
forcing green. Do not invent work to look productive.

## Inherited Latitude

Bounded internals inside your own diff are yours. Direction, intent, scope, production defaults, and
agent-visible behavior are not. You may not revise the issue's identity or desired outcome — this is
a repair, not a re-cut.

## File Ownership

Yours: `scripts/hooks/spine_rail.py` (you hold the serialized lane), `tests/test_spine_rail.py`,
`episodes/active/epic-568-530-001.md`, `map/INDEX.md`.
Not yours: `scripts/checklist_engine.py` — #510 holds that lane concurrently. Touching it breaks the
one-implementer rule.

Note: `tests/test_spine_rail.py` currently has an uncommitted modification in your worktree. Decide
deliberately whether it belongs in this lane, and say which way you went.

## Workspace

Worktree `.worktrees/epic-568-530`, branch `epic-568/530-binding`, spine
`.agent-work/epic-568-530/spine.json`. It is yours alone; no second Commander enters it. The spine's
lease is live and held by your predecessor's dead session — take it over, do not recreate it, and
release it last. Your spine is at `archive` blocked; reopen the gate you actually need through MCP
rather than editing spine state by hand.

## Inherited Context

Wave 1 (`#576`, `#577`, `#578`) put spine origin and worktree isolation on `main` at `0448275e`.
Spine interaction is MCP-only. #441 also implicates `spine_rail.py` but is fenced by an external
Codex quota until 2026-08-20, so the lane is yours uncontested.

## Pre-empted Steps

Do not re-run `understand` or `plan`; they are complete and their conclusions stand. Do not redesign
the change. Start from the three failures above.

## Data Locations

Findings file: `.agent-work/epic-568-530/FINDINGS-wave2-repair.md`. Anything you learn that is real
but outside this repair goes there, not into the diff.

## Budget

One bounded repair. If it grows past its own diff, stop and float.

## Stop Conditions

Stop and report if any of these fire:
- Clearing the guard would require changing what the episode record actually claims happened.
- Green requires touching a file outside your ownership.
- Green requires deleting or weakening a test rather than correcting a record.
- The suite stays red after the repair for a cause you cannot attribute.

## Return Shape

Report: what you reworded and why; your decision on the uncommitted `test_spine_rail.py` change; the
cache-clean full Linux suite counts before and after; confirmation the map is fresh; anything
floated. **You are fenced from push, PR, and merge** — that is the Admiral's delegated class. Take
the lane to the point where publication is all that remains, park at `archive`, and say so. Parking
there is correct behavior, not failure.
