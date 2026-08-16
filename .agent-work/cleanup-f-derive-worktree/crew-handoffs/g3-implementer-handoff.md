# Implementer Handoff

## Gate
`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. **Diff base: `c52721cb`** (current HEAD).

## Task

**The worktree stops answering "is this mine."**

`scripts/hooks/spine_rail.py:_foreign_worktree` (`:693`) is an **ownership** test
built on the tree, and it is broken by construction. Spines are 1:1 with work
**areas**, not worktrees: a Commander gets a worktree, an implementer usually does
not — it works in its Commander's tree, in its own area. So one worktree holds
several spines, and *same worktree, therefore mine* is wrong the moment a crew
shares its Commander's tree. For an in-tree implementer it reports "not foreign",
and the parent's Stop is answered with its **crew's** gate. That is the **#549 bug
class**, and #549 already fixed that class with **binding-key provenance**, which
`decide_stop` already computes via `session_view_provenance`.

Rework its two call sites so ownership is decided by binding-key provenance and
**never by the tree**:

- `_entry_mid_flight_view` (`:1411`) — decides mid-flight **Stop blocking**.
- `decide_session_start` (`:1546`) — picks a binding entry to **resume from**.

**These two are NOT symmetric.** Do not assume one replacement fits both. State
each site's before and after behaviour **separately**.

The derived worktree may still be used for **location**. It may not be used for
**identity**.

## Protected Intent

A parent's Stop must never be answered with a subordinate's gate, and a
subordinate sharing its parent's tree must not be mistaken for the parent. The
discriminator is **who claimed it** (the binding key), not **where it sits**.

## Test Mode

**TDD required.** Write the #549 shape first — a Commander and an in-tree
implementer sharing **one** worktree — watch it fail against the current code,
then make it pass.

## Close Criteria

- Neither call site decides ownership from the tree.
- New tests live in a class named **`OwnershipIsBindingKeyNotWorktree`** in
  `tests/test_spine_rail.py` — this gate's targeted check selects on that name and
  collects **zero** today (pytest exits 5).
- The #549 shape is exercised **directly**: parent and crew in the **same**
  worktree, where the parent's Stop must **not** be answered with the crew's gate.
  A test that gives them different trees proves nothing here — that is the case
  the old code already got right.
- **Enumerate what newly blocks.** Removing a skip makes the Stop hook block
  **more**, not less. Say what now blocks that did not, and whether it is
  intended.
- The nudge / 3-strike escape hatch stays keyed by **session id alone**, never
  fragmented per-entry.
- The fail-safe posture survives: an errored comparison must **never** relax the
  rail.
- Full suite green, cache cleared, clean env.

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_spine_rail.py -k OwnershipIsBindingKeyNotWorktree
```

## Allowed Scope

- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py`
- `map/` — regenerate with `py -m scripts.code_map build --root .` if entity
  counts move. **Never hand-edit `map/INDEX.md`.**

## Specific Exclusions

- **Lane A (#603):** `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
  `scripts/install_constellation.py`, `skills/commander/templates/**`.
