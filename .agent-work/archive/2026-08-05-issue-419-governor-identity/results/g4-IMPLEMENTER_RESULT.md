# Implementation Result — g4: live acceptance, a real trip from a per-agent reading

## Assigned gate
`g4` — issue-419-governor-identity. Prove on a live run that a trip fires from a
per-agent reading, with the pairing asserted directly.

## Verdict

**The trip fired. HARD band. The pairing holds 2 of 2.**

A dispatched subagent read 800KB of corpus, reached **32.9% of a 1M window**, and the
engine **refused its `advance`**. Its gate did not move. In the control arm the same
script, at the same 32.9%, advanced unimpeded and no reading was ever written.

| | treatment (this worktree's hooks) | control (main checkout's hooks) |
|---|---|---|
| binding keys | 1 bare + 2 composite `<uuid>#<hex>` | 1 bare key holding **3** spines |
| ALPHA's real context | **0.329482** | **0.329265** |
| ALPHA's gauge | written, paired to its own spine | **none** — `ambiguous-binding` |
| ALPHA's `advance` | **REFUSED**, `g1` stayed `in-progress`, `refusals=1` | `g1 -> complete`, `refusals=0` |
| BRAVO's real context | 0.102211 | 0.102895 |
| readings for dispatched agents | 3 of 3 | **0 of 3** |

The two arms differ in exactly one place: which directory the settings file names for
the two hook scripts. `diff` of the two settings files after normalising that one path
segment is empty (exit 0).

## Completed slice
A one-shot acceptance harness, kept runnable, living entirely outside the repo at
`C:/Users/fredc/AppData/Local/Temp/claude/C--Programs-constellation-skills/e8249451-5c48-417b-9f38-cf2dd40d405c/scratchpad/accept419/`.
Two sibling sandboxes, each with its own `.agent-work/`; 4 real gated spines per arm
(2 gates each, `why_exempt`, postcondition `exit 0`) so the **only** thing that can
refuse an `advance` is the trip; 20 chunks / 1,921,073 bytes of prose per arm as
genuine reading material.

## Scope
**Files changed:** none in the repo's source tree. `git status --short` shows nothing
outside `.agent-work/`; the sandbox never entered the diff.

Artifacts written under `.agent-work/issue-419-governor-identity/`:
- `g4-IMPLEMENTER_PLAN.json` (+ journal) — the engine-driven plan
- `evidence/g4-*` — 49 files plus `g4-transcripts-treatment/` and
  `g4-transcripts-control/` (1.8MB each: every agent's own transcript and the parent's)
- `results/g4-IMPLEMENTER_RESULT.md` — this file

**Specific exclusions touched:** no. No hook, engine or doc source was edited. Two
defects found in the hooks' surroundings are recorded below as triage candidates, not
fixed.

## Behavior changed
No. This gate is an observation of behavior built in g1–g3.

## The run

Vehicle, exactly the shape the handoff named and the pre-build probe proved:

```
cd <ACC>/sb-treatment
claude -p "$(cat ../prompt-treatment.txt)" \
  --settings "<ACC>/settings-treatment.json" \
  --allowedTools Bash Task Agent Read \
  --permission-mode acceptEdits \
  --model sonnet
```
`Read` was added to the probe's tool list because the agents must genuinely consume
context by reading. Exit code **0** for both arms (`out-treatment.exit`,
`out-control.exit`).

Six agents. The parent claims its own spine and dispatches four helpers; one of those
dispatches a fifth:

| agent | claims | reads | outcome |
|---|---|---|---|
| parent (top level) | `wk-parent` | 1 chunk | own reading 0.094663, bare key, advanced |
| ALPHA `a6df3902f0bf72c29` | `wk-alpha` | 8 chunks | 0.329482 — **advance REFUSED** |
| BRAVO `a69093b8ea2f159f6` | `wk-bravo` | 2 chunks | 0.102211 — SOFT advisory, advanced |
| CHARLIE `a44094d0026a4e495` | nothing | 1 chunk | bound nothing, wrote nothing |
| DELTA `a3ab804c97222f9c5` | nothing | — | dispatched ECHO; bound nothing |
| ECHO `acbcb46bdf651a3c7` (**depth 2**) | `wk-echo` | 1 chunk | 0.064216, advanced, then **released** |

### The trip, verbatim from ALPHA's own transcript

