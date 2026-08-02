# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1` (correlation screen)

## Completed slice
Built a committed, reproducible pure-DB/pandas correlation screen between physics capability axes
(`data/physics_estimates.db` `session_estimates`, `session_type='Q'`) and evo's own quali error
(driver's actual Q pace gap minus their per-season trailing-mean recent-history baseline), per the
pre-registered method in `PRE_REGISTRATION.md`. Ran it for real (no fabricated numbers) and wrote
findings.

## Scope
**Files changed:**
- `C:/Programs/f1-624/scripts/g1_correlation_screen.py` (new, committed-eligible — `git check-ignore`
  confirmed exit 1, not ignored)
- `C:/Programs/f1-624/.agent-work/624-phase0/G1_FINDINGS.md` (new, local-only per
  `lesson:shared-files-not-on-mission-branch`)

**Specific exclusions touched:** no — nothing under `src/` was modified; no sampler/NN invocation;
primary axis was not altered after seeing any correlation number.

## Behavior changed
No (analysis script only, no production code touched).

## Map Impact
- **Structural anchors touched:** none in `src/` — new leaf script only, references (does not import)
  `src/evo_predictor/quali_pace_gap_history.py`'s `compute_pace_gaps` formula and
  `src/data/database/_metadata_session.py`'s `get_quali_best_valid_laps_batch` SQL shape (reimplemented
  directly, not imported — see Assumptions).
- **Capabilities added/changed/affected:** new standalone diagnostic capability —
  `scripts/g1_correlation_screen.py [--check]` — reproducible physics-axis-vs-quali-error correlation
  screen; not wired into any pipeline.
- **Constraints/assumptions touched:** confirmed `constraint: DB-only analysis` honored (no FastF1
  calls, no sampler, no NN bundle load). Relied on `assumption:` that `session_estimates.constructor`
  and `session_classifications.team` name spaces can be reconciled per-year with normalize +
  exact/containment matching plus one explicit 2025-rebrand alias — verified with zero unresolved/
  ambiguous names across all 8 years (2019-2026) live before the script was finalized.
- **Decision candidates / resolved decisions:** none — this run only executed decisions already frozen
  in `PRE_REGISTRATION.md` / `PROBLEM_STATEMENT.md`.
- **Claims/evidence produced:** `HEADLINE: axis=lateral_total_grip_g pearson_r=-0.092306 n=2923` —
  backed by the full stdout below and reproducible via `--check`.
- **Trust limitations / drift found:** `session_estimates.constructor` vs `session_classifications.team`
  naming is NOT already reconciled anywhere in `src/` for this join direction (the existing
  `src/evo_predictor/team_canonicalization.py::canonicalize_team_name` only handles 2 aliases and is
  actually WRONG if applied here — it maps "alfa romeo" -> "Kick Sauber" unconditionally, which would
  misjoin 2021-2023 rows where `session_estimates` uses the constructor name "Alfa Romeo"/"Alfa Romeo
  Racing" directly, not "Kick Sauber"). This is a genuine map gap worth a Cartographer note if anyone
  else needs this join.
- **Triage candidates:** the Spearman-vs-Pearson sign mismatch on the primary axis (Pearson negative &
  CI-excludes-zero, Spearman near-zero) is flagged in `G1_FINDINGS.md` as a natural follow-up for Phase
  7's fuller G1 treatment — not investigated further here (out of this probe's scope).

## Test mode
**Required:** `evidence-only` (inspection-only per handoff — no existing test surface covers this new
script)
**Satisfied:** yes — verified by re-running the script and reproducing its own printed numbers via
`--check` (exit 0), plus the join-stage row counts are printed for reviewer spot-check against raw DB
rows.

## Evidence

