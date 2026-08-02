# Implementer Handoff

## Gate
`g1` (correlation screen)

## Task
Build a committed, reproducible pure-DB/pandas Python script that computes a partial-correlation screen between physics capability axes and evo's own quali error, per the pre-registered method below. NO neural-network inference, NO sampler invocation — this is a DB read + pandas computation only.

## Protected Intent
This is a Phase-0 INFORMATIONAL probe (not a go/no-go gate). The pre-registered primary axis and the recent-history-baseline construction must not be altered after seeing any correlation number — report whatever the number is, honestly, including a null.

## Test Mode
Inspection-only (this is an analysis script producing a findings artifact, not production behavior) — no existing test surface covers this new script; verification is via re-running the script and reproducing its own printed numbers, plus reviewer spot-checks against raw DB rows.

## Close Criteria
- Script exists at `C:/Programs/f1-624/scripts/g1_correlation_screen.py`, runs standalone with `py scripts/g1_correlation_screen.py` from cwd `C:/Programs/f1-624`, and also supports a `--check` flag that re-runs the analysis and exits 0 if the printed headline result matches the value recorded in the findings doc (exits 1 otherwise) — this is what `execute.json`'s `g1-integrate` postcondition `c1` runs.
- Reads `data/physics_estimates.db` table `session_estimates` via **absolute path** `C:/Programs/f1Brainz/data/physics_estimates.db` (untracked in this worktree — see Map Confidence Flags), filtered `session_type='Q'`.
- Reads the season DBs (`C:/Programs/f1Brainz/data/f1_data_<year>.db`, absolute paths, one per year 2019-2026) for: (a) actual quali classification/pace-gap per driver-event, (b) enough prior-Q history per driver to compute a trailing mean pace gap. Use whatever existing DB read method(s) `src/data/database.py`'s `DatabaseManager` exposes for quali classification (verify the exact method signature from source — do not guess it) and, if useful, the raw construction logic in `src/evo_predictor/quali_recent_history_adapter.py:57-163` / `src/evo_predictor/models/_features.py:38-39` as a REFERENCE for what "prior Q pace gaps" means (you do not need to import evo_predictor code directly if a simpler direct SQL/pandas recomputation of the same quantity is cleaner — your call, document which you did).
- Per `(year, round, driver)`, compute:
  - `actual_pace_gap` = driver's Q lap-time gap to that weekend's field median (seconds; lower/more-negative = faster). If a ready column/method already gives this, use it; otherwise derive from best Q lap times.
  - `recent_history_baseline` = trailing mean of THAT DRIVER's own prior-Q `actual_pace_gap` values (own history only, calendar order, no look-ahead — this is critical: only rounds strictly BEFORE the current one for that driver may contribute).
  - `quali_error` = `actual_pace_gap - recent_history_baseline`. Rows where the driver has no prior history (first appearance) get `quali_error = NaN` and are dropped.
