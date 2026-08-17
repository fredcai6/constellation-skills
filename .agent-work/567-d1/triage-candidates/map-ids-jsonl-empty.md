# map/ids.jsonl is empty, so map_orient can never RESOLVE in this repo

`map_orient.py orient` probes five candidates and all five miss: `docs/architecture/generated/map.json`,
`docs/architecture/index.md` and `docs/architecture/` are absent; `map/INDEX.md` has content but no
citable anchor id; `map/ids.jsonl` is an empty file. Verdict is always DEGRADED-UNPARSEABLE.

Every Commander in this repo therefore pays the degraded-discharge cost (substitutes, unmapped,
escalation) on every run, and no mission frame can ever cite a resolving anchor.

**Not acted on:** `map/INDEX.md` is Admiral-owned this wave (#544). Recorded so the Admiral can
decide whether the code map should emit citable anchor ids into `map/ids.jsonl`.
