APPROVE

# Review Result — gate `g4-review`

Work-id `w5-gates`, epic #418 wave 5. Reviewer survey:
`.agent-work/w5-gates/g4-review/review.json` (19 checks, 19 pass, 0 fail, consolidated
`APPROVE`). Engine session `g4-review-2026-08-08-rev1`.

Diff under review: `git diff 84d1e998 764a2728 -- tests/test_iterative_planning_doctrine.py`.
Every number below is one I produced myself. Where it agrees with the implementer's RESULT, it
agrees because both were run.

## Assigned Gate

`g4-review` — composition floor. The last review of the last gate of the last crew in the epic.

## Result

`APPROVE`

## The two required confirmations

### 1. The composition tests are NOT tautological — all six broken inputs reproduced

I built each broken input myself, at byte level, and watched the named selector go red. Discipline
applied to every row: the literal was asserted **unique** (`count == 1`) before mutating, the
mutation was asserted **present on disk in bytes** before any red was believed, the file was
restored from the saved original bytes, and the restore was verified with `read_bytes()` **and**
`git status` — never `read_text()`. Harness:
`.agent-work/w5-gates/g4-review/repro/red_repro.py`; per-case logs and
`red-repro-report.json` beside it.

| # | broken input | selector | my result |
|---|---|---|---|
| m1 | branch-deriving subshell in shipped `archive.c2b` replaced by a literal `<branch>` | `compose_spine` | **exit 1** — `AssertionError: {} != {'archive.c2b': ['<branch>']}` |
| m2 | ` -gt 0` → ` -ge 0` in the shipped template | `compose_spine` | **exit 1** — `AssertionError: 0 == 0 : no PR at all is not reachable` |
| m3 | `_is_installed_bundle` → `path.name.startswith("constellation-")` | `compose_verifier` | **exit 1, two SUBFAILED** (see below) |
| m4 | `if skills_root is not None:` → `if False:` | `compose_verifier` | **exit 1** — `AssertionError: 0 != 1 : --skills-root must make the same run resolvable` |
| m5 | stop branch disabled (`if decision == "stop":` → `if False:`) | `compose_terminal` | **exit 1** — `AssertionError: 0 != 1 : a verified stop must close prelaunch: REFUSED: only advance or replan may authorize NEXT_WAVE` |
| m6 | relaxation widened (`if decision == "stop":` → `if True:`) | `compose_terminal` | **exit 1** — `AssertionError: 0 == 0 : repair must not inherit the stop relaxation` |

All six mutations applied, all six restores byte-identical, `git status` clean on both mutated
paths after every case.

**The decoy row, verified specifically — it holds, and it is the sharpest evidence in the wave.**
Under the name-only revert the decoy leg returned:

```
AssertionError: 0 == 0 : name-only-decoy-inside-a-real-skills-root is not an installed bundle
```

Exit **0** from the **real installed bundle**, on a `constellation-`-named directory that carries no
`SKILL.md`, sitting inside the real skills root beside genuine bundles. That is **#501 reproduced
live against the artifact a user installs**, not in a repo-side fixture. The second polarity landed
in the same run: the `constellation-skills`-named checkout also went red, and it went red **for the
wrong reason** —

```
AssertionError: 'cannot locate an installed constellation skills root' not found in
'REFUSED: installed public verifier is missing: ...\programs\constellation-replan\scripts\verify_replan.py'
```

Both polarities of the g1 finding, caught by one mutation, exactly as claimed. The
`commander-worktree` leg correctly does **not** flip — a name test refuses it too — so **two** of
three subtests failing is the right expected shape, not a partial repro.

### 2. No owned fix silently depends on another crew's file

`scripts/verify_iterative_role_artifacts.py` imports only stdlib (`argparse`, `importlib.util`,
`json`, `re`, `sys`, `pathlib`). It does not import `scripts/checklist_engine.py` or
`scripts/install_constellation.py`, and it reads none of the handoff templates,
`docs/CREW_CONTEXT.md` or `docs/TREND_SNAPSHOT.md`. `COMMANDER_SPINE.template.json` is data.

