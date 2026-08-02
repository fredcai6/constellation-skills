# Launch Order: `cmdr-448 — issue #448, Phase 1 estimator competition`

Commanders start cold. Everything you need is pasted here.

## Mission

Run the **estimator competition** on the fixed Phase 0a grading harness: candidate filtering/estimation strategies on the track-manifold state space, with per-stream clock bias as estimated nuisance states, competing on identical terms. Output: a best-known-truth trajectory + covariance per lap that **passes the #446 gates on a held-out session set**, with every strategy's scores recorded. Run the `constellation-commander` skill end to end on issue #448 in your assigned worktree.

Full issue text (#448):

> Child of epic #445. **Gated on the #447 GO decision** [RATIFIED 2026-06-11 — gate is open]. Filtering/estimation strategies compete on the fixed #446 harness.
>
> **Framing changes vs the old windowed estimator** — Time-tag error is an estimated quantity: per-batch/per-stream clock bias as nuisance states (as in orbit determination), informed by the #447 measurement model. State space on the track manifold: arc-length s(t) along the known closed ribbon + bounded lateral offset, not free 3D position. Homogeneous, locally differentiable; lap closure and sector anchors become natural constraints. Track ribbon per circuit is itself an estimation product (cross-driver position consensus) — scope it here.
>
> Existing `src/preprocessing/` components reused where they fit; nothing is sacred.
>
> **Output / done-when** — A best-known-truth trajectory + covariance per lap that passes the #446 gates ((a) sector anchors within tolerance, (b) reduced chi-square ≈ 1) on a held-out session set, with the competition results recorded (every strategy's scores on the shared field).

## Prior-Wave Verdicts (pasted)

### Phase 0a (cmdr-446, merged PR #458): grading harness

`src/preprocessing/trajectory_grading/` (11 modules), 66 tests, report schema at `docs/report_schemas/trajectory_grading_report.md`. Gates: (a) sector-anchor (50 ms tolerance, anchor positions co-estimated as per-circuit calibration parameters — `s_finish` now ALSO free, see below), (b) covariance consistency (reduced chi-square band (0.5, 2.0)), (c) cross-residual DIAGNOSTIC only. Strawman (FastF1 merged product) rejected by gate (a) at 6–30× threshold on 3 sessions — the field discriminates.

### Phase 0b (cmdr-447, merged PR #467): measurement model + GO

**GO ratified by the human 2026-06-11.** Canonical reference: `docs/physics/measurement_model.md` (in your worktree — READ IT EARLY; every number traces to evidence). Headlines binding on you:

- Two separate ~4.2 Hz irregular grids (median dt 0.240 s), distinct base ticks, ~0.4% timestamp overlap. NOT one shared grid.
- Position on an exact 0.1 m grid (raw pos_data in DECIMETRES); Z genuinely usable (30/30), noise circuit-dependent (up to 8.12 m² at São Paulo).
- **Time-tag error: WHITE JITTER at ~0.13 s** (cadence-residual IQR 0.128–0.141 s). Random walk, per-batch structure, constant bias: all rejected 6/6. An apparent autocorrelation was proven a smoothing artifact.
- **Inter-stream clock offset: STABLE, ESTIMABLE bias** — |session mean| ≤ 0.081 s, per-lap std 0.084–0.129 s, low drift, 6/6 incl. wet São Paulo.
- Post-offset arc residuals: few metres (4.9–7.6 m on Belgian Q). Raw offset-inclusive chi-square 78.7–3292 — **offset-dominated, not noise-dominated**.
- Per-channel noise covariances are session-dependent (Speed 0.078–3.656 (km/h)²; X 0.033–1.190 m²; Y 0.022–0.837 m²; Z 0.018–8.121 m²) — set per session.

## Pre-Rulings

Each overridable if evidence contradicts it — say so explicitly when overriding.

1. **The harness is the fixed field.** No estimator-motivated changes to gate logic or thresholds. The single contracted configuration: band (0.5, 2.0); your trajectory product must already carry the offset so residuals are offset-removed by construction.
2. **`s_finish` is a free co-estimated anchor** (0b decision F3: `s3` pins to the track-length bound when it's fixed).
3. **Inter-stream offset is a first-class estimated state** (per-lap; collapse to per-session only if evidence shows it's tighter that way). Time-tag error enters as white jitter ~0.13 s per the measurement model.
4. **Track manifold state space**: arc-length s(t) + bounded lateral offset on a closed ribbon. The ribbon per circuit is an estimation product (cross-driver position consensus) — scope it INSIDE this issue; it does not gate separately.
5. **Held-out discipline declared before running**: split sessions into tuning vs competition sets up front, record the split in your workbench BEFORE any strategy sees the competition set. Gates must pass on held-out sessions.
6. **At least two genuinely different strategies** must compete (e.g., batch least-squares/smoother vs sequential filter family) plus the merged-product strawman as floor. A competition with one entrant is not a competition.
7. **No re-pull**: offline cache `C:/Programs/f1Brainz/outputs/cache`; raw `session.car_data`/`session.pos_data` only.
8. **Code placement**: physics region (`src/preprocessing/`), reuse existing components where they fit; nothing imports evo modules. Exploration in `scripts/`.
9. **Compute discipline**: estimator sweeps are long — checkpoint per-session/per-strategy results to disk (JSON) as you go; a continuation must be able to resume without recomputation. Commit early and often.

## Honest-Null Clause

A measured negative is a complete, successful deliverable. If NO strategy passes both gates on held-out sessions, that is the epic's done-bar answer (documented negative, bet bounded) — report it with full rigor: best scores achieved, the binding constraint, and what (if anything) would change the answer.

## Inherited Latitude

You may decide autonomously: strategy choice and count (≥2 + strawman), ribbon-estimation method, session split, numerical methods, module structure within the physics region, branch-local commits, opening the PR. You must float (`user-decision`): the phase verdict itself (you recommend, the human ratifies at the Admiral's checkpoint), cross-region boundary moves, scope changes, merging (Admiral merges), closing issues, anything fitting no listed class.

## File Ownership

Findings in `.agent-work/issue-448/` inside your worktree. Sole writer. Do not touch `.agent-work/445/`.

## Workspace

- Worktree: `C:/Programs/f1Brainz-worktrees/cmdr-448` (created)
- Branch: `issue-448-estimator-competition` (tracks origin/main, base `bd4033a` — includes harness + measurement model)
- Work ONLY here. Sibling worktrees belong to other commanders (evo epic, disjoint).
- Self-rebase if origin/main advances under you and touches your files; otherwise hold.

## Inherited Context (Active lessons + platform invariants)

- Python is `py`, never `python`. Tests: `py -m pytest tests/...`.
- cd to worktree root before git/gh calls.
- Crews via the Agent tool (run_crew.py's CLI launcher doesn't exist in this harness); record in `crew-runs.json` via run_crew's registry functions; `recover_crews` before each dispatch. Headless `claude -p` crews need piped empty stdin; crews never background long tasks.
- utf-8 in child env of captured python subprocesses.
- Untracked data is NOT in your worktree — absolute paths below.
- Engine: artifact checks `attach` then plain `advance`; `record` takes `--result`; engine from worktree root; imperatives may say `python` — use `py`. Lease lapses after 1800 s — heartbeat before long steps or re-claim `--force`.
- **Checkpoint your AGENT_FEEDBACK entry + lessons-delta early (at `review`)** — a session-limit death in `feedback` stranded them once (cmdr-447); don't let a tail-end death strand yours.
- simplification_limits on touched paths before review. Physics evidence bar: truth-anchored L1–L4, units/bounds/invariants explicit.
- TURN-ENDING RULE (hard): final turn ONLY when DONE or BLOCKED; poll long waits in foreground ≤10 min calls.

## Data Locations (absolute paths into the main checkout)

- FastF1 cache: `C:/Programs/f1Brainz/outputs/cache`
- Season DBs (sector/lap truth): `C:/Programs/f1Brainz/data/f1_data_<year>.db` (`lap_times`)
- 0a evidence: `C:/Programs/f1Brainz/.agent-work/archive/2026-06-11-issue-446/evidence/`
- 0b evidence + workbench: `C:/Programs/f1Brainz/.agent-work/archive/2026-06-11-issue-447/`

## Budget

Opus commander, Sonnet crews. This is the heaviest phase of the epic — expect long estimator runs. Foreground-poll long compute; checkpoint everything resumable; if you sense the session window closing mid-gate, prioritize committing state + pushing the branch over starting new work.

## Stop Conditions

Stop and return early when: a decision outside latitude is needed; ribbon estimation proves impossible from pooled position data (report why — it was a named epic risk); compute makes the competition infeasible in-session even with checkpointing (return with partial standings + resume plan); or scope balloons (e.g., force modeling creeping in — that is Phase 2, not yours).

## Return Shape

1. **Verdict**: gates passed on held-out sessions by ≥1 strategy / honest null / partial-with-resume-plan / blocked — recommendation clearly labeled (human ratifies at the checkpoint).
2. **Competition table**: every strategy × every session — gate (a) max/RMS residuals, gate (b) chi-square, diagnostics — tuning and held-out clearly separated.
3. **The winning product**: where the per-lap trajectory+covariance artifacts live, their schema, and how Phase 2 consumes them.
4. **PR** opened (push allowed, do NOT merge); PR number + check status; verdict posted as a comment on issue #448.
5. **Map impact**; **triage candidates**; **workflow feedback**; floated `user-decision`s with recommendations.
