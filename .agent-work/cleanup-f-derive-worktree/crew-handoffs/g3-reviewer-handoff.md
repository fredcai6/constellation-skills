# Reviewer Handoff

## Gate

`g3` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`. This is the last code gate of the lane and
the run's riskiest behaviour change: it makes a Stop hook block **more**, in code
that fires on every agent's turn, where a mistake deadlocks runs rather than
failing loudly.

## Survey State Location

Create your review survey checklist at
`.agent-work/cleanup-f-derive-worktree/g3-review/review.json`.

## What Was Implemented

The worktree stops answering "is this mine." `_foreign_worktree` is **deleted**
along with both its call sites, and ownership is decided by **binding-key
provenance**. The two call sites got **different** replacements:

- **`_entry_mid_flight_view`** now decides no ownership at all. Mid-flight is
  treated as a property of the spine — an open gate under an active lease, not
  honestly blocked — so it reads no payload and every such entry visible to the
  session blocks. Ownership moved **up** into `decide_stop`, where it decides
  only what is **rendered**: `session_view_provenance` is compared against
  `binding_key(payload)` (the acting agent's own key) instead of against the bare
  `sid`. The stopping agent is answered with **its own** gate wherever it has
  one, otherwise with #549's foreign-owner wording and the imperative withheld
  from both `reason` and `additionalContext`. Its signature narrowed from
  `(data, entry)` to `(entry)`.
- **`decide_session_start`** simply stops testing the tree. SessionStart carries
  no `agent_id`, so — the implementer argues — every entry in the merged view was
  claimed by *this* session and membership in the view **is** the binding-key
  answer.

New helper `_is_own_entry(owner_key, own_key)` holds the one comparison. It never
raises, and reads a missing key in two deliberate directions: an unplaceable path
is **own**, while an unidentifiable *agent* matches nothing.

Also a prose repair: two passages naming the deleted
`checklist_engine.worktree_from_spine_path` as a live twin now say what is true.

## How to Inspect the Diff

The change is **committed**. Review the commit range, not the working tree and
not `git diff main...HEAD`:

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree
git diff 999b7663..e3e50a69 -- scripts/hooks/spine_rail.py tests/test_spine_rail.py
git show --stat e3e50a69
```

