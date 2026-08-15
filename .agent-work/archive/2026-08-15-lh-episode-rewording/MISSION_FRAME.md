# Mission Frame

## Intent
Trivial, local, mechanical change: shrunk per this template's own escape hatch and
`commander-core.md` ("Mission frame" — "The map is context, not authority over code, and
not a tax on trivial work"). No `docs/architecture` map exists in this repo (confirmed
DEGRADED-UNPARSEABLE by `map_orient.py` at the context step; README.md substituted,
hash-pinned in `.agent-work/lh-episode-rewording/map-orientation.json`), and the change
itself is bounded to three named `statement` fields inside three named episode files,
rewritten through the store's one write path (`scripts/apply_episode_delta.py
restate-assertion`). No source/behavior code changes. The map would add nothing here.

## Affected Capabilities
- `episodes/` store — three `agent-supplied` assertion statements restated (wording
  only; `restate-assertion` never touches kind/strength/lifecycle-standing).

## Structural Anchors
- `episodes/active/launcher-hygiene-001.md` (assertion a5)
- `episodes/active/launcher-hygiene-002.md` (assertion a3)
- `episodes/active/launcher-hygiene-003.md` (assertion a5)
- `scripts/apply_episode_delta.py` — read-only use as the store's write path (not
  modified)
- `scripts/verify_episode_observations.py` — read-only reference; the guard itself is
  out of scope (`tests/test_episode_observations.py` and its exception list are
  explicitly NOT ours per LAUNCH_ORDER "File Ownership")

## Governing Constraints / Assumptions
- LAUNCH_ORDER "The escape hatch you must NOT take" — no exception-list addition, no
  record deletion, no guard edit.
- LAUNCH_ORDER — preserve substance completely; do not shorten; 003's installed-vs-repo
  skills-root finding must survive intact.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` "The Retired Learning Playbook" — an episode is
  a record of what happened, never a rule; restating wording must not turn it into one.

## Decision Anchors & Decision Pressure
No durable decision anchors exist for this narrow a change; the one substantive call
this run makes is the 002.a3 (a)/(b) determination named in the launch order, which is
resolved directly against the guard's own regex in the `understand` step (finding: (a))
rather than through the map.

## Claims / Evidence Surfaces
- `python -m pytest -q tests/test_episode_observations.py` — must be green after the
  restatements (currently 2 failed per LAUNCH_ORDER).
- Full clean-env suite (`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m
  pytest -q`) — must show 0 failed other than the two named pre-existing Windows-only
  failures (this run is on Linux, so N/A here; expect 0 failed locally).

## Map Confidence / Staleness / Disputes
No map exists in this repo (skill-source repo, not a project with a Cartographer
packet map) — not a staleness/confidence issue, a structural absence, discharged as
DEGRADED-UNPARSEABLE at context per `map_orient.py`.

## Out of Scope
The guard (`scripts/verify_episode_observations.py`), its test file and exception list,
`scripts/run_crew.py`, `tests/test_spine_lifecycle.py`, `tests/test_mcp_identity.py`,
`skills/commander/references/crew-dispatch.md`, `scripts/checklist_engine.py`,
`scripts/hooks/spine_rail.py`, `.mcp.json` — all explicitly not ours per LAUNCH_ORDER
"File Ownership". The two Windows-only CI failures named in the launch order.
