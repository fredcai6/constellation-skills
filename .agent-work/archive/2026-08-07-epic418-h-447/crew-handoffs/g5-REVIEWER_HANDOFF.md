# Reviewer Handoff — g5: the prose sweep, the doctrine tombstone, and the guard's last leg

## Gate
`g5-review` — issue #447, epic-418 workstream H. Spine `.agent-work/epic418-h-447/execute.json`.

## Survey State Location
`.agent-work/epic418-h-447/g5-review/review.json` — under the issue workbench, **never at the
worktree root**.

## Worktree
`C:/Programs/constellation-skills-wt/epic418-h-447`, branch `epic-418/h-447-episodes-retirement`,
HEAD `77e428d`, **nothing committed**. The only tree you may write to.

## How to Inspect the Diff
`git status --porcelain` then `git diff` — this gate's work is unstaged. 22 files, 331 insertions,
136 deletions.

## What Was Implemented
The written surface made to tell the truth about the retirement, plus a new approval census so the
guard can reach green.

Full specification, which is also your contract — it carries **eleven frozen invariants**:
`.agent-work/epic418-h-447/crew-handoffs/g5-IMPLEMENTER_HANDOFF.md`.
Implementer's result: `.agent-work/epic418-h-447/results/g5-IMPLEMENTER_RESULT.md`.

Headline claim, **Commander-confirmed**: `python scripts/verify_retirement.py` **exits 0 and prints
zero bytes.** All four legs green. Of the 85 `retired-name` findings, **32 removed by fixing the
surface** and **53 approved with a per-line reason**. The sweep created **13 new store mentions**,
each given its own reason, so that leg is still zero.

## The two checks that matter most

### A. Is this an absence-only edit?
The failure mode of a doc gate is a sweep that passes because the retired names are gone —
which a wholesale deletion would also achieve. **Invariants 7–10 name what must SURVIVE.** Grade
them as hard as the removals. Specifically: does `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` still say
what it said (16 insertions, 0 deletions, `git grep -c 'LESSONS.md'` = 12 at HEAD and now)? Does
`docs/CONSTELLATION_OVERVIEW.md`'s ruling paragraph survive? And where a pointer was *repointed*
rather than deleted, does the paragraph still make its original point, or was the argument quietly
thrown away with the pointer?

### B. Did the sweep write the defect it was sweeping out?
Episodes are a **record of what happened**, not a playbook. Tommy, 2026-08-06:

> *"we shouldn't be reading the episodes like lessons, it's a store for things that happened to
> replace both feedback and lessons."*

**Read every new or rewritten sentence as an agent would.** The gate rewrote the doctrine directory
and added a tombstone; if any new sentence tells an agent to read the store and condition behaviour
on what it finds, this gate produced the exact defect the run exists to fix. Pay closest attention
to the **redefined `harvest`** in `docs/agents/GLOSSARY.md` — the implementer redefined rather than
deleted it, on the ground that its live uses are all write-side. Verify that: check every live use
of `harvest` in the corpus and confirm the new definition covers them without licensing a read.

The **13 new store mentions** are the other place this could hide. Read all 13 census reasons and
the lines they approve.

## Close Criteria
Each becomes a review check. **RE-RUN every command yourself.** Redirect to a file then `echo $?`.

1. Invariants 1–6 true, each demonstrated by a command you ran.
2. Invariants 7–9 verifiably **unchanged**; invariant 10 changed **as specified** — pointers to a
   deleted module became descriptions of the property, not deletions of the sentence.
3. The `RECURSIVE_IMPROVEMENT_DESIGN.md` header says it is **history, not instruction**, and names
   where the current loop lives. Note the implementer's deliberate choice: **the header spells no
   retired name**, because naming one would have moved the `git grep -c` count and broken invariant
   7's own check. Judge whether the header is still clear without them.
4. The `ORCHESTRATOR_CONTEXT.md` tombstone carries **all five** clauses of invariant 4, written as
   doctrine an agent obeys rather than as a changelog entry. Grep each clause independently.
