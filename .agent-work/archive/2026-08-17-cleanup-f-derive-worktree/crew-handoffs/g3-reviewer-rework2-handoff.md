# Reviewer Handoff — g3 rework 2

## Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. The last code gate of the lane.

**You are the third reviewer on this gate.** Review 1 returned BLOCK (B1, B2,
B3); rework 1 answered all three. Review 2 confirmed those fixes, then found and
measured **B4** — a new defect in production code that the fix for B2 had
created. Rework 2 answers B4 with one condition.

Your job is narrow and it is the one that matters: **decide whether rework 2's
condition is right, and whether fixing B4 broke anything.** Two reworks on this
gate have each introduced a fresh defect while correctly fixing the named one.
Assume this one did too until you have measured otherwise.

## Survey State Location

`.agent-work/cleanup-f-derive-worktree/g3-review-rework2/review.json`.

The survey template hardcodes the Fowler record at
`.agent-work/<work-id>/FOWLER_PASS.json` and six prior files in this work-id show
every reviewer collides there. Instantiate yours with a suffixed path
(`FOWLER_PASS-g3-reviewer-attempt-3.json`) rather than clobbering committed
evidence.

## Read these first

1. `crew-handoffs/g3-reviewer-rework-result.md` — **B4**, and its four attacks on
   the differential's guard. This is the finding rework 2 answers.
2. `crew-handoffs/g3-implementer-rework2-result.md` — rework 2's answer.
3. `crew-handoffs/g3-implementer-rework-result.md` — rework 1, most of the change.
4. `crew-handoffs/g3-reviewer-result.md` — review 1: B1, B2, B3.
5. `crew-handoffs/g3-reviewer-rework-handoff.md` and
   `crew-handoffs/g3-reviewer-handoff.md` — the Close Criteria from both prior
   reviews. **All of them still govern.** Anything that passed must not have
   regressed.

## How to Inspect the Diff

Four commits, and you need them apart:

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

# rework 2 alone -- what you are chiefly judging
git diff 6bba3fd2..9b1a551e -- scripts/hooks/spine_rail.py tests/test_spine_rail.py

# the whole gate, base to head
git diff 999b7663..9b1a551e -- scripts/hooks/spine_rail.py tests/test_spine_rail.py
```

`999b7663` pre-gate · `e3e50a69` pass 1 (blocked on B1/B2/B3) · `6bba3fd2`
rework 1 (blocked on B4) · `9b1a551e` rework 2. `map/INDEX.md` also moves; it is
regenerated, never hand-edited (#544).

## What rework 2 did

One condition on the existing branch in `decide_session_start`:

```python
owned = _own_entries(list(sid_bindings.items()), owners, own_key)
spine = None
for _spine_path, entry in owned:
    ...
if spine is None and sid_bindings and not owned:
    return {}
