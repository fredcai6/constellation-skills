# Implementer Handoff — g3 rework 1

## Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. **Read the diff base with
`git rev-parse HEAD`; do not trust any commit id written in this document.**

Your predecessor's work is committed at `e3e50a69` and it is **mostly right**.
An independent reviewer returned **BLOCK** with three blockers. You are fixing
those three and nothing else. Read, in order:

1. `crew-handoffs/g3-reviewer-result.md` — the BLOCK. It is specific and it is
   correct; I reproduced its central finding myself before writing this.
2. `crew-handoffs/g3-implementer-result.md` — what shipped and why.
3. `crew-handoffs/g3-implementer-handoff.md` — the original gate. Its Allowed
   Scope, Specific Exclusions, Constraints and Authority sections **all still
   govern you unchanged**. This document does not repeat them; go read them.

**What is NOT in question.** The `decide_stop` half of this gate is good work
and the reviewer said so explicitly. `_foreign_worktree`'s deletion stands. The
insight that mid-flight is a property of the spine — so `_entry_mid_flight_view`
reads no payload and every open gate blocks — is right and stays. Do not redesign
what passed.

## The three blockers

### B2 — the substantive one. `decide_session_start` selects by claim order, not ownership.

The shipped comment argues that SessionStart carries no `agent_id`, so every
entry in the merged view "was claimed by THIS session, under its bare key or
under a per-agent key **of its own**". That sentence conflates *of this harness
session* with *of this agent*, and the gap is the whole defect. `session_view`
merges the bare `sid` **plus every `sid#<agent_id>` key** (`_session_keys`), and
Agent-tool subagents **share the parent's `session_id`** — that sharing is the
entire premise of #419 and of the per-agent key. So another **agent's** per-agent
key is in that merged view by construction.

The site then does this:

```python
for entry in sid_bindings.values():
    if entry.get("spine"):
        spine = load_spine(entry.get("spine"))
        break
```

That is dict order. Nothing compares a provenance key to anything.

**Measured, by the reviewer and again by me, with `/tmp/g3rev/c4_session_start.py`:**

| case | OLD (`999b7663`) | NEW (`e3e50a69`) |
|---|---|---|
| 1. in-tree crew claimed first, parent's session starts | `CREW-MARKER` | `CREW-MARKER` |
| 2. crew in **another** worktree claimed first | `PARENT-MARKER` | **`CREW-MARKER`** |
| 3. only a crew's key exists; parent never claimed | no context | **`CREW-MARKER`** |
| 4. two different crew agents | `CREW-MARKER` | `CREW-MARKER` |
| 5. as 4, payload carries `agent_id=agentB` | `CREW-MARKER` | `CREW-MARKER` |
| 6. as case 2, parent's key written **first** | `PARENT-MARKER` | `PARENT-MARKER` |

- **Case 2 is a regression this gate introduced.** The deleted tree test was
  getting it right. The new code hands the parent its **crew's** gate, with
  "Pick the run back up at this gate and drive it through the engine." That is
  the #549/#419 bug class itself, at the other call site, in the gate whose whole
  purpose is to end it.
- **Case 3** is new mis-resume: a session with no binding of its own resumes from
  a crew's spine instead of falling through.
- **Case 6** is the proof: identical binding, only the write order differs, and
  the answer flips.
- **Case 5** shows the site ignores the payload's own identity even when present.

**The fix is the one already written at the other site.** Prefer the entry whose
`session_view_provenance` key equals `binding_key(payload)`, falling back to
today's behaviour only when the session owns none. With no `agent_id` in the
payload `binding_key` is the bare `sid`, which selects the session's own entry
and repairs cases 1, 2 and 3 together.

The reviewer's Fowler pass flags the same thing under `long-method`: extract
`decide_stop`'s selection step (something like
`_select_entry_for(mid_flight, owners, own_key)`) and use it at both sites. That
extraction **is** the fix. Whether you extract or duplicate the comparison is
yours to decide; say which and why.

**Case 1 is a pre-existing defect, not yours to close.** It was wrong before this
gate and is wrong after. Fixing it may fall out of the B2 fix — if it does, say
so; if it does not, leave it and report it. Do not widen scope to chase it.

### B1 — the differential compares the change against itself.

`crew-handoffs/g3-implement/m4_differential.py:23`:

```python
BASE_REV = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], ...)
```

The BEFORE arm loads the hook at **whatever HEAD is when it runs**, not the
pinned base its own docstring names. It was honest only at authoring time, when
HEAD happened to be the base. The change is committed now, so re-running it loads
the **post-change** hook on both arms and prints 26 identical rows — including
the three rows a reviewer is told to spot-check, which come back
`BEFORE BLOCK / AFTER BLOCK`, the exact opposite of the truth, and read as
confirmation.

