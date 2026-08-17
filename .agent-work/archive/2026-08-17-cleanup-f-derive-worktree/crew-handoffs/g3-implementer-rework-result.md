# Implementation Result — g3 rework 1

## Assigned gate

`g3` rework 1 — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. **Diff base read with `git rev-parse HEAD`:
`06e23b894bb6f8eef7c16ae58db127c165e954ad`** — two `.agent-work`-only commits
past the `e3e50a69` the handoff names, and the hook itself is unchanged between
them (`git log -1 -- scripts/hooks/spine_rail.py` → `e3e50a69`).

Three blockers, fixed. Nothing else touched.

## Completed slice

### B2 — `decide_session_start` now selects by binding-key provenance

The defect was real and the reviewer's account of it is exact. `session_view`
merges the bare `sid` **plus every `sid#<agent_id>` key**, and Agent-tool
subagents share their parent's `session_id`, so another **agent's** entry is in
the merged view by construction — the shipped comment's "a per-agent key **of its
own**" conflated *of this harness session* with *of this agent*, and the site
then took `sid_bindings.values()`' first entry, which is dict order.

The site now asks the same question `decide_stop` asks: prefer the entry whose
`session_view_provenance` key equals `binding_key(payload)`. With no `agent_id`
in the payload `binding_key` yields the bare `sid`, which selects the session's
own top-level claim and ignores its crews'.

**Extracted, not duplicated — and I want to say why, since the handoff left it to
me.** The reviewer proposed `_select_entry_for(mid_flight, owners, own_key)`. I
extracted `_own_entries(candidates, owners, own_key)` instead: *the subset the
acting agent owns, in the order given*. It fits both sites verbatim because both
candidate sequences carry the abs spine path at element `[0]` — `decide_stop`
passes its `(spine_path, spine, aid)` tuples, `decide_session_start` passes the
merged view's `(spine_path, entry)` items — so the comparison genuinely is one
function and cannot drift.

What I deliberately did **not** fold in is the **fallback**. `decide_stop` must
still answer a stop that blocks regardless, so it keeps `(own or mid_flight)[0]`
and renders the foreign-owner wording; `decide_session_start` blocks nothing, so
owning none of the visible entries hands out no gate from the binding at all.
Unifying those two would put one site's answer in the other site's mouth — which
is the defect class this gate exists to end. The extraction is the *comparison*;
the fallback is each site's own, and the module header now says so.

`_entry_mid_flight_view` is untouched: mid-flight remains a property of the
spine, it reads no payload, and every open gate visible to the session still
blocks.

### B1 — the differential can now fail

`BASE_REV` was `git rev-parse HEAD`. Fixed at the root rather than at the
symptom:

- `BASE_REV = "999b7663"` — the gate's base, pinned, which is what the docstring
  always claimed. I chose the hardcoded pin over "parent of the commit that last
  touched the hook" deliberately: that derivation is honest today and becomes
  **wrong** the moment this rework is committed, because the parent of the rework
  commit is the post-change `e3e50a69`. It would have re-introduced the same class
  of silent degradation one commit later.
- A **third arm**, `BLOCKED_REV = "e3e50a69"` — the commit the reviewer refused —
  so the regression and its repair appear in one table instead of two runs a
  reader must reconcile.
- `_assert_arms_are_what_they_claim` identifies each arm by **symbols the changes
  moved**, not by a commit id anyone has to trust: BEFORE has `_foreign_worktree`
  and neither new symbol; BLOCKED has `_is_own_entry` but not `_own_entries`;
  AFTER has both; and all three sources differ pairwise.

**The guard was demonstrated to fail, not asserted.** Repointing `BASE_REV` at
`e3e50a69` → `REFUSING to print a differential that cannot fail: BEFORE lacks
_foreign_worktree / BEFORE already has _is_own_entry / BEFORE and BLOCKED are
byte-identical`, exit 1. Repointing `BLOCKED_REV` at `999b7663` → three
symmetric complaints, exit 1.

Full re-run output: `crew-handoffs/g3-implement-rework/m4-differential-before-after.txt`.
The rows the criterion asks to spot-check now read honestly:

