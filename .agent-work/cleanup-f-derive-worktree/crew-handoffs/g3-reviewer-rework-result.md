# Review Result — g3 rework 1

## Assigned Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. Review target: the rework `6bba3fd2` over the
blocked pass `e3e50a69` over the pre-gate base `999b7663`.

Survey driven at
`.agent-work/cleanup-f-derive-worktree/g3-review-rework/review.json` — 15 checks
(the 7 standard reviewer items plus this handoff's 8 Close Criteria as their own
checks), claimed under session
`constellation/cleanup-f-derive-worktree/g3/reviewer/attempt-2`, all visited,
consolidated.

I verified the working tree's `scripts/hooks/spine_rail.py` and
`tests/test_spine_rail.py` are byte-identical to `6bba3fd2` before measuring
anything, so what I measured is what shipped.

## Result

`BLOCK`

**One blocker, new, in production code, measured not read.** The rework answers
all three of the first review's blockers, and answers them well. Then it creates
a fourth.

I want the good part on the record first, because it is most of the change and
because two of the three fixes are better than the minimum they were asked for.
**B1** is fixed at the root, with a guard I could not defeat in four attacks.
**B3** is fixed, and re-reading whole found five more false sentences, three of
them the implementer's own from an hour earlier. **The two rewritten
pre-existing tests are not weakened** — that was the handoff's hardest look and
the answer is a clear yes. **B2's own six cases are fixed**, order-independent,
and they hold under every extension the criteria demanded but one.

That one is the blocker.

## Per-check findings against the rework's Close Criteria

| # | criterion | verdict |
|---|---|---|
| 1 | B2 fixed, measured not read — **and go further** | **FAIL — B4** (the six cases pass; the fallback-scan extension fails) |
| 2 | adjudicate the unshared fallback | **FAIL — B4** (rule endorsed, refinement rejected) |
| 3 | the two rewritten pre-existing tests | **PASS** |
| 4 | B1's guard cannot pass on a degenerate comparison | **PASS** |
| 5 | B3, and the prose generally | **FAIL** (four false sentences, one shape) |
| 6 | nothing that passed the first review regressed | **FAIL — B4** (per call: clean. across a pair of calls: not) |
| 7 | suite arithmetic reconciles against the diff | **PASS** |
| 8 | `_own_entries` correct at both sites | **PASS** |

And the standard items: handoff compliance **FAIL** (criteria 1, 2, 5, 6), scope
**PASS**, evidence **PASS**, quality vs inherited rules **FAIL**, reconciliation
**FAIL**, Fowler pass **PASS**.

### 1 — B2 is fixed; the extension the criterion named is where it breaks. FAIL

**I built my own instrument first, before running theirs**, as the handoff
insisted — `/tmp/g3rev2/rev2_instrument.py`, three arms extracted and pinned by
me (`999b7663` / `e3e50a69` / `6bba3fd2`), covering both call sites, with its own
arm guard that also asserts the working tree *is* the `NEW` arm. Output at
`/tmp/g3rev2/rev2-differential.txt`.

Re-ran `/tmp/g3rev/c4_session_start.py` at `6bba3fd2`. Cases 2, 3 and 6 match the
correct OLD behaviour, as the Commander reported. Case 1 is fixed too — the
implementer was right that it falls out of the rule rather than needing to be
reached for.

**A note on that harness, since this handoff calls its six cases "the
specification": cases 4 and 5 cannot be read.** Its marker test is a substring
match and `CREW-MARKER` is a substring of `OTHERCREW-MARKER`, so a single
rendered gate prints both markers. My own instrument used disjoint markers, which
is how I could tell those two rows apart at all.

Going further, as the criterion required:

| my case | what it constructs | NEW |
|---|---|---|
| A1 | session owns **two** entries, a crew's key leads the view | its own gate, never the crew's |
| A2 | first own entry carries no `spine`, a later one does | the later **own** gate |
| A3 | first own entry names an unreadable spine | still never the crew's |
| A4b/A4c | payload names agentB / agentA | that agent's gate |
| A4 | payload names agentZ, which owns nothing | nothing from the binding |
| A5/A5b | `agent_id` malformed (`a/b`) / explicitly null | nothing from the binding |
| A7 ×4 | `cwd` absent / int / dict / elsewhere | still its own gate |

