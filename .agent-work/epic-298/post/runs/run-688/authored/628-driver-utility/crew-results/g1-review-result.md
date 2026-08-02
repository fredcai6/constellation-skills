# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` (epic #601 wave-7 issue #628, driver-utility observable + resumable batch CLI)

## Result
`APPROVE`

verdict: APPROVE

## Survey
Driven end-to-end through the checklist engine at
`.agent-work/628-driver-utility/g1-review-survey.json` (session `ShipH-628-g1-review`), 8 items
(`r0-context, r1-handoff, r2-scope, r3-evidence, r4-quality, r5-reconciliation,
r-simplification-limits, r6-fowler`), all recorded `pass`, consolidated `APPROVE` with 0 findings on
the survey itself (0 open fails). Fowler-pass record at
`.agent-work/628-driver-utility/g1-fowler-pass.json`, `verify_fowler_pass.py` exit 0.

## Handoff compliance
Fully satisfied. The three deliverables named in the handoff are present and each independently
re-verified (not just re-read from the implementer's report):

1. `src/physics/utilization/driver_utility_observable.py` — `compute_regime_deficits` is a pure
   function reusing `regime_utilization._build_regime_masks` (imported at line 53, not reinvented).
   The per-regime metric is `deficit = v_ideal - v_real` (line 215) — a subtraction, never a ratio.
2. `scripts/build_driver_utility_observables.py` — resumable batch CLI. Builds ONE
   `build_car_ceiling(..., strictly_pre=True)` + ONE `simulate_lap` per `(constructor, round)`,
   shared across that constructor's requested drivers (`_process_constructor`, lines 268-302).
   `v_real` comes from the lean `fit_best_lap_trace` (not `fit_session_full`). Idempotent
   skip-if-present per axis and per error row. A round with no causal history writes one error row
   per driver instead of crashing the batch.
3. `tests/unit/physics/test_driver_utility_observable.py` — 8 unit tests, synthetic arrays only.

## Scope drift
None. `git diff --stat` against tracked files is empty — zero modification to
`regime_utilization.py`, `car_prior.py`, `session_fit.py`, or `characterize.py` (all imports from
those modules are read-only reuse). `git status --porcelain` shows only the 3 new files plus
`.agent-work/` and the untracked scratch DB. G2 (latent estimator) and G3 (gate harness) were
correctly not built, matching the handoff's explicit exclusion.

## Evidence verdict
All required evidence reproduced independently, in-turn, not accepted on the report's word:

**pytest (re-run):**
```
$ py -m pytest tests/unit/physics/test_driver_utility_observable.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-628
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 8 items

tests\unit\physics\test_driver_utility_observable.py ........            [100%]

============================== 8 passed in 1.15s ==============================
```

**F4 grep (re-run, handoff's literal command):**
```
$ grep -nE "v_real ?/ ?v_ideal|/ ?v_ideal|observed ?/ ?cap" src/physics/utilization/driver_utility_observable.py scripts/build_driver_utility_observables.py
(no output, exit 1 = no match)
```
Went further than the literal grep: ran an unscoped bare-`/` division scan across both files and
manually inspected every hit. Every division in the diff is either `std(...) / sqrt(n_points)` (the
SEM formula, operating on the deficit array, never on `v_real`/`v_ideal` individually) or docstring
prose/paths (`m/s`, `1/m`, `PYTHONPATH=...`). No division of `v_real` by `v_ideal`, or of any
"observed" by "capability" quantity, anywhere in either file.

**Ceiling+sim sharing (independently reproduced BEHAVIORALLY, not read from source only):**
Instrumented `build_car_ceiling` and `PhysicsSimulator.simulate_lap` with call counters via
`unittest.mock.patch`, then ran the CLI fresh on 2023 round 6 (Monaco) with `VER,PER` (both Red Bull
Racing — same constructor):
```
CALL COUNTS: {'build_car_ceiling': 1, 'simulate_lap': 1}
```
Confirms the "one ceiling + one sim per constructor-round, shared across drivers" claim is actually
true, not merely asserted.

**Idempotency (independently reproduced):**
```
$ py -c "..." # row count before
rows before: 8
$ PYTHONPATH=C:/Programs/f1-628 py scripts/build_driver_utility_observables.py --year 2023 --session-type Q --rounds 5 --drivers VER,PER --db data/driver_utility_observables.db
Loaded 216 ok-status estimate rows for 2023 Q from C:/Programs/f1Brainz/data/physics_estimates.db
round 5 (Miami): all requested drivers already present -- skipping
Done. Rows persisted to data/driver_utility_observables.db
$ py -c "..." # row count after
rows after re-run: 8
```
Row count unchanged (8 → 8); the 8 pre-existing rows in `data/driver_utility_observables.db` matched
the implementer's claimed output values exactly (spot-checked byte-for-byte against the result doc).

**strictly_pre=True (verified in `car_prior.py` source, not just cited):**
```
$ grep -n "strictly_pre" src/physics/utilization/car_prior.py
144:    strictly_pre: bool = False,
...
219:    mask = rounds < float(target_round) if strictly_pre else rounds <= float(target_round)
```
`strictly_pre=True` uses `round_idx < target_round` (strict), confirming the target round is
excluded from the causal ceiling's history — the ceiling is a purely predictive prior, matching the
F4 anti-circularity requirement.

**`fit_best_lap_trace` is the lean path (verified in `session_fit.py`):**
Its own docstring: "A cheap subset of `fit_session_full`'s chain... skipping every other flying
lap's smoothing AND `ParameterEstimator.estimate_parameters` entirely (the single most expensive
step)." Confirms claim (b) in the module docstring.

**git status data/:**
```
$ git status --porcelain data/
?? data/driver_utility_observables.db
```
Only the untracked scratch DB; nothing under `data/` is staged.

**simplification_limits (re-run):**
```
$ py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility_observable.py scripts/build_driver_utility_observables.py tests/unit/physics/test_driver_utility_observable.py
PASS (3 files checked)
```

## Code/doc quality
Minimal, maintainable, tested, project-rule compliant. Checked against `CREW_CONTEXT.md` +
`engine-config.json`'s `rules_root`: no `fastf1` import in either new file (DB-only access rule);
`_validate_inputs` names field/expectation/actual; TDD evidence present for the pure function;
`strictly_pre=True` satisfies the as-of-cutoff rule; missingness (`None` for thin regimes, `axis IS
NULL` error-row sentinel) is intentional, never zeroed/guessed; test docstrings label L1/L2 per
`TESTING.md`'s truth-level convention; no mutable module-level state or `DatabaseManager` singleton;
regime thresholds are named constants forwarded unchanged from `regime_utilization`, not inline
magic numbers.

**Fowler pass** (`r6-fowler`, mandatory, all 12 baseline smells visited, 0 skipped,
`verify_fowler_pass.py` exit 0): 3 flagged as non-blocking observations, 9 absent, 0 overridden.
- **duplicated-code (flagged):** `driver_utility_observable.py`'s `_validate_inputs` (lines 112-137)
  is a ~25-line near-verbatim copy of `regime_utilization.py`'s own `_validate_inputs` (same 4
  checks, nearly identical messages). Worth extracting to a shared helper on a future touch of
  either module. Does not affect correctness or F4.
