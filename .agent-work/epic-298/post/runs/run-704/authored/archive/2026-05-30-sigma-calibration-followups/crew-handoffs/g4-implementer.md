# Crew Handoff — G4 implementer

## Role: implementer | Gate: G4 (#304 p2-3 + #306)

## Task
Bounded research → written verdicts. Save:
- `.agent-work/sigma-calibration-followups/evidence/g4-nu-sweep.md` + `.json`
- `.agent-work/sigma-calibration-followups/evidence/g4-racestart.md` + `.json`

### A) Nu sensitivity (#304)
Smoke/single-module sweep nu ∈ {2,3,4,6,8} on:
1. `driver_race_start_power_from_race_weekend` (tight residuals)
2. `driver_quali_power_from_race_weekend` (higher variance)

Readouts: |r/sigma| percentile shape, per-pair sigma std, corr(sigma_pi, log_loss) if feasible on smoke scale, pairwise log-loss delta vs nu=4 baseline.

**Verdict:** keep shared nu=4 OR recommend ONE bounded default for G5 (e.g. student_t_nu_sigma=X). If deep per-(phase,scope) tuning needed → note as triage follow-up, don't chase.

### B) Race-start corr flip (#306)
For `driver_race_start_power_from_race_weekend`:
- Per-pair sigma + |r| distribution (promoted bundle vs fresh smoke with lambda=1)
- Event-level outlier audit: LOO + Spearman vs Pearson on corr(sigma_pi, log_loss)
- Single-module lambda_sigma_nll sweep {0, 0.5, 1, 2}

**Verdict:** artifact | needs lambda tuning | needs per-pair unc consumer

### G5 recommendation
End each verdict with explicit **recommended G5 settings** (defaults to keep if no change).

## Constraints
- Smoke/single-module only — NO full gold cycle in G4
- py for python; DB canonical
- Do NOT commit source unless fixing a blocker bug found during research
- Machine-checkable numbers in JSON

## Close criteria
Both evidence files with verdict + recommendation. Scripts in `.agent-work/sigma-calibration-followups/` OK.

Return IMPLEMENTER_RESULT with verdict summaries and recommended G5 settings.
