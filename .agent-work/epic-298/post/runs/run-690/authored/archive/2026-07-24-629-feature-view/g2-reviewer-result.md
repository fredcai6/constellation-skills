# Review Result

## Assigned Gate
`g2` — #629 feature-view Phase-5, `src/physics/feature_view/build_weekend_state.py`

## Result
`APPROVE`

## Handoff compliance
All close criteria independently verified, not taken on the implementer's word:

- **Column names read from the model's own accessors, not hardcoded**: confirmed by reading `model.py` lines 186-203 directly — `model_cols()` returns `{axis: f"{axis}_car_signal"}`, `layer_sigma_cols()` returns a per-axis ordered list whose LAST entry is always `f"{axis}_car_signal_sigma"`. `build_weekend_state.py` lines 123-126 build its `value_cols`/`sigma_cols` dicts from these two accessors at runtime.
- **Per-row/per-axis resolved/unresolved rule, adversarially verified**: constructed an independent scratch probe (`scratchpad/probe_g2.py`, own model fit on my own synthetic frame, not the implementer's fixtures) that forced THREE different axis outcomes on ONE row in a single call — one axis fully unresolved (NaN value+sigma → `None`/`None`, matching a direct `effective_axis_sigma(None, None, "unresolved")` call), a second axis left alone (stayed `resolved`, sigma passed through unchanged, verified numerically equal to the source column), a third axis forced to "value present, sigma NaN" (`unresolved`, value carried through unchanged, sigma widened to exactly `UNRESOLVED_AXIS_SIGMA_FRAC * abs(value)`). A DIFFERENT, untouched row in the SAME `records` list from the SAME call showed all three axes `resolved`. This proves the rule is genuinely per-row (the mixed row's forced statuses did not leak elsewhere) AND per-axis (three distinct outcomes on one row) — not a blanket constant.
- **`effective_axis_sigma` imported, not reimplemented**: confirmed the import statement (`build_weekend_state.py` line 84) and that the real function body (`estimate_store_fields.py` lines 139-169) matches the module docstring's claimed behavior exactly.
- **No `src.evo_predictor` import**: `grep -rn "evo_predictor" src/physics/feature_view/build_weekend_state.py` → clean.
- **Full suite reproduced**: `py -m pytest tests/unit/physics/feature_view -v` → 33 passed (27 G1 + 6 new), test-for-test identical to the implementer's claim.
- **`round_idx` omission reasoning sanity-checked against a real counterexample search**: programmatically scanned `src.utils.constants.F1_CALENDARS` across all 9 tracked years (2018–2026, including the COVID-restructured 2020 season, which historically ran same-circuit-different-name races e.g. Austria/Styria at the Red Bull Ring) — zero repeated `gp_name` within any single year. Also independently confirmed the sibling `src/physics/layer2/estimate_store.py`'s own natural key `_PK = ("year", "gp_name", "session_type", "constructor")` ALREADY omits `round_idx` — this is an established, precedented convention the composer is following, not a new invented claim.
- **`simplification_limits --paths src/physics/feature_view`**: reproduced, `PASS (4 files checked)`.

## Scope drift
None. `git status --porcelain` shows only 3 untracked paths: `.agent-work/629-feature-view/` (workbench), `src/physics/feature_view/` (new `build_weekend_state.py` + G1's pre-existing 3 files), `tests/unit/physics/feature_view/` (new test file + G1's 3 test files). File mtimes confirm `records.py` (08:25) and `store.py` (08:34) predate `build_weekend_state.py` (08:59) — untouched this gate. `__init__.py` content still reads "This gate (G1) builds only the store foundation" with no new export added, confirming G1 files were genuinely not modified. Specific Exclusions honored: no G1 defect found either (nothing to flag out-of-scope there).

