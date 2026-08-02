# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g4-review` (issue #666, epic #659)

## Result
`APPROVE`

## Handoff compliance
Handoff asked for `tests/unit/physics/fingerprint/test_bounded_validation.py` (13 tests) +
`scripts/fingerprint_bounded_validation.py` (runnable harness) running the G3 fit
(`fit_driver_fingerprints`) on the REAL 2023-Q bounded slice
(`.agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db`), asserting all acceptance
invariants on real numbers and emitting `bounded_fit_summary.json`. Fully satisfied and
independently reproduced (see Evidence verdict).

## Scope drift
None. mtime evidence (`Get-ChildItem` sorted by `LastWriteTime`) shows `fit.py` (08:42),
`store.py` (07:42), `vocabulary.py` (07:40), `address.py` (07:39), `frozen_constants.py` (07:09)
all predate the two files this gate touched — `test_bounded_validation.py` (09:02) and
`fingerprint_bounded_validation.py` (09:03). `git diff --stat` for `src/physics/layer2/pooling.py`
and `src/common/student_t.py` is empty. `scripts/fingerprint_class_coverage_675.py` (07:12)
predates this gate too — a pre-existing g1-implement artifact, not introduced here.

## Evidence verdict
Every close criterion was **independently reproduced against the real slice**, not accepted from
the implementer's report alone:

