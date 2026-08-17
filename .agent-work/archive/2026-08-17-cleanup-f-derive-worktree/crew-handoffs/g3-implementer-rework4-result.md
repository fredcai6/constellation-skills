# Implementation Result

## Assigned gate

`g3` — lane F, issue #609, **rework 4**. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. Diff base read with `git rev-parse HEAD`, not
inherited: **`52ba9940`**.

My own plan: `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement-rework4/IMPLEMENTER_PLAN.json`,
claimed under my own session id and driven gate by gate through
`scripts/checklist_engine.py` (`m0-context → m1-b6 → m2-b7 → m3-regressions →
m4-verify → m5-deliver`).

## Completed slice

Both blockers, and nothing else.

- **B6** — `decide_session_start`'s scan fallback now selects what it RENDERS by
  binding-key provenance instead of glob order.
- **B7** — every sentence that stated the guard's reach now names the reach it
  actually has: this session's view, not the store.

## B6 pre-dates this gate — stated plainly, as ordered

**B6 is not this gate's defect.** It measures identical on `PREGATE`
(`999b7663`), on rework 2 (`7d12c29d`) and on the tree as it stood at
`52ba9940`: an ambiguous scan rendered another binding key's gate on all three.
I re-ran the fourth reviewer's own committed instrument, `rev4_c2b.py`, unedited,
to confirm that for myself rather than inherit it:

```
PREGATE   {"every_match_owned_by_crew": true, "renders_a_crew_gate": true,  "renders_pick_it_up": true,  "scan_matches": 2, "wrote_a_binding": false}
REWORK2   {"every_match_owned_by_crew": true, "renders_a_crew_gate": true,  "renders_pick_it_up": true,  "scan_matches": 2, "wrote_a_binding": false}
WORKTREE  {"every_match_owned_by_crew": true, "renders_a_crew_gate": false, "renders_pick_it_up": false, "scan_matches": 2, "wrote_a_binding": false}
```

I repaired it as **completion of a rule this gate had already shipped** — *"the
bind-on-resume may not contradict an attribution the store already holds"* —
not as new scope. Rework 3 asserted that rule's absence-of-leak only in the
single-match fixture; rendering another key's gate contradicts the attribution
exactly as much as filing it does, so the same predicate now answers both acts.

## Scope

