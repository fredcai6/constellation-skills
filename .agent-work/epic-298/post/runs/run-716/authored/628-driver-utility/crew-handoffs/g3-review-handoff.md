# Reviewer Handoff — G3 (held-out gate harness)

## Gate
`g3-review` — the LOAD-BEARING falsifiable gate. Worktree **C:/Programs/f1-628** only.

## What was implemented
- `src/physics/utilization/driver_utility_gate.py` — held-out gate harness: fits δ on TRAIN via G2, evaluates
  OOS on HELD-OUT: limb-1 recomposition (RMSE_model vs δ=0 baseline per axis), limb-2 per-axis structure
  (cross-driver variance of CENTERED δ), straight/power = labeled confounded negative control (excluded from
  verdict), powered leakage self-test, non-gating reputational read, honest-null first-class.
- `tests/unit/physics/test_driver_utility_gate.py` — 13 tests.
- Result: `.agent-work/628-driver-utility/crew-results/g3-implement-result.md`.

## Task being verified
The falsifiability itself. Re-run the numbers and confirm the gate cannot be gamed.

## Close criteria (verify each, RE-RUN numbers)
- `py -m pytest tests/unit/physics/test_driver_utility_gate.py -q` → all pass (13).
- **Out-of-sample discipline (load-bearing):** confirm δ is fit ONLY on TRAIN rounds and a driver's held-out
  sessions never enter their own δ (train/held-out disjoint, asserted). No self-inclusive prediction anywhere
  (the `loo-residual-diagnostic` lesson). CONFIRM by reading the split + fit code, not just the tests.
- **Limb 2 centering:** cross-driver variance uses the per-axis-CENTERED δ; a pure shared car-offset with zero
  driver spread → ≈0 centered variance (there is a test — re-run it).
- **Straight = confounded negative control:** confirm the straight axis is labeled and CANNOT reach the
  verdict; a straight-axis "pass" must not count (there is a dedicated test — re-run it).
- **Powered leakage self-test:** confirm the non-causal ceiling inflates OOS replication vs causal by the
  pre-committed magnitude on a high-leverage roster, AND a null-construction companion gives ≈0 (specificity),
  AND the assert message encodes "null inflation ⇒ immaterial-OR-underpowered, never a silent pass." Verify the
  roster is large enough that the reported inflation isn't just rms-noise (the implementer widened it after a
  genuine TDD-red — sanity-check the power).
- **Honest-null reachable:** confirm a synthetic case with ZERO true driver signal yields NO limb-1 corner
  improvement (honest-null), i.e. the rubric does not guarantee a pass.
- `simplification_limits --paths` PASS; grep → NO-RATIO-OK.

## Allowed scope / exclusions
Review only the two new files + result. Do not review G1/G2. Out-of-scope finds → triage candidates.

## Map anchors (inbound)
Inherits g3-implement anchors — OOS + centered variance + confounded-negative-control + powered leakage
self-test + honest-null-reachable are the load-bearing review checks.

## Required evidence
Paste the pytest re-run, simplification-limits, grep, and cite the code lines proving (a) train/held-out
disjointness, (b) straight-axis verdict exclusion, (c) the leakage self-test's pre-committed magnitude + power.

## Verification commands
```bash
cd /c/Programs/f1-628 && py -m pytest tests/unit/physics/test_driver_utility_gate.py -q
cd /c/Programs/f1-628 && py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility_gate.py
cd /c/Programs/f1-628 && grep -nE "/ ?v_ideal|observed ?/ ?cap" src/physics/utilization/driver_utility_gate.py || echo NO-RATIO-OK
```

## Return format
REVIEW_RESULT with explicit `verdict: APPROVE` or `verdict: BLOCK`, re-run evidence, severity-ranked findings,
workflow feedback. BLOCK if OOS discipline is violated, a straight-axis pass can reach the verdict, the leakage
self-test is underpowered/silently-passing, or honest-null is unreachable.
