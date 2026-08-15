# Why there is no spine.json in this archive

The epic's spine is deliberately **not** copied here.

At the moment this archive was written, `closeout` had not yet advanced and the engine lease was
still held — the run's own ordering puts log archival before the closing advance and before release.
Copying the spine at that instant would have committed a **nonterminal** spine into tracked history,
which is the exact shape epic 568's own lifecycle ruling exists to prevent: archive refuses a
resolvable nonterminal child, and the standing handoff already records 24 archived spines in a bad
state.

The same reasoning was applied earlier in this closeout to the abandoned
`epic-568-codex-tier-routing` work area, which was dispositioned in the log rather than swept onto
`main`. Applying it to that case and not to the Admiral's own spine would have been the more
comfortable inconsistency.

The live spine remains at `.agent-work/epic-568/spine.json`, where it reaches `closeout: complete`
with its lease released as the run's final act. The full narrative record — every ruling, incident,
merge, wave launch, transition and owned error — is in `ADMIRAL_LOG.md` beside this note.
