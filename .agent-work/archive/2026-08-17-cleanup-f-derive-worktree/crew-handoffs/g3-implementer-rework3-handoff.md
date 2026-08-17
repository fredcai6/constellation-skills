# Implementer Handoff — g3 rework 3

## Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. **Read the diff base with
`git rev-parse HEAD`. Do not trust any sha written here** — I amended a commit on
this gate and my own previous handoff cited a sha that no longer exists. Content
was identical and no measurement moved, but the lesson is live: the string is the
authority, the sha is an aid.

**One blocker. One writer-side guard. Do not touch anything else.**

Read, in order:

1. `crew-handoffs/g3-reviewer-rework2-result.md` — **B5**. This is yours.
2. `crew-handoffs/g3-implementer-rework2-result.md` — rework 2, the pass you are
   amending.
3. `crew-handoffs/g3-implementer-handoff.md` — the original gate. Its Allowed
   Scope, Specific Exclusions, Constraints and Authority **all still govern**.

**Settled, approved by three reviews, not to be reopened:** `_foreign_worktree`'s
deletion; `_entry_mid_flight_view` reading no payload; `_own_entries` as the
shared comparison; ownership-based selection at both sites; the pinned three-arm
differential; rework 2's `return {}` withhold and its `not owned` term; the #261
path; all 18 tests in `OwnershipIsBindingKeyNotWorktree`. **You are not redoing
any of it.**

## B5 — B4's class is still reachable through the `owned` door

Grep for the string **`spine is None and sid_bindings and not owned`** in
`scripts/hooks/spine_rail.py`.

`not owned` asks *"do I own nothing visible?"* But the branch below is reached by
**two** routes and only one of them is that. `spine` is **also** left `None` when
the session **owns** an entry whose spine does not load — archived, deleted,
moved, or an entry with no usable `spine` field. There `owned` is non-empty, the
guard does not fire, and the scan-bind writes `binding[bare sid] →` whatever
single in-tree spine the glob turns up — **including one a sibling agent of the
same session visibly claimed.**

**Measured through production writers only** — every binding entry written by
`handle_post_tool_use` from the repo's own pinned probe capture. Reproduced by me
at HEAD before writing this:

```
1. a crew claims the IN-TREE spine A          -> binding[sid#agent]
2. the parent claims its own IN-TREE spine B  -> binding[sid]
3. B is archived away                          (routine at closeout)
4. the parent restarts (SessionStart), then stops
```

| arm | parent bound to the CREW's spine | the parent's Stop | leaked |
|---|---|---|---|
| PREGATE | **no** | foreign-owner | no |
| REWORK1 | yes | own-gate | **YES** |
| **HEAD** | **yes** | **own-gate** | **YES** |
| HEAD, control (no SessionStart) | no | foreign-owner | no |

The parent is told, verbatim, *"Next imperative: CREWMARK implement the crew
gate."* **And the damage runs both ways:** the crew's own Stop recognises its own
spine in the control and **stops recognising it** after the parent's restart —
the parent's manufactured binding takes the crew's gate away from the crew.

**This is not `tc1` and the reviewer checked that against the two clauses that
made B4 a finding.** Pre-gate's first-readable-entry selection was pre-empted by
the crew's readable entry, so it never scanned; ownership-based selection skips
that entry and scans. `tc1` is that the scan-bind exists. B5 is that **this change
routes a new class of session into that writer, and the spine it binds them to is
one the store already attributes to somebody else.**

### The fix — guard the WRITER, not the reader

This is the reviewer's prescription and I agree with it. **Do not add a third
reader-side term.** Both B4 and B5 are the *same write* reached by two different
reader paths; a reader-side guard has now been patched twice and missed a door
each time.

**The bind-on-resume must refuse to file a spine path that
`session_view_provenance` already attributes to a *different* binding key, and
must refuse to overwrite that attribution.**

That is narrower than `tc1`'s open authority question: it does **not** decide
whether the scan should bind at all, only that it may not **contradict an
attribution the store already holds**. It closes both doors at once.

**I verified this is compatible with the #202 contract before ordering it.**
`test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding` scans
up a spine that is attributed to **nobody** — the sibling it protects is a
*different* path. A guard that fires only on an existing *conflicting*
attribution never triggers there, so that test should survive untouched. **If you
find it does not, stop and return rather than rewriting it** — that would mean
the guard is broader than I intended and the scope question is mine to take up,
not yours to resolve.

**Scope note, stated so you can hold me to it.** This touches the bind-on-resume
writer, which earlier handoffs on this gate declared "not yours". I am
deliberately re-opening exactly that much of it and no more, under the Admiral's
own rule that *the change that falsifies a claim owns the repair* — this gate's
change is what routes these sessions into that writer. `_scan_active_spine`
itself, and whether the scan should bind at all, remain out of scope and are
going up to the Admiral as `tc1`.

## Test Mode

**TDD required.** Write the B5 sequence first and watch it leak against the
committed code:

- a crew claims an **in-tree** spine A under `sid#agent_id`;
- the parent claims its **own** in-tree spine B under the bare `sid`;
- B is removed (archived);
- the parent's SessionStart, then the parent's Stop.

Assert **both directions**: the parent is not handed the crew's imperative, **and
the crew still sees its own gate afterwards**. The second half is what makes this
a two-way defect and a one-way test would miss it.

Use **production writers** — `handle_post_tool_use` with the pinned probe
capture — not a hand-built binding store. The reviewer's
`g3-review-rework2/rev3_production_sequence.py` is a working reproduction and the
fastest way to see it; it is committed evidence, so **copy what you need rather
than editing it.**