I did not stop at reading imports — I tested the merge-order hazard directly. The only sibling
change to an out-of-bounds file is a **260-line addition to `scripts/install_constellation.py`**
carried by `epic-418/w5-readiness-458` and `epic-418/w5-gauge-477`, and that change is **already in
`main`**. Against `main`: `CORPUS_MARKER` is still `"CORPUS.json"`, and `install_skills`,
`select_skills`, `discover_skills` and `InterpreterResolution` all still carry the shapes the
composition fixture calls. **The merge does not break this branch.**

One latent coupling worth naming, not blocking: `verify_iterative_role_artifacts.py` **mirrors**
`install_constellation.CORPUS_MARKER` as its own literal with a comment saying so, and no test
asserts the two agree. Both copies currently agree, including on `main`, and the guard degrades
gracefully if they diverge because the sibling-bundle clause still identifies a real skills root.
Triage candidate `tc2`.

## Handoff compliance

The change does what the handoff asked. One new class `ComposedShippedArtifactTests` with three
composition tests over one fixture: the **real installer** (`install_constellation.install_skills`,
`dry_run=False`) lays down a real bundle, the **real `init_work_area.py` entrypoint** runs as a
subprocess against **that bundle's own** spine template with `--skill-dir` pointing at the bundle,
and the **bundle's own verifier** runs as a subprocess with `HOME`/`USERPROFILE` pointed at an empty
directory. Zero behavior introduced.

### Is the fixture real, or does it only look real? — real, proven by mutation

I did not settle this by reading the fixture. Mutating the **repo** copy of
`scripts/verify_iterative_role_artifacts.py` changed the behavior of the **bundle under test** in
four separate probes (m3–m6 all red). That can only happen if the installer really lays the file
down and the subprocess really runs the bundle's copy. Likewise, mutating
`skills/commander/templates/COMMANDER_SPINE.template.json` changed the **instantiated** spine (m1,
m2 red), proving the template under test is the bundle's copy of that source. And the empty `HOME`
is demonstrably in effect — the m4 refusal prints its own roots:

```
Roots tried (3): ...\wt; ...\projects\compose-verifier...\.claude\skills; ...\empty-home\.claude\skills
```

The developer's real `~/.claude/skills` cannot leak in and make a leg pass.

**One observation, not a defect.** `instantiate_bundle_spine` invokes `ROOT / "scripts" /
"init_work_area.py"` — the **repo's** copy — although the commander bundle also ships
`init_work_area.py`. The handoff's stated requirement is met (the **template** is the bundle's, and
`--skill-dir` is the bundle), and the installer copies the script with `shutil.copy2`, so the two
are byte-identical today. Pointing the subprocess at the bundle's copy would close the last leg that
still runs a repo-side script inside a composition test. Triage candidate `tc1`.

## Scope drift

None. `git diff --numstat 84d1e998 764a2728` lists exactly **one production path**:

```
353  15  tests/test_iterative_planning_doctrine.py
```

Everything else in the range is under `.agent-work/`. `scripts/verify_iterative_role_artifacts.py`,
`skills/commander/templates/COMMANDER_SPINE.template.json` and `scripts/init_work_area.py` are
**absent from the diff** — zero-line diffs, confirming every mutation was a probe. No out-of-bounds
path appears: no `checklist_engine.py`, no `test_checklist_engine.py`, no `install_constellation.py`,
no handoff templates, no `CREW_CONTEXT.md`, no `TREND_SNAPSHOT.md`, no `ADMIRAL_SPINE.template.json`.

`tests/test_iterative_planning_doctrine.py` is **unchanged between `764a2728` and HEAD `b47411cb`**,
so the reviewed ref is what the branch carries. The two
`.agent-work/epic-418-redux/transitions/close-to-w5/` files remain unstaged CRLF stat artifacts,
untouched.

## Evidence verdict

Every claimed measurement reproduced. Each command run bare or redirected, **never piped**; exit
codes captured with `echo "REAL_EXIT=$?"` after a redirect.

