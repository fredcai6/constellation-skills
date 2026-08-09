# Initial-cut contracts and filing seam

`SHAPED_BRIEF.template.json` is the direct, versioned input. Its v1 fields are
strict: unknown, missing, empty, wrongly typed, wrongly enumerated, or
unconfirmed values fail fast. `parked_possibilities` is an array of nonempty
strings; it may be empty.

The output manifest copies `title` to `epic.title`, `source_path` to
`epic.spec_path`, and preserves the shaped intent, definition of done,
good-enough boundary, hard constraints, fixed decisions, forecast,
uncertainties, and parked possibilities. Runnable drafts exist only at
`current_wave.issues`.

Each current issue requires `id`, `title`, `desired_outcome`, `useful_now`,
`appetite`, `acceptance_or_falsification_evidence`,
`implementation_latitude`, `hard_constraints_no_gos`, `local_unknowns`, a
nonempty `anchors` array, `type` (`AFK` or `HITL`), and `blocks`. `hitl_reason`
is required only for HITL. Zero edges is valid; targets must exist and the
graph must be acyclic.

Forecast entries contain only `outcome`, `why_likely`, and `entry_conditions`.
Uncertainties contain `unknown`, `affects`, `settle_by`, `current_evidence`, and
`next_probe`. Neither shape is tracker-runnable.

The epic body renders exactly these level-two headings: Intent and why;
Definition of done; Good-enough boundary and appetite; Hard constraints and
fixed decisions; Current wave; Wave forecast (nonbinding); Active uncertainty
register; Parked possibilities.

Every tracker implements `find_epic`, `create_epic`, `find_issue`, and
`create_issue`. Deterministic keys are embedded in bodies and recorded in a
manifest-bound receipt. On a retry, receipt entries are checked against the
expected manifest and entity keys before any adapter call. Missing entries are
recovered by key lookup. Epic and every child are safe across before-file,
after-file-before-receipt, and after-receipt crash windows.