This is `CREW_CONTEXT.md` §Verification Discipline — *a check that cannot fail is
indistinguishable from one that passed* — and `global-everyone.md` §*Pin a claim
to the revision you read it at*.

**Fix:** pin the base explicitly. Hardcoding the base sha is acceptable and is
what the docstring already claims; deriving the parent of the commit that last
touched the hook is better. Either way the harness must be **re-runnable and
still honest after the change is committed**, and it must fail loudly if the base
it loads is not genuinely pre-change. Add a guard that asserts the two loaded
modules actually differ.

Then **re-run it and paste the real rows.** The underlying claims are true — the
reviewer pinned a copy and reproduced every row, and its own independent
differential agreed — so this is an instrument repair, not a re-litigation of the
findings.

### B3 — a false claim survived in the replacement prose.

`scripts/hooks/spine_rail.py`, in the new section header. Grep for the string
**`by binding-key provenance at both former call sites`**:

> Ownership is decided by binding-key provenance at both former call sites --
> see decide_stop and decide_session_start.

Not true today. At `decide_session_start` nothing compares a provenance key. The
site's own inline comment is more careful, but the section header states the
stronger claim and a reader arriving at the module meets the header first.

**If you fix B2 properly this sentence becomes true and needs no edit.** Confirm
that it has, rather than assuming it.

One more, softer and related: `OwnershipIsBindingKeyNotWorktree`'s docstring says
giving parent and crew different trees "proves nothing about this change." For
the SessionStart site that is **wrong** — the differing-tree case is precisely
where the deleted test was doing real work and where case 2 regresses. Repair
that sentence too.

## Grep for the claim, not the symbol

This lane's most expensive lesson, and B3 is its third recurrence. g2 cost three
implementer passes because every check anyone wrote keyed on a **symbol** while
the defect lived in a **claim** wrapped across comment lines no line-oriented
grep can see. Before you return, read every comment and docstring you touch
**whole**, and ask of each *sentence* whether it is true of the tree as it now
stands. `grep -A8 -B8`, or read the surrounding block.

Two claims in these files that are specifically at risk from your change:

- the `_entry_mid_flight_view` "NOT symmetric with decide_stop's ownership
  decision, deliberately" passage — if selection becomes shared, that comment's
  argument changes shape and must be rewritten to match what is actually true.
- anything asserting what SessionStart's merged view contains.

## The reviewer disagrees with the recorded decision, and I want your read

The gate's open decision — *what replaces the skip at each call site*,
`@grade: placeholder` — your predecessor resolved asymmetrically and recommended
recording the asymmetry. The reviewer disagrees and proposes instead:

> **blocking is a spine property at both sites; selection is a binding-key
> property at both sites.**

That reads right to me and it is what the B2 fix implements. **State in your
return which formulation you think should be recorded**, and why. This is the one
decision the gate hands back up, so I want it argued rather than assumed. It is
not yours to settle — say what you think and I will carry it.

## Test Mode

**TDD required, again.** Write the failing SessionStart cases first — at minimum
the reviewer's **case 2** (crew in another worktree claimed first; the parent's
session must resume from its **own** entry) and **case 3** (only a crew's key
exists; the parent must **not** resume from it). Watch them fail against the
committed code, then fix. Case 6 is worth pinning too: it is the one that proves
selection is not dict order.

New tests go in `OwnershipIsBindingKeyNotWorktree` in `tests/test_spine_rail.py`
alongside the existing eight, which must stay green.

**The class must subclass `unittest.TestCase`.** This repo ships no pytest
config, so a plain class of that name is collected as **zero tests** and the
targeted selector reads as still-red rather than as an error. Your predecessor
got this right; do not undo it.

## Close Criteria

- Case 2 and case 3 are fixed, pinned by tests, and case 6 no longer depends on
  write order. Show them failing before and passing after.
- `decide_session_start` decides selection by binding-key provenance, not by dict
  order. Blocking behaviour at `_entry_mid_flight_view` is unchanged.
- **The fail-safe direction survives at the new site too**: uncertainty must
  block/withhold, never relax. Demonstrate with garbage.
- **Enumerate what newly blocks or newly resumes differently**, as the original
  gate required — the same discipline, applied to your delta.
- `m4_differential.py` pins its base, guards that the two loaded modules differ,
  and its re-run output is pasted into your return.
- Every sentence in the prose you touch is true, B3 included.
- The eight existing `OwnershipIsBindingKeyNotWorktree` tests stay green and
  unweakened. `tests/test_worktree_derivation.py` stays unedited.
