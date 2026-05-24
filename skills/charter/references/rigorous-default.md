# Rigorous Default

Charter starts here unless the user explicitly relaxes or strengthens by subsystem.

Default posture:

- correctness over velocity
- small composable units
- explicit contracts at meaningful boundaries
- one canonical path
- behavior changes are test-led where a test surface exists
- no relevant test surface means review/inspection evidence, not a TDD exception
- machine-checkable evidence when practical
- fail visibly rather than produce plausible wrong output
- no hidden fallback
- clear canonical input/data boundaries
- no speculative abstraction
- current context and architecture docs updated when their meaning changes
- compromises tracked with owner, reason, and exit condition when they affect future work

Cost of the default:

- slower starts
- more up-front test and evidence design
- fewer shortcuts through ambiguous boundaries
- more explicit stop/report behavior
- more documentation maintenance when meaning changes

Relaxation must name what gets faster, what risk increases, and where the relaxation applies.

Strengthening must name the extra proof, constraint, or enforcement mechanism.
