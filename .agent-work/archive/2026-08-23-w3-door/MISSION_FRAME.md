# Mission Frame

## Intent

Shrunk per the template's own escape hatch: this is a trivial, local, mechanical change —
one function (`_crew_door_env` in `scripts/run_crew.py`), fully named by the launch order,
with the design decision already pre-ruled by the Admiral ("clear both together, never
one alone" — settled, LAUNCH_ORDER Pre-Rulings). The architecture map adds nothing here:
`map/ids.jsonl` is empty and
`map/INDEX.md`'s per-package sub-indexes do not exist on disk (DEGRADED-UNPARSEABLE per
`.agent-work/w3-door/map-orientation.json`), so no citable anchor exists for this symbol
regardless of effort spent. The rest of this frame's sections are omitted; c6 (map_orient
verify-frame) is waived below for the same reason, and c1 is attested skipped-as-trivial.

## Out of Scope

Everything except `scripts/run_crew.py` and its own tests — per the launch order's File
Ownership, this file is this lane's alone this wave; three sibling lanes run concurrently
against other files. No change to `--spine`'s meaning, `SPINE_PARENT`, `CREW_SCRATCH_DIR`,
or the registry schema (all named in the launch order as floating to the Admiral).
