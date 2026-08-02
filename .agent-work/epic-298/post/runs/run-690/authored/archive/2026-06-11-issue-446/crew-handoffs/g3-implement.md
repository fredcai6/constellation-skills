# Implementer Handoff

## Gate
g3 — Multi-session strawman run + verdict

## Task
Exercise the g2 harness end-to-end over **≥3 cached sessions** and write the verdict that answers
the Phase 0a question: **does the harness discriminate, or is it an honest null?**

1. **Exploration driver** in `scripts/` (e.g. `scripts/run_trajectory_grading_strawman.py`) that
   runs the g2 `runner.run_grading(...)` over ≥3 sessions spanning 2022-2025 with **≥1 race and
   ≥1 quali**, writing one machine-readable JSON report per session to
   `.agent-work/issue-446/evidence/` (filenames containing "grading", e.g.
   `2023_belgium_Q_grading.json`). Document the exact session picks and WHY in the script header.
   Suggested picks (verify each is cached before relying on it): 2023 Belgium Q (already proven),
   2023 Belgium R, and one more from a different year (e.g. 2024 Bahrain Q or 2022 Spain R). Use a
   handful of drivers per session (e.g. top ~5) — enough laps for the anchor co-estimation, not the
   whole field, to keep runtime sane.

2. **Verdict** at `.agent-work/issue-446/VERDICT.md`: read the emitted reports and report, PER
   SESSION, the KEY NUMBERS:
   - strawman sector-anchor residuals (summary stat, e.g. RMS/median) + pass/fail at 50 ms;
   - covariance-consistency reduced chi-square + pass/fail;
   - cross-residual diagnostic: fitted inter-stream offsets per lap/session (range + stability);
   and then the DISCRIMINATION CONCLUSION: does the harness separate the strawman's known
   pathologies (sawtooth accel from differentiated interpolated position, time-base error,
   dishonest covariance), OR is it an HONEST NULL — i.e. at 50 ms with unknown (co-estimated)
   anchors the strawman cannot be distinguished from a good trajectory? **An honest null is a
   complete, successful deliverable — report it with the same rigor as a win.** Interpret WHY:
   if the strawman passes the sector-anchor gate, it likely means the gate (with free anchors) is
   too permissive at 50 ms and the discriminating power lives in gates (b)/(c) — say so, since
   that directly feeds Phase 0b's gate-tolerance design.

## Protected Intent
Honest reporting over a flattering story. Numbers must be traceable to the emitted reports. Do not
overclaim discrimination the numbers don't support; do not bury a null.

## Test Mode
Inspection-only for the driver (it is an exploration script, not shipping src/); the harness it calls
is already unit+integration tested. No new src/ shipping code in this gate.

## Close Criteria
- ≥3 machine-readable JSON reports under `.agent-work/issue-446/evidence/` (≥1 race, ≥1 quali,
  2022-2025), each schema-valid per the g1 report schema.
- `VERDICT.md` exists with per-session key numbers (anchor residuals + 50ms verdict, reduced
  chi-square, fitted inter-stream offsets) and a clearly-stated discrimination-or-honest-null
  conclusion with interpretation.
- The run was OFFLINE (no re-pull) and made no canonical-DB writes.

## Allowed Scope
`scripts/` (new exploration driver), `.agent-work/issue-446/evidence/` (generated reports — NOT
committed as bulky data), `.agent-work/issue-446/VERDICT.md`.

## Specific Exclusions
- No new shipping `src/` code beyond the `scripts/` driver. No changes to the g1/g2 harness modules
  (if you find a harness BUG that blocks the run, STOP and report it as a blocker — do not fix it
  here; it routes back through g1/g2).
- No re-pull; no get_telemetry outside the existing strawman; no canonical-DB writes; no evo imports.
- Do NOT commit the bulky JSON reports as durable data (they live under .agent-work evidence).

## Constraints
- ≥3 sessions, 2022-2025, ≥1 race + ≥1 quali, documented.
- Foreground compute — run the harness foreground; NEVER background a long run. If a single session
  looks like >30 min, checkpoint partial reports to disk and continue.
- Offline cache only; raw streams only (strawman excepted); truth from DB read-only.
- `py`, never `python`. Set utf-8 in the env of any captured subprocess.

## Map Anchors (inbound)
- **Structural:** `scripts/` (exploration driver, not a structural map node);
  `struct:preprocessing.trajectory_grading` exercised end-to-end.
- **Capability:** trajectory grading — discrimination evidence on real sessions.
- **Constraints/assumptions:** honest-null clause; evidence stays out of git unless curated.
- **Decision anchors:** grading-field-first — this run is the proof it discriminates (or the
  documented null that feeds 0b).
- **Evidence expectations:** harness discriminates OR documented honest null at 50ms — the
  ≥3-session report numbers.

## Required Evidence
- The ≥3 JSON reports on disk (list their paths in the result).
- `VERDICT.md` with the per-session numbers and conclusion.
- A note confirming offline (no re-pull) and no DB writes.

## Verification Commands
```bash
py scripts/run_trajectory_grading_strawman.py   # (or whatever you name it; runs the >=3 sessions)
py -c "import glob; print(glob.glob('.agent-work/issue-446/evidence/*grading*.json'))"
```

## Suggested Model Tier
stronger — reason: interpreting gate numbers into an honest discrimination/null verdict is the
analytical heart of Phase 0a; the interpretation must be sound and feed 0b correctly.

## Authority
Session selection (within 2022-2025, ≥1 race + ≥1 quali), driver subset, and report filenames are
yours. You may NOT: modify the harness, re-pull, write canonical DBs, or soften an honest null into
a false win. If the harness has a bug blocking the run, STOP and raise it as a blocker.

## Stop Conditions
Stop and return (blocker) if: fewer than 3 suitable sessions load offline (report what DID); the
harness errors in a way that needs a g1/g2 code change; a single session blows past a reasonable
runtime even after checkpointing; a decision outside authority is needed.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/issue-446/crew-handoffs/g3-implement-RESULT.md`: sessions
run + why, paths to the JSON reports, the per-session key numbers (copy them into the result too),
the discrimination/honest-null verdict, confirmation of offline+no-DB-writes, assumptions, any
blocker hit, workflow feedback.