| row | BEFORE (999b7663) | BLOCKED (e3e50a69) | AFTER |
|---|---|---|---|
| S3 own claim, other tree | **ALLOWED** | BLOCK, own-gate | BLOCK, own-gate |
| S4 crew in own tree | **ALLOWED** | BLOCK, foreign-owner, NOTHING | BLOCK, foreign-owner, NOTHING |
| S8 case/separator | **ALLOWED** | BLOCK, own-gate | BLOCK, own-gate |
| **S9 crew claimed first, parent restarts** | no context | **INJECT CREW-MARKER** | **INJECT PARENT-MARKER** |
| **S10 same binding, parent's key first** | no context | INJECT PARENT-MARKER | INJECT PARENT-MARKER |
| **S11 only a crew's key exists** | no context | **INJECT CREW-MARKER** | **no context** |
| **S12 payload names agent B** | no context | **INJECT AGENT-A-MARKER** | **INJECT AGENT-B-MARKER** |

S1, S2, S4–S8 are identical BLOCKED vs AFTER: the Stop path did not move.

### B3 — the false claim, and five more like it

The section header's *"Ownership is decided by binding-key provenance at both
former call sites"* is now **true**, and I confirmed it by reading both sites
rather than assuming the fix discharged it. I rewrote it anyway, to state the
rule instead of asserting a property one site did not have.

Reading whole rather than by symbol found five more sentences that had gone
false, **two of them mine**, written during this rework:

1. `_is_own_entry`'s `own_key is None` bullet said "the stop still BLOCKS" —
   decide_stop-only wording now that both sites call it.
2. `decide_session_start`'s "NOT symmetric with decide_stop's ownership decision,
   deliberately" passage — its whole argument inverted; replaced.
3. The test class docstring's "giving them different trees proves nothing about
   this change" — true of the Stop site, **false** of the SessionStart site,
   where the differing-tree case is exactly where the deleted test did real work.
4. *(mine)* "BLOCKING is a property of the spine at both sites" — vacuous at a
   site that never blocks; narrowed to "at the one site that blocks".
5. *(mine)* "a SessionStart ... hands out nothing" — it still falls through to the
   blind scan; narrowed to "no gate from the binding".
