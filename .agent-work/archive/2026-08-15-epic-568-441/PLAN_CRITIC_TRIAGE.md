# Cold critic triage — #441

The delegated principal accepts every blocking finding from
`COLD_PLAN_CRITIQUE.md`; each remains inside the frozen four-file scope.

- CP-01 accepted: require a deterministic spawned SessionStart-versus-claim
  mixed-writer race in addition to the multi-claim production-handler race.
- CP-02 accepted: every writer locks one stable sibling lock file that is never
  the replaced registry target, from before load through replacement/cleanup.
- CP-03 accepted: specify and test the POSIX/Windows adapter contract on Linux
  with injected contention, timeout, lock failure, and replacement failure.
- CP-04 accepted: require an old readable active binding to survive a writer
  transaction and still drive production Stop routing, discriminated from a
  foreign second identity.
- CP-05 accepted: implementer, reviewer, and Commander verification artifacts
  carry matched fields for red/green, mutation control, mixed-writer coverage,
  and the four-file blast radius. Final green tests remain command gates.

Non-blocking pressure is also adopted: symlink escape and validation/open race
coverage are explicit, and the degraded map gap remains a Commander reconcile
responsibility rather than being added to the implementation plan.