All correct. Then the third extension the criterion names — **the interaction
with the fallback scan** — and it fails. See **B4**.

### 2 — the unshared fallback, adjudicated. FAIL

**I agree with the rule and I reject the refinement.** Said plainly, because the
handoff asked for it plainly.

> Blocking is a spine property at the one site that blocks; selection is a
> binding-key property at both sites.

That is right, the first implementer's asymmetry was half right, and this is the
formulation that should go up. Sharing the *comparison* is right and it is
genuinely one function now: both sites call `_own_entries` and cannot drift on
the question "is this mine".

On the criterion's first question — **is there a case where
`decide_session_start` owning none of the visible entries should still answer
with something?** No, not from the binding. The asymmetry argument for that is
sound: a Stop blocks whatever it renders, so it must name a gate; a SessionStart
blocks nothing, so it need not.

On the criterion's second question — **does the split leave the two sites able to
drift the way the original asymmetry did?** **Yes, and it already has, in this
commit.** The refinement treats each site's empty-result path as private:

> the fallback is each site's own

> it still falls through to the blind scan below, which reads no binding key and
> is not this rule's business

It is not private. `decide_session_start`'s fallback is `_scan_active_spine`'s
bind-on-resume, and that path **writes** an entry under the bare `sid` — the
exact key `_own_entries` reads as OWN. So this site's fallback feeds the other
site's comparison, through the binding store. The two fallbacks are uncoupled in
code and coupled in effect, which is the worst of the two arrangements. **B4 is
the measured consequence, and it is a finding rather than a quibble — which is
what the handoff said to say if I thought the refinement would let the sites
drift.**

The fix does not require unifying the fallbacks. It requires
`decide_session_start` to tell two situations apart that it currently conflates:

- **"I have no binding at all"** → scan and bind. The pre-existing #261 path,
  untouched.
- **"I have visible bindings and own none of them"** → withhold, and do not
  manufacture one.

Both facts are already in hand at that point in the function: `sid_bindings` is
non-empty and `_own_entries(...)` returned `[]`.

### 3 — the two rewritten pre-existing tests. PASS

This is where the handoff wanted my hardest look, and it deserves a careful yes.
I read both against their predecessors line by line.

**`..._reads_through_to_a_composite_key_but_answers_only_its_owner`.** The old
form's only substantive assertion beyond the binding key was that a bare
SessionStart came back with `COMPOSITE-RESUME` in `additionalContext` —
read-through proved only as a side effect of the resume. The new form asserts
#419's read-through **directly and at the API**:

```python
assert list(sr.session_view(binding, sid)) == [sp]              # read-through intact
assert sr.session_view_provenance(binding, sid)[sp] == composite  # and attributed
```

It keeps the `_scan_active_spine(proj) == []` guard, so only the binding can
explain the answer, and it **adds** the owner round trip. Strictly more
assertions. The single claim it drops is the policy the change reverses.

**`..._withholds_a_composite_key_imperative_from_the_bare_session`.** Old:
`"g7" in ctx` and `"REGRESSION-MARKER" in ctx` — one field. New: `out == {}` plus
neither string anywhere in `json.dumps(out)` — **both** rendered fields. Stronger.

**The rejected alternative really is mutually exclusive with the fix**, and I
checked rather than accepted it. Both old tests build the first reviewer's case 3
in same-tree form: a subagent claims under `sid#agent_id`, then a bare
SessionStart expects to resume from it. Any rule that falls back to the leading
entry when the session owns none answers a bare session with another agent's
entry — which *is* case 3. You cannot keep those two tests green and fix case 3.
The implementer flagged the collision rather than burying it, and its account of
it is accurate.

**One caveat, an observation and not a blocker.** The round trip proves the entry
is still reachable only for a SessionStart payload carrying `agent_id` — a shape
nothing measured says the harness sends, as the implementer says itself. So "the
entry did not become unreachable" is true only hypothetically. It is harmless in
practice: SessionStart is a per-harness-session event and a subagent never
receives one of its own, so nothing that actually happens needs to reach a
composite-only entry here. The consequence worth recording is narrower — at this
site the merged view now returns exactly what
`binding.get(binding_key(payload))` would return, except for last-key-wins on a
path collision (see `tc5`).