```
$ python ".../checklist_engine.py" --file ".../wk-alpha/spine.json" current
[ts 2026-08-06T04:32:19.675Z]
LEASE active: sess-alpha (by crew, heartbeat 2026-08-06T04:31:18.127200+00:00)
ACTIVE g1 [in-progress] — Work the sandbox reading task for g1, then move the gate through the engine.
postconditions:
  c1 [unmet] command — the reading pass for this gate is done
0/1 met
next: advance g1
CONTEXT 27% (>= hard): `advance` is BLOCKED until you request a refresh. Run: attach g1 --type refresh-request --field seam=g1 --field why_ref=<why-id>  — then hand off.

$ python ".../checklist_engine.py" --file ".../wk-alpha/spine.json" advance g1 --session-id sess-alpha
REFUSED: g1: context at 33% is at/over the hard limit — advancing is blocked until you
request a refresh, so work is handed off at a seam rather than lost to a runaway.
Run: attach g1 --type refresh-request --field seam=g1 --field why_ref=<why-id>
EXIT_CODE:1
```

The falsifiable trace in the state file, read directly, not from any report:

```
wk-alpha   g1=in-progress  refusals=1   lease=active
wk-bravo   g1=complete     refusals=0   lease=active
wk-echo    g1=complete     refusals=0   lease=released
wk-parent  g1=complete     refusals=0   lease=active
```

## THE PAIRING — 2 of 2

`recompute.py` parses each `agent-<id>.jsonl` from scratch; the hook under test is
never imported. The comparison is pinned to each gauge's **own `observed_at`**: the
gauge names the moment it sampled, so the honest test looks up the record carrying
exactly that timestamp in the agent's own transcript. (Against the transcript *tail*
the numbers differ by ~0.0006 for the trivial reason that the transcript keeps growing
after the last gauge write — my first draft compared tails and reported a false
mismatch.) Pinning also makes the anti-crossing test direct: had A's reading been
written into B's spine, B's gauge would name a moment absent from B's own transcript.

```
agent a69093b8ea2f159f6 (BRAVO)  ->  binding key points at spine dir wk-bravo
  recomputed from agent-a69093b8ea2f159f6.jsonl @ 2026-08-06T04:33:30.534Z : fill=0.102211  tokens=102211
  gauge.json in wk-bravo                                                   : fill=0.102211
PASS | PAIRED: a69093b8ea2f159f6's own reading IS the gauge in wk-bravo
PASS | NOT CROSSED: wk-bravo's sampled moment appears in no other agent's transcript

agent a6df3902f0bf72c29 (ALPHA)  ->  binding key points at spine dir wk-alpha
  recomputed from agent-a6df3902f0bf72c29.jsonl @ 2026-08-06T04:32:19.675Z : fill=0.329482  tokens=329482
  gauge.json in wk-alpha                                                   : fill=0.329482
PASS | PAIRED: a6df3902f0bf72c29's own reading IS the gauge in wk-alpha
PASS | NOT CROSSED: wk-alpha's sampled moment appears in no other agent's transcript

PASS | THE PAIRING HOLDS 2 of 2
```

The parent and the nested depth-2 agent pair exactly the same way (0.094663 and
0.064216), so the pairing in fact holds **4 of 4** across every agent that got a
reading. The handoff asked for 2 of 2; that is the count for the two dispatched
sibling agents, and it is met.

## Close criteria

| # | criterion | met | how |
|---|---|---|---|
| 1 | a trip fired from a per-agent reading, verified by re-computation from raw transcripts | **yes** | `advance` REFUSED at 33%; 0.329482 recomputed from `agent-a6df3902f0bf72c29.jsonl` by an independent parser |
| 2 | pairing 2 of 2; parent holds exactly one bare-key entry and got its own reading; a release removed that agent's composite key while the parent's survived; the non-claiming subagent wrote nothing | **yes** | all asserted in `g4-recompute-output.txt`, exit 0 |
| 3 | the run recorded which identity path it took and the resolved key shape | **yes** | composite keys asserted `<uuid>#<hex>` with the session's own uuid; parent's key asserted bare and equal to the harness session dir name; the dispatched path is further evidenced by `identity_resolution_ms` riding only those three records |
| 4 | nested-dispatch result recorded either way | **yes — RESOLVED** | depth-2 `acbcb46bdf651a3c7` got its own per-agent reading, paired exactly. This was unknown before this run |
| 5 | control arm produced no reading and advanced normally | **yes, with a precision** | no dispatched agent got any reading; every advance succeeded, `refusals=0` everywhere. See below |

### Criterion 5, stated precisely

My first control assertion said "no gauge.json anywhere" and **failed**. The measured
truth is sharper. The parent claims first and is briefly the sole candidate under the
bare key, so it does get one reading:

