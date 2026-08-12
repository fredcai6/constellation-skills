# Reviewer Handoff

## Gate
`g2-review` — work-id `r418-460`, issue #460, worktree `C:/Programs/constellation-skills-wt/r418-460`,
branch `epic-418/b-460-episodes-observations`.

## What you are reviewing
Commit **`7df136e6`** — `g2(#460): restate 27 prescriptive canon statements as records of what happened`.

The work is **already committed** (the Commander had to commit it: see "The committed-diff note"
below). Read it with `git show 7df136e6` or `git diff 7df136e6^ 7df136e6 -- episodes/`.

The implementer's own account, with its full grounding table, is at
`.agent-work/r418-460/crew-handoffs/g2-implement-result.md`. **Verify it; do not accept it.**

## The change
27 prescriptive statements in `episodes/active/` were rewritten as records of what happened, using
the `restate-assertion` op shipped by gate g1, through
`python scripts/apply_episode_delta.py --store-root episodes`. The deltas that produced them are at
`.agent-work/r418-460/deltas/` (4 files plus `classification.md`).

Reported count: **48 examined / 32 in scope / 27 restated**. 5 left alone as UNGROUNDED.
`git diff --stat` for the episode files: 24 files changed, 54 insertions, 27 deletions.

## Protected Intent
`episodes/` is a store of **things that happened**. A record that tells a future agent what to do is
the retired learning playbook growing back inside the store that replaced it.

The one unrecoverable failure of this gate is a **synthesised past-tense claim the record cannot
support** — a falsification of a permanent store. That is the thing you are here to catch. An
UNGROUNDED entry left alone is a *correct* outcome, not a gap; a confidently-worded restatement whose
grounding does not actually say what it is cited as saying is the defect.

## The wording standard (Commander-set; apply it, do not relitigate it)
A statement is an **OBSERVATION** when it says what was done, by whom or by what, in the run being
recorded — past tense, a real subject, no second person, no forward-aimed modal.

A statement is an **INSTRUCTION** when it is in imperative mood (a bare base-form verb opening a
sentence or clause with no subject), addresses a reader (`you`, `your`), or carries a deontic modal
aimed forward (`must`, `should`, `always`, `never` used as a directive).

**Deliberate exemption — not a defect.** `task-intent` is written in the bare infinitive by house
convention (`docs/EPISODE_STORE.md:171`). Leave it alone unless it addresses a reader in the second
person. Do not report untouched `task-intent` statements as misses.

## What to check — in priority order

**r1 — grounding (the load-bearing check; spend most of your time here).**
For **every one** of the 27 restatements, open the episode and confirm that the sibling assertion
cited as grounding *actually says what it is quoted as saying*, and that the AFTER text asserts
nothing beyond it. The implementer's table gives episode id, assertion id, BEFORE, AFTER and a
quoted grounding for each — check the quote against the file, not against the table.

Flag as a BLOCK any restatement where:
- the cited grounding does not contain the quoted text, or
- the AFTER text claims something happened that no assertion in that record supports, or
- a hedge in the original ("would", "should", "if") became a bare factual claim in the AFTER.

Four restatements are declared to have **dropped an ungrounded clause** while keeping the grounded
part, each drop named in the writer's own history reason. Confirm the drop is named and that what
remains is supported.

**r2 — the 5 UNGROUNDED are genuinely ungrounded.** `issue-304-g3-005.d2`, `issue-308-014.a5`,
`issue-308-015.a5`, `issue-308-017.a5`, `issue-308-019.a5`. Confirm each really lacks grounding
rather than having been skipped as hard. An over-large UNGROUNDED list is a miss too.

**r3 — the count is real.** Re-derive 48 / 32 / 27 by command over `episodes/active/`, not from the
report. Confirm the 32 in scope are exactly `issue-304-g3-*` (5), `issue-308-*` (25), `issue-309-*` (2).

**r4 — the 16 `issue-447-*` records.** The implementer claims all 16 were read in full (80
statements) and needed no restatement. Spot-check at least 4 of them against the wording standard
yourself. If any plainly instructs, that is a miss.

**r5 — the write path was honoured.** Every change under `episodes/` must trace to a named delta file
under `.agent-work/r418-460/deltas/`, and every writer invocation must carry `--store-root episodes`.
Confirm the original statement survives **verbatim** in each restated assertion's `history` line —
that is what makes this a record that grew rather than a record that was rewritten
(`docs/EPISODE_STORE.md` §5). Check that `history` was *appended to*, not replaced, where an
assertion already had one.

**r6 — no boundary was crossed.** `git show --stat 7df136e6` must show **nothing** under
`docs/agents/`, no change to `scripts/apply_episode_delta.py`, `docs/EPISODE_STORE.md`,
`scripts/checklist_engine.py`, `scripts/collect_feedback.py`, or
`scripts/verify_worktree_precondition_coverage.py`, and **no new file that accumulates advice for
future agents** under any name. The 22 doctrine candidates must exist **only** as a list inside
`g2-implement-result.md`. A file created to hold them is a BLOCK.

**r7 — the store still parses.** Confirm `render_episode(parse_episode(text)) == text` still holds
for the restated files, and that the suite is green.

## The committed-diff note — not a finding
`tests/test_episode_negative_control.py::test_canon_episode_store_untouched` asserts
`git status --porcelain episodes/` is empty, so it goes red for **any** uncommitted change under
`episodes/` — which is exactly what this gate produces. The implementer correctly raised it rather
than editing a test outside its scope; the Commander cleared it by committing. Do not re-report it
as a defect of this change. That the guard is wider than its own docstring's stated intent is filed
as triage candidate `tc1` and is not yours to fix.

## Test command
Exactly `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`. **Never `py` for pytest.** Capture the
**real** exit code (`echo EXIT=$?` immediately after the redirect, never through a pipe).
Post-g1 baseline: **1745 passed, 4 skipped, 677 subtests, exit 0**.

## Specific Exclusions
- **Never hand-edit `episodes/`.** If you need to demonstrate something, work on a copy outside the
  repo, and restore/verify pristine afterwards.
- Do not edit `docs/agents/*`, `docs/EPISODE_STORE.md` (that is gate g4),
  `scripts/apply_episode_delta.py`, `scripts/checklist_engine.py`, `scripts/collect_feedback.py`, or
  `scripts/verify_worktree_precondition_coverage.py`.
- Do not create any file that accumulates advice for future agents.
- Never create a file whose basename contains `findings`.
- Do not commit.

## Authority
Yours: the verdict, and every finding behind it.
Not yours: the wording standard; whether any candidate becomes doctrine; the `restate-assertion`
design decision (settled at g1 and ratified by the Admiral).

## Return Format
Write **REVIEW_RESULT** to
`C:/Programs/constellation-skills-wt/r418-460/.agent-work/r418-460/crew-handoffs/g2-review-result.md`,
with an explicit **APPROVE** or **BLOCK** verdict on its own line, the per-check findings above, and
for any BLOCK the exact episode id + assertion id + what is wrong. A result returned only as chat
text does not count — the file is what the Commander verifies.

Drive your own `REVIEW_SURVEY.json` under `.agent-work/r418-460/g2-review/` per the reviewer skill.

## Suggested Model Tier
Stronger (Opus). The whole difficulty is judging whether a past-tense sentence is supported by the
record it sits in.
