# Review Result — g4 held-out-weekend diagnostic (#670, epic #659)

## Assigned Gate
`g4` — held-out-weekend DIAGNOSTIC (strictly-pre), the LEAKAGE-CRITICAL gate.

## Result
`APPROVE`

Verified independently (not on faith): both leakage guards re-run + counterfactually proven discriminating; σ-artifact magnitude spot-checked on the real slice; landed modules confirmed byte-untouched. Survey `.agent-work/670-season-run/g4-review/review.json` driven to consolidation, 0 open fails.

---

## CENTRAL ADJUDICATION 1 — ZERO LEAKAGE (both arms' driver inputs): CONFIRMED

**Guard 1 (fingerprint fit, as_of=R-1, internally derived).**
- `fit_cells_as_of` sets `as_of_round = held_out_round - 1` **internally** (script line 145); the caller only ever passes the HELD-OUT round R, so no caller can inject a leaking cutoff. Confirmed by source, not claim.
- `fit_driver_fingerprints._read_observable_rows` filters `round_idx <= as_of_round` INCLUSIVE (fit.py line 113). With as_of = R-1 the max admitted round is R-1, so **R is excluded**. Reasoned through the SQL directly.
- `run_stage_g` (pipeline.py) forwards `as_of_round` unchanged to `fit_driver_fingerprints` — that path is UNTOUCHED by g4.
- **DISCRIMINATING (independently reproduced, not trusted):** I rebuilt the fixture and fit at the *leaking* cutoff (`held_out_round=R+1` → as_of=R, which admits the round-R poison). Result: clean vs poison cells DIFFER, AAA/c0 utilization mean moves `0.5153 → 1.585e5`. At the honest cutoff (as_of=R-1) clean==poison. So the guard test's equality assertion genuinely bites; a leaking fit would fail it.

**Guard 2 (golf-null field pool, round_idx < R).**
- `golf_null_field_pool` SQL filters `round_idx < held_out_round` (script line 241/245) → round R excluded; plus a structural `AssertionError` if `max(rounds_used) >= held_out_round` (line 266).
- **DISCRIMINATING (independently reproduced):** pooling at the leaking bound (`held_out_round=R+1` → `round_idx < R+1`, admits round R) makes clean vs poison `per_class` DIFFER, c0 mean `0.615 → 2e5`. At the honest bound (`< R`) they are identical. Guard bites.

Both driver-input arms (fingerprint cells + golf null) are strictly-pre. The only non-strictly-prior input is the SHARED `__field__` track-geometry composition — it carries no driver-specific signal and is read identically across arms, so it cannot advantage any arm. **No driver input can include round ≥ R data. No leakage.**

## CENTRAL ADJUDICATION 2 — THE σ-ARTIFACT: REAL, HONEST, NOT METRIC-SHOPPING

- **(i) Magnitude is real.** Independently queried the real slice `refutil_season_2023.db` (1524 severity rows): `g_sigma_onesided` mean **1.147e9**, p90 **8.08e9**, max **9.62e9**; **20.2%** of rows > 1e6; vs `|time_deficit_s|` median **0.187s**. Matches the implementer's claim (mean ~1.1e9, p90 ~8e9, ~20%). fit.py `_compose_sigma` (line 257) folds `g_sigma_onesided` into cell σ in quadrature, so those cells' predictive intervals are vacuously wide (arms 1/2 coverage 1.000) and their log-score is catastrophic — a variance property of the LANDED #666 fit, not a bad point prediction. The golf null uses empirical field dispersion (well-scaled; coverage 0.911, not 1.0), so its σ-basis differs — log-score is genuinely not equal-footing across the arms.
- **(ii) Leading with |resid| is HONEST, not a workaround to hide a bad result.** The point metric does NOT flatter the driver term: golf null |resid| 0.830 BEATS fingerprint 0.854 — the report states plainly "the whole driver term does NOT beat the field null on point error" (both `fingerprint_beats_golf` / `baseline_beats_golf` reported **False**). Metric-shopping would claim victory; this surfaces the unfavorable near-null result. Only the genuinely-supported sub-claim is asserted (composition-weighting helps: arm1 0.854 < arm2 1.14).
- **(iii) Both metrics presented honestly with the caveat.** The report LEADS with a "⚠ Sigma interpretation — read first" block and prints BOTH the log-score and |resid| columns. The σ mis-calibration is correctly attributed to #666 (fit.py is do-not-edit) and routed as a triage candidate, not silently swallowed.