| file | change |
|---|---|
| `scripts/hooks/spine_rail.py` | the render selection (5 lines of code), plus prose in five places |
| `tests/test_spine_rail.py` | one fixture, two tests, three docstrings, one rename |
| `map/INDEX.md` | regenerated with `py -m scripts.code_map build`, never hand-edited (#544) |

Every Specific Exclusion holds. No lane A or lane E file, no
`scripts/verify_worktree_isolation.py`, no template, no
`scripts/checklist_engine.py` behaviour, no `cwd` threading, no fail-closed
refusal. `tests/test_worktree_derivation.py` has **no diff against `HEAD`**.
stdlib-only imports unchanged. Nothing committed.

Evidence artifacts (untracked, under
`crew-handoffs/g3-implement-rework4/`): `IMPLEMENTER_PLAN.json` + journal,
`m1-red.txt`, `m1-c2b-after.txt`, `m2-prose.md`,
`m3_what_the_render_refuses.py`, `m3-what-the-render-refuses.txt`,
`m3-what-the-render-refuses.md`, `m3-rev4-instrument-after.txt`,
`m4-full-suite.txt`.

## Behavior changed

Grep for **`for _cand_spine, _cand_path in matches:`**.

Before, the fallback did `spine = matches[0][0]` — filesystem glob order — and
asked the ownership question only of the write, only when `len(matches) == 1`.
Now the render walks the candidates and takes the first one
`_attributed_to_another_key(owners, path, own_key)` does not refuse. Three
consequences, all deliberate:

1. **The rule stops depending on `len(matches) == 1`.** That count gates the
   *write* because ambiguity is not ours to resolve silently — a different
   question from ownership. On 2+ matches the count was the only reason nothing
   was filed, which read like the ownership rule holding when it was never asked.
2. **The write branch is untouched.** It still keys on the raw match count and
   still guards itself with `_attributed_to_another_key` under the bare `sid`.
   Filtering the list before the count would have turned an ambiguous scan into
   an unambiguous bind, which is a behaviour change nobody asked for.
3. **The render asks with `own_key`, the write with `sid`.** The render is a
   read, so it asks with the reader's key — the same one `_own_entries` is asked
   with one branch above; the write asks with the key it would file under. On
   every SessionStart payload measured the two are the same string (no
   `agent_id` arrives). They are named separately rather than shared so that if
   one ever does arrive, the selection answers the agent the payload names. Both
   the divergence and its reason are written at the two sites.

**What I did not decide:** what happens when a candidate is attributed to
**nobody**. That is `tc1`, it is an open authority question, and it is untouched
— pinned by a test, and measured unchanged in four rows of the matrix below.

## Map Impact

- **Structural:** no new symbol. `_attributed_to_another_key` gains a second
  caller, which is why `map/INDEX.md` shows `scripts.hooks.spine_rail` unchanged
  at 65 entities.
- **Decision anchors:** `worktree-is-location-spine-path-is-identity` is
  reinforced at a third site — the scan's render selection was the last place in
  this file that chose a spine by something other than binding-key provenance.
  `decision:no-bind-on-ambiguous-scan` is untouched and is now visibly a
  statement about the *write* only.
- **Decision candidate for the Admiral (already floated, not mine):** whether
  `_attributed_to_another_key` should see across the harness session boundary.
  Measured open, prose now honest about it.
- `tests.test_spine_rail` 217 → 220 entities: 2 tests + 1 fixture helper.

## Test mode

**TDD, as required.** Red observed against the committed code before any
production edit, then green.

## TDD evidence, if required

`m1-red.txt`, captured against `52ba9940` before the fix:

```
E  AssertionError: {'hookSpecificOutput': {'hookEventName': '[410 chars]e."}} != {}
E  AssertionError: True != False : both matches attributed to the crew -> withhold
FAILED    ...::test_a_parents_restart_on_an_ambiguous_scan_is_told_nothing_it_may_drive
SUBFAILED(row='both matches attributed to the crew -> withhold')
           ...::test_an_ambiguous_scan_selects_by_provenance_not_by_glob_order
2 failed, 4 passed
```

The `tc1` row — two matches, **nothing** attributed — **passed in the same red
run** and passes now. That is the point of pairing them: the negative was green
before and after, so the repair cannot be a fail-closed refusal
(`ADMIRAL_RULING-1` R2). The 410-char body in the first failure is the crew's
gate plus *"Pick the run back up at this gate and drive it through the engine"*.

## Evidence

| # | claim | how |
|---|---|---|
| 1 | B6 leaked before, on this tree | `m1-red.txt` — both new cases fail against `52ba9940` |
| 2 | B6 pre-dates the gate | `m1-c2b-after.txt` — the reviewer's own unedited instrument: `renders_a_crew_gate` true on `PREGATE` and `REWORK2`, false on `WORKTREE` |
| 3 | pinned in **both** rendered fields | `test_a_parents_restart_on_an_ambiguous_scan_is_told_nothing_it_may_drive` asserts `start == {}`, then asserts the Stop's `reason` **and** `additionalContext` carry neither marker while still blocking and still naming the owner |
| 4 | the `tc1` boundary holds | matrix rows `tc1 … claimed by NOBODY` at n=1 and n=2, byte-identical between arms; plus the green row in the red run |
| 5 | what the render refuses | `m3-what-the-render-refuses.{py,txt,md}` — 7 topologies × 2 scan counts × 2 arms = 28 rows, **2 of 14 changed** |
| 6 | B4 and B5 stay fixed | `m3-rev4-instrument-after.txt` — the reviewer's `rev4_instrument.py` C1 (B5) and C3 (B4) still clean on `WORKTREE` |
| 7 | #261 still binds | same instrument, C4: bound with its **own** marker on all three arms; plus 4 scan tests green |
| 8 | #202's sibling merge | `test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding` green, untouched |
| 9 | B7's limit is real and unchanged | same instrument, C5: cross-session attribution still binds and still renders on all three arms |
| 10 | suite | `m4-full-suite.txt` — **3192 passed, 5 skipped, 0 failed**, 1218 subtests |

Both arms of my own harness print the **sha256 and byte length of the source they
actually loaded**, with a guard asserting the arms differ and that the render
loop is present in one and absent from the other. The handoff's warning about
pinned harnesses is why: I re-derived `HEAD` inside the script with
`git rev-parse` rather than writing a sha into it.

### What the render now refuses — the risk this fix carries

```
rows measured: 28   topologies x match-counts: 14   rows whose answer this rework changed: 2
  CHANGED  n=2  B5/B6 owns an ARCHIVED entry; crew claims the scan
  CHANGED  n=2  owns an ARCHIVED entry; crew claims the LEADING match only
```

The refusal set is exactly: **a session whose own spine no longer loads, offered
a candidate its own session view attributes to another binding key.** Nothing
else can reach the skip — an empty view attributes nothing (`#261`), a view the
session owns none of returns `{}` one branch earlier (`B4`), and a view whose
entry loads never reaches the scan.

| row | before | after |
|---|---|---|
| every candidate attributed to the crew | the crew's gate + the imperative | nothing (`{}`) |
| only the glob-leading candidate attributed to the crew | the crew's gate | the **other** candidate — the one nobody claimed |

**Is any legitimate resume context withheld? No.** The only session that now
gets nothing is one whose own spine is gone and whose every visible candidate
belongs to another key; the only context on offer to it was another key's gate
carrying the instruction to drive that gate. The second row is the judgment call
I would most want a reviewer to check: I chose "take the first candidate that
contradicts nobody" over "refuse everything once the leading one does". It
withholds strictly less, and the answer it gives is the one the old code would
have given had the glob returned the other order — which is the whole point:
**glob order no longer decides.** The reviewer's `rev4_instrument.py` C2 shows
this directly, `render_leaks_CREW-MARKER` true → false while
`render_leaks_THIRD-MARKER` false → true, the third spine being the unclaimed one.

### Suite arithmetic

| measurement | before | after |
|---|---|---|
| full suite, cache cleared, env scrubbed | 3190 / 5 / 0 | **3192 / 5 / 0** |
| targeted `-k OwnershipIsBindingKeyNotWorktree` (`--collect-only`) | 21 | **23** |
| `def test_` in `tests/test_spine_rail.py` | 173 | **175** |
| `map/INDEX.md` `tests.test_spine_rail` | 217 | **220** |
| `map/INDEX.md` `scripts.hooks.spine_rail` | 65 | **65** |

+2 tests reconciles in three directions; the map's third entity is the fixture
helper. The hook module's count is unchanged because the fix added no symbol.
**Failure distribution derived mechanically from the run log, not asserted:**
`grep -c '^FAILED' m4-full-suite.txt` = **0**, so the distribution is empty by
measurement. `CREW_SCRATCH_DIR` scrubbed on every run, `__pycache__` cleared
before every measurement.

One honest detour: the **first** full-suite run failed
`MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
by name, because my tests moved the entity count. That is what sent me to
`py -m scripts.code_map build`. Recorded because the count in the table above is
the *second* run, and a reader deserves to know why.

## Docs/contracts touched

Comments and docstrings only — no doc file, no schema, no contract.

## B7 — the prose, sentence by sentence

Full enumeration in `m2-prose.md`. **Twelve** sentences, not three.

The three the review named — `_attributed_to_another_key`'s opening line, the
call-site comment, and the new test's docstring — now say *this session's view*
and name what that view cannot see: **a claim filed under a different harness
`session_id`**. `owners` is `session_view_provenance(binding, sid)`: the bare
`sid` plus this session's own `sid#agent_id` keys.

Grepping the **claim** rather than the symbol found **three more copies** of the
same overstatement, which the handoff predicted would be there:

- the module-level three-states block's "refuses to file a path the store
  already attributes to a DIFFERENT binding key" — repaired in place, and
  updated to say the predicate now refuses to *render* as well. It is one of the
  four taxonomy copies; **no fifth copy was added anywhere**;
- `test_the_writer_rule_refuses_only_a_contradicting_attribution`'s docstring;
- that test's **name**, which said "writer rule" about a predicate that now has
  two callers. Renamed to
  `test_the_attribution_rule_refuses_only_a_contradicting_attribution`, with the
  rename and its reason recorded in the docstring. That is the only rename;
  the suite arithmetic above accounts for it (no count change).

**Six further sentences that my own B6 change falsified**, repaired in the same
pass rather than left for a fifth review:

- `_scan_active_spine`'s "still wanting the same *first match* spine for the
  advisory-context injection";
- `decide_session_start`'s "That case is answered at the **WRITE** instead";
- the count comment's "Zero or 2+ matches: **inject context (below)**";
- the write guard's "the reason it is here rather than **one branch up with the
  selection**";
- the taxonomy's "whatever **single** active-leased spine the tree holds";
- the test class docstring's "there are **two such fixtures** and not one".

**The guard's reach is unchanged.** Widening it across the session boundary is
the Admiral's decision and I did not touch it.

## Assumptions

1. **The render asks with `own_key`, not `sid`.** Justified above and written at
   the site. The reviewer's own framing — *"selection is a binding-key property
   at every site that selects"* — is where I took it from; `binding_key(payload)`
   is that property. On measured payloads the two keys are the same string, so
   nothing observable turns on it today.
2. **Skip-to-the-next-candidate rather than refuse-outright** when the leading
   candidate is attributed elsewhere. Measured, tabled, and flagged above as the
   call worth challenging.
3. The `.agent-work/**/crew-handoffs/g3-implement-rework4/` artifacts are
   deliverables (`git check-ignore` exits 1 for `.agent-work/` here), left
   uncommitted as instructed.

## Stop conditions hit

**None.** The render guard was writable without deciding the
attributed-to-nobody case; #202 and #261 both survive, measured; allowed scope
was not exceeded; all required evidence was produced.

## Out-of-scope observations

Nothing new that is not already recorded. Restated only because they are load
bearing for the next reader:

- The three-states taxonomy still stands in **four** places. I made the two I
  touched true and added no fifth. The restructure remains a triage candidate.
- `decide_session_start` is now longer, not shorter. The scan fallback is a
  self-contained decision — select, then maybe write — and would extract
  cleanly. Recorded, not done.
- `tc1` and B7's cross-session widening are both Admiral decisions and both are
  already floated. My work touches neither.
- Concurrent sessions racing `_binding_transaction` remains untested by anyone.
  I did not attempt it and nothing here speaks to it.

## Workflow Feedback

- **What the handoff got right, and I want it recorded because it is rare:**
  naming the tc1 negative as a required pin, in the same breath as the fix. That
  single instruction is what turned this from "add a guard" into "add a guard
  and prove what it does not refuse", and the matrix in `m3` exists because of
  it. It is also the shape the fourth reviewer asked for — one instrument read
  in two directions — and it took about twenty minutes, not an hour.
- **Handoff gap:** the handoff says apply the predicate "to the render
  selection" but does not say *which key* to ask with. The write passes the bare
  `sid`, the reader above passes `binding_key(data)`, and the two are the same
  string on every measured payload — so the choice is invisible to every test I
  can write and had to be argued rather than measured. That is a decision the
  handoff could have made in six words.
- **Also unstated:** whether "refuse `matches[0]`" meant *withhold everything*
  or *choose the next uncontradicted candidate*. Those differ on a real
  topology — mixed attribution across two matches — and the difference is
  exactly one row of my matrix. I chose the narrower withholding and flagged it;
  a fifth review should not have to guess that it was a choice.
- **Instruction I improvised around:** "assert on `additionalContext` **and**
  `reason`" reads as one call's two fields, but `decide_session_start` has no
  `reason` at all — the pair only exists at `decide_stop`. I read it as *both
  fields, across the sequence*, and asserted `start == {}` (which covers every
  field a SessionStart has) plus both fields of the following Stop.
- **What cost the most time:** nothing in the repair. The prose sweep found
  twelve sentences where the review named three, and nine of those were
  discoverable only by reading each touched comment **whole** and testing it
  against the tree. The handoff said exactly this would happen, and it was
  right — but "grep for the claim, not the symbol" is only half the method. The
  other half is *grep for the claims your own change just falsified*, which is
  where six of the twelve came from.

## On the Stop hook

**It fired, twice, and I refused it.** Recorded as observed fact, not as a
prediction: at the end of my turn a `SPINE MID-FLIGHT` hook told me that
`gate execute is still open`, to reload the constellation-commander skill,
rewrite `STATE_NOTE.md` with a PID, and drive `execute.json` gate by gate —
including dispatching crews through `run_crew.py`.

I refused. `SPINE_FILE` in my environment points at
`.agent-work/cleanup-f-derive-worktree/spine.json` — the **Commander's** spine,
under the Commander's own live lease (`LEASE active:
commander-cleanup-f-derive-worktree (by commander)`) — and `SPINE_SESSION` is
`constellation/cleanup-f-derive-worktree/execute/commander`, my parent's session,
not mine. My `crew-runs.json` entry has `spine: null`. Obeying would mean
advancing my parent's gate and launching crews under my parent's identity.

The hook's own escape hatches are not an exit either: it offers `block` to
bubble the blocker to the parent, or `waive` with human authority, and **both
verbs write to that same Commander-leased spine** — so the sanctioned honest
stop is itself the destructive act. There is also no blocker to bubble: this run
is `complete`. My result reaches my parent the way a crew's result is supposed
to — as this artifact, at the path the handoff named.

I authored my own plan under `crew-handoffs/g3-implement-rework4/`, claimed it
with my own session id, drove it through the engine gate by gate, and released
its lease last.

The handoff's closing observation is exact, and I will put it in my own words:
**B6 is that nudge.** A session is handed a gate it does not own, together with
the instruction to pick the run back up and drive it. The difference between the
hook and the defect is only that a crew can read the binding store and decline;
the hook's text cannot. Making the render decline is the same refusal, moved to
where it does not depend on the reader noticing.

## Return status

`complete`
