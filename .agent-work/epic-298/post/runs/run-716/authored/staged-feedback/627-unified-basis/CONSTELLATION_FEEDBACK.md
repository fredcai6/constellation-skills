# CONSTELLATION_FEEDBACK — 627-unified-basis — 2026-07-18

Constellation-doctrine/template improvements surfaced this run (for the upstream skills sweep). Each carries the
originating lesson id for stable grouping.

## 1. Name `simplification_limits` as a standing crew final-verify postcondition
- **Lesson:** simplification-limits-standing-final-verify (originating: tc7, g4-review)
- **Finding:** The g4 implementer never ran `py -m src.utils.simplification_limits`; it was not named in the
  IMPLEMENTER_HANDOFF's Verification Commands nor in the implementer's own IMPLEMENTER_PLAN `m*-final-verify`
  postcondition (which only named the pytest command). estimate_store.py silently grew to 1010>1000 lines and only
  the reviewer's independent run caught it (a CREW_CONTEXT-named, mechanical, all-regions review blocker).
- **Recommendation:** for any gate touching `src/` or `tests/`, the implementer/reviewer templates (or the crew
  final-verify) should carry `simplification_limits` as a standing postcondition, not something each handoff must
  remember to name. This is a per-project rigor gate that belongs in the template, not the per-gate handoff.

## 2. Resume-time subagent cwd defaults to the session root, not the worktree
- **Lesson:** subagent-resume-cwd-leak (relates to project lesson subagent-shell-cwd-leak)
- **Finding:** On `SendMessage`-resume of a crew subagent, its transcript showed `cwd C:\Programs\f1Brainz` /
  `gitBranch main` (the session default), NOT its assigned worktree. The crews (instructed to assert `__file__`
  under the worktree) still produced correct worktree edits, but a resumed crew that trusts its cwd would edit the
  MAIN checkout under the editable-install `.pth`. 
- **Recommendation:** the resume/recovery guidance (crew-dispatch.md) should note that a resumed subagent's cwd is
  the session root, and the resume prompt must re-assert the worktree cwd + `__file__` check, same as the initial dispatch.

## 3. Full-suite integrate postcondition is a poor fit under multi-agent CPU contention
- **Lesson:** integrate-fullsuite-vs-fast-gate-under-contention
- **Finding:** the g4-integrate full-suite postcondition (`tests/unit/physics/layer2/ + weekend_state/`) exceeded
  20+ min under concurrent Ship agents. The pragmatic gate was the diff-affected subset + simplification_limits,
  with the full run deferred to the Admiral's merge gate — but this required a human/Admiral WAIVER rather than
  being a first-class plan option.
- **Recommendation:** consider a sanctioned "fast integrate gate = diff-affected tests + simplification; full suite
  = merge-gate" pattern for compute-heavy suites, so the Commander does not have to waive a mechanical postcondition
  under contention. (Recurrence-debt note: apply_lessons_delta reported 4 constellation lessons / 38 unfixed
  recurrences at run 26 — the upstream fix backlog is growing.)
