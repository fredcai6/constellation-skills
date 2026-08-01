# Mission Frame — issue #103 (Cluster B diets, minus commander)

**Shrunk frame (reason):** skill-source repo with no `docs/architecture/` packet map; the "architecture" here is the skills corpus structure itself, governed by `docs/CONSTELLATION_OVERVIEW.md` and the epic-101 spec. The change is bounded doc-editing (fold/extract/sweep/rewrite) with no code or interface change, so the full map-first frame adds little; anchors below are the corpus-structural facts that govern the edits.

## Intent
Reduce duplication-with-drift and history-framing in the skills corpus so each SKILL.md reads as one deliberately-written, timeless document with doctrine living once. Four bounded items (admiral fold, docent extraction, cross-file history sweep, interrogator register rewrite), commander excluded (sibling #107).

## Affected capabilities / structural anchors
- `skills/admiral/SKILL.md` + `skills/admiral/references/fleet-doctrine.md` — Admiral operating doctrine; fleet-doctrine is the sanctioned home for platform/detached-survival doctrine and its provenance.
- `skills/docent/SKILL.md` — Docent method; self-contained-HTML constraint block extracts to a new `references/self-contained-html.md`.
- `skills/interrogator/SKILL.md` — single 439-word skill, dual-audience.
- `skills/explorer/SKILL.md`, `skills/charter/references/rigorous-default.md`, `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` — history-framing lines.

## Governing constraints (load-bearing; violating reds the suite)
- `test_relocated_doctrine_leaves_no_residual_in_carrier_skill_md`: retired signatures must stay ABSENT from every SKILL.md body — notably `delegate is not a replacement` (keep the hyphenated `delegate-not-replacement` form), `idle_notification`, `Unchanged-tree shortcut`, `FOLLOW THIS SKILL STRICTLY`; admiral must not contain `breaks recurrence counting`.
- Pointer lines' shared-file names (`global-everyone.md`, `global-orchestrator.md`, `fleet-doctrine.md`, and the new docent reference) must survive — do not sever a carrier's pointer.
- No new `global-*.md` filename (installer glob pins bundle composition). New docent reference lives under `skills/docent/references/` and must not match `global-*.md`.
- Bundle composition (`test_global_doctrine_buckets_bundled_per_audience`) is installer/tier-driven, not text-driven — safe against prose edits, but keep interrogator's `global-everyone.md` compliance pointer for correctness.
- Pre-ruling: a bullet duplicating what #108 moved to `_shared/global-orchestrator.md` is CUT to its existing pointer, not re-folded into fleet-doctrine.md.
- One writer per file; NOT `skills/commander/**`, NOT `docs/ROADMAP.md`, NOT `tests/`.

## Decision anchors / pressure
- Fold-vs-cut per admiral bullet (duplicate→cut-to-pointer; genuine delta→keep; detached-survival content not yet in fleet-doctrine→fold). Surfaced, resolved in-gate.
- Honest-null: an item load-bearing where it is (esp. fleet-doctrine provenance grounding) is skipped-and-reported.

## Evidence surfaces
Command-derived before/after word counts; grep for retired signatures (must be absent) and preserved pointer names (must be present); full suite `py -m pytest tests/ -q` green at each gate boundary. Doc-only → inspection-attestation, not test-shaped proxies.

## Out of scope
Commander diet (#107), `_shared/` content beyond pointer lines, ROADMAP, curator/harness clusters (C/E), any new test authoring beyond a legitimately-moved source line.
