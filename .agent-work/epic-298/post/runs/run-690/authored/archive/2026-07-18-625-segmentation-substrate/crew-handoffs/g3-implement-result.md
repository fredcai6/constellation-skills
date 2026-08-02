# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3 (execute.json: g3-implement)` — F12 falsifiable gate: held-out-circuit class-membership
stability (MANDATORY, launch order pre-ruling #4)

## Completed slice
New `src/physics/layer2/mixture_stability.py` implementing the held-out-circuit stability
check (`hungarian_match`, `component_agreement_stat`, `SplitResult`/`StabilityResult`,
`check_holdout_stability`), a mandatory discriminating unit test suite proving the check can
FAIL as well as PASS, and a new CLI `scripts/f12_held_out_stability.py` that was **run for
real** against `C:/Programs/f1Brainz/data/damage_integrals.db`. The real-data verdict is
**FAIL** — reported exactly as computed, with no post-hoc adjustment.

## Scope
**Files changed:**
- `src/physics/layer2/mixture_stability.py` (new)
- `scripts/f12_held_out_stability.py` (new)
- `tests/unit/physics/layer2/test_mixture_stability.py` (new — 8 cases)
- `.agent-work/625-segmentation-substrate/artifacts/f12_holdout_stability.json` (generated
  evidence artifact, git-tracked per this repo's `.agent-work/` convention)

**Specific exclusions touched:** no — `src/physics/layer2/property_mixture.py` was not
modified (`git diff` on that file shows no changes from this gate; `fit_property_mixture` is
imported and called with its default signature, never edited). `data/damage_integrals.db` was
never written to (connected via a `sqlite3` URI with `?mode=ro`, which fails writes at the
driver level, not just by convention — verified directly, see Evidence). No
`evo_predictor`/`latent_power`/`compound_prior` imports anywhere in the new files (grep
verified, see Evidence). No `circuits.yaml` or other production-default touched.

## Behavior changed
Yes — new capability only (no existing module edited). `mixture_stability.py` is a pure
statistical core (no DB I/O); `scripts/f12_held_out_stability.py` is the only piece that reads
the real DB, and only reads (never writes).

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — new `mixture_stability.py`
  module (`hungarian_match`, `component_agreement_stat`, `SplitResult`, `StabilityResult`,
  `check_holdout_stability`, `RADIUS_SCALE_M`, `LATERAL_G_SCALE`, `F12_AGREEMENT_THRESHOLD`,
  all public); new `scripts/f12_held_out_stability.py` CLI reading
  `data/damage_integrals.db`'s `grip_bin_obs` table read-only.
- **Capabilities added/changed/affected:** F12 falsifiable gate (new, now exercised) —
  held-out-circuit class-membership stability across 5 seeded 50/50 circuit-name splits, per
  launch-order pre-ruling #4 and CONVERGED_PLAN.md's cold-critic disposition #3 (5 splits, not
  1). This IS the mandatory gate deliverable itself.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored
  (grep-verified, zero matches). `constraint:canonical_data_source` — honored (real-data run
  reads `data/damage_integrals.db` via the absolute path only, read-only URI connection, no
  FastF1 call anywhere in the new code).
- **Decision candidates / resolved decisions:** cross-fit-standardization ambiguity (handoff's
  resolution (a) vs (b)) resolved as **(b)**: inverse-transform each independently-fit
  `MixtureFit`'s standardized `gmm.means_` back to raw `(radius_m, lateral_g)` units through
  that fit's own `scaler`, then combine via two fixed, pre-registered physical normalization
  constants (`RADIUS_SCALE_M = 50.0` meters, `LATERAL_G_SCALE = 0.5` g) chosen from domain
  magnitude alone, before any real-data run. `F12_AGREEMENT_THRESHOLD = 1.0` in that
  combined-normalized space, documented with rationale in the module docstring, chosen before
  the real run. Headline-verdict rule: strict all-splits-must-pass (`n_pass == n_splits`), not
  majority-vote — documented as a deliberate choice given this is the mandatory gate.
  `k`-mismatch between a split's two halves is treated as `float("inf")` (automatic FAIL for
  that split), never an exception. **NOTE:** CONVERGED_PLAN.md's terse Gate-3 line (`"mean
  Euclidean distance between matched STANDARDIZED component means"`) reads as implying
  resolution (a); the more detailed and more current handoff explicitly reopened this exact
  ambiguity and granted latitude to choose either — resolution (b) was chosen per the
  handoff's own steer ("(b) is probably simpler"). Flagged here for Cartographer/Commander
  awareness in case the terser CONVERGED_PLAN phrasing needs a one-line reconciliation edit.
