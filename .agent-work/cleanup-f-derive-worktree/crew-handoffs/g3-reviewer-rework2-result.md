# Review Result — g3 rework 2

## Assigned Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`.

Survey driven at `.agent-work/cleanup-f-derive-worktree/g3-review-rework2/review.json`
— 16 checks (the 7 standard reviewer items plus this handoff's 8 Close Criteria
and the open decision as their own checks), claimed under session
`constellation/cleanup-f-derive-worktree/g3/reviewer/attempt-3`, every item
visited and recorded, consolidated through the engine.

**Revision note, first, because every number below depends on it.** The handoff
pins rework 2 at `9b1a551e`. That commit is **not an ancestor of HEAD** — it was
amended into `7d12c29d` (same parent `b9709cfe`, committer timestamp 11 seconds
later) and now survives only in the reflog. `git diff 9b1a551e 7d12c29d` is
**empty across the whole tree**, so the content is identical and every number in
the handoff transfers unchanged. I measured at `HEAD = c5ad8d61` (hook file
byte-identical to `7d12c29d`), and my instrument asserts the working tree is
byte-identical to HEAD's blob before it prints anything.

## Result

`BLOCK`

**One blocker, new, in production code, measured through production writers.**

The good part first, because it is most of the change and it is right. **B4 is
fixed.** The condition is the one the last review named, the #261 path is intact
and pinned, the four new tests are genuine two-call sequences with the spine
in-tree, the rewritten pre-existing test lost no claim, the suite arithmetic
reconciles with an empty deletion set, and nothing the first two reviews approved
regressed. Two classes beyond B4 improved in the same direction: the
malformed-`agent_id` payload no longer gets an ownership record for an agent
`binding_key` had just declined to identify, and the ambiguous 2+-spine case no
longer renders a foreign gate as advisory context.

Then it leaves B4's own class open through a second door.

## Per-check findings against the handoff's Close Criteria

| # | criterion | verdict |
|---|---|---|
| 1 | B4 actually fixed, measured, minding the harness pin | **PASS** |
| 2 | the #261 path still works | **PASS** |
| 3 | `not owned` is the right discriminator | **FAIL — B5** |
| 4 | the withhold returns `{}` rather than falling through | **PASS** |
| 5 | the one pre-existing test rework 2 rewrote | **PASS** (with one observation) |
| 6 | nothing from either prior review regressed | **PASS** |
| 7 | suite arithmetic reconciles against the diff | **PASS** |
| 8 | prose | **FAIL** (five recurrences; one of them licensed B5) |
| — | the open decision, argued by four crews | **the refinement does not survive** |

Standard items: handoff compliance **FAIL** (one Close Criterion), scope
**PASS**, evidence **PASS**, quality vs inherited rules **FAIL**, reconciliation
**FAIL**, Fowler pass **PASS**.

### 1 — B4 is fixed. PASS

**I built my own instrument first and ran it before anyone else's**, as the
handoff insisted, and I did not re-run either `/tmp` harness until my own number
was in hand. It is now durable, in the workbench rather than in `/tmp`:
`g3-review-rework2/rev3_instrument.py` → `rev3-matrix.txt`.

Three arms extracted and pinned by me (`999b7663` / `6bba3fd2` / `c5ad8d61`),
six cells, each a **SessionStart then a Stop over one shared store** with the
spine genuinely inside `<project>/.agent-work/*/spine.json`, plus a
no-SessionStart control row for every cell. Markers are pairwise
non-substring, so no cell can print another's marker — the defect that made two
of review 1's six cases unreadable.

**The arm guard is behavioural, not symbolic.** This rework adds no symbol, so a
symbol check would happily pass with two identical arms loaded; mine refuses to
print unless the arms differ **by hash** *and* the `REWORK1` arm actually
manufactures the B4 binding while the `HEAD` arm does not. It also asserts the
working tree is byte-identical to HEAD's blob. (Which is the shelf-life hazard
the handoff names, now pointed at my own harness: `c5ad8d61` will stop being
HEAD, and when it does my guard **fails visibly** rather than printing a stale
confirming row.)

The B4 cell — crew owns the in-tree spine under `sid#agent`, parent owns nothing:

| arm | SessionStart wrote | SessionStart rendered | the later Stop | leaked |
|---|---|---|---|---|
| PREGATE `999b7663` | nothing | the crew's gate | foreign-owner | no |
| REWORK1 `6bba3fd2` | `binding[sid]` → the crew's spine | the crew's gate | **own-gate** | **YES** |
| **HEAD `c5ad8d61`** | **nothing** | **nothing** | **foreign-owner** | **no** |

Identical to the no-SessionStart control. B4 is closed.

I did not hit the pin trap the handoff warned about, because I never ran
`/tmp/g3rev2/rev2_composite.py` as an oracle — my own arms are pinned by me and
guarded by behaviour.

### 2 — the #261 path still works. PASS

Tested, not read. Empty binding, exactly one active-leased in-tree spine: HEAD
still binds under the **bare** `sid`, still injects the `RESUMING` context with
the scanned gate's imperative, and the **next call reads the write back as OWN**
and blocks with that imperative. Byte-identical behaviour to both older arms on
this cell. B4 was not traded for #261.

### 3 — `not owned` is the wrong discriminator. FAIL — B5

See **B5** below. This is the blocker.

### 4 — returning `{}` is right. PASS

I re-measured the fall-through myself rather than accepting the quoted render:
on the B4 cell both older arms inject the crew's gate as advisory context, and
that context ends *"Pick the run back up at this gate and drive it through the
engine"* — the same imperative `decide_stop`'s foreign-owner branch refuses to
render. Falling through would have fixed half of B4.

**Who newly gets nothing**, enumerated from my own matrix rather than from the
result doc — every session with a **non-empty** view owning **none** of it:

1. one in-tree spine (the B4 class) — previously also got a written binding;
2. 2+ in-tree spines — previously got the first match's context, no binding;
3. a payload whose `agent_id` `binding_key` refuses (#441) — previously got an
   ownership record for an agent the hook had just declined to identify;
4. `tc5`'s collision loser.

None legitimately needs a binding: a spine this session had claimed would be in
its view **and** owned, because the claim writes under the very key the
comparison reads. (4) is a real, narrow loss and is already recorded as `tc5`.
One consequence I checked rather than assumed: such a session now gets **no
SessionStart output at all**, indistinguishable from the hook being absent.
Acceptable — the only thing it could have said was about another agent's run —
but worth naming.

### 5 — the rewritten pre-existing test. PASS, with one observation

`test_session_start_bind_on_resume_still_writes_under_the_bare_key`, claim by
claim against `6bba3fd2`'s version:

| claim | fate |
|---|---|
| resume context injected (`ONLY-MARKER`) | kept |
| outer keys exactly `{composite, sid}` | kept |
| the scanned spine's `engine_session` is `eng-alone` | kept |
| the composite key's contents untouched | kept |
| `list(binding[sid].keys()) == [sp]` | → `set(...) == {own_spine, sp}` |
| — | **gained**: one-harness-session, outer key ORDER, #202's sibling merge |

The changed assertion is weaker in shape but not in exactness — still a set
**equality** over the bare key's whole contents. Nothing was lost. The new
fixture reaches the same code path, proven by the test's own two post-conditions
rather than by reading: the own entry is unreadable, the loop leaves `spine`
None, the scan-bind fires.

**The observation that matters:** this fixture is **B5's topology minus one
step**. Its outer key order is exactly the leaking order, and the only reason it
does not leak is that the surviving in-tree spine is claimed by *nobody* in the
store (`eng-alone`) rather than by the visible sibling. Had `run-sub`'s spine
been the survivor, this test would be asserting B5's leak as correct behaviour.

### 6 — nothing from either prior review regressed. PASS

The production delta `6bba3fd2..HEAD`, derived mechanically by stripping comment
lines from the diff, is **exactly three lines**: hoist `owned`, iterate `owned`,
and the new condition. `decide_stop`, `_entry_mid_flight_view`,
`_scan_active_spine`, the nudge block and the import block are untouched.

- B2's cases — re-ran `/tmp/g3rev/c4_session_start.py` at HEAD (its NEW arm reads
  the working tree, so it does measure this fix): case 1 PARENT, 2 PARENT, 3 no
  context, 6 PARENT (order-independent). All the correct OLD behaviour. Cases 4
  and 5 remain unreadable for the recorded substring reason.