6. *(mine)* "that is the #549/#419 failure at the other call site" — it is at
   **this** site. And two claims about captures ("no `agent_id` in any capture
   anyone has taken") narrowed to what the pinned capture actually covers, which
   is PostToolUse only.

## Files changed

- `scripts/hooks/spine_rail.py` — `_own_entries` added; `decide_session_start`
  selection; `decide_stop`'s selection line routed through the shared helper
  (no behaviour change there); prose.
- `tests/test_spine_rail.py` — 6 new methods in `OwnershipIsBindingKeyNotWorktree`
  (8 → 14); 2 pre-existing tests rewritten (see **the collateral** below); class
  docstring.
- `.agent-work/.../crew-handoffs/g3-implement/m4_differential.py` — B1.
- `map/INDEX.md` — regenerated with `py -m scripts.code_map build`, never
  hand-edited (#544): `scripts` 1224 → 1225 (`_own_entries`), `tests` 4843 → 4850.
- `.agent-work/.../crew-handoffs/g3-implement-rework/**` — this run's plan and
  evidence. **Nothing committed**, per the handoff.

`tests/test_worktree_derivation.py` unedited (`git diff --quiet` passes) and
green. No excluded file touched: no engine, template, installer, lane A or lane E
file, no `scripts/verify_worktree_isolation.py`, no fail-closed refusal, no `cwd`
threading. Import block byte-identical, 11 stdlib imports.

**Not mine, seen in `git status`:** `.agent-work/cleanup-f-derive-worktree/REPLAN_INPUT.json`
carries uncommitted D16/D17 entries in the Commander's own voice, written during
my run. I did not touch it.

## The collateral that needs your eye

**Two pre-existing tests asserted the behaviour B2 ends.** They and the fix
cannot both stand:

- `test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key`
- `test_session_start_composite_key_entry_still_renders_full_imperative_unchanged`

Both build the reviewer's **case 3 in same-tree form**: a subagent claims under
`sid#agent_id`, then a bare SessionStart expects to resume from it. They passed
before only because the payload's `cwd` matched the recorded worktree — the old
answer was tree-dependent, exactly like case 2's. The second one's docstring even
says it is guarding a site that was "explicitly out of scope for this gate"; that
fence is what this gate removed.

I rewrote both to the new rule and I claim they are **not weakened**: each still
asserts #419's read-through *directly* (the entry IS in `session_view`, and
`session_view_provenance` attributes it to the composite key — the old tests only
implied this), and the first adds a round trip proving the entry is still
reachable by the agent that owns it. What changed is who gets answered with it.

**The alternative I rejected:** fall back to the leading entry when the session
owns none. That leaves both tests untouched — and leaves case 3 unfixed, against
this handoff's own Close Criteria. Any rule that resumes a bare session from
another agent's entry recreates case 3; they are mutually exclusive. If you
prefer the other side of that trade, this is the decision to reverse, and it is
one line.

## Test mode

**Required:** TDD, again. **Satisfied.**

- **Red** (`m1-red.txt`), against the committed hook: **8 failed, 11 passed, 152
  deselected**. Case 2 answered with `CREW-MARKER`; case 3 injected the crew's
  gate where it must inject nothing; **case 6 sub-failed *only* on the
  crew's-key-first ordering and passed parent-first — the write-order proof
  itself**; the payload-identity case answered agent A when the payload named
  agent B; the unidentifiable-agent case handed out the entry on all four rows.
- **Green** (`m2-green.txt`): **14 passed, 152 deselected, 21 subtests passed.**
- The class subclasses `unittest.TestCase`, as my predecessor got right.

Every SessionStart case asserts `_scan_active_spine(proj) == []` **before**
acting, so a green cannot be the blind scan answering by luck.

## Evidence

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py -k OwnershipIsBindingKeyNotWorktree
# 14 passed, 152 deselected, 21 subtests passed        (m2-green.txt)

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py tests/test_worktree_derivation.py
# 184 passed, 1 skipped, 21 subtests passed

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q
# 3183 passed, 5 skipped, 1204 subtests passed, 0 failed   (m5-full-suite-after.txt)

py .agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/m4_differential.py
# three pinned arms, guard demonstrated able to fail   (m4-differential-before-after.txt)
```

**Floor, re-measured myself at my actual HEAD before editing** (cache cleared,
`SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`/`CREW_SCRATCH_DIR` scrubbed): **3177
passed, 5 skipped, 0 failed** — matching the handoff exactly. **After: 3183
passed, 5 skipped, 0 failed.**

**Delta +6, and it accounts for every test:** 6 new methods (8 → 14), 2 tests
renamed and rewritten in place (net zero), **no deletions**. Subtests +12 = 2
(write-order) + 4 (withhold) + 6 (inert location). Failure distribution derived
mechanically on **both** sides (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`):
empty, 0 `FAILED` lines each (`m5-suite-arithmetic.txt`).

**Close criteria, each answered:**

1. **Cases 2, 3 and 6** — fixed, pinned, shown failing before and passing after.
   Case 6 no longer depends on write order (S9/S10 agree; the red proves they did
   not).
2. **Selection by provenance, blocking unchanged** — `_entry_mid_flight_view`
   untouched; every Stop row identical BLOCKED → AFTER.
3. **Fail-safe at the new site, demonstrated with garbage** — a malformed
   `agent_id` (`a/b`, empty, wrong type, explicit null) makes `binding_key`
   refuse, nothing is attributable, and the session is told nothing from the
   binding. Separately, garbage in the *location* fields (`cwd` absent/int/dict,
   `worktree` null/int/empty — 6 rows) must not cost a session its own resume,
   and does not. **Withholding here is not blocking** — SessionStart never blocks
   — it is declining to hand out a gate, which is the fail-safe direction where
   the failure mode is being told to drive someone else's run.
4. **Newly blocks / newly resumes differently** — enumerated with intent in
   `m5-what-newly-blocks-and-resumes.md`. Nothing newly blocks in *this* rework;
   four SessionStart rows newly resume differently.
5. **Differential** — pinned, guarded, guard proven able to fail, output pasted.
6. **Prose** — every sentence in the changed regions read whole; six repaired.
7. **The eight existing class tests** — all still green and unweakened; they are
   8 of the 14.
8. **Suite** — green, cache cleared, clean env, count stated, distribution
   derived mechanically.

