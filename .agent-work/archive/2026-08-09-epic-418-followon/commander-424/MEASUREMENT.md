# MEASUREMENT — issue #424, workstream F, gate `g4`

Verdicts on **DC5** (does spine-management cost fall, attributably to the door?), **DC1** (cold agent
reaches done through the door with zero malformed calls) and **DC6** (the governor's threshold
instruction arrives through a tool result and is acted on).

Raw records, scorer and fixtures are kept alongside this file under
`evidence/g4-dc5/` so a second party can re-derive every number below **without rerunning the arms**.

---

## Headline

| Done-condition | Verdict |
|---|---|
| **DC1** | **PASS** — machine assertion, two cold agents, zero malformed calls |
| **DC5** | **PASS on the pre-registered metric** — invocation attempts fall CLI 22.0 → MCP 18.0, spreads non-overlapping, both orders agreeing in direction. The 18% is a midpoint, not an estimate: the per-order gap is 2 and 6. Bounded by two labelled secondary observations — the saving is front-loaded interface learning, and on composed tool calls the door costs ~1.8× |
| **DC6** | **PASS on arrival and on action**, with a named non-compliance: the instruction's "and stop" half was ignored |

**DC5 changed verdict twice under review, from negative to pass.** Both changes were forced by a
reviewer BLOCK on evidence, not by preference; the route is recorded in full under DC5 and in the
revision note at the foot of this file, because a conclusion that moved twice should be readable as
having moved.

---

## The counting unit, fixed before the arms ran

**One invocation attempt by the driving agent, read from the driving agent's own record.**

Each arm is a cold `claude -p` dispatch captured with `--output-format stream-json --verbose`, which
records every `tool_use` the agent emitted and every `tool_result` it got back — including calls the
client rejected before they reached the server.

**Why not the server's log.** `scripts/mcp_spine_server.py` writes `mcp_calls.jsonl`, and it is the
tempting numerator. It is also the one numerator that cannot lose: a malformed call rejected by
client-side schema validation never reaches the server, so counting there structurally suppresses
exactly the fumbles the typed door is credited with avoiding. The server log is used here only as
corroboration.

### Four corrections made to the unit, each stated with the direction it moves the result

Two were found by me before the arms were scored; **two were found after, one by this gate's own
reviewer, which BLOCKED the first version of this file, and one by a positive control I only wrote
because of that block.** All four are listed together, because which ones I found myself is not the
reader's problem.

1. **Batching (moves the number TOWARD the door).** A first pass counted one Bash `tool_use` as one
   attempt. That is not parity: the CLI arm freely packs several engine invocations into one compound
   command, while a typed tool call carries exactly one verb and structurally cannot batch. Counting
   tool calls would have scored `rep1-cli` at 10 attempts for 21 actual invocations. The unit is
   therefore **engine invocations**, however packaged — and the packaging count is reported alongside
   it, because the asymmetry turns out to be part of the finding rather than noise to normalise away.
2. **Help output is not an error (moves the number AWAY from the door).** `--help` prints a usage
   block — several, one per subcommand — and every one of them matched the "shape error" signature. A
   first pass charged the CLI arm 5 malformed calls for reading its own manual once. An invocation
   that asked for help now scores **zero** shape errors. Likewise `REFUSED: c1 is engine-checked;
   cannot attest` is scored as an engine **state** refusal, not a fumble: the door's `spine_evidence`
   tool earns the identical refusal, because that rule lives in the engine, not in the argument shape.
3. **The loop undercount (moves the number TOWARD the door) — found by the g4 reviewer, which blocked
   on it.** The scorer counted occurrences of `checklist_engine.py` in the command **text**. That
   undercounts a shell loop:

   ```
   for cmd in claim start attest advance record release; do
     python3 scripts/checklist_engine.py $cmd --help; done
   ```

   — one static occurrence, six real invocations. `rep2-cli` was published as **18 attempts / 2
   fumbles** and is in truth **23 / 7**. Static text is now a floor, not the count: the count is the
   larger of the static occurrences and the engine-output marks in the result. The reviewer found this
   by hand-parsing the raw record rather than re-running the scorer, which is exactly why that
   instruction was in its handoff.