| command | exit | collection |
|---|---|---|
| `-k compose_spine` | **0** | **1 passed**, 35 deselected |
| `-k compose_verifier` | **0** | **1 passed / 3 subtests passed**, 35 deselected |
| `-k compose_terminal` | **0** | **1 passed**, 35 deselected |
| coupled suite (8 files) | **0** | **399 passed / 506 subtests passed**, 60.5s |
| full suite at HEAD | **0** | **1891 passed, 2 skipped, 872 subtests**, 474s |
| full suite at `aa2038d9` | **0** | **1867 passed, 2 skipped, 829 subtests**, 484s |
| closure check `verify_iterative_role_artifacts.py commander --work-id w5-gates --skills-root ...` | **0** | `iterative role artifact ok: commander (w5-gates)` |

**Passed, not skipped.** The class carries `skipUnless(ROLE_VERIFIER.is_file(), ...)`. That file
exists and pytest reports `passed`, not `skipped`, on all three selectors — so the collection counts
are live, not vacuous. Zero collected would have been a gate failure; none occurred.

### The full-suite delta, derived rather than accepted

I refused to take `1867` on trust. I cut a throwaway detached worktree at `aa2038d9`, ran the full
suite there myself, and removed the worktree afterward (`git worktree list` is back to its prior
set). **1867 passed / 2 skipped** at base, **1891 passed / 2 skipped** at HEAD: `1867 + 24 = 1891`,
with skips unchanged at 2 on both sides, **measured on both sides**.

The attribution I derived from the file contents at each gate commit, not from the report — an AST
count of `test_*` methods per class at every commit in `aa2038d9..HEAD`. The method is validated
because its count at `764a2728` is **36**, exactly pytest's `1 selected + 35 deselected`.

| commit | | total | delta |
|---|---|---|---|
| `aa2038d9` | base (pre-wave) | 12 | — |
| `6f48ece4` | g1 end | 24 | **+12** — `GuardLocationStructureTests` 4 + `GuardRuntimeTests` 8 |
| `4b8abc12` | g2 end | 27 | **+3** — `InstalledIterativeRoleRuntimeTests` 4→7 |
| `84d1e998` | g3 end | 33 | **+6** — `ArchiveReachabilityRuntimeTests` 6 |
| `764a2728` | g4 | 36 | **+3** — `ComposedShippedArtifactTests` 3 |

`12 + 3 + 6 + 3 = 24`; `12 + 24 = 36`. **Zero removed** — every pre-existing class holds its count or
grows across the whole range. Only 3 of the 24 belong to this gate, as the handoff says.

### One premise in the implementer RESULT is wrong — non-blocking, please correct it

The RESULT says: *"Only `tests/test_iterative_planning_doctrine.py` differs from `aa2038d9` outside
`.agent-work/`."* **That is false.** `git diff --numstat aa2038d9 HEAD -- . ':(exclude).agent-work'`
returns **three** paths:

```
143   22  scripts/verify_iterative_role_artifacts.py
  1    1  skills/commander/templates/COMMANDER_SPINE.template.json
1370   2  tests/test_iterative_planning_doctrine.py
```

The two extra paths are the wave's own g1–g3 production fixes, each already reviewed at its gate, and
neither adds or removes a collected test — so **the `+24` conclusion stands and nothing is hidden**.
The sentence reads as if written against `84d1e998` rather than `aa2038d9`. It is a transcription-level
error in a provenance-sensitive document, and it is exactly the kind of premise a later reader would
use to skip checking whether other files changed. Correct the sentence; it does not change the verdict.

### Selector hygiene — re-derived, and by identity rather than by count

All six reserved selectors measured at HEAD, each exactly its pre-g4 number:

| selector | tests | subtests |
|---|---|---|
| `guard_location` | 11 | 11 |
| `guard_mutation` | 1 | 6 |
| `stop_boundary` | 2 | — |
| `stop_mutation` | 1 | 8 |
| `archive_c2b` | 4 | 4 |
| `archive_mutation` | 2 | 11 |

