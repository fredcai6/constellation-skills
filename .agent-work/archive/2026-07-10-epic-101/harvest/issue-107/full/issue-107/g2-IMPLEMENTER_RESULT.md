# Implementation Result — g2

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
g2 — delegated entry skill + install wiring + index + tests + admiral description line.

## Completed slice
Complete and green. The new `constellation-commander-delegated` entry skill is created, wired into install/index/admiral, covered by two new falsifiable per-skill tests, and the full suite is green. One handoff defect surfaced mid-run (a verbatim SKILL.md sentence collided with a pre-existing single-source-doctrine guard); I raised it as a blocker, the Commander adjudicated a pointer-not-paste rework, and I applied exactly that.

Done and verified:
- Created `skills/commander-delegated/SKILL.md` (frontmatter + body from the handoff; verbatim except the one Commander-directed rework sentence below).
- Added `"commander-delegated": _GLOBAL_ORCHESTRATOR,` to `SKILL_REFERENCE_BUNDLES` (NOT to `SKILL_SCRIPT_BUNDLES` — honored). No source `templates/`, `scripts/`, or `references/` dir created.
- Added the `## Constellation Commander (delegated)` entry to `SKILL_INDEX.md`, verbatim, immediately after the Commander entry.
- Replaced ONLY the `description:` line in `skills/admiral/SKILL.md`.
- Added `constellation-commander-delegated` to `SKILL_NAMES` and two new falsifiable per-skill test methods.
- Applied the Commander's adjudicated rework to the delegated SKILL.md's "Your principal" third paragraph (details under Assumptions). Did NOT amend the pre-existing residual-guard test.

Final suite: `py -m pytest tests/ -q` = **446 passed, 2 skipped, 143 subtests passed; 0 failed**.

## Scope
**Files changed (my 5 deliverable paths):**
- `skills/commander-delegated/SKILL.md` (NEW, untracked)
- `scripts/install_constellation.py` (one line added to `SKILL_REFERENCE_BUNDLES`)
- `SKILL_INDEX.md` (one entry added)
- `tests/test_install_constellation.py` (`SKILL_NAMES` + 2 new test methods; existing residual test NOT touched)
- `skills/admiral/SKILL.md` (description line only)

**Pre-existing (NOT mine, did not touch):** `skills/commander/SKILL.md` (M) and `skills/commander/references/` (??) are g1's uncommitted worktree state ("g1 already landed it"). I made zero edits under `skills/commander/**`.

**Specific exclusions touched:** no — `SKILL_SCRIPT_BUNDLES` untouched; no delegated source templates/scripts/references dirs; commander/interrogator/docent/_shared/ROADMAP untouched; admiral limited to the description line; the existing residual-guard test untouched.

## Behavior changed
Yes — `constellation-commander-delegated` is now a discoverable, installable skill carrying the `_GLOBAL_ORCHESTRATOR` reference bucket; admiral's and the delegated skill's descriptions now name each other as the confusable-pair disambiguator; the delegated skill reaches commander's core and delegate-not-replacement doctrine by prose pointer (no token).

## Map Impact
- **Structural anchors touched:** `skills/commander-delegated/SKILL.md` (new leaf); `scripts/install_constellation.py::SKILL_REFERENCE_BUNDLES` (+1 key); `SKILL_INDEX.md` (+1 entry); `tests/test_install_constellation.py::SKILL_NAMES` (+1) + 2 new tests; `skills/admiral/SKILL.md` description line.
- **Capabilities added/changed:** skill-install/bundle-composition now composes a 15th skill; skill-selection surface gains the commander-delegated ↔ admiral confusable-pair cross-reference (both directions).
- **Constraints/assumptions touched:** honored — `commander-core.md` does NOT match the `global-*.md` glob; cross-skill reach is by prose pointer, no `<…-skill-dir>` token; the issue-102 move-8 single-source residual guard stays intact (delegate-not-replacement now referenced, not re-pasted); green-at-boundary achieved.
- **Decision candidates / resolved decisions:** resolved by Commander — inline doctrine that trips the move-8 residual guard is expressed by pointer (hyphenated `delegate-not-replacement` + `see references/global-everyone.md`), matching how `commander-core.md` already handles it; a test carve-out was explicitly rejected as it would reintroduce a retired inline signature.
- **Claims/evidence produced:** delegated skill installs with the orchestrator bucket (proven); prose pointer `references/commander-core.md` present + a real installed commander core exists for it (proven); both new tests proven falsifiable; full suite green.
- **Trust limitations / drift found:** none outstanding.

