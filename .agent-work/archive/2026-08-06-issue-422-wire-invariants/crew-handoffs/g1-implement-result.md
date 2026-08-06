# Implementation Result

## Assigned gate
`g1-implement` (issue #329/#422, workstream D of epic #418)

## Completed slice
Converted the prose-only worktree-isolation invariant into a real engine gate. `COMMANDER_SPINE.template.json`'s `init` gate now carries a `c0` command precondition running `verify_worktree_isolation.py --here <repo-root>`, first in its `preconditions` array. A new standalone enumeration script, `scripts/verify_worktree_precondition_coverage.py`, fails when any worktree-entering template is missing that precondition. `tests/test_worktree_precondition_wiring.py` lands two deliberate-breakage tests proving both checks actually refuse when broken, not just that they pass when correct.

## Scope
**Files changed:**
- `skills/commander/templates/COMMANDER_SPINE.template.json` — added the `c0` precondition to the `init` gate's `preconditions` array (was `[]`); no other gate touched.
- `scripts/verify_worktree_precondition_coverage.py` — new file.
- `tests/test_worktree_precondition_wiring.py` — new file.

**Specific exclusions touched:** no — `verify_worktree_isolation.py` was read but not modified; no gate other than `init` was touched; no `checklist_engine.py` change; no PreToolUse-hook mechanism built.

## Behavior changed
Yes. A Commander instantiated from this template can no longer `start` its `init` gate without `verify_worktree_isolation.py --here <repo-root>` passing first — previously nothing in the engine enforced this, only prose. A second maintained-list script now catches a future worktree-entering template that ships without this precondition wired.

## Map Impact
- **Structural anchors touched:** `skills/commander/templates/COMMANDER_SPINE.template.json:init` — added precondition `c0`, first in the array, riding the unchanged `scripts/checklist_engine.py:1635 start()` precondition mechanism (per the inbound Structural anchor — not modified).
- **Capabilities added/changed/affected:** Commander spine `init` gate now proves worktree isolation before any git operation (matches the inbound Capability anchor — moved from "should prove" to "does prove, mechanically").
- **Constraints/assumptions touched:** `constraint:only-COMMANDER_SPINE-worktree-entering` honored — the enumeration list in `verify_worktree_precondition_coverage.py` carries exactly the one entry named in the handoff (`COMMANDER_SPINE.template.json`, gate `init`); no second candidate found (see Out-of-scope observations).
- **Decision candidates / resolved decisions:** `decision:worktree-entering-membership` — implemented as specified (explicit maintained tuple, not a heuristic), with the module docstring naming Admiral/Commander/Explorer/Crew roles and why each is or isn't in the list. Its `@grade: guess ... settle:` experiment ("confirm the enumeration check's refusal-on-omission fires when a second worktree-entering spine ships") is *partially* settled now: `EnumerationDeliberateBreakage` proves the refusal fires on a stripped copy of the one existing entry; it does not yet prove refusal on a genuinely *new second* template, since none exists yet — that half of the settle experiment stays open until a second worktree-entering role ships.
- **Claims/evidence produced:** `claim:no-template-wires-isolation` re-confirmed post-change: `grep -rln verify_worktree_isolation skills/*/templates/*.json` → `skills/commander/templates/COMMANDER_SPINE.template.json` (exactly one match, as expected; it was empty before this change).
- **Trust limitations / drift found:** none — enumeration list, template wiring, and tests all agree with the single Commander-only worktree-entering fact stated in the handoff.

## Test mode
**Required:** `test-after` (wiring existing, already-tested rail scripts into the engine — but the two deliberate-breakage tests are the acceptance criteria themselves, not incidental coverage)
**Satisfied:** yes — both deliberate-breakage tests exist, pass on the fixed tree, and were independently proven to fail on the pre-fix state (see "TDD evidence" below for the exact method).

## Evidence

```bash
python -c "import json; json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json', encoding='utf-8'))"
```
**Result:** no output, exit 0 — valid JSON after the surgical edit.

```bash
python scripts/verify_worktree_precondition_coverage.py
```
```
worktree-precondition coverage OK: 1 worktree-entering template(s) checked
```
**Result:** pass, exit 0, states the count checked (1).

```bash
python -m pytest tests/test_worktree_precondition_wiring.py -q
```
```
..                                                                       [100%]
2 passed in 1.00s
```
**Result:** pass.

```bash
python -m pytest tests/ -q
```
```
........................................................................ [  4%]
... (elided — 1623 passed, 2 skipped, 549 subtests) ...
..............                                                           [100%]
1623 passed, 2 skipped, 549 subtests passed in 493.26s (0:08:13)
```
**Result:** pass, full suite green, no regressions.

```bash
grep -rn "verify_worktree_precondition_coverage" --include=*.py .
```
```
./tests/test_worktree_precondition_wiring.py:8:  1. `scripts/verify_worktree_precondition_coverage.py` (the enumeration
./tests/test_worktree_precondition_wiring.py:33:COVERAGE_SCRIPT = ROOT / "scripts" / "verify_worktree_precondition_coverage.py"
```
**Result:** 2 call sites found (both in the new test file — one docstring reference, one the `COVERAGE_SCRIPT` path constant the test invokes via `subprocess.run`), beyond the script's own `if __name__ == "__main__"` — satisfies "expect ≥1: the test file."

```bash
grep -rln verify_worktree_isolation skills/*/templates/*.json
```
```
skills/commander/templates/COMMANDER_SPINE.template.json
```
**Result:** one match, as expected (was empty before this change) — re-confirms `claim:no-template-wires-isolation`.

## TDD evidence, if required
Test-after mode, so no red-step-first TDD cycle — instead, the required "prove the deliberate-breakage tests genuinely fail without the fix" evidence, produced by **reverting the real template via `git stash`, not a synthetic before-state fixture**:

1. `git stash push --quiet -- skills/commander/templates/COMMANDER_SPINE.template.json` — reverted the file to its last-committed (pre-fix) state; `git diff --stat` on the file showed empty, confirming the mutation applied.
2. `python -m pytest tests/test_worktree_precondition_wiring.py -q` against that reverted state:
   ```
   F.                                                                       [100%]
   FAILED tests/test_worktree_precondition_wiring.py::EnumerationDeliberateBreakage::test_refuses_broken_copy_and_passes_real_fixed_tree
   AssertionError: real template unexpectedly missing the precondition before stripping
   1 failed, 1 passed in 1.00s
   ```
   `EnumerationDeliberateBreakage` failed red — its own sanity assertion (that the real template starts from a state that DOES carry the precondition, before the test strips it) caught the missing fix immediately, proving the test genuinely depends on `c0` being wired. `EngineDeliberateBreakage` still passed, because by design it builds its own in-memory checklist independent of the template file — it proves the engine mechanism generically (a wired command precondition blocks `start()`), not that this specific template wires it; that half is the enumeration test's job.
3. `git stash pop --quiet` — restored the fix; `git diff --stat` showed `3 insertions(+), 1 deletion(-)` confirming the restore applied; re-validated JSON with `python -c "import json; json.load(...)"` (exit 0).
4. Re-ran `python -m pytest tests/test_worktree_precondition_wiring.py -q` → `2 passed in 1.05s` — confirmed green again.
- Refactor while green: no refactor needed.

## Docs/contracts touched
- none — the change is additive (one precondition, two new files); no existing doc or contract needed updating.

## Assumptions
- The coverage script's `--root PATH` flag (already required by the handoff's CLI spec) was reused as the enumeration test's mechanism for pointing at a broken copy, rather than adding a second override flag — the handoff explicitly left this "implementer's call, document which." Documented here and in the test file's docstring.
- The Engine deliberate-breakage test builds its own throwaway git repo (`git init` + one empty commit in a `tempfile.TemporaryDirectory`) rather than reusing this worktree's `.git`, mirroring the existing pattern in `tests/test_verify_worktree_isolation.py`'s `IntegrationTests`/`GitFailureTests` — this satisfies "never against this worktree's own `.git` or the shared checkout" without needing any new fixture machinery.
- `<repo-root>` resolution was not re-implemented; the existing `resolve_spine()` in `scripts/init_work_area.py` already owns that token family and needed no changes (confirmed by reading it, not modifying it).

