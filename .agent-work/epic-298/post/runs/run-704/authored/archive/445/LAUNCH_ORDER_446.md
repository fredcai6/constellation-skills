# Launch Order: `cmdr-446 — issue #446, Phase 0a trajectory grading harness`

Commanders start cold. Everything you need is pasted here.

## Mission

Build the **permanent trajectory grading harness** (epic #445, Phase 0a) BEFORE any filtering/estimator work, so every future estimation strategy competes on identical terms. Run the `constellation-commander` skill end to end on issue #446 in your assigned worktree.

Full issue text (#446):

> Child of epic #445. Build the permanent grading field BEFORE any filtering work, so every estimation strategy competes on identical terms.
>
> **Contract** — Input: a candidate per-lap trajectory product — `s(t)` (or equivalent) with covariance — plus the session's official lap/sector times from the DB.
>
> Scores:
> - **(a) Sector-anchor gate**: predicted sector-crossing times vs official sector times; initial tolerance ~50ms (revisit after 0b). Sector-loop positions along the ribbon are NOT published — treat anchor positions as per-circuit calibration parameters (co-estimated or sourced), not as known a priori.
> - **(b) Covariance-consistency gate**: reduced chi-square ≈ 1 on residuals — the reported covariance must honestly describe the error.
> - **(c) Cross-residual DIAGNOSTIC (not a gate)**: fit a per-lap inter-stream time offset as a free parameter; compare integrated-speed arc length vs position-derived arc length with lap closure. Report the fitted offsets per lap/session — stable → calibratable bias; wandering → quantified jitter. Independence of the two streams' clock pathologies is NOT assumed.
>
> **Bounds** — Read-only over already-collected telemetry (on disk; no re-pull) + DB sector times. No estimator work in this issue — the harness must run against a trivial strawman (e.g., FastF1's own interpolated channels wrapped as a 'trajectory') to prove it discriminates.
>
> **Done-when** — Harness runs on ≥3 sessions, scores the strawman, emits a machine-readable report; unit-tested scoring primitives.

## Prior-Wave Verdicts (pasted)

No prior waves — this is wave 1 of the epic. The governing diagnosis from the approved spec (`docs/superpowers/specs/2026-06-10-physics-state-space-direction-design.md`, read it in your worktree):

> FastF1 telemetry is **two independent, unsynchronized streams**: car data (speed/RPM/throttle/brake, irregular ~240ms) and position data (X/Y/Z, irregular ~220ms, ~0.1m quantization, unreliable Z). **Time tags are reconstructed, not measured** — the live-timing transport batches with jitter; the two streams have *different* unknown clock errors. Our collector ingests `lap.get_telemetry()` — FastF1's **merged, linearly interpolated** product. Differentiating interpolated, jitter-timestamped ~4-5Hz position twice yields sawtooth acceleration and correlated (non-white) errors. The old estimator assumed known sample times + white noise — the dominant error term (time-tag error) was not in the model. It was never a "simple filtering problem": a filter was asked to explain time-base error as physical acceleration.

The user thinks in astrodynamics/orbit-determination terms: sector times are range gates, clock biases are nuisance states, covariance honesty matters more than point accuracy.

## Pre-Rulings

Each overridable if evidence contradicts it — say so explicitly when overriding.

1. **Never re-pull telemetry.** Everything is on disk in the FastF1 cache. Load offline: `fastf1.Cache.enable_cache('outputs/cache')` — absolute path `C:/Programs/f1Brainz/outputs/cache` (untracked; NOT in your worktree).
2. **Raw streams only**: `session.car_data[driver]` / `session.pos_data[driver]`. NEVER `get_telemetry()` / `lap.get_telemetry()` — the merged product is the artifact under study. (Exception: the strawman candidate may deliberately wrap the merged product as its trajectory — that's the point of the strawman.)
3. **Code placement**: harness lives in the physics region — `src/preprocessing/` for shipping code (or a new submodule there), exploration in `scripts/`. NOT in `src/evo_predictor/`, `src/latent_power/`, `src/compound_prior/`. No imports from evo modules.
4. **DB-only rule scope**: reading the FastF1 cache offline is in-bounds for Phase 0 ONLY (instrument characterization, collection-side). Sector/lap truth comes from the season DBs via `src/data/database` DatabaseManager.
5. **Anchor positions are calibration parameters**, not known constants — design the scoring API so sector-loop positions along the track are estimated/supplied inputs with uncertainty, never hard-coded.
6. **Cross-residual is a diagnostic, not a gate** — report it, never pass/fail on it; the two streams' clock pathologies are not assumed independent.
7. **Machine-readable report**: pick a stable schema (JSON) and document it; future phases consume it. Per repo policy, a committed report schema needs producer + schema doc together.
8. **Session choice for the ≥3-session run**: prefer 2022-2025 sessions (deep cache coverage); pick at least one race and one quali; document which and why.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. If the harness reveals (for example) that sector-anchor scoring cannot discriminate at ~50ms with unpublished loop positions, report that with the same rigor as a win — it feeds 0b's gate directly.

## Inherited Latitude

You may decide autonomously: implementation structure within the physics region, test design, report schema details, session selection, branch-local commits. You must float to the Admiral (return a `user-decision`): anything crossing data/physics/evo region boundaries, scope changes (adding/dropping deliverables), pushing/opening the PR is allowed but merging is NOT (Admiral merges), closing issues, anything user-visible outside the physics region, and anything that fits no listed class.

## File Ownership

Your findings file: `.agent-work/issue-446/` inside your worktree (commander workbench convention). You are sole writer there. Do not touch `.agent-work/445/` (Admiral's area, main checkout) or other commanders' areas.

## Workspace

- Worktree: `C:/Programs/f1Brainz-worktrees/cmdr-446` (already created)
- Branch: `issue-446-grading-harness` (tracks origin/main, base `62ab7fa`)
- Work ONLY in this worktree. Other commanders are active in sibling worktrees (cmdr-410/413/451, evo epic — disjoint from you).
- Self-rebase if origin/main advances under you and it touches your files; otherwise hold rebases until done.

## Inherited Context (Active lessons + platform invariants)

- Python is `py`, never `python`. Tests: `py -m pytest tests/...`.
- Set-Location/cd to the worktree root before git/gh calls (subagent shells leak cwd).
- Headless `claude -p` crews from PowerShell need empty stdin piped (`$null | claude -p ...`) or they stall; crews must never background long tasks — long compute runs foreground in you, the commander.
- Set utf-8 in the child env of any python subprocess whose output you capture (cp1252 pipes silently corrupt output). The constellation engine itself owns utf-8 stdio now.
- Untracked files (DBs, caches, model artifacts) do NOT appear in your worktree — use the absolute paths in Data Locations.
- Engine quirks: artifact-check postconditions need `attach` then plain `advance` (attest is refused); `record` takes `--result pass|fail`; run the engine from your worktree root.
- New-module limits: run `py -m src.utils.simplification_limits` on touched paths (strict) before review; plan file splits when approaching limits.
- Physics-region evidence bar: truth-anchored tests at the highest applicable L1-L4 tier; units, bounds, invariants explicit.
- TURN-ENDING RULE (hard): end your final turn ONLY when DONE or BLOCKED. Never end a turn "waiting" on a background shell — poll long waits in foreground calls ≤10 min each. If you background a long compute step, keep polling it in the same turn until it finishes.

## Data Locations (absolute paths into the main checkout)

- FastF1 cache (telemetry source): `C:/Programs/f1Brainz/outputs/cache` (~36GB, 2018-2025, deep 2022-2025)
- Season DBs (sector/lap truth): `C:/Programs/f1Brainz/data/f1_data_<year>.db`, `lap_times` table (`sector1_time/sector2_time/sector3_time`, ms-precision floats)
- The season DBs' `telemetry` tables are EMPTY — do not look for telemetry there.

## Budget

Opus commander, Sonnet crews. No hard ceiling, but if a single compute step looks like >30 min, checkpoint progress to disk so a continuation can resume. Commit early and often on your branch.

## Stop Conditions

Stop and return early when: a decision outside your inherited latitude is needed; the cache turns out not to contain usable raw per-stream data for ≥3 suitable sessions (report what IS there); scope balloons beyond the issue's bounds (e.g., the harness seems to need real estimator work — it must not); or evidence for a gate primitive is impossible to produce.

## Return Shape

Final report (this is what the Admiral acts on — your last message is the only thing returned):

1. **Verdict**: harness built and discriminating / honest null / blocked — one paragraph.
2. **Evidence**: test results, the ≥3-session strawman run output (paths to the machine-readable reports), key numbers (strawman's sector-anchor residuals, chi-square, fitted inter-stream offsets per session).
3. **PR**: open a PR to main (push allowed) with the issue linked; report PR number and check status. Do NOT merge.
4. **Map impact**: what changed structurally (new modules, new report schema).
5. **Triage candidates**: follow-up work discovered, as a list.
6. **Workflow feedback**: what in this launch order / process helped or hurt — feeds the lessons audit.
7. Anything floated as `user-decision` with your recommendation.

Post the verdict as a comment on issue #446 as well.
