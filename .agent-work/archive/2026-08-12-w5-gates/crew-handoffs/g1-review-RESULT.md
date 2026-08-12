# Review Result

## Gate
`g1-review` — Location guard (fix B, issues #501 + #468), work-id `w5-gates`, epic #418 wave 5.

verdict: APPROVE

Survey driven through the engine at `.agent-work/w5-gates/g1-review/review.json` —
14 checks (7 template + 7 appended, one per close criterion), all visited, all `pass`,
consolidated `verdict=APPROVE findings=0`. Session lease `rev-g1-review-w5g`.
Fowler-pass record at `.agent-work/w5-gates/g1-review/fowler-pass.json`.
My own repro scripts are at `.agent-work/w5-gates/g1-review/repro/`.

**Everything below was reproduced, not accepted.** Where the implementer's result and my
run agree, I say so because I ran it, not because I read it.

---

## Per close criterion

### 1. The guard is not a check that cannot fail — PASS
I built the decoys myself (`repro/decoy.py`), without reading the implementer's tests for the
answer.

| case | shape | verdict |
|---|---|---|
| decoy 1 | `constellation-decoy/`, **no** `SKILL.md`, inside a `CORPUS.json`-marked root | **rejected** |
| decoy 2 | same, root marked only by clause 2 (a real sibling bundle) | **rejected** |
| positive control | real bundle, own `SKILL.md`, marked root | accepted |
| name-free control | `totally-unrelated-name/` with `SKILL.md` under a marked root | accepted |

Both decoys are name-test positives, so the old guard would have taken them. The predicate says
yes and no, and its yes does not consult the name. Criterion 1 holds.

One case beyond the criterion's text is **decoy 3** — see the finding below.

### 2. The new tests can actually fail — PASS
Replaced `_is_installed_bundle`'s body with `return True`, asserting the substitution matched
**exactly once** before writing (a silent no-match would read as a passing guard) and confirming
the marker landed at line 82.

```
python -m pytest tests/test_iterative_planning_doctrine.py -q -k guard_location
9 failed, 6 passed, 13 deselected      EXIT=1
```
RED for the right reasons: the decoy test itself (`AssertionError: True is not false`), both
non-installed rows of the three-location matrix (`False != True` for main-checkout and
commander-worktree), and three runtime tests that lost the refusal entirely.

Restored with `git checkout`; verified by **blob OID**, not raw bytes, per the repo's Windows
rule: HEAD `29c3c9ba` == worktree `29c3c9ba`, `git diff` on the pair empty. Re-ran the selector:
`10 passed, 13 deselected, 11 subtests, EXIT=0`.

### 3. Both polarities are addressed — PASS
Predicate measured on the **live filesystem**, as the handoff demanded (do not reason from
structure):

| location | own `SKILL.md` | parent `CORPUS.json` | parent `constellation-*/SKILL.md` siblings | installed? |
|---|---|---|---|---|
| main checkout `C:/Programs/constellation-skills` | False | False | 0 | **no** |
| commander worktree `.../epic418-w5-gates` | False | False | 0 | **no** |
| installed bundle `~/.claude/skills/constellation-replan` | True | True | 20 | **yes** |

`_is_skills_root('C:/Programs')` is now **False** — #501's wrong root is gone at the source.

- **Polarity (a)**, cwd = main checkout, fixed script: stderr note emitted, `iterative role
  artifact ok: admiral-prelaunch (epic-418-redux)`, **EXIT=0**. The quoted red
  `C:\Programs\constellation-replan\scripts\verify_replan.py` does **not** appear.
- **Control** (this is what makes the above discriminating rather than vacuous): the main
  checkout's own unfixed on-`main` copy still emits exactly that red, **EXIT=1**.
- **Polarity (b)**, cwd = worktree: same note + ok, **EXIT=0**.
  `REFUSED: role verifier must run from an installed constellation-* skill` does not appear.
- **Installed-bundle branch** measured with a fixture I built (`CORPUS.json` root +
  `constellation-under-test/SKILL.md` + the fixed script, `constellation-replan` deliberately
  **absent**), run with cwd = main checkout — where a probe *would* have found the real
  `~/.claude/skills` and succeeded. It instead refused naming the **fixture** root, EXIT=1, with
  **no stderr note**. That proves the own-bundle branch won and no probe ran.

### 4. `--skills-root` exists and WINS — PASS
From the same fixture bundle where the own-bundle branch provably won, adding
`--skills-root C:/Users/fredc/.claude/skills` flipped the identical invocation to
`iterative role artifact ok`, **EXIT=0**. Reverse direction: from a cwd where autodetection works
fine, pointing the flag at a plausible `CORPUS.json`-marked root with no verifiers drove
**EXIT=1**. So the flag overrides both a detected bundle and a working probe. Validation reached:
`--skills-root C:/no/such/dir` → `REFUSED: --skills-root is not a directory`. On the shared parser,
threaded to all three modes — `g4-integrate.c2`'s dependency is satisfied.

### 5. The refusal names the real problem and every root tried — PASS
Reproduced in a subprocess with an **isolated** `HOME`/`USERPROFILE` and a cwd holding no
`.claude/skills` (`repro/refusal.py`). Without that isolation the real `~/.claude/skills` leaks in
and the refusal is unreachable — a check that cannot fail. Isolated, EXIT=1:

```
REFUSED: cannot locate an installed constellation skills root: this script is not inside an
installed skill bundle (...\wt\some-worktree) and no known skills root was found -- pass
--skills-root <path> to name one explicitly. Roots tried (3): ...\wt; ...\proj\.claude\skills;
...\bare\.claude\skills
```

Count checked by **parsing**, not by eye: stated `(3)` == roots listed (3), and those three are
exactly the three the code consults, in order (`bundle.parent`, `<cwd>/.claude/skills`,
`~/.claude/skills`). Neither stale message appears. No under-inclusive enumeration.

### 6. The mutation floor holds — PASS
Two levels.

- **Command level, independent of the test**: wrong-but-plausible root → `REFUSED: installed
  public verifier is missing: ...wrong-root\constellation-replan\scripts\verify_replan.py`,
  EXIT=1; same invocation with the correct root → EXIT=0.
- **The test is itself falsifiable**: I substituted `self.user_skills` into the wrong-root slot
  (exactly one match, asserted) and got 3 SUBFAILED
  `AssertionError: 1 != 0 : acceptance must not survive a wrong root` across
  explorer/commander/admiral-prelaunch, EXIT=1. Restored; test blob OID `5c018b24` identical to
  HEAD, pair diff empty, selector back to `1 passed, 6 subtests, EXIT=0`.

The test also self-guards: it asserts the wrong root **is** plausible (`_is_skills_root(wrong)`)
and that each target is absent from it **and** present in the correct root, so a mis-built or
empty fixture cannot report clean.

### 7. Both `-k` selectors collect nonzero; coupled suite green — PASS
All bare and unpiped, exit codes read from pytest itself.

| command | result |
|---|---|
| `-k guard_location` | 10 passed, 13 deselected, 11 subtests, **EXIT=0** |
| `-k guard_mutation` | 1 passed, 22 deselected, 6 subtests, **EXIT=0** |
| `-k guard_no_such_selector_xyz` (my control) | 23 deselected, **EXIT=5** |
| coupled eight-file suite | 386 passed, 480 subtests, 52.22s, **EXIT=0** |

The zero-match control confirms on this machine that a bogus selector really exits 5 and would
fail the gate closed — so "both collect nonzero" is a claim with teeth. The suite delta was
reconciled independently rather than accepted: the test file holds **12** test methods on `main`
and **23** at HEAD (+11), and the two selectors collect exactly 10+1 = 11 tests and 11+6 = 17
subtests, matching the claimed 386−375 = 11 and 480−463 = 17. Nothing else moved.

---

## Blockers
**None.** No stop condition in the handoff was met: the diff was accessible, all evidence was
reproducible, the guard went RED under the permissive mutation, the decoy was rejected, both
polarities are addressed, and no policy decision was required.

---

## Observations (not blocking) and triage candidates

**1. The `constellation-*` glob runs on the PARENT, so the source repo self-matches — `tc1`/`tc5`.**
This is the finding worth the Commander's attention. `_is_skills_root` accepts a directory if any
`constellation-*` child carries a `SKILL.md`. Since `_is_installed_bundle(path)` asks that of
`path.parent`, a candidate that is itself named `constellation-*` and carries a `SKILL.md`
**satisfies the parent clause by matching itself**. The two-clause structural test therefore
collapses to "has `SKILL.md`" for exactly the directories the old name test used to accept.

I measured the consequence rather than asserting it, on a temp stand-in for `C:/Programs`:

```
today (no root SKILL.md):        _is_skills_root(Programs)=False   _is_installed_bundle(repo)=False
if the repo gains a root SKILL.md: _is_skills_root(Programs)=True    _is_installed_bundle(repo)=True
```

So the fix is correct **today** but conditional on `constellation-skills` never acquiring a
root-level `SKILL.md` — at which point #501's wrong-accept returns in its original shape. That is
not a reason to block: no real location is misjudged now, all three were measured, and the
failure mode is a visible refusal rather than a silent accept. One-line hardening — exclude the
candidate from its own parent scan, or require a *different* sibling bundle.

**2. `CORPUS_MARKER` can drift silently — `tc4`.** The constant is copied from
`install_constellation.py:1040` and nothing asserts the two still agree. A rename would make
`_is_skills_root` quietly fall back to its sibling-glob clause — which mostly still works, so the
drift would never surface as a failure. The repo's own rule covers this: define a guard by its
consumer's behaviour, not a hand-maintained copy. A one-line equality test closes it.

**3. Flag validation is shadowed in two of three modes — `tc2`.** `verify_explorer` and
`verify_commander` read their work-area artifact *before* resolving the root, so a bad
`--skills-root` surfaces as an artifact-missing refusal; only `admiral-prelaunch` reports
`--skills-root is not a directory` first. Both still refuse visibly with EXIT=1. Ordering nit.

**4. One claim in the implementer's result does not hold — `tc3`.** It states the `CORPUS_MARKER`
duplication "is commented at both ends of the intent". Only the verifier end carries the
back-reference; `install_constellation.py:1040` has no comment pointing at the duplicate (the
comment above it is about corpus-id hashing). This is an overstatement, not a defect — the
installer was correctly off-limits for editing, so the other end could not have been added
without violating scope.

### Fowler refactoring pass
Rail exits 0 (`smells=12, flagged=3, overridden=1`). I confirmed the rail can refuse by feeding it
a record with a dropped smell and one with an unlogged override — both REFUSED.
**Flagged:** duplicated-code (observation 2), shotgun-surgery (the option needed edits at five
parallel sites; the three `verify_*` functions must change in lockstep), comments-as-deodorant
(`_is_skills_root`'s "never by name" docstring is stronger than the predicate — observation 1).
**Overridden with logged standard:** long-method, subordinated to `CREW_CONTEXT.md`'s Verification
Discipline, whose mandated assert-what-you-looped-over and assert-the-mutation-applied checks are
what account for the length. All other baseline smells absent, each with a recorded reason.

---

## Scope
`git diff --name-only main...HEAD` excluding `.agent-work/` returns **exactly** the two allowed
files: `scripts/verify_iterative_role_artifacts.py` and `tests/test_iterative_planning_doctrine.py`.
Every named exclusion is untouched, `scripts/install_constellation.py` included (read-only for
`CORPUS_MARKER`; empty diff confirmed). The two
`.agent-work/epic-418-redux/transitions/close-to-w5/` files showing `M` are the known CRLF stat
artifact — empty `git diff`, left unstaged as instructed. Both files I mutated were restored and
verified by blob OID.

---

## Workflow Feedback

- **The handoff's review target was wrong, and it matters.** It says the target is the
  "UNCOMMITTED working tree", twice and emphatically. The implementer **committed** the pair at
  `c63c2bb0`; `git status` shows both files clean and `git diff` empty. A reviewer following the
  instruction literally would have found nothing to review and could plausibly have returned BLOCK
  on "the diff cannot be accessed". I reviewed `main...HEAD` restricted to the two files instead.
  Whoever writes the g2/g3/g4 handoffs should state the target as a resolvable ref, not a
  working-tree state that the implementer's own closeout may have changed.
- **Criterion 1's decoy definition is narrower than the guard's real attack surface.** It names
  only "`constellation-something` carrying no `SKILL.md`". That decoy passes. The case that
  actually exposes the predicate's weak clause — a `constellation-*` directory *with* a `SKILL.md`
  outside a skills root — is not asked for, and I only found it because I built a third decoy of
  my own. A future close criterion should ask for decoys in **both** directions of each clause.
- **The engine wrote a nested `.agent-work/w5-gates/w5-gates/` tree.** Driving a survey whose
  `work_id` is `w5-gates` from a file already living under `.agent-work/w5-gates/` produced
  duplicate `context/` and `mechanical/` manifests one level deeper. Harmless but untracked
  clutter that closeout will see as an orphan; worth a look by whoever owns the engine's work-area
  resolution.
- **`--session-id` must follow the verb, not precede it.** The engine reference shows
  `claim --session-id <id>` but the flag is parsed per-verb, so `<verb> --session-id ...` is the
  only accepted order; putting it first fails with `invalid choice`. One wasted round trip.
- **What worked:** the pinned-interpreter and never-pipe-pytest warnings, the on-disk measurement
  table, and the explicit "build the decoy yourself, do not read the implementer's test" framing.
  That last instruction is the reason this review has a finding at all.
