# Triage Recommendations — issue-369-pace-gap-form (2026-06-05)

Authority note: ORCHESTRATOR_CONTEXT allows autonomous issue creation, but this
run's spine requires explicit human approval per issue before filing. All
items below are issue-ready; none filed yet.

---

## R1: Race recent-history pace-gap re-encoding — design investigation

**Classification:** feature / research hardening
**Source:** spine triage_candidates tc1 (understand phase, human-confirmed scope cut)
**Structural anchor:** `src/evo_predictor/recent_history_adapter.py` (driver race RH), `constructor_race_recent_history_adapter.py`
**Problem:** #369 deliberately scoped pace-gap form encoding to quali only. Race pace-gap is a separate design problem: race lap times carry fuel burn, safety cars, stint structure — a single `(t−median)/median` per event is not obviously meaningful.
**Current truth:** race RH modules encode form as position→quality (v1). The quali provider/adapters (G1/G2) and plumbing (G3) exist and are reusable patterns.
**Evidence:** G4 A/B on the quali side came back MIXED (σ↔error corr: constructor better, driver worse) with a `pairwise_nll_skill` regression in both modules (`.agent-work/archive/.../evidence/ab_comparison.md`) — this weakens the prior for extending the encoding to race before the quali follow-up resolves.
**Suggested scope:** design note first (what race-pace quantity is comparable across events: median-relative on green-flag laps? stint-normalized? leave-as-is?), only then any implementation.
**Non-goals:** implementation before the design note; any default change.
**Acceptance criteria:** design note with a go/no-go recommendation grounded in the quali A/B outcome.
**Priority:** low. **Reason:** quali A/B did not confirm the variance claim; race variant is strictly harder.

---

## R2: Race-start recent-history form-encoding investigation

