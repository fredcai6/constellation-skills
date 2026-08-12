# Implementer handoff — the last unpinned decoder in the DC4 property test

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g3fix3` (post-archive fix)
**Worktree (work only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door` · **PR #533**
**Authority:** Commander for issue #424, under `LAUNCH_ORDER-424-continuation.md`, whose done
definition requires the **PR green**.

## Task

The previous crew fixed the door's own stdio (`scripts/mcp_spine_server.py` now pins UTF-8) and the
two identity/server test harnesses, and it flagged one it was scoped out of. It was right, and its
call is the reason this handoff exists:

`tests/test_mcp_imperative_equivalence.py`, `cli_current_text()`, line ~182:

```python
proc = subprocess.run(
    [sys.executable, str(ENGINE), "--file", str(spine_path), "current"],
    capture_output=True, text=True, timeout=30,
)
```

`text=True` with no `encoding=` decodes with the platform default — cp1252 on Windows. This is the
**CLI arm** of the DC4 byte-identity comparison, so on Windows the CLI side arrives mangled
(`â€”` for an em-dash) while the MCP side is now correct, and the property reds. It is almost
certainly the literal origin of the CI trace:

```
E  AssertionError: projection for 'g1-implement' has an ACTIVE line that does not match the
   expected 'ACTIVE <id> [<status>] — <imperative>' shape:
   "ACTIVE g1-implement [pending] â€” Fill templates/IMPLEMENTER_HANDOFF.template.md ..."
   tests\test_mcp_imperative_equivalence.py:215
```

**Pin it to UTF-8 explicitly, matching what the previous crew did to the other harnesses.** Then
sweep the file for any other subprocess call that decodes without an explicit encoding and pin those
too — `grep -n "text=True" tests/test_mcp_imperative_equivalence.py` should return nothing lacking an
`encoding=` when you are done.

## Constraints

- Only `tests/test_mcp_imperative_equivalence.py` is in scope.
- **Do not change any imperative text, template, or engine file**, and do not normalise, fold or
  strip non-ASCII anywhere. DC4's property must keep comparing rendered output **byte-for-byte** —
  it is the check that caught this defect and its strictness is the whole point.
- Do not touch `settings.json`, any checklist JSON, or anything under `episodes/`.
- Do not weaken the population walk or the non-zero gate-count assertion.

## Verification

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_imperative_equivalence.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Baseline: **2178 passed, 1 skipped, 1061 subtests, 0 failed** on Linux. Same bar, same 5 tests in the
property file.

**The target is Windows, which you cannot run.** Do what the previous crew did rather than asserting
platform behaviour: force the CLI subprocess to a non-UTF-8 default (e.g. `PYTHONIOENCODING=cp1252`
in its environment) and show the comparison going **RED before your fix and GREEN after**, so the
pinning is demonstrated to matter rather than argued for. If you add that as a permanent test,
say so; if you run it only as a one-off demonstration, say that instead — both are acceptable, but
be explicit about which.

State which claims you verified locally and which are reasoning about Windows.

## Reporting

Write your `IMPLEMENTER_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-handoffs/g3-implementer-result-utf8b.md
```

**Write that file before ending your turn — the write is the delivery.** Include exact commands with
real output and exit codes, the red-then-green demonstration, the local-vs-reasoned split, and a
blunt `## Workflow Feedback` section. Commit to `epic-418/f-424-mcp-door`.
