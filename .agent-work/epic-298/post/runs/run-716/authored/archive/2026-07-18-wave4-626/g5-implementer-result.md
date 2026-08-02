# Implementation Result — g5 (F6 held-out gate + writeup)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g5` — the F6 HELD-OUT gate harness + Phase-2 writeup. The culminating
deliverable: run the frozen metric on the four-layer model's held-out output,
produce an HONEST verdict, document everything.

## Completed slice
`gate_f6.py` built + run; test green; writeup + machine-readable JSON authored.
The harness IMPORTS the frozen g1 `gate_spec` (does not re-derive it), fits
`WeekendStateModel` on TRAIN weekends only, scores the held-out car-signal
against the paired held-out raw floor [F2] through the signal-preservation
guard [F1], applies a per-axis tc1 coverage floor (≥5 held-out car-seasons),
runs a leave-one-layer-out ablation [F4], and emits the verdict.

**VERDICT: PASS — 9 / 11 covered axis-beats (threshold ≥7). Honest and
untuned.** The frozen-rule count (pre-coverage-floor) is also 9; median
convergence ratio 0.40.

## Scope
**Files changed (all NEW):**
- `src/physics/weekend_state/gate_f6.py`
- `tests/unit/physics/weekend_state/test_gate_f6.py`
- `docs/physics/626-phase2-weekend-state-model.md`
- `docs/physics/626-f6-holdout-gate.json`
- `.agent-work/wave4-626/g5-implementer-plan.json` + this result (workflow artifacts)

**Specific exclusions touched:** no. Did NOT modify g1–g4 modules, `gate_spec`'s
frozen rule, the estimator, evo, or config; did NOT commit/modify `data/*.db`
(verified: no db in git status; docs under `docs/physics/`, all four
deliverables `git check-ignore` = tracked-ok).

## Behavior changed
Yes — adds the F6 held-out gate harness (new capability). No existing behavior
altered; imports the frozen rule and the g4 model, composes only.

## Test mode
**Required:** test-after (handoff). **Satisfied:** yes — `test_gate_f6.py`
asserts the harness runs end-to-end and emits a verdict (PASS *or*
DID-NOT-BEAT-FLOOR) with per-axis table + ablation, and **does NOT require
PASS** (`test_emits_a_valid_verdict_either_way` accepts both; the verdict-branch
test checks the covered-beats-vs-threshold relationship in whichever branch the
run lands).

## Evidence
```bash
cd C:/Programs/f1-626
py -m src.physics.weekend_state.gate_f6              # writes the JSON, prints the table
py -m pytest tests/unit/physics/weekend_state/test_gate_f6.py -q
```
**Result:** harness runs foreground in ~32s over 1,562 rows (train 1,061 /
held-out 501); `13 passed in 25.42s`. Bootstrap left at the FROZEN
N=2000/seed=626001 (fast enough — no cap needed).

## FULL per-axis held-out table (model σ vs paired floor σ; ratio<1 = faster convergence)

| axis | floor σ | model σ | ratio | coverage | boot lower-q | beat (frozen) | counts (tc1 ≥5) |
|---|---|---|---|---|---|---|---|
| drag_area_closed_m2 | 0.0852 | 0.0433 | 0.508 | 17 | 0.0293 | yes | yes |
| brake_decel_ms2 | 5.459 | 2.333 | 0.427 | 19 | 2.174 | yes | yes |
| brake_aero_decel_per_m | 0.00130 | 0.00022 | 0.168 | 51 | 0.00082 | yes | yes |
| traction_accel_ms2 | 0.820 | 0.252 | 0.307 | 14 | 0.494 | yes | yes |
| traction_aero_accel_per_m | 0.00121 | 0.00003 | 0.029 | 78 | 0.00098 | yes | yes |
| max_power_w | 13063 | 5021 | 0.384 | **3** | −1148 | no | no (thin + within noise) |
| power_drag_area_m2 | 0.0852 | 0.0433 | 0.508 | 17 | 0.0293 | yes | yes |
| lateral_mech_grip_g | 0.293 | 0.146 | 0.499 | 32 | 0.1395 | yes | yes |
| lateral_aero_grip_g | 0.000129 | ~0 | 0.000 | 22 | 0.0001 | yes | yes |
| coast_rolling_decel_ms2 | 0.1505 | 0.0625 | 0.415 | 15 | 0.0575 | yes | yes |
| coast_drag_area_m2 | — | — | — | **0** | — | no | no (0 guard-pass) |

