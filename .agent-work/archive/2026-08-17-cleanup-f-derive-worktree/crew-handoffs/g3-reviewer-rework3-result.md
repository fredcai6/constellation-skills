# Review Result

## Assigned Gate

`g3` — lane F, issue #609, rework 3. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`, head `68d190f7` (handoff commit `b8efbad2`).
Fourth review of this gate.

Survey: `.agent-work/cleanup-f-derive-worktree/g3-review-rework3/review.json`,
driven through the engine gate by gate, consolidated `BLOCK`, 4 findings.
Fowler record: `.agent-work/cleanup-f-derive-worktree/FOWLER_PASS-g3-reviewer-attempt-4.json`
(`verify_fowler_pass.py` exits 0).

## Result

`BLOCK`

**B5 is genuinely fixed.** I reproduced it independently, and the fix is narrow:
an enumeration of five topologies × two scan-match counts shows rework 3 changes
exactly **one row of ten**, and it is B5's own. Eight of the ten Close Criteria
pass.

Two fail, and both are the same shape as this gate's history — a door one step
beyond where the last instrument stopped.

## Per-criterion findings

| # | criterion | verdict |
|---|---|---|
| 1 | B5 is actually fixed | **pass** |
| 2 | B4 stays fixed | **pass** |
| 3 | the writer guard is correct and complete | **FAIL** — B6, B7 |
| 4 | the guard is not too broad | **pass** |
| 5 | #261's bind-on-resume still works | **pass** |
| 6 | the `return {}` on refusal | **pass** |
| 7 | fail-safe direction | **pass** |
| 8 | nothing from any prior review regressed | **pass** |
| 9 | suite arithmetic reconciles | **pass** |
| 10 | prose | **FAIL** — B7's sentence, in three places |

### 1. B5 is actually fixed — pass

I built my own instrument (`g3-review-rework3/rev4_instrument.py`) rather than
running theirs. Production writers only: every binding entry is written by
`handle_post_tool_use` from the repo's pinned probe capture. Three arms, each
printing the **sha256 and byte length of the source it actually loaded**, with a
guard asserting all three differ and that `_attributed_to_another_key` is present
in `WORKTREE` and absent from `REWORK2`.

```
arm PREGATE   999b7663   sha256=37cf424e9711 bytes=74877
arm REWORK2   7d12c29d   sha256=f0cde2e7b4c6 bytes=84999
arm WORKTREE  worktree   sha256=4b5cf14d5278 bytes=89859
guard ok: 3 distinct arms, symbol present only in WORKTREE

C1 B5 single-active
  PREGATE   {"attribution_after": "<sid>#<agent>", "bound": false, "crew_keeps_own_gate": false,
             "parent_stop_leaks": false, "render_leaks_CREW-MARKER": true}
  REWORK2   {"attribution_after": "<sid>",         "bound": true,  "crew_keeps_own_gate": false,
             "parent_stop_leaks": true,  "render_leaks_CREW-MARKER": true}
  WORKTREE  {"attribution_after": "<sid>#<agent>", "bound": false, "crew_keeps_own_gate": true,
             "parent_stop_leaks": false, "render_leaks_CREW-MARKER": false}
```

No bind, no leak, the attribution stays with the crew's key, and the crew keeps
its own gate — true **only** on `WORKTREE`, including against `PREGATE`, exactly
as the handoff claimed.

The harness-pin hazard is real and I confirmed it rather than tripping on it:
`g3-review-rework2/rev3_production_sequence.py` pins its `HEAD` arm to
`c5ad8d61`, a commit the tree has moved past. I did not rely on it.

### 2. B4 stays fixed — pass

`rev4_instrument.py` C3: parent owns nothing visible, only the crew's in-tree
spine. `WORKTREE` and `REWORK2` both write no binding and render nothing;
`PREGATE` leaks. Also rows 3–4 of the enumeration matrix, unchanged between arms.

### 3. The writer guard is correct and complete — **FAIL**

The guard is correct. It is not complete, in two directions, and both are
measured.

#### B6 — BLOCKER. The same door still *renders* another key's gate when the scan is ambiguous.

The guard sits **inside** `if len(matches) == 1 and sid:` and **after**
`spine = matches[0][0]`. So it governs the write, on an unambiguous scan, and
nothing else. With two or more active-leased spines the code writes no binding by
construction — and still renders `matches[0]`, **chosen by glob order, not by
binding-key provenance**.

