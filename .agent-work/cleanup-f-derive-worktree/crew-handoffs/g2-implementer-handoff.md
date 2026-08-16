# Implementer Handoff

## Gate
`g2` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. **Base for your diff: `9ff86f2d`** (g1, already
committed and independently approved).

## Task

**Retire stamp-and-compare.** Three coupled changes.

1. **`origin_worktree_refusal` stops COMPARING.** Delete the equality test
   between the stamped `origin.worktree` and the engine's ambient cwd, and every
   parameter that exists only to feed it (`scripts/checklist_engine.py:102-179`).
2. **The per-guarded-verb `git rev-parse --show-toplevel` goes away entirely**
   (`scripts/checklist_engine.py:3573-3578`, the single impure call site, sitting
   before `dispatch()` and returning without `save()`).
3. **`origin.worktree` keeps being WRITTEN and is read by NOTHING for a
   decision.** `spine_lifecycle.build_origin` and `init_work_area` keep stamping
   it. Pin the property with a test **whose name contains `provenance`**, in
   `tests/test_spine_origin_isolation.py`.

Plus: repair the prose this makes false — `docs/CHECKLIST_SCHEMA.md` (its `:120`
paragraph describes the retired mechanism, and its `:124` line cites the call site
as `:3411-3444` when it is `:3573-3578`) and `scripts/spine_lifecycle.py`.

**After this gate the predicate may have nothing left to do.** If it degenerates
to a function that returns `None` on every path, **say so plainly and delete it**
rather than leaving a hollow function behind. That is a judgment I am explicitly
delegating — make it, state it, and say which callers you removed.

## Protected Intent

There is **one** source of truth for a spine's worktree — its path — so there is
no second value that can disagree with the first, and no ambient reading a check
command could forge. Removing the comparison removes **no guard**: the **lease**
is and always was the ownership guard; the worktree comparison was a location
check wearing an ownership costume.

## Test Mode

**TDD required** for the provenance pin (write it, watch it fail against the
current tree, then make it pass). Test-after is fine for the deletions.

## Close Criteria

- No `rev-parse --show-toplevel` anywhere in `scripts/checklist_engine.py`.
- No decision path anywhere reads `origin.worktree` — **enumerated by command
  with the count stated**, not sampled.
- `origin.worktree` is still written. Prove it, don't assert it.
- A `provenance`-named test in `tests/test_spine_origin_isolation.py` pins that
  pairing and fails if either half breaks.
- The stale prose in `docs/CHECKLIST_SCHEMA.md` and `scripts/spine_lifecycle.py`
  is repaired.
- Full suite green, cache cleared, clean env.

**This gate's own targeted check**, which must go from red to green:

```bash
! git grep -q 'rev-parse --show-toplevel' -- scripts/checklist_engine.py \
  && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
       tests/test_spine_origin_isolation.py -k provenance
```

Both halves are red today (the grep matches; the `-k` selector collects zero and
pytest exits 5).

## THIS GATE ADDS NO FAIL-CLOSED REFUSAL

Read this twice. The shape refusal for an unowned spine path — "a guarded verb
against a spine whose path has no `.agent-work` ancestor is refused" — is gate
**g4**, and g4 is **floated to the Admiral and may not proceed**.

Measured reason: that refusal refuses **362 of the 429** guarded-verb engine
invocations the current suite makes, across **125 tests in 7 files**, three of
which sit in `tests/test_crew_launcher.py` — **fenced to lane E**. The gate would
have to break three tests it may not fix.

So `origin_worktree_refusal` (or whatever survives it) must **not** start
refusing anything it does not refuse today. Its guarded/exempt verb sets keep
their current meaning. **If you find yourself adding a refusal, stop.**

## Allowed Scope

- `scripts/checklist_engine.py`
- `scripts/spine_lifecycle.py`
- `docs/CHECKLIST_SCHEMA.md`
- `tests/test_spine_origin_isolation.py` — **pre-authorized rewrite.** Most of
  this file tests the comparison you are deleting; its scenarios are what this
  change now removes. Expect to rewrite it substantially. `test_it_is_pure` is
  worth keeping in spirit — see Constraints.
