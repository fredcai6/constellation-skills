# Wave 1b verdict — issue #624 (Stage-1 Phase 0 probes)

Commander: ShipB-624 (delegated, `constellation-commander-delegated`). Worktree: `C:/Programs/f1-624`, branch `feat/624-phase0-probes`, base `main` @ `16c314b9`. Spine driven to terminal `archive` through the checklist engine (`checklist_engine.py`); full journal at `.agent-work/archive/2026-07-18-624-phase0/spine.json` and `execute.json` in the worktree (not the main checkout — untracked work area, per `lesson:shared-files-not-on-mission-branch`).

## Per-probe verdicts

### 1. Correlation screen — **SIGNAL (small, honest)**

Pre-registered **before** any correlation code existed (`PRE_REGISTRATION.md`, timestamped 2026-07-18T01:39:24Z — verified by the reviewer via file-mtime ordering): primary axis `lateral_total_grip_g` (= `lateral_mech_grip_g + lateral_aero_grip_g`, chosen for physical coherence — the `session_estimates`-table analog of the previously-validated #445 apex-pace/cornering-capability finding, NOT the same computation, cited but not reused).

**Method**: semi-partial correlation by construction. `quali_error` = actual Q pace-gap-to-median minus the driver's own trailing-mean recent-history baseline (no look-ahead, per-season reset) — this residualizes against evo's existing recent-history feature by definition, computed pure DB/pandas (no sampler, no NN inference), matching the pre-ruling's "does NOT need the sampler" scoping. `data/physics_estimates.db` `session_estimates` (Q, 2019-2026, 1597 rows) joined to season DBs via a from-scratch year-aware team-name reconciliation (the existing `team_canonicalization.py` helper would MISJOIN pre-2024 Alfa Romeo rows if reused — confirmed live, filed as #635).

**Primary result**: Pearson r = **-0.0923**, 95% CI **[-0.1281, -0.0562]**, n=2923 — correctly-signed (more grip → more negative quali error, i.e. faster than recent-form predicts), CI excludes zero. Small but real.

**Secondary (exploratory, never headline)**: 9 other raw axes + a `power_to_drag` composite, all reported with CIs (full table in `G1_FINDINGS.md`); two secondary axes' CIs also exclude zero (`brake_decel_ms2` -0.0646, `traction_aero_accel_per_m` -0.0582) but are explicitly labeled non-primary.

**Caveat, reported honestly**: Spearman rho on the primary axis = +0.0135 (CI [-0.0228, +0.0497] includes zero) — sign-mismatched with the Pearson result. Filed as **#634** for Phase 7's fuller G1 treatment rather than investigated further here (out of Phase-0 scope).

Crew-reviewed (independent implementer + independent reviewer, both dispatched via Agent tool per `lesson:run-crew-cli-launcher-misfit`), **verdict APPROVE**. Reviewer independently reproduced the headline number, independently verified the join-grain via direct SQL (proved the `session_estimates` join key is structurally unique — cannot duplicate rows), and independently confirmed the team-name misjoin risk claim by simulating the existing helper against live DB values.

### 2. Wide-σ A/B checkpoint — **NULL (confirmed structural, not a bug)**

Pushed 2025 Japan's five-view `session_estimates` (constructor-broadcast, per-view `lateral_total_grip_g` as `residual_mean`) through the existing `driver_residual_history_adapter.build_neutral_driver_residual_history_field` seam via `RuntimeModuleContext.driver_residual_states['quali']`, with a deliberately widened σ (16x variance / 4x SD inflation, documented independence-floor + inflation-factor reasoning — NOT copy-pasted from a single view's own diagonal, since `x7-basis-map-RESULT.md` establishes no cross-view covariance is stored).

**Seam confirmed externally injectable**: `SampledEvoRuntime.predict_from_features(runtime_context=...)` accepts an externally-constructed `RuntimeModuleContext` with **zero `src/` modification** — this was an open question in the handoff, now answered cleanly yes.

**Headless smoke: GREEN**, confirms #623 stays fixed under this modification. CPU>0 rigorously confirmed (process-CPU-time polling, steady ~1.03 CPU-s per 0.5s wall across both runs, ~208.9s wall clock each — not the 0%-CPU deadlock signature). Independently re-confirmed by the reviewer.

