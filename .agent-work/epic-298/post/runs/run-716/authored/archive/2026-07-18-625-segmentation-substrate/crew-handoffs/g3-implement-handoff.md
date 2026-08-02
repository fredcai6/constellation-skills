# Implementer Handoff

## Gate
g3 (execute.json: g3-implement) — F12 falsifiable gate (MANDATORY per launch order pre-ruling #4)

## Task
Build a held-out-circuit class-membership stability check: fit Gate 2's property mixture
independently on two non-overlapping circuit subsets (repeated across 5 seeded splits), and
measure whether the two independently-fit mixtures recover the SAME property classes.

## Protected Intent
This check MUST be able to fail. It exists to prove (or disprove) that Gate 2's
soft-membership substrate isn't overfitting circuit-specific noise. A check that is
structurally guaranteed to pass regardless of input is worthless — the discriminating test
below is the load-bearing proof that it isn't. **A FAIL verdict on the real data is a
complete, valid, reportable outcome of this gate — do not weaken the check, adjust the
threshold, or change the split to force a PASS if the real run comes back FAIL.**

## Test Mode
Test-after, synthetic fixtures for the discriminating test; the real-data run is a script
invocation (evidence artifact), not itself a pytest assertion of PASS.

## Close Criteria
- New `src/physics/layer2/mixture_stability.py`:
  - `hungarian_match(means_a: np.ndarray, means_b: np.ndarray) -> np.ndarray` — shape `(k,)`
    permutation array (assumes `means_a`/`means_b` have the SAME `k`; if the two independently
    fit mixtures select DIFFERENT `k` for the two halves of a split, that split's
    `component_agreement_stat` should be treated as `float("inf")` / an automatic FAIL for
    that split, NOT an error — a `k`-mismatch is itself instability evidence, document this
    explicitly). Use `scipy.optimize.linear_sum_assignment` on the pairwise Euclidean
    distance matrix between `means_a` and `means_b` (both already in the SAME standardized
    space — see note below on cross-fit standardization).
  - `component_agreement_stat(fit_a: "MixtureFit", fit_b: "MixtureFit") -> float` — mean
    Euclidean distance between Hungarian-matched component means. IMPORTANT: `fit_a` and
    `fit_b` each carry their OWN `StandardScaler` (Gate 2's `MixtureFit.scaler`, fit on their
    own half's data) — comparing raw `means_` from two differently-scaled fits is not
    apples-to-apples. Pick ONE principled resolution and document it in the docstring: either
    (a) refit both fits' means back into a SHARED standardization (e.g. re-standardize both
    halves' raw descriptors together using ONE scaler before either fit, so `fit_a`/`fit_b`
    already share a common scale — this may mean this function operates on `MixtureFit`s
    that were fit with a shared external scaler rather than each fitting its own, which is a
    legitimate deviation from Gate 2's default `fit_property_mixture` behavior for THIS
    specific comparison use case), or (b) inverse-transform each fit's standardized means back
    to RAW (radius, lateral_g) units via each fit's own scaler before comparing (physically
    meaningful units, no shared-scaling assumption needed). Either is acceptable; (b) is
    probably simpler — choose and document which.
  - `F12_AGREEMENT_THRESHOLD` — a named module-level constant. Choose a value BEFORE running
    the real-data check in this same gate (not after seeing the real result) and state a
    one-line rationale for the chosen value/units in the module docstring (e.g. if using raw
    units per resolution (b) above, a threshold in meters for radius-distance and g-units for
    lateral_g-distance, or a combined normalized distance — your call, just be principled and
    state it BEFORE running real data).
  - `SplitResult` (per-split record: statistic value, `fit_a.k`, `fit_b.k`, pass/fail) and
    `StabilityResult` (dataclass: `splits: list[SplitResult]`, `mean_statistic: float`,
    `min_statistic: float`, `max_statistic: float`, `n_pass: int`, `n_splits: int`,
    `headline_verdict: str` — `"PASS"` if `n_pass == n_splits` else `"FAIL"`, or choose a
    majority-vote rule and document it — your call, document the rule chosen).
  - `check_holdout_stability(descriptors_by_circuit: dict[str, np.ndarray], n_splits: int = 5,
    base_seed: int = 42) -> StabilityResult` — `descriptors_by_circuit` maps `gp_name ->
    np.ndarray[N,2]` of that circuit's (radius, lateral_g) rows (already computed via Gate 1's
    `corner_descriptors.descriptors_from_frame`, upstream of this function — this function
    takes descriptors, not raw DB rows, so it stays unit-testable with synthetic fixtures with
    NO DB access). For each split `i` in `range(n_splits)`: seed `base_seed + i`, deterministic
    shuffle+split of the circuit NAMES (not rows) into two non-overlapping halves (as close to
    50/50 as the circuit count allows), pool all rows from each half's circuits into one
    descriptor array per half, run Gate 2's `fit_property_mixture` independently on each half,
    compute `component_agreement_stat`, record a `SplitResult`. Return the aggregated
    `StabilityResult`.
