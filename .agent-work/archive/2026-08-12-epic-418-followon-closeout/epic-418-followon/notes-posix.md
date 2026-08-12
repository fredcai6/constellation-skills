# POSIX suite-green — notes (epic-418 followon, posix-green worktree)

Branch: `epic-418/posix-suite-green`, worktree `/home/tommy/projects/constellation-skills-wt/posix-green`,
based on `a1eab1f1`. Host: Linux, `python`/`py` both resolve to a venv shim at
`~/.local/share/pyfix-venv` (Python 3.12.3, pytest 9.1.1).

Pinned baseline on `a1eab1f1` (verified by the Admiral): `6 failed, 2133 passed, 1061 subtests`.
Six named failures, addressed below as two Kind-A (shipped-code POSIX defect) fixes covering
three tests, and three Kind-B (test-fixture Windows-only assumption) fixes.

## 1. Kind A — `check_skill_freshness.py` interpreter-guess mirror bug

**Failures covered (3):**
- `tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_installed_path_rewritten_template_is_up_to_date`
- `tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_token_working_copy_up_to_date_against_promoted_baseline`
- `tests/test_install_constellation.py::TemplateBaselineTests::test_seeded_working_copy_reads_up_to_date_against_baseline`

**Mode:** `_normalized_hash()` reverses the installer's `python <` -> `<interpreter> <` rewrite by
GUESSING the interpreter via a local os.name-based `_platform_interpreter()` mirror, instead of
reading the actual per-skill `interpreter.json` sidecar `install_constellation.py` writes. On this
POSIX host the real host probe resolves `py` (order `py`/`python3`/`python`, all three resolve via
the fixed `pyfix-venv`), but the freshness guess hardcoded `python3` for `os.name != 'nt'` —
producing a false `upstream-changed`/`project-customized` read on an untouched template.

**Fix (`scripts/check_skill_freshness.py`):** added `_resolved_interpreter(skill, skills_root)`,
which reads `skills_root/<skill>/interpreter.json` for the interpreter actually probed/stamped by
the installer, falling back to `_platform_interpreter()`'s os.name guess only when the sidecar is
absent (skill never installed). `_normalized_hash` now calls `_resolved_interpreter` instead of
`_platform_interpreter` directly. No change to `install_constellation.py`.

**Before (failing):**
```
FFF                                                                      [100%]
=================================== FAILURES ===================================
_ FreshnessPathTokenTests.test_installed_path_rewritten_template_is_up_to_date _
    self.assertEqual(statuses["COMMANDER_SPINE.template.json"], "up-to-date")
E   AssertionError: 'upstream-changed' != 'up-to-date'
_ FreshnessPathTokenTests.test_token_working_copy_up_to_date_against_promoted_baseline _
    self.assertEqual(statuses[spine], "up-to-date")  # not phantom-customized
E   AssertionError: 'project-customized' != 'up-to-date'
_ TemplateBaselineTests.test_seeded_working_copy_reads_up_to_date_against_baseline _
    self.assertEqual("up-to-date", statuses["COMMANDER_SPINE.template.json"])
E   AssertionError: 'up-to-date' != 'upstream-changed'
=========================== short test summary info ============================
FAILED tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_installed_path_rewritten_template_is_up_to_date
FAILED tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_token_working_copy_up_to_date_against_promoted_baseline
FAILED tests/test_install_constellation.py::TemplateBaselineTests::test_seeded_working_copy_reads_up_to_date_against_baseline
3 failed in 0.11s
```

**After (passing):**
```
...                                                                      [100%]
3 passed in 0.09s
```

## 2. Kind B — `InterpreterProbeTests` sidecar test fakes `os.name` around a full install

**Failure covered (1):**
- `tests/test_install_constellation.py::InterpreterProbeTests::test_sidecar_records_resolved_via_for_probe_success_and_fallback`