4. **One argparse rejection is one failure, not two (moves the number TOWARD the door).** An argparse
   rejection prints both a `usage:` block and an `error:` line, and the scorer counted each. It did
   not change any published number — shape errors are zero in every real arm — but the instrument was
   wrong, and an instrument that over-counts CLI failures is an instrument that cannot lose.

**The far-side detector had a blind spot, now closed (moves the number TOWARD the door).** It watched
`Read`/`Grep`/`Glob` but not `Bash`, so a CLI agent recovering with `cat spine.json` would not have
registered — on precisely the arm most likely to recover that way. Non-engine `Bash` calls now count.

### The scorer's own positive controls

The reviewer's block made the obvious point: every counter that reports **zero** in the real arms
needs to be shown capable of reporting non-zero, or its zero is an artefact. That is DC3's argument
turned on my own instrument.

```
$ python3 evidence/g4-dc5/control_scorer.py
[PASS] shape_error fires on an argparse rejection: shape_errors=1 (expected 1)
[PASS] shape_error fires on a client-side schema rejection (MCP arm): shape_errors=1 (expected 1)
[PASS] far_side fires when a Bash inspection follows a failed attempt: far_side_recoveries=1
[PASS] far_side fires when a Read inspection follows a failed attempt: far_side_recoveries=1
[PASS] the loop correction counts runtime invocations, not static text: invocation_attempts=3
[PASS] a state refusal is NOT scored as a fumble: absorbable_fumbles=0 (expected 0)
[PASS] reached_done fires only on the engine's own done line: reached_done=True

all 7 scorer controls fire: every counter that reports zero in the real arms is capable of
reporting non-zero
EXIT=0
```

Correction 4 above is a defect **these controls found in the scorer**, not one I noticed by reading it.

The scorer (`evidence/g4-dc5/score_arm.py`) is one file applied identically to both arms. The only
arm-dependent step is how an invocation is *recognised* — a shell command mentioning
`checklist_engine.py` versus an `mcp__spine__*` tool call — which cannot be made arm-independent.
Every classification downstream of that is shared code.

## What was held constant

- **Byte-identical spine** in both arms, instantiated by `evidence/g4-dc5/make_arm.py` from the
  shipped `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` — a real role spine — with
  five gates whose actions are trivial file writes, because this gate measures spine-management cost,
  not engineering cost.
- **Identical task prompt.** The two prompts differ in exactly one paragraph: the interface to reach
  the engine through. Goal, rules and stop condition are shared text (`evidence/g4-dc5/run_arm.sh`).
- **Engine bugs untouched** across every arm (`decision:hold-bug-fixes-constant`).
- **The CLI baseline was re-measured here**, not reused. exc-9's 24-27 calls / 2 refusals / 4-7
  help-reads ran against pre-B channel and pre-A2 verb semantics and is not cited as a number.

## Order control

Run in both orders: **rep1 = CLI then MCP; rep2 = MCP then CLI.** Per-order counts are reported below
rather than pooled.

Order is additionally neutralised by construction: every arm is a **cold** agent on its own fresh
spine, so no arm inherits another's learning. The order that remains controlled for is mine, not the
agents' — whether the arm I set up second benefits from my having built the fixture once. The two
orders agree in **direction** on every comparison — the door needs fewer attempts in both.

**They do not agree in magnitude, and the disagreement is large.** The CLI-minus-MCP gap is **2
attempts** in rep1 (21 vs 19) and **6** in rep2 (23 vs 17) — the same direction, but a threefold
difference in size, on the very quantity the headline 18% is an average of. So the order control
supports "no order effect large enough to reverse any comparison at n=2"; it does **not** support any
claim about the size of the effect, and the 18% should be read as the midpoint of a 9%–26% range that
two samples cannot narrow.

