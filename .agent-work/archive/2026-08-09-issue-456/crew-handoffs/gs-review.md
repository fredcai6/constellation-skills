# Reviewer Handoff — gate `gs` (the run's LAST gate)

## Task statement

Two things: (1) cherry-pick the `skills/` PATHS ONLY from `d102c05` — four files,
9 changed lines — without letting `.agent-work/explore-code-map/cycle-3.json`
ride along; (2) make the map entry point resolve as a tracked file and give it a
freshness test that can actually fail.

## What was implemented

Read `.agent-work/issue-456/crew-handoffs/gs-implement-RESULT.md` in full first.

- Four skills files cherry-picked via `git checkout d102c05 -- <path>`.
- `map/INDEX.md` + `map/ids.jsonl` newly tracked — the **2-file** landing zone.
  `.gitignore` gained `map/*` with two negations so the other ~4,010 generated
  pages stay untracked.
- `tests/test_code_map.py` gained `MapTreeFreshnessTests` (2 tests).
- The landing-zone size was **measured, not assumed** — see
  `.agent-work/issue-456/landing-zone-measurement.md`. The 116-file zone is NOT
  stable (one reworded docstring rewrites its module `INDEX.md`); the 2-file zone
  is, and the measurement's negative control fires on it. Do not re-derive this;
  do challenge it if you think the method is wrong.

## How to inspect

```
git diff d102c05 -- skills/commander/references/commander-core.md skills/commander/templates/IMPLEMENTER_HANDOFF.template.md skills/implementer/SKILL.md skills/scout/SKILL.md
git diff --quiet -- .agent-work/explore-code-map/cycle-3.json
git ls-files map/
git log --oneline -3
```

## What to attack — in priority order

**1. The freshness test's teeth.** The implementer showed it RED two ways
(staled committed index; a shape edit to a mapped module left un-rebuilt). Both
are *its* mutations. **Find one it did not choose.** Candidates worth trying: a
docstring reword in a mapped module (should this move the root index? the
measurement says no — so does the test correctly stay green, or is it blind?);
deleting a module; renaming a symbol. Report what you tried and what happened,
including mutations that found nothing.

**2. `tc20`, already filed — confirm or refute.** The `ids.jsonl` half of the
test compares empty to empty (no anchor id has ever been authored in this repo)
and passed under *both* the implementer's mutations while its sibling went RED.
Is it a check that cannot fail? Say so plainly either way. This run has hit five
prior instances of exactly this and it is the thing most worth catching.

**3. The 2-file landing zone as shipped.** Does `map/INDEX.md` actually resolve
for a crew? Its links into `<module>/INDEX.md` do NOT resolve until a build runs
— that limitation is known and accepted, not a finding. What would be a finding:
the committed file being stale, wrong, or not matching a fresh build.

**4. The `.gitignore` rule.** Confirm it cannot silently start tracking the body
pages, and cannot silently start ignoring the two files that must ship.

## Close criteria

- The four skills paths carry exactly the `d102c05` diff; `cycle-3.json` untouched.
- `git ls-files map/` returns exactly two paths.
- `-k 'map_tree_freshness'` passes and is proven RED under at least one mutation
  **you** chose.
- Full suite green: expect **1840 passed, 2 skipped, 701 subtests, 0 failed**
  (baseline 1838 + the two new tests).
- `python -m scripts.code_map build --root .` then `check --root .`: 7/7, exit 0.
  **There is no standalone `scripts/code_map/build.py`** — the package CLI is the
  entry point.

## Known handoff defect — do not report it as new

My gate criterion literally reads "`git diff d102c05 -- skills/` is empty." That
is **unsatisfiable and always will be**: later gates legitimately moved four
other files under `skills/`. The implementer caught it, scoped the check to the
four cherry-picked paths, and amended its plan in-engine with logged authority
rather than reinterpreting it silently. That was the right call and the defect is
mine. Already routed to feedback.

## Allowed scope

Inspection, plus temporary mutation of source for probing, always reverted
byte-clean. Verify reverts with `git diff --quiet -- <path>`, **not**
`git status --porcelain` — this repo runs `core.autocrlf=true` with `text=auto`
and porcelain false-negatives on line-ending-only differences.

## Specific exclusions

- **Do not fix anything.** Verdict pass. BLOCK and describe if you find a defect.
- **Never `git add -A` or `git add .`** — ~4,010 untracked files under `map/` must
  stay untracked.
- Do not push, do not open a PR, do not merge.
- `C:\Programs\f1Brainz` and `C:\Programs\superCoolSpaceSim` are READ-ONLY.
- Do not re-litigate g8's docstring split or g7's tag grammar — both closed.

## Constraints

- stdlib-only.
- Full suite must be green at this gate boundary (critic F6).

## Inbound map anchors

- **Map entry point:** `map/INDEX.md` — the file this gate makes resolve.
- structural: the four `skills/` paths; `map/` — the committed page tree
- capability: hand crews their starting pages
- constraint: one gate per file and decision-class in scope — the rule this very
  commit adds
- decision: the landing zone — resolved by measurement, 2 files
- evidence: determinism — the committed entry point must match a fresh build

## Evidence from IMPLEMENTER_RESULT

`.agent-work/issue-456/crew-handoffs/gs-implement-RESULT.md` (engine artifact
`e-gs-implement-1`), no unresolved blockers.

## Survey convention for this gate

This is attempt 1, so start a fresh review survey. (If a later attempt is ever
needed: append a recheck item as a sibling, record it, and re-consolidate with
`--override-reason` — the convention prior gates used.)

## Authority

Verdict authority: `APPROVE` or `BLOCK`, yours alone. No edit authority.

## Return

Write `.agent-work/issue-456/crew-handoffs/gs-review-RESULT.md` — exactly that
path. Return status `complete`.
