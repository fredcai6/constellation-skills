# Triage Recommendation: `evo_predictor.md packet's scorer.py entry is stale`

## Classification
`stale generated map`

## Source checklist/artifact
- execute.json triage_candidates tc1 (flagged during cmdr-602 g2-claude source verification, 2026-07-12)

## Structural anchor
`docs/architecture/packets/evo_predictor.md` (packet prose, `scorer.py` module entry, lines ~122-123)

## Cartographer mismatch class
Packet-description drift (module content changed, packet prose not updated) — a content-drift class the mechanical `check_arch_map.py` checker does not test for (per `[Cartographer audit gaps]` project memory: green check is blind to content drift).

## Problem
The evo_predictor packet describes `src/evo_predictor/scorer.py` as: "Scores drivers given features and the 24-parameter vector. Used in legacy path." This no longer matches the file's actual current content.

## Current truth
`src/evo_predictor/scorer.py`'s current content (verified 2026-07-12) is small, unrelated helpers: `_circuit_distance` (weighted Euclidean distance between `CircuitProfile`s) and `_compound_distance` (mean absolute compound delta). It does not implement `score_drivers(features, params, form_drop_worst=2)` or reference the 24-parameter vector at all. `src/evo_predictor/ranker.py` does not exist in the repo.

## Desired/future concern
Update the packet's `scorer.py` entry to describe its actual current content and purpose (who calls `_circuit_distance`/`_compound_distance` and why), or remove the entry if the functions are dead code — a quick grep for callers would settle which.

## Evidence
- `src/evo_predictor/scorer.py` (read in full during cmdr-602 g2-claude, 2026-07-12) — content is `_circuit_distance`/`_compound_distance`, no 24-param scorer.
- `docs/architecture/packets/evo_predictor.md` lines 122-123 — the stale description.
- `find src/evo_predictor -iname "ranker*"` — no match; `ranker.py` does not exist.

## Impact
Agents reading the packet for evo_predictor orientation get a false picture of `scorer.py`'s role, risking wasted investigation or incorrect assumptions about the legacy scoring path's survival.

## Suggested scope
Cartographer (or a small reasoning-gate commander) reads current `scorer.py`, greps its callers, and rewrites the packet entry to match — or removes it if dead code. Single-file docs edit, no code change expected.

## Non-goals
Do not delete or refactor `scorer.py` itself as part of this fix unless the caller-grep shows it's genuinely dead code and a separate cleanup decision is made.

## Acceptance criteria
- [ ] `docs/architecture/packets/evo_predictor.md`'s `scorer.py` entry matches the file's actual current content
- [ ] Caller-grep result recorded (live code path vs. dead code) so the entry states usage accurately

## Recommended priority
`low`

**Reason:** Docs-only drift with no runtime/prediction impact; worth fixing on the next Cartographer reconcile pass rather than urgently.

## Related artifacts
- `docs/architecture/packets/evo_predictor.md`
- `src/evo_predictor/scorer.py`
- `.agent-work/cmdr-602/PROBLEM_STATEMENT.md` (full verification trail)

## Disposition
`recommend-and-defer`

**Detail:** cmdr-602's file-ownership fence this wave is `AGENTS.md` + `CLAUDE.md` only (launch order); editing `docs/architecture/packets/evo_predictor.md` is outside that fence. Filing authority for a new low-priority cleanup issue is not explicitly granted by the launch order's Inherited Latitude section, so this is recorded for the Admiral to route (file as an issue, or fold into the next Cartographer reconcile) rather than filed directly this run.

## Issue creation authority
`ask user` (routed via Admiral)
