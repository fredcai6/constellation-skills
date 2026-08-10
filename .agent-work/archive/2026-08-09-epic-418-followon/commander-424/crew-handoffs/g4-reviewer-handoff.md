# Reviewer handoff — gate `g4-review`: independent re-derivation of the DC5 measurement

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g4-review`
**Worktree (read/verify only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch
order.

## Task statement

**This is NOT a re-run of the arms.** It is an independent check of the conclusion. The gate that
produced the measurement waived its implement crew; that waiver does **not** cover this check, which
is why this gate exists and is not optional.

The artefact under review: `.agent-work/epic-418-followon/commander-424/MEASUREMENT.md`, with its raw
records, fixtures and instruments under `.agent-work/epic-418-followon/commander-424/evidence/g4-dc5/`.

**A number you cannot re-derive is a BLOCK.**

## The conclusion you are checking

| Done-condition | Verdict claimed |
|---|---|
| DC1 | PASS — machine assertion, two cold agents, zero malformed calls |
| DC5 | **MEASURED NEGATIVE on the claim as written** — spine-management cost did not fall |
| DC6 | PASS on arrival and action, with the instruction's "and stop" half ignored |

## Close criteria — each is a thing to do, not a thing to read

1. **Re-derive every headline number from the raw records, without trusting the summary.** The
   headline numbers are: CLI 21 / 18 invocation attempts, MCP 19 / 17; CLI 5 / 2 absorbable fumbles,
   MCP 0 / 0; CLI 10 / 10 tool calls carrying them, MCP 19 / 17; all four arms reached DONE. The
   records are each arm's `record.jsonl`. **Do not simply re-run `score_arm.py` and call the numbers
   confirmed** — that only proves the scorer is deterministic. Count at least one arm's attempts and
   fumbles **by your own independent means** (your own parse, or by hand) and say whether you got the
   same answer.
2. **Confirm the counting unit is genuinely identical across arms.** The claim is "one invocation
   attempt, read from the driving agent's own record". Check that the CLI arm's compound Bash
   commands are counted as *n* invocations rather than one, and that the MCP arm is not advantaged or
   disadvantaged by that choice. State whether you think the chosen unit is the right one; if you
   think a different unit is more honest, say which and what it would do to the verdict.
3. **Confirm client-rejected calls were counted and not silently dropped**, and that the server's
   `mcp_calls.jsonl` was used only as corroboration and never as the numerator. The whole design rests
   on this: a server-side numerator suppresses exactly the fumbles the door is credited with avoiding.
4. **Check the two disclosed unit corrections, in both directions.** MEASUREMENT.md discloses (a) a
   batching correction that moves the number *toward* the door and (b) a help-output correction that
   moves it *away*. Verify both are real, correctly applied, and correctly signed. **Look hard for a
   third correction that was not disclosed.**
5. **State whether order/practice effects were controlled or merely acknowledged.** Both orders were
   run (rep1 CLI-first, rep2 MCP-first) with per-order counts. Judge whether that plus cold agents
   actually neutralises practice transfer, or whether the claim is overstated.
6. **Check far-side recovery events were counted**, so "the agent stopped fumbling" is distinguishable
   from "the fumbling moved". The claim is zero in both arms. Verify that the far-side detector could
   have fired at all — if it is incapable of firing, "zero" means nothing, and that is a BLOCK.
7. **Check the honest-null clause was honoured.** A negative must be reported with the same rigor as a
   win, not softened — and equally not *inflated* into a stronger negative than the evidence carries.
   n=2 per arm is small; say plainly whether the write-up's confidence matches its sample.
8. **Check the UNMEASURED call.** A first DC6 arm (`dc6-mcp`) is reported as **UNMEASURED, not a
   negative**, because the engine declined a gauge sampled before the lease claim. Verify that
   reading is correct. **An unmeasured condition reported as a measured negative would be a serious
   defect; so would a measured negative softened into "unmeasured".** Check it lands on the right side.
9. **Check DC1's assertion is a machine assertion**, over the same records the DC5 numbers come from,
   and that it would fail if either half were untrue.
10. **Check DC6's verdict split is right** — arrival and action PASS, "and stop" ignored and reported
    as agent-compliance behaviour rather than a door defect. Say whether you agree with that
    attribution.

## Verification commands (the write-up's own re-derivation section)

```
cd /home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep1-cli
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep2-cli
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep1-mcp
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep2-mcp
python3 evidence/g4-dc5/assert_dc1.py evidence/g4-dc5/rep1-mcp evidence/g4-dc5/rep2-mcp
```

Add `--json` for per-call classification.

## What I want from you, stated plainly

**You have no stake in F succeeding, and neither do I at this point.** The governing rule is the
honest-null clause: **a measured negative that re-derives cleanly is an APPROVE, not a BLOCK.** Do not
block because the result is unflattering to the workstream, and do not approve a number you could not
reproduce because the conclusion sounds appropriately humble.

The failure modes I am most worried about, in order:

- a number that does not re-derive;
- an undisclosed correction, or a disclosed one whose direction is stated wrongly;
- the far-side detector being structurally incapable of firing, making its zero meaningless;
- the write-up claiming more (or less) than n=2 per arm can carry.

Any of those is a BLOCK. Say so and I will act on it rather than override it.

## Reporting

Write your `REVIEW_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g4-reviewer-result.md
```

**Write that file before ending your turn — the write is the delivery.** State the verdict as a bare
`APPROVE` or `BLOCK` on its own line so it is machine-readable. Include a `## Workflow Feedback`
section, blunt and specific. Log out-of-scope finds as triage candidates rather than fixing them. Do
not rerun the arms; if you believe a re-run is required to settle something, say so and block.
