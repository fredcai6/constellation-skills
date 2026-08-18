# Implementer Handoff

## Gate
g1-implement

## Task
Stop `scripts/install_constellation.py`'s real (non-`--dry-run`) CLI install from
rewriting the *installer checkout's own* tracked `.mcp.json` whenever the run
declares a destination elsewhere (`--dest`, or `--project` pointing somewhere
other than this checkout's own default). Keep the existing, tested self-install
wiring (no `--dest`/`--project` given) working exactly as before.

## Protected Intent
A fresh clone's own `.mcp.json` must still get wired with a real, launchable
interpreter automatically on a plain self-install (#539) — this fix narrows
*when* the wiring fires, it does not remove the mechanism.

## Test Mode
Test-after allowed — this is a small, mechanical, well-understood change with
an existing test suite (`RepoMcpConfigWiringTests` in
`tests/test_install_constellation.py`) to extend, not build from scratch.

## Close Criteria
- Add a pure `is_self_install(args: argparse.Namespace) -> bool` function to
  `scripts/install_constellation.py` returning `args.dest is None and args.project is None`.
- In `main()`'s tail (currently `if wire_repo_mcp_config: apply_repo_mcp_config_wiring(mcp_config_path if mcp_config_path is not None else default_mcp_config_path(), interpreter, dry_run=args.dry_run, out=out)`),
  change the guard so the **entire call is skipped** — not just its path
  argument changed — unless `mcp_config_path is not None or is_self_install(args)`.
  Do **not** ever call `apply_repo_mcp_config_wiring(None, ...)` — that function
  calls `mcp_config_path.is_file()` immediately and would raise `AttributeError`
  on `None`. Every existing test in `RepoMcpConfigWiringTests` passes an
  explicit `mcp_config_path` fixture, so `mcp_config_path is not None` is the
  escape hatch that keeps every one of those tests passing unmodified.
- Add one new test proving the confirmed bug is fixed: call `installer.main()`
  with CLI-shaped args (`--agent claude --scope user --dest <tmp-outside-the-repo>
  --skills workbench`), `wire_repo_mcp_config=True`, and **no** `mcp_config_path`
  override (so it resolves via the real `default_mcp_config_path()`, i.e.
  `installer.REPO_ROOT / ".mcp.json"`). Monkeypatch `installer.REPO_ROOT` to a
  throwaway git-initialized fixture directory containing its own `.mcp.json`
  (do **not** touch this checkout's real tracked `.mcp.json` in a test), snapshot
  that fixture file's bytes before the call, assert byte-identical after.
- Add unit tests for `is_self_install` directly: `True` when `dest=None,
  project=None`; `False` when either is set. Zero filesystem/subprocess.
- Update **only the docstring** of
  `test_default_mcp_config_path_points_at_this_checkouts_own_mcp_json` — the
  function it tests, `default_mcp_config_path()`, is unchanged and still pure,
  so its assertion (`installer.REPO_ROOT / ".mcp.json" == installer.default_mcp_config_path()`)
  stays exactly as-is. The docstring's claim ("a real CLI run... finds this
  checkout's own file") is no longer unconditional — note that the real CLI
  entry point now only *calls* wiring with this path when `is_self_install`
  holds; the function itself is untouched.
- In a code comment near the new guard, note explicitly (does not need a test):
  `--scope user` with no `--dest` still satisfies `is_self_install` and still
  wires the checkout's own `.mcp.json`, even though the install target is the
  user's home directory rather than this checkout's project scope — this
  matches today's behavior and is accepted, not treated as a second bug this
  wave.

## Allowed Scope
- `scripts/install_constellation.py` — only the `is_self_install` addition and
  the `wire_repo_mcp_config` guard in `main()`'s tail. Do not touch
  `SCRIPT_RUNTIME_COMPANIONS`, `SKILL_SCRIPT_BUNDLES`, or anything else in the
  file.
- `tests/test_install_constellation.py` — add the new tests named above;
  pre-authorized to touch the existing `RepoMcpConfigWiringTests` class and
  `test_default_mcp_config_path_points_at_this_checkouts_own_mcp_json`'s
  docstring (its assertion body stays unchanged).

## Specific Exclusions
- `map/INDEX.md` — Admiral-owned (#544), do not touch.
- `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, any
  `*SPINE*.template.json`, `specs/` — fenced to a sibling lane (K) this wave.
- `default_mcp_config_path()` itself — stays a pure, unconditional path
  resolver; the gating lives in the caller (`main()`), not here.

## Constraints
- `apply_repo_mcp_config_wiring(mcp_config_path, interpreter, *, dry_run, out)` —
  its first positional parameter is a `Path`, never `None`, when called.
- Existing tests all construct their own fixture `.mcp.json` under
  `tempfile.TemporaryDirectory()` and pass it as `mcp_config_path` — do not
  change that pattern for them.

## Map Anchors (inbound)
No architecture map exists in this repo (skill-source repo; `map/ids.jsonl` is
empty; DEGRADED-UNPARSEABLE per `map_orient.py`, waived by the Admiral this
wave — evidence `e-plan-1` on the parent spine). Start reading directly at:
- **Map entry point:** `scripts/install_constellation.py` — read
  `default_mcp_config_path`, `apply_repo_mcp_config_wiring`, and `main()`'s tail
  (search `wire_repo_mcp_config`) plus `resolve_target_roots`/`resolve_target_root`
  for how `--dest`/`--project` already resolve.
- **Decision anchor:** `decision:map-index-is-admiral-owned` — do not
  regenerate/hand-edit `map/INDEX.md`. `@grade: settled/doctrine`

## Deliverable Path Check
- **Committed** — `scripts/install_constellation.py`; `git check-ignore` exits 1
  (not ignored) — verified before dispatch.
- **Committed** — `tests/test_install_constellation.py`; `git check-ignore`
  exits 1 (not ignored) — verified before dispatch.

## Required Evidence
- Full output of `py -m pytest tests/test_install_constellation.py -q`, green.
- The new byte-identical-`.mcp.json` test's assertion is load-bearing — quote
  its exact before/after content or hash in the result, not just "test
  passed."
- A `grep -rn "is_self_install" scripts/` showing the one definition and its
  one call site in `main()`, plus its test call sites — confirms it isn't
  shipped-inert.

## Wiring Grep
```bash
grep -rn "is_self_install" --include=*.py . | grep -v "def is_self_install"
```
State the count of call sites found outside the definition and outside tests.
Zero non-test call sites is a stop condition.

## Verification Commands
```bash
py -m pytest tests/test_install_constellation.py -q
```

## Suggested Model Tier
sonnet — bounded, well-scoped, existing test patterns to extend. (Dispatched
with `--model sonnet` explicitly on the CLI; this field is descriptive only,
not load-bearing — the launcher enforces the tier, not this free-text field.)

## Authority
The predicate name (`is_self_install`), its exact boolean logic (`dest is None
and project is None`), and the guard's exact condition
(`mcp_config_path is not None or is_self_install(args)`) are fixed by this
handoff — do not redesign them. Everything else about how you write the code
(helper placement, docstrings, test structure) is yours.

## Stop Conditions
Stop and return if: the guard cannot be expressed without also changing
`default_mcp_config_path()`'s signature/behavior, an existing
`RepoMcpConfigWiringTests` case cannot pass unmodified under the new guard, or
you find a caller anywhere in the repo that depends on `wire_repo_mcp_config`
firing when `--dest` is set (search first — none is expected).

## Return Format
Return IMPLEMENTER_RESULT per the standard shape, including Workflow Feedback.
Write it to `.agent-work/567-j/crew-handoffs/g1-implement-result.md` before
ending your turn.