**Windows:** nothing in either ownership decision folds case or separators —
session and agent ids are opaque harness tokens compared for exact equality, and
`_AGENT_ID_ALLOWED` forbids a separator in an agent id outright. The existing
platform test **constructs** its expectation (`normcase` folding asserted true
only on `win32`) rather than inheriting it from this host, and the verdict is
asserted `block` on both platforms. My new cases involve no path comparison at
all. `_worktree_from_spine` still folds case; that is a location question and its
shared case table is unedited and green.

**Reviewer's case 1** (in-tree crew claimed first, parent restarts) — the handoff
said it was pre-existing, not mine to close, and that fixing it might fall out.
**It does fall out**: the parent's own bare-key entry is now selected whether or
not the crew shares its tree. Nothing was widened to reach it.

## My read on the decision formulation

**The reviewer is right, and I would record its formulation over my
predecessor's.**

> Blocking is a spine property at both sites; selection is a binding-key property
> at both sites.

My predecessor's asymmetry was half right, and the right half is real: mid-flight
genuinely *is* a property of the spine, `_entry_mid_flight_view` should read no
payload, and every open gate should block. That insight stands and I kept it.

But it answered the wrong question. Both sites also choose **which entry to speak
about**, and that is one question with one answer. The proof is that my
predecessor's own comment in `decide_stop` states the governing rule, and the
sentence is true verbatim of `decide_session_start`:

> Order alone would hand a Commander whichever entry happened to be claimed
> first — routinely its in-tree crew's, whose gate is precisely the one it must
> not be told to drive.

I would record it with one refinement the code now makes explicit, because
"symmetric" invited the wrong inference once already and I would rather it not
invite it again: **the comparison is shared; the fallback is not.** What a site
does when the acting agent owns nothing follows from the blocking half of the
rule — a Stop blocks either way so it must still name *something*, a SessionStart
blocks nothing so it names nothing. That is a consequence of the rule, not an
exception to it. `_own_entries`'s docstring and the module section header both
carry that wording now.

## Assumptions

- **A SessionStart payload may or may not carry `agent_id`; the change is correct
  either way.** The pinned capture is PostToolUse only. The site asks
  `binding_key`, the single composer, so an absent `agent_id` yields the bare
  `sid` — the top-level reading — and a present one is honoured instead of
  ignored. No test claims the harness sends it at SessionStart.
- **A session that owns nothing still falls through to `_scan_active_spine`.**
  That path reads no binding key and is `tc1`, which the handoff declared out of
  reach. My tests are constructed so it cannot manufacture a pass, and I did not
  touch it.
