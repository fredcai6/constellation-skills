# Reviewer Handoff — g2-review RE-REVIEW (attempt 2)

## This is a FOCUSED re-review, not a fresh one

`g2-review` returned **BLOCK** on attempt 1 with three blockers. I adjudicated them, reopened
`g2-implement`, and the rework has landed. **You are reviewing the REWORK ONLY.**

**Attempt 1's APPROVE findings stand and are NOT reopened**: the per-field derivation traces, the
seven call-site mutations (6 of 7 caught — the wiring is proven not ceremonial), the `refusals`
additivity proof, `EPISODE_STORE.md:781`, the `#344` latency claim, and the HUNT 3 rulings.
Read attempt 1's result for context but do not redo it:
`.agent-work/issue-305/crew/g2-review-result.md`

**The rework's own account:** `.agent-work/issue-305/crew/g2-implement-rework-result.md`

## Survey State Location

`.agent-work/issue-305/g2-review-rework/review.json` — **never** the worktree root. Drive it with
the **worktree's** `scripts/checklist_engine.py`. On a survey, `record` is the re-record verb;
`advance`/`reopen` refuse as gated-only. `--session-id` is **required** by `consolidate` and must
follow the verb.

## The diff

```
cd C:/Programs/constellation-skills-wt/e298-305
git diff 3db2763~1..3db2763 -- scripts/ tests/ docs/
```

Three files: `scripts/episode_capture.py`, `tests/test_episode_fields.py`,
`docs/CHECKLIST_SCHEMA.md`. Everything is committed; `git status --porcelain` must be clean.

## What the rework was told to do

1. **Fix shape B** — `reopen_total()` sums per-task `rework_count` alone; the journal witness,
   `find_spine_path()`, and the `spine_path` plumbing are **deleted** (~84 lines).
2. **A discriminating test** — because reviewer mutation **M5 survived** on attempt 1: replacing
   the whole two-witness `max` with `_rework_total` alone left all 63 episode tests green, so the
   reconciliation had **no test that discriminated it**.
3. **Correct the falsified "neither can over-count" invariant** everywhere it is asserted in prose.
4. **Correct `docs/CHECKLIST_SCHEMA.md`** on three measured points (CLI-boundary-alone claim,
   the malformed-verb example, and run-scoped → checklist-scoped) plus the composer comment.

---

# WHAT I NEED FROM YOU

## 1. A mutation outside BOTH shipped sets — this is the whole point of your dispatch

I cannot audit my own falsifiability, and neither can the implementer. **Two mutations are already
spent; do not repeat either:**

- **The implementer's:** restored the old `max(journal, rework)` expression. Reported RED with
  `2 != 1` (start seam) and `4 != 3` (reopen seam).
- **Mine (Commander, run and reverted; `episode_capture.py` blob OID verified identical to HEAD
  afterwards):** re-inflated the count by the escalation tally read from `cl["blockers"]`, without
  restoring the deleted journal reader. Both new tests went RED (`5 != 3` on the reopen-seam case).

**Devise a third, different one.** Suggestions, not a menu — pick better if you see better:
break the **call site** rather than the callee (ceremonial wiring stays green otherwise); make
`reopen_total` return a plausible constant; make it read a *different* task's `rework_count`; make
it silently drop the largest contributor. **Confirm the suite catches it, and say what you tried
that it did NOT catch** — a mutation that survives is the finding, not a failure.

## 2. Is the new test actually both-seams, or does it just claim to be?

The reviewer of attempt 1 measured that the over-count is **`E` at a `start` seam** but **`E−1` at
a `reopen` seam** — the in-flight verb's own journal line is not yet written, so **at `E=1` the
inflation is exactly cancelled and a reopen-only test passes on broken code.**

The implementer says it handled this by using **two** escalations in the reopen-seam case. **Verify
that is really what the test does**, and that the start-seam case is genuinely a `start` seam.
A test environment that cannot reach the failing condition is as vacuous as a predicate that cannot
discriminate.

Also confirm each test still **asserts the fixture reproduces the divergence** (journal lines vs.
rework total). Without that, the tests could drift quietly green if the fixture stopped escalating.