## Test mode
**Required:** test-after (install plumbing; wiring + tests co-land).
**Satisfied:** yes — new per-skill tests written, pass, and proven falsifiable; the full suite is green; the pre-existing residual guard remains green and intact.

## Evidence

### Full suite tail (green)
```bash
$ py -m pytest tests/ -q
......................................................... [ 45%]
........................................................................ [ 61%]
........................................................................ [ 77%]
.............................................................................s........s [ 96%]
...............                                                          [100%]
446 passed, 2 skipped, 143 subtests passed in 14.90s
```

### New-tests-only run (both pass)
```bash
$ py -m pytest tests/test_install_constellation.py -q -k "commander_delegated"
..                                                                   [100%]
2 passed, 38 deselected, 4 subtests passed in 0.55s
```

### Pre-existing residual guard still green + intact
```bash
$ py -m pytest tests/test_install_constellation.py -q -k "residual"
. [100%]
1 passed, 39 deselected, 105 subtests passed in 0.49s
```

### New test method source
```python
def test_commander_delegated_installs_with_orchestrator_bucket(self):
    # installs commander-delegated to a temp dest; asserts dir + SKILL.md exist
    # and references/ carries global-everyone.md, global-orchestrator.md,
    # design-it-twice-brief.md, windows.md (the _GLOBAL_ORCHESTRATOR bucket).

def test_commander_delegated_points_at_installed_commander_core(self):
    # (a) source delegated SKILL.md contains literal "references/commander-core.md";
    # (b) a full install of commander-delegated + commander yields an existing
    #     constellation-commander/references/commander-core.md (existence + path-literal,
    #     NOT behavioral resolution).
```

### Falsification note (tests bite)
- Deleting the `"commander-delegated": _GLOBAL_ORCHESTRATOR,` line from `install_constellation.py` reds `test_commander_delegated_installs_with_orchestrator_bucket` (4 subfails: global-everyone/global-orchestrator/design-it-twice-brief/windows all missing). Verified live during the block: `4 failed, 1 passed`.
- Changing the pointer string `references/commander-core.md` -> `references/BROKEN-core.md` in the delegated SKILL.md reds `test_commander_delegated_points_at_installed_commander_core` at the literal-string assert. Verified live: `1 failed`.
- Both restored; both green again.

### git status --porcelain
```
 M SKILL_INDEX.md
 M scripts/install_constellation.py
 M skills/admiral/SKILL.md
 M skills/commander/SKILL.md          <- PRE-EXISTING g1 state, NOT touched by me
 M tests/test_install_constellation.py
?? skills/commander-delegated/         <- my new skill (untracked until staged)
?? skills/commander/references/        <- PRE-EXISTING g1 state, NOT touched by me
```
Deliverable-path ignore check: all 5 of my paths return `git check-ignore` exit 1 (NOT ignored). New files show untracked as expected — the Commander archives; I did not commit.

**Result:** pass — all wiring + new tests + full suite green.

## TDD evidence, if required
Not TDD (test-after). New tests observed passing and independently proven falsifiable (above).

## Docs/contracts touched
- `SKILL_INDEX.md` (skill-selection surface entry) — the one doc in scope.

