# Constellation Feedback Export (staged — fenced, see FENCE.md)

## 2026-07-25 — f1Brainz — epic659-661 (SegmentMap)

- **Lesson:** lesson:engine-artifact-attest
- **Candidate:** engine-refuses-attest-on-artifact-postconditions
- **Observed:** `attest` is refused for `artifact`-kind postconditions (`review-result`,
  `implementer-result`, `user-decision`); the correct verb is `attach` (or `attest --evidence <id>`
  to satisfy a sibling gate's identical artifact postcondition by reference). This run confirmed
  the workaround holds with zero friction once known — `attach` used for every artifact
  postcondition (understand/plan/triage/review user-decision; g1/g2 implement implementer-result;
  g1/g2 review review-result), and `attest g2-integrate --cond c2 --evidence e-g2-review-1`
  satisfied the integrate APPROVE-match by reference. But the first-instinct-is-`attest` gap
  remains; the dry-run flags this as the 19th unfixed recurrence.
- **Cost:** none this run (workaround is muscle-memory for this Commander).
- **Proposal:** make `attest`'s refusal on an artifact-kind postcondition emit the exact
  `attach ... --type <evidence_type>` command inferred from the postcondition's declared
  `evidence_type`, so the redirect is a single copy-paste; or alias so one verb covers both
  null-check and artifact-kind conditions.
- **Grounding:** this run's spine.json/execute.json journal — every artifact postcondition
  satisfied via `attach`/`attest --evidence`; `.agent-work/LESSONS.md` lesson:engine-artifact-attest
  (19th recurrence per this run's apply_lessons_delta dry-run).
- **Confidence:** high

## 2026-07-25 — f1Brainz — epic659-661 (SegmentMap)

- **Lesson:** lesson:from-child-refuses-on-gated-checklist
- **Candidate:** gated-child-consolidation-not-from-child
- **Observed:** the Commander spine's `execute` step names `execute.json` (type:gated) as its
  `child_checklist`. When execute.json reached DONE, the spine's `execute.c1` (check:null) was
  satisfied by a plain `attest execute --cond c1` — NOT `advance execute --from-child execute.json`
  (which only works for a survey child via the `consolidation` field). This run knew the workaround
  from the banked lesson and hit no refusal, but the spine template's `execute` imperative still
  does not say "do not use --from-child for the gated child_checklist," and the engine's from-child
  refusal message still does not hint at the survey-only restriction — so a Commander without the
  banked lesson would rediscover it. First recurrence since the lesson was banked (624-phase0).
- **Cost:** none this run (workaround known).
- **Proposal:** either add to `COMMANDER_SPINE.template.json`'s execute-step imperative an explicit
  "the child_checklist is gated — satisfy execute.c1 with a plain `attest` once the child is DONE,
  do NOT use `advance --from-child` (that is survey-only)"; or make the engine's from-child refusal
  message name the survey-only restriction.
- **Grounding:** this run's spine.json journal (`attest execute --cond c1` after execute.json DONE,
  no --from-child attempted); `.agent-work/LESSONS.md` lesson:from-child-refuses-on-gated-checklist
  (banked 624-phase0, this is the 1st confirming recurrence).
- **Confidence:** high