```

- **`sid_bindings` non-empty and `_own_entries(...) == []`** → withhold: no
  binding **and no context**.
- **`sid_bindings` empty** → scan and bind. #261's path, untouched.

`_scan_active_spine`, `decide_stop`, `_entry_mid_flight_view` and rework 1's
ownership-based selection are all unchanged.

## Close Criteria

These carry the verdict.

1. **B4 is actually fixed, measured not read — and mind the harness's pin.**
   The reviewer's reproduction is at `/tmp/g3rev2/rev2_composite.py`. **Its `NEW`
   arm is pinned to `6bba3fd2`, the pre-fix commit, so running it unmodified
   shows the defect still present and that is not a finding.** I hit this myself
   and added a fourth arm loading the working-tree hook, with a guard that the
   two sources genuinely differ; the fixed arm then wrote no binding and rendered
   foreign-owner with no leak, matching OLD and BLOCKED. **Reproduce that
   yourself**, and note the irony worth carrying: the instrument that caught B1
   (a harness pinned to a moving `HEAD`) has the mirror-image shelf-life problem,
   pinned to a commit the tree has moved past. Neither is safe to re-run
   unexamined.
2. **The #261 path still works.** `sid_bindings` empty, exactly one active-leased
   spine, the bind-on-resume still happens. **This is the regression risk in the
   fix** — rework 2 must not have traded B4 for #261. Test it, do not read it.
3. **The `not owned` narrowing is the right term.** Rework 2 says it implemented
   the broader `sid_bindings` non-empty form first and it broke #202's
   `..._merges_onto_existing_sibling_binding`, whose session **owns** its entry
   and merely cannot read the spine it points at — not the B4 class. Narrowing to
   `not owned` restored it untouched. **Adjudicate that.** Is `not owned` the
   correct discriminator, or does it leave a reachable case where a session that
   owns something unreadable still gets bound to a spine it never claimed?
4. **The withhold returns `{}` rather than falling through for advisory context.**
   The handoff left this to the implementer, which measured the fall-through
   rendering the crew's imperative with "Pick the run back up at this gate and
   drive it through the engine" — the same leak in the other field. Is returning
   `{}` right, or does some session now lose context it legitimately needed?
   Enumerate who newly gets nothing.
5. **The one pre-existing test rework 2 rewrote.**
   `test_session_start_bind_on_resume_still_writes_under_the_bare_key`
   **arranged the B4 class as its fixture** — the acting session's only visible
   entry was its subagent's, and it asserted the scan bound the session to a
   spine it never claimed. Rework 2 kept every claim (resume context injected,
   write under the bare key, correct `engine_session`, sibling composite key
   untouched) and changed the fixture to a session with an **own** entry whose
   spine was deleted under it. **This is the most dangerous line in the diff** —
   a test that asserted the defect, rewritten by the agent fixing the defect.
   Decide whether the new fixture still reaches the same code path and whether
   anything was lost. It claims to have gained an assertion and lost none.
6. **Nothing from either prior review regressed.** Re-check specifically: B2's
   cases (the first reviewer's `/tmp/g3rev/c4_session_start.py`, cases 2, 3 and 6
   — I re-ran it and all still match correct OLD behaviour); the Stop path
   unchanged; fail-safe at both sites; nudge keyed by session id **alone**; #549's
   two-way rendering; stdlib-only import block; `_own_entries` still shared;
   `tests/test_worktree_derivation.py` unedited and green; the differential's
   guard still refusing every degenerate direction review 2 attacked it with.
7. **Suite arithmetic reconciles against the diff.** 3183 → **3187**, +4, with the
   targeted class 14 → **18**. Check that against the diff. One test was rewritten
   in place; a quiet deletion could hide there.
8. **Prose.** The lane's recurring defect, now four recurrences deep — B4 itself
   included a comment claiming the site "withholds rather than guessing" while
   the code it guarded went on to bind. **Grep for the claim, not the symbol.**
   Read every comment and docstring in the changed regions **whole** and ask of
   each *sentence* whether it is true of the tree as it now stands. Rework 1
   found three of its own false sentences an hour after writing them. Assume
   there is another.

## The open decision, argued by four crews

*What replaces the skip at each call site*, `@grade: placeholder`. Pass 1 said
the sites are asymmetric. Review 1 countered: **blocking is a spine property at
both sites; selection is a binding-key property at both sites.** Rework 1 agreed
and refined it: **the comparison is shared; the fallback is not.** Review 2 did
not overturn that.

B4 arguably tests the refinement: the fallback being each site's own is exactly
what let one site's fallback write ownership. **Say whether the refinement
survives B4, or whether B4 is evidence against it.** This is the one decision
going up to the Admiral and I would rather carry a contested reading with the
disagreement named than a consensus nobody tested.

## Allowed Scope

`scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`, `map/**`, and
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement*/**`.

## Specific Exclusions

Unchanged and still fenced. Flag if touched; an exclusion naming a path outside
your worktree is **Commander-verified, not reviewer-verified** — note it, do not
BLOCK on un-inspectability.

- **Lane A** — `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
  `scripts/install_constellation.py`, `skills/commander/templates/**`.
