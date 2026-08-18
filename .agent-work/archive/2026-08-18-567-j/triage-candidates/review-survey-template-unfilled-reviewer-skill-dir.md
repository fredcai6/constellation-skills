# Triage candidate: `REVIEW_SURVEY.template.json`'s `r6-fowler` check carries an unfilled placeholder

**Found at:** g2-review (reviewer crew), Workflow Feedback.

**What happened:** `REVIEW_SURVEY.template.json`'s `r6-fowler` postcondition
command carries a `<reviewer-skill-dir>` placeholder. The survey's own
instantiation convention only substitutes `<work-id>`, so `<reviewer-skill-dir>`
reaches the live checklist unfilled. The reviewer hit `REFUSED: command
postconditions unmet` on the first `record` attempt and had to
`amend --delta ... retext-check` the check text to the real path
(`scripts/verify_fowler_pass.py` lives at repo root, not under
`skills/reviewer/scripts/`) before it would pass.

**Why it matters:** every reviewer crew that self-bootstraps its own
`REVIEW_SURVEY.json` (the fallback path both this lane's g1 and g2 reviewers
used, per the separate `handoff-only-crew-inherits-parent-spine-env` triage
candidate) hits this same refusal and has to independently rediscover the
same `amend --delta retext-check` workaround.

**Recommendation (not mine to decide or file):** either substitute
`<reviewer-skill-dir>` the same way `<work-id>` is substituted at
instantiation time, or drop the placeholder and hardcode the repo-root-relative
path (`scripts/verify_fowler_pass.py`), since every consumer of this template
lives in the same repo layout.

**Disposition:** staged only, per `decision:no-issue-filing-mid-run`. Filed
nowhere; the human or Admiral routes this from here.
