# Implementer Result — gate `g4-implement`

Crew: `constellation/w5-gates/g4/implementer/attempt-1`. Work-id `w5-gates`, epic #418 wave 5.

## Status

**COMPLETE.**

**Provenance note, stated plainly because it matters for how much this document is worth.** The
implementer completed all eight plan items' worth of measurement but hit a **hard context trip at its
own plan item m6** and stopped rather than push through, recording a refresh-request
(`e-m6-closure-check-1`, `seam=m6-closure-check`, `why_ref=w-6`). Its two unreached items were m6
(run the closure check — one command) and m7 (write this file). It returned everything below in its
final report and correctly declined to fabricate the attestation it could not make.

**This file was therefore transcribed by the Commander from the implementer's returned report, and
the Commander ran m6 itself.** Every measurement in the "What the implementer measured" section is
the implementer's, reported as its own. The "Commander's independent verification" section at the end
is the Commander's own re-measurement, run before this file was written. Nothing here is inferred
from the other; where they agree, they agree because both were run.

Its returned status was `BLOCKED` **on the trip, not on the work** — the distinction the honest-null
clause exists to preserve. With m6 run and m7 written, there is no unresolved blocker, and c1 is met
on content.

## What the implementer built

One new test class, `ComposedShippedArtifactTests`, in `tests/test_iterative_planning_doctrine.py`.

What makes these composition tests rather than restatements: a single fixture in which the **real
installer** lays down a real bundle, the **real `init_work_area.py` entrypoint** (as a subprocess,
not an in-process `resolve_spine` call) instantiates *that bundle's own* spine template, and the
**bundle's own verifier** runs as a subprocess with `HOME`/`USERPROFILE` pointed at an empty
directory. g1, g2 and g3 each measured its own fix repo-side or in its own fixture; **none of them
touched the artifact a user actually installs.**

The class name and every method name avoid all six reserved selector tokens (`guard_location`,
`guard_mutation`, `archive_c`, `archive_mutation`, `stop_boundary`, `stop_mutation`), so no test
added here can satisfy an earlier gate's floor.

## What the implementer measured

Every composition test was shown to go **red on a stated broken input, actually run broken** — the
discipline this gate exists to enforce.

### Test 1 — `test_compose_spine_instantiates_and_ships_a_runnable_reachability_check`

Selector `-k compose_spine`, collects 1.

| broken input | result |
|---|---|
| pre-#439 literal `<branch>` reintroduced into the shipped template | **RED** — `AssertionError: {} != {'archive.c2b': ['<branch>']}` |
| `-gt 0` narrowed to `-ge 0`, so the exit code stops carrying the verdict | **RED** — `AssertionError: 0 == 0 : no PR at all is not reachable` |

Mutation asserted present on disk (`old not in text and new in text`) before believing the red;
target asserted unique (`count == 1`) before mutating; template restored byte-identical.

**No-op conditions and their guards:** (a) the leftover-token scan finding nothing to scan — guarded
by asserting at least 5 command checks were collected; (b) `archive.c2b` vanishing from the spine —
guarded by `assertEqual(1, len(c2b))`, which raises rather than skipping; (c) the two reachability
legs agreeing — guarded by asserting the two exit codes **differ**, so a check stuck on one answer
cannot pass.

### Test 2 — `test_compose_verifier_locates_itself_by_structure_across_the_real_locations`

Selector `-k compose_verifier`, collects 1 test / 3 subtests. Five legs.

| broken input | result |
|---|---|
| `_is_installed_bundle` reverted to `path.name.startswith("constellation-")` | **RED twice** |
| `--skills-root` ignored (`if skills_root is not None:` → `if False:`) | **RED** — `AssertionError: 0 != 1 : --skills-root must make the same run resolvable` |

**The sharpest single piece of evidence in this gate:** under the name-only revert, the decoy leg
returned **exit 0** — `AssertionError: 0 == 0 : name-only-decoy-inside-a-real-skills-root is not an
installed bundle`. That is **#501 reproduced live**, against the installed artifact. The
`constellation-skills`-named checkout leg also went red, refusing for the wrong reason — both
polarities of the g1 finding, caught by one mutation.

