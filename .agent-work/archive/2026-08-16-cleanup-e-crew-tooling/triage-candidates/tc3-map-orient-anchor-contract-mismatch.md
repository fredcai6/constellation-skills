# Triage Recommendation: `map_orient.py`'s anchor contract never matches this repo's own generated map

## Classification
`tooling`

## Source checklist/artifact
- `execute.json` `triage_candidates[2]`; `.agent-work/cleanup-e-crew-tooling/map-orientation.json` (this run's own DEGRADED-UNPARSEABLE receipt).

## Structural anchor
`none` (the mismatch is between two tools, not a structural node in either)

## Cartographer mismatch class
none

## Observations

### Observation 1
- **What's wrong:** `map_orient.py`'s `orient`/`verify-orientation` verbs (`/home/tommy/.claude/skills/constellation-commander/scripts/map_orient.py`) look for citable anchor ids matching `\b(?:struct|capability|event|constraint|assumption|claim|decision):[A-Za-z0-9_.\-]+\b` inside `docs/architecture/` packets or this repo's own `map/INDEX.md`/`map/ids.jsonl`. This repo's own generated map (`map/INDEX.md`, produced by `scripts/code_map`) is a module/entity-count index with no anchor-id syntax at all, and `map/ids.jsonl` is structurally empty (0 lines) even immediately after a fresh `py -m scripts.code_map build`. Every commander run against this repo therefore reads `DEGRADED-UNPARSEABLE` at the context step's map-orientation check, regardless of whether the map is actually stale or current.
- **Expected:** a commander run against a repo whose own generated map is fresh and accurate should read `RESOLVED`, or at minimum a degraded mode that reflects genuine staleness rather than a permanent format mismatch.
- **Conditions:** any commander/delegated-commander run against `constellation-skills` itself (a skill-source repo whose own `map/` is code-derived, not docs/architecture-packet-derived). Reproduced this run: `py map_orient.py orient --root . --work-id cleanup-e-crew-tooling` → `DEGRADED-UNPARSEABLE`, `anchor_count: 0`, even after `map/INDEX.md` was freshly regenerated and committed.
- **Type:** `measured` — ran `map_orient.py orient` and `verify-orientation` directly against this repo at the context step of this run, and again conceptually re-derivable via `map/ids.jsonl`'s line count (`wc -l map/ids.jsonl` → 0) and `map/INDEX.md`'s content shape (module+entity-count prose, no `struct:`/`decision:`/etc. tokens).
- **Rev:** `cleanup/e-crew-tooling` at base `e36e630b`, and separately confirmed unrelated to this run's own changes (the same mismatch would occur on unmodified `main`, since it is a property of `map/`'s generation format, not this run's diff).

## Possible fix
Either (a) teach `map_orient.py` a second, code-map-aware citation format (module/qualified-symbol names as citable "anchors" when the map is a `scripts.code_map`-style index rather than a `docs/architecture` packet map), or (b) accept this repo's own generated map is structurally out of `map_orient.py`'s scope and document the expected `DEGRADED` reading as normal-and-discharged for this repo specifically (e.g. a `docs/agents/` note naming the substitute path every run should declare) rather than leaving each run to rediscover and re-argue the same discharge.

## Open questions
- Is `map_orient.py`'s anchor-id contract intentionally scoped to `docs/architecture`-packet repos only, with code-derived maps like this repo's `map/` meant to stay permanently `DEGRADED` by design? Or is the code-map format meant to eventually gain anchor ids (`map/ids.jsonl` existing as a field at all suggests intent, but it is unpopulated)?

## Recommended priority
`medium`

**Reason:** Not a correctness defect in this run's own work (discharged cleanly via the documented substitute path each time), but a recurring tax on every future commander/delegated-commander run against this repo — each one re-derives and re-records the same discharge from scratch.

## Related artifacts
- `.agent-work/cleanup-e-crew-tooling/map-orientation.json`
- `/home/tommy/.claude/skills/constellation-commander/scripts/map_orient.py`

## Disposition
`recommend-and-defer`

**Detail:** `map_orient.py` is installed constellation-commander skill tooling, not an owned file of this run (`scripts/run_crew.py`/`recover_crews.py`/tests only), and its fix would affect every repo using the commander skill, not just this one — well outside this delegated run's latitude to decide or file alone.

## Issue creation authority
`ask user`
