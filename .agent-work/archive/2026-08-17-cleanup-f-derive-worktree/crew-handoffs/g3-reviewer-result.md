# Review Result

## Assigned Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. Review target: commit `e3e50a69` over base
`999b7663`.

Survey driven at
`.agent-work/cleanup-f-derive-worktree/g3-review/review.json` — 19 checks (the
7 standard reviewer items plus the handoff's 12 Close Criteria as their own
checks), claimed under session
`constellation/cleanup-f-derive-worktree/g3/reviewer/attempt-1`, all visited,
consolidated.

## Result

`BLOCK`

Three blockers. One is substantive and lives in production code (**B2**); two
are evidence and prose defects that the lane's own doctrine names explicitly
(**B1**, **B3**). All three fixes are small and I have named each one.

The core of the gate is right, and I want that on the record before the
blockers: at `decide_stop` this is a good change, genuinely evidenced, and it
does what the lane set out to do.

## Per-check findings against the Close Criteria

| # | criterion | verdict |
|---|---|---|
| 1 | #549 shape genuinely exercised; red reproduces | **PASS** |
| 2 | fail-safe posture survives | **PASS** |
| 3 | each call site's before/after reproduces when run | **FAIL — B1** |
| 4 | `decide_session_start`'s argument, tested not read | **FAIL — B2** |
| 5 | nothing newly stops blocking | **PASS** |
| 6 | nudge / 3-strike hatch keyed by session id alone | **PASS** |
| 7 | #549's two-way rendering survives | **PASS** |
| 8 | stdlib only, import block unchanged | **PASS** |
| 9 | `_same_path` survives correctly or is deleted | **PASS** |
| 10 | no surviving `worktree_from_spine_path` claim, replacements true | **FAIL — B3** |
| 11 | `tests/test_worktree_derivation.py` unedited and green | **PASS** |
| 12 | suite green, count stated, distribution derived | **PASS** |

### 1 — the #549 shape is genuinely exercised. PASS

The shared tree is real, not asserted. `_parent_and_in_tree_crew` writes both
spines under one `self.proj` and issues both claims with `cwd=self.proj`, then
asserts `len({e["worktree"] for e in entries.values()}) == 1`. The
parent/crew asymmetry is structural rather than hand-written:
`_real_parent_payloads()` filters the sha256-pinned capture for `"agent_id" not
in p` and `_real_subagent_payloads()` for `"agent_id" in p`. The crew claims
*first*, so its key leads the merged view — which is what makes the assertion
about ownership rather than luck. And the assertion is about the parent's own
gate rendering: `PARENT-MARKER` in both `reason` and `additionalContext`,
`CREW-MARKER` in neither.

**Red reproduced independently.** I did not take `m1-red.txt`. I built a scratch
tree at `/tmp/g3rev/constellation-skills`, copied `tests/` and `scripts/`, and
replaced the hook with `git show 999b7663:scripts/hooks/spine_rail.py`
(byte-diff against `999b7663` confirmed empty). Result:

```
8 failed, 3 passed, 152 deselected in 0.37s
```

The implementer's red reported 153 deselected — one more, consistent with its
red predating the net −1 test-count change. Not a defect.

The failure is for the *right* reason. On the old hook the parent's Stop came
back as:

```
SPINE MID-FLIGHT (foreign-owned): a gate on .../run-crew/spine.json is still
open under c9b25095-...#a8f0a946eaaa2fe6c -- STILL BLOCKED, but this is not
your gate to drive.
```

The parent's own open gate never rendered at all. The gate did not do nothing.

### 2 — the fail-safe posture survives. PASS

I built my own differential (`/tmp/g3rev/rev_differential.py`), loading both
hooks as two modules in one process against fresh temp project dirs, 26
scenarios. **Regressions (old BLOCKED → new ALLOWS): 0.**

Garbage I constructed myself — `cwd` absent/int/dict, `worktree`
null/int/empty, `agent_id` `a/b`/``/`12345`/`None` — blocks on both sides.

I tried to make `_is_own_entry` raise, including with an object whose `__eq__`
raises `RuntimeError` on either side, plus `object()`, `bytes` vs `str`, and
`NaN`. It never raised. The catch-all returning `False` is the correct
direction: an errored comparison reads as foreign, which *withholds* rather
than relaxes.

### 3 — the before/after claim. FAIL (B1)

See **Blockers**. The claims are all true; the shipped instrument is not.