- **Rewriting the two `#419`-era tests is inside my latitude** ("what precisely
  replaces the skip at each of the two call sites"), because the fix the handoff
  specified is unimplementable while they stand. Flagged above rather than
  buried, since it is the one place I changed a claim someone else made.

## Stop conditions hit

None. Allowed scope was sufficient, no exclusion needed touching, all required
evidence was producible.

## Out-of-scope observations

The three the handoff recorded as **not mine** (`tc1` scan-bind, `agent_id: null`
on Stop, `bind()`'s `None`→`str(project_dir)` substitution) I did not chase and
do not re-report — except to note that my new withhold test is scoped explicitly
around `tc1`, and its docstring says so, so a later reader does not mistake the
scoping for an oversight.

One new, small: **`test_garbage_location_data_never_relaxes_the_rail`'s "null
worktree" row still proves something other than its label** (the reviewer's
`tc3`) — I left it, since repairing it means changing `bind()`'s helper behaviour
for a row that is already recorded. My own inert-location test has the same row
and the same caveat, and it is honest either way: the point there is that
location data cannot cost a session its resume, which holds whatever `bind()`
substitutes.

## Workflow feedback

- **What the handoff got right, and it is worth saying:** it gave me the
  reviewer's constructed cases *as a table with expected values*, and told me to
  read `/tmp/g3rev/c4_session_start.py` rather than re-derive. That script showed
  me in one read why case 3's OLD answer was "no context" — the crew's spine sat
  outside the scan's glob — which is the single fact my whole test construction
  turns on. Ten minutes saved and a wrong test avoided.
- **The one thing that would have saved the most time:** the handoff says to fall
  back "to today's behaviour only when the session owns none". Read literally
  that means *the leading entry*, which leaves case 3 unfixed and contradicts the
  Close Criteria two paragraphs later. The reviewer's own wording has the same
  ambiguity. What both must mean is *the pre-existing fall-through to the scan*.
  I resolved it toward the Close Criteria; naming the fallback explicitly would
  have removed the only real ambiguity in this dispatch.
- **The collision was foreseeable from the handoff and was not foreseen.** Two
  shipped tests assert exactly what B2 forbids. The handoff's Close Criteria say
  "the eight existing class tests stay green" but say nothing about the rest of
  the file, and I do not think anyone knew. A line in the reviewer's BLOCK — "the
  fix will break `test_session_start_resumes_from_a_spine_bound_only_under_a_
  composite_key`" — would have turned my largest judgement call into a confirmed
  instruction. It is the sort of thing the *reviewer* is best placed to see,
  having read all eight reworked tests looking for weakening.
- **`grep for the claim, not the symbol` earned its place again, on my own
  prose.** Three of the six false sentences I repaired were written by me, in
  this run, an hour earlier. The discipline that catches that is re-reading the
  block whole *after* the code settles, not while writing it.
- **Instructions improvised around** (fourth crew on this issue to report it):
  the implementer skill opens with "a spine is bound for you; `spine_status` is
  your first call". My `crew-runs.json` entry has `spine: null` while
  `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` point at the **parent Commander's**
  spine under the parent's live lease, so obeying literally means driving someone
  else's gate. I authored my own plan at
  `crew-handoffs/g3-implement-rework/IMPLEMENTER_PLAN.json`, claimed it with my
  own session id, drove all seven items through the `checklist_engine.py` CLI,
  and wrote nothing to the parent spine.
- **Engine friction, minor:** `attest` takes `--cond`, but the natural spelling
  `--condition` fails with a bare usage error. One retry, no harm.

## Map impact

- **Structural:** `_own_entries` **added** beside `_is_own_entry`, 2 call sites
  (`decide_stop` selection, `decide_session_start` selection).
  `decide_session_start` gained `session_view_provenance` + `binding_key` reads —
  it had neither before, which is the substance of B2.
  `_entry_mid_flight_view`, `_same_path`, `_worktree_from_spine` unchanged.
- **Capabilities:** `scripts.hooks.spine_rail` — SessionStart resume-context
  selection. Stop refusal unchanged by this rework.
- **Constraints honoured:** stdlib-only (import block byte-identical, printed by
  the differential); fail-safe not fail-open, now demonstrated at *both* sites;
  #549's two-way rendering intact; nudges keyed by `sid` alone; derivation table
  unedited.
- **Decisions:** `worktree-is-location-spine-path-is-identity` now holds at both
  call sites in both their blocking and their selection decisions. The gate's
  `@grade: placeholder` decision — *what replaces the skip at each call site* — I
  argue above should be recorded in the reviewer's formulation, refined with
  "the comparison is shared; the fallback is not".
- **Claims/evidence:** cases 2, 3, 5 and 6 are pinned by tests; the three-arm
  differential is re-runnable and self-guarding.

## On the Stop hook

**I refuse it, and I am recording the refusal here as instructed.**

Measured rather than assumed: `SPINE_FILE` →
`.agent-work/cleanup-f-derive-worktree/spine.json`; `SPINE_SESSION` →
`constellation/cleanup-f-derive-worktree/execute/commander`, not mine;
`SPINE_PARENT` → `constellation/cleanup-f-derive-worktree/execute/commander/attempt-4`.
My own `crew-runs.json` entry has `spine: null`. Obeying a `SPINE MID-FLIGHT`
nudge would mean advancing my parent's gate under my parent's live lease, and the
hook's own escape hatches (`block`, `waive`) write to that same spine — so the
sanctioned honest stop is itself the destructive act. **I wrote nothing to the
parent spine.**

Worth one line for the record, since this gate is about exactly this: what I
changed today would not have prevented this nudge. It comes from the parent's own
session state via the mechanism in `tc1`, not from a binding of mine. What
binding-key provenance now prevents is the adjacent failure — an agent that
*has* a binding being answered with another agent's gate — at both call sites
rather than one.

## Return status

complete
