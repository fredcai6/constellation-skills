# Constellation Feedback Export

Lessons scoped `constellation` — about the skills, templates, or engine themselves,
not this project. Appended by the feedback/closeout steps; swept by the skills
repo's `collect_feedback.py`, which treats scope tags as claims to verify
(cross-project recurrence is the validator). Per-entry collection/resolution
state lives in the sidecar `CONSTELLATION_FEEDBACK.collected.json` (script-owned;
collected means ingested by a sweep, resolved means acted on upstream — a
candidate stays visible in sweep reports until resolved). Just append entries;
never edit the sidecar by hand. Never archived with a run.

Recurrence is the validator, so a finding's **identity must be stable across
runs**. When this export derives from a `constellation`-scoped lesson, carry that
lesson's id in the **Lesson** field — the sweep fingerprints on it, so the same
finding groups even as its prose/slug drift. Reword a recurring finding by
`amend`-ing the lesson (its id is preserved), not by inventing a new slug. Only
when there is no originating lesson does the sweep fall back to the candidate
slug.

## `<date>` — `<project>` — `<work-id>`

- **Lesson:** `<originating lesson:id from LESSONS.md (stable identity), or n/a>`
- **Candidate:** `<short-kebab-slug>`
- **Observed:** `<the skill/template/engine behavior that was ambiguous, missing, wrong, or improvised around>`
- **Cost:** `<what it caused>`
- **Proposal:** `<concrete change to the skill set>`
- **Grounding:** `<artifact + line citation from this project>`
- **Template vintage:** `<template name + baseline sha (short) from TEMPLATES_MANIFEST, or n/a>`
- **Confidence:** `high | medium | low`
