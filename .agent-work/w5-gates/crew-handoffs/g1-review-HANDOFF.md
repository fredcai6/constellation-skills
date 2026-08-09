# Reviewer Handoff

## Gate
`g1-review` — Location guard (fix B, issues #501 + #468), work-id `w5-gates`, epic #418 wave 5.

Worktree: `C:/Programs/constellation-skills-wt/epic418-w5-gates`, branch `epic-418/w5-bookend-gates`.
Use absolute paths. **Use `python`, never `py`** — different interpreters on this machine; `py` has no
pytest, so `py -m pytest` exits nonzero and reads exactly like a red suite when the tests never ran.
**Never pipe a pytest command into `tail` or `head`** — `$?` then belongs to `tail`, and a zero-match
`-k` selector (exit 5) reads as exit 0.

## Survey State Location
Create your review survey checklist at
`.agent-work/w5-gates/g1-review/review.json` — under the run workbench, never at the worktree root.

## What Was Implemented

`_installed_skills_root()` in `scripts/verify_iterative_role_artifacts.py` no longer decides by
directory name. Two new helpers decide by structure:

- `_is_skills_root(path)` — true when `path` holds the installer's `CORPUS.json` marker, or holds at
  least one `constellation-*` child carrying its own `SKILL.md`.
- `_is_installed_bundle(path)` — true when `path` carries its own `SKILL.md` **and** its parent is a
  skills root.

`_installed_skills_root(skills_root=None)` resolves in order: explicit `--skills-root` wins → this
script's own bundle when it really is one → probe `<cwd>/.claude/skills` then `~/.claude/skills`,
announcing the resolved root on stderr → else refuse, naming every root tried and their count.

A new `--skills-root` flag is threaded through all three modes. Tests were added to
`tests/test_iterative_planning_doctrine.py`.

## How to Inspect the Diff

The review target is the **UNCOMMITTED working tree**, not `git diff main...HEAD`.

```bash
cd C:/Programs/constellation-skills-wt/epic418-w5-gates
git status --porcelain
git diff scripts/verify_iterative_role_artifacts.py tests/test_iterative_planning_doctrine.py
```

Two files under `.agent-work/epic-418-redux/transitions/close-to-w5/` show `M` in `git status` but have
**empty diffs** — a CRLF stat artifact from a repro run, blob OIDs identical to HEAD. I verified this
myself. It is not a content change and not this gate's business.

The implementer's result is at
`.agent-work/w5-gates/crew-handoffs/g1-implement-RESULT.md`. Read it, then reproduce rather than trust
it. Everything under `.agent-work/` is local-only and correctly absent from the tracked diff.

## Task Statement

The implementer was given
`.agent-work/w5-gates/crew-handoffs/g1-implement-HANDOFF.md`. Read it — it is the contract the diff is
judged against. In short: replace the name test in `_installed_skills_root()` with a structural one,
introduce a load-bearing `--skills-root` flag, and fix **both polarities** of the defect.

The defect's two polarities, both of which must be addressed:

- **(a) Wrong-accept from the main checkout.** The source repo is named `constellation-skills`, so
  `startswith("constellation-")` was True. The guard resolved to `C:/Programs` and the run then failed
  downstream naming the wrong problem:
  `REFUSED: installed public verifier is missing: C:\Programs\constellation-replan\scripts\verify_replan.py`.
  This is the polarity #501 and #468 describe.
- **(b) Wrong-refusal from a Commander worktree.** A worktree directory is not named `constellation-*`,
  so the guard refused outright:
  `REFUSED: role verifier must run from an installed constellation-* skill`. This polarity is in
  neither issue and is a finding this run returns.

## Close Criteria

Each becomes a review check. The first three are the reason this gate exists — a cold critic panel
BLOCKed the original plan because this gate could have closed with zero work done.

1. **The guard is not a check that cannot fail.** Independently confirm a **name-only decoy** — a
   directory named `constellation-something` that carries **no** `SKILL.md` — is NOT accepted as an
   installed bundle. Build the decoy yourself; do not read the implementer's test and call it confirmed.
2. **The new tests can actually fail.** Replace the guard with an unconditionally-permissive version
   (e.g. make `_is_installed_bundle` return `True`) and confirm the `guard_location` tests go **RED**.
   Restore the file afterwards and confirm `git diff` is back to the reviewed state. A guard whose tests
   stay green under that mutation is a BLOCK, however correct the code reads.
3. **Both polarities are addressed.** Measure, from each location, what the **fixed** script does:
   installed bundle accepts; main checkout resolves as not-installed and falls through to the probe with
   a visible stderr note; Commander worktree the same. #501's quoted red output must no longer appear
   when the **fixed** script runs with the main checkout as cwd.
   Note: the copy of the script sitting in `C:/Programs/constellation-skills` is the **unfixed** one on
   `main` and is outside this gate's scope — run the worktree copy by absolute path with the cwd you
   want to test, rather than the main checkout's own copy.
4. **`--skills-root` exists and WINS when given**, including over a correctly-detected bundle. Confirm
   by passing a root and observing the resolution actually uses it. This flag is load-bearing:
   `g4-integrate.c2` depends on it.
5. **The refusal names the real problem and every root tried**, with the count. Confirm the enumerated
   count matches the roots actually listed — an under-inclusive enumeration presented as complete is the
   same defect class this wave is about.
6. **The mutation floor holds.** `guard_mutation` points the resolver at a plausible-but-wrong root and
   the acceptance check still goes RED. Confirm it fails on the broken input and passes on the correct
   one.
7. **Both `-k` selectors collect a nonzero number of tests**, unpiped, and the coupled suite is green.

## Allowed Scope

The implementation was permitted to touch exactly:

- `scripts/verify_iterative_role_artifacts.py`
- `tests/test_iterative_planning_doctrine.py`

Flag any tracked file outside that pair.

## Specific Exclusions

Off-limits to the implementation; flag if touched:

- `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` — **issue #418 wave 5, crew 4 owns them.**
- `scripts/install_constellation.py` — crew 2 (readable for the `CORPUS_MARKER` constant, not editable).
- Handoff templates — crew 3. `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md` — crew 5.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — this crew's, but gate g3's, not g1's.
- Hooks, any `settings.json`, `docs/agents/*` doctrine.

## Constraints the Implementation Must Respect

- **The guard must not be widened into a check that cannot fail.** Launch-order pre-ruling 4: "accept
  the repo checkout too" makes the guard pass everywhere, which is worse than the original defect. The
  guard's job is to answer *where am I running from*. Note the probe fallback is **specified** by the
  frozen plan and is not itself the widening the pre-ruling forbids — what the pre-ruling forbids is a
  predicate that stops discriminating. Criterion 2 is how you tell the two apart.
- Fail visibly; no silent fallback. The stderr note must actually be emitted when the probe resolves.
- The stderr note is **for a human, never for a check**: the engine's verdict for a `command` condition
  is the exit code and stdout is discarded (`docs/CHECKLIST_SCHEMA.md`).
- Verifier changes owe targeted tests **plus** the relevant broader suite
  (`docs/agents/ORCHESTRATOR_CONTEXT.md`, "strengthened durable system"). No no-test-surface exception.
- The test naming contract is load-bearing: three-location matrix and decoy tests carry `guard_location`;
  the wrong-root mutation test carries `guard_mutation`. A zero-match selector exits 5 and fails the gate
  closed — that is deliberate.

## Map Anchors (inbound)

This repo has **no architecture map** — orientation is `DEGRADED-NO-MAP`, so anchors are named by path
and there are no `struct:`/`decision:` ids to cite.

- **Structural:** `scripts/verify_iterative_role_artifacts.py` — `_installed_skills_root()`, formerly at
  line 53, the guard predicate.
- **Capability:** Role-artifact verification — a strengthened durable system.
- **Constraints/assumptions:** `README.md` "Repo layout vs. installed layout" — `skills/<name>/` in the
  repo becomes `constellation-<name>/` when installed, shared infrastructure copied into each bundle.
  The repo's own name, `constellation-skills`, collides with the installed prefix, and **that collision
  is the defect.**
- **Decision anchors:** decision pressure — how a running process identifies an installed bundle: by
  structure, not by name.
  `@grade: settled/human · leans g1-implement,g1-review · (launch-order pre-ruling 4 — not yours to unsettle; a contradiction is a float, not a revision)`
- **Evidence expectations:** the three-location matrix above, plus the decoy.
- **Map confidence flags:** the source-repo/installed-bundle duality is this run's one **unmapped seam**.
  Nothing records it as an architectural fact; `README.md` documents it in prose only. **Measure it on
  disk. Do not reason from structure.**

## Evidence Produced

From the implementer, and re-run by me (the Commander) before dispatching you. Reproduce it rather than
accept it:

- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k guard_location` → **10 passed,
  13 deselected, 11 subtests passed, exit 0.**
- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k guard_mutation` → **1 passed,
  22 deselected, 6 subtests passed, exit 0.**
- Coupled suite (eight files, command below) → **386 passed, 480 subtests, 38.9s, exit 0.** Base commit
  was 375 passed / 463 subtests, so the delta is exactly this gate's additions.
- Structural predicate measured on disk before dispatch: main checkout — no own `SKILL.md`, parent has
  no `CORPUS.json` and 0 `constellation-*/SKILL.md` children; worktree — the same; installed bundle —
  own `SKILL.md`, parent `CORPUS.json` present, 20 sibling bundles.

```bash
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```

Your verdict is recorded against engine postcondition **`g1-review.c1`**, and `g1-integrate.c4` matches
on `verdict: APPROVE`.

## Suggested Model Tier

Stronger. The whole gate is about telling a working guard apart from one that cannot fail, and those two
look identical from the outside.

## Stop Conditions

Return BLOCK if: the diff cannot be accessed; evidence is absent or unverifiable; the guard survives the
permissive mutation with green tests; the decoy is accepted; either polarity is unaddressed; or a policy
decision is required before a verdict is possible.

## Return Format

Write your REVIEW_RESULT to
`.agent-work/w5-gates/crew-handoffs/g1-review-RESULT.md` — that file is the deliverable and the gate
verifies it exists and is fresh. It must state, on its own line, `verdict: APPROVE` or `verdict: BLOCK`.
Include per-check findings keyed to the numbered close criteria, blockers, out-of-scope observations, and
workflow feedback.
