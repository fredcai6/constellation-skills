# Constellation Feedback — staged exports (671-reconcile)

No NEW constellation-platform export this run.

This was a doc/map-only reconcile with no crew gates, so the two chronically-exported
constellation lessons (`lesson:engine-artifact-attest`, `lesson:run-crew-cli-launcher-misfit`)
were not freshly exercised in a way that adds signal:
- `engine-artifact-attest` — confirmed again (attach-not-attest for all four user-decision
  checkpoints), but this is recurrence-debt on an already-exported lesson, not new signal;
  a bare confirm rides the existing export. No re-export.
- `run-crew-cli-launcher-misfit` — N/A: no `run_crew.py` crew dispatch this run (reasoning-gate
  run; research/critic/cartographer-verify used the Agent tool directly, which is the correct
  shape for non-crew aids, not the crew-launcher path this lesson describes).

Carried observation (NOT a new export, logged for the Admiral's harvest): the
`self-authored-reasoning-gate-checks-need-review-scrutiny` lesson got a strong second
data point this run (a cold critic caught a false-green grep invariant + a staged-diff-blind
deletion guard in the commander's own reasoning-gate checks). If it recurs once more it may be
ripe to graduate from "re-observe" into a standing commander-core rule (pre-flight your own
reasoning-gate invariants: presence-greps key on zero-today tokens; deletion guards use
`git status --porcelain`, not `git diff`). Left in the playbook to re-observe, per its bank_reason.
