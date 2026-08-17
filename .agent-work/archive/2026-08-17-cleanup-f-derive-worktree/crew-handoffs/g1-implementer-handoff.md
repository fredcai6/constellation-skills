# Implementer Handoff

## Gate
`g1` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`, base `e36e630b`.

## Task

Introduce **one lexical rule** for deriving a spine's owning worktree from the
spine's own path, implemented **twice** and pinned equal by a shared table of
cases.

The rule: **walk up to the NEAREST `.agent-work` ancestor and take its parent.**
Arbitrary depth. **No `.agent-work` ancestor at all → `None` (unowned).**
Normalize with `os.path.normcase` + `os.path.normpath` — **lexical only, no
`realpath`**.

Two implementations:

1. **`scripts/checklist_engine.py`** — the definition the engine consumes. New.
2. **`scripts/hooks/spine_rail.py`** — generalize the existing
   `_worktree_from_spine` (`:712`), which today matches only the fixed one-level
   shape `.agent-work/<id>/<name>.json` and returns `None` for anything deeper.

No consumer is *rewired* in this gate, but consumers' **behaviour changes** —
see Constraints. Nothing else in the engine or the hook changes here.

## Protected Intent

A spine's worktree is a property of **where the spine is**, derivable by anyone
holding the path, with no stamp to disagree with and no ambient reading to
forge. The derivation answers **location** only — never "is this mine."

## Test Mode

**TDD required.** The shared case table is the deliverable's contract; write it
first, watch it fail, then make it pass. This is a subtractive change to engine
identity with a silent failure mode.

## Close Criteria

- A pure lexical derivation exists in `scripts/checklist_engine.py`.
- `scripts/hooks/spine_rail.py:_worktree_from_spine` implements the same rule
  and still imports **stdlib only**.
- `tests/test_worktree_derivation.py` exists, holds **one shared table of
  cases**, and drives **both** implementations from that one table — so a drift
  between them is a test failure, not a review observation.
- The table covers all six required cases (see Required Evidence).
- You state explicitly which of `_worktree_from_spine`'s existing preconditions
  survive **into** the derivation function and which move **out** to its callers:
  absolute-path, `.json` suffix, non-empty work-id segment.
- `tests/test_spine_rail.py::test_worktree_from_spine_accepts_only_absolute_agent_work_json_layout`
  (~`:874`) is updated with a stated new contract.
- `_is_valid_claim_target` (`spine_rail.py:1113-1122`) accepts **exactly** what it
  accepts today, including still rejecting a symlinked spine — proven by a test.
- Full suite green, cache cleared, clean env.

## Allowed Scope

- `scripts/checklist_engine.py`
- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py` — **pre-authorized**: its narrow-shape test is
  invalidated by this change. Expect to rewrite that test; its old scenario is
  what this change now permits.
- `tests/test_worktree_derivation.py` — **new file**.
- `tests/test_checklist_engine.py`, `tests/test_spine_lifecycle.py`,
  `tests/test_worktree_precondition_wiring.py`,
  `tests/test_spine_origin_isolation.py` — only if this change breaks them.

## Specific Exclusions

