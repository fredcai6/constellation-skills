# Commander result — `commander-315-native`

**Verdict: implemented, independently APPROVED on integrity, and BLOCKED on one floated collision.**
PR **#577** is open against `main` and is **not merged**.

Refresh relaunch: a fresh agent re-claimed the same session id after the previous agent tripped
the context HARD gate at `start execute` and idled by design. Cold-started from the engine.

---

## 1. What landed

Branch `epic-568/c2-native-isolation`, base `9bb8c1b6`, HEAD `ed25bf8f`. PR
https://github.com/fredcai6/constellation-skills/pull/577

- **Write side** — `init_work_area.instantiate_spine` stamps a top-level `origin` block carrying
  exactly `{work_id, worktree, opened_by}`. Nothing guessed: branch, base, parent and the
  dispatching session are `spine_lifecycle.build_origin`'s to fill. Keys are a strict subset of
  that block's; `setdefault` preserves an existing `origin`.
- **Read side** — `checklist_engine.origin_worktree_refusal(spine, *, cwd, verb) -> str | None`,
  pure, matching the repo's existing `spine_lifecycle.closeout_refusal` precedent. One caller, in
  `main()`, after `load()` and before `dispatch()`, returning **without persisting**.
- **Deletion** — `COMMANDER_SPINE`'s `init` precondition `c0`,
  `scripts/verify_worktree_precondition_coverage.py`, and the enumeration tests that asserted the
  wiring being removed.
- **Docs** — `docs/CHECKLIST_SCHEMA.md` documents `origin`.
- **New coverage** — `tests/test_spine_origin_isolation.py`, 31 tests.

`scripts/spine_lifecycle.py`, `scripts/hooks/spine_rail.py` and `scripts/agent_work_root.py` are
untouched. `base_dir` is untouched; the resolved root is carried as `engine_cwd`.

## 2. What this certifies — and what it does not

Certified: **coverage** (every guarded verb on every spine carrying `origin`, not only where a
check was wired into a template); **unbypassability from the spine** (the check is no longer in
the spine); **an independent expected side** (a creation-time stamp, not a literal inside a check).

**Not certified, anywhere:** non-forwardability. The engine reads its ambient cwd, so a check
authored as `cd <origin.worktree> && ...` still satisfies it. The function docstring and the
schema docs both say so explicitly. The reviewer swept the whole change and every artifact for a
restatement and found none.

## 3. Before / after repro

`python .agent-work/commander-315-native/repro_native.py`, unedited:

```
A  origin spine, cwd = WORKTREE ROOT -> PASS     (want PASS)
B  origin spine, cwd = MAIN CHECKOUT -> REFUSED  (want REFUSED after the change)
C  no-origin,    cwd = MAIN CHECKOUT -> PASS     (want PASS in both worlds -- the fallback)
D  origin spine, cwd = WT SUBDIR     -> PASS     (want PASS -- containment, not equality)
B refused AND took no lease (state fact): True
GATE ARMED: True
```

Case B is decided on the **state fact** (no `engine_session` written), never on a substring of the
refusal prose. Before the change, B passed.

## 4. `init.c0` is gone and the native refusal fires where it used to

`skills/commander/templates/COMMANDER_SPINE.template.json` `init.preconditions` is now `[]`;
`scripts/verify_worktree_precondition_coverage.py` no longer exists. Verified by a check that is
**armed** — it exits 1 on the pre-change tree and 0 now. (My first draft of that check probed
`init`'s *post*conditions, where no `c0` exists, so it would have passed vacuously without the
deletion happening. Caught and corrected through the engine before it shipped — the exact defect
class this epic removes, authored by me, in a check meant to detect it.)

Exact count, since the launch order said "three": **4 test methods across 3 enumeration classes**
were removed — `test_refuses_broken_copy_and_passes_real_fixed_tree`,
`test_refuses_new_second_entry_without_naming_known_fixed_entry`,
`test_passes_once_new_entry_carries_the_precondition`,
`test_failure_output_states_enumerated_count` — plus the `COVERAGE_SCRIPT` constant and its helper.

The case `init.c0` used to catch — a Commander driving its spine from the main checkout — is now
caught by the engine at `claim`, one verb earlier and on every spine rather than only Commander
spines.

## 5. The new origin-carrying test

`tests/test_spine_origin_isolation.py`, 31 tests, is the deliverable the amended order made an
exit criterion. It covers a spine that **actually carries `origin`**:

- the **match** side (worktree root, and a subdirectory of it — containment, not equality);
- the **mismatch** side (a foreign tree, refused, spine byte-identical afterwards);
- the **sibling-prefix** case (`/w/repo-2` against `/w/repo` is not inside);
- the guarded/exempt verb sets asserted **as data**, membership and non-membership, derived from
  `MUTATING_VERBS`;
- eleven unusable-`origin` shapes, none of which raises;
- the in-process MCP shape (below).

`tests/test_worktree_precondition_wiring.py` stays green and unweakened, and is **not** cited as
coverage of this change — every fixture in it builds an `origin`-less spine, so it is green by
construction and is evidence for the fallback branch only. Its three surviving tests all pass.

