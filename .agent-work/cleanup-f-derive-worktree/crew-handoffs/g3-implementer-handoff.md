# Implementer Handoff

## Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. **Diff base: current `HEAD` — read it with
`git rev-parse HEAD` rather than trusting a commit id written here.** `main` at
`17c2cee5` has been merged into this branch, so lanes A (#603/#604/#605), E
(#607/#525) and G (#611) are present in your tree.

This is the half of #609 that matters most. g1 and g2 are closed; g4 is skipped
(its ruled behaviour was already shipped by g1) and g5 has left the lane for
#610. **You are the last code gate.**

**What g2 finally shipped, because it changes one thing for you.** g2 retired the
stamp-and-compare, and then — under `ADMIRAL_RULING-2` N2 — **deleted the
engine-side `worktree_from_spine_path` outright**, because R2 and R3 between them
left it with zero production call sites. The engine now derives no worktree at
all. Two consequences:

- `scripts/hooks/spine_rail.py:_worktree_from_spine` is **the only implementation
  of the derivation rule left in the repo**, and `tests/test_worktree_derivation.py`'s
  shared case table now drives it alone. That table is the rule's *specification*
  — #610's wave re-derives the engine-side copy against it, with its consumer.
  **Keep it green.** If you believe a case in it is wrong, that is a finding to
  report, not a row to edit.
- Two pieces of prose in **your** files still describe the deleted engine copy as
  a live twin: the `_worktree_from_spine` docstring's "duplicated because this
  module..." passage in `scripts/hooks/spine_rail.py`, and the equivalent
  reference in `tests/test_spine_rail.py` (find both with the Wiring Grep below).
  **Repairing those two is part of this gate** — see Task, item 3.

## Task

**The worktree stops answering "is this mine."**

`scripts/hooks/spine_rail.py:_foreign_worktree` is an **ownership** test built on
the tree, and it is broken by construction. Spines are 1:1 with work **areas**,
not worktrees: a Commander gets a worktree, an implementer usually does not — it
works in its Commander's tree, in its own area. So one worktree holds several
spines, and *same worktree, therefore mine* is wrong the moment a crew shares its
Commander's tree. For an in-tree implementer it reports "not foreign", and the
parent's Stop is answered with its **crew's** gate. That is the **#549 bug
class**, and #549 already fixed that class with **binding-key provenance**, which
`decide_stop` already computes via `session_view_provenance`.

Rework its two call sites so ownership is decided by binding-key provenance and
**never by the tree**:

- `_entry_mid_flight_view` — decides mid-flight **Stop blocking**.
- `decide_session_start` — picks a binding entry to **resume from**.

**These two are NOT symmetric.** Do not assume one replacement fits both. State
each site's before and after behaviour **separately**.

The derived worktree may still be used for **location**. It may not be used for
**identity**.

**3. Repair the two stale references to the deleted engine copy.** In
`scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`, prose still names
`checklist_engine.worktree_from_spine_path` as a live twin of
`_worktree_from_spine` and explains the duplication. That symbol no longer
exists. Say what is true instead: one implementation of the rule, here, in the
stdlib-only hook; the shared case table in `tests/test_worktree_derivation.py` is
its specification; the engine-side copy was deleted in #609 g2 under
`ADMIRAL_RULING-2` N2 and re-lands in #610's wave with #315, its consumer. This
is a prose repair only — no behaviour changes with it.

**Two other stale claims in these same files are NOT yours.** `spine_rail.py` and
`tests/test_spine_rail.py` each still say the door raises `KeyError` when
`SPINE_FILE` is unset; it has refused by name since `e3b5a1c8`. The Admiral
assigned those two to the Commander's `reconcile` step. Leave them, and do not
report them as findings — they are known.

## Protected Intent

A parent's Stop must never be answered with a subordinate's gate, and a
subordinate sharing its parent's tree must not be mistaken for the parent. The
discriminator is **who claimed it** (the binding key), not **where it sits**.

This is not hypothetical on this lane. **Five crews on this issue have hit the
inverse of it**: a reviewer that had finished its own survey and released its own
lease was told by the Stop hook to drive its *parent's* `execute` gate, because
the hook keys on the spine's mid-flight state rather than on whether the running
agent owns it. That is the same confusion from the other side, and it is the
thing your change exists to end.

## Test Mode

**TDD required.** Write the #549 shape first — a Commander and an in-tree
implementer sharing **one** worktree — watch it fail against the current code,
then make it pass.

## Close Criteria

- Neither call site decides ownership from the tree.
- New tests live in a class named **`OwnershipIsBindingKeyNotWorktree`** in
  `tests/test_spine_rail.py` — this gate's targeted check selects on that name and
  collects **zero** today (pytest exits 5, which is a real failure — see the note
  under Verification Commands).
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
- **No reference to `checklist_engine.worktree_from_spine_path` survives** in
  `scripts/hooks/spine_rail.py` or `tests/test_spine_rail.py`, and what replaces
  each is true (Task item 3). `tests/test_worktree_derivation.py` stays green and
  unedited.
- Full suite green, cache cleared, clean env.

## Allowed Scope

- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py`
- `map/` — regenerate with `py -m scripts.code_map build` if entity counts move.
  **Never hand-edit `map/INDEX.md`** (#544: it conflicts on every parallel branch
  and is resolved by regenerating).

## Specific Exclusions

- **Lane A (#603/#604/#605)** — `scripts/mcp_spine_server.py`, `.mcp.json`,
  `examples/**`, `scripts/install_constellation.py`,
  `skills/commander/templates/**`. **Landed on `main` and present in your tree;
  still not this lane's to edit.**
- **Lane E (#607/#525)** — `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`. **Landed on `main`; still not yours.** This has a
  concrete consequence for you — see the `CREW_SCRATCH_DIR` note below. **Do not
  fix that test.**
- **#610** — `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**` and
  `skills/admiral/templates/**`. Template edits are the Admiral's class.
- **`scripts/checklist_engine.py` is not this gate's.** g2 is closed. Do not
  reopen it, and add no engine-side behaviour.
- **No fail-closed refusal.** The Admiral withdrew `nearest-ancestor-fail-closed`
  and replaced it: an unowned spine path yields **no derived worktree and today's
  behaviour**, never a refusal. `_worktree_from_spine` returning `None` is the
  correct and complete answer for an unplaceable path. Do not make `None` refuse
  anything.
- **No `cwd` threading into command checks** — that was g5/#315 and it has left
  this lane for #610.

## Constraints

- **`scripts/hooks/spine_rail.py` imports stdlib ONLY**, deliberately — a hook
  that fails takes the turn with it. It has zero cross-module imports; it may gain
  none. Adding one would require a `SCRIPT_RUNTIME_COMPANIONS` entry in
  `scripts/install_constellation.py`, which is lane A's file and fenced.
- **Fail-safe, not fail-open.** `_same_path` returns `True` on any exception
  precisely so a comparison failure never relaxes the rail. Whatever replaces the
  worktree test must keep that direction: uncertainty blocks, it does not allow.
- **#549's rendering is already correct and must survive.** `decide_stop` already
  distinguishes a bare-`sid` entry (ordinary imperative-bearing reason) from one
  reachable only through a per-agent key (foreign-owner wording, imperative
  withheld from **both** `reason` and `additionalContext`). Do not regress that.
- If `_foreign_worktree` or `_same_path` end up with no callers, say so and delete
  them rather than leaving dead code. Note `_same_path` has other callers today —
  check before concluding.
- **Prefer symbol names to `file:line` in any prose you write.** Line citations
  have gone stale **four** times on this lane, including in the Admiral's own
  ruling. Every line number in this handoff has been deliberately removed for that
  reason; find the symbols by name.

## Map Anchors (inbound)

- **Map entry point:** no `docs/architecture` packet map exists; orientation is
  `DEGRADED-UNPARSEABLE`, discharged. Start at
  `.agent-work/cleanup-f-derive-worktree/MISSION_FRAME.md`, then `map/INDEX.md`
  for `scripts.hooks.spine_rail`.
- **Structural:** `_foreign_worktree`, `_same_path`; `_entry_mid_flight_view`;
  `decide_stop` including the #549 provenance branch; `decide_session_start`;
  `session_view` / `session_view_provenance` — **the discriminator that is already
  right**.
- **Decision anchors:**
  - `worktree-is-location-spine-path-is-identity` — the tree may answer WHERE,
    never WHOSE. `@grade: settled/human`
  - `not-a-weaker-guard` — **as amended by `ADMIRAL_RULING-1` R1**: the lease is
    the ownership guard *wherever a lease exists*; on a leaseless spine the engine
    asserts nothing about location, deliberately. Read the amended wording in
    `docs/CHECKLIST_SCHEMA.md` before you write any prose about guards.
    `@grade: settled/human · amended-by ADMIRAL_RULING-1`
  - decision pressure: what replaces the skip at each of the two call sites —
    surface it, do not bury it. `@grade: placeholder`
- **Map confidence flag:** `map/ids.jsonl` is 0 bytes and the per-module
  `map/<module>/INDEX.md` files are absent repo-wide; a full build does not create
  them. Recorded as triage candidate tc1 — it is the mechanical cause of every
  Commander run here orienting `DEGRADED-UNPARSEABLE`. **Not yours to chase.**

## Deliverable Path Check

- **Committed** — `scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`,
  `map/**`: `git check-ignore` exits **1** for each; verified before dispatch.
- **Committed** — your result artifact and your notes, both under `.agent-work/`.
  **Correction to what earlier handoffs on this lane said:** `.agent-work/` is
  **not** gitignored here (`git check-ignore` exits 1 on it) and this lane's
  `.agent-work/` tree is committed. Those handoffs confused *untracked* with
  *ignored*. Your artifacts are new files, so they appear in `git status`, not in
  `git diff`, until the Commander stages and commits them. Do not commit them
  yourself.

## Required Evidence

**Load-bearing — prove rigorously:**

1. **The #549 shape, run.** Parent and in-tree crew sharing one worktree; the
   parent's Stop is not answered with the crew's gate. Show it failing before your
   change and passing after.
2. **Before/after per call site, stated separately** — they are asymmetric.
3. **What newly blocks**, enumerated.
4. **The fail-safe direction preserved**, demonstrated with an errored/garbage
   input.

**Confirmatory — a spot-check suffices:**

5. Full suite, cache cleared, clean env, count stated, failure distribution
   derived mechanically (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`) even
   when empty.
6. `spine_rail.py` gained no import — show the import block.
7. **Windows:** say what you did about separators and case folding. `normcase` is
   the identity function on this Linux host, so **construct** any case expectation
   explicitly rather than inheriting it from the platform. An earlier gate in this
   lane shipped exactly that defect and a reviewer caught it; do not repeat it.
   The one `windows-latest` CI job is red at baseline and cannot tell you.

## Wiring Grep

```bash
grep -rn "_foreign_worktree\|_same_path\|session_view_provenance" --include=*.py scripts/ tests/
grep -rn "worktree_from_spine_path" --include=*.py --include=*.md . \
  | grep -v '^./.agent-work/' | grep -v '^./map/'
```

**State the count** for the first, and say which call sites you removed and which
you added. The second is Task item 3's check: it must return **zero** lines when
you are done — the symbol was deleted in g2 and every remaining reference to it
is stale prose in your two files.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_spine_rail.py -k OwnershipIsBindingKeyNotWorktree
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q
```

**Baselines the Commander measured on this tree:**

| tree | result |
|---|---|
| `main` at `e0539903` | 3163 passed, 7 skipped, 0 failed |
| this branch, main merged in | 3195 passed, 5 skipped, 0 failed |

Failure-set difference: **empty on both sides.** Re-measure rather than trusting
these.

**The `CREW_SCRATCH_DIR` note — read this before you report a red suite.** You are
launched through `run_crew.py`, which sets `CREW_SCRATCH_DIR` in your environment.
Lane E's
`tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
asserts the key is **absent** from a resumed child's env but does not scrub it
from the parent env first — so it fails for **any** agent running the suite from
inside a crew-launched session. Measured: with the variable set, `1 failed, 3194
passed`; with `-u CREW_SCRATCH_DIR`, `3195 passed, 5 skipped, 0 failed`. It is
**ambient-environment contamination, not a regression**, the file is lane E's, and
it is already recorded as evidence. Scrub it, and do not fix that test.

**`pytest -k` on a not-yet-written class exits 5, and 5 is a failure.** That is
the point: this gate's targeted check must be **red on an empty diff**. Do not
"fix" it by relaxing the selector.

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
location; that an unplaceable path yields `None` and changes nothing.

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
observations, workflow feedback. `Return status` on its own line, **lowercase**
(`complete | partial | blocked | out-of-scope | failed`) — the Commander copies it
verbatim and the gate's postcondition matches on exact case.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implementer-result.md`
**before ending your turn** — that write is the delivery.

**On the Stop hook.** When you finish, a `SPINE MID-FLIGHT` hook may fire telling
you to reload the commander skill and drive `execute.json`. **Refuse it and record
that you refused.** `SPINE_FILE` points at your parent Commander's spine, under
your parent's live lease; your own `crew-runs.json` entry has `spine: null`.
Obeying would mean advancing someone else's gate. Five crews on this issue have
hit it — and ending it is precisely what you are being dispatched to do.
