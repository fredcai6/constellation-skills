# Implementer Result — g3 rework 2

## Assigned Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. Diff base read with `git rev-parse HEAD`:
**`b9709cfe`**, whose `scripts/hooks/spine_rail.py` and
`tests/test_spine_rail.py` I confirmed byte-identical to `6bba3fd2` before
measuring anything.

Plan driven at
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement-rework2/IMPLEMENTER_PLAN.json`
— 6 items, claimed under session
`constellation/cleanup-f-derive-worktree/g3/implementer/attempt-3`, every item
started, attested and advanced through `checklist_engine.py`.

## Completed Slice

**B4 is fixed by one condition on the existing branch, and it is the condition
the reviewer named — narrowed by one term, for a reason I measured.**

```python
owned = _own_entries(list(sid_bindings.items()), owners, own_key)
spine = None
for _spine_path, entry in owned:
    ...
if spine is None and sid_bindings and not owned:
    return {}
```

`decide_session_start` now tells apart the two situations it conflated:

- **`sid_bindings` non-empty and `_own_entries(...) == []`** → withhold. No
  binding written, and no context either.
- **`sid_bindings` empty** → scan and bind. #261's path, untouched.

I did not revert rework 1's ownership-based selection, did not touch
`_scan_active_spine`, did not touch `decide_stop` or `_entry_mid_flight_view`,
and did not unify the two sites' fallbacks.

### Two judgment calls, both inside the authority the handoff granted

**1. The withhold returns `{}` rather than falling through for advisory
context.** The handoff left this to me. I measured it before deciding: on the
B4 fixture, the fall-through renders

```
RESUMING an active Constellation spine run after a restart or compaction.
ENGINE current -> ... ACTIVE g3 [in-progress] -- CREW-MARKER implement the crew
gate  Pick the run back up at this gate and drive it through the engine.
```

That is the crew's imperative handed to the parent as an instruction to act on
— the same leak in the other rendered field, and the same one `decide_stop`'s
foreign-owner branch refuses to render. Withholding the binding while still
rendering that would have fixed half of B4.

**2. The guard is `not owned`, not `sid_bindings` non-empty.** I implemented
the broader form first and it broke two pre-existing tests. One of them
(`..._merges_onto_existing_sibling_binding`, #202) is **not** the B4 class: that
session **owns** its entry and merely cannot read the spine it points at. It
contradicts nobody, and withholding there would have reached into `tc1`'s open
question about whether the scan should bind at all — which the handoff
explicitly says this fix does not touch. Narrowing to `not owned` restored it
untouched. The narrower rule is also the one the reviewer wrote.

### The one pre-existing test I rewrote, and why

`test_session_start_bind_on_resume_still_writes_under_the_bare_key` **arranged
the B4 class as its fixture**: the acting session's only visible entry was its
subagent's, and it asserted that the scan bound the session to a spine it never
claimed. Its *claims* are still all pinned — resume context injected, the write
lands under the **bare** key, the correct `engine_session`, the sibling
composite key untouched — but the fixture now gives the session an **own** entry
whose spine was deleted out from under it, which is the realistic shape and the
one that still reaches the scan. It gained an assertion (the sibling merge) and
lost none. Everything else in the file is unedited except docstrings.

## Files Changed

| file | change |
|---|---|
| `scripts/hooks/spine_rail.py` | one hoisted local (`owned`), one two-line condition, and prose |
| `tests/test_spine_rail.py` | +4 test methods and 1 helper in `OwnershipIsBindingKeyNotWorktree`; 1 pre-existing test's fixture rewritten; 4 docstrings repaired |
| `map/INDEX.md` | regenerated with `py -m scripts.code_map build`, never hand-edited (#544) |

Nothing else. No lane A, lane E, `#610`, template, or `checklist_engine.py`
file is touched. **I committed nothing.**

## Test Mode Satisfied — TDD

Required, and done in that order.

**RED** (`crew-handoffs/g3-implement-rework2/m1-red.txt`), against the committed
code, three arms of one fixture with the SessionStart as the only variable:

| arm | SessionStart wrote | the later Stop | leaked |
|---|---|---|---|
| control, no SessionStart | — | foreign-owner | no |
| **SessionStart then Stop** | **`binding[parent-sid]` → the crew's spine** | **own-gate** | **YES** |

with the parent handed, verbatim, `Next imperative: CREW-MARKER implement the
crew gate` in `reason` and `ACTIVE g3 [in-progress] -- CREW-MARKER implement the
crew gate` in `additionalContext`. Three of the four new tests failed.

**GREEN** (`m2-green.txt`): the same instruments, same fixtures. The SessionStart
writes nothing, renders nothing, and the Stop is byte-identical to the control.