**No-op conditions and their guards, per leg:** (1) every leg seeds a valid `REPLAN_INPUT` first,
because `verify_commander` reads the artifact *before* resolving the skills root — an unseeded work
area refuses on the missing artifact and never reaches the guard, which is precisely how a refusal
test becomes a no-op; (2) the refusal legs therefore assert the refusal **reason** and `Roots tried`,
not merely a nonzero exit; (3) the `--skills-root` leg would pass on any code that resolves any root,
so it is asserted only as a **difference** against the same script with the same argv refusing
without the flag; (4) the accept leg asserts stderr carries no `note:`, so a bundle that resolved via
fallback cannot read as a structural accept.

### Test 3 — `test_compose_terminal_transition_closes_prelaunch_from_the_installed_bundle`

Selector `-k compose_terminal`, collects 1. Two legs.

| broken input | result |
|---|---|
| pre-#506 conflation restored (stop branch deleted) | **RED** — `AssertionError: 0 != 1 : a verified stop must close prelaunch: REFUSED: only advance or replan may authorize NEXT_WAVE` |
| relaxation widened to *any* null `launch_id` | **RED** — `AssertionError: 0 == 0 : repair must not inherit the stop relaxation` (repair wrongly accepted) |

**No-op conditions and their guards:** (1) the live fixture not really being an applicable stop —
asserted before the run; (2) an early refusal writing no Markdown at all — so the golden leg asserts
the exact rendered **content** of both files rather than a zero exit, which a short-circuit cannot
produce; (3) the refusal leg being rejected upstream at G2 rather than at the authorization clause —
guarded by asserting the exact refusal reason and that neither Markdown file appeared.

**Honest scope note the implementer volunteered:** test 3 composes fix A with fix B's *resolution
path*, but it would **not** detect a fix-B regression on its own, because the bundle is named
`constellation-commander` and a name test still accepts it. Test 2 is where that regression is
caught. This is the right kind of note — it says what the test does not prove.

### Suites

- **Coupled suite: 399 passed / 506 subtests, exit 0** (52s). Baseline 396/503, so +3 tests and
  +3 subtests, all this gate's.
- **Full suite: 1891 passed, 2 skipped, exit 0**, 497s — well inside the 16-minute budget. Run bare,
  redirected to a file, never piped.
- **Delta +24 against the 1867 base, accounted test by test.** Three production paths differ from
  `aa2038d9` outside `.agent-work/` — `scripts/verify_iterative_role_artifacts.py`,
  `skills/commander/templates/COMMANDER_SPINE.template.json` and
  `tests/test_iterative_planning_doctrine.py` — but only the last carries tests, so the whole +24 is
  accounted for there. (Corrected by the Commander at g4-review. The original sentence claimed a
  single differing path, which holds against the g4 baseline `84d1e998` but not against the wave
  fork point `aa2038d9`. Found by the g4 reviewer; re-derived by the Commander with
  `git diff --numstat aa2038d9 764a2728 -- . ':(exclude).agent-work/**'`. The delta conclusion is
  unaffected.)
  Collection on that file: **12 at base, 36 now, 0 removed.** Attribution: 12 guard (g1 — 4
  `GuardLocationStructureTests` + 8 `GuardRuntimeTests`), 3 stop (g2), 6 archive (g3), 3 composition
  (g4). 1867 + 24 = 1891 exactly; skips unchanged at 2. **Worth flagging: 1867 is the pre-wave
  baseline, so 21 of the 24 belong to g1–g3, not to this gate.**
- The known `test_context_manifest` interaction did **not** fire — its targets are
  `checklist_engine.py`, `agent_work_root.py`, `COMMANDER_SPINE.template.json` and `.gitattributes`,
  none of which is dirty in the final tree.

### Files touched

