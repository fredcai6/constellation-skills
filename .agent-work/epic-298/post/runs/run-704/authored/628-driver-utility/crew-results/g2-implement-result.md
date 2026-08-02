# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2-implement` (epic #601 wave-7 issue #628 Phase 3b, delegated)

## Completed slice
Built the driver-utility latent estimator with an explicit resolved/unresolved status per axis
and its banked artifact:

1. `src/physics/utilization/driver_utility.py` — `estimate_driver_utility(rows_df) -> DataFrame`:
   pools G1's per-(round, driver, axis) observable rows into one row per `(year, driver,
   constructor, axis)`, via `pool_random_effects` (REUSED, not reinvented) over each group's
   valid `(g_deficit, sigma_lapsampling)` pairs -> `delta=pooled.mu, sigma=pooled.sigma_mu,
   tau=pooled.tau`. `status="resolved"` iff `n_sessions >= MIN_RESOLVED_SESSIONS(=3)` else
   `"unresolved"`. `effective_sigma` is computed via `effective_axis_sigma` (REUSED, not
   reimplemented) fed a real per-axis `reference_value` (population std of `g_deficit` for that
   axis across all valid input rows, floored to `REFERENCE_VALUE_FLOOR_MS=0.1` m/s). Every
   `(year, driver, constructor, axis)` combo present in the axis-non-null input rows emits exactly
   one output row — including a zero-valid-observation group (delta/sigma both `None`, status
   `"unresolved"`, effective_sigma synthesized from `reference_value` alone).
2. `write_driver_utility_db(df, path)` — persists the estimator's output to an UNTRACKED SQLite DB
   (table `driver_utility`), replace-on-rerun for the same slice (`to_sql(if_exists="replace")`).
3. `tests/unit/physics/test_driver_utility.py` — TDD unit tests (8 tests, synthetic rows only).

## Scope
**Files changed:**
- `src/physics/utilization/driver_utility.py` (new)
- `tests/unit/physics/test_driver_utility.py` (new)

**Specific exclusions touched:** no — did not build the held-out gate (G3) or run the real batch
(G5); no held-out split logic added; did not modify `pool_random_effects` or
`estimate_store_fields.py` (read-only reuse/import only).

## Behavior changed
Yes — one new module adds the driver-utility latent estimator + banked-artifact writer. No
existing module's behavior changed (`pooling.py`, `estimate_store_fields.py`,
`driver_utility_observable.py` untouched; imported read-only).

## Map Impact
- **Structural anchors touched:** `struct:physics.utilization` — added `driver_utility.py`
  (`estimate_driver_utility`, `write_driver_utility_db`). Reused `pooling.pool_random_effects`
  and `estimate_store_fields.effective_axis_sigma` (read-only imports, not modified). Consumes
  G1's committed row schema (`driver_utility_observable.py` /
  `scripts/build_driver_utility_observables.py`'s persisted columns) as its documented input
  contract.
- **Capabilities added/changed/affected:** new capability — a teammate-relative driver-utility
  latent (`delta`, measured against a per-constructor `strictly_pre=True` causal ceiling), pooled
  across sessions via DerSimonian-Laird random effects, with an explicit resolved/unresolved
  status and a reserved wide `effective_sigma` for thin/absent support, banked to
  `data/driver_utility.db`.
- **Constraints/assumptions touched:** OWNER HARD requirement — honored: every (driver, axis) in
  the input emits exactly one row with an explicit status; nothing dropped silently (tested,
  including the zero-valid-observation edge case and an axis-null error row that must NOT produce
  a phantom output row). `constraint:no-reinvent-sentinel` — honored (`effective_axis_sigma`,
  `pool_random_effects` used unmodified).
- **Decision anchors:** `decision:c1_driver_utilization_design` — implemented per the Commander's
  construction (teammate-relative additive latent via DL pooling + reused sentinel); not
  re-opened.
- **Claims/evidence produced:** well-supported driver's `delta` matches an independently-computed
  `pool_random_effects` call exactly (`TestResolvedPooling`); a thin (2-session) driver/axis is
  `"unresolved"` with `effective_sigma` widened to the reserved scale even though its own raw
  `delta`/`sigma` are both tiny (`TestUnresolvedReservedSigma`) — this test caught a REAL bug (see
  below); a noisy thin driver's pooled `delta` shrinks toward its trustworthy (low-sigma) session
  relative to the naive/raw mean (`TestShrinkage`); every input `(year, driver, constructor,
  axis)` combo appears exactly once in the output, including a zero-valid-observation group and
  correct exclusion of an axis-null error row (`TestNothingDropped`); the banked artifact
  round-trips and is idempotent on rerun (`TestBankedArtifact`).
- **Trust limitations / drift found:** a real defect was found and fixed mid-build (see "Bug found
  and fixed" below) in how this module calls `effective_axis_sigma` — the seam's own literal
  behavior (`value` always wins over `reference_value` when `value is not None`) does not match a
  naive reading of the handoff's literal call form `effective_axis_sigma(value=delta, ...)`.
  Future callers of `effective_axis_sigma` for a metric that can be genuinely ~0 while unresolved
  should be aware of this: pass `value=None` when status != "resolved", not the raw candidate
  value, or the reference_value fallback never fires.
- **Triage candidates:** none new; G3 (held-out gate) and G5 (real batch run) are the natural next
  gates and should build against this gate's output schema (`delta, sigma, status, tau,
  n_sessions, n_points, effective_sigma`).

## Bug found and fixed (mid-build, via TDD red)
`effective_axis_sigma`'s docstring says an unresolved axis widens sigma to `UNRESOLVED_AXIS_SIGMA_FRAC
* abs(value)` when `value` IS present, and only falls back to `reference_value` when `value is
None`. The handoff's literal call form (`effective_axis_sigma(value=delta, ...)`) therefore silently
defeats its own stated purpose whenever `delta` is near 0 for an unresolved (thin) driver/axis —
`reserved = 1.0 * abs(delta) ≈ 0`, and `max(sigma, reserved) ≈ sigma` (unchanged, not widened). This
was caught by `test_thin_driver_unresolved_with_wide_effective_sigma`'s RED failure
(`effective_sigma=0.01`, expected `>= 0.1`). Fix: pass `value=(delta if status == "resolved" else
None)` to `effective_axis_sigma`, forcing the `reference_value` fallback for every unresolved axis —
matching the store's own established convention elsewhere (`_drag_area_fields` nulls the point value,
not just the sigma, on a degenerate/unresolved axis). `delta` itself is still always populated in the
output DataFrame from the raw pool (informational candidate value); only the value fed to
`effective_axis_sigma` is conditioned on status.

## Test mode
**Required:** `TDD required (synthetic observable rows)`
**Satisfied:** yes — `estimate_driver_utility`'s core pooling was built test-first (RED observed:
`ModuleNotFoundError`, then implemented to green). The unresolved/shrinkage slice was also written
test-first and observed a genuine RED (the bug above) before being fixed to green. The
nothing-dropped and banked-artifact slices were written test-first against the already-built
cohesive module (status/pooling/sigma logic is naturally one function, not cleanly separable
across further TDD increments without artificial fragmentation) and passed immediately — recorded
honestly below as test-after verification of already-implemented behavior for those two slices,
not a fresh red-green cycle.

## Evidence

### 1. pytest — full pass
```
$ py -m pytest tests/unit/physics/test_driver_utility.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-628
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 8 items