## 3. Is fix B complete, and is its stated cost honest?

- Any **dead references** to the deleted `journal_reopens` / `find_spine_path` / `spine_path`
  plumbing? (I grepped repo-wide and found none — **that is my claim, so check it.**)
- Is the **under-count cost real and correctly described**? The docstring concedes that an `amend`
  dropping a `pending` gate with `rework_count > 0` loses those reopens. **Confirm that path is
  actually reachable** — if it is *not*, the docstring overstates the cost, and if it is reachable
  in a way the docstring understates, that is a finding.
- **Deviation to adjudicate:** the implementer folded `_rework_total()` **into** `reopen_total()`
  rather than keeping it as a private helper, on the reasoning that with one witness left, two
  names for one sum is indirection with no reader. I am inclined to accept. **Confirm the behaviour
  is identical** (including the `None`-on-malformed-checklist path and the bool-is-not-int guard),
  and say if you disagree.

## 4. Are the doc and prose corrections TRUE as written?

The implementer says it **re-measured all three** schema-doc claims itself rather than trusting my
handoff. **Spot-check at least one by measurement, not by reading.** The three:
1. The arming write `cl.setdefault("refusals", 0)` is inside `claim()`, a verb function — so
   "written by the CLI boundary alone, never by a verb function" was wrong.
2. A malformed verb exits via argparse with code 2 **before the checklist loads**, so it is never
   counted (`checklist_engine.py frobnicate a` → exit 2, counter unmoved).
3. The field is **checklist-scoped**: a foreign session's lease-conflict refusal increments the
   owning run's tally.

The implementer also found a **third** falsified-prose site the handoff missed (`ReopensFieldTests`'
class docstring said "`reopens` comes from the JOURNAL") and says a repo-wide sweep found no
fourth. **Verify the sweep** — a wrong comment is a correctness defect here, and this is the very
invariant the gate falsified.

**ADJUDICATED, do not reopen:** `refusals` gets a **documentation** fix, not a semantics change.
The attribution question is filed as **#367**. Fix shape **B** is ruled. Do not re-litigate either.

## 5. Handoff error to be aware of

My rework handoff said the falsified test docstring was in `tests/test_episode_capture.py`; it is
in `tests/test_episode_fields.py:383`. The implementer caught it and said so, correctly — **the
code wins**. Flagged so you do not chase the wrong file.

---

## Rulings in force — do NOT reopen

Seam placement · episode-store location · `#327` · `#362` · `#359` (known, travelling in the PR
body) · `constraint:frozen-field-group` · fix shape B · the `refusals` doc-not-code ruling.

## Standing constraints

- **`python -m pytest`, not `py`.** Baseline to beat: **1472 passed / 2 skipped / 472 subtests**
  (I ran it myself post-rework). `Path.read_text(newline=...)` is 3.13+ and fails CI;
  `write_text(newline=...)` is 3.10+ and is safe. A local green is never the gate.
- Explicit `encoding='utf-8', newline='\n'` on every write. Compare **normalized content or blob
  OIDs, never raw bytes** (#319).
- **Do not touch `C:/Programs/constellation-skills`** or any sibling worktree. Commit nothing.
- `--finding` text with backticks is shell-mangled and silently drops words.

## Protocol

**If something here proves wrong, tell me and PROCEED with the rest.** If the code contradicts this
handoff, **the code wins — say so.** My claims in section 3 (no dead references) and section 4 (the
sweep) are exactly the kind I have gotten wrong before; treat them as claims.

## Return Shape

Write to **`.agent-work/issue-305/crew/g2-review-rework-result.md`**. Verdict
**APPROVE / APPROVE-WITH-FOLLOWUPS / BLOCK**, covering:

1. Your independent mutation — what you broke, what caught it, and **what survived**.
2. Both-seams verification of the new test.
3. Fix B completeness, the under-count cost's honesty, and your ruling on the fold-in deviation.
4. The doc/prose corrections, with at least one **re-measured**.
5. Anything you deviated on.
6. Suite result via `python -m pytest`.
