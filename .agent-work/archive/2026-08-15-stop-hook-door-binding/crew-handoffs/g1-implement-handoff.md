# Implementer Handoff

## Gate
`g1` (execute.json: `g1-implement`)

## Task
Teach `scripts/hooks/spine_rail.py`'s `handle_post_tool_use` (the PostToolUse hook handler) to record a
session->spine binding when the engine is claimed/released through the MCP spine door
(`mcp__spine__spine_lease`, `action=claim`/`action=release`), not only through a Bash `checklist_engine.py
claim`/`release` invocation. Register a narrow PostToolUse matcher for that door tool in
`.claude/settings.json` so the handler is even invoked for a door call. `decide_stop` and
`_mid_flight_reason` already correctly refuse a mid-flight turn-end whenever a binding exists — they need
no change; the gap is purely that a door-issued claim never creates one.

## Protected Intent
The Stop hook's fail-open contract: a malformed, unrecognized, or partially-parseable door payload must
never raise, hang, or wedge a turn. `spine_rail.py` is a PostToolUse hook on every agent's critical path in
this repo — a defect here is worse than the bug it fixes.

## Test Mode
TDD required. Capture a genuine RED (the door-claimed mid-flight case, refused today by neither
`handle_post_tool_use` nor `decide_stop`) before writing the fix, then GREEN. This is a security/reliability
hook; inspection alone is not enough — `tests/test_spine_rail.py` is the existing, mature test surface for
exactly this module.

## Close Criteria
- `handle_post_tool_use` recognizes a door-issued `spine_lease` claim/release (via `tool_name` ==
  `mcp__spine__spine_lease` and `tool_input.action` in `("claim", "release")`) and records/removes a
  binding entry equivalent in shape to the existing Bash-path entry (`{spine, engine_session, worktree,
  claimed_at, path_source}`).
