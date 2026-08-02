# Implementer Handoff — g2 (pilot pipeline orchestrator)

## Gate
`g2` (issue #669, epic-659 Wave 5a — the 3-circuit end-to-end pilot / tracer bullet)

## Task
Build a THIN orchestrator that wires the six ALREADY-LANDED epic-659 stages into ONE invocable, offline pipeline
and runs them per circuit, collecting each C/D/E/H GATING verdict + acceptance slots into a results JSON + report.
This is WIRING ONLY — call the existing stage functions/CLIs; build NO new model, NO new analysis, NO new frozen
constant. Lowest dimensionality.

## Protected Intent
Prove the MACHINE runs end-to-end before the season-scale bet (#670). The pipeline must be honest: a stage that
breaks or a gating check that fails must be REPORTED as broken (not masked); the archived-observables fallback is
for a genuine data-coverage/hang PARK only and must stamp provenance so a fall-back is never mistaken for a fresh run.

## Test Mode
test-after allowed (this is integration wiring; unit-test the pure helpers + the gating-collection + the
fallback/timeout branch + the non-empty assertions with fixtures — see Required Evidence).

## Close Criteria
- New package `src/physics/pilot/` (`__init__.py` + `pipeline.py`) + CLI `scripts/run_pilot_669.py` + a small
  structural verifier `scripts/verify_pilot_results_669.py` + tests under `tests/unit/physics/pilot/`.
- ONE command (`run_pilot_669.py`) runs, per circuit, the full chain C -> D -> E -> G -> H -> PANEL OFFLINE, writing
  ALL run artifacts to ISOLATED own-DB/scratch paths (an `--out-dir`, default under `.agent-work/669-pilot/artifacts/`).
- Emits `.agent-work/669-pilot/artifacts/pilot_results.json` (machine-readable, per-circuit) + a human report to
  `docs/physics/pilot_669_report.md` (the actual 3-circuit report file is produced by the RUN in g3; your code must
  be able to emit it — test the emitter against a temp path).
- Per-circuit results carry: the 6 acceptance slots (maps / grip-G+heldout-score / observables / fingerprint /
  join-prior / panel), a C/D/E/H gating pass/fail + numbers, and `provenance: "fresh" | "fell-back"` (+ reason).
- CRITIC-HARDENING (binding — each has a unit test):
  1. **Per-stage wall-time budget + auto-park (critic #5/#7):** invoke each HEAVY stage (E; and grip fit D if run
     as a subprocess) via `subprocess.run(..., timeout=<budget>)` with `env["PYTHONIOENCODING"]="utf-8"`. On timeout
     OR non-zero exit OR FastF1-fallthrough, PARK that circuit's fresh path and FALL BACK to the archived
     `fp_slice_2023Q.db` observables for the downstream G/H/PANEL stages, stamping `provenance="fell-back"` + reason.
     Attempt FRESH once per circuit before falling back. Budgets: E ~180s (probe measured 65s + validate ~60s, ~2x
     margin); grip ~180s. Do NOT rely on a human poll to detect a hang.
  2. **Two-segment-map consistency tripwire (critic #4):** per circuit, compare C's PERSISTED segment map
     (derive_segment_map -> scratch segment_maps.db) against E's LIVE re-derived map (E logs "segment map ...:
     N segments, k=4"): assert segment COUNT matches (and a boundary signature if cheap); record any divergence as a
     flagged finding in the results. Do NOT unify the two paths (out of scope) — just tripwire.
  3. **Non-empty/finite gating (critic #8):** a stage that ran without raising but produced N=0 rows / null / non-finite
     params is a FAIL, not a vacuous pass. Assert: observables rows > 0; fingerprint cells populated (k per driver/
     channel) with finite mean/sigma; join prior non-null with finite mean.
  4. **grip-G vs fingerprint naming (critic #9):** the results schema must name the D-stage grip held-out score as
     `grip_g` distinctly from the fingerprint stage (`fingerprint`).
- CLOSE CRITERION (critic #1 — binding): demonstrate `run_pilot_669.py` runs the FULL C->D->E->G->H->PANEL chain on
  ONE circuit (Great Britain) OFFLINE end-to-end GREEN, and paste the console tail as evidence. The FIRST full-chain
  run must NOT be the unattended g3 run.
- pyright-0 on the new `src/physics/pilot/` module + the two scripts.
- `tests/unit/physics/pilot/` green on the pinned 3.14 interpreter.

## STAGE WIRING (source-verified entry points — call these; do NOT reinvent)
Per circuit (Monaco r6, Great Britain r10, Belgium r12 — all 2023 Q; drivers VER,PER,LEC,SAI):
- **C (segment map + gating):** `from src.physics.segment_map.derivation.derive import derive_segment_map` ->
  persist to a scratch `segment_maps.db` via its store; C GATING = reuse `split_half_boundary_drift` from
  `scripts/validate_segment_map_662.py` and assert `median_drift_m < MAP_STABILITY_DRIFT_M` (=10, from
  `src/physics/layer2/frozen_constants.py`); record physical corner count as DESCRIPTIVE (the Bahrain/Austria typing
  spot-checks in validate_segment_map_662 are for THOSE circuits, not the pilot slice — do not force them here).
- **D (grip-G fit + held-out score):** `from src.physics.layer2.grip_batch import run_grip_batch` to fit grip for the
  3 circuits' 2023-Q sessions into a scratch `grip_estimates` DB (`GripStore`), producing "fitted grip-G". Compute a
  held-out reconciliation SCORE by reusing the held-out logic exercised in
  `tests/unit/physics/layer2/test_grip_heldout.py` (fit on a team-stratified split, measure before/after RMS on held-out
  drivers). D GATING for the tracer bullet = the fit COMPLETES + a held-out score is PRODUCED (+ optionally the
  synthetic separability harness `test_grip_synthetic_recovery.py` reproduces recovery>=90% / |corr| high). IMPORTANT:
  the grip held-out score is EXPECTED to show grip WORSENS reconciliation (#663 measured null: +155% RMS; grip is
  non-identifiable, ships mu=0 one-sided sigma+) — that WORSE score is the KNOWN MEASURED FINDING, NOT a gate fail.
  The D gate FAILS only if the fit crashes or produces no score. If a circuit's held-out split is too thin, that is a
  data-coverage PARK (honest gap), not a fail.
- **E (reference laps + observables + gating):** invoke `scripts/build_class_utilization_observables.py` as a SUBPROCESS
  (timeout+utf-8 per critic #5) with `--year 2023 --session-type Q --rounds <r> --drivers VER,PER,LEC,SAI --db
  <scratch>/refutil_<circuit>.db --estimate-store C:/Programs/f1Brainz/data/physics_estimates.db --grip-bin-db
  C:/Programs/f1Brainz/data/damage_integrals.db --telemetry-store C:/Programs/f1Brainz/data/telemetry_store.db
  --per-year-db <scratch-copy-of-f1_data_2023.db> --grip-store <scratch>/grip_estimates.db --validate
  --artifact-dir <scratch>/e_artifacts_<circuit>`. E GATING = read the `--validate` jackknife artifact: assert
  `within_anchor` true (boundary drift < MAP_STABILITY_DRIFT_M) AND the positive control FIRED. **Reversibility:** COPY
  the worktree `data/f1_data_2023.db` to a scratch path ONCE and pass THAT as `--per-year-db` (fully avoids dirtying
  the tracked DB); do NOT point --per-year-db at the tracked worktree/main copy.
- **G (fingerprint smoke fit):** `from src.physics.fingerprint.fit import fit_driver_fingerprints` +
  `from src.physics.fingerprint.store import DriverFingerprintStore` — fit each driver in-process on E's
  `driver_class_observables` (the scratch refutil DB) into a scratch fingerprint DB, `as_of_round=<circuit round>`
  (strictly-pre — do NOT read past it), both channels. G GATING = k cells written per driver/channel, all statuses set,
  finite mean/sigma (non-empty assertion). Do NOT use the bounded-validation CLI (it needs an abs --slice-db + does
  extra work) — call the core fit.
- **H (the join + t7 gating):** `from src.physics.fingerprint.join import join_weekend_prior` — composition =
  E's `reference_laps` field-fingerprint (`ReferenceUtilizationStore(...).get(...).fingerprint`) x G's cells
  (`DriverFingerprintStore.get_fingerprint(...)`, in-memory list) -> `WeekendUtilizationPrior`. H GATING = the 4
  reduces-to-simple-case invariants: run `tests/unit/physics/fingerprint/test_join.py::test_t7_1 .. test_t7_4` via
  pytest (subprocess) as the H gating-check AND assert the circuit's real join prior is non-null with finite mean.
- **PANEL (dry-run):** `from scripts.instrument_panel_668_report import run_panel` (or invoke the CLI as a subprocess
  with utf-8) on E's raw observables (`--no-write`/dry-run so it does not clobber the committed #668 report). PANEL is
  a SIZING dry-run (no hard gate) — record it ran + produced instrument outputs.

## Allowed Scope
CREATE: `src/physics/pilot/__init__.py`, `src/physics/pilot/pipeline.py`, `scripts/run_pilot_669.py`,
`scripts/verify_pilot_results_669.py`, `tests/unit/physics/pilot/__init__.py`, `tests/unit/physics/pilot/test_*.py`.
You MAY import (read-only) from the landed stage modules named above. You may reuse `split_half_boundary_drift` /
the held-out harness helpers by importing them.

## Specific Exclusions
- Do NOT modify ANY landed stage module (segment_map/*, layer2/*, utilization/*, fingerprint/*, instrument_panel/*)
  — pure consumer. Do NOT unify the two segment-map paths (#671). Do NOT touch `docs/architecture/*` (map fence,
  #671). Do NOT edit or overwrite the committed `docs/physics/instrument_panel_668_*` report (PANEL runs dry-run).
- Do NOT mint a frozen constant (a needed threshold is a FLOAT to the Admiral — stop and return).
- Do NOT write to any `data/f1_data_*.db` (tracked) or touch the FastF1 cache. Do NOT `git add -A`.

## Constraints
- OFFLINE ONLY — no FastF1 online call; all inputs from on-disk stores (absolute MAIN paths for the gitignored
  physics_estimates.db / telemetry_store.db / damage_integrals.db; a SCRATCH COPY of f1_data_2023.db for --per-year-db).
- Consume the LANDED frozen sets (MAP_STABILITY_DRIFT_M, REPLICATION_*, etc. from frozen_constants.py); mint nothing.
- Strictly-pre causal cutoffs preserved (fingerprint as_of_round = the circuit round; never read past it). No baked
  normality — preserve the Student-t sigma the stages carry.
- Interpreter PIN `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`; add the worktree-first `.pth`
  guard to the bare CLI scripts (`_REPO_ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(_REPO_ROOT))`)
  so they import the WORKTREE's src (esp. the new pilot module), not the global editable install.
- pyright-0 on the new module + scripts.

## Map Anchors (inbound)
- **Structural:** `struct:physics.pilot` (NEW src/physics/pilot/pipeline.py + scripts/run_pilot_669.py); consumes
  struct:physics.{segment_map.derivation, layer2 grip, utilization, fingerprint, instrument_panel}.
- **Capability:** `capability:pilot-orchestration` — compose 6 stages per-circuit + collect C/D/E/H gating + emit report.
- **Constraints:** constraint:offline-only, constraint:reversibility-isolated-own-db, constraint:frozen-sets-consume-only,
  constraint:strictly-pre-no-leakage, constraint:pyright-0-new-module.
- **Decision anchors:**
  `decision:pilot-fresh-vs-archived` — FRESH is the default (g1 probe measured offline+tractable); archived
  fp_slice_2023Q.db is the per-stage-timeout/park-on-hang net only, provenance-stamped.
  `@grade: settled/measured · leans g2-implement`
  `decision:two-segmap-paths` — run C persisted + gating AND let E re-derive live; tripwire the consistency, do NOT unify.
  `@grade: settled/inherited`
  `decision:pass-vs-limitation-boundary` — a C/D/E/H GATING FAIL = machine broken (report/float), NOT an "honest
  finding"; only a data-coverage PARK is complete-with-gap. `@grade: settled/measured`
- **Evidence expectations:** the GB full-chain offline run is green; results JSON structurally complete (3 circuits x
  6 slots x C/D/E/H verdict x provenance); non-empty/finite assertions hold.
- **Map confidence flags:** durable arch map is stale-by-design for all epic-659 stages (deferred to #671); plan from
  code, not the map — do NOT edit docs/architecture/*.

## Deliverable Path Check
- **Committed:** `src/physics/pilot/pipeline.py`, `src/physics/pilot/__init__.py`, `scripts/run_pilot_669.py`,
  `scripts/verify_pilot_results_669.py`, `tests/unit/physics/pilot/*` — verify each with `git check-ignore <path>`
  exiting 1 (not ignored) before you claim the diff. New files are untracked until staged (`git status`, not `git diff`).
- **Local-only (run artifacts, gitignored):** `.agent-work/669-pilot/artifacts/pilot_results.json`, the scratch DBs.
- **Committed (produced in g3, but your emitter targets it):** `docs/physics/pilot_669_report.md`.

## Required Evidence
- **Load-bearing (prove rigorously):** (1) the GB full-chain offline run console tail showing all 6 stages ran +
  a per-circuit results object; (2) `pytest tests/unit/physics/pilot/ -q` green on pinned 3.14; (3) pyright-0 on the
  new module (`pyright src/physics/pilot/ scripts/run_pilot_669.py scripts/verify_pilot_results_669.py` or the repo's
  pyright invocation, scoped); (4) a unit test proving the fallback/timeout branch stamps provenance="fell-back";
  (5) a unit test proving the non-empty/finite gating FAILS on a zero-row/null fixture.
- **Confirmatory (spot-check):** the two-map consistency tripwire fires on a divergence fixture; verify_pilot_results_669.py
  exits non-zero on a results JSON missing a circuit/slot.
- FIXTURE SHORTCUT: the g1 probe already produced a real GB scratch observables DB at
  `C:/Users/fredc/AppData/Local/Temp/claude/C--Programs-f1Brainz/75f751ad-3984-44e8-a745-c0c90f57a861/scratchpad/probe_gb.db`
  (3 reference_laps + 24 driver_class_observables, VER/PER/LEC/SAI). Use it to develop/test G/H/PANEL wiring without
  re-running E each iteration.

## Verification Commands
```bash
PY="C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe"
# unit tests
"$PY" -m pytest tests/unit/physics/pilot/ -q
# GB full-chain offline smoke (paste console tail)
"$PY" scripts/run_pilot_669.py --circuits "Great Britain" --out-dir .agent-work/669-pilot/artifacts
# structural verifier self-check
"$PY" scripts/verify_pilot_results_669.py .agent-work/669-pilot/artifacts/pilot_results.json
# pyright on the new module (scoped)
pyright src/physics/pilot/ scripts/run_pilot_669.py scripts/verify_pilot_results_669.py
```

## Suggested Model Tier
stronger — reason: 6-stage integration with several silent-correctness traps (fallback masking, vacuous-pass,
two-map divergence), AFK-critical, many wiring seams.

## Authority
Decisions already made (do NOT re-open): FRESH default + archived fallback shape (Admiral/Commander, g1-measured);
two-segmap tripwire-not-unify; grip-G ships mu=0 sigma+ (epic ruling); the frozen sets are consumed as-is. You must
NOT decide alone: any new threshold/constant (FLOAT), any change to a landed stage, any scope beyond wiring.

## Stop Conditions
Stop and return IMPLEMENTER_RESULT if: a landed stage must be modified to wire it; a new constant/threshold is needed;
the GB full-chain cannot run offline; allowed scope must be exceeded; or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (paste the GB
full-chain console tail + pytest + pyright results), assumptions used, stop conditions hit, out-of-scope observations,
workflow feedback. Deliver it via SendMessage to cmdr-669 before ending your turn, and write it to
`.agent-work/669-pilot/crew/g2-implementer-result.md`.
