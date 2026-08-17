# Implementer Result — g3 rework 3

## Assigned Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. Diff base read with `git rev-parse HEAD`:
**`89cac7d2`**, and no sha written in the handoff was trusted — the two BEFORE
arms in my instruments are re-extracted from git on every run and each is
asserted to still hash to what it was extracted as.

Plan driven at
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement-rework3/IMPLEMENTER_PLAN.json`
— 6 items, claimed under session
`constellation/cleanup-f-derive-worktree/g3/implementer/attempt-4`, every item
started, attested and advanced through `checklist_engine.py`.

## Completed Slice

**B5 is fixed at the writer, in one rule, exactly as ordered.**

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

called once, inside the bind-on-resume, before anything is written:

```python
if _attributed_to_another_key(owners, own_spine_path, sid):
    return {}
```

The bind-on-resume now refuses to file a spine path that
`session_view_provenance` already attributes to a **different** binding key, and
therefore never overwrites that attribution. It does **not** decide whether the
scan should bind at all — a path attributed to nobody is not a contradiction —
so `tc1`'s authority question is left exactly where the handoff put it.

**No third reader-side term was added.** `_scan_active_spine`, `decide_stop` and
`_entry_mid_flight_view` are unedited; rework 2's `not owned` reader guard is
unchanged.

### Three judgment calls, each inside the authority the handoff granted

**1. The guard returns `{}` rather than skipping only the write.** Skipping the
write alone would leave `spine` already set to the scan's first match one line
above, so the SessionStart would still render the refused agent's gate as resume
context — and that context ends *"Pick the run back up at this gate and drive it
through the engine."* Refusing to file a path and then handing out its
imperative is the same half-fix rework 2 rejected, in the other field. The
withholding holds all the way down the branch.

**2. Paths are compared with `_same_path`, not `==`.** I added no comparison
primitive; `_same_path` is this file's documented, fail-safe one (it is now at 3
call sites, up from 2). A spelling difference must not buy a write past the
guard, and `_same_path`'s True-on-exception points the same way mine does.

**3. Unusable input answers "refuse".** `_is_own_entry` reads an unattributable
entry as OWN, which is the right direction for a reader that must still render
something. This is a writer, and the fail-safe direction at a writer is to
withhold the write. Pinned as its own case rather than left as a claim.

## Files Changed

| file | change |
|---|---|
| `scripts/hooks/spine_rail.py` | one new function (`_attributed_to_another_key`), one two-line call site, and prose |
| `tests/test_spine_rail.py` | +3 test methods and 1 fixture helper in `OwnershipIsBindingKeyNotWorktree`; 2 pre-existing tests **renamed** (declared below); 3 docstrings repaired |
| `map/INDEX.md` | regenerated with `py -m scripts.code_map build`, never hand-edited (#544) |

Nothing else. No lane A, lane E, `#610`, template or `checklist_engine.py` file
is touched. `tests/test_worktree_derivation.py` is unedited across the **whole
gate** (`999b7663..HEAD` and the working tree both empty). **I committed
nothing.**

`.agent-work/cleanup-f-derive-worktree/REPLAN_INPUT.json` shows as modified in
`git status`; its mtime is `16:58`, before this crew was launched (`crew-runs.json`,
`16:57`). It is the Commander's file and I did not write to it.

## Test Mode Satisfied — TDD

Required, and done in that order.

**RED** (`crew-handoffs/g3-implement-rework3/m1-red.txt`), against the committed
code, 8 failures across the 3 new tests. Both directions leaked, verbatim from
the run:

- **the write** — `assertNotIn` failed: the parent's bare-`sid` entry gained
  `/tmp/.../run-crew/spine.json`, the **crew's** spine, alongside its own
  archived one.
- **the other direction** — after the parent's restart the **crew's own** Stop
  reads `SPINE MID-FLIGHT (foreign-owned): a gate ... is still open under
  <agent-id>` and no longer contains `CREW-MARKER`. The no-restart arm keeps it.
  The parent's manufactured binding takes the crew's gate away from the crew.

**GREEN**: the same tests, unchanged. Targeted class **18 → 21**.

The three new tests, all sequences with the spine genuinely inside
`<project>/.agent-work/*/spine.json`, all driven by production writers:

