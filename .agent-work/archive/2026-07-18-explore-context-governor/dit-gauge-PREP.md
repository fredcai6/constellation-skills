# Prepped panel — Gauge-file seam (design-it-twice, launch after why-capture converges)

Interface under design: the **gauge** — a harness-specific writer emits context-fill to a well-known local file every tool call; the engine reads it at each gate; the file is the portability seam; adapters are swappable per harness (Claude Code PostToolUse hook, Codex, pi); missing/stale file → no reading → engine gives no advice, never forces (fail-safe).

Shared read list for all three designers:
- X2 result (`excursion-x2-result.md`) — the `strategic-compact` technique: a hook parses `transcript_path` and sums token fields (no native API).
- X3 result (`excursion-x3-result.md`) — per-harness hook/extension capabilities (Claude Code PostToolUse; pi extension API; Codex).
- `DESIGN_SPEC.md` — the "Gauge" module section.
- Claude Code hook docs if reachable.

Three candidates, distinct constraints:

- **Gauge-A · minimal-interface** — the file is the smallest viable payload (e.g. a single fraction, or fraction+window). Simplest write, simplest read, simplest staleness rule. Honest cost: does too-thin a payload lose signal the trip policy needs?
- **Gauge-B · ports-and-adapters** — a formal `GaugeReader` port the engine depends on, the file as one adapter, an explicit "absent/no-op" adapter for harnesses without hooks. This is the natural framing (2+ real adapters = a real seam). Honest cost: over-abstraction if only Claude Code ever ships.
- **Gauge-C · max-flexibility / extensible-signal** — a richer, versioned, extensible record (fraction, window, model, timestamp, source, confidence) so new harnesses/signals fit without breaking the read contract. Honest cost: versioning/extensibility complexity vs YAGNI.

Compared on: depth, locality, seam placement, testability. Each writes to `dit-gauge-{A-minimal,B-ports,C-flex}.md`, returns a 4-5 line summary. Design only, no implementation. Model: sonnet, background, watchdog on the set.

(Refresh/handoff panel — 2 candidates — prepped verbally in the spec plan; brief it after the gauge panel converges.)
