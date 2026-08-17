# Reviewer Handoff — g3 rework 1

## Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. The last code gate of the lane.

**You are the second reviewer on this gate.** The first returned **BLOCK** with
three blockers; a rework answered all three. Your job is to decide whether the
rework is right — **and to check that fixing them broke nothing that was
passing.**

## Survey State Location

`.agent-work/cleanup-f-derive-worktree/g3-review-rework/review.json`.

Note for the survey template's Fowler record: it hardcodes
`.agent-work/<work-id>/FOWLER_PASS.json`, and five prior files in this work-id
show every reviewer collides there. Instantiate yours with a suffixed path
(e.g. `FOWLER_PASS-g3-reviewer-attempt-2.json`) rather than clobbering committed
evidence or amending the postcondition afterwards.

## Read these first

1. `crew-handoffs/g3-reviewer-result.md` — the BLOCK. B1, B2, B3.
2. `crew-handoffs/g3-implementer-rework-result.md` — the rework's answer.
3. `crew-handoffs/g3-implementer-result.md` — the original pass, still the bulk
   of the change.
4. `crew-handoffs/g3-reviewer-handoff.md` — the first review's 12 Close Criteria.
   **They still govern.** Criteria 1, 2, 5–9, 11 and 12 were PASSes and this
   rework must not have broken them.

## How to Inspect the Diff

Three commits, and you need them apart:

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

# the rework alone -- what you are chiefly judging
git diff e3e50a69..6bba3fd2 -- scripts/hooks/spine_rail.py tests/test_spine_rail.py

# the whole gate, base to head
git diff 999b7663..6bba3fd2 -- scripts/hooks/spine_rail.py tests/test_spine_rail.py

