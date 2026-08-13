# Plan alternatives — engine-native worktree isolation

Design-it-twice, run before the plan froze. Two candidates authored in parallel by cold
Plan agents under **distinct named constraints**, each given the same ruled direction and
the same four hard constraints (engine-native never a forwarded cwd; root distinct from
`base_dir`; zero changes to `spine_lifecycle.py`; `spine_rail.py`/`agent_work_root.py`
not editable).

Both agents ran read-only with no write tools, so they returned their candidates as text
and this file is the record of what they returned. Neither agent saw the other's work.

- **Candidate A — "minimum blast radius"**: fewest changed lines, fewest new call sites.
- **Candidate B — "maximum falsifiability"**: every part of the new behaviour provable to
  refuse with fabricated inputs — no git repo, no worktree, no subprocess.

---

## Candidate A — minimum blast radius

**Shape.** One helper `_refuse_outside_origin_worktree(cl, cwd=None)` placed directly above
`dispatch()`, raising `EngineError`. One call site: the first statement of `dispatch()`'s
`else:` branch (`checklist_engine.py:3091`), above `require_session`. No signature changes
anywhere. `cwd` is a defaulted test seam; the single production call passes nothing.

**Verb scope.** Exactly the `else:` branch — every verb in `MUTATING_VERBS`. `claim` is
**not** guarded (it has its own `elif` at 3088), nor are `current`/`heartbeat`/`release`.
Rationale offered: a wrong-tree agent is refused at its first `start` anyway, before any
state mutation, and leaving `release` open keeps a misplaced session recoverable without
`--force`.

**Stamp.** `{work_id, worktree: Path(root).resolve().as_posix(), opened_by:
"init_work_area"}`, injected with `setdefault` between the existing `json.loads` guard and
`dest.write_text`. Refuses to guess `branch`/`base`/`parent`/`opened_at`.

**Path semantics.** Inside-the-root via `Path.resolve()` + `is_relative_to`, not
equal-to-root — because the check being replaced compares `git rev-parse --show-toplevel`,
which succeeds from any subdirectory. Equal-to-root would be a behaviour regression
smuggled in under a mechanism change.

**Costs it names against itself.** `claim` unguarded; the `cwd` test seam is "a foot-gun" a
future caller could use to re-create the `X == X` disarming; `instantiate_spine` stops
being a byte-preserving writer; nothing verifies the stamped root is really a worktree.

---

## Candidate B — maximum falsifiability

**Shape.** A **pure** function
`origin_worktree_refusal(spine: dict, *, cwd: str, verb: str) -> str | None` —
refusal-or-None, matching this repo's existing precedent `spine_lifecycle.closeout_refusal`.
No filesystem, no clock, no subprocess. The impure caller is three lines at the very top of
`dispatch()`, before the `heartbeat`/`release`/`current` early returns:

```python
reason = origin_worktree_refusal(cl, cwd=str(Path.cwd().resolve()), verb=v)
if reason:
    raise EngineError(reason)
```

Placing it above the early returns makes the verb exemption **a data fact inside the pure
function**, exercised in production by every verb — so a unit test driving `verb="current"`
proves the production exemption instead of a dead branch.

**Verb scope.** `WORKTREE_GUARDED_VERBS = MUTATING_VERBS | {"claim"}`. `claim` is guarded
because it writes the lease and taking ownership from the wrong tree *is* the defect.
`current`/`heartbeat`/`release` are exempt on two measured grounds: `mcp_spine_server.py`
drives `checklist_engine.main()` in-process and never chdirs, and orchestrator doctrine has
an invoker read a subordinate's `current` cross-tree for `REFRESH REQUESTED:`. Reading state
from elsewhere is supported; doing work elsewhere is not.

**Stamp.** Same three keys as A, via a pure `stamp_origin(root, work_id)` helper. Same
refusal to guess the other four, with the added argument that omission keeps the whole stamp
a pure function of `(root, work_id)` that a test can assert by exact dict equality.

**Path semantics.** Inside-the-root, **segment-wise**, never `str.startswith` — `/w/repo-2`
is not inside `/w/repo`. Symlink resolution deliberately stays *outside* the pure function
(stored side resolved at write time, cwd side at read time); case-folding stays *inside* via
`os.path.normcase`, which is pure.

**Falsification set.** Eleven named tests, each pinning a refuse-case/pass-case pair in the
same test. The load-bearing ones: the sibling-prefix test that kills a naive `startswith`;
the verb-loop test that drives every guarded verb and every exempt verb with the *same*
wrong cwd; the origin-less-shape test that walks `{}`, `{"origin": None}`, `{"origin": {}}`,
empty-string and non-string `worktree`; and one **wiring** test through `dispatch()` that
goes red if the call site is deleted.

**Costs it names against itself.** "A perfect pure function that is never called is still a
check that cannot fail" — exactly one test covers the wiring and must never be weakened into
a pure-function test. `normcase` is identity on POSIX so any case-folding assertion is
platform-conditional. Guarding `claim` blocks a cross-tree stale-lease takeover.

**One finding worth more than the candidate.** `spine_lifecycle.py:311` stores
`str(Path(worktree))` — **not** `.resolve()`d. A worktree path traversing a symlink, opened
via `open_work`, would false-refuse from inside its own tree. `spine_lifecycle.py` is
zero-change by ruling, so this must be **filed, not fixed here**.

---

## Convergence — candidate B, with two things taken from A

Not a menu: **B is the recommendation.**

1. **Falsifiability is the dominant axis in this repo.** "A check that cannot fail" is the
   named defect class in inherited doctrine and in this project's `two-bin rule`, and the
   whole reason this issue exists is that the previous direction produced a check that
   could not discriminate. A candidate optimised so every branch can be driven to refuse
   with fabricated inputs is the one that answers the actual failure mode.
2. **B's verb scope is right and A's is not.** The very first case in this run's own repro
   is a `claim` from the main checkout against a worktree spine — it passes today. Under A
   it would still pass. A lease taken from the wrong tree is not harmless: it locks out the
   agent that belongs there.
3. **B's placement is better.** Above the early returns, with the exemption as data, means
   the exempt path is production-exercised rather than a branch no test reaches.

Taken from A:

- **Use `Path.is_relative_to` for containment** rather than a hand-rolled segment compare.
  It is already segment-wise, so it satisfies B's requirement while being less code to get
  wrong. B's sibling-prefix test is kept regardless — the test pins the behaviour, not the
  implementation.
- **Preserve an existing `origin` rather than overwriting it.** A's `setdefault` posture is
  safer than B's merge if any future template ever carries the block.

**Untaken road, named:** a third candidate that guards *every* verb including `current`.
Not authored, because both candidates independently measured the same blocker — the MCP
server calls the engine in-process from a cwd it never sets — and inherited doctrine
requires cross-tree `current` reads. It would break a supported workflow to close a hole
that carries no write.
