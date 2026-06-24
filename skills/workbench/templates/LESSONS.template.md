# Lessons Playbook

<!-- playbook-state: run-tick=0 cap=20 dormancy-runs=10 -->

Curated, bounded workflow lessons for this repo — the distilled derivative of the
append-only `.agent-work/AGENT_FEEDBACK.md` log. Read the **Active** section at the
Commander `context` step and condition planning on it. This file is **never edited
by hand or by an LLM directly**: propose structured delta operations
(add/confirm/disconfirm/mention/retire) in a `lessons-delta.json` and apply them
with `apply_lessons_delta.py`, which enforces the cap, grounding citations, and
counter rules deterministically.

Rules the apply script enforces:

- Hard cap on Active lessons (default 20); beyond it, retire before adding.
- Every lesson and every confirm/disconfirm cites a grounding artifact line
  (feedback entry, log line, engine state). No citation, no entry.
- `confirmed`/`disconfirmed` are symmetric; when disconfirmed catches confirmed,
  the lesson is flagged `charter-review` instead of silently kept.
- **Counter semantics split by scope.** For most scopes a confirm is *trust* —
  the lesson held again. For a `constellation`-scoped lesson it is the opposite:
  a recurrence of an unfixed shared-machinery defect. The script accrues
  `recurrences` (debt), not `confirmed` (trust), and flags `recurrence-debt`.
  Pay the debt by exporting to `CONSTELLATION_FEEDBACK.md` and fixing upstream,
  then retire it — never let a constellation defect get "confirmed" into a
  permanent local workaround.
- `retire` **deletes** a lesson outright — there is no graveyard. Delete a lesson
  once you believe it's handled (internalized into the workflow, or a
  constellation defect fixed upstream); worst case it re-surfaces in a later run
  and you learn it again. Active lessons unconfirmed for `dormancy-runs` ticks are
  auto-deleted, except `constellation`-scoped debt, which is pinned until you
  retire it by hand.

Lesson shape (script-owned; shown for readers):

```markdown
### lesson:<kebab-id>
- scope: handoff | commander | admiral | project | constellation
- task-class: general-workflow | <project-domain-tag>
- statement: <the lesson, one or two sentences, actionable>
- grounding: <artifact citation that produced it>
- mentions: 0 / confirmed: 0 / disconfirmed: 0
- recurrences: 0   (constellation scope only — debt; omitted when 0)
- status: active | charter-review | recurrence-debt
- added / last-confirmed: <date> (<work-id>)
```

## Active