`999b7663` is the pre-change base; `e3e50a69` is the gate's commit. `map/INDEX.md`
also moved in that commit — it was regenerated with `py -m scripts.code_map build`,
never hand-edited (#544), and is not interesting to read.

The implementer's own evidence files are under
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/`, and its
`IMPLEMENTER_RESULT` is at `crew-handoffs/g3-implementer-result.md`. Read the
result, but **do not accept it as evidence** — the three items below are the ones
you re-run yourself.

## Task Statement

`scripts/hooks/spine_rail.py:_foreign_worktree` was an **ownership** test built on
the tree, and it is broken by construction. Spines are 1:1 with work **areas**,
not worktrees: a Commander gets a worktree, an implementer usually does not — it
works in its Commander's tree, in its own area. So one worktree holds several
spines, and *same worktree, therefore mine* is wrong the moment a crew shares its
Commander's tree. For an in-tree implementer it reported "not foreign", and the
parent's Stop was answered with its **crew's** gate — the **#549 bug class**,
which #549 already fixed with binding-key provenance.

The two call sites were declared **not symmetric** and the implementer was
required to state each site's before and after behaviour separately, and to
**enumerate what newly blocks**, since removing a skip makes the Stop hook block
**more**.

The derived worktree may still be used for **location**. It may not be used for
**identity**.

## Close Criteria

Each becomes a review check. The first three are the gate's own instruction and
carry the verdict.

1. **The #549 shape is genuinely exercised — a shared-tree parent and crew, not
   two trees.** This is the criterion most likely to be faked by accident. A test
   that gives the parent and the crew *different* worktrees proves nothing here:
   that is the case the old code already got right. Read
   `OwnershipIsBindingKeyNotWorktree` in `tests/test_spine_rail.py` and confirm
   the parent and crew genuinely share **one** worktree path, that the parent's
   payload carries **no** `agent_id` while the crew's does, and that the assertion
   is about the parent's **own** gate rendering — not merely that the stop blocks.
   Then check the claimed red: the implementer says `m1-red.txt` shows 8 failures
   against the unmodified hook. **Reproduce it** —
   `git stash` is not available to you on a committed change, so check out the old
   hook into a temp path and import it, or run
   `git show 999b7663:scripts/hooks/spine_rail.py` into a scratch module and drive
   the same payloads. If the new tests pass against the **old** hook, the gate did
   nothing and that is a BLOCK.
2. **The fail-safe posture survives.** `_same_path` returned `True` on any
   exception precisely so a comparison failure never relaxed the rail. Whatever
   replaced the worktree test must keep that direction: **uncertainty blocks, it
   does not allow.** The implementer claims six garbage rows (`worktree` null /
   int / empty; `cwd` int / dict / absent) block before and after, and that a
   malformed `agent_id` blocks with the imperative withheld. Construct garbage
   yourself and confirm no input makes the rail *more* permissive than before.
   `_is_own_entry` is claimed never to raise — try to make it raise.
3. **Each call site's before/after claim reproduces when you run it.** The
   implementer shipped a differential harness at
   `crew-handoffs/g3-implement/m4_differential.py` that runs the old and new hook
   against identical payloads in one process. Run it. Then satisfy yourself it is
   honest — a harness the implementer wrote to grade its own change is a
   convenience, not an authority. Spot-check at least the three newly-blocking
   rows (S3, S4, S8) against the code by hand.
4. **`decide_session_start`'s argument is the weakest link in the return; test
   it, do not read it.** The claim is that SessionStart carries no `agent_id`, so
   every entry in the merged view belongs to this session and membership in the
   view *is* the answer. If a per-agent key from a *different* agent can reach
   that merged view, the site now resumes from an entry it does not own. The
   implementer notes #419's read-through as the mechanism. Determine whether that
   is true or merely plausible.
5. **Nothing newly stops blocking.** Three classes are claimed to newly block and
   each is claimed intended; the surviving allowed-Stop shapes are claimed
   unchanged (no binding, unreadable spine, released lease, honest engine block,
   3-strike hatch). Verify the *negative* direction: find a shape that blocked
   before and no longer does, or confirm there is none.
6. **The nudge / 3-strike escape hatch stays keyed by session id ALONE**, never
   fragmented per-entry.
7. **#549's rendering survives.** `decide_stop` must still distinguish a
   bare-`sid` entry (ordinary imperative-bearing reason) from one reachable only
   through a per-agent key (foreign-owner wording, imperative withheld from
   **both** `reason` and `additionalContext`).
8. **stdlib only.** `scripts/hooks/spine_rail.py` has zero cross-module imports
   and may gain none — a hook that fails takes the turn with it. The import block
   is claimed byte-identical (11 imports). Check it.
9. **`_same_path` survives correctly or is deleted.** The implementer kept it,
   citing callers in `git_worktree_roots` and `resolve_spine_candidate`. Confirm
   it has real callers; dead code left behind is a finding.
10. **No reference to `checklist_engine.worktree_from_spine_path` survives in
    `scripts/hooks/spine_rail.py` or `tests/test_spine_rail.py`**, and what
    replaces each is **true**. See the claim-not-symbol warning below.
11. **`tests/test_worktree_derivation.py` is unedited and green.** It is the
    surviving specification of the derivation rule, for #610's wave to re-derive
    the engine-side copy against. `git diff 999b7663..e3e50a69 --stat` must not
    list it.
12. **Suite green**, cache cleared, clean env, count stated, failure distribution
    derived mechanically even when empty.

## Grep for the CLAIM, not the symbol

This lane's most expensive lesson, and it is why g2 cost three implementer passes
and three reviewers. Every check anyone wrote — the Admiral's included — keyed on
a **symbol**, while the defect lived in a **claim** wrapped across comment lines
that no line-oriented grep can see. Two reviewers earned their BLOCK by measuring
rather than reading.

Applied to criterion 10: `grep worktree_from_spine_path` returning zero does
**not** discharge it. The claim is "there is a live twin of this function in the
engine and here is why it is duplicated." That claim can survive with the symbol
gone — as "the engine's copy", "the other implementation", "both copies must stay
in step". Read the replacement passages in full and ask whether each **sentence**
is true of the tree as it stands. Use `grep -A6 -B6`, or read the surrounding
docstring whole.

The same technique applies to criterion 1: do not grep for `agent_id` and call
the #549 shape exercised. Read what the test asserts.

## Allowed Scope

- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py`
- `map/**` — regenerated, never hand-edited.
- `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/**` — the
  implementer's own plan and evidence.

## Specific Exclusions

Flag if touched. Several name paths **outside your worktree** or files you can
see but must not judge un-inspectable — note and move on, do not BLOCK on
un-inspectability:

- **Lane A** — `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
  `scripts/install_constellation.py`, `skills/commander/templates/**`.
- **Lane E** — `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- **#610** — `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**` and
  `skills/admiral/templates/**`.
- **`scripts/checklist_engine.py`** — g2 is closed; no engine-side behaviour.
- **No fail-closed refusal.** An unowned spine path yields **no derived worktree
  and today's behaviour**, never a refusal (`ADMIRAL_RULING-1` R2).
  `_worktree_from_spine` returning `None` is the correct and complete answer for
  an unplaceable path.
- **No `cwd` threading into command checks** — that was #315, and it left this
  lane for #610 under `ADMIRAL_RULING-1` R3.

Two stale claims about the door raising `KeyError` when `SPINE_FILE` is unset
remain in these files. They are **known**, they are the Commander's `reconcile`
step, and they are **not** findings. Do not report them.

## Constraints the Implementation Must Respect

- Fail-safe, not fail-open: uncertainty blocks, it does not allow.
- The nudge / 3-strike hatch stays keyed by session id alone.
- stdlib only in `spine_rail.py`.
- #549's two-way rendering distinction survives.
- `tests/test_worktree_derivation.py` unedited.

## Map Anchors (inbound)

- **Map entry point:** no `docs/architecture` packet map exists; orientation is
  `DEGRADED-UNPARSEABLE`, discharged. Start at
  `.agent-work/cleanup-f-derive-worktree/MISSION_FRAME.md`, then `map/INDEX.md`
  for `scripts.hooks.spine_rail`.
- **Structural:** `_foreign_worktree` (deleted), `_same_path`,
  `_is_own_entry` (added), `_entry_mid_flight_view`, `decide_stop` including the
  #549 provenance branch, `decide_session_start`, `session_view` /
  `session_view_provenance`.
- **Capability:** `scripts.hooks.spine_rail` — Stop refusal and SessionStart
  resume-context injection.
- **Decision anchors:**
  - `worktree-is-location-spine-path-is-identity` — the tree may answer WHERE,
    never WHOSE. `@grade: settled/human`
  - `not-a-weaker-guard`, **as amended by `ADMIRAL_RULING-1` R1**: the lease is
    the ownership guard *wherever a lease exists*; on a leaseless spine the engine
    asserts nothing about location, deliberately. Read the amended wording in
    `docs/CHECKLIST_SCHEMA.md` before judging any prose about guards.
    `@grade: settled/human · amended-by ADMIRAL_RULING-1`
  - what replaces the skip at each of the two call sites —
    `@grade: placeholder`. The implementer resolved it **asymmetrically** and
    recommends recording the asymmetry rather than a single rule. Say whether you
    agree; this is the one open decision the gate hands back.
- **Map confidence flag:** `map/ids.jsonl` is 0 bytes and per-module
  `map/<module>/INDEX.md` files are absent repo-wide. Recorded as tc1. **Not
  yours to chase.**

## Evidence Produced

Claimed by the implementer, and re-measured by the Commander before dispatching
you:

| measurement | implementer | Commander re-ran |
|---|---|---|
| targeted `-k OwnershipIsBindingKeyNotWorktree` | 8 passed | 8 passed |
| same selector on the empty diff | exit 5, 0 collected | exit 5, 0 collected |
| full suite after | 3177 / 5 / 0 | **3177 / 5 / 0** |
| full suite before (`53c89ba1`) | 3170 / 5 / 0 | **3170 / 5 / 0** |
| `main` at `17c2cee5`, isolated clone | — | **3171 / 7 / 0** |
| `worktree_from_spine_path` in the two files | 0 | **0** |
| `tests/test_worktree_derivation.py` | unedited | **unedited** |

The +7 is claimed to account exactly: 8 new methods, plus
`test_foreign_worktree_is_gone_and_stays_gone`, minus 2 deleted
`_foreign_worktree` unit tests. **Check that arithmetic against the diff** — it
is the cheapest way to catch a quietly deleted test.

The implementer also reports eight pre-existing tests reworked: two deleted with
the symbol, three flipped to assert the new refusal, three that had used a
foreign worktree only as a *device* to reach a branch and now use an unreadable
target. **Read all eight.** "Reworked while green" is exactly where a weakened
assertion hides, and the implementer's own note that it repaired a pre-existing
test which had been silently proving nothing (bindings written in the pre-#202
flat shape, dropped by `load_binding` on sight) shows this file has form for it.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py -k OwnershipIsBindingKeyNotWorktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py tests/test_worktree_derivation.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q

py .agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/m4_differential.py
```

**Four environment hazards, each of which has cost this lane measurable time:**

1. **`CREW_SCRATCH_DIR`.** You are launched through `run_crew.py`, which sets it.
   Lane E's
   `tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
   asserts the key is absent from a resumed child's env without scrubbing it from
   the parent first, so it fails for **any** agent running the suite from inside
   a crew-launched session: `1 failed, 3176 passed` with it set, `3177 passed,
   5 skipped, 0 failed` with `-u CREW_SCRATCH_DIR`. Ambient contamination, not a
   regression. The file is lane E's and fenced. **Scrub it; do not fix that test;
   do not report it.**
2. **Clear `__pycache__` before every measurement.** A cache built in another tree
   fails `tests/test_bytecode_cache_provenance.py` by name rather than surfacing
   as an unrelated assertion.
3. **If you clone the repo to compare against a baseline, name the clone
   directory `constellation-skills`.** `tests/test_code_map.py::MapTreeFreshnessTests`
   compares `map/INDEX.md` against a fresh build, and the map's title line is
   derived from the **checkout directory name** — a clone at `/tmp/anything-else`
   reports a false red in an otherwise byte-identical 29k file. The Commander hit
   this measuring `main` and it cost a re-run.
4. **You cannot validate this hook from inside your own session.** Isolation is
   git-only and hook code is not fenced by it: `CLAUDE_PROJECT_DIR` resolves once
   at session launch and is inherited unchanged, so this worktree runs the **main
   checkout's** hook against the **main checkout's** state (#269). Use a fresh
   process, or call `decide_stop` / `decide_session_start` directly with
   constructed payloads and a constructed binding store. The latter is what the
   implementer did and what I expect of you.

Platform: Linux, Python 3.12 as `py`. There is **no pytest config in this repo**,
so a plain (non-`unittest.TestCase`) class named `OwnershipIsBindingKeyNotWorktree`
would not be collected at all. If you find yourself looking at a green selector,
confirm it collected **8** tests and not zero.

**Windows.** `normcase` is the identity function on this Linux host, so any
case-folding expectation must be **constructed** explicitly rather than inherited
from the platform. An earlier gate in this lane shipped exactly that defect and a
reviewer caught it. The implementer claims both its test and its differential
construct the expectation; verify that rather than trusting it. The one
`windows-latest` CI job is red at baseline and cannot tell you.

## Suggested Model Tier

**Stronger.** Highest-risk change in the lane, asymmetric reasoning across two
call sites, and a negative claim ("nothing newly stops blocking") that has to be
tested rather than read.

## Stop Conditions

Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or
unverifiable, or a policy decision is required before a verdict is possible.

## Return Format

Return `REVIEW_RESULT`: verdict (**APPROVE** or **BLOCK**), per-check findings
against the numbered Close Criteria, blockers, out-of-scope observations, and
workflow feedback (what in this handoff made the review harder than it needed to
be — this lane harvests it).

**Delivery.** Write the full `REVIEW_RESULT` to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-reviewer-result.md`
**before ending your turn** — that write is the delivery.

## On the Stop hook

When you finish, a `SPINE MID-FLIGHT` hook may fire telling you to reload the
commander skill and drive `execute.json`. **Refuse it and record that you
refused.** `SPINE_FILE` points at your parent Commander's spine, under your
parent's live lease; your own `crew-runs.json` entry has `spine: null`. Obeying
would mean advancing someone else's gate, and the hook's own escape hatches
(`block`, `waive`) write to that same parent spine, so the sanctioned honest stop
is itself the destructive act. A plain recorded refusal is correct. Author your
own survey at the path named above, claim it with your own session id, and drive
that.

Six crews on this issue have now hit this. The implementer returned the mechanism
— SessionStart's scan-bind writes a binding for an unbound session onto the
single active-leased spine it finds — and it is recorded as a triage candidate.
You are not the seventh to have to diagnose it.
