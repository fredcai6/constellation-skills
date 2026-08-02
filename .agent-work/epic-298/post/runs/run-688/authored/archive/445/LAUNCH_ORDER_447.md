# Launch Order: `cmdr-447 — issue #447, Phase 0b instrument characterization + GO/NO-GO`

Commanders start cold. Everything you need is pasted here.

## Mission

Answer the epic's bounded question — **is the FastF1 telemetry correlatable enough to support trajectory estimation?** — by characterizing the raw instruments empirically, producing `docs/physics/measurement_model.md` (numbers, covariances, an explicit time-tag error model), and assembling the **GO/NO-GO evidence** for the epic's decision point. Run the `constellation-commander` skill end to end on issue #447 in your assigned worktree.

You do NOT decide GO/NO-GO. You produce the measured evidence and a recommendation; the Admiral presents it to the human, who ratifies the fork. Structure your verdict accordingly.

Full issue text (#447):

> Child of epic #445; runs alongside/after #446 (0a). The bounded question: **is the data correlatable enough to support trajectory estimation?**
>
> **Work** — Over the already-collected telemetry — the FastF1 cache at `outputs/cache/` (~36GB, 2018-2025; NOT the season DBs, whose `telemetry` tables are empty; no re-pull, load offline via `fastf1.Cache.enable_cache('outputs/cache')`) — pull the per-stream raw samples with native time bases (`session.car_data[driver]` / `session.pos_data[driver]`; never the merged/interpolated `get_telemetry()`) and characterize per stream:
> - sampling-interval distributions; position quantization; Z-channel quality
> - time-tag jitter magnitude (residuals against smooth fits and against sector-crossing constraints)
> - inter-stream clock-offset stability per lap / per session
> - noise covariances per channel
>
> **Deliverable** — `docs/physics/measurement_model.md` — numbers, covariances, and an explicit time-tag error model (the thing the old estimator had to assume).
>
> **GO/NO-GO gate (epic decision point)** — GO: offsets estimable, cross-residuals bounded → Phase 1 estimator competition opens. NO-GO: measurements not mutually constrainable → document why, close the epic's estimation phases, redirect to the model-side quali gap. A designed outcome, not a failure.

## Prior-Wave Verdicts (pasted)

### cmdr-446 (Phase 0a, merged as PR #458 → main 0e05aa8) — verdict in full:

> **Harness built and DISCRIMINATING.** The permanent, read-only trajectory grading harness exists in `src/preprocessing/trajectory_grading/` (11 modules: contract, sector_anchor, covariance_gate, cross_residual, db_truth_loader, offline_loader, report_schema, runner, strawman_candidate, …), 47 unit + 19 integration tests passing, report schema documented at `docs/report_schemas/trajectory_grading_report.md`.
>
> **Strawman results (FastF1's merged/interpolated product wrapped as a trajectory, 50 ms tolerance):**
>
> | Session | anchor gate (a) | max resid | RMS | reduced chi-sq (b) | cov gate (b) | offset range (c) |
> |---|---|---|---|---|---|---|
> | 2023 Belgium Q | FAIL | 1.505 s | 0.300 s | 11.14 | PASS | [-0.20,+0.41] s |
> | 2023 Belgium R | FAIL | 1.067 s | 0.158 s | 3.07 | PASS | [-0.23,+0.03] s |
> | 2022 Spain R | FAIL | 0.296 s | 0.070 s | 0.60 | PASS | [-0.08,+0.36] s |
>
> Gate (a) rejects the strawman by 6–30× threshold — free-anchor co-estimation absorbs mean bias but not per-lap sector-time variance. Reviewer independently confirmed all numbers and the decimetre arc-length scaling (6941.6 m vs FastF1's published 6949.5 m on Spa — pos_data is in DECIMETRES).
>
> **Findings feeding YOU directly:**
> 1. **Gate (b)'s acceptance band [0.01, 100] is too loose to discriminate** (chi-squares 0.60–11.14 all pass). Tightening toward ~[0.5, 2.0] is the headline 0b calibration task — your measured noise model is what justifies the band.
> 2. **Cross-residual (c) fitted inter-stream offsets wander per lap** (ranges above) → points at quantified jitter, not a stable calibratable bias. Your characterization must say which, with distributions.
> 3. Open design question assigned to you: **should `s_finish` be a free anchor** for circuits with ambiguous start/finish-line positions? Decide from evidence and document.
> 4. Practical: DB GP naming is "Belgium" while FastF1 events say "Belgian Grand Prix" — harness's db_truth_loader handles the mapping for its sessions; check before assuming new sessions resolve.

## Pre-Rulings

Each overridable if evidence contradicts it — say so explicitly when overriding.

1. **Never re-pull telemetry**: offline cache only, `fastf1.Cache.enable_cache('C:/Programs/f1Brainz/outputs/cache')` (untracked; NOT in your worktree).
2. **Raw streams only**: `session.car_data[driver]` / `session.pos_data[driver]`. The merged `get_telemetry()` is the artifact under study, never an input.
3. **pos_data is in decimetres** — confirmed by cmdr-446 against Spa's published track length. Account for it everywhere.
4. **Reuse the 0a harness** (`src/preprocessing/trajectory_grading/`): its offline_loader, db_truth_loader, and cross_residual primitives are your starting point. Extend in place or alongside in the physics region; do not fork private copies.
5. **Code placement**: characterization analysis in `scripts/`; anything shipping (noise-model loaders, the measurement-model artifact reader) in `src/preprocessing/`. Never in evo modules.
6. **Session coverage**: characterize across ≥6 sessions spanning ≥2 seasons (2022-2025 preferred, deep cache), mixing race + quali + at least one wet or red-flagged session if available — instrument pathologies hide in messy sessions. Document selection.
7. **The measurement model document is the deliverable**, not code: `docs/physics/measurement_model.md` with explicit numbers — per-stream sampling-interval distributions, quantization steps, Z-channel verdict, time-tag jitter magnitude + model (bias vs random walk vs per-batch), per-channel noise covariances, inter-stream offset stability. Every number traceable to a script + session.
8. **Gate framing**: GO = offsets estimable AND cross-residuals bounded (the spec's words). Operationalize both halves with measured thresholds and show your operationalization before applying it.
9. **Honest NO-GO is a designed outcome** — it bounds the bet at characterization cost and redirects effort. Do not rescue a marginal result; present marginal as marginal.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. NO-GO evidence presented with rigor is exactly as valuable as GO evidence.

## Inherited Latitude

You may decide autonomously: analysis structure, session selection (within pre-ruling 6), statistical methods, measurement-model document structure, the covariance-band recommendation, the `s_finish` design call, branch-local commits, opening the PR. You must float (return `user-decision`): the GO/NO-GO itself (recommendation only — the human ratifies), anything crossing data/physics/evo boundaries, scope changes, merging (Admiral merges), closing issues, anything fitting no listed class.

## File Ownership

Your findings live in `.agent-work/issue-447/` inside your worktree (commander workbench convention). Sole writer. Do not touch `.agent-work/445/` (Admiral's, main checkout).

## Workspace

- Worktree: `C:/Programs/f1Brainz-worktrees/cmdr-447` (already created)
- Branch: `issue-447-instrument-characterization` (tracks origin/main, base `0e05aa8` — includes the merged 0a harness)
- Work ONLY here. Sibling worktrees belong to other commanders (evo epic, disjoint).
- Self-rebase if origin/main advances under you and touches your files; otherwise hold.

## Inherited Context (Active lessons + platform invariants)

- Python is `py`, never `python`. Tests: `py -m pytest tests/...`.
- cd to the worktree root before git/gh calls (subagent shells leak cwd).
- Headless `claude -p` crews need empty stdin piped (`$null | claude -p ...`); crews never background long tasks — long compute runs foreground in you.
- utf-8 in the child env of any python subprocess whose output you capture.
- Untracked data does NOT appear in your worktree — absolute paths below.
- Engine quirks: artifact checks `attach` then plain `advance`; `record` takes `--result`; run engine from worktree root. Engine imperatives may say `python` — use `py`.
- Lease note from cmdr-446: a >30 min crew step lapses the 1800 s spine lease — re-claim with `--force` if `advance` is refused, or heartbeat before long steps.
- run_crew.py assumes a CLI launcher that doesn't exist in this harness — cmdr-446's working pattern: dispatch crews via the Agent tool, record each in `crew-runs.json` via run_crew's registry functions, `recover_crews` before each dispatch.
- New-module limits: `py -m src.utils.simplification_limits` on touched paths before review.
- Physics-region evidence bar: truth-anchored, units/bounds/invariants explicit; docs need valid commands and current references.
- TURN-ENDING RULE (hard): end your final turn ONLY when DONE or BLOCKED; poll long waits in foreground calls ≤10 min each.

## Data Locations (absolute paths into the main checkout)

- FastF1 cache: `C:/Programs/f1Brainz/outputs/cache` (~36GB, 2018-2025, deep 2022-2025)
- Season DBs (sector/lap truth): `C:/Programs/f1Brainz/data/f1_data_<year>.db`, `lap_times` table (ms-precision floats)
- Season DBs' `telemetry` tables are EMPTY.
- Merged 0a evidence reports (for cross-reference): `C:/Programs/f1Brainz/.agent-work/archive/2026-06-11-issue-446/evidence/`

## Budget

Opus commander, Sonnet crews. Characterization sweeps over many sessions can be long — checkpoint intermediate per-session results to disk (JSON) so a continuation can resume; commit early and often.

## Stop Conditions

Stop and return early when: a decision outside inherited latitude is needed; the cache lacks usable raw per-stream data for the required session spread (report what IS there); the question turns out to need estimator work (it must not — characterization only); or evidence for a required quantity is impossible to produce.

## Return Shape

Final report (your last message is the only thing the Admiral receives):

1. **Verdict**: characterization complete + GO recommendation / NO-GO recommendation / marginal-with-analysis / blocked — one paragraph, recommendation clearly labeled as a recommendation.
2. **GO/NO-GO evidence pack**: the operationalized gate criteria, the measured values against them, and the headline numbers (jitter magnitude + model class, offset stability, recommended chi-square band, per-channel covariances). This becomes the human's decision brief — write it so a careful non-specialist can follow it.
3. **Deliverable**: `docs/physics/measurement_model.md` committed; PR opened (push allowed, do NOT merge); PR number + check status. Verdict posted as a comment on issue #447.
4. **Map impact**: structural changes (new modules, schema changes, doc additions).
5. **Triage candidates**: follow-ups discovered, as a list.
6. **Workflow feedback**: what helped/hurt — feeds the lessons audit.
7. Anything floated as `user-decision` with your recommendation.