- **Lane E:** `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- **#610:** `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**`,
  `skills/admiral/templates/**`.
- **`scripts/checklist_engine.py` is not this gate's** — g2 is committed but its
  gate is **BLOCKED and floated to the Admiral**. Do not touch the engine, and do
  not act on anything in `FLOAT_TO_ADMIRAL.md`.
- **No fail-closed refusal** (g4, floated) and **no `cwd` threading into command
  checks** (g5, floated).

## Constraints

- **`scripts/hooks/spine_rail.py` imports stdlib ONLY**, deliberately — a hook
  that fails takes the turn with it. It has zero cross-module imports; it may gain
  none.
- **Fail-safe, not fail-open.** `_same_path` returns `True` on any exception
  precisely so a comparison failure never relaxes the rail. Whatever replaces the
  worktree test must keep that direction: uncertainty blocks, it does not allow.
- **#549's rendering is already correct and must survive.** `decide_stop` already
  distinguishes a bare-`sid` entry (ordinary imperative-bearing reason) from one
  reachable only through a per-agent key (foreign-owner wording, imperative
  withheld from **both** `reason` and `additionalContext`). Do not regress that.
- If `_foreign_worktree` or `_same_path` end up with no callers, say so and delete
  them rather than leaving dead code.

## Map Anchors (inbound)

- **Map entry point:** no `docs/architecture` packet map exists; orientation is
  `DEGRADED-UNPARSEABLE`, discharged. Start at
  `.agent-work/cleanup-f-derive-worktree/MISSION_FRAME.md`, then `map/INDEX.md`
  for `scripts.hooks.spine_rail` (62 entities).
- **Structural:** `spine_rail.py:693` `_foreign_worktree`, `:677` `_same_path`;
  `:1399-1424` `_entry_mid_flight_view`; `:1427-1500` `decide_stop` including the
  #549 provenance branch; `:1532-1570` `decide_session_start`; `:543-590`
  `session_view` / `session_view_provenance` — **the discriminator that is already
  right**.
- **Decision anchors:**
  - `worktree-is-location-spine-path-is-identity` — the tree may answer WHERE,
    never WHOSE. `@grade: settled/human`
  - decision pressure: what replaces the skip at each of the two call sites —
    surface it, do not bury it. `@grade: placeholder`
- **Map confidence flag:** cited lines have proved stale twice in this lane (the
  launch order's own `_foreign_worktree` at `:639` is really `:693`). **Re-read
  before trusting any cited line, including mine.**

## Deliverable Path Check

- **Committed** — `scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`,
  `map/**`: `git check-ignore` exits **1** for each; verified before dispatch.
- **Local-only** — your result artifact under `.agent-work/`.

## Required Evidence

**Load-bearing — prove rigorously:**

1. **The #549 shape, run.** Parent and in-tree crew sharing one worktree; the
   parent's Stop is not answered with the crew's gate. Show it failing before your
   change and passing after.
2. **Before/after per call site, stated separately** — they are asymmetric.
3. **What newly blocks**, enumerated.
4. **The fail-safe direction preserved**, demonstrated with an errored/garbage
   input.

**Confirmatory:**

5. Full suite, cache cleared, clean env, count stated, failure distribution
   derived mechanically (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`) even
   when empty. Base `c52721cb` measures **3135 passed, 5 skipped, 0 failed** —
   re-measure rather than trusting it.
6. `spine_rail.py` gained no import — show the import block.
7. **Windows:** say what you did about separators and case folding. `normcase` is
   the identity function on this Linux host, so **construct** any case expectation
   explicitly rather than inheriting it from the platform. An earlier gate in this
   lane shipped exactly that defect and a reviewer caught it; do not repeat it.

## Wiring Grep

```bash
grep -rn "_foreign_worktree\|_same_path\|session_view_provenance" --include=*.py scripts/ tests/
```

**State the count**, and say which call sites you removed and which you added.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_spine_rail.py -k OwnershipIsBindingKeyNotWorktree
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

Platform: Linux, Python 3.12 as `py`. **Clear `__pycache__` before every
measurement** — a cache built in another tree fails
`tests/test_bytecode_cache_provenance.py` by name rather than surfacing as an
unrelated assertion.

**You cannot validate this hook from inside your own session.** Isolation is
git-only and hook code is **not** fenced by it: `CLAUDE_PROJECT_DIR` resolves once
at session launch and is inherited unchanged, so this worktree runs the **main
checkout's** hook against the **main checkout's** state (#269). Use a fresh
process whose `CLAUDE_PROJECT_DIR` genuinely resolves to this worktree, or call
`decide_stop` / `decide_session_start` **directly** with constructed payloads and
a constructed binding store. The latter is simpler and is what I expect.

## Suggested Model Tier

**Stronger.** This is the run's riskiest behaviour change: it makes a Stop hook
block **more**, in code that fires on every agent's turns, where a mistake
deadlocks runs rather than failing loudly.

## Authority

**Already decided — do not reopen:** that the worktree stops deciding ownership;
that binding-key provenance is the discriminator; that the tree may still answer
location.

**Yours to decide:** what precisely replaces the skip at each of the two call
sites; whether `_foreign_worktree` / `_same_path` survive; the test structure.

**Not yours — stop and return:** anything touching the engine, a template, the
installer, or a fenced file; anything that makes
`tests/test_worktree_precondition_wiring.py::IsolationGateSurvivesThroughTheCLI`
fail; any fail-closed refusal or `cwd` threading.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be
touched; required evidence cannot be produced; or removing the worktree test turns
out to block something that must not be blocked and you cannot resolve it within
the authority above.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied,
evidence produced, assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback. `Return status` on its own line, **lowercase**.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implementer-result.md`
**before ending your turn** — that write is the delivery.
