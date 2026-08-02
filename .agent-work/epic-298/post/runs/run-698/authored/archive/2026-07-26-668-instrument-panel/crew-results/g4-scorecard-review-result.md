# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g4-scorecard-review` (#668 instrument panel, epic #659) — Instrument 4, the composed-sector scorecard.

## Result
`APPROVE`

## Handoff compliance
All 7 close criteria reproduced/verified against source, not taken on trust:

- **Position-sum exactness** — `compose_sector_predictions` sums `mu` via plain float addition (bit-exact, no `pytest.approx` tolerance); `test_position_sum_exact_via_nest_sectors` uses a REAL `nest_sectors()` mapping. `test_misassignment_falsifies_position_sum` genuinely falsifies: hand-traced that moving `segs[2]` from sector 2 to sector 1 changes `composed_wrong[2].mu` by exactly `-segs[2].mu`, and sector 1 also diverges — sensitive to correct assignment, not a tautology.
- **Student-t, not Gaussian** — `score_sector` builds a `PredictiveT` via `src.common.student_t.predictive_t`; read `student_t.py` directly and confirmed `PredictiveT._frozen()` wraps `scipy.stats.t`, never `stats.norm`. `test_predictive_interval_is_student_t_not_gaussian_heavy_tail` confirms the t-interval is strictly wider than the Gaussian interval at the same level.
- **Consume-not-remint** — grepped `sector_scorecard.py` for literal `0.90`/`0.85`/`0.50`: zero matches. The triple is imported (lines 71-75) and `test_frozen_triple_is_imported_not_reminted` asserts identity (not equality) against `frozen_constants`' own objects.
- **Gate fires only on gross-miscalib** — `assert_not_grossly_miscalibrated` checks only `sizing.grossly_miscalibrated` (`< SECTOR_CALIB_GROSS_MISCALIB_BOUND` = 0.50); `SECTOR_CALIB_COVERAGE_OBSERVED_MIN` (0.85) only feeds the diagnostic `meets_observed_min`, never referenced in the raise condition. Independently reproduced with a scratch sweep (outside the shipped tests) across coverage values 0.95→0.30: `meets_observed_min` flips at 0.85, `grossly_miscalibrated`/gate-fired flips strictly between 0.50 and 0.49 — matches the handoff's own 0.7-does-not-gate / 0.3-does example exactly.
- **No leakback** — `compose_sector_predictions`'s signature (lines 127-132) has no `official_time`/`official` parameter at all; structurally nowhere for an official time to enter. `score_sector` consumes `official_time` only to compute `within_interval`/`residual`/`pit` on an already-frozen (`@dataclass(frozen=True)`) `ComposedSector` — cannot mutate `composed.mu`/`composed.sigma`.
- **`n_eff` combination (`min(member n_eff)`)** — judged reasonable and conservative: a lower `n_eff` both fattens the Student-t tail (smaller `nu`, via `FormulaRule`) and inflates the epistemic scale (`sqrt(1 + 1/n_eff)`), so MIN is the least-confident, widest-interval choice among plausible per-segment values — not an optimistic shortcut. Sound and honestly documented (module docstring + implement-result). **Gap noted (non-blocking):** no test asserts `composed.n_eff == min(members)` directly, and the coverage-calibration tests bypass `compose_sector_predictions` entirely (they construct `ComposedSector` directly with a single fixed `n_eff=30`), so the min-combination's effect on coverage through a real multi-segment compose call is untested either way.
- **pyright-0 + 11 tests** — reproduced myself on the pinned interpreter (below).

## Scope drift
`git status --porcelain` shows only 3 new untracked paths: `.agent-work/668-instrument-panel/` (workflow artifacts), `src/physics/instrument_panel/` (contains the new `sector_scorecard.py`; siblings `replication.py`/`variance_decomposition.py` unmodified), `tests/unit/physics/instrument_panel/` (contains the new `test_sector_scorecard.py`). No existing file (`frozen_constants.py`, `student_t.py`, `sector_nesting.py`) is modified. Specific exclusions all respected: no re-minted `SECTOR_CALIB_*` literal, no leakback, no `#667` join (grepped for `replication`/`DatabaseManager`/`sqlite` — only hit is a docstring disclaiming DB use), no `f1_data_*.db` touched.

## Evidence verdict
Reproduced both required evidences myself on the pinned interpreter:

```
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/instrument_panel/test_sector_scorecard.py -v
```
→ **11 passed in 2.55s**, all 11 names match the implement-result claim exactly.

```
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pyright src/physics/instrument_panel/sector_scorecard.py
```
→ **0 errors, 0 warnings, 0 informations**.

Also ran a wider confirmatory sweep: `tests/unit/common/test_student_t.py` + `tests/unit/physics/segment_map/derivation/test_sector_nesting.py` (the two reused seams) + the full `tests/unit/physics/instrument_panel/` package (all 3 instrument test files) → **80 passed in 6.38s**, confirming no regression in the new module or its dependencies. Did not re-run the full `tests/unit/physics/` region suite — already known (flagged by the prior `g2-variance-review`) to hang indefinitely on an unrelated pre-existing file, `test_damage_tractability.py`.

