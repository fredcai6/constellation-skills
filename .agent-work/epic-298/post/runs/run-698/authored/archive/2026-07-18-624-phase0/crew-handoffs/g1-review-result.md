# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` (correlation screen) — independent review

## Result
`APPROVE`

## Handoff compliance
Matches the handoff exactly: `scripts/g1_correlation_screen.py` (new, committed-eligible) is a pure DB/pandas
partial-correlation screen between `data/physics_estimates.db` `session_estimates` (Q) axes and evo's own
quali_error (actual Q pace gap minus per-season trailing-mean recent-history baseline), per the frozen
`PRE_REGISTRATION.md` primary axis. Headline claimed (`pearson_r=-0.0923, n=2923`, primary axis
`lateral_total_grip_g`) independently reproduced exactly. All 7 explicit close-criteria verified pass (detail
below). Survey driven through the checklist engine at
`.agent-work/624-phase0/g1-review/review.json` (14 items: r0-context, r1-handoff, r2-scope, r3-evidence,
r4-quality, r5-reconciliation, r6-fowler, c1-c7; all recorded pass; consolidated APPROVE).

## Scope drift
None. `git status --short` shows exactly `scripts/g1_correlation_screen.py` (new) + `.agent-work/624-phase0/`
(local-only work area, not a diff concern per the handoff). `git diff --stat HEAD` is empty — no tracked file
modified. Grep for `sampled_predict|sampled_runtime|torch|module.?bundle|import src` returns zero matches.

## Evidence verdict
Test mode `evidence-only` satisfied. Independently re-ran both commands from `C:/Programs/f1-624`:
- `py scripts/g1_correlation_screen.py` → `HEADLINE: axis=lateral_total_grip_g pearson_r=-0.092306 n=2923`, exit 0.
- `py scripts/g1_correlation_screen.py --check` → `[--check] PASS: recomputed pearson_r=-0.092306 n=2923 matches recorded r=-0.092306 n=2923`, exit 0.

Both match the implementer's pasted stdout and the handoff's claimed headline verbatim.

## Code/doc quality
Meets project rules (`py` not `python`; DB-only via direct `sqlite3` reads, no FastF1/Jolpica; absolute
worktree-untracked-data paths; module-level constants only, no mutable state). Fowler code-smell pass run
separately (`.agent-work/624-phase0/g1-review/fowler_pass.json`, `verify_fowler_pass.py` exits 0): 12 baseline
smells rendered, 11 absent, 1 flagged (non-blocking) — `data-clumps` on the recurring
`(year, round_num, driver/constructor)` key-tuple convention threaded through several loader functions;
appropriate/idiomatic for a ~400-line one-off diagnostic script, noted only as a forward-looking observation.

## Map impact verdict
- **Evidence supports claimed change:** yes — headline number independently reproduced twice.
- **Constraints not violated:** yes — `DB-only analysis` constraint honored (no FastF1 calls, no sampler, no NN
  bundle load, confirmed by grep and by reading imports).
- **Notes match the diff:** yes — Map Impact notes in IMPLEMENTER_RESULT (new leaf script, no `src/`
  structural touch, references-not-imports `compute_pace_gaps`) match the actual diff.
- **Decision candidates surfaced:** none required — this run only executed decisions already frozen in
  `PRE_REGISTRATION.md`/`PROBLEM_STATEMENT.md`.
- **Durable context routed:** yes — the `team_canonicalization.py` misjoin-risk gap was flagged as a Cartographer/
  triage candidate in IMPLEMENTER_RESULT, and re-flagged here as `tc1` after independent confirmation.

## Reconciliation check
No architecture divergence requiring Commander reconciliation. New leaf diagnostic script, not wired into any
pipeline. One genuine map gap (team-name-space reconciliation between `session_estimates.constructor` and
`session_classifications.team` is not solved anywhere in `src/`) is correctly surfaced, not silently absorbed.

## Close-criteria verification (handoff items 1-7)

1. **Pre-registration discipline — PASS.** `PRIMARY_AXIS = "lateral_total_grip_g"` (script line 82), computed
   `df["lateral_mech_grip_g"] + df["lateral_aero_grip_g"]` (line 173) — exact match to `PRE_REGISTRATION.md`.
   File mtimes: `PRE_REGISTRATION.md` 2026-07-17 18:39:41, script 2026-07-17 18:55:39 (script strictly later,
   consistent with registration-before-code). Both files are untracked (never committed) so no git-log edit
   trail exists to check further; mtime evidence is consistent with the claim.
