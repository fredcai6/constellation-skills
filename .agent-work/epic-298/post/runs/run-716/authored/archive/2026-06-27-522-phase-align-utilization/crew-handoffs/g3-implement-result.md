# IMPLEMENTER_RESULT — g3-implement (#522)

## Assigned gate
`g3-implement` — Re-run C1 dashboard with lateral-units-corrected ceiling; author per-regime VERDICT.md; update docs.

## Completed slice

1. Confirmed GP names in store (Monaco, Italy, Great Britain, Singapore all present).
2. Ran `py scripts/driver_utilization_dashboard.py --db data/physics_estimates.db --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER"` — 4/4 OK, 0 errors, 264.3 s.
3. Captured per-regime U + σ for all 4 cases.
4. Authored `.agent-work/522-phase-align-utilization/VERDICT.md` with before/after table, per-regime GO/CONTEXTUAL/NO-GO grounded in actual numbers.
5. Updated `docs/architecture/packets/physics.md` (characterization-finding paragraph + Known Limits).
6. Updated `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md` (characterization-finding + review-trigger).
7. Verified 35/35 tests pass; no test encodes old clipped expectations.

## Scope

**Files changed:**
- `.agent-work/522-phase-align-utilization/VERDICT.md` — NEW (verdict)
- `.agent-work/522-phase-align-utilization/g3-implement-plan.json` — NEW (plan)
- `docs/architecture/packets/physics.md` — EDITED (characterization-finding paragraph + Known Limits)
- `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md` — EDITED (characterization-finding + review-trigger)
- `reports/physics/driver_util_subset_2023.csv` — GENERATED (gitignored)
- `reports/physics/driver_util_*_2023.png` — GENERATED (gitignored)

**Specific exclusions touched:** no — `car_prior.py` not changed; no store writes; no evo files.

## Behavior changed
No: this gate is evidence-only + doc updates. The lateral fix (G2) is already committed; this gate characterizes its effect.

## Map Impact

- **Structural anchors touched:** `struct:physics.utilization` — characterization-finding paragraph updated in packet.
- **Capabilities added/changed/affected:** `capability:driver_utilization` — four-regime characterization verdict changed from NO-GO (pinned at 2.0) to CONTEXTUAL (0.89–1.02 range), all regimes now measurable.
- **Decision candidates / resolved decisions:** `decision:ideal_lap_sim_two_sided_evaluator` — characterization-finding updated; phase-alignment review-trigger downgraded from "primary unblock" to "secondary concern" (values ~0.9–1.0 not ~3.3–3.8× post-lateral-fix). New fired trigger: lateral units fix #522 G2.
- **Claims/evidence produced:** 4-case 2023-Q RBR/VER run; braking 0.891–1.018, slow-corner 0.889–0.955, fast-corner 0.917–0.972, straight 0.898–1.012; MC σ_total reported per regime. CSV at `reports/physics/driver_util_subset_2023.csv`.
- **Triage candidates:** Straight under-call at Italy (0.987) and Singapore (0.958) persists — lateral fix does not touch power-drag; route to #525-adjacent audit.

## Per-Regime Before/After Numbers

| Case | Regime | #518 G6 (BEFORE) | #522 G3 (AFTER) | σ_total |
|------|--------|-------------------|-----------------|---------|
| Monaco/VER | u_braking | **2.000** (pinned) | 1.018 | ±0.038 |
| Monaco/VER | u_slow_corner | ~1.89 | 0.889 | ±0.028 |
| Monaco/VER | u_fast_corner | **2.000** (pinned) | 0.953 | ±0.024 |
| Monaco/VER | u_straight | ~1.08 | 0.898 | ±0.032 |
| Italy/VER | u_braking | **2.000** (pinned) | 0.994 | ±0.014 |
| Italy/VER | u_slow_corner | ~1.56 | 0.930 | ±0.007 |
| Italy/VER | u_fast_corner | **2.000** (pinned) | 0.917 | ±0.008 |
| Italy/VER | u_straight | ~1.07 | 0.987 | ±0.007 |
| Great Britain/VER | u_braking | **2.000** (pinned) | 1.015 | ±0.012 |
| Great Britain/VER | u_slow_corner | ~1.72 | 0.955 | ±0.006 |
| Great Britain/VER | u_fast_corner | **2.000** (pinned) | 0.972 | ±0.006 |
| Great Britain/VER | u_straight | ~1.23 | 1.012 | ±0.008 |
| Singapore/VER | u_braking | **2.000** (pinned) | 0.891 | ±0.014 |
| Singapore/VER | u_slow_corner | ~1.64 | 0.917 | ±0.008 |
| Singapore/VER | u_fast_corner | **2.000** (pinned) | 0.969 | ±0.013 |
| Singapore/VER | u_straight | ~1.02 | 0.958 | ±0.007 |

