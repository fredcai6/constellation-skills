# Mission Frame

Map is DEGRADED-UNPARSEABLE for this worktree (map/INDEX.md packet dirs absent, map/ids.jsonl
empty — logged at `.agent-work/567-e/map-orientation.json`). No map node ids exist to cite.
Anchors below are the three hash-pinned substitutes plus a direct read of the affected source
(no map packet exists for it either).

## Intent
Wire an MCP door refusal (issue #541) so it lands in the durable `episodes/` store instead of
vanishing, proven by triggering a real refusal in a fresh process and reading it back out.
Fold in the inherited lane-D1-sweep item: replace `_THE_CLI_IS_PER_CALL`'s CLI recommendation
in `scripts/mcp_spine_server.py`, since agent-facing CLI advice is out of doctrine (issue #559,
already ratified in this same file).

## Affected Capabilities
- The MCP door's own rejection path (`scripts/mcp_spine_server.py`: `_tool_error`,
  `_log_rejection`, `_rejectionlog`) — currently writes a local JSONL sidecar
  (`mcp_rejections.jsonl`), never `episodes/`.
- The episode store's only write path (`scripts/apply_episode_delta.py --store-root episodes`)
  and its retrieval (`scripts/query_episodes.py`, `scripts/verify_episode_captured.py`).
- The two `_spine_bind` containment refusal sites that end in `_THE_CLI_IS_PER_CALL`
  (`scripts/mcp_spine_server.py:1396,1437`).

## Structural Anchors
- `docs/EPISODE_STORE.md` — record grammar, write path, retirement layout (substitute, hash-pinned)
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — project overlay, "Retired Learning Playbook" section
  (substitute, hash-pinned)
- `docs/agents/GLOSSARY.md` — episode/episode-store/harvest terms (substitute, hash-pinned)
- `scripts/mcp_spine_server.py` (2268 lines, read directly — no map packet exists) —
  `_tool_error` (:797), `_log_rejection` (:761), `_rejectionlog` (:297), `_telemetry_path`
  (:253), `_THE_CLI_IS_PER_CALL` (:1247), `_spine_bind` refusal sites (:1396, :1437),
  `run_engine` (:695, engine-native refusal path, currently uncaptured as a rejection)
- `scripts/apply_episode_delta.py` — validated delta writer, `create` op's five-assertion
  requirement (read via --help)

## Governing Constraints / Assumptions
No map anchor ids exist to cite (DEGRADED-UNPARSEABLE, repo-wide this wave) — these are
prose constraints read directly from the substitute docs, not map `constraint:` nodes:
- `episodes/` has exactly one write path, `scripts/apply_episode_delta.py --store-root
  episodes`; never hand-edited (`docs/EPISODE_STORE.md` §1, §10).
- An episode is a record of what happened, never read back as an instruction
  (`docs/agents/ORCHESTRATOR_CONTEXT.md`, "The Retired Learning Playbook").
- `docs/EPISODE_STORE.md` §10, load-bearing for this run's central design choice: "nothing
  auto-*creates* an episode, and nothing should — an auto-created one could only carry
  fabricated assertions."
- No inode containment on `spine_bind`'s hardlink hole — standing, out of scope (launch
  order pre-ruling).

## Decision Anchors & Decision Pressure
No map `decision:` anchors exist to cite under DEGRADED orientation; these are this run's
own decision candidates, not resolved map nodes:
- **Capture-is-literal-derivation-only** (mine, resolving the §10 conflict above): every
  field a mechanical refusal-capture writes into an episode's agent-supplied bin must be a
  literal derivation from data the refusal itself produced (verbatim message, actual
  tool/args, the refusal's own named escape hatch) — never invented narrative.
  @grade: guess · leans plan,g1-implement · settle: build it and show the five fields
  against a real captured refusal; a field that reads as invented rather than quoted fails.
- **Decision pressure** — which refusals get captured (door-own only, or engine-native too;
  every refusal or a filtered subset) — count what a real run emits before choosing
  (the launch order's capture-filter-is-yours ruling).
- **Decision pressure** — how an unbound-door refusal (no work-id) is handled: skip capture
  and say why, vs. a sentinel run id.

## Claims / Evidence Surfaces
No map `claim:` anchors exist under DEGRADED orientation; these are this run's own
acceptance claims, each checked by command, not by reading the capture code:
- A refusal triggered through the door in a fresh process is readable back out of
  `episodes/` via `query_episodes.py` — re-run the trigger and the query.
- With the capture removed (or the mechanism disabled), the same refusal leaves no trace
  in `episodes/` — re-run the same way on the unmodified/reverted path.
- The two `_spine_bind` sites no longer end in a CLI recommendation — grep for the literal
  string post-change.

## Map Confidence / Staleness / Disputes
- Map is DEGRADED-UNPARSEABLE for the whole repo this wave (not just this run's area) —
  `map/INDEX.md` is Admiral-owned and known-stale under concurrent lanes (launch order,
  the map-index-is-admiral-owned ruling). Altered plan: read source directly for the one file
  in scope rather than trusting any packet; no scout/verify gate planned since the source read
  already happened at context/understand and is small (one file, ~2270 lines, already read
  in full at the relevant sections).

## Out of Scope
- Closing the hardlink hole (`spine_bind`, forbidden per launch order).
- #305's general "automated capture of the mechanical half" for all episodes — this run
  covers door refusals only.
- #308's rhyme-detection/consolidation.
- Any file another lane owns this wave (see launch order's File Ownership table).
- Filing issues; promoting an observation into `docs/agents/*`; editing
  `docs/superpowers/plans|specs/**`; regenerating `map/INDEX.md`.
