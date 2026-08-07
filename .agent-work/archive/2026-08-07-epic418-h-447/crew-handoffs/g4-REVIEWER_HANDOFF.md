# Reviewer Handoff — g4: carry the live content, then untrack and delete

## Gate
`g4-review` — issue #447, epic-418 workstream H. Spine `.agent-work/epic418-h-447/execute.json`.

## Survey State Location
`.agent-work/epic418-h-447/g4-review/review.json` — under the issue workbench, **never at the
worktree root**.

## Worktree
`C:/Programs/constellation-skills-wt/epic418-h-447`, branch `epic-418/h-447-episodes-retirement`,
HEAD `100a33c`, **nothing committed**. The only tree you may write to.

## How to Inspect the Diff
**`git diff HEAD`** — not `git diff` and not `git diff --cached`. This gate deliberately leaves
work **staged** (`git rm --cached` necessarily stages, and the eight new episodes are `git add`ed
so the archive-phase gate can see them), so a plain `git diff` shows almost nothing.
`git status --porcelain` first.

## What Was Implemented
Three parts.

1. **Carry** — the eight live lessons from `.agent-work/LESSONS.md` migrated into `episodes/` as
   `issue-447-001` … `issue-447-008`, written through `scripts/apply_episode_delta.py` only.
   `.agent-work/AGENT_FEEDBACK.md`'s 2119 lines dropped with a stated reason.
2. **Untrack** — `git rm --cached` (never plain `git rm`) on both retired paths.
3. **Delete** — the playbook machinery: three scripts, the `lessons-auditor` skill tree, two
   workbench templates, three test files; plus pruning/retargeting of tests that loaded a deleted
   module.

Full specification, which is also your contract:
`.agent-work/epic418-h-447/crew-handoffs/g4-IMPLEMENTER_HANDOFF.md`.
Implementer's result: `.agent-work/epic418-h-447/results/g4-IMPLEMENTER_RESULT.md`.

## The one check that matters most: did a rule get carried across?

Episodes are a **record of what happened**, not a playbook. Tommy, 2026-08-06:

> *"we shouldn't be reading the episodes like lessons, it's a store for things that happened to
> replace both feedback and lessons."*

A lesson's `statement` is **prescriptive** — it tells a future agent what to do. The carry required
each statement to become the episode's **`workaround` assertion, rewritten as an observation of
what was done in that run**. If any `workaround` still reads as an instruction, the playbook has
been migrated into the store and this gate has produced the exact defect the run exists to prevent.

**Grade all eight yourself, by reading, not by regex.** A statement can be perfectly imperative
without containing the word "must" — *"pair every `-k` gate with an unfiltered run"* is a rule in
plain indicative mood. The test is: **would a future agent who found this line read it as
something to do, or as a report of something that happened?**

Also check the other four assertion kinds on each episode. `task-intent`, `expected-behavior`,
`observed-behavior` and `impact-cost` must be **grounded in the source lesson's `grounding`
field**, never synthesised. Spot-check at least three episodes against
`.agent-work/epic418-h-447/context/LESSONS-main-861ecbe.md` line by line. A fabricated
`observed-behavior` is a BLOCK — that is the fabrication the store's own doctrine forbids, and it
would be invisible to every mechanical check here.

The implementer flags one it says is honest rather than convenient: **W1**'s source rule was *"must
be run against a decoy"*, but that run caught its checks by cold reading, not a decoy — so the
episode reports the cold reading. Judge whether that is honesty or a dodge.

## Close Criteria
Each becomes a review check. **RE-RUN every command yourself.** Redirect to a file then `echo $?`.

1. **Eight** episodes under `episodes/active/` carry run id `issue-447`; all eight are **staged**
   (`git status` shows `A `), and all were written by the writer — **verify nothing under
   `episodes/` was hand-edited**. Check the existing 32 episodes are byte-untouched
   (`git ls-files -s episodes/active/` blob OIDs against `HEAD`).
