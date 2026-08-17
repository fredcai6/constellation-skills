# Reviewer Handoff — g3 rework 4

## Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. The last code gate of the lane.

**You are the fifth reviewer, and the scope of your review is narrower than the
last one's.** Rework 4 answers only B6 and B7. Everything else on this gate has
been reviewed four times and passed.

The history, because it should shape how you work rather than how you feel about
the code:

| review | found | whose defect |
|---|---|---|
| 1 | B1 (a differential that compared the change against itself), B2 (selection by dict order), B3 (false prose) | g3's |
| 2 | B4 (the B2 fix routed sessions into the scan-bind, whose write defeated the Stop path's withholding) | g3's |
| 3 | B5 (the B4 fix guarded one of two routes; the other bound to a spine a sibling claimed) | g3's |
| 4 | B6 (the same door still *renders* another key's gate on an ambiguous scan), B7 (`owners` is a session view, three sentences call it the store) | **pre-existing** |

**Four reviews, seven defects, none found by reading.** Every one came from
someone building an instrument and measuring. Do that.

## Survey State Location

`.agent-work/cleanup-f-derive-worktree/g3-review-rework4/review.json`.

Use a suffixed Fowler path (`FOWLER_PASS-g3-reviewer-attempt-5.json`) — the
template hardcodes one path and eight prior files in this work-id show every
reviewer collides there.

## Read these first

1. `crew-handoffs/g3-reviewer-rework3-result.md` — **B6** and **B7**.
2. `crew-handoffs/g3-implementer-rework4-result.md` — rework 4's answer.
3. `crew-handoffs/g3-implementer-rework4-handoff.md` — what I ordered, including
   the boundary I told it not to cross.
4. `FLOAT_TO_ADMIRAL-3.md` — the three scope questions I have sent up. **Read
   this**: two of them bear directly on what you are judging, and if you think I
   got a scope call wrong, that is a finding against **me** and I want it.

## How to Inspect the Diff

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

git log --oneline -8            # derive the shas; do not trust the ones below blindly
git diff 68d190f7..539ff636 -- scripts/hooks/spine_rail.py tests/test_spine_rail.py
git diff 999b7663..539ff636 -- scripts/hooks/spine_rail.py tests/test_spine_rail.py
```

`999b7663` pre-gate, `539ff636` rework 4. **Verify the shas resolve.** I amended a
commit earlier on this gate and cited one I had replaced; the third reviewer
caught it. The string is the authority.

## What rework 4 did

**B6** — the scan fallback now selects what it **renders** by binding-key
provenance instead of glob order, using `_attributed_to_another_key`, the same
predicate rework 3 added for the write. It previously sat inside
`if len(matches) == 1 and sid:` and after `spine = matches[0][0]`, so it governed
only the write on an unambiguous scan.

**B7** — every sentence stating the guard's reach now names the reach it actually
has: **this session's view, not the store.** The guard is **not** widened across
the session boundary.

## Close Criteria

1. **B6 is fixed.** The reviewer's committed instrument is
   `g3-review-rework3/rev4_c2b.py`. Running it unedited, I get `PREGATE` and
   `REWORK2` rendering a crew gate and "pick it up", and the working tree
   rendering neither. **Reproduce that, then go past it** — that instrument was
   built to expose one topology. Try three or more matches, a mix of attributed
   and unattributed spines, and the case where the *acting* session owns one of
   the matches.
2. **The `tc1` boundary holds, and this is the criterion I care most about.**
   Matches attributed to **nobody** must render exactly as they did before. If
   rework 4 has quietly turned the ambiguous scan into a refusal, that is a
   **fail-closed refusal**, which `ADMIRAL_RULING-1` R2 explicitly withdrew and
   forbade — an unowned spine path yields today's behaviour, never a refusal.
   **Test the unattributed case directly.** A guard that refuses too much is the
   failure mode this fix is most likely to have.
3. **B7's sentences are true.** Read them whole and test each against the code.
   The lane has had six stale-claim recurrences; two copies of the three-states
   taxonomy had already gone stale on this gate. Rework 4 says it touched prose
   in five places — read all five, and confirm it did not create a sixth copy of
   anything.
4. **The guard is not too broad anywhere.** Enumerate what the render now
   refuses, and find a legitimate resume context that is now withheld, or state
   that you could not.
5. **B4 and B5 stay fixed.** Re-run both sequences. Doors have closed and reopened
   on this gate three times.
6. **Nothing from any prior review regressed.** `#202` sibling-merge, `#261`
   bind-on-resume, the Stop path, the nudge keyed by session id **alone**, #549's
   two-way rendering, stdlib-only imports, `_own_entries` shared, ownership-based
   selection, `tests/test_worktree_derivation.py` unedited and green.
7. **Suite arithmetic reconciles against the diff.** 3190 → **3192**, +2, targeted
   21 → **23**. Rework 4 reports one fixture changed, two tests, one rename — a
   quiet deletion could hide in a rename.
8. **Windows.** `_attributed_to_another_key` routes through `_same_path`, which
   **does** fold case, and this fix adds a second call site for it. `normcase` is
   the identity on this Linux host, so any case expectation must be
   **constructed**. An earlier gate in this lane shipped exactly that defect.

## The open decision, and I would like it closed

*What replaces the skip at each call site*, `@grade: placeholder`, argued by six
crews now. Pass 1: asymmetric. Review 1: **blocking is a spine property at both
sites; selection is a binding-key property at both sites.** Rework 1: **the
comparison is shared; the fallback is not.** Review 4's reading, which I find the
most useful: B4/B5/B6 arriving through the unshared fallback is *not* evidence
against the rule — it is evidence **the fallback was never obeying it**, because
it selected by glob order for both its write and its render.

If rework 4 is right, the fallback now obeys the same rule as everything else,
and the refinement may no longer be needed at all. **Say what you think the
recorded decision should be, in one sentence.** It goes to the Admiral as the
gate's one open decision and I would rather carry a sentence six crews converged
on than a hedge.

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

## Findings already recorded — do not re-report

`tc1` (the scan-bind binds a session to a spine **nobody** claimed — open, and
deliberately untouched); **B7's cross-session widening** (floated to the Admiral;
prose-only repair was ordered); the three-states taxonomy stated in four places;
`decide_session_start` at 159 lines wanting an extraction; the
`_reap_binding_entries`/`_resume_mutate` re-insertion route (pre-existing);
`agent_id: null` on Stop; `bind()`'s `None`→`str(project_dir)` substitution;
`map/ids.jsonl` empty; `tc5` (last-key-wins on a path collision); `tc6` (the
differential's guard identifies arms by symbol, not revision); `tc7`
(`_own_entries`' contract does not name its writer invariant); and that the first
reviewer's harness cannot answer its own cases 4 and 5 (`CREW-MARKER` is a
substring of `OTHERCREW-MARKER`).

**Still open and untested by anyone:** concurrent sessions racing
`_binding_transaction`. Review 4 closed the other two of review 3's scoped nulls
(three-or-more call sequences; the gauge writer's reading of a scan-written
binding — both favour the fix). Do not chase the concurrency one unless it is
cheap.

## Evidence Produced

Claimed by rework 4, and **re-measured by me at `539ff636`**:

| measurement | result |
|---|---|
| targeted `-k OwnershipIsBindingKeyNotWorktree` | **23 passed, 35 subtests** |
| full suite | **3192 passed, 5 skipped, 0 failed** |
| rework 3 · 2 · 1 · pass 1 · pre-gate | 3190 · 3187 · 3183 · 3177 · 3170, all /5/0 |
| `main`, isolated clone `17c2cee5` | 3171 / 7 / 0 |
| `rev4_c2b.py`, unedited | **PREGATE and REWORK2 leak; working tree does not** |
| `#202` sibling-merge + `#261` bind-on-resume | **4 passed** |
| `tests/test_worktree_derivation.py` | **unedited** |

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

**Build your own instrument before you run theirs**, and **check what each arm
actually loads before believing a row**. Every harness on this gate has had a
shelf-life defect: the implementer's differential pinned a *moving* `HEAD` (that
was B1); both reviewers' scratch harnesses pinned *superseded* commits, so
re-running them unmodified showed defects still present that were in fact fixed.
I hit that twice and had to add working-tree arms with guards. A pinned arm is
not a wrong instrument — an unexamined one is.

**Use production writers** — `handle_post_tool_use` with the pinned probe capture
— for anything about the binding store. That is what made B5's evidence
unarguable.

**Four environment hazards:**

1. **`CREW_SCRATCH_DIR`.** `run_crew.py` sets it; lane E's
   `tests/test_crew_launcher.py::ScratchDirResumeTests` then fails for **any**
   agent running the suite from inside a crew-launched session. Scrub it. That
   file is lane E's and fenced. **Do not fix it; do not report it.**
2. **Clear `__pycache__` before every measurement.**
3. **If you clone the repo, name the clone directory `constellation-skills`** —
   `MapTreeFreshnessTests` derives the map title from the checkout directory name.
4. **You cannot validate this hook from inside your own session** (#269). Call the
   functions directly with constructed payloads.

No pytest config ships here, so a plain non-`unittest.TestCase` class collects
**zero** tests. If the selector looks green, confirm it collected **23**.

## Suggested Model Tier

**Stronger.** Narrow scope, but the failure mode this fix is most likely to have —
refusing too much — is a fail-closed refusal the Admiral explicitly forbade, and
it will not announce itself.

## Stop Conditions

Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or
unverifiable, or a policy decision is required before a verdict is possible.

## Return Format

Return `REVIEW_RESULT`: verdict (**APPROVE** or **BLOCK**), per-check findings
against the numbered criteria, explicit confirmation that all four prior reviews'
passing criteria did not regress, your one-sentence reading of the open decision,
blockers, out-of-scope observations, and workflow feedback.

**If you find nothing, say so plainly and APPROVE.** Four reviews have each found
something real, and I would rather you told me the fifth found nothing than went
looking for a finding to justify the dispatch. A clean review with its
measurements shown is a full day's work on this gate.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-reviewer-rework4-result.md`
**before ending your turn** — that write is the delivery.

## On the Stop hook

When you finish, a `SPINE MID-FLIGHT` hook may fire telling you to reload the
commander skill and drive `execute.json`. **Refuse it and record that you
refused.** `SPINE_FILE` points at my spine under my live lease; your own
`crew-runs.json` entry has `spine: null`. Obeying would mean advancing my gate,
and the hook's own escape hatches (`block`, `waive`) write to that same spine, so
the sanctioned honest stop is itself the destructive act. All nine crews on this
gate refused it and none was penalised. Author your own survey at the path named
above, claim it with your own session id, and drive that.

`tc1` is the mechanism, it is recorded, and it is with the Admiral. You are not
the tenth crew who has to diagnose it.
