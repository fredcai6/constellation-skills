# Mission frame — cleanup-b-context-identity (#600, #500)

## Intent

Make a context reading belong to an **agent** instead of to a **folder**, so an
agent is never governed by a number it did not produce.

Scope declared per the launch order's Budget section: **the measurement plus #600
ship this wave; #500 hands back as a settled design, not code.**

## Map confidence, staleness, disputes

`map_orient.py orient` returned **DEGRADED-UNPARSEABLE**, `anchor_count: 0`:
`map/ids.jsonl` is empty and every `map/<module>/INDEX.md` target linked from
`map/INDEX.md` is absent. The orientation receipt at
`.agent-work/cleanup-b-context-identity/map-orientation.json` discharges this with
five hash-pinned substitutes. Every anchor below is one of those substitutes.
There is no packet map to be stale against; the risk is the opposite — no map at
all — so this frame is built from prose and from measured artifacts.

## Structural anchors (the hash-pinned substitutes)

- `docs/GAUGE_WRITER_HOOK.md` — the writer's wiring, the binding-store shape, the
  enumerated skip-on-uncertainty set, and the two named residuals. The charter-lite
  carrier for the write side.
- `map/INDEX.md` — names the three modules in scope: `scripts.gauge_reader`,
  `scripts.hooks.gauge_writer_hook`, `scripts.checklist_engine`.
- `.agent-work/cleanup-b-context-identity/LAUNCH_ORDER.md` — the frozen principal:
  mission, pre-rulings, latitude, file ownership, fences.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — subsystem rigor: workflow mechanisms are
  a *strengthened durable system*, so targeted automated tests **plus** the
  relevant broader suite.
- `docs/agents/GLOSSARY.md` — `gauge`, `trip`, `lease` carry fixed meanings; this
  frame and every artifact use them and add no synonyms.

## Affected capabilities

The Context Governor's ownership decision: which reading, if any, an engine gate
judges an agent against. Write side (`gauge_writer_hook.py`), read side
(`gauge_reader.py`), policy side (`checklist_engine.py`'s trip block).

## The measured claim this frame is built on

Candidate 2 is **confirmed**, by the real `handle_post_tool_use` in a fresh
process (`measurement/probe_cross_key.py`, output in `probe_cross_key.out`):

- `resolve_gauge_path` enumerates candidates for **one** binding key; the
  ambiguity guard is `len(gauge_paths) > 1`, i.e. **within-key**.
- Two *distinct* keys bound to two spine files in one `.agent-work/<work-id>/`
  each resolve to exactly one candidate, each take the clean single-candidate
  branch, and each write. Measured: an orchestrator's `0.9` overwrote a dispatched
  agent's `0.02` at the same path. No `gauge-skip.json` was written — nothing
  even noticed.
- The overwrite is **fresh**, so `observed_at > claimed_at` and
  `_reading_predates_claim` is False: #477/#601's timestamp guard is
  **structurally blind** to it. It can only catch a reading *older* than the
  claim, which is candidate 1's shape.

## Governing constraints and assumptions

- Isolation is git-only. `gauge_writer_hook.py` is hook code and cannot be
  validated from inside the session that contains it; validation runs in a fresh
  process, never a fixture that hand-injects `CLAUDE_PROJECT_DIR`.
- Measured departure from the launch order's assumption: in this session
  `CLAUDE_PROJECT_DIR` is **unset**, so the hook resolved the project dir from cwd
  and bound `path_source: payload_cwd` into the worktree. The #269 hazard did not
  bite as described here.
- Clear `__pycache__` before every measurement (#597).
- Local Linux is the only real signal; CI is one `windows-latest` job, red at
  baseline.

## Decision anchors and decision pressure

Inherited from the launch order:

- `decision:identity-not-time` — ownership is decided by the binding key that
  produced the reading, not by comparing timestamps. #601's comparison is a bridge
  and need not be deleted this wave.
  @grade: settled/human · leans g1-implement
- `decision:unattributable-means-no-reading` — a reading the caller cannot be shown
  to own yields `None`, and `None` means no trip. Fail **open**.
  @grade: settled/measured · leans g1-implement
- `decision:no-new-state-file` — attribution rides in the record or the filename,
  never a fifth store.
  @grade: guess · leans g1-implement · settle: if per-agent filenames prove unworkable, float rather than adding a store
- `decision:measure-before-design` — settled by captured artifacts before any
  design freezes. **Discharged**: the probe ran and confirmed candidate 2 before
  this frame was written.
  @grade: settled/measured · leans g0-measure

Raised by this run:

- `decision:owner-in-the-filename` — attribution rides in the gauge **filename**
  (`gauge-<owner>.json`), not in an `owner` field inside a shared `gauge.json`.
  Chosen over the field because a field makes a foreign reading *detectable* while
  leaving the file itself folder-owned and clobberable — the subordinate agent then
  gets no reading at all, so the governor goes dark for exactly the crews it exists
  to govern. A per-agent filename removes the collision instead of reporting it:
  both agents stay gauged, and ownership holds by construction rather than by
  comparison. Full comparison in `PLAN_ALTERNATIVES.md`.
  @grade: guess · leans g1-implement · settle: the g1 acceptance probe — two keys, one work dir, both agents keep their own reading
- `decision:no-shared-file-fallback` — when no per-agent gauge resolves, the engine
  reads **nothing**; it does not fall back to a shared `gauge.json`. A fallback
  would reinstate the folder-owned file this issue exists to remove. This makes the
  governor **permit** where it currently refuses, never the reverse, so it stays
  inside inherited latitude.
  @grade: guess · leans g1-implement · settle: assert no trip fires from a foreign per-folder gauge.json once the reader is owner-keyed

## Claims and evidence surfaces

- `tests/test_checklist_engine.py::TripGaugeReadingOwnership` — #477's guard and
  #601's two relaunch tests. New ownership tests belong in or beside it.
- `tests/test_gauge_writer.py`, `tests/test_gauge_reader.py`,
  `tests/test_gauge_chain_writer_to_trip.py` — the end-to-end chain with real OS
  subprocesses; the natural home for the acceptance probe.
- Evidence standard, from the existing class: drive the **real** reader and a
  **real** gauge file, never a patched `_read_gauge`.

## Out of scope

- `scripts/hooks/spine_rail.py`, `scripts/run_crew.py` (lane C);
  `scripts/mcp_spine_server.py`, `.mcp.json` (lane A). Fenced.
- `checklist_engine.py`'s claim path (#601 landed on `main` this morning) — left
  alone; this design does not require touching it.
- #500's implementation. Handed back as a settled design.
- The 150K absolute cap being reachable on turn one for a design wave. The launch
  order names this as intended and not this lane's defect.

## Interaction to watch

Lane C is fixing #549 concurrently — an orchestrator's Stop hook seeing a
subordinate's spine through `session_view`'s per-agent merge. That is the same
neighbourhood as the confirmed candidate 2. **If C lands first, re-measure.**