- The Stop path — unchanged by construction (no diff) and unchanged by
  measurement (every Stop row).
- Fail-safe at both sites, nudge keyed by `sid` **alone**, #549's two-way
  rendering — held, and #549 is strengthened on the B4 cell.
- Stdlib-only import block — byte-identical, printed by the differential.
- `_own_entries` still shared — exactly 2 production call sites (1658, 1747).
- `tests/test_worktree_derivation.py` — unedited across the **whole gate**
  (`999b7663..HEAD` empty), and green.
- The differential's guard — `m4_differential.py` exit 0, guard accepting, all
  rows as recorded.

**Caveat, stated as scope rather than as a finding:** none of those instruments
can reach B5, because every SessionStart row in all of them places its spines
outside the scan's glob. They are correct and they are blind here.

### 7 — suite arithmetic reconciles. PASS

Full suite at HEAD, `__pycache__` cleared and `SPINE_*`/`CREW_SCRATCH_DIR`
scrubbed: **3187 passed, 5 skipped, 1208 subtests, exit 0** — my own run.
Targeted selector: **18 passed**, 152 deselected, 25 subtests, so it really
collected 18 rather than reading green at zero.

For the quiet-deletion risk the criterion names, I did not compare counts — I
diffed the **set of `def test_*` names across the entire `tests/` tree**:
2923 → 2927, **+4**, and the **removed set is EMPTY**. The four added are exactly
the four new methods; the rewritten test kept its name and appears in neither
set. 3183 + 4 = 3187.

### 8 — prose. FAIL

Five recurrences, and one of them is the sentence that licensed B5. Read whole,
sentence by sentence, against the tree as it stands.

1. **`decide_session_start`, the branch comment** — *"An OWN entry whose spine is
   merely unreadable also lands here … **this agent is contradicting no one**,
   and whether the scan should bind a session to a spine **nobody claimed** is a
   separate open question."* Both halves are false in the topology I reproduced:
   the store visibly records a sibling agent's claim on the very path the scan
   then files under this agent's bare key, and the write flips provenance so the
   crew loses its own gate. **This is not a describing error — it is the argument
   that scoped B5 out of the fix.**
2. **Module comment, ~line 700** — *"a SessionStart blocks nothing and so hands
   out nothing."* Unqualified and false: the site still hands out the scanned
   gate **and writes a binding** whenever the agent owns any entry that does not
   load. The same comment then frames the code as a two-way split when the code
   is three-way, and the third case is where B5 lives.
3. **`_own_entries` docstring** — *"The one thing an empty result must NOT do at
   either site is reach a writer."* False as written, and contradicted by its own
   next sentence: on #261's path `_own_entries` returns `[]` and the writer is
   reached, by design.
4. **A test NAME** — `test_a_restarting_parent_is_never_bound_to_its_in_tree_crews_spine`.
   The universal is falsified by my production-writer sequence. A false test name
   is the worst placement of this defect, because the name is what the next
   reader greps.
5. **`test_bind_on_resume_is_withheld_only_when_the_session_owns_nothing_visible`
   docstring** — *"the discriminator, stated as the two-by-two it actually is."*
   It is not: the third row (non-empty view, owns something unreadable → **binds**)
   is missing, and its claim that the two rows stop the fix drifting *"back into
   always bind (which is B4)"* is precisely what B5 disproves.

The shape the last review found holds again: **every sentence that keeps a
qualifier is true, every sentence that drops one is false.**

## Blockers

### B5 — the withhold is gated on the wrong term, and B4's class is still reachable through the `owned` door

`scripts/hooks/spine_rail.py:1782`

**The mechanism.** The guard is
`if spine is None and sid_bindings and not owned: return {}`. `not owned` asks
*"do I own nothing visible?"* But the branch below is reached by **two**
routes, and only one of them is that. `spine` is also left `None` when the
session **owns** an entry whose spine does not load — archived, deleted, moved,
or an entry with no usable `spine` field. There `owned` is non-empty, the guard
does not fire, and the scan-bind writes `binding[bare sid] →` whatever single
in-tree spine the glob turns up — **including one a sibling agent of the same
session visibly claimed.**

**Measured through production writers only** — no hand-built store, every binding
entry written by `handle_post_tool_use` from the repo's own pinned probe capture
(`g3-review-rework2/rev3_production_sequence.py` → `rev3-b5-production-sequence.txt`):

