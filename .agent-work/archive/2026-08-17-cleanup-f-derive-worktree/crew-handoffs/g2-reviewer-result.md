# REVIEW_RESULT

## Gate

`g2` — lane F, issue #609, "retire stamp-and-compare". Diff base `9ff86f2d`.
Worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`.
Survey driven at `.agent-work/cleanup-f-derive-worktree/g2-review/review.json`
(7 items, all visited, consolidated).

Verdict: BLOCK

## Summary

**The code change is right. One claim shipped alongside it is not.**

Everything the gate asked for landed, and I reproduced every figure the
implementer reported — all of them match. The block is not "the subtraction was
wrong." It is that the gate's own load-bearing claim, the one the close criteria
put me here to test, is **measurably false in a case nobody drove**, and that
false claim is now shipped as fact in three artifacts including a user-facing
doc.

I did not take the implementer's negative on trust. I ran my own search, and it
returned a positive.

---

## Findings

### B1 — BLOCKING. The removed comparison *was* the only guard on a leaseless spine

**Severity: blocking.**

**Claim.** `docs/CHECKLIST_SCHEMA.md:124` now states: *"**Removing it removed no
guard.** The comparison answered *where am I*, never *is this mine* — ownership
is the **lease** (`engine_session`, below), and always was."* The same claim is
in `scripts/checklist_engine.py:95-97` ("Nothing was left unguarded by that
removal") and in the test module docstring at `tests/test_spine_origin_isolation.py:25-27`.

**Why it is false.** `require_session` (`scripts/checklist_engine.py:1026-1030`):

```python
if verb not in MUTATING_VERBS:
    return
lease = _active_lease(cl)
if lease is None:
    return  # no lease claimed: legacy behavior, no session needed
```

With **no active lease there is no ownership guard at all.** The origin
comparison was therefore the *sole* refusal on that path, and it is gone. "The
lease was always the guard" holds only where a lease exists.

**The evidence I ran.** Same fixture, base engine extracted at `9ff86f2d`
(`git show 9ff86f2d:scripts/checklist_engine.py`) versus the working tree, spine
stamped with its own worktree, every verb driven from a *foreign git worktree*:

| scenario (driven from a foreign tree) | BEFORE `9ff86f2d` | AFTER (this diff) |
|---|---|---|
| never-claimed spine, `start` | **exit 1, REFUSED** | **exit 0**, gate `pending`→`in-progress` |
| never-claimed spine, `attach` | **exit 1, REFUSED** | **exit 0** |
| lease **released**, then `start` | **exit 1, REFUSED** | **exit 0**, gate written |
| unclaimed spine, `claim` | exit 1, REFUSED | exit 0 |
| **active lease held by s1**, `claim` + `start` by s2 | exit 1, REFUSED | exit 1, REFUSED |

The last row is the implementer's table, and it is correct — *for that row*. The
refusal messages BEFORE are the origin predicate's own: `REFUSED: start refused:
this spine belongs to the worktree /tmp/…/wt, but the engine is running in …`.

**What this means for the reported behaviour delta.** The result artifact says:
*"The one genuine behaviour delta: an unclaimed spine can now be claimed from a
foreign tree (exit 1 → exit 0)."* That understates it in two dimensions. The
delta is **every mutating verb, not just `claim`**, on **any spine with no active
lease — never-claimed *or released*** — and unlike `claim` these verbs **write
state into a tree the agent is not standing in**. A Commander integrating on the
sentence as written would be misinformed about what changed.

**Why the implementer's negative missed it.** `probe_adversarial.py` drives
agent-two only while agent-one **holds the lease** (lines 92-103), plus a single
leaseless `claim` (lines 111-113). It never drives a mutating verb on a leaseless
spine, and never exercises the released-lease state at all. The conclusion — *"I
did not find a case where the removed comparison was the only thing preventing
harm"* — is broader than the probe that supports it. Under
`references/global-everyone.md` §Scoped nulls, a null must state what was **not**
tested; this one is stated unscoped.

**What I am not doing.** `not-a-weaker-guard` is `@grade: settled/human`, and
doctrine is explicit that such an anchor is not mine to unsettle — and the
anchor's own text says *"A genuine counter-case is a finding, not something to
ship around."* So this is **floated as contradicting evidence**, not decided
here. The subtraction may be exactly what the Admiral ruled.

**What I would change.** Two exits, both cheap, and this may be a **prose-only
repair**:

1. Narrow the claim in all three places to what is true — the lease is the guard
   *wherever a lease exists*; on a leaseless spine the engine now asserts nothing
   about location, deliberately. `docs/CHECKLIST_SCHEMA.md` already has the right
   sentence one paragraph down ("Nothing checks at engine level that an agent is
   standing in the spine's worktree"); the contradiction is between that
   paragraph and the one above it.
2. Restate the behaviour delta in the result artifact as measured above, so the
   Commander integrates the real blast radius.

If the Admiral judges the leaseless widening itself unacceptable, that is a
different and larger conversation — but it belongs to the ruling tier.

---

### B2 — Supporting. The Windows case/separator rows are inert at the cwds the test uses

**Severity: medium.** Not independently blocking; it is the reason B1's kind of
gap can recur.

Evidence section 8 claims the folding expectation was *constructed*, not
inherited: *"the differential table carries a backslashed, drive-lettered
`C:\W\REPO` row and an upper-cased copy of the real worktree path … which is a
real assertion on Linux."*

**Measured, under a stamp-reading mutant** (`normcase(stored) != normcase(cwd)`
→ refuse), driving `start`:

```
--- FOREIGN cwd (the only kind the shipped test drives from)
    the spine's own worktree         exit=1 refused=True
    the same path, wrong case        exit=1 refused=True
    a Windows-shaped path            exit=1 refused=True
    a foreign tree                   exit=1 refused=True