2. Every `workaround` is an observation, not a rule. **This is the criterion above.**
3. Each episode carries `lesson:<slug>` as an `artifact-ref`.
4. `AGENT_FEEDBACK.md` dropped with a reason **naming the commit** that retains the content.
5. `git ls-files --error-unmatch` on **both** retired paths exits non-zero, **and both files still
   exist on disk** (`test -f`). `git rm --cached`, never plain `git rm` — check the reflog/status
   shape, not the claim. Deleting the working-tree copy would strand this run's own closeout.
6. The retired scripts, `skills/lessons-auditor/` and the two workbench templates are gone;
   **`scripts/stage_feedback.py` and `scripts/collect_feedback.py` SURVIVE** and still import.
7. Guard leg `retired-path-still-tracked` is **gone**
   (`python scripts/verify_retirement.py | cut -f1 | sort -u`).
8. This run's own closeout gate — the installed
   `C:/Users/fredc/.claude/skills/constellation-commander/scripts/verify_agent_feedback.py
   epic418-h-447 --phase feedback` — runs with an **unchanged** exit code (implementer measured
   1 → 1). Verify it is unchanged, not merely non-fatal.
9. The suite count delta reconciles **exactly**, explained by name.

## The two departures the implementer declared — grade these carefully
1. **Pruning widened from two test files to four.** The handoff named
   `tests/test_agent_work_root.py` and `tests/test_feedback_tooling.py`. A by-command enumeration
   found 19 failures across four files (+6 in `test_install_constellation.py`, +4 in
   `test_stage_feedback.py`). Verify the widening was **forced by the deletion** (a test loading a
   now-deleted module) and is not scope creep, and that nothing in `stage_feedback.py` /
   `collect_feedback.py` itself broke — only tests **about** the deleted verifier.
2. **6 tests retargeted rather than pruned**, on the ground that their subject was a deleted
   *template* but the machinery under test (`check_skill_freshness`, the baseline manifest)
   survives, so pruning would have silently dropped its only coverage. **This is the claim most
   worth checking**: confirm the surviving machinery really is still covered after the retarget —
   a retarget that quietly weakens an assertion is worse than a prune, because it looks like
   coverage. Every prune and retarget should carry a `#447 g4` comment at the code site; verify
   they do.

Disposition should reconcile: **13 pruned + 6 retargeted = 19**, and **85 + 13 + 1 = 99** collected
delta. Re-derive both sums; do not accept them.

## The known blocker — expected, and NOT yours to fail the gate on
`tests/test_episode_negative_control.py::test_canon_episode_store_untouched` **FAILS**. It asserts
`git status --porcelain episodes/` is empty, which is incompatible with the staged episodes this
gate is required to produce. The Commander's integrate commit closes it — Commander-confirmed the
test reads `git status`, so a commit makes it clean.

Do **not** BLOCK on it. **Do** tell me two things: (a) whether committing genuinely closes it or
merely hides it, and (b) whether the negative control still does its real job afterwards — it exists
to catch a *test run* accidentally writing to the canon store, and I want to know if this change
blunts that.

## Also expected, not defects
- `python scripts/verify_retirement.py` still exits 1 with ~85 `retired-name-on-shipped-surface`
  findings. All prose; that is **g5's** gate. The guard going green is g6.
- `tests/test_retirement_guard.py::test_canon_is_clean` is expected to xfail.

## Allowed Scope — flag anything outside it
**WRITE via the writer only:** `episodes/active/issue-447-*.md`
**CREATE:** `.agent-work/epic418-h-447/episode-delta.json`
**DELETE / UNTRACK:** the paths in Parts 2 and 3 of the implementer handoff
**EDIT:** the pruned/retargeted test files; `scripts/verify_retirement.py` — **one comment** at the
`retired-path-still-tracked` leg, **no logic change** (diff it and confirm comments only).

Not in scope for g4: the spine templates, the installer, any prose in `skills/*/SKILL.md`,
`commander-core.md`, or `docs/` — that is g5.

**Fenced — a concurrent Commander owns these. If touched, that is a BLOCK and I need to know
immediately:** `scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py`,
`scripts/gauge_reader.py`, `docs/GAUGE_WRITER_HOOK.md`.