- The door path resolves the claimed spine's absolute path from this process's own `SPINE_FILE` environment
  variable (the door tool call carries no `--file`; the door itself reads `SPINE_FILE`/`SPINE_SESSION` from
  its own environment per `scripts/mcp_spine_server.py`'s existing contract — `SPINE =
  Path(os.environ["SPINE_FILE"]).resolve()`), reusing the existing `_is_valid_claim_target` containment/
  readability validator UNCHANGED (do not write a second validator).
- `engine_session` for a door-recorded entry comes from `os.environ.get("SPINE_SESSION")` (may be empty/
  absent — record whatever is actually present, do not fabricate a value).
- A malformed/unrecognized door payload (missing `tool_input`, missing `action`, unresolvable `SPINE_FILE`,
  `SPINE_FILE` pointing outside `.agent-work/<work-id>/`, etc.) records no binding and raises nothing —
  `handle_post_tool_use` still returns `{}` unconditionally, matching its existing `except Exception: return
  {}` fail-open wrapper.
- RED: a unit test proves that, on the code as it exists BEFORE this gate's fix, a door-claimed mid-flight
  spine's turn-end is NOT refused by `decide_stop` (no binding was ever recorded). Capture this as a
  documented RED — either a test marked to show pre-fix behavior in the PR description/why-trail, or a
  git-stash-based before/after — your choice of mechanism, but the RED must be genuine (run against the
  actual pre-fix code, not asserted from reading).
- GREEN: after the fix, the equivalent door-claimed mid-flight case IS refused by `decide_stop` (same
  refusal text/shape as the existing Bash-path case — `_mid_flight_reason` is unchanged, so this should
  fall out for free once a binding exists).
- CONTROL: legitimate turn-ends claimed via the door are NOT refused — terminal spine with released lease;
  foreign worktree; unreadable/malformed spine; honestly-blocked gate (`status == "blocked"`) — mirroring
  the existing Bash-path CONTROL tests (`test_stop_no_binding_allows`, `test_stop_unreadable_spine_allows`,
  `test_stop_released_lease_allows`, `test_stop_blocked_status_honest_stop_allows`) but driven through a
  door-shaped claim.
- Fail-open proof: a unit test feeding `handle_post_tool_use` a door-shaped payload with each of several
  malformed shapes (missing `action`, non-dict `tool_input`, unresolvable/absent `SPINE_FILE`, `SPINE_FILE`
  pointing at a non-checklist file) asserts `{}` is returned and no binding is written, no exception
  escapes.
- Every existing `tests/test_spine_rail.py` Bash-path test passes UNMODIFIED — same assertions, same
  fixtures. If a Bash-path test's assertion needs to change to accommodate this gate, STOP and report; that
  would mean the Bash path moved, which this gate must not do.
- `.claude/settings.json`'s `PostToolUse` array gains exactly one additional entry: `{"matcher":
  "mcp__spine__spine_lease", "hooks": [{"type": "command", "command":
  "\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\" PostToolUse", "shell": "bash", "timeout": 10}]}` —
  same hook command/shell/timeout shape as the existing `Bash`-matcher entry. The existing `Bash`-matcher
  entry and the `gauge_writer_hook.py` `*`-matcher entry are untouched (same JSON, same order, byte-for-byte
  except for the one new array element). `Stop` and `SessionStart` blocks are untouched.

Never pin a literal file/line count you have not re-derived — verify with `git diff --stat` at close, not
from memory of this handoff.

## Allowed Scope
- `scripts/hooks/spine_rail.py` — additive changes to `handle_post_tool_use` and its helpers only. Do not
  edit `_mid_flight_reason`, `decide_stop`, `decide_session_start`, or any Stop/SessionStart-only code path.
- `tests/test_spine_rail.py` — add new tests for the door path (RED/GREEN/CONTROL/fail-open). Existing tests
  are pre-authorized to run unmodified (no change expected) — if you find yourself needing to touch one,
  stop and explain why in your result rather than editing it silently.
- The `PostToolUse` array (only) inside `.claude/settings.json`.

## Specific Exclusions
- `scripts/checklist_engine.py`, `scripts/run_crew.py`, `scripts/apply_episode_delta.py`,
  `scripts/verify_episode_observations.py`, `scripts/hooks/gauge_writer_hook.py`, `.mcp.json` — a sibling
  lane (`episode-guard-at-write`) or other tooling owns these; out of bounds regardless of how related they
  look.
- The `Stop`, `SessionStart`, and `gauge_writer_hook` entries of `.claude/settings.json`.
- No new subprocess anywhere in `scripts/hooks/spine_rail.py`'s PostToolUse path (the one existing `git
  worktree list` probe at line ~816 is unrelated to this gate and must stay exactly as it is).
- Do not widen the matcher to `mcp__spine__*` or `"*"` — exactly `mcp__spine__spine_lease`, and only that
  name (this repo's `.mcp.json` registers exactly one MCP server, `spine`; `mcp__spine-epic__spine_lease` is
  a distinct, unregistered-in-this-repo tool name and is explicitly out of scope this gate — record it as
  an out-of-scope observation, do not add it).

## Constraints
- Fail-open, always: any error anywhere in the new code path must be caught (or structurally incapable of
  raising past `handle_post_tool_use`'s existing top-level `try/except Exception: return {}`) so a hook
  error, timeout, or unparseable payload never blocks a turn.
- No new subprocess on the PostToolUse path.
- Stdlib only (matches the module's existing constraint — `json, os, re, shlex, subprocess, sys, pathlib`,
  no new imports beyond what's already there unless genuinely required, in which case name it in your
  result).
- Windows-friendliness: the existing module is careful about native paths and UTF-8; do not regress that
  (you are adding an env-var read, not new path-string parsing, so this should be a non-issue — flag it if
  it isn't).

## Map Anchors (inbound)
No packet-level map exists for this area (`map/INDEX.md` is DEGRADED-UNPARSEABLE — its per-module pages are
absent). Source-level orientation only, already read at frame time — start here:
- **Map entry point:** none (DEGRADED) — start directly at `scripts/hooks/spine_rail.py`'s
  `handle_post_tool_use` (~line 1066) and `tests/test_spine_rail.py`'s existing `test_post_claim_*` /
  `test_post_release_*` / `test_stop_*` tests (~lines 1248-1330, 740-900) as the pattern to extend.
- **Structural:** `scripts/hooks/spine_rail.py::handle_post_tool_use` (binding writer), `::_is_valid_claim_target`
  (reuse unchanged), `::decide_stop` / `::_mid_flight_reason` (untouched, but is what your fix makes
  effective). `.claude/settings.json` `PostToolUse` block. `scripts/mcp_spine_server.py` (read-only
  reference for how the door reads `SPINE_FILE`/`SPINE_SESSION` — do not edit it, it is out of scope).
- **Capability:** session->spine binding store — gains a second, additive recording source (door claims),
  alongside the existing Bash-command source.
- **Decision anchors:**
  - Door-binding source of truth: resolve the claimed spine path from this process's own
    `SPINE_FILE`/`SPINE_SESSION` environment, reusing `_is_valid_claim_target` unchanged.
    `@grade: settled/measured · leans g1-implement`
  - Matcher scope: `mcp__spine__spine_lease` only, not the whole namespace, not `mcp__spine-epic__`.
    `@grade: guess · leans g1-implement,g2-review · settle: if a later run finds mcp__spine-epic__ reachable
    from this repo's own configuration, add its tool name to the matcher then`
- **Evidence expectations:** RED (door-claimed mid-flight refused, wasn't before), CONTROL (terminal/
  foreign/unreadable/honest-blocked door-claimed spines not refused), fail-open proof (malformed door
  payload -> no binding, no raise), Bash-path-unchanged (existing tests pass unmodified).
- **Map confidence flags:** `map/INDEX.md` DEGRADED-UNPARSEABLE for this area — proceed on direct source
  read (already done at frame/plan time); this is a recorded triage candidate, not something for you to
  fix.

## Deliverable Path Check
- **Committed** — `scripts/hooks/spine_rail.py`; verified via `git check-ignore -v scripts/hooks/spine_rail.py`
  exiting 1 (not ignored).
- **Committed** — `tests/test_spine_rail.py`; verified via `git check-ignore -v tests/test_spine_rail.py`
  exiting 1 (not ignored).
- **Committed** — `.claude/settings.json`; verified via `git check-ignore -v .claude/settings.json` exiting
  1 (not ignored).

## Required Evidence
- `python -m pytest -q tests/test_spine_rail.py` — full pass, paste the summary line (e.g. `NNN passed`).
- The exact new test names added, and a one-line statement of what each proves (RED/GREEN/CONTROL/fail-open
  — map each new test to which of the four evidence categories it satisfies; a test may satisfy more than
  one).
- `git diff --stat` for the three touched files.
- The exact `.claude/settings.json` diff (should be a single-entry addition to the `PostToolUse` array;
  paste it).

Load-bearing (prove rigorously): the RED capture is genuine (ran against pre-fix code), the CONTROL tests
cover all four legitimate-turn-end shapes, the fail-open tests cover at least three distinct malformed-
payload shapes. Confirmatory (spot-check suffices): exact wording of any new test docstring/comment.

## Wiring Grep
```bash
grep -rn "mcp__spine__spine_lease" --include=*.py --include=*.json . | grep -v test_spine_rail.py
```
State the count of non-test call sites found (expected: 1, in `.claude/settings.json`'s new `PostToolUse`
matcher string — a matcher string is not a "call site" in the usual sense, but it is the wiring that makes
the new code path reachable at all; state plainly that this is the wiring and there is no separate Python
call site because the dispatch is done by the harness matching `tool_name`, not by a Python caller).

## Verification Commands
```bash
python -m pytest -q tests/test_spine_rail.py
git diff --stat scripts/hooks/spine_rail.py tests/test_spine_rail.py .claude/settings.json
git diff .claude/settings.json
```

## Suggested Model Tier
Stronger — this is a security/reliability-critical hook (a misfire wedges every agent in the repo); the
existing module is dense, carefully-commented, invariant-heavy code that rewards care over speed.

## Authority
Design already decided by `LAUNCH_ORDER.md` and this gate's anchors (do not re-litigate): fail-open always,
no new subprocess, narrow matcher (`mcp__spine__spine_lease` exactly), `_mid_flight_reason`/`decide_stop`
untouched, Bash path byte-for-byte unchanged. You decide implementation-local details only (exact helper
function shape, variable names, test structure).

## Stop Conditions
Stop and return if: you find yourself needing to edit `_mid_flight_reason` or `decide_stop` (the diagnosis
would be wrong — report this, do not push through); an existing Bash-path test needs to change; the fix
would require a new subprocess; `SPINE_FILE`/`SPINE_SESSION` turn out not to be reliably present in this
hook's own environment when a door claim fires (report what you actually observed instead of guessing past
it).

## Return Format
Return IMPLEMENTER_RESULT per the standard contract, written to
`.agent-work/stop-hook-door-binding/crew-handoffs/g1-implement-implementer-result.md` before ending your
turn.
