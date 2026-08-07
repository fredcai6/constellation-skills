# Reviewer Handoff — g3: rewire the closeout obligations onto episode capture

## Gate
`g3-review` — issue #447, epic-418 workstream H. Spine `.agent-work/epic418-h-447/execute.json`.

## Survey State Location
`.agent-work/epic418-h-447/g3-review/review.json` — under the issue workbench, **never at the
worktree root**.

## Worktree
`C:/Programs/constellation-skills-wt/epic418-h-447`, branch `epic-418/h-447-episodes-retirement`,
HEAD `dbf9a23`. The only tree you may write to. Absolute paths; your cwd resets between bash calls.

## What Was Implemented
The Commander and Admiral closeout obligations were swapped off the retired lessons playbook and
onto episode capture, and the installer stopped shipping the playbook's machinery.

```
scripts/install_constellation.py                         | 25 +-
skills/admiral/templates/ADMIRAL_SPINE.template.json     |  9 +-
skills/commander/templates/COMMANDER_SPINE.template.json |  9 +-
tests/data/store_mentions.approved.txt                   | 63 +
tests/test_install_constellation.py                      | 85 +-
```

## How to Inspect the Diff
The review target is the **UNCOMMITTED WORKING TREE**, not `git diff main...HEAD`.
`git status --porcelain` first, then `git diff`. HEAD is `dbf9a23`; everything before it is g1/g2
and already reviewed.

## Task Statement
Full implementer specification, which is also your contract:
`.agent-work/epic418-h-447/crew-handoffs/g3-IMPLEMENTER_HANDOFF.md`.
Implementer's result: `.agent-work/epic418-h-447/results/g3-IMPLEMENTER_RESULT.md`.

## The one thing that matters most
Episodes are a **record of what happened**, not a playbook. The human's constraint, verbatim,
2026-08-06:

> *"we shouldn't be reading the episodes like lessons, it's a store for things that happened to
> replace both feedback and lessons."*

**The named failure mode of this gate is a read path re-pointed at `episodes/`.** Playbook
machinery — adjudication, ripeness, apply-or-defer, `bank_reason`, dormancy, dispositions,
the lessons-auditor dispatch — was required to be **DELETED, not translated into episode
vocabulary**. Grade that first and grade it hard: a deletion that quietly became a rename is the
defect this whole run exists to fix, and it would pass every mechanical check in this handoff.

Read the two spine templates' new `feedback` / `closeout` imperatives **as an agent would**, and
ask: does any sentence here tell me to go read the store and condition my behaviour on what I
find? If yes, that is a BLOCK.

## Close Criteria
Each becomes a review check. **RE-RUN every command yourself.** Redirect to a file then
`echo $?` — a pipe captures the pipe's exit code.

1. `verify_retirement.py`'s **`replacement-absent` leg is gone** — both spines name
   `verify_episode_captured.py` in a task **imperative**, both bundles carry it, the script exists.
2. **`unapproved-store-mention` is zero**, and every new approval in
   `tests/data/store_mentions.approved.txt` carries a reason naming a **write** path, a bundle
   entry, or a re-staging block. **Read all 63 added lines.** An approval whose reason amounts to
   "an agent reads the store here" is a BLOCK — the census is the place this defect would hide.
3. Neither spine contains lesson / ripeness / apply-or-defer / `bank_reason` / dormancy /
   disposition vocabulary, and **no instruction anywhere tells an agent to read `episodes/`.**
