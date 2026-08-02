# Review Result — G3 (held-out driver-utility gate harness)

verdict: APPROVE

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3-review` — #628 Phase 3b, the LOAD-BEARING falsifiable gate. Worktree `C:/Programs/f1-628`.
Files under review (both NEW/untracked):
- `src/physics/utilization/driver_utility_gate.py`
- `tests/unit/physics/test_driver_utility_gate.py`

## Result
`APPROVE`

The gate cannot be gamed. Every load-bearing property the handoff flagged was RE-RUN and independently
reproduced by the reviewer (not trusted from the tests). Survey driven through the engine, all 7 items pass,
consolidated APPROVE (0 fail findings). One MINOR non-blocking duplicated-code observation for Commander.

## Re-run evidence (reviewer-reproduced)

```
$ py -m pytest tests/unit/physics/test_driver_utility_gate.py -q
13 passed in 1.84s

$ py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility_gate.py
PASS (1 files checked)

$ grep -nE "/ ?v_ideal|observed ?/ ?cap" src/physics/utilization/driver_utility_gate.py || echo NO-RATIO-OK
NO-RATIO-OK

$ py C:/Users/.../scripts/verify_fowler_pass.py .../g3-fowler-pass.json
fowler pass ok (smells=12, flagged=['duplicated-code'], overridden=['primitive-obsession'])  EXIT=0
```

Independently reproduced numeric claims (via the test helpers, reviewer-driven):

```
# Powered leakage self-test (causal alpha=1 vs non-causal alpha=0.05)
seed= 11 leak_min=0.554 null_max=0.0000
seed=  1 leak_min=0.558 null_max=0.0000
seed=  2 leak_min=0.421 null_max=0.0000
seed=  3 leak_min=0.733 null_max=0.0000
seed= 42 leak_min=0.356 null_max=0.0000
seed=  7 leak_min=0.626 null_max=0.0000
pre-committed threshold = 0.15   (leak min across seeds = 0.356, a 2.4x margin; null identically 0.0)

# Honest-null reachable (zero true driver signal)
HONEST-NULL verdict = honest_null; corner improvements {braking:-0.018, slow:-0.284, fast:-0.218}  (spurious fit HURTS OOS)

# Straight = confounded negative control cannot reach the verdict
STRAIGHT-ONLY signal -> straight limb-1 improvement 2.031, confounded_negative_control=True,
                        yet run_gate verdict = honest_null

# Disjointness enforced
recomposition_limb(rows, train=(1,2,3), held=(3,4)) -> ValueError "train_rounds and heldout_rounds must be disjoint"