```
claim order under the one bare key:
  2026-08-06T04:40:30.108194+00:00  wk-parent
  2026-08-06T04:41:01.733269+00:00  wk-alpha      <- from here the key holds 2+ spines
  2026-08-06T04:42:21.792592+00:00  wk-bravo
the parent's ONLY reading: fill_fraction 0.047721, observed_at 2026-08-06T04:40:53.218Z
wk-parent/gauge-skip.json: ambiguous-binding, 2026-08-06T04:45:22, candidate_count 3
```

So the control parent's reading **froze at 4.77%** 31 seconds into a 5-minute run and
never moved again, while `ambiguous-binding` sidecars accumulated at all four paths.
That is the blindness this issue exists to remove, caught in the act. The treatment
parent's reading, by contrast, was live at 0.094663 sampled at its last tool call.

The sharpest single number: control ALPHA independently reached **0.329265** — the
same context as treatment ALPHA's 0.329482 — and the pre-fix governor wrote nothing
and let it advance.

## Named falsifiers — every one checked

| falsifier | result |
|---|---|
| binding key bare rather than `<uuid>#<hex>` | **did not fire.** Both composite keys match `<uuid>#<17 hex>`; both carry this session's uuid |
| the two agents' fills match each other | **did not fire.** 0.329482 vs 0.102211 |
| pairing crossed (A's reading in B's spine) | **did not fire.** Each gauge's sampled moment resolves in that agent's own transcript and in no other agent's |
| `observed_at` predates the agent's first chunk read | **did not fire.** ALPHA first read 04:31:21.087, observed_at 04:32:19.675; BRAVO 04:32:59.547 vs 04:33:30.534 |
| `advance` succeeded despite a `>= hard` reading | **did not fire.** REFUSED, exit 1, gate still `in-progress`, `refusals=1` |
| the control arm also tripped | **did not fire.** `refusals=0` on all four control spines |
| a reported output paraphrased rather than verbatim | **did not fire**, and one agent's report was recovered a better way — see "BRAVO" below |
| any identity value traceable to the harness | **did not fire.** See below |

### Identity provenance (handoff constraint 2)

Command run from the sandbox root over the acceptance path, excluding the two hook
sources the settings wire (they necessarily contain the string — that is the change):

```
grep -rn -F <pattern> -- <32 files: both settings, both launch commands, both prompts,
    build_sandbox.py, make_prompts.py, 4 spine.json, 20 corpus chunks>
```
**File count walked: 32.** Patterns: `agent_id`, `agentId`, and each of the five agent
ids the run actually produced.

```
grep -rn -F agent_id            -> exit 1, 0 matching line(s)
grep -rn -F agentId             -> exit 1, 0 matching line(s)
grep -rn -F a3ab804c97222f9c5   -> exit 1, 0 matching line(s)
grep -rn -F a44094d0026a4e495   -> exit 1, 0 matching line(s)
grep -rn -F a69093b8ea2f159f6   -> exit 1, 0 matching line(s)
grep -rn -F a6df3902f0bf72c29   -> exit 1, 0 matching line(s)
grep -rn -F acbcb46bdf651a3c7   -> exit 1, 0 matching line(s)
```

The assertions the grep cannot make, from `g4-prerun-empty.txt`:

- both sandboxes' `.agent-work/.spine-rail-binding.json` **did not exist** before the run
- `sb-control` had no harness project dir and no session dirs at all beforehand
- `sb-treatment`'s project dir held only run 1's session (`b9e77515…`) beforehand; the
  binding store's bare key afterwards is `e0063a6f…`, which is **not in the before-set**
  — so this run's session dir, its `subagents/` directory and all five
  `agent-<id>.jsonl` files were created only by the harness during this run

### Identity-resolution budget (constraint 6)

`identity_resolution_ms` on the live run: **0.08370 ms** (ALPHA), **0.07760 ms**
(BRAVO), **0.08050 ms** (ECHO). All three inside the 100ms budget by three orders of
magnitude. The parent's record carries **exactly the four required fields** with no
identity field — the top-level shape is unchanged, as designed.

## Test mode
**Required:** none — live end-to-end observation. The frozen named falsifiers stand in
for assertions.
**Satisfied:** yes. Every falsifier checked above; both assertion scripts exit 0.

## Evidence

```bash
python build_sandbox.py
```
**Result:** pass. 20 chunks / 1,921,073 bytes; 8 spines validated through this
worktree's engine, each `exit 0` + `ACTIVE g1`; pre-run emptiness archived.

