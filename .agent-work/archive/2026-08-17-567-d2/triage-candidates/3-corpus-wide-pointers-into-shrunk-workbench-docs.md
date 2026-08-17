# Triage candidate: verify corpus-wide pointers into workbench's shrunk docs once every wave-2 lane merges

**Found during:** 567-d2 understand + plan, comparing the door's tool schemas
against `checklist-engine.md`/`status-model.md`.

**What:** ~20+ files across the corpus (`skills/_shared/global-everyone.md`,
`skills/commander/references/commander-core.md`,
`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`,
`skills/reviewer/templates/REVIEW_RESULT.template.md`,
`skills/implementer/templates/IMPLEMENTER_RESULT.template.md`, most other
skills' own `SKILL.md`, several `tests/*.py`) cite
`workbench references/checklist-engine.md` or `references/status-model.md` by
name or section heading. This lane's shrink was deliberately scoped to keep
every section any of those citations depend on (verified for the ones this
lane could find: the `## MCP door` and `## Session lease` sections, and the
`Crew Return Status`/`Review Verdict` sections of `status-model.md`) — but this
lane could only verify citations it could find by grep, in files it does not
own and cannot exhaustively audit for every possible dependency shape.

**Why this lane didn't resolve it fully:** Most of these files are fenced to
other lanes this wave (lane D1 owns `skills/**` except `skills/workbench/**`),
and lane D1 is independently removing "CLI fallback" clauses from ~13 other
files this same wave — a second pass after all wave-2 lanes merge is the right
place to re-sweep for any pointer this lane's grep missed or that D1's own
edits newly introduce/remove.

**Suggested disposition:** recommend-and-defer to the Admiral's epic-close
sweep — `grep -rn "checklist-engine.md\|status-model.md" skills/ docs/ tests/
scripts/` once every wave-2 lane has merged, confirm every hit still resolves
to real content at the section granularity it expects.
