# Plan candidate — constraint: push the clear into the primitive

Constraint: express "clear" as a first-class capability of `crew_env` itself (a sentinel
value, e.g. a module-level `CLEAR` marker, or a boolean `clear_spine=True` kwarg), so any
future direct caller of `crew_env` gets the same safety, not just `_crew_door_env`.

## Gate plan

- **g1** (crew gate): implement + review
  - Add a `clear_spine: bool = False` kwarg to `crew_env`. When true, `env.pop("SPINE_FILE",
    None)` and `env.pop("SPINE_SESSION", None)` unconditionally (mutually exclusive with
    passing `spine_file`/`spine_session`; raise if both given).
  - `_crew_door_env`'s `spine is None` branch calls
    `crew_env(parent=resolved_parent, scratch_dir=scratch_dir, clear_spine=True)`.
  - Update both docstrings (as in the minimal-diff candidate) plus `crew_env`'s own
    docstring/signature doc for the new kwarg.
  - Flip the same test as the minimal-diff candidate, plus add direct `crew_env`-level
    unit tests for `clear_spine=True` (mirroring `CrewEnvSpineBindingTests`).
  - Same suite run before closing the gate.

## Tradeoffs

- + Generalizes the safety to any future direct `crew_env` caller, not just the one
  wrapper that exists today.
- + Makes "clear" a nameable, testable unit at the lowest layer, symmetric with
  "assign" and "leave untouched."
- - Larger diff and a new parameter/contract on a function the mission does not name
    (mission says "in `_crew_door_env`, make...") — grows `crew_env`'s public surface for
    a caller that does not exist yet (the mission's Inherited Latitude floats "any change
    to what `--spine` itself means" to the Admiral, and while this is not that, expanding
    `crew_env`'s contract is more than "how the clear is expressed" strictly requires).
  - Two ways to reach the same env dict shape (explicit pop in the wrapper vs. a kwarg on
    the primitive) is marginal duplication of concept for a function with exactly one
    caller today — speculative generality the mission's minimal-diff framing argues
    against ("YAGNI": no second caller exists to justify the primitive-level feature yet).
