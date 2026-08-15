# Triage Recommendation: `full test suite false-fails when run inside a spine-bound shell`

## Classification
`bug`

## Source checklist/artifact
- This commander's own execute-gate closeout (`.agent-work/crew-verdict-and-door/execute.json` g1-integrate/g2-integrate; amendment record on the checklist itself).

## Structural anchor
`tests/test_mcp_identity.py:600` (`DC3InheritanceMechanismTests::test_launching_the_parent_never_touches_the_calling_processs_own_environ`)

## Cartographer mismatch class
None.

## Observations
### Observation 1
- **What's wrong:** `test_launching_the_parent_never_touches_the_calling_processs_own_environ` asserts `SPINE_FILE`/`SPINE_SESSION`/etc. are absent from `os.environ` at test time. When the test process is itself a spine-bound crew (dispatched via `run_crew.py --backend cli --spine ...`, which binds those vars into the child's real shell environment before Claude Code even starts), the assertion fails for a reason the test does not intend to check: the vars were already present before the test — or anything under test — ran at all.
- **Expected:** The test should verify a property of `run_crew.py`'s own subprocess-launch behavior (does launching a child mutate the launcher's `os.environ`), independent of whatever the launcher's own ambient environment happens to carry from ITS OWN dispatch.
- **Conditions:** Running `python -m pytest` (whole suite or this test alone) from inside a shell that itself has `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` set — i.e., any Commander or crew currently mid-dispatch via the `cli` backend with `--spine`. Reproduced by running the single test with and without `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`: fails as-is, passes stripped.
- **Type:** `measured` — ran `python -m pytest -q tests/test_mcp_identity.py::DC3InheritanceMechanismTests::test_launching_the_parent_never_touches_the_calling_processs_own_environ` both ways in this session's own shell.
- **Rev:** `f06d314e` (this run's g1 commit; unrelated to the diff — the test's pass/fail depends only on the calling shell's ambient environment, not on any code in this diff).

## Desired behavior
N/A — this is a defect (a check that fails for reasons unrelated to what it verifies, in a real and now-common environment: a Commander driving its own bound spine), not an enhancement.

## Possible fix
The test could `del`/patch `os.environ` for the three `SPINE_*` keys at its own start (save and restore), so it verifies the launch behavior in isolation from whatever the test RUNNER's own environment carries. This is a self-contained fix inside `tests/test_mcp_identity.py`, which this run did not touch (outside `crew-verdict-and-door`'s file-ownership fence: `scripts/run_crew.py` + tests it authored, not every test file).

## Open questions
- Is this a known, accepted characteristic of running the suite from inside a dispatched crew's shell (i.e., "always strip these vars before running the full suite" is meant to be tribal knowledge), or a genuine test-isolation gap worth fixing at the test level? This run worked around it locally (amended `execute.json`'s own suite-check commands to strip the three vars via the engine's `retext-check` verb) rather than deciding this question.

## Recommended priority
`medium`

**Reason:** Any Commander or crew that runs the full suite from inside its own `--spine`-bound dispatch (which is exactly what the doctrine recommends: verify the door, then work) hits a false failure that costs a diagnostic detour to attribute — this run spent real effort distinguishing it from a genuine regression.

## Related artifacts
- `.agent-work/crew-verdict-and-door/execute.json` (amendment: `retext-check g1-integrate.c1`, `retext-check g2-integrate.c1`)
- `.agent-work/crew-verdict-and-door/REPLAN_INPUT.json` (`D-spine-bound-shell-false-failure`)

## Disposition
`recommend-and-defer`

**Detail:** `recommend-and-defer: this run's launch order grants no tracker-filing authority, and tests/test_mcp_identity.py is outside the file-ownership fence (scripts/run_crew.py + the tests this run itself authored). Worked around locally via an engine amendment to this run's own suite-check commands, not fixed at the source.`

## Issue creation authority
`issue-ready only`