**Classification:** research hardening / unresolved decision
**Source:** spine triage_candidates tc2 — **user explicitly requested this investigation** (lower priority) at understand-confirm
**Structural anchor:** `src/evo_predictor/race_start_recent_history_adapter.py`
**Problem:** #369's "analogously race-start" premise does not apply: race-start RH history is grid→target-lap gain, not position-quality. What a pace-like / variance-enriching re-encoding even MEANS for start history is an open question.
**Current truth:** race-start RH per-event quantity is `grid_pos − target_lap_pos` style gain features (`mean_grid_to_target_lap_gain`, …); no form_encoding concept exists there.
**Evidence:** code inspection during issue-369 understand phase (interrogation.json q1/q7).
**Suggested scope:** short investigation: enumerate candidate enrichments (e.g. gain normalized by field churn, launch-delta from telemetry if DB carries it, variance-of-gain windows), assess data availability in the DB, recommend file-or-drop.
**Non-goals:** implementation; touching quali/race encodings.
**Acceptance criteria:** written recommendation (pursue with spec / drop with reason).
**Priority:** low (user's own words). **Reason:** explicit user wish, parked.

---

## R3: Split `src/data/database/_metadata.py` (at 999-line strict ceiling)

**Classification:** cleanup / architecture weakness
**Source:** execute tc1 (G1 implementer + reviewer observation)
**Structural anchor:** `src/data/database/_metadata.py` (DatabaseMetadataMixin)
**Problem:** the file sits at exactly 999 lines (MAX_FILE_LINES strict). Any future read-method addition breaches limits immediately; G1 had to compact docstrings below sibling standard to fit.
**Current truth:** mixin holds completeness metadata, classifications batch, race-start order, practice laps, environment, and the new quali best-laps query; assembled into DatabaseManager in `database/manager.py`.
**Evidence:** `py -m src.utils.simplification_limits --paths src/data/database/_metadata.py` → PASS at 999/999; G1 IMPLEMENTER_RESULT + REVIEW_RESULT.
**Suggested scope:** split along read-domain seams (e.g. `_metadata.py` core vs `_session_queries.py`), no behavior change, re-export through manager unchanged; restore full docstrings on compacted methods.
**Non-goals:** schema or query changes.
**Acceptance criteria:** limits PASS with headroom; `tests/unit/data` green; no import-path changes for consumers.
**Priority:** medium. **Reason:** hard blocker for the next DB read method anyone adds.

---

## R4: Decompose `build_driver_recent_history_pair_batch` (race RH adapter)

**Classification:** cleanup
**Source:** execute tc2 (G2 implementer stash-verified baseline finding)
**Structural anchor:** `src/evo_predictor/recent_history_adapter.py`
**Problem:** pre-existing strict-limits violations: cc=30 (<20), function_lines=143 (<100).
**Current truth:** violations exist on main (baseline-identical, verified via stash round-trip during G2); function untouched by #369.
**Evidence:** limits output in G2 IMPLEMENTER_RESULT; commander stash verification.
**Suggested scope:** same decomposition pattern as issue #363 / the G2 quali-adapter refactor (`_resolve_encoding_fns`/`_build_pairs` helper extraction is a ready template in `quali_recent_history_adapter.py`). Behavior-preserving; existing tests green unmodified.
**Non-goals:** encoding changes; touching the quali adapters.
**Acceptance criteria:** limits PASS on the file; `tests/unit/evo_predictor/test_recent_history_adapter.py` (and region) green unmodified.
**Priority:** low-medium. **Reason:** debt, not a blocker; clean template exists.

---

## R5: Evo plumbing strict-limits debt (monster functions)

**Classification:** cleanup / architecture weakness
**Source:** execute tc3 (G3 baseline-verified via clean worktree at HEAD)
**Structural anchor:** `src/evo_predictor/data_adapter/_build.py`, `module_training_orchestration.py`, `sampled_runtime.py`, `module_adapters/_common.py`
**Problem:** pre-existing violations concentrated in the plumbing layer every new knob must thread through: `build_race_features` (cc=29, 231 lines), `build_all_race_features` (cc=27, 215 lines), `build_labeled_batches_for_module` (cc=36, 163 lines), `build_evidence_mode_eval_batches` (106), `build_recent_history_holdout_eval_batches` (148), `predict_from_features` (153), `_build_recent_history_race_features` (cc=22).
**Current truth:** all baseline-verified pre-existing before #369 G3; G3 added only irreducible kwarg threading (+3 lines) after rework restored everything else to baseline.
**Evidence:** clean-worktree baseline limits run (commander, 2026-06-05); G3 IMPLEMENTER_RESULT rework section.
**Suggested scope:** one decomposition pass per file (likely separate gates); each behavior-preserving with region tests green.
**Non-goals:** behavior/contract changes; combining with feature work.
**Acceptance criteria:** named functions under limits or split issues landed per the grandfathered-paths policy; region green.
**Priority:** medium. **Reason:** this debt taxes every future evo change (it taxed #369 twice: rework cycles in G3).

---

## R6: Pace-gap encoding follow-up — disposition of the A/B outcome

**Classification:** unresolved decision
**Source:** execute tc4 (G4 evidence)
**Structural anchor:** issue #369; `quali_recent_history_adapter.py` v2 path; cross-ref issue #368 (median-pace race_weekend cousin — these results are evidence for its "decide" phase)
**Problem:** the issue's untested variance claim is now tested at n=24: NOT confirmed. σ↔rank-MAE corr: constructor improved (0.427→0.494), driver worsened (0.534→0.420); σ↔NLL ~flat; ordering flat (as predicted); `pairwise_nll_skill` regressed in both (driver 0.453→0.343, constructor 0.519→0.390 — fusion weights consume `exp(-skill)`).
**Current truth:** the capability is merged-ready, flag-gated, default OFF, bit-identical when off. Evidence: `.agent-work/.../evidence/ab_comparison.md` (committed 3efb206).
**Suggested scope (if pursued later):** longer-epoch convergence check for the v2 feature space; fusion-weight impact quantification; larger-n eval. Until then: default stays `position_quality`.
**Recommended disposition:** comment the verdict on #369 at closeout (happens at this run's review/archive regardless); no separate issue unless the user wants the follow-up tracked independently.
**Priority:** low. **Reason:** evidence says don't invest more until something changes.

---

## R7: NLL metric naming friction — `corr_sigma_pi_trace_vs_log_loss` vs schema-v6 `pairwise_nll`

**Classification:** cleanup / missing doc
**Source:** G4 implementer out-of-scope observation 1
**Structural anchor:** `src/evo_predictor/module_uncertainty_diagnostics.py` / `gold_module_cycle.py` key naming; `docs/report_schemas/`
**Problem:** the uncertainty-diagnostics surface still names its correlation key `corr_sigma_pi_trace_vs_log_loss` while schema v6 eval metrics standardized on `pairwise_nll` (sign-flipped convention). Cross-arm comparison required a manual sign bridge in G4; the next consumer will hit the same trap.
**Current truth:** promoted v6-era artifacts carry log_loss-named keys computed from NLL-domain quantities; G4 bridged it correctly (verified by reviewer against `nll_eval.py` skill=chance−raw).
**Suggested scope:** rename the emitted key (or document the convention in the report schema doc) — possibly folds into #335 (regenerate gold artifacts against v6) since a rename implies artifact regeneration.
**Non-goals:** changing the math.
**Acceptance criteria:** one consistent NLL naming/sign convention across gold report, unc_diag, and backtest outputs, OR the convention bridge documented in `docs/report_schemas/`.
**Priority:** low. **Reason:** trap, not a defect; G4 verified the math is right.

---

# Routing outcomes (user-approved 2026-06-05)

| Rec | Disposition |
|---|---|
| R1 | Filed #394, linked as sub-issue of #392 |
| R2 | Filed #395 (low) |
| R3 | Record-only — "we will deal with it when we get to it" |
| R4 | Filed #396 |
| R5 | Filed #397 |
| R6 | Verdict commented on #369; judgement deferred to full retrain, noted on #335 |
| R7 | Folded into #335 (comment) |
