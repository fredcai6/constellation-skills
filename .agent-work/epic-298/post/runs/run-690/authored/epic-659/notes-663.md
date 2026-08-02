# Notes — #663 Grip baseline module G (cmdr-663)

Worktree: `C:/Programs/f1brainz-wt/epic659-663`, branch `epic659/663-grip-g`. Work area: `.agent-work/663-grip-g/` (worktree-local).

## Verdict: **built + measured-null**

Module G is built (grip_store.py, grip_baseline.py, grip_batch.py — 6 gates, all reviewed and APPROVED), and its two GATING acceptance criteria were run with full rigor against real 2023 data and a real synthetic-recovery experiment. Both point at the same real, diagnosed defect: **G's saturating-curve+free-offset parameterization is structurally non-identifiable on realistic F1 session shapes** — offset and asymptote alias (correlation pinned toward ±1 even in the estimator's cleanest tested regime). Per the launch order's Honest-Null Clause, this is a complete, successful deliverable: a measured negative, not a build failure.

## Build summary (g1-g3)

- **g1** `src/physics/layer2/grip_store.py` — `GripEstimateRecord` (PK session-level `(year, gp_name, session_type)`, field-pooled — NOT per-constructor like `EstimateRecord`) + `GripStore` (standalone SQLite, additive-only migration mirroring `estimate_store.py:400-412`). One rework cycle (reviewer BLOCKed on 2 over-complex test functions, CC=20/22; fixed, re-approved).
- **g2** `src/physics/layer2/grip_baseline.py` — the fit logic. Reuses `session_race.compute_cumulative_track_laps`'s exact counting convention (vectorized), reuses `tyre_supplant.race_degradation_slopes` UNCHANGED via a local session-type-generalized reader (`tyre_supplant.py` never touched), Student-t residuals via `predictive_t`. Implements both frozen fallback rules with real, tested effects: thin-session wide-sigma (3.0x, floor = 2 stints of 4 laps) and rain-flag wide-sigma (4.0x, distinct constant, verified exactly 4.000x).
- **g3** `src/physics/layer2/grip_batch.py` (`run_grip_batch`, injectable-fn, per-unit failure isolation) + `get_grip_at` on `grip_store.py` (delta-method sigma propagation, `GripRecordNotFoundError`). Reviewer scrutiny confirmed a self-flagged gap (batch driver doesn't wire weekend-sibling sessions for the thin-fallback lookup) is real but does NOT bite g4/g5 (neither routes through `run_grip_batch`) — filed as triage tc1.

## GATING gate 1 — g4 held-out reconciliation: **MEASURED NEGATIVE**

4 contrasting 2023 circuits (Monaco, Spain, Netherlands, Saudi Arabia; FP-vs-FP pairs), team-stratified 50/50 driver split (genuinely disjoint, asserted), G fit on fit-set drivers only, scored on held-out drivers only. Truth side is regression-free (raw fastest-3-lap median) — leakage-avoided by design, verified by grep (zero executable regression calls on the truth-side path).

**Subtracting G worsens reconciliation RMS by +155.5%** (aggregate before 3.02s -> after 7.72s, 0/4 circuits improved, 37 held-out cells). Negative-control swap test confirms the signal is directional/real (swap RMS 8.62s, worse than both before and after — not a subtraction-machinery tautology). Diagnosed to structurally unidentified per-session fits: e.g. Monaco FP2 offset=93.2s, asymptote=-107640s, offset<->asymptote correlation=-0.99999999996 (independently re-derived by the reviewer to full precision).

Reviewer independently verified all 8 close criteria (split integrity, fit-set-only fit, held-out-only scoring, leakage-avoidance claim, negative-control wiring, diagnosis reproduction, honest-null operationalization, scope honesty) — APPROVE, "REAL, not artifact."

## GATING gate 2 — g5 synthetic-recovery: **MEASURED SPLIT, confirms g4**

72 replicates, 6-cell SNR x curve-bend factorial, calling G's REAL fit function directly (`fit_grip_baseline_from_laps`, imported not reimplemented) on synthetic data with KNOWN injected curve+offsets.

- **Parameter recovery: 94.4% (>=90% threshold) -> PASSES**, but only HOLLOWLY — driven by honest sigma-widening at low SNR (trivial coverage from wide intervals); the one high-confidence regime (high SNR, full curve bend) drops to 66.7% because aliasing bias then escapes the narrow interval.
- **Separability: 31.9% (>=90% threshold) -> FAILS decisively.** Median |offset<->asymptote correlation| = 0.835 across all replicates, and even the estimator's CLEANEST regime (SNR=5, full bend) only reaches median |corr|=0.939 — the aliasing is intrinsic to the functional form, not a data-quality artifact.

Reviewer independently fitted 5 REAL 2023 sessions to spot-check the synthetic SNR calibration: real field-pooled residual RMS = 12.2-14.5s, confirming the harness's low-SNR tier (~11s) is honest (if anything easier than reality) — and reproduced g4's degenerate real-fit asymptotes independently (Netherlands 8040s, Vegas -7870s) as a bonus corroboration. APPROVE.

## Why this is the deliverable, not a blocker

Per `decision:held-out-not-in-sample` and `decision:synthetic-identifiability` (both `settled/human`, both GATING per the issue), and the Honest-Null Clause ("a measured negative is a complete, successful deliverable... report it with full rigor and its scope"): the module is BUILT (all 3 core gates reviewed+APPROVED), its acceptance evidence is REAL (run against actual 2023 data + a controlled synthetic experiment, not self-scored), and the result — G's current curve parameterization cannot be trusted as a cross-session subtractable baseline — is itself the falsifiable, honest answer the two GATING gates exist to produce. Two independent implementer/reviewer pairs, working from different data sources (real DB vs. synthetic with known truth), converged on the identical diagnosis. This is strong evidence the defect is real and structural, not a fluke of one harness.

## What was tested / what was NOT tested (scoped-null discipline)

- Tested: G's SPECIFIC parameterization (`session_offset + curve_asymptote*(1-exp(-curve_rate*x))`, fit via least-squares on tyre_supplant-corrected residual pace) on FP-session 2023 data (4 circuits) and matched synthetic data (72 replicates, SNR range covering the measured real regime).
- NOT tested: whether a DIFFERENT curve parameterization (bounded/anchored asymptote, fixed rate, or a simpler flat-offset-only model) would be identifiable — that is the natural next experiment, not something this build's evidence rules out. NOT tested: race-session (`R`) identifiability specifically (g4's slice was FP-only; g2's fit logic itself is session-type-uniform and untested per-type here). NOT tested at full-season scale (4/22 circuits — Budget latitude).

## Triage candidates (for g6 / Admiral)

1. **G's curve parameterization needs reworking for identifiability** (the substantive finding) — candidates: reparameterize to an identifiable basis (anchor the curve's initial value, bound the total gain instead of a free asymptote), fix or tightly prior the rate, or fall back to a flat-offset-only model (drop the intra-session curve term entirely) when `|curve_offset_correlation|` crosses a threshold. This is the natural next issue, not fixed in this build (issue #663 built + gated the module as specified; reworking the functional form is a new, informed design decision).
2. **tyre_separation.py reconciliation** (interrogation q7) — a second within-session-covariate implementation (G) now exists alongside `tyre_separation.py`'s `g_track`, per that ADR's own Review Trigger ("if pooling.py is extended to support within-session covariate axes, evaluate whether the two implementations should be unified"). Confirmed structurally distinct (per-circuit linear vs per-session saturating curve; cross-season pooled vs single-weekend) — not urgent, but worth a future look now that both exist.
3. **#511 grip_decay_prior_k unification** — `physics_config.py`'s `grip_decay_prior_k` and `session_fit.py`'s hardcoded `k_tire=0.01` are two independent literals for the same concept, explicitly flagged unreconciled in the existing code. Untouched by this build; still open.
4. **layer2_evolution.py wiring to consume G** — `src/physics/weekend_state/layer2_evolution.py`'s own floated "no bridge" Known Limit is now structurally closable (G's `cumulative_track_laps` convention IS the bridge it needed), but actually wiring it up is out of this issue's scope and should wait until G's identifiability is fixed (wiring a known-non-identifiable G into another module would just propagate the defect).
5. **GripEstimateRecord's session-level PK vs EstimateRecord's per-constructor PK** — a durable structural divergence (deliberate, field-pooled-vs-per-car distinction) worth a Cartographer decision anchor at reconcile so a future reader doesn't mistake it for an inconsistency.
6. **tc1 (from g3-review): weekend-neighbor batch wiring** — `run_grip_batch` doesn't pass sibling-session fits across sessions within a weekend for the thin-session fallback (the fallback mechanism exists and is tested in `grip_baseline.py` directly, just not wired end-to-end in the batch orchestrator). Confirmed non-blocking for g4/g5 (neither routes through the batch driver). Real gap for a future full-season production batch run.
7. **sessions.rainfall schema/storage mismatch** (from g2) — declared `REAL` in `schema.sql`, actually stored as an int64 blob (wet-sample count). `session_surface_features.session_rain_flag` is a cleaner canonical rain source repo-wide; worth a schema-doc fix or a migration to the cleaner column.
8. **Fuel not fully removed from G's residual** (from g2) — `race_degradation_slopes` doesn't expose its internal fuel coefficient, so G's residual still carries fuel burn-off, absorbed into curve+offset. Full de-fuel would require exposing that term from `tyre_supplant.py` (additive change) — deferred, and likely secondary to the identifiability fix (candidate 1) which is the dominant defect.
9. **Sigma-gating downstream** (from g4/g5 reviewers) — `get_grip_at` already returns an honest (often large) sigma for a degenerate fit, but nothing currently gates "should this G value even be subtracted" on that sigma. A future consumer-side convention (e.g. skip subtraction when sigma exceeds some multiple of the raw signal) is worth naming once a consumer actually exists.

