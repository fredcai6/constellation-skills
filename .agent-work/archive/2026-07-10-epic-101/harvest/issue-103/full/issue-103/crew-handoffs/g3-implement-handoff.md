# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g3` — Interrogator register rewrite (in place, single skill)

## Task
Replace the body of `skills/interrogator/SKILL.md` (everything BELOW the YAML frontmatter, keeping the frontmatter unchanged) with the TARGET DRAFT below. This rewrites the register so agent-loaded/delegated prose leads and the human-at-keyboard case is a brief mode note — the x2 mis-tailoring fix. It stays ONE skill; do NOT split; do NOT bloat. All doctrine preserved.

## Protected Intent
Every operative rule the interrogator carried still present; the only change is register/ordering so the common (delegated/agent) invocation reads first and the interactive-human case is a mode note. The `global-everyone.md` compliance pointer survives.

## Test Mode
inspection-only — single-file register rewrite; verified by a doctrine-preservation checklist + word count + suite green.

## Close Criteria
- Frontmatter (`---` name/description block) unchanged.
- Body replaced with the TARGET DRAFT verbatim (fix any obvious typo you spot, else verbatim).
- Word count within ~10% of 439 (target band ~395–483). Report `wc -w`.
- Doctrine-preservation checklist (all must be present in the new body): relentless one-question-at-a-time; recommended answer per question; list-is-a-prompt-not-a-script; behavior-framing (capability→examples→events→constraints) mapped to the `capability`/`event`/`constraint`/`assumption` ontology handing to Cartographer; compliance pointer to `references/global-everyone.md`; survey drive from `templates/INTERROGATION.template.json` through `scripts/checklist_engine.py` with verbs ask/append/skip/consolidate; answer-from-code-instead-of-asking; delegated reading (counterpart = frozen launch order/delegate; skip what it settles; context query for a missing fact; float for a choice outside latitude; never block on an absent human); interactive reading (human at keyboard, e.g. Admiral latitude interrogation, wait for the answer); the four "While interrogating" bullets; template + checklist-engine reference footer.
- Single skill: exactly one `# Constellation Interrogator` H1; no new files; not split.
- No forbidden signature (`idle_notification`, `Unchanged-tree shortcut`, etc. — none belong here anyway).
- Suite green: `py -m pytest tests/test_install_constellation.py -q`.

## TARGET DRAFT (body — everything below the frontmatter)

```
# Constellation Interrogator

Resolve the handed-in goal to common understanding through relentless, one-question-at-a-time interrogation. Whoever handed you the goal is your **counterpart** — most often a dispatching delegate (a Commander running under an Admiral launch order, or any delegated dispatch), sometimes a human at the keyboard. Walk the design tree, resolving dependencies one at a time; for each question give a recommended answer. If you're given a list of questions, treat it as a prompt, not a script: decide your own initial question set, and don't let an over-prescribed seed shortcut your framing.

Frame an ambiguous ask in behavior terms first. Start from the capability, then drill: **what capability is being added or changed** (the present-tense thing the system will do); **concrete examples/use cases** of that capability in action, including the edge cases; **events that matter** architecturally (boundary-crossing or contract signals, not every runtime event); and the **governing rules/constraints/assumptions**. Resolve which capability is in play before debating mechanism. Map this framing to the existing `capability`/`event`/`constraint`/`assumption` ontology so the resolved understanding hands cleanly to the Cartographer.

Compliance/engine-drive rule: inherited — see `references/global-everyone.md`.

Drive the question list as a `survey` from `templates/INTERROGATION.template.json` through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): ask one question at a time and resolve its answer; `append` follow-ups and new branches as answers open them; `skip` questions an earlier answer settled; then `consolidate` into the resolved understanding. If a question can be answered from the code, explore the code instead of asking.

**Where the answer comes from (two modes).** *Delegated* (the common case — no reachable human): your counterpart is the **frozen launch order / dispatching delegate**. Answer each question from it, `skip` questions it already settles, and when it neither answers nor lets you safely proceed, take it **to the delegate** — a missing fact as a **context query**, a choice outside inherited latitude as a **float** — rather than blocking on an absent human. *Interactive* (a human is at the keyboard — e.g. the Admiral's own latitude interrogation): ask the human directly and **wait for the answer**.

## While interrogating
- Ask one question at a time.
- Challenge terms that conflict with the glossary; propose a precise canonical term for vague or overloaded ones.
- Stress-test domain relationships with concrete edge-case scenarios.
- Cross-check claims against the code and surface contradictions.

Keep going until the goal is resolved or your counterpart says enough, then consolidate the result for the invoker.

Template: `templates/INTERROGATION.template.json`. Reference: workbench `references/checklist-engine.md`.
```

## Allowed Scope
`skills/interrogator/SKILL.md` only.

## Specific Exclusions
No other file. NOT `skills/commander/**`, `_shared/**`, `tests/**`. Do not split into multiple skills. Do not add a `references/` file.

## Constraints
- One skill, no split, no bloat; word count in the ~395–483 band.
- Keep the `global-everyone.md` compliance pointer.
- Frontmatter unchanged.

## Map Anchors (inbound)
- **Structural:** `skills/interrogator/SKILL.md` (single file).
- **Constraints:** stays one skill; register agent-first; all doctrine preserved.

## Deliverable Path Check
- **Committed** — `skills/interrogator/SKILL.md`; `git check-ignore` exit 1.
- **Local-only** — `.agent-work/issue-103/crew-handoffs/g3-implement-result.md`.

## Required Evidence
- `wc -w skills/interrogator/SKILL.md` before (439) and after.
- `grep -c "^# Constellation Interrogator" skills/interrogator/SKILL.md` (expect 1).
- `grep -o "global-everyone.md" skills/interrogator/SKILL.md` (expect present).
- Suite tail: `py -m pytest tests/test_install_constellation.py -q`.

## Verification Commands
```bash
cd /c/Programs/constellation-wt-103
wc -w skills/interrogator/SKILL.md
grep -c "^# Constellation Interrogator" skills/interrogator/SKILL.md
grep -o "global-everyone.md" skills/interrogator/SKILL.md
py -m pytest tests/test_install_constellation.py -q
```

## Suggested Model Tier
`simple bounded — place the provided draft, verify counts + doctrine checklist`

## Authority
The target draft and register decision are made. Do not rewrite it in your own voice; place it as given. If you believe a doctrine item is missing from the draft, STOP and return rather than adding freely.

## Stop Conditions
Stop if: a doctrine item from the checklist is absent from the target draft; word count lands far outside the band; scope must be exceeded.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/issue-103/crew-handoffs/g3-implement-result.md` AND final message before idling): body replaced, word count before/after, doctrine-preservation checklist confirmed, grep evidence, suite tail, assumptions, stop conditions, out-of-scope observations, workflow feedback.