### 4 — `decide_session_start`. FAIL (B2)

See **Blockers**. This is the substantive one.

### 5 — nothing newly stops blocking. PASS

Verified in the negative direction by measurement. Every surviving allowed-Stop
shape is unchanged: no binding, unreadable spine, released lease, honest engine
block, and the 3-strike hatch on the third no-progress stop — ALLOW on both
sides in each case. The newly-blocking rows are exactly the implementer's three
declared classes and no more.

*Scoped null:* this covers the Stop path. The SessionStart path has a separate
regression (B2), which is not a blocking regression.

### 6 — nudge keyed by session id alone. PASS

`spine_rail.py:1583-1592` aggregates one progress signal across every
mid-flight entry — `seq` a sum, `active_ids` a sorted list — then writes a
single `nudges[sid]`. Both delete paths key on `sid` alone. The new test
asserts `list(sr.load_nudges(proj)) == [sid]` with *two* mid-flight entries
present, which is the assertion that would catch fragmentation.

### 7 — #549's rendering. PASS, and sharper

Both directions measured, with the imperative checked across **both** rendered
fields together. Bare-`sid` entry → ordinary imperative-bearing reason. Entry
reachable only through another agent's per-agent key → `foreign-owned` wording
with the imperative in neither field. The distinction is now made against
`binding_key(payload)` rather than the bare `sid`, so the crew side of the
inverse works too: a crew is answered with `CREW-MARKER`, not its parent's gate.

### 8 — stdlib only. PASS

