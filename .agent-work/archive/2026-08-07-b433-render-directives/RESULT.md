# RESULT — issue #433, render `directives` in the `current` projection

**Status: complete.** All three execute gates are done and the spine is driven to closeout. This run
was finished by the **third** Commander dispatched to it: the first stopped at the `plan` seam and
the second at `g2-integrate`, both on context-governor HARD trips. No committed work was redone.

Full detail — inventory, dispositions, triage candidates, crew workflow feedback — is in
`.agent-work/epic-418-redux/notes-433.md`.

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

The schema's declared type (`[string] | null`) was drifted; corrected in `g3-schema` below.

## Subsumption

Pre-declared candidate set: **10** (filed before the first code change). **Closed: 0 of 10.** Each
declined in writing with a reason in `notes-433.md`; #345 (built-not-wired) is served in part and
stays open.

## Triage — nine candidates, all filed

Registered in `execute.json` as `tc1`-`tc9` and **filed to the tracker**, not banked worktree-locally:

| candidate | issue |
|---|---|
| `append()`/`_build_amend_task` duplicate the Task shape by hand | #474 |
| a template-only Task field is invisible to the superset assertion — **`anchors` is one today** | #475 |
| nothing checks the schema doc's Task table against the builder | #476 |
| the gauge is read per checklist directory, so a crew inherits its Commander's reading | #477 |
| crew work areas are minted beside the owning plan, not under it | #478 |
| dead defensive branch in `_render_directive_lines` (proved dead by mutation; kept deliberately) | #479 |
| the flat-list silent drop — fixed in g2, filed as the record | #480 |
| a stale gauge reading outlives its session | #481 |
| reviewer/dogfooding conflict: the engine you drive is the engine you break | #482 |

**Read #475 first.** It is the one candidate that shows the defect class #420 and #433 both attacked
is *still open today*, by name: `anchors` reaches the corpus through templates only, so the superset
assertion this issue shipped cannot see it.

Authority to file: LO-433's Inherited Latitude floats *closing* an issue but not *filing* one, and
the spine's triage step names the citation that satisfies its user-approval postcondition in
delegated mode. The Admiral can overrule cleanly.

## Isolation proof

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/r418-433
worktree OK: in C:/Programs/constellation-skills-wt/r418-433
EXIT=0
```

## The schema record (g3)

`docs/CHECKLIST_SCHEMA.md` corrected in the two pinned places, verified by command postconditions
frozen at plan time rather than proxies invented at execution time:

- **Task table row** — declared `[string] | null`; now declares `{name: {…contract}}` | `[string]` |
  `null`, names the dict shape the corpus actually carries, and carries the real `replan_input`
  example.
- **Rendering section** — asserted a **false** "Known gap, not yet closed: `directives` … is not
  rendered". Now states positively that a populated `directives` block renders on the same
  omit-when-empty terms, names both live shapes, and records what made the completeness property
  capable of failing, including its stated residual limit (template-only fields).

The carried-forward g1 reviewer finding is resolved rather than merely noted: the "is not rendered"
sentence the reviewer flagged is the **same sentence** that carried "Known gap", so c1's conjunction
does catch it. A grep for every `not rendered` / `never surfaced` / `known gap` / `directives`
mention confirms the only remaining `directives` references (handoff and amend-op rows) were already
correct and are untouched.

```
c1 $ ! grep -qi 'known gap' docs/CHECKLIST_SCHEMA.md && grep -qF 'a populated `directives` block' docs/CHECKLIST_SCHEMA.md   -> 0
c2 $ grep -F '| `directives` |' docs/CHECKLIST_SCHEMA.md | grep -q 'dict' && ! grep -qF 'null | forced primitive specifics handed down' docs/CHECKLIST_SCHEMA.md   -> 0
```

## Third-dispatch independent verification

The successor did not take the seam handoff on trust. In its own hands
(`evidence/g2-integrate-successor-commander-verification.txt`):

- Broad suite re-run: **1731 passed, 4 skipped, 647 subtests, REAL_EXIT=0**.
- Red-proof re-reproduced from scratch by nulling the `directives` passthrough in `state()`. The
  property failed **naming the field**, and the failure message shows `constraints:` and `anchors:`
  still rendered while `directives:` is absent — i.e. neither of the other fields covered for it,
  which is precisely the single-flag defect the per-field ledger replaced:

```
AssertionError: 'DIRECTIVE_TEMPLATE_UNIQUE_TEXT' not found in '...' : populated field 'directives'
(value {'replan_input': {'template': 'DIRECTIVE_TEMPLATE_UNIQUE_TEXT', ...}}) has content
'DIRECTIVE_TEMPLATE_UNIQUE_TEXT' missing from current()'s output
REAL_EXIT=1
```

- Tree restored **byte-identical** by `git hash-object` (`ef979b43…` before and after),
  `git status --short` empty, suite green again.

## A note on the governor reading

The `gauge.json` in this work dir held the **second** Commander's reading (18.4%, over the 15% hard
band). The gauge writer hook is not wired into this worktree's `.claude/settings.json` — the known
open item from #180 — so nothing refreshed it for the third dispatch. The successor neither
hand-wrote a gauge record (that would forge the instrument) nor filed a refresh-request claiming a
context exhaustion it was not experiencing (that would put a false statement in the journal and cost
a fourth dispatch). It did the gate work, which needs no `advance`, and advanced once the stale
reading aged out of the reader's 30-minute window on its own — the documented degradation. **This is
worth an issue: a fresh dispatch inherits its predecessor's reading and is blocked by it.**

## PR status

Opened against `main`. The branch is based on `73b4517`, which the Admiral's squash-merge orphaned,
so GitHub reports the PR **CONFLICTING**. That is expected and is not a defect in this work; the
Admiral replants the branch onto `main`. No rebase or merge was attempted here, per LO-433.