**Not masking a diagnostic defect:** the diagnostic faithfully propagates the fit's cell σ through `join → predictive_t → t.logpdf`; the bad log-score originates in the landed fit's σ, not in g4 code.

---

## Handoff compliance
Delivered exactly the mandated 3-arm strictly-pre held-out diagnostic composing landed pieces only (`join_weekend_prior` + `fit_driver_fingerprints` via `run_stage_g` + `derive_pilot_vocabulary` + `ReferenceUtilizationStore` + a field-mean pool). No new statistical model. All close criteria met.

## Scope drift
Only the two sanctioned NEW files are g4's (`scripts/run_heldout_diagnostic_670.py`, `tests/unit/physics/fingerprint/test_heldout_diagnostic.py`; both untracked). Excluded modules `join.py`/`fit.py`/`store.py`/`frozen_constants.py`: **zero committed diff vs main AND absent from the working-tree modified set**. `run_stage_g` untouched.

## Evidence verdict
Re-ran on the pinned 3.14 interpreter: **5/5** diagnostic tests, **108 passed / 13 skipped** fingerprint suite, **pyright 0/0/0**. Plus my own counterfactual (both guards discriminating) and real-slice σ query. Evidence demonstrably backs the behavior. T7-1 identity (uniform composition == unweighted resolved-cell mean) and composition=`__field__` row both covered by passing tests and confirmed by source reading. Student-t preserved on all three arms (`predictive_t` + `stats.t.logpdf(df=prior.nu)`, no normal approximation).

## Code/doc quality
Minimal, maintainable, well-documented for a subtle-and-silent gate. Project crew rules honored: explicit as-of cutoff with no None-means-latest fallback; read-only DB access (`file:...?mode=ro`); intentional missingness (`truth=None` → skipped, fully-thin → unresolvable not forced); named constants. Fowler pass verified (exit 0): 2 non-blocking observations (long-method `run_diagnostic`; minor duplicated arm-add blocks + a deliberately-mirrored column map), 3 overrides logged against the CREW explicit-identity/as-of standard.

## Map impact verdict
- **Evidence supports claimed change:** Yes — sizes composition-weighting vs driver-overall vs golf null strictly-pre.
- **Constraints not violated:** Zero-leakage (both guards), Student-t, one documented baseline, offline read-only — all honored.
- **Notes match the diff:** Yes; no structural anchors edited, new composition-only consumer over landed seams.
- **Decision candidates surfaced:** `decision:diagnostic-baseline` settled as join T7-1 uniform-composition, stated + justified per #667 TC-1.
- **Durable context routed:** Two triage candidates correctly routed — (1) #666 fit σ calibration (g_sigma_onesided dominance, independently confirmed); (2) driver-term near-null on the 2023-only slice → multi-season / vocabulary variant.

## Reconciliation check
No architecture divergence requiring Commander reconcile. New leaf diagnostic script over existing seams; no contract/schema change.

## Blockers
- none

## Out-of-scope observations
- **Shared-worktree residue (NOT a g4 defect):** the working tree carries sibling-gate edits `M src/physics/pilot/pipeline.py` (adds `budget_s`/`refutil_db` run-params to `run_circuit` for the season run — NOT `run_stage_g`) and `M data/f1_data_2023.db`. Outside g4's diff; flagged so integrate/closeout does not attribute them to g4.
- Conclusions are a COMPLETE no-frame-kill result (composition-weighting helps; driver term thin/near-null vs golf null on the bounded 2023 slice), correctly routed to structural follow-on work rather than reported as failure.

## Workflow Feedback
- **Handoff gaps:** none material — the handoff's two central adjudications were precisely scoped and correct. The one real friction it flagged in advance (log-score confounded by differing σ-bases) is a genuine handoff/landed-fit mismatch the implementer surfaced well; a future handoff mandating a primary metric should name which σ-basis the arms share, or mark |resid| co-primary when σ-bases differ.
- **Context rediscovered:** that `run_stage_g` (pipeline.py) is the ready-made fit+read wrapper the diagnostic composes — the map anchors named `join`/`fit`/`derive_pilot_vocabulary` but not this wrapper; adding it would have saved a lookup. Also had to disentangle sibling-gate working-tree modifications from g4's own diff in the shared worktree.
- **Instructions improvised around:** none — engine, templates, and Fowler rail covered the review cleanly.
- **What would have made this easier:** a one-line note in the handoff that `git status` in this shared worktree shows sibling-gate `M pipeline.py`/`M *.db` residue would have pre-empted the scope disambiguation.

## Return status
`complete`