Import block byte-identical, extracted by me rather than read off the
implementer's harness: 11 lines, `errno json os re shlex subprocess sys
tempfile time`, `from datetime import datetime, timezone`, `from pathlib import
Path`. Zero cross-module imports; none gained.

### 9 — `_same_path`. PASS

Not dead code. Real callers survive at `spine_rail.py:971`
(`git_worktree_roots`) and `spine_rail.py:1112` (`resolve_spine_candidate`).
`scripts/verify_skip_guard.py` also names its two platform tests in a skip
allowlist, so the pair is load-bearing beyond this file. Keeping it was right.

### 10 — grep for the claim. FAIL (B3)

The symbol side is clean: `worktree_from_spine_path` appears **0** times in the
two files. Repo-wide two remain, both outside allowed scope and both *true*
prose recording the deletion.

I then read each replacement passage whole and tested each sentence. The
`_worktree_from_spine` docstring holds up: "the ONE implementation of the rule
in the repo" is true (`IMPLEMENTATIONS` has the single `hook` entry;
`checklist_engine.py:3507` says outright the engine holds no copy;
`spine_lifecycle.py:96` is a pointer); "its specification is the shared case
table … which drives this function" is true (`_require` raises at collection if
the symbol goes); the `ADMIRAL_RULING-2` N2 attribution and the re-lands-as-a-copy
sentence both hold. The test file's replacement passage holds up too.

One sentence does not. See **B3**.

### 11 — `tests/test_worktree_derivation.py`. PASS

Absent from `git diff 999b7663..e3e50a69 --stat`. Green: 19 passed. Its
`IMPLEMENTATIONS` table and `_require` guard are intact, so the specification
survives whole for #610's wave.

### 12 — suite. PASS

`__pycache__` cleared repo-wide, env scrubbed of `SPINE_FILE`, `SPINE_SESSION`,
`SPINE_PARENT`, `CREW_SCRATCH_DIR`:

```
3177 passed, 5 skipped, 1192 subtests passed in 128.18s   (exit 0)
```

Failure distribution derived mechanically even though empty —
`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c` produced no rows; `FAILED`
line count 0.

**The +7 arithmetic reconciles against the diff**, checked rather than
accepted: 8 new class methods + `test_foreign_worktree_is_gone_and_stays_gone`
= 9 genuinely new; 4 renames that are net zero; exactly 2 outright deletions,
both `_foreign_worktree` unit tests. 9 − 2 = +7. **No test was quietly
deleted.**

## Handoff compliance

The assigned task is done, and at `decide_stop` it is done well. The two sites'
before/after were stated separately, what newly blocks was enumerated with
intent, and the derived worktree is no longer used for identity anywhere in the
Stop path. It fails on two of the handoff's own numbered criteria (3 and 4).

## Scope drift

None. Non-`.agent-work` files in the commit range are exactly `map/INDEX.md`,
`scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`. I checked every
named exclusion mechanically against `git diff --name-only`: no lane A file, no
lane E file, no `scripts/verify_worktree_isolation.py`, no template of any kind,
no `scripts/checklist_engine.py`. No fail-closed refusal was added
(`ADMIRAL_RULING-1` R2 respected — an unplaceable path still yields `None`). No
`cwd` threading (R3 respected). The other `.agent-work` paths in the range are
the Commander's own engine writes bundled into the same commit.

## Evidence verdict

Largely strong and it reproduces — with one broken artifact.

I independently reproduced: the targeted red, the full suite, the derivation
suite, the import block, the +7 arithmetic, and every before/after row once the
differential's base is pinned correctly.

**I read all eight reworked tests looking for a weakened assertion and found
none.** The three flips all *strengthen*: `assert out == {}` becomes `assert
out["decision"] == "block"` plus a marker assertion, and
`test_binding_worktree_comes_from_resolved_spine_in_real_linked_worktree` now
additionally asserts the owner key is named and the child's imperative is
withheld from **both** rendered fields. The device swaps replace a foreign
worktree with a genuinely unreadable target, which is honest — that is the shape
that still reaches the branch. The repaired test
(`test_session_start_unreadable_skip_bound_reinject_fallback_reinject`) is
markedly better than what it replaced: real nested `bind()` shape, the readable
leg placed outside the scan's reach, an explicit `_scan_active_spine(proj) == []`
guard, and a marker assertion, so only the binding can explain the result. That
repair was worth making and the implementer was right to report it.

Two bookkeeping notes, neither a blocker: the result says three tests used a
foreign worktree as a *device* and I count four
(`test_session_start_bind_on_resume_still_writes_under_the_bare_key` is the
fourth); and the `null worktree` row of
`test_garbage_location_data_never_relaxes_the_rail` does not write a null
worktree, because `bind()` substitutes `str(project_dir)` for `None`.

## Code/doc quality

High, apart from B3. `_is_own_entry` is a small named predicate whose two
asymmetric readings of a missing key are documented *and* justified in opposite
directions. The deletion is pinned by a test, so a re-landing is a deliberate
act with a red test to answer for. Narrowing `_entry_mid_flight_view` from
`(data, entry)` to `(entry)` honestly expresses that the site no longer reads
the payload — the signature carries the design claim.

Refactoring pass (Fowler) recorded at
`.agent-work/cleanup-f-derive-worktree/FOWLER_PASS-g3-reviewer-attempt-1.json`;
`scripts/verify_fowler_pass.py` exits 0 (smells=12, flagged=`long-method`,
`duplicated-code`, `comments-as-deodorant`; overridden=`primitive-obsession`
with the stdlib-only + single-composer standard logged). Each flagged smell ties
to a finding rather than decorating the review — notably, extracting
`decide_stop`'s selection step as `_select_entry_for(mid_flight, owners,
own_key)` **is** the B2 fix, because that is precisely the rule
`decide_session_start` is missing.

## Map impact verdict

- **Evidence supports claimed change:** yes for `decide_stop`; **no** for
  `decide_session_start`, where the claimed property is not the one the code has.
- **Constraints not violated:** confirmed — fail-safe, nudge-by-sid, stdlib-only,
  #549 rendering, derivation table unedited. All five hold.
- **Notes match the diff:** yes. Every structural anchor in the Map Impact
  section checks out against the diff, including `_same_path`'s surviving callers.
- **Decision candidates surfaced:** yes — the asymmetry was surfaced as the open
  decision rather than settled silently. I disagree with the proposed resolution;
  see below.
- **Durable context routed:** yes, and I have added three triage candidates.

**The open decision the gate hands back** — *what replaces the skip at each call
site*, `@grade: placeholder`, resolved asymmetrically with a recommendation to
record the asymmetry:

**I do not agree.** The asymmetry is right about **blocking** and wrong about
**selection**. Mid-flight genuinely is a property of the spine, so
`_entry_mid_flight_view` should read no payload and every open gate should block
— that part is a real insight and I would keep it. But both sites also choose
*which* entry to speak about, and the implementer's own comment in `decide_stop`
states the governing rule exactly:

> Order alone would hand a Commander whichever entry happened to be claimed
> first — routinely its in-tree crew's, whose gate is precisely the one it must
> not be told to drive.

That sentence is true verbatim of `decide_session_start`, and my case 6 shows
selection there is nothing but claim order. The right record is not "the two
sites are asymmetric" but: **blocking is a spine property at both sites;
selection is a binding-key property at both sites.**

## Reconciliation check

No `docs/` or contract change needed. `docs/CHECKLIST_SCHEMA.md`'s amended
`not-a-weaker-guard` wording is untouched and this gate removes no guard from a
leased spine — it moves an ownership question off the tree, which is what
`worktree-is-location-spine-path-is-identity` asks for. That decision is now
honoured in the hook's blocking and rendering decisions; B2 is where it is not
yet honoured in its selection decision.

## Blockers

### B1 — the shipped differential compares the change against itself

`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/m4_differential.py:23`

```python
BASE_REV = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], ...)
```

The BEFORE arm loads the hook at **whatever HEAD is when it runs**, not the
pinned pre-change base its own docstring names ("BEFORE the change (git HEAD
999b7663)"). It was honest only at authoring time, when HEAD happened to be
`999b7663`. The change is committed now, so re-running it loads the
**post-change** hook on both arms.

I ran it as the handoff instructs. The header prints `BEFORE (ca577709)` and
every row comes back identical — including all three rows the criterion asks a
reviewer to spot-check. `S3`, `S4` and `S8` read `BEFORE BLOCK / AFTER BLOCK`,
which is the exact opposite of the truth, and it reads as confirmation.

This is `CREW_CONTEXT.md` §Verification Discipline — *a check that cannot fail is
indistinguishable from one that passed* — and `global-everyone.md` §*Pin a claim
to the revision you read it at*.

**Fix:** one line, `BASE_REV = "999b7663"`, or derive the parent of the commit
that last touched the hook.

**The underlying claims are true.** I pinned a copy and re-ran the implementer's
own harness:

| row | BEFORE (999b7663) | AFTER |
|---|---|---|
| S1 parent, in-tree crew | foreign-owner, NOTHING | own-gate, `PARENT-MARKER` |
| S2 crew stops | foreign-owner, NOTHING | own-gate, `CREW-MARKER` |
| S3 own claim, other tree | **ALLOWED** | BLOCK, own-gate |
| S4 crew in own tree | **ALLOWED** | BLOCK, foreign-owner, NOTHING |
| S5 SessionStart | no context | INJECT `RESUME-MARKER` |
| S6 ×6 garbage | BLOCK | BLOCK |
| S7 malformed `agent_id` | own-gate, `FAILSAFE-MARKER` | foreign-owner, NOTHING |
| S8 case/separator | **ALLOWED** | BLOCK, own-gate |

My independent differential agrees on every row.

**Hand spot-check of S3/S4/S8 against the code**, as the criterion requires —
verified by reading, not only by running:

- **S3** — old `_entry_mid_flight_view` called `_foreign_worktree(data, entry)`;
  `cwd` and `worktree` both truthy and `_same_path` False → True → entry skipped
  → `mid_flight` empty → `return {}`. New signature takes no payload, so there is
  no skip; `owners.get(path)` is the bare `s1` and `binding_key(payload)` is
  `s1`, so `_is_own_entry` is True → own-gate rendering.
- **S4** — the crew's entry is filed under `CREW_KEY` with the crew's own tree.
  Old: `_foreign_worktree` True → skipped → allow. New: blocks; `owners.get` is
  `CREW_KEY` vs `own_key` `SID` → `_is_own_entry` False → the `own` list is empty
  → falls back to `mid_flight[0]` → foreign-owner branch, imperative withheld
  from both fields.
- **S8** — old `_same_path` folds through `normcase`, which is the identity on
  POSIX, so `C:\Foo\wt` vs `c:/foo/wt` differ here and match on Windows:
  platform-dependent allow/block. New never reads `worktree` → blocks on both.

### B2 — `decide_session_start` selects by claim order, not by ownership

**This is the substantive blocker.** Criterion 4 said to test it, not read it, so
I did: `/tmp/g3rev/c4_session_start.py`, six constructed cases, OLD vs NEW.

The claim is that "every entry in the merged view was claimed by *this* session,
under its bare key or under a per-agent key **of its own**". But `session_view`
merges the bare `sid` **plus every `sid#<agent_id>` key** (`_session_keys`,
`spine_rail.py:515`), and Agent-tool subagents *share the parent's session_id* —
that sharing is the entire premise of #419 and of the per-agent key. So a
**different agent's** per-agent key is in the merged view by construction. "A
per-agent key of its own" conflates *of this harness session* with *of this
agent*.

