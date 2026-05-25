# Constellation Status Model

## Step Status

Use for checklist/controller steps:

```text
pending | in-progress | blocked | complete | skipped
```

Rules:

- `skipped` requires `skipped because <reason>`.
- `blocked` requires blocker, owner/authority needed, and next action.
- `complete` requires evidence or note.

## Crew Return Status

Use for implementer/reviewer result status:

```text
complete | partial | blocked | out-of-scope | failed
```

Rules:

- `partial` requires completed portion, missing portion, and next action.
- `blocked` requires blocker and needed authority/evidence.
- `out-of-scope` requires scope concern and return-to-Pilot note.
- `failed` requires failure evidence and recommended recovery.

## Review Verdict

Use for reviewer judgment:

```text
APPROVE | BLOCK | COMMENT
```

Rules:

- `APPROVE` means no blockers found against handoff, evidence, scope, and project rules.
- `BLOCK` requires blockers.
- `COMMENT` means observations only; gate may still need Pilot decision.

## Pilot Decision

Use for evidence integration and gate control:

```text
continue | ask user | revise plan | send back to Crew | request Cartographer | collect Triage candidate | close out | stop Pilot
```

Rules:

- Reviewer approval alone does not close a gate.
- Pilot closes gates only after required evidence is integrated.
- Any decision that changes scope, authority, architecture, or evidence requires recorded authority.