# Centering (pure car offset, zero driver spread)
per_axis_structure_limb -> centered_cross_driver_variance = 0.0 on every corner axis
```

## Handoff compliance
All close criteria satisfied and re-verified:

- **Out-of-sample discipline (load-bearing) — CONFIRMED by reading the code, not just tests.**
  `recomposition_limb` (driver_utility_gate.py:198) calls `_split_train_heldout` (:86), which asserts
  `train_set & held_set` is empty and raises `ValueError` on any overlap (:98-102) — reproduced. `_fit_train_delta`
  (:108) runs `estimate_driver_utility` on the **train frame only** and returns the `{(driver,axis): delta}` map;
  `_axis_recomposition` (:116) scores each held row with `delta_map.get((d, axis), 0.0)`. A driver's held-out
  round-4 session therefore never enters its own rounds-1..3 δ fit — proper leave-round-out, honoring the
  `loo-residual-diagnostic` lesson (no self-inclusive prediction). Limb 2 (`per_axis_structure_limb`, :184) also
  reads only the TRAIN fit. `run_gate` (:246) fits δ on TRAIN, scores limb 1 on the disjoint held rounds.

- **Straight/power axis = confounded negative control that CANNOT reach the verdict — CONFIRMED.**
  `STRAIGHT_AXIS="straight"` is in `CONFOUNDED_NEGATIVE_CONTROL_AXES` and NOT in `CORNER_AXES` (:59-63).
  `_corner_verdict` (:229) iterates `[r for r in recomp.values() if r.is_corner_axis]` — the straight row's
  `is_corner_axis` is False, so it is structurally excluded from every verdict branch. Reproduced with a
  straight-only fixture: straight limb-1 improvement 2.03 (huge) yet verdict `honest_null`. A straight "pass"
  can never count.

- **Powered leakage self-test — CONFIRMED genuinely powered and specific.**
  `PRE_COMMITTED_INFLATION_MS = 0.15` is set before any number is observed (test:221). The causal (alpha=1,
  strictly_pre) vs non-causal (alpha=0.05, through-W) contrast on a **16-driver / 8-constructor** high-leverage
  roster inflates the OOS replication metric by 0.554 min at seed 11 — a 3.7x margin — and 0.356–0.733 across 6
  seeds, so the pass is not seed-cherry-picked. The null-construction companion (alpha_causal=alpha_noncausal=1.0)
  is a *structural* zero (byte-identical frames -> inflation identically 0.0 every seed), proving specificity.
  The assert message encodes "null inflation => causal apparatus IMMATERIAL-or-UNDERPOWERED, NEVER a silent pass."
  The implementer's widening after the 4-driver TDD-red is justified: rms(eps) over few held points is too noisy;
  16 drivers stabilizes it.

- **Honest-null reachable — CONFIRMED.** A zero-driver-signal synthetic yields NO corner improvement: verdict
  `honest_null`, corner improvements slightly negative (a δ fit on pure noise HURTS out-of-sample — the true
  no-signal signature). The rubric does not guarantee a pass; `honest_null` is a first-class returnable verdict
  with no kill switch and nothing tuned toward a pass (`_corner_verdict` :229, `MIN_CORNER_IMPROVEMENT_MS`=0.01).

- **Limb-2 centering — CONFIRMED.** `_axis_structure` (:158) computes `centered = delta - mean_over_drivers(delta)`;
  a pure shared car offset gives ~0 centered variance on every axis (reproduced = 0.0). Documented honestly as
  interpretive (variance is translation-invariant; centering *licenses* reading the spread as driver signal).

## Scope drift
Clean. Only the two allowed new files, both untracked. G1/G2 untouched — `estimate_driver_utility` is imported
read-only and its single-DataFrame signature matches `driver_utility.py:130`. No real batch / FastF1 / telemetry
(synthetic rows only). No `observed/capability` ratio (grep NO-RATIO-OK). No kill switch. Nothing staged or
committed. Specific exclusions all respected.

## Evidence verdict
Required evidence present, reproducible, and genuinely demonstrative. TDD red→green→refactor honored, including a
*meaningful* m4 red (underpowered 4-driver roster -> min inflation 0.045 < 0.15) fixed by widening TEST POWER, not
by moving the pre-committed threshold or touching production code — verified by the seed sweep above. Tests are
behavior-focused (falsifiability properties), not implementation-coupled.

## Code/doc quality
Minimal, well-factored, self-documenting. Small frozen dataclasses as value objects; short single-purpose helpers;
fails visibly (disjoint overlap and missing required columns raise with named fields); no hidden fallback (an
unresolved driver falls back to δ=0 == car-only baseline, documented, earns no artificial limb-1 credit);
missingness intentional (G2 resolved/unresolved status). Docstrings state the falsifiability contract, the
negative-control framing, and the named cross-round-leak limit honestly.

Fowler pass: 12 baseline smells rendered; verify_fowler_pass.py exit 0.
- **flagged (MINOR, non-blocking):** duplicated-code — `_fit_train_delta` (:108) and `_resolved_delta_frame`
  (:152) both refit `estimate_driver_utility(train_rows)` and apply the identical resolved-filter predicate, so
  `run_gate` fits G2 twice on the same train frame (once per limb) and splits twice. Correct but a small
  refit/filter duplication that could be factored. Out-of-scope observation for Commander, below.
- **overridden:** primitive-obsession — string axes + float deltas are the documented numeric house style
  matching the G1/G2 schema; wrapping them would diverge from surrounding code. Logged standard + reason in the
  Fowler record.

## Map impact verdict
- **Evidence supports claimed change:** yes — the produced synthetic evidence (OOS recovery when signal exists,
  honest-null when zero, centering removes car offset, powered leakage self-test) backs the claimed falsifiable
  held-out gate capability.
- **Constraints not violated:** yes — OOS discipline enforced structurally (disjoint assert, TRAIN-only fit); the
  straight negative control is excluded from the verdict; centered variance is the limb-2 signal.
- **Notes match the diff:** yes — new `driver_utility_gate.py` under `struct:physics.utilization`, G2 reused by
  import with no modification, confirmed against the diff.
- **Decision candidates surfaced:** N/A — no authority-requiring decision arose; `decision:c1_driver_utilization_design`
  correctly cited, cross-round leak named as an attenuated (not eliminated) limit.
- **Durable context routed:** yes — the one out-of-scope observation is captured below for Commander; no dropped
  context.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconcile. Self-contained new module reusing the G2
estimator by import.

## Blockers
- none — confirmed after full re-run: OOS discipline holds, straight axis cannot reach the verdict, the leakage
  self-test is powered and specific, and honest-null is reachable.

## Out-of-scope observations
- MINOR (Triage candidate): `run_gate` refits `estimate_driver_utility` twice on the same TRAIN frame (via
  `_fit_train_delta` and `_resolved_delta_frame`) and re-splits twice; the resolved-filter predicate is duplicated
  in both helpers. A small factoring (fit once, share the resolved frame) would remove the duplication and the
  double G2 call. Non-blocking on a synthetic-only harness; matters more once wired to a real batch (G5).

## Workflow Feedback
- **Handoff gaps:** The handoff did not name the survey-state location field (`Survey State Location`) that the
  reviewer skill says it provides; I followed the skill's canonical `.agent-work/<work-id>/<gate>-review/review.json`.
  Prior gates in this epic instead used a flat `.agent-work/<work-id>/g{1,2}-review-survey.json` — a minor
  inconsistency worth pinning in the handoff so review artifacts land in one predictable place.
- **Context rediscovered:** none material — the handoff's four focus points mapped cleanly onto specific code
  lines and test fixtures; I re-derived the leak/null seed sweep myself to test power beyond the single seed the
  implementer reported, which the handoff explicitly asked for.
- **Instructions improvised around:** `checklist_engine.py current` rejects `--session-id` (read-only verb); I ran
  it without the flag. Minor, engine-doc already implies read-only needs no session — no change needed.
- **What would have made this easier:** none — confirmed after review: the handoff's pre-committed magnitude,
  power caveat, and the four falsifiability checks were precise enough to verify directly; the only additive value
  was the multi-seed power sweep, which the handoff already invited.

## Return status
`complete`