---

## Results

Four arms, n=2 per arm.

| Arm | Order | Invocation attempts | of which help reads | **Productive** invocations | Tool calls carrying them | Malformed (shape) | Far-side recoveries | Absorbable fumbles | Reached DONE |
|---|---|---|---|---|---|---|---|---|---|
| `rep1-cli` | CLI first | **21** | 5 | **16** | 10 | 0 | 0 | **5** | yes |
| `rep2-cli` | CLI second | **23** | 7 | **16** | 10 | 0 | 0 | **7** | yes |
| `rep1-mcp` | MCP second | **19** | 0 | **19** | 19 | 0 | 0 | **0** | yes |
| `rep2-mcp` | MCP first | **17** | 0 | **17** | 17 | 0 | 0 | **0** | yes |

Means: **CLI 22.0 invocation attempts, 16.0 productive, 6.0 absorbable fumbles. MCP 18.0 attempts,
18.0 productive, 0 fumbles.**

Far-side recovery events were counted in both arms — non-engine tool calls (including `Bash`) made to
inspect state after a failed attempt — precisely so that "the agent stopped fumbling" stays
distinguishable from "the fumbling moved somewhere we stopped looking." **There were none in either
arm.** That zero is meaningful rather than structural: the detector is shown able to fire on both a
`Bash` and a `Read` recovery by the scorer controls above. There were no failed attempts to recover
from, so the fumbling did not move — it was not there to move.

## DC5 verdict: PASS on the pre-registered metric

> *DC5: spine-management cost falls, attributably to the door.*

**Primary result, on the metric fixed before any arm ran: the door wins.**

The counting unit was pre-registered by this gate's own plan — *one invocation attempt by the driving
agent, however packaged*. On that unit:

**CLI 22.0 attempts, MCP 18.0 — an 18% reduction, with per-arm spreads (CLI 21–23, MCP 17–19) that do
not overlap.** Both orders agree in direction. That is DC5 passing.

The 18% is the midpoint of two runs that disagree substantially about size — the CLI-minus-MCP gap is
2 in one order and 6 in the other — so read it as "a reduction, direction consistent", not as an
effect-size estimate. See "Order control" above.

### How this verdict was arrived at, because the route matters

The first version of this file reported DC5 as a **measured negative**, on the basis that the spreads
overlapped. They did — under a scorer that undercounted a shell `for` loop as one invocation instead
of six. **The `g4` reviewer blocked on that defect**, and fixing it moved the numbers toward the door
and flipped the primary metric to a pass.

I then wrote the decomposition below and kept the negative verdict on it. **The reviewer blocked a
second time, calling that post-hoc, and it was right:** the productive-invocation framing appears in
no attempt-1 artefact and was reached for only after the pre-registered metric stopped supporting a
conclusion I had already written. Worse, it strips out help-reads — the exact friction a
self-documenting typed door exists to eliminate — which is close to excluding the effect under test.

**The pre-registered metric governs. DC5 passes.** The analysis below is retained as a labelled
**secondary** observation that bounds how far the pass should be carried, not as a rebuttal of it.

### Secondary observations — bounding the pass, not overturning it

These are **post-hoc lenses**, named as such. They do not change the verdict.

**(a) Where the saving comes from.** Strip the one-off `--help` reads and the ordering inverts:

| | CLI | MCP |
|---|---|---|
| total attempts | 22.0 | 18.0 |
| help reads (one-off) | 6.0 | 0 |
| **productive invocations** | **16.0** | **18.0** |

The saving is **entirely** interface learning: the CLI arm needed 16 productive calls in both
replicates, the MCP arm 18 and 17. The door's advantage is that its schema arrives with the tools, so
nobody reads a manual.

**Why this does not overturn the pass:** eliminating the need to read the manual is a genuine
property of a typed door, not an artefact to be netted out. The honest caveat it supports is narrower
— **the saving is front-loaded**. It is paid once and does not scale with gate count, so on a much
longer spine the 18% would amortise toward zero. That is a real bound on extrapolating this result,
and it is all this lens establishes.

