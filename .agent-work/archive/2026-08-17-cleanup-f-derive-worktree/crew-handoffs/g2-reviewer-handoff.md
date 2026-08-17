# Reviewer Handoff

## Gate
`g2` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`.
**Diff base: `9ff86f2d`** (g1, committed and independently approved).

## What was implemented

**Stamp-and-compare is retired.** Three coupled changes:

1. `origin_worktree_refusal` stops comparing the stamped `origin.worktree`
   against the engine's ambient cwd.
2. The per-guarded-verb `git rev-parse --show-toplevel` in `main()` is gone.
3. `origin.worktree` keeps being **written** as provenance and is read by nothing
   for a decision, pinned by a `provenance`-named test.

Plus prose repairs in `docs/CHECKLIST_SCHEMA.md` and `scripts/spine_lifecycle.py`.

This is a large **subtraction**: `git diff 9ff86f2d --stat` is 273 insertions,
**623 deletions**, concentrated in `scripts/checklist_engine.py` (−168 net) and
`tests/test_spine_origin_isolation.py` (695 changed).

## How to inspect the diff

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree
git diff 9ff86f2d --stat
git diff 9ff86f2d
```

Read the implementer's account first:
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-result.md`.
Then the gate plan (`.agent-work/cleanup-f-derive-worktree/execute.json`, task
`g2-implement`) and `.agent-work/cleanup-f-derive-worktree/MISSION_FRAME.md`.

## Task statement

Verbatim from the frozen plan: the refusal stops comparing; the ambient git read
goes away; the stamp stays written and is read by nothing for a decision, pinned
by a test. **This gate adds no fail-closed refusal** — see below.

## Close criteria — verify each yourself

- **No `rev-parse --show-toplevel` anywhere in `scripts/checklist_engine.py`.**
- **No decision path reads `origin.worktree`.** The implementer was told to
  enumerate by command and state the count. **Reproduce that enumeration
  yourself** and judge whether every survivor is genuinely not a decision.
  (I count 6 surviving mentions of `origin_worktree_refusal` under `scripts/`,
  all of which look like prose to me — two of them in **fenced** files the gate
  could not edit. Confirm or correct that reading.)
- **`origin.worktree` is still written.** A retirement that quietly stopped
  stamping it would satisfy "nothing reads it" for the wrong reason.
- **The `provenance` test genuinely pins both halves.** Apply the deletion test
  in both directions: make the code stop writing the stamp — does it go red? Make
  something read it for a decision — does it go red? If either stays green, the
  pin is decorative and this gate is not met.
- **The subtraction removed no guard that was doing work.** This is the
  load-bearing judgment of the gate and the reason you are here. Go looking, in
  the deleted code, for a case where the comparison was the only thing preventing
  harm. The implementer was asked to run that search and report either way —
  **do not take its negative on trust; run your own.**
- **The refusal path's position.** It sat *before* `dispatch()` and returned
  *without* `save()`, so a refusal never wrote into the tree it protected.
  Confirm nothing now writes state on a path that previously refused first.
- Full suite green, cache cleared, clean env.

**This gate's targeted check** — I ran it and it passes; reproduce it:

```bash
! git grep -q 'rev-parse --show-toplevel' -- scripts/checklist_engine.py \
  && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
       tests/test_spine_origin_isolation.py -k provenance