Stronger than matching counts: I listed the **node IDs** each selector collects, and **not one belongs
to `ComposedShippedArtifactTests`**. Every match sits in `GuardLocationStructureTests`,
`GuardRuntimeTests`, `InstalledIterativeRoleRuntimeTests` or `ArchiveReachabilityRuntimeTests`. That
*proves* no new test leaked into an earlier gate's floor, rather than inferring it from an unchanged
total. The rename is complete: `-k compose_stop` collects **zero** — 36 deselected, `REAL_EXIT=5`
(redirected, not piped, so the 5 is real).

### The shared-shim refactor did not weaken g3

The 15 removed lines move the shim-writing code and nothing else. `GH_STUB_SOURCE`,
`GIT_STUB_SOURCE` and `MODELLED_FLAGS = ("--head", "--state", "--json", "--jq")` all sit **above the
first hunk** and appear in the diff only as the two `write_text` call sites being relocated verbatim.
The single behavioral difference is `mkdir(parents=True)` becoming `mkdir(parents=True,
exist_ok=True)`. g3's floors still collect and pass their exact counts (`archive_c2b` 4/4,
`archive_mutation` 2/11), and
`test_archive_mutation_the_stub_refuses_an_unmodelled_check_shape` — which carries the
`--repo someone/else` and `--limit 100` refusal legs — is still collected and green. The refactor in
fact **strengthens** the new class: `compose_spine` now runs the shipped check through the same
strict stub that refuses an unmodelled shape.

## No-op analysis

This run has been BLOCKed twice for checks that could not fail. I looked for a third and did not find
one.

- **The refusal legs assert the REASON, not a nonzero exit.** Each asserts
  `"cannot locate an installed constellation skills root"` **and** `"Roots tried"`. I measured that
  this is load-bearing rather than decorative: under m3 the source-checkout leg went red
  **specifically because the reason changed**, while its exit code was still nonzero. A leg asserting
  only `assertNotEqual(0, returncode)` would have passed there. That is direct evidence the guard the
  handoff worried about is working.
- **The seeding really is required and really happens.** `seed_commander_artifact` copies a valid
  `REPLAN_INPUT` before every leg, and the m4 output confirms the refusal reason is the skills-root
  refusal — not a missing-artifact refusal — so the guard is genuinely reached rather than
  short-circuited upstream.
- **`compose_spine`:** `command_checks` asserts at least 5 command checks collected (7 exist in the
  shipped template, so the scan is never over an empty set); `assertEqual(1, len(c2b))` raises rather
  than skipping if `archive.c2b` vanishes; and the two reachability legs are asserted to **differ**,
  so a check stuck on one answer cannot pass. m2 drove exactly that assertion red.
- **`compose_terminal`:** the live fixture is asserted to be a genuinely applicable `stop` before the
  run; the golden leg asserts the exact rendered **content** of both Markdown files, which a
  short-circuit cannot produce; the refusal leg asserts the exact reason **and** that neither file
  appeared.
- **`compose_verifier` accept leg:** asserts stderr carries no `note:`, so a bundle that resolved
  through the fallback path cannot read as a structural accept.
- **A silent install failure cannot pass.** `instantiate_bundle_spine` asserts `returncode == 0` and
  that `spine.json` was actually written; a missing `bundle_script` would fail the accept leg.
- **The docstring claims were verified, not trusted.** `CREW_CONTEXT.md` warns that docstrings are
  hand-authored and never checked against what runs, so I treated the `NO-OP CONDITIONS` prose as a
  claim and measured each guard by mutation. Every claimed guard went red as described.

## Code/doc quality

Meets the inherited rules. The `ORCHESTRATOR_CONTEXT.md` constraint — a mechanism or workflow
behavior change owes targeted automated tests **plus** the relevant broader suite, both commands
named — is satisfied, and this is the gate where the broader suite is named: three targeted
selectors, the eight-file coupled suite, and the full suite, all named and all green, with no
deliberately-red suite left standing across gates. `CREW_CONTEXT.md` "Writing Files On Windows": every
new `write_text` passes `encoding="utf-8", newline="\n"` explicitly, and read-backs pass
`encoding="utf-8"`. `python` used throughout, never `py`.

