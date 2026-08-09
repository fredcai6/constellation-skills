# Implementation Result

## Assigned gate
`g1-implement` — Location guard (fix B, issues #501 + #468), work-id `w5-gates`.

## Completed slice
`_installed_skills_root()` now decides "where am I running from" by **structure**, not by directory
name, and takes an explicit `--skills-root` override. Both polarities of the defect are fixed: the
main checkout is no longer wrongly accepted, and a Commander worktree is no longer wrongly refused.

Engine plan driven to done: `.agent-work/w5-gates/g1-implement-IMPLEMENTER_PLAN.json`
(m0-context → m1-predicate → m2-resolution → m3-mutation → m4-suite → m5-result).

## Scope
**Files changed:**
- `scripts/verify_iterative_role_artifacts.py` (+99/-31 region)
- `tests/test_iterative_planning_doctrine.py` (+366)

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `tests/test_checklist_engine.py`,
`scripts/install_constellation.py`, handoff templates, `docs/`, hooks and `settings.json` are all
untouched. `install_constellation.py` was read only, for `CORPUS_MARKER`.

One item worth stating plainly: running the repro from the main checkout regenerates
`.agent-work/epic-418-redux/transitions/close-to-w5/{CURRENT_TRUTH,WAVE_REVIEW}.md`, which are
**tracked**. They show `M` in `git status` in this worktree. Their blob OIDs are **identical to
HEAD** — the `M` is the CRLF working-tree stat artifact `docs/agents/CREW_CONTEXT.md` warns about,
and `git diff` on them is empty. No content change landed outside allowed scope.

```
CURRENT_TRUTH.md  HEAD=bf8f6729173d19879c7d5d147db2e48e8f3f8271  WT=bf8f6729173d19879c7d5d147db2e48e8f3f8271
WAVE_REVIEW.md    HEAD=c708fd08d53bba11939768affcd4d8b8ee992fde  WT=c708fd08d53bba11939768affcd4d8b8ee992fde
```

## Behavior changed
Yes.

- New `_is_skills_root(path)`: true when the directory carries the installer's `CORPUS.json`, **or**
  holds at least one `constellation-*` child with its own `SKILL.md`.
- New `_is_installed_bundle(path)`: own `SKILL.md` **and** parent is a skills root.
- New `_candidate_skills_roots()`: `<cwd>/.claude/skills`, then `~/.claude/skills`.
- `_installed_skills_root(skills_root=None)` resolves in the handoff's order: explicit flag →
  own bundle → probe (with a visible stderr note) → refuse naming every root tried.
- `--skills-root` added to the parser and threaded through `verify_explorer`, `verify_commander`,
  `verify_admiral_prelaunch`.

**Project-before-user ordering kept.** I found no evidence for the other order. Most-specific-wins
matches `install_constellation.py`'s two scopes, and `settings_path_for_target_root` (:663-668)
derives settings from the resolved target root the same way.

## Test mode
**Required:** test-after allowed, tests required (strengthened durable system: targeted tests plus
the relevant broader suite; no no-test-surface exception).
**Satisfied:** yes. 11 new tests / 17 new subtests, plus the eight-file coupled suite green.

## Evidence

### 1. Three-location matrix, measured on disk (LOAD-BEARING)

`test_guard_location_predicate_separates_the_three_real_locations` builds all three as real trees
under `tempfile` — a real installer-produced bundle, a main-checkout shape, a worktree shape — and
asserts the predicate on each, recording the three structural columns in the subTest label.

```bash
python -m pytest tests/test_iterative_planning_doctrine.py -q -k guard_location_predicate
```
```
3 passed, 12 deselected, 5 subtests passed in 0.30s
EXIT=0
```

Observed behaviour at each location, from the live runs below:

| Location | verdict | what the run does now |
|---|---|---|
| installed bundle (`~/.claude/skills/constellation-*`) | installed | resolves its own parent, no note |
| main checkout `C:/Programs/constellation-skills` | not installed | falls through to the probe, visible note |
| worktree `.../epic418-w5-gates` | not installed | falls through to the probe, visible note |

The test also asserts what the sibling scan looped over (`parent_bundle_siblings >= 3`), so an empty
scan cannot report clean, and asserts the old name test disagrees on **both** non-installed rows in
opposite directions.

### 2. Name-only decoy rejected (LOAD-BEARING)

`test_guard_location_predicate_rejects_name_only_decoy` puts `constellation-decoy/` (no `SKILL.md`)
**inside a real skills root**, so clause 2 holds and clause 1 is the only thing rejecting it. It
asserts the decoy name does start with `constellation-`, i.e. the old guard would have taken it.
Covered by the run in item 1. A companion test proves the accept direction is also name-free: a
bundle named `oddly-named-bundle` under a `CORPUS.json`-marked root is accepted, with
`sum(marked.glob("constellation-*")) == 0` asserted.

### 3. `guard_mutation` RED on a wrong root, green on the right one (LOAD-BEARING)

By hand, same command, only the root differs:

```bash
cd /tmp/g1-mut-demo && python .../scripts/verify_iterative_role_artifacts.py commander \
  --work-id demo-run --skills-root C:/Users/fredc/.claude/skills
```
```
iterative role artifact ok: commander (demo-run)
EXIT=0
```

```bash
cd /tmp/g1-mut-demo && python .../scripts/verify_iterative_role_artifacts.py commander \
  --work-id demo-run --skills-root /tmp/g1-mut-demo/wrong-root
```
```
REFUSED: installed public verifier is missing: C:\Users\fredc\AppData\Local\Temp\g1-mut-demo\wrong-root\constellation-replan\scripts\verify_replan.py
EXIT=1
```

The test `test_guard_mutation_wrong_skills_root_drives_the_acceptance_check_red` does this for all
three modes (6 subtests: correct/wrong × explorer/commander/admiral-prelaunch). The wrong root is
*plausible* — it satisfies `_is_skills_root` — so nothing upstream rejects it; it simply lacks the
verifiers, which is exactly #501's original shape.

**And the test itself can fail.** I substituted the correct root into the wrong-root slot,
asserted the substitution applied, and observed RED:

```
MUTATION APPLIED: 1 substitution
E   AssertionError: True is not false : explorer target must be absent from the wrong root
1 failed, 22 deselected in 0.62s
EXIT=1
=== restored; re-run ===
1 passed, 22 deselected, 6 subtests passed in 1.22s
EXIT=0
```

### 4. Both `-k` selectors collect nonzero (LOAD-BEARING)

Run unpiped, exit codes read from the pytest process itself:

```bash
python -m pytest tests/test_iterative_planning_doctrine.py -q -k guard_location
```
```
10 passed, 13 deselected, 11 subtests passed in 2.09s
EXIT=0
```

```bash
python -m pytest tests/test_iterative_planning_doctrine.py -q -k guard_mutation
```
```
1 passed, 22 deselected, 6 subtests passed in 1.19s
EXIT=0
```

Both nonzero. The two test classes are named `GuardLocationStructureTests` and `GuardRuntimeTests` —
neither class name contains `guard_location` or `guard_mutation` (no underscores), so each selector
matches on **method names alone**, and neither gate's floor is satisfiable by the other's tests.
Neither selector collides with `stop_*` or `archive_*`.

### 5. Refusal message, quoted exactly (LOAD-BEARING)

```
REFUSED: cannot locate an installed constellation skills root: this script is not inside an installed skill bundle (C:\Users\fredc\AppData\Local\Temp\g1-refusal\wt\epic418-w5-gates) and no known skills root was found -- pass --skills-root <path> to name one explicitly. Roots tried (3): C:\Users\fredc\AppData\Local\Temp\g1-refusal\wt; C:\Users\fredc\AppData\Local\Temp\g1-refusal\proj\.claude\skills; C:\Users\fredc\AppData\Local\Temp\g1-refusal\bare\.claude\skills
```

It names the real problem (no skills root locatable), not the old wrong one, and enumerates every
root tried. `test_guard_location_resolution_refusal_names_the_problem_and_every_root_tried`
**asserts the count**: it parses the stated `(3)`, parses the `;`-separated list, asserts
`int(stated) == len(roots) == 3`, and asserts the exact ordered list. It also asserts the two old
messages are absent.

### 6. Coupled suite green (confirmatory)

```bash
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py \
  tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py \
  tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```
```
386 passed, 480 subtests passed in 55.97s
EXIT=0
```

Base was 375 passed / 463 subtests. Delta is **+11 tests / +17 subtests**, which is exactly my
additions (3 + 7 + 1 tests; 5 + 6 + 6 subtests) — nothing else moved.

### 7. Red repros re-run

```bash
cd C:/Programs/constellation-skills && python scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
```
```
REFUSED: installed public verifier is missing: C:\Programs\constellation-replan\scripts\verify_replan.py
EXIT=1
```
This is the **repo-root copy as it exists on `main`** — still unfixed, exactly as the handoff
predicted. Recorded, not treated as my fix's result. The main checkout is outside my edit scope.

Running the **fixed** script with the main checkout as cwd — the wrong-accept polarity:
```bash
cd C:/Programs/constellation-skills && python C:/Programs/constellation-skills-wt/epic418-w5-gates/scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
```
```
note: this script is not inside an installed bundle (C:\Programs\constellation-skills-wt\epic418-w5-gates); resolved installed skills root C:\Users\fredc\.claude\skills
iterative role artifact ok: admiral-prelaunch (epic-418-redux)
EXIT=0
```
`C:\Programs\constellation-replan\...` never appears again — `C:/Programs` is no longer resolved as
a skills root. `git status` in the main checkout came back **clean** and the two regenerated files
hashed identical before and after.

The wrong-refusal polarity, from this worktree:
```bash
cd C:/Programs/constellation-skills-wt/epic418-w5-gates && python scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
```
```
note: this script is not inside an installed bundle (C:\Programs\constellation-skills-wt\epic418-w5-gates); resolved installed skills root C:\Users\fredc\.claude\skills
iterative role artifact ok: admiral-prelaunch (epic-418-redux)
EXIT=0
```
`REFUSED: role verifier must run from an installed constellation-* skill` no longer appears.

### 8. Wiring grep

```bash
grep -rn "skills_root\|_is_skills_root\|_probe_skills_root" --include=*.py scripts/ tests/
```

Production call sites per new symbol (excluding the definition line):

| symbol | production call sites | test call sites |
|---|---|---|
| `_is_skills_root` | **2** (`_is_installed_bundle`:82, probe loop:109) | 6 |
| `_is_installed_bundle` | **1** (`_installed_skills_root`:104) | 3 |
| `_candidate_skills_roots` | **1** (probe loop:108) | 0 |
| `skills_root` parameter | **3** — one per mode (:158, :167, :203), fed from `main()` (:235, :237, :239) | 5 |
| `--skills-root` argparse | **1** (:228), reached by all three modes | 4 |

Nothing is shipped-inert. I named the probe helper `_candidate_skills_roots`, not
`_probe_skills_root`; the handoff's grep pattern still catches it via `skills_root`.

## Map Impact

- **Structural anchors touched:** `scripts/verify_iterative_role_artifacts.py` —
  `_installed_skills_root()` (was :53) is now a four-step resolver at :91, backed by two new pure
  predicates (`_is_skills_root` :57, `_is_installed_bundle` :72) and a scope list
  (`_candidate_skills_roots` :85). The public CLI surface gained `--skills-root`.
- **Capabilities added/changed/affected:** role-artifact verification is now runnable from a source
  checkout and from a Commander worktree, not only from an installed bundle. `g4-integrate.c2`'s
  `--skills-root` invocation is supported.
- **Constraints/assumptions touched:** the README's "repo layout vs. installed layout" duality is now
  encoded in code rather than only in prose. The constraint that the repo's own name collides with
  the installed prefix is **honored by no longer consulting the name at all**. `CORPUS_MARKER` is
  duplicated (not imported) from `install_constellation.py` — an installed bundle has no installer on
  its path; the duplication is commented at both ends of the intent.
- **Decision candidates / resolved decisions:** `decision:` how a running process identifies an
  installed bundle — resolved as specified, by structure. Project-before-user probe ordering kept;
  no contrary evidence found. Both remain `@grade: settled/human`, unchanged by me.
- **Claims/evidence produced:** the source-repo/installed-bundle duality — this run's named unmapped
  seam — is now **measured on disk** at all three locations rather than reasoned from structure.
- **Trust limitations / drift found:** repo orientation is still `DEGRADED-NO-MAP`; nothing records
  this seam as an architectural fact. Candidate for Cartographer.

## Docs/contracts touched
None. `--skills-root` is documented in its own `argparse` help. The skill templates that invoke this
script (`ADMIRAL_SPINE`, `COMMANDER_SPINE`, `EXPLORER_SPINE`, `skills/*/SKILL.md`) are unchanged and
still work — they use the absolute installed path, which now hits the own-bundle branch. Triage
candidate below covers whether they should adopt the flag.

## Assumptions
- The engine's project-scope probe uses `Path.cwd()`, matching `_work_area()`'s existing use of
  `Path.cwd()`, so both resolve against the same directory.
- `--skills-root` validates `is_dir()` only, per handoff step 1 — deliberately **not** the
  skills-root structural test, so a wrong-but-real directory still reaches the downstream
  missing-verifier refusal. This is what makes the `guard_mutation` floor reachable.
- Tests isolate `HOME`/`USERPROFILE` into a temp home so the developer's real `~/.claude/skills`
  cannot leak in and make a probe pass. Without this the refusal test would be unfalsifiable on this
  machine.

## Stop conditions hit
None. The structural predicate separated all three locations, the mutation test reaches RED on a
broken input, no exclusion needed touching, and no decision outside my authority came up.

## Out-of-scope observations
Triage candidates, not fixed here:

1. **The other verifiers still resolve roots by hand.** `check_corpus_freshness.py`,
   `check_skill_freshness.py` and `verify_coverage_ledger.py` each take their own `--skills-root`
   with unrelated defaults (`verify_coverage_ledger.py:111` defaults to `repo_root / "skills"` — the
   *repo* layout, not the installed one). Four scripts now answer "where are the skills" four ways.
2. **The spine templates could pass `--skills-root` explicitly.** They currently rely on the
   absolute installed path landing in a bundle. That works, but an explicit flag removes the
   dependency on where the script file happens to sit. Related to episode `w3a-465-001`, which
   records this exact class of instantiation defect and proposes an in-suite guard for it.
3. **The probe's stderr note is invisible to the engine.** A `command` condition discards stdout and
   the engine's verdict is the exit code, so a run that silently drifts to a *different but valid*
   skills root will pass its gate with the note unread. Not a defect of this change — the note is
   the best available signal — but worth knowing the guard cannot announce this through the engine.

## Workflow Feedback

- **Handoff gaps:** the **Required resolution order** step 4 says the refusal must name "every root
  tried" without saying whether the script's own implied root counts as one. I included it, so the
  count is 3, not 2. My first test asserted the *bundle directory* rather than its *parent* and
  failed — the ambiguity cost one cycle. Worth a sentence in a future handoff, since the count is
  asserted by a test and therefore load-bearing.
- **Context rediscovered:** nothing significant. The handoff's on-disk measurement table was
  accurate and saved real time — I reproduced it as fixtures rather than re-deriving the predicate.
  The one thing I had to work out myself was that `~/.claude/skills` really exists on this machine,
  so any probe test that does not isolate `HOME`/`USERPROFILE` is a check that cannot fail. That is
  the wave's own theme and would be worth naming in handoffs that ask for probe-order tests.
- **Instructions improvised around:** the implementer plan template's `c1` TDD-red postcondition does
  not fit a test-after gate whose floor is "a test must go red on a broken input." I collapsed `c1`
  to a manual attest of the *paired* runs on `m3-mutation` and kept the green command on `c2`. The
  template says to collapse to a single postcondition for test-after, which would have dropped the
  red demonstration the handoff requires; keeping both was the closest compliant thing.
- **What would have made this easier:** one line in the handoff fixing whether the own-location root
  is counted in "every root tried". Everything else was sufficient — the protected-intent section in
  particular made the permissive-guard trap unmissable.

## Return status
`complete` — **no unresolved blockers.**
