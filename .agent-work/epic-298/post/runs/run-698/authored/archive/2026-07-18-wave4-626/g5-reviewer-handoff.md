# Reviewer Handoff

## Gate
`g5` — F6 held-out gate + writeup. VERDICT emitted = PASS (9/11). Your job: scrutinize the PASS HARDEST of all — this is exactly where a fake win would hide. An honest PASS must survive an adversarial read; if it doesn't, BLOCK.

## Survey State Location
`.agent-work/wave4-626/g5-review/review.json`.

## What Was Implemented
`src/physics/weekend_state/gate_f6.py` (imports frozen g1 `gate_spec`; fits `WeekendStateModel` on TRAIN only; scores held-out car-signal vs the PAIRED held-out floor through the signal-preservation guard; per-axis tc1 coverage floor ≥5 car-seasons; leave-one-layer-out ablation; emits verdict + JSON) + `test_gate_f6.py` (13 tests, does NOT require PASS) + `docs/physics/626-phase2-weekend-state-model.md` + `docs/physics/626-f6-holdout-gate.json`. Verdict: PASS, 9/11 covered axis-beats, median convergence ratio 0.40. Ablation: −L4→0 beats, −L3→2, −L1 Δ0, −L2 Δ0 (g3 FLOAT confirmed). Caveat: only 30% of car-season-axis instances preserve accuracy. Result: `.agent-work/wave4-626/g5-implementer-result.md`.

## How to Inspect the Diff
UNCOMMITTED tree; `git status --porcelain` then read `gate_f6.py`, the test, and both `docs/physics/626-*` files directly.

## Task Statement
Build the F6 held-out gate + writeup, emit an honest verdict. Full task: `.agent-work/wave4-626/g5-implementer-handoff.md`.

## Close Criteria (each a review check — scrutinize the PASS)
- **Frozen rule, not re-tuned:** `gate_f6.py` IMPORTS g1 `gate_spec` constants/functions and does NOT re-derive or re-tune the decision rule. Confirm nothing was adjusted after seeing held-out numbers.
- **No leakage:** model fit on TRAIN weekends only; held-out car-signal from train-only hyperparameters. Confirm the split is the g1 frozen `holdout.py` and the model isn't refit on held-out.
- **[F2] Paired floor:** the floor is recomputed on the IDENTICAL held-out weekends (per car-season), NOT the 624 full-sample table. Verify this is what the "beat" compares against.
- **[F1] Signal-preservation guard applied:** the PASS requires faster convergence AND preserved held-out accuracy. Confirm the guard is actually gating the beats — the −L3 ablation dropping to 2 beats (over-shrinker rejected) is evidence it works; verify.
- **[tc1] Coverage floor:** an axis-beat needs ≥5 held-out car-seasons; thin-coverage axes cannot pad the tally. Confirm.
- **[F4] Ablation honest:** −L2 Δ0 (confirms g3 FLOAT), reported not hidden. Confirm the ablation is real (re-runs the gate with each layer removed).
- **Honesty of the verdict + caveat:** the 30%-accuracy-preservation caveat and the per-axis nulls (max_power 3/80, coast 0/81) are surfaced prominently in the writeup, NOT buried. A PASS that hides that only 30% of instances preserve accuracy would be misleading — verify the writeup represents this fairly.
- Re-run `test_gate_f6.py` (13 pass); confirm the test does NOT require PASS.
- Docs under `docs/physics/` (not gitignored `reports/`); no evo import; no `data/*.db` staged.

## Allowed Scope
`gate_f6.py`, its test, the two `docs/physics/626-*` files.

## Specific Exclusions
g1-g4 modules/gate_spec/estimator/evo/config untouched. (DBs outside worktree — Commander-verified.)

## Constraints the Implementation Must Respect
Re-run x4's own metric (not a new one); no-leakage; frozen rule not re-tuned; `constraint:physics_region_no_evo_import`; docs in docs/physics; no data/*.db commit.

## Map Anchors (inbound)
- Structural: `gate_f6.py` + `docs/physics/626-*` (NEW); imports g1 gate_spec/floor/holdout + g4 model.
- Capability: F6 held-out gate vs x4 floor, verdict either way.
- Decision: ≥7/11 outside noise + tc1 coverage floor.
- Evidence: per-axis held-out table + ablation + density secondary.

## Evidence Produced
`py -m pytest tests/unit/physics/weekend_state/test_gate_f6.py -q` → 13 passed (commander re-ran: 13 passed, ~26s). Verdict JSON: `docs/physics/626-f6-holdout-gate.json` (verdict=PASS). Full table + ablation in the implementer result.

## Suggested Model Tier
Stronger — adversarial scrutiny of a PASS verdict; the whole run's credibility rests on this PASS being real, not massaged.

## Stop Conditions
BLOCK if: the decision rule was re-tuned post-hoc, the floor is NOT the paired held-out floor, there is leakage, the coverage floor isn't applied, the ablation is faked, or the writeup buries the accuracy-preservation caveat so the PASS reads as stronger than it is.

## Return Format
Return REVIEW_RESULT to `.agent-work/wave4-626/g5-reviewer-result.md`: verdict (APPROVE = the PASS is honest and survives scrutiny / BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