## Assumptions
- `M skills/commander/SKILL.md` + `?? skills/commander/references/` are g1's uncommitted worktree changes (handoff: "g1 already landed it"); I treated `skills/commander/**` as frozen and made no edits there. commander-core.md was already present when I started.
- **Commander-directed rework (supersedes paste-verbatim for one sentence only):** the delegated SKILL.md "Your principal" third paragraph now ends "…via your return/stop shape. Asking up is always sanctioned, never a failure — this is inherited delegate-not-replacement doctrine (see `references/global-everyone.md`)." The hyphenated `delegate-not-replacement` + pointer keeps the issue-102 move-8 residual guard green while preserving the delegate≠replacement intent by reference. This was an explicit Commander adjudication, not my improvisation.
- The m1-wire engine command-check needed `sys.modules[spec.name]=m` before `exec_module` (Python 3.14 dataclass import quirk the test file's `load_module` already handles) — a harness detail of my own check only; the real installer/tests are unaffected.

## Stop conditions hit
One, mid-run, resolved: the paste-verbatim SKILL.md sentence "A delegate is not a replacement" collided with the pre-existing issue-102 move-8 residual-scan guard ("cannot make the suite green without touching a fenced test" + "exact-specified text does not fit the mechanism"). I did NOT force-fit: I blocked, bubbled to the Commander, and the Commander adjudicated a pointer-not-paste rework (rejecting a test carve-out because it would reintroduce a retired inline signature). Applied that exact fix; no stop condition remains open.

Engine-state note: the engine deliberately treats a `blocked` gate as a parent-adjudicated terminal state with no self-unblock verb (`reopen` requires `complete`, `start` refuses `blocked`; blocked/skipped gates are not churned). The m2-tests gate therefore remains `blocked` in the plan, with an attached `resolution` evidence item (`e-m2-tests-2`) recording the Commander verdict, the applied fix, the green suite (0 failed), and that the residual guard stays intact. The underlying close criterion is met and evidenced; the residual `blocked` label reflects the escalate-then-adjudicate path, not open work.

## Out-of-scope observations
- The collision was a handoff defect (verbatim text re-pasted single-sourced doctrine inline). It is now resolved by pointer, matching the `commander-core.md` precedent. No further out-of-scope work; only this one guard ever blocked the boundary, and it is green.

## Workflow Feedback
Mandatory section — real friction this run:
- **Handoff gaps:** The handoff's "must not leave any test red" + the paste-verbatim SKILL.md body were in direct, undetected conflict with the repo's pre-existing issue-102 move-8 residual test, and the Allowed-Scope test-file grant ("SKILL_NAMES + new methods") gave no in-scope path to green. Root cause: the verbatim body re-pasted a single-sourced doctrine signature. The launch order should have authored that paragraph in pointer form from the start (hyphenated `delegate-not-replacement` + `see references/global-everyone.md`) so it passes the guard — exactly the fix the Commander later directed.
- **Context rediscovered:** That `skills/commander/**` shows dirty (g1 uncommitted) in this worktree — the handoff says "g1 already landed it" but not that it is uncommitted here, so the `git status` deliverable-path check needed manual mine-vs-g1 disambiguation.
- **Instructions improvised around:** (1) The IMPLEMENTER_PLAN command-check idiom for loading the installer needed `sys.modules[spec.name]=m` (Py 3.14 dataclass quirk) not mentioned in the template; the repo's own `load_module` helper already does this, so I mirrored it. (2) The engine has no verb to move a `blocked` gate forward after a parent adjudicates in the same session; I recorded the resolution as attached evidence instead. A `resolve`/`unblock` verb, or explicit guidance that a parent-adjudicated blocked gate stays blocked-with-evidence, would remove the ambiguity.
- **What would have made this easier:** Author single-sourced doctrine references in handoff-verbatim SKILL bodies as pointers, not re-pastes, and dry-run the proposed body against the residual-guard test during handoff authoring to catch the collision before dispatch.

## Return status
complete

---

## COMMANDER REWORK RECONCILIATION (2026-07-10)

The crew was returned for the scoped reword (Commander adjudication: reword to a single-source pointer, NOT a test carve-out — a carve-out would reintroduce a retired inline signature the launch order forbids). The crew applied the edit to `skills/commander-delegated/SKILL.md` (final binding sentence now: "Asking up is always sanctioned, never a failure — this is inherited delegate-not-replacement doctrine (see `references/global-everyone.md`)") but idled before rewriting this result document. Per the idle-crew-at-integrate rule, the Commander judges from the completed artifact (the diff) + independent world-verification:

- `grep -c "delegate is not a replacement" skills/commander-delegated/SKILL.md` → 0 (retired signature gone)
- `grep -c "delegate-not-replacement" skills/commander-delegated/SKILL.md` → 1 (pointer form present)
- `py -m pytest tests/ -q` → **446 passed, 2 skipped, 143 subtests passed** (Commander-run, this tree)
- `py -m pytest tests/test_install_constellation.py -q -k commander_delegated` → 2 passed, 4 subtests

**Return status: COMPLETE.** The move-8 residual guard is preserved (not amended); all g2 wiring stands; the boundary is green.

---

## CREW ADDENDUM (post-reconciliation)

The crew did NOT idle silently — this run completed the reword, re-ran the suite green, recorded the resolution against the engine's `blocked` m2-tests gate as evidence `e-m2-tests-2`, and rewrote this result to its final complete form above. The Commander's independent verification and this crew's evidence agree: green boundary, guard intact, return status complete.