- **Lane E** — `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- **#610** — `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**` and
  `skills/admiral/templates/**`.
- **`scripts/checklist_engine.py`** — g2 is closed; no engine-side behaviour.
- **No fail-closed refusal** (`ADMIRAL_RULING-1` R2), **no `cwd` threading** (R3).

The stale `KeyError`-era door claims in these files are **known**, are the
Commander's `reconcile` step, and are **not findings**.

## Findings already recorded — do not re-report

`tc1` (the scan-bind binds a session to a spine it never claimed — the open
authority question **B4 sits next to but is not**); `agent_id: null` on Stop;
`bind()`'s `None`→`str(project_dir)` substitution; `map/ids.jsonl` empty; `tc5`
(provenance is last-key-wins on a path collision); `tc6` (the differential's guard
identifies arms by symbol, not revision); `tc7` (`_own_entries`' contract does not
name its writer invariant); and that the first reviewer's harness cannot answer
its own cases 4 and 5 because `CREW-MARKER` is a substring of `OTHERCREW-MARKER`.

## Evidence Produced

Claimed by rework 2, and **re-measured by me at `9b1a551e` before dispatching
you**:

| measurement | at | result |
|---|---|---|
| targeted `-k OwnershipIsBindingKeyNotWorktree` | `9b1a551e` | **18 passed, 25 subtests** |
| full suite | `9b1a551e` | **3187 passed, 5 skipped, 0 failed** |
| full suite | `6bba3fd2` | 3183 / 5 / 0 |
| full suite | `e3e50a69` | 3177 / 5 / 0 |
| full suite | `53c89ba1` (pre-gate) | 3170 / 5 / 0 |
| `main`, isolated clone | `17c2cee5` | 3171 / 7 / 0 |
| B4 harness, working-tree arm | `9b1a551e` | **no binding written, foreign-owner, no leak** |
| B2 harness cases 2, 3 | `9b1a551e` | **still correct** |
| `tests/test_worktree_derivation.py` | `9b1a551e` | **unedited** |

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

py .agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/m4_differential.py
```

**Build your own instrument before you run theirs.** This is the third time on
this gate that the decisive finding came from a reviewer holding an independent
number when someone else's harness printed confirming rows. Both harnesses in
`/tmp` are pinned to revisions the tree has moved past — useful, not
authoritative.

**Two calls, not one.** B4 was invisible to every single-call differential because
the Stop path is unchanged per call. Any check of rework 2 must exercise
**SessionStart then Stop**, with the spine genuinely **inside**
`<project>/.agent-work/*/spine.json` where the scan can find it. A test whose
spine sits outside the glob cannot see this class at all.

**Four environment hazards:**

1. **`CREW_SCRATCH_DIR`.** You are launched through `run_crew.py`, which sets it.
   Lane E's `tests/test_crew_launcher.py::ScratchDirResumeTests` fails for **any**
   agent running the suite from inside a crew-launched session. Scrub it. That
   file is lane E's and fenced. **Do not fix it; do not report it.**
2. **Clear `__pycache__` before every measurement** — a stale cache fails
   `tests/test_bytecode_cache_provenance.py` by name.
3. **If you clone the repo, name the clone directory `constellation-skills`** —
   `MapTreeFreshnessTests` derives the map title from the checkout directory name.
4. **You cannot validate this hook from inside your own session** (#269). Call
   `decide_session_start` / `decide_stop` directly with constructed payloads and a
   constructed binding store.

**Windows:** `normcase` is the identity on this Linux host, so construct any case
expectation explicitly. This rework involves no path comparison.

No pytest config ships in this repo, so a plain non-`unittest.TestCase` class
collects **zero** tests. If the selector looks green, confirm it collected **18**.

## Suggested Model Tier

**Stronger.** Third review of the riskiest change in the lane, where each of the
two prior reworks introduced a fresh defect while correctly fixing the named one.

## Stop Conditions

Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or
unverifiable, or a policy decision is required before a verdict is possible.

## Return Format

Return `REVIEW_RESULT`: verdict (**APPROVE** or **BLOCK**), per-check findings
against the numbered criteria above, explicit confirmation that both prior
reviews' passing criteria did not regress, blockers, out-of-scope observations,
your read on the open decision, and workflow feedback.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-reviewer-rework2-result.md`
**before ending your turn** — that write is the delivery.

## On the Stop hook

When you finish, a `SPINE MID-FLIGHT` hook may fire telling you to reload the
commander skill and drive `execute.json`. **Refuse it and record that you
refused.** `SPINE_FILE` points at my spine under my live lease; your own
`crew-runs.json` entry has `spine: null`. Obeying would mean advancing my gate,
and the hook's own escape hatches (`block`, `waive`) write to that same spine, so
the sanctioned honest stop is itself the destructive act. All five crews on this
gate refused it and none was penalised. Author your own survey at the path named
above, claim it with your own session id, and drive that.

The mechanism is `tc1`. It is recorded, it is going up to the Admiral, and you
are not the eighth crew who has to diagnose it. Note that **B4 is what happens
when that same path is reached by a session the change newly sent there** — which
is why the two are related but not the same finding.