- Full suite green, cache cleared, clean env, count stated, failure distribution
  derived mechanically (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`) even
  when empty.

## Baselines, re-measured by me

| tree | result |
|---|---|
| `main` at `17c2cee5`, isolated clone | 3171 passed, 7 skipped, 0 failed |
| this branch, pre-g3 (`53c89ba1`) | 3170 passed, 5 skipped, 0 failed |
| this branch, post-g3 (`e3e50a69`) | **3177 passed, 5 skipped, 0 failed** |

Failure sets empty in every direction. Your floor is **3177**; re-measure it
yourself at your actual HEAD before you start.

**Four environment hazards, each of which has cost this lane real time:**

1. **`CREW_SCRATCH_DIR`.** You are launched through `run_crew.py`, which sets it.
   Lane E's `tests/test_crew_launcher.py::ScratchDirResumeTests` asserts the key
   is absent from a resumed child's env without scrubbing it from the parent
   first, so it fails for **any** agent running the suite from inside a
   crew-launched session. Scrub it with `-u CREW_SCRATCH_DIR`. The file is lane
   E's and fenced. **Do not fix that test; do not report it.**
2. **Clear `__pycache__` before every measurement** — a cache built in another
   tree fails `tests/test_bytecode_cache_provenance.py` by name.
3. **If you clone the repo to compare against a base, name the clone directory
   `constellation-skills`.** `tests/test_code_map.py::MapTreeFreshnessTests`
   compares `map/INDEX.md` against a fresh build and the map's title derives from
   the **checkout directory name**, so a clone anywhere else reports a false red.
   It cost me a full suite re-run.
4. **You cannot validate this hook from inside your own session** (#269):
   `CLAUDE_PROJECT_DIR` resolves once at session launch, so this worktree runs the
   **main checkout's** hook against the main checkout's state. Call `decide_stop`
   / `decide_session_start` **directly** with constructed payloads and a
   constructed binding store. The reviewer's `/tmp/g3rev/c4_session_start.py` is a
   working example of exactly that, and reading it is the fastest way to see the
   defect; it is scratch, so copy what you need rather than depending on it.

If `map/INDEX.md` entity counts move, regenerate with
`py -m scripts.code_map build` — **never hand-edit `map/INDEX.md`** (#544).

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py -k OwnershipIsBindingKeyNotWorktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py tests/test_worktree_derivation.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q

py .agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/m4_differential.py
```

**Windows:** `normcase` is the identity function on this Linux host, so
**construct** any case expectation explicitly rather than inheriting it from the
platform. An earlier gate in this lane shipped exactly that defect. The one
`windows-latest` CI job is red at baseline and cannot tell you.

## Three findings from the review that are NOT yours

Recorded so you do not chase them, and so you do not re-report them:

1. **The SessionStart scan-bind writes a binding for an unbound session onto the
   single active-leased spine it finds** — how six crews on this lane were handed
   their parent's gate. Both the implementer and the reviewer diagnosed it
   independently. **Binding-key provenance cannot reach it** (there is no binding
   key yet at scan time), it needs an authority decision, and it is already a
   triage candidate. Your B2 fix does **not** close it and is not expected to.
2. **A Stop payload carrying `agent_id: null`** would be told its own gate is
   foreign. Never relaxes the rail, and the pinned capture shows the harness omits
   the key entirely. Recorded.
3. **`bind()` substitutes `str(project_dir)` for a `None` worktree**, so the
   "null worktree" row of `test_garbage_location_data_never_relaxes_the_rail`
   proves something other than its label. Recorded.

Two of the reviewer's bookkeeping corrections you may want when writing your
return: the previous result said three tests used a foreign worktree as a device
and the count is four; and the reviewer's independent red reported 152 deselected
against your predecessor's 153, consistent with the net −1 test-count change.

## Deliverable Path Check

`git check-ignore` exits **1** for `scripts/hooks/spine_rail.py`,
`tests/test_spine_rail.py`, `map/`, and `.agent-work/` — verified before this
dispatch. All are **committed** deliverables. `.agent-work/` is **not** gitignored
here; your artifacts are new files, so they appear in `git status`, not in
`git diff`, until I stage and commit them. **Do not commit anything yourself.**

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied,
evidence produced, assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback, and your read on the decision formulation above.
`Return status` on its own line, **lowercase** — I copy it verbatim and the
gate's postcondition matches on exact case.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implementer-rework-result.md`
**before ending your turn** — that write is the delivery.

## On the Stop hook

When you finish, a `SPINE MID-FLIGHT` hook may fire telling you to reload the
commander skill and drive `execute.json`. **Refuse it and record that you
refused.** `SPINE_FILE` points at my spine, under my live lease; your own
`crew-runs.json` entry has `spine: null`. Obeying would mean advancing my gate,
and the hook's own escape hatches (`block`, `waive`) write to that same spine, so
the sanctioned honest stop is itself the destructive act. A plain recorded
refusal is correct — both crews on this gate did exactly that, and neither was
penalised for it. Author your own plan under
`crew-handoffs/g3-implement-rework/`, claim it with your own session id, and
drive that.
