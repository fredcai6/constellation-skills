# Delta Reviewer Handoff — A+B follow-up commits

A previous independent Reviewer already APPROVED `efe92791..99a46a08`. **Do not
re-review that range.** Three commits landed after it, in response to that
review's own two findings. Review only those.

Range: `99a46a08..HEAD` on `afk/20260821-ab`.

- `4e13b789` — F2: restore coverage the B2 AST patches removed
- `ee59a7b9` — F1: document the now-required `--parent` in dispatch doctrine
- `8957d925` — map regeneration for F2's new tests

## Standing criterion

No bad actors. The only adversary is an honest agent about to make a mistake.
**Ease of use is the success measure.** F1 exists *because* the prior review
found this batch had made a tool harder to use, so judge it against that bar
specifically.

## F2 — `4e13b789`

The prior review found that B2's scripted AST patches added `--parent` to
`--resume` and `--verify-result` test calls that do not need it, leaving no
regression proving those paths work *without* it. The behavior was verified by
hand at the time; the proof was what went missing.

- Confirm `ParentOptionalForRecoveryVerbsTests` actually pins that. It must fail
  if someone later moves enforcement from `CrewSpec.__post_init__` into argparse
  `required=True` — **verify that by mutation**, not by reading. That migration
  is the realistic future mistake, and a test that passes either way is worthless
  here.
- The tests use synthetic registry entries so no `CrewSpec` is constructed.
  Confirm that is true and that they are not passing vacuously.
- `--verify-result` is reached via the `#432` `--accept-mtime-only-risk` path.
  Confirm that path is genuinely exercised.

## F1 — `ee59a7b9`

`skills/commander/references/crew-dispatch.md` gained a section on `--parent`.

Judge it as a document an agent must act on, not as prose:

- Does it name the value to pass — the dispatcher's own `SPINE_SESSION` — or
  only say that a parent is required? The second would be a new trap.
- Does it state that `--resume` and a bare `--abandon` need no `--parent`? If it
  does not, it creates the opposite error.
- Does it match the shape of the file's existing "Name a tier" section, or does
  it introduce a competing convention?
- Is anything in it false? It claims `verify_declared_dispatch.py` checks
  `crew-runs.json:parent`. Verify that.

## Map — `8957d925`

Must be `map/INDEX.md` alone: 3 line-pairs, `tests` 5319→5323, nothing
structural. A doc edit and three test methods have no business moving structure.
Confirm by reading the whole diff.

## Evidence

- Full ordinary suite, zero failures. Report exact counts.
- `git diff --check 99a46a08..HEAD` exits 0.
- Confirm nothing outside `skills/commander/references/crew-dispatch.md`,
  `tests/test_crew_launcher.py` and `map/INDEX.md` moved in this range.
- Confirm the branch was NOT rebased onto or merged with `main`; base must
  still be `efe92791`. `main` has moved three commits and must not have leaked in.

## Constraints

Do not call any `mcp__spine__*` tool. Do not commit, push, or open a PR. Do not
edit source or tests.

## Result

`.agent-work/20260821-ab/crew-handoffs/ab-delta-reviewer-result.md` — verdict,
per-commit verdicts, your F2 mutation test, your judgment on F1 as an actionable
document, and workflow feedback.