5. `python scripts/verify_retirement.py` exits **0** and prints **nothing**.
6. **Every census entry in BOTH files carries a reason that describes THAT line.** This is the
   criterion most worth your time. The gate exists partly because the old census approved
   `CREW_CONTEXT.md`'s read instruction under a reason written once for a block of four lines and
   true of three of them. Read all of `tests/data/store_mentions.approved.txt` and all of
   `tests/data/retired_names.approved.txt`. **A reason amounting to "an agent is still told to use
   the retired thing" is NOT approvable** — that is a BLOCK, and the surface should have been fixed
   instead. Approvable: a frozen historical record; a deny-glob re-staging block; a survivor script
   naming what it stages; a comment recording why the retirement was untrack-not-delete.
7. The new census is **one parser, not a fork** — `parse_approved`/`load_approved` grew one optional
   `census_path`. Verify that, and verify the leg was **not weakened into a pattern allowlist**; the
   census must still name exact sites so anything new has to be looked at.
8. The new census test exists and is **red-proved**. The implementer claims two proofs: removing the
   tombstone approval takes the scan 0→1 at the exact path/line (restore verified byte-identical,
   sha256 `bb101b2b…`, 15536 bytes both ways), and a two-line decoy where one line is approved and
   the other still fires. **Do your own** — do not replay theirs.
9. Line endings: every changed file is fully CRLF as at `77e428d`. The implementer warns that
   `grep -c $'\r$'` is unreliable here (reported 0 on a file Python measured 107/107 CRLF) and that
   three files the editor flipped to LF were converted back. **Check the bytes in Python**, not with
   grep.

## The suite — read this before grading it
`FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` reports **5 failed, 1619 passed** (Commander-run).
Three distinct failures, and **all three are working-tree-vs-HEAD artifacts, not regressions**:

- `tests/test_retirement_guard.py::test_canon_is_clean` — `XPASS(strict)`. The tree went clean, which
  is the point; the marker is **g6's** to remove. **Expected.**
- `tests/test_episode_negative_control.py::test_canon_episode_store_untouched` — pins `episodes/`
  against HEAD, and invariant 3 mandates editing `episodes/README.md`.
- `tests/test_context_determinism.py::RealCheckoutSkew::test_a_clean_checkout_differs_only_in_rev_never_in_shape`
  (2 subfailures on `scripts/agent_work_root.py`) — pins a tracked path against HEAD, and invariant
  5 mandates editing its docstring.

The implementer proved causality for the latter two by restoring each file from HEAD (test green)
and putting its version back byte-identically. Deselecting the three gives **1619 passed, 2 skipped,
exit 0**.

**Do not BLOCK on these three.** Do tell me: (a) whether you agree all three are HEAD-pinning
artifacts and not masked regressions — re-derive the causality yourself rather than replaying the
implementer's transcript, and (b) whether the count arithmetic closes (baseline 1618, +3 new tests,
−2 guards → 1619).

Also expected: `python scripts/verify_retirement.py` **now exits 0** — that is the deliverable, not
an anomaly.

## Declared deviations — grade on merits
1. **`harvest` redefined, not deleted.** Invariant 2 allowed either. Verify the live uses really are
   all write-side.
2. **The `Lesson:` field name was KEPT** in `CONSTELLATION_FEEDBACK.template.md` while its *accepted
   value* became an episode id. Reason: `scripts/collect_feedback.py` parses that field by literal
   name and fingerprints cross-run recurrence on it, so renaming would silently drop every export's
   stable identity. Invariant 6 said "accepts an episode id", not "is renamed". **Verify the parser
   claim at the source** — if `collect_feedback.py` does not in fact key on the literal string, the
   deviation loses its justification.
3. **The RECURSIVE_IMPROVEMENT_DESIGN header spells no retired name** — see criterion 3.

## Allowed Scope — flag anything outside it
Invariants 1–6 and 10's enumerated files; `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` **header only**;
plus `scripts/verify_retirement.py`, `tests/data/retired_names.approved.txt`,
`tests/test_retirement_guard.py`, `tests/data/store_mentions.approved.txt`.

