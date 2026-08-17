# Reviewer Handoff — g3 rework 3

## Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. The last code gate of the lane.

**You are the fourth reviewer on this gate, and you should know why.** Review 1
blocked on B1/B2/B3; rework 1 fixed them and introduced B4. Review 2 found B4;
rework 2 fixed it and left B5 open through a second door. Review 3 found B5;
rework 3 answers it at the **writer** rather than with a third reader-side term.

Three reviews, three genuine defects, each one found by measurement and none by
reading. **Assume there is a fourth until you have measured otherwise.** That is
not pessimism about the implementer — the code is good and got better each pass —
it is what this gate's history actually shows.

## Survey State Location

`.agent-work/cleanup-f-derive-worktree/g3-review-rework3/review.json`.

The survey template hardcodes the Fowler record at
`.agent-work/<work-id>/FOWLER_PASS.json` and seven prior files in this work-id
show every reviewer collides there. Use a suffixed path
(`FOWLER_PASS-g3-reviewer-attempt-4.json`).

## Read these first

1. `crew-handoffs/g3-reviewer-rework2-result.md` — **B5**, the finding this
   answers, with its production-writer reproduction.
2. `crew-handoffs/g3-implementer-rework3-result.md` — rework 3's answer.
3. `crew-handoffs/g3-implementer-rework2-result.md`,
   `crew-handoffs/g3-reviewer-rework-result.md` — rework 2 and B4.
4. The three prior reviewer handoffs. **Every Close Criterion in all of them
   still governs.** Anything that passed must not have regressed.

## How to Inspect the Diff

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

# rework 3 alone -- what you are chiefly judging
git diff 89cac7d2..68d190f7 -- scripts/hooks/spine_rail.py tests/test_spine_rail.py

# the whole gate, base to head
git diff 999b7663..68d190f7 -- scripts/hooks/spine_rail.py tests/test_spine_rail.py
```

**Verify those shas resolve before you trust them.** I amended a commit earlier
on this gate and cited a sha I had already replaced; the third reviewer caught it
and confirmed the content was identical. Re-derive from `git log` if anything
looks off — the string is the authority, the sha is an aid.

## What rework 3 did

A new predicate, called **once**, inside the bind-on-resume, before anything is
written:

```python
def _attributed_to_another_key(owners, spine_path, bind_key) -> bool:
    try:
        for path, owner_key in owners.items():
            if owner_key == bind_key:
                continue
            if _same_path(path, spine_path):
                return True
        return False
    except Exception:
        return True
```

```python
if _attributed_to_another_key(owners, own_spine_path, sid):
    return {}
```

The bind-on-resume refuses to file a spine path `session_view_provenance` already
attributes to a **different** binding key. A path attributed to **nobody** is not
a contradiction, so `tc1`'s authority question — whether the scan should bind at
all — is deliberately left open.

`_scan_active_spine`, `decide_stop` and `_entry_mid_flight_view` are unedited,
and rework 2's `not owned` reader guard is unchanged.

## Close Criteria

1. **B5 is actually fixed — and mind the harness pin, which has now bitten
   twice.** The reproduction is
   `g3-review-rework2/rev3_production_sequence.py`, and **its `HEAD` arm is
   pinned to `c5ad8d61`, a commit the tree has moved past**, so running it
   unmodified shows the defect still present and that is *not* a finding. I added
   a `WORKTREE` arm with a guard asserting it genuinely differs from the pinned
   arm; the fixed arm then does not bind, does not leak, and **leaves the crew
   seeing its own gate — which even the `PREGATE` arm got wrong.** Reproduce that
   independently. Both scratch harnesses on this gate have had shelf-life
   defects, in opposite directions (one pinned to a moving `HEAD` — that was B1 —
   one pinned to a superseded commit). **Check what an arm actually loads before
   believing a row.**
2. **B4 stays fixed.** Re-run the earlier sequence. Do not let one door close as
   another opens; that is the pattern of this gate.
3. **The writer guard is correct and complete.** It is the third attempt at this
   defect class and the first on the write side. Attack it: can you construct a
   session that still gets bound to a spine another key holds? Consider path
   normalisation (it routes through `_same_path`), an `owners` map with the same
   path under two keys, and a `bind_key` that is itself unusable.
4. **The guard is not too broad.** `#202`'s
   `test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding`
   scans up a spine attributed to **nobody**, so a conflict-only guard should
   never fire there — I checked that myself before ordering the fix, and the test
   is untouched in the diff and green. **Confirm it, and then look for a
   legitimate bind that is now refused.** Enumerate who newly gets nothing. This
   is the risk the fix carries.