git show --stat 6bba3fd2
```

`999b7663` is the pre-gate base, `e3e50a69` the first (blocked) pass, `6bba3fd2`
the rework. `map/INDEX.md` also moved; it was regenerated with
`py -m scripts.code_map build`, never hand-edited (#544), and is not interesting.

## What the rework did

**B2** — `decide_session_start` now prefers the entry whose
`session_view_provenance` key equals `binding_key(payload)`, via a new shared
helper `_own_entries(candidates, owners, own_key)` that **both** call sites use.
The implementer deliberately did **not** share the *fallback*: `decide_stop` keeps
`(own or mid_flight)[0]` because a stop blocks either way and must name
something; `decide_session_start` owning none of the visible entries hands out no
gate from the binding at all. `_entry_mid_flight_view` is untouched.

**B1** — `m4_differential.py` now pins `BASE_REV = "999b7663"`, adds a third
`BLOCKED_REV = "e3e50a69"` arm, and guards with
`_assert_arms_are_what_they_claim`, which identifies each arm by the symbols the
changes moved rather than by a commit id. The implementer says it demonstrated
the guard failing in both directions.

**B3** — the section header rewritten, plus five more false sentences found by
reading whole rather than by symbol. **Three of those five were written by the
rework implementer itself, in the same run, an hour earlier.**

## Close Criteria

The first review's 12 still apply. These are the rework's own, and they carry
the verdict.

1. **B2 is actually fixed, measured not read.** The first reviewer's harness is
   at `/tmp/g3rev/c4_session_start.py` and its six cases are the specification.
   The Commander re-ran it against the rework and got cases 2, 3 and 6 all
   matching the correct OLD behaviour. **Re-run it yourself, and then go further
   than it does** — it was written to expose one defect, not to prove a fix. In
   particular: a session that owns *several* entries, a payload whose `agent_id`
   names an agent with no entry, and the interaction with the fallback scan.
2. **The unshared fallback is the rework's main judgement call. Adjudicate it.**
   The implementer argues the comparison is shared but the fallback is each
   site's own, because a Stop blocks either way and a SessionStart blocks
   nothing. That reads right to me, but I want it independently judged rather
   than accepted: is there a case where `decide_session_start` owning none of the
   visible entries *should* still answer with something? And does the split leave
   the two sites able to drift the way the original asymmetry did?
3. **The two rewritten pre-existing tests. This is where I want your hardest
   look.** `test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key`
   and `test_session_start_composite_key_entry_still_renders_full_imperative_unchanged`
   asserted the behaviour B2 ends; they are renamed and rewritten as
   `..._reads_through_to_a_composite_key_but_answers_only_its_owner` and
   `..._withholds_a_composite_key_imperative_from_the_bare_session`. The
   implementer claims they are **not weakened** — that each still asserts #419's
   read-through directly (the old form only implied it) and adds a round trip.
   I read the first and agree it looks stronger. **You decide.** Rewriting a test
   to match the change it was guarding is the single most dangerous move in this
   diff, and the implementer flagged it honestly rather than burying it, which is
   why it deserves a careful yes rather than a suspicious no.
   Also weigh the alternative it says it rejected: falling back to the leading
   entry when the session owns none, which leaves both tests untouched and leaves
   case 3 unfixed. It claims the two are mutually exclusive. Are they?
4. **B1's guard genuinely cannot pass on a degenerate comparison.** Run the
   differential. Then try to defeat the guard — repoint an arm and confirm it
   refuses, as the implementer says it did. A guard that only *claims* to fail is
   the same defect one level up, and this is the second instrument on this gate
   to be graded, so do not grade it by reading it.
5. **B3, and the prose generally.** The header claim is now true only because B2
   was fixed. Verify that, and then apply the lane's rule — **grep for the claim,
   not the symbol.** Read every comment and docstring in the changed regions
   whole and ask of each *sentence* whether it is true of the tree as it now
   stands. The rework found three of its own false sentences an hour after
   writing them; assume there is a fourth.
6. **Nothing that passed the first review regressed.** Specifically re-check:
   fail-safe posture at **both** sites now (uncertainty withholds, never
   relaxes); the nudge/3-strike hatch still keyed by session id **alone**; #549's
   two-way rendering intact; stdlib-only import block unchanged;
   `tests/test_worktree_derivation.py` unedited and green; the Stop path's rows
   unchanged from `e3e50a69` to `6bba3fd2`.
7. **Suite arithmetic reconciles against the diff.** Claimed +6 (3177 → 3183):
   6 new methods (8 → 14), 2 renamed-and-rewritten in place (net zero), **no
   deletions**. Check that against the diff rather than accepting it — a quietly
   deleted test is what this check exists to catch, and this rework rewrote two
   tests, which is exactly where one could hide.
8. **`_own_entries` is correct at both sites.** It assumes both candidate
   sequences carry the abs spine path at element `[0]`. Confirm that holds for
   both callers and that the coupling is documented rather than incidental.

## The open decision, now argued twice

The gate's `@grade: placeholder` decision — *what replaces the skip at each call
site*. The first implementer resolved it asymmetrically. The first reviewer
disagreed and proposed:

> Blocking is a spine property at both sites; selection is a binding-key property
> at both sites.

The rework implementer **agrees with the reviewer over its predecessor**, with a
refinement:

> The comparison is shared; the fallback is not. What a site does when the acting
> agent owns nothing follows from the blocking half of the rule — a Stop blocks
> either way so it must still name something, a SessionStart blocks nothing so it
> names nothing. That is a consequence of the rule, not an exception to it.

**Say whether you agree, and say it plainly.** This is the one decision the gate
hands up to the Admiral, it has now been argued by three crews, and I would
rather carry a contested reading with the disagreement named than a consensus
nobody tested. If you think the refinement is a hedge that will let the sites
drift, say so — that is a finding, not a quibble.

## Allowed Scope

`scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`, `map/**`, and
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement*/**`.

## Specific Exclusions

Unchanged from the first review, and all still fenced. Flag if touched; an
exclusion naming a path outside your worktree is **Commander-verified, not
reviewer-verified** — note it, do not BLOCK on un-inspectability.

- **Lane A** — `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
  `scripts/install_constellation.py`, `skills/commander/templates/**`.