**G0/G1 result: bit-identical structural null.** Brier baseline = injected = 0.13028701052631578 exactly; G1 delta = 0.0. **Root cause, independently confirmed by both implementer and reviewer** (the reviewer specifically ruled out "this is a script bug" by tracing `driver_residual_states`'s sole consumer through the entire codebase): `driver_quali_power_from_residual_history` is registered in `module_adapters/_registry.py` but present in **ZERO** `params/gold/*.json` manifests' active fusion `steps` — the injected data is structurally never read regardless of content. Filed as **#636** (prerequisite for any future physics-injection test: wire the module into a manifest first).

Crew-reviewed, **verdict APPROVE**. `git checkout -- data/` run in the main checkout after this probe per known issue #632; confirmed clean.

### 3. Integration tracer — **ROUND-TRIPS (contract gap named, not a wiring failure)**

Ran the exact verified headless invocation from the launch order, 2025 Japan, seed 42. Completed headless in ~4 min, `.pth` confirmed resolving to the worktree before the run. Produced a 514 KB well-formed output.

**"Round-trips" operationally verified**: no error; `scripts/g3_schema_assert.py --check` (committed) asserts the output's schema (`stage_snapshots: {quali, race_start, race}`, `position_distribution` sums to 1.0 per driver, etc.) and spot-checks 3 real drivers (VER/NOR/PIA, the DB's actual top-3 Q classification) against the prediction — all present with non-trivial, sane probability mass. All checks PASS.

**Contract gap, named as a finding not a failure**: DESIGN_SPEC's Phase-5 four-record contract (weekend-state / car-basis posterior / lap evidence / as-of feature view) is **UNBUILT** — Phase 0 runs before Phase 5. Today's live artifact is a single monolithic JSON keyed by simulation STAGE (quali/race_start/race), not the Phase-5 taxonomy. This decouples seam/wiring risk (confirmed sound) from architecture-shape risk (Phase 5's job, not Phase 0's), exactly as the launch order scoped this tracer to do.

