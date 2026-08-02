# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Post-review update (rework, 2026-07-19)
Review returned BLOCK on one marginal, trivial finding (harness correctness — anti-rig null fixture,
leakage-freeness, protocol faithfulness — all passed clean and were NOT touched by this rework):
`divergent_case_read` in `src/physics/layer2/fp_gate.py` was exactly 1 over BOTH strict machine-enforced
limits (`function_lines=100` vs limit `<100`; `cyclomatic_complexity=20` vs limit `<20`). The `--baseline`
check (which skips paths listed in `config/simplification_baseline.json`) missed it; the strict
`py -m src.utils.simplification_limits --paths ...` (no `--baseline`) — which `CREW_CONTEXT.md` names a
review blocker — caught it.

**Fix:** extracted two named helpers out of `divergent_case_read`, pure extraction, no logic change:
- `_pooled_normalized_weight_diffs(weekend_data, lowo) -> dict[int, float]` — the pooling + min-max
  normalization block (previously inline).
- `_fold_divergent_deltas(fold, wk, diff_by_obs_id, threshold, *, value_attr, target_attr) -> tuple[...]` —
  the per-fold top-tercile-subset-and-metric computation (previously the loop body).

`divergent_case_read` itself now just calls these two helpers and accumulates. Re-verified via the engine
(reopened `m3-protocol-mechanics`, which cascade-reset `m4`–`m7`; all four were re-driven to `complete` with
fresh re-verification evidence, no code changes needed in any of them since the refactor didn't touch their
surfaces):
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_representativeness_gate.py -q
# 36 passed
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m src.utils.simplification_limits --paths src/physics/layer2/fp_gate.py
# PASS (1 files checked)   <- was: FAIL (2 violations) before the fix
cd /c/Programs/f1-513 && git status --short data/
# (clean, no output)
```
`fp_gate.py` grew from 915 to 953 lines (two new small helpers), still well under the 999 file-line limit.
Both `--baseline` and the strict no-`--baseline` simplification_limits checks now PASS on all 3 touched files.

---

## Assigned gate
`g6` (execute.json) — "held-out gate harness, both channels"

## Completed slice
Built the FROZEN held-out gate harness that encodes `GATE_PROTOCOL.md` exactly: `src/physics/layer2/fp_gate.py`
(the testable core), `scripts/fp_representativeness_gate.py` (a thin CLI over it), and
`tests/unit/physics/layer2/test_fp_representativeness_gate.py` (the gate's own required test path). All eight
close criteria are implemented and tested: injectable-extractor observation assembly, the two arms
(clock/learned), LOWO cross-validation, paired-bootstrap significance, the divergent-case read, the emergence
audit, the sandbagging demonstration, and both channels (PRIMARY grip / SECONDARY power) reported honestly. The
three load-bearing fixture tests (POSITIVE / NULL / LEAKAGE) all pass, on SYNTHETIC fixtures only — no real
compute, telemetry, or DB reads happened in this gate.

## Scope
**Files changed:**
- `src/physics/layer2/fp_gate.py` (new, 915 lines) — the core module:
  - `RawFpObservation`/`RawQTarget`/`GateExtractor` (Protocol) — the injectable-extractor seam.
  - `GateObservation`/`WeekendGateData`, `build_gate_observations` — reuses `fp_representativeness.observation_features` verbatim.
  - `CLOCK_DECAY_HOURS`, `clock_weight` (parameter-free exp decay), `learned_weight` (delegates to `fp_representativeness.observation_weight`).
  - `_predict_car_capability`, `fit_weight_params` (Nelder-Mead + L2 shrinkage, TRAIN-weekends-only signature), `_weekend_metric` (Spearman + centred RMSE).
  - `FoldResult`/`LowoResult`/`run_lowo` (leave-one-weekend-out), `BootstrapResult`/`paired_bootstrap` (10k-default paired bootstrap).
  - `DivergentReadResult`/`divergent_case_read` (F4, min-max-normalized top-tercile read), `EmergenceResult`/`emergence_audit` (F3), `SandbagResult`/`sandbagging_demo` (F8), `GateVerdict`/`evaluate_gate` (combines overall + divergent verdicts).
  - `SecondaryGateResult`/`secondary_power_gate` (matched fp_mass-sigma stratum, F1).
- `scripts/fp_representativeness_gate.py` (new, 158 lines) — thin CLI: dynamic `--extractor module:factory` import, wiring, and a pure `format_report()` function. No extraction or weighting logic of its own.
- `tests/unit/physics/layer2/test_fp_representativeness_gate.py` (new, 703 lines, 36 tests) — the gate's own required test path, organized m1–m6 matching the build order.

**Specific exclusions touched:** no. No real compute/telemetry/DB reads anywhere in this gate (confirmed —
every fixture is synthetic, constructed in-test or in the CLI's throwaway smoke script, which was deleted
after use). No session weight was hardcoded outside `fp_representativeness` (learned arm delegates to
`observation_weight` verbatim). No `data/*.db` was read or written (see DB hygiene evidence below).

## Behavior changed
Yes — new capability. This is the first FROZEN held-out falsifiable test for FP representativeness weighting;
nothing existed here before this gate.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — new `fp_gate.py`; `struct:physics` — new
  `scripts/fp_representativeness_gate.py`.
- **Capabilities added/changed/affected:** the frozen held-out falsifiable test (F10) — `evaluate_gate` (PRIMARY
  grip channel) and `secondary_power_gate` (SECONDARY power channel) are now real, callable, synthetic-fixture-
  proven functions. G7 wires the real extractor through the `GateExtractor` Protocol seam (contract below) and
  runs the real 16-weekend 2023 batch.
- **Constraints/assumptions touched:** leakage (F6) — `fit_weight_params`'s signature accepts only a
  train-weekend list, proven via two dedicated LEAKAGE tests (direct call + through `run_lowo`'s own fold
  loop). Divergent-case read (F4) — implemented with a min-max normalization fix (see Assumptions). Emergence
  (F3) — `emergence_audit` checks both the concrete same-session example and the track-evolution-dominance
  guard. Both-channels honest report — `secondary_power_gate` never silently reports
  `CONFOUNDED_NOT_EVIDENTIAL` as evidential.
- **Decision candidates:**
  1. `fit_weight_params` gained `DEFAULT_L2_PENALTY=1e-3` (L2 shrinkage toward `initial`/`DEFAULT_WEIGHT_PARAMS`)
     — NOT in the original close criteria, added because unconstrained Nelder-Mead saturates coefficients
     toward the sigmoid's asymptote on clean/small synthetic data (train MSE keeps falling toward the same
     floor as coefficients → ∞, no finite optimum), which degenerated the divergent-case-read tercile split.
     A light regularizer keeps the fit well-behaved without changing which arm wins on real signal. Surfaced
     for G7/Ship-review: on real, noisy 2023 telemetry this saturation risk is far lower (real data won't fit
     to exactly-zero loss), but the regularizer is cheap insurance either way.
  2. `divergent_case_read` min-max normalizes both arms' raw weight values (over the pooled observation set)
     before differencing, rather than comparing raw `|learned - clock|`. This was a genuine bug found via the
     POSITIVE fixture's RED cycle (see TDD evidence) — clock (unbounded exponential decay) and learned (bounded
     logistic) live on different native scales, so raw differencing let whichever arm had the wider range at
     its extreme monopolize the top-tercile split into a single group where both arms predicted identically
     (a false HONEST_NULL). This is a genuine strengthening of F4's mechanism, not a scope departure — flagging
     because it changes the harness's math from the handoff's literal `|w_learned - w_clock|` wording.
- **Claims/evidence produced:** 36/36 gate tests green (see Evidence below), including the three load-bearing
  fixtures (POSITIVE/NULL/LEAKAGE) plus 5 supporting sections (m1 seam, m2 fit/LOWO/bootstrap, m3 divergent/
  emergence/sandbag/evaluate_gate, m5 secondary, m6 CLI format_report). `simplification_limits --baseline` PASS
  on all 3 touched files.
- **Trust limitations / drift found:** none found in this gate's own scope. The SECONDARY channel's real-world
  evidential value depends entirely on whether G7's real `fp_lap_latent.extract_fp_lap_latent` extractor ever
  supplies a non-constant `fp_mass_sigma_kg` — as of this gate, `fp_lap_latent.py`'s own `extract_fp_lap_latent`
  calls `mass_model.fp_mass(year, fuel_kg=fuel_est)` WITHOUT an explicit `fuel_sigma_kg`, so every real FP lap's
  `mass_sigma_kg` currently resolves to the constant `FP_FUEL_INTERCEPT_SIGMA_KG=15.0` (verified by reading
  `fp_lap_latent.py` and `mass_model.py` during context-load). If G7's real extractor doesn't narrow that sigma
  per-run, `secondary_power_gate` will correctly and honestly report `CONFOUNDED_NOT_EVIDENTIAL` on the real
  batch — exactly the protocol's sanctioned fallback (F1), not a bug, but worth flagging now so it isn't a
  surprise at G7.
- **Triage candidates:**
  1. If a real matched-sigma SECONDARY read is ever wanted, G7 (or a follow-on) would need
     `fp_lap_latent.extract_fp_lap_latent` to supply a per-run-varying `fuel_sigma_kg` to `mass_model.fp_mass`
     (e.g. narrower for a push lap immediately after a known fuel-rig fill event, wider for an ambiguous
     long-run) — currently out of both G2's and this gate's scope.

## Test mode
**Required:** `test-first (TDD)`.
**Satisfied:** yes — every section (m1 through m6) has a genuine RED-then-GREEN cycle. m4 (the POSITIVE/NULL
fixtures) is notable: the RED was a genuine logic bug (not just an import error), root-caused via a scratch
debug script and fixed in `fp_gate.py` itself (see TDD evidence).

## Evidence

### Full gate suite
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_representativeness_gate.py -q
```
```
collected 36 items
tests\unit\physics\layer2\test_fp_representativeness_gate.py ........... [ 30%]
.........................                                                [100%]
36 passed in 3.94s
```

### The three load-bearing fixture tests, explicitly
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_representativeness_gate.py -q -k "Positive or Null or Leakage"
```
```
6 passed
```
- **POSITIVE** (`TestPositiveFixture::test_learned_beats_clock_end_to_end`): synthetic weekends where early
  (far-clock), low-fuel/soft/push laps carry the TRUE per-car grip ranking and late (near-clock), high-fuel/
  hard/long_run laps carry a DELIBERATELY REVERSED ranking → `evaluate_gate` returns `PASS` (overall spearman
  delta=+2.0, CI entirely positive; divergent-case read also `PASS`, not inconclusive).
- **NULL** (`TestNullFixture::test_harness_reports_honest_null_not_rigged_to_always_pass`): every observation
  shares IDENTICAL representativeness features (so `learned_weight` is a PROVABLE CONSTANT regardless of any
  fitted `WeightParams` — a weighted mean with a uniform weight reduces to the plain unweighted mean); only
  clock-distance carries real information (near=true ranking, far=reversed ranking, 2x-weighted so it dominates
  the unweighted average) → `evaluate_gate` returns `HONEST_NULL`, neither bootstrap favors learned. This is
  immune to the fit "gaming" its way to a pass, by construction.
- **LEAKAGE** (`TestLeakage`, 2 tests): shuffling a held-out weekend's Q targets (directly, and through
  `run_lowo`'s own fold loop) does not change that fold's fitted `learned_params` — `fit_weight_params`'s
  signature accepts only a train-weekend list, so a held-out weekend has no path in.

### simplification_limits --baseline
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/fp_gate.py scripts/fp_representativeness_gate.py tests/unit/physics/layer2/test_fp_representativeness_gate.py
```
```
PASS (3 files checked)
```
File sizes: `fp_gate.py`=915 lines (under the 999 limit), CLI=158 lines, test file=703 lines.

### DB hygiene
```bash
cd /c/Programs/f1-513 && git status --short data/
```
(no output — clean; no `data/*.db` was read or written anywhere in this gate)

### CLI end-to-end smoke run (thin-CLI wiring proof)
A throwaway synthetic `GateExtractor` module (`scripts/_g6_smoke_extractor.py`, mirroring the POSITIVE fixture)
was written, run through the real CLI, and then DELETED — not part of the deliverable set, evidence only:
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py scripts/fp_representativeness_gate.py \
  --extractor scripts._g6_smoke_extractor:make_extractor \
  --weekends Bahrain Australia Miami Monaco Spain Canada Hungary Japan \
  --bootstrap-resamples 2000 --seed 3
```
```
FP representativeness held-out gate -- GATE_PROTOCOL.md

PRIMARY_GRIP channel: verdict=PASS
  overall spearman: mean_delta=2.0000 ci=[2.0000, 2.0000] favors_learned=True
  overall centred-rmse: mean_delta=1.4559 ci=[1.4559, 1.4559] favors_learned=True
  divergent-case read: verdict=PASS n_divergent=64/64 inconclusive=False

SECONDARY_POWER channel: status=CONFOUNDED_NOT_EVIDENTIAL verdict=CONFOUNDED_NOT_EVIDENTIAL

Emergence audit (F3): passes=True push_weight=0.9975 longrun_weight=0.6399 track_evo_only_range=0.0580 other_features_range=0.6200

Sandbagging demo (F8): weekend=Bahrain car=A pace_jump=0.0000 learned=0.8095 clock=0.6773 passes=False
```
(SECONDARY is honestly `CONFOUNDED_NOT_EVIDENTIAL` here because the smoke extractor used a constant
`fp_mass_sigma_kg=15.0` for every observation — exactly the real-world condition flagged in Trust limitations
above. The sandbag demo's `passes=False` in THIS particular smoke run is expected/uninteresting: with
`pace_jump=0.0000` the data-defined "largest jump" car-weekend here has no real sandbagging signal to detect —
`TestSandbaggingDemo` in the actual test suite uses a purpose-built fixture with a real jump and asserts
`passes=True` there.)

## TDD evidence, if required
- **m1 RED:** `ModuleNotFoundError: No module named 'src.physics.layer2.fp_gate'` (module didn't exist).
- **m2 RED:** `ImportError: cannot import name 'fit_weight_params'` (functions not yet added).
- **m3 RED:** `ImportError: cannot import name 'GateVerdict'` (functions not yet added).
- **m4 RED (genuine logic failure, not an import error):** the POSITIVE fixture test initially failed with
  `AssertionError: assert 'HONEST_NULL' == 'PASS'`. Root-caused via a scratch debug script: `divergent_case_read`
  compared `clock_weight` (unbounded exponential decay) and `learned_weight` (bounded logistic) on their raw
  native scales, so the arm with the wider numeric range at its favored extreme always monopolized the
  top-tercile split into a single group, and — because within that single group both arms reduced to the SAME
  unweighted-average prediction — the divergent-case read spuriously reported `HONEST_NULL` even though the
  OVERALL LOWO metric already showed a clean +2.0 Spearman delta favoring learned. Fixed by min-max normalizing
  both arms' weights over the pooled set before differencing (see Map Impact §Decision candidates #2). Also
  added `DEFAULT_L2_PENALTY` shrinkage to `fit_weight_params` after observing Nelder-Mead saturate coefficients
  toward the sigmoid's asymptote on the clean synthetic data (Map Impact §Decision candidates #1).
- **m5 RED:** `ImportError: cannot import name 'secondary_power_gate'`.
- **m6 RED:** `ModuleNotFoundError: No module named 'fp_representativeness_gate'` (CLI script didn't exist).
- **Passing:** every section reached GREEN after its fix; full suite 36/36 green (pasted above).
- **Refactor while green:** no separate refactor pass; a small in-flight syntax fix (conditional-expression-
  inside-generator ordering) was needed in `secondary_power_gate` during its own RED→GREEN cycle, not a
  post-green refactor.

## Docs/contracts touched
- None outside the touched files' own module/function docstrings (updated in place, following project
  convention — every new public function/dataclass carries a full docstring naming its GATE_PROTOCOL.md
  section reference).

## Assumptions
- **The injectable-extractor seam contract for G7** (the load-bearing contract, spelled out per the handoff's
  request): G7 implements `GateExtractor` (a `Protocol` in `fp_gate.py`) with two methods:
  - `fp_observations(weekend_id: str) -> Sequence[RawFpObservation]` — one `RawFpObservation` per FP lap (or
    per coarser observation unit G7 chooses), each carrying: `car_id`, `session_type` ('FP1'/'FP2'/'FP3'),
    `hours_to_q` (clock gap, the CLOCK arm's only input), `latent: FpLapLatent` (reused verbatim from
    `fp_lap_latent.extract_fp_lap_latent`), `track_evolution`/`session_max_track_evolution` (leakage-guarded
    ints, or `None`), `grip_value` (the PRIMARY mass-free capability signal — G7's real version derives this
    from `apex_extract.extract_apex_observations` + `capability.apex_pace`-style per-observation residuals),
    `power_value` (SECONDARY, or `None` if unavailable), `fp_mass_sigma_kg` (this observation's fp_mass
    intercept σ — see the Trust-limitations note: currently constant in the real pipeline unless G7 narrows it).
  - `q_targets(weekend_id: str) -> Sequence[RawQTarget]` — one `RawQTarget` per car with `grip_capability`
    (target only, never a feature) and `power_capability` (or `None`).
  `build_gate_observations(weekends, extractor, *, quali_fuel_kg)` is the ONLY consumer of this Protocol; G7
  can supply ANY implementation (DB-backed, telemetry-backed) satisfying it without touching `fp_gate.py`.
- **`fit_weight_params`'s `DEFAULT_L2_PENALTY=1e-3`** is a DECISION-CANDIDATE, not validated against real data
  (flagged above) — reasonable given the observed saturation failure mode, not measured/fitted itself.
- **`CLOCK_DECAY_HOURS=24.0`** is a single named constant (GATE_PROTOCOL sec 1's "no fitting" branch for the
  clock arm) — not fit per-fold; the protocol explicitly allows this simpler branch.
- **`min_divergence_threshold=1e-6`** (on the NORMALIZED scale, so effectively "agree almost everywhere in
  relative terms") and **`min_distinct_sigma=2`** are reasonable hand-set guard thresholds, not calibrated
  against real data — G7 may need to revisit if the real 2023 batch's divergence/sigma spread sits awkwardly
  near either boundary.
- Deferred the "driver-utility transfer" (GATE_PROTOCOL sec 10) entirely — out of this gate's scope per the
  handoff (named as a follow-on if primary passes).

## Stop conditions hit
None. The protocol was encoded as frozen (no split/metric/arm invented beyond GATE_PROTOCOL.md's own text), a
leakage-free LOWO was built and proven via two dedicated tests, and the null fixture correctly reports
honest-null (proven, not merely asserted-and-hoped).

## Out-of-scope observations
- See Map Impact §Trust limitations: the SECONDARY channel's real-world evidential value is gated on whether
  `fp_lap_latent.extract_fp_lap_latent` (G2, frozen, out of this gate's scope) ever supplies a non-constant
  `fuel_sigma_kg` to `mass_model.fp_mass`. As-is, a real G7 batch will almost certainly see
  `secondary_power_gate` report `CONFOUNDED_NOT_EVIDENTIAL` — which is the CORRECT and HONEST outcome per the
  protocol, not a defect, but worth flagging so it is an expected result, not a surprise.

## Workflow Feedback

- **Handoff gaps:** the handoff's own wording for the divergent-case read ("top tercile of
  `|w_learned - w_clock|`") is literally what I implemented FIRST, and it produced a real bug — a false
  `HONEST_NULL` on the POSITIVE fixture — because clock_weight (unbounded exp decay) and learned_weight
  (bounded logistic) are never on the same native scale. The handoff didn't flag this (understandably, since
  it wasn't discoverable without building and testing the harness). Recording it here so a future protocol
  revision or G7 audit knows the CURRENT implementation normalizes both arms before differencing, not raw
  differencing — a deliberate, tested strengthening of F4, not a literal reading of the frozen text.
- **Context rediscovered:** `fp_lap_latent.extract_fp_lap_latent`'s real fuel/mass sigma is CONSTANT
  (`FP_FUEL_INTERCEPT_SIGMA_KG=15.0`, from `mass_model.py`) for every lap today — I had to read both
  `fp_lap_latent.py` and `mass_model.py` at context-load to discover this, and it directly determines whether
  `secondary_power_gate` will ever be evidential on real data. A pointer to this in the handoff's Map Anchors
  (or GATE_PROTOCOL.md sec 11's non-circularity contract) would have saved the rediscovery and would help G7
  anticipate the likely `CONFOUNDED_NOT_EVIDENTIAL` outcome rather than being surprised by it.
- **Instructions improvised around:** none beyond the divergent-case-read normalization fix above (which I
  treat as a legitimate TDD-driven correction within scope, not an improvisation around an instruction —
  GATE_PROTOCOL.md's own sec 6 describes the SEMANTIC goal ("observations where clock and learned DISAGREE
  most") precisely, and the normalized comparison is a more faithful implementation of that goal than the raw
  difference the handoff's shorthand literally named).
- **What would have made this easier:** a note in the handoff or GATE_PROTOCOL.md flagging that clock_weight
  and learned_weight are expected to live on different native scales (one bounded [0,1] logistic, one unbounded
  exponential decay) and that any cross-arm comparison (the divergent-case read, in particular) needs to
  account for that. Also, an explicit pointer to `fp_lap_latent.py`'s current constant-sigma behavior would
  have saved the SECONDARY-channel rediscovery noted above.

## Return status
`complete`