## Stop conditions hit
- none — no `checklist_engine.py` change was needed, no second worktree-entering template surfaced, both deliberate-breakage tests were provably made to fail without the fix using temp-only fixtures, and all required evidence was producible.

## Out-of-scope observations
- **Triage candidate:** none found. I looked for a second worktree-entering template candidate (per the handoff's instruction to name one, not add it) by reading `LAUNCH_ORDER.template.md`, `ADMIRAL_SPINE.template.json`, and `EXPLORER_SPINE.template.json` as pre-authorized — none of them are dispatched into an isolated worktree today, so the enumeration list correctly stays at one entry.
- The `decision:worktree-entering-membership` `settle:` experiment (see Map Impact above) is only half-exercised: it's proven for a stripped copy of the existing entry, not yet for a genuinely new second worktree-entering template, since none exists. Worth re-confirming with a live second entry whenever one ships (e.g. if a future role gets its own provisioned worktree).

## Workflow Feedback
- **Handoff gaps:** none — the handoff's exact `c0` JSON shape, the coverage-script contract, and the two deliberate-breakage test shapes were all specified precisely enough to implement without guessing. The one open implementer's-call point (`--root` vs. a script override flag) was flagged explicitly in the handoff itself as a documented choice, not a gap.
- **Context rediscovered:** had to read `tests/test_checklist_engine.py`'s `gate()`/`gated()`/`load_engine()` helpers and `tests/test_verify_worktree_isolation.py`'s `IntegrationTests`/`GitFailureTests` classes directly to find the exact idiom for (a) building a minimal in-memory gated checklist against the real engine module, and (b) constructing a throwaway git repo for a git-dependent test without touching the real one. The handoff's pointer ("see `tests/test_checklist_engine.py` for the existing pattern") was accurate and sufficient — this is a "had to look," not a "the handoff was missing it."
- **Instructions improvised around:** none — no skill/template/engine instruction failed to cover the situation.
- **What would have made this easier:** none — this handoff's precision (exact JSON shape for `c0`, named module-docstring rationale for the maintained list, two named deliberate-breakage constructions with explicit fixture-isolation rules) is close to the ideal shape for a bounded wiring task; nothing concrete comes to mind to improve it.

## Return status
`complete`
