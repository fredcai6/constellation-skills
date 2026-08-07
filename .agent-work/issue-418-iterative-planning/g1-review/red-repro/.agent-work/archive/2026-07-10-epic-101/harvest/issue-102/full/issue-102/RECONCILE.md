# Reconcile — issue #102 (skill-source repo, no packet map)

Per commander doctrine: no docs/architecture packet map exists, so reconcile the structural record
directly rather than dispatching Cartographer.

## What structural records the change could touch
- `docs/CONSTELLATION_OVERVIEW.md:28-29` — the context-artifact table describing the `_shared` buckets
  (`global-{everyone,orchestrator,crew}.md`, `design-it-twice-brief.md`).
- `scripts/install_constellation.py:98-113` — `SKILL_REFERENCE_BUNDLES` (the bundle mechanism).

## Assessment
- The context-artifact table describes each `_shared` bucket by its PURPOSE ("inherited approach
  doctrine read first at each checklist's context step; identical across projects; the home for
  general-workflow constellation lessons"), NOT as a rule-by-rule inventory. This cluster consolidated
  more doctrine INTO those buckets and out of the per-role SKILL.md carriers — which makes the table's
  description MORE accurate, not less. No edit needed to keep it true.
- The bundle mechanism is unchanged: no new `global-*.md` filename; the existing buckets
  (global-everyone, global-orchestrator) gained subsections and still bundle exactly as before. The
  regression net (content-pin + no-residual) now MECHANICALLY guards the structure the table asserts.
- `design-it-twice-brief.md` row (29) is unchanged — move 10 was subsumed by prior #99, no edit.

## Reconcile outcome: reasoned no-op (compliant)
The change touched no schema or design-doc CLAIM that is now stale; it strengthened the already-recorded
`_shared`-buckets-are-the-single-home structure. Recording a reasoned no-op per doctrine.

## Map impact (for the return report)
- `_shared/global-everyone.md`: 781 → 1180 words (+399) — gained Engine-drive compliance, A delegate is
  not a replacement, Verify claimed side-effects against the world, Scoped nulls (+ engine-mechanism pointer).
- `_shared/global-orchestrator.md`: 883 → 1083 words (+200) — gained Unchanged-tree shortcut, Idle
  subagent adjudication.
- Per-role SKILL.md carriers shrank correspondingly (see wordcount-before/after.txt); corpus total
  17097 → 16649 words (−448 net) — the reduction is the deletions (6 banners) + trims, honestly net of
  the relocations (which are relocated, not removed, from a role's installed total).
- Bundling unchanged; a new mechanical regression net (2 tests) now guards relocated doctrine.