- **MANDATORY discriminating unit test** (this is the single most important test in this
  gate): two synthetic scenarios —
  1. Both halves drawn from the SAME generator (e.g. same 2-3 fixed Gaussian blobs, just
     different random draws/circuit groupings) — assert the resulting `StabilityResult`
     headline verdict is `"PASS"`.
  2. The two halves drawn from DELIBERATELY SHIFTED generators (e.g. blob means shifted by a
     magnitude clearly larger than `F12_AGREEMENT_THRESHOLD`) — assert the headline verdict is
     `"FAIL"`.
  Both must be exercised with `check_holdout_stability` itself (not just
  `component_agreement_stat` in isolation) — construct `descriptors_by_circuit` dicts with
  enough fake circuit names/rows to drive a real split.
- New `scripts/f12_held_out_stability.py`: a CLI that (1) connects to
  `data/damage_integrals.db` (absolute path passed via `--db` flag, default
  `C:/Programs/f1Brainz/data/damage_integrals.db` — READ-ONLY, do not write to this DB), loads
  the full `grip_bin_obs` table (`SELECT gp_name, mu_lat_p90, v_mean FROM grip_bin_obs`), (2)
  groups by `gp_name`, applies Gate 1's `corner_descriptors.descriptors_from_frame` per
  circuit group to build `descriptors_by_circuit`, (3) runs `check_holdout_stability`, (4)
  writes the FULL result (every split's statistic, the headline verdict, `F12_AGREEMENT_
  THRESHOLD`'s value, the circuit list and how many circuits/rows went into each half of each
  split, a timestamp) to `.agent-work/625-segmentation-substrate/artifacts/
  f12_holdout_stability.json`. Print a one-line human-readable summary to stdout. **Run this
  script for real** against the real DB as part of this gate — do not just write the script,
  execute it and report the actual verdict (PASS or FAIL) honestly in your IMPLEMENTER_RESULT.
  A FAIL is a complete, acceptable outcome — report it plainly, do not characterize it as a
  bug or try additional splits/thresholds to flip it to PASS.

## Allowed Scope
`src/physics/layer2/mixture_stability.py` (new), `scripts/f12_held_out_stability.py` (new),
`tests/unit/physics/layer2/test_mixture_stability.py` (new),
`.agent-work/625-segmentation-substrate/artifacts/f12_holdout_stability.json` (generated
evidence artifact — this path is git-tracked in this repo, per Deliverable Path Check below).

## Specific Exclusions
Do not modify `src/physics/layer2/property_mixture.py`'s selection logic (reuse
`fit_property_mixture`/`MixtureFit` exactly as Gate 2 built them — this gate composes Gate 2,
it does not change it). Do not write to `data/damage_integrals.db` (read-only). Do not touch
`circuits.yaml` or any production default. No `evo_predictor`/`latent_power`/`compound_prior`
imports.

## Constraints
- `constraint:physics_region_no_evo_import`.
- `constraint:canonical_data_source` — the real-data run reads `data/damage_integrals.db`
  (SQLite) via the absolute path, never a live FastF1 call.
- `F12_AGREEMENT_THRESHOLD` chosen and documented BEFORE the real run — the reviewer will
  check the module docstring's rationale reads as principled-before-the-fact, not
  reverse-engineered from the real result.
- The real-data run's verdict (PASS or FAIL) is reported exactly as computed — no
  post-hoc threshold/split adjustment to change it.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — new `mixture_stability.py`, module;
  `data/damage_integrals.db` `grip_bin_obs` table (read-only, absolute path
  `C:/Programs/f1Brainz/data/damage_integrals.db` — NOT present in this worktree, it is
  untracked/gitignored in the main checkout — always use the absolute path, never assume a
  worktree-local copy exists).
- **Capability:** F12 falsifiable gate — held-out-circuit class-membership stability
  (MANDATORY, launch order pre-ruling #4).
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`,
  `constraint:canonical_data_source`.
- **Decision anchors:** pre-ruling #4 (falsifiable gate mandatory); `circuits.yaml`'s
  `downforce` field is explicitly RULED OUT as the independent-proxy alternative (provisional/
  low-trust) — this gate uses held-out-circuit stability, not that proxy.
- **Evidence expectations:** the discriminating test (same-generator PASS, shifted-generator
  FAIL) is the load-bearing proof this check can fail; the real-data run's honest verdict is
  the gate's actual deliverable.
- **Map confidence flags:** `grip_bin_obs.bin` is per-lap-normalized, not a stable
  cross-session arc-length index (see MISSION_FRAME.md Map Confidence) — irrelevant to THIS
  gate specifically (you're pooling per-circuit descriptor rows, not relying on bin position
  identity), noted for completeness only.

## Deliverable Path Check
- **Committed** — `src/physics/layer2/mixture_stability.py`; `git check-ignore -v` exited 1 (not ignored). New file.
- **Committed** — `scripts/f12_held_out_stability.py`; exited 1 (not ignored). New file.
- **Committed** — `tests/unit/physics/layer2/test_mixture_stability.py`; exited 1 (not ignored). New file.
- **Committed** — `.agent-work/625-segmentation-substrate/artifacts/f12_holdout_stability.json`; exited 1 (not ignored) — this repo tracks `.agent-work/`, so this generated evidence artifact IS meant to be committed (unlike a typical gitignored `.agent-work` convention elsewhere — verified for THIS repo specifically).

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_mixture_stability.py -v` — full output, all
  PASS, including both discriminating-test scenarios explicitly named in the output.
- The actual stdout transcript of running `scripts/f12_held_out_stability.py` against the real
  DB, plus the resulting `f12_holdout_stability.json` content pasted in full in your
  IMPLEMENTER_RESULT.
- State plainly: how many circuits were in `grip_bin_obs`, how many rows survived
  `descriptors_from_frame`'s NaN/non-positive guard, and the final headline verdict.

## Verification Commands

```bash
cd /c/Programs/f1-625
py -m pytest tests/unit/physics/layer2/test_mixture_stability.py -v
py scripts/f12_held_out_stability.py --db C:/Programs/f1Brainz/data/damage_integrals.db
```

## Suggested Model Tier
Stronger — this is the mandatory falsifiable gate; get the statistics right, and the honesty
of the real-data verdict matters more than in any other gate this run.

## Authority
CONVERGED_PLAN.md Gate 3 (with cold-critic disposition #3 baked in — 5 seeded splits, not a
single split) governs this gate's shape. The exact `F12_AGREEMENT_THRESHOLD` value and the
standardization-reconciliation approach ((a) vs (b) above) are yours to choose and document —
these are implementation-detail decisions within your latitude, not decisions to escalate.
Whether the real-data run comes back PASS or FAIL is NOT yours to adjust — report it exactly.

## Stop Conditions
Stop and return if: `data/damage_integrals.db` is unreachable at the given absolute path (do
not silently fall back to a different/fabricated dataset); Gate 2's `fit_property_mixture`/
`MixtureFit` don't match what this handoff describes (report the actual signature); a decision
outside this handoff's scope is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced (INCLUDING the full real-data verdict and JSON content), assumptions used, stop
conditions hit, out-of-scope observations, workflow feedback. Write it to
`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g3-implement-result.md`
before ending your turn, and also return it as your final assistant text response.
