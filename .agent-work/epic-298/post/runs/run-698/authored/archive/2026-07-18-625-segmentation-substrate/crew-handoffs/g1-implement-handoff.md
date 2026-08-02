# Implementer Handoff

## Gate
g1 (execute.json: g1-implement)

## Task
Extend `src/physics/layer2/arcs.py` to support a straight-arc grouper mirroring the existing
`BrakingArc`/`identify_braking_arcs` pattern, and add a new `src/physics/layer2/
corner_descriptors.py` module computing a lateral-g/radius descriptor axis from
`grip_bin_obs`-shaped rows.

## Protected Intent
`identify_braking_arcs`'s existing public signature and behavior must stay byte-identical for
every existing caller (`session_braking.py`). This is additive work, not a refactor of
working code.

## Test Mode
TDD not required — physics fitting code in this repo is test-after with synthetic fixtures
(project norm, see `tests/unit/physics/test_segment_classifier.py`,
`tests/unit/physics/layer2/test_arcs.py`). Both new/changed pieces are pure functions —
write tests alongside the implementation, not after a separate pass.

## Close Criteria
- `arcs.py`'s `_contiguous_runs` accepts a `regimes: set[str]` parameter (generalized from
  the hardcoded single-regime check it currently has) — read the current source first, don't
  assume the exact current signature.
- `identify_braking_arcs`'s existing public call signature is UNCHANGED; internally it now
  passes its own regime set through to the generalized `_contiguous_runs`.
- New `StraightArc` frozen dataclass: `sample_indices` (the run's sample index range/list,
  matching `BrakingArc`'s own field shape), `length_m` (float, cumulative straight-line
  position delta over the run), `duration_s` (float, `(last.timestamp_ms - first.timestamp_ms)
  / 1000.0`), `top_speed_ms` (float, `max(sample.speed for sample in run)`).
