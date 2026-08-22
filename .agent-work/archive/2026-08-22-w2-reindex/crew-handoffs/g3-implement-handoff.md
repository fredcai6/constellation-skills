# Implementer Handoff

## Gate
g3 (g3-implement) — end-to-end red/green proof + regression backstop

## Task
Prove, against real scratch git repos (never this actual repo's own git state), that gates 1-2's
shipped code actually works end to end: the installed hook fires on a real `git commit`, fixes a
stale map silently, is a true no-op when fresh, respects both partial-commit shapes for real, fires
correctly from a second worktree sharing the same `.git` (the real hazard this repo's own dev
layout has), and that `tests/test_code_map.py::MapTreeFreshnessTests` remains the exact backstop it
was before this mission, unmodified. No new production code in this gate — proof only, against
gates 1-2's already-approved code.

## Protected Intent
This is the mission's own acceptance test. Every hard constraint from the launch order gets its
final proof here: the hook never blocks a commit, stages exactly two paths, is installed (not
merely built), and the freshness test is untouched.

## Test Mode
Real subprocess `git` + `pytest`, per `docs/agents/ORCHESTRATOR_CONTEXT.md`'s Dogfooding section —
an in-session observation of hook behavior is not evidence; every claim in this gate comes from a
fresh-process scratch checkout you can show the commands and output for.

## Close Criteria
- Every scratch setup is `git worktree add` against **one shared scratch `.git`** — never
  `git clone`, which cannot reproduce the shared-hooks-directory topology this repo actually has.
- New test file `tests/test_code_map_precommit_e2e.py`, each case using real subprocess `git`
  install + commit against that shared-`.git` scratch topology.
- `git diff -- tests/test_code_map.py` across the whole plan (all three gates, i.e. right now)
  is empty.
- Full local suite green at or above `3622 passed, 6 skipped, 0 failed` (the base baseline) plus
  every test this plan added across gates 1-3.

## Required Evidence, in `tests/test_code_map_precommit_e2e.py`
Each numbered case its own scratch `git worktree add` pair off one shared scratch `.git` (init a
bare or plain scratch repo, then `git worktree add` real worktrees off it — this is what makes the
shared-hooks-directory topology real, not simulated):

1. **RED PROOF, pinned to the shipped SHA** — without the hook installed, hand-edit a tracked `.py`
   source file in a scratch worktree checked out at commit `9d5aac6d` (the base this branch is built
   on — confirm via `git rev-parse HEAD` in the scratch checkout, or use `git worktree add` from a
   clone of this actual repo at that SHA), commit normally, run
   `tests/test_code_map.py::MapTreeFreshnessTests` against that scratch checkout — show it **FAILS**
   (confirms the backstop still catches an un-hooked commit exactly as today).
2. Install via the real CLI entry point (`python scripts/install_constellation.py ...` with no
   override, so `install_git_pre_commit_hook=True` fires for real) against that scratch checkout.
3. **GREEN PROOF** — repeat the hand-edit-and-commit; `git log -1 --stat` includes `map/INDEX.md`
   (and `map/ids.jsonl` if it changed) in the SAME commit; `MapTreeFreshnessTests` now passes with
   no manual rebuild step.
4. **Pathspec-restricted partial commit for real** — `git commit -- <path>` naming only one of two
   changed tracked files; assert `map/` untouched, the unstaged sibling stays dirty.
5. **Hunk-restricted partial commit for real** — `printf 'y\nn\n' | git commit -p` on a file with
   two well-separated hunks; assert `map/` untouched, the rejected hunk's effect never lands in the
   commit.
6. **Unrelated-dirty-file survives untouched** — a dirty tracked file NOT staged remains dirty and
   outside the commit after a stale-map commit.
7. **SECOND-WORKTREE case** — a second `git worktree add` off the **same shared scratch `.git`**
   (not a second clone); install once from the first worktree; commit for real from the second;
   assert the hook fires there too (this is the honest exercise of the shared-hooks-directory fact
   — not a synthetic stand-in for it) and touches only that worktree's own `map/` tree.
8. **TIMING** — time case 3's real end-to-end invocation including worktree materialization; report
   the number next to gate 1's 2.9s-build-only / 3.25-3.77s-full-mechanism figures. Do not presume
   it stays the same; report what you measure.

## Full-suite-green sequencing (do not misread a pre-existing test's own behavior as a hook defect)
Run the full local suite check in a **fresh, clean scratch checkout** (`git status --porcelain`
empty) separate from the checkout used for cases 4-5. `MapTreeFreshnessTests` compares disk content
(including any unstaged remainder) against the committed map — this is a pre-existing,
hook-independent property of that test, present for ANY tracked mappable file with an unstaged
diff, not something this mission's hook introduces. A leftover partial-hunk residue from case 5
sitting in a working tree you then run the full suite against will produce a real, expected
`MapTreeFreshnessTests` failure that is **not** a hook defect — do not let it read as one; run the
regression check in its own clean checkout instead.

## Regression
Run the full local `pytest` suite (this actual repo's uncommitted working tree, gates 1-2's code
included): report pass/skip/fail counts against the `3622 passed, 6 skipped, 0 failed` baseline plus
this plan's new tests. `git diff -- tests/test_code_map.py` across the whole plan (gates 1-3) is
empty — attach that diff output verbatim (it should print nothing).

## Allowed Scope
`tests/` only — specifically the new `tests/test_code_map_precommit_e2e.py`. No production code
changes in this gate.

## Specific Exclusions
Do not modify `scripts/code_map/`, `scripts/hooks/`, or `scripts/install_constellation.py` — gates
1-2's code is already approved; this gate proves it, never patches it. If a real defect surfaces
during this gate's proof, STOP and return `blocked` with the concrete evidence rather than silently
patching gates 1-2's shipped code from inside a proof-only gate.

## Constraints
- Every scratch checkout is discarded (temp dir) at test end; nothing from it is committed anywhere
  real.
- Red-proof pinned to the shipped SHA (`9d5aac6d` at gate authoring time — confirm the actual
  current `HEAD` of this branch when you run this gate, since gates 1-2 landed as uncommitted
  working-tree changes and may or may not be committed by the time you run; state whichever SHA you
  actually pinned against).

## Map Anchors (inbound)
- **Map entry point:** this checkout's own `git worktree list` output (the required topology for
  case 7) and `tests/test_code_map.py::MapTreeFreshnessTests` (the backstop this gate's proof and
  regression check both exercise).
