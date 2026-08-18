# Workflow feedback — lane D1 (#559), commander-delegated

## How closely the skills, handoffs and checklists were followed

Closely, with one structural exception forced by the system itself: **`execute.json` was driven
through the CLI, not the door.** The door refuses to rebind while the process holds its own spine's
lease, so a Commander cannot drive its own child checklist through it. That is the Admiral's F-1
ruling and it held all run.

Every crew went through `run_crew.py`; `recover_crews.py` ran before every dispatch; no crew was
hand-launched. Two BLOCKs were handled by `reopen` rather than override, and both rework rounds
preserved the prior round's survey and result as audit records.

## Where instructions had to be improvised around

1. **Every crew dispatch needed its environment sanitized.** `run_crew.py` binds `SPINE_FILE`/
   `SPINE_SESSION` only when `--spine` is given; without it the child inherits the dispatcher's, so
   `env -u SPINE_FILE -u SPINE_SESSION -u CREW_SCRATCH_DIR` prefixed every launch. Nothing in the
   dispatch documentation says to do this.
2. **The hard-band refusal and the Stop hook disagree, and both are binding.** The engine refuses
   `start` at the hard band and tells you to hand off; the Stop hook refuses the handoff and is
   authoritative (#595). The workable sequence — attach the refresh-request, then `start`, then work
   — is in the launch order but not in the engine's own refusal text, which reads as "stop here."
3. **A crew's own plan location is convention, not documentation.** Every crew discovered
   `CREW_SCRATCH_DIR` by reading a sibling's result artifact.

## What was ambiguous, missing, or contradictory

- **The census unit.** "15 `CLI fallback` occurrences / 9 `<engine>` tokens" mixed occurrences and
  lines. The same slip then recurred at three consecutive tiers — my handoff, the crew's result, my
  next handoff — which is evidence it is a template problem rather than an author problem. Phrasing
  every census as "N occurrences across M files containing them" would end it.
- **The Fowler record path** is per-work-id, so the second reviewer in a run silently destroys the
  first gate's audit evidence. Then the per-gate fix collides across rework rounds.
- **`docs/agents/GLOSSARY.md` has no entry for "door"** — the term this epic makes load-bearing.

## Crew Workflow Feedback harvested at each `gN-integrate`

Six crews, and the most useful items were their accounts of their own errors: an implementer whose
first pattern accepted a bare `--` and red-lit an em-dash sentence, caught only because it wrote the
predicate's own test before trusting the predicate; an implementer that batched two vertical slices
into one editing pass and noted the engine had recorded the order it *claimed*, not the order it
*worked*; a reviewer that recorded a check before running the compound command behind it; and a
reviewer that traced a 7-vs-6 suite discrepancy to its own side effect rather than to the claim it
was auditing — *"when your measurement disagrees with a claim, suspect your measurement's side
effects before you suspect the claim."*

Two crews refused a premise in their own handoff and measured the truth instead. Both were right and
both were mine.

## My own mistakes

Three of my checks were defective **in the same way each time — authored from what the output should
say rather than run against what it does say**: `set -o pipefail` in five postconditions (illegal in
dash); two that matched the guard's own census line as a violation; two that required a whole-corpus
green another lane's un-merged files made unobtainable. I also repeated a wrong boundary in two
handoffs, and dispatched a re-reviewer with a `--result` path its handoff did not name, so it
overwrote the previous round's BLOCK result — recoverable only because it was committed.

## What would have helped

Naming the counting unit in any census. Stating in the crew-dispatch reference that a no-`--spine`
crew inherits the dispatcher's spine environment. And a line in the doctrine that already requires
POSIX-form command checks saying that `set -o pipefail` is not POSIX — that one line would have
prevented five broken checks and the gate refusal that finally exposed them.