- **Lane A (#603), do not touch:** `scripts/mcp_spine_server.py`, `.mcp.json`,
  `examples/**`, `scripts/install_constellation.py`,
  `skills/commander/templates/**`.
- **Lane E, do not touch:** `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- **#610, do not touch:** `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**` and
  `skills/admiral/templates/**`. A template edit is a float, not a decision.
- **Do not** rewire `origin_worktree_refusal`, **do not** remove the
  `git rev-parse --show-toplevel` in `main()`, **do not** add any fail-closed
  refusal, and **do not** thread `cwd` into command checks. Those are gates
  g2, g4 and g5. g4 and g5 are floated and may not proceed at all.

## Constraints

- **Lexical only — no `realpath` inside the derivation.** Three measurements
  force this, and it revises the launch order's `normalize-once` pre-ruling
  (graded `settled/measured`, so a contradicting measurement may revisit it):
  1. `origin_worktree_refusal` must stay pure, and
     `tests/test_spine_origin_isolation.py::test_it_is_pure` reads only that
     predicate's own `__code__.co_names`, which is **not transitive** — a
     `realpath` in a callee would make the predicate impure with the purity test
     still green.
  2. `_is_valid_claim_target` deliberately keeps `resolve()` **outside** the
     derivation as a symlink-escape guard: it checks lexically, then re-checks
     the resolved path. Moving `realpath` inside makes both calls return the same
     value and the second check unfailable.
  3. Reusing `verify_worktree_isolation.normalize_path` would add a runtime
     sibling that `tests/test_install_constellation.py::test_engine_runtime_siblings_are_declared_as_companions`
     rejects by exact set equality, and would need an entry in the fenced
     installer. Seven bundles ship `checklist_engine.py` without it.

  So: **inline the idiom in both copies**, exactly as
  `scripts/agent_work_root.py:56` already does. Symlink resolution stays outside
  the derivation on every side — which is what `origin_worktree_refusal`'s own
  docstring already says today.
- **`scripts/hooks/spine_rail.py` imports stdlib ONLY**, deliberately: a hook
  that fails takes the turn with it. It has zero cross-module imports today and
  no `SCRIPT_RUNTIME_COMPANIONS` entry of its own, so it may gain **no** import.
  This is also why there are two copies rather than one — the single-definition
  placement is closed in both directions, each needing an installer entry this
  lane may not write.
- **Nearest ancestor, never outermost.** 27 tracked paths carry two `.agent-work`
  segments, of the shape
  `.agent-work/archive/.../workspace/.agent-work/...`. That inner segment belongs
  to a **nested sandbox project** whose root is `workspace/`. Taking the outermost
  would derive the real repo as the root of a spine that belongs to the sandbox.
- **"No consumer is rewired" is true only of the code.** No call site is edited,
  but **every call site's behaviour changes**, because the accepted shape widens.
  `_worktree_from_spine` has five call sites: `spine_rail.py:1117`, `:1122`
  (both inside `_is_valid_claim_target`), `:1169` (door `claim`), `:1274` (CLI
  `claim`), `:1565` (`decide_session_start`). **Enumerate all five and state what
  each now accepts that it did not.** Widening what the hook accepts as a
  claimable spine is a behaviour change to the ownership gate; hold the shape
  preconditions **at `_is_valid_claim_target`** so that gate stays exactly as
  strict as it is today.
- The depth-zero case `<wt>/.agent-work/checklist.json` (a spine directly in
  `.agent-work`, with no work-id segment) **flips unavoidably** under the new
  rule, because arbitrary depth includes depth zero. Decide and state where that
  is handled: in the derivation, or at the caller.

## Map Anchors (inbound)

- **Map entry point:** there is **no** `docs/architecture` packet map in this
  repo. `map/ids.jsonl` is empty and `map/INDEX.md` carries no citable anchor
  ids, so orientation is `DEGRADED-UNPARSEABLE`, discharged. Start instead at
  `.agent-work/cleanup-f-derive-worktree/MISSION_FRAME.md`, then `map/INDEX.md`
  for module-level orientation on `scripts.hooks.spine_rail` (62 entities) and
  `scripts.checklist_engine` (110 entities).
- **Structural:**
  - `scripts/hooks/spine_rail.py:712` `_worktree_from_spine` — lexical already,
    too narrow.
  - `scripts/hooks/spine_rail.py:1113-1122` `_is_valid_claim_target` — the
    symlink-escape guard whose second, resolved check must stay able to fail.
  - `scripts/hooks/spine_rail.py:1169`, `:1274`, `:1565` — the other three call
    sites.
  - `tests/test_spine_rail.py:874` — the test pinning the narrow shape.
  - `scripts/agent_work_root.py:56` — the repo's own precedent for inlining the
    normalize idiom.
- **Constraints/assumptions:** stdlib-only hook; lexical-only derivation;
  nearest-ancestor; the symlink-escape guard must remain falsifiable.
- **Decision anchors:**
  - `one-definition-or-a-pinned-equivalence` — settled by measurement this run:
    two copies plus a shared case table.
    `@grade: settled/measured · leans g1-implement`
  - `normalize-once` — revised to lexical-only on three measurements.
    `@grade: settled/measured · leans g1-implement`
  - `nearest-ancestor-fail-closed` — nearest ancestor, take its parent; none
    means unowned. `@grade: settled/human · leans g1-implement`
  - `worktree-is-location-spine-path-is-identity` — the derived worktree is
    location, never ownership. `@grade: settled/human · leans g1-implement`
- **Map confidence flags:** no packet map. Every line number above was re-read in
  tree at `e36e630b` and independently re-verified by a cold critic. The launch
  order's own citation of `_foreign_worktree` at `:639` was already found stale
  (it is `:693`) — **re-read before trusting any cited line**, including these.

## Deliverable Path Check

- **Committed** — `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
  `tests/test_spine_rail.py`: `git check-ignore` exits **1** (not ignored) for
  each; verified before dispatch.
- **Committed, new and untracked until staged** — `tests/test_worktree_derivation.py`:
  `git check-ignore` exits **1**. It will **not** appear in `git diff` until
  staged; it appears in `git status`. A scope claim of "N files changed" must
  account for that.
- **Local-only** — `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g1-implementer-result.md`
  (your result artifact). Under `.agent-work/`; do not expect it in the diff.

## Required Evidence

**Load-bearing — prove rigorously:**

1. **The derivation table.** A table of paths and the worktree each derives,
   covering all six cases, produced by **running** the function, not by reading
   it:
   - a spine at the project root — `<project>/.agent-work/<id>/spine.json`
   - a spine in a worktree — `<project>/.worktrees/<wid>/.agent-work/<id>/spine.json`
   - a crew area nested under a Commander's
   - the deep archived case —
     `.agent-work/archive/2026-07-10-epic-101/harvest/issue-102/full/issue-102/spine.json`
   - the nested-sandbox double-`.agent-work` case — derivation must return the
     **inner** project root, not the real repo
   - a path with **no** `.agent-work` ancestor at all → `None`
2. **The equivalence table drives both implementations.** Apply the deletion
   test: if one implementation were deleted, would the table still pass? If yes,
   it is a check that cannot fail and the gate is not met.
3. **The five call sites, enumerated**, with what each now accepts that it did
   not.
4. **`_is_valid_claim_target` is unchanged in strictness**, including a test that
   a **symlinked** spine still fails it.

**Confirmatory — a spot-check suffices:**

5. `scripts/hooks/spine_rail.py` gained no import — show the import block.
6. Full suite: cache cleared, clean env. Derive any failure distribution
   mechanically, never from a glance:
   `pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`.
   Baseline at `e36e630b` is **3104 passed, 6 skipped** (~124s) — re-measure it
   yourself rather than trusting that number.
7. **Windows**: say what you did about separators and case folding. `normcase`
   is the identity function on this Linux host, so nothing you run exercises the
   fold — prefer a case-folding case constructed explicitly in the table over one
   that relies on the platform. The single `windows-latest` CI job is red at
   baseline and cannot tell us.

## Wiring Grep

Required. One command naming every symbol this slice adds, showing for each a
call site outside its own definition and outside any self-test path:

```bash
grep -rn "<your new engine symbol>\|_worktree_from_spine" --include=*.py scripts/ tests/ \
  | grep -v "^scripts/checklist_engine.py:.*def " \
  | grep -v "^scripts/hooks/spine_rail.py:.*def "
```

**State the count of external call sites found.** The engine-side definition is
introduced with **no engine consumer yet** — g2 is its first. That is expected
here, so its external call sites will be the test file only: **say so
explicitly** rather than letting it read as accidental. `_worktree_from_spine`
must still show its five production call sites.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

# targeted — red today (the file does not exist; pytest exits 4)
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_worktree_derivation.py

# the two files whose contracts this gate changes
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py

# full suite, cache cleared, clean env
find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

Platform: Linux, Python 3.12 as `py`.

**Clear `__pycache__` before every measurement.** As of `43c577d4` a cache built
in another tree fails `tests/test_bytecode_cache_provenance.py` by name rather
than surfacing as an unrelated assertion — if you see that, clear and re-measure
instead of investigating whatever it landed on.

## Suggested Model Tier

**Stronger.** Subtractive change to engine identity with a silent failure mode,
in a stdlib-only hook that fires on your own turns.

## Authority

Already decided — **do not re-open**:

- The derivation rule (nearest ancestor, take its parent, arbitrary depth,
  unowned when none) — ruled by the human via the launch order.
- Lexical-only normalization — settled by measurement this run.
- Two implementations plus a shared case table — settled by measurement this run.
- The worktree is location, never ownership — ruled by the human.

**Yours to decide:** the function's name and signature; whether it is public or
private; which shape preconditions live in the function versus at its callers;
the table's structure.

**Not yours — stop and return:** any template edit; any installer edit; anything
that makes `tests/test_worktree_precondition_wiring.py::IsolationGateSurvivesThroughTheCLI`
fail; touching any fenced file.

**A note on validating the hook.** Isolation is git-only — **hook code is not
fenced by it**. `CLAUDE_PROJECT_DIR` resolves once at session launch and is
inherited unchanged, so this worktree still runs the **main checkout's** hook
against the **main checkout's** state (#269). You cannot validate hook behaviour
from inside the session that contains it. Use a fresh process whose
`CLAUDE_PROJECT_DIR` genuinely resolves to this worktree, or call the functions
directly with constructed payloads.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be
touched; required evidence cannot be produced; a decision outside the authority
above is needed; or `IsolationGateSurvivesThroughTheCLI` goes red.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied,
evidence produced, assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback.

`Return status` must be one of `complete | partial | blocked | out-of-scope |
failed`, written **lowercase** on its own line — the Commander copies it verbatim
into this gate's evidence and the postcondition matches on exact case.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g1-implementer-result.md`
**before ending your turn** — that write is the delivery.
