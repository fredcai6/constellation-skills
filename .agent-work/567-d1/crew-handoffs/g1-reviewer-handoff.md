# Reviewer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g1-review` — Author the regrowth guard against the DIRTY tree: review.

## Task statement

The implementer created **one new file**, `tests/test_cli_retirement_guard.py` — the guard that
closes issue #559 (*"the door is the interface, not a second path — remove the CLI fallback for
agents"*).

The deliverable of this epic is **not** the deletion. The instruction corpus text has been deleted
twice and has grown back twice, so the deliverable is the mechanism that makes the third deletion
stick. This guard is that mechanism. It is authored **before** the sweep on purpose: a guard
written against an already-clean corpus can only be red-proofed against a scratch string its own
author chose, which any pattern passes. Authored now, its RED is produced by the real corpus.

**The gate closes on the guard being RED for the right reason.** Do not ask for it to be green;
making it green is the sweep, which gate `g2` owns.

## How to inspect the diff

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
git status --porcelain -- skills specs docs scripts episodes tests map   # expect exactly: ?? tests/test_cli_retirement_guard.py
cat tests/test_cli_retirement_guard.py
```

The full `IMPLEMENTER_RESULT` is at `.agent-work/567-d1/crew-handoffs/g1-implementer-result.md`.
Read its "Two census discrepancies against the handoff baseline" section — the implementer reported
two places where its census disagrees with the handoff's stated baseline rather than smoothing
them, and your job includes judging whether its explanations hold.

## Close criteria

1. The file exists, **collects cleanly** (so the failure below cannot be an import error misread as
   a finding), and **fails** with exit 1.
2. The failure output names **real sites** that exist in this tree at the lines/JSON paths given.
3. The guard **states the count** of texts and files it scanned in every failure message, and
   asserts floors so it cannot pass vacuously on an empty or narrowed walk.
4. **Exception list length is zero.** No file is named as an exclusion anywhere.
5. Nothing else was modified — in particular `tests/test_mcp_adoption.py` is imported, never edited.

## The review's real work: attack the pattern

Close criteria 1–5 are cheap to confirm and are not why you were dispatched. Two things are:

### 1. Attack the pattern — try to write a regrowth it would MISS

This is the load-bearing request. The guard pins three patterns:

- `ENGINE_PLACEHOLDER_RE` = `<engine>`
- `CLI_FALLBACK_RE` = `CLI[\s-]+fallback`, case-insensitive
- `ENGINE_INVOCATION_RE` — a *command-shaped* `checklist_engine.py` reference: an interpreter runs
  it, or a path leads to it, or a long flag / engine verb follows it.

Write plausible regrowth text — the kind a future agent restoring this doctrine would actually
write — and check whether the pattern catches it. **Report every miss you find, with the exact
string.** Candidate directions worth trying, not a closed list: a differently-worded fallback
("if the door is unavailable, run the engine directly"), an invocation via a variable or an alias,
a bare `checklist_engine.py` with the command on the next line, a token other than `<engine>`
standing in for the same command line, the clause split across a JSON string boundary.

A miss is **not** automatically a BLOCK. The guard's own docstring declares three things it
deliberately does not enforce; judge whether a miss you find falls inside a declared limit
(report it as an observation) or defeats the guard's stated purpose (that is a finding).

### 2. Judge the invocation predicate's line

`ENGINE_INVOCATION_RE` is the only pattern here that *judges* rather than matches: it separates
"run this from a shell" from "this file is the engine". Measured by the implementer on this tree:
**10 command forms caught, 6 prose mentions left alone.** Both directions are pinned in the
assertion path by `TestTheInvocationPredicateItself`.

The six left alone are `skills/_shared/global-everyone.md:70,178,254`,
`skills/admiral/references/fleet-doctrine.md:234`, `skills/explorer/SKILL.md:115` (a scripts
manifest), `skills/write-a-skill/SKILL.md:20` (an archetype table cell). Read at least two of them
and say whether the line is drawn in the right place. Where the line ought to sit is a doctrine
call the Commander owns — your job is to report whether the drawn line is defensible and whether
the test genuinely pins it, not to move it.

### 3. Confirm the two reported census discrepancies

Re-measure both yourself rather than accepting the implementer's arithmetic:

- `<engine>`: the guard reports **10 occurrences** where the baseline recorded **9**. The claim is
  that the baseline counted *lines* and that `skills/commander/templates/COMMANDER_SPINE.template.json`
  `tasks.archive.imperative` carries **two** tokens on one line. Verify that, because if it is true
  the sweep must edit both and a one-per-line sweep would leave one behind.
- `CLI fallback`: the guard reports **16** where the baseline recorded **15**. The claim is that the
  loosened `[\s-]` separator also catches `CLI-fallback` at
  `skills/workbench/references/checklist-engine.md:45`, in a sentence that *forbids* the thing while
  quoting it. Verify the site and judge whether accepting that false-alarm class (rather than
  narrowing the pattern to duck it) is the right call.

## Constraints on you

1. **Re-run the verification commands yourself and read the exit code.** A pasted summary is a
   pointer to evidence, never the evidence.
2. **Do not edit anything.** This is a review. Report findings; the implementer or a later gate
   fixes them.
3. Do **not** ask for the guard to be made green, and do **not** propose adding an exception list —
   that decay (11 entries across five runs in a sibling guard) is the named failure mode this
   design exists to avoid.
4. The guard walking `skills/workbench/**` — lane D2's fenced files — is **known and expected**.
   Those sites are not this lane's to sweep; lane D2 deletes those files and this lane merges last.
   Do not raise it as a defect; `g5-final` re-runs the guard on the rebased tree.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
python3 -m pytest tests/test_cli_retirement_guard.py --collect-only -q     # expect 9 collected
python3 -m pytest tests/test_cli_retirement_guard.py -q                    # expect 3 failed, 6 passed
python3 -m pytest tests/test_mcp_adoption.py -q                            # expect green: the imported-from suite is untouched
git status --porcelain -- skills specs docs scripts episodes tests map     # expect one line
```

The gate's own closing check, which the Commander has already re-run independently (exit 0):

```sh
test -f tests/test_cli_retirement_guard.py \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g1-guard.log 2>&1 \
  && grep -qiE 'CLI fallback|<engine>' /tmp/g1-guard.log
```

## Map anchors (inbound)

There is **no architecture map in this repo** — `map_orient` returns `DEGRADED-UNPARSEABLE`. Your
map entry points:

- **`tests/test_mcp_adoption.py:838`** — `TestTier2SpineAlreadyBoundForDispatchedCrews`. **Read
  this first.** It already asserts this same absence, for two files, and already pins the human
  ruling verbatim. The guard under review is that precedent widened from 2 files to the whole
  corpus — judge it as a generalization of an in-tree precedent, not as a new invention.
- **`tests/test_mcp_adoption.py:415–478`** — `INSTRUCTION_FILES`, `_walk_instruction_files`,
  `_instruction_texts`, `_json_strings`. This is the repo's own machine-readable definition of
  "agent-facing instruction text", which the guard imports.
- `.agent-work/567-d1/notes-1.md` — the measured baseline and site enumeration.
- `.agent-work/567-d1/plan-rigor/RESULT-critic.md` — the cold plan critic's findings, especially
  **F1** (why a specificity proof against `docs/superpowers/` is vacuous) and **F7** (why the guard
  is authored first).

## Evidence produced by the implementer

- Verbatim RED output with all three failure messages and their complete site lists.
- `9 tests collected`; `3 failed, 6 passed`; `tests/test_mcp_adoption.py` at `189 passed, 2 skipped`.
- Scan census: `scanned 1007 texts across 103 files (101 under skills/, 2 under specs/)`.
- Floors asserted: ≥60 skills files, ≥1 spec file, ≥600 texts.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop conditions

Stop and return if: the guard does not collect; it fails for a reason other than the corpus (import
error, empty walk); or reviewing it would require editing a file another lane owns.

## Return format

Write the full `REVIEW_RESULT` to
`.agent-work/567-d1/crew-handoffs/g1-reviewer-result.md` **before ending your turn** — that write is
the delivery. Include a `Verdict` field whose value is exactly `APPROVE` or `BLOCK` (uppercase).
Include a `Workflow Feedback` section: what helped, what got in the way, and your own mistakes.
