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

## `2026-07-24` — `constellation-skills` — `issue-227`

- **Lesson:** `n/a` (no originating LESSONS.md entry — this is a template-content defect, not a recurring project pattern)
- **Candidate:** `launch-order-template-asserts-unverified-data-locations`
- **Observed:** The LAUNCH_ORDER template's "Data Locations" section let the Admiral assert, as fact, that `.agent-work/archive/` "holds prior-epic transcripts that may be useful as baseline corpus material." No raw JSONL transcripts exist anywhere under `.agent-work/`. The template invites a confident pointer to input data without requiring the author to have verified it exists, and a delegated Commander reads that section as settled context rather than as a hypothesis to check.
- **Cost:** Gate g1's implementer burned a research detour discovering the claim was false, then had to independently locate the epic's own x1-overread excursion to learn the transcript schema. The gate shipped a synthetic-but-labelled corpus instead of a real one, which permanently scopes issue #227's item-5 acceptance: the instrument is validated as a comparative yardstick but cannot speak to real-world magnitudes. Also surfaced a second-order gap: real transcripts live outside the repo under `~/.claude/projects` and carry user conversation content, so there is no sanctioned redaction path for a run that legitimately needs real-transcript input.
- **Proposal:** Two changes. (1) In the LAUNCH_ORDER template's Data Locations section, require each named input path to carry a verification marker — either "verified present <date>" or an explicit "UNVERIFIED — confirm before relying on this" — so a Commander knows which pointers are load-bearing facts and which are leads. (2) Add a short note on transcript material specifically: real session transcripts are outside the repo and carry user conversation content, so a run needing them requires a redaction/consent path rather than a copy; absent one, a labelled synthetic corpus is the sanctioned fallback and its limitation must be stated in the verdict.
- **Grounding:** `.agent-work/epic-226/launch-orders/LAUNCH_ORDER-227.md` §Data Locations, lines 228-232 ("`.agent-work/archive/` holds prior-epic transcripts that may be useful as **baseline corpus material**"); refuted by `.agent-work/issue-227/results/g1-implement-result.md` §"Out-of-scope discoveries" ("No real JSONL transcripts exist anywhere under `.agent-work/`— confirmed by command"); consequence recorded in `.agent-work/epic-226/verdicts/commander-227.md` §4A.
- **Template vintage:** `LAUNCH_ORDER.template.md` — vintage not recorded in this worktree (no TEMPLATES_MANIFEST present); observed via the instantiated `LAUNCH_ORDER-227.md` at epic-226 filing time.
- **Confidence:** `high` — the falsifying check is a single command over `.agent-work/`, and it was run independently by both the implementer and the Commander.
