## What

`skills/interrogator/templates/INTERROGATION.template.json`'s `zc-consolidate` fill carries the
identical placeholder defect that `skills/reviewer/`'s `r6-fowler` carried before #465: an
unfilled placeholder that `record(result="pass")` executes as a `command`-kind postcondition, and
the identical "an open fail cannot consolidate to APPROVE" prose claim that ignores the
engine's `--override-reason` path (`docs/CHECKLIST_SCHEMA.md:276`).

## Why it matters

`zc-consolidate`'s template is already `type: "survey"`, so #465's engine-side fix (lifting
`amend`'s `retext-check` op onto surveys) already supplies the half that matters most. Only the
interrogator's prose remains — the fix is a same-shape, much smaller version of #465's own change.

## Evidence

- `.agent-work/w3a-465/RESULT.md` section 7, item 1 (this triage candidate's origin)
- `skills/interrogator/templates/INTERROGATION.template.json` `zc-consolidate`
- Compare `skills/reviewer/SKILL.md`'s corrected sentence (commit `6774e75e`) as the pattern to mirror

## Suggested scope

Correct the interrogator's `SKILL.md` (or equivalent) prose the same way #465 corrected the
reviewer's — name the `--override-reason` path, drop the "cannot consolidate" absolute claim. No
engine change needed; the survey-retext-check affordance already lifted in #465 covers it.

## Out of scope

Any other prose or structure in `skills/interrogator/**` — this candidate is scoped to the one
mirrored defect.

## Origin

Raised during #465 (epic #418 wave 3), out of that issue's fence (`skills/interrogator/**`).