Reasoning gate (commander-direct, no crew — mechanical schema-assert + spot-check substituted for review per the plan's cold-critic-triaged disposition). `git checkout -- data/` cleanup confirmed after this probe too (#632).

### 4. SQ coverage probe — **PLAUSIBLY COMPATIBLE**

`load_quali_session(2023, "Austria", "SQ", ...)` loads a real SQ session without error; `estimate_session(..., session=<SQ session>)` runs to completion via the existing `session=` override, bypassing the internal hardcoded `"Q"` load while `quali_mass()` still applies unconditionally (the known, documented gap — genuinely uncorrected here).

**Numeric plausibility, not crash-only** (per the plan's own cold-critic finding): compared all 11 axes against the SAME constructor's SAME-weekend stored Q estimate (2023 Austria, Red Bull Racing — tighter than an adjacent-round comparison). **10/11 axes plausible** (same-sign, 0.4x-2.5x band): drag, power, both lateral-grip components, traction, and coast axes all land 0.5x-1.4x of the Q value despite the mass mismatch. One flag: `brake_aero_decel_per_m` (ratio 2.96x) — likely that axis's known noise-sensitivity per x7 ("already the most locally-fit, least density/circuit-sensitive quantity"), not necessarily SQ-specific; recommend-and-deferred rather than filed (single data point, folds naturally into future #513 FP/SQ work).

Reasoning gate, commander-direct. **Self-caught correction reported honestly**: the first run of the probe script accessed `SessionEstimate` as if it had flat attributes matching DB column names; it actually nests per-view (`.lateral.lateral_mech_grip_g`, etc.) — produced an all-n/a table, self-caught (obviously wrong output), corrected against verified source, re-run. Architecture-boundary check (`constraint:physics_region_no_evo_import`) confirmed clean — the one over-broad self-authored grep postcondition (matched docstring mentions, not real imports) was `waive --force`d with a fully-documented reason after independent verification the real constraint holds.

### 5. SQ coverage probe extends the screen's n — see #4 above (folded together; SQ store coverage is still zero rows in `session_estimates` — this probe used the estimator directly, not the store).

### 6. Baseline lock — **DONE, verbatim-verified**

`docs/physics/624-phase0-baseline-lock.md` (committed) freezes:
- **x4's per-axis relative-normalization floor** (11-axis table: field σ, noise SD abs/rel, weekends-to-resolve at 1-field-σ) — table transcribed and **byte-diff-verified identical** against the source excursion file (`x4-normalization-RESULT.md`), zero recomputation.
- **x7's five-fracture checklist** (mechanical grip triplet, dual-CdA reconciliation, cross-view covariance persistence [non-deferrable per F5], shared-trajectory-noise propagation, longitudinal a_long reconciliation) — transcribed from `x7-basis-map-RESULT.md` section (b).

Reasoning gate, commander-direct (pure transcription, no new computation — verified as such via the byte-diff check).

## Wave 7A / #623 confirmation

Headless A/B smoke ran green in both g2 and g3 (two independent full sampler invocations, both CPU-bound throughout, no deadlock). #623's fix holds under this wave's additional load.

## Isolation evidence

```
$ git worktree list
C:/Programs/f1Brainz 16c314b9 [main]
C:/Programs/f1-624   16c314b9 [feat/624-phase0-probes]

$ py -c "import src.evo_predictor.run as r; print(r.__file__)"
C:\Programs\f1-624\src\evo_predictor\run.py
```
(Re-confirmed before every run that touched `src.*`, per the `.pth` trap warning.)

## PR

**#637**: https://github.com/fredcai6/f1Brainz/pull/637 (base `main`, branch `feat/624-phase0-probes`, commit `cc264e02`). 8 files changed (4 new scripts, 1 new doc, 3 architecture-packet updates), 1222 insertions. Not merged — Admiral's call per Inherited Latitude.

## Triage candidates filed / deferred

- **#634**: Pearson/Spearman sign mismatch on g1's primary axis — filed.
- **#635**: `team_canonicalization.py` year-agnostic misjoin risk (confirmed live, would break pre-2024 Alfa Romeo rows if reused for this join direction) — filed.
- **#636**: residual-history injection seam code-complete + externally usable but wired into zero production manifests — filed.
- SQ probe's flagged `brake_aero_decel_per_m` axis — recommend-and-defer, folds into future #513 FP/SQ mechanics work, not filed standalone.

## Map impact

Cartographer reconciled: `docs/architecture/packets/evo_predictor.md` (residual-history seam finding — sharpens the pre-existing "not in production manifest" note with the confirmed-externally-injectable-but-dormant fact), `packets/physics.md` (baseline-lock doc reference), `index.md` (2026-07-18 reconciliation-log entry). `check_arch_map.py` green, unchanged node/packet/overlay counts (42/20/12) — zero `src/` changes this run, confirmed by both Cartographer and my own independent `git status --short` re-check.

## Anything floated to the Admiral

**Nothing required floating this run** — no genuine gap outside inherited latitude was hit. Two decisions I made within my own delegated latitude, documented for your visibility rather than floated as blocking questions:

1. **"Evo's own quali error" construction** (`PROBLEM_STATEMENT.md` "Gap resolution" section): the launch order named the *method* (semi-partial correlation vs recent-history) but left the exact operationalization of "quali error" underspecified, and no ready-made artifact existed (would have needed either heavier NN-inference machinery, arguably scope-creeping past "no new modeling," or a from-scratch pure-DB/pandas construction). I chose the latter: `quali_error` = actual pace-gap minus the driver's own trailing-mean recent-history baseline — the same primitive named in the launch order as "evo's existing recent-history feature," so residualizing against it is exact by construction, not approximate. Reported here for your review, not blocking.
2. **g4's target weekend and comparison baseline**: chose 2023 Austria (a sprint weekend with `session_estimates` already covering the SAME weekend's Q session for a tight same-weekend comparison, rather than a looser adjacent-round comparison the launch order's imperative literally named). A strictly better substitute for the same purpose, not a deviation in spirit.

Neither is a scope-cut or a deferral of Phase 0 scope itself — both are implementation-detail decisions squarely within "run analyses... write findings/artifacts" latitude. The one genuine SCOPE decision this wave produces — whether/how to defer pieces of Phases 1-6 based on these reads — is explicitly **not mine to make** (Pre-Ruling: "you PRODUCE the reads, you do NOT decide deferrals"). My read for your checkpoint: g1's signal is real but small (consistent with `decision:regime_readiness_rubric`'s prior "circuit-conditional, fine-margin" finding — nothing here overturns that prior); g2's null is entirely a WIRING gap (module never activated), not evidence against the physics axes themselves — the seam works, the axes weren't reachable to test end-to-end; g3/g4 are clean, unsurprising confirmations. Nothing here argues for cutting scope; if anything g2's finding suggests the fastest next unlock (wiring the residual-history module into a manifest) is cheap and would let a REAL end-to-end physics-injection test happen before committing to the full Phase 1-6 build.