```
353  15  tests/test_iterative_planning_doctrine.py
```

That is the whole production diff. `scripts/verify_iterative_role_artifacts.py`,
`skills/commander/templates/COMMANDER_SPINE.template.json` and `scripts/init_work_area.py` are all
**zero-line diffs** — every mutation above was a probe, restored. **This gate introduced no
behavior**, as its imperative requires.

The 15 removed lines are one refactor: the `gh`/`git` stub-shim fixture was extracted from
`ArchiveReachabilityRuntimeTests.setUpClass` into a module-level `write_offline_stubs()` now shared by
both classes — so a check shape one suite proves unmodelled cannot be silently answered in the other.
That is a direct hardening of the g3 BLOCK, applied one level up.

`.agent-work/epic-418-redux/transitions/**` untouched and unstaged, as instructed.

### Floats

**None.** Nothing went red outside the ownership scope; the full suite was green end to end. Nothing
needed a waiver.

## Commander's independent verification

Run by the Commander before writing this file, at the same tree:

| check | result |
|---|---|
| production `git diff --numstat` | `353 15 tests/test_iterative_planning_doctrine.py` — the three other owned files are zero-diff, confirmed |
| `-k compose_spine` | exit 0, **1** collected |
| `-k compose_verifier` | exit 0, **1** test / **3** subtests |
| `-k compose_terminal` | exit 0, **1** collected |
| **no selector collision** | all six reserved floors re-run and each collects **exactly** its pre-g4 count: `guard_location` 11/11 subtests, `guard_mutation` 1/6, `stop_boundary` 2, `stop_mutation` 1/8, `archive_c2b` 4/4, `archive_mutation` 2/11 — so nothing added here leaked into an earlier gate's floor |
| **the run's own closure check** (m6) | `python scripts/verify_iterative_role_artifacts.py commander --work-id w5-gates --skills-root C:/Users/fredc/.claude/skills` → `iterative role artifact ok: commander (w5-gates)`, **exit 0** |

**That last row is this run's finding 2 discharged against the live run.** Before fix B, this run's
own spine could not close `execute` from this worktree — the check refused on the guard. It now runs
for real, with the skills root named explicitly so the verdict is not silently decided by whatever
happens to be installed on this machine.

The full suite is not re-run here; it is `g4-integrate`'s c1 and the Commander runs it there.

## Workflow feedback (the implementer's, carried up verbatim in substance)

1. **A CRLF trap that fact 6 of the handoff does not cover, and it bit this crew.**
   `Path.read_text()` plus `write_text(..., newline="")` silently converts a CRLF file to LF, and
   verifying the restore with `read_text() == read_text()` **cannot detect it** — universal-newline
   translation normalizes both sides. The probe printed `RESTORED IDENTICAL: True` while the file's
   bytes had changed; only `git status` caught it, as a zero-line diff — the same stat artifact as
   the transitions files. Restored with `git checkout --`.
   **Recommendation: handoffs should say verify mutation restores with `read_bytes()`, never
   `read_text()`.** The existing warning covers "the mutation didn't apply"; this is its mirror image,
   "the restore didn't restore", and it is the more dangerous of the two because it leaves a modified
   artifact behind after a green run.
2. **`references/windows.md` §4 is still wrong on this box.** Third crew to hit it. It should be
   fixed or deleted rather than warned around in every handoff.
3. The implementer's own plan named a selector `-k compose_stop` that collected **zero**, and the
   engine correctly refused the advance; the method is named `test_compose_terminal_...` precisely to
   avoid the g2 collision. Corrected through `amend --delta` (`retext-check`), not by hand.
   **Recommendation for handoffs: state your selector AND check it collects more than zero before you
   write the plan item.**
4. The context trip fired at item 7 of 8. The plan was one item finer than it needed to be — the
   three composition tests share one fixture and could have been a single gate. A handoff for a
   multi-test gate could say so.

## Triage candidates raised

None new from this gate. The three deferrals routed at `g4-integrate` are unchanged.
