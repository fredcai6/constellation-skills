# Mission Frame — cmdr-602 (shrunk)

Shrunk per doctrine: two content-fill doc edits into two already-lean bootstrap pointer files, content fully
specified by the ratified launch order + source verification in PROBLEM_STATEMENT.md. No design/interface
choice, no code path, no architecture decision — the map adds process-hygiene value (confirming the live
evo_predictor architecture facts) already captured in PROBLEM_STATEMENT.md, not additional planning surface.

## Intent
Land the epic #601 mission statement in `AGENTS.md` and correct `CLAUDE.md` for evo_predictor architecture
accuracy (source-verified pointer, since no literal stale text exists to replace — see PROBLEM_STATEMENT.md),
without touching any other file.

## Affected Capabilities
None (no runtime capability changed) — two static bootstrap/context files consumed by future agent sessions.

## Structural Anchors
- `AGENTS.md` (repo root) — Codex agent bootstrap pointer file, 17 lines.
- `CLAUDE.md` (repo root) — Claude agent bootstrap pointer file, 14 lines, created fresh 2026-07-05 (`eba82d2b`).
- `src/evo_predictor/sampled_runtime.py`, `module_adapters/_registry.py`, `src/latent_power/field_solve.py`,
  `src/evo_predictor/fusion.py` — verified source of the live architecture facts cited in CLAUDE.md's new pointer
  (see PROBLEM_STATEMENT.md for line-level citations).

## Governing Constraints / Assumptions
- File-ownership fence: `AGENTS.md` + `CLAUDE.md` only this wave (launch order).
- "Keep AGENTS.md tight; it is a bootstrap file, not an essay" (launch order Pre-Ruling) — applies equally to
  CLAUDE.md by house style (both are lean pointer files today).
- Docs-change evidence bar (ORCHESTRATOR_CONTEXT): correct repo/domain, valid commands, existing references,
  current workflow.

## Decision Anchors & Decision Pressure
None — content is fully specified by the launch order Pre-Rulings; no new durable structural decision.

## Claims / Evidence Surfaces
- Architecture claims (3-stage sampled runtime, 12 latent-power modules, Bradley-Terry, precision-weighted
  fusion) verified against source in PROBLEM_STATEMENT.md — each gate re-cites the same evidence, no re-derivation.

## Map Confidence / Staleness / Disputes
- `docs/architecture/packets/evo_predictor.md` `scorer.py` entry is stale (describes a 24-param function that no
  longer matches the file). Out of fence — floated as a triage candidate, not fixed here.
- The operator's personal MEMORY.md (outside the repo) carries the actual stale evo_predictor description that
  motivated this issue. Floated to the Admiral, not actioned here (outside fence, outside repo).

## Out of Scope
Any file other than `AGENTS.md`/`CLAUDE.md` (README.md, docs/AGENT_GUIDE.md, docs/architecture/packets/*, the
operator's MEMORY.md) — all deliberately untouched this wave.

## Plan-alternatives / cold-critic — named untaken roads
Both skipped as trivial: this run fills two fixed, launch-order-specified content blocks into existing lean
pointer files. There is no load-bearing interface, no design choice, and no alternative shape for "state the
mission" or "state the verified architecture facts" that would produce a meaningfully different candidate to
compare. Recorded here as the required named skip rather than silently omitted.
