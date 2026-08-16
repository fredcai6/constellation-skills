# Mission Frame — lane A, `cleanup/a-door` (#604, #603, #605)

Base `a69bbac4`. Built from the `context` step's map input, which came back
**DEGRADED-UNPARSEABLE** — see "Map confidence" below. Anchors are cited against the
hash-pinned substitutes in `.agent-work/cleanup-a-door/map-orientation.json`, not against
map ids, because this repo currently has none.

## Intent

Make the MCP door usable by the session that needs it. Today the door binds one spine at
import from `.mcp.json`'s demo default and cannot be rebound, so an orchestrator cannot
point it at a spine it is about to create — which is why every epic since #424 has driven
its own spine through the CLI, the opposite of what #559 ruled.

Exit criterion, from the order: a session started with **no** `SPINE_FILE` calls
`spine_open`, gets bound, and drives a real spine end to end without touching the CLI.

## Affected capabilities

- **Door identity acquisition** — how the process decides which spine it speaks for.
  Changes from import-time-only to import-time-or-bind-on-open. Load-bearing interface.
- **Door telemetry** — the call log and start marker. Must become non-fatal.
- **Door refusal surface** — what an unbound / missing / unreadable binding answers.
  Changes from "crash at import" or "confident demo answer" to "refusal naming the path".
- **Shipped example** — `examples/mcp-interactive-demo/` must run where it is installed.

## Structural anchors

Cited against substitute `map/INDEX.md` (hash-pinned) and read directly:

- `scripts/mcp_spine_server.py:145-147` — the three import-time env reads.
- `scripts/mcp_spine_server.py:162,167,177` — `CALLLOG`, `START_MARKER`, `REJECTIONLOG`,
  all derived from `SPINE` at import.
- `scripts/mcp_spine_server.py:188` — `_resolve_confined(bound_dir: Path = SPINE.parent)`,
  a **default argument** evaluated once at import. The subtlest rebind hazard.
