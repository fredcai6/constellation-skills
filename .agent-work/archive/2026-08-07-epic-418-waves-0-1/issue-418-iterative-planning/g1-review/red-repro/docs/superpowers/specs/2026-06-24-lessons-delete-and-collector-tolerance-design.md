# Lessons delete-not-mark + a collector that sees every repo

**Date:** 2026-06-24
**Status:** Approved (design), pending implementation plan
**Branch:** `constellation/lessons-delete-and-collector-tolerance`
**Relates to:** [docs/RECURSIVE_IMPROVEMENT_DESIGN.md](../../RECURSIVE_IMPROVEMENT_DESIGN.md)

## Problem

A sweep of the four dogfooding repos under `C:\Programs` (f1Brainz, network_elo,
st-cleanroom-e3, story_time) surfaced two coupled defects in the recursive-improvement
machinery itself:

1. **The collector is blind to 3 of the 4 repos.** `collect_feedback.py` only parses
   the structured field format (`- **Candidate:**`, `- **Observed:**`). Only f1Brainz
   writes that. network_elo / story_time / st-cleanroom write an older prose shape
   (`### Lesson: … **Upstream fix:** …`), and `_is_finding()` silently drops every one.
   The casualty is the *strongest* signal the system exists to catch: the only genuinely
   cross-project finding (`worktree-isolation-not-guaranteed`, independently in network_elo
   and story_time) is invisible.

2. **The Dormant section is a drift-causing trap, not a safety net.** `apply_lessons_delta.py`
   never deletes — `retire` parks a lesson in `## Dormant`, unconfirmed lessons auto-demote
   there after N ticks, and a later `confirm` can revive. In practice nothing revives:
   - `add` rejects any id already present in Dormant (`"id already exists (dormant)"`), so a
     recurring lesson can't be cleanly re-added under its old id. The auditor coins a *new*
     slug instead — which is exactly the slug-drift already corrupting the upstream collector
     (`spine-lease-stale-on-long-crew` vs `…-step` fingerprint as two findings).
   - Dormant has no cap and grows forever; its only reader is one auditor line.

   It is a collector with no front end, and it actively manufactures the drift that breaks
   recurrence counting.

## Goals

- The collector sees findings from every repo regardless of export format.
- Lessons are **deleted** when an agent believes they're handled, not parked. Worst case a
  lesson re-surfaces and is learned again — that re-surfacing is itself signal.
- Remove bookkeeping that no front end reads (Dormant; the upstream `resolved` sidecar +
  auto-close lifecycle).
- Keep the one piece of upstream bookkeeping that *is* a front end: the human-gated GitHub
  inbox where findings get pulled into the top-level structure.

## Non-goals