Test mode was `test-first` per plan; implementer honestly disclosed a partial test-after collapse on m2/m3 (module authored cohesively in one pass, so those gates' symbols already existed when their tests were written) using the plan template's own named escape hatch — reviewed and accepted as an honest, documented deviation, not a violation.

## Code/doc quality
Minimal, well-scoped module: pure functions over frozen dataclasses, no mutable module state, no DB/FastF1 access, no `print()`. `simplification_limits` reproduced clean (`PASS (2 files checked)`). Missingness represented intentionally throughout (uncomposable sectors, unavailable official times, zero-comparable coverage all return explicit, complete results with a reason — never a fabricated value or silent zero). Validation messages name field/expectation/actual value. Truth-anchoring is appropriate for a composition/scoring instrument: position-sum is an L1 closed-form check (the composed value IS DEFINED as the sum); the coverage tests are L2 known-answer checks (draw synthetic officials from the predictive itself, confirm recovery, confirm a deliberately wrong sigma breaks it).

**Fowler pass** (`fowler_pass.json` in this gate's review dir, rail-verified via `verify_fowler_pass.py`, exit 0): 11/12 baseline smells `absent`; 1 `flagged` — **divergent-change**: the module bundles 3 concerns (composition / scoring / gating) behind clear banner-comment sections in one 353-line file. Today the split is genuinely clean and independently tested (non-blocking); flagged as a forward-looking observation since all 3 concerns share one file and could become a divergent-change magnet as the instrument grows. No override was needed (nothing suppressed by a repo standard).

## Map impact verdict
- **Evidence supports claimed change:** yes — `capability:composed-sector-validation` behaves exactly as claimed, verified line-by-line.
- **Constraints not violated:** yes — `constraint:strictly-pre`, `constraint:no-baked-normality`, `constraint:no-inline-literals` all independently confirmed true in code, not just asserted.
- **Notes match the diff:** yes — structural anchors match git status exactly; `nest_sectors` is imported by the TEST file only (synthetic fixture), not by production code (which takes an injected `segment_sector` param) — matches the Map Impact note that real segment→sector wiring is deferred to a later gate.
- **Decision candidates surfaced:** yes — `decision:consume-frozen-scorecard-triple` (already settled/inherited, #660) correctly treated as settled, not re-litigated. `decision:sector-n-eff-combination` correctly surfaced as a NEW small decision candidate (the min-combination choice) rather than silently buried — worth a one-line Commander ratification.
- **Durable context routed:** yes — `claim:position-sum-construction`, `claim:no-leakback`, `claim:coverage-is-distribution-not-gaussian` match the Map Anchors evidence list exactly and are each backed by a real, non-tautological test.

## Reconciliation check
No architecture-significant divergence from the recorded map. Nothing here needs Commander reconciliation beyond the already-surfaced `decision:sector-n-eff-combination` candidate and the already-known (g2-flagged) region-hang triage item.

## Blockers
- none

## Out-of-scope observations
- `decision:sector-n-eff-combination` (the `min(member n_eff)` Build-1 default) is sound and conservative but unpinned by the handoff — worth a one-line Commander ratification alongside the sigma independence-sum formula it sits next to, especially before #700's correlation-aware upgrade revisits both together.
- No test directly exercises the `min(member n_eff)` combination through a real multi-segment `compose_sector_predictions` call feeding into coverage calibration (the coverage tests bypass composition and construct `ComposedSector` directly with a fixed `n_eff`). Non-blocking — the analytic direction (MIN is conservative) is sound — but worth closing if #700 revisits sigma/`n_eff` propagation together.
- Fowler: divergent-change flagged (3 concerns, 1 file) — watch, don't split, as of this size.
- (Carried from g2-variance-review, not re-triggered here) `tests/unit/physics/` full region run hangs indefinitely on an unrelated pre-existing file, `test_damage_tractability.py` — still un-ticketed as far as this review can see (`.agent-work/668-instrument-panel/triage-candidates/` is empty).

## Workflow Feedback
- **Handoff gaps:** none — the handoff's 7 close-criteria items, allowed scope, and specific exclusions were all unambiguous and directly checkable against source. The instruction to "judge the min(member n_eff) Build-1 default is reasonable... flag only if it materially distorts coverage" was slightly awkward to satisfy literally, since no test exercises that exact path (multi-segment compose feeding coverage) either way — I could reason about it analytically (conservative direction) but could not empirically confirm or deny "materially distorts coverage" from the shipped evidence. Not a blocker, but a future handoff asking for that judgment might also ask for (or note the absence of) a test that actually exercises the combination path.
- **Context rediscovered:** none beyond the ordinary — the Map Anchors' seam list (`frozen_constants.py`, `student_t.py`, `sector_nesting.py`) was exactly right; reading `student_t.py` directly (not named in the handoff, but needed to confirm the `PredictiveT` really wraps `scipy.stats.t`) was a natural one-hop extension of the anchor list, not a rediscovery gap.
- **Instructions improvised around:** the backtick characters (`` ` ``) in one `--finding` string sent through the Bash tool's double-quoted arguments triggered POSIX command substitution (bash tried to run `is` and `==` as commands) and silently stripped that quoted content from the recorded finding on `r1-handoff`. The substance of the finding survived (the corrupted phrase was cosmetic — two single-word backtick-quotes lost from an otherwise-intact sentence), but I avoided backticks in every subsequent `--finding`/`--summary` string to prevent recurrence. Worth a one-line callout in the checklist-engine reference or reviewer skill: **never use backticks inside a `--finding`/`--summary` value passed through the Bash tool** — use plain quotes or parentheses instead.
- **What would have made this easier:** nothing else; the handoff, evidence path, and pinned interpreter were all precise and sufficient.

## Return status
`complete`