`rev4_c2b.py` removes glob order as a variable: the crew claims **both**
remaining active spines (#202 already sanctions one key holding N), so whichever
one the glob returns first is one the store visibly attributes to another
binding key. The fixture asserts that before it measures anything.

```
PREGATE   {"every_match_owned_by_crew": true, "renders_a_crew_gate": true,
           "renders_pick_it_up": true, "scan_matches": 2, "wrote_a_binding": false}
REWORK2   {... identical ...}
WORKTREE  {... identical ...}

WORKTREE rendered additionalContext ->
  RESUMING an active Constellation spine run after a restart or compaction.
  ENGINE current -> LEASE active: eng-a (by commander, ...)
  ACTIVE g3 [in-progress] -- CREWA-MARKER the crew's first ...
```

The parent is handed the crew's imperative and told to *"Pick the run back up at
this gate and drive it through the engine"*. That is the #549 failure class this
gate exists to end, unchanged by the gate, on the door this rework opened. B5's
own finding named this field: *"naming the crew's gate there is the same leak in
the other field."* Rework 3 asserts its absence only in the single-match fixture.

This is not hypothetical topology. Two `spine.json` under one `.agent-work` is an
Admiral plus a Commander, or two Commanders in one tree.

The fix is small and stays inside the rule already agreed: apply the same
predicate to the **render selection** — refuse `matches[0]` for `spine` when it
is attributed to another key — rather than only to the write. That also removes
the `len(matches) == 1` coupling, which is about *ambiguity*, not about ownership.

#### B7 — BLOCKER. `owners` is the acting session's *view*, not the store.

At the call site, `owners = session_view_provenance(binding, sid)` — the bare
`sid` key plus this session's own `sid#agent` keys. An attribution held by a
**different harness session_id** is not in it, so the guard cannot see it and the
bind proceeds.

`rev4_instrument.py` C5: another session claims the crew's spine, the parent's
own entry is archived, one active spine remains.

```
C5 cross-SESSION attribution
  PREGATE   {"bound": true, "parent_stop_claims_it_as_own": true, "render_leaks_CREW-MARKER": true}
  REWORK2   {... identical ...}
  WORKTREE  {... identical ...}
```

The parent binds to a spine another key holds and its next Stop renders it as its
own gate — B5's damage, one door over, on all three arms. `run_crew.py` launches
each crew as its own `claude -p` session, so cross-session claims in one tree are
this project's normal case, not an exotic one.

I am **not** asking for the guard to be widened without a decision: whether a
resume may bind across a session boundary sits next to the recorded `tc1`
authority question and is the Admiral's call. What blocks here is that the code
**states** the wider rule while implementing the narrower one — see criterion 10.

#### The three attacks the handoff named — all clean

- **Path normalisation.** Correct in both platform directions. `os.path.normcase`
  is the identity on this host, so I constructed the case expectation explicitly
  and then simulated a Windows host by substituting `str.lower` for `normcase`
  (`rev4_probes.py` P1, restoration asserted):

  | | `_same_path(lower, upper)` | guard refuses? |
  |---|---|---|
  | linux (measured) | `False` | `False` — correct: two different files |
  | win32 (simulated) | `True` | `True` — correct: one file |

  This is the right answer on each platform, not an accident that happens to pass
  here.
- **Same path under two keys.** Handled: `session_view_provenance` is
  last-key-wins (recorded `tc5`), so the surviving attribution is the one both
  the reader and this guard agree on. Where the winner is the bare `sid` itself,
  the write is a no-op refresh of the session's own entry.
- **An unusable `bind_key`.** Unreachable: `if len(matches) == 1 and sid:` already
  excludes a falsy `sid`, and a session whose entries are keyed `sid#agent` never
  reaches the fallback — `_own_entries` returns empty and the B4 branch above
  returns `{}` first.

### 4. The guard is not too broad — pass, measured

`rev4_who_newly_gets_nothing.py` enumerates five topologies × two scan-match
counts on the `REWORK2` and `WORKTREE` arms and prints what it looped over.

| topology | extra active spines | changed by rework 3? |
|---|---|---|
| no binding at all (#261) | 0, 1 | no |
| owns nothing visible; crew claims the scanned spine (B4) | 0, 1 | no |
| owns an ARCHIVED entry; crew claims the scanned spine (B5) | 0 | **yes** |
| owns an ARCHIVED entry; crew claims the scanned spine (B5) | 1 | no ← B6 |
| owns an ARCHIVED entry; scanned spine claimed by NOBODY (tc1) | 0, 1 | no |
| owns an ARCHIVED entry; scanned spine is its OWN bare claim | 0, 1 | no |

```
rows measured: 20   topologies x match-counts: 10   rows whose answer rework 3 changed: 1
```

Exactly one row. Nobody legitimate newly gets nothing. `tc1`'s
bind-a-spine-nobody-claimed row still binds, deliberately, and the session's own
bare claim still binds. `#202`'s
`test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding` has no
hunk touching it anywhere in `999b7663..68d190f7` and is green.

The same table is where B6 shows up as an unchanged row, which is why I ran it
this way rather than as a list of assertions.

### 5. #261's bind-on-resume still works — pass

`rev4_instrument.py` C4: empty binding store, one active-leased spine → bound on
all three arms, and the render carries the session's **own** marker. Enumeration
rows 1–2 agree.

### 6. The `return {}` on refusal — pass

Returning is right. By the time the guard runs, `spine` is already
`matches[0][0]`, so skipping only the write would still render the foreign gate —
the leak in the other field. Nothing legitimate is lost: the refused session is
one whose own spine no longer loads, so the only context on offer was another
binding key's gate. It matches the shape of the B4 branch one level up.

(That `spine` is assigned before the guard is exactly what makes B6 possible one
match-count over. The two answers are consistent: withhold the render too.)

### 7. Fail-safe direction — pass

`rev4_probes.py` P2, eight adversarial inputs: `owners.items()` raising, an
`owner_key` whose `__eq__` raises, `None` owners, list owners, `None` spine path,
`None` bind key, a non-str owners key, a `None` owner key. **All eight answer
`True` (refuse); none raises.** I could not make it raise.

No deadlock for a genuine owner. A session whose own spine loads never reaches
the fallback (`spine` is not `None`), and if `owners` were unusable then
`_own_entries` returns `[]` and the earlier `sid_bindings and not owned` branch
returns `{}` before the guard is consulted. The two withholding directions agree.

### 8. Nothing from any prior review regressed — pass

The rework-3 `spine_rail.py` diff is five hunks: the module header comment,
`_own_entries`' docstring (×2), the new function, and two blocks in
`decide_session_start`. `decide_stop`, `_scan_active_spine` and
`_entry_mid_flight_view` are byte-unchanged.

- **Stop path** — unchanged, and measured working in C1 both ways.
- **Nudge keyed by session id alone** — measured, not read:
  `parent → count 1, crew → 2, parent → 3 (escape hatch, decision continue),
  crew → 4`. One shared counter, never fragmented per entry.
- **#549 two-way rendering** — parent gets the foreign-owned wording with the
  imperative withheld; the crew still gets `CREW-MARKER` as its own (C1).
- **stdlib-only imports** — `errno, json, os, re, shlex, subprocess, sys,
  tempfile, time, datetime, pathlib`, plus the guarded optional `msvcrt`.
- **`_own_entries` still shared** — called by `decide_stop` and
  `decide_session_start`; ownership-based selection intact at both.
- **`tests/test_worktree_derivation.py`** — unedited across the whole gate, green.
- **The differential's guard** — `_assert_arms_are_what_they_claim` untouched
  since rework 1 (`6bba3fd2`), verified by `git log`. I did **not** re-run it: its
  arms are pinned to superseded revisions, so a green run would prove nothing
  about this tree. Stating that plainly rather than claiming a re-run.

### 9. Suite arithmetic reconciles — pass

| measurement | result |
|---|---|
| full suite, `__pycache__` cleared, env scrubbed | **3190 passed, 5 skipped, 0 failed** |
| targeted `-k OwnershipIsBindingKeyNotWorktree` | **21 collected** (`--collect-only`), 21 passed, 33 subtests |
| `def test_` count in `tests/test_spine_rail.py` | 170 → **173** |
| `map/INDEX.md` | `scripts.hooks.spine_rail` 64 → **65**; `tests.test_spine_rail` 213 → **217** |

3187 → 3190 = +3; targeted 18 → 21 = +3. The diff removes two test defs and adds
them back renamed, adds three genuinely new ones plus one non-test helper: 3 + 1
= the map's +4 test entities, 1 = the map's +1 script entity. No quiet deletion.

### 10. Prose — **FAIL**

One fresh sentence is false about the tree as it stands, and rework 3 writes it
three times.

> `_attributed_to_another_key`: *"Whether **the store** ALREADY attributes
> `spine_path` to a binding key other than `bind_key`"*

The call site passes `session_view_provenance(binding, sid)` — this **session's
view** of the store, never the store. The same overstatement appears at the call
site (*"it may not CONTRADICT an attribution the store already holds"*) and in
the new test's docstring (*"must not file a spine path the store already
attributes to a DIFFERENT binding key"*).

This is not pedantry about a word. C5 measures the difference: a real attribution
the sentence claims is covered, and the code cannot see. It is the same failure
mode as the comment B5's finding caught — a sentence true of the case in front of
the author and false of the case one door over — and it is the sentence the next
reader will grep.

Everything else in the changed regions checks out sentence by sentence:

- *"provenance is last-key-wins, so the write hands this session the other
  agent's gate as its own AND takes that gate away from the agent that claimed
  it"* — measured, C1's `REWORK2` row, both directions.
- *"Paths are compared with `_same_path`, so a differently-spelled route to the
  same file still counts"* — true; P1 confirms both platform directions.
- *"NEVER raises"* — P2, eight adversarial inputs.
- *"#261's resumed session and #202's sibling merge are both untouched"* —
  enumeration rows 1–2 and the #202 test.
- *"a SessionStart, blocking nothing, hands out nothing — and writes nothing"* —
  **true**, and I checked it carefully because B6 looks like a counterexample: the
  sentence is scoped to the owns-nothing-visible door, where the code does return
  `{}` before the scan. It is not claiming the B5 door. Not a finding.
- The `_own_entries` docstring's new paragraph — accurate, including its
  self-correction that its own answer cannot speak for the second door.

## Handoff compliance

The handoff asked for B5 answered at the writer, and that landed: correct,
minimal, no collateral (criteria 1 and 4). But the gate asked to be judged
against all ten Close Criteria and two fail, so the handoff is not satisfied.

## Scope drift

None. `68d190f7` touches `scripts/hooks/spine_rail.py`,
`tests/test_spine_rail.py`, `map/INDEX.md` and
`.agent-work/**/crew-handoffs/g3-implement*` — all inside Allowed Scope. Every
Specific Exclusion holds: no change to lane A's files, lane E's files,
`scripts/verify_worktree_isolation.py`, any template, or
`scripts/checklist_engine.py`. No fail-closed refusal (`ADMIRAL_RULING-1` R2) —
the guard withholds a write, it never refuses a tool call — and no `cwd`
threading (R3). Exclusions naming paths outside this worktree are
Commander-verified, not reviewer-verified; noted, not blocked on.

**On the scope note I was invited to challenge:** re-opening the bind-on-resume
writer is correct and is the minimum that answers B5. I do **not** think the
guard reaches into `tc1`'s territory — measured, it changes one row of ten and
leaves every bind-a-spine-nobody-claimed row alone. The scope call was right.

## Evidence verdict

Every row of the handoff's Evidence Produced table reproduces, and I re-derived
each one independently rather than re-running the supplied harness. All cited
shas resolve. The claimed shelf-life defect in `rev3_production_sequence.py` is
real (`HEAD` pinned to `c5ad8d61`) and I avoided it. Test mode is satisfied: the
three new tests are behaviour-focused, and the new fixture asserts which door it
uses before it measures anything.

## Code/doc quality

Minimal and well-placed. Moving the rule to the writer is the right structural
call and I would keep it. Fowler pass:
`flagged = [long-method, duplicated-code, shotgun-surgery]`,
`overridden = [large-class, primitive-obsession, comments-as-deodorant]`, each
override carrying the standard that wins and why. The shotgun-surgery flag is the
one that fed this review: the same rule has needed a new site in each of three
reworks, and it is measurably needed at a fourth — which is B6.

`decide_session_start` is now 159 lines, 62 code and 92 comment, and the
three-states taxonomy is stated in four places. Two of those copies have already
been wrong once each on this gate. Neither is a blocker.

## Map impact verdict

- **Evidence supports claimed change:** yes — reproduced independently.
- **Constraints not violated:** yes — exclusions and both Admiral rulings hold.
- **Notes match the diff:** yes — `map/INDEX.md` was regenerated in the same
  commit and its entity counts reconcile exactly with the diff.
- **Decision candidates surfaced:** partly. B7's widening question needed
  surfacing as a decision and was instead absorbed into a sentence that claims
  the wider rule. That is the shape of the criterion-10 failure.
- **Durable context routed:** yes — three triage candidates recorded in the
  survey.

Architecture-insignificant otherwise: one module-private predicate, no new
boundary or contract.

## Reconciliation check

No unreconciled divergence. The stale `KeyError`-era door claims are the
Commander's `reconcile` step and are not findings.

## Blockers

1. **B6 — the ambiguous-scan render path.** `decide_session_start` selects
   `matches[0]` for the resume context by glob order rather than by binding-key
   provenance, so with ≥2 active-leased spines a session on B5's door is still
   handed another key's gate plus *"Pick the run back up at this gate and drive
   it through the engine"*. Measured identical on `PREGATE`, `REWORK2` and
   `WORKTREE`, with glob order removed as a variable
   (`g3-review-rework3/rev4_c2b.py`, `rev4-c2b.txt`). Suggested repair: apply
   `_attributed_to_another_key` to the render selection as well as the write,
   which also decouples the rule from `len(matches) == 1`.

2. **B7 — `owners` is a session view, and three fresh sentences call it the
   store.** A cross-session attribution is invisible to the guard and the bind
   proceeds (`rev4_instrument.py` C5, identical on all three arms). The
   **prose** must be corrected either way — that alone clears this blocker.
   Whether to widen the guard across the session boundary is an Admiral
   decision, not the implementer's, and it sits next to the recorded `tc1`
   authority question.

## Out-of-scope observations

- The three-states taxonomy is stated in four places in `spine_rail.py`; two
  copies have already gone stale on this gate. State it once, point at it.
- `decide_session_start` at 159 lines is the natural home for an extraction: the
  bind-on-resume writer block is already a distinct decision with its own guard.
- The two candidates above plus B7's widening question are recorded as triage
  candidates in the survey.

## The three scoped nulls left open by review 3

I closed two of the three.

- **Three-or-more call sequences — CLOSED.** `rev4_probes.py` P3 runs
  SessionStart → Stop → SessionStart → Stop on B5's topology at `WORKTREE`. No
  binding is written on any round and the attribution never moves. Round 2 does
  differ from round 1 — the parent's Stop stops blocking — and that is **not** a
  leak: it is the documented 3-strike escape hatch, keyed by session id alone and
  therefore shared between the parent's and the crew's stops. I measured the
  counter directly (`1, 2, 3, 4`) rather than inferring it, because a reviewer
  reading only round 2 would read the escape hatch as a regression.
- **The gauge writer's reading of a scan-written binding — CLOSED, and it favours
  the fix.** `rev4_probes.py` P4: after the refused bind, the parent key resolves
  to one gauge path (its own) and the crew key to its own. In the counterfactual
  where the bind is present — what rework 2 wrote — the parent key resolves to
  **two** candidates, its own and the crew's, which is the 2+-candidate state
  #600 made the writer reason about. The refusal keeps that candidate set clean.
- **Concurrent sessions racing `_binding_transaction` — NOT closed.** Not cheap
  from a single-process harness, and I did not attempt it. It remains open, and
  nothing in this review speaks to it.

## The open decision, argued by five crews

**The refinement survives, and rework 3 is what completes it — but the way it is
stated is what keeps costing this gate a review.**

Review 1's formulation ("blocking is a spine property at both sites; selection is
a binding-key property at both sites") is right and I would not overturn it. B4
and B5 both arriving through the unshared fallback is **not** evidence against
it. It is evidence that the fallback was never actually obeying it. Look at what
each site does with a selection it has withheld:

- `decide_stop` withholds and then **renders** the withheld thing, in the
  foreign-owner wording, with the imperative removed. Selection governs the
  render.
- `decide_session_start` withheld and then **fell through to a writer and a
  renderer that select by something else entirely** — glob order. B4 fixed the
  fall-through for one door. B5 fixed the write for the other. B6 is the render
  on that same door, still selecting by glob order.

So the correct reading is not "the comparison is shared, the fallback is not" and
not "the sites are asymmetric". It is: **selection is a binding-key property at
every site that selects, and the scan's fallback is a third selection site that
has never been held to the rule.** Rework 3's writer constraint is that rule
reaching the fallback's *write*; the missing half is the same rule reaching the
fallback's *render*. `_attributed_to_another_key` is the right shared instrument
for both — it is the first thing on this gate that is a property of the store
rather than of one call path, which is why I would keep it and extend its reach
rather than add a fourth site-specific rule.

Where I disagree with the handoff's framing: the guard is described as "a shared
constraint on the *writer* both fallbacks reach". It is not shared with the store
— it reads one session's view (B7). Fixing the sentence and fixing the reach are
the same conversation, and that is the one I would put to the Admiral.

## Workflow Feedback

- **Handoff gaps:** the "Survey State Location" section says *"The survey
  template hardcodes the Fowler record at `.agent-work/<work-id>/FOWLER_PASS.json`"*.
  That is true of the **installed** copy at
  `~/.claude/skills/constellation-reviewer/templates/`, but this repo's own
  overlay at `.agent-work/templates/REVIEW_SURVEY.template.json` ships a
  `<fowler-pass-record-path>` **placeholder** with an explicit instantiation-time
  substitution path and a documented `amend` repair path. The two copies have
  diverged. Following the handoff literally would have sent me down the repair
  path for a problem the governing template no longer has. I used the overlay,
  substituted at instantiation, and needed no `amend`.
- **Context rediscovered:** that the enumeration in criterion 4 ("enumerate who
  newly gets nothing") and the completeness attack in criterion 3 are the **same
  measurement** read in two directions — the rows that changed answer 4, the rows
  that did not answer 3. Nothing in the handoff connects them, and I nearly built
  two harnesses. One matrix answers both, and it is the artifact I would hand the
  fifth reviewer first.
- **Instructions improvised around:** `flag-candidate` numbers triage candidates
  `tc1, tc2, tc3` **per survey file**. Seven surveys on this gate each start at
  `tc1`, and the handoff's "Findings already recorded" list cites `tc1`, `tc5`,
  `tc6`, `tc7` from earlier surveys as if the ids were gate-wide. My survey's
  `tc1` is a different finding from the `tc1` the handoff tells me not to
  re-report. I named my findings B6/B7 in prose to avoid the collision, but the
  ids in `review.json` will read as duplicates to anyone reading across surveys.
- **What would have made this easier:** the handoff's Close Criteria are ordered
  by what the implementer did, not by what a reviewer must build. Criteria 1, 2,
  3, 4, 5 are all one parameterised matrix over (topology × scan-match count ×
  arm); 6, 7, 10 are cheap follow-ons; 8, 9 are bookkeeping. Saying so — "these
  five are one instrument" — would save the fifth reviewer an hour and would have
  made B6 unmissable, because it is a row in that matrix that nobody had a reason
  to add.

## On the Stop hook

**It fired, twice, and I refused it.** Recorded as instructed, as observed fact
rather than as a prediction: at the end of my turn a `SPINE MID-FLIGHT` hook
told me `gate execute is still open`, to reload the commander skill, rewrite
`STATE_NOTE.md` and drive `execute.json` gate by gate.

I refused. `SPINE_FILE` points at the Commander's spine
(`.agent-work/cleanup-f-derive-worktree/spine.json`) under the Commander's own
live lease — `LEASE active: commander-cleanup-f-derive-worktree (by commander)`.
My own `crew-runs.json` entry has `spine: null`, and my `SPINE_SESSION` is
`constellation/cleanup-f-derive-worktree/execute/commander`, the parent's, not
mine. Obeying would mean advancing another agent's gate.

The hook's own escape hatches are not an exit either: it offers `block` "to
bubble the blocker to the parent", but that verb writes to that same
Commander-leased spine, so the sanctioned honest stop is itself the destructive
act. My blocker reaches my parent the way a crew's blocker is supposed to — as
this result artifact, which exists at the path the handoff named. My own survey
is consolidated to `BLOCK` and its lease released.

I authored that survey at the path the handoff named, claimed it with my own
session id, and drove that.

The irony is on the record: the leak I am blocking on (B6) is the mechanism that
produces exactly this hook for exactly these crews.

## Return status

`complete` — review finished, verdict `BLOCK`, survey consolidated, all checks
visited and recorded.
