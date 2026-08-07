# Reviewer Handoff — g4: live acceptance, a real trip from a per-agent reading

**Work id:** issue-419-governor-identity · **Gate:** g4 · **Worktree:**
`C:/Programs/constellation-skills-wt/epic418-a-419` · branch `epic-418/a-419-governor-identity`,
HEAD `f8b0743`

## What was run

A two-arm live acceptance. A headless `claude -p` was launched with a settings file wiring
`PostToolUse` to a set of hooks by absolute path, cwd inside a disposable sandbox. Five agents: a
parent that claimed its own spine, two subagents claiming their own spines and reading deliberately
different amounts of an 800KB corpus, one subagent that claimed nothing, and one nested depth-2
dispatch. The **treatment** arm's settings named this worktree's hooks; the **control** arm's named the
main checkout's unmodified hooks and ran the byte-identical script.

Reported outcome: a **HARD trip fired** — subagent ALPHA reached 0.329482 fill and the engine refused
its `advance` — while the control arm produced no reading for any dispatched agent and advanced
normally.

## Your job

**This gate is the whole issue's deliverable, and it is the one gate whose evidence is a story rather
than a test suite.** Be adversarial. Your task is to try to explain the observed trip **without** the
change, and to check whether the evidence would look the same in a defective world.

## Where to look

Evidence, 51 files: `.agent-work/issue-419-governor-identity/evidence/g4-*` plus the full transcript
sets in `g4-transcripts-treatment/` and `g4-transcripts-control/`.
The implementer's account: `.agent-work/issue-419-governor-identity/results/g4-IMPLEMENTER_RESULT.md`.
The handoff it worked from: `.agent-work/issue-419-governor-identity/handoffs/g4-IMPLEMENTER_HANDOFF.md`
— its "Named falsifiers" list is the frozen bar.

**Recompute from the raw transcripts yourself.** `g4-recompute.py` is the implementer's own checker;
run it, but do not stop there — the point is that you reach the same numbers by your own route. Do not
import the hook under test.

## The named falsifiers — check each, and say so

Any one of these firing is a BLOCK, not something to explain away.

1. The binding key is bare rather than `<uuid>#<hex>`.
2. The two agents' fills match each other.
3. **The pairing is crossed** — A's reading in B's spine directory. This is the one that matters most:
   two composite keys existing, two distinct readings, a trip firing and a silent control **all still
   pass on a swap**, and a swap is exactly the misattribution class this issue exists to kill. Verify
   that each agent's own `agent-<id>.jsonl` recomputes to the `gauge.json` in the spine directory that
   the **same** id's binding key points at, and **state the count**.
4. `observed_at` predates the agent's first chunk read — a stale or parent-sourced record.
5. `advance` succeeded despite a `>= hard` reading.
6. The control arm also tripped.
7. A reported output is paraphrased rather than verbatim.
8. **Any identity value can be traced to the harness rather than to the payload.** The implementer
   reports a 7-pattern grep over a 32-file acceptance path returning zero matches, plus a set-difference
   proof that the session directory and all five agent transcripts were created only by the harness.
   Reproduce both. The grep alone is corroborating, not sufficient — a pre-seeded binding file, a
   hand-made `subagents/agent-<hex>.jsonl`, or an environment variable would all evade it.

## Two things the implementer disclosed that you should weigh, not skip

- **Treatment run 1 was discarded and re-run.** It also fired the trip, but two helper agents never
  claimed because the harness appended a PowerShell-only `$LASTEXITCODE` echo and the dispatched
  agents' shell was not consistently PowerShell. Run 1 is archived as
  `g4-out-treatment-run1.txt` and reported as not counted. **Check that the counted run is genuinely
  the re-run**, that nothing from run 1 leaked into the counted evidence, and that discarding it was
  honest rather than convenient.
- **One agent's authored report was blocked by a classifier at its final message**, so the implementer
  recovered its commands and raw results from the agent's own transcript instead. Judge whether that
  substitution is stronger evidence (no agent wrote it) or weaker (selected after the fact by the
  party being reviewed).

## Close criteria

1. A trip fired from a per-agent reading on a live run, verified by **your** re-computation from the
   raw transcripts, not from the harness's report.
2. The pairing holds, count stated. The parent held exactly its one bare-key entry and got its own
   reading. A release removed that agent's composite key while the parent's survived. The non-claiming
   subagent wrote nothing.
3. The run recorded which identity path it took and the resolved key shape, so a silent fallback could
   not have passed.
4. The nested depth-2 result is recorded either way. The implementer reports it **resolved** — a new
   fact, unknown before this run. Verify it, because if it is wrong the governor is silently blind for
   every nested agent and nobody would ever see it.
5. The control arm produced no reading for any dispatched agent and advanced normally.

## Scope

Review the evidence and the acceptance harness. The harness deliberately lives outside the repo and is
not committed — confirm that nothing outside `.agent-work/` entered the diff. `scripts/hooks/*` is
closed and reviewed; a defect you find there is a finding, not a BLOCK on this gate, unless it
invalidates the observation.

## Return format

`REVIEW_RESULT` at `.agent-work/issue-419-governor-identity/results/g4-REVIEW_RESULT.md`, verdict the
literal word **APPROVE** or **BLOCK**, each falsifier checked with its result, each close criterion met
or not with evidence **you personally reproduced**, findings separated in-scope and out-of-scope, and a
**Workflow Feedback** section (a bare "none" is not acceptable).

A measured negative is a complete result. If the observation does not hold up, say so with the same
rigor a win would get.
