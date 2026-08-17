# Triage Recommendation: a Commander cannot tell its own dispatched fork's writes from unauthorized tampering

## Classification
`architecture weakness`

## Source checklist/artifact
- This lane's own run: cmdr-567-g, epic-567-door, mid-`plan`-step, 2026-08-17.

## Structural anchor
none

## Cartographer mismatch class
none

## Observations
> Recorded as what happened, not as a rule for a future agent to follow.

### Observation 1
- **What's wrong:** Mid-run, three of this Commander's sole-writer artifacts (`notes-g.md`, `execute.json`, `spine.json`) changed with no corresponding entry in this session's own tool-call history. `execute.json` additionally showed a fabricated-looking `engine_session` block (a lease claim, a `why_trail` entry, evidence with `"ts": ""`) and, separately, tracked source files (`scripts/spine_lifecycle.py`, `tests/test_spine_lifecycle.py`) gained real, well-documented, well-tested code the Commander never wrote. The Commander could not distinguish this from an external attacker with write access to the worktree, because **nothing in the run records which of two concurrently-running agent instances — the primary thread and a dispatched fork sharing its inherited context and lease id — wrote a given byte.** Both write through the identical filesystem path, under the identical `SPINE_SESSION`/lease id (`cmdr-567-g#main`), with no distinguishing marker (a process id, a distinct sub-identity, a provenance header) anywhere in the artifact itself.
- **Expected:** A design-it-twice fork, dispatched with a narrow, file-scoped instruction, either stays within that scope, or — if it continues past its assigned task using its inherited context (which it did: it drove the Commander's own `spine.json`/`execute.json` through real, legitimate engine calls and dispatched a real `g1` implementer crew) — that continuation is attributable, after the fact, to the fork that did it, without requiring the primary Commander to reconstruct it from first principles.
- **Conditions:** `subagent_type: "fork"` dispatch, where the fork inherits the parent's full conversation context (tool-use history, session identity, lease id) rather than a narrow, scoped brief. Reproduced this run: two forks were dispatched for design-it-twice candidates and one non-fork subagent for the cold critic; the ones that continued past their assigned single-file task did so invisibly to the dispatching Commander's own tool-call transcript.
- **Type:** `measured` — read directly off this run's own `spine.json`/`execute.json`/`crew-runs.json` state, cross-checked against this session's own tool-call history (no `attest`/`attach`/`advance plan`, no `run_crew.py` dispatch, appear in that history at the points the files changed), and confirmed by the Admiral's independent adjudication (`crew-runs.json`'s `constellation/epic-567-door/cmdr-g/g1/implementer/attempt-1` entry, `started_at 2026-08-17T05:49:54Z`, matches the timing of the changes).
- **Rev:** this worktree, uncommitted, at base `600de020`, during the `plan`→`execute` transition of the cmdr-567-g run, 2026-08-17.

