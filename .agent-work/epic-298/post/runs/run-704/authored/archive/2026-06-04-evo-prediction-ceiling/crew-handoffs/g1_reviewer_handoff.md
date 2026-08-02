# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g1` — offline evidence harness (significance + coverage). Measurement only.

## What Was Implemented
A torch-free analysis harness `.agent-work/evo-prediction-ceiling/evidence/sigma_significance_probe.py`
that reads `reports/evo/gold_cycle_260603_173742_2018thru2024.details.json` and reports
(a) per-module `sigma_corr` significance at n=24 (point, bootstrap + Fisher-z 95% CI,
p-value, verdict, and `r_crit(n=24,alpha=0.05)`), and (b) per-phase calibrated-sigma
level/flatness with a race-start mis-level-vs-coverage-aligned verdict. Also writes
`g1_evidence.json`. No src/tests/docs changed.

## How to Inspect the Diff
- `git status --porcelain` — expect ONLY untracked `.agent-work/evo-prediction-ceiling/`.
- Read `.agent-work/evo-prediction-ceiling/evidence/sigma_significance_probe.py`.
- Re-run: `py .agent-work/evo-prediction-ceiling/evidence/sigma_significance_probe.py`
  and `py .agent-work/evo-prediction-ceiling/evidence/sigma_significance_probe.py --selftest`.

## Task Statement
Measure, statistically honestly: (a) whether the race-start `sigma_corr` values
(−0.119/−0.092/+0.108/+0.206) are distinguishable from 0 at n=24, and produce the
n-aware `r_crit(n)` threshold for G2; (b) whether race-start calibrated-sigma is
mis-leveled (too high/too flat) vs quali/race, or already coverage-aligned. A
"coverage-aligned / no mis-level" verdict is a valid expected outcome.

## Close Criteria (each becomes a review check)
- Harness re-runs to exit 0 and is deterministic (two runs byte-identical).
- `r_crit(n=24, alpha=0.05)` is CORRECT — independently recompute: t_crit(df=22,0.975)=2.0739,
  r_crit = t_crit/sqrt(22+t_crit^2) ≈ 0.4044. Confirm the harness prints ≈0.404.
- The four race-start `sigma_corr` point estimates MATCH the engine's embedded
  `corr_sigma_pi_trace_vs_rank_mae` in details.json (spot-check at least one).
- The 95% CIs are methodologically sound (bootstrap percentile AND Fisher-z) and
  agree; the "indistinguishable-from-0" verdict for all 4 race-start modules follows
  (every CI spans 0, every p>0.3).
- The level verdict ("coverage-aligned") is DEFENSIBLE and ROBUST to the
  `entity_count=None` fallback. Scrutinize: does collapsing effective_dof to 1
  invalidate the "not too high / not too flat" conclusion? The implementer judged
  flatness on CV(raw sigma) to be fallback-independent — confirm that reasoning, and
  confirm the significance result (part a) independently supports "no signal to
  re-level toward" regardless of the level analysis.
- Scope clean: no src/tests/docs touched.

## Allowed Scope (what implementation was permitted to touch)
Files only under `.agent-work/evo-prediction-ceiling/evidence/`. Read-only on reports.

## Specific Exclusions (flag if touched)
Any change to `src/`, `tests/`, `docs/`; torch; new pip deps; DB/live calls.

## Constraints the Implementation Must Respect (each a review check)
- `py` for python.
- Statistically defensible small-n correlation CI (bootstrap + Fisher-z).
- Deterministic (seeded bootstrap).
- No new dependencies (graceful stdlib fallback).

## Evidence Produced
r_crit(n=24)=0.4044; race-start: all 4 indistinguishable-from-0 (p 0.34–0.91, CIs
span 0); 5/12 modules significant overall, 0/4 race-start; pearson matches engine
<1e-6; level verdict coverage-aligned (calSig/err ratio 0.7515 vs 0.6325 ref = +19%,
under 25% materiality; CV(raw sigma) race_start 0.220 ≈ ref 0.231). Selftest PASS;
two runs byte-identical; git status clean of src/tests/docs.

## Suggested Model Tier
stronger — reason: the verdict is pivotal (it collapses G3) and the value is
statistical-methodology correctness; review must be independent and rigorous.

## Stop Conditions
Return BLOCK if: the harness does not re-run clean, r_crit or the CIs are wrong, the
pearson values do not match the engine, the level verdict is not supported by the
numbers, or any src/tests/docs were touched.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings (with your
independent r_crit recompute and a pearson spot-check), blockers, out-of-scope
observations.