| case | OLD (999b7663) | NEW |
|---|---|---|
| 1. in-tree crew claimed first, parent's session starts | `CREW-MARKER` | `CREW-MARKER` |
| 2. crew in **another** worktree claimed first | `PARENT-MARKER` | **`CREW-MARKER`** |
| 3. only a crew's key exists; parent never claimed | no context | **`CREW-MARKER`** |
| 4. two different crew agents | `CREW-MARKER` | `CREW-MARKER` |
| 5. as 4, payload carries `agent_id=agentB` | `CREW-MARKER` | `CREW-MARKER` |
| 6. as case 2 but parent's key written **first** | `PARENT-MARKER` | `PARENT-MARKER` |

- **Case 2 is a regression introduced by this gate.** The old tree test was
  getting it right; the new code hands the parent the crew's gate — with
  "Pick the run back up at this gate and drive it through the engine." That is
  the #549/#419 bug class itself, at the other call site, in the gate whose whole
  purpose is to end it.
- **Case 3** is new mis-resume: a session with no binding of its own now resumes
  from a crew's spine instead of falling through.
- **Case 1** shows the defect class pre-exists for in-tree crews. This change
  *widens* it to out-of-tree crews.
- **Case 6** proves the mechanism: identical binding, parent's key written first,
  and the answer flips. Selection is nothing but dict order.
