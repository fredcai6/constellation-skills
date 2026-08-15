# Mission Frame

## Intent

Make external Codex crew routing able to read persisted optional model metadata
and optional reasoning effort, without changing the Claude launch contract.

## Affected Capabilities

- No citable map capability exists for `scripts/run_crew.py`; the bounded
  launcher registry and external record-only backend are the substituted frame.

## Structural Anchors

- `scripts/run_crew.py` — `CrewSpec`, registry entry construction, backend
  dispatch, resume/relaunch, and CLI parser.
- `tests/test_crew_launcher.py` — focused behavioral coverage.

## Governing Constraints / Assumptions

- `LAUNCH_ORDER:Pre-rulings` — metadata-only, no external process launcher.
- `LAUNCH_ORDER:Pre-rulings` — Claude argv and defaults remain unchanged.
- `LAUNCH_ORDER:Pre-rulings` — legacy registry entries use optional lookup.

## Decision Anchors & Decision Pressure

- decision:metadata-only — persist optional reasoning effort only.
  @grade: settled/human · leans g1-implement
- decision:claude-argv — never add a reasoning effort flag to Claude argv.
  @grade: settled/human · leans g1-implement
- decision:legacy-registry — absent legacy metadata remains readable.
  @grade: settled/human · leans g1-implement

## Claims / Evidence Surfaces

- Focused unit tests prove external registry persistence, resume compatibility,
  relaunch threading, and unchanged Claude argv.

## Map Confidence / Staleness / Disputes

- The map is degraded and has no citable anchor for this launcher; the README
  substitute and frozen launch order are recorded in `map-orientation.json`.

## Out of Scope

- External process launching, migrations, defaults, engine/hook/lifecycle work,
  and files outside the launch-order ownership boundary.
