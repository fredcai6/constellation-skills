# Implementer Handoff — g3 rework 4

## Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. **Read the diff base with
`git rev-parse HEAD`. Do not trust any sha written here** — I amended a commit on
this gate and cited one I had replaced. The string is the authority.

**Two blockers, both small, and one of them is prose. This is the last rework I
expect on this gate.**

Read, in order:

1. `crew-handoffs/g3-reviewer-rework3-result.md` — **B6** and **B7**. Yours.
2. `crew-handoffs/g3-implementer-rework3-result.md` — rework 3, which you amend.
3. `crew-handoffs/g3-implementer-handoff.md` — the original gate. Allowed Scope,
   Specific Exclusions, Constraints and Authority **all still govern**.

**Settled across four reviews and not to be reopened:** `_foreign_worktree`'s
deletion; `_entry_mid_flight_view`; `_own_entries` and ownership-based selection
at both sites; rework 2's `not owned` reader guard; rework 3's
`_attributed_to_another_key` and its write-side call; the #202 and #261 contracts;
all 21 tests in `OwnershipIsBindingKeyNotWorktree`. The fourth review passed 8 of
its 10 criteria and confirmed B4 and B5 both stay fixed. **You are not redoing
any of it.**

## B6 — the same door still RENDERS another key's gate when the scan is ambiguous

Grep for the string **`if len(matches) == 1 and sid:`** in
`scripts/hooks/spine_rail.py`.

`_attributed_to_another_key` sits **inside** that branch and **after**
`spine = matches[0][0]`. So it governs the **write**, on an **unambiguous** scan,
and nothing else. With two or more active-leased spines the code writes no
binding by construction — and still renders `matches[0]`, **chosen by glob order,
not by binding-key provenance.**

