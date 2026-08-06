# Reviewer Handoff — g2: the gauge writer attributes the reading to the acting agent

**Work id:** issue-419-governor-identity · **Gate:** g2 · **Worktree:**
`C:/Programs/constellation-skills-wt/epic418-a-419` · branch `epic-418/a-419-governor-identity`

## What was implemented

`scripts/hooks/gauge_writer_hook.py` now attributes a reading to the agent that produced it: it
resolves the gauge path from the **composite** binding key (`session_id#agent_id`, composed by
`spine_rail.binding_key`, which landed and was reviewed in gate g1), reads the fill from the acting
agent's **own derived transcript** (`<parent transcript stem>/subagents/agent-<agent_id>.jsonl`),
inverts the sidechain filter for that transcript while requiring `agentId` equality, fails closed with
a `subagent-transcript-missing` sidecar when the derived transcript is absent, and records the
identity-resolution duration on the dispatched-agent record.

Commit `5491bd4`.

## How to inspect the diff

```
cd C:/Programs/constellation-skills-wt/epic418-a-419
git show --stat 5491bd4
git diff 340c46d..HEAD -- scripts/hooks/gauge_writer_hook.py tests/
```

The implementer's account is at
`.agent-work/issue-419-governor-identity/results/g2-IMPLEMENTER_RESULT.md`. **Every claim in it is a
pointer to evidence you reproduce yourself, never an accepted fact.**

## Close criteria — verify each

1. The gauge path resolves from the composite key, so a dispatched agent finds its own binding.
2. A subagent's reading comes from its own derived transcript, polarity inverted, `agentId` equality
   enforced.
3. `agent_id` present + derived transcript absent ⇒ `gauge.json` byte-identical (bytes **and** mtime),
   no uncalibrated flag, and a `gauge-skip.json` with `subagent-transcript-missing`.
4. An unresolvable identity writes nothing.
5. A payload with no `agent_id` behaves byte-identically to before.
6. Every pre-existing test in `tests/test_gauge_writer.py` passes **unedited** — confirm none were
   changed, not merely that they pass.

## Where to look hardest

- **The one failure this gate must never ship is a confident wrong number.** Hunt for any path by
  which the **parent's** transcript can reach `compute_record` when `agent_id` is present. Fan-out to
  the parent is the exact misattribution already tried and reverted under #202/#261. Read the branch;
  do not infer it from a test name.
- **Reproduce the non-vacuity measurement.** The implementer reports that reverting
  `gauge_writer_hook.py` to `340c46d` turns **23 of 30** new tests red, and names the 7 that stay green
  with reasons. Reproduce it. Note the revert target is `340c46d`, **not** `HEAD` — g1's reviewer found
  a stale "revert to HEAD" recipe silently proving nothing once the work was committed, so check you
  are reverting to the pre-change file. If the count does not reproduce, that alone is a BLOCK.
- **The sidechain conjunct.** The pre-existing real fixture cannot falsify it — all 4 of its lines are
  `isSidechain` truthy with the same `agentId`, so `agentId`-equality alone passes every obvious
  assertion. A derived fixture (`subagent_transcript_with_mainchain_tail.jsonl`) was added to close
  that. Verify it actually does: that the extra line carries the **matching** `agentId` with
  `isSidechain` falsy, and that it is skipped **by the conjunct** rather than by being unusable for
  some other reason.
- **The `_spine_rail is None` guard.** Moving the `binding_key` call out to `handle_post_tool_use`
  strands the guard that used to live inside `resolve_gauge_path`. Confirm it was carried, and that a
  sibling-import failure produces a visible skip rather than an exception swallowed into silence.
- **Two things the implementer flagged, which the Commander wants a second opinion on:**
  1. The duration field rides the **dispatched-agent path only**, because recording it on a top-level
     record would break the four-key assertion the pre-existing tests pin. Is that the right reading of
     "records its own duration in the gauge write"? Say what you think.
  2. `spine_rail`'s `agent_id` check is a **denylist** and this module's is an **allowlist**, so they
     disagree by design: an id like `a:b` gets a binding written by `spine_rail` that this module will
     never resolve — an orphaned dict entry, no filesystem hazard. Confirm that characterization
     (especially "no filesystem hazard") and confirm the divergence carries a comment at the code site.

## The standard that governs your verdict

**A check that cannot fail is worse than no check.** For every new test, ask whether it passes in a
world where the change did nothing. Any guard that loops must assert what it looped over and state the
count.

## Allowed scope / exclusions

Review `scripts/hooks/gauge_writer_hook.py`, `tests/test_gauge_writer.py`, and the new fixture.
`scripts/gauge_reader.py`, `scripts/checklist_engine.py` and `scripts/hooks/spine_rail.py` are out of
scope and were required to be untouched — verify that, and report a violation as a finding.
`docs/GAUGE_WRITER_HOOK.md` is knowingly stale and belongs to the next gate; do not report it.

## Verification commands

```
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_gauge_writer.py tests/test_gauge_reader.py tests/test_spine_rail.py -q
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests -q
```

**`python -m pytest`, never `py`.** Counts: 1621 at HEAD `990712f`, 1637 after g1, and g2 reports
**1667**. A count that has not moved means the new tests do not exist.

## Return format

`REVIEW_RESULT` at `.agent-work/issue-419-governor-identity/results/g2-REVIEW_RESULT.md`, verdict the
literal word **APPROVE** or **BLOCK**, each close criterion met or not with evidence you personally
reproduced, findings separated into in-scope and out-of-scope, and a **Workflow Feedback** section (a
bare "none" is not acceptable; if genuinely none, say what you checked).
