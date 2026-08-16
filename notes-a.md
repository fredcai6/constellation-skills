# Lane A working notes — `cleanup/a-door` (#604, #603, #605)

Sole writer: commander `constellation/cleanup-a-door/execute/commander/attempt-1`.
Base `a69bbac4`. Written per `constellation-how-to-talk`.

## Problem statement (understand step)

Reconciled against `LAUNCH_ORDER.md` (frozen principal) and the three filed issues, read
from GitHub 2026-08-16. The order's mechanism claims match the code exactly; nothing in
Mission was already shipped. Three defects, confirmed at file:line:

**#604 — telemetry is fatal.** `_log()` (`scripts/mcp_spine_server.py:180`) opens `CALLLOG`
with no guard, and `run_engine` calls it at `:461` *outside* its own `try/except`. `main()`
catches only `KeyError` around `call_tool` (`:1359`), so a `FileNotFoundError` from `_log`
unwinds the whole process. `START_MARKER.write_text` (`:184`) has the same exposure. The
fix shape already exists in this module: `_log_rejection` (`:472`) wraps its write, reports
to stderr, and never raises.

**#603 — the binding is fixed before the spine exists, and fails open when unset.**
`SPINE = Path(os.environ["SPINE_FILE"]).resolve()` at `:146` is import-time. Worse for
fail-closed: it is `os.environ[...]`, so an *unset* var raises `KeyError` at import and the
server dies at startup — the client sees `Connection closed`, not a refusal. `.mcp.json`
currently prevents that by supplying the demo default, which is the fail-*open* half.

**#605 — the shipped demo spine is unusable.** Six absolute paths into
`constellation-skills-wt/f-424`, a worktree deleted during the epic-418-followon closeout
(`examples/mcp-interactive-demo/spine.json`, lines 20/28/78/86/109/117).

## What bind-on-open actually costs (settles `decision:bind-on-open-over-new-verb`)

The pre-ruling asked me to attempt the `spine_open` binding first and report the cost. The
cost is **not** in the identity guard — it is in four import-time derivations of `SPINE`
that a rebind would leave pointing at the old spine:

- `CALLLOG` (`:162`), `START_MARKER` (`:167`), `REJECTIONLOG` (`:177`)
- `_resolve_confined`'s `bound_dir: Path = SPINE.parent` **default argument** (`:188`),
  evaluated once at import — the subtlest of the four.

So bind-on-open requires making these late-bound. `_identity_violation`'s semantics are
untouched: it still compares argv against *the* bound spine and still refuses any argv
naming another. Only *which* spine is bound changes — exactly what
`decision:one-spine-per-process-stands` sanctions ("changes *when* the binding is decided,
never *how many* are live at once").

Two AST pins constrain where the rebind may sit:

- `tests/test_mcp_lifecycle.py:137` pins every `return` in `call_lifecycle_tool` to
  literally `_spine_open(args)` / `_spine_close(args)`. Its positive control (`:162`) is
  literally `out = _spine_open(args)` — so a mutate-then-return in `call_lifecycle_tool`
  is the banned shape.
- `tests/test_mcp_lifecycle.py:194` bans the identifiers `SPINE`, `SESSION`, `run_engine`
  from `_spine_open`'s own source.

The rebind therefore goes in a module-level helper that `_spine_open` calls. That passes
the second pin on its letter — and passing a pin on its letter while changing what the pin
was written to assert is the failure this module's own history records. So the pin must be
**extended to state the new truth** (`_spine_open` may not *drive* the bound spine; it may
hand the new identity to one named binder), not routed around. Extending a pin to cover a
new true property is not weakening `_identity_violation`, and is inside latitude
("where the fail-closed check sits", "whether `spine_open` or a new verb carries the
binding"). If it turns out the pin cannot be extended without weakening it, the
Honest-Null Clause applies and I stop.

## Floated to the Admiral — the "door-detection change" is undefined

**Status: blocking gate 4 only. Gates 1–3 proceed.**

File Ownership grants me `scripts/install_constellation.py` and
`skills/commander/templates/COMMANDER_SPINE.template.json` "**for the door-detection change
only**, which lands last." The order never says what that change is. Measured, not assumed:

- Mission names exactly three defects (#604, #603, #605). None of them touches either file.
- #603, #604 and #605, read from GitHub today, never mention either file.
- `grep -rn "door.detect|detect.*door|door_detect|DOOR_DETECT" scripts/ skills/ docs/`
  returns **one** hit, and it is a false positive: the word "detects" inside the spine
  template's `init` imperative, about `--skill-dir` auto-detection. **There is no
  door-detection concept in this repo to change.**
- The installer does not seed the demo default either — `rewrite_mcp_config_interpreter`
  (`scripts/install_constellation.py:571`) rewrites `mcpServers[*].command` only, never
  `env`. So "drop the demo default from `.mcp.json`" is not undone by an install run, and
  gate 4 is not needed to make gates 1–3 hold.

I will not invent it. The plausible reading — teach the commander spine template to detect
an unbound door and fall back — collides directly with a must-float item: "any change that
makes an agent-facing skill teach the CLI as a default." Guessing here is exactly the
guess-past-the-edge-of-latitude the doctrine forbids.

**Query:** what is the door-detection change, and is it in scope for this lane? If it is
the fallback-teaching reading, that is a decision outside my latitude and I need it ruled.

## Corrections to the launch order (both measured, neither blocking)

1. **"Charter-lite carrier: this repo has no `docs/agents/` overlay" is false.**
   `docs/agents/ORCHESTRATOR_CONTEXT.md`, `GLOSSARY.md` and `CREW_CONTEXT.md` are all
   tracked and present. I read them at `context` rather than substituting README.
2. **Map orientation is DEGRADED repo-wide**, not just for this lane's area.
   `map/ids.jsonl` is tracked but **empty (0 bytes)** at `a69bbac4`, while `map/INDEX.md`
   carries 27KB of generated structure, so `map_orient.py` can resolve no anchor id for
   *any* area. Discharged with four hash-pinned substitutes plus an escalation; receipt at
   `.agent-work/cleanup-a-door/map-orientation.json`. `map/` is not mine this wave — filed
   as a triage candidate, not fixed. This also means the `plan` step's `verify-frame`
   anchor gate cannot be satisfied by any frame and will be taken as a recorded waiver.
