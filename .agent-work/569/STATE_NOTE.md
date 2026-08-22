# Crash-resume state note — 569

- **step:** execute · wave 2 dispatching (three lanes, all sonnet, all via run_crew.py --role commander)
- **slug:** work-id `569`, Admiral spine `.agent-work/569/spine.json` (session `constellation/569`, lease active), driven from /home/tommy/projects/constellation-skills on `main` @ 9d5aac6d. Lanes: `w2-basis` (/home/tommy/projects/569-w2-basis, branch epic-569/w2-basis), `w2-ledger` (/home/tommy/projects/569-w2-ledger), `w2-reindex` (/home/tommy/projects/569-w2-reindex). All based on 9d5aac6d, main verified green there at 3622 passed / 6 skipped.
- **next command:** check for results — `ls /home/tommy/projects/569-w2-{basis,ledger,reindex}/.agent-work/w2-{basis,ledger,reindex}/RESULT.md`. Adjudicate per .agent-work/569/LATITUDE_CONTRACT.md; VERIFY EACH MERGE by test-merging into main in a scratch worktree and running the full suite BEFORE merging — a MERGEABLE PR turned main red in wave 1 and no automated signal caught it. Then STOP AND PRESENT: the contract's autonomous clearance ENDS after wave 2.
- **pid:** none — foreground Admiral. Commanders are separate `claude` processes launched by run_crew.py with a durable registry at each worktree's .agent-work/<id>/crew-runs.json; recover with `python scripts/recover_crews.py <work-id>`.
- **expected artifact:** three RESULT.md files, three merged PRs, then the wave-2 checkpoint presentation

## Wave-2 checkpoint agenda (owed to the human, do not skip)

1. **#558 review-level doctrine** — brief prepared at `.agent-work/569/558-CHECKPOINT-BRIEF.md`. Human asked to discuss before wave 3.
2. **`decision:widening-is-not-a-new-check`** — Admiral's reading that widenings ship live while new refusals ship report-only. Graded a guess; needs ratification.
3. **Blocking lints from wave 1** — shipped blocking under an Admiral pre-ruling that contradicted the contract's "surfaced" classification. Needs retroactive ratification or reversal.
4. **No automated defence against a PR that reds main** — measured in wave 1. Candidate scope.
5. **The sonnet experiment result** — what each commander named as underspecified in its order.

## Known state, do not re-diagnose

- Wave 1 lanes `w1-wiring` and `w1-verdict` are merged and terminal; their worktrees at /home/tommy/projects/569-w1-* still exist and need sweeping at closeout (collect any CONSTELLATION_FEEDBACK.md export FIRST).
- Wave 1 was dispatched in-harness via the Agent tool, which was an Admiral error; wave 2 uses run_crew.py so commanders have their own spine doors and the Stop hook resolves correctly.
- A transient `spine.json` read failure is NOT corruption — the engine writes atomically. Re-read before concluding.
- Heartbeat age is a poor liveness signal: it only advances on engine verbs, so a commander doing git work or a long plan-alternatives pass looks dead while healthy. Inspect the worktree.

_Updated: 2026-08-22T17:05:00+00:00_
