# Reconcile — issue #106

Skill-source repo with no `docs/architecture/` packet map, so structural reconcile is direct (commander-core "no packet map" path).

- **In-fence structural record — DONE:** the eval harness is a new self-contained repo-tool family whose structural record is its own `evals/README.md` (authored + committed at g4): it documents the runner interface, the situational bar, the exit-code contract, the N-of-M meaning, the stated limitations, and the named next scenario. That IS the harness's map.
- **Out-of-fence map impact — SURFACED to Admiral (no-op here):** `docs/CONSTELLATION_OVERVIEW.md` lists `scripts/checklist_engine.py` as the substrate but has no eval-harness entry. A one-line mention of the autonomous eval harness (`scripts/run_skill_eval.py` + `evals/` + the situational bar) would fit the overview, but that file is outside this run's fence ("Yours: evals/**, scripts/run_skill_eval.py, tests/test_run_skill_eval.py, README under evals/; Fences: everything else"). Recommended to the Admiral/curator as a small follow-up, not edited here.
- No existing schema/design doc in-fence was touched by this change beyond the new files' own docstrings and README.
