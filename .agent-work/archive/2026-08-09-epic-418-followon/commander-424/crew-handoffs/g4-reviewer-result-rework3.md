# Review Result

## Assigned Gate
`g4-review` (rework 3, attempt 4) — issue #424, workstream F, epic #418

## Result
APPROVE

## Handoff compliance
Both of this round's two named edits land, and the propagation the handoff described checks out.

**Fix 1 — duplicate paragraph.** MEASUREMENT.md's secondary observation (c) (lines 225–229) now
ends once, on its mitigated close: "Same direction, different mechanism, and worth knowing which
one was actually bought." The leftover unedited remnant that attempt-3 blocked on — the flatter,
more negative restatement ending "…had, on this task, nothing to absorb." — is gone: a grep for
that exact phrase returns zero hits. The shared sentence "did not fumble the argument shape,"
which appeared twice (lines 217 and 223) in the version attempt-3 reviewed, now appears exactly
once (line 226). A whole-file scan for repeated non-blank lines finds only markdown boilerplate
(table separators, code fences) — no remaining content duplication anywhere in the file.

**Fix 2 — `tc1`'s arithmetic.** The order-control paragraph (lines 133–138) now reads: "The
CLI-minus-MCP gap is **2 attempts** in rep1 (21 vs 19) and **6** in rep2 (23 vs 17) — the same
direction, but a threefold difference in size." I reran `score_arm.py` on all four arms this
session and reproduced 21/19/23/17 exactly, confirming 21−19=2 and 23−17=6 against the raw
records, not just the prose. 6÷2=3, matching the stated "threefold difference." The paragraph
concludes the order control "supports 'no order effect large enough to reverse any comparison at
n=2'; it does **not** support any claim about the size of the effect" — direction only, as the
prior block demanded. This is the per-order CLI-vs-MCP gap that motivated the original `tc1`
finding, not the within-arm cross-order spread (2 and 2) that wrongly stood in for it last round.

**Propagation.** The consequence is now stated consistently in three places: the headline table
("The 18% is a midpoint, not an estimate: the per-order gap is 2 and 6"), the DC5 PASS section
("The 18% is the midpoint of two runs that disagree substantially about size… read it as 'a
reduction, direction consistent', not as an effect-size estimate. See 'Order control' above"),
and the order-control paragraph itself, which additionally computes a 9%–26% range. I checked
that range independently: 2/21=9.5%, 6/23=26.1%, midpoint≈17.8%≈18% — internally consistent, not
just asserted.

## Scope drift
Stayed strictly read/verify-only in the f-424 worktree. No measurement arm was rerun — only the
five commands the handoff named (`score_arm.py` ×4, `control_scorer.py`), which read existing
`evidence/g4-dc5/rep*/record.jsonl` and produced no new writes (`score.json` mtimes in each arm
directory predate this session, left over from attempt-3's own run of the same commands).

## Evidence verdict
Reran all five verification commands foreground:
- `score_arm.py` on all four arms reproduces `rep1-cli=21/5, rep2-cli=23/7, rep1-mcp=19/0,
  rep2-mcp=17/0` exactly, matching MEASUREMENT.md's Results table and the 2-vs-6 figures the
  order-control paragraph now cites.
- `control_scorer.py` reproduces all 7 `[PASS]` controls verbatim.

Instruments confirmed untouched since attempt-2: `evidence/g4-dc5/score_arm.py` (mtime
1786319206) and `control_scorer.py` (mtime 1786319174) both predate the attempt-2 review result's
mtime (1786320192) — no write to either since that review signed off on them, matching attempt-3's
own independent finding on the same question.

## Code/doc quality
No new rigor defects. Positive controls remain load-bearing (re-confirmed by rerun), numbers are
asserted against re-run behavior rather than trusted from prose, and the revision note at the
file's foot still names the full three-version correction history. `CREW_CONTEXT.md`'s
Verification Discipline is met.

## Reconciliation check
No architecture/structural-baseline divergence — this gate produces a measurement write-up and
disposable fixtures, not shipped code. Nothing to reconcile.

## Blockers
- None.

## Out-of-scope observations
- None.

## Workflow Feedback

- **Handoff gaps:** none material. The handoff was unusually precise for a fourth round — it
  quoted the exact replacement text for both fixes and named the three propagation sites in
  advance, which let this review check the claim against the artifact directly rather than having
  to first reconstruct what "fixed" should look like.
- **Context rediscovered:** none beyond what attempt-3's result already carried forward cleanly.
  Its result file quoted enough of the previously-reviewed text (Results table, DC1/DC6 headline
  rows, control block, observation (b)) that this round's no-drift check could diff against those
  quotes directly, without needing a stored prior-version snapshot of MEASUREMENT.md (the file is
  untracked, so `git diff` against history isn't available — the prior review's own quotations
  were the only baseline, and they were sufficient here, but a project that wants no-drift checks
  to be cheap across an untracked working file would benefit from a lightweight snapshot-on-block
  convention).
- **Instructions improvised around:** none. This round's survey used the same pattern as
  attempt-3's (r0–r6 template items plus rework-specific appended items, r7–r10 here) mapped
  directly onto the handoff's five numbered "what to check" items; that pattern continues to hold
  up across rounds.
- **What would have made this easier:** nothing new this round. The suggestion from prior rounds
  (a `--json` per-call dump alongside each `score.json`) still stands but wasn't needed here.

## Return status
`complete`
