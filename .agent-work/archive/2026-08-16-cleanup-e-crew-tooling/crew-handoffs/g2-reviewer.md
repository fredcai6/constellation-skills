# Reviewer Handoff

## Gate
g2 (issue #525)

## Survey State Location
`.agent-work/cleanup-e-crew-tooling/g2-review/review.json`.

## What Was Implemented
`scratch_dir(work_id, gate, role, worktree, attempt, root)` in `scripts/run_crew.py`, keyed on the full 5-field tuple `active_duplicate`/`next_attempt` use (including `worktree`, hashed as a raw string, not resolved). `CliBackend.dispatch` reserves it via `Path.mkdir(exist_ok=False)` before any registry write, raising `CrewLaunchError` on collision; `CliBackend.resume` only recomputes/gets the path (no re-reserve). New `CREW_SCRATCH_DIR` env var wired into the CLI-backend child's environment; the path is recorded on the registry entry.

## How to Inspect the Diff
Uncommitted working tree, not `git diff main...HEAD`:
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-e-crew-tooling
git status --porcelain
git diff scripts/run_crew.py tests/test_crew_launcher.py
```
Note: this diff sits ON TOP of g1's already-integrated, already-reviewed changes (the `_parent_lease_heartbeat` context manager and its wraps) in the same two files — that code is NOT in scope for this review; focus on the g2 additions (`scratch_dir`, the `CREW_SCRATCH_DIR` wiring, the collision-detection in `dispatch`, the get-not-reserve path in `resume`).

## Task Statement
Full original task, close criteria, allowed scope, exclusions, constraints, and map anchors are in `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g2-implementer.md` — read it in full.

## Close Criteria
- `scratch_dir` keys on **all 5 fields**: `work_id`, `gate`, `role`, `worktree`, `attempt`. This is the single most important thing to verify — the plan gate's own cold critic caught a draft that dropped `worktree`, which would let two different worktrees dispatching the same work_id/gate/role collide at the same attempt number (since `next_attempt` scopes attempts per-worktree). Confirm the fix actually holds by tracing `next_attempt`'s real scoping and cross-checking `scratch_dir`'s signature and body.
- `worktree` is hashed as the **raw** string, never `Path(...).resolve()`'d first — confirm by reading the code, not just the docstring's claim.
- `CliBackend.dispatch`: reserves BEFORE `build_entry`/`entries.append`/`save_registry`, so a collision leaves no partial registry entry behind. Raises `CrewLaunchError` naming the path and the full tuple on `FileExistsError`.
- `CliBackend.resume`: computes the SAME path but does NOT call `mkdir` at all (no re-reservation, no raise) — an existing directory there is expected, not a collision. Confirm the legacy-entry case (`entry.get("worktree")` is `None`) degrades sanely (no crash, `CREW_SCRATCH_DIR` simply unset) rather than being silently mishandled.
- `CREW_SCRATCH_DIR` set only for the CLI backend (matches `door_bound`/`SPINE_FILE` scope) — external backend gets nothing new.
- `run_log_paths` itself is untouched (its own worktree-omission is explicitly out of scope for this gate — confirm it was NOT "fixed" as a drive-by, since that would be scope creep even though well-intentioned).
- Genuinely disjoint paths for varying gate/role/worktree/attempt; genuinely raised, never-silent collision when forced.

## Allowed Scope
Read-only review of `scripts/run_crew.py`, `tests/test_crew_launcher.py` (the g2-specific portions of the diff).

## Specific Exclusions
Do not re-review g1's `_parent_lease_heartbeat` code or tests — already reviewed and integrated at g1-review/g1-integrate. If you notice it, that's fine to mention, but it is not this gate's BLOCK surface.

## Constraints the Implementation Must Respect
`decision:no-silent-truncation` (collision raises, never overwrites), `decision:namespace-by-assignment` (tuple matches the registry's own key verbatim), no reaping/expiry/force-claim, `Path.mkdir` is cross-platform stdlib (no new POSIX-only seam).

## Map Anchors (inbound)
Same as `g2-implement`'s anchors in `execute.json` — structural: `run_crew.py:230-234` `run_log_paths`, `:330-390` `active_duplicate`/`next_attempt` (the real key tuple to verify against), `:890-968` env wiring, `:1028-1126` `build_entry`, `:1357`/`:1403` dispatch/resume. Decision: `namespace-by-assignment`, `no-silent-truncation`.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g2-implementer-result.md` — read in full. Claims 206 tests pass (188 g1 + 18 new), a concrete disjoint-paths demonstration, and the exact `CrewLaunchError` message on a forced collision. Independently re-run the mechanical test command; do not accept the collision-message claim without reading the actual code path that raises it.

## Suggested Model Tier
stronger — the worktree-in-key-tuple correctness is exactly the kind of subtle regression the plan-gate critic already caught once.

## Stop Conditions
BLOCK if: `worktree` is not genuinely part of the key (this is the one thing that must not regress), the diff touches any file outside scope, `run_log_paths` was modified, the collision path doesn't actually raise before any side effect, or the mechanical suite doesn't reproduce green in your hands.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.

**Delivery.** Write the full REVIEW_RESULT to `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g2-reviewer-result.md` before ending your turn.