The four new tests are **sequences** with the spine genuinely inside
`<project>/.agent-work/*/spine.json`, and each asserts on **both** halves —
what the first call wrote to the store and what the second call rendered:

1. `test_a_restarting_parent_is_never_bound_to_its_in_tree_crews_spine` — the
   blocker itself.
2. `test_a_restart_does_not_change_what_the_next_stop_is_told` — two arms
   asserted **equal to each other**, not each to its own expectation, so the
   property pinned is "a restart cannot move this answer".
3. `test_bind_on_resume_still_binds_a_session_that_has_no_binding_at_all` —
   #261, including that the next call reads the write back as OWN.
4. `test_bind_on_resume_is_withheld_only_when_the_session_owns_nothing_visible`
   — both directions in one loop, so the fix cannot drift into "never bind"
   (breaks #261) or back into "always bind" (is B4).

`OwnershipIsBindingKeyNotWorktree` now collects **18**, up from 14; the 14 are
unmodified except for two docstrings, and green.

## Evidence Produced

Every number measured at `b9709cfe` + this working tree.

| what | result |
|---|---|
| targeted selector `-k OwnershipIsBindingKeyNotWorktree` | **18 passed**, 152 deselected, 25 subtests |
| `tests/test_spine_rail.py` + `tests/test_worktree_derivation.py` | 188 passed, 1 skipped, 25 subtests |
| **full suite**, cache cleared, env scrubbed | **3187 passed, 5 skipped, 1208 subtests, exit 0** |
| failure distribution, derived mechanically | **0 lines** matching `^FAILED` |
| floor re-measured before I changed anything | 3183 passed, 5 skipped, 0 failed |
| pinned three-arm differential | exit 0, guard accepts, arms refuse nothing new |

**Suite arithmetic reconciles against the diff.** 3183 → 3187 = **+4**, exactly
the four new methods. Subtests 1204 → 1208 = **+4** = 2 arms + 2 rows. No test
deleted; the one rewritten test kept its name.

**The Stop path did not move**, and I proved it by running rework 1's own
harness **twice with only its AFTER arm swapped** — once with `6bba3fd2`'s hook
in the tree, once with mine — and diffing. All 13 Stop rows: **identical**.
S9–S12 (SessionStart selection): **identical**, which is expected and is itself
the finding, since every one of those fixtures places its spines outside the
scan's glob. The swapped hook was restored and `cmp` confirms byte-identity.

**A third instrument, mine** (`m2_withhold_matrix.py`,
output at `m2-withhold-matrix.txt`): three pinned arms
(`999b7663` / `6bba3fd2` / working tree) × **ten cells**, each a SessionStart
then a Stop over one shared store, each reporting both the (key, path) pairs
written and the marker rendered. **Four cells moved; six did not.**

Its arm guard is worth one line, because the obvious guard would not have
worked: this rework **adds no symbol**, so a symbol check alone would pass with
both arms loaded from the same file. The arms are therefore separated by
**behaviour** on the one cell the change exists to move — REWORK1 *must*
manufacture the B4 binding and AFTER *must not*, or the harness refuses to print.
I also had to fix my own first version of it: it counted new binding **keys**,
which reports "no write" for a session that already holds a `sid` key — silently
hiding exactly the `tc5` and unreadable-entry rows. It counts (key, path) pairs
now.

**Import block:** unchanged and stdlib-only, printed by the differential.

**Windows:** one line, as the handoff predicted — the change compares no paths
at all. It reads the truthiness of a dict and of a list.

## What Newly Withholds

Full enumeration in `m2-what-newly-withholds.md`, derived from the matrix rather
than from memory. Five classes, all requiring a **non-empty** view the acting
agent owns **none** of:

1. **one** active-leased in-tree spine — was: bind + render + the next Stop
   answers with it as its own. Now: nothing. **This is B4.**
2. **2+** in-tree spines — was: no binding but the scanned gate's context. Now:
   nothing.
3. **no** in-tree spine — unchanged, nothing either way.
4. `binding_key` refuses the payload (#441 malformed `agent_id`) — was: **it
   wrote an ownership record for an agent the hook had just declined to
   identify.** Now: nothing.
5. `tc5`'s collision loser — was: the scanned gate's context. Now: nothing.

**Does any session that legitimately needs a binding now fail to get one? No,
with one named exception.** A session in this class has claims under its session
id, none of them its own — and if it had ever claimed a spine, that claim wrote
under the very key the comparison asks about, so the entry would be in the view
**and** owned. Any spine the scan could hand it is by construction one it never
claimed.

The exception is class 5: a session that really did claim a path its subagent
also claimed loses it to last-key-wins provenance, and now loses the scan's
re-bind with it. That is a real, narrow loss. It is not a reason to keep the
fallback — papering over a provenance collision by manufacturing ownership from
a glob is the exact move B4 condemns. It is `tc5`, already recorded, and it
wants a decision about which of two keys owns a path both claimed.

One consequence checked rather than assumed: `gauge_writer_hook.resolve_gauge_path`
resolves from the binding key, so a withheld session gets no gauge path. That is
correct here — the gauge it would otherwise have written was for **another
agent's** spine under this session's name.

## The Prose

Recorded with before/after quotes in `m3-prose.md`. Seven sentences: the four
the reviewer measured false, plus `_own_entries`' "each site's fallback is its
own business" claim (the one the reviewer rejected), plus the class docstring's
promise that every case places its spines outside the scan's reach — which
stopped being true of the class the moment I added in-tree cases.

The reviewer found the shape exactly: every sentence keeping the qualifier
"**from the binding**" was true and every sentence dropping it was false. The
repair removes the need for the qualifier rather than restoring it, because the
code now withholds from the scan too.

## Assumptions Used

- `SessionStart` payloads carry no `agent_id` in anything measured; the site
  still asks `binding_key` rather than assuming it, and my tests do not depend
  on the assumption either way.
- A binding key that composed a claim is the key `binding_key` composes for that
  same agent later. This is the writer invariant `tc7` names, and my
  "no legitimate binding is lost" argument rests on it. Stated rather than
  buried, because if it ever fails, class 5 grows.
- `map/INDEX.md`'s counts are the check on the map, since I regenerate rather
  than hand-write: `tests` 4850 → 4855 = 4 methods + 1 helper; `scripts`
  unchanged at 1225, because this rework adds no symbol.

## Stop Conditions Hit

None. Scope was not exceeded, no excluded file was touched, and every piece of
required evidence was produced.

## Out-of-Scope Observations

I chased none of the recorded findings (`tc1`, `agent_id: null` on Stop,
`bind()`'s `None`→`str(project_dir)`, `map/ids.jsonl`, `tc5`, `tc6`, `tc7`) and
re-report none of them. **B4 does not close `tc1`**, exactly as the handoff
says: `tc1` is that the scan-bind exists, and it still exists and still binds a
session with an empty view to a spine it never claimed. What is closed is that
this change widened who reached it.

Two new observations, neither a defect I was asked to fix:

1. **`tests/test_spine_origin_isolation.py:451` still names
   `checklist_engine.worktree_from_spine_path`**, the symbol g2 deleted. The
   original gate's Wiring Grep required zero references **in my two files** and
   there are zero; this one is in a file outside my scope, and
   `tests/test_worktree_derivation.py`'s reference is a deliberate record of the
   deletion. Reporting the location only — not chasing it.
2. **`decide_session_start` is now ~115 lines** doing selection, withhold, blind
   scan, bind-on-resume and rendering in one body. The rework reviewer flagged
   `long-method` on it at 105 lines and tied the flag to B4 directly: *"the
   coupling between its first and third parts **is** B4, and at that length
   nothing invites a reader to check it."* My fix puts the missing discriminator
   on one visible line, which is the cheapest available answer, but the function
   is longer than before, not shorter. Extracting the bind step remains the
   structural fix and is a triage candidate, not this gate's work.

## Map Impact

Reusing the inbound anchor vocabulary.

- **Structural.** `decide_session_start` gains no symbol and no import; it gains
  one local (`owned`) and one condition. `_own_entries` keeps exactly 2
  production call sites. `_entry_mid_flight_view`, `decide_stop`, `_same_path`,
  `_worktree_from_spine` and `_scan_active_spine` are **unedited**.
- **The anchor that was missing, and is the fact B4 turns on:**
  `decide_session_start`'s **binding read and its scan-bind write are the same
  `if spine is None:` branch**, so a change to what the read returns is a change
  to how often the write fires. The rework reviewer named this as context that
  three separate agents rediscovered; it is now stated in the code, in the class
  docstring, and here.
- **Decision anchors.** `worktree-is-location-spine-path-is-identity` is
  unaffected — this change reads no path. `not-a-weaker-guard` holds: the change
  only ever withholds. The `@grade: placeholder` decision pressure the original
  handoff recorded ("what replaces the skip at each site") now has a third,
  narrower answer worth recording: **a site that withholds must withhold all the
  way down its own branch, because the branch below it writes the key the rule
  above it reads.**
- **Constraint check.** Stdlib-only: held, import block byte-identical. #549
  two-way rendering: held, and strengthened — it now survives a restart.
  Nudges keyed by `sid` alone: untouched. Fail-safe not fail-open: held, and
  this is the first evidence on this gate that reaches the in-tree topology.

## Workflow Feedback

- **The handoff's best instruction is the one that made the test possible.**
  "Your test must be a **sequence** … with the spine genuinely inside
  `<project>/.agent-work/*/spine.json`… A single-call test cannot see this and
  will pass while the defect stands." That is a falsifier stated as a
  construction, and it is the third time on this gate that naming the falsifier
  did the crew's hardest thinking for it. It also told me *why* every prior
  instrument missed it, which is what let me distrust my own first matrix when
  its "bound" column read `-` for a row I expected to move — the metric was
  wrong, not the code.
- **The one thing the handoff got slightly wrong, and it cost a cycle.** It
  states the fix as "`sid_bindings` non-empty and `_own_entries(...) == []` →
  withhold" and then, one line later, as "It is a condition on the existing
  branch." Implemented literally as the second, the natural condition is
  `sid_bindings` non-empty — which is broader than the first and breaks #202's
  sibling-merge test, because an **own** entry with an unreadable spine also
  arrives at that branch with `spine is None`. Both readings are in the document
  and only one is right. A single sentence — "an own entry whose spine is
  unreadable reaches this branch too, and must keep the scan" — would have
  removed the ambiguity. I found it by running the suite, which is the cheap
  way, but it is the sort of thing that gets "fixed" the wrong direction under
  time pressure.
- **Context rediscovered:** none of substance — the rework reviewer's Workflow
  Feedback had already surfaced the same-branch fact, and this handoff carried
  it forward. That worked.
- **What would have made this easier:** the handoff says "Do not commit anything
  yourself" and the original says artifacts "appear in `git status`, not in
  `git diff`". Both true and both useful. What neither says is whether a crew
  should regenerate `map/INDEX.md` when its own test count moves — the original
  handoff's Allowed Scope permits it and #544 forbids hand-editing, so I
  regenerated, but the first full-suite run went red on
  `MapTreeFreshnessTests` before I did. Naming "regenerate the map **before**
  you measure the suite" in the Verification Commands block would save every
  crew on this repo one 128-second run.

## On the Stop Hook

I refused it, and I am recording the refusal as instructed.

Verified rather than assumed: `SPINE_FILE` →
`.agent-work/cleanup-f-derive-worktree/spine.json`; `SPINE_SESSION` →
`constellation/cleanup-f-derive-worktree/execute/commander`, not mine;
`SPINE_PARENT` → `constellation/cleanup-f-derive-worktree/execute/commander/attempt-4`;
my own `crew-runs.json` entry has `spine: null`. Obeying would mean advancing my
parent's gate under my parent's live lease, and the hook's escape hatches
(`block`, `waive`) write to that same spine, so the sanctioned honest stop is
itself the destructive act. **I wrote nothing to the parent spine.** I authored
my own plan at
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement-rework2/IMPLEMENTER_PLAN.json`,
claimed it with my own session id, and drove all six items through it.

The handoff's closing line is right, and it is worth stating precisely rather
than as irony: the nudge I refused is produced by `tc1` — the scan-bind — and
B4 is what happens when a fix *feeds* that same mechanism. The defect I fixed
and the instruction I declined are the same failure seen from two sides: an
agent being handed another agent's next imperative as its own.

**Postscript — it fired after I finished, twice in one turn.** After this
result was written, my plan advanced to DONE and my own lease released, the
`SPINE MID-FLIGHT` nudge fired with the parent's `execute` imperative. I
refused it and wrote nothing to the parent spine. Re-verified at that moment
rather than assumed: my plan reports `LEASE released` and `DONE: no open
items`; `.agent-work/cleanup-f-derive-worktree/spine.json`'s `engine_session`
is `{"session_id": "commander-cleanup-f-derive-worktree", "status": "active",
"claimed_by": "commander"}` — an active lease held by someone else; my
`crew-runs.json` entry has `spine: null`. This is the fifth crew on this issue
to record the same refusal, and the second to record it firing *after* an
honest, complete finish, which is evidence for `tc1`'s authority decision: the
nudge is not tied to having work left.

**One thing this firing does NOT show, stated because it would be easy to claim
otherwise.** It says nothing about whether my change works. `CLAUDE_PROJECT_DIR`
resolves once at session launch (#269), so this worktree's sessions run the
**main checkout's** hook, not the one I just edited. This nudge came from
unmodified code. It is also not the B4 shape: B4 is a SessionStart manufacturing
a binding that a later Stop reads as OWN, and nothing here wrote a binding at
all — the Stop is answered from the parent's own live claim on its own spine.
Fixing B4 does not close this, exactly as the handoff and both reviews say.

## Return status

`complete`
