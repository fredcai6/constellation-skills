# Launch Order: `impl-w5-engine` — nine issues inside `checklist_engine.py`

Epic #418, wave 5 (the final wave). **Implementer-with-plan.**

## Mission

Nine small, independent defects, all landing in `scripts/checklist_engine.py` and
`tests/test_checklist_engine.py`. **You are the sole writer of both files for this entire wave** —
that is why these are one crew and not two, and it is the single most important constraint here.

They fall into four themes. Do them in this order; the first theme is one change, the rest are
near-one-liners.

| # | Theme | Issues |
|---|---|---|
| 1 | **The Task shape is written in three places and reconciled nowhere** | **#474** `append()` and `_build_amend_task` duplicate the Task shape by hand · **#475** a template-only Task field is invisible to the completeness superset assertion (`anchors` is one today) · **#476** nothing checks `CHECKLIST_SCHEMA.md`'s Task table against the engine's Task builder |
| 2 | **Validation blind spots** | **#427** the refusals counter records zero when a refusal happens before the lease claim · **#503** `--authority` on `amend`/`waive` is validated only as non-empty, so "human ratification" is enforced by nothing |
| 3 | **Render / record branches** | **#479** dead defensive branch in `_render_directive_lines` (proved dead by mutation; kept deliberately) · **#480** the `record` directives flat-list branch silently dropped content — *inside the fix for that very defect class* |
| 4 | **Line endings** | **#493** journal append is still text-mode, the same defect class as the fixed `save()` · **#495** six repo JSON writers pass `encoding` but not `newline` |

**#475 is the one that matters most beyond its own size** — it is what moves the epic's
done-condition 2 from *substantially met* to **met**.

## Read every body yourself

**I have not read all nine bodies, and I am telling you that rather than paraphrasing them.** The
table above is titles plus my grouping. `gh issue view <n> --json body` on each one before you plan
it. Last wave a comment was posted on an issue based on a plausible reading of its title and had to
be corrected — do not inherit that.

## Pre-Rulings

All overridable with a stated reason, except where marked.

1. **Theme 1 is one change, not three.** #474, #475 and #476 are three symptoms of one cause: the Task
   shape has no single source. Fix the cause — a single Task definition the builder, the amend path,
   the completeness assertion and the schema doc all derive from — and the three close together. If
   you find they genuinely do not share a cause, say so and do them separately.
2. **NOT OVERRIDABLE — #475's fix must fail on a planted template-only field.** The whole defect is
   that the superset assertion cannot see a field that exists only in a template. A fix verified only
   against fields that already render is a check that cannot fail. **Plant one and watch it go red.**
3. **#479 is a `keep` candidate, not automatically a delete.** The issue says the branch was *proved
   dead by mutation and kept deliberately*. Either delete it with the mutation evidence, or record
   why it stays and make that reason checkable. **Do not delete it just to close the issue.**
4. **#503 — do not build a cryptographic ratification scheme.** The engine cannot prove a human made
   a call and should not pretend to. What it can do is stop accepting any nonempty string as
   authority. Make the failure mode visible; say plainly what it still cannot enforce.
5. **#495 — enumerate the six writers by command, not by memory**, and report which six you found. If
   one of them is inside `checklist_engine.py`, it is yours; if any sits in a file another crew owns,
   **float it rather than editing across the line.**
6. **You may not change a test's expectation to make it pass.** If a test and the code disagree,
   decide which is right and say which — in writing, with the reason.

## Honest-Null Clause

**A measured negative is a complete deliverable, per issue.** Nine issues does not mean nine fixes are
owed. If one of these turns out not to be real, or turns out to be much larger than filed, **close it
with a reason or report it as larger — do not force it.** Reporting eight fixed and one refuted is a
better return than nine soft passes.

**Report partials as partials.** Wave 4 reported one done-condition partial rather than rounding up,
and that was the right call.

## Inherited Latitude

You may: pick the implementation shape; refactor what you touch; add tests; open and push your PR;
comment on and close the nine issues you verify. You may **not**: touch any file another crew owns
(list below); add CLI surface without saying why; edit `skills/<role>/references/global-*.md` (those
are install-time copies `install_constellation.py` regenerates — the canonical source is
`skills/_shared/global-*.md`); or promote an observation into `docs/agents/*` doctrine.

## File Ownership

**Yours alone this wave — sole writer:** `scripts/checklist_engine.py`,
`tests/test_checklist_engine.py`. Also yours: `docs/CHECKLIST_SCHEMA.md`'s Task table (#476).

**Explicitly not yours:** `scripts/verify_iterative_role_artifacts.py`,
`COMMANDER_SPINE.template.json`, `scripts/init_work_area.py` (crew 1);
`scripts/install_constellation.py` (crew 2); crew handoff templates (crew 3);
`docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md` (crew 5).

**If a fix appears to need a file you do not own, that is a float, not a decision.**

Working notes: `notes-1.md`. **Never `findings-1.md`** — the harness `Write` tool refuses that basename.

## Workspace

- **Worktree:** `C:/Programs/constellation-skills-wt/epic418-w5-engine` — **provisioned and verified.**
- **Branch:** `epic-418/w5-engine-internals`, based on `ea854471`.
- All nine installed bundles were re-synced immediately before this dispatch. **Re-derive the engine
  hash yourself** (`git rev-parse HEAD:scripts/checklist_engine.py`) rather than copying one from any
  document, including this one.

## Inherited Context

- **You are editing the engine while every other crew in the wave is driving it.** Keep each change
  small and independently revertible, and run the full suite before you push. Main was green at
  **1867 passed / 2 skipped / 829 subtests / real exit 0** on the merged tree.
- The epic's central finding: **a check that cannot fail** — a signal identical in the healthy and
  the defective world. Twelve specimens in wave 4 alone. **#480 is a specimen that appeared inside
  the fix for its own defect class, and #479 and #503 are both on this list for the same reason.**
  You are working in the highest-density area for it.
- **NEVER read an exit code from a piped command.** `cmd | head` reports `head`'s exit. This has cost
  this run twice, including once while proving an anti-vacuity check fires. Run unpiped, or capture
  to a file and echo `$?`.

## Budget

- **Model tier: Sonnet.** Nine small changes, well-specified.
- Watch your own context gauge — nine issues is a lot of reading. A HARD reading changes your
  instruction rather than refusing your verb (#467, merged): write the handoff and hand off cleanly.

## Stop Conditions

Stop and float if: a fix needs a file you do not own; theme 1 does not share a cause; the suite goes
red for a reason you did not introduce; or any check you write cannot be made to fail on a broken
input.

## Return Shape

**A line per issue: fixed / refuted / larger-than-filed / blocked**, each with its evidence. For #475
specifically, **show the planted template-only field going red before your fix.** For #495, the
command you used to enumerate the six writers and what it returned. PR number. Anything you did not do.
