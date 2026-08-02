# Implementer Handoff — g3-replication-implement

## Gate
g3-replication-implement (#668 instrument panel, epic #659) — **the load-bearing instrument.**
Worktree `C:/Programs/f1brainz-wt/epic659-668`, branch `epic659/668-instrument-panel`.
PINNED interpreter `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Task
Build **Instruments 2 + 3** in `src/physics/instrument_panel/replication.py` (+ tests):
(2) the **golf-corrected split-half replication** + a **σ-honesty check**, and (3) the
**per-class channel comparison**. PURE module, synthetic-tested, F12-INDEPENDENT (thresholds
are INJECTED params, not imported from any frozen module — G6 wires the frozen values later).

## Protected Intent (READ TWICE — this is the subtle-and-silent hazard)
Raw split-half replication FLATTERS by smuggling **overall driver skill** back into a per-class
residual. A mechanically-plausible-but-wrong correction can report a healthy replication that is
a pure **shared-class-structure artifact** with ZERO driver-utilization content. The correction
is LOAD-BEARING. It must be **DOUBLE-CENTERING**, and the synthetic falsifier must PROVE a
weaker correction fails.

## The golf-correction — DOUBLE-CENTERING (exact spec)
For a set of observations `v[d,c]` (driver d, severity class c) in one split-half:
`residual[d,c] = v[d,c] − driver_mean[d] − class_mean[c] + grand_mean`
(the standard two-way ANOVA interaction residual). This removes BOTH the driver main effect
(overall skill) AND the class main effect (shared class structure). What remains is the genuine
**driver×class interaction**. This is a pure DATA TRANSFORM (arithmetic on observations) — it is
**NOT** a fitted interaction term and adds NO model parameter, so owner ruling 4 (no interaction
terms / no bespoke model) is respected. Per-driver demean ALONE (removing only the driver mean)
is WRONG — it leaves the shared class main effect, which replicates trivially. Do not do that.

## Split-half mechanism (INJECTED unit — do not hardcode)
The split-half UNIT is registered in `.agent-work/668-instrument-panel/F12_PREREGISTRATION.md`
(primary: cross-circuit 2-vs-2 over the 4 available circuits; fallback: within-session
lap-parity). Structure the module so the split is **injected** — accept either two pre-split
observation sets (`half_a`, `half_b`) or a splitter callable — so cross-circuit and lap-parity
both plug in without a code change. Per class: double-center each half INDEPENDENTLY, then
compute the split-half **Pearson r of the per-driver interaction-residual profile** between the
two halves (correlation across drivers). Where the primary unit enumerates the 3 distinct 2v2
partitions, average r over them (leave this to the caller/param — the core takes two halves).

## Thresholds (INJECTED dataclass — F12-independent)
Define a frozen dataclass `ReplicationThresholds(threshold, min_support_n, r_floor_cap,
r_floor_support_ref, channel_tie_margin)` and a pure `r_floor(n, thresholds)` implementing
`threshold + (r_floor_cap − threshold) * clip((r_floor_support_ref − n)/r_floor_support_ref, 0, 1)`.
Tests inject the proposal defaults (threshold=0.5, min_support_n=15.0, r_floor_cap=0.7,
r_floor_support_ref=100.0, channel_tie_margin=0.1). DO NOT import a frozen REPLICATION_* module
(it is not minted yet). A class whose per-half resolved support < min_support_n in either half
is EXCLUDED before correlating.

## σ-honesty check (OUT-OF-SAMPLE — non-negotiable)
Given cells/observations carrying a stated σ, check whether the HELD-OUT half's observed value
falls within the predictive interval built from the OTHER half's estimate — an OUT-OF-SAMPLE
coverage test (held-out half or LOO), NEVER self-referential/self-weighted (a self-inclusive
coverage is structurally blind to σ-too-small; repo lesson:loo-residual-diagnostic-over-self-weighted-predictor).
Build the interval with `predictive_t` from `src/common/student_t.py`
(`predictive_t(mu, sigma, n_eff, nu_loss=DEFAULT_NU_LOSS, rule=FormulaRule()).interval(level)` /
`.cdf` for PIT) — Student-t, NON-Gaussian (owner ruling 5). Report empirical out-of-sample
coverage vs nominal.

## Channel comparison (registered decision rule)
Run the replication per class in BOTH channels: `utilization` (value = time_deficit_s) and
`energy` (value = deployment_share). Per class, the channel with the higher split-half r
**earns the join weight there** iff (a) its r ≥ r_floor(n) AND (b) it beats the other channel
by `channel_tie_margin` (Δr). If neither clears r_floor → class "unresolved, no channel earns
weight" (no-frame-kill). If both clear but within the tie margin → default to `utilization`
(time-deficit, the driver-aligned channel). Return a per-class winner/verdict object.

## no-valid-split branch (no-frame-kill)
A class with insufficient resolved support (< min_support_n per half) or < 2 resolved units per
half returns an explicit `unmeasurable` verdict (a COMPLETE result — zero signal size is a
success, never a fabricated number). Never raise/skip silently.

## THREE-ARM synthetic falsifier (the deliverable that proves correctness)
Extend `scripts/pooling_imbalance_validation_665.py`'s generative model with a TRUE driver×class
INTERACTION term (the existing model is additive with NO interaction — you must add one). Then
in `tests/unit/physics/instrument_panel/test_replication_channel.py`:
- **Arm (a) pure overall-skill:** `v = grand + driver_effect[d] + noise` (no class, no
  interaction). After double-centering, cross-half r ≈ 0 → verdict does NOT replicate. Assert.
- **Arm (b) pure shared-class, ZERO interaction:** `v = grand + class_effect[c] + noise` (class
  effect SHARED across drivers). After double-centering (removes class main effect), r ≈ 0 →
  does NOT replicate. Assert. **This is the arm that distinguishes a correct correction from a
  broken one.**
- **Arm (c) injected interaction:** `v = grand + driver + class + strength*interaction[d,c] +
  noise`. After double-centering, residual ≈ interaction → cross-half r is HIGH → replicates.
  Assert r ≥ threshold and recovers monotonically with `strength`.
- **NEGATIVE-CONTROL / self-validation test:** implement per-driver-demean-ONLY as a helper and
  assert it FAILS arm (b) (reports HIGH r on pure shared-class) — proving the falsifier actually
  discriminates and that double-centering is necessary, not cosmetic.
- **σ-honesty tests:** correct stated σ → out-of-sample coverage ≈ nominal (within CI);
  understated σ → coverage materially BELOW nominal (detected). Confirm the interval is
  Student-t (exercise the heavy-tail path), not ±1.96σ.

## Allowed Scope
CREATE `src/physics/instrument_panel/replication.py`,
`tests/unit/physics/instrument_panel/test_replication_channel.py`. READ-ONLY reuse:
`src/physics/layer2/pooling.py`, `src/common/student_t.py`,
`scripts/pooling_imbalance_validation_665.py`, `src/physics/fingerprint/address.py`
(FINGERPRINT_CHANNELS). May add a small synthetic-generator helper (with interaction) either in
the test file or a test-support module under tests/.

## Specific Exclusions
- Do NOT read any real DB (F12-independent, synthetic-only). Do NOT import a frozen REPLICATION_*
  module (not minted). Do NOT bake threshold literals into the module logic — inject them.
- Do NOT add a fitted interaction term to any MODEL (double-centering is a data transform, fine).
- Do NOT touch #660/#664/#666/#667 producers or any `f1_data_*.db`.
- Do NOT route through the #667 join (`join.py`) — the panel reads cells/observables directly.

## Constraints
- Pure/deterministic (seed the RNG in tests). Student-t coverage (no Gaussian). Double-centering
  (not per-driver demean). Out-of-sample σ-honesty. Thresholds injected. pyright-0.
- `predictive_t` signature: `predictive_t(mu, sigma, n_eff, *, nu_loss, rule)`; `PredictiveT`
  has `.interval(level)`, `.cdf(x)`, `.ppf(q)`. `DEFAULT_NU_LOSS`, `NU_FLOOR`, `FormulaRule`
  are in `src/common/student_t.py`.

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/pooling.py` (additive, no interaction); `src/common/student_t.py` (predictive_t); `scripts/pooling_imbalance_validation_665.py` (extend generator); `src/physics/instrument_panel/` (new).
- **Capability:** driver-utilization measurement (replication sizing).
- **Constraints:** constraint:lowest-dimensionality; constraint:no-baked-normality; constraint:no-frame-kill.
- **Decision anchors:** decision:golf-correction-is-DOUBLE-CENTERING — remove driver AND class main effects; replicate interaction residual on raw observations.
  `@grade: settled/measured · leans g3`
- **Evidence:** claim:golf-correction-removes-skill (3-arm + negative control); claim:coverage-is-distribution-not-gaussian; σ-honesty out-of-sample.

## Deliverable Path Check
- **Committed** — `src/physics/instrument_panel/replication.py`,
  `tests/unit/physics/instrument_panel/test_replication_channel.py` (+ any test-support module);
  verified `git check-ignore` exits 1. New files show in `git status`, not `git diff` until staged.

## Required Evidence
- LOAD-BEARING: the pytest output showing ALL arms pass INCLUDING the negative-control test that
  proves per-driver-demean-only FAILS arm (b). Quote the negative-control assertion.
- LOAD-BEARING: the σ-honesty test showing understated σ is detected out-of-sample.
- LOAD-BEARING: pyright-0 on the new module.
- Confirmatory: channel-comparison decision-rule unit test (winner/tie/unresolved paths).

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_replication_channel.py -q
```

## Suggested Model Tier
stronger — this is the load-bearing correctness hazard of the whole panel; the double-centering
vs per-driver-demean distinction and the 3-arm+negative-control falsifier must be exactly right.

## Authority
Double-centering (not per-driver demean), out-of-sample σ-honesty, injected thresholds, and the
3-arm+negative-control falsifier design are DECIDED (commander, from the cold-critic-forced
correction). Do not simplify them away. If double-centering seems to leave "no signal to
replicate" on some arm, that is the point for the null arms — do not add signal to make a test
pass. STOP and return if a real DB read or a frozen-module import seems required.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a real DB / frozen-module import seems
needed, the negative-control cannot be made to fail arm (b) (means the correction is wrong —
surface it), or an interaction term in a model seems required.

## Return Format
Return IMPLEMENTER_RESULT (completed slice, files, evidence incl. the negative-control assertion,
assumptions, stops, out-of-scope, workflow feedback). WRITE it to
`.agent-work/668-instrument-panel/crew-results/g3-replication-implement-result.md` before ending
your turn — that file IS the deliverable.