**Must be untouched — Commander already confirmed empty diffs, re-confirm:** `docs/superpowers/**`,
`tests/fixtures/**`, `episodes/active/**`, `episodes/retired/**`, `RETURN.md` (another workstream's
tracked file).

**Fenced — a concurrent Commander owns these. If touched, that is a BLOCK and I need to know
immediately:** `scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py`,
`scripts/gauge_reader.py`, `docs/GAUGE_WRITER_HOOK.md`.

## Constraints the Implementation Must Respect
- `python`, **never** `py`, including in your own commands.
- Prefix suite runs `FORCE_COLOR=0 NO_COLOR=1` — a colourised environment produces 10 phantom
  `HARNESS ERROR` failures in `tests/test_mutation_floor.py`. Commander-measured; not a regression.
- Windows: `encoding='utf-8', newline='\n'` on every write.
- `episodes/active/` and `episodes/retired/` are written only through `apply_episode_delta.py`;
  `episodes/README.md` is ordinary prose and was in scope.
- Do not commit, push, or change git state — including `git stash`, `git restore`, `git reset`.
- If you mutate a file to red-prove something, back it up in **binary**, restore byte-identically,
  and verify by hash.
- Use your own session scratchpad for temp files, **never** `/tmp` — a concurrent Commander shares
  it.
- No Fable at any tier; cap any dispatch at Opus and name the model.

## Map Anchors (inbound)
- **Structural:** `struct:docs/agents/ORCHESTRATOR_CONTEXT.md`, `struct:docs/agents/CREW_CONTEXT.md`,
  `struct:docs/agents/GLOSSARY.md`, `struct:episodes/README.md`, `struct:docs/EPISODE_STORE.md`,
  `struct:scripts/verify_retirement.py`.
- **Capability:** `capability:episode-store`; `capability:run-closeout-learning`.
- **Constraints:** `constraint:episodes-are-not-prescriptions` — **THE constraint; invariants 1, 2
  and 4 are where it gets written down**; `constraint:doctrine-lives-in-docs-agents`;
  `constraint:record-stores-never-hand-edited`.
- **Decisions:** `decision:episodes-replace-both` `@grade: settled/human` — **no successor playbook
  is created**; `decision:untrack-do-not-delete` `@grade: settled/measured`;
  `decision:store-hardening-out-of-scope` `@grade: settled/human`. A contradiction with a
  `settled/human` anchor is a decision candidate to float back, not to revise in place.
- **Evidence expectations:** `claim:suite-no-failures`; `claim:guard-fails-on-purpose` — the new
  census must be shown firing before it is trusted.

## Evidence Produced — reproduce, do not read
| command | claimed / Commander-confirmed |
|---|---|
| `python scripts/verify_retirement.py` | exit **0**, **0 bytes** printed — Commander-confirmed |
| `git diff --stat docs/RECURSIVE_IMPROVEMENT_DESIGN.md` | 16 insertions, 0 deletions — confirmed |
| `git grep -c 'LESSONS.md' -- docs/RECURSIVE_IMPROVEMENT_DESIGN.md` | 12, same at HEAD — confirmed |
| `git diff --stat docs/superpowers/ tests/fixtures/ episodes/ RETURN.md` | empty — confirmed |
| `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` | 5 failed / 1619 passed — confirmed; see above |
| `python -m pytest tests/test_retirement_guard.py -q` | re-run it |

## Suggested Model Tier
**Opus** — the load-bearing checks are readings of prose for prescriptive force and of 53+13 census
reasons for honesty. No mechanical check catches either. No Fable.

## Stop Conditions
BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, a fenced file was
touched, a survivor invariant (7–9) was violated, the leg was weakened into a pattern allowlist, any
census reason does not describe its line, or any new doctrine sentence instructs an agent to read
the store and act on it.

## Return Format
Write `REVIEW_RESULT` to `.agent-work/epic418-h-447/results/g5-REVIEW_RESULT.md` with an explicit
**APPROVE** or **BLOCK** on its own line, a per-invariant verdict (all eleven), your verdict on the
census reasons, per-check findings with the command you ran and its **real** exit code, blockers,
out-of-scope observations, and workflow feedback. Deliver the substance as your final message too.