```
1. a crew claims the IN-TREE spine A          -> binding[sid#agent]   (the accepted B4 fixture)
2. the parent claims its own IN-TREE spine B  -> binding[sid]
3. B is archived away                          (routine at closeout)
4. the parent restarts (SessionStart), then stops
```

| arm | parent bound to the CREW's spine | provenance flips | the parent's Stop | leaked |
|---|---|---|---|---|
| PREGATE `999b7663` | **no** | — | foreign-owner | no |
| REWORK1 `6bba3fd2` | yes | to the bare `sid` | own-gate | **YES** |
| **HEAD `c5ad8d61`** | **yes** | **to the bare `sid`** | **own-gate** | **YES** |
| HEAD, control (no SessionStart) | no | — | foreign-owner | no |

The parent is told, verbatim, *"SPINE MID-FLIGHT: gate g3 is still open … Next
imperative: CREWMARK implement the crew gate."* That is #549 verbatim, produced
by the change whose stated purpose is to end it. **And the damage runs both
ways:** the crew's own Stop recognises its own spine in the control and stops
recognising it after the parent's restart — the parent's manufactured binding
takes the crew's gate away from the crew.

**The SessionStart is the only variable.** Two calls, one shared store, spine
genuinely in-tree — exactly the construction the handoff demanded, applied to the
case the fix does not cover.

**A second, independent route to the same leak** (`rev3-b5-reap-route.txt`):
`_reap_binding_entries` drops an outer key whose every entry was reaped
(`if kept:`), and `_resume_mutate` then re-inserts `new_map[sid]` — **at the end
of the dict**. Since provenance is last-key-wins, the reap-and-rebind flips
ownership by itself, with the natural key order. That route is identical on all
three arms, so it is pre-existing and I do not count it against this gate; I
record it because it means the leak does not depend on an unusual claim order.

**Why this is B5 and not `tc1`.** I checked this before writing it up, against
the exact two clauses that made B4 a finding rather than `tc1`:

- *the change widens who reaches the scan-bind* — **yes, measured.** Pre-gate's
  first-readable-entry selection was pre-empted by the crew's readable entry, so
  it never scanned. Ownership-based selection skips that entry and scans. The
  PREGATE row does not bind; the HEAD row does.
- *the binding it writes defeats the Stop path's foreign-owner withholding* —
  **yes, measured**, in both directions.

`tc1` is that the scan-bind exists and binds a session to a spine nobody claimed.
I do not re-report it. B5 is that **this change routes a new class of session
into that writer, and the spine it binds them to is one the store already
attributes to somebody else.**

**Fix, and where it belongs.** Not another reader-side term. Both B4 and B5 are
the **same write** reached by two different reader paths, and a reader-side guard
has now been patched twice and missed a door each time. Guard the **writer**: the
bind-on-resume must refuse to file a spine path that `session_view_provenance`
already attributes to a **different** binding key, and must refuse to overwrite
that attribution. That is narrower than `tc1`'s open authority question — it does
not decide whether the scan should bind at all, only that it may not contradict
an attribution the store already holds — and it closes both doors at once.

**Scoped null.** I tested SessionStart→Stop pairs and the crew's own Stop across
the pair. I did **not** test three or more calls, concurrent sessions racing
`_binding_transaction`, or the gauge writer's reading of a scan-written binding
in the B5 topology.

## Handoff compliance

**FAIL on one Close Criterion.** The code is faithful: the implementer handoff
prescribed the fix verbatim as *"`sid_bindings` non-empty and
`_own_entries(...) == []` → withhold"*, and that is exactly what shipped, inside
scope, without reverting rework 1's selection and without touching
`_scan_active_spine`, `decide_stop` or `_entry_mid_flight_view`. **B5 is a defect
in the specification the implementer was handed, not a deviation from it** — and
the implementer's own Workflow Feedback flagged that this handoff stated the
condition two ways, which is the same ambiguity seen from the inside.

The criterion that fails outright is *"the comment above the branch says what the
code does"*: the comment's justification for the case it excludes is false.

## Scope drift

