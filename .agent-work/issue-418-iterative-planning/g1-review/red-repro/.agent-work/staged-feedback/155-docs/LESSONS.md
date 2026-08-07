# Lessons Playbook

<!-- playbook-state: run-tick=1 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=issue-155 -->

Open problems carried forward — NOT a log of everything learned. If a lesson is
understood and fixable, apply the fix and record it in AGENT_FEEDBACK; do not
bank it here. A lesson lives here only because it needs to be re-observed to be
understood, so every `add` states a bank-reason (what re-observation will
clarify). Reaching the cap is a failure mode — it means the bank is being used
to accumulate instead of to adjudicate. Read the Active section at the Commander
context step. Never edit by hand or by LLM: apply structured deltas via
apply_lessons_delta.py, which enforces cap, grounding, and counter rules.

Counter semantics split by scope: for most scopes a confirm is trust
(the lesson held again). For a constellation-scoped lesson it is the
opposite — a recurrence of an unfixed shared-machinery defect, so it
accrues recurrences (debt) and flags recurrence-debt. Pay the debt by
exporting to CONSTELLATION_FEEDBACK and fixing upstream. Once the fix
ships, `resolve` the lesson (cite the shipping PR): it goes terminal
(fixed-upstream) — never ripe again, a later confirm is ignored rather
than re-exported, and it ages out of the playbook on its own. Do not keep
confirming a constellation defect into a permanent workaround.

## Active

### lesson:from-child-gated-consolidation-refusal
- scope: constellation
- task-class: commander-spine-execute-close
- statement: checklist_engine.py's `advance <spine-step> --from-child <execute.json>` assumes the child checklist is a `survey` (it reads `child.consolidation`, set only by the `consolidate` verb, which itself refuses on a `gated` file). A `gated` execute.json child -- the normal case for a Commander's own execute plan -- has no `consolidation` key at all, so `--from-child` REFUSED twice in a row (relative path -> 'not found'; absolute path -> 'has no consolidation yet') before the real cause (gated vs survey mismatch) was findable only by reading the engine source directly.
- grounding: issue-155 (W3-155-docbatch), execute step: `advance execute --from-child .agent-work/issue-155/execute.json` REFUSED 'not found', then with an absolute path REFUSED 'has no consolidation yet'; `consolidate` itself then REFUSED 'consolidate is for survey checklists'. Advancing spine `execute` WITHOUT `--from-child` (plain `--why`) succeeded immediately once the gated/survey distinction was understood from checklist_engine.py source (lines ~1038-1058).
- bank-reason: This is a design/ergonomics question for the engine owner, not something a Commander run can fix in-place: either `--from-child` should special-case a `gated` child (deriving an implicit all-terminal consolidation from `items` state) or its REFUSED text on a gated child should say so directly instead of the current two-step discovery path. Needs a human call on which fix is right, and checklist_engine.py is outside this run's file-ownership fence regardless -- banking to re-observe whether this recurs for other Commander runs closing a gated execute.json via --from-child before deciding the fix.
- target: scripts/checklist_engine.py (advance()'s --from-child handling, or its --help/REFUSED text)
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-19 (issue-155)
- last-confirmed: none
- runs-since-confirmed: 1