## Constraints the Implementation Must Respect
- **Record stores are never hand-edited.** Verify by blob OID, not by inspection.
- `python`, **never** `py`, including in your own commands.
- Prefix suite runs `FORCE_COLOR=0 NO_COLOR=1` — a colourised environment produces 10 phantom
  `HARNESS ERROR` failures in `tests/test_mutation_floor.py`. Commander-measured; not a regression.
  Baseline at `100a33c` was **1716 passed, 0 failed**.
- Windows: `encoding='utf-8', newline='\n'` on every write.
- Do not commit, push, or change git state — **including `git stash`, `git restore` and
  `git reset`**. This gate's value is in the staged index; disturbing it destroys the evidence.
- If you mutate a file to red-prove something, back it up in **binary**, restore byte-identically,
  and verify the restore.
- Use your own session scratchpad for temp files, **never** `/tmp`.
- No Fable at any tier; cap any dispatch at Opus and name the model.

## Map Anchors (inbound)
- **Structural:** `struct:episodes/README.md`, `struct:docs/EPISODE_STORE.md`,
  `struct:scripts/verify_retirement.py` (comment only).
- **Capability:** `capability:episode-store`; `capability:run-closeout-learning`.
- **Constraints:** `constraint:episodes-are-not-prescriptions` — **THE constraint, and the carry is
  exactly where it is at risk**; `constraint:record-stores-never-hand-edited`;
  `constraint:doctrine-lives-in-docs-agents`.
- **Decisions:** `decision:episodes-replace-both` `@grade: settled/human`;
  `decision:untrack-do-not-delete` `@grade: settled/measured`. A contradiction with a
  `settled/human` anchor is a decision candidate to float back, not to revise in place.
- **Evidence expectations:** `claim:suite-no-failures`.

## Evidence Produced — reproduce, do not read
| command | claimed |
|---|---|
| `python scripts/query_episodes.py select --field run --value issue-447` | count 8 |
| `python scripts/verify_episode_captured.py issue-447 --store-root episodes` | 0 |
| `... --phase archive` | 0 |
| `git ls-files --error-unmatch` both retired paths | non-zero |
| installed `verify_agent_feedback.py epic418-h-447 --phase feedback` | 1 → 1, unchanged |
| `python scripts/verify_retirement.py \| cut -f1 \| sort -u` | `retired-path-still-tracked` gone |
| `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` | 1 failed (the known negative control) |

Post-commit expectation the implementer states: **1618 passed, 0 failed** (1716 − 85 deleted − 13
pruned). It also says its own journal recorded 1703 and that that number is wrong. Re-derive the
arithmetic yourself and say whether 1618 is right — a number carried in prose and never re-derived
is one of this run's own recorded findings.

## Out-of-scope observation the implementer raised — confirm or refute it
The migration precedent the handoff pointed at, `episodes/active/issue-308-001.md`, has an
**imperative `workaround` of its own** (*"Give the harness the same fail-safe discipline as the
production code under test: wrap per-iteration work in try/except…"*). If true, the precedent
teaches the very inversion this gate exists to prevent. Confirm it, and say whether you think the
existing store needs an `amend-assertion` pass — but note `decision:store-hardening-out-of-scope`
says general store quality work is a **different job**, so this is a float, not a fix.

## Suggested Model Tier
**Opus** — the load-bearing check is a reading of eight prose statements for imperative force, which
no mechanical check catches. No Fable.

## Stop Conditions
BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, a fenced file was
touched, plain `git rm` was used, any existing episode was modified or hand-edited, an assertion
was synthesised rather than grounded, or any `workaround` still reads as a rule.

## Return Format
Write `REVIEW_RESULT` to `.agent-work/epic418-h-447/results/g4-REVIEW_RESULT.md` with an explicit
**APPROVE** or **BLOCK** on its own line, per-check findings (one per close criterion and per
constraint, each with the command you ran and its **real** exit code), your verdict on all eight
`workaround` statements individually, blockers, out-of-scope observations, and workflow feedback.
Deliver the substance as your final message too.