- **Case 5** shows the site ignores the payload's own identity even when present.

**Fix — it is the one already written at the other site.** Prefer the entry whose
`session_view_provenance` key equals `binding_key(payload)`, falling back only
when the session owns none. With no `agent_id` in the payload, `binding_key` is
the bare `sid`, which selects the session's own entry and repairs cases 1, 2 and
3 together. This is the same extraction the Fowler pass flags under
`long-method`.

### B3 — a false claim survived in the replacement prose

`scripts/hooks/spine_rail.py:685-687`, in the **new** section header:

> Ownership is decided by binding-key provenance at both former call sites --
> see decide_stop and decide_session_start.

It is not. At `decide_session_start` nothing compares a provenance key to
anything; the site takes the first entry in dict order
(`spine_rail.py:1685-1689`), and B2 measures it selecting entries the acting
agent does not own. The site's own inline comment is more careful ("Membership in
the view IS the binding-key answer at this site"), but the section header states
the stronger claim, and a reader arriving at this module meets the header first.

This is exactly the defect class the handoff warned about — the symbol went and
the false claim survived in the prose that replaced it. Softer and related:
`OwnershipIsBindingKeyNotWorktree`'s docstring says giving parent and crew
different trees "proves nothing about this change". For the SessionStart site
that is wrong; the differing-tree case is precisely where the deleted test was
doing real work and where the new code regresses.

If B2 is fixed, B3's sentence becomes true and needs no separate edit.

## Out-of-scope observations

Recorded as triage candidates on the survey.

1. **`tc1` — the SessionStart scan-bind still binds a session to a spine it never
   claimed.** When a session has no binding, `decide_session_start` falls through
   to `_scan_active_spine` and, on exactly one active-leased spine, **writes a
   binding** for that session and injects "drive this gate". A `run_crew.py`
   crew has its own `session_id` and no binding, so the single active spine it
   finds is its parent Commander's, under the parent's live lease. Binding-key
   provenance cannot fix it — there is no binding key yet at scan time; the
   discriminator would have to be the engine lease's owner. Reported by the g3
   implementer as its observation 1; **I reproduce the diagnosis and second it**,
   having hit it myself. Needs an authority decision.
2. **`tc2` — a Stop payload carrying `agent_id: null` would be told its own gate
   is foreign.** `binding_key` reads a present-but-null `agent_id` as *unusable*
   rather than *absent*, so nothing matches and the agent gets foreign-owner
   wording with its own imperative withheld — where the pre-change hook rendered
   it. Measured. It never relaxes the rail, so it is not a constraint violation,
   and the pinned capture shows the harness omits the key entirely for a
   top-level agent, so the shape is hypothetical today. Worth recording in case a
   harness version ever starts sending an explicit null.
3. **`tc3` — `bind()`'s `None` substitution makes a labelled test row prove
   something else.** Detailed under Evidence verdict.
4. `map/ids.jsonl` is 0 bytes and per-module `map/<module>/INDEX.md` files are
   absent repo-wide — already recorded as the lane's tc1, confirmed still true,
   not chased.