- **Lane E** — `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- **#610** — `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**` and
  `skills/admiral/templates/**`.
- **`scripts/checklist_engine.py`** — g2 is closed; no engine-side behaviour.
- **No fail-closed refusal** (`ADMIRAL_RULING-1` R2) and **no `cwd` threading**
  (R3).

The stale `KeyError`-era door claims in these files are **known**, are the
Commander's `reconcile` step, and are **not findings**. Do not report them.

## Four findings already recorded — do not re-report

1. **`tc1` — the SessionStart scan-bind** binds a session to a spine it never
   claimed, which is how six crews on this lane were handed their parent's gate.
   Diagnosed independently by the first implementer and seconded by the first
   reviewer. **Binding-key provenance cannot reach it** and the rework does not
   close it. Needs an authority decision.
2. **A Stop payload carrying `agent_id: null`** would be told its own gate is
   foreign. Never relaxes the rail; hypothetical today.
3. **`bind()` substitutes `str(project_dir)` for a `None` worktree**, so the
   "null worktree" row of `test_garbage_location_data_never_relaxes_the_rail`
   proves something other than its label.
4. `map/ids.jsonl` is 0 bytes and per-module `map/<module>/INDEX.md` files are
   absent repo-wide — the lane's tc1. Not yours to chase.

## Evidence Produced

Claimed by the rework, and **re-measured by me at `6bba3fd2` before dispatching
you** (the first reviewer rightly noted my last table gave numbers without
revisions):

| measurement | rework claims | I re-ran, at | result |
|---|---|---|---|
| targeted `-k OwnershipIsBindingKeyNotWorktree` | 14 passed | `6bba3fd2` | **14 passed, 21 subtests** |
| full suite | 3183 / 5 / 0 | `6bba3fd2` | **3183 passed, 5 skipped, 0 failed** |
| full suite, first pass | 3177 / 5 / 0 | `e3e50a69` | **3177 / 5 / 0** |
| full suite, pre-gate | 3170 / 5 / 0 | `53c89ba1` | **3170 / 5 / 0** |
| `main`, isolated clone | — | `17c2cee5` | **3171 / 7 / 0** |
| reviewer harness cases 2, 3, 6 | fixed | `6bba3fd2` | **all match correct OLD behaviour** |

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

**Build your own instrument before you run theirs.** The first reviewer named
this as the single thing that separated a real review from a rubber stamp on this
gate, and it is why B1 was caught at all: it had a contradicting number already
in hand when the implementer's harness printed 26 confirming rows. Reproduce the
before/after yourself **first**, then run
`crew-handoffs/g3-implement/m4_differential.py` and reconcile the two. If they
disagree, the harness is the suspect.

**Four environment hazards, each of which has cost this lane real time:**

1. **`CREW_SCRATCH_DIR`.** You are launched through `run_crew.py`, which sets it.
   Lane E's `tests/test_crew_launcher.py::ScratchDirResumeTests` asserts the key
   is absent from a resumed child's env without scrubbing it from the parent
   first, so it fails for **any** agent running the suite from inside a
   crew-launched session. Scrub it. That file is lane E's and fenced. **Do not
   fix it; do not report it.**
2. **Clear `__pycache__` before every measurement** — a stale cache fails
   `tests/test_bytecode_cache_provenance.py` by name.
3. **If you clone the repo to compare, name the clone directory
   `constellation-skills`** — `tests/test_code_map.py::MapTreeFreshnessTests`
   derives the map title from the checkout directory name, so a clone anywhere
   else reports a false red. It cost me a full suite re-run.
4. **You cannot validate this hook from inside your own session** (#269):
   `CLAUDE_PROJECT_DIR` resolves once at session launch, so this worktree runs the
   **main checkout's** hook. Call `decide_stop` / `decide_session_start` directly
   with constructed payloads and a constructed binding store.

**Windows:** `normcase` is the identity function on this Linux host, so any
case-folding expectation must be **constructed**, never inherited. The one
`windows-latest` CI job is red at baseline and cannot tell you.

There is **no pytest config in this repo**, so a plain non-`unittest.TestCase`
class is collected as **zero tests**. If a selector looks green, confirm it
collected **14**.

## Suggested Model Tier

**Stronger.** A rework of the riskiest change in the lane, whose central
judgement call is a rewritten pair of pre-existing tests.

## Stop Conditions

Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or
unverifiable, or a policy decision is required before a verdict is possible.

## Return Format

Return `REVIEW_RESULT`: verdict (**APPROVE** or **BLOCK**), per-check findings
against the numbered Close Criteria above **and** confirmation that the first
review's passing criteria did not regress, blockers, out-of-scope observations,
your read on the open decision, and workflow feedback.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-reviewer-rework-result.md`
**before ending your turn** — that write is the delivery.

## On the Stop hook

When you finish, a `SPINE MID-FLIGHT` hook may fire telling you to reload the
commander skill and drive `execute.json`. **Refuse it and record that you
refused.** `SPINE_FILE` points at my spine under my live lease; your own
`crew-runs.json` entry has `spine: null`. Obeying would mean advancing my gate,
and the hook's own escape hatches (`block`, `waive`) write to that same spine, so
the sanctioned honest stop is itself the destructive act. A plain recorded
refusal is correct — all three crews on this gate did exactly that and none was
penalised. Author your own survey at the path named above, claim it with your own
session id, and drive that.

The mechanism is `tc1` above. It is recorded, it is going up to the Admiral, and
you are not the seventh crew who has to diagnose it.
