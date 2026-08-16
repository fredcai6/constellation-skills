# Problem statement — lane F, #609 (absorbing #315)

Reconciled against the frozen `LAUNCH_ORDER.md` (delegated mode; no reachable
human). Sources: the launch order, issue #609 including its 2026-08-16
refinement, and the code as it stands at `e36e630b`.

## The ask, in one line

A spine's worktree is **derived from its path**. Nothing stamps it for a
decision, nothing compares it, nothing reads an ambient cwd to find it.

## Protected intent

- Derivation is **lexical**: nearest `.agent-work` ancestor, take its parent.
  Arbitrary depth. No `.agent-work` ancestor at all means **unowned** — refuse,
  never guess a root.
- The derived worktree is **location** (cwd for checks, where git runs), never
  **ownership**. Ownership is the lease; among spines sharing a tree the
  discriminator is binding-key provenance (#549).
- `origin.worktree` keeps being **written** as provenance and is **read by
  nothing for a decision**.
- Removing the origin comparison does not remove a guard — the lease was
  always the guard.

## Baseline reconciled against the code (order's assumptions vs. reality)

| Order says | Verified in tree at `e36e630b` |
|---|---|
| `origin_worktree_refusal` compares stamp against ambient cwd | Yes — `scripts/checklist_engine.py:102-179`, pure predicate; equality since #588 |
| A `git rev-parse --show-toplevel` per guarded verb in `main()` | Yes — `scripts/checklist_engine.py:3573-3578`, before `dispatch()` |
| `_check_condition` has `base_dir` and drops it | Yes — `:898` has it, `:927` calls `_run_check_command(chk["command"])`, which runs `subprocess.run` with no `cwd=` (`:883`) |
| `_worktree_from_spine` is lexical but too narrow | Yes — `scripts/hooks/spine_rail.py:712`; requires exactly `.agent-work/<id>/<name>.json`, returns `None` for anything deeper |
| `_foreign_worktree` is an ownership test | Yes — `scripts/hooks/spine_rail.py:693` (order cites `:639`; **actual line is 693** — drift, noted). Call sites: `_entry_mid_flight_view` (`:1411`) and `decide_session_start` (`:1546`) |
| `verify_worktree_isolation` ships in no template/spec | Confirmed: zero occurrences outside `scripts/`, its own tests, `tests/test_worktree_precondition_wiring.py`, and doc prose |
| `spine_rail.py` imports stdlib only | Confirmed — `errno json os re shlex subprocess sys tempfile time datetime pathlib` plus optional `msvcrt`. **Zero** cross-module imports, and **no** `SCRIPT_RUNTIME_COMPANIONS` entry of its own |

## What ships

1. One derivation function — pure, lexical, arbitrary depth, nearest
   `.agent-work` ancestor; unowned when there is none.
2. `origin_worktree_refusal` stops comparing; what remains is a shape question
   answered without git and without cwd.
3. The per-guarded-verb `git rev-parse --show-toplevel` in `main()` goes away.
4. #315: command-kind checks run with `cwd=` the derived worktree.
5. `_foreign_worktree` stops being an ownership test; binding-key provenance
   (#549) is the discriminator.

Plus a test pinning that **nothing reads `origin.worktree` for a decision**
while it continues to be written.

## The one genuine gap — floated to the Admiral

`tests/test_worktree_precondition_wiring.py::IsolationGateSurvivesThroughTheCLI`
and deliverable 4 are, as far as I can see from the code, mutually exclusive.
That test builds a spine at `<worktree>/.agent-work/w1/spine.json` whose `init`
precondition is `verify_worktree_isolation.py --here <worktree>`, launches
`main()` from the **main checkout**, and asserts the gate REFUSES. Deliverable 4
runs that command check with `cwd` = the worktree derived from the spine path =
`<worktree>`, so `git rev-parse --show-toplevel` returns `<worktree>` and the
comparison becomes `EXPECTED == EXPECTED`. The gate passes and the assertion
fails.

This is structural, not incidental: **any** cwd forced to a location inside the
worktree disarms a check whose subject *is* the ambient cwd. The fixture's own
docstring anticipates it and sanctions a fixture update ("teach it the new form
and keep both sides asserted"), but names an invariant — "a launcher standing in
the wrong worktree is still refused" — that #609 deliberately retires, since the
launcher's location stops being consulted at all.

The launch order reserves this to the Admiral in two places, so it is floated
rather than decided here. The run is sequenced so this gap blocks only the #315
gate; derivation and the retirement land first and leave the test green.

## Out of scope (fenced)

`scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
`scripts/install_constellation.py`, `skills/commander/templates/**` (lane A);
`scripts/run_crew.py`, `scripts/recover_crews.py`, `tests/test_crew_launcher.py`
(lane E); `scripts/verify_worktree_isolation.py` (#610). `run_crew.py`'s own
worktree computation is a real cleanup and is **not** this wave's.
