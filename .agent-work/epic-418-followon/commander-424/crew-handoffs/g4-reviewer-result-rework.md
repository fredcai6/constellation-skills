# Review Result

## Assigned Gate
`g4-review` (rework, attempt 2) — issue #424, workstream F, epic #418

## Result
BLOCK

## Handoff compliance
Every re-derivation task the handoff asked for succeeds this time. `rep2-cli` independently
re-derives to **23 attempts / 7 absorbable fumbles**, by a parser written from scratch that never
imports `score_arm.py` (different code path: counts runtime `RAIL:`/`usage:` markers directly, no
reuse of the `max(static, runtime)` logic). `rep1-cli` (21/5), `rep1-mcp` (19/0), `rep2-mcp` (17/0)
did not move and nothing was over-corrected into existence. `control_scorer.py`'s controls are
load-bearing, not vacuous: I broke the loop-correction in a scratch copy of `score_arm.py` and
watched its control fail (`invocation_attempts=1`, expected 3, exit 1); I broke the MCP
client-schema-rejection control the same way (had to remove both the `"is not a valid"` pattern
*and* the `is_err` fallback before it failed — it has doubled coverage, not a flaw, but worth
knowing) — then restored both, confirmed the tracked `evidence/g4-dc5/score_arm.py` and
`control_scorer.py` were never touched (`git status` still shows them untracked and unmodified),
and reran the clean baseline (all 7 PASS).

**But the handoff's own central question gets a plain answer that blocks anyway: the
productive-invocation decomposition is post-hoc.** Not fabricated — the arithmetic is correct and
fully disclosed — but reached for. MEASUREMENT.md's own revision note and your rework handoff both
say, on the record, that the *original* basis for the DC5 negative was "the spreads overlap
completely" (raw totals). Correcting the loop bug flipped that: CLI 22.0 vs MCP 18.0, no longer
overlapping — a PASS on the pre-registered primary metric ("one invocation attempt, however
packaged," fixed *before* any arm ran). The productive/help-reads split that now carries the
verdict is new to this rework — it appears nowhere in any attempt-1 artifact (checked by grep
across the original handoff, the original result, and the original review survey) — and it was
introduced only after the pre-registered metric stopped supporting the negative.

It also has a construct-validity problem independent of timing: help-reads are the exact
friction category a self-documenting typed door claims to eliminate (MEASUREMENT.md's own text
elsewhere credits the CLI's help-reads with *avoiding* fumbles). Stripping that category out
before comparing arms is close to excluding the effect under test. And of three legitimate lenses
present in the data — raw totals (door wins), productive invocations (CLI wins), tool-calls/"acts
of attention" (CLI wins, and this lens *was* already in the original pre-fix write-up, so it is
not itself post-hoc) — the write-up keeps the two that preserve the pre-existing negative and
recasts the one pre-registered lens that doesn't as mere "onboarding cost." That's backwards: the
raw-totals metric is the one that was committed to in advance; the other two are the ex-post
reframings, yet it's treated the other way around.

## Scope drift
Stayed read/verify-only in the f-424 worktree. No arm was re-dispatched via `claude -p`. All
independent verification was (a) a from-scratch parser reading existing `record.jsonl` files, or
(b) exercising `score_arm.py`/`control_scorer.py` against synthetic fixtures and deliberately
broken **scratch copies** — the tracked evidence files were never written to.

## Evidence verdict
Raw records, the fixed scorer, the new `control_scorer.py`, and per-arm `score.json` are present
and internally consistent — every `score.json` reflects the fixed scorer's output (e.g.
`rep2-cli/score.json` shows 23/7, not the stale 18/2), confirming the published tables were
regenerated rather than hand-edited. The defect this round is not in evidence presence or
authenticity; it is in which verdict the now-correct evidence is used to support.