- New `identify_straight_arcs(samples, min_len)` groups contiguous samples whose `regime` is
  one of `{"straight_throttle", "straight_coast", "straight_brake"}` (import this set from
  `src.physics.physics_data_models._VALID_REGIMES` filtered to the non-`"corner"` members, or
  cite the three literal strings directly if importing the filtered set is awkward — either
  is fine, just don't hardcode a DIFFERENT set than what `_VALID_REGIMES` actually contains)
  into `StraightArc` records, applying the same `min_len` convention `identify_braking_arcs`
  already uses (read its current default/semantics from source).
- New `src/physics/layer2/corner_descriptors.py`:
  - `bin_row_to_descriptor(mu_lat_p90: float, v_mean: float) -> tuple[float, float]` returning
    `(radius_m, lateral_g)` where `lateral_g = mu_lat_p90` (it is already in g-units per
    `grip_bin_obs.py`'s own docstring — do not re-divide by G) and
    `radius_m = v_mean**2 / (mu_lat_p90 * GRAVITY_MS2)` (import `GRAVITY_MS2` from
    `src.physics.constants` — verify the exact import path from source, do not guess).
    Guard: raise `ValueError` (or return `(float("nan"), float("nan"))` — YOUR CHOICE, but
    be consistent and document it in the docstring) when `mu_lat_p90 <= 0` or either input is
    NaN — a physically-impossible/degenerate input must not silently produce a fabricated
    finite radius.
  - `descriptors_from_frame(df: pandas.DataFrame) -> numpy.ndarray` shape `(N, 2)` — columns
    `[radius_m, lateral_g]`, one row per surviving `grip_bin_obs`-shaped input row (columns
    `mu_lat_p90`, `v_mean`), DROPPING (not erroring on) rows where `mu_lat_p90 <= 0` or NaN
    in either column, returning a shorter array than the input length in that case.
- All new/changed public functions and dataclasses carry docstrings citing the physical
  formula/reasoning (this module will be read cold by Phase 2/4 consumers later).

## Allowed Scope
- `src/physics/layer2/arcs.py` (edit — generalize `_contiguous_runs`, add `StraightArc` +
  `identify_straight_arcs`)
- `src/physics/layer2/corner_descriptors.py` (new file)
- `tests/unit/physics/layer2/test_arcs.py` (edit — add new test classes/cases for the
  straight-arc grouper; DO NOT remove or weaken any existing `TestIdentifyBrakingArcs`-style
  case — those must stay green unmodified)
- `tests/unit/physics/layer2/test_corner_descriptors.py` (new file)

## Specific Exclusions
- Do not touch `src/physics/segment_classifier.py` (that's Gate 2's scope).
- Do not touch `data/damage_integrals.db` or any DB file — this gate is pure-function code
  operating on in-memory samples/DataFrames, no DB I/O.
- Do not touch `src/evo_predictor/circuits.yaml` or any production default/config.
- Do not import anything from `evo_predictor`, `latent_power`, or `compound_prior`
  (`constraint:physics_region_no_evo_import`).

## Constraints
- `identify_braking_arcs`'s existing public signature is frozen — verify this by reading
  `src/physics/layer2/session_braking.py`'s call site before touching `arcs.py`, so you know
  exactly what must not change.
- `GRAVITY_MS2` — import from `src.physics.constants` (verify the exact constant name/value
  from source before use; do not hardcode `9.81` inline).
- `mu_lat_p90` in `grip_bin_obs` rows is ALREADY in g-units (p90 of `a_lat/G`, per
  `src/physics/layer2/grip_bin_obs.py`'s module docstring and `lap_bin_observations`'s
  `mu_lat = a_lat / G` line) — do not re-divide by `G` again when producing `lateral_g`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `src/physics/layer2/arcs.py`, module (existing
  `_contiguous_runs`/`BrakingArc`/`identify_braking_arcs` pattern to generalize, not
  duplicate); `src/physics/layer2/grip_bin_obs.py`, module (read-only reference only — do not
  edit — for `mu_lat_p90`/`v_mean` semantics, `N_BINS=32`, `CORNER_GATE_MS2=3.0`).
- **Capability:** straight-as-first-class-segment grouping (new); lateral-g/radius descriptor
  axis (new) — both named deliverables of DESIGN_SPEC.md Phase 1.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** none directly governing this gate's specific mechanics.
- **Evidence expectations:** the arcs.py pattern (`BrakingArc`/`identify_braking_arcs`) IS the
  reuse template this gate is expected to generalize — a reviewer will check you did not
  duplicate `_contiguous_runs`'s logic into a second copy.
- **Map confidence flags:** none for this gate specifically (the `grip_bin_obs` bin-stability
  caveat matters for Gate 4, not this gate, since this gate only computes a per-row
  radius/lateral-g pair, not a per-circuit aggregate).

## Deliverable Path Check
- **Committed** — `src/physics/layer2/arcs.py`; `git check-ignore -v src/physics/layer2/arcs.py` exited 1 (not ignored).
- **Committed** — `src/physics/layer2/corner_descriptors.py`; `git check-ignore -v src/physics/layer2/corner_descriptors.py` exited 1 (not ignored) — this is a NEW file, so it will show as untracked in `git status` until staged, not yet in `git diff`.
- **Committed** — `tests/unit/physics/layer2/test_arcs.py`; exited 1 (not ignored).
- **Committed** — `tests/unit/physics/layer2/test_corner_descriptors.py`; exited 1 (not ignored) — new file, untracked until staged.

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_arcs.py tests/unit/physics/layer2/test_corner_descriptors.py -v` — full output pasted, all PASS, including every pre-existing `test_arcs.py` case (confirm none were removed — count before/after).
- A short note confirming `_contiguous_runs` was generalized (not duplicated) — cite the exact diff hunk or before/after signature.

## Verification Commands

```bash
cd /c/Programs/f1-625
py -m pytest tests/unit/physics/layer2/test_arcs.py tests/unit/physics/layer2/test_corner_descriptors.py -v
```

## Suggested Model Tier
Simple bounded — pure-function additive code with a clear existing pattern to mirror; no
statistical/modeling judgment calls (that's Gates 2/3).

## Authority
The overall Phase 1 plan (`CONVERGED_PLAN.md`) is frozen by the commander after
plan-alternatives + cold critic review — do not re-litigate the gate boundaries or deliverable
shape; if something in this handoff is genuinely ambiguous or wrong against the real source,
stop and report rather than guessing past it.

## Stop Conditions
Stop and return if: `identify_braking_arcs`'s real signature doesn't match what's described
here (report the actual signature, don't silently adapt past a contradiction); a decision
outside this handoff's scope is needed (e.g. whether to also touch `segment_classifier.py`);
required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
Deliver it via SendMessage back to this commander before ending your turn.
