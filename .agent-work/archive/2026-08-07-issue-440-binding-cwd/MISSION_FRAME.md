# Mission Frame — issue #440, worktree-dispatched binding resolution

## Intent

Make a HARD governor trip fire from a per-agent gauge reading produced by an agent **dispatched into
a worktree**, by fixing how the spine-rail binding store resolves a relative `--file`. Small,
local, one-function change in one hook module; the map adds little, so this frame is deliberately
short. Orientation came back **DEGRADED-NO-MAP** (this repo has no `docs/architecture/`), so every
anchor below is cited against the substitutes the receipt hash-pinned, not against map ids.

**Note on grammar:** `verify-frame` refuses *any* map-anchor id under `DEGRADED-NO-MAP`, including
the `@grade`-welded rulings the Commander template asks for. The rulings below are therefore written
in plain prose with their grades welded, and the naming clash is filed as a triage candidate.

## Affected Capabilities

- Session→spine binding maintenance (`spine_rail.handle_post_tool_use`) — records which spine an
  acting agent claimed. This run changes only **where a relative `--file` resolves to**.
- Gauge write placement (`gauge_writer_hook`) — reads the binding to decide where `gauge.json`
  goes. Untouched; it inherits the fix.
- Gate-boundary trip (`checklist_engine._trip_hard_gate`) — reads `gauge.json` beside the spine.
  Untouched; it is the observer that proves the fix.

## Structural Anchors

- `docs/GAUGE_WRITER_HOOK.md` — hash-pinned substitute for the map. Its
  "Known limits of the binding store itself (#419)" section states this exact defect and is the
  structural record this run must reconcile.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — hash-pinned substitute. "Workflow mechanisms and
  verifiers" is a *strengthened durable system*: targeted automated tests **plus** the relevant
  broader suite.
- `scripts/hooks/spine_rail.py` — `_resolve_abs` (l.390) and its one caller in
  `handle_post_tool_use` (l.438). File level; the whole change lands here.
- `scripts/hooks/gauge_writer_hook.py` — reads the binding through spine_rail; not edited.
- `tests/test_spine_rail.py` — where the targeted tests land.

## Governing Constraints / Assumptions

- **#269 is upstream and not this run's to change.** `CLAUDE_PROJECT_DIR` resolves once at session
  launch. Work with it.
- **The binding key shape is a load-bearing interface** (`session_id` / `session_id#agent_id`).
  Changing it needs the Admiral. This run does not touch it.
- **Hook code is not fenced by worktree isolation** — validating from inside this worktree runs the
  *main checkout's* hook code and proves nothing. Acceptance must run in a fresh process against a
  hook wired by absolute path.
- **Skip-on-uncertainty is the store's existing posture** — silence beats a confident wrong record.
  A resolution that cannot be verified must bind nothing.
- Baseline to beat: **1688 passed, 2 skipped** on `cbd9aee`. Assert strictly greater.

## Rulings & Decision Pressure

- **fix-the-resolution-not-the-caller** — the fix lands in the binding store's resolution, not in
  call sites.
  `@grade: settled/measured · leans g1 · settle: DONE — read #419's six real payloads plus this run's own live binding entry; the payload carries no per-agent root, so the resolution must verify against the filesystem rather than trust cwd. The ruling survives its own settle experiment.`
- **not-fixing-269** — the harness's fixed `CLAUDE_PROJECT_DIR` is upstream and out of scope.
  `@grade: settled/human · leans g1,g2`
- **existence-verified-resolution** — a relative `--file` resolves against an ordered candidate root
  list (cd-target parsed from the command → payload `cwd` → git worktree roots → project_dir) and
  the **first candidate where the file actually exists** wins; none exists → bind nothing.
  `@grade: guess · leans g1 · settle: the two-arm live fire in g2 — treatment must trip HARD where control does not`
- **existing-bindings** — the live store's 60 broken entries are data, not code.
  `@grade: guess · leans g3 · settle: check whether a stale binding causes a WRONG reading or merely a missing one`
- Decision pressure: whether a resolution that finds **no** existing candidate should fall back to
  today's cwd-join (write something) or bind nothing (write nothing). Surfaced as a candidate; the
  frame's read is bind-nothing, on skip-on-uncertainty.

## Evidence Surfaces

- After the fix, a worktree-dispatched agent's binding entry names
  `<worktree>/.agent-work/<work_id>/spine.json` — checked by unit tests over real payload shapes
  **and** by the g2 live run's binding-store dump.
- The engine refuses that agent's `advance` with a HARD trip — checked by the g2 treatment arm's
  captured output and exit code.
- The byte-identical script on the base-commit hook advances normally and leaves a phantom
  `.agent-work/` in the sandbox main — the g2 control arm.
- Full suite strictly greater than 1688 passed, 2 skipped.

## Map Confidence / Staleness / Disputes

- **No map exists at all** (DEGRADED-NO-MAP, receipt `map-orientation.json`). The plan trusts no
  map: every structural statement above was read from source or from a hash-pinned doc this run
  opened. Escalated to the Admiral in `RETURN.md`.
- `docs/GAUGE_WRITER_HOOK.md` is **current** on this point — it already names the defect — so it is
  a reconcile target, not a stale input.

## Out of Scope

- The identity mechanism (#419) — settled.
- #269 itself.
- Reaping abandoned binding keys; the missing lock around load-modify-save; validating `--file`
  against shell mangling. All named in `docs/GAUGE_WRITER_HOOK.md` as known limits; none is this
  issue's obligation. Comment-and-float if touched.
- The gauge writer's read side and the engine's trip bands.