- No mass rewrite of historical feedback entries (parser tolerance covers them; rewriting
  old logs is the dead-weight curation we're removing).
- No change to lesson counter semantics for non-constellation scopes, the recurrence-debt
  model for constellation scope, or the inbox *filing* logic.
- Not renaming the `retire` op (keeps blast radius down; see Decision D5).

## Design

### Piece 1 — Engine: replace Dormant with deletion (`scripts/apply_lessons_delta.py`)

- **`retire` becomes a hard delete.** The lesson is removed from the playbook entirely. It
  still requires a `reason` (printed to the apply log and intended for the commit message);
  nothing is persisted in the playbook — git history is the audit trail.
- **Drop `## Dormant` entirely:** remove the section from `Playbook`, `render_playbook`, the
  revive-from-dormant branch in `confirm`, and the auto-demotion-to-dormant branch in the
  tick path.
- **Tick auto-aging deletes.** A lesson unconfirmed for `dormancy-runs` ticks is **deleted**,
  not parked — *except* `constellation`-scoped lessons, which are **pinned** (never
  auto-deleted): they represent shared-machinery defects that persist until fixed upstream,
  and are removed only by an explicit `retire` when the fix ships. (`dormancy-runs` /
  `runs-since-confirmed` are retained and now drive deletion.)
- **Backward compatibility / migration:** `load_playbook` still *tolerates* a legacy
  `## Dormant` heading in existing files — it parses those lessons and **discards** them
  (they are not carried forward). `render_playbook` no longer emits the section. Net effect:
  the first delta applied to any existing playbook garbage-collects its graveyard in one
  write. No separate migration step.
- **Drift trap removed:** with no Dormant, re-adding a previously-deleted id just succeeds.

### Piece 2 — Collector: parse the prose format too (`scripts/collect_feedback.py`)

- Extend parsing so a finding can be recognized in either shape:
  - **Field shape (current):** `## <heading>` block containing `- **Field:** value` lines.
  - **Prose shape (legacy):** `### <slug> (scope)` sub-heading under a `## <epic>` block,
    with inline `**Lesson:** <id>`, `**Upstream fix:** …`, and the leading paragraph as the
    `observed` text. A `### …` sub-block with a `**Lesson:**`/`**Upstream fix:**`/observed
    paragraph counts as a finding.
- `_is_finding()` updated to accept either shape; identity still flows through `fingerprint()`
  (lesson id → candidate slug → content hash), so prose entries that carry a `**Lesson:**`
  id fingerprint stably. Note this buys **visibility, not auto-grouping**: network_elo named
  the worktree-isolation finding `…-not-real-on-windows` and story_time `…-not-guaranteed`,
  with no shared `Lesson:` id — so they surface as two findings, not one. The parser stops
  them being invisible; cross-repo grouping is what the field-format `Lesson:` id buys going
  forward (Piece 3), not something the parser can infer.
- Note in `_render_group`/report that st-cleanroom-e3's export is byte-identical to
  story_time's (a clone) — dedup by project name already collapses it; no special-casing.

### Piece 3 — Repos onto the current template (installer propagation)

- Use the installer's template-propagation path to refresh `CONSTELLATION_FEEDBACK.template.md`
  and `LESSONS.template.md` (delete-semantics preamble, Piece 5) into the three stale repos,
  so **future** entries use the field format with stable `Lesson:` ids. Combined with Piece 2,
  both legacy and new entries are collectable.
- This is propagation only — it does not touch the repos' already-written log entries.

### Piece 4 — Upstream bookkeeping: keep the front end, drop the unused back end (`collect_feedback.py`)

- **Keep** the inbox issue *filing* — the GitHub backlog in this repo is the human-read front
  end where findings get pulled up. `eligible_for_filing`, `issue_spec`, recurrence counting,
  and the filing half of `sync_issues` stay.
- **Drop** the `resolved` sidecar state and the inbox **auto-close** path as vestigial: under
  delete-not-mark a consuming repo *deletes* a collected finding rather than marking it
  resolved, so the auto-close trigger can never fire. Remove `mark_resolved`,
  `resolved_across`, the `--resolve`/`--note` CLI, the `to_close` logic and `gh_close_issue`
  wiring, the resolution-comment/close branches, **and the resolved-skip in `collect()`**
  (it reads `state["resolved"]`); `load_sidecar` drops the `resolved` key from its default
  shape. Issues close the normal way (a PR that fixes the finding references it; a human
  closes it).
- **Keep** `collected` sidecar state purely as filing-dedup within the window before a
  consuming repo deletes the entry, and keep the inbox ledger's idempotent *file* + *comment-
  on-growth* behavior (recurrence pressure is still useful on an open issue).

  *(Open sub-question for the plan, not blocking: whether `collected` is now fully redundant
  with the fingerprint-keyed inbox ledger. Default: keep `collected`; revisit if it proves
  redundant.)*

### Piece 5 — Teach the repo agents to delete (skills + templates)

- `skills/workbench/templates/LESSONS.template.md`: replace the dormant/revive/auto-demote
  preamble lines with delete semantics — "delete a lesson with `retire` once you believe it's
  handled; worst case it re-surfaces and you learn it again," and remove the `## Dormant`
  section from the template body.
- `skills/lessons-auditor/SKILL.md` + `templates/LESSON_CANDIDATES.template.md` +
  `templates/LESSONS_AUDIT.template.json`: stop referencing "Active and Dormant" (just
  Active); direct the auditor to emit `retire`(=delete) for handled/obsoleted project lessons
  and for constellation findings confirmed fixed upstream.
- `skills/commander/` + `skills/admiral/` closeout text and the two SPINE templates: where
  they mention retiring/dormant lessons, align to delete semantics.

### Tests

- `tests/test_apply_lessons_delta.py`: remove dormant/revive/auto-demote-to-dormant tests; add
  (a) `retire` deletes outright, (b) tick auto-aging deletes a stale lesson, (c) constellation
  lessons are pinned from auto-aging, (d) an id can be cleanly re-added after deletion,
  (e) loading a legacy file with a `## Dormant` section discards it on next render.
- `tests/test_apply_lessons_delta.py` round-trip: a constellation recurrence-debt lesson still
  renders/parses identically (unchanged).
- `tests/test_collect_feedback.py` (or wherever collector tests live): add prose-format parsing
  tests (single finding, cross-project grouping via `**Lesson:**` id, content-less block still
  dropped); remove the `resolved`/`--resolve`/auto-close tests for the dropped machinery;
  keep file + comment-on-growth tests.

## Decisions (resolved during brainstorming)

- **D1** Remove Dormant entirely rather than keep it as an auto-aging pen — it's unread and
  causes slug drift via the re-add collision.
- **D2** Auto-aging deletes, but **pins** constellation-scoped lessons (unpaid upstream debt
  must not silently vanish).
- **D3** Keep inbox *filing*; drop the `resolved` sidecar + auto-close (no front end; can't
  fire under delete-not-mark).
- **D4** Parser tolerance over historical rewrite.
- **D5** Keep the op name `retire` (now meaning delete) to limit churn; revisit a rename to
  `delete` later if the verb misleads.

## Rollout order

1. Engine (Piece 1) + its tests — self-contained, unblocks the template/skill copy changes.
2. Collector parser tolerance (Piece 2) + tests.
3. Collector bookkeeping removal (Piece 4) + test updates.
4. Templates + skills delete semantics (Piece 5).
5. Installer propagation into the three repos (Piece 3) — last, after templates are final.