### 4 — B1's guard. PASS

Fixed at the root. Ran it: exit 0, header
`BEFORE (999b7663) vs BLOCKED (e3e50a69) vs AFTER (working tree)`, and the three
rows the first review asked a reviewer to spot-check now read honestly — S3 and
S8 `BEFORE ALLOWED → BLOCK own-gate`, S4 `BEFORE ALLOWED → BLOCK foreign-owner,
rendering NOTHING`.

**I did not grade it by reading it.** Four attacks, each actually run:

| attack | result |
|---|---|
| `BASE_REV` → `e3e50a69` | **REFUSES**, exit 1: lacks `_foreign_worktree` / already has `_is_own_entry` / BEFORE and BLOCKED byte-identical |
| `BLOCKED_REV` → `999b7663` | **REFUSES**, three symmetric complaints |
| `BLOCKED_REV` → `6bba3fd2` | **REFUSES**: already has `_own_entries` / BLOCKED and AFTER byte-identical |
| working-tree hook reverted to `e3e50a69` (AFTER arm) | **REFUSES**: AFTER lacks `_own_entries` / BLOCKED and AFTER byte-identical |

Hook restored afterwards; `git diff --quiet` confirms byte-identical.

The implementer also chose the hardcoded pin over "parent of the commit that last
touched the hook" for the right reason, and said so: that derivation is honest
today and becomes wrong the moment the rework is committed.

**One limit, named not blocking.** The guard identifies arms by *symbol*, so any
pre-g3 revision passes as BEFORE — I pointed `BASE_REV` at `c23c3d0f` and it
printed a full happy table. It therefore proves "BEFORE is some revision before
g3 touched the hook", not "BEFORE is `999b7663`". That is the weaker of the two
claims, but it is not the degenerate class the guard exists to catch, and the pin
is a literal in the source. Recorded as `tc6`.

My independent instrument agrees with this differential on every overlapping row.

### 5 — B3 and the prose. FAIL

The header claim is now **true** — I verified it at both sites rather than
inferring it from the fix — and the implementer rewrote it anyway to state the
rule instead of asserting a property, which is better than what was asked. Five
of the six sentences it repaired check out.

The criterion told me to assume there is a fourth false sentence. There are four,
and they share one shape.

**The pattern: every sentence that keeps the qualifier "from the binding" is
true, and every sentence that drops it is false** — because that qualifier is
exactly what the blind scan defeats.

True, precisely scoped: `_own_entries`' *"it hands out nothing **from the
binding**"*; `_is_own_entry`'s *"decide_session_start hands out no gate **from the
binding**"*.

False, generalised:

1. `spine_rail.py:1735-1741` — *"Nothing another agent claimed is ever
   substituted: this site withholds rather than guessing, which is the fail-safe
   direction."* Measured false. A session owning none of the visible entries,
   with one in-tree active spine, is handed exactly what another agent claimed —
   and bound to it.
2. The module section header's parenthesis — *"it still falls through to the
   blind scan below, which reads no binding key and is not this rule's
   business."* The scan reads no binding key but **writes** one, under the bare
   `sid`, which is this rule's own input. The disclaimer is the false half.
3. `tests/test_spine_rail.py`,
   `test_session_start_withholds_when_it_cannot_say_who_is_starting` — *"A
   session that owns nothing still falls through to `_scan_active_spine` …
   **exactly as it did before**."* False. Before, a session that owned nothing
   but could *see* entries did not fall through at all: the loop took the first
   visible entry and `spine` was non-`None`. This change widens the fall-through
   class, which is the opposite of "exactly as before".
4. `test_session_start_does_not_resume_from_a_crews_binding_it_never_claimed` —
   *"A session that claimed NOTHING must not be handed a gate."* True of what the
   test arranges (spines outside the glob), false of the code, which hands it one
   whenever the scan finds exactly one.

These are not cosmetic. **(1) and (3) are precisely the sentences a reader would
rely on to conclude that B4 cannot happen.**

### 6 — nothing that passed the first review regressed. FAIL

**Everything survives per call. The fail-safe posture regresses across a pair of
calls.**

What holds, each re-measured by me at `6bba3fd2` rather than read:

- **The Stop path did not move.** All 13 rows of my own instrument are identical
  `e3e50a69` → `6bba3fd2` — parent with in-tree crew, crew stopping, own claim
  from another tree, crew-only, malformed `agent_id`, agent owning nothing,
  released lease, no binding, and five garbage-input rows. Same on every
  overlapping row of the implementer's differential.
- **#549's two-way rendering intact** — own-gate renders the imperative,
  foreign-owner withholds it from both `reason` and `additionalContext`.
- **Nudge / 3-strike hatch keyed by session id alone** — one write at
  `spine_rail.py:1629` (`nudges[sid]`), both deletes at `:1294` and `:1430` on
  `sid`.
- **Stdlib-only import block byte-identical** between `e3e50a69` and `6bba3fd2`
  (md5 of the extracted import lines matches). `_entry_mid_flight_view`
  untouched. `_same_path` still has two real callers (`:982`, `:1123`).
- **`tests/test_worktree_derivation.py` unedited across the whole gate** —
  `git diff --name-only` empty for both `999b7663..6bba3fd2` and
  `e3e50a69..6bba3fd2` — and green at 19 passed.
- The targeted selector **collects 14**, not zero.

What regresses: **B4**.

### 7 — suite arithmetic. PASS

Checked against the diff, not accepted.

`def test_` in `tests/test_spine_rail.py`: `999b7663`=153, `e3e50a69`=160,
`6bba3fd2`=**166**. +6 over the blocked pass.

The names **removed** by the rework are exactly two — and both reappear among the
eight added, as their renamed replacements. So the renames are net zero and
**there are no deletions.** The remaining six added names are the six genuinely
new methods, confirmed independently by the class count: 8 methods at `e3e50a69`,
14 at `6bba3fd2`.

My own suite run at `6bba3fd2`, `__pycache__` cleared repo-wide and
`SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`/`CREW_SCRATCH_DIR` scrubbed:

```
3183 passed, 5 skipped, 1204 subtests passed in 128.13s   (exit 0)
```

Failure distribution derived mechanically even though empty: 0 lines matching
`^FAILED`. 3177 + 6 = 3183. Subtests 1192 → 1204 = +12, matching the claimed
2 (write-order) + 4 (withhold) + 6 (inert location).

### 8 — `_own_entries` at both sites. PASS

Correct, and the precondition holds for a reason I checked rather than assumed.
All three binding writers — `_door_claim_mutate` (`:1264`), `_claim_mutate`
(`:1370`), `_resume_mutate` (`:1772`) — write
`key_bindings[abs_spine] = {"spine": abs_spine, ...}`, so the binding **key** and
the entry's `spine` field are the same string by construction.

That matters, because the two callers pass structurally different things:
`decide_session_start` passes `list(sid_bindings.items())`, whose `[0]` **is** the
dict key; `decide_stop` passes `_entry_mid_flight_view`'s tuples, whose `[0]` is
`entry.get("spine")` — from the entry **body**. They coincide only because of that
writer invariant.

Divergence would be benign and asymmetric: at `decide_session_start`
`owners.get()` can never miss (provenance is built from the same `entries.keys()`
that `session_view` merges), so `_is_own_entry`'s `owner_key is None → OWN` branch
is **unreachable** from this site; at `decide_stop` a miss reads as OWN, the
documented deliberate direction.

Documentation gap, recorded as `tc7`, not a blocker and not a regression: the
docstring describes both callers as passing "the abs spine path that `owners` is
keyed by" without recording that one derives it from the entry body, nor that the
identity is a writer invariant rather than a type guarantee.

## Handoff compliance

The rework did what its handoff asked — all three blockers answered, nothing else
touched — and did the hardest parts well. It fails on this review's own criteria
1, 2, 5 and 6, which are all one defect.

The implementer's own assumption names it, and is half right:

> A session that owns nothing still falls through to `_scan_active_spine` … My
> tests are constructed so it cannot manufacture a pass, and I did not touch it.

Accurate about the scan's **code**. Wrong about its **reach**. Not touching a path
is not the same as not sending more traffic down it.

## Scope drift

None. Non-`.agent-work` files in the rework commit are exactly three:
`map/INDEX.md`, `scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`.