**Covered beats: 9/11 ≥ 7 → PASS.** The two non-beats are honest per-axis nulls:
`max_power_w` (only 3/80 car-seasons preserve accuracy — below the tc1 floor —
and the bootstrap lower quantile is negative) and `coast_drag_area_m2` (0/81
guard-pass; the model over-shrinks it on every car-season).

## Accuracy preservation ([F1] half of PASS)
Overall **268 / 888 (30%)** car-season-axis instances preserve held-out accuracy
(guard pass). Range: traction_aero 96%, brake_aero 63%, lateral_mech 40% … down
to max_power 4%, coast_drag 0%. The PASS holds on the accuracy-preserving subset
F1 was written to isolate — NOT a free tightening of every car-season.

## Per-layer ablation ([F4], leave-one-layer-out)

| variant | covered beats | median ratio | Δ vs full (marginal) |
|---|---|---|---|
| full | 9 | 0.400 | — |
| −L1 (no density removal) | 9 | 0.400 | **0** |
| −L2 (inert) | 9 | 0.400 | **0** |
| −L3 (no field-median differencing) | 2 | 0.087 | **7** |
| −L4 (no EB shrink) | 0 | 1.000 | **9** |

- **−L4 → all convergence collapses** (ratio 1.0, 0 beats): the L4 EB shrink is
  the entire engine.
- **−L3 → 2 beats, ratio 0.087**: shrinking the residual directly tightens even
  harder numerically but the guard rejects it on 9/11 axes — the exact
  "over-shrinker kills signal" failure F1 anticipated; L3's median differencing
  is what makes the shrink accuracy-preserving.
- **−L1 → Δ 0**: density removal is convergence-neutral (its value is in the
  Mexico/Monaco secondary, not here).
- **−L2 → Δ 0, exactly**: the honest confirmation of the g3 FLOAT — Layer 2 is
  inert on this frame, kept as an explicit seam, not credited. *(This is the
  Layer-2 ≈ 0 marginal the handoff predicted.)*

## Density secondary (Mexico↔Monaco, g2)
L1 tightens the cross-venue residual on **6 of 7** density-sensitive axes
(median |z| e.g. drag 2.21→1.22, traction_aero 2.35→1.08, max_power 1.75→0.83,
coast_drag 8.70→5.17). Sole exception `lateral_aero_grip_g` is already
density-insensitive (|z|≈0.07 raw) so the small increase is noise on a null gap.
Consistent with g2's residual-consistency finding + its setup/aero-confound
caveat.

## VERDICT (stated plainly)
**PASS — 9/11 covered axis-beats (≥7 threshold), median convergence ratio 0.40.**
Untuned: rule + split frozen in g1 before any held-out number was seen; nothing
adjusted after the fact. The PASS is genuine but narrow — two layers (L4 shrink,
L3 median differencing) do all the work, L1 is convergence-neutral, L2 is an
honest float, and the beat holds on the accuracy-preserving ~30% of car-seasons.

## Docs/contracts touched
- `docs/physics/626-phase2-weekend-state-model.md` (writeup, matches 624/625 precedent)
- `docs/physics/626-f6-holdout-gate.json` (machine-readable per-axis + ablation + verdict)

## Assumptions
- **tc1 coverage floor = 5 held-out car-seasons** (my defensible choice per the
  handoff Authority): above the spread-definition floor of 2, gives a
  car-season median not dominated by 1–2 points, still reachable on a ~1/3 split.
  It is a strictly *tightening* gate (can only turn a beat off); here it removed
  no beat the frozen rule kept.
