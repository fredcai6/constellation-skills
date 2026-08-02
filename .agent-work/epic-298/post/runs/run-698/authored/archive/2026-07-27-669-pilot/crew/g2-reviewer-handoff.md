# Reviewer Handoff — g2 (pilot pipeline orchestrator)

## Gate
`g2` (issue #669, epic-659 Wave 5a — 3-circuit end-to-end pilot / tracer bullet)

## Survey State Location
Create your survey at `.agent-work/669-pilot/g2-review/review.json` (NOT the worktree root).

## What Was Implemented
A THIN offline orchestrator wiring the six landed epic-659 stages (C segment-map → D grip-G → E reference-laps+
observables → G fingerprint → H join → PANEL) into ONE per-circuit command. New package `src/physics/pilot/`
(`__init__.py`, `pipeline.py`) + `scripts/run_pilot_669.py` + `scripts/verify_pilot_results_669.py` +
`tests/unit/physics/pilot/` (5 files, 29 tests). Emits a per-circuit `pilot_results.json` + a markdown report.
Pure consumer — no landed-stage edit, no new model, no new frozen constant.

## How to Inspect the Diff
Worktree `C:/Programs/f1brainz-wt/epic659-669`, branch epic659/669-pilot. Review the UNCOMMITTED working tree (NOT
`git diff main...HEAD`). Use `git status --porcelain` then `git diff` (untracked-safe). The new files show under
`git status` (untracked until staged), NOT `git diff`. Pinned interpreter for any run:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` (NEVER bare `py`).

## Task Statement
Wire the 6 landed stages into ONE offline invocable pipeline, run per circuit (Monaco/Great Britain/Belgium 2023-Q,
drivers VER/PER/LEC/SAI), collect each C/D/E/H GATING verdict + acceptance slots + fresh|fell-back provenance into a
results JSON + report. WIRING ONLY. Full handoff: `.agent-work/669-pilot/crew/g2-implementer-handoff.md` (read it).

## Close Criteria (each a review check)
- Deliverables present + tracked-able (`git check-ignore` exits 1): src/physics/pilot/{__init__,pipeline}.py,
  scripts/run_pilot_669.py, scripts/verify_pilot_results_669.py, tests/unit/physics/pilot/*.
- THIN wiring: pure consumer of the landed stages — NO new model/analysis, NO landed-stage module edited, NO new
  frozen constant minted (verify by reading pipeline.py — it should import+call, not reimplement).
- The full C→D→E→G→H→PANEL chain runs OFFLINE on Great Britain end-to-end GREEN. RE-RUN IT YOURSELF:
  `"$PY" scripts/run_pilot_669.py --circuits "Great Britain" --out-dir <a scratch dir>` and confirm: provenance=fresh,
  all C/D/E/H gates PASS, all 6 slots ran, C n_segments == E live-rederived segment count (two-map tripwire silent),
  C median_drift_m < 10, E within_anchor=True + positive control fired. (This is a ~1-2 min offline run.)
- `"$PY" -m pytest tests/unit/physics/pilot/ -q` green on pinned 3.14 (implementer reported 29 passed) — RE-RUN.
- pyright-0 on the new module + scripts — RE-RUN (`"$PY" -m pyright src/physics/pilot/ scripts/run_pilot_669.py scripts/verify_pilot_results_669.py`).
- The four critic-hardening items are REAL + non-vacuous (read the tests): (1) per-stage wall-time budget auto-parks +
  falls back to archived fp_slice observables with provenance="fell-back" — verify the fallback test actually exercises
  the timeout/fallthrough branch; (2) two-segment-map count tripwire flags divergence (verify the divergence fixture
  test fails-loud, does not unify); (3) non-empty/finite gating FAILS on zero-row/null/non-finite fixtures (verify the
  negative tests); (4) results schema names grip_g distinctly from fingerprint.

## Allowed Scope
CREATE only: src/physics/pilot/*, scripts/run_pilot_669.py, scripts/verify_pilot_results_669.py, tests/unit/physics/pilot/*.
Read-only imports from landed stage modules are allowed.

## Specific Exclusions (flag if touched)
No landed stage module edited (segment_map/*, layer2/*, utilization/*, fingerprint/*, instrument_panel/*); the two
segment-map paths tripwired NOT unified; docs/architecture/* untouched; the committed docs/physics/instrument_panel_668_*
report untouched (PANEL runs dry-run). NOTE: the archived fp_slice path is on the MAIN checkout (outside your worktree)
— that reference is Commander-verified, not a BLOCK on un-inspectability.

## Constraints the Implementation Must Respect (each a review check)
- OFFLINE ONLY — no FastF1 online call. Verify: gitignored input stores read from absolute MAIN paths; E's --per-year-db
  is a SCRATCH COPY of f1_data_2023.db (NOT the tracked worktree/main copy); no write to any data/f1_data_*.db; no
  FastF1 cache touch. Confirm `git status` shows no ` M data/f1_data_*.db` attributable to the pipeline (a pre-existing
  worktree dirty DB is noted-not-blocked; the Commander restores it).
- Strictly-pre causal cutoffs preserved: fingerprint as_of_round = the circuit round; round_idx <= as_of_round; no read
  past the cutoff (no race-outcome leakage).
- Frozen sets consumed not minted (MAP_STABILITY_DRIFT_M etc. imported from frozen_constants.py).
- No baked normality — the Student-t sigma the stages carry is preserved (grip-G ships mu=0 one-sided sigma+; verify the
  pipeline does NOT point-subtract G).
- Fallback HONESTY: a fall-back records the gap + stamps provenance; it does NOT silently substitute archived data as if
  fresh. A C/D/E/H gating FAIL is reported as machine-broken, NOT masked.

## Map Anchors (inbound)
- **Structural:** struct:physics.pilot (NEW pipeline.py + 2 scripts); consumes struct:physics.{segment_map.derivation,
  layer2 grip, utilization, fingerprint, instrument_panel}.
- **Capability:** capability:pilot-orchestration.
- **Constraints:** offline-only, reversibility-isolated-own-db, frozen-sets-consume-only, strictly-pre-no-leakage, pyright-0.
- **Decision anchors:**
  decision:pilot-fresh-vs-archived — FRESH default, archived is park-net only, provenance-stamped. `@grade: settled/measured`
  decision:two-segmap-paths — tripwire not unify. `@grade: settled/inherited`
  decision:pass-vs-limitation-boundary — a C/D/E/H gating FAIL = machine broken; only a data-coverage PARK is complete-with-gap. `@grade: settled/measured`
  (A contradiction you find on a settled/measured anchor: re-measure/flag as a candidate to the Commander, do not silently revise.)
- **Map confidence flags:** durable arch map stale-by-design for epic-659 stages (#671) — do NOT expect/require map edits.

## Evidence Produced (from IMPLEMENTER_RESULT — reproduce it)
- GB full-chain offline GREEN, provenance=fresh; C n_segments=41 == E=41; C median_drift_m=0.566<10; E within_anchor=True
  + positive control fired; all C/D/E/H PASS; slots_ran all 6. Recorded against g2-integrate.c1 (the tests-pass command).
- 29 pilot tests green (pinned 3.14). pyright 0/0/0. verifier exits 0.
- Implementer caught+fixed a provenance-inversion bug (fallthrough detector false-matched a benign "fastf1" mention →
  narrowed to the precise store-miss warning). VERIFY the fix: a fresh E run stamps provenance="fresh", not "fell-back".

## Suggested Model Tier
stronger — reason: silent-correctness stakes (fallback masking, vacuous-pass, provenance inversion, leakage), AFK-critical.

## Stop Conditions
BLOCK if: the diff cannot be accessed, the GB full-chain does not reproduce green offline, evidence is unverifiable, or a
policy decision is required.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow
feedback. Write it to `.agent-work/669-pilot/crew/g2-reviewer-result.md` AND deliver to cmdr-669 via SendMessage before
ending your turn. If APPROVE, state it plainly so the engine review-result match (verdict=APPROVE) is satisfied.
