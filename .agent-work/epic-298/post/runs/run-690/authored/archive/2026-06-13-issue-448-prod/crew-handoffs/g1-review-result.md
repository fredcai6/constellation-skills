VERDICT: APPROVE

# Review Result

## Assigned Gate
`g1 — windowless trajectory module build`

## Result
`APPROVE`

## Handoff compliance
The change did exactly what the handoff asked: lifted and cleaned the validated
E1-E12 lab estimator into `src/preprocessing/trajectory/` as a faithful,
cruft-free production module with clean boundaries, ready for the g2 test suite.
All 7 required modules are present. `tests/oracles/` is correctly placed outside
`src/`. No existing files were modified. Admiral decisions D2 (salvage loaders)
and D3 (fit_stint_hp as first-class public) are both honored.

## Scope drift
None. Only new files added: 7 under `src/preprocessing/trajectory/`, 2 under
`tests/oracles/`, 1 plan artifact. `src/preprocessing/__init__.py` untouched
(g3 owns that). No windowed/ribbon symbols re-exported.

## Evidence verdict
Evidence is complete and internally consistent: import smoke (`import ok`),
simplification-limits PASS (7 files), cross-region grep empty, FastF1 grep
confirming only `loaders.py` hits, forward-smoother smoke output
(`pos_at`/`speed_at`/`nis_series`), and NSStintSmoother r==1 nesting
max_diff 1.07e-14. Oracle smoke also provided. Evidence mode matches the
agreed `evidence-only smoke` (full test suite is g2).

## Code/doc quality
Clean. All modules have module-level docstrings citing lab sources. Public
functions have type hints, named parameters, and descriptive validation messages
(field + expectation + actual pattern). No print() calls in src/. No
experiment-only scaffolding. Simplification limits PASS on all 7 files.

## Map impact verdict

- **Evidence supports claimed change:** Yes. Smoke output directly demonstrates
  `StintSmoother.fit`, `pos_at`, `speed_at`, `nis_series`, and the NSStintSmoother
  r==1 nesting invariant (1.07e-14 max_diff). The claimed capability is real.

- **Constraints not violated:** Confirmed by independent grepping:
  `constraint:physics_region_no_evo_import` (empty grep for evo_predictor /
  latent_power / src.physics); `constraint:db_only_boundary` (fastf1/Cache hits
  only in loaders.py). No JointFusion or oracle imports in src/.

- **Notes match the diff:** The Map Impact notes accurately describe the diff:
  `struct:preprocessing child` (new subpackage, parent __init__ unchanged);
  `capability:windowless-full-stint-trajectory-estimation` (new); both
  constraints honored; D2/D3 decisions documented; session_offset adaptation
  flagged as a workflow observation.

- **Decision candidates surfaced:** The session_offset adaptation (lab version
  calls `fit_window`/`JointFusion`; production port decoupled to `StintSmoother`
  slices) was surfaced explicitly in the implementer result as an out-of-scope
  observation and assumption. Authority was not overstepped; the spirit
  (chi²-target on short windows) is preserved and the delta will be cross-validated
  in g2. Appropriately flagged.

- **Durable context routed:** The new struct anchor and capability are flagged
  as Cartographer candidates (index.md update; g3 or closeout owns it). Triage
  candidate listed for the enable_cache grep pattern in handoffs.

## Close criteria checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | `py -c "import src.preprocessing.trajectory as t; print('ok')"` succeeds | PASS |
| 2 | `simplification_limits --paths src/preprocessing/trajectory` clean | PASS — 7 files |
| 3 | No cross-region import (evo_predictor / latent_power / src.physics) | PASS — grep empty |
| 4 | fastf1/enable_cache/Cache. only in loaders.py | PASS — __init__.py re-export is string, no fastf1 import |
| 5 | Lab cruft stripped (EVID, os.makedirs, sys.path.insert, e6 stitch path) | PASS — all greps empty |
| 6a | matern52_sde P_inf matches lab exactly | PASS — exact match to e10_lib.py lines 93-99 |
| 6b | discretize Q = P_inf - Phi P_inf Phi^T matches lab | PASS — exact match |
| 6c | Diffuse-diagonal init (P[0,0]=P[3,3]=1e6, P[1,1]=P[4,4]=1e4, acc from P_inf, no cross) | PASS — exact match |
| 6d | Per-axis linear detrend + velocity trend add-back | PASS — exact match |
| 6e | Affine-offset iterated-EKF speed update | PASS — exact match to e10_lib lines 250-254 |
| 6f | NSStintSmoother r==1 reduces to StintSmoother | PASS — verified structurally; smoke 1.07e-14 |
| 7 | SIG_SPD=0.49, NOMINAL_OFFSET=0.09, kernel orders documented | PASS |
| 8 | Salvaged loaders: read-only DB URI (mode=ro), offline raises on uncached | PASS |
| 9 | Public input validation (field/expectation/actual) | PASS — 7 public boundaries spot-checked |
| 10 | fit_stint_hp is first-class public function in calibration.py | PASS |

## Reconciliation check
The new `src/preprocessing/trajectory/` subpackage adds a capability not
currently in `docs/architecture/index.md`. Commander should route a Cartographer
update at g3/closeout to record:
- New structural anchor: `src/preprocessing/trajectory/` (windowless trajectory
  estimation subpackage)
- New capability: `capability:windowless-full-stint-trajectory-estimation`
- Constraints: physics_region_no_evo_import, db_only_boundary

No existing architectural contracts are broken.

## Blockers
None.

## Out-of-scope observations

1. **session_offset adaptation (g2 validation item):** The production
   `session_offset` uses `StintSmoother` slices instead of the lab's
   `fit_window`/`JointFusion`. The spirit and delta grid are preserved.
   Functional correctness of the returned delta is a g2 concern (compare to E4
   results), not a g1 blocker. Correctly flagged by implementer.

2. **Cartographer anchor (triage candidate):** `docs/architecture/index.md`
   does not yet reflect the new `src/preprocessing/trajectory/` subpackage or
   the `capability:windowless-full-stint-trajectory-estimation` capability.
   Commander should assign a Cartographer run at closeout.

3. **Handoff grep pattern for enable_cache (workflow):** The handoff's grep
   `fastf1|enable_cache|Cache.` catches the `__init__.py` re-export of
   `enable_cache` as a string occurrence. This is benign but was noted by the
   implementer as a potential future handoff improvement (refine the pattern to
   exclude function re-exports).

## Workflow Feedback

- **Handoff gaps:** The verification command `py -m src.utils.simplification_limits
  src/preprocessing/trajectory` (positional) is wrong; the tool requires
  `--paths src/preprocessing/trajectory`. The implementer caught this mid-run
  and used the correct form. Commander should update the command in future
  handoffs.

- **Context rediscovered:** The `session_offset` -> `fit_window` -> `JointFusion`
  dependency chain was not surfaced in the handoff. The handoff says "port
  session_offset from e4_run" without noting the JointFusion decoupling was
  non-trivial. A "dependency surprises" field in future handoffs would surface
  this before implementation.

- **Instructions improvised around:** The engine's `consolidate` verb does not
  accept `--result`/`--finding` (only `--verdict`/`--summary`); had to adjust
  from the `record` syntax. No skill/template instruction covered this;
  discovered via `--help`.

- **What would have made this easier:** A "dependency surprises" handoff field
  (e.g., "watch out for these lab cross-dependencies") and the corrected
  `--paths` form in the verification command block.

## Return status
`complete`