**PASS.** The rework-2 commit touches `scripts/hooks/spine_rail.py`,
`tests/test_spine_rail.py`, `map/INDEX.md` (regenerated — `tests` 4850 → 4855 =
4 methods + 1 helper; `scripts` unchanged at 1225, correct since the rework adds
no symbol), and workbench artifacts. **No** lane A, lane E, `#610`, template or
`checklist_engine.py` path is touched anywhere in `6bba3fd2..HEAD`, checked by
pattern rather than by eye. Exclusions naming paths outside this worktree are
Commander-verified, not reviewer-verified, and I do not block on them.

One literal-reading note, not a finding: the engine also wrote
`crew-handoffs/cleanup-f-derive-worktree-g3-implement-rework2/{context,mechanical}/`,
which the Allowed Scope's `crew-handoffs/g3-implement*/**` glob does not cover.
Engine side-effects of driving the plan, not hand edits.

## Evidence verdict

**PASS.** Every claimed side-effect reproduced at its source: full suite
3187/5/0, targeted selector 18, differential exit 0 with its guard accepting,
review-1's B2 harness correct at HEAD, `test_worktree_derivation.py` unedited,
map counts consistent, name-set delta +4 with an empty removed set.

One claim did not reproduce as stated — the `9b1a551e` pin, resolved above.
Content-identical, so nothing rests on it, but it is the exact hazard this
handoff warns about, arriving from the third direction: not a moving `HEAD`, not
a stale pin, but **a pin to a commit that was amended out from under it.**

## Code/doc quality

**FAIL.** Held: minimal change (three production lines), no speculative
abstraction, TDD red→green with the sequence test the handoff demanded,
stdlib-only imports byte-identical, no hidden fallback (the new condition only
ever withholds earlier, never widens), Windows not in play (the change compares
no paths — it reads the truthiness of a dict and a list).

Broken: *fail visibly rather than emit plausible wrong output* — the uncovered
case emits a plausible wrong output, another agent's gate rendered as this
session's own, silently. And `constellation-how-to-talk`'s grounding rule, five
times.

## Fowler pass

**PASS**, recorded at
`.agent-work/cleanup-f-derive-worktree/FOWLER_PASS-g3-reviewer-attempt-3.json`
(suffixed, because the template hardcodes one path and seven prior records in
this work-id collide there), rail exit 0, 12 smells visited.

**flagged:** `long-method` (`decide_session_start` at ~130 lines doing five
things — B5 lives in the coupling between its first and fourth parts, and at that
length nothing invites a reader to check it); `data-clumps` (`sid_bindings`,
`owners`, `own_key` travel together as three loose locals, which is why the
discriminator is spelled as raw truthiness on one line and why the third state
has no name); `shotgun-surgery` (one rule restated in four places — four of my
five false sentences are in three different restatements); `divergent-change`
(three unrelated axes of change have landed in that one body on this gate alone);
**`comments-as-deodorant`** (a one-line condition carrying ~30 lines of comment
whose argument for the excluded case is false — the deodorant did not merely fail
to help, it certified the gap).

**overridden, with the standard and reason logged:** `feature-envy` (no binding
module exists to move behaviour to, and the stdlib-only single-file constraint
forbids inventing one); `primitive-obsession` (`binding_key` and `_is_own_entry`
are documented sole authorities, which is how this repo has already chosen to
answer it; a `BindingKey` type would be the speculative abstraction doctrine
forbids).

## Map impact verdict

The structural claims check out against the diff: no new symbol, no new import,
one local and one condition, `_own_entries` still at 2 production call sites,
`_entry_mid_flight_view` / `decide_stop` / `_same_path` / `_worktree_from_spine` /
`_scan_active_spine` unedited. `not-a-weaker-guard` holds as stated;
`worktree-is-location-spine-path-is-identity` is unaffected.

**The one claim that must not go up as recorded** is the new decision anchor:
*"a site that withholds must withhold all the way down its own branch, because
the branch below it writes the key the rule above it reads."* The principle is
right and I endorse it. The code implements it for **one of the two ways that
branch is reached.** Recording it as satisfied would put a general rule in the
map that the tree does not honour — the same failure as the false comments, one
tier up.

## Reconciliation check

**FAIL**, on that anchor. Commander reconciles it before this goes to the
Admiral: either the anchor is recorded as *aspired to and not yet met*, or B5 is
fixed and it is met.

## The open decision, argued by four crews

**The refinement does not survive B4, and B5 is the second measurement against
it.**

