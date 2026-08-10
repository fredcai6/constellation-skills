# Implementer handoff — `test -f` in a fixture check makes four tests Windows-only-red

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g3fix4` (post-archive fix)
**Worktree (work only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door` · **PR #533**
**Authority:** Commander for issue #424, under `LAUNCH_ORDER-424-continuation.md`, whose done
definition requires the **PR green**.

## The break

Windows CI is down to **4 failures**, all in `tests/test_mcp_spine_server.py::ToolsWrapEngineTests`,
all the same shape — `spine_advance` returns `isError: True` where the test expects success:

```
adv = self.client.call("spine_advance", task_id="g1", why="notes.txt written, understood")
>       self.assertFalse(adv.get("isError"))
E       AssertionError: True is not false
tests\test_mcp_spine_server.py:274
```

Failing: `test_spine_start_and_advance_drive_a_gate_to_complete`,
`test_spine_advance_mechanical_flag`, `test_spine_evidence_attach_satisfies_artifact_postcondition`,
`test_spine_evidence_waive_satisfies_without_making_check_true`.

The cause is in the fixture, two lines:

```python
tests/test_mcp_spine_server.py:67
    "check": {"kind": "command", "command": f"test -f {w}/notes.txt"},
tests/test_mcp_spine_server.py:92
    "check": {"kind": "command", "command": f"test -f {w}/optional_report.txt"},
```

`test -f` is a POSIX shell builtin. The engine runs check text through the shell, and on Windows
there is no `sh`/`test`, so the postcondition fails, so `advance` refuses, so `isError` is true. The
file it is looking for genuinely exists — the check is simply unrunnable on the platform.

**This is a fixture defect, not a product defect.** The engine and the door behave correctly: a check
that cannot run is a failing check. Do not change engine or server behaviour.

## Task

Replace both `test -f` checks with the **portable house pattern this repo already uses** for command
checks — `tests/test_checklist_engine.py` lines 25-26:

```python
PASS_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(0)"'
FAIL_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(1)"'
```

i.e. drive the check through `sys.executable` rather than a shell builtin. Yours must still be a
genuine **file-existence** check — the tests around it write the file and then expect the gate to
advance, and one of them (`optional_report.txt`) depends on the check **failing** while the file is
absent, then being satisfied by `waive`. So:

- with the file present, the check must exit 0;
- with the file absent, it must exit non-zero.

Mind the quoting: the path is interpolated into a shell command line and, on Windows, will contain
backslashes and may contain spaces. A naive f-string that works on Linux can break on Windows purely
on quoting, which is the same class of bug as the one you are fixing.

## Then sweep, so this is the last round

CI has now been red four times on four different platform assumptions in these files
(`select.select`, server stdio encoding, test-harness decode encoding, and now a shell builtin).
Before you finish, **grep the three files this workstream owns** —
`tests/test_mcp_spine_server.py`, `tests/test_mcp_identity.py`,
`tests/test_mcp_imperative_equivalence.py` — for anything else that assumes POSIX: shell builtins or
`sh`-only syntax in check text or subprocess calls, `/`-only path assembly inside command strings,
`os.kill`/signal use, `/dev/null`, backticks, `&&`/`||` chaining inside a check command. Report what
you found **and what you deliberately left alone**, with the reason.

## Constraints

- In scope: `tests/test_mcp_spine_server.py`, and the other two files only if the sweep finds a real
  portability defect. Name anything you change.
- **Do not change `scripts/mcp_spine_server.py`, `scripts/checklist_engine.py`, `.mcp.json`, any
  template, or any imperative text.**
- **Do not weaken the assertions.** `optional_report.txt`'s check must still genuinely fail while the
  file is missing — that is what makes the `waive` test meaningful. A check rewritten to always pass
  would turn a real test into a decorative one.
- Do not touch `settings.json`, any checklist JSON, or anything under `episodes/`.

## Verification

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Baseline: **2178 passed, 1 skipped, 1061 subtests, 0 failed** on Linux. Same bar.

**Demonstrate both directions of the new check** rather than asserting them: run it yourself with the
file present (exit 0) and absent (exit non-zero), and paste the exit codes. A file-existence check
that cannot fail would silently disable the `waive` test.

You cannot run Windows. State which claims you verified locally and which are reasoning about
Windows — that distinction is what the last three rounds turned on.

## Reporting

Write your `IMPLEMENTER_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-handoffs/g3-implementer-result-posix.md
```

**Write that file before ending your turn — the write is the delivery.** Include exact commands with
real output and exit codes, both directions of the new check, the sweep findings (including what you
left alone and why), the local-vs-reasoned split, and a blunt `## Workflow Feedback` section. Commit
to `epic-418/f-424-mcp-door`.
