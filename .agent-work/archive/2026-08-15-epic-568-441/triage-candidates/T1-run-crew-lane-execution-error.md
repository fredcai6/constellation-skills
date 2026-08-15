# Triage Recommendation: `run_crew.py implementer dispatch fails immediately with "Execution error" in this lane`

## Classification
`tooling`

## Source checklist/artifact
- `.agent-work/epic-568-441/crew-runs/g1-implementer-attempt-1.stdout.txt`
- `.agent-work/epic-568-441/crew-runs/g1-implementer-attempt-2.stdout.txt`
- `.agent-work/epic-568-441/LAUNCH_ORDER-resume-3.md`

## Structural anchor
`path:scripts/run_crew.py`

## Cartographer mismatch class
`none`

## Observations

### Observation 1
- **What's wrong:** `python scripts/run_crew.py` dispatch of an implementer for gate `g1` in this worktree/lane (`constellation/epic-568-441/g1/implementer/attempt-1`) exited with `Execution error` immediately, before any implementer work began.
- **Expected:** The dispatch should run the implementer crew and either complete, block honestly on a real obstacle, or exit with a diagnosable error naming the actual cause.
- **Conditions:** Worktree `/home/tommy/projects/constellation-skills/.worktrees/epic-568-441`, dispatching gate `g1` / role `implementer`. Two sibling lanes (other commander worktrees) were running implementer crews successfully on the same machine at the same time, per `LAUNCH_ORDER-resume-3.md`, which narrows this to something specific to this lane rather than the dispatch mechanism generally.
- **Type:** `measured` — read `.agent-work/epic-568-441/crew-runs/g1-implementer-attempt-1.stdout.txt` directly.
- **Rev:** as observed 2026-08-14/2026-08-15, this worktree, branch `epic-568/441-binding-store`.

### Observation 2
- **What's wrong:** A second dispatch attempt (`constellation/epic-568-441/g1/implementer/attempt-2`) also died with `Execution error`, and this time left NO entry in `.agent-work/epic-568-441/crew-runs.json` at all — the registry that `recover_crews.py` reads to detect running/resumable/conflicting crews.
- **Expected:** A dispatch attempt that fails should still leave a registry entry recording the attempt and its failure, so `recover_crews.py` can report it accurately rather than being blind to it.
- **Conditions:** Same worktree/lane as Observation 1, second attempt.
- **Type:** `measured` — read `.agent-work/epic-568-441/crew-runs/g1-implementer-attempt-2.stdout.txt` and confirmed no matching entry in `crew-runs.json`.
- **Rev:** as observed 2026-08-15, this worktree, branch `epic-568/441-binding-store`.

## Possible fix
The failure and the missing-registry-entry gap may be independent. Worth checking first whether this lane's worktree/session state (e.g. a stale lock, a leftover PID reference, or a worktree-relative path assumption `run_crew.py` makes) differs from the sibling lanes that dispatched successfully at the same time. No production code was inspected for this issue — `scripts/run_crew.py` was explicitly fenced off from this run's own four-file scope (sibling lanes were live), so this is a hypothesis only.

## Open questions
- Is the failure reproducible on demand in this exact worktree, or was it transient (e.g. a race with another live lane's use of a shared resource)?
- Why did attempt-2 leave no `crew-runs.json` entry at all, when attempt-1 (also a failure) did?

## Recommended priority
`medium`

**Reason:** Blocked this run's implementer dispatch twice, forcing the Commander to implement in-process per the launch order instead of the intended crew-dispatch path. Not urgent because the work-around (direct implementation) is available and was used successfully, but it degrades the delegated-execution model this repo is built around if it recurs.

## Related artifacts
- `.agent-work/epic-568-441/crew-runs.json`
- `.agent-work/epic-568-441/LAUNCH_ORDER-resume-3.md`
- `.agent-work/epic-568-441/REPLAN_INPUT.json` (discrepancy `D-dead-child-dispatches`)

## Disposition
`recommend-and-defer`

**Detail:** Issue-filing authority is not explicit in this run's launch order (scoped to the one bounded #441 fix), and `scripts/run_crew.py` itself is fenced off from this run because sibling lanes were live on it concurrently — diagnosing or fixing it is out of this run's latitude. Recorded here so the Admiral can decide whether to file it.

## Issue creation authority
`ask user`