```bash
$ cd C:/Programs/f1-624 && py scripts/g1_correlation_screen.py
[stage1] raw session_estimates Q rows: 1597
[stage2] driver-round quali_error rows before physics join (post history-drop): 2985
         (dropped for no prior-season history: 175)
         (team->constructor unresolved, excluded from join attempt: 0)
[stage3] rows after physics join (final analysis n pool): 2985

=== PRIMARY (pre-registered) ===
lateral_total_grip_g         n=2923  pearson_r=-0.0923 [-0.1281, -0.0562]  spearman_rho=+0.0135 [-0.0228, +0.0497]

=== SECONDARY / EXPLORATORY (never headline) ===
drag_area_closed_m2          n=2767  pearson_r=+0.0069 [-0.0304, +0.0441]  spearman_rho=-0.0001 [-0.0374, +0.0372]
brake_decel_ms2              n=2923  pearson_r=-0.0646 [-0.1006, -0.0284]  spearman_rho=-0.0102 [-0.0464, +0.0261]
brake_aero_decel_per_m       n=2923  pearson_r=-0.0026 [-0.0388, +0.0337]  spearman_rho=+0.0037 [-0.0325, +0.0400]
traction_accel_ms2           n=2923  pearson_r=-0.0017 [-0.0380, +0.0345]  spearman_rho=-0.0144 [-0.0506, +0.0219]
traction_aero_accel_per_m    n=2923  pearson_r=-0.0582 [-0.0942, -0.0220]  spearman_rho=-0.0140 [-0.0503, +0.0222]
max_power_w                  n=2767  pearson_r=-0.0204 [-0.0576, +0.0169]  spearman_rho=-0.0193 [-0.0565, +0.0180]
power_drag_area_m2           n=2767  pearson_r=+0.0069 [-0.0304, +0.0441]  spearman_rho=-0.0001 [-0.0374, +0.0372]
coast_rolling_decel_ms2      n=2920  pearson_r=-0.0340 [-0.0702, +0.0023]  spearman_rho=-0.0335 [-0.0697, +0.0028]
coast_drag_area_m2           n=2920  pearson_r=+0.0060 [-0.0303, +0.0423]  spearman_rho=-0.0007 [-0.0370, +0.0356]
power_to_drag                n=2767  pearson_r=-0.0253 [-0.0625, +0.0119]  spearman_rho=+0.0018 [-0.0355, +0.0390]

HEADLINE: axis=lateral_total_grip_g pearson_r=-0.092306 n=2923
```

```bash
$ cd C:/Programs/f1-624 && py scripts/g1_correlation_screen.py --check
... (identical body as above) ...
[--check] PASS: recomputed pearson_r=-0.092306 n=2923 matches recorded r=-0.092306 n=2923
$ echo $?
0
```

```bash
$ cd C:/Programs/f1-624 && git check-ignore scripts/g1_correlation_screen.py; echo "exit=$?"
exit=1
$ git status --short
?? .agent-work/624-phase0/
?? scripts/g1_correlation_screen.py
$ git diff --stat
(empty — nothing staged; both new files are untracked)
```

**Result:** pass — script runs standalone with exit 0, `--check` exits 0 and reproduces the recorded
headline, `git check-ignore` confirms `scripts/g1_correlation_screen.py` is not gitignored (exit 1),
and `git status` shows exactly the two new paths (`scripts/g1_correlation_screen.py` is the single new
file under `scripts/`; `.agent-work/624-phase0/` is an untracked local work directory that already
existed before this run and now also contains `G1_FINDINGS.md` plus this run's own plan/journal files —
all local-only, none intended for the mission branch).

## TDD evidence, if required
N/A — test mode is evidence-only (inspection), not TDD; no red/green cycle applies to a standalone
analysis script with no existing test surface.

## Docs/contracts touched
- none (no `docs/` files modified)

## Assumptions
- Reimplemented `compute_pace_gaps` and the `get_quali_best_valid_laps_batch` SQL shape directly in
  the script (raw SQL, no `import src.*`), per the handoff's explicit allowance ("you do not need to
  import evo_predictor code directly if a simpler direct SQL/pandas recomputation... is cleaner").
  Chosen specifically to sidestep the worktree editable-install `.pth` trap (project memory
  `editable-install-pth-worktree-trap`: a bespoke script's `import src.*` run from this worktree can
  silently resolve to the MAIN checkout's `src/`, not this worktree's) and to keep the script fully
  self-contained per the "pure DB/pandas" constraint. Verified `compute_pace_gaps`'s exact formula
  ((t-median)/median) from source before reimplementing it (not guessed).
