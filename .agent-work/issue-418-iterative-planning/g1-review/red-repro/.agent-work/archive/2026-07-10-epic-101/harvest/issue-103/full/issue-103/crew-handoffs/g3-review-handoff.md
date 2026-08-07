# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g3` — Interrogator register rewrite (single skill, in place)

## Survey State Location
`.agent-work/issue-103/g3-review/review.json`.

## What Was Implemented
`skills/interrogator/SKILL.md` body rewritten in place so the delegated/agent invocation leads and the interactive-human case is a brief mode note; frontmatter unchanged; stays one skill. See handoff `.agent-work/issue-103/crew-handoffs/g3-implement-handoff.md` (TARGET DRAFT + doctrine checklist) and result `.agent-work/issue-103/crew-handoffs/g3-implement-result.md`.

## How to Inspect the Diff
Review target = UNCOMMITTED working tree in `C:\Programs\constellation-wt-103`. `git status --porcelain` then `git --no-pager diff skills/interrogator/SKILL.md`. Compare against `git show HEAD:skills/interrogator/SKILL.md` for doctrine coverage.

## Task Statement
Register rewrite in place: agent/delegated prose first, human-direct as a mode note; ALL doctrine preserved; one skill, no split, no bloat.

## Close Criteria (each a review check)
- **All doctrine preserved** — diff the new body against `git show HEAD:skills/interrogator/SKILL.md` and confirm NONE of these rules were dropped: relentless one-question-at-a-time; recommended answer per question; list-is-a-prompt-not-a-script; behavior-framing (capability→examples→events→constraints) → `capability`/`event`/`constraint`/`assumption` ontology → Cartographer handoff; compliance pointer to `references/global-everyone.md`; survey drive from `templates/INTERROGATION.template.json` through `scripts/checklist_engine.py` with ask/append/skip/consolidate; answer-from-code-instead-of-asking; delegated reading (counterpart = launch order/delegate, skip settled, context query, float, never block on absent human); interactive reading (wait for the answer); the four "While interrogating" bullets; template + checklist-engine footer.
- **Register actually shifted**: the opening no longer leads with a human-direct "Interview the user" imperative; the delegated/agent case is presented as the common mode and the human-at-keyboard case as a mode note.
- **Single skill**: exactly one `# Constellation Interrogator` H1; no new file; not split.
- **Word count** within ~395–483 (reported 439→439).
- **global-everyone.md pointer** present.
- Only `skills/interrogator/SKILL.md` changed.
- Suite green: `py -m pytest tests/test_install_constellation.py -q`.

## Allowed Scope
`skills/interrogator/SKILL.md` only.

## Specific Exclusions
`skills/commander/**`, `_shared/**`, `tests/**` untouched; no new files.

## Constraints the Implementation Must Respect
One skill, no split, no bloat; frontmatter unchanged; global-everyone.md pointer kept.

## Evidence Produced
IMPLEMENTER_RESULT: 439→439 words; H1 count 1; pointer present; forbidden grep 0; suite `38 passed`. Reproduce each. Attach verdict to `g3-review.c1`.

## Suggested Model Tier
`stronger — verify doctrine-preservation across a register rewrite`

## Stop Conditions
BLOCK if: a doctrine rule was dropped, the register did not actually shift, it was split, word count is far outside band, an out-of-scope file changed, or the suite reds.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-103/crew-handoffs/g3-review-result.md` AND final message before idling): verdict APPROVE or BLOCK on its own line, per-check findings with reproduced evidence, blockers, out-of-scope observations, workflow feedback.
