# Constellation Feedback Export

Lessons scoped `constellation` — about the skills, templates, or engine themselves, not this project. Appended by the feedback/closeout steps; swept by the skills repo's `collect_feedback.py`. Never archived with a run.

## `2026-07-19` — `constellation-skills` — `157-drill`

- **Lesson:** n/a (fresh finding, no originating LESSONS.md id)
- **Candidate:** `drill-scenario-decontamination`
- **Observed:** Both fresh auditors authoring the two #157 reproduction drills independently hit the SAME contamination trap: a drill scenario that pre-itemizes the divergent clauses (G1) or names the harness/fixtures / frames the deliverable as a pipeline (G2) makes the WEAK-doctrine (before) arm pass too, collapsing the very variable under test. Each had to discard 1-2 attempts and rewrite the scenario to describe roles/missions POSITIVELY (by what they do) or BY OUTCOME, so the failure trigger stays latent and only the doctrine text makes the armed author go looking.
- **Cost:** ~2-3 wasted arm-runs per drill before a clean fail-pre/pass-post separation; risk of a false-PASS drill if the contamination is not caught.
- **Proposal:** Graduate an anti-contamination rule into the reproduction-drill doctrine (its home is the lessons-auditor / `docs/superpowers/specs/2026-07-07-lesson-repro-drills-design.md` or a drills authoring reference): "State the drill scenario positively / by-outcome; never pre-itemize or alarm-flag the failure trigger — a scenario that names or flags what the doctrine is supposed to make the author notice passes both arms and proves nothing." Ship it (per its own doctrine) with a drill.
- **Grounding:** `docs/superpowers/drills/spec-prename-per-role.md` Method notes (Attempts 1-3 decontamination); `docs/superpowers/drills/eval-latitude-preclearance.md` Method notes (first-attempt contamination discarded).
- **Template vintage:** n/a
- **Confidence:** high (independently rediscovered by two fresh agents in one batch)

## `2026-07-19` — `constellation-skills` — `157-drill`

- **Lesson:** n/a (fresh finding)
- **Candidate:** `delegated-commander-in-team-synchronous-crew`
- **Observed:** A delegated Commander running as an in-process TEAMMATE cannot dispatch named subagents (flat roster) nor background subagents ("in-process teammates cannot spawn background agents") — every crew member (auditors, reviewer) had to run as a synchronous, unnamed, foreground subagent, one at a time. NOTE the asymmetry: the top-level teammate is blocked, but its subagents CAN spawn their own sub-subagents (the drill arms ran as genuine fresh sonnet sub-subagents). This tension with the "prefer background subagent dispatches" guidance is real in the team harness.
- **Cost:** No parallelism across the three crew dispatches (serialized ~3 opus runs); the standard "dispatch in background and poll" pattern is unavailable, so poll-actively guidance does not apply to the top-level dispatch here.
- **Proposal:** Add a note to `references/crew-dispatch.md` (or the delegated-commander skill): "Inside a team harness a delegated Commander dispatches crew SYNCHRONOUSLY and unnamed (no background, no named teammates); nested spawning by the crew itself is still available, which is what lets a fresh auditor run genuine two-arm sub-dispatches."
- **Grounding:** this run's dispatch attempts — two Agent tool errors ("Teammates cannot spawn other teammates — the team roster is flat"; "In-process teammates cannot spawn background agents. Use run_in_background=false").
- **Template vintage:** n/a
- **Confidence:** high
