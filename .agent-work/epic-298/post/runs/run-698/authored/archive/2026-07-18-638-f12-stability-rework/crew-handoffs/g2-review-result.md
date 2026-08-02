# Review Result — G2 (log-space property mixture + support-driven-k fix, #638)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2-review` — independently verify the Phase-1 corner property-class mixture rework so the
mandatory F12 held-out-circuit stability gate earns a GENUINE (non-gamed) PASS.

## Result
`APPROVE`

All 11 survey checks recorded pass; engine consolidated `verdict=APPROVE findings=0`. Survey:
`.agent-work/638-f12-stability-rework/g2-review/review.json`. Fowler record:
`.agent-work/638-f12-stability-rework/g2-review/fowler_pass.json` (verify_fowler_pass.py exit 0).

## Handoff compliance
All four commander-decided changes present and correct, matching DIAGNOSIS.md exactly:
1. **Log-space fit encapsulated** — `_to_log_space` (property_mixture.py:58) log10s column 0 only;
   applied in `fit_property_mixture` *before* `scaler.fit_transform` (line 152) and in
   `posterior_membership` *before* `scaler.transform` (line 208). Callers pass RAW descriptors;
   log space never leaks. `MixtureFit` dataclass shape unchanged, so
   `scaler.inverse_transform(gmm.means_)` yields `(log10 radius, lateral_g)` — verified by
   `test_inverse_transform_of_means_yields_log_radius`.
2. **OR support criterion** — `(weights_ >= 0.05) | (weights_ * N >= 150)` (lines 166-168); a k is
   a candidate only if `supported.all()`.
3. **`k_range` default `(2, 4)`** (line 101).
4. **Gate `LOG_RADIUS_SCALE = 0.30`** (mixture_stability.py:86), replacing `RADIUS_SCALE_M = 50`;
   `_normalize`/`component_agreement_stat` compare in log-radius units.

## Scope drift
Clean. Exactly 5 files changed (`git status --porcelain`). Excluded files
(`corner_descriptors.py`, `regime_rollup.py`, `segment_classifier.py`, `build_regime_rollup.py`)
NOT in the diff — their raw-descriptor callers keep working through the encapsulated transform
(30 caller tests green). No evo import in either physics.layer2 module
(`constraint:physics_region_no_evo_import` honored). `scripts/f12_held_out_stability.py` change is
import + print + JSON-key rename only (no logic).

## Evidence verdict
Independently reproduced (not trusted from the result doc):
- `test_property_mixture.py test_mixture_stability.py -q` → **23 passed** (6.46s / 6.71s).
- Caller spot-check `test_regime_rollup.py test_observability_router.py -q` → **30 passed** (3.75s).
- `py -m src.utils.simplification_limits --paths <both src files>` → **PASS (2 files checked)**.
- `TestSupportDrivenK` + `TestLargeNDoesNotOverSelectK` → **4 passed**.

Test mode `test-after` (synthetic/unit, no DB) is appropriate for this gate; the ~6-min real-data
5/5 F12 is correctly deferred to G3 and not required here.

### F12 falsifiability — LOAD-BEARING, independently proven
I perturbed the model, not just confirmed the green test. Inserted `return 0.0` at the top of
`component_agreement_stat` (masks all component disagreement), then ran
`test_shifted_generator_two_circuits_gives_fail`. It **FAILED** as required:
`assert result.headline_verdict == "FAIL"` got `"PASS"` — the neutralized statistic made every
split (wrongly) pass, and the discriminating test correctly caught the masked instability. The
test is genuinely able to FAIL; it is not vacuous.

**File restoration (important workflow note):** my first restore used `git checkout --
src/physics/layer2/mixture_stability.py`, which reverted the file to **HEAD** and thereby
**wiped the implementer's uncommitted #638 changes** (working tree dropped to 4 modified files).
I recovered by extracting the file's hunks from the captured full diff and `git apply`-ing them;
`git apply --check` passed, then the applied `git diff` md5 (`c36b55db…`) matched the
pre-perturbation baseline exactly and the tree was back to 5 modified files. Confirmed no
perturbation remnant (`grep` count 0) and the 23-test suite passes again. **`git diff` is back to
the reviewed state.**