## Map impact

**NOT YET APPLIED to docs/architecture/** — a Cartographer subagent drafted these updates at this run's own reconcile step, but per the Admiral's Wave-0 map fence (multiple parallel commanders editing `docs/architecture/packets/physics.md` in the same window would collide on merge), those edits were reverted from the PR branch (commit `0ad736c6`) and are recorded here as prose only, for the epic's single consolidated Cartographer reconcile at closeout to fold in.

- New capability: grip-baseline artifact storage + fit + query surface, all within `struct:physics.layer2` (no boundary crossing — physics-region only, no evo/data coupling).
- Closes (partially) the `#626 layer2_evolution.py` Known Limit's stated blocker (no per-car `cumulative_track_laps` bridge) — G reuses the SAME bridge convention, though wiring is candidate 4 above, not done here.
- `tyre_separation.py`/`g_track` confirmed an untouched peer (candidate 2).
- Decision pressure recorded: GripEstimateRecord's session-level PK (candidate 5) — for Cartographer at reconcile.
- The reverted draft content (module docs, the decision-anchor file, index/overlay entries) is preserved in this PR's git history at commit `86e2a206` (`docs/architecture/...` paths) if the consolidated reconcile wants a starting draft rather than writing from scratch.

## Fit/test decisions made (all in-latitude, none floated)

Full detail in `.agent-work/663-grip-g/INTERROGATION_RECORD.json` (7 questions, 2 fact/5 decision, all resolved). Summary:
- "Cumulative car-laps" = field-wide `cumulative_track_laps` (reuses `compute_cumulative_track_laps` exactly), not per-car.
- G's fit scope = ALL session types uniformly (generalizes `tyre_supplant`'s hardcoded `session_type='R'`); no blanket per-type exclusion.
- #560 thin-session rule = wide-sigma fallback (never silent skip), floor = 2 stints of >=4 laps (reusing `MIN_STINT_LAPS`).
- Held-out split = driver-based ~50/50, team-stratified.
- Synthetic-recovery criterion = 90%-of-replicates 2-sigma parameter recovery AND <0.8 offset/curve correlation.

## Simplification limits

`py -m src.utils.simplification_limits --strict src/physics/layer2/grip_baseline.py src/physics/layer2/grip_store.py src/physics/layer2/grip_batch.py` — run at g6 close, see PR description / return for result.

## Workflow feedback highlights (full detail in AGENT_FEEDBACK.md staging)

- **New, real environment gotcha:** plain `py` on this Bash-tool sandbox's PATH resolves to a codex-runtime shim missing scipy/fastf1 (confirmed pre-existing, repo-wide — even the unmodified `estimate_store.py` fails to import under it). The real launcher is `/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe`. Discovered at g1, fixed across all 6 gates' postcondition commands via engine `amend` (retext-check), and carried into every subsequent crew handoff. Worth banking as a lesson.
- `lesson:engine-artifact-attest` (attach not attest for artifact-checked postconditions) confirmed again this run.
- `lesson:run-crew-cli-launcher-misfit` (Agent-tool dispatch + run_crew.py --backend external) confirmed again this run.
- Two crew gates (g4, g5) each surfaced a load-bearing negative scientific result; both reviewers independently re-derived key diagnostic numbers to full precision (not just re-running the harness) before approving — this rigor is what makes the honest-null verdict trustworthy, and is worth banking as a pattern for future GATING-gate reviews on scientific/statistical modules.
