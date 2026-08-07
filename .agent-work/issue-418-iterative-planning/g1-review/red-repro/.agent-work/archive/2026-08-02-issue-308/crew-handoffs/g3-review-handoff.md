# Reviewer Handoff

## Gate
`g3-review` (issue #308, epic-298) — independent review of the cap removal landed at `HEAD` on branch `epic-298/308`.

## Worktree
`C:/Programs/constellation-skills-wt/e298-308`. **Never touch the main checkout `C:/Programs/constellation-skills`.** Interpreter is `python` — **`py` has no pytest and reports a silently green suite.**

## The change under review
The single commit `feat(#308): drop the 20-entry hard cap from the lessons writer (g3)` — inspect with `git show HEAD --stat` and `git show HEAD -- scripts/apply_lessons_delta.py tests/test_apply_lessons_delta.py skills/workbench/templates/LESSONS.template.md`. Ignore the `.agent-work/issue-308*` files in that commit; they are workflow artifacts, not the change.

The implementer's own account is at `.agent-work/issue-308/crew-handoffs/g3-implement-result.md`. **Read it as a claim, not as evidence.**

## What this gate was required to do
Remove the 20-entry hard cap from `scripts/apply_lessons_delta.py` outright — **no replacement numeric cap, soft threshold, or configurable limit** — while the writer keeps working in every other respect (add / retire / confirm / export / render). The Curator's regular cleanup pass is the stated replacement retention story.

## Hunt these two specifically
The Commander named these before dispatch, so they are the load-bearing part of your review:

1. **A cap renamed rather than removed.** Anything that still refuses, warns, or throttles on active-entry count, under any name — including a value read from the header, an env var, a default argument, or a threshold expressed in a different unit. `! grep -nE 'DEFAULT_CAP|active cap' scripts/apply_lessons_delta.py` is the gate's own check; it is a *necessary* condition, not a sufficient one, and you should assume it is easy to satisfy while leaving a cap in place. Find the sufficient condition yourself.

2. **A test now passing vacuously because its refusal path was deleted rather than inverted.** `tests/test_apply_lessons_delta.py::test_cap_enforced_and_retire_before_add` existed to prove the cap refused. It has been replaced. Determine by construction whether the replacement can actually fail — not whether it passes.

## Additional risk the Commander is specifically unsure about
The `playbook-state` header grammar changed: `cap=(\d+)` became a **tolerated-and-discarded non-capturing group** `(?:\s+cap=\d+)?`, and the group indices after it were renumbered (`state.group(2..6)` became `group(2..5)`). Two things to satisfy yourself about, by running code rather than reading it:

- **Legacy tolerance is real**: a header still carrying `cap=20` parses, and the field is dropped on the next render. Every lessons file in the repo has one.
- **The renumbering is correct**: `dormancy-runs`, `apply-recurrences`, `apply-confirmed` and `ticked-work-ids` still bind to the right values, including when the optional groups are ABSENT. An off-by-one here would silently swap two integers and the suite might not notice.

## Independent reproduction required
Reproduce the behaviour change **in your own hands**, and use a technique that does not mutate the file under review:
- `python .agent-work/issue-308/checks/cap_is_gone.py` (green now).
- To see it red, do **not** `git checkout` the writer — that reverts the real edit. Load the pre-change writer from `git show 752a62f:scripts/apply_lessons_delta.py` into a scratch path and drive that copy instead, or use `importlib` to load by path.
- `python -m pytest -q` — full suite, and report the counts you observed, not the ones you were told.

## Out of scope — do not report as defects
- `.agent-work/LESSONS.md` still holds 20 active lessons and its preamble still describes a cap. **The migration is gate g4 and it is deliberately not done yet.** The implementer was explicitly forbidden from touching lesson content.
- `skills/lessons-auditor/SKILL.md` and `docs/EPISODE_STORE.md` still reference the cap. Both were excluded from g3 and are filed as triage candidates.
- The lessons READ path (launch orders, spine templates instructing agents to read the Active section) is gate g5.

## Deliverable
Write `REVIEW_RESULT` to `.agent-work/issue-308/crew-handoffs/g3-review-result.md`, with an explicit verdict of **ACCEPT** or **REWORK**. For each finding give severity, the exact command that demonstrates it, and its output. State plainly which of the two hunted classes you found and which you searched for and did not find — **a null you actually looked for is a result; silence is not.** Include a workflow-feedback section.

Do not commit; do not edit production code. If you find something that needs fixing, report it.