- **Cutoff-leakage (crown):** wrote a fresh reviewer-authored script (not reusing the
  implementer's test helpers) that built a physically-truncated `round_idx<=7` copy of the real
  slice from scratch and called the actual `fit_driver_fingerprints`. `full(as_of_round=7)` was
  byte-identical to `truncated(as_of_round=7)` across all 4 drivers × 2 channels × 4 classes; the
  real slice has 96 total rows, 48 at `round_idx<=7` (48 genuine future rows excluded — not a
  vacuous check); `full(as_of_round=12)` genuinely differs from `full(as_of_round=7)`.
- **k=4 + unresolved-not-missing:** independently called `build_summary` at both `as_of_round=7`
  and `=12`. Both return exactly 32 cells (4×2×4). At r=7: 8/8 c1 cells (all drivers, both
  channels) are `unresolved` — a genuine measured-null, never a missing row. At r=12: 0
  measured-null cells (c1 crosses the support floor once GB/Belgium are visible).
- **Sigma-widening idempotent:** reran the real fit **3 times** (not just the test's 2) into the
  same store for VER at r=12. Row counts stayed exactly k=4 both channels across all 3 reruns
  (no duplicate accumulation); the c1/utilization cell's mean/sigma/support_n were byte-identical
  across reruns and matched the independently-regenerated summary artifact exactly.
- **Class shared_floor = sqrt(var_circuit), non-zero, driver-overall not floored:** confirmed
  from the regenerated `bounded_fit_summary.json`: utilization `var_circuit=4.258539667224817`,
  `shared_floor_class_axis=2.0636229469611975` == `sqrt(var_circuit)` exactly (energy channel
  likewise); `var_team` (driver axis) is a materially different, much smaller value and never
  equals the floor.
- **Both channels:** `channel_summary` has exactly `{utilization, energy}`, both `var_circuit>0`
  with resolved cells.
- **F12 provenance (not a silent PASS):** independently read
  `docs/physics/625-f12-holdout-stability.json` directly — `headline_verdict='PASS'`, `n_pass=5/5`,
  `mean_statistic=0.5402`, 22 circuits. Confirmed by direct set-difference that `'Belgium'`
  (one of the slice's 4 circuits) genuinely IS absent from that artifact's `circuit_names` — the
  honest caveat in the provenance string is factually correct, not invented. A documented
  `UNVERIFIED` fallback exists for a missing artifact (non-blocking observation: that branch is
  not exercised by any assertion in this repo's current data state, since the real artifact is
  present).
- **`honest_statement` matches the numbers:** every numeric claim in the regenerated summary's
  prose was cross-checked against the underlying cell data and found accurate (support ratios,
  per-driver c1 status/support_n, the r6/7 vs r10/12 threshold crossing, the shared_floor
  dominance claim).
- **Full suite + no blob:** `tests/unit/physics/fingerprint/` reproduced 96/96 green;
  `git status --porcelain` / `git diff --cached --stat` confirm nothing staged; the slice DB is
  git-ignored (`.gitignore:285`).

## Code/doc quality
Fowler code-smell pass run (`g4-review/fowler_pass.json`, `verify_fowler_pass.py` exit 0): 4
non-blocking observations — a duplicated spy-closure pattern (written 3x across the test file and
the script), a data-clump on the `(driver, channel, class_id)` triple threaded through the
report-building helpers, primitive-obsession in the raw-dict cell records, and an 8-positional-arg
`_resolved_cell_record`. None violate a documented repo standard or rise to a defect — all are
minor, contained to new report-building helpers, not production logic.

## Map impact verdict
- **Evidence supports claimed change:** yes — no production behavior changed (validation-only
  gate); the real-data harness genuinely demonstrates the invariants, independently reproduced
  above.
- **Constraints not violated:** yes — DB-only read access (raw `sqlite3` `mode=ro`), explicit
  `as_of_round` at every call site, missingness represented via named `unresolved` status, no
  module-level mutable state.
- **Notes match the diff:** yes — `struct:physics.fingerprint` / `struct:physics.utilization`
  anchors correctly named; the `map_version` varies-per-round real-data detail was independently
  confirmed via direct DB read.
- **Decision candidates surfaced:** none forced; `decision:c1_driver_utilization_design`
  correctly cited as genuinely evidenced on real rounds.
- **Durable context routed:** the Belgium/F12-corpus gap was named in prose (Map Impact +
  `honest_statement`) but never actually filed as a Triage candidate by the implementer — this
  reviewer filed it as `tc1` via `flag-candidate` so Commander/Triage sees a structured candidate,
  not just prose.

## Reconciliation check
None. No structural/contract baseline concern beyond the `tc1` triage candidate above.

## Blockers
- none

## Out-of-scope observations
- `tc1` (filed in the survey): `docs/physics/625-f12-holdout-stability.json`'s 22-circuit corpus
  does not include Belgium, one of this slice's 4 circuits. The verdict is still a legitimate
  substrate-level PASS (correctly caveated), but a future gate needing a per-circuit F12 guarantee
  will need this closed. Route to Triage.
- The `ClassVocabulary` `UNVERIFIED`-fallback branch in `production_vocabulary()` is real and
  handoff-authorized but is not exercised by any assertion in this repo's current data state (the
  artifact is present, so only the `PASS` branch runs). Not a defect — worth a follow-up test with
  a monkeypatched-missing-artifact fixture if/when this path matters for a future gate.
- Fowler observations (duplicated spy-closure pattern x3, data-clump, primitive-obsession,
  long-parameter-list) — all non-blocking, see Code/doc quality above.

## Workflow Feedback

- **Handoff gaps:** none blocking. The handoff's phrasing around the F12 sourcing path ("derive
  from the existing f12 machinery... or an explicit UNVERIFIED+override") left it genuinely
  ambiguous whether "derive" meant re-run the 22-circuit stability machinery or read its already-committed
  output — the implementer resolved this reasonably (read the committed artifact) but a future
  handoff could state which is intended when a prior gate's real verdict is already committed, to
  save the implementer's (correctly-flagged) ambiguity-resolution step.
- **Context rediscovered:** none beyond what the implementer's result already surfaced (the
  `map_version` varies-per-round real-data detail) — that context was already carried in the
  implementer's result and Map Impact notes, so this reviewer did not have to rediscover it from
  scratch, just verify it.
- **Instructions improvised around:** none. The `r6-fowler` survey item required appending 8 new
  domain-specific checks (r7-r14) beyond the 7-item template — this is exactly what the skill's
  "append checks the context warrants" instruction anticipates, not an improvisation.
- **What would have made this easier:** none — the g3-review survey (`g3-review/review.json`) was
  a strong worked example for structuring the domain-specific checks and the Fowler pass record;
  reusing its shape saved real time.

## Return status
`complete`