## 6. The `mcp_spine_server.py:361` in-process caller — how I handled it, and where it broke

**My ruling, given to the implementer:** the guard applies with no exemption, no env override and
no bypass. I gave four reasons. **Reason #1 was false, and the implementer falsified it.**

I claimed a dispatched crew's cwd is its spine's worktree. It is not:
`run_crew.launch_process` (`scripts/run_crew.py:676`) is
`subprocess.run(argv, input=stdin, stdout=out, stderr=err, env=env)` — **no `cwd=`**. A crew
inherits the *dispatcher's* cwd. I verified this myself rather than accepting it; the reviewer
verified it a third time.

**The break is structural.** `spine_open` creates a **new** worktree and stamps `origin.worktree`
to it. The next verb on that spine is `claim`, issued in-process through the door, which never
chdirs. The door's process cannot already stand inside a directory that did not exist a moment
earlier. So **`spine_open` → `claim` in one session is now impossible through the door, by
construction**. `tests/test_mcp_lifecycle.py::FullStdioRoundTripTests` fails on exactly this.

Two candidate resolutions I **rejected on measurement**, not on preference:

- **Adjust the verb scope** (explicitly in my latitude). It cannot work: the round trip drives
  `start`, `attach` and `advance`, all in `MUTATING_VERBS`. Dropping `claim` moves the failure one
  call later.
- **Let the door supply `SPINE.parent`'s toplevel as the measured side.** Measured **equal to the
  stamped `origin.worktree` by construction**, because both derive from the same creation act.
  That is the `X == X` tautology this issue exists to avoid, and it stops measuring where the
  *actor* is — converting a guard on the actor into a guard on the file's location.

Every remaining honest fix changes **who sets cwd**, in `run_crew.py` or `mcp_spine_server.py` —
both outside allowed scope, both production behaviour, both requiring a float. **See §10.**

Worth naming: `origin` was **already** being stamped by `spine_lifecycle.build_origin` before this
change. The collision is a pre-existing write side meeting a new read side, not something this
change invented.

## 7. Failure set, diffed against main's baseline

`main`'s stated Linux baseline: **2934 passed, 5 skipped, 0 failed**.
This branch at `ed25bf8f`: **2959 passed, 6 skipped, 1 failed, 1130 subtests passed**.

Mechanical distribution (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`):

```
      1 FAILED tests/test_mcp_lifecycle.py
```

**Set difference: exactly `{tests/test_mcp_lifecycle.py}`** — the floated collision, nothing else.
The +25 passed is the 31 new tests less the 4 deleted enumeration methods and collection deltas;
the +1 skipped is the `skipUnless(os.name == "nt")` case-folding test.

Reproduced twice by me and twice by the reviewer. The Windows failures the Admiral cited do not
reproduce on Linux, as stated.

**One transient**, worth reporting rather than hiding: my first full-suite run also showed
`tests/test_gauge_chain_writer_to_trip.py::test_containment_repo_agent_work_untouched_by_the_chain`
failing. It passed on re-run and passes three times in isolation. Cause: that test snapshots the
repo's **live** `.agent-work` directory before and after and asserts equality, and a crew launcher
was still writing `crew-runs.json` into it during that window. Not caused by this change; filed as
`tc11`.

## 8. `verify_worktree_isolation.py --here`

```
worktree OK: in /home/tommy/projects/constellation-skills-wt/epic-568-315-native
EXIT=0
```

Run from inside the worktree. Run from the main checkout, the identical command **refuses** —
`wrong worktree: you are in /home/tommy/projects/constellation-skills, not your assigned worktree`
— which is the launch order's own demonstration that this checker's subject is the ambient cwd,
and is precisely why the comparison had to move into the engine.

## 9. The two live origin-less spines — my choice

**Left to the fallback. Not backfilled.** Three reasons, in order of weight:

1. One of the two is `.agent-work/commander-315/spine.json`, which lives in
   `constellation-skills-wt/epic-568-315` — a worktree the launch order forbids me to enter. I
   could not backfill it without breaching a no-go.
2. The other is `examples/mcp-interactive-demo/spine.json`, a shipped demo fixture. Stamping it
   with a machine-specific absolute path would make a committed example unusable anywhere else.
3. Backfilling means hand-editing spine state the engine owns, which the role doctrine forbids.

At n=2 the fallback is exactly the designed path, and it is the branch
`test_worktree_precondition_wiring.py` covers. My own run's spine is also origin-less — it predates
the stamp — so this change did not alter the rules under its own feet mid-run.

## 10. Floated to the Admiral — one ruling needed

**The collision in §6.** Options, none of them mine:

1. **`run_crew.launch_process` passes `cwd=<the spine's worktree>`.** Makes my reason #1 true
   rather than assumed, and is arguably correct independent of this issue. Does **not** fix
   `spine_open` → `claim`, which happens before any dispatch.
2. **The door `chdir`s around its in-process `main()` call.** Fixes both halves and keeps the
   no-bypass ruling intact in substance — the door then genuinely *is* in the spine's tree. Costs
   `mcp_spine_server` its cwd-independence invariant, which is load-bearing there.
3. **Accept the break and reconcile the test** — only if `spine_open` → `claim` in one session is
   genuinely unsupported. The test asserts it is supported; I could not establish otherwise.

**My recommendation: 1 + 2.** Neither weakens the guard. 1 is right on its own merits; 2 is the
only thing that closes the pre-dispatch half. Note that 2 is consistent with what this change
claims, since non-forwardability is explicitly **not** claimed — a caller choosing where it stands
is the acknowledged limit, not a breach.

**Ratified by me, disclosed for the record** (not floats): `EXPECTED_COMMAND_CHECK_COUNT` `13 → 12`
in `tests/test_shipped_check_commands_resolve.py`, mechanically forced by the authorized `init.c0`
deletion. The reviewer proved 12 is the only correct value by mutating it to 13 and to 11 and
watching both go red. The tripwire still pins an exact count and is not weakened.

## 11. Independent review

**`APPROVE`** on the change's integrity — the trap, the arm, the fallback, the no-gos, the
overclaim, the new coverage, the in-process caller — with **`Merge readiness: NOT READY`** while
the collision stands. The reviewer reproduced both arming reverts itself and wrote its own probe
rather than replaying the implementer's transcript. One recorded finding (`r2-scope`, the census
constant), carried through `consolidate --override-reason` for my ratification rather than rework.