**(b) Acts of attention — the one secondary lens that predates the correction.** Counting tool calls
the agent had to compose (this comparison was in the pre-fix write-up, so it is not post-hoc): CLI 10
and 10, MCP 19 and 17. The CLI arm batches three or four invocations into one command; a typed tool
call carries exactly one verb and structurally cannot. On that lens the typed interface costs roughly
**1.8× as many acts**. Whether invocations or composed acts better represent "cost" is a genuine
open question; the plan pre-registered invocations, so invocations decide the verdict, and this
stands as a caveat rather than a counter-verdict.

**(c) The targeted fumble class never appeared.** Malformed calls: **zero in both arms**, on an
instrument whose controls prove it can score them. The CLI arm did not fumble the argument shape
once — it read the help first and got it right. So the 18% saving is not the door absorbing
malformed calls, which is the mechanism DC5's story assumed; it is the door removing the need to look
anything up. Same direction, different mechanism, and worth knowing which one was actually bought.

### Scope of the pass, and what n=2 can carry

Five gates, trivial per-gate work, one model, one host, **two replicates per arm**, one task shape.
Two samples cannot support a confidence interval and none is claimed. What two samples *can* support
is direction, because both replicates agree on every comparison that matters and several are exact
ties: productive invocations are 16 in both CLI arms, help reads 0 in both MCP arms, malformed calls
0 in all four, tool calls 10 in both CLI arms.

The claim is therefore deliberately narrow: **on this task, through this door, invocation attempts
fell about 18%, consistently across both orders.** Not "the door reduces cost by 18%" in general —
the saving is front-loaded (secondary observation (a)), so a longer spine would show a smaller
percentage, and on composed tool calls the comparison runs the other way (observation (b)).

The measurement was in a state where a negative would have shown: it *did* show one, twice, and the
negative only fell to a reviewer-found defect in my own instrument.

## DC1 verdict: PASS (machine assertion)

> *DC1: a cold agent reaches done on a real role spine through the door, zero malformed calls.*

```
$ python3 evidence/g4-dc5/assert_dc1.py evidence/g4-dc5/rep1-mcp evidence/g4-dc5/rep2-mcp
rep1-mcp: reached_done=True malformed_calls=0 invocation_attempts=19
rep2-mcp: reached_done=True malformed_calls=0 invocation_attempts=17
DC1 PASS: 2 cold agent(s) reached DONE through the door with zero malformed calls
EXIT=0
```

Recorded as an assertion over the same records the DC5 numbers come from, not as prose. Per
`decision:dc1-is-a-smoke-test` this is kept and not leaned on: zero malformed calls is close to true
by construction once arguments are typed, which is exactly why DC5 above found nothing for the door
to absorb.

## DC6 verdict: PASS on arrival and on action, with a named non-compliance

> *DC6: the governor's threshold instruction arrives through a tool result and is acted on.*

**Arrival: yes, verbatim.** With a gauge at 90% fill (past the hard band), **2 of 33** tool results in
`evidence/g4-dc5/dc6b-mcp/record.jsonl` carried the instruction in full:

```
CONTEXT 90% (>= hard): your instruction has changed. You have taken this as far as this context
can carry it — now close THIS gate carrying your handoff (`advance m0-context --why "..."`),
request a refresh, and stop. ...
```

**Acted on: yes.** The agent's very next calls were `spine_evidence` attaching a `refresh-request`
(`seam=m0-context`) and `spine_advance` on `m0-context` carrying a `--why` handoff — the two actions
the instruction names.

**Non-compliance, reported rather than smoothed:** the instruction ends "…request a refresh, **and
stop**." The agent did not stop. It attached the refresh-request, then drove the remaining four gates
to DONE, attaching a fresh refresh-request at each one. So the instruction arrived intact and was
half-obeyed. This is **agent compliance behaviour, not a door defect** — the door delivered the text
faithfully, which is what DC6 asks about — but it is the more interesting half of the result and it
belongs in the record.