Rework 1 held *"the comparison is shared; the fallback is not."* Review 2
rejected the second half and measured B4. Rework 2 accepted the finding, kept the
refinement, and patched **one** entry point into the shared writer. B5 is a
second entry point into the same writer, measured, still open.

The two sites' fallbacks are not private and cannot be made private by naming:
`decide_session_start`'s fallback **writes** the bare `sid` key that
`decide_stop`'s ownership comparison **reads**. They are one mechanism with two
doors.

What survives is the first half, plus a stronger second half:

> **Selection is a binding-key property at both sites. Blocking is a spine
> property at the site that blocks. And because one site's fallback is the other
> site's input, a withholding must hold all the way down its own branch — which
> puts the guard at the WRITER, not at whichever reader path was named.**

Rework 2's own comment states this correctly — *"A withholding that feeds a
writer is not a withholding"* — and then implements it at the reader.

**The disagreement, named as the handoff asked:** rework 1 and rework 2 hold that
the fallback is each site's own business; review 2 and I hold that it is not, and
there are now two independent measurements on our side. I would carry this up as
contested with the disagreement named, exactly as the handoff prefers.

## Out-of-scope observations

- **A triage candidate, flagged in my survey** (the engine numbered it `tc1`
  locally, which collides with this work-id's already-recorded `tc1`; they are
  different things): guard the scan-bind at the **writer** — refuse to file a
  spine path the store already attributes to a different binding key, and refuse
  to overwrite that attribution. Narrower than `tc1`'s authority question and it
  closes both B4's and B5's doors at once.
- The rewritten pre-existing test sits one file-deletion away from asserting B5's
  leak as correct behaviour. Worth a comment there whichever way B5 is resolved.
- I chased none of the recorded findings and re-report none of them: `tc1`,
  `agent_id: null` on Stop, `bind()`'s `None`→`str(project_dir)`, `map/ids.jsonl`,
  `tc5`, `tc6`, `tc7`, and the `CREW-MARKER`/`OTHERCREW-MARKER` substring defect
  in review 1's harness (which I confirmed is still why its cases 4 and 5 cannot
  be read).

## Workflow Feedback

