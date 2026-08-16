# Triage Recommendation: corpus carries zero authored map anchors, forcing every run into DEGRADED orientation

## Classification
missing structural node

## Source checklist/artifact
- execute.json triage_candidates tc1 (flagged from g1-implement)
- `.agent-work/cleanup-c-liveness-rail/map-orientation.json`

## Structural anchor
`map/ids.jsonl` (repo-relative path; no node id exists to cite — that is the finding)

## Cartographer mismatch class
none — no Cartographer run this lane; found via `map_orient.py orient` returning DEGRADED-UNPARSEABLE

## Observations

### Observation 1
- **What's wrong:** `map/ids.jsonl` is an empty tracked file at baseline; `map_orient.py orient` cannot resolve any entrypoint (`docs/architecture/generated/map.json`, `docs/architecture/index.md`, `docs/architecture` all absent; `map/INDEX.md` has content but zero citable anchor ids; `map/ids.jsonl` is empty) and returns `DEGRADED-UNPARSEABLE` with `anchor_count: 0`.
- **Expected:** at least some portion of the corpus carries authored anchor tags (`decision:`/`capability:`/`struct:`/etc.) so map-first orientation can RESOLVE for at least the most-touched areas (e.g. `scripts/run_crew.py`, `scripts/hooks/spine_rail.py`, `scripts/checklist_engine.py`).
- **Conditions:** any run against this repo at baseline `a69bbac4`; reproduced on a fresh rebuild (`python -m scripts.code_map build --root .` produces byte-identical `map/ids.jsonl`, confirming this is not a stale-map issue but a genuine zero-anchors state).
- **Type:** `measured` — ran `map_orient.py orient --root <worktree> --work-id cleanup-c-liveness-rail`, got `DEGRADED-UNPARSEABLE`, `anchor_count: 0`; independently ran `python -m scripts.code_map build --root .` and diffed `map/ids.jsonl` before/after (byte-identical, `ids: 0` in the build report).
- **Rev:** `a69bbac4` (this lane's dispatch baseline); still true at this lane's head, `590bf44d`.

## Possible fix
Author a first batch of anchor tags on the highest-traffic modules this epic's lanes are actively touching (`run_crew.py`, `spine_rail.py`, `checklist_engine.py`) so at least those areas RESOLVE instead of every run falling back to DEGRADED. This is a corpus-wide authoring effort, not a mechanical fix — someone has to decide what counts as a `decision:`/`capability:` anchor for each area.

## Open questions
- Is DEGRADED-by-default an accepted steady state for this repo (map-first doctrine substituted by file:line citations in launch orders), or is anchor authoring simply not yet started? The `map_orient.py` tool's own docstrings suggest anchors are an intentional, not-yet-populated mechanism.

## Recommended priority
low

**Reason:** every lane in this epic has successfully substituted file:line citations for map anchors without being blocked; this is a quality-of-life / tooling-completeness gap, not a correctness blocker.

## Related artifacts
- `.agent-work/cleanup-c-liveness-rail/MISSION_FRAME.md` (this lane's DEGRADED discharge)
- `.agent-work/cleanup-c-liveness-rail/map-orientation.json`

## Disposition
`recommend-and-defer`

**Detail:** filing authority is unclear this run — the launch order's Inherited Latitude does not name issue-filing among this lane's decisions, and this finding is corpus-wide, not scoped to this lane's two owned files.

## Issue creation authority
`issue-ready only`
