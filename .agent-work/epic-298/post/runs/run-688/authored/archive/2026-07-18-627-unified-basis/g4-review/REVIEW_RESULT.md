# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
g4 (σ-honesty wiring + explicit-unknown semantics — #506 + Tier-1 #3)

## Result
`APPROVE` (updated after independent re-verification of a follow-up fix — see "Addendum: re-verification" at the end of this document. Original BLOCK verdict and its full reasoning are preserved below unmodified for audit.)

## Handoff compliance
All four close-criteria items are genuinely implemented and independently confirmed via direct diff read (not just IMPLEMENTER_RESULT.md's word):

1. **SYSTEMATIC_FLOOR retirement.** The flat `SYSTEMATIC_FLOOR` dict + `_apply_floor` are fully removed from `estimate_store.py`, replaced by `_floor_with_budget` (guarded per-session call into G1's `systematic_budget()`, with an honest-wide fallback constant for cda/p_max ONLY when rho/mass are missing) and `_floor_constant_rel` (A0/A2's session-independent curvature/terrain bound). Every field-builder (`_drag_area_fields`, `_braking_fields`, `_traction_fields`, `_power_drag_fields`, `_lateral_fields`) is threaded through the computed `budgets`.
2. **`{axis}_shared_sigma` persistence.** 9 new nullable `EstimateRecord` fields are genuinely persisted, not dead dataclass slots — `EstimateStore._cols` / `_init_schema` / `_migrate_missing_columns` derive the SQL schema dynamically from `EstimateRecord.__dataclass_fields__` and self-heal via `ALTER TABLE`, so the new columns write and backfill correctly (confirmed by reading the schema builder, not assumed).
3. **Non-optional pooled floor (the #506 core).** `pooling.pool_random_effects` gained `shared_floor` (default `0.0`, floors `sigma_mu` in quadrature *after* DerSimonian–Laird shrinkage, rejects negative values). `pool_driver.pool_store`'s single `pool_random_effects` call site *always* passes `shared_floor=_shared_floor_for_param(...)` — confirmed by direct diff read that there is no alternate/legacy call path inside `pool_store` that could silently regress to unfloored. `_shared_floor_for_param` gracefully returns `0.0` (a real, passed no-op floor) rather than omitting the kwarg when the store has no shared-sigma data.
4. **Real explicit-unknown status.** `_axis_statuses` computes genuine `resolved`/`unresolved` per axis from actual session inputs (`theta_R` always unresolved; cda/p_max unresolved on PowerDrag degeneracy/absence; a_b/b_b on absent braking; a_t/b_t on absent traction; A0/A2 on absent lateral) — confirmed against the corresponding new unit tests. `effective_axis_sigma` + `normalize_axis_status` give a real, numerically-testable unresolved≫resolved contract (see Evidence verdict).

## Scope drift
None. `git status --porcelain` shows exactly the allowed 6 files (`estimate_store.py`, `pooling.py`, `pool_driver.py` + their 3 test files) plus the untracked `.agent-work/627-unified-basis/` workbench/local-script area the handoff explicitly permits. `git status --porcelain data/` is clean (no `data/*.db` write). `systematic_budget.py` and `weekend_state/*` are byte-identical to `HEAD` (grep + diff confirm zero changes) — the read-only exclusion was honored. The one known stale `SYSTEMATIC_FLOOR` prose reference inside `weekend_state/layer1_physics.py` (lines 23, 107) is present exactly as the handoff pre-flagged (out-of-scope doc-drift item tc6) — noted, not blocking.

## Evidence verdict
Both of the handoff's named "hardest judgments" were **independently reproduced end-to-end**, not accepted on the report's word — re-ran the implementer's own local `characterize_g4.py` myself against the real, untouched `C:/Programs/f1Brainz/data/physics_estimates.db` (read-only):

- **Pooled-floor plateau (Part A):** my own run reproduced sigma_mu(CdA) at n=17 = 0.039607 unfloored / 0.066314 floored, and sigma_mu(P_max) at n=22 = 7,310.6 / 20,222.0 — matching IMPLEMENTER_RESULT.md's reported numbers to the reported precision. Confirms sigma_mu shrinks below the derived shared floor without it, and plateaus at/above the floor with it, at every n from 2–22 on real RBR 2023 Q data.
- **weekend_state 0-flip (Part B):** my own run recomputed all 1562 real Q `ok` rows and got the identical result — `PASS 9/11` both before and after, `TOTAL FLIPS: 0/11 axes`. The script writes only to `.agent-work/.../scratch/*.db`, confirmed never touching `data/*.db`.
- Also independently confirmed `A0_CURVATURE_TERRAIN_BOUND_REL == 0.04` in `systematic_budget.py`, verifying the claimed bit-identical A0 old-vs-new equivalence is load-bearing by construction, not coincidence.
- Also spot-checked `estimate_batch.py`'s real production call site: `rho=rho` is unconditionally passed to `record_fn` — corroborates the "fallback path is test-only in production" claim (for the rho half).
- **Property-test numeric distinction:** confirmed by direct code read — `test_effective_sigma_degenerate_power_drag_unresolved_vs_resolved_cda` and `test_effective_sigma_absent_lateral_unresolved_vs_resolved` assert `unresolved_sigma > 10×`/`5× resolved_sigma` respectively. A real numeric assertion, not a comment.
- **Test suite:** independently re-ran the 3 directly-modified test files — `71 passed in 15.87s`, exactly matching the implementer's reported 48+15+8=71. The full required command (`tests/unit/physics/layer2/ tests/unit/physics/weekend_state/ -q`, 835 items) was independently launched by this review and observed progressing cleanly through its first ~100+/835 tests (zero failures, including 100% of the directly-owned region's own test files) before this review's active window closed — the run did not finish inside this session due to the same session-wide multi-agent contention IMPLEMENTER_RESULT.md itself documented (confirmed alive via `Get-Process`, CPU time still climbing, not hung). Given the implementer's own transcript already reports 835 passed on this exact command/worktree, every directly-touched test file passed cleanly under independent re-run, and zero anomalies appeared in the partial re-run, this is accepted as corroborated rather than a live blocker — **but the untouched tail of the full 835-test sweep was not independently observed to completion and should be confirmed by Commander before merge.**

## Code/doc quality
**BLOCKER found here.** `py -m src.utils.simplification_limits --paths src/physics/layer2/estimate_store.py src/physics/layer2/pooling.py src/physics/layer2/pool_driver.py` → **FAIL, exit 1**: `src/physics/layer2/estimate_store.py: file_lines=1010 (limit: <1000)`.

- Confirmed `estimate_store.py` was 791 lines at `HEAD` before this diff (`git show HEAD:<path> | wc -l`) — this diff's `+313/-97` pushed it from comfortably under the limit to 1010. This is a **genuinely new violation**, not pre-existing debt.
- `config/simplification_baseline.json` (the project's explicit grandfather allowlist for files already ≥1000 lines) contains only `src/physics/layer2/stint_estimator.py` — `estimate_store.py` is not grandfathered, and this diff does not add it.
- CREW_CONTEXT.md, "Verification By Region": *"Simplification limits (all regions)... Review blocker when skipped or failing on in-scope Python."* This is one of the project's own explicit, mechanical, named review blockers.
- IMPLEMENTER_RESULT.md's Evidence section never mentions running this check (only the layer2/weekend_state pytest suites); the implementer's own `IMPLEMENTER_PLAN.json` `m7-final-verify` postcondition also only names the pytest command — the simplification-limits gate was never on anyone's radar for this gate, not just failed and hidden.
- No function-length or cyclomatic-complexity violations — only the file-length metric failed.
- Everything else checked clean: no FastF1/Jolpica/live-API imports (DB-only rule); `shared_floor`'s `ValueError` names the field + actual value; units/bounds are explicit and documented in every new docstring; missingness (`None` on absent budget/shared component) is intentional and documented.

**Fix is mechanical and cheap:** either split `estimate_store.py` (e.g. extract the new `_floor_with_budget`/`_axis_statuses`/`_session_systematic_budgets` cluster into a sibling module) or add it to `config/simplification_baseline.json` with a tracking issue, per the project's own grandfathering mechanism. Implementer's call — the gate cannot close silently over a failing check the project explicitly names as a blocker.

## Map impact verdict
- **Evidence supports claimed change:** Yes — see Evidence verdict above; both the pooled-floor and weekend_state claims are independently reproduced with matching real numbers, not just asserted.
- **Constraints not violated:** Yes — "pooling cannot average away a shared bias" is now enforced end-to-end (confirmed via `pool_random_effects`/`pool_store` diff read + the plateau reproduction); `{axis}_sigma` column names are unchanged (additive-only migration, confirmed via the dynamic schema builder).
- **Notes match the diff:** Yes — every structural/capability/constraint claim in IMPLEMENTER_RESULT.md's Map Impact matches what the diff actually touched. No overstatement found.
- **Decision candidates surfaced:** Yes — the cda/p_max fallback-path-closure question and the `_shared_floor_for_param` median-vs-max/fixed-lookup judgment call are both surfaced with documented rationale, appropriately deferred to Commander/architecture review rather than silently decided.
- **Durable context routed:** Yes — Triage candidates (fallback-path closure, provenance flag for fallback-vs-real-budget floored rows) are named for follow-on, not dropped.

## Reconciliation check
No architecture-map contradiction. `docs/architecture/packets/physics.md`'s `struct:physics.layer2` node describes the `session_estimates`/pooling pathway generically without pinning `SYSTEMATIC_FLOOR` or the pre-G4 sigma semantics as load-bearing map content, so retiring it does not contradict recorded structure. `record_from_estimate`'s public signature is unchanged; `pool_random_effects` gained a backward-compatible optional kwarg (default `0.0`, bit-identical, proven by `test_shared_floor_zero_reproduces_unfloored_pooling`).

## Blockers
- `src/physics/layer2/estimate_store.py` fails the project's mechanical `simplification_limits` file-length gate (1010 lines, limit <1000) — a new violation introduced by this diff, not grandfathered, not run/reported by the implementer. Fix: split the file or add a documented `config/simplification_baseline.json` entry + tracking issue.

## Out-of-scope observations
- Fowler pass (r6, full record in `.agent-work/627-unified-basis/g4-review/fowler_pass.json`, `verify_fowler_pass.py` exit 0): **flagged** `shotgun-surgery` (a future 10th-axis addition now ripples one more touch point than before this gate — non-blocking, no axis was added here) and `speculative-generality` (`ParamPool.shared_floor` currently has only test consumers, not yet a proven second production adapter — cheap, well-documented, but worth watching). **Overridden** `duplicated-code` and `data-clumps`, each with a logged repo-standard + reason (see the record).
- The full 835-test `tests/unit/physics/layer2/ tests/unit/physics/weekend_state/` re-run launched by this review did not finish inside the session (session-wide multi-agent contention, same as the implementer's own experience) — recommend Commander re-confirm it completes green before merge, or re-run in isolation off-peak.
- The known stale `SYSTEMATIC_FLOOR` prose citation in `weekend_state/layer1_physics.py` (out-of-scope doc-drift, tc6) remains — not blocking, as pre-flagged by the handoff.

## Workflow Feedback

- **Handoff gaps:** The handoff's Evidence Produced / Stop Conditions sections named the pytest suites and the pooled-floor/weekend_state real-number evidence as the required checks, but did not name the project's own `simplification_limits` gate — a check CREW_CONTEXT.md documents as a blanket, mechanical, all-regions review blocker. Neither the handoff nor the implementer's own `IMPLEMENTER_PLAN.json` `m7-final-verify` postcondition included it, so it silently fell through both the implementer's self-check and would have fallen through review too if not run independently. Worth adding `py -m src.utils.simplification_limits --paths <touched>` as a standing final-verify postcondition template for any gate touching `src/`/`tests/`, not something each handoff has to remember to name.
- **Context rediscovered:** none material — the handoff and result doc were unusually thorough and the diff was easy to verify against both.
- **Instructions improvised around:** none — the skill's engine-drive + independent-reproduction instructions fit this task well. The one adaptation: given r4-quality already determined a BLOCK verdict, and the full 835-test sweep was legitimately still running (confirmed alive via CPU, not hung) after ~25 minutes of session-wide contention, I closed r3-evidence on the strength of the two independently-reproduced hardest-judgment claims + the fully-reproduced directly-relevant 71-test subset + a clean partial re-run, rather than blocking the review's own completion on a slow, diff-unrelated test file (`test_damage_tractability.py`, explicitly marked `@pytest.mark.slow`) finishing. Flagged the gap explicitly rather than silently treating it as fully confirmed.
- **What would have made this easier:** a documented "run the region's simplification_limits check" line item inside the reviewer skill's own survey template (not just inherited from CREW_CONTEXT prose) would make this class of finding harder to miss on a first pass, independent of whether a given project's CREW_CONTEXT happens to spell it out.

## Return status
complete

---

## Addendum: re-verification (verdict updated BLOCK → APPROVE)

**Trigger:** team-lead (relaying ShipF-627) reported the r4-quality file-length blocker fixed via a pure structural extraction — `estimate_store.py`'s field-flattening helpers moved verbatim to a new sibling module `src/physics/layer2/estimate_store_fields.py`, re-imported back into `estimate_store.py` — and asked for independent re-verification before updating the verdict. Per this skill's doctrine, the claim was reproduced, not accepted on the report's word.

**Independent checks performed (all in `C:/Programs/f1-627`, `py -c "import src.physics.layer2.estimate_store_fields as m; print(m.__file__)"` confirmed resolving under this worktree):**

1. **Mechanical gate re-run.** `py -m src.utils.simplification_limits --paths src/physics/layer2/estimate_store.py src/physics/layer2/estimate_store_fields.py src/physics/layer2/pooling.py src/physics/layer2/pool_driver.py` → **PASS, exit 0** (4 files checked). Line counts: `estimate_store.py`=438, `estimate_store_fields.py`=635, `pooling.py`=239, `pool_driver.py`=235 — all under the 1000-line limit; no function-length or cyclomatic-complexity violations. The original BLOCK finding is resolved.

2. **Behavior-preservation read.** Read the full `git diff` of `estimate_store.py` (now mostly deletions) side by side with the complete new `estimate_store_fields.py`. Every relocated function and constant (`_sigma`, `_cov_list`, `_inflate`, `_THETA_R_LITERAL`, the `_FALLBACK_*` constants, `_RHO_INFLATION`, `_TRUST_RANK`, `UNRESOLVED_AXIS_SIGMA_FRAC`, `normalize_axis_status`, `effective_axis_sigma`, `_axis_statuses`, `_session_systematic_budgets`, `_floor_with_budget`, `_floor_constant_rel`, `_drag_area_fields`, `_braking_fields`, `_traction_fields`, `_power_drag_fields`, `_lateral_fields`, `_coast_fields`, `_cda_jacobian_cross_terms`, `_fused_cda_inputs`, `_fused_cda_fields`, `_cross_view_covariance_fields`, `_fit_quality`, `_degrade_trust`, `_support_trust_profile`) is byte-identical to the pre-extraction diff this review already validated above — confirmed a verbatim cut/paste, not a rewrite. No default, threshold, unit, or control-flow changed. `estimate_store.py` now keeps only `EstimateRecord`/`EstimateStore`/`record_from_estimate`, re-importing the rest via one explicit import block.

3. **Real external consumer check.** `regime_readiness.py` imports `_cov_list` directly from `estimate_store` (a "private"-named but real cross-module dependency). Ran `py -c "import src.physics.layer2.regime_readiness"` — imports cleanly. Also directly imported `_cov_list`, `_sigma`, `UNRESOLVED_AXIS_SIGMA_FRAC`, `effective_axis_sigma`, `normalize_axis_status`, `_RHO_INFLATION`, `_THETA_R_LITERAL` from `estimate_store` in an isolated interpreter — all resolved. No caller's import path broke.

4. **Test re-run.** `py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_pooling.py tests/unit/physics/layer2/test_pool_driver.py tests/unit/physics/layer2/test_cross_view.py tests/unit/physics/layer2/test_systematic_budget.py -q` → **98 passed in 9.74s**, matching the reported count. `git diff --stat` confirms `pooling.py`, `pool_driver.py`, and all three test files carry the exact same diff this review already fully validated pre-extraction (unchanged line counts) — only `estimate_store.py` shrank and the new sibling file appeared. `git status --porcelain data/` still clean.

**Verdict:** the original BLOCK finding (file-length limit) is genuinely fixed by a pure, verified-behavior-preserving structural split; nothing else in the diff changed. Combined with the already-independently-reproduced core evidence (pooled-floor plateau, weekend_state 0-flip, numeric unresolved-vs-resolved property test, targeted test subset), this gate is now **APPROVE**.

**Carried-forward, still-non-blocking notes** (unchanged from the original review, not affected by the extraction):
- The full 835-test `tests/unit/physics/layer2/ + tests/unit/physics/weekend_state/` cross-region sweep was not independently observed to completion by this review (session-wide contention) — team-lead separately reports it running clean in the background; recommend Commander confirm it finishes green before merge.
- The new `estimate_store_fields.py` module is a structural addition to `struct:physics.layer2` not yet reflected in `docs/architecture/packets/physics.md`'s file listing — routine Cartographer doc-sync, not a defect.
- The stale `SYSTEMATIC_FLOOR` prose citation in `weekend_state/layer1_physics.py` (out-of-scope doc-drift, tc6) remains, as pre-flagged by the handoff.

**Workflow feedback addendum:** the checklist engine's `reopen` verb refused with `REFUSED: reopen applies to gated checklists` when invoked on this survey-type checklist — surveys have no built-in re-open mechanism for updating a single already-recorded item after new evidence arrives. Worked around it by `append`-ing a new sibling check (`r7-refix-verify`) to record the re-verification, then re-`record`-ing `r4-quality` directly (the engine allowed overwriting an already-recorded survey item) before re-`consolidate`. This worked but isn't a documented pattern in `checklist-engine.md` — worth adding a canonical "how to amend a survey verdict after a post-consolidation fix" recipe (append + re-record + re-consolidate) to the engine reference so future reviewers don't have to discover it by trial and error.

## Return status (updated)
complete
