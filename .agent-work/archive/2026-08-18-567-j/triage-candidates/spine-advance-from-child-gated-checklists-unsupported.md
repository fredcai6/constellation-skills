# Triage candidate: `spine_advance --from_child` refuses a completed GATED child checklist

**Found at:** execute step closeout, this lane.

**What happened:** `execute.json` (the Commander's own gate plan for this run,
`type: "gated"`) has no MCP door binding of its own — the MCP door only
binds one spine per process, and this process was already bound to the
parent `spine.json`. Driving `execute.json` therefore went through
`checklist_engine.py`'s CLI directly (`--file .agent-work/567-j/execute.json`),
which the launch order itself anticipated ("If you find yourself reaching
for `checklist_engine.py` on the command line, stop and record it — this
epic exists to remove that path").

Once every gate in `execute.json` was closed, folding that completion back
into the parent spine's `execute` postcondition (`c1`) should have used
`spine_advance --from_child <path>` per the MCP tool's own documented
contract ("path to a child checklist file whose consolidation attaches as
review-result before advancing"). Two refusals in sequence:
1. A relative `--from_child` path refused with "child checklist ... not
   found" — needed an absolute path.
2. With the absolute path, refused with "child ... has no consolidation
   yet." Running `checklist_engine.py ... consolidate` on `execute.json`
   directly then refused with "consolidate is for survey checklists" —
   `execute.json` is `type: "gated"`, and `consolidate` (and, it appears,
   `from_child`) is built for a `type: "survey"` child (e.g. a reviewer's
   `REVIEW_SURVEY.json`), not a `gated` one.

The actual close worked by falling back to a plain `spine_advance` with no
`from_child` at all, attesting the parent gate's own `c1`/`c2` postconditions
directly from evidence already gathered while driving the child.

**Why it matters:** `from_child` is documented as the mechanism for folding
a driven child checklist's result into its parent, but it silently only
supports the `survey` shape. A Commander whose own gate plan (`execute.json`)
is always `gated` cannot use the documented consolidation path for the one
child checklist every Commander run produces — this is not an edge case, it
is the central shape of the role.

**Recommendation (not mine to decide or file):** either extend
`from_child`/`consolidate` to accept a completed `gated` child (folding its
terminal state the same way a `survey`'s consolidation folds in), or update
the tool's own documentation/rail text to say plainly that `from_child` is
survey-only, so a Commander doesn't have to rediscover this by trial and
error at the one moment (execute closeout) every run reaches.

**Disposition:** staged only, per `decision:no-issue-filing-mid-run`. Filed
nowhere; the human or Admiral routes this from here.