- **The handoff's best instruction is criterion 3, and it is why this review
  found anything.** It did not ask me to confirm the fix; it asked *"is `not
  owned` the correct discriminator, or does it leave a reachable case where a
  session that owns something unreadable still gets bound to a spine it never
  claimed?"* That is the finding, stated as a question, one review before anyone
  measured it. Three handoffs in a row on this gate have done the crew's hardest
  thinking by naming the falsifier. Keep doing exactly that.
- **The pin problem has now bitten from a third direction and the lesson should
  be written down once.** B1 came from a harness pinned to a moving `HEAD`.
  Review 2's harness was pinned to a commit the tree moved past. This handoff was
  pinned to a commit that was **amended out from under it** — content-identical,
  so harmless, but unreachable except through the reflog, which is precisely what
  `global-everyone.md` says a durable pin must not be. The general rule that
  covers all three: **cite a revision AND state the property that makes it the
  right one, so a reader can re-derive the pin when it rots.** My own instrument
  does this — it pins `c5ad8d61` and then asserts the working tree still matches
  it, so it fails visibly rather than confirming.
- **"Build your own instrument before you run theirs" is the single highest-value
  line in this handoff**, and it paid off in a way worth recording: my instrument
  and theirs agree on every cell either can see. B5 was not found by disagreeing
  with a number — it was found by building a cell that no existing harness
  contained, because the handoff told me which construction every prior instrument
  was missing. **Naming the blind spot is worth more than naming the answer.**
- **The one thing that cost me time.** The survey template hardcodes the Fowler
  record path, and the handoff had to warn me about a collision that seven prior
  records in this work-id already demonstrate. The project template does carry a
  `<fowler-pass-record-path>` placeholder, so instantiating correctly is possible
  — but the *bundled* skill template hardcodes `.agent-work/<work-id>/FOWLER_PASS.json`,
  and an agent reading the skill rather than the project overlay will collide
  every time. The two copies have drifted; the bundled one should carry the
  placeholder too.
- **What would have made this easier:** the handoff's Evidence table lists numbers
  re-measured by the Commander at `9b1a551e`. Since that commit is no longer
  reachable by name, a reviewer verifying "was this re-measured at the thing I am
  reviewing?" has to discover the amendment first. Naming the *branch tip at
  dispatch time* alongside the commit id would have removed the question.

## On the Stop hook

**I refused it, and I am recording the refusal as instructed.**

Verified rather than assumed: `SPINE_FILE` →
`.agent-work/cleanup-f-derive-worktree/spine.json`; `SPINE_SESSION` →
`constellation/cleanup-f-derive-worktree/execute/commander`, not mine;
`SPINE_PARENT` → `constellation/cleanup-f-derive-worktree/execute/commander/attempt-4`;
my own `crew-runs.json` entry has `spine: null`. Obeying would mean advancing my
parent's gate under my parent's live lease, and the hook's escape hatches
(`block`, `waive`) write to that same spine, so the sanctioned honest stop is
itself the destructive act. **I wrote nothing to the parent spine.** I authored my
own survey at `.agent-work/cleanup-f-derive-worktree/g3-review-rework2/review.json`,
claimed it with my own session id, and drove all 16 checks through it.

This is the sixth crew on this issue to record the same refusal. The mechanism is
`tc1`, it is recorded, and I did not re-diagnose it.

One thing worth adding to that record, because it is what my own review turned
up: **B5 is `tc1`'s mechanism pointed at a session that a *sibling agent's* claim
is already sitting on.** The nudge I refused and the defect I found are the same
failure seen from two sides — an agent being handed another agent's next
imperative as its own — and B5 is the version where the hook *manufactures the
paperwork* to make the misattribution stick.

### Postscript — it fired after I finished, twice in one turn, and the store explains why

After this result was written, my survey consolidated to `BLOCK` and my own lease
released, the `SPINE MID-FLIGHT` nudge fired with the parent's `execute`
imperative. **Twice, in one turn.** I refused both and wrote nothing to the
parent spine. Re-verified at that moment rather than assumed: `SPINE_FILE` →
the parent's `spine.json`, whose `engine_session` is
`{"session_id": "commander-cleanup-f-derive-worktree", "status": "active",
"claimed_by": "commander"}` — an active lease held by someone else; my own survey
reports `LEASE released` and `DONE: no open items`; my `crew-runs.json` entry has
`spine: null`. This is the **sixth** crew on this issue to record this refusal
and the third to record it firing after an honest, complete finish — which is
evidence for `tc1`'s authority decision: **the nudge is not tied to having work
left.**

I did not use the hook's own escape hatches. `block` and `waive` both write to
the parent's spine under the parent's live lease, so on this configuration the
sanctioned honest stop is itself the destructive act. My honest stop is that my
own survey is `DONE`, its verdict is consolidated, and the result artifact the
handoff names exists — which is the channel my parent actually reads.

**And then the binding store answered the question, which I record as verified
evidence and NOT as a new finding — this is `tc1`, already recorded, and I am not
re-reporting it.** `.agent-work/.spine-rail-binding.json` currently holds **23
distinct bare session-id keys, every single one bound to the same spine** — the
commander's — which exactly **one** session ever claimed. The last key,
`46ffd22d-419a-4288-8ec8-523811f989c4`, matches this session's own harness
session directory: **my own session has been handed an ownership record for a
spine I never claimed**, and that record is what the Stop path then reads as OWN
and renders the commander's imperative from. Six crews have refused this nudge
one at a time; the store shows the mechanism has fired 23 times in this one
work-id.

Two things this does and does not show, stated precisely rather than as irony:

- **It does show** that the scan-bind's write is not a theoretical concern about
  a data shape. It is production state, it accumulates, and it is the direct
  cause of every refusal on this issue. `tc1`'s authority question is not a
  cleanup item.
- **It does not show** anything about whether this change works, and it is not
  B4's or B5's shape. Every one of those 23 keys is a **bare** session id — crews
  here are separate headless processes with their own session ids, so each
  arrives with an EMPTY view and takes the #261 path, which this change leaves
  untouched by design. B4 and B5 need a **composite** sibling key in the same
  session's view, which is the Agent-tool topology, not this one. I checked that
  before writing it down, because "the defect I found is the thing happening to
  me right now" is exactly the claim that would be satisfying and wrong.

## Return status

`BLOCK`