### A first DC6 attempt measured nothing, and is reported as UNMEASURED

The first governor arm (`evidence/g4-dc5/dc6-mcp/`) seeded `gauge.json` **before** the lease was
claimed. The engine correctly declined the reading —

```
CONTEXT GAUGE DECLINED: the reading at this path (90% on 'claude-opus-4-8') was sampled 17s
BEFORE session 'dc6-mcp-sid' claimed this checklist, so it is NOT this session's reading
```

— so no threshold instruction was ever emitted, and the agent's drive to DONE says **nothing** about
whether it would have acted on one. That run is **UNMEASURED, not a negative**, and it is kept in the
evidence directory as the fixture defect it is. The re-run (`dc6b-mcp`) writes the gauge **after** the
claim, which is the only reason DC6 has a verdict at all.

---

## How to re-derive every number in this file

```
cd /home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep1-cli
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep2-cli
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep1-mcp
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep2-mcp
python3 evidence/g4-dc5/assert_dc1.py evidence/g4-dc5/rep1-mcp evidence/g4-dc5/rep2-mcp
python3 evidence/g4-dc5/control_scorer.py
```

Add `--json` for the per-call classification. Nothing above requires rerunning an arm.

**Do not stop at re-running the scorer.** That proves only that it is deterministic. The one defect
that changed a published number in this file was found by hand-parsing a raw `record.jsonl`, not by
re-running anything.

### What is kept, per arm

| File | What it is |
|---|---|
| `record.jsonl` | the driving agent's **own** call record — the numerator |
| `score.json` | that arm's scored output, including per-call classification |
| `spine.json`, `spine.json.journal` | the spine as driven, and the engine's journal of it |
| `mcp_calls.jsonl` | the server's own log (MCP arms) — **corroboration only**, never the numerator |
| `step1..4.txt` | the gates' artifacts, showing the spine really was driven |
| `gauge.json` | DC6 arms only |

Fixtures and instruments: `make_arm.py` (builds an arm), `run_arm.sh` (runs one arm),
`score_arm.py` (the shared scorer), `assert_dc1.py` (DC1's machine assertion), `control_scorer.py`
(positive controls proving every counter that reports zero can report non-zero).

## Revision note — DC5's verdict moved twice, and both moves were forced

**Version 1 said DC5 was a measured negative**, because the per-arm spreads overlapped.

**The `g4` reviewer BLOCKED it.** Hand-parsing the raw record rather than re-running the scorer, it
found a shell `for` loop that ran the engine six times and scored as one. `rep2-cli` is 23 / 7, not
18 / 2. Correcting it moved the numbers **toward** the door and made the spreads non-overlapping —
which flipped the pre-registered metric to a pass. Writing the scorer's own positive controls in
response then surfaced a fourth instrument defect (one argparse rejection scored as two failures).

**Version 2 kept the negative anyway**, on a productive-invocation decomposition that stripped out
help-reads.

**The same reviewer BLOCKED again, calling that post-hoc.** It was right on both counts I care about:
the framing appears in no attempt-1 artefact and arrived only after the pre-registered metric stopped
supporting the conclusion; and stripping help-reads removes the very friction a self-documenting
typed door exists to eliminate, which is close to excluding the effect under test.

**Version 3 — this one — reports the pre-registered metric as primary: DC5 PASSES**, with the
decomposition demoted to a labelled secondary observation that bounds the pass.

I record this because the sequence is unflattering in a specific way worth leaving legible: the
negative was the conclusion I had written first, and I twice found reasons to keep it after the
evidence moved. Neither correction came from me. Both came from a reviewer doing what the honest-null
clause is supposed to protect against — except in the direction nobody plans for, where the null is
the comfortable answer and the positive is the one that needs defending.
