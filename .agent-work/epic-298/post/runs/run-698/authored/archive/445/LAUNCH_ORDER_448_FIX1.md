# Launch Order: `cmdr-448-fix1 — issue #448 fix-and-rerun wave (Phase 1 retry)`

Commanders start cold. Everything you need is pasted here.

## Mission

The Phase 1 estimator competition returned an honest null — but the null is **contaminated by two named implementation bugs and one open calibration question**. Your mission: fix exactly those defects, re-run the *identical frozen competition*, and report whether the null stands on clean evidence. The human has ruled the epic does not close on a persistent null (it would go to a strategy-brainstorm instead), so your job is purely to decontaminate the measurement — NOT to make it pass. Honest measurement is the bar; gate-softening to manufacture a pass is the cardinal failure mode of this wave.

Run the `constellation-commander` skill end to end on this bounded scope, in the existing cmdr-448 worktree, continuing branch `issue-448-estimator-competition` (PR #468 is OPEN and UNMERGED by the human's ruling — your commits will flow into it).

## Prior-Wave Verdict (pasted — the contaminated null)

Competition on held-out {2023 Belgian R, 2024 British Q, 2023 São Paulo R}, tuning {Belgian Q, Spanish R, British R}, knobs frozen pre-held-out (reviewer re-derived all 18, zero leakage):

| Strategy | gate (a) best max | gate (b) chi² | both pass |
|---|---|---|---|
| A — batch LS/RTS, per-session τ | 0.96 s | 18k–42k | no |
| B — sequential EKF + FB-RTS, per-lap τ | **0.55 s** (Silverstone Q) | 705–1370 | no |
| strawman (`get_telemetry` floor) | 0.57 s | 1.4 (passes b on 2/3) | no |

Full table + resumable per-cell checkpoints: `.agent-work/archive/2026-06-12-issue-448/competition/` (in the worktree/branch). Named contaminants from that run's own triage:

1. **[HIGH] Strategy A gate-(b) chi² inflation is OUR arithmetic**: documented `arc_speed_variance_m2` per-step understatement; named fix: propagate accumulated `k·(σ_v·dt)²`.
2. **[HIGH] Strategy B non-monotone `session_time_s` bug on >50-lap races** — it errored on Interlagos; never got a fair run there.
3. **[HIGH, open question] Gate-(a) sector-crossing calibration** — how much of the residual is anchor-position calibration error vs genuine trajectory error? Unanswered.
4. [LOW] 28 pyright `reportArgumentType` errors across the new estimator region (the `raw: object` boundary idiom) — the human declined to merge with these red.

## Scope (exhaustive — nothing else)

- **F1**: Fix Strategy A's variance accumulation (`arc_speed_variance_m2`). Truth-anchored test demonstrating honest covariance on a synthetic known-answer case.
- **F2**: Fix Strategy B's session-time monotonicity on long races. Regression test on a >50-lap synthetic or Interlagos itself.
- **F3**: Gate-(a) residual decomposition diagnostic: quantify anchor-calibration error vs trajectory error (e.g., residual structure across laps/drivers — anchor error is common-mode per circuit sector, trajectory error is not). If evidence shows a calibration term, document it; any resulting gate change must be justified from sector-time truth alone, NEVER from "it lets a strategy pass," and floats to the Admiral as a `user-decision` before being applied.
- **F4**: Clear the 28 pyright errors in the estimator region (annotation-level; behavior unchanged; tests stay green).
- **F5**: Re-run the IDENTICAL frozen competition — same split, same frozen knobs (re-freeze nothing), reusing the archived per-cell checkpoints where valid (cells whose inputs are untouched by F1–F3 may be reused; recompute touched cells). Updated standings table, tuning/held-out separated.

Explicitly OUT of scope: new strategies, new sessions, gate-threshold changes (except a floated F3 calibration correction), strawman changes, any evo coupling.

## Pre-Rulings

1. The frozen split and frozen knobs are immutable. Re-freezing or re-tuning ANY knob invalidates the wave.
2. F3 gate changes: float before applying (see above). Everything else in scope is yours to execute.
3. If F1+F2 fixes change a strategy's *tuning-set* behavior so radically that the frozen knobs are arguably stale — STOP and report; do not silently re-tune.
4. No re-pull; raw streams; decimetres; offline cache. (Same data rules as all prior waves.)
5. Report the outcome even-handed: "null stands clean" and "a strategy now passes" are equally successful deliverables of THIS wave.

## Inherited Latitude

Yours: implementation of F1/F2/F4, diagnostic design for F3, checkpoint reuse judgment in F5, branch commits/pushes. Float to Admiral: applying any F3-derived gate change; anything outside the F1–F5 list; merging (held by the human); issue filing/closing.

## File Ownership / Workspace

- Worktree: `C:/Programs/f1Brainz-worktrees/cmdr-448` (EXISTS — inherited from the cmdr-448 lineage; prior spine is archived, branch is clean and synced with origin at the archived state). Work ONLY there, on branch `issue-448-estimator-competition`.
- Findings: `.agent-work/issue-448-fix1/` inside the worktree (new work area — the prior `issue-448` package is archived; leave it).
- Prior archived run: `.agent-work/archive/2026-06-12-issue-448/` (read-only reference).

## Inherited Context (platform invariants — unchanged from prior waves)

- Python `py` never `python`; tests `py -m pytest tests/...`; cd worktree root before git/gh; crews via Agent tool + registry shim (`register_crew.py` pattern from the prior run); piped empty stdin for headless crews; utf-8 child env; engine artifact-checks attach-then-advance; lease re-claim `--force` if stale; simplification_limits before review.
- SURVIVAL DISCIPLINE (three session-limit deaths in this lineage): commit and PUSH after every gate; checkpoint long computations per-cell; AGENT_FEEDBACK entry + lessons-delta at `review` not `feedback`.
- TURN-ENDING RULE: final turn only when DONE or BLOCKED; poll long compute foreground ≤10 min calls; never end a turn to float something inside your latitude.

## Data Locations

- FastF1 cache: `C:/Programs/f1Brainz/outputs/cache`; season DBs: `C:/Programs/f1Brainz/data/f1_data_<year>.db`; archived competition checkpoints: in-worktree `.agent-work/archive/2026-06-12-issue-448/competition/`.

## Budget

Opus commander, Sonnet crews. F5 reuses checkpoints — should be much cheaper than the original competition. If the window closes, push and let a continuation finish.

## Return Shape

1. **Verdict**: null stands clean / one-or-both strategies now pass / partial — recommendation labeled (human ratifies at the boundary).
2. **Updated competition table** (tuning/held-out separated) + what each fix changed, cell by cell.
3. **F3 decomposition result**: anchor-calibration share vs trajectory share of the gate-(a) residual, with the evidence; any proposed calibration change floated, not applied.
4. PR #468 updated (push; do NOT merge); check status (pyright should now be green per F4); verdict comment on issue #448.
5. Map impact; triage candidates; workflow feedback; floated `user-decision`s.
