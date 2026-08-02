# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3-review` (issue #666, epic #659)

## Result
`APPROVE`

## Handoff compliance
Yes. `fit.py` implements the strictly-pre hierarchical Student-t shrinkage fit exactly as the
handoff specified: field -> driver-overall -> class cell + class-across-drivers parent via
`fit_two_way`, recency-weighted (`0.5**(delta_round/halflife)`), both channels
(`utilization`/`time_deficit_s`, `energy`/`deployment_share`), writing exactly `vocabulary.k`
cells per channel into the G2 store via `write_fingerprint`. Independently reproduced 14/14
`test_fit.py` and 83/83 whole-package.

## Scope drift
None. mtime evidence confirms only `fit.py` (08:17) and `test_fit.py` (08:15) were modified in
this gate; `address.py`/`store.py`/`vocabulary.py`/`frozen_constants.py` and their tests carry
earlier G1/G2 timestamps and are untouched. `pooling.py`/`student_t.py`/`driver_utility.py` were
read-only consumed (confirmed empty `git diff` for the two forbidden files). No G2 schema
change, no G4 build.

## Evidence verdict
Satisfies TDD test mode. All required evidence independently reproduced, including by sabotage
(not just re-running the implementer's own commands):

- **Cutoff-leakage keystone:** removed the `AND round_idx <= ?` SQL clause -- BOTH
  `TestCutoffLeakageKeystone` tests went genuinely RED (`ValueError` from `_recency_weight`'s
  own defensive guard firing on a leaked future row). Restored (diff-confirmed byte-identical),
  reran GREEN. Confirmed the **non-target-driver** poison test is present and is the load-bearing
  case (poisons PER while fitting VER, proving the cutoff protects the class-across-drivers
  parent/field pooling, not just the target driver's own rows). #628's 14.6x precedent is cited
  in both the test docstring and the module docstring.
- **Sigma priced once:** `grep` confirms `pool_random_effects` appears in exactly one file and
  one call expression (`_price_sigma_with_shared_floor`). Sabotaged a second call (feeding the
  first call's own output back in) -- both `TestSigmaPricedAtSingleSite` and
  `TestSigmaIdempotence::test_helper_single_application...` went RED (spy count 8 vs 4 resolved
  cells; `once != math.hypot(sigma0, shared_floor)`). Restored, reran GREEN. Verified
  `shared_floor = math.sqrt(max(pool.var_circuit, 0.0))` where `pool = fit_two_way(values,
  drivers_arr, classes_arr)` -- `var_circuit` is genuinely the between-CLASS variance since
  `classes_arr` is the `circuits` argument. Driver-overall level (`pool.team_effects`) is only
  ever read via `pool.predict(...)`, never separately floored.
- **G byte-identical point:** sabotaged `_compose_sigma` to drop the `g_sigma_onesided`/
  `sigma_lapsampling` quadrature terms -- both `TestGByteIdenticalPoint` and
  `TestSigmaLapsamplingPresentButZero::test_nonzero_lapsampling_widens_sigma` went RED (sigma
  collapsed identical across scenarios); the two cells' **mean** stayed identical throughout,
  confirming point-independence holds structurally (`g_sigma_onesided` never enters
  `fit_two_way`'s input values). Restored, reran 14/14 GREEN.
- **sigma_lapsampling present-but-zero:** confirmed directly in `_aggregate_cells`/
  `_combine_bucket` -- `sigma_lapsampling` is unconditionally set via `_optional_weighted_mean`,
  defaulting a fully-NULL column to literal `0.0`, never omitted.
- **as_of_round required:** confirmed via `inspect.signature` -- `KEYWORD_ONLY`,
  `default=inspect._empty`. Falls out of Python's own binding.
- **Exactly k cells + unresolved-not-missing, both channels:** reproduced
  `TestBothChannelsWritten` and `TestExactlyKCellsAndUnresolved` directly (thin-support and
  data-absent classes both come back `status="unresolved"` with `mean=None`/`sigma=None`, never
  a missing row; `len(cells) == vocab.k` in both channels).
- **No forbidden file edited, no blob:** `git diff --stat` empty for `pooling.py`/`student_t.py`;
  `git diff --cached --stat` empty; the one workbench DB artifact is confirmed git-ignored
  (`.gitignore:285`).

## Code/doc quality
Minimal, maintainable, project-rule compliant. `simplification_limits --paths` PASS on both
files. Fowler refactoring pass run (`fowler_pass.json`, `verify_fowler_pass.py` exit 0): 4
non-blocking observations --
1. minor test duplication between `test_g_sigma_onesided_changes_sigma_not_mean` and
   `test_nonzero_lapsampling_widens_sigma` (same arrange/act/assert shape),
2. a data-clump/primitive-obsession in `_combine_bucket`'s repeated positional 5-tuple
   unpacking (a small named struct would remove the positional fragility),
3. `fit_driver_fingerprints`'s 12-parameter signature (3 positional + 9 keyword-only), which
   scales up `store.write_fingerprint`'s own existing convention rather than introducing a new
   style.

None of these rise to a blocker; none touch a crown invariant or a documented repo-standard
violation.

## Map impact verdict
- **Evidence supports claimed change:** yes -- claimed `struct:physics.fingerprint.fit` anchor
  matches the diff's actual function list (`fit_driver_fingerprints`, `_read_observable_rows`,
  `_aggregate_cells`, `_price_sigma_with_shared_floor`, `_compose_sigma`, `_fit_channel`).
- **Constraints not violated:** yes -- DB-BLOB guard honored (tests use `tmp_path` only);
  `decision:c1_driver_utilization_design` and `decision:pooled_sigma_shared_systematic_floor`
  both honored as specified (verified above, not just asserted).
- **Notes match the diff:** yes.
- **Decision candidates surfaced:** n/a -- no new authority-requiring decision arose in this
  gate; the #675 verdict was already adjudicated upstream (G1-integrate, cited correctly).
- **Durable context routed:** yes -- `notes-666.md` carries staged prose for a future
  Cartographer reconcile pass; crew correctly did not edit `docs/architecture/` directly.

## Reconciliation check
None. No divergence from recorded architecture requiring Commander reconciliation beyond the
already-pending Cartographer reconcile (expected, not a defect).

## Blockers
- none

## Out-of-scope observations
- The 4 Fowler-pass observations above (test duplication, data-clump/primitive-obsession in
  `_combine_bucket`, long parameter list on the public entry point) are worth a future
  lightweight cleanup pass but do not warrant a triage issue on their own -- non-blocking,
  cosmetic.
- The implementer's own out-of-scope note (belt-and-suspenders floor enforcement redundancy
  between `fit.py` and `store.write_fingerprint`) is confirmed accurate and is not a defect.

## Workflow Feedback
- **Handoff gaps:** none material. The handoff's close-criteria list mapped cleanly onto
  independently-reproducible sabotage tests; no field was missing or ambiguous.
- **Context rediscovered:** none beyond what the handoff/notes-666.md already pointed at.
- **Instructions improvised around:** none -- the survey-append pattern (7 additional
  crown-invariant-specific checks beyond the 7 base template items) mapped the handoff's "each a
  review check" instruction directly onto the engine's `append` verb with no friction.
- **What would have made this easier:** nothing significant. One micro-note: `current` (the
  read-only verb) does not accept `--session-id` -- passing it errors with "unrecognized
  arguments." Not a defect, just worth flagging since the verb-loop reference lists
  `--session-id` as required "on each call" for mutating verbs without calling out that
  `current` is the one read-only exception.

## Return status
`complete`