--- the spine's OWN worktree (never driven by the test)
    the spine's own worktree         exit=0 refused=False
    the same path, wrong case        exit=1 refused=True     <-- separates here
    a Windows-shaped path            exit=1 refused=True
    a foreign tree                   exit=1 refused=True
```

From a foreign cwd **no stamp can match**, so a comparison refuses every string
row identically and the case row discriminates nothing the plain
`"a foreign tree"` row does not. The rows separate only from the spine's own
worktree, and `_assert_one_answer_for_every_stamp` is called with `self.foreign`
and `self.nogit` only.

To be fair to the change: **the class as a whole is not vacuous.** It is saved by
`self.assertEqual([0, 0, 0], first["codes"], "every stamp was refused, not
accepted")` — which is exactly why my re-introduction mutant went red (8 failed).
The defect is confined to the two rows' claimed discriminating power.

**What I would change.** One line: also call
`self._assert_one_answer_for_every_stamp(self.worktree)`. Measured above, the
wrong-case row then genuinely separates on Linux (exit 0 vs exit 1) — which makes
the "constructed, not inherited" claim true instead of asserted.

---

## Close criteria — verified one by one

| criterion | verdict | what I ran |
|---|---|---|
| No `rev-parse --show-toplevel` in `checklist_engine.py` | **PASS** | `git grep -n` returns nothing, rc=1. Surviving `--show-toplevel` under `scripts/` are `episode_capture.py:96`, `map_orient.py:1040`, `mcp_spine_server.py:611`, `verify_worktree_isolation.py:123` — all other modules. |
| No decision path reads `origin.worktree` | **PASS** | `grep -rn --include=*.py -E "[\"']origin[\"']" scripts/` → **COUNT: 2**, both writes (`spine_lifecycle.py:323`, `init_work_area.py:188`). Non-Python readers: 0 (the three `"origin"` hits in `docs/installed_externals_manifest.json` are an unrelated field). `ORIGIN_GUARDED_VERBS`/`ORIGIN_EXEMPT_VERBS`: zero references outside archive, doc prose and the pinning test. |
| `origin.worktree` is still written | **PASS** | Both producers, pinned; confirmed by mutation (below). |
| The `provenance` test pins **both halves** | **PASS** | Ran the deletion test in both directions myself — see below. |
| The subtraction removed no guard that was doing work | **FAIL** | Finding **B1**. |
| The refusal path's position: nothing now writes state where it previously refused first | **PASS** | `main()` now runs `load` → `refusals` arming → `dispatch` with nothing between. The arming is pre-existing (#427) and non-refusing. |
| Full suite green, cache cleared, clean env | **PASS** | 3135 passed, 5 skipped, 0 failed, 125.30s. |
| **No fail-closed refusal smuggled in** | **PASS** | Proved mechanically, not sampled — below. |

### The provenance pin, both directions, run by me

```
MUTANT 1  delete the init_work_area worktree line        -> FAILED test_provenance_the_stamp_is_written_by_both_producers   (1 failed, 3 passed)
MUTANT 1b delete build_origin's "worktree" entry         -> FAILED the same test                                            (1 failed, 3 passed)
MUTANT 2  re-add a cwd comparison reading the stamp      -> 8 failed, 2 passed
RESTORED  (engine byte-identical to pre-mutation)        -> 13 passed, 18 subtests passed
```

Each mutation **asserted that it applied** before running — a `replace` that
silently matched nothing leaves a green suite that reads like a passing guard.
Mutant 1b's first attempt failed that assertion (two occurrences) and was redone
scoped to `build_origin`'s body.

### No fail-closed refusal was smuggled in — mechanical, not sampled

Every added line under `scripts/` in this diff is docstring or comment prose:

```bash
git diff 9ff86f2d -- scripts/ | grep '^+' | grep -v '^+++' | sed 's/^+//' \
  | grep -vE '^\s*#' | grep -vE '^\s*$'
```

leaves **only docstring text** — the `worktree_from_spine_path` rationale repair
and the `build_origin` provenance note. There are **zero executable additions in
production code**, so no new early-return, refusal, or verb-set change is
possible. g4's shape refusal is absent. `scripts/hooks/spine_rail.py` is
untouched. The tripwire `tests/test_worktree_precondition_wiring.py` is green
standalone and in the full suite.

### The −24 reconciles mechanically, and no test silently stopped running

| measure | base `9ff86f2d` | now | delta |
|---|---|---|---|
| full suite passed | 3159 | **3135** | −24 |
| skipped | 6 | **5** | −1 |
| collected | 3165 | **3140** | −25 |
| `tests/test_spine_origin_isolation.py` collected | **38** | **13** | **−25** |

I measured the base collected count for that file directly (`git show
9ff86f2d:tests/… > tests/zz_base_origin_probe.py`, collect, remove). The −25 is
**entirely** inside the one changed test file — and since it is the **only test
file that differs from base**, the whole-suite delta is necessarily confined
there. The base file carried exactly one skip
(`@unittest.skipUnless(os.name == "nt")` at `:306`); the new file carries none,
which is the 6→5. Base numbers verified at source in
`g2-implement/m5-full-suite-BASE.txt`.

### The handoff's own count, corrected

The handoff counts "6 surviving mentions of `origin_worktree_refusal` under
`scripts/`, all prose, **two of them in fenced files**." The 6 is right and all
6 are prose. The fenced share is **3 mentions across 2 files**
(`mcp_spine_server.py:18`, `:371`; `run_crew.py:860`), not two — `:384` carries
`--show-toplevel` prose, not the symbol. Correction only; nothing turns on it.

### Reproduced figures

Targeted check green (`4 passed, 9 deselected, 18 subtests`). Four-file run
`85 passed`. Wiring grep `35 → 21`. `map/INDEX.md` regenerates **byte-identically**
under `py -m scripts.code_map build --root .` and touches nothing else under
`map/` — genuinely regenerated, not hand-edited. All implementer evidence
artifacts exist and are fresh (timestamped this run).

## Scope

No breach. Exactly the five allowed paths differ. A targeted diff over every
excluded path — `mcp_spine_server.py`, `.mcp.json`, `examples/`,
`install_constellation.py`, `skills/commander/templates/`, `run_crew.py`,
`recover_crews.py`, `test_crew_launcher.py`, `verify_worktree_isolation.py`,
`hooks/spine_rail.py`, `.agent-work/templates`, `skills/admiral/templates` —
returns empty. No untracked files outside `.agent-work/`.

**On deleting the two verb sets** (the one decision the implementer offered to
reverse): I judge it **compliant**. The handoff sentence "its guarded/exempt verb
sets keep their current meaning" sits inside the paragraph forbidding *new*
refusals, the gate's own constraint sanctions deleting a degenerate predicate
rather than leaving a function that returns `None` on every path, and the sets'
only production reader was inside that predicate. No reversal needed.

**Supersession cited correctly** in all three required places
(`docs/CHECKLIST_SCHEMA.md:122`, `checklist_engine.py:96`,
`tests/test_spine_origin_isolation.py:22`), and the ruling file itself is
correctly left unedited.

## Fowler refactoring pass

Record at `.agent-work/cleanup-f-derive-worktree/FOWLER_PASS.json`;
`verify_fowler_pass.py` exits 0 (12 smells, flagged `duplicated-code`,
`shotgun-surgery`, `comments-as-deodorant`; overridden `primitive-obsession`,
`divergent-change`, each with the winning standard logged). The g1 reviewer's
record was preserved as `FOWLER_PASS-g1-reviewer-attempt-2.json` rather than
overwritten. No rail exception used.

Two flags converge on B1 and are worth the Commander's eye: the falsified claim
is **hand-copied into three files with nothing checking the copies**
(`duplicated-code`), and it is asserted **in a comment** where CREW_CONTEXT
requires an assertion against behaviour (`comments-as-deodorant`). Repairing B1
in one place and not the other two is the concrete risk.

## Out-of-scope observations (triage candidates, not blockers)

- **tc1 — Lane A (#603).** `mcp_spine_server._standing_in_the_bound_spines_worktree`
  exists *solely* to satisfy the guard this gate deleted; its own docstring says
  so. That justification is now void. The `chdir` may still be wanted (g5 wants
  the engine standing in the right tree for command checks) but it currently has
  no stated reason to exist and its tests pass either way. I confirm the
  implementer's read of this.
- **tc2 — Lane E.** `run_crew.py:860` carries present-tense prose describing the
  retired comparison. Correctly left stale (fenced).
- **tc3 — in scope but deliberately untouched.**
  `tests/test_worktree_precondition_wiring.py:15-17` and
  `tests/test_mcp_door_engine_cwd.py:5` both still say enforcement is
  engine-native via `origin_worktree_refusal`. Now false. Leaving the tripwire
  alone before g5 was the right call; repair when g3/g5 opens those files.
- **tc4 — doctrine.** Line-number anchors are not carrying their weight on this
  lane: three stale citations (`spine_rail :639` vs `:693`;
  `CHECKLIST_SCHEMA.md`'s `:3411-3444`; this gate's handoff `:3573-3578` vs the
  real `:3638-3643`). Symbol names would have been correct in all three. I second
  the implementer's suggestion.

## Workflow Feedback

- **The crew/spine misfit, again — fifth crew on this issue.** `SPINE_FILE` /
  `SPINE_SESSION` point at the **Commander's** spine under the Commander's active
  lease, while my `crew-runs.json` entry has `spine: null`. The reviewer skill's
  opening ("a spine is bound for you; `spine_status` is your first call") reads as
  if that spine were mine; obeying it literally means advancing my parent's
  `execute` gate. I called `spine_status` (read-only), confirmed the mismatch,
  authored my own survey at
  `.agent-work/cleanup-f-derive-worktree/g2-review/review.json`, claimed it under
  my own session id, and **wrote nothing to the parent spine**. The durable fix
  is a lease-ownership check in the hook, not more prose.
- **The handoff's best instruction was "do not take its negative on trust."**
  That single sentence is what produced B1. Keep it in every reviewer handoff
  where the implementer reports a measured negative — and consider asking the
  *implementer* handoff to state the negative's **scope** (what was and was not
  driven), which would have surfaced the leaseless gap before it reached me.
- **The `not-a-weaker-guard` anchor is stated more strongly than it is true.**
  "The lease was always the guard" is false for the leaseless shape the engine
  supports deliberately (`require_session`'s early return, and the child-gate-plan
  shape #357 names). If the anchor had read "the lease is the guard wherever a
  lease exists," this gate would have had a correct premise to build on and B1
  would be a scope note rather than a block.
- **Handoff gap.** The close criteria ask me to confirm the refusal path's
  position is not re-occupied, but give no way to enumerate "every early-return on
  the verb path" mechanically. The strongest available proof turned out to be
  "zero executable additions in the whole `scripts/` diff" — a diff-shape argument,
  not a verb-path one. Worth naming in future handoffs, because it is both cheaper
  and stronger than walking the verb path.
- **Minor, recorded for honesty.** A backtick in one `--finding` string was shell-
  interpreted, dropping the word "claim" from the `r3-evidence` finding as stored
  in the survey JSON. The text in this artifact is the complete version. I did not
  churn engine state to repair a cosmetic loss.

## Engine provenance

Survey `.agent-work/cleanup-f-derive-worktree/g2-review/review.json`, claimed by
`constellation/cleanup-f-derive-worktree/g2/reviewer/attempt-1`, all 7 items
visited and recorded (`r0-context` pass, `r1-handoff` pass, `r2-scope` pass,
`r3-evidence` fail, `r4-quality` fail, `r5-reconciliation` fail, `r6-fowler`
pass), consolidated `verdict=BLOCK findings=3`, 4 triage candidates flagged. The
lease is released after this write.

Working tree confirmed restored after all mutation testing: `git diff 9ff86f2d
--stat` is back to 5 files / 273 insertions / 623 deletions, and
`checklist_engine.py`, `init_work_area.py` and `spine_lifecycle.py` are
byte-identical to their pre-mutation copies.

## Stop-hook refusal, recorded

After this result was written and my own lease released, the Stop hook fired
`SPINE MID-FLIGHT: gate execute is still open`, instructing me to reload the
`constellation-commander` skill, rewrite `STATE_NOTE.md`, and drive
`execute.json` gate by gate. **I refused, and wrote nothing to the parent
spine.** State verified at the moment of refusal, by command:

- **My own survey** (`g2-review/review.json`): `LEASE released:
  constellation/cleanup-f-derive-worktree/g2/reviewer/attempt-1`, `DONE: no open
  items.` Nothing of mine is abandoned; the deliverable is on disk.
- **My `crew-runs.json` entry**: `{"role": "reviewer", "gate": "g2", "spine":
  null}` — **no spine is bound to this crew.**
- **The spine the hook points at** (`SPINE_FILE`,
  `.agent-work/cleanup-f-derive-worktree/spine.json`): `LEASE active:
  commander-cleanup-f-derive-worktree (by commander)`. That is my parent's
  `execute` gate under my parent's live lease.

Obeying would mean advancing my parent's gate or force-taking a live lease. The
hook's own escape hatches do not fit: it offers `block` or `waive`, but **both
write to the parent's spine**, so the sanctioned "honest stop" is itself the
destructive act. The only non-destructive exit is to refuse and record it here.

This is the **fifth** crew on this issue to hit it, and the first to hit it as a
**reviewer** — so it is not implementer-specific. Note also that it fired
**after** my work was fully closed and my lease released: the hook is keyed on
the spine's mid-flight state, not on whether the running agent has anything open.
The durable fix is a lease-ownership check in the hook — compare the spine's
`engine_session.session_id` against the running crew's session id and stay silent
when they differ — not more prose telling crews what to do about a spine that was
never theirs.

**One thing in that spine's `current` genuinely needs the Commander's eye**, and
I surface it rather than act on it: the `execute` gate is now reporting
`CONTEXT 33% (>= hard)` with `REFRESH REQUESTED: execute (why_ref w-4)`, a
`TRIP LEDGER` of 1 begin at/over the hard line under the current understanding,
and a `TRIP HISTORY` of 2 across the checklist. The rail's instruction there —
close the gate carrying a handoff (`advance execute --why …`) so a fresh agent
picks up from the DIGEST — is addressed to the lease holder, which is the
Commander, not to me.
