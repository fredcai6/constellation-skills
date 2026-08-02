# Implementer Handoff — G6 (held-out gate harness, both channels)

## Gate
`g6` (execute.json)

## Task
Build the FROZEN held-out gate harness that tests the load-bearing falsifiable claim (does
observation-property representativeness weighting BEAT clock-distance-to-Q on held-out weekends).
Deliver a TESTABLE core module `src/physics/layer2/fp_gate.py` + a thin CLI `scripts/fp_representativeness_gate.py`.
G6 builds + tests the harness on a SMALL SYNTHETIC FIXTURE only — NO real compute here (that is G7).

## Protected Intent
The harness must encode `GATE_PROTOCOL.md` EXACTLY (read
`.agent-work/513-fp-fits/GATE_PROTOCOL.md` in full — it is the frozen contract). The test's discriminating
power is in the DIVERGENT cases; a harness that pools everywhere clock and learned coincide is wrong.
Honest-null (learned ≤ clock) is a first-class PASS-able outcome — the harness must report it straight.

## Test Mode
TDD required. All tests run on a SYNTHETIC fixture (no telemetry, no real DB).

## Close Criteria — the harness core (`fp_gate.py`) must implement + test:
1. **Observation assembly** `build_gate_observations(...)`: per (weekend, car, session) — a per-car grip
   capability (PRIMARY, mass-free: `apex_pace`/lateral grip from apex observations) and, per FP
   observation, its representativeness features (from `fp_representativeness.observation_features` over
   `fp_lap_latent`) + a clock-distance-to-Q value (session-start-time gap to Q). SECONDARY: a per-car
   longitudinal power-to-weight capability carrying the fp_mass intercept σ. Injectable extractor seam so
   G7 supplies the real apex/fit extractor and tests supply a synthetic one.
2. **Two arms** `clock_weight(obs)` (parameter-free clock-distance-to-Q; nearer=higher) and
   `learned_weight(obs, params)` (fit `fp_representativeness.WeightParams` on TRAIN weekends only).
3. **LOWO cross-validation** `run_lowo(weekends, ...)`: leave-one-weekend-out; fit learned params on the
   other 15, predict held-out weekend's per-car Q grip from its weighted FP observations under each arm;
   per-weekend metric (Spearman + centred RMSE across cars). ALL normalizers fit within-train-fold only
   (leakage guard F6). Q-capability is the target ONLY — never enters features/weights.
4. **Paired significance** (F7): paired bootstrap (default 10k) over the per-weekend (learned − clock)
   deltas → mean delta + 95% CI + PASS/HONEST-NULL verdict.
5. **Divergent-case read** (F4): identify observations where |w_learned − w_clock| is in the top tercile;
   report the verdict READ ON those. If the divergent set is thin (clock≈learned everywhere) → INCONCLUSIVE.
6. **Emergence audit** (F3): residualize track_evolution vs session identity; confirm the fitted learned
   weighting still responds to within-session residual features (else it flags calendar-in-disguise).
7. **Sandbagging demo** (F8): given a per-car-weekend sandbagging proxy (largest FP-best→Q pace jump),
   assert `learned_weight < clock_weight` on that car-weekend's FP observations (direction from the protocol).
8. **Both channels reported**: PRIMARY (grip) verdict AND SECONDARY (longitudinal) verdict — the SECONDARY
   at a MATCHED fp_mass-σ stratum or labeled "confounded, not evidential" (F1). Honest-null on EITHER is
   reported straight (Admiral directive: SECONDARY reported whichever way it lands).

## Fixture tests (must include)
- A POSITIVE fixture: synthetic weekends where representativeness genuinely diverges from clock (early-session
  low-fuel soft push laps are the Q-representative ones) → the harness DETECTS learned beats clock on held-out.
- A NULL fixture: synthetic weekends where clock IS the best signal → the harness correctly reports honest-null
  (learned does NOT beat clock) — proves the harness is not rigged to always pass.
- A LEAKAGE test: confirm no held-out Q info reaches the learned weights (e.g. shuffling held-out Q targets
  does not change the learned params fit on train).

## Allowed Scope
- New `src/physics/layer2/fp_gate.py`, new `scripts/fp_representativeness_gate.py` (thin CLI over the core).
- New `tests/unit/physics/layer2/test_fp_representativeness_gate.py` (EXACT path — the gate's own check).
- Import `fp_representativeness`, `fp_lap_latent`, `apex_extract`/`capability` (for the real extractor seam)
  — but the real extraction runs in G7; here use the injectable seam + synthetic fixtures.

## Specific Exclusions
- NO real compute / real telemetry / real DB reads in this gate — synthetic fixtures only.
- Do NOT hardcode any session weight — weighting comes ONLY from `fp_representativeness`.
- Do NOT read/modify/commit any data/*.db.

## Constraints
- physics-region: no evo/latent_power/compound_prior/fastf1 imports.
- Encode GATE_PROTOCOL.md exactly; the split/metric/arms are FROZEN — do not invent new ones.
- Leakage-free (train/held-out disjoint; normalizers within-train-fold).
- Keep files < 1000 lines; `py -m src.utils.simplification_limits --baseline --paths <touched>` PASS.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — new `fp_gate.py`; `struct:physics` — new gate CLI script.
- Capability: the frozen held-out falsifiable test (F10).
- Constraints: leakage (F6), divergent-case read (F4), emergence (F3), both-channels honest report.

## Deliverable Path Check
- Committed — `src/physics/layer2/fp_gate.py`, `scripts/fp_representativeness_gate.py`,
  `tests/unit/physics/layer2/test_fp_representativeness_gate.py`. Tracked.

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_fp_representativeness_gate.py -q` green (paste summary).
- The POSITIVE + NULL + LEAKAGE fixture tests explicitly.
- `py -m src.utils.simplification_limits --baseline --paths <touched>` PASS.
- `git status --short data/` clean.

## Verification Commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_representativeness_gate.py -q && py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/fp_gate.py
```

## Suggested Model Tier
`stronger` — the harness encodes the whole falsifiable protocol; leakage-freeness + the positive/null
fixture discrimination are load-bearing.

## Authority
The protocol (GATE_PROTOCOL.md) is FROZEN — implement it, do not redesign it. The injectable-extractor seam
(so G7 supplies the real apex/fit extractor) is DECIDED (Ship I). You choose code structure; do not weaken
the leakage guard or the divergent-case read.

## Stop Conditions
Stop and return if the protocol cannot be encoded as frozen, a leakage-free LOWO cannot be built, or the
null fixture cannot be made to correctly report honest-null.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode, evidence (incl. positive/null/leakage
fixtures), assumptions, stop conditions, out-of-scope observations, workflow feedback.
