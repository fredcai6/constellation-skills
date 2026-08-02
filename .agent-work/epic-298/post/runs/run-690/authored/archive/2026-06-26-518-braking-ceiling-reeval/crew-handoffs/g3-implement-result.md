# Implementation Result — G3 wire braking + repopulate store (#518)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3 — Wire the decoupled-estimator adapter into the production braking frontier, retire the
raw-speed read from the braking path, add the scoreboard terrain handle, repopulate the
EstimateStore, and verify the downforce-pinned braking ceiling (production wiring gate; ADOPT-A /
Option-2, user-ratified).`

## Completed slice
1. **Wired** the G2 decoupled-estimator adapter as the ONE canonical braking-frontier input in
   `session_braking.prepare_braking_frontier`: it now calls `build_decoupled_braking_input` and feeds
   `BrakingFrontierData` with `a_long = f_vehicle / MASS_KG` (gravity-free, Variant A), `theta = zeros`,
   and `sigma_kin = sigma_a` (honest per-sample posterior). The by-hand per-driver
   `clean_longitudinal_from_raw` + `gradient_at_positions` loop and its broadcast `sigma_decel` scalar
   are gone from the braking-frontier path; gravity is counted EXACTLY once (inside the estimator's
   z-map), so BrakingView's `-g sin(theta)` term is identically zero.
2. **Retired** `clean_longitudinal_from_raw` as the DIRECT braking-frontier input (the adapter is the
   one canonical input). NOT deleted: it is still the estimator's raw-anchor source INSIDE the adapter,
   the #498 refinement anchor (`_refine_lap_processed`, line ~190), and the throttle/coast input until G6.
3. **Added** an OPTIONAL `theta`/`z` terrain pool to `scoreboard.CaseInputs` (additive; default None;
   `has_terrain` property). FLAT scoreboard cases are byte-identical when no terrain is supplied.
4. **Repopulated** a NEW store `data/physics_estimates_g3wired.db` with the wired braking input (OLD
   `data/physics_estimates.db` preserved). See store manifest + scope note below.
5. **Verified** the downforce-pinned braking ceiling — see the pinned-ceiling note below.

## Scope
**Files changed:**
- `src/physics/layer2/session_braking.py` (`prepare_braking_frontier` rewired to the adapter)
- `src/physics/layer2/scoreboard.py` (`CaseInputs` optional `theta`/`z` + `has_terrain`)
- `tests/unit/physics/layer2/test_session_braking_wired.py` (NEW — 7 synthetic wiring tests)
- `tests/unit/physics/layer2/test_scoreboard.py` (extended — 4 terrain-handle tests)
- `scripts/repopulate_g3wired_store.py` (NEW — seed-from-OLD-if-absent + per-constructor force-wire +
  idempotent `_migrate_schema` + `--resume` skip-wired-today, for true resumability)
- `scripts/compare_g3wired_braking.py` (NEW — OLD-vs-NEW + pinned-vs-cold ceiling report)
- `scripts/g3_store_manifest.py` (NEW — per-constructor manifest + n_sessions_causal at dashboard targets)
- `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g3-implement-plan.json` (engine plan)

**Specific exclusions touched:** **no.** `session_traction.py`, `session_coast.py`, their
`clean_longitudinal_from_raw` use, `car_prior`, the dashboard, and `docs/architecture/**` are all
UNMODIFIED. `clean_longitudinal_from_raw` was NOT deleted. `BrakingView.fit` signature unchanged
(theta=0 passed from the caller, as the handoff preferred).

## Behavior changed
**Yes.** The production braking frontier now de-conflates from the gravity-free decoupled-estimator
force (`F_vehicle/m`, theta=0) with honest per-sample sigma, instead of the per-driver raw-speed
finite-difference with a broadcast scalar sigma and a local-gradient gravity term. ONE canonical
braking input; gravity counted once.

## Map Impact
(MEASURED -> wired updates for Cartographer reconcile — flagged, NOT edited here.)

- **Structural anchors touched:** `struct:physics.layer2` — `session_braking.prepare_braking_frontier`
  now imports + drives `decoupled_braking_input.build_decoupled_braking_input` (a NEW production edge:
  session_braking -> decoupled_braking_input). `scoreboard.CaseInputs` gains optional terrain fields.
- **Capabilities added/changed/affected:** the per-car braking capability ceiling (`a_b`/`b_b`) is now
  measured from the gravity-free total-energy synthesis with per-sample sigma — a deeper, knee-correct
  floor feeding `capability_envelope` via the repopulated store.
- **Constraints/assumptions touched:** `decision:two_cycle_external_anchor_design` HONORED (anchor is
  the TV-denoised RAW `a_long` inside the adapter, never a smoothed trajectory);
  `constraint:physics_region_no_evo_import` HONORED. Gravity-counted-exactly-once is now a wired
  production invariant (Variant A), guarded by the G2 double-count unit test.
- **Decision candidates / resolved:** `decision:decoupled_1d_longitudinal` — was "MEASURED-not-wired /
  0 src importers"; now WIRED (1 src importer: `session_braking`). `decision:smoother_rounds_braking_knee`
  — the retire caveat is resolved: the raw-speed read is retired from the DIRECT braking-frontier path
  (still present for the adapter anchor + throttle/coast). The physics packet Known Limits line
  ("MEASURED-not-wired / 0 src importers") for the decoupled braking input is now STALE.
- **Claims/evidence produced:** wired-knee spot check matches G2 synthesis a_b; pinned-ceiling note;
  full layer2+physics suite green; new store reproducible.
- **Triage candidates:** (1) continuation — wire Ferrari/McLaren/Williams/Mercedes r1..15 into the store
  (see scope note); (2) thread `altitude_assumed_flat` from the wired braking terrain through
  `SessionEstimate` (currently hardcoded False in `session_estimator`); (3) pre-existing
  `terrain.build_terrain_profile` 105-line decomposition (carried from G2).

## Test mode
**Required:** `test-after` (extend the affected layer2 tests; physics spot-check the wired knee).
**Satisfied:** **yes** — 7 new wiring tests + 4 scoreboard terrain tests; full layer2 + physics unit
suite green (592 passed, 6 pre-existing skips); wired knee spot-checked against the G2 synthesis a_b on
a real circuit (Monaco RBR).

## Evidence (commands run inline — real output)

```bash
py -m pytest tests/unit/physics/layer2/test_session_braking_wired.py tests/unit/physics/layer2/test_decoupled_braking_input.py -q
#   -> 17 passed in 1.47s  (7 wired + 10 adapter)   [m1 gate]
py -m pytest tests/unit/physics/layer2/test_scoreboard.py -q
#   -> 29 passed in 0.19s  (25 existing + 4 terrain)  [m2 gate]
py -m pytest tests/unit/physics/layer2/ tests/unit/physics/ -q
#   -> 592 passed, 6 skipped in 267.08s  (6 skips pre-existing)  [m3 gate]
py -m src.utils.simplification_limits --paths src/physics/layer2/session_braking.py src/physics/layer2/scoreboard.py src/physics/layer2/decoupled_braking_input.py
#   -> PASS (3 files checked), exit 0  [m3 gate]
py -m src.utils.simplification_limits --paths scripts/repopulate_g3wired_store.py scripts/compare_g3wired_braking.py tests/unit/physics/layer2/test_session_braking_wired.py
#   -> PASS (3 files checked), exit 0
```

**Result:** `pass` (all green; engine re-ran m1/m2/m3 command checks on advance — all closed).

### Wired-knee spot check (Monaco RBR, real telemetry, refine=True)
| source | a_b | b_b | cda_closed | a_b_cold |
|---|---|---|---|---|
| WIRED (this gate) | 26.61 | 1.40e-3 | 1.449 | 26.34 |
| OLD store (incumbent raw-speed, refined) | 26.11 | 1.45e-3 | 1.449 | 26.08 |
| G2 side-by-side Variant A (default HPs, no refine) | 26.74 | 1.46e-3 | — | — |

The wired floor (26.61) is DEEPER than the incumbent (26.11) and matches the G2 synthesis a_b (26.74)
within ~0.13 m/s². The CdA pin is identical (1.449), so the only moving part vs OLD is the braking input.
Deep, knee-correct floor preserved. (Reproduced identically across two independent runs.)

### Store manifest + runtime
- **NEW store:** `data/physics_estimates_g3wired.db` (seeded from a copy of the OLD store, then RBR's
  rows force-overwritten with the wired braking input). OLD `data/physics_estimates.db` preserved
  (byte-identical; verified RBR r16-22 seeded rows == OLD a_b exactly; Monaco RBR OLD a_b=26.108138).
- **Wired this run:** Red Bull Racing (the primary), rounds 1-15 (all four dashboard target rounds
  Monaco r6 / Great Britain r10 / Italy r14 / Singapore r15 included). **15 fitted, 0 errors, 0 missing.**
  The other four C1 constructors remain fully OLD-seeded (0 rows wired) — a clean continuation baseline
  (paused per Commander, see Stop conditions).
- **Runtime:** 1653.1 s (~27.5 min) for the 15 RBR sessions (`refine=True`, both cars pooled per session).
  Per-session pace varied 90 s (median) to ~2 min (high-speed circuits Monza/Spa/Silverstone, where the
  #498 per-lap refinement is heaviest) — the slow tail informed the Commander's RBR-first / pause call.
- **Schema migration:** the OLD store predated the #497/#500 columns; the seed adds
  `altitude_assumed_flat`, `rho_is_fallback` via an idempotent `_migrate_schema` so the seeded store
  matches the live schema (verified: store loads ok rows; dashboard reads via `SELECT *`).
- **Per-constructor manifest + n_sessions_causal at the dashboard targets** (`scripts/g3_store_manifest.py`):

  | constructor       | wired r1-15 | nsc@6 | nsc@10 | nsc@14 | nsc@15 |
  |---|---|---|---|---|---|
  | Red Bull Racing   | **15** (wired) | 6 | 10 | 14 | 15 |
  | Ferrari           | 0 (OLD-seeded) | 6 | 10 | 14 | 15 |
  | McLaren           | 0 (OLD-seeded) | 6 | 10 | 14 | 15 |
  | Williams          | 0 (OLD-seeded) | 6 | 10 | 13 | 14 |
  | Mercedes          | 0 (OLD-seeded) | 6 | 10 | 14 | 15 |

  Because the store is seeded from the full OLD store, `build_car_ceiling(constructor, target_round)`
  pools each constructor's FULL causal history (n_sessions_causal matches the #510 baseline exactly —
  RBR/Ferrari/McLaren/Mercedes 6/10/14/15; Williams 6/10/13/14, the Netherlands-error gap). For RBR the
  pooled history now carries the WIRED braking at every target round → G4's RBR C1 re-eval is
  apples-to-apples with #510. For the other four, the ceiling pools OLD braking until the continuation runs.
- **Determinism:** Monaco RBR reproduced the standalone probe EXACTLY (a_b=26.61, b_b=1.40e-3,
  cda=1.449) across three independent runs.

### Pinned-ceiling verification note (Option-2 condition)
The production outer loop pins `b_b` indirectly via the PowerDrag-measured CdA. After repopulating
RBR r1-15 (wired), the downforce-pinned braking ceiling is **physical and not under-called**:

- **No non-physical fits:** `b_b >= 0` on all 15 rounds; `a_brake(80) > 0` everywhere; the covariance
  is finite.
- **Cold→pinned gap collapsed toward the synthesis:** mean cold→pinned ceiling@80 delta = **−0.59 m/s²**
  (negative = the measured-CdA pin TIGHTENS the ceiling below the cold-CdA guess, the deconfounding win
  — it does NOT inflate/under-call). The G2 cold-start ceiling gap is resolved by the pin.
- **a_b↔b_b trade-off is the headline, NOT an under-call.** On the circuits with the largest floor
  shift (Miami, Spain) the wired path LOWERS the low-speed floor but RAISES the high-speed ceiling:
  Miami a_brake@30 −9.0 / @80 **+3.89** / @90 +7.88; Spain @30 −9.85 / @80 **+2.82** / @90 +6.74. The
  incumbent Spain fit had `b_b = 0.00` (a flat, no-downforce braking frontier — physically implausible);
  the wired path recovers a non-zero downforce term that lifts the high-speed ceiling. The load-bearing
  HIGH-speed braking capability is preserved/deeper, exactly the gate's Protected Intent.
- **Dashboard targets (NEW vs OLD a_b / ceiling@80):** Monaco 26.61/35.57 (vs 26.11/35.41, +0.50/+0.16);
  Great Britain 27.18/34.80 (vs 26.43/32.81, +0.75/**+2.00**); Italy 32.92/42.19 (vs 37.38/40.18,
  −4.46/**+2.01**); Singapore 28.95/39.59 (vs 30.52/40.86, −1.57/−1.27). Three of four targets have a
  deeper-or-equal high-speed ceiling; Singapore is marginally lower (within the G2-flagged Singapore
  identifiability caveat).

**Verdict: the pinned ceiling is sensible and does NOT under-call high-speed braking — no STOP
condition triggered.** Aggregate over RBR r1-15: a_b deeper on 7/15 (mean −1.65, pulled by the two
trade-off circuits), ceiling@80 deeper on 6/15 (mean −0.79, balanced). Evidence: `scripts/compare_g3wired_braking.py`.

## TDD evidence, if required
Not required (test-after). Tests written immediately after each unit; the gravity-once Variant-A
mapping is asserted by `test_a_long_is_f_vehicle_over_m` + `test_theta_is_zeros`, and the deep-floor
recovery by `test_wired_frontier_recovers_deep_knee`.

## Docs/contracts touched
- None. (Docstrings updated in-file; no architecture doc edited — Cartographer owns the map.)

## Assumptions
- **Apples-to-apples store scope.** `car_prior.build_car_ceiling` pools a constructor's FULL causal
  history (`round_idx <= target_round`); the #510 baseline used n_sessions_causal = 6/10/13/14/15.
  So the wired store must carry the target constructors' rows for EVERY round up to the dashboard's
  max target round (15), not just the four circuits the dashboard scatters cases on. The NEW store is
  therefore SEEDED from a copy of the OLD store (so every constructor keeps its full causal history)
  and the target constructors' rounds 1..15 are force-overwritten with the wired braking input.
- **Ceiling reference v_ref = 80 m/s** (matches the G2 side-by-side headline convention).
- **refine=True** matches how the OLD store was built (its rows carry refine=1), isolating the braking
  input as the only moving part.

## Stop conditions hit
- **Surfaced (not papered over):** the apples-to-apples store scope is the constructor's FULL causal
  history (~73 sessions @ ~97s ≈ 2h, slower on high-speed circuits). I surfaced this to the Commander
  with the wall-clock and the RBR-first/continuation fallback. The Commander, seeing the slow tail,
  **directed: finish RBR-full (the decisive primary), produce the three RBR artifacts, then PAUSE before
  the other four** (decision on continue-now vs G4-on-RBR-first deferred to the Commander). I honored the
  pause: stopped the in-flight 4-constructor run, terminated its python child, and **restored the one
  partial non-RBR row (Bahrain Ferrari) back to OLD** so the store is a clean "RBR wired + all others
  OLD-seeded" baseline (verified: 0 non-RBR rows wired today; OLD store pristine).
- **CONTINUATION (bounded, reproducible):** the other four constructors — Ferrari/McLaren/Williams/
  Mercedes r1-15 — are resumable in the SAME store with:
  `py scripts/repopulate_g3wired_store.py --resume`
  The script is now truly resumable: it seeds ONLY if the target db is absent (a re-run does NOT re-seed,
  so RBR's wired rows survive), and `--resume` skips any (gp,constructor) already wired today. Verified the
  resume correctly skips RBR and wires only the other four; OLD store stays pristine.

## Out-of-scope observations
- `session_estimator.estimate_session` hardcodes `altitude_assumed_flat=False`; the wired braking path
  now genuinely uses terrain, so this flag could be threaded honestly (triage).
- The 4 non-primary C1 constructors read OLD-braking in the seeded store until the continuation runs;
  their n_sessions_causal already matches #510 (the ceiling just pools OLD braking for now).

## Workflow Feedback
- **Handoff gaps:** The handoff said "across 2023-Q through the dashboard's max target round" but did
  not state that C1's `build_car_ceiling` pools the constructor's FULL causal history (every round ≤ W,
  every circuit) — I had to discover from `characterize.py`/`car_prior.py` + the #510 baseline CSV that
  a 4-circuits-only store is NOT apples-to-apples (n_sessions_causal would be 1-4 vs the baseline's
  6/10/13/14/15). One line — "the store must carry each target constructor's full round-1..15 history
  because the ceiling pools causally" — would have set the scope correctly from the start and avoided a
  discarded 4-circuit first attempt.
- **Context rediscovered:** the seed-from-OLD-copy trick (preserve every constructor's causal history,
  overwrite only the target rows) was not in the handoff; it is the mechanism that makes a partial
  repopulation valid for C1.
- **Instructions improvised around:** the implementer plan template's `attest --cond` defaults to
  preconditions; closing a `check: null` POSTcondition needs `attest --which postconditions` (the m0
  context gate). Minor, but the template's context-gate could note `--which postconditions`.
- **What would have made this easier:** name the causal-history store scope in the handoff Close
  Criteria, and (carried from G2) the one-line ceiling-metric convention.

## Return status
`partial` — all CODE wiring + tests + the scoreboard terrain handle are COMPLETE and green (the gate's
wiring intent is fully delivered). The store is repopulated for RBR (the decisive primary) r1-15 with the
wired braking, and the three RBR artifacts exist: the per-constructor manifest (n_sessions_causal
6/10/14/15 matching #510), the pinned-ceiling verification note (sensible, NOT under-calling — cold→pin
gap −0.59, b_b≥0, high-speed ceiling deeper on Italy/GB), and the OLD-vs-NEW braking comparison at the
dashboard targets. Per the Commander's explicit decision (given the slow per-session tail), I stopped at
RBR-full and PAUSED before the other four; the store is a clean "RBR wired + all others OLD-seeded"
baseline (OLD store pristine). The other four constructors (Ferrari/McLaren/Williams/Mercedes r1-15) are
a bounded, RESUMABLE continuation in the same store: `py scripts/repopulate_g3wired_store.py --resume`.
The Commander will decide continue-now vs G4-on-RBR-first.