- `tests/test_checklist_engine.py`, `tests/test_spine_lifecycle.py`,
  `tests/test_worktree_precondition_wiring.py`, `tests/test_mcp_door_engine_cwd.py`
  — only as this change breaks them.
- `map/` — regenerate with `py -m scripts.code_map build --root .` if entity
  counts move. **Never hand-edit `map/INDEX.md`.**

## Specific Exclusions

- **Lane A (#603):** `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
  `scripts/install_constellation.py`, `skills/commander/templates/**`.
  `mcp_spine_server.py` carries **prose** describing the guard you are retiring
  (`:18`, `:371`, `:384`) and `scripts/run_crew.py` does too (`:860`). **You may
  not edit either.** Report the stale prose as an out-of-scope observation for the
  owning lane.
- **Lane E:** `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- **#610:** `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**`,
  `skills/admiral/templates/**`.
- **Not this gate:** any fail-closed refusal (g4, floated); any `cwd` threading
  into command checks (g5, floated); `_foreign_worktree` and the Stop hook (g3).
  `scripts/hooks/spine_rail.py` should not need to change at all — if you think it
  does, that is a finding.

## Constraints

- **Removing the origin comparison removes NO guard.** If you find a case where
  the comparison was genuinely the only thing preventing harm, that is a
  **finding to report**, not something to ship around. I want that search done
  honestly, and a negative result stated as a negative result.
- The refusal path must keep sitting **before `dispatch()`** and returning
  **without `save()`**, so a refusal never writes into the tree it protects. If
  the whole path goes away, say what now occupies that position and why nothing
  is lost.
- `tests/test_spine_origin_isolation.py::test_it_is_pure` reads only
  `origin_worktree_refusal.__code__.co_names` and is **not transitive** — it
  cannot see impurity in a callee. Do **not** treat it as proof of purity. If the
  predicate survives in any form and still needs a purity guarantee, make that
  guarantee real rather than inherited.
- This **supersedes** the 2026-08-15 worktree-identity ruling in
  `.agent-work/rulings/2026-08-15-worktree-identity.md`. Cite it where your change
  contradicts it and **say so plainly** in your result.

## Map Anchors (inbound)

- **Map entry point:** no `docs/architecture` packet map exists; orientation is
  `DEGRADED-UNPARSEABLE`, discharged. Start at
  `.agent-work/cleanup-f-derive-worktree/MISSION_FRAME.md`, then `map/INDEX.md`
  for `scripts.checklist_engine` and `scripts.spine_lifecycle`.
- **Structural:** `scripts/checklist_engine.py:102-179` (the predicate — read its
  docstring before changing it; it **already withdraws** the unforgeability
  claim), `:3573-3578` (the single impure call site), `:98-99`
  (`ORIGIN_EXEMPT_VERBS` / `ORIGIN_GUARDED_VERBS`);
  `scripts/spine_lifecycle.py:build_origin`; `docs/CHECKLIST_SCHEMA.md:120`,
  `:124`.
- **Decision anchors:**
  - `derivation-authoritative-stamp-becomes-provenance` — derivation is
    authoritative immediately; the stamp keeps being written and nothing reads it
    for a decision. `@grade: settled/human`
  - `not-a-weaker-guard` — the lease was always the guard. `@grade: settled/human`
  - `worktree-is-location-spine-path-is-identity` `@grade: settled/human`
  - `nearest-ancestor-fail-closed` — **its second half is g4 and is floated.**
    `@grade: settled/human`

  A `settled/human` anchor is **not yours to unsettle**. Contradicting evidence is
  a finding, not a licence.
- **Available to you from g1 (`9ff86f2d`):**
  `checklist_engine.worktree_from_spine_path` — lexical, pure, nearest
  `.agent-work` ancestor, `None` when unowned. **This gate is its first
  consumer** — if it is the right tool here, use it; if this gate turns out not to
  need it at all, say that plainly rather than wiring it in for appearances.
- **Map confidence flag:** every line number above was read in tree, but the
  launch order's own citation of `_foreign_worktree` at `:639` was already found
  stale (`:693`), and `docs/CHECKLIST_SCHEMA.md:124`'s own citation is stale too.
  **Re-read before trusting any cited line, including these.**

## Deliverable Path Check

- **Committed** — `scripts/checklist_engine.py`, `scripts/spine_lifecycle.py`,
  `docs/CHECKLIST_SCHEMA.md`, `tests/test_spine_origin_isolation.py`, `map/**`:
  `git check-ignore` exits **1** for each; verified before dispatch.
- **Local-only** — your result artifact under `.agent-work/`.

## Required Evidence

**Load-bearing — prove rigorously:**

1. **The guarded-verb path exercised BEFORE and AFTER.** Show a guarded verb
   running through `main()` on both sides, with the `git rev-parse` subprocess
   gone after. Show that the verbs still refused where they should be still are.
2. **The enumeration.** By command, **with the count stated**, of every remaining
   read of `origin.worktree` anywhere in the repo — and for each, why it is not a
   decision. Do not sample.
3. **The provenance pin**, demonstrated to fail if either half breaks (stop
   writing the stamp → red; read it for a decision → red).
4. **The adversarial search** for a case where the removed comparison was the
   only thing preventing harm, and its result stated either way.

**Confirmatory:**

5. Full suite, cache cleared, clean env, count stated, failure distribution
   derived mechanically (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`) even
   when empty.
6. The tripwire `tests/test_worktree_precondition_wiring.py` **still green** —
   this gate must not disturb it. Its collision with g5 is g5's problem, not this
   gate's.
7. **Windows:** say what you did about separators and case folding. `normcase` is
   the identity function on this Linux host, so construct any case expectation
   explicitly rather than inheriting it from the platform. The one
   `windows-latest` CI job is red at baseline and cannot tell us.

## Wiring Grep

Required. If the predicate survives, show its call sites; if it is deleted, show
that **nothing** still calls it:

```bash
grep -rn "origin_worktree_refusal\|worktree_from_spine_path" --include=*.py scripts/ tests/
```

**State the count**, and say explicitly which call sites you removed and which
you added.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

# this gate's targeted check -- red today, must be green after
! git grep -q 'rev-parse --show-toplevel' -- scripts/checklist_engine.py \
  && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
       tests/test_spine_origin_isolation.py -k provenance

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_spine_origin_isolation.py tests/test_spine_lifecycle.py \
  tests/test_worktree_precondition_wiring.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

Platform: Linux, Python 3.12 as `py`. **Clear `__pycache__` before every
measurement** — a cache built in another tree fails
`tests/test_bytecode_cache_provenance.py` by name rather than surfacing as an
unrelated assertion.

Suite at your base `9ff86f2d`: **3159 passed, 6 skipped, 0 failed.** Re-measure
it yourself rather than trusting that number.

## Suggested Model Tier

**Stronger.** This is the subtractive heart of the issue, in engine identity,
with a silent failure mode — a wrong deletion here shows up as nothing at all.

## Authority

**Already decided — do not reopen:** that the comparison goes; that the ambient
git read goes; that the stamp stays written and unread; that the lease is the
guard.

**Yours to decide:** whether the degenerate predicate is deleted or kept as a
seam; the shape of the provenance test; how the prose is reworded; whether this
gate consumes `worktree_from_spine_path` at all.

**Not yours — stop and return:** any fail-closed refusal; any template or
installer edit; any fenced file; anything that makes
`tests/test_worktree_precondition_wiring.py::IsolationGateSurvivesThroughTheCLI`
fail.

**Validating hook behaviour:** isolation is git-only and **hook code is not
fenced by it**. `CLAUDE_PROJECT_DIR` resolves once at session launch, so this
worktree still runs the **main checkout's** hook against the **main checkout's**
state (#269). Use a fresh process or call functions directly with constructed
payloads. You should not need the hook at all this gate.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be
touched; required evidence cannot be produced; you find a case where the removed
comparison was the only thing preventing harm; or the tripwire goes red.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied,
evidence produced, assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback. `Return status` on its own line, **lowercase**
(`complete | partial | blocked | out-of-scope | failed`).

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-result.md`
**before ending your turn** — that write is the delivery.
