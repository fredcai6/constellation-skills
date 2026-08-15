# Triage Recommendation: `map/INDEX.md links to per-module pages that do not exist on disk`

## Classification
`stale generated map`

## Source checklist/artifact
- This run's `context` step (`map_orient.py orient` -> `DEGRADED-UNPARSEABLE`) and `MISSION_FRAME.md`'s
  Map Confidence section.

## Structural anchor
`map/INDEX.md`

## Cartographer mismatch class
None — no `docs/architecture` packet map exists in this repo; this is the derived code map
(`scripts/code_map`), not a Cartographer packet.

## Observations

### Observation 1
- **What's wrong:** `map/INDEX.md` links to per-module pages (e.g.
  `scripts.hooks.spine_rail/INDEX.md`, `tests.test_spine_rail/INDEX.md`) that do not exist anywhere under
  `map/` — `map/` contains only `INDEX.md` and `ids.jsonl` at its root, no per-module subdirectories.
- **Expected:** each linked per-module page exists and carries citable per-entity anchor ids, so
  `map_orient.py orient` resolves `RESOLVED` for this area instead of `DEGRADED-UNPARSEABLE`.
- **Conditions:** reproduced against the whole `map/INDEX.md` file, not just the `scripts.hooks.*`/
  `tests.test_spine_rail` area this run touched — `find map -maxdepth 1 -type d` returns only `map`
  itself, zero subdirectories, for the entire repo.
- **Type:** `measured` — ran `python scripts/map_orient.py orient --root <worktree> --work-id
  stop-hook-door-binding`, got `DEGRADED-UNPARSEABLE`, candidate `[4] code-map-index: map/INDEX.md ->
  unparseable (content but no citable anchor id (unfilled template?))`; independently confirmed
  `find map -maxdepth 1 -type d` returns one entry (`map` itself).
- **Rev:** as observed 2026-08-15, worktree `stop-hook-door-binding`, branch base `main` at `2c46cab8`.

## Recommended priority
`medium`

**Reason:** this is the second run in one day to hit and independently confirm the same gap (this run's
own `context` step, plus every prior Commander run in this repo that has read a DEGRADED map this way) —
it silently degrades every future run's map-first planning to source-read, which the doctrine tolerates
but does not prefer.

## Related artifacts
- `.agent-work/stop-hook-door-binding/map-orientation.json`
- `.agent-work/stop-hook-door-binding/MISSION_FRAME.md`

## Disposition
`recommend-and-defer`

**Detail:** `recommend-and-defer: fixing scripts/code_map's generator (or map/INDEX.md's own content) is
outside this run's File Ownership fence (scripts/hooks/spine_rail.py, tests/test_spine_rail.py, the
PostToolUse block of .claude/settings.json only) and outside this run's bounded appetite (one gate). No
tracker-filing authority exercised.`

## Issue creation authority
`issue-ready only`
