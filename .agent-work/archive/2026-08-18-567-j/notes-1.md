# Lane J working notes

## Understand — reconciled against LAUNCH_ORDER.md

### #619 — installer

Confirmed by direct read of `scripts/install_constellation.py`:

- `default_mcp_config_path(repo_root: Path = REPO_ROOT) -> Path` returns
  `REPO_ROOT / ".mcp.json"`, where `REPO_ROOT = Path(__file__).resolve().parents[1]`
  — i.e. **wherever the running copy of `install_constellation.py` itself lives**,
  never the CLI caller's declared `--dest`/`--project`.
- `main()`'s real-CLI branch (`if __name__ == "__main__": main(wire_repo_mcp_config=True)`)
  always calls `apply_repo_mcp_config_wiring(default_mcp_config_path(), interpreter, ...)`
  **unconditionally**, regardless of `--dest`, after every real (non-dry-run) install.
  A machine-probed interpreter (`py`/`python3`/`python`, whichever answered on
  *this* host) gets stamped into that file's `mcpServers[*].command`.
- This exactly reproduces lane D2's finding: run from inside a worktree with
  `--dest /tmp/...` (entirely outside the repo) still mutates *that worktree's
  own* tracked `.mcp.json`, because `REPO_ROOT` resolves to wherever the script
  physically sits, not to `--dest`.
- Existing test `test_default_mcp_config_path_points_at_this_checkouts_own_mcp_json`
  (tests/test_install_constellation.py:4252) asserts this as *intended* today —
  "a real CLI run... finds this checkout's own file" with no gate on `--dest`.
  Fixing #619 changes this test's expectation.
- Local Unknown #2 (one bug or two) — **two, but coupled**: (a) the value written
  is machine-probed and stamped into a *tracked* file with no way to declare a
  different one, and (b) the location it writes to ignores `--dest` and is tied
  to the running script's own path. The fix in scope this wave is (b) — gate
  the repo-mcp-wiring on whether this run is actually installing *for this same
  checkout* (no `--dest`, and no `--project` pointing elsewhere) — because (a)'s
  design (a tracked file holding a real launchable per-machine interpreter name,
  with `MCP_INTERPRETER_PLACEHOLDER` as the alternative) is a deliberate, tested,
  cited decision (#539) that this launch order does not ask me to relitigate.
- Local Unknown #3 (is cwd-wiring load-bearing) — yes: it is the documented,
  tested mechanism (#539) by which a fresh clone's own `.mcp.json` gets a real
  interpreter with "nothing to remember." Keep it for the self-install path;
  narrow it so it never fires for a declared-elsewhere destination.

### #633 — model tier

Confirmed by direct read of `scripts/run_crew.py`:

- `CrewLaunchSpec.__post_init__` already raises `CrewLaunchError` when `model`
  is falsy (`decision:refuse-a-tierless-dispatch`, issue #611, already merged
  on `main` before this wave's base). So the literal "silently inherits the
  host's `~/.claude/settings.json` default" failure mode described in the
  mission is **already closed** for any caller going through `CrewLaunchSpec`
  — a dispatch with no `--model` at all raises today, it does not silently run
  Opus.
- What is **not** built yet is everything the human actually asked for: "a
  default expectation per role and an allowed choices per role that the
  dispatcher can choose from with reason," expressed per-harness. Today
  `--model` is a bare string with no table behind it: nothing validates it
  against a role's allowed set, nothing records *why* a non-default choice was
  made, and an absent `--model` is a hard refusal rather than a resolved
  role-appropriate default.
- The harness dimension already has a real, declared (never detected) hook:
  `--command` (`DEFAULT_LAUNCHER = "claude"`), already the literal binary
  `build_crew_argv` invokes and already overridable for "non-default CLIs"
  per its own `--help` text. Local Unknown #1 (detect vs declare) is settled:
  **declared** — this flag already exists and already works that way; the
  table keys on its value.
- Plan: add a role x harness tier table (shape/location is my latitude) inside
  `run_crew.py`; resolve an absent `--model` from the table (role default,
  never the host); refuse-by-name a `--model` outside the role's allowed set;
  require and record `--reason` for an in-set non-default choice, in the
  registry beside `model`. `decision:ship-todays-tiers` fixes the `claude`
  harness's values; `codex`/`local` get the same schema with no populated
  rows yet (no invented facts about model names I have not verified) — an
  unpopulated harness/role refuses by name rather than guessing, which is the
  fail-closed-cheaper behaviour extended to "no table entry" too.

## Latitude checks

- Both fixes are inside sole-writer files (`scripts/install_constellation.py`,
  `scripts/run_crew.py`) — no fence crossed.
- Template edits (`skills/admiral/templates/LAUNCH_ORDER.template.md`,
  `.agent-work/templates/LAUNCH_ORDER.template.md`) are in my ownership list;
  scope is to let a launch order *declare* a role's model tier/harness where it
  deviates from the table default, per `decision:reason-on-deviation`. Confirm
  during plan whether this is needed for the acceptance tests in the Return
  Shape, or whether it is out of scope for today's cut (Return Shape doesn't
  name the templates explicitly — treat as **latitude, not requirement**;
  touch only if the table integration needs a place to declare a deviation
  reason at dispatch time, which `--reason` on the CLI already covers).
