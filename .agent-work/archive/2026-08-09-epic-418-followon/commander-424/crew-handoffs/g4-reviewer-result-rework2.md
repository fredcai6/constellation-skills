# Review Result

## Assigned Gate
`g4-review` (rework 2, attempt 3) — issue #424, workstream F, epic #418

## Result
BLOCK

## Handoff compliance
The substance of what this round asked for is delivered. DC5's verdict now leads with the
pre-registered raw-invocation-attempts metric as **PASS**, unhedged, in both the headline table and
the "DC5 verdict: PASS on the pre-registered metric" section header ("Primary result... the door
wins"). The productive-invocation decomposition is correctly demoted to a labelled, post-hoc,
secondary/bounding role. Observation (b) is correctly marked as pre-existing rather than post-hoc —
I independently confirmed this against attempt-1 artifacts: `crew-handoffs/g4-reviewer-handoff.md`
line 32 already reported "10 tool calls carrying them, MCP 19/17" in the *original* pre-fix handoff,
while grepping that same handoff and result for "productive" / "help read" returns nothing — (a)/(c)
really are new to this rework, (b) really did predate it. The n=2 bounding and front-loading caveats
survive intact, and are if anything *more* visible now (the front-loading caveat is pulled into the
headline table itself). Every re-derivable number reproduces exactly (see Evidence verdict).

**But two of the handoff's own six "what to check" items are not fully satisfied.** Read as a
first-time reader (check 1), MEASUREMENT.md's secondary-observations block contains a leftover,
unedited duplicate paragraph immediately after observation (c) that restates its point in flatter,
more negative, unmitigated language — sitting exactly where the failure mode you named ("a formal
pass that still reads like a negative") could actually land. And `tc1` (check 5) is not correctly
fixed: the false "agree in direction and magnitude" claim is gone, but the arithmetic now cited to
support "they do not agree in magnitude" computes the wrong quantity — one that is internally
inconsistent with the very claim it's attached to, and that quietly drops the real per-order
magnitude gap (2 vs 6) that motivated the original finding.

Both defects are narrow, mechanical, one-paragraph fixes. Neither reopens the substantive
PASS-vs-negative question, which I judge resolved.

## Scope drift
Stayed strictly read/verify-only in the f-424 worktree. No measurement arm was rerun. Only the six
scorer/assert/control commands named in the handoff were executed, all reading existing
`evidence/g4-dc5/rep*/record.jsonl` files; nothing under `evidence/g4-dc5/` was written by this review.

## Evidence verdict
Reran all six verification commands foreground:

- `score_arm.py` on all four arms reproduces `rep1-cli=21/5, rep2-cli=23/7, rep1-mcp=19/0,
  rep2-mcp=17/0` exactly, matching MEASUREMENT.md's Results table (means CLI 22.0, MCP 18.0, 18%
  reduction: (22-18)/22 = 18.2%, confirmed).
- `assert_dc1.py` reproduces DC1 PASS, `malformed_calls=0` on both MCP reps, `EXIT=0`.
- `control_scorer.py` reproduces all 7 `[PASS]` controls verbatim, matching the block MEASUREMENT.md
  quotes.

Instruments confirmed untouched since attempt-2: `evidence/g4-dc5/score_arm.py` and
`control_scorer.py` are untracked (no meaningful `git diff` against a commit), but neither file's
mtime is newer than the attempt-2 result — no write to either instrument has happened since that
review signed off on them. DC1, DC6 (arrival/action/non-compliance split, the `dc6-mcp` UNMEASURED
call) are unchanged text from the version attempt-2 already verified in full, and this round's diff
touches only `MEASUREMENT.md` prose — `evidence/g4-dc5/*` content is identical.

## Code/doc quality
Two rigor/editing defects, both narrow:

1. **Leftover duplicate paragraph.** MEASUREMENT.md lines 216–225: secondary observation (c) —
   "The targeted fumble class never appeared... Same direction, different mechanism, and worth
   knowing which one was actually bought" — is immediately followed by an unlabelled, near-verbatim
   restatement of the same malformed-calls point, but *without* that mitigating close. The leftover
   instead ends: "So the headline benefit a typed door is supposed to deliver had, on this task,
   nothing to absorb." Verified by grep: "did not fumble the argument shape" appears at both line
   217 and line 223; no other verbatim-line duplication exists elsewhere in the file (whole-file
   repeated-line scan). This reads as an unedited draft remnant, not a deliberate second observation.
   **Fix: delete lines 222–225, keep (c) as written.**

2. **`tc1`'s replacement arithmetic doesn't support its own claim.** The order-control paragraph
   (lines 123–133) now reads: "They do not agree in magnitude — the CLI arm's attempts differ by 2
   between orders (21 vs 23) and the MCP arm's by 2 (19 vs 17)." Recomputed independently from the
   published Results table: `21 vs 23` and `19 vs 17` are each arm's own *within-arm, across-order*
   spread — and both are identical (2 and 2), which if anything supports agreement, not disagreement.
   The quantity that actually demonstrates magnitude disagreement, and that motivated the original
   `tc1` finding ("+2 vs +6, a 3x difference"), is the **per-order CLI-minus-MCP gap**: order "CLI
   first" gives 21−19=2; order "MCP first" gives 23−17=6. That 2-vs-6 figure — the sharper, more
   informative instability bound — is nowhere in the v3 text; it has been replaced by a pair of
   numbers that don't logically make the stated point. **Fix: cite the per-order gap (2 vs 6), not
   the within-arm spread.**

Everything else meets Verification Discipline (`CREW_CONTEXT.md`): the positive controls are
load-bearing (re-confirmed by rerun), numbers are asserted against re-run behavior rather than only
described in prose, and the revision note names the full three-version correction history rather
than quietly republishing corrected numbers.

## Reconciliation check
No architecture/structural-baseline divergence — this gate produces a measurement write-up and
disposable fixtures, not shipped code. Nothing to reconcile.

## Blockers
- **Leftover duplicate paragraph, MEASUREMENT.md lines 222–225**, restating secondary observation
  (c) in flatter, more negative, unmitigated language immediately after (c)'s own mitigated version —
  the exact undermining-prose pattern this round asked me to hunt for. Delete it.
- **`tc1`'s fix cites the wrong quantity.** The order-control paragraph's "do not agree in magnitude"
  claim is backed by two equal, non-supporting numbers (the within-arm cross-order spread, 2 and 2)
  instead of the per-order CLI-vs-MCP gap (2 vs 6) that is the actual evidence for magnitude
  disagreement and that motivated the original finding. Restate the parenthetical using 2 vs 6.

Both are one-paragraph edits. Neither changes the DC5 headline number (independently re-verified,
22.0 vs 18.0, 18%) and neither reopens the post-hoc/pre-registered framing question, which this
review judges resolved on its merits.

## Out-of-scope observations
- None beyond the two blockers above, which are in-scope for this gate.

## Workflow Feedback

- **Handoff gaps:** none material. The four numbered concerns and the explicit six-item close list
  were precise, and concern 4 (overcorrection toward the door) is what led me to the `tc1` arithmetic
  defect even though I went looking for something else (a softened headline claim) and found this
  instead — the framing of "check for overcorrection" was broad enough to catch a failure mode its
  own author hadn't specifically named.
- **Context rediscovered:** none beyond what attempt-2's result already carried forward cleanly —
  the attempt-1/attempt-2 handoffs and results gave a complete, groppable timeline for confirming
  observation (b) predates the correction (r8) without needing anything not already in the repo.
- **Instructions improvised around:** none. Appending five rework-specific survey items (`r7`–`r11`)
  on top of the template's `r0`–`r6`, doing the deep technical items first and circling back to the
  holistic `r1`/`r4` findings informed by them, worked the same way it did in attempt-2's review —
  confirms that pattern is reproducible, not a one-off.
- **What would have made this easier:** nothing new this round. The same suggestion from attempt-1/
  attempt-2 stands (a `--json` per-call dump alongside each `score.json`), but it wasn't needed here
  since no re-derivation from raw records was required — only re-running the existing scorer/control
  commands and independent arithmetic on the already-published Results table.

## Return status
`complete`
