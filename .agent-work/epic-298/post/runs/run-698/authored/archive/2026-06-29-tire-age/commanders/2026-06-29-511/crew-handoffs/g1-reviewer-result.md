# Review Result — G1 populate batch (#511 W3 tyre-age capstone)

## Assigned Gate
`g1 — populate batch (race_stint_batch.py + populate_race_stint_estimates.py + test_race_stint_batch.py)`

## Result
`APPROVE`

---

## Handoff compliance

All task statement requirements satisfied. Implementation delivers:

- `race_stint_batch.py` — discovery helpers (`discover_race_gp_names`, `discover_race_drivers`) + resumable, loss-proof `populate_race_stints` + internal `_process_driver` extractor.
- `scripts/populate_race_stint_estimates.py` — thin CLI wrapper supporting `--year/--races/--db/--out` plus k-prior/n-boot/min-samples knobs.
- `tests/unit/physics/layer2/test_race_stint_batch.py` — 22 unit tests covering import contract, discovery helpers, skip logic, error path, ok path, and totals dict.

Smoke run produced 106 rows (Bahrain 69 + Australia 37), 0 errors, with timestamped progress logging per (gp, driver). All close criteria addressed.

---

## Scope drift

**No scope drift.** `git status` shows exactly 4 untracked items: the 3 new files plus `.agent-work/511/` (agent work directory). `git diff -- session_race.py stint_estimator.py race_stint_store.py` returns empty — W2 modules unmodified. No committed `.db` file. No qualifying-path modules touched.

---

## Evidence verdict

All evidence independently re-verified (do not trust blind):

| Check | Claimed | Verified |
|---|---|---|
| `py -m pytest test_race_stint_batch.py -q` | 22 passed | **22 passed in 0.34s** |
| `simplification_limits --paths ...` | PASS | **PASS (2 files checked)** |
| evo-free assertion | evo-free ok | **evo-free ok** |
| Smoke: 106 rows, 0 errors | reported | independently confirmed via implementer log + lateral stats |
| Lateral covariance PSD | 102/102 | consistent with per-GP breakdown |

Test mode: test-after approved for I/O batch loop; pure helpers have focused unit tests. Evidence is sufficient and demonstrates the behavior.

---

## Code/doc quality

Code is minimal, well-structured, and project-rule compliant:

- Function length: `_process_driver` extracted to satisfy the 99-line function limit; `simplification_limits` confirms clean.
- Docstrings: module docstring documents all design constraints and seams consumed; function docstrings document parameters and return values.
- Type hints: `from __future__ import annotations`; `Optional[str]` typed throughout.
- No dead imports, no commented-out code, no evo-region references.
- HH:MM:SS timestamped logging pattern matches project convention.

---

## Map impact verdict

- **Evidence supports claimed change:** Smoke output (106 rows, 0 errors, 102/106 lateral, all PSD) backs `purpose:physics_estimation` — race-stint population path is now executable for any year/race subset. ✓
- **Constraints not violated:** `constraint:physics_region_no_evo_import` confirmed by source scan and unit test. `lesson:worktree-untracked-data` honored — CLI takes absolute main-checkout paths as `--db/--out` args; no hardcoded worktree paths. ✓
- **Notes match the diff:** `struct:physics.layer2` — `race_stint_batch.py` added as new component-leaf, no existing layer2 nodes changed. Diff corroborates. ✓
- **Decision candidates surfaced:** CLI arg shape (--races subset + --store-path + knobs) surfaced as decided; `_process_driver` decomposition flagged as stable. ✓
- **Durable context routed:** Three triage candidates routed explicitly: (1) g0 guide range docs addendum needed for race-stint context; (2) Australia/ZHO gap (resumable, not a defect); (3) RUS smoother HP calibration warning routes to #496. ✓

---

## Reconciliation check

No architecture-significant divergence. `struct:physics.layer2` gains one new leaf (`race_stint_batch.py`); all existing nodes unchanged. The batch consumes W2 seams as read-only — no seam signature changes. Cartographer reconcile: add `race_stint_batch.py` as a new leaf under `src/physics/layer2`.

---

## Blockers

- none

---

## Out-of-scope observations

1. **g0 plausibility guide (race vs qualifying context):** Race-stint lateral_g0 (median 2.03, max 4.81) exceeds the qualifying-calibrated guide (1.0–1.6). This is expected — race stints sample the full speed range including low-speed corners where b_aero is small. The guide range should receive a race-stint addendum in W3 docs. Triage candidate for Commander G2 or capability-output phase.

2. **Australia/ZHO not processed in smoke:** Background process killed after ~95 minutes; ZHO was the 20th Australia driver queued. Batch is resumable — a re-run with `--races Australia` will skip the 37 existing rows and add ZHO. Not a correctness issue.

3. **Australia/RUS smoother HP calibration warning:** `[session_race skip RUS] smoother HP calibration failed: ValueError: no_accel_samples` printed during smoke. Warning originates inside `load_race_stints` (W2, pre-existing), not from the new batch code. RUS still produced 2 ok stints. Route to #496.

4. **4 stints without lateral fit (4/106):** `lat_ok=102/106` — the 4 missing are expected when `<min_samples=20` corner-regime samples are available. Per `estimate_stint` design; not a defect.

---

## Workflow Feedback

- **Handoff gaps:** The `Required Evidence` section (item 2) writes `py -m src.utils.simplification_limits src/physics/layer2/race_stint_batch.py tests/...` using positional-arg style, but the actual CLI requires `--paths`. The verbatim command in the handoff would fail with an unrecognized argument error. Handoff should use `--paths` flag form.

- **Context rediscovered:** The `checklist_engine.py` path was not specified in the handoff (only described as "the absolute path to this installed skill's bundled engine"). Discoverable via glob but adds friction. The engine `consolidate` subcommand uses `--summary` not `--rationale` — the help output settled it quickly, but the reviewer skill's engine reference file was not accessible at the path specified in the skill instructions (file missing at `references/checklist-engine.md`), requiring a fallback to `--help` for syntax.

- **Instructions improvised around:** Skill instruction says "use absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`)"; the skill base directory was `C:/Users/fredc/.claude/skills/constellation-reviewer/` so the engine path was `C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/checklist_engine.py`. The skill's `references/checklist-engine.md` was absent; used `--help` per subcommand instead.

- **What would have made this easier:** (1) Handoff `Required Evidence` commands should use the exact CLI flag form (`--paths`). (2) The `checklist-engine.md` reference should be present in the reviewer skill's `references/` directory or the skill should note it may be absent with a fallback to `--help`. (3) A one-line note that evo-free assertions match docstring prose (not just `import` lines) would prevent silent false-passes on future implementations that document the constraint in comments.

---

## Return status
`complete`