- **Structural:** `scripts/install_constellation.py`'s real CLI entry point (the actual delivery
  path this gate proves fires).
- **Constraints/assumptions:** must-be-installed-not-merely-built (hard, proven here);
  do-not-weaken-the-freshness-test (hard, proven unmodified here); red-proof pinned to shipped
  revision (launch order standing pre-ruling).
- **Evidence expectations:** hook fires (claim) — this gate is its proof. Staging boundary honest
  (claim) — case 6 is its proof. Freshness test unchanged (claim) — the `git diff` evidence is its
  proof.

## Deliverable Path Check
- **Committed** — `tests/test_code_map_precommit_e2e.py`; new file, untracked until staged.

## Required Evidence (summary — see numbered cases above for the full list)
All 8 numbered cases above, each producing real command output you attach verbatim. A claimed
test-failure distribution, if anything fails during development, must be derived mechanically
(`pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`).

## Wiring Grep
```bash
grep -rn "install_git_pre_commit_hook=True\|install_git_precommit_hook(" --include=*.py scripts/install_constellation.py
```
Confirm the real `__main__` entry point is what this gate's install step (case 2) actually
exercises — not a test-only code path.

## Verification Commands
```bash
python -m pytest tests/test_code_map_precommit_e2e.py -q
python -m pytest -q
git diff -- tests/test_code_map.py
```

## Suggested Model Tier
stronger — reason: real subprocess git orchestration across multiple scratch worktrees, with
several interacting correctness properties (partial-commit shapes, shared-hooks topology, timing),
rewards careful reasoning over a fast bounded edit.

## Authority
Case list and topology requirements (worktree not clone) are already decided — see
`.agent-work/w2-reindex/PLAN_CRITIC.md` finding 10 and its disposition. Do not substitute `git
clone` for any case; it silently defeats the point.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required
evidence cannot be produced, a real defect surfaces in gates 1-2's shipped code (return `blocked`
with evidence rather than patching it here), or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT to
`.agent-work/w2-reindex/crew-handoffs/g3-implement-implementer-result.md` before ending your turn.
State the exact commit SHA the red-proof (case 1) actually ran against.