Every named exclusion checked mechanically against `git diff --name-only` over the
**whole gate** (`999b7663..6bba3fd2`), not just the rework: no lane A file, no
lane E file, no `scripts/verify_worktree_isolation.py`, no template of any kind,
no `scripts/checklist_engine.py`. `ADMIRAL_RULING-1` R2 and R3 both respected —
the rework's hook diff adds no new `cwd` read and no new `raise`, so no
fail-closed refusal and no `cwd` threading. The stale `KeyError`-era door claims
are the Commander's `reconcile` step and I do not report them.

## Evidence verdict

Present, reproducible, and it reproduces for me. I re-measured the whole Evidence
Produced table at `6bba3fd2`: targeted selector 14 passed / 152 deselected / 21
subtests; `test_spine_rail.py` + `test_worktree_derivation.py` green; derivation
19 passed alone; full suite 3183 / 5 / 0. The differential runs, exits 0, prints
honest rows, and agrees with my independent instrument everywhere they overlap.
TDD was required and satisfied — red at 8 failed / 11 passed, green at 14.

**The gap is scope, not honesty.** Every SessionStart row of every instrument on
this gate — the differential's section (5), all six new tests, and the two
rewritten ones — deliberately places its spines **outside**
`<proj>/.agent-work/*/spine.json` so the blind scan finds nothing. That scoping is
stated openly in the differential's own section header and in the withhold test's
docstring, so it is honest rather than concealed. But it means **no evidence on
this gate exercises the in-tree topology** — which is the topology this lane
actually runs in, and exactly where the change regresses. Evidence that cannot
reach the defect is why a third instrument had to exist.

## Code/doc quality

High in the code, and the prose is where it slips. `_own_entries` is a good
extraction: one comparison, two sites, no possible drift on "is this mine", and it
fits both call shapes without contorting either. Routing `decide_stop`'s selection
through it with no behaviour change is the right way to land a shared helper.
Keeping the *fallback* unshared is defensible reasoning that happens to be wrong
for a reason nobody had measured.

Refactoring pass (Fowler) recorded at
`.agent-work/cleanup-f-derive-worktree/FOWLER_PASS-g3-reviewer-attempt-2.json`;
`scripts/verify_fowler_pass.py` exits 0 (smells=12, flagged=`long-method`,
`comments-as-deodorant`; overridden=`data-clumps`, `primitive-obsession`,
`divergent-change`, each with its standard logged). Both flags tie to a finding
rather than decorating the review:

- **`long-method`** — `decide_session_start` is ~105 lines doing selection, blind
  scan, bind-on-resume and rendering in one body. The coupling between its first
  and third parts **is** B4, and at that length nothing invites a reader to check
  it. Extracting the bind step would put the missing discriminator on one visible
  line of the caller.
- **`comments-as-deodorant`** — the rework added ~45 comment lines to that
  function and grew the section header from 4 lines to 19, arguing a property the
  code does not have. This is the smell in its harmful form: prose standing in for
  a structural guarantee, in a function too long to check cheaply.

Inherited-rule check: `a check that cannot fail is indistinguishable from one that
passed` — met, B1 fixed and the guard survives four attacks. `Pin a claim to the
revision you read it at` — met. `Assert against behaviour, never against text` —
met. Windows expectations constructed, not inherited — met. **Broken:**
`global-crew.md` — *"No hidden fallback; fail visibly."* B4 is that rule broken,
and the doctrine names it better than I did.

Minor, not a blocker: `CREW_CONTEXT`'s "any guard that loops must assert what it
looped over" is honoured by `test_session_start_location_data_is_inert_not_load_bearing`
(`assertEqual(len(rows), 6)`) but not by
`test_session_start_withholds_when_it_cannot_say_who_is_starting`, whose four-row
`subTest` loop asserts no count.

## Map impact verdict

- **Evidence supports claimed change:** yes for the selection change at both
  sites, per call. **No** for the claim *"fail-safe not fail-open, now
  demonstrated at both sites"* — demonstrated per call only, and false across a
  SessionStart followed by a Stop.
- **Constraints not violated:** four of five hold — stdlib-only, #549 two-way
  rendering, nudges by `sid`, derivation table unedited. **Fail-safe does not
  hold** (B4).