- `scripts/mcp_spine_server.py:180-184` — `_log`, unguarded (#604).
- `scripts/mcp_spine_server.py:441-461` — `run_engine`; `_log(rec)` sits outside the
  `try/except`.
- `scripts/mcp_spine_server.py:236-363` — `_identity_violation`. **Fenced semantics.**
- `scripts/mcp_spine_server.py:622-736` — `_spine_open` / `_spine_close` /
  `call_lifecycle_tool`, the lifecycle door.
- `.mcp.json` — the demo default.
- `examples/mcp-interactive-demo/spine.json` — six absolute paths.

## Governing constraints and assumptions

- `_identity_violation`'s semantics are **fenced**: any change floats to the Admiral.
- `scripts/checklist_engine.py`, `scripts/hooks/**`, `scripts/run_crew.py`,
  `scripts/gauge_reader.py` are owned by lanes B and C — do not touch.
- Two AST pins constrain the rebind's location (`tests/test_mcp_lifecycle.py:137`, `:194`).
  A third pins `call_tool`'s return shapes (`tests/test_mcp_identity.py:1484`).
- The door must be validated by launching the server as a **subprocess** with the intended
  environment, never by reasoning about this session's own connection.
- Suite is the only Linux signal; CI is one red `windows-latest` job.

## Decision anchors and decision pressure

Inherited from the order, restated with grades:

- `decision:one-spine-per-process-stands` — one spine per process; `_identity_violation`
  keeps refusing any argv naming another. Bind-on-open changes *when*, never *how many*.
  `@grade: settled/human · leans g2-implement,g2-review`
- `decision:fail-closed-beats-fail-open` — unbound/missing/unreadable yields a refusal
  naming the path. Never a demo answer, never a crash, never silence.
  `@grade: settled/measured · leans g2-implement`
- `decision:telemetry-never-fatal` — the call log is diagnostic; a failed write drops the
  record and continues. `@grade: settled/measured · leans g1-implement`
- `decision:bind-on-open-over-new-verb` — bind inside `spine_open` rather than add
  `spine_bind`; overridable if the identity checks cannot be expressed without weakening.
  `@grade: guess · leans g2-implement · settle: attempt the spine_open binding first and report what it costs`
- `decision:demo-spine-is-generated-not-hand-fixed` — produce the demo spine from the
  example's own directory. `@grade: guess · leans g3-implement · settle: whichever is smaller once the example's build is read`

**Decision pressure this frame raises (candidates, not yet decisions):**

- **`decision:rebind-must-relocate-derived-globals`** — a rebind is only honest if
  `CALLLOG`, `START_MARKER`, `REJECTIONLOG` and `_resolve_confined`'s `bound_dir` default
  follow the new binding. Leaving any at its import-time value would silently write one
  spine's telemetry into another's directory and confine paths against the wrong tree.
  This is the measured cost the `bind-on-open` pre-ruling asked me to report.
- **`decision:add-a-module-wide-assignment-pin`** — *revised by the cold critic (finding 7),
  and the revision is the point.* I first read the rebind helper as passing
  `test_mcp_lifecycle.py:194`'s identifier ban on its mere letter, and concluded the pin
  must be "extended". That is wrong, and dangerously so. `:194` bans those identifiers from
  `_spine_open`'s **own source**; a module-level binder that `_spine_open` calls leaves the
  pin's letter *and its stated purpose* intact — nothing is weakened. Worse, "extend the
  pin" reads naturally as *replace a hard identifier ban with a softer intent-shaped
  statement*, which would have weakened a guard in the very motion used to argue against
  weakening guards. **Ruled:** keep `:194` and its positive control **byte-identical**, and
  **add** a strictly stronger module-wide AST pin asserting that the set of assignments to
  `SPINE` and `SESSION` is exactly {module scope, the one named binder}, with its own
  mutated positive control. That catches the real regression — a second, quieter rebind
  site — which an `_spine_open`-scoped ban cannot see.

Two further roots the critic proved, folded into g3 rather than left to the implementer:
`_primary_checkout_for_lifecycle` (`:593`) does its own hard `os.environ["SPINE_FILE"]`
read on `spine_open`'s path, and `open_work` returns **three** binding values — so binding
`SPINE` alone leaves `SESSION` empty and `claim` refuses, and the exit criterion is not
reached.

## Claims and evidence surfaces

| Claim | How this run confirms it |
|---|---|
| #604 kills the server | Subprocess probe against a nonexistent spine dir: exit code + `FileNotFoundError` before the fix, clean refusal after. Both exit codes recorded. |
| #603 fails open when unbound | Probe transcript: unbound door refuses **by name**, then `spine_open` binds it, then a real verb succeeds. |
| #605 demo is unusable | Drive the regenerated demo spine from a directory that is **not** the one it was generated in. |
| Nothing else regressed | Full clean-env, cache-cleared Linux suite at published head, plus a `main` baseline re-measured at gate time. |

## Map confidence, staleness, disputes

**Low — the map is unusable, repo-wide.** `map/ids.jsonl` is tracked but empty (0 bytes)
while `map/INDEX.md` carries 27KB of generated structure, so `map_orient.py` resolves zero
anchors for any area. Discharged as DEGRADED with four hash-pinned substitutes plus an
escalation. Consequence for this plan, stated rather than silently absorbed: the `plan`
step's `verify-frame` gate (c6) **cannot pass for any frame**, so it is taken as a
**recorded waiver**, not a silent skip. Filed as triage candidate `tc1`; `map/` is not
lane A's to fix this wave.

No disputed areas. No stale packet claims — there are no packets.

## Out of scope

- Any change to `_identity_violation`'s semantics (fenced; floats to the Admiral).
- Any change to `checklist_engine.py`, `scripts/hooks/**`, `run_crew.py`,
  `gauge_reader.py` (lanes B and C).
- A tool taking a spine path per call — the order rules it out and it would undo the guard.
- `map/ids.jsonl` (tc1, deferred).
- The **door-detection change** in `install_constellation.py` and
  `COMMANDER_SPINE.template.json`. The order grants the files but never defines the change,
  and no such concept exists in the repo. **Floated to the Admiral; not invented here.**
- Publication. Commander parks at `archive`.
