# Mission Frame

Shrunk per template guidance ("skip or shrink this frame for a trivial local/mechanical change where
the map adds nothing"). This repo's generated packet map does not exist (context step: `README.md` and
`map/INDEX.md` are the DEGRADED substitutes, hash-pinned in `.agent-work/stop-hook-door-binding/map-orientation.json`)
and the per-module map pages `map/INDEX.md` links to (e.g. `scripts.hooks.spine_rail/INDEX.md`) do not
exist on disk, so there is no packet-level structure to frame against beyond the one-line summaries
`map/INDEX.md` itself carries. This run is bounded, single-file-family, and the design is already fixed
by `LAUNCH_ORDER.md`'s Non-negotiables and Evidence-bar sections (fail-open, no new subprocess, narrow
matcher, Bash path byte-for-byte unchanged) — no plan-alternatives panel or cold critic is run; that skip
is the named untaken road (see `understand`'s attached user-decision).

## Intent

Teach `scripts/hooks/spine_rail.py`'s PostToolUse handler to record a session->spine binding when the
engine is claimed/released through the MCP spine door (`spine_lease` action=claim/release), not only
through a Bash `checklist_engine.py claim`/`release` invocation — so the existing, unchanged `decide_stop`
Stop-hook refusal (`_mid_flight_reason`) can see and refuse a door-driven mid-flight turn-end, which it
currently cannot (`if not sid_bindings: return {}`). Register a narrow (not `"*"`) PostToolUse matcher for
the door tool(s) in `.claude/settings.json` so the handler is even invoked for a door call.

## Affected Capabilities

- The spine rail's PostToolUse binding-store writer (`handle_post_tool_use`,
  `scripts/hooks/spine_rail.py`) — currently reads only `tool_input.command` (a Bash command string);
  gains a second, additive code path reading `tool_name` + `tool_input` fields for the MCP door shape.
- The spine rail's Stop-hook mid-flight refusal (`decide_stop`, `_mid_flight_reason`) — untouched; it
  already correctly refuses whenever a binding exists, regardless of how that binding was recorded.
- `.claude/settings.json`'s `PostToolUse` hook registration — gains one additional narrow-matcher entry
  invoking the same `spine_rail.py PostToolUse` handler for the door claim/release tool call(s).

## Examples / Events

- The failure this closes: a Commander whose spine is claimed entirely via `mcp__spine__spine_lease` /
  `spine_start` / `spine_advance` ends its turn mid-gate believing a backgrounded command will resume it;
  nothing resumes it; `decide_stop` allows the exit because no binding was ever recorded for that session.
  Documented in `.agent-work/triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md`
  and independently reproduced in the archived
  `.agent-work/archive/2026-08-15-launcher-hygiene/triage-candidates/stop-hook-binding-gap-for-mcp-door-sessions.md`.
- The control that already works: `launcher-hygiene` attempt 2 claimed via Bash `checklist_engine.py
  claim`, was refused mid-flight, resumed, and finished — proving `_mid_flight_reason`/`decide_stop`
  need no change, only a second binding source.

## Structural Anchors

No packet-level map anchors exist for this area (see header). Source-level orientation only (confirmed
by direct read, not by a map claim): `scripts/hooks/spine_rail.py` — `handle_post_tool_use` (binding
writer, ~line 1066), `decide_stop`/`_mid_flight_reason` (Stop refusal, ~line 1197), `_is_valid_claim_target`
(claim-target validator, reused unchanged for the door path). `.claude/settings.json` — `PostToolUse` block.
`tests/test_spine_rail.py` — existing Bash-path binding tests, whose behavior must not move.

## Governing Constraints / Assumptions

- Fail-open: a malformed or unrecognized door payload records no binding and raises nothing (LAUNCH_ORDER
  Non-negotiables; existing module-level contract, `spine_rail.py:9-19`).
- No new subprocess on the PostToolUse path (LAUNCH_ORDER Non-negotiables; existing comment,
  `spine_rail.py:809`).
- `_mid_flight_reason`/`decide_stop` need no change — if a plan edits them, the diagnosis was wrong
  (LAUNCH_ORDER, "The change" section).
- The Bash `checklist_engine.py claim`/`release` path must be entirely unchanged in behavior
  (LAUNCH_ORDER, "The change" section) — proven by the existing `tests/test_spine_rail.py` suite staying
  green, unmodified in its Bash-path assertions.