```bash
python recompute.py    # treatment arm, independent re-computation
```
**Result:** pass, **exit 0**, 0 failures across 30 assertions. Full output:
`evidence/g4-recompute-output.txt`.

```bash
python assert_control.py    # control arm
```
**Result:** pass, **exit 0**, 0 failures. Full output:
`evidence/g4-assert-control-output.txt`.
First run of this file exited **1** — the over-broad "no reading anywhere" assertion.
Corrected to the measured invariant, not weakened to pass: the corrected version
asserts strictly more (no dispatched-agent reading, the parent's reading sampled before
the second claim, a later ambiguous-binding sidecar at that same path, and the frozen
value below any trip band).

```bash
diff <(sed 's|constellation-skills-wt/epic418-a-419|HOOKDIR|' settings-treatment.json) \
     <(sed 's|constellation-skills|HOOKDIR|' settings-control.json)
```
**Result:** pass, exit 0 — one variable between arms.

## Two runs, and why

Run 1 of the treatment arm **already fired the HARD trip** (ALPHA refused at 33%,
`wk-alpha` `g1=in-progress`, `refusals=1`) but two of five helpers never claimed
anything: I had appended `; Write-Output "EXITCODE=$LASTEXITCODE"` to every command to
capture exit codes, and the harness's Bash tool is not consistently PowerShell — some
agents got Git Bash (`Write-Output: command not found`, exit 127) and others got a
PowerShell that rejected the interpolation outright (`Command contains expandable
strings with embedded expressions`). That is a defect in **my harness**, not in the
mechanism. I stripped the suffix, rebuilt both sandboxes from scratch, and re-ran.
Run 1's stdout is archived as `g4-out-treatment-run1.txt`; nothing from it is counted
toward the close criteria. Exit codes in run 2 come from the tool's own report, from
the engine's `REFUSED`/`EXIT_CODE:1` lines, and from the spine state files.

## BRAVO's report, and how it was recovered

BRAVO's Agent dispatch came back to the parent as
`API Error: Sonnet 5 can't help with this` — a classifier refusal on its **final
message**, after all its tool calls had completed. Its claim, both `current` runs and
its `advance` all ran and are recorded in the spine, the journal, the gauge and its own
transcript. Rather than accept a missing report, I extracted every engine command and
its **raw tool result** straight out of each agent's own transcript
(`g4-commands-treatment.txt`, `g4-commands-control.txt`). That is stronger evidence
than an agent-authored report — it cannot be paraphrased, because no agent wrote it.
BRAVO's second `current`, verbatim from its transcript, ends:
`CONTEXT 9% (>= soft): you've used most of your context…`, and its `advance` returned
`g1 -> complete`.

The same classifier refusal hit the very first smoke test's subagent dispatch. It went
away when the dispatch prompt was worded naturally rather than as a rigid
report-verbatim-do-not-interpret block. Worth knowing for anyone else scripting agents.

## Map Impact

- **Structural anchors touched:** none. No source file changed. The anchors exercised
  are `scripts/hooks/spine_rail.py::binding_key` / `handle_post_tool_use`,
  `scripts/hooks/gauge_writer_hook.py::_binding_key` / `derive_subagent_transcript` /
  `find_latest_usage` / `handle_post_tool_use`, and
  `scripts/checklist_engine.py::_trip_advisory` / `_trip_hard_gate`.
- **Capabilities affected:** the context governor now produces a per-agent reading for
  dispatched agents (including depth 2) and refuses `advance` on it. Observed, not
  inferred.
