# Triage Recommendation: 2 `falsifiable-unresolved-placeholder` faults left in the shipped corpus

## Classification
`bug`

## Source checklist/artifact
- epic-569/w3-promote g0-corpus-survey and g8-validate-spine-wiring-and-docs

## Structural anchor
`path: skills/commander/templates/EXECUTE_PLAN.template.json; skills/implementer/templates/IMPLEMENTER_PLAN.template.json`

## Cartographer mismatch class
`none`

## Observations

### Observation 1
- **What's wrong:** `EXECUTE_PLAN.template.json`'s `g1-integrate.c1` condition (or the sibling
  `g1-implement.p1` — both trace to the same literal unfilled placeholder text) carries a raw
  template placeholder string (e.g. `"<exact test command>"`/`"<qualitative dependency on a prior
  gate, or none>"`) in the shipped file, which `scripts/validate_spine.py` flags as
  `falsifiable-unresolved-placeholder` when scanning the shipped template directly rather than an
  instantiated spine.
- **Expected:** the shipped template either resolves the placeholder to a real value, or
  `validate_spine.py`'s scan is scoped to skip templates whose placeholders are meant to be filled
  per-run at authoring time (this may already be correct behavior for a *different* reason — see
  Open Questions).
- **Conditions:** running `scripts/validate_spine.py` (or the `discover_checklist_templates` +
  `validate_file` sweep) directly against the shipped `skills/*/templates/*.json` files.
- **Type:** `measured` — `python3 -c "... discover_checklist_templates + validate_file sweep ..."`
  → `{'falsifiable-all-null': 13, 'falsifiable-unresolved-placeholder': 2}`, one of the two
  attributed to `EXECUTE_PLAN.template.json`.
- **Rev:** `epic-569/w3-promote` branch, commit `4d92dc45` (this wave's own final commit — the
  fault predates this wave and was measured, not caused, by it).

### Observation 2
- **What's wrong:** same defect class in `IMPLEMENTER_PLAN.template.json`'s `m1.c2` — its `command`
  field holds the literal `"<exact test command>"`.
- **Expected:** same as Observation 1.
- **Conditions:** same as Observation 1.
- **Type:** `measured` — same sweep, the other of the two `falsifiable-unresolved-placeholder`
  faults.
- **Rev:** same as Observation 1.

## Open questions
- Is `falsifiable-unresolved-placeholder` even the right code for a placeholder that every
  Commander is *expected* to fill at authoring time (per-run, in its own `execute.json` copy),
  rather than a defect in the shipped template itself? `epic-569/w3-promote`'s own g0 survey found
  this same shape at `EXECUTE_PLAN.template.json`'s `g1-implement.p1` and treated it as "not a
  bucket at all in the shipped file's own right" — the placeholder is filled per-run, not a defect
  to promote away. If that reasoning is right, the fix may be to scope `validate_spine.py`'s
  placeholder check to skip these two specific, intentionally-per-run-filled fields, not to fill
  them in the shipped template (which would be meaningless — there is no single correct value).

## Recommended priority
`low`

**Reason:** neither fault blocks anything today; both were explicitly declined as out of
`epic-569/w3-promote`'s own promotion scope (a different defect class than `check: null`) per
`decision:validate-spine-wiring-is-in-scope`'s settle clause, and the corpus-wide
`falsifiable-all-null` floor this wave DID own was not blocked by them.

## Related artifacts
- `.agent-work/w3-promote/notes-1.md` g8 section
- `.agent-work/w3-promote/RESULT.md` §5

## Disposition
`recommend-and-defer`

**Detail:** issue-filing authority is unclear this run — no explicit issue-creation authority is
named in `docs/agents/ORCHESTRATOR_CONTEXT.md` or the launch order's Inherited Latitude section;
delegated mode with no reachable human this gate. Also genuinely underspecified (see Open
Questions) — worth a human ruling on whether this is a `validate_spine.py` scoping fix or a
template fix before anyone files a specific issue.

## Issue creation authority
`issue-ready only`