4. The Commander `feedback` imperative carries this sentence **verbatim**:
   *"An episode is a record, not a rule: write what you observed, and do NOT write a rule for a
   future agent to follow — a rule to follow belongs in docs/agents/* and is a human's call."*
5. `feedback.c1` and `archive.c1` retargeted **in place**; `feedback.c2` and `closeout.c6` deleted;
   `archive.c4` `deny_globs` unchanged with both retired paths kept; **no other condition id
   changed, added, or renumbered.** Diff the condition-id lists of both templates before and after
   (`git show HEAD:<path>` vs the working copy) rather than reading the diff hunks — a renumber is
   easy to miss by eye.
6. Both templates still parse (`json.load`), the diff is **surgical** (single-digit line counts,
   not a whole-file rewrite), and **line endings are unchanged**: both files must be all-CRLF with
   **zero bare LF**. A text-mode rewrite that flips 134 line endings is the same class of defect as
   a `json.dump` round-trip. Check the bytes, not the diff.
7. The new install test is **GENERAL** — every `kind:"command"` postcondition in both installed
   spine templates must name a script that exists in that skill's installed `scripts/` directory.
   A test that only asserts the two specific new names is a BLOCK: the point is protecting every
   future rewiring. **Red-prove it yourself**: point a spine command at a nonexistent script, watch
   the test go red, restore from a byte backup, confirm byte-identical.
8. The Commander's own closeout path still works — the installed
   `C:/Users/fredc/.claude/skills/constellation-commander/scripts/verify_agent_feedback.py` runs
   with an **unchanged** exit code (implementer measured 1 → 1). Dropping a script from
   `SKILL_SCRIPT_BUNDLES` must not have deleted the already-installed copy.
9. No new suite failures beyond tests deliberately changed, each explained by name.

## Deviations the implementer declared — grade these on their merits, not on the letter
1. **`--store-root episodes` added to the `check` commands, not only the imperatives.** The
   handoff's literal `c1` string omitted it. Without it, an installed copy resolves the store under
   `~/.claude/skills/` and the gate exits 2 (REFUSED) every run. Judge whether the deviation serves
   the handoff's stated rationale; I believe it does.
2. **One clause trimmed beyond the letter** — the archive imperative's *"leaving the unified
   AGENT_FEEDBACK.md at the agent-work root"*, which contradicted the retargeted `archive.c1`.
   Confirm the **work-area move itself** is still instructed.
3. **`query_episodes.py` unbundled is a default, not a boundary** — comment at
   `scripts/install_constellation.py:141-159`. Verify the comment names all four routes around it
   (repo-relative execution, plain Read/Grep, the unfiltered `copytree` at ~line 915,
   `SCRIPT_RUNTIME_COMPANIONS`) and does **not** overclaim a structural guarantee.
4. **Admiral closeout renumbered 1–5** because the auditor that was step 1 is gone. Confirm steps
   3/4/5 (cartographer reconcile, hygiene, user acceptance) are byte-identical.

## Expected and NOT defects — do not BLOCK on these
- `python scripts/verify_retirement.py` still **exits 1**. Remaining legs are
  `retired-name-on-shipped-surface` (117) and `retired-path-still-tracked` (5). Both are **g4 and
  g5's work** — untracking the two files and their machinery, and the prose sweep. The guard going
  green is g6.
- `tests/test_retirement_guard.py::test_canon_is_clean` carries `xfail(strict=True)` and is
  expected to xfail while the tree is deliberately dirty.
- **Known escalation, already floated to the Commander, NOT the implementer's defect:** the
  `retired-name-on-shipped-surface` leg has **no approval mechanism**, so `archive.c4`'s
  `deny_globs` entries (which correctly name both retired paths as a re-staging block) can never be
  approved. The Commander owns the ruling. Do not BLOCK g3 on it — but **do** tell me if you think
  the implementer should have solved it inside this gate instead.

## Allowed Scope — flag anything outside it
```
skills/commander/templates/COMMANDER_SPINE.template.json
skills/admiral/templates/ADMIRAL_SPINE.template.json
scripts/install_constellation.py
tests/test_install_constellation.py
tests/data/store_mentions.approved.txt
```
Not in scope for g3 (they are g4/g5): deleting `apply_lessons_delta.py`,
`verify_lessons_applied.py`, `verify_agent_feedback.py`; untracking the two retired files; deleting
`skills/lessons-auditor/`; any prose in `skills/*/SKILL.md`, `commander-core.md`, or `docs/`;
writing any episode.

**Fenced — a concurrent Commander owns these. If they are touched, that is a BLOCK and I need to
know immediately:** `scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py`,
`scripts/gauge_reader.py`, `docs/GAUGE_WRITER_HOOK.md`.

## Constraints the Implementation Must Respect
- Raw-text surgical edits to the compact JSON templates; **no `json.load`/`json.dump`
  round-trip**. Verify by diff shape and by byte-level line-ending check, not by taking the claim.
- `python`, **never** `py` — including in your own commands.
- Never delete a postcondition with id `c1`; only terminal conditions deleted.
- Windows: `encoding='utf-8', newline='\n'` on every write.
- Scope discipline (Tommy's standing ruling, epic-418): build what needs to work and no more; a
  declined corner case carries a comment **at the code site** and is reported up. Verify each
  declined case actually has its comment where the result says it does.
- Use your own session scratchpad for temp files, **never** `/tmp` — a concurrent Commander shares
  it and has already polluted one evidence file this epic.
- No Fable at any tier; cap any dispatch at Opus and name the model.

## Map Anchors (inbound)
- **Structural:** `struct:skills/commander/templates/COMMANDER_SPINE.template.json`,
  `struct:skills/admiral/templates/ADMIRAL_SPINE.template.json`,
  `struct:scripts/install_constellation.py` (bundle level).
- **Capability:** `capability:run-closeout-learning` — this gate is where its owner changes;
  `capability:episode-store`.
- **Constraints:** `constraint:episodes-are-not-prescriptions` — **THE constraint**;
  `constraint:doctrine-lives-in-docs-agents`; `constraint:record-stores-never-hand-edited`.
- **Decisions:** `decision:episodes-replace-both` — one store of observations replaces two inboxes
  plus a playbook; **no successor playbook is created.** `@grade: settled/human`.
  `decision:untrack-do-not-delete` `@grade: settled/measured`.
  A contradiction with a `settled/human` anchor is a decision candidate to float back, not
  something to revise in place.
- **Evidence expectations:** `claim:suite-no-failures`.

## Evidence Produced — reproduce it, do not read it
| command | claimed exit |
|---|---|
| `python -m pytest tests/test_install_constellation.py -q` | 0 (103 passed, 371 subtests) |
| `json.load` both spines | 0 |
| `python scripts/verify_retirement.py` | 1 (122 findings, all g4/g5) |
| `python -m pytest tests/test_retirement_guard.py -q` | 0 (12 passed, 1 xfailed) |
| `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` | 0 — **1716 passed, 0 failed** |
| installed `verify_agent_feedback.py epic418-h-447 --phase feedback` | 1 → 1, unchanged |

Leg distribution claimed: `replacement-absent` 4→0, `unapproved-store-mention` 9→0,
`retired-name` 130→117, `retired-path` 5→5. Commander independently confirmed the post-change
distribution; confirm the rest.

**Suite runs must be prefixed `FORCE_COLOR=0 NO_COLOR=1`.** A colourised environment puts an ANSI
reset between `FAILED` and the node id, defeating `tests/test_mutation_floor.py:255`'s regex and
producing 10 phantom `HARNESS ERROR` failures. Commander-measured; not a regression.

## Suggested Model Tier
**Opus** — the load-bearing check is a reading of intent (was the playbook deleted or renamed?),
not a mechanical one. No Fable.

## Stop Conditions
BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, a fenced file was
touched, a `c1` was deleted or conditions renumbered, the templates were reflowed, or any surface
now instructs an agent to read the episode store.

## Return Format
Write `REVIEW_RESULT` to `.agent-work/epic418-h-447/results/g3-REVIEW_RESULT.md` with an explicit
**APPROVE** or **BLOCK** on its own line, per-check findings (one per close criterion and per
constraint, each with the command you ran and its **real** exit code), blockers, out-of-scope
observations, and workflow feedback. Deliver the substance as your final message too.