## Code/doc quality
Verification Discipline ("a check that cannot fail is indistinguishable from one that passed")
is substantially better honored than attempt 1: `control_scorer.py` exists because of that rule,
and I confirmed by breaking it that it is genuinely load-bearing rather than asserted on faith.
The write-up is transparent about its own history rather than quietly republishing corrected
numbers. One minor, carried-forward defect: the Order-control section still claims the two orders
"agree in direction and magnitude" though the corrected per-order gaps are +2 and +6 — already
flagged non-blocking in attempt 1 and unchanged by this rework's rewrite (logged as `tc1`).

## Reconciliation check
No architecture/structural-baseline divergence — this gate produces a measurement write-up and
disposable fixtures, not shipped code. The thing that needs reconciling is a decision, not an
architecture drift: which DC5 verdict ships as the gate's answer, now that the pre-registered
metric and the productive-invocation metric disagree.

## Blockers
- **The productive-invocation decomposition that carries the current DC5 verdict is post-hoc.**
  It replaced an invalidated argument only after the loop-fix correction moved the pre-registered
  primary metric (raw invocation attempts) to favor the door, it is not the unit fixed before the
  arms ran, and it strips out exactly the cost category (interface-learning reads) the door's
  value proposition claims to eliminate. Recommend: report the pre-registered raw-attempts result
  as DC5's primary finding (a PASS at the raw-total level) and demote the onboarding/productive-cost
  analysis to an explicitly-labeled secondary extrapolation about longer spines — or, if you judge
  the productive metric the truer one after all, say so explicitly and declare it primary rather
  than reaching for it after the fact.

## Out-of-scope observations
- **Triage candidate (`tc1`):** MEASUREMENT.md's Order-control section claims the two orders
  "agree in direction and magnitude." Direction agreement is real; magnitude is not (+2 vs +6, a
  3x difference). Flagged non-blocking in attempt 1's review, still unfixed in this rework's text.
  Recommend dropping "and magnitude" or stating the gap sizes and noting they differ.
- The MCP client-schema-rejection control in `control_scorer.py` has doubled coverage (a
  `SHAPE_PATTERNS` regex match *and* an independent `is_err` fallback both catch the same test
  fixture) — not a defect, but worth knowing before anyone assumes the pattern list alone is what
  that control exercises.

## Workflow Feedback

- **Handoff gaps:** none material. The four "be loud about" items and the six-item close list were
  precise and, unusually, the handoff explicitly pre-authorized the answer I ended up giving
  ("'it is post-hoc' is an answer I will accept and act on") — that framing made it easier to give
  a direct verdict instead of hedging.
- **Context rediscovered:** the fact that the *original* DC5 negative rested solely on "spreads
  overlap completely," with no productive/help-reads decomposition anywhere, is not stated
  explicitly in MEASUREMENT.md's revision note — the note says the old basis "is false" and "has
  been removed" but doesn't say what replaced it or when that replacement first appeared. I had to
  reconstruct that timeline by grepping the attempt-1 handoff, result, and survey files for
  "overlap" vs "productive." A one-line note in the revision section ("the productive-invocation
  framing is new to this rework, introduced to replace the invalidated overlap argument") would
  have made the post-hoc question answerable from the artifact alone rather than requiring
  cross-referencing three other files.
- **Instructions improvised around:** none. Appending six rework-specific survey items
  (`r7`-`r12`) on top of the template's `r0`-`r6` worked cleanly through `append`, and the survey
  engine allows visiting items out of declared order, which let me do the deep technical
  re-derivation (`r7`-`r12`) before circling back to write the holistic `r1`-`r6` findings informed
  by it — worth confirming that's intentional survey behavior rather than an oversight, since
  `checklist-engine.md`'s verb-loop summary doesn't call out that surveys, unlike gated plans,
  don't enforce start-order.
- **What would have made this easier:** a `--json` per-call dump alongside each `score.json` (as
  noted in attempt 1's feedback) would still have saved time — I ended up writing a second
  from-scratch parser rather than diffing against one.

## Return status
`complete`
