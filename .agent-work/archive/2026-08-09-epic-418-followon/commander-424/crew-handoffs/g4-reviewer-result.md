# Review Result

## Assigned Gate
`g4-review` — independent re-derivation of the DC5 (and DC1/DC6) measurement, issue #424 workstream F

## Result
`BLOCK`

BLOCK

## Handoff compliance
The handoff asked for an independent re-derivation of MEASUREMENT.md's headline numbers, not a
re-run of the arms, and named ten close criteria plus four things to be "loud about." All ten
were driven through the reviewer survey (`.agent-work/epic-418-followon/commander-424/g4-review/review.json`,
items r7–r16) and are individually recorded there with evidence. Full survey engine-driven from
claim through consolidate; verdict BLOCK.

## Scope drift
None. Worked read/verify-only inside `/home/tommy/projects/constellation-skills-wt/f-424`. No
measurement arm was re-dispatched. Two forms of "own independent means" were used, both
explicitly sanctioned by the handoff: (a) hand-parsing existing `record.jsonl` files with my own
script, independent of `score_arm.py`; (b) exercising `score_arm.py` against small synthetic
`record.jsonl` fixtures I authored in my scratchpad, to positive-control the far-side detector —
this tests the scorer's mechanism, not a rerun of an arm (same logic the handoff draws from DC3's
positive-control requirement).

## Evidence verdict
Evidence is present and authentic (raw records, scorer, DC1 assertion, fixtures, per-arm
artifacts, all in `evidence/g4-dc5/`, all dated together). The defect is not in evidence presence
— it is that one of the four headline numbers computed *from* that evidence is wrong.

**The blocking finding.** Independently parsing `rep2-cli/record.jsonl` by hand, not by re-running
`score_arm.py`, I found its third Bash tool_use is a shell for-loop:

```
for cmd in claim start attest advance record release; do
echo "=== $cmd ==="
python3 scripts/checklist_engine.py $cmd --help 2>&1
done
```

The tool_result contains six distinct `usage: checklist_engine.py <subcmd>` blocks — the engine
really was invoked six times. `score_arm.py`'s `engine_invocations()` counts *static occurrences
of the substring* `"checklist_engine.py"` in the Bash command's source text, which is **1** for
this command (the string appears once, inside the loop body), not 6. The call is credited as 1
invocation attempt / 1 usage-read instead of 6/6.

- Reported: `rep2-cli` = 18 invocation attempts, 2 absorbable fumbles.
- True, by direct read of the record: **23 invocation attempts, 7 absorbable fumbles** (18+5,
  2+5).

I checked every other Bash command in both CLI arms for the same pattern (`for `, `while `,
`xargs`, `eval`, `$(`) and found exactly one instance, confined to this one call. `rep1-cli`'s own
4-invocation command is four literal, non-looped lines, each mentioning the engine once, and its
static count is correct (verified against 4 distinct usage blocks in its result text).

This is not a matter of interpretation — the handoff's own governing rule states it plainly: **"A
number you cannot re-derive is a BLOCK."** I could not re-derive `rep2-cli`'s reported number from
the raw record.

**Why this is load-bearing, not cosmetic.** With the correction, the per-arm attempt-count spreads
no longer overlap at all: CLI `[21, 23]` vs MCP `[19, 17]`, versus the reported (overlapping)
`[18, 21]` vs `[17, 19]`. MEASUREMENT.md's central argument for the negative — "per-arm spreads...
overlap it completely" — is not true of the corrected data. I am not asserting the corrected
numbers prove DC5 should have passed (n=2 is still n=2, and the "acts of attention" reading still
favors MCP either way); I am asserting the write-up's own stated basis for confidence in the
negative changes once the record is read correctly, and that is exactly the kind of thing this
gate exists to catch.

**The undisclosed-correction hunt (criterion 4) turned this up as a side effect.** MEASUREMENT.md
states "Two corrections made to the unit mid-measurement, both stated because both matter." Both
disclosed corrections (batching → toward the door; help-output → against the door) are real,
correctly applied, and correctly signed — I verified both independently. But there is a third,
undisclosed adjustment baked silently into the counting instrument: the loop-undercounting bug
above. It isn't a deliberate methodological choice like the other two (no stated rationale, no
disclosed direction) — it's an uncaught bug — but it moves a headline number exactly the way an
undisclosed correction would, and the handoff asked me to look hard for exactly this.

## Code/doc quality
MEASUREMENT.md itself is well-written per `constellation-how-to-talk` and follows
`CREW_CONTEXT.md`'s Verification Discipline in spirit (states scope, reports the negative as a
complete result, names exact commands). The one place it doesn't follow that discipline is the
place that broke: **"A check that cannot fail is indistinguishable from one that passed."**
`score_arm.py`'s invocation counter was never positive-controlled against a looped/batched shell
command — the exact shape that broke it. Fowler pass (`g4-review/fowler-pass.json`, verified
`verify_fowler_pass.py` exit 0): one smell flagged (long-method on `score()` — the per-call
classification logic would likely have had its bug caught sooner if isolated and unit-tested on
its own), one overridden with a logged reason (comments-as-deodorant — the extensive rationale
comments are decision documentation for an independent auditor, not compensation for unclear
code; removing them would have removed information this exact review needed).