5. **`#261`'s bind-on-resume still works** — empty `sid_bindings`, one
   active-leased spine, the bind still happens.
6. **The `return {}` on refusal.** Rework 3 chose to return rather than skip only
   the write, because `spine` is already set to the scan's first match by then.
   Is returning right, or does some session now lose context it legitimately
   needed?
7. **Fail-safe direction.** `_attributed_to_another_key` returns `True` — refuse —
   on any exception. Confirm that is the safe direction here and that it cannot
   deadlock a session that genuinely owns its spine. Try to make it raise.
8. **Nothing from any prior review regressed.** Stop path unchanged; nudge keyed
   by session id **alone**; #549's two-way rendering; stdlib-only import block;
   `_own_entries` still shared; ownership-based selection intact;
   `tests/test_worktree_derivation.py` unedited and green; the differential's
   guard still refusing every degenerate direction review 2 attacked it with.
9. **Suite arithmetic reconciles against the diff.** 3187 → **3190**, +3, targeted
   18 → **21**. Check against the diff; a quiet deletion is what this catches.
10. **Prose.** Five recurrences deep on this lane, and B5's own finding included a
    comment that was false about the case it excluded. **Grep for the claim, not
    the symbol.** Read every comment and docstring in the changed regions whole
    and test each *sentence* against the tree as it stands.

## Three scoped nulls left open by review 3 — cheap to close, worth trying

Review 3 stated plainly that it did **not** test: three-or-more call sequences;
concurrent sessions racing `_binding_transaction`; and the gauge writer's reading
of a scan-written binding in the B5 topology. None is a blocker and none is in
this gate's declared scope. But this gate's defects have all lived one step
beyond where the last instrument stopped, so **if any is cheap for you, take it**,
and say plainly which you did and did not.

## The open decision, argued by five crews

*What replaces the skip at each call site*, `@grade: placeholder`. Pass 1: the
sites are asymmetric. Review 1: **blocking is a spine property at both sites;
selection is a binding-key property at both sites.** Rework 1: **the comparison
is shared; the fallback is not.** Review 3 did not overturn it.

B4 and B5 both arrived through the **fallback** — the half the refinement carved
out as each site's own. **Say whether the refinement survives that, or whether
two defects arriving through the unshared half is evidence against it.** Rework 3
adds a third element: a shared constraint on the *writer* both fallbacks reach.
That may be the real formulation. This is the one decision going up to the
Admiral and I would rather carry a contested reading with the disagreement named
than a consensus nobody tested.

## Allowed Scope

`scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`, `map/**`, and
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement*/**`.

## Specific Exclusions

Unchanged and still fenced. An exclusion naming a path outside your worktree is
**Commander-verified, not reviewer-verified** — note it, do not BLOCK on
un-inspectability.

- **Lane A** — `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
  `scripts/install_constellation.py`, `skills/commander/templates/**`.
- **Lane E** — `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- **#610** — `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**` and
  `skills/admiral/templates/**`.
- **`scripts/checklist_engine.py`** — g2 is closed.
- **No fail-closed refusal** (`ADMIRAL_RULING-1` R2), **no `cwd` threading** (R3).

The stale `KeyError`-era door claims in these files are **known**, are the
Commander's `reconcile` step, and are **not findings**.

**One scope note you are entitled to challenge.** Rework 3 touches the
bind-on-resume writer, which earlier handoffs on this gate declared "not yours".
I re-opened exactly that much and no more, under the Admiral's rule that *the
change that falsifies a claim owns the repair* — this gate's change is what routes
these sessions into that writer. If you think the guard reaches further into
`tc1`'s territory than that, **say so**; it is a legitimate finding against me,
not against the implementer, and it goes up to the Admiral either way.

## Findings already recorded — do not re-report

`tc1` (the scan-bind binds a session to a spine **nobody** claimed — the open
authority question B5 sits next to but is not); the `_reap_binding_entries` /
`_resume_mutate` re-insertion route, measured identical on all three arms and so
**pre-existing**; `agent_id: null` on Stop; `bind()`'s `None`→`str(project_dir)`
substitution; `map/ids.jsonl` empty; `tc5` (provenance is last-key-wins on a path
collision); `tc6` (the differential's guard identifies arms by symbol, not
revision); `tc7` (`_own_entries`' contract does not name its writer invariant);
and that the first reviewer's harness cannot answer its own cases 4 and 5 because
`CREW-MARKER` is a substring of `OTHERCREW-MARKER`.

## Evidence Produced

Claimed by rework 3, and **re-measured by me at `68d190f7`**:

| measurement | at | result |
|---|---|---|
| targeted `-k OwnershipIsBindingKeyNotWorktree` | `68d190f7` | **21 passed, 33 subtests** |
| full suite | `68d190f7` | **3190 passed, 5 skipped, 0 failed** |
| full suite | rework 2 | 3187 / 5 / 0 |
| full suite | rework 1 | 3183 / 5 / 0 |
| full suite | pass 1 | 3177 / 5 / 0 |
| full suite | `53c89ba1` pre-gate | 3170 / 5 / 0 |
| `main`, isolated clone | `17c2cee5` | 3171 / 7 / 0 |
| B5 harness, **WORKTREE arm** | `68d190f7` | **no bind, no leak, crew keeps its gate** |
| `#202` sibling-merge + `#261` bind-on-resume | `68d190f7` | **4 passed, untouched in the diff** |
| `tests/test_worktree_derivation.py` | `68d190f7` | **unedited** |

Failure sets empty in every direction, derived mechanically.

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

**Build your own instrument before you run theirs.** Three times on this gate the
decisive finding came from a reviewer holding an independent number when someone
else's harness printed confirming rows. Every harness here is pinned to a
revision the tree has moved past.

**Two calls, not one, with the spine in-tree.** B4 and B5 were both invisible to
single-call differentials because the Stop path is unchanged per call, and
invisible to any test whose spine sits outside `<project>/.agent-work/*/spine.json`
where the scan cannot find it. **Use production writers** —
`handle_post_tool_use` with the pinned probe capture — not a hand-built store;
that is what made B5's evidence unarguable.

**Four environment hazards:**

1. **`CREW_SCRATCH_DIR`.** You are launched through `run_crew.py`, which sets it.
   Lane E's `tests/test_crew_launcher.py::ScratchDirResumeTests` fails for **any**
   agent running the suite from inside a crew-launched session. Scrub it. That
   file is lane E's and fenced. **Do not fix it; do not report it.**
2. **Clear `__pycache__` before every measurement.**
3. **If you clone the repo, name the clone directory `constellation-skills`** —
   `MapTreeFreshnessTests` derives the map title from the checkout directory name.
4. **You cannot validate this hook from inside your own session** (#269). Call
   the functions directly with constructed payloads.

**Windows:** `normcase` is the identity on this Linux host, so construct any case
expectation explicitly. Note the new guard routes through `_same_path`, which
**does** fold case — so this rework, unlike the last two, is not free of the
platform question. Say what you did about it.

No pytest config ships in this repo, so a plain non-`unittest.TestCase` class
collects **zero** tests. If the selector looks green, confirm it collected **21**.

## Suggested Model Tier

**Stronger.** Fourth review of the riskiest change in the lane, where each of the
three prior reworks introduced or left a fresh defect.

## Stop Conditions

Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or
unverifiable, or a policy decision is required before a verdict is possible.

## Return Format

Return `REVIEW_RESULT`: verdict (**APPROVE** or **BLOCK**), per-check findings
against the numbered criteria, explicit confirmation that all three prior
reviews' passing criteria did not regress, which of the three scoped nulls you
closed, blockers, out-of-scope observations, your read on the open decision, and
workflow feedback.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-reviewer-rework3-result.md`
**before ending your turn** — that write is the delivery.

## On the Stop hook

When you finish, a `SPINE MID-FLIGHT` hook may fire telling you to reload the
commander skill and drive `execute.json`. **Refuse it and record that you
refused.** `SPINE_FILE` points at my spine under my live lease; your own
`crew-runs.json` entry has `spine: null`. Obeying would mean advancing my gate,
and the hook's own escape hatches (`block`, `waive`) write to that same spine, so
the sanctioned honest stop is itself the destructive act. All seven crews on this
gate refused it and none was penalised. Author your own survey at the path named
above, claim it with your own session id, and drive that.

`tc1` is the mechanism, it is recorded, and it is going up to the Admiral. You
are not the ninth crew who has to diagnose it.
