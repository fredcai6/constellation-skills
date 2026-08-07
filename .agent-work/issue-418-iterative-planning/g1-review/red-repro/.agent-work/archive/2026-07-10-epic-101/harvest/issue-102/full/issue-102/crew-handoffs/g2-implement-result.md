# IMPLEMENTER_RESULT — g2-implement (issue #102, Move 2: engine-invocation string)

## Outcome: SUBSTANTIALLY SUBSUMED BY MOVE 1 + narrow completing edit (honest partial — COMPLETE deliverable)

Move 1 (commit `55d2378`, "single-source mandatory-compliance boilerplate to global-everyone")
already single-sourced the GENERIC engine-invocation/compliance clause into
`skills/_shared/global-everyone.md` §"Engine-drive compliance". The residual survey confirms **no
generic engine-invocation duplicate survives** outside role-specific or canonical-source contexts.
The only genuine gap was that global-everyone's engine-drive doctrine did **not** point at the
canonical engine MECHANISM. I made that one narrow completing edit and nothing else. No
role-specific spine content was force-merged (that would have been semantic loss — see stop
conditions).

## Completed slice
Added a one-clause pointer (4 lines) in `global-everyone.md`'s "Engine-drive compliance" section
directing to the canonical engine mechanism (`workbench references/checklist-engine.md`). No new
`global-*.md` filename; mechanism content not duplicated.

## Files changed
- `skills/_shared/global-everyone.md` (+4 lines, single hunk). Tracked/committed path (git
  ls-files exit 0); not gitignored.
- (local-only, gitignored) `.agent-work/issue-102/crew-handoffs/g2-implement-plan.json` — engine
  state; `.agent-work/issue-102/crew-handoffs/g2-implement-result.md` — this file.

## FIRST-STEP grep evidence + classification (before-state, post-Move-1 tree)

Command:
```
grep -rn "through the engine\|one step at a time\|drive the gated\|drive a controller\|gate by gate" skills/*/SKILL.md
grep -n "checklist-engine" skills/_shared/global-everyone.md
```

Output + classification of all 11 hits:

| Hit | Text (abridged) | Classification |
|---|---|---|
| admiral/SKILL.md:10 | "Compliance/engine-drive rule: inherited — see `references/global-everyone.md`" | POINTER to global-everyone (already inherited) → leave |
| admiral/SKILL.md:14 | "Drive `ADMIRAL_SPINE.template.json` through the engine: init → latitude → execute → closeout" | ROLE-SPECIFIC (own spine + steps) → keep local |
| cartographer/SKILL.md:8 | "drive `CARTOGRAPHER.template.json` through the engine as your controller" | ROLE-SPECIFIC (own template) → keep local |
| commander/SKILL.md:12 | "drive every spine step... Compliance/engine-drive rule: inherited — see `references/global-everyone.md`" | ROLE-SPECIFIC + POINTER → keep local |
| commander/SKILL.md:25 | amend/reopen verbs, hand-edit ban | ROLE-SPECIFIC engine-usage detail → keep local |
| commander/SKILL.md:30 | "Drive the gated spine (`COMMANDER_SPINE.template.json`) through the engine one step at a time: init → context → ..." | ROLE-SPECIFIC (own 10-step spine) → keep local |
| commander/SKILL.md:36 | "drive `execute.json` gate by gate" | ROLE-SPECIFIC execute-step detail → keep local |
| explorer/SKILL.md:33 | "Drive the gated spine (`EXPLORER_SPINE.template.json`) through the engine one step at a time. Instantiate it at `init` via..." | ROLE-SPECIFIC (own spine + init instantiation) → keep local |
| scout/SKILL.md:8 | "Drive `SCOUT.template.json` as a gated checklist through the engine (workbench `references/checklist-engine.md`)" | ROLE-SPECIFIC (own template) + already points at mechanism → keep local |
| workbench/SKILL.md:3 | description frontmatter "drive a gated/survey checklist through the engine" | CANONICAL mechanism source → leave |
| workbench/SKILL.md:39 | "Drive a controller one step at a time with the absolute path to... `scripts/checklist_engine.py`... See `references/checklist-engine.md`" | CANONICAL mechanism source → leave |

`grep -n "checklist-engine" skills/_shared/global-everyone.md` → **EMPTY** (confirmed the pointer
was missing — the gap this move closes).

Conclusion: every "through the engine one step at a time" instance names that role's OWN spine
template and steps; there is **no generic, role-agnostic engine-invocation duplicate** left to
consolidate. Consolidating any of these into global-everyone would delete role-specific workflow
content — explicitly barred by the handoff. Move 2 is therefore subsumed by Move 1 except for the
missing mechanism pointer.

## Added-pointer quote (exact)
```
How you invoke the engine (the mechanism — controller types, verbs, evidence shape, ordering, the rework and
consolidation guards) is explained once in workbench `references/checklist-engine.md`; each role skill only names
its own spine/survey template and drives it, it never re-explains the engine.
```

## After-state verification
- `grep -c 'checklist-engine.md' skills/_shared/global-everyone.md` → **1** (points exactly once;
  no new global-*.md file).
- Role-specific spine instructions preserved: post-edit residual grep shows
  commander:30, explorer:33, workbench:39 unchanged in substance.

## Suite tail
```
442 passed, 2 skipped, 26 subtests passed in 13.27s
```
Both engine command-checks (`grep -c ... -eq 1`; pytest) passed on `advance m2-edit`.

## Engine drive
Gated plan `g2-implement-plan.json` driven through the bundled engine
(`C:/Users/fredc/.claude/skills/constellation-implementer/scripts/checklist_engine.py`):
m0-context → m1-survey → m2-edit, all complete; lease released. `current` → "DONE: no open items."

## Assumptions
- "workbench `references/checklist-engine.md`" is the correct citation form — matches the exact
  phrasing already used by admiral:63, cartographer:27, commander:113, implementer:14/24, etc.
- Move 1's `global-everyone.md` §"Engine-drive compliance" is the intended destination section
  (handoff named it explicitly).

## Stop conditions
None triggered. The grep did NOT contradict the subsumed-by-move-1 reading — it confirmed it.
No consolidation would have required deleting role-specific spine instructions, so I did not force one.

## Out-of-scope observations (triage candidates)
- Skills reference `references/global-everyone.md` (a per-skill bundled copy) while the canonical
  source is `skills/_shared/global-everyone.md`. The bundling/sync mechanism between _shared and
  per-skill `references/` copies was not inspected here — worth a residual/content-pin check that
  the g7 pin already anticipates. Not touched.
- No banner/manifest/prototyper work done (explicitly excluded: g3, #105, g1).

## Workflow feedback
- Handoff was complete and unusually well-specified: it pre-flagged the reconcile-judgment risk,
  gave the classification taxonomy (generic/role-specific/canonical), and named both honest
  outcomes as complete deliverables. This removed all ambiguity — no improvisation needed.
- Minor friction: the plan template's `config_ref` points at `docs/agents/engine-config.json`,
  which does not exist in this repo. The engine did not require it (command checks ran fine), so it
  is inert — but a handoff/template note that config_ref is optional/unused here would save a
  verification detour.
- Engine ergonomics: `current` rejects `--session-id` while all mutating verbs require it. Not a
  blocker once learned, but the asymmetry cost one refused call.
