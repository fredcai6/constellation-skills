# Implementer Handoff

## Gate
`g1-implement` — Location guard (fix B, issues #501 + #468), work-id `w5-gates`.

Worktree: `C:/Programs/constellation-skills-wt/epic418-w5-gates`, branch `epic-418/w5-bookend-gates`.
Run everything from that directory. **Use `python`, never `py`** — on this machine they are different
interpreters and `py` has no pytest, so `py -m pytest` exits nonzero and reads exactly like a red suite
when in fact the tests never ran.

## Task

Replace the name test in `_installed_skills_root()` (`scripts/verify_iterative_role_artifacts.py:53-59`)
with a **structural** one, and introduce a `--skills-root` flag.

Today the guard is:

```python
skill_root = Path(__file__).resolve().parents[1]
_require(skill_root.name.startswith("constellation-"),
         "role verifier must run from an installed constellation-* skill")
return skill_root.parent
```

The defect has **two polarities**, and both must be fixed:

- **(a) Wrong-accept from the main checkout.** The source repo is named `constellation-skills`, so
  `startswith("constellation-")` is True. The guard returns `C:/Programs` as the skills root and the
  run then fails downstream naming the wrong problem:
  `REFUSED: installed public verifier is missing: C:\Programs\constellation-replan\scripts\verify_replan.py`.
  This is the polarity #501 and #468 describe.
- **(b) Wrong-refusal from a Commander worktree.** A worktree directory is not named `constellation-*`,
  so the guard refuses outright:
  `REFUSED: role verifier must run from an installed constellation-* skill`. This polarity is in
  neither issue and is a finding this run returns.

### Required predicate

A directory is an **installed bundle** when **both** hold:

1. it carries its own `SKILL.md`; **and**
2. its parent is a **skills root** — the parent carries the installer's `CORPUS.json` marker
   (`install_constellation.py:1040`, `CORPUS_MARKER = "CORPUS.json"`), **or** the parent contains at
   least one `constellation-*/` directory that carries a `SKILL.md`.

I measured this predicate on disk at all three locations before writing this handoff, and it separates
them cleanly:

| Location | own `SKILL.md` | parent `CORPUS.json` | parent `constellation-*/SKILL.md` count | verdict |
|---|---|---|---|---|
| `C:/Programs/constellation-skills` (main checkout) | False | False | 0 | not installed |
| `C:/Programs/constellation-skills-wt/epic418-w5-gates` (this worktree) | False | False | 0 | not installed |
| `C:/Users/fredc/.claude/skills/constellation-admiral` | True | True | 20 | installed |

Note clause 2's sibling test does **not** smuggle the name check back in: it asks about the *parent's*
children, and the repo root carries no `SKILL.md` at all, so clause 1 already excludes it.

### Required resolution order

1. `--skills-root <path>` **wins if given**. Validate the path is a directory; refuse with a clear
   message if it is not.
2. Else, if the script's own `parents[1]` is an installed bundle by the predicate above, return its
   parent.
3. Else probe the known skills roots, taking the first that satisfies the skills-root test in clause 2
   above: project scope `<cwd>/.claude/skills`, then user scope `~/.claude/skills`. On a hit, print a
   **visible stderr note naming the root resolved** and return it.
4. Else **REFUSE**, and the message must name the real problem and **every root tried**. This is
   #468's explicit ask: today's message names the wrong problem.

Project-before-user ordering in step 3 is most-specific-wins, matching the installer's two install
scopes (`install_constellation.py:663-664`). If you find evidence that the other order is correct,
say so in your result rather than silently swapping it.

**`--skills-root` does not exist today and this gate introduces it.** It is load-bearing, not
optional: `g4-integrate.c2` invokes
`python scripts/verify_iterative_role_artifacts.py commander --work-id w5-gates --skills-root C:/Users/fredc/.claude/skills`
and that must work. Add it to the `argparse` parser in `main()` and thread it through
`verify_explorer` / `verify_commander` / `verify_admiral_prelaunch` to `_installed_skills_root()`.

## Protected Intent

**The guard answers one question: "where am I running from".** Widening it so it passes everywhere is
explicitly refused by the launch order's pre-ruling 4. That converts a guard that wrongly refuses into
**a check that cannot fail**, which is worse than today's defect — and this whole wave is about checks
that cannot fail. A cold critic already measured that an unconditionally-permissive guard left the old
whole-file test run green, which is why this gate's close criteria select on specific test names.

The stderr note in step 3 is **for a human**. The engine's verdict for a command condition is the exit
code and stdout is discarded (`docs/CHECKLIST_SCHEMA.md`), so never make a check depend on that text.

## Test Mode

Test-after allowed, tests required. This is a verifier — `docs/agents/ORCHESTRATOR_CONTEXT.md` classes
workflow mechanisms and verifiers as a **strengthened durable system** owing targeted automated tests
**plus** the relevant broader suite. No no-test-surface exception is available here.

## Test Naming Contract — load-bearing

This gate's close criteria are `-k` selectors. A selector that matches zero tests exits 5, which is how
the gate fails closed when the tests were never written. **Misnaming a correct test makes the gate
unpassable**, and one of the two selectors is non-overridable, so this is not a style preference:

- The **three-location matrix** and the **name-only decoy** tests MUST carry `guard_location` in their
  test method names.
- The **wrong-root mutation** test MUST carry `guard_mutation` in its name.

Both selectors run against `tests/test_iterative_planning_doctrine.py` only. Do not reuse the other
gates' tokens (`stop_*`, `archive_*`) — each gate's floor must be unsatisfiable by a sibling's test.

## Close Criteria

The implementer proves each of these:

- `_installed_skills_root()` decides by structure, not by name, exactly as specified above.
- `--skills-root` exists, wins when given, and is reachable from all three modes.
- Tests named `*guard_location*` cover the three-location matrix — installed bundle accepts; main
  checkout does not resolve as installed; a worktree-shaped directory does not resolve as installed —
  **plus** a name-only decoy: a directory named `constellation-something` that carries **no**
  `SKILL.md` must NOT be accepted as an installed bundle.
- A test named `*guard_mutation*` points the resolver at a plausible-but-wrong root and shows the
  acceptance check still goes **RED**. This is #501's second Acceptance criterion. It is a
  non-overridable floor: if it cannot be made to fail on a broken input, that is a stop condition.
- The refusal message names the real problem and every root tried.
- The coupled suite (eight files, command below) is green.

Build the location fixtures as real directory trees under `tempfile` — the existing
`InstalledIterativeRoleRuntimeTests` (`tests/test_iterative_planning_doctrine.py:250-297`) already
installs a real bundle into a tempdir via `install_constellation.py` and shells out with
`subprocess.run`; follow that shape rather than monkeypatching, so the tests measure the guard on disk.
That class's `run_role` helper is at :289.

## Allowed Scope

- `scripts/verify_iterative_role_artifacts.py`
- `tests/test_iterative_planning_doctrine.py`

Both are pre-authorized for edits, including reconciling any existing test in that file whose scenario
this change invalidates. Both are tracked, not ignored.

## Specific Exclusions

- `scripts/checklist_engine.py` and `tests/test_checklist_engine.py` — **crew 4 owns them this wave**
  (epic #418 wave 5). If the fix appears to need either, **STOP and float**; do not edit them.
- `scripts/install_constellation.py` — crew 2. Read it for the `CORPUS_MARKER` constant; do not edit it.
- Handoff templates — crew 3. `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md` — crew 5.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — in this crew's ownership but it belongs
  to gate g3. Leave it alone here.
- No hooks, no `settings.json`, no `docs/agents/*` doctrine edits.
- Any red that lands in a file outside the allowed scope is a **FLOAT**, not an edit.

## Constraints

- The guard must not become permissive. See Protected Intent.
- Fail visibly: no silent fallback that quietly resolves a root without saying so.
- The refusal path must enumerate every root tried. Assert the count in your test rather than eyeballing
  the message.
- **HONEST NULL:** if the structural predicate turns out not to separate the three locations, report that
  with the measurement and stop. Do **not** widen the guard to make a check pass. A measured negative is
  a complete deliverable here.

## Map Anchors (inbound)

This repo has **no architecture map** — orientation is `DEGRADED-NO-MAP`, so there are no `struct:` or
`decision:` ids to cite and anchors are named by path.

- **Structural:** `scripts/verify_iterative_role_artifacts.py` — `_installed_skills_root()` at line 53,
  the guard predicate.
- **Capability:** Role-artifact verification — a strengthened durable system, so targeted tests plus the
  relevant broader suite; no no-test-surface exception.
- **Constraints/assumptions:** `README.md` "Repo layout vs. installed layout" — `skills/<name>/` in the
  repo becomes `constellation-<name>/` when installed, with shared infrastructure copied into every
  bundle. The repo's own name, `constellation-skills`, collides with the installed prefix, and **that
  collision is the defect.** Also: the engine's verdict for a `command` condition is the exit code;
  stdout is discarded (`docs/CHECKLIST_SCHEMA.md`).
- **Decision anchors:** decision pressure — how a running process identifies an installed bundle: by
  structure, not by name.
  `@grade: settled/human · leans g1-implement,g1-review · (launch-order pre-ruling 4; not yours to unsettle)`
- **Evidence expectations:** after the fix — installed bundle accepts; main checkout is not-installed and
  falls through to the probe with a visible stderr note; Commander worktree the same. #501's quoted red
  output must no longer appear from the main checkout.
- **Map confidence flags:** the source-repo/installed-bundle duality is this run's one **unmapped seam**.
  Nothing records it as an architectural fact; `README.md` documents it in prose only. Therefore
  **measure the guard on disk from each of the three locations** rather than reasoning from structure.

## Deliverable Path Check

- **Committed** — `scripts/verify_iterative_role_artifacts.py`; `git check-ignore` exited **1** (not
  ignored), verified before dispatch.
- **Committed** — `tests/test_iterative_planning_doctrine.py`; `git check-ignore` exited **1**, verified
  before dispatch.
- **Local-only** — your `IMPLEMENTER_RESULT` at
  `.agent-work/w5-gates/crew-handoffs/g1-implement-RESULT.md`; under `.agent-work/`, not expected in the
  diff.

No new tracked files are expected. Both deliverables already exist and are tracked, so `git diff` shows
both.

## Required Evidence

**Load-bearing — prove rigorously:**

1. The three-location matrix, measured on disk, with the actual observed behaviour at each location.
2. The name-only decoy is rejected.
3. The `guard_mutation` test goes **RED** on a wrong root and green on the right one — paste both runs.
4. Both `-k` selectors report a nonzero collected count. **Do not pipe a pytest command into `tail` or
   `head`** — the shell's `$?` then belongs to `tail`, not pytest, and a zero-match exit 5 reads as
   exit 0. Read the exit code from the unpiped command.
5. The refusal message text, quoted exactly, showing it names the real problem and every root tried.

**Confirmatory — a spot-check suffices:**

6. The coupled suite is green.

## Wiring Grep

`--skills-root` and any new helper must be reached by a real caller, not only by their own definition:

```bash
grep -rn "skills_root\|_is_skills_root\|_probe_skills_root" --include=*.py scripts/ tests/
```

State the count of call sites found for each new symbol. A helper referenced only by its own definition
is shipped-inert and is a stop condition, not a note.

## Verification Commands

Run from `C:/Programs/constellation-skills-wt/epic418-w5-gates`. Exactly as written, unpiped:

```bash
python -m pytest tests/test_iterative_planning_doctrine.py -q -k guard_location
python -m pytest tests/test_iterative_planning_doctrine.py -q -k guard_mutation
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```

The coupled suite measured **44s** and **375 passed / 463 subtests** on the base commit. The full suite
is not run at this gate — it takes about 16 minutes and is g4's job.

Also re-run the two red repros by hand and paste the new output:

```bash
cd C:/Programs/constellation-skills && python scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
cd C:/Programs/constellation-skills-wt/epic418-w5-gates && python scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
```

The first is the wrong-accept polarity and the second the wrong-refusal polarity. After the fix, neither
may produce its old message. **The main checkout is not in your allowed scope for edits** — you are only
running a command there, and only from the repo-root copy of the script as it exists on `main`; expect
that copy to still be unfixed, so record what it does rather than treating its output as your fix's
result. Prefer running the fixed script explicitly:
`python C:/Programs/constellation-skills-wt/epic418-w5-gates/scripts/verify_iterative_role_artifacts.py ...` with the appropriate `cwd`.

## Suggested Model Tier

Stronger. The predicate is small but the failure mode is subtle — a guard that passes everywhere looks
identical to a guard that works, and that is the exact defect class this wave exists to kill.

## Authority

Already decided, not yours to reopen:

- The predicate is structural, not name-based (launch-order pre-ruling 4).
- `--skills-root` is introduced here and is load-bearing.
- The test naming contract above.
- The ownership fence.

You may decide: the internal shape of the helpers, the exact refusal wording (as long as it names the
real problem and every root tried), and the test fixture construction.

## Stop Conditions

Stop and return if: the allowed scope must be exceeded; a specific exclusion must be touched; the
structural predicate does not separate the three locations; the mutation test cannot be made to go red
on a broken input; or a decision outside the authority above is needed.

## Return Format

Write your `IMPLEMENTER_RESULT` to
`.agent-work/w5-gates/crew-handoffs/g1-implement-RESULT.md` — the file is the deliverable, and the gate
verifies it exists and is fresh. Include: completed slice, files changed, test mode satisfied, evidence
produced (with the pasted command output for each load-bearing item), assumptions used, stop conditions
hit, out-of-scope observations, and workflow feedback — what in this handoff or the workflow made the
work harder than it needed to be.

State plainly whether any blocker is unresolved. The gate's close criterion is
"IMPLEMENTER_RESULT returned with **no unresolved blockers**".
