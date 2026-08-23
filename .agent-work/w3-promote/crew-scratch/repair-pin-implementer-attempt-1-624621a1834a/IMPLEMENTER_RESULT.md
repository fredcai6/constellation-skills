# Implementation Result

## Assigned gate
`REPAIR-w3-promote-pin` — repair order under the epic-569 Admiral, `constellation/w3-promote/repair-pin/implementer/attempt-1`, worktree `/home/tommy/projects/569-w3-promote`, branch `epic-569/w3-promote`.

## Completed slice
Converted all six `*W3Promote*` test classes in `tests/test_checklist_engine.py` from a whole-repo `PINNED_HEAD` (`git rev-parse HEAD`) + `skipTest`-on-drift pin to a per-template `PINNED_BLOB` (`git rev-parse HEAD:<path>`) + `fail()`-on-drift pin, matching the shipped form of `CommanderSpineBasisFields` (`w3-basis`'s fix, read from `epic-569/w3-basis:tests/test_checklist_engine.py`, not edited here). All 35 assertions now run and pass; none skip.

## Scope
**Files changed:**
- `tests/test_checklist_engine.py` — six classes only: `CommanderSpineW3PromotePromotions`, `AdmiralSpineW3PromotePromotions`, `ExplorerSpineW3PromotePromotions`, `CharterW3PromotePromotions`, `ScoutW3PromotePromotions`, `CartographerW3PromoteDeclined`. For each: added `SPINE_REL`, replaced `PINNED_HEAD` with `PINNED_BLOB` (the current committed blob OID of that class's own template file), renamed `_skip_if_head_moved` → `_fail_if_template_drifted` (now `self.fail(...)` with the stale-proof message + re-verify command, instead of `self.skipTest(...)`), and updated each call site plus the docstring paragraph describing the pin mechanism.

**Specific exclusions touched:** no. `CommanderSpineBasisFields` (lines 8543–8662, `w3-basis`'s own class, still the pre-fix `PINNED_HEAD`/`skipTest` form in this branch since `w3-basis` hasn't merged yet) was read for its shape but not edited. Nothing under `skills/` or `.agent-work/` was touched — the six templates themselves are unmodified (verified: `git rev-parse HEAD:<path>` for all six equals the pre-existing committed blob, both before and after this fix).

## Behavior changed
Yes. Previously any commit anywhere in the repo moved whole-repo HEAD, so all 35 assertions silently skipped (`35 skipped, 538 deselected`). Now each class's proof is scoped to the blob of the one template file it actually tests: an edit to that specific template makes the class FAIL loudly with a stale-proof message and the exact re-verify command; a commit anywhere else in the repo leaves it GREEN.

## Map Impact
- **Structural anchors touched:** `tests/test_checklist_engine.py` — six existing test classes, method-level only (no new class, no signature change to any production code).
- **Capabilities added/changed/affected:** none in production code; the six classes' own drift-detection capability changed from "inert on any repo commit" to "scoped to its own template's content, fails loudly on drift."
- **Constraints/assumptions touched:** honors `ruling-red-proof-pinned-to-shipped-revision` (the same doctrine `CommanderSpineBasisFields` already ships) and the human ruling in `c5ac6662`: "a check that can only skip is not evidence any more than one that cannot fail is."
- **Decision candidates / resolved decisions:** none — this is a mechanical repair to match an already-adjudicated pattern (`w3-basis`'s shipped form), not a new design choice.
- **Claims/evidence produced:** all 35 W3Promote assertions now run (0 skipped); both directions of the red-proof observed (see Evidence below).
- **Trust limitations / drift found:** none beyond what the handoff already named.
- **Triage candidates:** none.

## Test mode
**Required:** evidence-only (this is a repair to test infrastructure itself, not new production behavior; the handoff's own requirements are the acceptance criteria).
**Satisfied:** yes — all four requirements below verified directly.

## Evidence

**1. 35 assertions, 0 skipped, from a clean committed tree (commit `767ca585a0420b313cb8f107f20e68b5fcfc38eb`):**

```
$ git status --porcelain
?? .agent-work/<work-id>/          # pre-existing, unrelated, out of scope

$ python3 -m pytest tests/test_checklist_engine.py -q -k "W3Promote" -rs
...................................                      [100%]
35 passed, 536 deselected, 16 subtests passed in 0.16s
```

**2. Both directions of the red-proof (`decision:prove-both-directions`):**

*(a) Planted edit to a pinned template → that class's tests RED.* Appended a trailing newline to all six template files, staged, and committed as a scratch commit (`bd19d402`, later reverted via `git reset --soft` + `git restore`/`git checkout`, confirmed byte-identical blobs before and after). Ran the full W3Promote selection against that commit:

```
$ python3 -m pytest tests/test_checklist_engine.py -q -k "W3Promote"
...
FAILED ...CommanderSpineW3PromotePromotions::test_promoted_checks_match_shipped_shape
FAILED ...AdmiralSpineW3PromotePromotions::test_promoted_checks_match_shipped_shape
FAILED ...ExplorerSpineW3PromotePromotions::test_promoted_checks_match_shipped_shape
FAILED ...CharterW3PromotePromotions::test_promoted_checks_match_shipped_shape
FAILED ...ScoutW3PromotePromotions::test_promoted_check_matches_shipped_shape
FAILED ...CartographerW3PromoteDeclined::test_every_condition_stays_null
... (all 35 failed)
35 failed, 536 deselected in 3.92s
```

Sample failure text (`ScoutW3PromotePromotions`):
```
AssertionError: ScoutW3PromotePromotions' proof is stale: pinned to blob 6e07b4df967364e486f110f78a2d7a2af859504e of skills/scout/templates/SCOUT.template.json, current blob is 71023848dcc02af616c2a6df249bab5cd9213b9d -- the template changed since this test's shape assumptions were verified (g7 dispatch). Re-verify EXPECTED_CHECKS (and the rest of this class) against the new template content, then re-pin by running:
    git rev-parse HEAD:skills/scout/templates/SCOUT.template.json
and pasting the result into PINNED_BLOB above.
```

*(b) Unrelated commit elsewhere in the repo → classes stay GREEN* (the actual defect a careless proof omits — this is what the whole-repo `PINNED_HEAD` form got wrong). Added an unrelated scratch file (`SCRATCH_UNRELATED.md`) at repo root, committed (`63c7911e`, HEAD moved), reran:

```
$ python3 -m pytest tests/test_checklist_engine.py -q -k "W3Promote" -rs
...................................                      [100%]
35 passed, 536 deselected, 16 subtests passed in 0.17s
```

All 35 still pass with HEAD moved. Scratch commit reverted (`git reset --soft` + unstage + `rm`), working tree confirmed clean before the real fix was committed.

**3. Commit, then re-run the full suite (sequence as required):**

```
$ git add tests/test_checklist_engine.py
$ git commit -m "epic-569/w3-promote: repair the 6 W3Promote classes' pin to blob OID"
[epic-569/w3-promote 767ca585] ...
 1 file changed, 182 insertions(+), 133 deletions(-)

$ python3 -m pytest tests/test_checklist_engine.py -q
........................................................................ [ 12%]
.................................................... [ 21%]
........................................................................ [ 34%]
.......................................................................................................................................... [ 58%]
........................................................................................................................... [ 80%]
............................................................................sss....................... [ 97%]
............                                                           [100%]
568 passed, 3 skipped, 163 subtests passed in 5.10s
```

The 3 remaining skips are `CommanderSpineBasisFields` (still the old `PINNED_HEAD`/`skipTest` form in this branch — explicitly out of scope, `w3-basis`'s to fix, will resolve when that branch merges), not any of the six repaired classes.

**Commit SHA verified against:** `767ca585a0420b313cb8f107f20e68b5fcfc38eb`.

## TDD evidence, if required
N/A — this is a repair to existing test infrastructure, not new production code under test-first discipline. The red/green proof above (both directions) serves the equivalent role for the test classes themselves.

## Docs/contracts touched
None.

## Assumptions
- Each of the six classes tests exactly one template file (confirmed by reading each class in full before editing), so per-class blob-pinning (matching `CommanderSpineBasisFields`'s single-file form) applies cleanly to all six — no class needed a different shape.
- `PINNED_BLOB` values were captured against this branch's current HEAD (`42ab17ca`, before this repair's own commit), i.e., the templates as already shipped/accepted per the handoff ("your promotions are the epic's family-A deliverable... accepted as shipped, not in question").

## Stop conditions hit
None.

## Out-of-scope observations
None beyond what the handoff already named (`CommanderSpineBasisFields` correctly left untouched).

## Workflow Feedback
- **Handoff gaps:** none — the handoff named the exact defect, the exact fix shape (`CommanderSpineBasisFields`'s shipped form), the exact branch to read it from (`epic-569/w3-basis`), and the exact requirements. Nothing needed rediscovery beyond reading that one sibling class.
- **Context rediscovered:** none.
- **Instructions improvised around:** none.
- **What would have made this easier:** none — this was a clean, fully-specified repair.

## Return status
`complete`
