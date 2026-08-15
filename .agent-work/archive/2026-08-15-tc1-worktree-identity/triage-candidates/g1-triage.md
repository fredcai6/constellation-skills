# Triage — tc1-worktree-identity / g1

Two candidates surfaced during g1 (implementer's Map Impact, confirmed real by the reviewer). Neither is
fixed-now (both are out of this run's File Ownership / scope) and neither is filed as an issue (this
LAUNCH_ORDER grants no explicit issue-filing authority — no "Inherited Latitude" section exists in it).
Both route **recommend-and-defer**.

## Candidate 1 — spine_rail.py lexical/git derivation split needs a durable home
**Statement:** `scripts/hooks/spine_rail.py::_worktree_from_spine` derives worktree ownership lexically;
`scripts/mcp_spine_server.py::_worktree_root_for_lifecycle` asks git. The 2026-08-15 worktree-identity
ruling rules this split deliberate (each has a real reason) but names it "a documentation deliverable,
not a code change" — and explicitly forbids touching `spine_rail.py` in this run (fenced: live #441
target).
**Disposition:** recommend-and-defer. Recommend a docstring/doc change landing once #441 is off
`spine_rail.py`, writing down the split the ruling already ratified. Not filed as an issue this run —
no issue-filing authority in this LAUNCH_ORDER.

## Candidate 2 — DC3InheritanceMechanismTests false-fails inside any crew-dispatched process
**Statement:** `test_mcp_identity.py::DC3InheritanceMechanismTests::test_launching_the_parent_never_touches_the_calling_processs_own_environ`
asserts `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` are absent from the calling process's own environment.
Any `run_crew.py`-dispatched crew carries all three by design, so this test fails inside every crew's own
full-suite gate — reproduced by both the implementer and reviewer on an *unchanged* HEAD tree with those
vars set vs unset, with zero relation to this run's diff.
**Disposition:** recommend-and-defer. Recommend an explicit skip-or-scrub for crew-run suites so a crew's
own full-suite gate stops tripping on its own dispatch envelope. Not filed as an issue this run.

## Non-candidate (noted, no action)
`_git()` raises `FileNotFoundError` if the `git` binary itself is absent — pre-existing behavior of the
shared helper everywhere it's used; git is a hard dependency of this repo's tooling; out of this ruling's
"no toplevel resolvable" scope. No disposition needed.
