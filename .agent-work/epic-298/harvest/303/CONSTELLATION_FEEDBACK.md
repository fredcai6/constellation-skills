# Constellation Feedback Export (staged — see FENCE.md)

## 2026-07-31 — constellation-skills — 303

- **Lesson:** `lesson:prove-command-fails-postcondition`
- **Candidate:** document-negation-wrapper-in-plan-template
- **Observed:** `templates/IMPLEMENTER_PLAN.template.json` documents the TDD red/green postcondition split inline (a `check: null` red step + a `command`-check green step), but has no inline guidance for the sibling case a must-fail command postcondition — a gate whose whole point is proving a command correctly fails (exit non-zero), which does not fit `command`'s default "exit 0 = pass" semantics. The `! <command>` bash-negation-wrapper pattern that solves this lives only in a banked lesson, not in the template a plan author actually copies from.
- **Cost:** none this run (the pattern was already known from the launch order's inherited-context section), but a plan author without that launch-order context would have no signal from the template itself that this pattern exists, and would likely fall back to a `check: null` self-report for a must-fail check — exactly the weaker shape `decision:refusal-is-mechanically-checked` warns against.
- **Proposal:** add one inline comment/example to `templates/IMPLEMENTER_PLAN.template.json` (alongside the existing red/green TDD guidance) showing the `! <command>` negation-wrapper shape for a postcondition that must prove a command *fails*, citing `lesson:prove-command-fails-postcondition`.
- **Grounding:** `C:/Programs/constellation-skills-wt/298-303/.agent-work/issue-303/execute.json` gate `m2-fixtures` (three `command` postconditions using the `! py scripts/verify_spec_confirmed.py <fixture> --phase confirm` shape, all three satisfied on first `advance`, no rework); `C:/Programs/constellation-skills-wt/298-303/.agent-work/issue-303/notes-303.md` "m2" section.
- **Template vintage:** `templates/IMPLEMENTER_PLAN.template.json`, worktree HEAD at base commit `b69e6c8` — no TEMPLATES_MANIFEST baseline sha available in this worktree to cite.
- **Confidence:** medium (second data point on the underlying lesson; the template-doc proposal itself is a single-run observation, not yet independently corroborated by another run hitting the same gap).
