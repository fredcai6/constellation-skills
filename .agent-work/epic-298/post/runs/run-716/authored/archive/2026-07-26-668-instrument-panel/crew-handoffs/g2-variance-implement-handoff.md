# Implementer Handoff — g2-variance-implement

## Gate
g2-variance-implement (#668 instrument panel, epic #659). Build in worktree
`C:/Programs/f1brainz-wt/epic659-668`, branch `epic659/668-instrument-panel`.
**Interpreter PIN:** `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Task
Build **Instrument 1 — the variance-decomposition instrument**: a PURE function that splits
segment-time variance into three shares — **car-reference / driver-utilization / residual** —
and reports the driver-utilization share as a **FLOOR**. This is the panel's "set the size"
instrument. New package `src/physics/instrument_panel/` (create `__init__.py` + the module).

## Protected Intent
This instrument SIZES the driver-utilization signal; it never gates. A mis-sized share
misdirects where Build-2 effort goes. The driver-utilization share must read as a floor (a
lower bound on how much of segment-time variance is driver, not car).

## Test Mode
TDD required — the instrument is pure math with a synthetic ground truth; each share must be
independently falsifiable.

## Close Criteria
- A pure function (e.g. `decompose_segment_time_variance(values, drivers, classes) ->
  VarianceShares`) returning `car_reference_share`, `driver_utilization_share`,
  `residual_share` (each in [0,1], summing to ~1.0 up to fp tolerance) plus a boolean/flag that
  the driver-utilization share is a FLOOR.
- Realized via the ADDITIVE `TwoWayPool` arithmetic in `src/physics/layer2/pooling.py`
  (`fit_two_way(values, teams=drivers, circuits=classes)`): **`frac_team` = driver-utilization
  share, `frac_circuit` = car-reference share, `frac_resid` = residual share.** NO bespoke
  model, NO interaction term (owner ruling 4 — the additive pool has none; do not add one).
- Synthetic tests: generate `value = a*car_effect[class] + b*driver_effect[driver] + noise`
  with KNOWN a,b (reuse `scripts/pooling_imbalance_validation_665.py`'s
  `draw_ground_truth`/generative style), and assert each recovered share tracks its injected
  coefficient monotonically (e.g. raising b raises driver_utilization_share; a pure-car signal
  gives driver_utilization_share ≈ 0; a pure-driver signal gives car_reference_share ≈ 0).
  Include an edge test: a degenerate single-class or single-driver input returns a sane result
  (no crash, shares still valid).
- pyright-0 on the pinned interpreter for the new module.

## Allowed Scope
- CREATE `src/physics/instrument_panel/__init__.py` (package marker + a short module docstring).
- CREATE `src/physics/instrument_panel/variance_decomposition.py`.
- CREATE `tests/unit/physics/instrument_panel/__init__.py` and
  `tests/unit/physics/instrument_panel/test_variance_decomposition.py`.
- READ-ONLY reuse: `src/physics/layer2/pooling.py`, `scripts/pooling_imbalance_validation_665.py`.

## Specific Exclusions
- Do NOT touch any #660/#664/#666/#667 producer module. Do NOT read any real DB — this
  instrument is pure and synthetic-tested (F12-independent; no frozen REPLICATION_* needed).
- Do NOT add an interaction term or any bespoke statistical model (owner ruling 4).
- Do NOT write any artifact to an `f1_data_*.db` (#632). No new DB needed here at all.

## Constraints
- Pure module; deterministic; numpy allowed (already a dep).
- `TwoWayPool` dataclass fields you will use: `frac_team`, `frac_circuit`, `frac_resid`,
  `var_team`, `var_circuit`, `var_resid`, `grand_mean`, `predict(team, circuit)`. Convention:
  `teams=drivers`, `circuits=classes` (the whole stack uses this — matches #665/#675).
- Match the house style of neighboring `src/physics/layer2/` modules (frozen dataclass return,
  explicit docstring, SI/unit notes where relevant).

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/pooling.py` (TwoWayPool, file-level); `src/physics/instrument_panel/` (new, file-level).
- **Capability:** driver-utilization measurement (variance sizing).
- **Constraints:** constraint:lowest-dimensionality (no interaction term); constraint:no-frame-kill (driver share = floor).
- **Decision anchors:** decision:consume-frozen-scorecard-triple — n/a here.
  `@grade: settled/inherited`
- **Evidence expectations:** each share recovers its synthetic ground-truth coefficient (monotone).

## Deliverable Path Check
- **Committed** — `src/physics/instrument_panel/__init__.py`, `variance_decomposition.py`,
  `tests/unit/physics/instrument_panel/__init__.py`, `test_variance_decomposition.py`; all
  verified `git check-ignore` exits 1 (not ignored). New files appear in `git status`, not yet
  in `git diff` until staged.

## Required Evidence
- LOAD-BEARING: the pytest run output showing the synthetic-recovery tests pass:
  `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_variance_decomposition.py -q`
- LOAD-BEARING: pyright-clean on the new module (state the command + 0 errors).
- Confirmatory: the shares sum to ~1.0 and lie in [0,1] on a spot example.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_variance_decomposition.py -q
```

## Suggested Model Tier
simple-bounded — well-specified pure-math reuse; the risk is the axis mapping, which is pinned above.

## Authority
The car-reference=frac_circuit / driver-utilization=frac_team mapping and the no-interaction
constraint are DECIDED (commander, from the launch order + #665/#675 convention). Do not
redesign them. If the additive pool cannot express one of the three shares cleanly, STOP and
return rather than inventing a model.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a real DB read seems required, an
interaction term seems needed, or the pool's fields cannot yield the three shares.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
(pytest + pyright output), assumptions, stop conditions hit, out-of-scope observations,
workflow feedback. WRITE THE RESULT to
`.agent-work/668-instrument-panel/crew-results/g2-variance-implement-result.md` before ending
your turn — that file is the deliverable.
