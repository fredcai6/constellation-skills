# Triage candidate: duplicated precedence prose

**Source:** reviewer's r6-fowler pass on g1, `cmdr-567-c` (epic-567-door lane C).

**Statement:** The Stop-hook-authoritative-over-advisory precedence sentence is now written out
independently in two places: `scripts/hooks/spine_rail.py`'s `_mid_flight_reason` (runtime refusal
text) and `skills/commander/references/crew-dispatch.md` (read-ahead doctrine). If
`decision:stop-hook-is-authoritative` is ever revised, both copies need manual sync; nothing enforces
they stay in agreement.

**Disposition:** recommend-and-defer. Non-blocking today — the two locations serve genuinely
different audiences/moments (one is a live refusal message, the other is doc read before hitting the
fork), and the task explicitly scoped both edits. Worth a single source of truth if a third location
ever needs the same sentence. Not filed as an issue this run (`decision:no-issue-filing`).