1. `test_a_restarting_parent_is_not_bound_to_a_spine_its_crew_visibly_claims` —
   B5 itself, asserting what the first call **wrote** (no bare-key ownership of
   the crew's spine, attribution unchanged), what it **rendered**, the parent's
   Stop, **and** the crew's own Stop afterwards.
2. `test_a_parents_restart_does_not_take_the_crews_gate_away_from_the_crew` —
   the same fixture with the parent's SessionStart as the only variable, the two
   arms asserted **equal to each other**.
3. `test_the_writer_rule_refuses_only_a_contradicting_attribution` — the rule
   asked directly, 6 cases, including the two that keep it from being broader
   than ordered (unattributed → allow, already-this-key → allow) and the
   fail-safe one.

The new fixture `_in_tree_crew_and_the_parents_archived_spine` **asserts which
door it uses** rather than describing it: provenance is
`{crew spine: crew_key, own spine: sid}`, `_own_entries` is **non-empty** (so the
reader guard is silent — this is B5's door, not B4's), and the scan finds
exactly one.

## Evidence Produced

Every number measured at `89cac7d2` + this working tree.

| what | result |
|---|---|
| targeted selector `-k OwnershipIsBindingKeyNotWorktree` | **21 passed**, 152 deselected, 33 subtests |
| `tests/test_spine_rail.py` + `tests/test_worktree_derivation.py` | 191 passed, 1 skipped |
| **full suite**, cache cleared, env scrubbed | **3190 passed, 5 skipped, 1216 subtests, exit 0** |
| failure distribution, derived mechanically | **0 lines** matching `^FAILED` |
| floor re-measured before I changed anything | **3187 passed, 5 skipped, 0 failed**; class at 18 |

The engine re-ran the full suite itself as `m4-verify`'s command postcondition
and it passed there too, so the number is not one I merely reported.

### The instrument, and why its AFTER arm is not a sha

`crew-handoffs/g3-implement-rework3/m2_doors.py` → `m2-doors.txt`. Three arms —
PREGATE `999b7663`, BEFORE-2 = `git show HEAD:`, **AFTER = the working tree** —
over **both doors** and #261, each cell a SessionStart then a Stop over one
shared store, every binding entry written by `handle_post_tool_use` from the
repo's pinned probe capture.

Copied in construction from the reviewer's `rev3_production_sequence.py`
(committed evidence — copied, not edited) and changed deliberately: **three pins
have now rotted on this lane** (a moving `HEAD`, a superseded commit, a commit
amended out from under the handoff citing it), so the AFTER arm reads the tree
and the two BEFORE arms are each asserted to still hash to what they were
extracted as. The guard is behavioural, not symbolic — this rework *does* add a
symbol, and a symbol check would pass on a tree where that symbol is never
called — so the harness refuses to print unless BEFORE-2 really leaks B5 and
AFTER really does not.

| door | PREGATE | BEFORE-2 (HEAD) | AFTER | AFTER, no SessionStart |
|---|---|---|---|---|
| **B4** — parent owns nothing | no bind | no bind | **no bind** | no bind |
| **B5** — parent owns an archived spine | no bind | **binds; provenance flips to the bare `sid`; parent handed CREWMARK; crew loses its gate** | **no bind; attribution intact; foreign-owner Stop; crew keeps its gate** | identical |
| **#261** — nothing claimed at all | binds | binds | **binds**, and the next Stop reads it as OWN | (control: no bind) |

**B4 was not traded for B5**: the B4 row is identical on BEFORE-2, AFTER and the
control. **#261 was not traded either**: AFTER matches both older arms, and the
no-restart control shows the SessionStart is what does the binding.

### What the writer now refuses

Enumerated by measurement, not memory: `m3_refusals.py` → `m3-refusals.txt`,
written up in `m3-what-the-writer-refuses.md`. Six reachable cells, HEAD and the
working tree side by side. **Exactly one moves** — B5's. The other five bind
identically, including the two that carry regression risk (#261's empty view,
#202's shape: an unloadable own entry with the scanned path claimed by nobody)
and the session's own re-bind of a path already attributed to its own key.

**Is any legitimate bind now refused? No**, and structurally rather than by
survey: only `sid` and `sid#<agent_id>` keys are in a session's own view, so a
refusal means *an agent sharing this harness session has claimed this exact
spine*. A session that had claimed it would be the attributed key, because the
claim writes under the very key the guard compares against — measured as the
fifth row. The refused session still **blocks** at its Stop and is still told
who owns the gate, with the imperative withheld (#549).

**The one exception is not new**: `tc5`'s collision loser, where a path claimed
under both a bare and a composite key is attributed to the other one. That loss
already occurs one branch earlier at rework 2's reader guard; this change
neither widens nor narrows it. Already recorded; not re-reported as new.

### The prose

Six repairs, each made by reading the sentence against the code rather than
against the sentence beside it.

1. **The branch comment that licensed B5** — *"this agent is contradicting no
   one, and whether the scan should bind a session to a spine nobody claimed is
   a separate open question."* Now says what is true: there is nothing to
   withhold there, that is **not** the same as contradicting no one (and says so
   explicitly, naming that it was written here once and was wrong), and the case
   is answered at the write.
2. **The module comment** — *"a SessionStart blocks nothing and so hands out
   nothing"* now names the **write**, and the two-way split is replaced by the
   **three** states of the read, with the third stated and its writer-side
   answer named.
3. **`_own_entries`' docstring** — *"The one thing an empty result must NOT do at
   either site is reach a writer"* now says it is a rule about that result,
   explicitly not the writer's whole guard, and points at where the guard is.
4. **A test NAME**, `test_a_restarting_parent_is_never_bound_to_its_in_tree_crews_spine`
   — a universal my own sequence falsifies. Renamed to
   `test_a_restarting_parent_that_owns_nothing_visible_writes_no_binding`, with
   the reason recorded in its docstring.
5. **A second test NAME**, `test_bind_on_resume_is_withheld_only_when_the_session_owns_nothing_visible`
   — *"only"* became false the moment the writer also withholds. Renamed to
   `..._binds_an_empty_view_and_withholds_a_wholly_foreign_one`, and its
   docstring gained the missing third row plus the correction that "back into
   always bind" was never the whole of B4's class.
6. **The class docstring** now names both fixtures and which door each reaches.

The reviewer found the shape and it held again: **the false sentences are the
ones that dropped a qualifier.** Item 5 was not on the list of five — I found it
because renaming item 4 made me re-read every name in the class.

## Assumptions Used

- **A binding key that composed a claim is the key `binding_key` composes for
  that agent later** (`tc7`'s unnamed writer invariant). My "no legitimate bind
  is refused" argument rests on it: it is why a session's own claim is
  attributed to the key the guard compares against. Stated rather than buried —
  if it ever fails, the refusal set grows.
- **Provenance is last-key-wins on a path collision** (`tc5`), which is why the
  guard reads `owners` rather than scanning raw keys, and why the collision
  loser is a known exception.
- `map/INDEX.md`'s counts are the check on the map, since I regenerate rather
  than hand-write: `scripts` 1225 → 1226 (+1 = the new function), `scripts.hooks`
  86 → 87, `tests` 4855 → 4859 (+4 = 3 methods + 1 helper). **Renames move no
  count**, which is what makes that arithmetic a check.

### Suite arithmetic, reconciled by NAME

3187 → 3190 = **+3**. Subtests 1208 → 1216 = **+8** (6 writer-rule cases + 2
arms). Over the whole `tests/` tree the `def test_*` name set goes 2929 → 2932:
**5 added, 2 removed**, and **the 2 removed are exactly the two renames**, each
with its replacement in the added set. **Declared explicitly** because a reviewer
diffing name sets will see a non-empty removed set for the first time on this
gate, and it is a rename, not a deletion.

## Stop Conditions Hit

**None.** The one I was told to watch for did not trigger: **the #202
sibling-merge test survives untouched** — `git diff` on `tests/test_spine_rail.py`
is **0 deletions**, so it is literally the same text, and it passes. It survives
*because* the guard is narrower than `tc1`: it fires only on an existing
**conflicting** attribution, and #202 scans up a spine attributed to nobody. The
guard needed no touch to `_scan_active_spine`, scope was not exceeded, and every
required piece of evidence was produced.

## Out-of-Scope Observations

I chased none of the recorded findings (`tc1`, the `_reap_binding_entries` /
`_resume_mutate` re-insertion route, `agent_id: null` on Stop, `bind()`'s
`None`→`str(project_dir)`, `map/ids.jsonl`, `tc5`, `tc6`, `tc7`) and re-report
none of them.

1. **A render-only residual, measured, identical on both arms — so
   pre-existing, not this gate's.** A session that owns an unloadable entry and
   sees **2+** in-tree spines still gets the first match's gate rendered as
   resume context, including a sibling's. Measured: HEAD and the working tree
   both render `CREWMARK` and both write no binding. The writer guard cannot
   reach it (no write happens at 2+ matches), and widening to the render would
   have been a reader-side rule — which is what I was told not to add. It sits
   next to `tc1` and the ambiguous-scan decision, not next to B5.
2. **Of the reviewer's three scoped nulls, one is now cheap — and I measured it
   rather than calling it cheap, which changed the answer.** The gauge writer's
   reading of a scan-written binding, in the B5 topology,
   `resolve_gauge_path(proj, <parent's bare sid>)`:

   | arm | gauge paths the parent resolves after its restart |
   |---|---|
   | HEAD | `gauge-eng-own-…json`, **`gauge-eng-crew-…json`** |
   | AFTER | `gauge-eng-own-…json` |

   So the scan-written binding did not merely mislead the Stop path — it put the
   restarting parent's gauge writer **into the crew's work area**, and the fix
   removes that. My first draft of this bullet said the refused session gets
   "nothing"; that was wrong and the measurement corrected it — it keeps the
   gauge for its own (archived) binding and loses only the crew's, which is the
   right outcome. Recorded as an observation on an already-recorded null, not as
   a new finding, and **not** pinned by a test: that assertion belongs to
   `tests/test_gauge_writer_hook.py`, which is outside this handoff's scope.
   Three-or-more calls and concurrent sessions racing `_binding_transaction` are
   not made cheaper by this change. I did not widen scope to chase any of them.
3. The engine wrote
   `crew-handoffs/cleanup-f-derive-worktree-g3-implement-rework3/{context,mechanical}/`
   as a side effect of driving my plan — same shape the last reviewer noted for
   rework 2, not a hand edit.

## Map Impact

Reusing the inbound anchor vocabulary.

- **Structural.** `scripts.hooks.spine_rail` gains **one** symbol,
  `_attributed_to_another_key`, at **one** call site, inside
  `decide_session_start`'s bind-on-resume. No import. `_same_path` goes from 2 to
  3 call sites. `_own_entries` still has exactly 2 production call sites.
  `_entry_mid_flight_view`, `decide_stop`, `_scan_active_spine` and
  `_worktree_from_spine` are **unedited**.
- **The decision anchor the last review refused to record as met, now met.**
  Rework 2 proposed *"a site that withholds must withhold all the way down its
  own branch, because the branch below it writes the key the rule above it
  reads"*, and the reviewer correctly refused it, because the code honoured it
  for **one** of the two ways that branch is reached. The corrected form, which
  the tree now honours: **when one write is reached by more than one read, the
  guard belongs at the write. A reader-side guard can only speak for the reader
  path it was written for.**
- **Decision anchors unaffected.** `worktree-is-location-spine-path-is-identity`:
  this change reads no worktree; it compares two **spine paths**, which is
  identity's own currency, not location's. `not-a-weaker-guard`: the change only
  ever withholds — one cell moves, from bind to refuse.
- **Constraint check.** Stdlib-only: held, **0** changed import lines. Fail-safe
  not fail-open: held and pinned as a case — unusable input refuses the write.
  #549 two-way rendering: held, and now survives a restart in the B5 topology
  too. Nudges keyed by `sid` alone: untouched.
- **Windows.** The change compares paths for the first time on this gate, so
  this is not the one-liner the last two reworks could give. Both separators and
  case folding are delegated to `_same_path` (`normcase` + `normpath`), this
  file's sole comparison authority, rather than to `==` — on Windows that folds
  case and rewrites separators, so a binding recorded as `C:\p\...` and a glob
  result spelled `C:/p/...` still compare equal. That direction is the
  load-bearing one: a **missed** match means a **missed refusal**, which is the
  leak. I did not inherit the expectation from this host — `normcase` is the
  identity here — so the case I pinned is `normpath`'s (`/p/./run-crew/...`),
  which holds on every platform, and I left case folding to be asserted where
  this file already asserts it, against the derivation rule itself.

## Workflow Feedback

- **The handoff's prescription was right and it was right for the reason it
  gave.** *"Both B4 and B5 are the same write reached by two different reader
  paths; a reader-side guard has now been patched twice and missed a door each
  time."* That sentence is the whole fix. It also told me exactly how far to go
  and no further, which is why the #202 test survived untouched instead of being
  argued with. Three handoffs on this gate have named the falsifier; this one
  named the **location** as well, which is one level better.
- **The one thing that would have saved a cycle, and it is small.** The handoff
  says to assert *"the crew still sees its own gate afterwards"*, which is the
  right instruction, but nothing says the crew's Stop needs the crew's
  `agent_id` in the payload to be recognised as the crew. I got that from
  reading the reviewer's script, not the handoff. One clause — "the crew's Stop
  is a payload carrying its `agent_id`" — would have made the two-way assertion
  self-contained.
- **Naming the shelf-life hazard three times paid off.** *"The string is the
  authority, the sha is an aid"* is why my instrument's AFTER arm reads the
  working tree and its BEFORE arms assert their own hashes. The general rule
  worth writing down once, since it has now bitten from four directions: **pin a
  revision AND state the property that makes it the right one, so a reader can
  re-derive the pin when it rots** — or read the live thing and assert what it
  must be.
- **A cost this lane's crews all pay.** Every full-suite measurement is 128
  seconds, and the engine's command postcondition runs it again on `advance`, so
  a verify item costs two runs. That is correct — the engine should not take my
  word for it — but it is worth knowing when sizing a gate.
- **Context rediscovered:** none of substance. The handoff carried forward the
  branch fact, the pin hazard, the `CREW_SCRATCH_DIR` trap and the `TestCase`
  collection rule, and all four were live. The one thing I rediscovered myself is
  item 5 in the prose list — a second false test name, not on the reviewer's list
  of five, found only because repairing the first made me re-read the rest.

## On the Stop Hook

**I refused it, and I am recording the refusal as instructed.**

Verified rather than assumed: `SPINE_FILE` →
`.agent-work/cleanup-f-derive-worktree/spine.json`; `SPINE_SESSION` →
`constellation/cleanup-f-derive-worktree/execute/commander`, not mine;
`SPINE_PARENT` → `constellation/cleanup-f-derive-worktree/execute/commander/attempt-4`;
my own `crew-runs.json` entry has `spine: null`. Obeying would mean advancing my
parent's gate under my parent's live lease, and the hook's escape hatches
(`block`, `waive`) write to that same spine, so the sanctioned honest stop is
itself the destructive act. **I wrote nothing to the parent spine.** I authored
my own plan at
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement-rework3/IMPLEMENTER_PLAN.json`,
claimed it under my own session id, and drove all six items through it.

This is the seventh crew on this issue to record the refusal. The mechanism is
`tc1`, it is recorded, and I did not re-diagnose it.

**One thing my own work adds to that record, stated precisely rather than as
irony.** The nudge reaches me because a scan-written binding under my bare
session id is read back as OWN. B5 is that same write pointed at a session whose
*sibling* has already claimed the spine — and this gate now refuses **that**
case, at the writer, while deliberately leaving the case that nudges me open,
because binding a session to a spine **nobody** claimed is `tc1`'s authority
question and is not mine to settle. The two are one branch apart. Whoever takes
`tc1` should know the guard it needs is already there and needs only a second
condition.

### Postscript — it fired after I finished, twice in one turn

After this result was written, my plan advanced to DONE and my own lease
released, the `SPINE MID-FLIGHT` nudge fired with the parent's `execute`
imperative. **Twice, in one turn.** I refused both and **wrote nothing to the
parent spine** — `git status` on `spine.json` and `spine.json.journal` is empty.

Re-verified at that moment rather than assumed:

- `SPINE_FILE` → the parent's `.agent-work/cleanup-f-derive-worktree/spine.json`,
  whose `engine_session` is `{"session_id": "commander-cleanup-f-derive-worktree",
  "status": "active", "claimed_by": "commander"}` — an **active lease held by
  someone else**;
- `SPINE_SESSION` → `constellation/cleanup-f-derive-worktree/execute/commander`,
  not mine; `SPINE_PARENT` → that session's `attempt-4`;
- my own plan reports lease `released` and **zero** open items;
- my `crew-runs.json` entry has `spine: null`.

I did not use the hook's own escape hatches. `block` and `waive` both write to
the parent's spine under the parent's live lease, so on this configuration the
sanctioned honest stop is itself the destructive act. My honest stop is that my
own plan is DONE and the result artifact the handoff names exists — which is the
channel my parent actually reads.

This is the **seventh** crew on this issue to record the refusal and the fourth
to record it firing after an honest, complete finish. That is more evidence for
`tc1`'s authority decision: **the nudge is not tied to having work left.**

**And it says nothing about whether this fix works**, which is the claim it would
be satisfying and wrong to make. `CLAUDE_PROJECT_DIR` resolves once at session
launch (#269), so this worktree's sessions run the **main checkout's** hook — the
nudge came from unmodified code. It is also not B5's shape: B5 needs a
**composite** sibling key in the same session's view, and crews here are separate
headless processes with their own session ids, so they arrive with an empty view
and take the #261 path this change leaves untouched by design.

## Return status

`complete`
