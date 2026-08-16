# Triage Recommendation: `run_log_paths` omits `worktree` from its stdout/stderr naming

## Classification
`bug`

## Source checklist/artifact
- `execute.json` `triage_candidates[0]`, found while scoping g2's `scratch_dir` key tuple against `active_duplicate`/`next_attempt`'s real scoping.

## Structural anchor
`scripts/run_crew.py:230-234` (`run_log_paths`), cross-referenced against `scripts/run_crew.py:330-390` (`active_duplicate`, `next_attempt`)

## Cartographer mismatch class
none

## Observations

### Observation 1
- **What's wrong:** `run_log_paths(work_id, gate, role, attempt, root)` builds each dispatch's stdout/stderr capture path from a 4-field tuple (`work_id`, `gate`, `role`, `attempt`) that omits `worktree`, while `active_duplicate`/`next_attempt` — the functions that decide whether a dispatch is a duplicate and what attempt number it gets — key on the full 5-field tuple `(work_id, gate, role, worktree, attempt)`. Since `next_attempt` scopes attempt numbers per-worktree, two different worktrees dispatching the same `work_id`/`gate`/`role` can each independently reach `attempt=1`, and both would compute the identical `run_log_paths` stdout/stderr file pair.
- **Expected:** two dispatches distinguishable only by worktree should never share a stdout/stderr capture path.
- **Conditions:** two git worktrees dispatching a crew for the same `work_id`/`gate`/`role`, both starting fresh (no prior attempt recorded for either worktree) — a realistic shape whenever the same work item is being driven from more than one worktree (e.g. two Commander instances resuming/relaunching after a worktree move).
- **Type:** `inferred` — read directly off `run_log_paths`'s signature (`run_crew.py:230`) against `next_attempt`'s real per-worktree scoping (`run_crew.py:380-390`), not exercised against a live collision; no test currently forces this specific two-worktree scenario.
- **Rev:** `cleanup/e-crew-tooling` at the commit this run integrated (`scripts/run_crew.py` as of g2-integrate, base `e36e630b`).

## Possible fix
Add `worktree` to `run_log_paths`'s signature and fold it into the path (the same worktree-hashing approach this run's `scratch_dir` uses would be a natural, already-reviewed precedent) — but this changes every existing dispatch's stdout/stderr path shape, which is a behavior change touching every caller and every archived registry entry's recorded `stdout`/`stderr` fields, not a narrow patch. Worth scoping carefully rather than assumed trivial.

## Open questions
- Is a two-worktree-same-work-id-same-gate-same-role dispatch a real, observed shape in this repo's actual usage, or only a theoretical one implied by `next_attempt`'s scoping? If never observed in practice, this may be a `low`-priority latent risk rather than an active defect.

## Recommended priority
`low`

**Reason:** Narrower in blast radius than #525 (only stdout/stderr *capture* paths collide, not evidence/scratch content itself — a collision here would interleave/overwrite log text, not silently misattribute a gate's actual findings), and no observed occurrence yet; the risk is structural, inferred from the code, not measured from an incident the way #525 was.

## Related artifacts
- `scripts/run_crew.py:230-234`, `:380-390`
- `.agent-work/cleanup-e-crew-tooling/execute.json` (g2's anchors block, where this was found and explicitly excluded from g2's scope)

## Disposition
`recommend-and-defer`

**Detail:** This run's launch order (`LAUNCH_ORDER.md`) grants latitude over "the namespacing scheme's exact shape, the error surface for a collision, and test structure" for #525 specifically — it does not grant authority to file new GitHub issues, and `docs/agents/ORCHESTRATOR_CONTEXT.md`'s Repo Action Authority section covers commits/pushes/PRs, not issue creation. Filing authority is unclear this run; producing the recommendation and deferring the filing decision.

## Issue creation authority
`ask user`