- **Notes match the diff:** yes. `_own_entries` added beside `_is_own_entry` with
  exactly 2 call sites; `decide_session_start` gained `session_view_provenance` +
  `binding_key` reads it had neither of before; `_entry_mid_flight_view`,
  `_same_path`, `_worktree_from_spine` unchanged. `map/INDEX.md`'s counts are
  consistent with the change rather than hand-written — `scripts` 1224 → 1225 is
  the single new `_own_entries`, `tests` 4843 → 4850 is +7 = 6 new methods + the
  new `_parent_and_out_of_tree_crew` helper, renames net zero. I did not re-run
  `py -m scripts.code_map build`, to avoid dirtying the worktree; the arithmetic
  is the check.
- **Decision candidates surfaced:** yes, and argued rather than asserted. My
  adjudication is above.
- **Durable context routed:** yes — three new triage candidates (`tc5`–`tc7`) on
  the survey.

## Reconciliation check

No `docs/` or contract change needed. This gate removes no guard from a leased
spine; it moves an ownership question off the tree, which is what
`worktree-is-location-spine-path-is-identity` asks for. That decision now holds at
both call sites in their selection decisions. Where it does **not** hold is one
step later: the scan-bind writes an ownership fact that no binding key ever
authorised, and the same decision then reads it as authoritative.

## Blockers

### B4 — the fix's withholding routes a session into the scan-bind, which then manufactures the ownership the fix requires

`scripts/hooks/spine_rail.py:1730-1783`

**The mechanism.** Before this rework, `decide_session_start` selected the first
entry in the merged view, so a session that could *see* any entry left the loop
with `spine` non-`None` and the `if spine is None:` block — which contains
`_scan_active_spine` **and the bind-on-resume write** — never ran. The rework
makes selection ownership-based, which is right, and in doing so newly routes an
entire class of sessions into that block: **those that can see entries but own
none of them.**

On exactly one active-leased spine under `<project>/.agent-work/*/spine.json`,
that block **writes a binding under the bare `sid`** for a spine the session never
claimed. The bare `sid` is precisely the key `_own_entries` reads as OWN. So the
next Stop from that session is answered with another agent's gate **as its own**.

**Measured, three arms, same fixture, the only variable being whether a
SessionStart precedes the Stop** (`/tmp/g3rev2/rev2_composite.py`):

| arm | SessionStart wrote | the later Stop | crew's imperative leaked |
|---|---|---|---|
| OLD `999b7663` | nothing | foreign-owner | no |
| BLOCKED `e3e50a69` | nothing | foreign-owner | no |
| **NEW `6bba3fd2`** | **`binding[sid]` → the crew's spine** | **own-gate** | **YES** |

Control row, same fixture with no SessionStart: all three arms foreign-owner, no
leak. The SessionStart is the whole difference.

**What the parent is actually told** (`/tmp/g3rev2/rev2-forensic.txt`), both
rendered fields:

```
reason:  SPINE MID-FLIGHT: gate g3 is still open -- you are in the MIDDLE of the
         spine ... Next imperative: CREW-MARKER implement the crew gate
context: ENGINE current -> LEASE active: eng-crew (by crew, ...)
         ACTIVE g3 [in-progress] -- CREW-MARKER implement the crew gate
```

That is #549 verbatim — one agent handed another's next imperative as an
instruction to act on — produced by the change whose stated purpose is to end it,
and in the direction that *relaxes* rather than withholds.

**Why every instrument on this gate missed it.** Two reasons, both structural.
The Stop path is unchanged per call — all 13 of my Stop rows are identical
`e3e50a69` → `6bba3fd2` — so the defect is invisible to any single-call
differential. And every SessionStart row on this gate places its spines outside
the scan's glob, so the scan never fires in any of them. The defect needs the
in-tree topology *and* two calls.

**Reachability.** The shape is: (a) the merged view is non-empty, (b) the acting
agent owns none of it, (c) exactly one active-leased spine sits under
`<project>/.agent-work/*/spine.json`. Concretely: a crew claims the in-tree spine
under `sid#agent_id`, the parent has no claim of its own, and the parent's session
restarts after a compaction. That is this lane's own topology, and restarts after
compaction are routine on it.