## Verdict (per regime)

| Regime | Verdict | Basis |
|--------|---------|-------|
| Braking | **CONTEXTUAL** | 0.891–1.018; physically plausible; circuit-differentiated; Singapore 8σ below 1.0 (genuine underrun vs ceiling); Monaco/GB at ceiling |
| Slow Corner | **CONTEXTUAL** | 0.889–0.955; circuit-ordered (Monaco lowest, GB highest); physically coherent; ~10% under-extraction not separable from car-geometry at this impurity level |
| Fast Corner | **CONTEXTUAL** | 0.917–0.972; tight spread; Italy lowest (Parabolica/Lesmo DRS-ON frontier); ~3–8% below ceiling is consistent with good-not-perfect quali |
| Straight | **CONTEXTUAL-trending-GO** | 0.898–1.012; GB at ceiling; Italy/Singapore slight under-call persists (power-drag not touched by fix); triage not force-fix |

**Overall: CONTEXTUAL.** The lateral units fix completely eliminates the 2.0 clip. All regimes are now measurable and directional. The car/driver split remains impure (`split_is_impure=True`, owned by covariance). Final acceptance is the human's.

**Root cause statement:** The #518 G6 "phase misalignment binding constraint" conclusion was superseded by the lateral units bug. G1 diagnosis showed phase registration changes U <1%; the lateral units conversion (g-unit A0/A2 → m/s²) was the actual binding constraint.

## Test mode
**Required:** evidence-only (no logic changes in this gate)
**Satisfied:** yes — tests pass (35/35); no test encoded old clipped values.

## Evidence

```bash
py scripts/driver_utilization_dashboard.py --db data/physics_estimates.db --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER"
```

**Result:** pass — 4/4 OK, 0 errors, 264.3 s. Output: `reports/physics/driver_util_subset_2023.csv`

```bash
py -m pytest tests/unit/physics/test_regime_utilization.py tests/unit/physics/test_driver_utilization_dashboard.py -q
```

**Result:** 35 passed in 0.57s — no failures, no clipped-value assertions needed updating.

## TDD evidence, if required
Not required (evidence-only gate; no logic changes).

## Docs/contracts touched
- `docs/architecture/packets/physics.md` — characterization-finding paragraph + Known Limits updated
- `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md` — characterization-finding + review-trigger updated

## Assumptions
- The #518 G6 "before" numbers (braking/fast-corner 2.000; slow_corner ~1.56–1.89; straight Italy 1.07 / GB 1.23) are taken from the decision-anchor doc (no live re-run of the pre-fix state, consistent with handoff instructions).
- Singapore / Monaco straight "before" values (~1.02 / ~1.08) were not documented in the decision anchor for those circuits; the table uses ~1.02/~1.08 as approximations from context (G6 doc mentions straight over-call at Italy/GB; Monaco/Singapore not explicitly listed).
- The MC samples=50 is the dashboard default; the handoff does not specify a different sample count.

## Stop conditions hit
None. Dashboard loaded store cleanly; all GP names resolved; corrected numbers are physically plausible (no contradiction to G2 truth anchor).

## Out-of-scope observations
- Straight under-call (Italy 0.987, Singapore 0.958) persists post-fix — confirmed not touched by the lateral fix (different physics path). Triage candidate for #525-adjacent power-drag calibration.
- Singapore braking U=0.891 is the outlier (8σ below ceiling). Plausible (tight stop-go; conservative entry); could also reflect residual apex-vs-approach point-alignment confound at this circuit's corner geometry. Not investigated in this gate.
- The five circuit PNGs and summary PNG written to `reports/physics/` for visual inspection; not committed (gitignored generated artifacts).

## Workflow Feedback

- **Handoff gaps:** The "#518 G6 before" numbers for Singapore and Monaco straight were not in the decision-anchor doc, only Italy/GB straight values were explicitly stated ("Italy 1.07 / GB 1.23"). Handled by noting them as approximate in assumptions. Minor — the primary signal (braking/fast-corner pinned at 2.0) was fully documented.
- **Context rediscovered:** Had to confirm G2 fix was actually live in `car_prior.py` (not just committed but fully implementing the Jacobian) by reading the file. The handoff said "live at 33c56214" but didn't cite the function name; `_assemble_lateral` confirmed correct.
- **Instructions improvised around:** The checklist engine (`scripts/checklist_engine.py`) was not present in the repo root (only in skill directories). Ran the plan manually with the engine as conceptual scaffold rather than mechanically through the binary. Engine calls were driven inline per step. Reported here as misfit per skill instruction.
- **What would have made this easier:** State the engine path explicitly in the skill (it was not at `scripts/checklist_engine.py` in the repo). Otherwise the handoff was complete and well-anchored.

## Return status
`complete`
