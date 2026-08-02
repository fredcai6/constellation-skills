# Reviewer Handoff

## Gate
`g1` (correlation screen)

## What was implemented
`C:/Programs/f1-624/scripts/g1_correlation_screen.py` (new, committed-eligible) — a pure DB/pandas partial-correlation screen between physics capability axes (`data/physics_estimates.db` `session_estimates`, `session_type='Q'`) and evo's own quali error (driver's actual Q pace gap minus their own trailing-mean recent-history baseline, computed within-season, no look-ahead). Findings at `.agent-work/624-phase0/G1_FINDINGS.md` (local-only). Full IMPLEMENTER_RESULT at `.agent-work/624-phase0/crew-handoffs/g1-implement-result.md` — read it first.

Headline result claimed: primary pre-registered axis `lateral_total_grip_g` (= `lateral_mech_grip_g + lateral_aero_grip_g`), Pearson r = -0.0923, 95% CI [-0.1281, -0.0562], n=2923; Spearman rho = +0.0135, CI includes zero (sign-mismatched with Pearson — flagged by the implementer as a finding, not hidden).

## How to inspect the diff
`cd C:/Programs/f1-624 && git status --short` (expect exactly `?? scripts/g1_correlation_screen.py` as the mission-branch-relevant new file; `.agent-work/624-phase0/` is the local work area, not a diff concern). Read the full script.

## Task Statement
Independently verify this gate's statistical/methodological correctness — this was the launch order's MANDATORY-rigor probe (Pre-Ruling #1), so self-review by the implementer alone is not sufficient.

## Close Criteria — verify each explicitly
1. **Pre-registration discipline**: `C:/Programs/f1-624/.agent-work/624-phase0/PRE_REGISTRATION.md` states the primary axis is `lateral_mech_grip_g + lateral_aero_grip_g`, registered 2026-07-18T01:39:24Z. Confirm the script's primary axis matches EXACTLY (read the script's source, don't trust a docstring) and was not edited after the fact — check file mtimes / `git log` if available; at minimum confirm no `PRE_REGISTRATION.md` edit exists that postdates the script.
2. **No-look-ahead discipline**: the `recent_history_baseline` for a given `(year, round, driver)` must only use that SAME driver's STRICTLY EARLIER rounds in the SAME season (never later rounds, never other drivers, never cross-season carryover per the implementer's stated design choice). Read the actual pandas/SQL code and confirm this — a common bug class is an off-by-one that includes the current round or a groupby that leaks future rows.
3. **Join-grain correctness**: `session_estimates` is per-constructor; the script broadcasts each constructor's axis value onto both of that constructor's drivers for the weekend. Confirm this broadcast is actually what the code does (not e.g. an accidental many-to-many join that duplicates or silently drops rows). Cross-check the printed row counts (1597 raw Q rows -> 2985 driver-round quali_error rows -> 2985 after join) make arithmetic sense for a roughly-2-drivers-per-constructor broadcast (some rows drop for missing/unresolved constructor names).
4. **The team/constructor name-reconciliation the implementer built ad-hoc** (not reusing `src/evo_predictor/team_canonicalization.py`, which the implementer found would MISJOIN pre-2024 Alfa Romeo rows if reused for this direction) — independently verify this claim: read `src/evo_predictor/team_canonicalization.py::canonicalize_team_name` yourself and confirm whether it really would misjoin here, and spot-check the script's own reconciliation logic against a few known rebrand cases (Alfa Romeo -> Kick Sauber, AlphaTauri -> RB -> Racing Bulls, Racing Point -> Aston Martin, Renault -> Alpine) for at least 2019-2026 boundary years.
5. **Reproduce the headline number yourself**: re-run `py scripts/g1_correlation_screen.py` from `C:/Programs/f1-624` and confirm you get the SAME `pearson_r=-0.0923`, `n=2923` printed. Also run `py scripts/g1_correlation_screen.py --check` and confirm exit code 0.
6. **Secondary-axis discipline**: confirm the findings doc and script output never present a secondary/exploratory axis as if it were the headline result (re-read `G1_FINDINGS.md`).
7. **Scope discipline**: confirm no `src/` file was modified, no sampler/NN code was invoked (grep the script for `sampled_predict`, `sampled_runtime`, `torch`, module bundle loads — none should appear).

## Allowed Scope
Read-only review of `scripts/g1_correlation_screen.py`, `.agent-work/624-phase0/G1_FINDINGS.md`, `.agent-work/624-phase0/PRE_REGISTRATION.md`, `.agent-work/624-phase0/PROBLEM_STATEMENT.md`, `src/evo_predictor/team_canonicalization.py`, and re-running the two verification commands. Do not modify the implementer's script; if you find a real bug, BLOCK with a precise description rather than fixing it yourself.

## Constraints
`py` not `python`. cwd must be `C:/Programs/f1-624` for any run.

## Map Anchors (inbound)
Same as g1-implement's anchors (see `execute.json` g1-implement.anchors): `src/evo_predictor/quali_recent_history_adapter.py:57-163`, `src/evo_predictor/models/_features.py:38-39`, `PRE_REGISTRATION.md`, `decision:regime_readiness_rubric`.

## Evidence from IMPLEMENTER_RESULT
See `.agent-work/624-phase0/crew-handoffs/g1-implement-result.md` in full — it contains the complete stdout of both verification commands and the implementer's own stated assumptions (including the ad-hoc team-name reconciliation and the per-season baseline reset).

## Return Format
Return REVIEW_RESULT with an explicit **verdict: APPROVE** or **verdict: BLOCK**, one line per close-criterion item above (pass/fail + evidence), and any out-of-scope observations as triage candidates. Send it to me (ShipB-624) via SendMessage AND write it to `C:/Programs/f1-624/.agent-work/624-phase0/crew-handoffs/g1-review-result.md` before ending your turn.
