# Constellation Feedback Export — staged (624-phase0)

Lessons scoped `constellation` from this run, staged per the fencing posture (see `FENCE.md`) for the Admiral to harvest into the shared `.agent-work/CONSTELLATION_FEEDBACK.md` at closeout.

## from-child-refuses-on-gated-checklist

`checklist_engine.py advance <parent> --from-child <child.json>` only works when the child is a SURVEY-type checklist — it reads the child's top-level `consolidation` field, which is populated only by `consolidate`, and `consolidate` itself refuses on gated checklists ("consolidate is for survey checklists"). This matters because the Commander spine's OWN standard shape names `execute.json` — a GATED checklist — as the `execute` step's `child_checklist`, so any commander reaching that exact step and taking the imperative's "attach its consolidation as review-result first" language at face value will hit this refusal.

**Reproduction (this run, 624-phase0)**: `advance execute --from-child .../execute.json` → `REFUSED: child ... has no consolidation yet`. Attempted `consolidate` on `execute.json` directly → `REFUSED: consolidate is for survey checklists`. Recovered by skipping `--from-child` entirely and running plain `attest execute --cond c1 --which postconditions` (the postcondition's `check` is `null`) once `execute.json`'s own `current` reported `DONE: no open items`.

**Suggested fix**: either the `advance` subcommand help text / the spine template's `execute` step imperative should say explicitly "do not use `--from-child` for a gated child_checklist like execute.json — attest the check:null postcondition directly once the child reports DONE," or the engine's refusal message on a gated child should hint at the survey-only restriction rather than the generic "has no consolidation yet" (which reads as "you forgot a step," not "this flag doesn't apply here").

Full grounding: `.agent-work/staged-feedback/624-phase0/AGENT_FEEDBACK.md` (2026-07-18 entry) and `lessons-delta.json` op `from-child-refuses-on-gated-checklist` (both in this same staged directory).
