# Cold plan critic — findings disposition

Critic dispatched (general-purpose subagent, cold read of MISSION_FRAME.md + execute.json + PLAN_ALTERNATIVES.md
+ LAUNCH_ORDER-663.md + INTERROGATION_RECORD.json only). All 9 findings triaged and applied to the frozen plan
before approval -- none rejected.

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| F1 | BLOCKING | g4's held-out truth channel needs LOO/leakage discipline + rank-deficiency check (launch order names this exactly) | APPLIED -- g4-implement now requires the leakage check + full-rank truth-OLS (driver/race FE not stint FE for fuel), g4-review now verifies it explicitly |
| F2 | MAJOR | Rain-flag wide-sigma re-estimation (frozen Mission requirement) missing from g2 | APPLIED -- g2-implement/review now require a real, tested fit-time effect for rain_flag, distinct named constant from the thin-session fallback |
| F3 | MAJOR | g4/g5-implement offered a scripts/ escape hatch while integrate hardcoded a pytest path | APPLIED -- committed both to the pytest path explicitly, escape hatch removed |
| F4 | MAJOR | Honest-Null Clause stated in prose but not operationalized in the postcondition check shape | APPLIED -- g4/g5-implement now explicitly instruct: pytest must exit 0 whenever the harness runs+reports (pass or null), never assert the metric/rate clears a threshold |
| F5 | MAJOR | g1/g3/g4/g5-implement never pinned the exact test file path -review/-integrate assume | APPLIED -- every -implement imperative now names its exact test file path |
| F6 | MINOR | MISSION_FRAME misattributed the session_type parameterization site to race_degradation_slopes instead of _read_clean_race_laps | APPLIED -- MISSION_FRAME.md Structural Anchors corrected |
| F7 | MINOR | No check for post-hoc loosening of the two 'guess'-graded criteria (split scheme, 0.8 threshold) | APPLIED -- g4-review/g5-review now explicitly check for recorded reasoning if either was changed |
| F8 | MINOR | PK-shape decision pressure absent from g6's explicit triage-candidate list | APPLIED -- added as candidate 4 in g6-verdict |
| F9 | MINOR | verify_worktree_isolation.py evidence not referenced anywhere in execute.json | APPLIED -- e0-context now references it (it was run as the launch order's literal first step, before spine init, outside this checklist) |
