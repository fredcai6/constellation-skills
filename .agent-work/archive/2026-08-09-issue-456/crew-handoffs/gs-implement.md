# Implementer Handoff — gate `gs`: land the skills cherry-pick with a real check

## Task

Two things, in order.

**1. Cherry-pick the `skills/` PATHS ONLY from `d102c05`.** Four files:
`skills/commander/references/commander-core.md`,
`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`,
`skills/implementer/SKILL.md`, `skills/scout/SKILL.md`. Nine changed lines total.

**Never `git cherry-pick d102c05` wholesale.** That commit also touches
`.agent-work/explore-code-map/cycle-3.json`, which is exploration scratch and
must not ride this branch. `52376d9` (cartographer `map-model.md`) is a separate
change, deliberately excluded. Use `git checkout d102c05 -- <the four paths>`.

Why this gate exists at all: those four files had **no owning gate**, which is
the gap critic F3 found. The sharp edge is that the commit being picked is the
one that *adds* the rule "confirm `execute.json` contains one gate for every file
and decision-class in the issue's stated file-ownership scope." Shipping that
rule while breaking it on its own files is not acceptable.

**2. Make the map entry point resolve, and give it a freshness test.** The
cherry-picked skills instruct crews to start from a **map entry point**. Right
now `map/` is untracked, so that instruction dangles.

## The landing-zone decision — already measured, do not re-derive

Read `.agent-work/issue-456/landing-zone-measurement.md` first. Summary:

- The full 116-file landing zone (every `INDEX.md` + `ids.jsonl`) is **NOT**
  stable — one reworded docstring rewrites its module `INDEX.md`.
- **`map/INDEX.md` + `map/ids.jsonl` (2 files) IS stable**: unchanged under a
  body-only edit, changed under a shape edit (the negative control fires).

**Ship the 2-file stable zone.** Commit `map/INDEX.md` and `map/ids.jsonl`;
add a `.gitignore` rule so the remaining ~4,007 generated files under `map/`
stay untracked. This retires critic F9's repo-doubling objection outright.

Do **not** commit the body pages. Do **not** `git add -A` in this worktree —
the untracked `map/` tree is exactly what must stay untracked, and a blanket add
would land 4,000 files.

## The freshness test — this is the gate's real deliverable

Write a test selected by `-k 'map_tree_freshness'`. It does not exist yet;
`grep -rn map_tree_freshness tests/ scripts/` returns nothing today, so the
gate's own closing selector currently collects **zero** tests and would exit 5.

It must assert: **the committed entry point matches a fresh build.** Rebuild
into a temp location (or rebuild and compare, restoring afterwards) and assert
`map/INDEX.md` is byte-identical to what a fresh build produces. `ids.jsonl` is
empty in this repo — no anchor id has ever been authored here — so assert its
content matches too, but do not treat emptiness as a bug.

**The test must be able to fail.** Before you report, prove it: mutate something
that should move the root index (add a top-level function to any mapped module),
run the selector, and confirm it goes RED. Revert byte-clean and confirm with
`git diff --quiet -- <path>`, **not** `git status --porcelain` — this repo runs
`core.autocrlf=true` with `text=auto` and porcelain false-negatives on
line-ending-only differences. Report the exact RED output. A freshness test that
passes because it compares a file to itself is worthless, and this run has hit
five separate instances of a check that cannot fail — do not make it six.

## Also state, in your result

Which gate owns keeping the committed entry point fresh, now that it is tracked.
One sentence, and name the mechanism (the freshness test) rather than an
intention.

## Close criteria

- The four skills files carry exactly the 9-line diff from `d102c05`; verify
  with `git diff d102c05 -- skills/` being empty afterwards.
- No exploration scratch rides along: `.agent-work/explore-code-map/cycle-3.json`
  untouched.
- `map/INDEX.md` and `map/ids.jsonl` tracked; nothing else under `map/` tracked.
- `-k 'map_tree_freshness'` collects at least one test, passes, and has been
  shown RED under a real mutation.
- Full suite green, including the skills-vocab and installer tests. Expect the
  baseline **1838 passed, 2 skipped, 701 subtests, 0 failed** plus your new test.
- `python -m scripts.code_map build --root .` then `check --root .`: 7/7, exit 0.

**Build/check entry point:** the package CLI, `python -m scripts.code_map build
--root .`. There is **no** standalone `scripts/code_map/build.py` — three
reviewers on the previous gate each rediscovered that the hard way.

## Allowed scope

`skills/` (the four paths only), `tests/test_code_map.py`, `.gitignore`,
and tracking `map/INDEX.md` + `map/ids.jsonl`.

## Specific exclusions

- Do not touch `scripts/code_map/*.py` — it closed under review at gate `g8`
  and is not yours to change. If you believe it is wrong, report it, do not edit.
- Do not merge to `main`. Not covered by the human's approval.
- Do not modify `.agent-work/explore-code-map/`.
- `C:\Programs\f1Brainz` and `C:\Programs\superCoolSpaceSim` are READ-ONLY.

## Constraints

- stdlib-only.
- The FULL suite must be green at this gate boundary (critic F6).
- Test mode: the freshness test is TDD — write it, see it fail against a
  deliberately stale committed index, then make it pass.

## Inbound map anchors

- **Map entry point:** `map/INDEX.md` — the very file this gate makes resolve.
- structural: `skills/commander/references/commander-core.md`,
  `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`,
  `skills/implementer/SKILL.md`, `skills/scout/SKILL.md`, `map/` — the committed
  page tree
- capability: hand crews their starting pages
- constraint: one gate per file and decision-class in scope — the rule this very
  commit adds
- decision: whether the committed map tree ships and which gate owns its
  freshness — **resolved by measurement**, see above
- evidence: determinism — the committed entry point must match a fresh build

## Required evidence

The `git diff d102c05 -- skills/` emptiness check, `git ls-files map/` showing
exactly two paths, the freshness test's RED output under your mutation with the
revert proven byte-clean, and the close-criteria numbers re-run by you.

## Authority

Edit authority within allowed scope. Commit your work. **Do not push, do not
open a PR, do not merge** — the Commander owns those.

## Return

Write `.agent-work/issue-456/crew-handoffs/gs-implement-RESULT.md` — exactly
that path. Return status `complete`, and name any unresolved blocker explicitly
rather than working around it.