- Join physics: `session_estimates` is per-`(year, gp_name, session_type='Q', constructor)` — broadcast each constructor's axis values onto BOTH of that constructor's drivers for that weekend (document this broadcast explicitly in the findings doc; it's a known Phase-0 simplification, not an error).
- Compute the **PRE-REGISTERED primary axis**: `lateral_total_grip_g = lateral_mech_grip_g + lateral_aero_grip_g` (verbatim from `.agent-work/624-phase0/PRE_REGISTRATION.md` — read that file first, do not re-derive the axis choice). Report `corr(lateral_total_grip_g, quali_error)` (Pearson AND Spearman, report both) with `n` and a 95% CI (Fisher z-transform is fine for Pearson), as the **headline result**.
- Compute the other 9 raw axes + the secondary `power_to_drag = max_power_w / drag_area_closed_m2` composite (also named in `PRE_REGISTRATION.md`) the same way, clearly labeled "secondary/exploratory" in all output — never presented as if they were the primary result.
- Write findings to `C:/Programs/f1-624/.agent-work/624-phase0/G1_FINDINGS.md`: method recap, primary result with n/coefficient/CI, full table of all 11 axes + the secondary composite, an honest read of what this does and does NOT show (it is NOT the ~0.80 ceiling answer — that's G1 in Phase 7; it IS informational about where signal lives per critic disposition F7).

## Allowed Scope
- New file: `C:/Programs/f1-624/scripts/g1_correlation_screen.py`.
- New file: `C:/Programs/f1-624/.agent-work/624-phase0/G1_FINDINGS.md`.
- Read-only access to `C:/Programs/f1Brainz/data/*.db` (main checkout, absolute paths — these DBs are untracked/absent from this worktree per `lesson:worktree-untracked-data`).
- May read (not modify) any `src/` file for reference (e.g. `src/data/database.py`, `src/evo_predictor/quali_recent_history_adapter.py`) to verify exact method signatures before using them.

## Specific Exclusions
- Do NOT modify any file under `src/`.
- Do NOT invoke the sampler (`sampled-predict`, `sampled-backtest`) or load any NN module bundle — pure DB/pandas only.
- Do NOT alter the pre-registered axis in `PRE_REGISTRATION.md` for any reason, even if the correlation looks weak or noisy on the registered axis — report the number honestly instead.

## Constraints
- `py` not `python` (this machine's launcher).
- Absolute paths into `C:/Programs/f1Brainz/data/` for all DB reads (this worktree has no untracked data files).
- `PYTHONIOENCODING=utf-8` if the script prints any non-ASCII.
- Cite every DB method/column signature from source before using it (`lesson:handoff-cite-exact-seam-signature` — I have NOT verified the exact `DatabaseManager` quali-classification method signature for you; verify it yourself from `src/data/database.py` before calling it).

## Map Anchors (inbound)
- **Structural:** `src/evo_predictor/quali_recent_history_adapter.py:57-163` — recent-history feature builder (reference only); `src/evo_predictor/models/_features.py:38-39` — `quali_pace_gap_history_full` field semantics (raw seconds from field median, calendar order).
- **Capability:** `session_estimates` 11-axis Q store, `data/physics_estimates.db`.
- **Constraints/assumptions:** DB-only analysis (`docs/agents/ORCHESTRATOR_CONTEXT.md`); Pre-Ruling #1 (mandatory partial correlation, pre-registered axis, no fishing).
- **Decision anchors:** `decision:regime_readiness_rubric` — prior finding that the regime-capability vector is circuit-conditional/fine-margin (`frac_team` ~0-4%); a weak/null result here is CONSISTENT with this prior, not a surprise — say so if it happens, don't over-interpret a null as a bug.
- **Evidence expectations:** `.agent-work/624-phase0/PRE_REGISTRATION.md` — the frozen axis and its rationale, timestamped 2026-07-18T01:39:24Z, BEFORE this gate. Read it first; do not deviate from it.
- **Map confidence flags:** the `data/*.db` files are untracked/absent from this worktree (`C:/Programs/f1-624`) — you MUST use absolute paths into `C:/Programs/f1Brainz/data/`, verified to exist before the script assumes them.

## Deliverable Path Check
- **Committed** — `C:/Programs/f1-624/scripts/g1_correlation_screen.py`; run `git check-ignore scripts/g1_correlation_screen.py` from `C:/Programs/f1-624` before dispatch confirms exit 1 (not ignored) — `scripts/` is not gitignored per repo convention (verified: other committed diagnostic scripts already live there, e.g. `scripts/diagnose_quali_evidence.py`).
- **Local-only** — `C:/Programs/f1-624/.agent-work/624-phase0/G1_FINDINGS.md`; this is inside the commander's own work-area, never committed on the mission branch per `lesson:shared-files-not-on-mission-branch` (only the script itself is a mission-branch deliverable).

## Required Evidence
- Full stdout of running `py scripts/g1_correlation_screen.py` from `C:/Programs/f1-624`, showing the primary result (n, Pearson r, Spearman rho, 95% CI) and the secondary-axes table.
- The exact row counts at each join stage (raw `session_estimates` Q rows; rows after driver-broadcast; rows after dropping no-history rows) — so the reviewer can sanity-check nothing silently vanished.
- `git status`/`git diff --stat` showing exactly the two new files.

## Verification Commands
```bash
cd C:/Programs/f1-624 && py scripts/g1_correlation_screen.py
cd C:/Programs/f1-624 && py scripts/g1_correlation_screen.py --check
```

## Suggested Model Tier
Stronger — reason: real statistical-methodology risk (partial correlation, join-grain correctness, no-look-ahead discipline for the recent-history baseline) that a weaker model is more likely to get subtly wrong.

## Authority
The pre-registered axis, the DB-only/no-sampler constraint, and the `quali_error` construction are ALL ALREADY DECIDED (see `PRE_REGISTRATION.md` and `.agent-work/624-phase0/PROBLEM_STATEMENT.md` "Gap resolution" section) — do not re-litigate them. You decide implementation details only (exact SQL, exact DB helper methods used, exact CI method).

## Stop Conditions
Stop and return if: the DB lacks a usable per-driver Q pace-gap/classification source entirely (would mean the whole probe needs re-scoping — float this, don't invent a substitute silently); a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (paste the full stdout), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