tests\unit\physics\test_driver_utility.py ........                       [100%]

============================== 8 passed in 1.18s ==============================
```

### 2. Simplification limits
```
$ py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility.py tests/unit/physics/test_driver_utility.py
PASS (2 files checked)
```

### 3. Deliverable path check (not gitignored) + no data/*.db staged
```
$ for f in src/physics/utilization/driver_utility.py tests/unit/physics/test_driver_utility.py; do git check-ignore "$f" && echo "IGNORED:$f"; done
(no output -- neither path is gitignored)

$ git status --short -- data/
?? data/driver_utility_observables.db     (G1's pre-existing untracked scratch DB; untouched by G2)

$ git status --short
?? .agent-work/628-driver-utility/
?? data/driver_utility_observables.db
?? src/physics/utilization/driver_utility.py
?? tests/unit/physics/test_driver_utility.py
```
No `data/driver_utility.db` exists on disk — G2's tests write only to pytest `tmp_path`, never the
real `data/` path (that write is G5's real-batch job, out of this gate's scope). Nothing was
staged.

**Result:** pass

## TDD evidence, if required
- Failing test observed (m1, core pooling): `ModuleNotFoundError: No module named
  'src.physics.utilization.driver_utility'` when `test_driver_utility.py` was written before the
  module existed.
- Failing test observed (m2, unresolved/reserved-sigma — a REAL bug, not a scaffolding gap):
  ```
  FAILED tests/unit/physics/test_driver_utility.py::TestUnresolvedReservedSigma::test_thin_driver_unresolved_with_wide_effective_sigma
  assert np.float64(0.01) >= (1.0 * 0.1)
  ```
  Root cause and fix described in "Bug found and fixed" above.
- Passing test observed: full 8/8 pass, see Evidence #1 above.
- Refactor while green: no separate refactor pass was needed; the implementation stayed under
  simplification limits throughout (`PASS (2 files checked)`, no violations at any step).

## Docs/contracts touched
- none — no committed docs or contracts reference this module yet; this result's Map Impact
  section carries the anchors forward for Cartographer reconcile.

## Assumptions
- **Input row schema**: the handoff did not literally spell out `rows_df`'s column names; G1's
  committed persisted schema (`year, session_type, gp_name, round_idx, constructor, driver, axis,
  g_deficit, n_points, sigma_lapsampling, n_sessions_causal, error`) was adopted as the documented
  contract, since G1 is the only real producer of these rows and its result file explicitly names
  this gate's output schema as the contract G2 should build against. `estimate_driver_utility`
  only requires `year, driver, constructor, axis, g_deficit, sigma_lapsampling` to be present
  (`n_points`/`error` are used when present, degrading gracefully when absent) so it is not
  brittle to the exact G1 column set.
- **"axis has real support"** (Close Criteria's `status="resolved"` predicate: "`n_sessions >=
  MIN_RESOLVED_SESSIONS` AND the axis has real support") is read as automatically satisfied by
  `n_sessions` already counting only non-null, non-errored `g_deficit`/`sigma_lapsampling` rows —
  i.e., "real support" is not a separate condition beyond the session count, since a null/errored
  row was never counted toward `n_sessions` in the first place.
- **`n_points` aggregation**: summed across every row in the group (including rows whose
  `g_deficit` was null but a nonzero-but-below-`MIN_REGIME_POINTS` count of track points still
  landed in that regime), not just the valid/pooled rows — this reports the total observed support
  for the axis, not just the pooled-session support.
- **`REFERENCE_VALUE_FLOOR_MS=0.1`**: a project-constant floor (not derived from the handoff),
  chosen conservatively relative to G1's real-data deficit magnitudes (~0.05-6 m/s per the G1 CLI
  smoke evidence) so a population std computed from too few/too-similar drivers still yields a
  genuinely wide reserved sigma rather than collapsing toward 0.
- **Output row ordering**: `groupby(..., sort=True)` gives deterministic
  `(year, driver, constructor, axis)`-sorted output; not specified by the handoff, chosen for
  reproducibility.

## Stop conditions hit
- none — no cited seam signature mismatched the handoff's "Exact seam signatures" section
  (`pool_random_effects`, `effective_axis_sigma`, `normalize_axis_status`,
  `UNRESOLVED_AXIS_SIGMA_FRAC` all matched source exactly on inspection); scope was not exceeded;
  the explicit-unknown contract WAS satisfiable by reusing `effective_axis_sigma` — it just
  required calling it with `value=None` for unresolved axes rather than the handoff's literal
  `value=delta` form (see "Bug found and fixed" above), which is a caller-side application detail,
  not a seam mismatch; the artifact did not need a tracked data file.

## Out-of-scope observations
- The `effective_axis_sigma`-priority-of-`value`-over-`reference_value` behavior documented above
  is a genuine trap for any future caller passing a metric that can be legitimately ~0 while
  unresolved. Worth a doc note on `effective_axis_sigma` itself (or in its module docstring)
  flagging "pass `value=None` when status != resolved if your metric can be ~0" as an explicit
  usage pattern, since this is the second time (after this gate) the nuance has had to be
  rediscovered from first principles rather than being stated in the seam's own contract.
- G3 (held-out gate) and G5 (real batch run over real observable rows from
  `data/driver_utility_observables.db`) are the natural next gates.

## Workflow Feedback
- **Handoff gaps:** the handoff's exact call form (`effective_axis_sigma(value=delta, sigma=sigma,
  status=status, reference_value=<...>)`, line 30 of the handoff) is not literally correct for
  satisfying its own stated intent ("Because δ is a deficit that can be ≈0, you MUST pass a
  non-trivial reference_value ... so an unresolved axis gets a genuinely WIDE reserved σ") — as
  written, that call form still yields `reserved ≈ 0` whenever `delta ≈ 0`, because
  `effective_axis_sigma` prioritizes `value` over `reference_value` whenever `value is not None`.
  The handoff correctly flagged the subtlety in prose ("the one subtlety is the reference_value
  for unresolved δ") but the prescribed literal call form did not itself encode the needed
  `value=None`-when-unresolved fix. A TDD test caught this before it shipped, so no lasting harm,
  but a future handoff citing this exact seam should either spell out `value=(delta if
  status=="resolved" else None)` directly, or explicitly flag "read effective_axis_sigma's own
  docstring closely — value beats reference_value whenever value is not None."
- **Context rediscovered:** the real `rows_df` schema was not in the handoff text itself (Allowed
  Scope only names the seam functions to reuse); it had to be rediscovered from G1's committed
  result file (`crew-results/g1-implement-result.md`) and the CLI's `_connect` table DDL. This
  cost real time (reading three files) that a one-line pointer in the handoff ("input row schema =
  G1's persisted columns, see driver_utility_observable's CLI") would have saved.
- **Instructions improvised around:** the plan's `m2`-`m4` postcondition commands assumed a strict
  TDD red-green cycle per gate, but because `status`/`effective_sigma`/`write_driver_utility_db`
  are naturally cohesive with the core pooling function (artificially splitting them across
  separate un-implemented stubs would have meant repeatedly half-building and half-testing one
  interdependent function), the m3/m4 "red" attestations honestly recorded "written first, ran
  immediately green against the already-built m1/m2 implementation" rather than fabricating a
  false failure. This is compliant with the skill's own guidance ("collapse to the single
  green/observable postcondition for a test-after/inspection run") but the plan's c1 wording
  ("observed failing... manual attest") did not anticipate this outcome for a mid-sequence item
  whose red step turns out to already be green; I attested with an honest note explaining why
  instead of leaving it ambiguous.
- **What would have made this easier:** (1) the handoff naming the exact `rows_df` schema (or
  pointing at G1's result file) up front; (2) explicitly calling out the
  `value`-beats-`reference_value` precedence in `effective_axis_sigma`'s cited seam signature
  section, since it is the single subtlety the handoff itself flagged as the hard part.

## Return status
`complete`