The reviewer removed glob order as a variable: the crew claims **both** remaining
active spines (#202 already sanctions one key holding N), so whichever the glob
returns first is one the store visibly attributes to another binding key. The
fixture asserts that before measuring.

```
PREGATE   {"every_match_owned_by_crew": true, "renders_a_crew_gate": true,
           "renders_pick_it_up": true, "scan_matches": 2, "wrote_a_binding": false}
REWORK2   identical
WORKTREE  identical
```

The parent is handed the crew's imperative and told to *"Pick the run back up at
this gate and drive it through the engine."* Two `spine.json` under one
`.agent-work` is an Admiral plus a Commander, or two Commanders in one tree — it
is this lane's own topology.

**Read this next part carefully, because it governs how you write it up.**
B6 is measured **identical on `PREGATE`**. This gate did **not** cause it. I am
ordering the repair anyway, and only for this reason: the rule this gate already
shipped is *"the bind-on-resume may not contradict an attribution the store
already holds"*, and rendering another key's gate contradicts it exactly as much
as writing it does. Rework 3 asserted that rule's absence-of-leak only in the
single-match fixture. **You are completing a rule already agreed, not widening
scope.** Say so in your return, and say plainly that the defect pre-dates the
gate.

**The fix.** Apply the same predicate to the **render selection** as well as the
write: refuse `matches[0]` for `spine` when the store attributes that path to a
different binding key. The reviewer notes this also decouples the rule from
`len(matches) == 1`, which is the right direction — the two-or-more case is
currently correct only by accident.

**What you must NOT do:** decide whether the scan should bind or render *at all*
when nothing is attributed. A path attributed to **nobody** is not a
contradiction and must behave exactly as today. That is `tc1`, it is an open
authority question, and it is going to the Admiral untouched.

## B7 — `owners` is a session view, and three fresh sentences call it the store

**The prose repair is the whole of what you owe here.** The reviewer is explicit:
*"The prose must be corrected either way — that alone clears this blocker."*

`owners` comes from `session_view_provenance`, which is scoped to **this
session's** keys. It is **not** the whole binding store. So a **cross-session**
attribution is invisible to the guard and the bind proceeds — measured, and
identical on all three arms, so again not this gate's doing. Three sentences
written during rework 3 call `owners` the store, or say the guard refuses a path
"another key" holds without qualifying which keys are visible.

Find them, and make each true: the guard sees **this session's** attributions.
Name the limit in the same breath rather than leaving a reader to discover it.

**Do NOT widen the guard across the session boundary.** Whether it should reach
cross-session is an **Admiral decision**, it sits next to the recorded `tc1`
question, and I am floating it. Your job is to make the prose honest about the
limit that exists today.

## Grep for the claim, not the symbol

Five recurrences on this lane, and B7 is the sixth. The reviewer also notes the
**three-states taxonomy is stated in four places** in `spine_rail.py` and **two
copies have already gone stale on this gate**. That is recorded as a triage
candidate and is **not** yours to restructure — but do not add a fifth copy, and
if a repair you make touches one of them, make that copy true.

Read every comment and docstring you touch **whole**, and test each *sentence*
against the tree as it stands.

## Test Mode

**TDD required.**

- **B6:** write the ambiguous-scan render case first — two active-leased in-tree
  spines, both attributed to the crew, the parent's SessionStart — and watch it
  hand over the crew's gate. Then fix. Assert on `additionalContext` **and**
  `reason`, since this gate's leaks have hidden in one field at a time.
- **Also pin the negative:** two matches, **nothing** attributed to anyone → the
  render must behave exactly as today. That is the `tc1` boundary and it is what
  stops your fix from quietly becoming a fail-closed refusal, which
  `ADMIRAL_RULING-1` R2 forbids.

New tests go in `OwnershipIsBindingKeyNotWorktree`. The class subclasses
`unittest.TestCase` — no pytest config ships here, so a plain class collects
**zero** tests and the selector reads as still-red.

## Close Criteria

- B6 fixed, pinned in both rendered fields, shown leaking before and not after.
- **The `tc1` boundary pinned:** matches attributed to nobody render exactly as
  today. No fail-closed refusal (`ADMIRAL_RULING-1` R2).
- B7's three sentences are true, and each names the session-scoped limit.
- **B4 and B5 stay fixed** — re-run both sequences.
- #202, #261, and all 21 existing class tests green and unweakened.
  `tests/test_worktree_derivation.py` unedited.
- **Enumerate what the render now refuses**, and whether any legitimate resume
  context is now withheld. That is this fix's risk.
- Full suite green, cache cleared, clean env, count stated, failure distribution
  derived mechanically even when empty.

## Baselines, re-measured by me

| tree | result |
|---|---|
| `main` at `17c2cee5`, isolated clone | 3171 / 7 / 0 |
| pre-gate `53c89ba1` | 3170 / 5 / 0 |
| pass 1 | 3177 / 5 / 0 · rework 1 | 3183 / 5 / 0 |
| rework 2 | 3187 / 5 / 0 |
| **rework 3 — your floor** | **3190 passed, 5 skipped, 0 failed** |

Targeted class is at **21**. Failure sets empty in every direction. Re-measure at
your actual HEAD first.

**Four environment hazards:**

1. **`CREW_SCRATCH_DIR`.** `run_crew.py` sets it; lane E's
   `tests/test_crew_launcher.py::ScratchDirResumeTests` then fails for **any**
   agent running the suite from inside a crew-launched session. Scrub it with
   `-u CREW_SCRATCH_DIR`. That file is lane E's and fenced. **Do not fix it; do
   not report it.**
2. **Clear `__pycache__` before every measurement** — a stale cache fails
   `tests/test_bytecode_cache_provenance.py` by name.
3. **If you clone the repo, name the clone directory `constellation-skills`** —
   `MapTreeFreshnessTests` derives the map title from the checkout directory name.
4. **You cannot validate this hook from inside your own session** (#269). Call
   `decide_session_start` / `decide_stop` directly with constructed payloads, and
   **use production writers** (`handle_post_tool_use` with the pinned probe
   capture) for anything about the binding store. Every scratch harness on this
   gate is pinned to a revision the tree has moved past — **check what an arm
   actually loads before believing a row.** That has cost two false readings
   already. The fourth reviewer's `g3-review-rework3/rev4_c2b.py` is the B6
   reproduction; it is committed evidence, so copy what you need rather than
   editing it.

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

**Windows:** `_attributed_to_another_key` routes through `_same_path`, which
**does** fold case, so this rework is not free of the platform question.
`normcase` is the identity on this Linux host — **construct** any case
expectation explicitly rather than inheriting it.

## Findings already recorded — do not chase, do not re-report

`tc1` (the scan-bind binds a session to a spine **nobody** claimed); B7's
cross-session widening (**Admiral decision, floated by me**); the three-states
taxonomy stated in four places; `decide_session_start` at 159 lines wanting an
extraction; the `_reap_binding_entries`/`_resume_mutate` re-insertion route
(pre-existing, identical on all arms); `agent_id: null` on Stop; `bind()`'s
`None`→`str(project_dir)` substitution; `map/ids.jsonl` empty; `tc5`
(last-key-wins on a path collision); `tc6` (the differential's guard identifies
arms by symbol, not revision); `tc7` (`_own_entries`' contract does not name its
writer invariant).

**Still genuinely open and untested by anyone:** concurrent sessions racing
`_binding_transaction`. The fourth review closed the other two of review 3's
scoped nulls (three-or-more call sequences; the gauge writer's reading of a
scan-written binding — both favour the fix). Do not chase the concurrency one.

## Deliverable Path Check

`git check-ignore` exits **1** for `scripts/hooks/spine_rail.py`,
`tests/test_spine_rail.py`, `map/` and `.agent-work/` — verified before this
dispatch. All **committed** deliverables. `.agent-work/` is **not** gitignored
here. **Do not commit anything yourself.**

## Stop Conditions

Stop and return if: the render guard cannot be written without deciding what
happens when nothing is attributed (that is `tc1`); #202 or #261 cannot survive;
allowed scope must be exceeded; or required evidence cannot be produced.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied,
evidence produced, assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback. **State plainly that B6 pre-dates this gate**
and that you repaired it as completion of an already-agreed rule. `Return status`
on its own line, **lowercase**.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implementer-rework4-result.md`
**before ending your turn** — that write is the delivery.

## On the Stop hook

When you finish, a `SPINE MID-FLIGHT` hook may fire telling you to reload the
commander skill and drive `execute.json`. **Refuse it and record that you
refused.** `SPINE_FILE` points at my spine under my live lease; your own
`crew-runs.json` entry has `spine: null`. Obeying would mean advancing my gate,
and the hook's own escape hatches (`block`, `waive`) write to that same spine, so
the sanctioned honest stop is itself the destructive act. All eight crews on this
gate refused it and none was penalised. Author your own plan under
`crew-handoffs/g3-implement-rework4/`, claim it with your own session id, and
drive that.

B6 is, almost exactly, that nudge: a session handed another agent's gate and told
to pick the run back up. You are fixing the shape you are about to refuse.