**Mode:** the fallback half of the test wrapped the FULL `install_skills()` call (which internally
calls `write_corpus_marker` -> `compute_corpus_id`, doing a bare `Path(skills_dir)` re-wrap) inside
`mock.patch.object(installer.os, "name", "nt")`. `Path()`'s class selection reads `os.name` at call
time, so the re-wrap silently became a `WindowsPath` instance; the next path-join on it raised for
real on this POSIX host. The hazard was already documented 20 lines above in the same file
(`_install_commander_spine`'s comment: pathlib refuses to build a foreign path flavor).

**Fix (`tests/test_install_constellation.py`):** narrowed the `os.name` mock to wrap only the
`resolve_interpreter()` call (matching the existing
`test_resolve_interpreter_falls_back_to_os_default_on_total_failure` pattern), then threaded the
resulting `InterpreterResolution` explicitly via `install_skills(..., interpreter=resolution)` so
`install_skills` does not re-probe and never touches `os.name` itself. Same assertions kept
(`resolved_via == "os-default-fallback"`, `interpreter == "py"`) — **Windows fallback semantics
unchanged; the test still proves the same Windows behaviour, just without corrupting an unrelated
code path via a too-broad mock.**

**Before (failing):**
```
......F                                                                  [100%]
=================================== FAILURES ===================================
_ InterpreterProbeTests.test_sidecar_records_resolved_via_for_probe_success_and_fallback _
    cls = <class 'pathlib.WindowsPath'>
    args = (WindowsPath('/tmp/tmpj_73nikz/skills'), 'constellation-admiral')
E   NotImplementedError: cannot instantiate 'WindowsPath' on your system
=========================== short test summary info ============================
FAILED tests/test_install_constellation.py::InterpreterProbeTests::test_sidecar_records_resolved_via_for_probe_success_and_fallback
1 failed, 6 passed in 0.13s
```

**After (passing):**
```
.......                                                                  [100%]
7 passed in 0.06s
```

## 3. Kind B — `test_same_path_windows_normcase_sep_equivalence` hardcodes Windows folding as universal

**Failure covered (1):**
- `tests/test_spine_rail.py::test_same_path_windows_normcase_sep_equivalence`

**Mode:** the test asserted `sr._same_path("C:\\Foo", "c:/foo") is True`, relying on ntpath's
`normcase` (lowercases + folds backslash/forward-slash). On POSIX, `os.path.normcase` is identity
and backslash is not a separator, so posixpath correctly treats these as two DIFFERENT strings —
the shipped `_same_path` (`scripts/hooks/spine_rail.py:313`, wraps `os.path.normcase`+`normpath`)
is doing the platform-correct thing on both platforms; the test just hardcoded Windows-only folding
as if it were universal.

**Fix (`tests/test_spine_rail.py`):** skipped the Windows assertion on non-Windows via
`pytest.mark.skipif(sys.platform != "win32", ...)`, and added a companion test,
`test_same_path_posix_case_and_backslash_are_significant`, asserting the platform-correct POSIX
behaviour (`is False`, i.e. no spurious relaxation on POSIX either), skipped on `win32`. **The
Windows test itself was not deleted or weakened — it still asserts `is True` verbatim, and will run
and prove that behaviour on an actual Windows host under the `skipif`.**

**Before (failing):**
```
tests/test_spine_rail.py .F.                                             [100%]
=================================== FAILURES ===================================
_______________ test_same_path_windows_normcase_sep_equivalence ________________
    assert sr._same_path("C:\\Foo", "c:/foo") is True
E   AssertionError: assert False is True
=========================== short test summary info ============================
FAILED tests/test_spine_rail.py::test_same_path_windows_normcase_sep_equivalence
================= 1 failed, 2 passed, 106 deselected in 0.14s ==================
```

**After (passing, Windows case now skipped on this Linux host, POSIX companion runs):**
```
tests/test_spine_rail.py .s..                                            [100%]
================= 3 passed, 1 skipped, 106 deselected in 0.10s =================
```

## 4. Kind B — `_write_hang_cmd` always wrote a Windows `.cmd` batch file

**Failure covered (1):**
- `tests/test_run_skill_eval.py::test_real_runner_process_death_leaves_resumable_state`

**Mode:** `_write_hang_cmd()` always wrote a Windows `.cmd` batch file and spawned it via
`Popen(shell=False)`, which cannot execute on Linux (no exec bit, no shebang, not a PE) — fails with
`PermissionError`. The production code under test, `run_skill_eval._tree_kill`
(`scripts/run_skill_eval.py:621`), was ALREADY portable — it branches on `os.name` and falls back to
`proc.kill()` on non-Windows — so no production-code change was needed or made.

**Fix (`tests/test_run_skill_eval.py`, test-fixture only):** `_write_hang_cmd` now branches on
`os.name`: unchanged `.cmd`/`py -c` shim on Windows (verbatim), a chmod'd shebang shell script
(`#!/bin/sh` invoking `exec sys.executable -c 'import time; time.sleep(600)'`) on POSIX, both
spawned via `Popen(shell=False)` with no shell interpreter between. `_confirm_hang_primitive`'s
docstring/messages were generalized away from the literal `.cmd` (now platform-neutral) without
changing behaviour — it still fails loudly rather than silently switching mechanisms.
**`run_skill_eval._tree_kill` needed no change — its non-Windows branch (`proc.kill()`) already
existed and reaps the POSIX subject correctly.**

**Before (failing):**
```
F                                                                        [100%]
=================================== FAILURES ===================================
____________ test_real_runner_process_death_leaves_resumable_state _____________
    p = subprocess.Popen([str(hang_cmd)], stdin=subprocess.DEVNULL, ...)
E   PermissionError: [Errno 13] Permission denied: '.../hang.cmd'
=========================== short test summary info ============================
FAILED tests/test_run_skill_eval.py::test_real_runner_process_death_leaves_resumable_state
1 failed in 0.13s
```

**After (passing, a real subprocess is spawned and killed):**
```
.                                                                        [100%]
1 passed in 0.82s
```

## Windows behaviour preserved — one line per Kind-B fix

- `InterpreterProbeTests` (#2): identical Windows-fallback assertions kept (`resolved_via ==
  "os-default-fallback"`, `interpreter == "py"`); only the `os.name` mock's blast radius was
  narrowed to the resolution call.
- `test_same_path_windows_normcase_sep_equivalence` (#3): kept verbatim under
  `skipif(sys.platform != "win32")`, still asserts `is True` and will run for real on a Windows CI
  host.
- `_write_hang_cmd` / `_confirm_hang_primitive` (#4): the Windows branch (`.cmd` + `py -c` shim,
  `Popen(shell=False)`) is untouched byte-for-byte; only a POSIX branch was added alongside it.

## Full-suite proof

Command: `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`

First full-suite pass (after all four fixes) surfaced one NEW, non-baseline failure:
`tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`.
Cause: our own in-fence edits added entities the map hadn't seen (`_resolved_interpreter` in
`scripts/check_skill_freshness.py`: scripts 1037->1038 entities; the new POSIX companion test in
`tests/test_spine_rail.py`: tests 3454->3455 entities), so `map/INDEX.md`'s committed entity counts
went stale relative to a fresh build. Fixed by running the project's own documented rebuild,
`python3 -m scripts.code_map build --root .` (deterministic, no manual edit) — `map/INDEX.md` is
included in this branch's diff.

Full-suite tail after the map rebuild:
```
2139 passed, 1 skipped, 1061 subtests passed in 94.21s (0:01:34)
```
0 failed. The 1 skip is the Windows-only `test_same_path_windows_normcase_sep_equivalence`
(expected on this Linux host). `2139 = 2133 (baseline passed) + 6 (all six baseline failures now
pass)`; `1061` subtests unchanged from baseline.

## Reported, not changed — belongs to the human

`scripts/install_constellation.py`'s `INTERPRETER_CANDIDATES = ("py", "python3", "python")` order
prefers `py` first, even on POSIX. On this host all three candidates resolve identically via the
`pyfix-venv` shim, so it happens not to matter here — but on a generic POSIX host where `py` is not
a real interpreter, this order means the *first* probe attempt is a Windows-launcher name. This is a
real, pre-existing finding, not touched by this change (confirmed by `git diff` — zero changes to
`scripts/install_constellation.py` in this branch).

## Other out-of-fence finds (named, not fixed)

- None found beyond the `INTERPRETER_CANDIDATES` order above. Blast-radius grep (see PR/commit
  evidence) turned up no other live caller of `_normalized_hash`/`_platform_interpreter`/
  `_resolved_interpreter` outside `scripts/check_skill_freshness.py` itself, and no file under the
  concurrent f-424 agent's ownership (new MCP files, `.mcp.json`) was touched — none exists in this
  worktree.