### k stays support-driven — independently proven
`TestSupportDrivenK::test_k_responds_up_when_a_supported_cluster_is_added` asserts `fit_two.k == 2`
AND `fit_three.k == 3` AND `fit_three.k > fit_two.k` — **mechanically impossible for any pinned
constant k** (it cannot be both 2 and 3), so the test would fail if k were hardcoded. Downward
response + floor-guard covered by `test_tiny_cluster_below_both_arms_is_floor_rejected` (5-pt speck
fails both arms → k stays 2) and `test_minority_below_5pct_but_above_150_obs_is_supported_by_count_arm`
(sub-5% but 300-obs minority survives on the count arm → k=2, asserts `weights_.min() < 0.05`).

## Code/doc quality
Minimal, well-encapsulated, maintainable. `_to_log_space` is the single home of the transform
(de-duplicates fit/query). Docstrings thoroughly updated to the log-radius space. Determinism
preserved (`random_state` threaded through every GMM fit and `check_holdout_stability`). Fowler
pass: 12 smells rendered, 0 flagged, 2 documented overrides (duplicated-code: test-fixture helper
mirrors the pre-existing repo convention — the old `_make_blobs` was duplicated the same way, and
the production change actually DE-duplicates; long-parameter-list: `min_component_support_count`
injection mirrors the existing `min_component_weight_frac` param per the constant-injection
convention). `verify_fowler_pass.py` exit 0.

## Map impact verdict
- **Evidence supports claimed change:** yes — unit suites exercise the log-radius fit, the OR
  support arm, and the log-space gate comparison.
- **Constraints not violated:** support-driven k, F12 falsifiable, no-evo-import all honored
  (independently verified above).
- **Notes match the diff:** structural (`fit_property_mixture`+`_to_log_space`,
  `_normalize`/`component_agreement_stat`), capability (property-mixture-fit, f12-holdout-stability),
  and constraint anchors all match what the diff touched. No overstated/missing impact.
- **Decision candidates surfaced:** the design choices (raw→log, relative→absolute floor, k-cap-4,
  gate normalization) are all pre-registered in DIAGNOSIS.md and surfaced for Admiral visibility at
  merge; none loosen the pass threshold.
- **Durable context routed:** the stale packet doc is routed to Triage (below).

## Reconciliation check
`F12_AGREEMENT_THRESHOLD == 1.0` unchanged; k-mismatch→`inf` auto-fail intact
(mixture_stability.py:136-137); Hungarian match intact (line 144); strict all-splits-must-pass rule
unchanged. Gate not weakened — only the normalization constant moved into the fit's log space.
Three new constants all carry in-module domain-reasoned, pre-registered comments
(`MIN_COMPONENT_SUPPORT_COUNT=150`, `k_range` ceiling 4, `LOG_RADIUS_SCALE=0.30`) — not tuned to a
result.

## Blockers
- none

## Out-of-scope observations
- **Triage (tc1):** `docs/architecture/packets/physics.md:979` still documents the F12 gate
  normalization as `RADIUS_SCALE_M = 50` (raw metres). After #638 this is `LOG_RADIUS_SCALE = 0.30`
  (log10). Cartographer reconcile — out of this gate's scope (map doc). Confirmed real at that line.

## Workflow Feedback
- **Handoff gaps:** The handoff's simplification-limits command uses the positional form
  (`--paths` omitted in prose but the implementer already flagged this); the CLI requires `--paths`.
  Minor — I used `--paths` and it passed. The handoff was otherwise precise and the two load-bearing
  checks were called out clearly, which made the review tractable.
- **Context rediscovered:** none — DIAGNOSIS.md + implement-result carried enough to reproduce every
  claim.
- **Instructions improvised around:** The restore mechanism for the falsifiability perturbation is a
  real trap: the reviewed state is UNCOMMITTED, so `git checkout -- <file>` reverts to HEAD and
  destroys the implementer's changes rather than undoing only my perturbation. A safer instruction
  would be to `cp` the file to a backup before perturbing and `cp` it back (or `git stash` the whole
  tree first), NOT `git checkout`. I recovered via `git apply` of the captured diff and verified by
  md5, but future reviewers should be warned. Recommend the handoff/skill say: "back up the file by
  copy before perturbing; restore by copy — never `git checkout` an uncommitted working-tree change."
- **What would have made this easier:** a one-line note in the handoff that the reviewed changes are
  uncommitted (so restore-by-checkout is unsafe), plus the `--paths` fix.

## Return status
`complete`
