# Lesson Candidates: `<run-or-epic-id>`

Nominations only — nothing here is applied until the dispatcher routes it. Every
candidate cites a grounding artifact line; ungrounded candidates were discarded.

## Candidates

### `<short-kebab-slug>`
- **Scope:** `handoff | commander | admiral | project | constellation`
- **Task-class:** `general-workflow | <domain tag>`
- **Observed:** `<the exact step, field, or instruction that was ambiguous, missing, wrong, or improvised around>`
- **Cost:** `<what it caused — rework, rediscovery, wrong assumption, incident>`
- **Proposal:** `<concrete change>`
- **Grounding:** `<artifact + line/entry citation>`
- **Corroboration:** `<telemetry that backs it (rework/BLOCK/waive/incident) | assertion-only>`
- **Confidence:** `high | medium | low` `<low = queue for human review, do not propagate>`
- **Routing:** `template delta (<which template>) | playbook delta (<op>) | Charter nomination | constellation export | retire lesson:<id> | drop — <reason>`

## Existing-Lesson Reconciliation
- `confirm lesson:<id>` — `<grounding>`
- `disconfirm lesson:<id>` — `<grounding>`
- `<or none — checked Active lessons against this run's evidence>`

## Playbook Delta (ready to apply)

For the dispatcher to write to `lessons-delta.json` and apply via `apply_lessons_delta.py`. Only `high`/`medium` confidence playbook-routed candidates appear here.

```json
{
  "work_id": "<run-or-epic-id>",
  "tick": true,
  "ops": []
}
```

## Queued for Human Review
- `<low-confidence candidates and out-of-scope observations, or none>`

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed after review: <what you checked>`.
- **Brief gaps:** `<what the run brief should have carried>`
- **Artifact gaps:** `<what was unreadable, missing, or written too performatively to use>`
- **What would have made this audit easier:** `<one concrete change>`
