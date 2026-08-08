# Crash-resume state note — b433-render-directives

Handed off at a seam. The Commander driving this spine tripped the context governor's HARD band at
`g2-integrate` (16% of a 1M window, hard cap 15%), filed the refresh-request the engine demands
(`e-g2-integrate-3`, seam `g2-integrate`, `why_ref` `w-6`), and stopped. That is the sanctioned exit,
not a failure. This is the **second** such handoff on this job: the predecessor stopped the same way
at the `plan` seam.

**Reuse this spine, this lease and this `why_trail`. Never copy or recreate them.** Cold-start from
the engine's own output — the DIGEST line plus the ACTIVE gate and its imperative is the whole brief.

- **step:** execute · gate `g2-integrate`, all evidence attached, `advance` blocked by the HARD band
  and released by the pending refresh-request. `g1` and `g2` are done and reviewed; `g3-schema`
  (a two-place doc correction plus the broad-suite run) is the only execute gate left, then the spine
  steps reconcile → triage → review → feedback → archive.
- **slug:** b433-render-directives · branch `epic-418/b-433-render-directives` · worktree
  `C:/Programs/constellation-skills-wt/r418-433`
- **next command:** `cd C:/Programs/constellation-skills-wt/r418-433 && python scripts/checklist_engine.py --file .agent-work/b433-render-directives/execute.json advance g2-integrate --why "<your understanding>"`
- **pid:** none — foreground
- **expected artifact:** `.agent-work/b433-render-directives/RESULT.md`, then a PR against `main`
  opened with `gh pr create -F <file>`

## What the next agent must know before touching `g3-schema`

The gate's own postconditions are pre-authored and pinned; do not invent proxies for them. But the
**g1 reviewer found one thing the pinned chain does not cover**: `docs/CHECKLIST_SCHEMA.md:138` also
carries a separate sentence asserting `directives` "is not rendered", which contains neither the
phrase `known gap` that `c1`'s negation looks for nor the type string `c2` looks for. Correct that
sentence too, and consider whether `c1` should be amended through the engine to catch it — a
postcondition that passes while a false sentence survives is the shape this whole issue is about.

Everything the run measured, decided, produced and harvested is written up in
`.agent-work/epic-418-redux/notes-433.md` under "Execution log — successor Commander", including the
subsumption dispositions (closed 0 of 10, each declined in writing) and seven triage candidates.

_Updated: 2026-08-08T00:00:00Z_
