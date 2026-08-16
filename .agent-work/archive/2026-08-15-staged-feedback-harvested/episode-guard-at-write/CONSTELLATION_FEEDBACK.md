# Workflow feedback export — episode-guard-at-write

Staged for the Admiral to harvest: `scripts/checklist_engine.py`'s archive-gate `c4` git-change-policy
deny-globs `.agent-work/CONSTELLATION_FEEDBACK.md` unconditionally, so this run cannot commit a direct
edit to the durable root without a human waiver. Per the delegated-commander skill's fenced
feedback/archive closeout clause, the export is staged here instead of waived through.

## 2026-08-15 — episode-guard-at-write — G2 REPLAN_INPUT ceremony has no lightweight path for a one-issue delegated commander run

**Episode:** episode-guard-at-write-004

**Target:** the commander spine's `execute` step c2 (`verify_iterative_role_artifacts.py commander`, backed by `skills/replan/scripts/verify_replan.py::verify_replan_input`).

**Defect (scope, not correctness):** the check is not wrong — it validated correctly and caught a real
mistake on the first pass (an extra `issue` key left in a `wave_evidence` entry). The gap is that its
G2 schema assumes an epic-level wave plan (`epic`, `definition_of_done`, `good_enough`,
`hard_constraints`, `fixed_decisions`, a typed `current_wave` with `blocks` edges, `wave_forecast`,
`uncertainty_register`, `parked_possibilities`) even when the actual principal is a single frozen
Admiral launch order for one bounded issue, with none of that structure existing anywhere else in the
run. Closing execute's c2 required synthesizing plausible epic-shaped fields from scratch rather than
citing anything real, because nothing else in a one-issue delegated run produces them.

**Grounding:** this run (`episode-guard-at-write`, attempt 2, delegated single-issue launch order under
`admiral-post-568`) had no wave, no forecast, no uncertainty register, and no parked possibilities to
report — the entire "plan" was LAUNCH_ORDER-2.md's few paragraphs. Every G2 field still had to be
filled with something, so the authored packet is a plausible-sounding artifact standing in for
structure that was never decided by anyone.

**Suggested fix:** give `verify_iterative_role_artifacts.py commander` (or the spine step's directive)
a reduced-schema mode for a single-issue delegated run — one that asks for `completed_outcomes`,
`wave_evidence`, and `discrepancies` against the launch order directly, without requiring an epic/wave
skeleton invented solely to satisfy the validator's field-set check.