- File ownership fence: `scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`, the `PostToolUse` block
  of `.claude/settings.json` only. Not `scripts/checklist_engine.py`, `scripts/run_crew.py`,
  `scripts/apply_episode_delta.py`, `scripts/verify_episode_observations.py`, `scripts/hooks/gauge_writer_hook.py`,
  `.mcp.json`, or the sibling `episode-guard-at-write` worktree (LAUNCH_ORDER, "File Ownership").

## Decision Anchors & Decision Pressure

No map decision: anchors exist for this area (DEGRADED — see below), so the decisions below are recorded
as run-local decision pressure, plain-prose (deliberately not using the map's typed `decision:` citation
syntax, which `verify-frame` refuses to resolve against a DEGRADED orientation — see Map Confidence below).

- **Door-binding source of truth** — the door path resolves the claimed spine path from this process's
  own `SPINE_FILE`/`SPINE_SESSION` environment (the door tool takes no `--file` argument; it reads its
  own environment per the door's documented contract), reusing the existing `_is_valid_claim_target`
  containment/readability check unchanged, rather than inventing a second resolution ladder.
  Grade: settled/measured — confirmed by reading `scripts/mcp_spine_server.py` (`SPINE =
  Path(os.environ["SPINE_FILE"]).resolve()`) and `resolve_project_dir()`'s existing precedent of reading
  `CLAUDE_PROJECT_DIR` from `os.environ` inside this same hook. Leans on g1-implement.
- **Matcher scope** — register the narrow tool name(s) actually capable of a claim/release
  (`mcp__spine__spine_lease`), not the whole `mcp__spine__*` namespace and never `"*"` — LAUNCH_ORDER
  explicitly prefers a narrow matcher. This repo's own `.mcp.json` registers exactly one MCP server
  (`spine`), so no `mcp__spine-epic__` tool is reachable from this repo's own settings; the epic-tier
  sibling raised as an open question in the archived triage candidate is left unaddressed and recorded
  as a triage candidate rather than guessed at, since it is not observable from this repo.
  Grade: guess — leans on g1-implement, g2-review. Settle: if a later run finds `mcp__spine-epic__`
  reachable from this repo's own configuration, add its exact tool name to the matcher then.

## Claims / Evidence Surfaces

No map claim: anchors exist for this area (DEGRADED); the evidence surfaces below are this run's own,
plain-prose for the same reason as above.

- **RED** — a door-claimed spine with an open gate, at turn end, is refused by `decide_stop`, and
  demonstrably was not refused before this change. Checked by a unit test driving `handle_post_tool_use`
  with a synthetic door payload then `decide_stop` on the resulting binding store.
- **CONTROL** — a legitimate turn end (terminal spine + released lease; foreign spine; unreadable/malformed
  spine; honestly-blocked gate) is not refused. Checked by unit tests covering each case per
  `decide_stop`'s own enumerating comment.
- **Fail-open proof** — a door payload the handler cannot parse (missing fields, wrong types, unresolvable
  `SPINE_FILE`) leaves the turn unblocked and raises nothing. Checked by unit tests feeding malformed
  payloads through `handle_post_tool_use`.
- **Bash path unchanged** — the existing `tests/test_spine_rail.py` Bash-path binding tests pass
  unmodified. Checked by running the full suite.

## Map Confidence / Staleness / Disputes

`map/INDEX.md` is DEGRADED-UNPARSEABLE for this repo (context step; confirmed again here) — its per-module
pages are absent, so no anchor id in this area is citable against a real map inventory. This is a known,
already-escalated gap (recorded in `understand`'s attached user-decision and flagged as a triage candidate
at this run's `triage` step), not silently trusted — this frame proceeds on direct source read instead,
named as such throughout.

## Out of Scope

- `scripts/checklist_engine.py`, `scripts/run_crew.py`, `scripts/mcp_spine_server.py`,
  `scripts/apply_episode_delta.py`, `scripts/verify_episode_observations.py`,
  `scripts/hooks/gauge_writer_hook.py`, `.mcp.json` — not-mine per File Ownership.
- Any change to `_mid_flight_reason` or `decide_stop`'s refusal logic — explicitly out of scope; a plan
  needing to touch either means the diagnosis was wrong.
- The `Stop`, `SessionStart`, and `gauge_writer_hook` entries of `.claude/settings.json` — only the
  `PostToolUse` block's spine_rail registration is touched, and only additively.
- Repairing the stale/unfilled `map/INDEX.md` per-module pages — filed as a triage candidate, not fixed
  here.