**Fowler refactoring pass** — `.agent-work/w5-gates/g4-review/fowler-pass.json`;
`scripts/verify_fowler_pass.py` exits **0** (smells=12, flagged=`['long-parameter-list',
'divergent-change']`, overridden=`['long-method', 'feature-envy', 'data-clumps',
'comments-as-deodorant']`). Two flags, both observations:

- **long-parameter-list** — `seed_boundary(self, boundary_id, launch_id, source, result, decision)`
  takes five parameters, positional at both call sites, which hides the load-bearing fact that
  `launch_id` is `None` in both cases behind argument order. Keyword arguments would fix it without
  changing behavior. Not fixed here: the gate imperative forbids introducing behavior.
- **divergent-change** — `tests/test_iterative_planning_doctrine.py` is now ~1838 lines and eight
  classes changing for four unrelated reasons. The six hand-kept-disjoint selector tokens are
  currently doing the job module boundaries would do. Out of scope here; raised for a later wave.

The four overrides each carry the specific standard and why it subordinates the smell. The
`long-method` override matters most: the length of `compose_verifier` is what **buys** the
non-tautology, because the `--skills-root` leg is asserted only as a **difference** between the same
script run twice with the same argv. Splitting it would convert a measured difference into two
absolute assertions, either of which could pass on a stuck answer.

## Map impact verdict

Orientation is `DEGRADED-NO-MAP`; anchors are named by path with no `struct:`/`decision:` ids.

- **Evidence supports claimed change:** Yes. The structural anchor (the three owned files plus the
  doctrine test file as one composition surface) is exercised end to end, and all three capability
  anchors — role-artifact verification, boundary transition verification, spine instantiation and
  archive closure — are covered by one fixture, each shown to fail on a stated broken input.
- **Constraints not violated:** The `ORCHESTRATOR_CONTEXT.md` constraint is met as recorded above.
- **Notes match the diff:** Substantially yes, with the one false premise named under *Evidence
  verdict* (three paths differ from `aa2038d9`, not one).
- **Decision candidates surfaced:** The decision anchor — whether the run's own execute closure check
  counts as evidence — is discharged. I re-ran it myself: exit 0, with the skills root named
  explicitly so the verdict is not silently decided by machine state. No decision requiring authority
  the implementer lacked was left unsurfaced.
- **Durable context routed:** Yes — four triage candidates recorded on the survey (`tc1`–`tc4`),
  including one routed to Cartographer.

The RESULT carries no section **labelled** `Map Impact`. For a zero-behavior, test-only diff under
degraded orientation that is not a blocker, and the handoff's anchors are addressed in substance —
but it is worth naming so the next gate does not read the omission as precedent.

## Reconciliation check

Nothing requiring reconciliation. The map-confidence flag is answered in the intended way: with no map
asserting how templates, top-level scripts and installed bundles relate, composition is established by
running the real artifacts end to end rather than by trusting structure. That is exactly what this
gate now demonstrates, and I verified it by mutation rather than by inspection.

## Blockers

**None.** I looked hard for one — both g2 and g3 blocked and were repaired, and the handoff is right
that a BLOCK with proof is this gate working. Every stated BLOCK trigger was tested and none fired:
the diff is accessible; all six broken inputs go red; no leg is a no-op; the fixture demonstrably runs
the shipped artifacts; the full-suite delta reconciles on both sides with measured numbers; no
selector collision exists; the shared shim did not weaken g3's whitelist; and no owned fix depends on
another crew's file.

## Out-of-scope observations — floats to the Commander

1. **Correct the RESULT's false premise** (Commander action, this file): *"Only
   `tests/test_iterative_planning_doctrine.py` differs from `aa2038d9` outside `.agent-work/`"* is
   wrong — three paths differ. The conclusion it supports is unaffected. This is the one place the
   transcribed document does not survive independent checking, and given the RESULT's provenance note
   it should be fixed rather than left for a PR reader to trip over.
2. **`tc1` — the last repo-side script inside a composition test.** `instantiate_bundle_spine` runs the
   repo's `init_work_area.py`, not the bundle's, although the bundle ships it. Byte-identical today.
