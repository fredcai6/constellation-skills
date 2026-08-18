# Implementation Result

## Assigned gate
`g1-implement`

## Completed slice
`scripts/install_constellation.py`'s real (non-`--dry-run`) CLI install no longer rewrites the
installer checkout's own tracked `.mcp.json` when the run declares a destination elsewhere
(`--dest`, or `--project` pointing somewhere other than this checkout's own default). A plain
self-install (no `--dest`/`--project`) still wires it automatically, exactly as before.

## Scope
**Files changed:**
- `scripts/install_constellation.py` — added `is_self_install(args)`; gated the
  `apply_repo_mcp_config_wiring` call in `main()`'s tail on
  `mcp_config_path is not None or is_self_install(args)`; added the doctrine comment on the
  accepted `--scope user` edge case.
- `tests/test_install_constellation.py` — added `IsSelfInstallTests` (4 tests); added
  `test_a_dest_outside_the_checkout_never_touches_this_checkouts_own_mcp_json` to
  `RepoMcpConfigWiringTests`; updated the docstring (only) of
  `test_default_mcp_config_path_points_at_this_checkouts_own_mcp_json`; added `import argparse`.

**Specific exclusions touched:** no — `map/INDEX.md`, `scripts/checklist_engine.py`,
`scripts/mcp_spine_server.py`, `*SPINE*.template.json`, `specs/`, and
`default_mcp_config_path()`'s own signature/behavior were all left untouched.

## Behavior changed
yes — `main(wire_repo_mcp_config=True, mcp_config_path=None)` (the real CLI entry point's shape)
now skips wiring entirely when `--dest`/`--project` names a target outside this checkout, instead
of unconditionally calling `apply_repo_mcp_config_wiring(default_mcp_config_path(), ...)` and
rewriting this checkout's own `.mcp.json` regardless of where the install actually went.

## Map Impact
No architecture map exists in this repo (skill-source repo, `map/ids.jsonl` empty,
DEGRADED-UNPARSEABLE, waived by the Admiral this wave per the handoff's Map Anchors). No map
artifacts to update.

## Test mode
**Required:** `test-after`
**Satisfied:** yes — the fix and its tests were built together; the new regression test was
additionally red-proofed by temporarily reverting the guard to the old unconditional
`if wire_repo_mcp_config:` and confirming it fails, then restoring the fix and confirming green
(see TDD evidence below; this repo's `docs/agents/CREW_CONTEXT.md` verification-discipline rule
requires demonstrating a check can fail before offering it as evidence, even under test-after).

## Evidence

```bash
$ py -m pytest tests/test_install_constellation.py -q
.......................................................................................................................................................... [ 74%]
....................................................          [100%]
206 passed, 506 subtests passed in 3.05s
```

**Result:** pass (205 pre-existing + 1 new test class net; see full breakdown in TDD evidence).

**Byte-identical assertion (load-bearing):** the new test snapshots a throwaway fixture
`.mcp.json` (git-initialized directory standing in for "this checkout"), calls
`installer.main(["--agent","claude","--scope","user","--dest",<tmp-outside-the-checkout>,
"--skills","workbench"], wire_repo_mcp_config=True)` with no `mcp_config_path` override, and
asserts the fixture file's bytes are unchanged. Exact fixture content asserted byte-identical:

```
{
  "mcpServers": {
    "spine": {
      "command": "<python-interpreter>",
      "args": [
        "scripts/mcp_spine_server.py"
      ],
      "env": {
        "SPINE_FILE": "${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}"
      }
    }
  }
}
```

254 bytes, sha256 `0dccb1d7835a390786641aec75f6edd196939fe67691921addff962a98915c40`, both
before and after the call — proven identical because with `--dest` set,
`is_self_install(args)` is `False` and `mcp_config_path` is `None`, so the new guard skips the
`apply_repo_mcp_config_wiring` call outright.

**Wiring grep (proves `is_self_install` isn't shipped-inert):**

```bash
$ grep -rn "is_self_install" scripts/
scripts/install_constellation.py:2369:def is_self_install(args: argparse.Namespace) -> bool:
scripts/install_constellation.py:2529:        # satisfies `is_self_install` and still wires the checkout's own
scripts/install_constellation.py:2533:        if wire_repo_mcp_config and (mcp_config_path is not None or is_self_install(args)):

$ grep -rn "is_self_install" --include=*.py . | grep -v "def is_self_install"
./scripts/install_constellation.py:2529:  (comment, doctrine note)
./scripts/install_constellation.py:2533:  (the one call site, in main()'s tail guard)
./tests/test_install_constellation.py:4068,4075,4080,4085,4090  (IsSelfInstallTests, 4 tests)
./tests/test_install_constellation.py:4283,4301  (docstrings/comments in the new/updated tests)
```

**Non-test, non-definition call sites: 1** (`scripts/install_constellation.py:2533`, the one
guard in `main()`'s tail). Not shipped-inert.

## TDD evidence, if required

- Failing test observed (guard reverted to `if wire_repo_mcp_config:`, unconditional):
  ```
  $ py -m pytest tests/test_install_constellation.py -k test_a_dest_outside_the_checkout_never_touches_this_checkouts_own_mcp_json -q
  AssertionError: b'...".command": "<python-interpreter>"...' != b'...".command": "py"...' :
  fixture .mcp.json must stay byte-identical when --dest is set
  1 failed, 205 deselected in 0.09s
  ```
- Passing test observed (guard restored to
  `if wire_repo_mcp_config and (mcp_config_path is not None or is_self_install(args)):`):
  ```
  $ py -m pytest tests/test_install_constellation.py -q
  206 passed, 506 subtests passed in 3.08s
  ```
- Refactor while green: no refactor needed beyond the fix itself.

## Docs/contracts touched
- none — `default_mcp_config_path()`'s own docstring/behavior is unchanged; only the
  already-scoped `test_default_mcp_config_path_points_at_this_checkouts_own_mcp_json` docstring
  was updated per the handoff's Close Criteria.

## Assumptions
- none.

## Stop conditions hit
- none. No `RepoMcpConfigWiringTests` case needed modification; no caller anywhere in the repo
  depends on `wire_repo_mcp_config` firing when `--dest` is set (searched the wiring grep above);
  the guard did not require changing `default_mcp_config_path()`'s signature or behavior.

## Out-of-scope observations
- none.

## Workflow Feedback

- **Handoff gaps:** The Close Criteria's literal test recipe ("Monkeypatch `installer.REPO_ROOT`
  ... so it resolves via the real `default_mcp_config_path()`") does not work as written:
  `default_mcp_config_path(repo_root: Path = REPO_ROOT)` binds its default argument once, at
  `def` time, when the module is first `exec`'d — a plain `mock.patch.object(installer,
  "REPO_ROOT", ...)` called afterward reassigns the module global but never touches the
  function's already-bound default (confirmed with a 6-line standalone Python repro before
  writing the real test). Naively following the instruction as literally stated would either do
  nothing (test passes vacuously, no real coverage) or — worse — resolve to the REAL checkout's
  tracked `.mcp.json` if the guard under test were buggy, which is exactly what "do not touch
  this checkout's real tracked `.mcp.json` in a test" was trying to prevent. I also confirmed
  that patching `REPO_ROOT` itself (as opposed to `default_mcp_config_path`'s bound default) is
  actively harmful for a different reason: `install_skills` reads `REPO_ROOT` directly (not as a
  bound default) to locate this checkout's real `skills/`/`scripts/` source trees, so patching it
  breaks the install half of the same `main()` call with a `FileNotFoundError` — observed directly
  when I first tried it. The working fix: patch only `installer.default_mcp_config_path.__defaults__`
  to redirect the bound default to a throwaway fixture, restored in `finally`, and leave
  `REPO_ROOT` alone. Suggest updating the handoff template/close-criteria wording for future waves
  that ask for this pattern.
- **Context rediscovered:** none beyond the above — the handoff's Map Anchors correctly named
  every symbol I needed to read.
- **Instructions improvised around:** the exact test mechanics of the byte-identical proof (see
  Handoff gaps above); the fixed predicate name/logic/guard condition were followed exactly as
  given.
- **What would have made this easier:** a note in the handoff (or a shared testing reference) on
  Python's def-time default-argument binding, since this is a recurring shape (`REPO_ROOT` gates
  three other functions in this same file the same way — `validate_required_scripts`,
  `source_hook_path`, `discover_skills`/`SOURCE_ROOT`) and the same monkeypatch mistake would
  recur for any of them.

## Return status
`complete`
