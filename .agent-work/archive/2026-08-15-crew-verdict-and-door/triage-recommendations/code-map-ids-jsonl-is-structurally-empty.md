# Triage Recommendation: `map/ids.jsonl is structurally empty repo-wide`

## Classification
`stale generated map` / `tooling`

## Source checklist/artifact
- This commander's context-step map orientation (`.agent-work/crew-verdict-and-door/map-orientation.json`).

## Structural anchor
`map/ids.jsonl`, `scripts/code_map/` (the generator)

## Cartographer mismatch class
None — this is the code-map tool's own output, not a Cartographer packet.

## Observations
### Observation 1
- **What's wrong:** `map/ids.jsonl` is empty (0 lines), and `map_orient.py orient` reads this repo as `DEGRADED-UNPARSEABLE` for every run — not specific to this issue's area.
- **Expected:** Either `ids.jsonl` should carry populated anchor ids after a build (if population was ever intended), or `map_orient.py`'s degraded-verdict machinery should not treat an intentionally-anchor-free code map as "unparseable" the same way it treats a genuinely broken one.
- **Conditions:** Any `map_orient.py orient`/`verify-orientation` run against this repo's current `HEAD`.
- **Type:** `measured` — ran `python -m scripts.code_map build --root .` fresh; its own JSON summary reports `"ids": 0`. Ran `python scripts/map_orient.py orient ...`; verdict `DEGRADED-UNPARSEABLE`.
- **Rev:** `453f8492` and unchanged through this run's own `35f6c663` (map/INDEX.md moved with the code diff; `ids.jsonl` stayed empty both before and after).

## Desired behavior
N/A — filed as a defect/tooling gap, not an enhancement request; the "desired" state depends on which of the two readings in Open Questions is correct.

## Open questions
- Was `map/ids.jsonl` population ever implemented in `scripts/code_map`, or is an anchor-id-free structural map an intentional, accepted shape for this repo (which carries no `docs/architecture/` packet overlay at all)? This run could not settle it from the `code_map` CLI's own output alone.

## Recommended priority
`medium`

**Reason:** Every run in this repo currently orients `DEGRADED-UNPARSEABLE`, which is tolerable (this run discharged it via declared substitutes) but means map-first orientation never actually resolves here — worth a deliberate ruling either way rather than every future run rediscovering and re-escalating the same gap.

## Related artifacts
- `.agent-work/crew-verdict-and-door/map-orientation.json`
- `.agent-work/crew-verdict-and-door/REPLAN_INPUT.json` (`D-map-ids-zero`, `uncertainty_register`)

## Disposition
`recommend-and-defer`

**Detail:** `recommend-and-defer: this run's launch order grants no tracker-filing authority, and the code-map generator (scripts/code_map/) is outside the file-ownership fence (scripts/run_crew.py + tests only).`

## Issue creation authority
`issue-ready only`