## Map impact verdict
Not applicable — no shipped code/architecture change; this gate produces a measurement write-up
and disposable scratch fixtures under `evidence/g4-dc5/`.

## Reconciliation check
None. Nothing here diverges from recorded architecture; Cartographer reconciliation is not
implicated.

## Blockers
- **`rep2-cli`'s reported invocation-attempt/fumble counts do not re-derive from the raw record.**
  True count is 23/7, not 18/2, because `score_arm.py`'s `engine_invocations()` counts static
  substring occurrences of `checklist_engine.py` in Bash command text rather than actual runtime
  invocations, silently undercounting a 6-way shell for-loop as 1. This is load-bearing: corrected
  per-arm CLI/MCP attempt-count spreads no longer overlap, materially changing the strength of the
  stated basis for the DC5 negative. Fix the counter (or forbid loop-packaged invocations and
  re-measure), re-score `rep2-cli`, and re-derive the DC5 table, means, and the "spreads overlap
  completely" claim before this gate can close.

## Out-of-scope observations
- **Triage candidate (logged, `tc1` in the survey):** `score_arm.py`'s `engine_invocations()`
  should count actual invocations (e.g., from `usage: checklist_engine.py <subcmd>` / RAIL-banner
  occurrences in the tool_result) rather than static command-text substring occurrences, with a
  positive-control fixture exercising it against a loop. This is the mechanical fix underlying the
  blocker above; not applied here per reviewer scope (verify and report, not fix).
- **Triage candidate (logged, `tc2` in the survey):** the far-side-recovery detector's
  `INSPECT_TOOLS = {Read, Grep, Glob}` excludes `Bash`, but the CLI arm's `--allowedTools` is
  `Bash Write Read` and Bash is its dominant/near-exclusive tool (Read was called once across both
  CLI reps combined). A Bash-based state inspection after a failure (e.g. `cat spine.json`) is
  silently invisible to the detector — an arm-asymmetric blind spot, since the MCP arm has no Bash
  tool at all and so no equivalent gap. I positive-controlled the detector directly (a synthetic
  `record.jsonl`, not a rerun of any arm) and confirmed it CAN fire via `Read` — so this is not the
  "structurally incapable of firing" BLOCK trigger the handoff named, and I graded r12 pass on that
  basis. But in the actual dataset `shape_errors=0` and `other_errors=0` in all four arms, so the
  far-side channel had zero real trigger events to react to regardless of tool coverage — "zero
  far-side recoveries" is true but untested by this measurement, and MEASUREMENT.md's own text
  ("it simply was not there to move") already concedes this rather than overclaiming a tested null.
  Recommend disclosing the Bash blind spot and adding a Bash-based positive control if this
  instrument is reused on a task shape where CLI-arm failures actually occur.
- Minor wording precision (not a blocker): DC6's "the agent's very next calls were..." (arrival →
  action) skips over four intervening engine-state-refused attempts (`spine_start` ×2, one failed
  `advance`) visible in `dc6b-mcp/record.jsonl` between the arrival and the successful
  refresh-request attach. The qualitative claim (both named actions were eventually taken) is
  correct; the word "next" overstates immediacy.
- Minor wording precision (not a blocker): with r7's correction applied, the two measurement
  orders still agree in *direction* (CLI costs more than MCP in both `rep1` and `rep2`) but no
  longer agree closely in *magnitude* (+2 attempts vs +6, corrected) — "agree in direction and
  magnitude" overstates this once corrected.

## Workflow Feedback

- **Handoff gaps:** none material. The handoff's four "be loud about" items and ten close criteria
  were precise enough to drive directly into survey checks (r7–r16) with no interpretation needed.
- **Context rediscovered:** the handoff and MEASUREMENT.md both state the counting unit ("one
  invocation attempt... however packaged") but neither anticipates or tests the shell-loop case
  that breaks it. Nothing in the evidence directory hints at this gap — I only found it by reading
  every Bash command's actual result text end to end rather than trusting the command's static
  shape, which is exactly the "independent means, not just a rerun" instruction doing its job. If
  a future version of this instrument exists, a one-line note pointing re-derivers at "check every
  Bash call for loops/variable-substitution that could hide multiple invocations behind one string
  match" would save the next reviewer the full manual trace.
- **Instructions improvised around:** none — the reviewer-survey engine handled a
  measurement-write-up review (no code diff to a shipped surface) fine once I treated
  `evidence/g4-dc5/*.py` + `MEASUREMENT.md` as the "diff" for r1–r6 and the Fowler pass. One minor
  engine friction: `current` refuses `--session-id` (it's read-only and needs none), which isn't
  obviously stated in `checklist-engine.md`'s verb-loop summary; harmless once discovered.
- **What would have made this easier:** a `--json` per-call classification dump alongside each
  `score.json` (the handoff already suggests `--json` exists; the arm directories don't carry a
  pre-generated one) would have let me diff my hand-parse against the scorer's own per-call
  reasoning line-by-line instead of re-deriving the walk from scratch.

## Return status
`complete`
