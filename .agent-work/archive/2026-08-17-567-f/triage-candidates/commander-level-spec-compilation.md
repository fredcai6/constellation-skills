# Triage candidate: no Commander-level spec compilation into a spine

**Found in:** lane-f (#535, epic-567-door wave 2), during the measurement step.

**Observation.** `spine_open`'s `spec` parameter compiles `generate_spine.py`'s
`compile_spec` over a `specs/<role>.spine.toml` file. Only two such specs exist:
`specs/implementer.spine.toml` and `specs/reviewer.spine.toml` (confirming the LAUNCH_ORDER's
named Local Unknown #3) -- there is no `commander.spine.toml` or equivalent, and the schema
(`CHECK_KINDS = ("qualitative", "pytest", "script", "population", "artifact")`) has no field
for prose like Mission, Pre-Rulings, Inherited Latitude, or File Ownership -- it compiles
postcondition *checks*, not narrative context. Separately, a Commander's own `spine.json` is
stamped from `templates/COMMANDER_SPINE.template.json` -- a fixed, mission-independent
10-step workflow -- by the Admiral's `stand-up-work-area.md` step, never spec-compiled from a
launch order at all. The mission-specific content (everything a launch order carries beyond
the fixed step names) has no compiled-into-the-spine representation today; it travels only as
a pasted `--handoff` document, exactly as it did for this dispatch (both `--handoff` and
`--spine` were given to launch this session).

**Why it is not closeable inside `scripts/run_crew.py`.** The files that would need to change
-- a Commander-level spec schema, a compiler for it, and/or the `COMMANDER_SPINE.template.json`
itself -- live under `skills/**`, fenced to lane D1 this wave, and `scripts/mcp_spine_server.py`
/ `scripts/generate_spine.py`, fenced to lane E. This lane's file ownership is
`scripts/run_crew.py` only.

**What #535 would need to close this, if the human wants the fuller reading pursued.** A
Commander-level (or Admiral-launch-order-level) spec schema that can carry Mission/
Pre-Rulings/Latitude/File-Ownership fields, a compiler extending `generate_spine.py`'s pattern
to that schema, and a `stand-up-work-area.md` change to mint the Commander's spine from it
instead of the fixed template -- an architecture-level, multi-lane change.

**Disposition:** recommend-and-defer. Not filed as an issue this run (`decision:no-issue-filing-mid-run`).
