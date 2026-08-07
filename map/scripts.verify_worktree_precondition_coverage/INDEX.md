# scripts.verify_worktree_precondition_coverage
scripts/verify_worktree_precondition_coverage.py, 144 lines, 3 holes

Verify every worktree-entering role's spine wires the worktree-isolation gate.

The prose invariant ("a Commander's first step is to verify it is running in
its provisioned worktree") is only real once it is a command precondition on
the role's spine, not a sentence a human or agent can silently skip (#329).
This script is the enumeration side of that fix: it fails when a
worktree-entering template does NOT carry the wired precondition, catching
a template that was simply left out when the invariant was wired (the #392
shape this issue exists to prevent).

WORKTREE_ENTERING_GATES below is an explicit, hand-maintained list, not an
auto-detector, and that is deliberate. Which roles actually get dispatched
into an isolated worktree is an architectural fact about the fleet -- it is
decided by who provisions worktrees and who gets launched into one via an
Admiral LAUNCH_ORDER -- and that fact is not recoverable by scanning a
spine's JSON content:

  - Admiral provisions a real worktree per Commander (`git worktree add`)
    but does not itself enter one -- Admiral stays in the primary checkout,
    so ADMIRAL_SPINE.template.json carries no such precondition and never
    should.
  - Commander is the one role actually dispatched INTO an isolated worktree
    -- COMMANDER_SPINE.template.json's `init` gate is the one entry today.
  - Explorer is human-synchronous / upstream-only and is never delegated
    into a worktree -- EXPLORER_SPINE.template.json carries no such
    precondition either.
  - Crew (Implementer/Reviewer/Prototyper) run inside the Commander's
    already-isolated worktree; they do not provision or enter a new one of
    their own, so they have no c0-equivalent precondition to carry.

Adding a new worktree-entering role means adding its (template, gate) pair
to this list BY HAND. That is a known, accepted limit -- not something this
script silently covers by inference -- see issue #422/#329.

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, sys
imported by: none found

```python
WORKTREE_ENTERING_GATES: tuple[tuple[str, str], ...] = (('skills/commander/templates/COMMANDER_SPINE.template.json', 'init'),)
ISOLATION_SCRIPT_MARKER = 'verify_worktree_isolation.py'
```

- [_utf8_stdio](_utf8_stdio.md) function: HOLE: no docstring
- [CoverageError](CoverageError.md) class: Raised when a worktree-entering template is missing the wired precondition.
- [_condition_wires_isolation](_condition_wires_isolation.md) function: True if `cond` is a command check that runs verify_worktree_isolation.py
- [_gate_wires_isolation](_gate_wires_isolation.md) function: HOLE: no docstring
- [verify_coverage](verify_coverage.md) function: Check every listed (template, gate) pair. Returns the count checked on
- [main](main.md) function: HOLE: no docstring
