# Workflow feedback — `cmdr-567-f` (epic #567 lane F)

Staged rather than written to the durable root; see `FENCE.md` beside this file. Advisory,
per `docs/agents/ORCHESTRATOR_CONTEXT.md`: "Feedback is advisory and may be brief or
absent." The 3 episodes at `episodes/active/567-f-*.md` are the record; this is the
reflection.

## How closely I followed the skills, handoffs and checklists

Closely, no code-scope deviations. This lane's mission was measure-first, and the
measurement itself was the deliverable: `scripts/run_crew.py` has zero diff on this branch.
I drove `execute.json` (the plan's own sub-checklist) via `checklist_engine.py`'s CLI
directly rather than through the MCP door, because the door's verbs are scoped to the one
spine this process is bound to (`567-f/spine.json`), and `execute.json` is a separate,
secondary artifact `commander-core.md` describes as driven "in this context" -- not the
bound spine itself. I did not read that as the CLI-workaround the launch order warns against
(which is about avoiding the door for the *bound* spine), but if that reading is wrong, it's
worth the Admiral naming explicitly, since I could find no MCP verb that targets a checklist
file other than the bound one.

## Where the instructions were ambiguous, missing, or contradictory

- **`plan`'s c6 (`verify-frame`) and a degraded-map mission frame fight each other by
  default.** Writing the frame's own explanatory prose in the natural way -- naming a
  governing decision as `decision:map-index-is-admiral-owned` -- trips the anchor scanner
  even though the mention was never meant as a map citation; ANY matched anchor is an
  automatic refusal in DEGRADED mode, with no distinction between "citing a real map node"
  and "mentioning a decision's name in prose." Fixed by rewording the decision references
  in plain words and citing the DEGRADED substitutes literally, which made the check pass
  genuinely -- see the episode for the fuller before/after.
- **`spine_evidence action=waive` refuses on your own bound spine unconditionally**, even
  for a Commander waiving its own gate's non-blocking check, with instructions to
  `spine_halt block` and ask up instead. Correct as a safety property, but the refusal
  message reads as if the only path forward is to stall the run on the Admiral -- when the
  actual fix (rewrite the frame so the check passes on its own merits) was available and
  local. Worth a one-line addition to that refusal's own text suggesting "or make the
  underlying check pass" before "ask up," since a literal reading otherwise pushes toward
  blocking on something fixable in five minutes.
- **`docs/agents/engine-config.json` does not exist** though `context`'s imperative names
  it as a project delta to read; treated as optional (the schema's own `context_refs` marks
  it `required: false`) and recorded here rather than substituted.

## What would have helped

- A short note in `commander-core.md` or `crew-dispatch.md` stating explicitly that
  `execute.json` is driven via `checklist_engine.py --file execute.json` (a separate
  artifact) rather than through the MCP spine door -- I inferred this correctly but had to
  reason it out from the door tools' own descriptions ("acts on the spine THIS door is bound
  to") rather than being told directly, and the launch order's "if you reach for
  `checklist_engine.py`, stop and float it" warning made me second-guess a legitimate use of
  it.

## Crew workflow feedback, harvested

None -- no crew was dispatched this run (the execute gate was authored as a single
reasoning gate, crew-waived: the deliverable was the measurement writeup itself, not code or
an independently-verifiable change).

## What went well, briefly

The measurement itself was clean and fast to ground: `run_crew.py`'s own `--help` text,
source reads with exact line numbers, a live demonstration (this session's own dispatch is
proof of the mechanism), and existing test coverage
(`test_spine_only_branch_names_no_document_and_names_spine_status`,
`test_external_backend_refuses_spine_only_with_no_handoff`) all agreed, so the honest-null
verdict rests on multiple independent kinds of evidence rather than one read of the code.
The pre-rulings (`decision:honest-null-is-likely-and-fine`, `decision:no-issue-filing-mid-run`)
made the right call cheap to take -- there was no pressure to manufacture a build to justify
the session.