**This is not `tc1`, and I checked that before writing it up.** `tc1` is that the
scan-bind exists and binds a session to a spine it never claimed — recorded, and
I do not re-report it. What is new here, and recorded nowhere, is that **this
change widens who reaches it, and that the binding it writes then defeats the
Stop path's foreign-owner withholding.** The first reviewer wrote "fixing B2 does
not close `tc1`", which is true; nobody measured that fixing B2 *feeds* it.

**Fix.** Distinguish the two situations `decide_session_start` currently
conflates, both of which are already in hand at that point in the function:

- `sid_bindings` empty → scan and bind. The pre-existing #261 path, untouched.
- `sid_bindings` non-empty and `_own_entries(...) == []` → withhold. Fall through
  for advisory context if that is wanted, but **write no binding**.

That is a condition on the existing branch. It touches neither
`_scan_active_spine` nor `tc1`'s open authority question, and it does not require
unifying the two sites' fallbacks — the refinement can stand once the fallback
stops writing ownership.

**Scoped null.** I tested the SessionStart→Stop pair. I did not test longer
sequences, concurrent sessions racing the same `_binding_transaction`, or the
gauge writer's reading of a scan-written binding.

## Out-of-scope observations

Recorded as triage candidates on the survey. The four the handoff named as
already recorded (`tc1` scan-bind, `agent_id: null` on Stop, `bind()`'s `None`
substitution, `map/ids.jsonl`) I confirmed still stand and do not re-report.

1. **`tc5` — provenance is last-key-wins on a path collision, so a session can
   stop owning its own entry.** When a parent and its own subagent both bind the
   **same** abs spine path, `session_view_provenance` attributes it to whichever
   key `_session_keys` lists last — the subagent's. Measured on three arms: the
   parent's SessionStart then gets no context and its Stop gets foreign-owner
   wording with its **own** imperative withheld. The Stop half pre-exists the
   rework and the first review passed it; the SessionStart half is new here. Both
   are in the withholding direction, so this is not a rail relaxation. Worth
   recording because "which of two keys owns a path both claimed" is a real
   question this gate's rule does not answer.
2. **`tc6` — the differential's guard identifies arms by symbol, not by
   revision.** It proves "BEFORE is some revision before g3 touched the hook", not
   "BEFORE is `999b7663`"; `BASE_REV = c23c3d0f` printed a full happy table. It
   refuses every degenerate direction I could construct, so this is a limit, not a
   defect. Pairing the symbol check with a `git rev-parse` equality on the pinned
   literal would close it for whoever inherits the harness.
3. **`tc7` — `_own_entries`' contract does not name the writer invariant it rests
   on.** Detailed under criterion 8.
4. **The first reviewer's harness cannot answer its own cases 4 and 5.**
   `CREW-MARKER` is a substring of `OTHERCREW-MARKER` and the marker test is a
   substring match, so one rendered gate prints both. It lives in `/tmp` and is
   ephemeral, so this is a note rather than a triage candidate — but this handoff
   calls its six cases "the specification", and two of them cannot be read.

## Workflow Feedback

- **Handoff gaps:** (a) **Close Criterion 1 is the best-written check I have been
  given on this lane and it is why B4 was found.** It did not say "confirm B2 is
  fixed"; it said the harness "was written to expose one defect, not to prove a
  fix", then **named three specific extensions**, one of which was "the
  interaction with the fallback scan". I would not have constructed the in-tree
  case on my own initiative — every artifact I had inherited placed its spines
  outside the glob, and I would have inherited that framing with them. A criterion
  that names the falsifier does the reviewer's hardest thinking for it, and this
  is now twice on this gate (the first review said the same of its criterion 4).
  (b) **Criterion 6's list is the right list and it is scoped to single calls.**
  Every item on it — fail-safe posture, nudge keying, two-way rendering, the Stop
  path's rows — is a property of one hook invocation, and B4 is a property of two.
  Adding "and re-check the properties that hold across a SEQUENCE of calls, since
  this hook's sites share one mutable store" would have pointed straight at it.
  (c) The Evidence Produced table now carries the revision each number was
  measured at, which the first review asked for. It worked: I could reconcile
  every row without asking what "the Commander re-ran" meant.
