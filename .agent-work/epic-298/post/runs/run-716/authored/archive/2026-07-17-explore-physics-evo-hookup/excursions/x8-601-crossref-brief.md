# Excursion Brief: `x8-601-graph-cross-reference`

## The one named question

For every issue in the #601 epic graph and its linked physics issues, what disposition does the exploration's confirmed direction imply — DONE / KEEP-AS-IS / ABSORB-INTO-NEW-EPIC / CLOSE-REPLACED-BY-<new work> — such that nothing closes without a named replacement?

## Type

research

**Why this type:** issue-graph audit against a written design frame; nothing to build.

## What "answered" looks like

A disposition table covering: #601 (epic) + children #602–#610, plus #450, #513, #506, #589, #577, #609 (and its pile where relevant to the new plan), #499, #483, #389, #425/#375. Columns: issue, one-line current state (verified via `gh issue view`, incl. any status banners/comments — note #601's banner was updated 2026-07-16 and #499/#483 got status comments 2026-07-17), what the exploration direction does to it, disposition, replacement (named new-epic workstream or "survives as-is"), evidence citation. Also: list anything OPEN in the repo issue tracker that plausibly belongs to this program but wasn't named above (sweep, don't assume).

The exploration's direction is defined by `.agent-work/explore-physics-evo-hookup/IDEAS_BOARD.md` — read it in full first (The point, Thematic bearings, Cycle-4 decisions, Banked one-offs, Rejected ideas). Treat it as the authoritative design frame.

## Budget / stop conditions

- Read-only (`gh issue view/list` allowed). Do NOT close, edit, or comment on any issue.
- ~45–60 min. UNKNOWN disposition acceptable per item with reason; silence is not.
- **Scoped nulls:** disposition recommendations are inputs to the human's route decision, not decisions.

## Research excursion

- **Sources:** GitHub issues via `gh`; `.agent-work/explore-physics-evo-hookup/IDEAS_BOARD.md`; `.agent-work/601-fantasy-league/`, `.agent-work/epic-601*/` work areas for in-flight state; excursion results x1–x7 in `.agent-work/explore-physics-evo-hookup/excursions/` for evidence already gathered.
- **Findings format:** the disposition table + a short "surprises" section (anything in the issue graph that contradicts the board).

## Return

Full findings → `.agent-work/explore-physics-evo-hookup/excursions/x8-601-crossref-RESULT.md`. Final message = summary of disposition counts + surprises.