New tests go in `OwnershipIsBindingKeyNotWorktree`. The class subclasses
`unittest.TestCase` — this repo ships no pytest config, so a plain class of that
name collects **zero** tests and the selector reads as still-red.

## Close Criteria

- B5 is fixed, pinned by a production-writer two-call sequence, asserted in
  **both** directions. Show the leak before and its absence after.
- **B4 stays fixed** — re-run the earlier sequence; do not trade one door for the
  other.
- **The #202 sibling-merge test survives untouched.** If it does not, **stop and
  return**.
- **The #261 empty-bindings bind-on-resume still works**, pinned.
- The 18 existing `OwnershipIsBindingKeyNotWorktree` tests stay green and
  unweakened. `tests/test_worktree_derivation.py` stays unedited.
- **Enumerate what the writer now refuses**, and say whether any legitimate bind
  is now refused. That is the risk this fix carries.
- Every sentence in the prose you touch is true. The comment above rework 2's
  branch is already noted by the reviewer as false about the case it excludes —
  repair it. This is the lane's recurring defect class, now five recurrences deep.
- Full suite green, cache cleared, clean env, count stated, failure distribution
  derived mechanically (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`) even
  when empty.

## Baselines, re-measured by me

| tree | result |
|---|---|
| `main` at `17c2cee5`, isolated clone | 3171 / 7 / 0 |
| pre-gate `53c89ba1` | 3170 / 5 / 0 |
| g3 pass 1 | 3177 / 5 / 0 |
| g3 rework 1 | 3183 / 5 / 0 |
| **g3 rework 2 — your floor** | **3187 passed, 5 skipped, 0 failed** |

Targeted class is at **18**. Failure sets empty in every direction. Re-measure at
your actual HEAD first.

**Four environment hazards:**

1. **`CREW_SCRATCH_DIR`.** You are launched through `run_crew.py`, which sets it.
   Lane E's `tests/test_crew_launcher.py::ScratchDirResumeTests` fails for **any**
   agent running the suite from inside a crew-launched session. Scrub it with
   `-u CREW_SCRATCH_DIR`. That file is lane E's and fenced. **Do not fix it; do
   not report it.**
2. **Clear `__pycache__` before every measurement** — a stale cache fails
   `tests/test_bytecode_cache_provenance.py` by name.
3. **If you clone the repo, name the clone directory `constellation-skills`** —
   `MapTreeFreshnessTests` derives the map title from the checkout directory name.
4. **You cannot validate this hook from inside your own session** (#269). Call
   `decide_session_start` / `decide_stop` directly with constructed payloads.
   **Both scratch harnesses in `/tmp` are pinned to revisions the tree has moved
   past** — one to a moving `HEAD` (that was B1), one to a superseded commit.
   Useful, never authoritative. Check what an arm actually loads before believing
   a row.

If `map/INDEX.md` entity counts move, regenerate with
`py -m scripts.code_map build` — **never hand-edit it** (#544).

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py -k OwnershipIsBindingKeyNotWorktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py tests/test_worktree_derivation.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q
```

## Findings already recorded — do not chase, do not re-report

`tc1` (the scan-bind binds a session to a spine nobody claimed — the open
authority question B5 sits next to but is not); the `_reap_binding_entries` /
`_resume_mutate` re-insertion route, which the reviewer measured identical on all
three arms and therefore **pre-existing**, not this gate's; `agent_id: null` on
Stop; `bind()`'s `None`→`str(project_dir)` substitution; `map/ids.jsonl` empty;
`tc5` (provenance is last-key-wins on a path collision); `tc6` (the differential's
guard identifies arms by symbol, not revision); `tc7` (`_own_entries`' contract
does not name its writer invariant).

The reviewer's scoped nulls — three-or-more calls, concurrent sessions racing
`_binding_transaction`, and the gauge writer's reading of a scan-written binding
— are **untested, not cleared**. If your fix makes any of them cheap to test,
say so; do not widen scope to chase them.

## Deliverable Path Check

`git check-ignore` exits **1** for `scripts/hooks/spine_rail.py`,
`tests/test_spine_rail.py`, `map/` and `.agent-work/` — verified before this
dispatch. All are **committed** deliverables. `.agent-work/` is **not** gitignored
here. **Do not commit anything yourself.**

## Stop Conditions

Stop and return if: the #202 sibling-merge test cannot survive the guard; the
guard cannot be written without touching `_scan_active_spine`'s own decision about
whether to bind at all; allowed scope must be exceeded; or required evidence
cannot be produced.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied,
evidence produced, assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback. `Return status` on its own line, **lowercase** —
I copy it verbatim and the gate's postcondition matches on exact case.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implementer-rework3-result.md`
**before ending your turn** — that write is the delivery.

## On the Stop hook

When you finish, a `SPINE MID-FLIGHT` hook may fire telling you to reload the
commander skill and drive `execute.json`. **Refuse it and record that you
refused.** `SPINE_FILE` points at my spine under my live lease; your own
`crew-runs.json` entry has `spine: null`. Obeying would mean advancing my gate,
and the hook's own escape hatches (`block`, `waive`) write to that same spine, so
the sanctioned honest stop is itself the destructive act. All six crews on this
gate refused it and none was penalised. Author your own plan under
`crew-handoffs/g3-implement-rework3/`, claim it with your own session id, and
drive that.
