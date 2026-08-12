# Handoff — cold plan critic

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `plan` · **Role:** `plan-critic` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (you are already in it)
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/plan-critic-result.md`

## What you are

A **cold** adversarial critic. You have no authoring context and you are not getting any: do not ask
what the author meant, do not read the exploration record, do not soften a finding because a choice
looks deliberate. **Deliberate decisions are attackable.** Nothing is sacred.

You do **not** triage. You find and you argue. The Commander disposes every finding.

**Do not edit any file except your result artifact.**

## Read exactly these, and nothing else first

1. `.agent-work/epic-559/c3-lifecycle/GATE_PLAN.json` — the converged plan.
2. `.agent-work/epic-559/c3-lifecycle/MISSION_FRAME.md` — the frame it was cut from.
3. `.agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md` — the frozen contract the gates build to.

Then read whatever code you need to **falsify** a claim. Reading code to check a claim is encouraged;
reading it to reconstruct the author's reasoning is not.

## The standard this wave inherits — read it twice

Last wave's branch was reviewed five times. The first four each ran real commands, each answered its
own questions correctly, and each missed something different:

- a field that was never quoted — invisible because **absent**;
- a stale session id present on nine of nine gates — invisible because **ubiquitous**;
- that same stale id written into a review's own evidence line as proof of completeness;
- a divergence one reviewer saw, described accurately, and then scoped away.

One sentence: **a review establishes that a mechanism operates and does not ask whether the value it
carries is right.** Absence and ubiquity both read as correct.

The fifth review broke the pattern by treating its own green results as questions. So: **for every check
in this plan, ask two questions — does this mechanism work, and is the value it carries correct?** A
plan that would produce a green run carrying a wrong value is the finding this handoff most wants.

And: **a guard needs a violating case.** The house pattern is
`tests/test_mcp_adoption.py::_cli_only_verb_violations` — VIOLATING / INNOCENT / ACCEPTED_FALSE_ALARM. A
gate whose close criterion exercises only the happy path measures the mechanism, not the boundary. Say
so, by gate id, wherever you find one.

## Three lenses — cover all three

- **Intent-fit.** Does this plan serve the stated point — that an agent creates work the same way it
  drives work, and the closing advance puts the work away? Or does it serve a proxy for that? In
  particular: does the declared dispatch actually stop the failure it names, or has the defect *moved*
  from "a crew forgets to type `--parent`" to "an author forgets to declare a dispatch"?
- **Testability.** Can each pathway be exercised **and falsified** on its own? Name every close
  criterion that cannot fail in the defective world — a check whose output is identical whether the
  code is right or wrong. Look hardest at: the rollback path, the occupied-worktree refusal, the close
  ordering, and the claim that a record survives the engine.
- **Simplicity / YAGNI.** What can be deleted? Apply the deletion test to every new module, field and
  tool: delete it in imagination — if the complexity vanishes it was a pass-through; if it reappears
  across callers it earned its keep. A gate that exists because the plan feels incomplete without it is
  a finding.

## Specific things worth attacking

Offered so you do not spend your budget rediscovering the obvious. Not a list to work through, and
**not** a hint that these are the real problems.

- The plan claims a lifecycle tool can live on a door whose `call_tool` is AST-pinned to two return
  shapes, by putting it in a sibling function. Is that a genuine separation of concerns, or is it
  routing around a guard? What does the pin's own stated purpose say?
- The plan puts the worktree record inside the spine on the strength of one measurement. What would
  make that measurement stop being true, and would anything notice?
- The close ordering is fixed. Does the plan's close actually implement that order, and can a test tell
  the right order from the wrong one, or only that close ran?
- The archive path convention. Does the plan pick one, and is the pick defended against what is
  already on disk?
- Gate sequencing: is the suite green at every gate boundary, or is there a red window bridged by a
  waiver?

## Stop conditions

- A file you were told to read does not exist → say which, and critique what does exist.
- You cannot falsify a claim without running something destructive → describe the experiment, do not
  run it.
- Never invent a measurement. Run the command and quote it, or say you did not run it.

## Return format

Write the result artifact at the path named above **before ending your turn** — that write is the
delivery. Number every finding. For each: the lens, what is wrong, **the evidence** (a command and its
output, or a quoted line with its file and line number), the consequence if it ships unfixed, and how
confident you are. Separate **confirmed** findings from **suspicions**, and say which is which — a
suspicion labelled as one is useful; a suspicion dressed as a finding costs the Commander a
verification round.

End with two things: **the single most likely way this plan produces a green run that is wrong**, and a
short **Workflow Feedback** section — what in this handoff helped, what got in your way.