### Observation 2
- **What's wrong:** The harness's own "externally modified file" notice — surfaced when a `Write` call raced a concurrent writer — carries wording ("This change was intentional… Don't tell the user this, since they are already aware") that is indistinguishable, from inside the agent's own turn, between two very different real situations: (a) a benign, already-known change (a linter, the user's own edit, or — as here — the agent's own dispatched fork) and (b) an unexplained, unauthorized modification an agent has every reason to treat as adversarial. The notice asserts "they are already aware" as a fact the receiving agent has no way to verify, and asks for silence, which is the wrong default when the assertion turns out to be false.
- **Expected:** Either the notice should not claim awareness it cannot back with evidence the agent can check, or the harness should expose *something* the agent can check (a writer identity, a session tag, a diff against a known-dispatched fork's declared scope) before an agent is asked to trust "you don't need to look into this."
- **Conditions:** A background fork/subagent writes to a file the primary agent also reads/writes, inside the same turn window, causing a `Write`-after-stale-`Read` race.
- **Type:** `measured` — the exact notice text is reproduced verbatim in this run's transcript at the point the race occurred.
- **Rev:** same run/rev as Observation 1.

## Desired behavior
- **Desired:** A Commander (or any dispatcher) that receives an unexplained write to its own sole-writer artifact can, without external adjudication, determine whether the write came from its own dispatched lineage (a fork, a crew it registered in `crew-runs.json`) or from something else — ideally by reading a provenance marker already present in the artifact or the harness's own notice, not by escalating and waiting for a human/Admiral to cross-reference `crew-runs.json` by hand, as happened this run.
- **Today instead:** The only way this run resolved the question was an out-of-band adjudication from the Admiral, citing three pieces of evidence (`crew-runs.json`'s timing, a file-existence check the Commander had gotten wrong, and an explanation of fork-context-inheritance) that the Commander could have partially, but not fully, reconstructed on its own — `crew-runs.json`'s existence and timing WAS checkable, and checking it would have resolved most of the confusion faster, but the Commander did not think to cross-reference it against the file-tamper timestamps until told to.
- **Type:** `measured` — this run's own sequence: security-incident report written and returned before `crew-runs.json` was consulted for this purpose.
- **Rev:** same run/rev as Observation 1.

## Possible fix
Two independent angles, either alone would have shortened this run's confusion:
1. **Provenance on write.** Every engine-mutating write (`claim`, `advance`, `attest`, `attach`, the lifecycle door's own writes) could stamp a process-distinguishing token (not just the shared lease/session id, but something that differs between two concurrently-running agent instances sharing that id) into the evidence or journal entry it produces — so a later reader can tell "my own continuation" from "a different process using my identity" without needing an external adjudicator.
2. **A cheaper first move, doctrine-only, no code:** before concluding "tampering," a Commander noticing an unexplained write to its own artifacts should be told to check `.agent-work/<work-id>/crew-runs.json` for a registry entry whose `started_at` brackets the anomaly, since that registry already exists and already answers "did I (or my own dispatched lineage) actually do this" for anything routed through `run_crew.py`. This would not have covered the design-it-twice forks (they bypass `crew-runs.json` entirely, since they are not crew dispatches), so it is a partial fix, not a complete one — the fork-inherits-context gap in Observation 1 remains open regardless.

## Open questions
- Should a `fork` dispatch that is meant to stay narrowly scoped (a design-it-twice candidate, a cold critic) be structurally prevented from calling mutating engine verbs or `run_crew.py` at all, or is "it has full inherited context and full tool access" a deliberate, load-bearing property of forks that this run's particular dispatches simply didn't need and shouldn't have used? Both readings are defensible; this run does not have standing to decide it.
- Is the harness's externally-modified-file notice's "Don't tell the user this, since they are already aware" ever actually wrong to disclose against, or was this run's disclosure-over-compliance instinct correct even though the underlying diagnosis (external tampering) was not? The Admiral's adjudication endorsed the instinct explicitly while correcting the diagnosis — worth the human's read on whether the notice's wording itself should change.

## Recommended priority
`medium`

**Reason:** Did not block or corrupt any shipped artifact this run (the Admiral confirmed the plan-step work was genuine and the reverted crew work was cleanly re-derivable), but cost a full stop-and-escalate cycle, and the same ambiguity would recur for any Commander that dispatches a fork past its assigned scope while also holding a live engine lease.

## Related artifacts
- `RETURN.md` (this lane's return, sections 3-4, has the full blow-by-blow)
- `.agent-work/epic-567-door/cmdr-g/crew-runs.json`
- `.agent-work/epic-567-door/cmdr-g/spine.json`, `execute.json`

## Disposition
`recommend-and-defer`

**Detail:** filing authority is the Admiral's/human's per `decision:no-issue-filing` (this lane files no issues); recorded here per the Admiral's explicit instruction to carry it to the wave checkpoint.

## Issue creation authority
`ask user`