- **Context rediscovered:** that `decide_session_start`'s selection branch and its
  bind-on-resume branch are the same `if spine is None:` block, so a change to
  what the first one returns is a change to how often the second one **writes**.
  Nothing in the handoff, the Map Anchors, the implementer's result or the first
  review connects those two, and all three of us read the function. The Map
  Anchors list `session_view` / `session_view_provenance` / `_scan_active_spine`
  as separate structural anchors; one line saying "`decide_session_start`'s
  binding read and its scan-bind write are one branch, so withholding at the read
  routes traffic into the write" is the fact B4 turns on.
- **Instructions improvised around:** the reviewer skill still opens with "a spine
  is bound for you; `spine_status` is your first call" — fifth crew on this issue
  to report it. My `crew-runs.json` entry has `spine: null` while
  `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` point at the parent Commander's
  spine under the parent's live lease, so obeying literally means driving someone
  else's gate. I authored my own survey at the handoff's path, claimed it with my
  own session id, and drove all 15 checks through the `checklist_engine.py` CLI.
  Two smaller ones: `--session-id` is a **per-verb** argument, not a global, so
  the natural `--file X --session-id Y start item` fails with an unhelpful
  "invalid choice" pointing at the verb list; and `attach` requires `--type`,
  which the skill's prose does not mention. Both cost one retry each. The Fowler
  path collision the handoff warned me about is real and I did as instructed —
  instantiated at `FOWLER_PASS-g3-reviewer-attempt-2.json` up front rather than
  amending the postcondition afterwards. That advice saved a repair cycle and
  belongs in the survey template, not in a per-gate handoff.
- **What would have made this easier:** **the handoff's own ordering — "build your
  own instrument before you run theirs" — is now load-bearing twice and should be
  promoted from this gate's prose into the reviewer skill.** It is what found B1
  last time and B4 this time, and the mechanism is the same both times: an
  inherited instrument carries the inherited framing, so a reviewer who runs it
  first inherits the blind spot along with the numbers. Writing mine first is why
  I constructed an in-tree case at all — not because I suspected anything, but
  because I had not yet been told which shapes mattered.

## On the Stop hook

I refused it, and I am recording the refusal here as instructed.

Measured rather than assumed: `SPINE_FILE` →
`.agent-work/cleanup-f-derive-worktree/spine.json`; `SPINE_SESSION` →
`constellation/cleanup-f-derive-worktree/execute/commander`, not mine;
`SPINE_PARENT` → `constellation/cleanup-f-derive-worktree/execute/commander/attempt-4`;
my own `crew-runs.json` entry has `spine: null`. Obeying a `SPINE MID-FLIGHT`
nudge would mean advancing my parent's gate under my parent's live lease, and the
hook's escape hatches (`block`, `waive`) write to that same spine, so the
sanctioned honest stop is itself the destructive act. **I wrote nothing to the
parent spine.**

I authored my own survey at
`.agent-work/cleanup-f-derive-worktree/g3-review-rework/review.json`, claimed it
with my own session id, drove all 15 checks, and consolidated there.

Worth one line, since B4 is adjacent to it: the mechanism behind this nudge is
`tc1`, and B4 is not `tc1`. `tc1` is that the scan-bind exists. B4 is that this
change sends a new class of sessions into it and then reads what it writes as
ownership. Fixing B4 does not close `tc1`; closing `tc1` would close B4 as a side
effect, which is one more reason the authority decision on `tc1` matters.

**Postscript — it fired twice.** After this result was written, my survey
consolidated and my own lease released, the `SPINE MID-FLIGHT` nudge fired again
with the parent's `execute` imperative. I refused it again and wrote nothing to
the parent spine. Re-verified at that moment rather than assumed: `SPINE_FILE`'s
`engine_session` is `{"session_id": "commander-cleanup-f-derive-worktree",
"status": "active", "claimed_by": "commander"}` — an active lease held by someone
else — while my own survey shows `status: released` and no open items. Recording
it because it is evidence for `tc1`'s authority decision: the nudge is not tied to
having work left, and it repeats after an honest, complete finish. This run's
correct exit was to refuse twice, and the second refusal cost a turn to establish
that nothing had changed.

## Return status

`complete`
