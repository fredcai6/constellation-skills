# Cold plan critic — issue-456

Run against `plan-candidate.json` + `MISSION_FRAME.md` + `ownership-scope.md`
only, by an agent with no authoring context. 15 findings; 4 BLOCKING.

Dispositions marked **APPLIED** are folded into `plan-candidate.json` already.
Dispositions marked **HUMAN** change the gate count or scope and are Tommy's
call at plan approval.

## The critic's single most-important change

> Strip g1 to format-independent invariants and move every corpus-count and
> render-shape baseline into one new baseline gate after g6 — because as
> written, g1's thresholds are guaranteed to be rewritten by g4, g5 and g6, and
> a threshold that gets edited whenever a later gate turns it red is exactly the
> print-only diagnostic this whole issue exists to replace.

## Findings

| ID | Gate | Sev | Finding | Disposition |
|---|---|---|---|---|
| F1 | g1,g4,g5,g6 | BLOCKING | g1 commits hole counts, ASCII provenance, edge recall and churn — all measured against rendered output. g4 deletes a stage, g5 restructures the index, g6 changes every referenced-by line. g1's baselines are invalidated three times after being committed, and the cheapest in-gate fix each time is to edit the baseline. | **HUMAN** — split g1; new baseline gate after g6 |
| F2 | g2 | BLOCKING | g2's stated mechanism is not what the evidence measures. | **APPLIED** — and the critic's own numbers were wrong too; see below |
| F3 | none | BLOCKING | The skills cherry-pick has no gate. The plan ships the very rule it breaks (`d102c05` adds the one-gate-per-file rule). Second-order: skills tell crews to cite a map entry point that will not exist in this repo. | **HUMAN** — add an integration gate; rule on the dangling entry point |
| F4 | g1,g2,g9 | BLOCKING | The corpus is modified by this run, so absolute counts are stale before g2 finishes. File count drifted 233→239→241 during authoring alone. | **APPLIED** — thresholds must be ratios or run-time invariants |
| F5 | g1–g9 | MAJOR | Nine gates share one command; vacuous for g5, g6, g8, g9 where the close criterion is judgment or process, not a property. | **APPLIED** — per-gate selectors |
| F6 | g1–g9 | MAJOR | The full suite is never re-run after g0, though g0 edits `.gitignore`, g4 removes a stage and g9 adds a fixture dir. First signal would be CI after all ten gates. | **APPLIED** — every gate runs the full suite plus its selector |
| F7 | g0 | MAJOR | g0 is three gates wearing one label, and "port with no behavior change" is unfalsifiable — there is no prior behavior to diff against. Its file list is also incomplete: `render_fn.py` imports `render as R`, and no `render.py` was present. | **APPLIED (partly)** — claim narrowed to "no defect fixes, no schema changes"; `render.py` recovered from `evidence/x11`, so the import graph closes. **HUMAN** on splitting g0 |
| F8 | g0 | MAJOR | The installer confidence flag pointed at `_direct_runtime_siblings`, a TEST HELPER called with a hardcoded entry — it can never reach `scripts/code_map/` and passes vacuously. The real hazard is `install_constellation.py`: the install destination stays flat, so a package with intra-package imports cannot survive bundling. | **APPLIED** — flag rewritten at the real hazard |
| F9 | g5,g6 | MAJOR | Nothing owns the committed `map/` tree. ~3,411 pages into a repo tracking ~3,441 files roughly doubles it, and g4/g5/g6 each churn it wholesale. Also: 75% of the corpus is test code, so g5's routing tier and g6's split are designed against a unittest-shaped corpus. | **HUMAN** — name an owning gate, or rule the tree out of this run |
| F10 | g9 | MAJOR | A four-way conjunction across a code fix, a fixture, a prose artifact and a measurement. Can only pass or fail whole; the prose conjunct absorbs the others' slack. | **HUMAN** — split |
| F11 | ownership-scope | MINOR | The coverage claim was false: class 10 and the four `skills/` files had no gate. | **APPLIED** — corrected in place, and it does not pass yet |
| F12 | g0/g4 | MINOR | g0 adds a `.gitignore` entry for the supplement; g4 deletes the supplement stage; nothing removes the dead line. | **APPLIED** — added to g4's close |
| F13 | g1 | MINOR | g1's close pointed at a falsifier table in neither the plan nor the frame. | **APPLIED** — six falsifiers inlined |
| F14 | scale | MINOR | At ~30 dispatches the first failure is F1: reviewers independently re-derive corpus counts and start disagreeing with g1's numbers. Least worth crew overhead: g3 (fold into g2), g5, g9. | **HUMAN** — gate count |
| F15 | frame | MINOR | Three places leaned on assertion: the stale file count, the D2 characterization, and the installer flag. All were checkable in under a minute; none had been checked. | **APPLIED** — all three corrected |

## Where the critic was itself wrong

F2 is correct that the D2 mechanism was mis-stated, and correct that "all N
collisions resolve" is a vacuous close criterion. **Its replacement numbers were
also wrong**, for the same root cause as the Commander's: both flattened the
symbol to `module.name`.

`astx.py:_func` emits `mod:{clsstack[-1]}.{name}` whenever any class is on the
stack, so methods are already qualified by their class and cannot collide as
either pass assumed. Simulating the real rule gives **4** real collisions, not
75 and not 67+7 — all of them a closure inside a method being folded onto its
class, which is D2 exactly. See `reference/d2_collisions.txt`.

The lesson worth keeping: three passes were spent because each modelled the
symbol rule instead of reading the code that emits it. The x13 renderer's own
docstring stated the defect precisely the whole time.