- `recent_history_baseline` resets each season (does not carry over year-to-year), matching
  `build_quali_pace_gap_history`'s per-season prior-rounds construction, since `PROBLEM_STATEMENT.md`
  names that function's construction as "the literal existing recent-history feature" this probe should
  reproduce.
- Built a from-scratch team-name<->constructor-name reconciliation (normalize + exact + containment +
  one explicit rebrand alias) rather than reusing `src/evo_predictor/team_canonicalization.py`, because
  that helper's alias map is year-agnostic and would misjoin pre-2024 "Alfa Romeo" rows (see Map Impact
  / Trust limitations above). Verified zero unresolved/ambiguous names across all 8 years live before
  finalizing.
- `--check`'s tolerance is `rel_tol=abs_tol=1e-6` on `pearson_r` plus an exact `n` match — tight enough
  to catch a real regression, loose enough to tolerate floating-point noise across repeated runs (the
  underlying computation is fully deterministic given a fixed DB state, so exact reproduction is
  expected and observed).

## Stop conditions hit
- none — the DB had a usable per-driver Q pace-gap source (`lap_times`/`sessions`), so the primary stop
  condition ("DB lacks a usable per-driver Q pace-gap/classification source entirely") did not apply.

## Out-of-scope observations
- `power_drag_area_m2` and `drag_area_closed_m2` produce numerically identical correlation figures in
  the secondary-axis table for every row where both are populated (same underlying drag-fit pairing in
  `session_estimates` for those sessions) — observed and reported as-is in `G1_FINDINGS.md`, not
  investigated further (would be scope creep for this probe; flagged for whoever next touches the
  physics estimator's drag-fit column semantics).
- The Spearman result on the primary axis is near-zero and sign-mismatched with the Pearson result
  (Pearson negative & CI excludes zero; Spearman positive & CI includes zero) — flagged in
  `G1_FINDINGS.md`'s honest-read section as a natural follow-up for Phase 7's fuller G1 treatment.

## Workflow Feedback

- **Handoff gaps:** none blocking. One soft gap: the handoff's line 18 says "Use whatever existing DB
  read method(s) `src/data/database.py`'s `DatabaseManager` exposes" but `src/data/database.py` no
  longer exists as a single file — it is now the package `src/data/database/` (multiple `_*.py`
  mixins assembled in `manager.py`). Not a real blocker (found the right file, `_metadata_session.py`,
  in one grep), but a handoff citing a stale path costs a round-trip a future implementer might not
  make cleanly.
- **Context rediscovered:** the `session_estimates.constructor` vs `session_classifications.team`
  name-space mismatch was NOT flagged anywhere in the handoff, `PRE_REGISTRATION.md`, or
  `PROBLEM_STATEMENT.md`, despite `PROBLEM_STATEMENT.md` explicitly stating "Store is per-`(year,
  gp_name, session_type, constructor)`, not per-driver" (i.e. the broadcast-onto-drivers requirement
  was flagged, but the underlying name-reconciliation problem that broadcast requires was not). Had to
  discover it live by diffing distinct constructor/team values per year across both DB families, then
  verify a matching scheme resolves every year with zero ambiguity before trusting the join. This was
  the single largest chunk of implementation-adjacent research in this run.
- **Instructions improvised around:** none — the handoff's explicit escape hatch ("you do not need to
  import evo_predictor code directly if a simpler direct SQL/pandas recomputation... is cleaner — your
  call, document which you did") covered the choice made; documented per that instruction.
- **What would have made this easier:** naming the constructor/team name-mismatch explicitly in the
  handoff's Map Anchors (even just "these two tables use different spellings for the same team; you
  will need a reconciliation step") would have saved the discovery pass. Otherwise the handoff was
  complete and accurate (DB paths, absolute-path requirement, and the pre-registered axis were all
  exactly as stated).

## Return status
`complete`