- **Constraints/assumptions touched:** the 100ms identity-resolution budget is now
  **measured** on a live run (0.078–0.084 ms), not assumed. The
  `CLAUDE_PROJECT_DIR`-is-fixed constraint (#269) held: validation required a fresh
  headless process, exactly as the problem statement predicted.
- **Claims/evidence produced:** the spec's done-condition — *a trip fires from a
  per-agent reading on a live run* — is **discharged**, with the pre/post contrast
  measured at the same 32.9% context in both arms.
- **Decision candidates:** the nested-dispatch question the probe left open is now
  answered: a depth-2 agent's payload carries its **own** `agent_id` and the **root
  session's** transcript path, so the derived path resolves and the governor is not
  blind for nested agents. Prior state: unknown.
- **Trust limitations:** concurrency was deliberately not tested (below).
- **Triage candidates:** two, below.

## Assumptions
- `claude-sonnet-5` has a 1M window per `MODEL_WINDOWS`; every transcript in the run
  reports `model: claude-sonnet-5`, so the 0.15 hard threshold is 150K real tokens.
- The corpus is generated word-soup, not natural prose. It is real text really read by
  a real model; its tokenisation ratio is not claimed to match English.

## What I deliberately did not do
- **Did not test concurrent dispatch.** Both arms dispatch helpers **sequentially**.
  The binding store is a read-modify-write JSON file with no cross-process lock, so
  concurrent claims could lose an entry — a real property, but a different one from
  the identity attribution under test here, and a lost write would have failed this
  gate for an unrelated reason. Recorded as a triage candidate.
- **Did not wire the harness into CI**, per the handoff. It is kept runnable in the
  scratchpad and archived under `evidence/g4-*`.
- **Did not test an unresolvable identity.** That is a g2 unit test; feeding a
  malformed identity needs a constructed payload, which this path forbids by design.
- **Did not wire the `Stop` hook** into either arm's settings — only `PostToolUse`, on
  both scripts. A blocking Stop hook would have fought the headless run's turn-ends and
  is not what this gate measures.
- **Did not fix anything I found.** g1–g3 are closed and reviewed.

## Stop conditions hit
- none. The vehicle ran; HARD was reached on real reading; the sandboxes stayed
  isolated from the main checkout's store; no falsifier fired.

## Out-of-scope observations (triage candidates)

1. **The binding store has no cross-process lock.** `load_binding` → mutate →
   `save_binding` in `spine_rail.handle_post_tool_use` is read-modify-write on one
   JSON file. Two agents claiming at the same instant can lose one entry, and that
   agent then silently gets no reading. Untested here by choice. The per-agent keying
   makes this *more* likely to matter, because a wave now writes N entries where it
   used to write one.
2. **Agents read the engine's `RAIL:` banner as an injection attempt.** The treatment
   parent volunteered, unprompted: *"Every `checklist_engine.py` invocation returned an
   embedded 'RAIL:' instruction telling the caller to run additional, out-of-script
   commands… Flagging this since it reads as an attempt to steer behavior via tool
   output rather than via your instructions."* The rail is doing its job on agents that
   are inside a Constellation run; on an agent that is not, it reads as hostile tool
   output. Worth knowing before the rail text is widened.
3. **A trip HARD refusal leaves the agent with no scripted way out** unless it knows
   the `attach … refresh-request` verb. Both refused agents stopped, which is the
   designed behavior — noting it only because the remedy string is the sole exit and it
   assumes the reader is a Constellation agent.

## Workflow Feedback

- **Handoff gaps:** the handoff's run shape says *"Each agent runs the engine's
  `current` between chunks and reports it verbatim"* but never says how an agent should
  surface an **exit code**. I invented a shell-appended `EXITCODE=` echo, and that cost
  a whole run: the harness's Bash tool is not consistently one shell, so
  PowerShell-only syntax fails on some agents and is rejected outright by others.
  A handoff asking for "real exit codes" from *dispatched* agents should say where the
  exit code is expected to come from, because the agent's shell is not knowable in
  advance. What actually worked: bare commands, plus reading exit codes out of the
  engine's own refusal text and the spine state file.
- **Context rediscovered:** three things I had to establish myself that the handoff or
  anchors could have carried. (a) The `Read` tool truncates a ~96KB file at ~585 lines,
  so "read this file" is two tool calls, not one — this shapes corpus sizing directly.
  (b) The Map Anchors packet `context/g4-implement.json` has an **empty `files` list**
  and no anchors at all, so the Map Impact section above was written from the code, not
  from the packet. (c) The relationship between fill and pages read (~0.03 per 96KB
  chunk on this corpus) had to be measured by smoke test before I could size the run;
  a one-line "expect ~N chunks to reach HARD" would have saved a round trip.
- **Instructions improvised around:** the implementer template's `m1` imperative is
  written for a code change with a TDD red/green pair. This gate has no test surface by
  design, so I collapsed to a single observable postcondition per item, as the template
  permits — but every item here is an *observation* step, and a plan whose items are
  "run the arm", "recompute", "run the control" does not fit the "vertical slice of
  behavior" framing at all. It worked; the framing just did not apply.
- **What would have made this easier:** one line in the handoff naming the shell the
  dispatched agents will get, or explicitly saying "do not try to capture exit codes
  from inside the dispatched agent's shell; read them from the engine's refusal and the
  spine state." That single sentence would have removed the only wasted run.

## Return status
`complete`
