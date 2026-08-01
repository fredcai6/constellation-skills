# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g2` — Docent extraction

## Survey State Location
`.agent-work/issue-103/g2-review/review.json` (under the issue workbench, not worktree root).

## What Was Implemented
Extracted the self-contained-HTML constraint block from `skills/docent/SKILL.md` into new `skills/docent/references/self-contained-html.md`; body keeps the method + a one-hop pointer. See handoff `.agent-work/issue-103/crew-handoffs/g2-implement-handoff.md` and result `.agent-work/issue-103/crew-handoffs/g2-implement-result.md`.

## How to Inspect the Diff
Review target = UNCOMMITTED working tree in `C:\Programs\constellation-wt-103`. `git status --porcelain` then `git --no-pager diff skills/docent/` and read the new `skills/docent/references/self-contained-html.md`.

## Task Statement
Relocate the self-containment hard constraints to a reference without losing any constraint; keep the freshness/stamp method in the body.

## Close Criteria (each a review check)
- New file `skills/docent/references/self-contained-html.md` exists and contains ALL of: no-external-resource-loads rule (inline CSS/JS, no CDN/fonts/remote images/fetch/XHR/WebSocket, file:// under CSP), the restrained/readable/dark-light-aware rule, the shared-CSS-block rule, AND the self-containment grep verification recipe. Confirm nothing from the original constraint block was dropped (compare against `git show HEAD:skills/docent/SKILL.md`).
- SKILL.md body has a one-hop pointer to `references/self-contained-html.md` (grep it) and no longer inlines the full block.
- The freshness method stays in the body: `docent_freshness.py stamp` and `check` commands, the STALE banner doctrine, and "stale is worse than none" preamble all still present in SKILL.md.
- New filename does NOT match `global-*.md`.
- Only `skills/docent/**` changed.
- Suite green: `py -m pytest tests/test_install_constellation.py tests/test_docent_freshness.py -q`.

## Allowed Scope
`skills/docent/**` only.

## Specific Exclusions
`skills/commander/**`, `_shared/**`, `tests/**`, `scripts/docent_freshness.py` must be untouched.

## Constraints the Implementation Must Respect
- No constraint lost (relocation only).
- No new `global-*.md` filename; one-hop pointer.
- Freshness protection not weakened.

## Evidence Produced
IMPLEMENTER_RESULT: SKILL.md 1110→1005; new ref 214 words; pointer grep=2; suite `47 passed`. Reproduce each; also diff the extracted text against `git show HEAD:skills/docent/SKILL.md` to confirm no constraint dropped. Attach your verdict to `g2-review.c1`.

## Suggested Model Tier
`simple bounded — mechanical extraction check`

## Stop Conditions
BLOCK if: a constraint was dropped (not just relocated), the pointer is missing, the freshness method was weakened, an out-of-scope file changed, or the suite reds.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-103/crew-handoffs/g2-review-result.md` AND final message before idling): verdict APPROVE or BLOCK on its own line, per-check findings with reproduced evidence, blockers, out-of-scope observations, workflow feedback.
