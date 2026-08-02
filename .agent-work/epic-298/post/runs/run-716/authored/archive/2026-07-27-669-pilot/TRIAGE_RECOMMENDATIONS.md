# Triage recommendations — #669 pilot

Disposition for all: **recommend-and-defer** — issue-filing authority is the Admiral's (LAUNCH_ORDER-669 floats
user-decisions to the Admiral; the epic-659 established pattern is the Admiral routes commander triage at merge).
No fix-now applied: none clears all four fix-now rungs cleanly (see per-item). Route these at #669 merge.

## tc1 — run_pilot_669.py default --report-path writes into tracked docs/physics/
- **What:** on a bare `run_pilot_669.py` run (no `--out-dir`/`--report-path`), the report defaults into tracked
  `docs/physics/`. Intended for the g3 committed deliverable, but an ad-hoc exploratory run dirties tracked docs.
- **Recommendation:** default the report under `--out-dir` (untracked); g3/season runs pass an explicit
  `--report-path docs/physics/...`. Acceptance: a bare run writes no tracked file.
- **Why not fix-now:** the docs/physics/ default is the INTENDED g3 behavior; changing it re-touches a just-reviewed
  deliverable + needs a re-run to regenerate the report at an explicit path — disproportionate for a cosmetic default.
- **Out of scope:** the g3 committed report itself (correct as-is).

## tc2 — critic-#3 non-empty-gating negatives under a fixture-level skipif (latent vacuity)
- **What:** the pure-decider negative tests (non-empty/finite gating FAILs on degenerate input) sit under
  `test_downstream.py`'s fixture-level `skipif`; they executed here (0 skipped, fixtures present) but would
  silently SKIP on a machine lacking the fallback DB / probe fixture — a latent vacuity.
- **Recommendation:** move the pure-decider negatives to inline synthetic inputs (no external fixture) so they never
  skip. Acceptance: the non-empty-gating negatives run unconditionally.
- **Why not fix-now:** touches the reviewed test harness after APPROVE; low-risk but out of the tracer-bullet's bite.

## tc3 — split_half_boundary_drift (C gating) has no store/db path (latent coupling)
- **What:** the C-gating `split_half_boundary_drift` relies on the default `data/telemetry_store.db` resolving; it
  resolved offline here (real telemetry, GB median 0.566m), but a worktree without a resolvable default store would
  fail C gating with a confusing error.
- **Recommendation:** give it an explicit store arg (touches the landed #662 stage → its own issue).
- **Why not fix-now:** modifying a landed stage is out of #669 scope (wiring-only; #671/#662 territory).

## Already routed to existing issues (in docs/physics/pilot_669_report.md, NOT new candidates)
- Belgium grip-G held-out data-coverage PARK (FP2/FP3 missing) → #692 (populate grip store) + #670 (FP coverage).
- GB grip-G evolution-corrected ~2.37e5 blow-up (n_cells=2) = known #663 non-identifiability → #678 (sharpen).
- Monaco wide join σ (scale ~1.2e4) → #700 (correlation-aware σ) at season scale.
- PANEL instruments 2/3/4 (cross-circuit) → #668/#670 full-panel over the corpus.