3. **`tc2` — the mirrored `CORPUS_MARKER`.** Duplicated literal across an owned file and crew 2's file,
   with no test asserting they agree. Currently agreeing, degrades gracefully. A one-line equality
   test removes the silent-drift risk.
4. **`tc3` — the doctrine test file is a divergent-change file.** ~1838 lines, eight classes, four
   reasons to change. Candidate for a split in a later wave.
5. **`tc4` — durable context for Cartographer.** The template / top-level-script / installed-bundle
   seam this gate exercises has no map id, and the only record that the three wave-5 fixes compose
   across it now lives inside one test class.

**Nothing went red outside the ownership scope.** No float is a defect requiring repair before merge.

### Tree state on exit

Clean of production changes. `git status` shows no `tests/`, `scripts/` or `skills/` modification.
Both mutated paths restored byte-identical and verified with `read_bytes()` plus `git status` after
every one of the six probes. The two
`.agent-work/epic-418-redux/transitions/close-to-w5/` CRLF stat artifacts are untouched and unstaged,
as instructed. The throwaway base-measurement worktree was removed and pruned.

One thing for the Commander to expect: driving the survey modified the tracked engine sidecars under
`.agent-work/w5-gates/w5-gates/mechanical/r*.json` — the same files g3's review created. That is the
engine's own bookkeeping, not an edit of mine, and it belongs in this gate's commit. My scratch lives
under `.agent-work/w5-gates/g4-review/`.

## Workflow Feedback

- **Handoff gaps.** The broken-input table's decoy row says **"RED twice"** without saying *which two
  of the three subtests*. The `commander-worktree` leg legitimately does **not** flip under a name
  revert — a name test refuses it too — so a reviewer who expects three reds will think the repro is
  partial and may go looking for a defect that is not there. State the expected shape: *2 of 3
  subtests, and here is why the third does not move.* This is the mirror of the g2 and g3 blocks: an
  expected-count claim without the reasoning is a trap in both directions.
- **Context rediscovered.** The handoff names the six reserved selectors but gives no way to check the
  claim except re-running them and comparing totals. Comparing totals is the **weak** form — it cannot
  distinguish "no new test matched" from "one new test matched and one old test was renamed". I had to
  work out that `--collect-only` node-ID listing settles it by identity. Handoffs asserting selector
  hygiene should ask for node IDs, not counts.
- **Instructions improvised around.** Two.
  (a) The handoff asks me to "derive the attribution yourself" against a base of **1867**, but 1867 is
  itself a claim, and nothing in the handoff says how to measure it without a second checkout. I cut a
  throwaway detached worktree at `aa2038d9`, ran the suite there, and removed it — ~8 minutes, and it
  turned the reconciliation from arithmetic into a measurement on both sides. If that is the expected
  route it should be named, because it sits in tension with "leave the tree as you found it" and a
  reviewer may reasonably decide not to touch `git worktree` at all.
  (b) The `REVIEW_SURVEY` template's `r6-fowler` postcondition ships a `<fowler-pass-record-path>`
  placeholder to be resolved *at instantiation*, which is correct — but the template also ships
  `python scripts/verify_fowler_pass.py` as a **repo-relative** command, and the engine's command
  checks do not run from the worktree root in a way I could rely on. I absolutized both halves at
  instantiation. Worth making the template's own script path a placeholder too, so the two
  substitutions are visibly one job.
- **What would have made this easier.** The implementer's own feedback item 1 is right and I hit the
  same hazard from the other side, so I will second it concretely: **handoffs should say to verify
  mutation restores with `read_bytes()`, and to run `git status` on the mutated path after every
  probe, not once at the end.** Per-probe is the part that matters — a single end-of-run `git status`
  cannot tell you *which* of six probes failed to restore. I built that into my harness as a hard
  `SystemExit` and it is the reason I can attest all six restores rather than just the final tree.
  Separately: `references/windows.md` §4 is still wrong on this box and has now cost four crews. It
  should be fixed or deleted, not warned around in every handoff.

## Return status

`complete`