- **Ablation is built by re-composing the FROZEN layer functions**
  (`fit_car_pools`/`apply_layer4`/`relative_component`) with one layer's input
  swapped — never a re-implementation and never a modification of g4 `model.py`.
  For the F6-measured car-signal, L3's active component is the relative (median)
  differencing (the re-anchor does not feed the shrink), so `−L3` removes the
  median differencing; `−L1` shrinks the raw-axis relative; `−L4` is the
  un-shrunk `l3_relative`; `−L2` = full (inert).
- Ran the harness as `py -m src.physics.weekend_state.gate_f6` from the worktree
  root so the worktree `src` wins over the global editable `.pth` (the
  editable-install trap); pytest is already worktree-safe.

## Stop conditions hit
- None. The held-out split left adequate coverage on 9 axes (≥14 car-seasons);
  the two thin/degenerate axes (max_power cov 3, coast_drag cov 0) are reported
  as honest nulls, not forced. The model applied leak-free on held-out (g4-proved).

## Out-of-scope observations (triage candidates)
- **Over-shrink on `max_power_w` and `coast_drag_area_m2`** (4% / 0% guard-pass):
  the L4 EB pool collapses these axes on nearly every car-season. Worth a
  follow-on look at whether their stored σ is mis-scaled (driving τ→0-ish
  hard-shrink) or whether these axes genuinely lack week-to-week signal.
- **The 30% overall guard-pass rate** means the model's convergence win is
  concentrated; a Phase-P consumer should weight the car-signal by its
  guard/coverage, not treat all 11 axes as uniformly improved.
- **L2 un-float** (already g4-triaged): needs a per-car representative-lap
  `cumulative_track_laps` bridge + a grip-`g`→axis-unit mapping — estimator
  work, out of scope here.

## Workflow Feedback
- **Handoff gaps:** the handoff said "leave-one-layer-out ablation … with/without
  each of the 4 layers" but did not note that, for the F6-measured car-signal,
  L3's re-anchor does NOT feed the measured quantity (only the relative/median
  component does). I had to derive the true computational dependency from the g4
  source to define an honest `−L3`. A one-line "the car-signal path is
  raw→L1→L3(relative)→L4; the L3 re-anchor is decomposition-only" would have
  saved that trace.
- **Context rediscovered:** that `−L4` degenerates to essentially the floor
  (l3_relative ≈ weekend_relative(raw axis) for the mechanical axes) — obvious
  only after reading all four layer modules; a note that "the floor IS the
  un-shrunk relative reading" would have framed the ablation faster.
- **Instructions improvised around:** the plan template's `m1` TDD wording
  assumes a red-first flow; this was test-after (handoff), so I collapsed to the
  single green postcondition as the template's own test-after clause allows — no
  real friction.
- **What would have made this easier:** none beyond the ablation-dependency note
  above — the handoff carried task/intent/scope/exclusions/evidence/test-mode/
  stop-conditions, and the frozen `gate_spec` exposed exactly the primitives
  (`paired_holdout_floor_per_car_season`, `signal_preservation_guard`,
  `evaluate_gate`) the harness needed.

## Map Impact
- **Structural anchors:** `gate_f6.py` (NEW) imports g1 `gate_spec`/`frame`/
  `holdout`/`layer1_physics`/`layer3_fieldcar`/`layer4_car` + g4 `model`; docs
  `626-*` (NEW). No new edges into evo (boundary honored, asserted by test).
- **Capabilities:** F6 held-out convergence-speed gate vs the #624 paired floor,
  with tc1 coverage floor + per-layer ablation, emitting an honest verdict.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`
  (asserted); no-leakage held-out (train-only fit, reused from g4); no
  `data/*.db` write; docs in `docs/physics/`.
- **Decision realized:** PASS threshold ≥7/11 outside noise (F6 pinned) + tc1
  ≥5 coverage; verdict = PASS (9/11).
- **Claims/evidence:** the four-layer model beats the paired held-out floor on
  9/11 covered axes; the win is L4(shrink)+L3(median), L1 convergence-neutral,
  L2 exactly 0 (g3 FLOAT confirmed) — all backed by the JSON + green test.
- **Trust limitations:** the PASS is narrow (30% guard-pass; concentrated in L4);
  max_power/coast_drag are per-axis nulls — flagged as triage.

## Return status
`complete`
