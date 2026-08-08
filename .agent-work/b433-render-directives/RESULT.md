# RESULT — issue #433, render `directives` in the `current` projection

**Status: handed off at a seam, not finished.** Two of three execute gates are done, reviewed and
committed; the third (`g3-schema`, a two-place doc correction) and the spine's closeout steps remain.
The Commander driving this run tripped the context governor's HARD band at `g2-integrate`, filed the
refresh-request the engine demands (`e-g2-integrate-3`, seam `g2-integrate`, `why_ref` `w-6`), and
stopped. This is the second such handoff on this job; the predecessor stopped the same way at `plan`.

Full detail — inventory, dispositions, triage candidates, crew workflow feedback — is in
`.agent-work/epic-418-redux/notes-433.md` under "Execution log — successor Commander". Resume
instructions are in `STATE_NOTE.md` beside this file.

## Verdict

`directives` renders, and the class of unrendered-field defects is closed by a completeness property
that has been observed **failing** — not merely passing.

## Evidence

**Test command and real exit code** (no pipe, so `$?` is pytest's own):

```
$ cd C:/Programs/constellation-skills-wt/r418-433 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
1731 passed, 4 skipped, 647 subtests passed in 386.42s
REAL_PYTEST_EXIT=0
```

Baseline from LO-433 (main at `ca0e36a`): 1721 passed, 4 skipped, 643 subtests, exit 0. Green, above
baseline, +10 tests.

**Before / after `current` for a populated `directives` block** — captured on this run's OWN spine
`execute` gate, so the deliverable proves itself. Full capture:
`evidence/g1-before-after-current.txt`. The delta is purely additive, 8 lines, first line
byte-identical:

```
directives:
  replan_input:
    template: ../constellation-replan/templates/REPLAN_INPUT.template.json
    output: .agent-work/b433-render-directives/REPLAN_INPUT.json
    evidence_fields: completed_outcomes, wave_evidence, discrepancies
    classifications: blocks_current_wave_exit, invalidates_forecast_or_decomposition, later_only, evidence_only, drop
    auto_file_discrepancies: false
    check: verify_iterative_role_artifacts.py commander
```

The g1 reviewer extended this corpus-wide: 370 checklist files, 2981 gates, **8 gates change output —
exactly the 8 with a populated block — and 0 first lines change.**

**Proof the completeness property FAILS when a populated field is deliberately unrendered.** Three
red-proofs, produced by the implementer, independently reproduced by a cold reviewer, and one
reproduced a third time by the Commander in its own hands:

| proof | world it recreates | result |
|---|---|---|
| R2 | the extractor blinded to dicts (the old `_flatten`) | ledger set-mismatch naming `anchors`, `directives` — EXIT=1 |
| R4 | a populated field that flattens to nothing | fails **by name** — EXIT=1 |
| R5 | a field added to `_build_amend_task`, not to the fixture | superset assertion fails **by name** — EXIT=1 |

The Commander's own R4 run (`evidence/g2-integrate-commander-red-reproduction.txt`):

```
E   AssertionError: Items in the second set but not the first:
E   'commander_r4_break' : populated field(s) ['commander_r4_break'] were carried by the loop but
E   asserted NOTHING -- _leaf_texts read no text out of them, so current()'s output was never
E   checked against their content
REAL_RED_EXIT=1
```

Tree restored md5-identical after each break; break-marker greps return zero.

**The g1 golden was captured RED before the renderer existed**, and the Commander reproduced that too
(`evidence/g1-integrate-commander-red-reproduction.txt`): engine reverted to HEAD
(`git diff --quiet` exit 0, `grep -c _render_directive_lines` = 0) with the goldens still in the tree
→ 5 failed, `REAL_RED_EXIT=1`; restored, md5 OK.

## Inventory result — render, not delete

2955 gates scanned tree-wide, **8 populated `directives` blocks, every one a dict of nested contract
dicts**. Not vestigial: three shipped spine templates carry it (commander `execute`, admiral
`execute`, explorer `confirm`), every run instantiated from them inherits it, and
`tests/test_iterative_planning_doctrine.py` asserts the parsed contract in all three. Rendered.

The schema's declared type (`[string] | null`) is drifted — that correction is `g3-schema`, the
remaining gate.

## Subsumption

Pre-declared candidate set: **10** (filed before the first code change). **Closed: 0 of 10.** Each
declined in writing with a reason in `notes-433.md`; #345 (built-not-wired) is served in part and
stays open.

## Isolation proof

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/r418-433
worktree OK: in C:/Programs/constellation-skills-wt/r418-433
EXIT=0
```

## What remains

1. `g3-schema` — correct `docs/CHECKLIST_SCHEMA.md`'s Task table row and the Rendering section, then
   the broad-suite postcondition. **Read `STATE_NOTE.md` first**: the g1 reviewer found a third false
   sentence at line 138 that the gate's pinned invariant chain does not currently catch.
2. Spine closeout: reconcile → triage → review → feedback → archive, then release the lease last.
3. Open the PR against `main` with `gh pr create -F <file>`. Not opened here: the deliverable is
   incomplete, and LO-433 authorizes the PR "when green" in the sense of finished-and-green.