## Workflow Feedback

- **Handoff gaps:** (a) **Close Criterion 3 named the wrong authority for the
  before/after claim.** It says "Run it. Then satisfy yourself it is honest,"
  which frames the harness as the primary instrument and the audit as a
  follow-up. The harness was structurally incapable of answering by the time I
  ran it, and the *only* reason I caught it is that I had already built my own
  differential and had a contradicting number in hand. A reviewer who ran the
  handoff's commands in the order given would have seen 26 identical rows and
  read them as confirmation. The criterion should say: reproduce the before/after
  yourself first, *then* run the implementer's harness and reconcile the two.
  (b) **Criterion 4 was the best-written check in this handoff and it is worth
  saying why** — it named the falsifier ("if a per-agent key from a different
  agent can reach that merged view"), which turned an unfalsifiable prose claim
  into a six-line test. Criterion 3 would have caught B1 on its own if it had
  been written the same way. (c) The Evidence Produced table gives the Commander's
  re-measured numbers but not the *revision* each was measured at; since HEAD
  moved twice during this gate (`999b7663` → `e3e50a69` → `97675d95` →
  `ca577709`), "the Commander re-ran" is not by itself locatable.
- **Context rediscovered:** that `session_view` merges *other agents'* per-agent
  keys, not just this agent's. Both the handoff and the implementer's result use
  "this session" to mean both "this harness session" and "this agent", and B2
  lives entirely in that gap. The Map Anchors list `session_view` /
  `session_view_provenance` as structural anchors but do not say what the merge
  admits, which is the one fact criterion 4 turns on. One sentence — "the merged
  view contains every agent under this harness session, not just the acting one"
  — would have made B2 visible from the anchors alone.
- **Instructions improvised around:** the reviewer skill opens with "a spine is
  bound for you; `spine_status` is your first call." My `SPINE_*` env points at
  the **parent Commander's** spine under the parent's live lease while my
  `crew-runs.json` entry has `spine: null`, so obeying literally means driving
  someone else's gate. I authored my own survey at the path the handoff named,
  claimed it with my own session id, and drove it through the `checklist_engine.py`
  CLI. Two smaller ones: the skill says `advance` after `record`, but the engine
  refuses `advance` on a `survey` ("advance is for gated checklists; use record")
  — harmless once seen, but it reads as a failure the first time; and the survey
  template hardcodes the Fowler record at `.agent-work/<work-id>/FOWLER_PASS.json`,
  which on a multi-gate issue means every reviewer either clobbers a prior gate's
  committed evidence or amends the postcondition. Four prior `FOWLER_PASS-*.json`
  files in this work-id show everyone has hit it. I instantiated mine with a
  suffixed path rather than amending afterwards.
- **What would have made this easier:** the handoff's own warning — "a harness
  the implementer wrote to grade its own change is a convenience, not an
  authority" — was exactly right and should be promoted from prose into the
  criterion's *procedure*: **build your own instrument before you run theirs.**
  That single ordering is what separated a real review from a rubber stamp on
  this gate, and it cost me maybe twenty minutes.

## On the Stop hook

I refused it, and I am recording the refusal here as instructed.

`SPINE_FILE` points at
`.agent-work/cleanup-f-derive-worktree/spine.json` under my parent's live lease;
`SPINE_SESSION` is `constellation/cleanup-f-derive-worktree/execute/commander`,
not mine; `SPINE_PARENT` is
`constellation/cleanup-f-derive-worktree/execute/commander/attempt-4`. Obeying a
`SPINE MID-FLIGHT` nudge would mean advancing someone else's gate under someone
else's lease, and the hook's own escape hatches (`block`, `waive`) write to that
same parent spine, so the sanctioned honest stop is itself the destructive act.
A plain recorded refusal is correct. **I wrote nothing to the parent spine.**

I authored my own survey at
`.agent-work/cleanup-f-derive-worktree/g3-review/review.json`, claimed it with my
own session id, drove all 19 checks, and consolidated there.

Worth noting for the record: the mechanism behind this — `tc1` — is the one
defect in this area that **this gate does not fix and cannot fix**, and my B2
finding is adjacent to it rather than the same thing. B2 is about which entry a
session with bindings resumes from; `tc1` is about a session with *no* binding
acquiring one it never claimed. Fixing B2 does not close `tc1`.

## Return status

`complete`
