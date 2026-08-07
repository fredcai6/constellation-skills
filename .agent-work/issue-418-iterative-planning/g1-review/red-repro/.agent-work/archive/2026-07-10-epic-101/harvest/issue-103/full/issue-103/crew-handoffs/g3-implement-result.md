# IMPLEMENTER_RESULT — g3 Interrogator register rewrite

## Body replaced
Yes. `skills/interrogator/SKILL.md` body (everything below the YAML frontmatter) replaced with the TARGET DRAFT verbatim. Frontmatter (`name`/`description` block) unchanged. No typos spotted in the draft; placed as given.

## Word count before/after
- Before: `439` (`wc -w skills/interrogator/SKILL.md`)
- After: `439`
- Band: ~395–483 (target 439). In band. (Whole-file count including frontmatter; body-only was 415 before.)

## Doctrine-preservation checklist (all present in new body)
- relentless one-question-at-a-time — "relentless, one-question-at-a-time interrogation"; "Ask one question at a time."
- recommended answer per question — "for each question give a recommended answer."
- list-is-a-prompt-not-a-script — "treat it as a prompt, not a script: decide your own initial question set… don't let an over-prescribed seed shortcut your framing."
- behavior-framing (capability→examples→events→constraints) mapped to `capability`/`event`/`constraint`/`assumption` ontology handing to Cartographer — full paragraph 2.
- compliance pointer to `references/global-everyone.md` — "Compliance/engine-drive rule: inherited — see `references/global-everyone.md`."
- survey drive from `templates/INTERROGATION.template.json` through `scripts/checklist_engine.py` with verbs ask/append/skip/consolidate — paragraph 4.
- answer-from-code-instead-of-asking — "If a question can be answered from the code, explore the code instead of asking."
- delegated reading (counterpart = frozen launch order/delegate; skip settled; context query for missing fact; float for choice outside latitude; never block on absent human) — "Where the answer comes from" / *Delegated*.
- interactive reading (human at keyboard, e.g. Admiral latitude, wait for the answer) — *Interactive*.
- four "While interrogating" bullets — present (one-at-a-time; challenge terms/glossary; stress-test edge cases; cross-check code).
- template + checklist-engine reference footer — "Template: … Reference: workbench `references/checklist-engine.md`."

All items present. No STOP condition triggered.

## Single skill
Exactly one `# Constellation Interrogator` H1 (grep -c = 1). No split. No new files. No `references/` file added.

## Grep evidence
```
wc -w skills/interrogator/SKILL.md            -> 439 skills/interrogator/SKILL.md
grep -c "^# Constellation Interrogator" ...   -> 1
grep -o "global-everyone.md" ...              -> global-everyone.md
git check-ignore skills/interrogator/SKILL.md -> exit 1 (committed, not ignored)
grep -c -E "idle_notification|Unchanged-tree shortcut" -> 0 (no forbidden signature)
```

## Suite tail
```
.......................... [ 68%]
............                                                             [100%]
38 passed, 118 subtests passed in 3.44s
```

## Assumptions
- "Before (439)" in the handoff refers to the whole-file `wc -w` (includes frontmatter); confirmed — the before count was 439 whole-file. After is also 439, so the register rewrite is word-neutral.
- Kept the blank line between frontmatter and H1 (matches prior file and standard skill formatting).

## Stop conditions
None triggered. All doctrine items found in the draft; word count in band; scope not exceeded.

## Out-of-scope observations
None. Change confined to `skills/interrogator/SKILL.md`. No touch to `skills/commander/**`, `_shared/**`, or `tests/**`.

## Workflow feedback
Clean, self-contained handoff: verbatim draft + explicit doctrine checklist + exact grep/verification commands made this deterministic. The one mild friction: the "before (439)" figure is a whole-file count while the draft is described as "body," which could invite a body-only comparison — calling out which count is meant would remove the ambiguity. Otherwise ideal for a bounded placement task.
