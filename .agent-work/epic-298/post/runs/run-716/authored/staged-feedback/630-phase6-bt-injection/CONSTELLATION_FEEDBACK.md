# Constellation Feedback Export (staged — fenced, see FENCE.md)

## 2026-07-25 — f1Brainz — 630-phase6-bt-injection

- **Lesson:** lesson:engine-artifact-attest
- **Candidate:** engine-refuses-attest-on-artifact-postconditions
- **Observed:** `attest` is refused for `artifact`-kind postconditions (e.g. `review-result`,
  `implementer-result`, `user-decision`); the correct verb is `attach`. This run confirmed the
  workaround holds (used `attach` throughout, zero friction once known) but the underlying
  ergonomic gap remains: an agent's first instinct at an artifact-kind postcondition is
  `attest` (it reads like the natural "confirm this is done" verb), and the engine's refusal
  message is the only thing that redirects to `attach`.
- **Cost:** none this run (the redirect message is clear and the workaround is now
  well-known/muscle-memory for this Commander), but this is the 16th confirmed recurrence of
  the same underlying friction across the fleet's history per `.agent-work/LESSONS.md`'s
  recurrence count — the fix belongs upstream (a friendlier default, or `attest` transparently
  routing to `attach` for artifact-kind conditions when no qualitative judgment is actually
  needed) rather than in continuing to confirm the same workaround indefinitely.
- **Proposal:** either rename/alias so the same verb works for both null-check and
  artifact-kind postconditions (removing the need to know which kind a condition is before
  choosing a verb), or make the refusal message's redirect a single-command copy-paste
  (it already is close — consider whether `attest`'s refusal could literally emit the exact
  `attach ... --type ...` command to run, inferred from the postcondition's declared
  `evidence_type`).
- **Grounding:** this run's spine.json/execute.json journal (every artifact postcondition
  satisfied via `attach`, e.g. `g1-implement.c1`, `g2-review.c1`, `understand.c1`,
  `plan.c3`, `triage.c2`, `review.c1`); `.agent-work/LESSONS.md` lesson:engine-artifact-attest,
  mentions: (see playbook header) — 16 confirmed recurrences before this run's dry-run flagged
  further bare-confirm as recurrence-debt rather than new signal.
- **Template vintage:** n/a (engine behavior, not a template)
- **Confidence:** high

## 2026-07-25 — f1Brainz — 630-phase6-bt-injection

- **Lesson:** lesson:run-crew-cli-launcher-misfit
- **Candidate:** no-headless-claude-cli-in-agent-tool-harness
- **Observed:** `run_crew.py`'s default/spawn backend assumes a headless `claude -p` CLI
  binary is launchable as a subprocess; in the Constellation Agent-tool harness (this
  environment) no such binary exists, so every crew dispatch this run used
  `--dispatch external` (record-only registry entry) + a synchronous Agent-tool subagent
  call + `--verify-result` after the subagent returns. This worked cleanly for all 9
  dispatches this run (0 registry conflicts, 0 stale/duplicate-crew refusals), but it is a
  two-step manual choreography (record the durable entry, THEN separately dispatch the
  actual agent, THEN separately verify) that a first-time Commander would not discover
  without already knowing to read `references/crew-dispatch.md`'s "Backend: CLI vs
  Agent-tool harness" section.
- **Cost:** none this run (the pattern is now well-documented in
  `references/crew-dispatch.md` and this Commander followed it without friction), but this
  is the 11th confirmed recurrence of the same underlying environment mismatch — the fix
  belongs upstream (an `external` backend that IS the harness-native Agent-tool dispatch
  path directly, rather than a manual three-step choreography around a CLI-shaped
  abstraction that doesn't fit this harness) rather than in continuing to confirm the
  workaround indefinitely.
- **Proposal:** consider whether `run_crew.py` could detect the Agent-tool harness
  environment directly (not just "no `claude` on PATH") and provide a single combined
  helper — e.g. a thin wrapper that records the registry entry AND returns the exact
  Agent-tool dispatch parameters/prompt template needed, so a Commander doesn't have to
  remember to chain 3 separate commands correctly every time.
- **Grounding:** this run's `crew-runs.json` (9 entries, all `backend: external`,
  `dispatch: external`, all reaching `completed`/fresh via `--verify-result`);
  `.agent-work/LESSONS.md` lesson:run-crew-cli-launcher-misfit, 11 confirmed recurrences
  before this run's dry-run flagged further bare-confirm as recurrence-debt.
- **Template vintage:** n/a (engine/script behavior, not a template)
- **Confidence:** high
