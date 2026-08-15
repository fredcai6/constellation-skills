# Mission Frame

## Intent

Ship three independent false-signal fixes named by LAUNCH_ORDER `launcher-hygiene`, each with red-before/green-after
evidence, without letting any one grow a second subsystem: (1) isolate `test_mcp_identity.py`'s DC3 environ
assertion from the calling shell's own ambient `SPINE_*` vars; (2) make `run_crew.py`'s `spine_terminal` resolve
through the `archive` gate's relocation instead of reading a stale absence as `failed`; (3a) document the
harness-auto-backgrounding hazard and the poll-until idiom in `crew-dispatch.md`; (3b, optional) a Stop-hook
mechanical check, shippable only with a falsifiable red+control pair. No packet map (`docs/architecture`) exists
in this repo — substituted the code_map-derived `map/INDEX.md` (regenerated) per the context step's DEGRADED
discharge.

## Affected Capabilities

- **crew launch verdict** (`scripts/run_crew.py`) — judges a dispatched crew `completed`/`blocked`/`failed` from
  exit code + result-artifact freshness + bound-spine terminality. This run touches only the spine-terminality leg.
- **DC3 identity-seam test** (`tests/test_mcp_identity.py`) — proves launching a door subprocess never mutates the
  launching process's own `os.environ`. This run touches only the test's isolation from ambient env, not the
  assertion's target behavior.
- **Commander crew-dispatch doctrine** (`skills/commander/references/crew-dispatch.md`) — documents how a gate
  dispatches a crew through `run_crew.py`. This run adds the missing auto-backgrounding hazard + idiom, changes
  no dispatch mechanics.
- **spine rail Stop hook** (`scripts/hooks/spine_rail.py::decide_stop`) — refuses a turn-end while the bound spine
  is mid-flight. Read only, 3b decision pending on feasibility below.

## Structural Anchors

- `scripts.run_crew:spine_terminal` — reads the spine file at `spine` (relative-to-`root` or absolute); the exact
  function Task 2 fixes. (`map/scripts.run_crew/INDEX.md`)
- `scripts.run_crew:finalize_from_exit_code` — the sole caller of `spine_terminal` in both the `result is not None`
  rescue branch and the `result is None` spine-only branch; unchanged by this run except transitively.
- `scripts.hooks.spine_rail:decide_stop`, `scripts.hooks.spine_rail:handle_post_tool_use` — Task 3b's target and
  its precondition. (`map/scripts.hooks.spine_rail/INDEX.md`)
- `tests.test_mcp_identity:DC3InheritanceMechanismTests` (class), its `setUp`/`tearDown`, and the one test method
  named by LAUNCH_ORDER — Task 1's exact target.

## Governing Constraints / Assumptions

- `close_work` (`scripts/spine_lifecycle.py`) refuses unless the lease is already released and every gate is
  already terminal — confirmed by reading it directly. The relocation therefore always happens AFTER genuine
  terminality, never before; a fix that resolves `spine_terminal` through the archive path cannot become a rubber
  stamp for a genuinely incomplete run, because an incomplete run's spine is never moved there at all.
- `archive_name_for(work_id, today)` = `f"{today}-{work_id.replace('/','-')}"` — the naming convention Task 2's
  relocation lookup must key off exactly (work_id derived from the spine's own parent-dir name relative to
  `.agent-work`, never trusted from an unrelated field), matched precisely (never a substring/prefix match) so an
  archived `w1` can never be mistaken for `w10-x`.
- Fail-open hooks (Pre-Ruling 4): any 3b hook change must never crash or hang a turn; `spine_rail.py`'s existing
  `main` already wraps every handler and returns `{}` on any exception.

## Decision Anchors & Decision Pressure

This repo carries no `docs/architecture` packet map (no `decision:`/`claim:`-node vocabulary exists to anchor
against — see Map Confidence below), so this section is prose, not typed anchors:

- Recorded decision — no-crew-dispatch-this-run: LAUNCH_ORDER's "Do not park — this applies to you... Do not
  dispatch a crew. Everything here is yours, in this turn" overrides the commander skill's normal crew-gate
  default; every gate below is authored as a reasoning gate, no `gN-implement`/`gN-review`. Settled by the
  Admiral's own launch order; leans on every gate.
- Recorded decision — task2 fix shape: resolve `spine_terminal`'s miss through the archive relocation by deriving
  work_id from the spine path and globbing `.agent-work/archive/*-<work_id>/<spine-basename>`, matched only when
  the file actually exists there; do not touch `spine_blocked_id` (archiving requires no blocked gate, so it needs
  no relocation-awareness) and do not touch `checklist_engine.py` (not mine, and `archive` relocating is correct).
  Settled by reading `finalize_from_exit_code`/`close_work` directly (done, see Structural Anchors).
- Decision pressure — Task 3b feasibility: `handle_post_tool_use` only binds a session that claims via a Bash
  `checklist_engine.py claim` command — never via the MCP door `spine_lease` tool this very session used to claim
  its own lease — so `decide_stop`'s existing mid-flight block is already a no-op for MCP-door sessions today.
  Resolved at plan time below (a feasibility gate, not a code decision).

## Claims / Evidence Surfaces

- Task 1 red: `test_launching_the_parent_never_touches_the_calling_processs_own_environ` fails inside this
  session's own bound shell today. Checked: ran it directly, captured the `AssertionError: 'SPINE_FILE'
  unexpectedly found in environ(...)`.
- Task 2 real composition: a genuinely terminal spine, moved by a REAL `close_work` call (not a mock), must read
  terminal again at its original recorded path once resolved through the relocation. Checked: new test driving
  `spine_lifecycle.close_work` + `run_crew.spine_terminal` together.
- Task 2 no-rubber-stamp: a non-terminal spine that was never archived must still read `failed`. Checked:
  companion test asserting `spine_terminal` stays `False` with no archive dir present.
- Suite baseline: full clean-env suite from inside this worktree reads 3028 passed / 6 skipped per LAUNCH_ORDER's
  own stated baseline; re-measured before touching anything and again after.

## Map Confidence / Staleness / Disputes

- No `docs/architecture` packet map exists in this repo (DEGRADED-UNPARSEABLE at context, discharged with
  `map/INDEX.md`, `map/scripts.run_crew/INDEX.md` and `map/scripts.hooks.spine_rail/INDEX.md` as the hash-pinned
  substitutes — see the context step's receipt). The code_map-derived map is regenerated fresh this run
  (`python -m scripts.code_map build --root .`), so confidence in the anchors above is current-as-of-this-run,
  not stale.
- `tests/test_mcp_identity.py` is not itself broken out as a distinct map entity (module-level test file); read
  directly by path/line per LAUNCH_ORDER's own citation, not through the map.

## Out of Scope

- `scripts/checklist_engine.py` — not mine; `archive` relocating the work area is correct behavior, never touched.
- `.mcp.json`, `docs/CHECKLIST_SCHEMA.md`, `skills/admiral/templates/LAUNCH_ORDER.template.md`, `.worktrees/tc6-doctrine/` — fenced to a sibling lane.
- Fixing `handle_post_tool_use`'s MCP-door binding blindness (the decision-pressure item above) — a second
  subsystem by the Budget rule; floated as a triage candidate, not fixed this run.
- `spine_blocked_id` — untouched; archiving requires no blocked gate, so it carries no relocation exposure.
