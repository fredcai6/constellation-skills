# Admiral binding refinements (fold into G3/G4/G5 + archive) — received during G2 compute

## Reversibility (ARCHIVE-critical)
Even READS of tracked `data/f1_data_2023.db` WAL-churn it. Before committing ANYTHING at archive:
`git status`, then `git checkout -- data/f1_data_*.db` on ANY tracked DB showing Modified (WAL churn from
coverage reads INCLUDED). Final diff = report (+minimal code) ONLY — zero DB blobs. Whole run must stay git-revertible.

## Decision 1 — held-out composition (G4): ENDORSED with requirements
Composition = shared track-geometry applied IDENTICALLY across all 3 arms; driver fingerprint cells stay
strictly-pre (as_of_round=R-1). Ruling #3 targets DRIVER-SPECIFIC leakage, which stays excluded. Requirements:
- (a) keep the composition caveat PROMINENT in the diagnostic report.
- (b) report a strictly-prior sensitivity readout wherever a prior-circuit/prior-year composition exists (robustness check).
- (c) **CONFIRM the composition is the FIELD-REFERENCE (median-across-cars) per-class share — NEVER a driver's own
  R-laps informing their own prediction.** (The join reads `composition` from the reference_laps FIELD row —
  verify this is field/median-across-cars, not driver-specific, in G4 implement + review.)
Admiral carries this caveat into the FOR-OWNER block. Admiral-adjudicated (interpretation of settled ruling) — proceed.

## Decision 2 — split scheme at 22 circuits (G3): ENDORSED as scaling READ-ADAPTER with refinement
PROVIDED the frozen replication rules (double-centering, REPLICATION_* thresholds, the r-computation) are
byte-UNCHANGED; only HOW you partition scales. REFINEMENT (important):
- do NOT use a single 11v11 split (loses the variance-reduction of the landed exhaustive-2v2-AVERAGED scheme;
  noisily mis-sizes replication).
- AVERAGE over MULTIPLE deterministic balanced splits (a fixed, seed-free deterministic subsample of balanced
  partitions) — faithfully generalize the landed averaging.
- Report the EXACT scheme (how many splits, how constructed) in the report.
- G3-review still adjudicates the new-method line; if the reviewer judges it crosses into new method, FLOAT to
  the Admiral BEFORE committing it.

## Per-round parks / no-frame-kill (G5 report + FOR-OWNER):
- Surface parked rounds EXPLICITLY: rounds 1-2 (Bahrain/Saudi) = no strictly-prior data for E's car ceiling; plus
  any others that park. State plainly the panel/fingerprint analysis is on the ~20 COVERED rounds (3-22). Frame as
  a COMPLETE deliverable with a stated gap (no-frame-kill), not a shortfall.
- The held-out diagnostic on EARLY covered rounds (3-5) will have thin/unresolved fingerprints (little prior data)
  — report as honest thin-cell behavior, do NOT force it.

## Closeout harvest:
- Capture a lessons-delta: the season-runner needed per-round fault isolation; real-data early-round property
  (strictly-pre E car ceiling → no-prior rounds park) that the synthetic unit tests didn't exercise.
- Also capture: git-bash `tasklist`/`ps` liveness check is UNRELIABLE (false-negatived a live PID); use PowerShell
  Get-Process CPU for detached-process liveness (reinforces the crew-idle-strands-deliverable lesson).