## Evidence verdict
All implementer evidence independently reproduced verbatim: 33/33 tests, `simplification_limits` PASS (4 files), evo-import grep clean, `git check-ignore` exit=1. TDD red→green evidence is a real `ModuleNotFoundError` followed by a real passing run — accepted as-is (no implementer-supplied number was taken without a from-scratch reproduction of the equivalent check). Additionally produced my own adversarial evidence (not just re-running the implementer's tests) per the Close Criteria's explicit demand — see Handoff compliance above.

## Code/doc quality
Minimal, single-purpose composer (~30 line function body). Fowler pass run to completion (12/12 smells visited, 0 flagged, 2 overridden — `data-clumps` and `primitive-obsession`, both citing the same standard G1 already logged: `estimate_store.py`'s `_PK`/raw-str convention, plus the fact that `WeekendStateRecord`'s shape is G1's frozen decision, not this gate's to revisit). `verify_fowler_pass.py` exits 0. Two non-blocking observations recorded (see Out-of-scope observations).

## Map impact verdict
- **Evidence supports claimed change:** Yes — the claimed resolved/unresolved contrast and widening behavior were independently reproduced with fresh numbers, not just re-read from the implementer's report.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` clean (grep-verified); `effective_axis_sigma` reused not reimplemented (verified at source); `WeekendStateModel.fit/transform`'s no-leakage contract consumed read-only, not touched.
- **Notes match the diff:** Yes — Map Impact accurately describes a new composer module inside the existing G1 package, no reverse dependency, decision candidates properly scoped to what the handoff pre-authorized.
- **Decision candidates surfaced:** The resolved/unresolved rule is correctly flagged as a new (but pre-authorized) convention; the "no reference_value table" gap is correctly flagged as a future decision candidate, not silently built.
- **Durable context routed:** Nothing beyond what the handoff already scopes to G3-G5 (composers for `CarBasisPosteriorRecord`/`LapEvidenceRecord`/`FeatureViewRow`).

## Reconciliation check
No divergence from recorded architecture. `docs/architecture/packets/physics.md` documents `struct:physics.weekend_state` in detail but has no `struct:physics.feature_view` entry yet — consistent with feature_view being a genuinely new, still-mid-epic component not yet due for Cartographer mapping (matches G1's own reviewer finding). `build_weekend_state.py` consumes `WeekendStateModel` read-only, exactly as documented.

## Blockers
- none

## Out-of-scope observations
- **Non-blocking, this gate**: `build_weekend_state_records`'s row-dict access (`row["year"]`, `row["gp_name"]`, etc.) raises a bare `KeyError` rather than a field/expectation/actual-named `ValueError` if `transformed_df` is missing an expected column — the project's CREW_CONTEXT convention is "validation exceptions name field, expectation, and actual value when practical." Judged non-blocking here: this is an internal composer with a documented caller precondition (`model.transform()`'s own output), not a public/external-data boundary, and a `KeyError` still fails visibly (never silently). Worth a one-line fix if a future gate turns this into a more general-purpose entry point.
- **Non-blocking, this gate**: `_none_if_nan`'s `except TypeError: return x` clause (source line ~106) is unreachable as written — `isinstance(x, float)` is `False` for non-float inputs, so the guarded line never raises inside the `try` block it wraps. Independently reproduced that `_none_if_nan(pd.NA)` raises an UNCAUGHT `TypeError` from the trailing `float(x)` call, contradicting what the `except` clause implies it handles. Confirmed non-triggering today: `WeekendStateModel.transform()` builds every axis column via `.to_numpy(dtype=float)` / `np.zeros` throughout — plain `float64` + `np.nan`, never pandas nullable `Float64`/`pd.NA`. Flagging as a latent trap for a future caller that feeds nullable-dtype columns, not a current defect. Not filed as a GitHub issue (too small/speculative for a formal triage ticket at this gate); noted here for Commander's awareness.
- Beyond the above: none beyond what the handoff already names as G3-G5's job (CarBasisPosteriorRecord/LapEvidenceRecord/FeatureViewRow composers, real process-noise-link/parc-ferme fits).

## Workflow Feedback
- **Handoff gaps:** none — the handoff named exact close criteria, exact functions to verify (`model_cols()`/`layer_sigma_cols()`), and gave concrete counterexample-search guidance (a repeated-`gp_name` calendar year) that was directly actionable.
- **Context rediscovered:** `docs/agents/CREW_CONTEXT.md` and `GLOSSARY.md` DO exist in this worktree (my first `ls` pass on `r0-context` mistakenly reported them missing before I actually listed `docs/agents/`; corrected in the same survey item once caught — see `r0-context`'s finding). Worth noting for future reviewers: don't trust a first quick look — actually `ls` the directory before asserting a file is absent.
- **Instructions improvised around:** none. The handoff's `--paths` correction and PATH-prepend note (bare `py` resolving to a pytest-less interpreter) both matched exactly as documented; no deviation needed.
- **What would have made this easier:** nothing concrete — this was an unusually precise handoff (exact line-range citations, exact accessor names, a genuinely falsifiable round_idx claim with a concrete counterexample shape named). The one friction point was self-inflicted (see Context rediscovered above), not a handoff gap.

## Return status
`complete`