```

## THIS GATE MUST ADD NO FAIL-CLOSED REFUSAL — verify it did not

The shape refusal for an unowned spine path ("a guarded verb against a spine
whose path has no `.agent-work` ancestor is refused") is gate **g4**, which is
**floated to the Admiral and may not proceed**. It would refuse **362 of 429**
guarded-verb invocations across **125 tests**, three of them in a lane-E-fenced
file.

So: confirm the engine now refuses **nothing it did not refuse before this gate**,
beyond losing the comparison. A refusal smuggled in here would be a **BLOCK**.
Check the guarded/exempt verb sets and every early-return on the verb path.

## Allowed scope of the change (flag anything outside it)

`scripts/checklist_engine.py`, `scripts/spine_lifecycle.py`,
`docs/CHECKLIST_SCHEMA.md`, `tests/test_spine_origin_isolation.py`, `map/**`, and
any test this change legitimately broke. Five files differ from `9ff86f2d`.

## Specific exclusions (a breach here is a BLOCK)

- **Lane A (#603):** `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
  `scripts/install_constellation.py`, `skills/commander/templates/**`.
  `mcp_spine_server.py:18`, `:371`, `:384` and `run_crew.py:860` carry **prose
  describing the retired guard** and are **deliberately left stale** — that is
  correct behaviour, not a defect, and belongs in your out-of-scope observations
  for the owning lanes.
- **Lane E:** `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- **#610:** `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**`,
  `skills/admiral/templates/**`.
- **Not this gate:** `_foreign_worktree` / the Stop hook (g3); any `cwd`
  threading into command checks (g5, floated). `scripts/hooks/spine_rail.py`
  should be **untouched** by this gate.

## Constraints the change had to respect

- **`tests/test_spine_origin_isolation.py::test_it_is_pure` is not transitive** —
  it reads only `origin_worktree_refusal.__code__.co_names` and cannot see
  impurity in a callee. If any purity claim survives in this diff, judge whether
  it is *guaranteed* or merely *inherited from a test that cannot see*.
- This change **supersedes** the 2026-08-15 worktree-identity ruling in
  `.agent-work/rulings/2026-08-15-worktree-identity.md`. The implementer was told
  to cite it where the change contradicts it and say so plainly. Check that it
  did.
- `worktree_from_spine_path` (from g1) was **available but optional** here. If the
  gate used it, check the use is real; if it did not, that is fine and stated.

## Map anchors (inbound)

No `docs/architecture` packet map exists; orientation is `DEGRADED-UNPARSEABLE`,
discharged. Start at `.agent-work/cleanup-f-derive-worktree/MISSION_FRAME.md`,
then `map/INDEX.md` for `scripts.checklist_engine` and `scripts.spine_lifecycle`.

Decision anchors:

- `derivation-authoritative-stamp-becomes-provenance` `@grade: settled/human`
- `not-a-weaker-guard` — the lease was always the guard `@grade: settled/human`
- `worktree-is-location-spine-path-is-identity` `@grade: settled/human`
- `nearest-ancestor-fail-closed` — **second half floated as g4**
  `@grade: settled/human`

A `settled/human` anchor is **not yours to unsettle**; contradicting evidence is a
finding to report.

**Map confidence flag:** cited line numbers have already proved stale twice in
this lane (`_foreign_worktree` at `:639` vs `:693`;
`docs/CHECKLIST_SCHEMA.md:124`'s own citation). **Re-read before trusting any
cited line, including mine.**

## Evidence the implementer produced

A before/after of the guarded-verb path; an enumeration of remaining
`origin.worktree` reads with counts; the provenance pin; and an adversarial
search for a guard genuinely lost. Reproduce every figure — a correct conclusion
does not excuse a wrong supporting number.

**Measured by me, in my own hands:** targeted check **passes**; full suite
**3135 passed, 5 skipped, 0 failed** (125.76s), cache cleared, clean env. The
count is *lower* than g1's 3159 because this gate deleted the tests for the
comparison it removed — confirm that drop is entirely accounted for by deletions
you can point at, and not by tests that silently stopped running.

## Verification commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

! git grep -q 'rev-parse --show-toplevel' -- scripts/checklist_engine.py \
  && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
       tests/test_spine_origin_isolation.py -k provenance

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_spine_origin_isolation.py tests/test_spine_lifecycle.py \
  tests/test_worktree_precondition_wiring.py tests/test_mcp_door_engine_cwd.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

Platform: Linux, Python 3.12 as `py`. Clear `__pycache__` before every
measurement — a cache built in another tree fails
`tests/test_bytecode_cache_provenance.py` by name.

**The tripwire** `tests/test_worktree_precondition_wiring.py` must be **green**.
Its collision with the #315 `cwd` thread belongs to gate g5, which is floated; it
must not be disturbed here.

**Windows:** `normcase` is the identity function on this host and the one
`windows-latest` CI job is red at baseline. Judge whether any case expectation in
this diff is **constructed** or merely inherited from the platform — a
predecessor gate shipped exactly that defect and it took a reviewer to catch it.

## Stop conditions

Stop and return if the diff touches a fenced file, if required evidence cannot be
reproduced, or if a judgment outside this gate's scope is needed.

## Return format

Return `REVIEW_RESULT` with `Verdict: APPROVE` or `Verdict: BLOCK` on its own
line, plus findings (severity, claim, the evidence you ran, what you would
change), out-of-scope observations, and Workflow Feedback.

`BLOCK` for anything failing a close criterion or breaching an exclusion.
Out-of-scope finds are triage candidates, not blocks.

**Delivery.** Write the full `REVIEW_RESULT` to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-result.md`
**before ending your turn** — that write is the delivery.