2. **No-look-ahead discipline — PASS.** `gaps.sort_values(["year","driver_id","round_num"])` then
   `groupby(["year","driver_id"])["actual_pace_gap"].transform(lambda s: s.shift(1).expanding().mean())`.
   `shift(1)` excludes the current round; `expanding().mean()` only covers strictly-earlier positions; groupby
   key includes `year` so no cross-season carryover. First-round-of-season rows get NaN baseline and are
   dropped (175 rows, matches printed/`G1_FINDINGS.md` count).
3. **Join-grain correctness — PASS.** Independent SQL against `data/physics_estimates.db`:
   `GROUP BY year, round_idx, constructor HAVING COUNT(*)>1` on `session_estimates WHERE session_type='Q'`
   returns **zero** duplicate keys; distinct-key count (1597) exactly equals row count (1597) — the join's
   right-hand side is provably unique, so `merge(..., how='inner')` structurally cannot duplicate rows, only
   drop unmatched left rows. Script's own printed counts (2985 in → 2985 out, 0 unresolved) confirm no drop
   occurred either.
4. **Team-name reconciliation vs `team_canonicalization.py` — PASS, claim CONFIRMED not just plausible.** Read
   `src/evo_predictor/team_canonicalization.py`: `_TEAM_ALIAS_MAP = {"alfa romeo": "Kick Sauber", "alphatauri":
   "RB"}` is flat and year-agnostic. Independently simulated it against live DB values: in 2021/2023,
   `session_classifications.team == "Alfa Romeo"` canonicalizes to `"Kick Sauber"`, but
   `session_estimates.constructor` for those years is `"Alfa Romeo Racing"`/`"Alfa Romeo"` — `"Kick Sauber"`
   does not appear in `session_estimates` until 2024. Reusing `canonicalize_team_name` for this join direction
   would silently drop/misjoin all pre-2024 Alfa Romeo rows — confirmed, not hypothetical. Separately
   spot-checked the script's own `match_constructor` against all 94 distinct team labels 2019-2026 (Alfa
   Romeo/Kick Sauber, AlphaTauri/RB/Racing Bulls, Racing Point/Aston Martin, Renault/Alpine, and every other
   team) — zero unresolved, matching the implementer's own verification.
5. **Reproduce the headline number — PASS.** Both `py scripts/g1_correlation_screen.py` and
   `py scripts/g1_correlation_screen.py --check` independently re-run; identical `pearson_r=-0.092306 n=2923`,
   both exit 0.
6. **Secondary-axis discipline — PASS.** `G1_FINDINGS.md`'s sole `HEADLINE:` line names only the primary axis;
   the 9 raw axes + `power_to_drag` composite appear only under a section headed
   "secondary/exploratory, never headline"; script stdout literally headers that block
   `=== SECONDARY / EXPLORATORY (never headline) ===`. No secondary number is ever presented unlabeled,
   including the two secondary axes whose CIs also exclude zero (`brake_decel_ms2`, `traction_aero_accel_per_m`)
   — both explicitly called out as secondary in the honest-read section.
7. **Scope discipline — PASS.** Grep for `sampled_predict|sampled_runtime|torch|module.?bundle|import src`
   returns zero matches; only imports are `argparse, math, re, sqlite3, sys, pathlib, numpy, pandas`.
   `git status`/`git diff --stat HEAD` confirm no `src/` file modified.

## Blockers
- none

## Out-of-scope observations
- (`tc1`) `src/evo_predictor/team_canonicalization.py::canonicalize_team_name` is year-agnostic and would
  misjoin pre-2024 Alfa Romeo rows if reused for the `session_estimates`↔`session_classifications` join
  direction (confirmed live). Worth a Cartographer note or follow-up issue so the next implementer doesn't
  rediscover this from scratch.
- (`tc2`) The team-level→driver-level physics broadcast (both teammates share identical constructor-level
  axis values) dilutes any true per-driver signal — already documented by the implementer as a Phase-0
  simplification, not an error, but flagged again here as a natural strengthening point if the physics
  estimator is ever extended to per-driver granularity.

## Workflow Feedback

- **Handoff gaps:** none blocking. The handoff did not state a survey-state-location path explicitly (the
  skill's own doctrine supplied `.agent-work/<work-id>/<gate>-review/review.json`); worth adding to future
  reviewer handoffs so the path isn't inferred each time.
- **Context rediscovered:** none beyond what IMPLEMENTER_RESULT already documented — the handoff and
  implementer evidence were unusually complete (exact line-number-free but unambiguous script excerpts,
  full stdout pasted, assumptions section covering the reconciliation choice).
- **Instructions improvised around:** none — the 7 close-criteria in the handoff mapped cleanly onto 7
  appended survey leaves (c1-c7), which kept each independently auditable rather than folding them into the
  generic r1-handoff item.
- **What would have made this easier:** nothing material; this was a well-formed, self-contained handoff with
  precise, falsifiable close-criteria — the kind that makes independent reproduction fast.

## Return status
`complete`