Full result: `.agent-work/commander-315-native/crew-handoffs/g1-reviewer-result.md`.

## 12. Map impact

- `scripts.checklist_engine` — one new module-level pure function plus two verb sets and one
  statement in `main()`; entity count 106 → 107.
- `scripts.init_work_area` — `instantiate_spine` now writes a re-serialized dict rather than the
  resolved text.
- `scripts.verify_worktree_precondition_coverage` — **module removed**.
- `map/INDEX.md` regenerated; the diff is exactly attributable to the removed and added modules,
  with no unrelated drift.
- Worktree isolation moves from a per-template `command` check to an **engine invariant**.
- `map_orient.py` still returns `DEGRADED-UNPARSEABLE`, anchor count 0. File paths were used
  throughout, as instructed.
- **Newly relied on and now contradicted:** the assumption that a crew process's cwd is its
  spine's worktree.

## 13. Triage candidates

Filed on the spine as `tc6`–`tc12`: `run_crew` spawning without `cwd=`; the
`mcp_spine_server` cwd-independence tension; the origin stamp not reaching child checklists
(`review.json`, `IMPLEMENTER_PLAN.json`) where crew subagents actually work; a stamped spine
becoming unclaimable once its worktree is removed at closeout; the hand-maintained
`EXPECTED_COMMAND_CHECK_COUNT` census; the `.agent-work`-snapshotting containment test that any
concurrent writer breaks; and the `json.dumps` escape-and-reflow of instantiated spines.

## 14. Known behaviour change, recorded not patched

`instantiate_spine` re-serializes with `json.dumps(..., indent=2)`. Measured: 34 non-ASCII
characters in `COMMANDER_SPINE` become `\uXXXX` escapes, and hand-formatted one-line condition
dicts are reflowed. Parsed content, key order, rendered text and the trailing newline are all
unchanged, and no consumer reads a written spine as raw text — verified across `scripts/*.py`,
`scripts/hooks/*.py` and every shipped check command.

I chose **not** to patch it after review (`ensure_ascii=False` would remove half of it), so the
merged change is the reviewed change rather than an uncertified edit on top of a certified one.
Filed as `tc12`.

## 15. Workflow feedback — what I observed

- **I froze an unverified empirical claim into a handoff's `Authority` section, and an implementer
  built on it.** My reason #1 was checkable with one grep and was wrong. The implementer had to go
  read `launch_process` to find out. The cost was not the wrong sentence; it was that a *settled*
  ruling rested on it, so the ruling now has to be reopened after the code was written against it.
- **My own verification check was vacuous on first write.** I authored `c5` to prove `init.c0` was
  deleted and pointed it at the wrong condition list, where it would have passed without the
  deletion happening. I only caught it because I ran it expecting a failure and got one — arming a
  check before trusting it is what saved it.
- **I dispatched a crew before `start`ing its gate.** The engine let me `attach` evidence to a
  pending gate, so nothing objected until the implementer's exit note pointed out that
  `g1-implement` still read `pending`. A crew noticed my process error before the engine did.
- **The implementer crew inferred from process ancestry that I was dead and wrote a "run-state
  note" into its result artifact saying so.** I was alive. The inference was reasonable — its
  launcher had reparented — but a crew writing confident claims about its dispatcher's liveness
  into a durable artifact is a way for false facts to enter the record.
- **`run_crew.py` is foreground/blocking and outlives a 10-minute tool timeout.** My first dispatch
  was killed mid-flight by my own shell timeout, leaving the crew `RESUMABLE` with real work
  already in the tree. `--resume` recovered it cleanly, which is the registry doing exactly its
  job.
- **A test that snapshots the live `.agent-work` tree cannot tell "the thing under test wrote" from
  "anything else wrote."** It went red once under a concurrent crew launcher and green on re-run.
  Any suite run concurrent with live agent activity can hit it.
