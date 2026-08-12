## Current planning truth — after wave 2

**B extended is complete.** #433, #436, #460 and #464 are merged and closed; main is green at `476e044d`. Done-condition #2 is met.

### Wave 3 (current)

| Issue | What it settles |
|---|---|
| #461 | the episode-store negative control reds every run that legitimately captures an episode, between `git add` and the commit |
| #465 | reviewer `r6-fowler` ships a placeholder no engine verb can fill, and filling it in text mode rewrites every CRLF |
| #488 | the gauge writer counts bindings rather than distinct paths, blinding any Admiral that drives its own latitude survey |
| #489 | a fixture glob silently picks `matches[0]` with no signal a second match existed |

#488 and #489 are wave-2 discoveries folded in under a standing preference: a genuinely cheap fix gets done in the current wave rather than filed and deferred.

### Forecast (nonbinding)

A2 — trip semantics, cut at its turn against what B extended actually left behind. Then F (#424, the MCP front door), then C (#421, relocation against a settled verb contract). E (#423) runs on what survives.

### Open, not scheduled

- **#457** — the lease field carries no liveness information in either direction. Evidenced this wave, deliberately not fixed: both readings are uninformative, so correcting it means deciding how liveness is encoded, which ends at a load-bearing interface.
- **The governor's 17-21% trip band** — a production default, and a human call. Wave 3 gives the first Admiral-side measurement, since #488's fix restores the orchestrator's own gauge.
- **#452**, **#458** — the governor's remaining work.

### The lens this epic keeps producing

A check that cannot fail: a signal whose value is identical in the healthy and defective worlds. Four independent instances surfaced in wave 2 alone. It is not a scheduled workstream, but it is the thing #418 is fundamentally about, and it is worth asking of any guard this epic ships.