- **Claims/evidence produced:** THE headline claim of this gate — **the real-data F12 check
  FAILS**: across all 5 seeded circuit-name splits against the full `grip_bin_obs` table (22
  circuits, 612,615 rows), `fit_property_mixture` selected a *different* `k` on the two halves
  of *every single split* (4v6, 6v2, 4v6, 5v3, 3v4) — the two independently-fit mixtures never
  even agreed on how many property classes exist, let alone where they sit. This is a clean,
  unambiguous instability finding (not a borderline pass/fail near the threshold) — every split
  hit the automatic `k`-mismatch FAIL path before the distance-threshold comparison was ever
  reached. Full per-split detail (seeds, `k_a`/`k_b`, circuit membership, row counts) is in the
  committed JSON artifact and pasted in full below.
- **Trust limitations / drift found:** the FAIL verdict itself is new evidence for
  Cartographer/Commander to route: Gate 2's soft-membership property mixture, fit on the real
  `grip_bin_obs` data, does not currently pass the mandatory falsifiability check — before this
  substrate is treated as reliable for any downstream (Gate 4 rollup, future callers), the
  `k`-instability finding needs disposition (e.g. investigate whether `k_range=(2,6)`'s BIC
  selection is simply too sensitive at this row count, whether pooling strategy needs revision,
  or whether the substrate needs a different selection rule) — this implementer run's scope was
  to report the verdict honestly, not to diagnose or fix it.
