# Triage Recommendations — evo-prediction-ceiling

Authority: issue creation is autonomous for non-trivial tasks per ORCHESTRATOR_CONTEXT,
but this run requires explicit human approval per issue before filing.

---

## tc1 — Deferred fused-Brier confirmation → RECOMMEND: DROP (moot)

**Classification:** unresolved decision (resolved)

**Problem:** Authored at plan time as the tracked compromise for the "offline + deferred
retrain" done-bar, assuming G3 would ship a runtime σ re-level.

**Current truth:** G3 (re-level) was **declined** — the evidence showed no mis-level. The
only changes this run are (a) diagnostic-flag semantics (report-only, not consumed by
prediction/fusion at runtime) and (b) docs + one architecture packet line. **Nothing this
run changes runtime σ values or predictions, so there is no Brier impact to confirm.**

**Impact:** None. The recurring model-bound re-check (re-verify race-start `sigma_corr`
significance + coverage each gold cycle) is already documented in the §4 re-check protocol
of `docs/evo/prediction_ceiling_and_priorities.md`.

**Recommendation:** Do **not** file. Drop as moot. (If desired, the §4 protocol already
covers the recurring check.)

**Issue creation authority:** ask user (recommend: drop)

---

## tc2 — Gold-cycle reporter emits `entity_count=None` per event → RECOMMEND: FILE

**Classification:** bug (data-quality / report producer)

**Structural anchor:** `src/evo_predictor/` (gold cycle reporting) → `event_level_metrics`

**Problem:** Every `event_level_metrics[*].entity_count` in the gold-cycle `details.json`
is `None`. The post-hoc σ calibration computes `calibrated_σ = α·trace + β·max(entity_count−1,1)`;
with `entity_count=None` the `effective_dof` term collapses to a constant `1`, so the
`β·dof` half of the calibration is **degenerate** (a per-module constant offset, carrying
no per-event field-size information).

**Current truth:** Calibration still fits `α` and a constant `β` offset; the dof-scaling
the formula intends never engages.

**Evidence:**
- G1 harness: all 288 event rows have `entity_count=None` (stated in IMPLEMENTER_RESULT,
  forced the dof→1 fallback).
- G1 reviewer independently confirmed (swept dof ∈ {1,5,10,20} as a robustness check).

**Impact:** Second-order for *this* run (we found the race-start level is fine regardless),
but it means a designed calibration mechanism is silently inert. Any future σ-level work
that leans on the dof term would be building on a degenerate input.

**Suggested scope:** Populate per-event `entity_count` (the scored field size) in the
gold-cycle reporter that writes `event_level_metrics`; verify the calibration `β·dof` term
becomes meaningful.

**Non-goals:** Re-leveling σ; changing the calibration objective.

**Acceptance criteria:**
- [ ] `event_level_metrics[*].entity_count` is populated with the real per-event entity
      count in newly written gold-cycle details.
- [ ] A unit test asserts `entity_count` is a positive int for scored events.
- [ ] `effective_dof` reflects the populated count (no silent None→1 collapse for scored events).

**Recommended priority:** medium — **Reason:** silent degeneracy of a designed calibration
term; cheap to fix; prevents future work building on a constant.

**Issue creation authority:** ask user (recommend: file)

---

## tc3 — σ/error-correlation diagnostic key-set mismatch → RECOMMEND: FILE

**Classification:** bug (latent diagnostic inconsistency)

**Structural anchor:** `src/evo_predictor/module_uncertainty_diagnostics.py`
(`_SIGMA_ERROR_CORR_KEYS`) ↔ `src/evo_predictor/gold_module_cycle.py`
(`uncertainty_calibration` correlations)

**Problem:** The diagnostic evaluates the sigma/error-correlation flags over
`_SIGMA_ERROR_CORR_KEYS = (corr_sigma_pi_trace_vs_log_loss, corr_sigma_pi_trace_vs_brier,
corr_sigma_pi_trace_vs_rank_mae)`, but the gold cycle only ever **emits**
`corr_sigma_pi_trace_vs_nll` and `corr_sigma_pi_trace_vs_rank_mae`. So: `log_loss` and
`brier` are never present (silently filtered), and the emitted `nll` channel is **not in
the key list** and is therefore ignored by the flag logic. Net: the sigma/error gate is
driven by **`rank_mae` alone**, not the multi-channel set the code implies.

**Current truth:** After G2, the (now n-aware) `wrong_sign` / `insignificant` flags are
computed only from `rank_mae`; the design intent of multiple channels is silently unmet.

**Evidence:**
- G2 implementer out-of-scope observation (#1), confirmed against both modules' source.
- G2 reviewer corroborated: "only `corr_sigma_pi_trace_vs_rank_mae` is populated; log_loss/
  brier are null and correctly filtered."

**Impact:** The diagnostic looks more multi-channel than it is; if `brier`/`log_loss`
channels were intended (they are named in the schema), they are silently absent, and `nll`
is computed-but-unused by the flag. Affects how comprehensively the honest gate screens σ.

**Suggested scope:** Reconcile the key sets — either (a) align `_SIGMA_ERROR_CORR_KEYS` to
the channels actually emitted (`rank_mae` + `nll`), or (b) emit `brier`/`log_loss`
correlations if they are intended; add a test asserting producer/consumer key-set
consistency.

**Non-goals:** Changing the significance gate (done in G2); re-leveling σ.

**Acceptance criteria:**
- [ ] The diagnostic's evaluated key set exactly matches the gold-cycle emitted set (no
      silently-absent or computed-but-ignored channels).
- [ ] A unit test asserts producer keys ≡ consumer keys for the sigma/error correlations.

**Recommended priority:** medium — **Reason:** latent silent gap in a probability-adjacent
diagnostic; now load-bearing after G2 made the gate the honest screen.

**Issue creation authority:** ask user (recommend: file)