- **data-clumps (flagged):** the `(year, session_type, gp_name, round_idx[, constructor, driver])`
  identifier tuple recurs as separate keyword params across ~9 of the CLI's functions. A small
  context object would collapse it, and would pay off further once G2/G3 extend the same schema.
  (The per-axis field group in `RegimeDeficits` mirrors the sibling `RegimeUtilization`'s
  established shape for the same 4-regime domain — that instance is not flagged, it matches
  surrounding conventions per `global-crew.md`.)
- **long-parameter-list (flagged):** `_process_constructor`/`_process_driver` each carry ~11 params
  — same root cause as the data-clumps finding. Mitigated today by all-keyword-only call sites
  (readable, if verbose).

None of the three flagged items are blockers — full record at
`.agent-work/628-driver-utility/g1-fowler-pass.json`.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in the implementer's Map Impact section
  was independently reproduced above (F4 no-ratio, shared ceiling/sim, idempotency, lean fit path).
- **Constraints not violated:** yes — `constraint:no-ratio-observable` (F4) and `constraint:db-only`
  both honored and independently verified; `decision:c1_driver_utilization_design` followed
  faithfully (causal through-W ceiling, both-teammate frontier, split-impure posture unchanged) and
  not re-opened.
- **Notes match the diff:** yes — the structural anchors, capability description, and evidence
  claims all match what the diff actually contains; no overstatement found.
- **Decision candidates surfaced:** n/a — no new authority-requiring decision arose in this gate.
- **Durable context routed:** yes — the `.gitignore` gap for the scratch DB was already surfaced by
  the implementer as a triage candidate and is re-flagged below (out-of-scope, non-blocking).

## Reconciliation check
No architecture divergence requiring Commander/Pilot reconciliation. The new files land inside the
already-mapped `struct:physics.utilization` component (`docs/architecture/packets/physics.md` line
1217, `path: src/physics/utilization/`) as an additive extension that follows
`decision:c1_driver_utilization_design` faithfully. The map doesn't yet list the two new files by
name — expected content drift for Cartographer's next pass (this is G1 of a multi-gate build; G2/G3
still pending), not a review-blocking gap.

## Blockers
- none

## Out-of-scope observations
- `data/driver_utility_observables.db` (the scratch DB this CLI writes) is not covered by any
  `.gitignore` glob — independently confirmed via `git check-ignore -v` (exit 1 = not ignored) and
  inspection of `.gitignore`'s `data/` section (only individually-named DBs are listed, no
  `data/*.db` wildcard). Recommend a follow-up to add an explicit ignore entry. Already surfaced by
  the implementer; re-confirmed independently here and flagged as a triage candidate (`tc1`) on the
  survey.
- Fowler-pass findings (duplicated-code, data-clumps, long-parameter-list) — see Code/doc quality
  above; candidates for a future cleanup pass, not this gate.

## Workflow Feedback
- **Handoff gaps:** none material. The handoff's F4 grep command (`grep ... || echo NO-RATIO-OK`) is
  non-blocking as literally written (grep exits 0 on a match, so `||` never fires) — the implementer
  already flagged this and built a strict inverted gate form for the actual engine postcondition; I
  used the same literal form for human-readable evidence but ran a broader unscoped division scan on
  top of it for independent verification, since the literal command alone would not have caught a
  cleverly-renamed alias of the forbidden ratio.
- **Context rediscovered:** none beyond what the handoff's "Exact seam signatures" pointed at —
  `strictly_pre`'s `<` vs `<=` semantics in `car_prior.py` and `fit_best_lap_trace`'s "cheap subset"
  docstring both confirmed the handoff's claims on first read of the cited files.
- **Instructions improvised around:** the project-local `.agent-work/templates/REVIEW_SURVEY.template.json`
  carries `r-simplification-limits` in place of the skill-bundled `r6-fowler`; per the skill's
  "append checks the context warrants," both were included in this survey (project delta +
  skill-mandated Fowler pass) rather than choosing one over the other.
- **What would have made this easier:** nothing significant — the handoff's "Exact seam signatures"
  section and the implementer's Map Impact/evidence sections were unusually complete and accurate,
  which made independent reproduction (rather than just re-reading the report) fast.

## Return status
`complete`
