# Lessons Playbook

<!-- playbook-state: run-tick=0 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 -->

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
- **Apply-or-defer is forced at feedback.** A lesson is *ripe* when its scope threshold is
  crossed — non-constellation `confirmed >= apply-confirmed` (default 3) with a `target`, or
  constellation `recurrences >= apply-recurrences` (default 1). The `feedback` step refuses to
  advance (via `verify_lessons_applied.py`) until every ripe lesson is settled: **apply** it
  (`apply` op — edit the `target`, then the lesson is deleted as paid), **export** it
  (`export` op — constellation only; status `exported`, pinned until shipped upstream), or
  **defer** it (`defer` op — records `deferred-at`; re-fires only when the count climbs).
- **Match the fix form to the failure before applying.** Name the strongest rung the
  `target` supports — pick the highest that fits, not the easiest:
  1. Mechanical constraint → an **engine gate or script check**. One-line test: could a
     script refuse this instead of a sentence warning about it? If yes, this rung wins.
  2. Omitted element → a **required template slot** — a structural field the artifact
     cannot skip, not a reminder to remember it.
  3. Wrong-shaped output → a **positive recipe or contract** stating what to produce.
     Prohibitions backfire here, so state the target shape directly.
  4. Discipline slip → a **prohibition plus a rationalization counter** (last resort, for
     letter-vs-spirit dodges where the agent already knows better).
- **Prove the doctrine edit with a reproduction drill.** Applying a *ripe* lesson whose
  `target` is a **doctrine artifact** (a `.md` skill/doc or a `.template.*`) requires a
  reproduction **drill**, referenced in the apply op's `drill` field — before/after-arm
  proof (fail reproduces on the old text, no longer fires on the edited text) that the
  fresh-context auditor, not the editor, runs and commits under
  `docs/superpowers/drills/`. The apply script refuses a ripe doctrine apply that omits
  `drill` (field-presence only — it never grades the drill). Code-targeted applies (a test
  suite is the proof) and non-ripe applies are exempt.

Lesson shape (script-owned; shown for readers):

```markdown
### lesson:<kebab-id>
- scope: handoff | commander | admiral | project | constellation
- task-class: general-workflow | <project-domain-tag>
- statement: <the lesson, one or two sentences, actionable>
- grounding: <artifact citation that produced it>
- target: <editable artifact this applies to: docs/agents/*, a template, skills/_shared/global-*, or CONSTELLATION_FEEDBACK.md> (optional)
- mentions: 0 / confirmed: 0 / disconfirmed: 0
- recurrences: 0   (constellation scope only — debt; omitted when 0)
- status: active | charter-review | recurrence-debt | deferred | exported
- added / last-confirmed: <date> (<work-id>)
```

## Active
