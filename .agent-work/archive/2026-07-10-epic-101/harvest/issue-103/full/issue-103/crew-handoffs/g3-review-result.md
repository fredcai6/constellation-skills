# REVIEW_RESULT

VERDICT: APPROVE

Gate `g3` — Interrogator register rewrite (single skill, in place). Reviewed the UNCOMMITTED working tree in `C:\Programs\constellation-wt-103`. Every claim reproduced independently.

## Per-check findings (reproduced evidence)

### All doctrine preserved — PASS
Diffed new body against `git show HEAD:skills/interrogator/SKILL.md`. Every listed rule survives (register moved; no rule dropped):
- **relentless one-question-at-a-time** — "through relentless, one-question-at-a-time interrogation" + bullet "Ask one question at a time." Present.
- **recommended answer per question** — "for each question give a recommended answer." Present.
- **list-is-a-prompt-not-a-script** — "If you're given a list of questions, treat it as a prompt, not a script: decide your own initial question set, and don't let an over-prescribed seed shortcut your framing." Present.
- **behavior-framing (capability→examples→events→constraints) → capability/event/constraint/assumption ontology → Cartographer handoff** — paragraph 2 unchanged from HEAD (identical text). Present.
- **compliance pointer to references/global-everyone.md** — line 12 verbatim. Present.
- **survey drive from templates/INTERROGATION.template.json through scripts/checklist_engine.py with ask/append/skip/consolidate** — paragraph 4 retains all four verbs. Present. (Note: "wait for the answer" in this sentence was reworded to "resolve its answer"; the literal "wait for the answer" doctrine was relocated to the Interactive mode, where it now correctly lives — not dropped.)
- **answer-from-code-instead-of-asking** — "If a question can be answered from the code, explore the code instead of asking." Present (plus "Cross-check claims against the code" bullet).
- **delegated reading** — "Delegated (the common case — no reachable human): your counterpart is the frozen launch order / dispatching delegate. Answer each question from it, skip questions it already settles, and when it neither answers nor lets you safely proceed, take it to the delegate — a missing fact as a context query, a choice outside inherited latitude as a float — rather than blocking on an absent human." All five elements (counterpart=launch order/delegate, skip settled, context query, float, never block on absent human) present.
- **interactive reading (wait for the answer)** — "Interactive (a human is at the keyboard — e.g. the Admiral's own latitude interrogation): ask the human directly and wait for the answer." Present; the Admiral latitude case is preserved as the interactive example.
- **four "While interrogating" bullets** — all four present (one-question / challenge-terms / stress-test edge cases / cross-check code).
- **template + checklist-engine footer** — "Template: `templates/INTERROGATION.template.json`. Reference: workbench `references/checklist-engine.md`." Present.

### Register actually shifted — PASS
Opening no longer leads with the human-direct imperative "Interview the user relentlessly" (HEAD's first line). `head -8 | grep -i 'interview the user'` → no match. New opening: "Resolve the handed-in goal … Whoever handed you the goal is your **counterpart** — most often a dispatching delegate …, sometimes a human at the keyboard." Delegated is stated as "the common case"; interactive/human-at-keyboard is the mode note. Register is agent/delegated-first.

### Single skill — PASS
`grep -c '^# Constellation Interrogator'` → 1. `grep -n '^# '` → only line 6. No new/untracked files (`git ls-files --others --exclude-standard` empty). Not split.

### Word count — PASS
Full-file `wc -w`: HEAD 439, working tree 439. In band ~395–483. Reported 439→439 confirmed.

### global-everyone.md pointer — PASS
Line 12 present.

### Only skills/interrogator/SKILL.md changed — PASS
`git status --porcelain` → ` M skills/interrogator/SKILL.md` only. `git diff --name-only HEAD -- skills/commander _shared tests` → 0. Exclusions untouched, no new files.

### Suite green — PASS
`py -m pytest tests/test_install_constellation.py -q` → `38 passed, 118 subtests passed in 3.43s`.

## Blockers
None.

## Out-of-scope observations
- Git emits `warning: LF will be replaced by CRLF` on the working-copy file — pre-existing line-ending config, not introduced by this change; no action needed.

## Workflow feedback
Handoff close criteria were precise and each reproducible from a single command; the doctrine checklist made line-by-line verification fast. The one subtlety worth flagging for future rewrites: the "wait for the answer" phrase legitimately moves from the survey-drive paragraph into the Interactive mode, which could read as a drop under a naive grep — a reviewer must confirm relocation vs. deletion. Handled here; the criteria implicitly allowed for it ("register may move; rules must not be dropped").