- **Triage candidates:** the `k`-instability finding above is a strong triage candidate for a
  follow-up issue (root-cause the BIC/support-floor selection's sensitivity to circuit
  composition at ~300k-row half-pool scale) — flagged for Commander/Cartographer, not filed
  here (out of this gate's scope).

## Test mode
**Required:** `test-after` (handoff: "synthetic fixtures for the discriminating test; the
real-data run is a script invocation (evidence artifact), not itself a pytest assertion of
PASS")
**Satisfied:** yes — TDD red→green was additionally run for the module (test file written
first, observed failing via `ModuleNotFoundError`, then implementation written to green), a
strict superset of the test-after minimum. The real-data script run is evidence-only, per the
handoff, and was executed for real (twice, reproducibly) rather than merely written.

## Evidence

```bash
cd /c/Programs/f1-625
py -m pytest tests/unit/physics/layer2/test_mixture_stability.py -v && py scripts/f12_held_out_stability.py --db C:/Programs/f1Brainz/data/damage_integrals.db
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- ...\python.exe
collecting ... collected 8 items

tests/unit/physics/layer2/test_mixture_stability.py::TestHungarianMatch::test_identity_when_already_aligned PASSED [ 12%]
tests/unit/physics/layer2/test_mixture_stability.py::TestHungarianMatch::test_recovers_permutation_when_rows_swapped PASSED [ 25%]
tests/unit/physics/layer2/test_mixture_stability.py::TestComponentAgreementStat::test_same_generator_gives_small_statistic PASSED [ 37%]
tests/unit/physics/layer2/test_mixture_stability.py::TestComponentAgreementStat::test_shifted_generator_gives_large_statistic PASSED [ 50%]
tests/unit/physics/layer2/test_mixture_stability.py::TestComponentAgreementStat::test_k_mismatch_returns_inf_not_error PASSED [ 62%]
tests/unit/physics/layer2/test_mixture_stability.py::TestCheckHoldoutStabilityDiscriminating::test_same_generator_all_circuits_gives_pass PASSED [ 75%]
tests/unit/physics/layer2/test_mixture_stability.py::TestCheckHoldoutStabilityDiscriminating::test_shifted_generator_two_circuits_gives_fail PASSED [ 87%]
tests/unit/physics/layer2/test_mixture_stability.py::TestCheckHoldoutStabilityDiscriminating::test_split_pools_rows_and_records_circuit_membership PASSED [100%]

============================== 8 passed in 10.06s ==============================
F12 held-out-circuit stability: FAIL (n_pass=0/5, mean_stat=inf, min=inf, max=inf, threshold=1.0, n_circuits=22, n_rows=612615) -> .agent-work\625-segmentation-substrate\artifacts\f12_holdout_stability.json
```

**Result:** `pass` (tests) / **FAIL** (real-data F12 verdict — a complete, valid, honestly
reported outcome per the handoff, not adjusted).

**How many circuits were in `grip_bin_obs`:** 22 (`n_circuits_in_grip_bin_obs`).
**How many rows survived `descriptors_from_frame`'s NaN/non-positive guard:** all 612,615 of
612,615 total rows survived (`n_rows_survived_descriptor_guard` == `n_rows_in_grip_bin_obs`) —
the real `mu_lat_p90`/`v_mean` data in `grip_bin_obs` contained no NaN/non-positive rows to
drop, so no rows were lost to that guard.
**Final headline verdict:** **FAIL** (`n_pass=0/5`).

Full `f12_holdout_stability.json` content (verbatim):
```json
{
  "timestamp_utc": "2026-07-18T05:29:59.701230+00:00",
  "db_path": "C:\\Programs\\f1Brainz\\data\\damage_integrals.db",
  "f12_agreement_threshold": 1.0,
  "radius_scale_m": 50.0,
  "lateral_g_scale": 0.5,
  "n_circuits_in_grip_bin_obs": 22,
  "n_rows_in_grip_bin_obs": 612615,
  "n_circuits_with_surviving_descriptors": 22,
  "n_rows_survived_descriptor_guard": 612615,
  "circuit_names": [
    "Abu Dhabi", "Australia", "Austria", "Azerbaijan", "Bahrain", "Brazil", "China",
    "Emilia Romagna", "Great Britain", "Hungary", "Italy", "Japan", "Las Vegas", "Mexico",
    "Miami", "Monaco", "Netherlands", "Qatar", "Saudi Arabia", "Singapore", "Spain",
    "United States"
  ],
  "n_splits": 5,
  "base_seed": 42,
  "mean_statistic": "Infinity",
  "min_statistic": "Infinity",
  "max_statistic": "Infinity",
  "n_pass": 0,
  "headline_verdict": "FAIL",
  "splits": [
    {"split_index": 0, "seed": 42, "statistic": "Infinity", "k_a": 4, "k_b": 6,
     "circuits_a": ["Qatar","Italy","Netherlands","United States","Las Vegas","Monaco",
                    "Emilia Romagna","China","Hungary","Azerbaijan","Abu Dhabi"],
     "circuits_b": ["Saudi Arabia","Brazil","Japan","Miami","Spain","Austria","Bahrain",
                    "Singapore","Australia","Mexico","Great Britain"],
     "n_rows_a": 283300, "n_rows_b": 329315, "passed": false},
    {"split_index": 1, "seed": 43, "statistic": "Infinity", "k_a": 6, "k_b": 2,
     "circuits_a": ["Brazil","Australia","Las Vegas","Emilia Romagna","United States","Italy",
                    "Singapore","Austria","Mexico","Great Britain","China"],
     "circuits_b": ["Spain","Japan","Netherlands","Saudi Arabia","Hungary","Miami","Qatar",
                    "Bahrain","Monaco","Abu Dhabi","Azerbaijan"],
     "n_rows_a": 244655, "n_rows_b": 367960, "passed": false},
    {"split_index": 2, "seed": 44, "statistic": "Infinity", "k_a": 4, "k_b": 6,
     "circuits_a": ["Abu Dhabi","Singapore","Hungary","Spain","Monaco","Saudi Arabia",
                    "Bahrain","Netherlands","Mexico","Italy","Las Vegas"],
     "circuits_b": ["Great Britain","United States","Azerbaijan","Japan","Qatar","Austria",
                    "Brazil","Australia","Miami","China","Emilia Romagna"],
     "n_rows_a": 344221, "n_rows_b": 268394, "passed": false},
    {"split_index": 3, "seed": 45, "statistic": "Infinity", "k_a": 5, "k_b": 3,
     "circuits_a": ["Bahrain","Miami","China","Spain","Japan","Mexico","Australia",
                    "Saudi Arabia","Italy","Netherlands","Great Britain"],
     "circuits_b": ["Monaco","Las Vegas","Hungary","Austria","United States","Azerbaijan",
                    "Emilia Romagna","Abu Dhabi","Brazil","Qatar","Singapore"],
     "n_rows_a": 323690, "n_rows_b": 288925, "passed": false},
    {"split_index": 4, "seed": 46, "statistic": "Infinity", "k_a": 3, "k_b": 4,
     "circuits_a": ["Singapore","United States","Italy","Abu Dhabi","Australia",
                    "Emilia Romagna","Saudi Arabia","Mexico","Miami","Austria","Bahrain"],
     "circuits_b": ["Hungary","Las Vegas","Qatar","Spain","China","Netherlands",
                    "Great Britain","Brazil","Japan","Monaco","Azerbaijan"],
     "n_rows_a": 294323, "n_rows_b": 318292, "passed": false}
  ]
}
```
(Two independent runs of the script — once via `py -m scripts.f12_held_out_stability`, once
via the handoff's exact `py scripts/f12_held_out_stability.py` form — reproduced the identical
verdict, per-split `k_a`/`k_b`, and circuit membership, confirming determinism.)

Additional evidence — `simplification_limits` on touched files (project norm):
```bash
py -m src.utils.simplification_limits --paths src/physics/layer2/mixture_stability.py scripts/f12_held_out_stability.py tests/unit/physics/layer2/test_mixture_stability.py
```
```
PASS (3 files checked)
```

`constraint:physics_region_no_evo_import` grep check:
```bash
grep -rn "evo_predictor\|latent_power\|compound_prior" src/physics/layer2/mixture_stability.py scripts/f12_held_out_stability.py tests/unit/physics/layer2/test_mixture_stability.py
```
```
(no output, exit 1 -- no matches)
```

Read-only DB connection verified (write attempt correctly rejected):
```bash
py -c "import sqlite3; con=sqlite3.connect('file:C:/Programs/f1Brainz/data/damage_integrals.db?mode=ro', uri=True); con.execute('CREATE TABLE t (x int)')"
```
```
sqlite3.OperationalError: attempt to write a readonly database
```

Deliverable-path check (project norm — not gitignored, real new files):
```bash
git status --short
```
```
?? scripts/f12_held_out_stability.py
?? src/physics/layer2/mixture_stability.py
?? tests/unit/physics/layer2/test_mixture_stability.py
```
(plus `.agent-work/625-segmentation-substrate/` already untracked as a whole directory, which
includes the new `artifacts/f12_holdout_stability.json`; this repo tracks `.agent-work/`
generated evidence artifacts per the handoff's Deliverable Path Check.)

## TDD evidence, if required
- Failing test observed: `py -m pytest tests/unit/physics/layer2/test_mixture_stability.py -v`
  → collection `ERROR`, `ModuleNotFoundError: No module named
  'src.physics.layer2.mixture_stability'` (before the module existed).
- Passing test observed: full green, 8/8 (see Evidence section above).
- Refactor while green: no separate refactor pass was needed; one implementation-quality fix
  was made before finalizing (see Assumptions: JSON `Infinity`-token serialization), applied
  before the final evidence run above, not after seeing it pass/fail.

## Docs/contracts touched
- none beyond the module's own docstring (no committed contract/schema doc governs this
  module).

## Assumptions
- **Cross-fit-standardization resolution: (b), raw units.** Documented at length in
  `mixture_stability.py`'s module docstring and under Map Impact above. Chosen per the
  handoff's own steer that (b) is "probably simpler," and because it avoids any deviation from
  Gate 2's `fit_property_mixture` default one-scaler-per-fit behavior.
- **`RADIUS_SCALE_M = 50.0` meters / `LATERAL_G_SCALE = 0.5` g / `F12_AGREEMENT_THRESHOLD =
  1.0`** — chosen from domain-magnitude reasoning alone (typical gaps between adjacent
  corner-radius/lateral-g property classes), fixed and documented in the module docstring
  BEFORE the real-data run. Not adjusted after seeing the FAIL result.
- **Headline-verdict rule: strict all-splits-must-pass** (`n_pass == n_splits`), not
  majority-vote — chosen because this is the mandatory F12 gate; a single unstable split is
  itself instability evidence and should not be averaged away.
- **JSON `Infinity`-token fix (implementation-quality, does not touch the verdict):**
  `json.dumps`'s default `allow_nan=True` emits bare `Infinity`/`-Infinity`/`NaN` tokens, which
  are a Python-only extension, not valid per RFC 8259 — a problem for an evidence artifact
  meant for downstream consumption (e.g. Gate 4's rollup script, per CONVERGED_PLAN item 6).
  Added a small `_json_safe` pass in the script that quotes these as strings
  (`"Infinity"`/`"-Infinity"`/`"NaN"`) before writing, verified the artifact round-trips through
  strict `json.load` (see Evidence). This was applied BEFORE the final evidence run, purely a
  serialization-correctness fix — it does not change `component_agreement_stat`'s numeric
  return value, the threshold, or the verdict logic in any way.
- **Direct-invocation `sys.path` bootstrap:** the handoff's exact Verification Command is
  `py scripts/f12_held_out_stability.py --db ...` (direct file invocation), but this repo's
  existing scripts (e.g. `scripts/grip_residual_trends.py`) document `py -m scripts.<name>`
  as their usage convention. Direct-file invocation only puts `scripts/` on `sys.path`, not the
  repo root, which breaks the `src.*` absolute imports. Added a small repo-root `sys.path`
  bootstrap at the top of `f12_held_out_stability.py` so BOTH invocation forms work — verified
  by running both forms for real against the DB (see Evidence: two independent runs,
  identical output).
- `SplitResult` carries `circuits_a`/`circuits_b`/`n_rows_a`/`n_rows_b` fields beyond the
  handoff's minimum listed set ("statistic value, fit_a.k, fit_b.k, pass/fail") — the handoff
  itself asked for "enough circuit/row-count fields for the script's JSON evidence needs" in
  the module's imperative context, and the script's Required Evidence explicitly asks for "how
  many circuits/rows went into each half of each split," so these fields were added to satisfy
  that requirement directly from `check_holdout_stability` rather than recomputing it
  separately in the script.

## Stop conditions hit
None — `data/damage_integrals.db` was reachable at the given absolute path; Gate 2's
`fit_property_mixture`/`MixtureFit` matched the handoff's description exactly (confirmed at
m0-context by reading the live source); no decision outside this handoff's scope was needed
(both open "your call" points — cross-fit-standardization resolution, threshold value — were
explicitly delegated to this implementer run by the handoff's Authority section).

## Out-of-scope observations
- The real-data FAIL verdict itself (Gate 2's soft-membership mixture is not stable across
  circuit-composition splits at the current `k_range=(2,6)`/support-floor settings) is a
  finding for Commander/Cartographer to route as a follow-up triage candidate — diagnosing or
  fixing the instability is explicitly out of this gate's scope (this gate's job was to build
  and honestly run the falsifiable check, not to make it pass).
- CONVERGED_PLAN.md's Gate-3 line phrasing ("mean Euclidean distance between matched
  STANDARDIZED component means") is terser than, and could be read as conflicting with, the
  handoff's more detailed (and more current) (a)/(b) resolution discussion — flagged for a
  possible one-line CONVERGED_PLAN reconciliation edit, not acted on here (out of this gate's
  authority to resolve a plan-document wording question).

## Workflow Feedback
- **Handoff gaps:** none material. The handoff was unusually thorough — it named the exact
  ambiguity (cross-fit standardization), offered both resolutions with tradeoffs, and
  explicitly pre-delegated the choice ("your call... Either is acceptable"). The one soft gap:
  CONVERGED_PLAN.md's own Gate-3 summary line uses different, terser wording ("standardized
  component means") than the handoff's detailed (a)/(b) discussion — not a contradiction in
  substance, but a future reader skimming only CONVERGED_PLAN could get a different
  implication than the handoff intends. Noted under Out-of-scope observations.
- **Context rediscovered:** this repo's scripts convention (`py -m scripts.<name>` rather than
  direct-file invocation, seen in `scripts/grip_residual_trends.py`'s own docstring) was not
  called out anywhere in the handoff, and the handoff's own Verification Command uses direct
  invocation — the two conventions conflict at the `sys.path` level. Resolved by making the new
  script work under both forms (see Assumptions) rather than picking one, so neither convention
  is silently broken.
- **Instructions improvised around:** none beyond the two documented, in-latitude "your call"
  choices (threshold/resolution) the handoff explicitly pre-authorized.
- **What would have made this easier:** noting the `py -m scripts.<name>` vs direct-file
  invocation split explicitly in `global-crew.md`/`windows.md` (alongside the existing `py`
  vs bare `python` launcher note) would save a future gate from rediscovering it — this repo's
  scripts are inconsistently invocable depending on which convention a given script's author
  assumed.

## Return status
`complete`
