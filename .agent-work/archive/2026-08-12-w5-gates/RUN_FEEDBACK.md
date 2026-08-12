# Run feedback — w5-gates (epic #418, wave 5)

Written at the `feedback` gate by `commander-w5-gates-g`, the seventh session on this
run. Earlier sessions did the substance; this is the consolidated reflection the gate
asks for, plus the crew Workflow Feedback harvested at each `gN-integrate`.

## How closely the run followed the skills, handoffs and checklists

Closely, in the sense that matters: no gate was closed on an unmeasured claim, and the
one gate that could not be passed honestly was waived on named authority rather than
forced green. The run produced four implemented gates (g1–g4), each with an independent
review, and every review finding was either discharged or routed.

The place the run did *not* follow doctrine cleanly is session continuity. Seven
Commander sessions drove one run. Six of those handoffs were caused by the context
gauge, and at least four were caused by the gauge defect described below rather than by
real context exhaustion. That is the dominant fact about this run's execution and it is
not a quality problem in the work — it is overhead the mechanism imposed on itself.

## Where I had to improvise or work around the instructions

- **The final gate's own check is broken.** `archive.c2b` ships an unsubstituted
  `<branch>` placeholder. The engine runs check text through `sh -c`, where an unquoted
  `<` is input redirection: the shell tries to open a file named `branch`, exits 1, and
  `gh` never runs. It is red in every state of the world. This wave *fixed* that defect
  at g3, but the spine was instantiated before g3 landed, so the run driving the repair
  never received it. Resolved by an Admiral waiver after the substance was independently
  confirmed — branch pushed, PR #516 open with all six closing references — and not by
  hand-substituting the branch name.
- **Episode capture had already been done when I was briefed to do it.** My launch brief
  said the `feedback` step was outstanding in full. Running the capture gate first showed
  five episodes already recorded and green. I wrote only the reflection and added the
  four episodes the crew feedback warranted, rather than re-applying a delta that would
  have minted duplicates — the writer assigns ids by run+sequence scan, so re-applying
  the previous delta would have created `w5-gates-006` through `-010` as copies.
- **Two of the Admiral's files show as modified with an empty diff.**
  `.agent-work/epic-418-redux/transitions/close-to-w5/{CURRENT_TRUTH,WAVE_REVIEW}.md`
  appear in `git status` as `M`, but `git diff` on them is empty — pure CRLF
  normalization, no content change. Nobody touched the Admiral's area. Flagging it
  because a crew told "do not touch these" sees them dirty and may either panic or, worse,
  commit them to make the tree clean.

## What was ambiguous, missing or contradictory

The sharpest contradiction is doctrinal, and it bit twice at two different levels: the
reach-up doctrine says to file a refresh-request and go idle, while crew doctrine says
the result file *is* the task and that going idle with it unwritten strands the gate with
no error signal. Those collide precisely when a trip fires *after* the work is done but
*before* it is recorded. The g3 implementer hit it and resolved it by doing both. My
predecessor hit the same shape at `feedback` — episodes captured, reflection unwritten —
and the handoff could not express "the work behind this gate is already green."

## Crew Workflow Feedback harvested at each gN-integrate

Recurring across crews, in descending order of how many crews paid for it:

1. **`--session-id` must follow the verb** (g1-review, g2-review, g3-review — three
   crews). The reference lists it in a per-verb flag list, which does not convey
   positional requirement; placing it first fails with `invalid choice`, and the first
   `start` failure reads like a lease conflict rather than a parse error.
2. **Handoffs asserted `.agent-work/` is untracked; it is tracked here** (g2-review,
   g3-review). The g2 commit carries nine tracked `.agent-work/w5-gates/` files. The
   g3 reviewer nearly raised a false scope alarm.
3. **PATH composition was never stated** (g3-implement, g3-review — two crews, one
   gate). `gh` yes, `jq` no, `bash` yes, `python` yes. The gate's expensive part was
   entirely determined by that answer and both crews discovered it independently.
4. **Expected-count claims without their reasoning are traps in both directions**
   (g2-review, g3-review, g4-review). "RED twice" without saying which two of three
   subtests; a table naming 500 subtests when 501 was the number to expect post-commit;
   criteria 1 and 7 asking different questions about the same four survivors.
5. **Stale line-number anchors** (g2-implement): the handoff's own re-measured line
   numbers were already off by two. Harmless because the same handoff said to find code
   by text, but it shows anchors go stale faster than the warning about them.
6. **Template gaps around TDD shape** (g1-implement, g2-implement, g3-implement): the
   `IMPLEMENTER_PLAN` template has no vocabulary for a slice that contains a sanctioned
   expectation change, nor for a test-after gate whose floor is "a test must go red on a
   broken input."
7. **Engine findings are passed as shell arguments** (g3-review), so a finding containing
   `$(...)` — unavoidable when the subject under review *is* a shell command — is command
   substituted before the engine sees it.
8. **The engine wrote a nested `.agent-work/w5-gates/w5-gates/` tree** (g1-review) when
   driving a survey whose `work_id` matches the directory it already lives in. Harmless
   clutter that closeout will read as an orphan.
9. **Reviewer skill vs engine mismatch for surveys** (g3-review): the skill says to
   `advance` each recorded check; for a survey the engine answers `REFUSED: advance is
   for gated checklists; use record`.

## What would have helped

One line in each handoff naming what is on PATH. One line stating that `.agent-work/` is
tracked. Scope assertions phrased against a named commit rather than a range. And, above
everything else on this run, a context gauge that reports the reading of the agent asking
for it — that single defect cost this wave more sessions than all the engineering did.
