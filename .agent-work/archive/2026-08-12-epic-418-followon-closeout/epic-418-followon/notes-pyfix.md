# notes-pyfix.md — local `py`/`python`/pytest fix (epic-418-followon)

Machine: this Linux box (`/home/tommy/projects/constellation-skills`), user `tommy`.
Date: 2026-08-09.
Scope fence honored: **zero repo file changes**; everything below lives under
`/home/tommy/.local/`.

## Starting state

```
$ which py python python3
/usr/bin/python3            # py: absent, python: absent
$ /usr/bin/python3 -c "import pytest"
ModuleNotFoundError: No module named 'pytest'
```

No prior `python`/`py` anywhere on PATH — confirmed before touching anything
(`which py python python3` only resolved `/usr/bin/python3`; `~/.local/bin`
held only `claude`, `gh`, `uv`, `uvx`). Nothing was overwritten.

## Step 1 attempted: plain symlink to system python3, then pip install --user pytest

```
$ /usr/bin/python3 -m pip install --user pytest
error: externally-managed-environment
× This environment is externally managed
...
hint: See PEP 668 for the detailed specification.
```

Blocked by PEP 668 (Debian's externally-managed-environment guard). Per the
launch order, did **not** pass `--break-system-packages`. `pipx` is not
installed on this box either (`which pipx` → nothing).

## Step 2: venv, made pip-installable, wired the shim so `python -m pytest`
## finds it

Created a virtualenv confined to `~/.local/`:

```
/usr/bin/python3 -m venv --copies /home/tommy/.local/share/pyfix-venv
/home/tommy/.local/share/pyfix-venv/bin/python -m pip install --upgrade pip -q
/home/tommy/.local/share/pyfix-venv/bin/python -m pip install pytest -q
```

Result: pytest 9.1.1 installed into the venv (`pip show pytest` → `Version:
9.1.1`). `--copies` was required, not the venv default — the default venv
makes `bin/python` a *symlink out to* `/usr/bin/python3.12`, and CPython's
venv auto-detection keys off the invocation path's own directory (not its
realpath target). A plain `ln -s .../pyfix-venv/bin/python
~/.local/bin/python` therefore silently resolved to `/usr/bin/python3.12`'s
prefix and missed the venv's site-packages entirely (`ModuleNotFoundError:
No module named pytest` even though the venv had it). Verified this
empirically before settling on the fix — see the false start below.

False start (kept here because it's a reusable gotcha for the cross-device
permafix): a bare symlink `~/.local/bin/python -> pyfix-venv/bin/python`
gave `sys.prefix == /usr`, `sys.executable ==
/home/tommy/.local/bin/python` — venv not detected, pytest not found. Fixed
by (a) rebuilding the venv with `--copies` so `bin/python` is a real ELF
binary, and (b) NOT symlinking directly — instead a tiny POSIX shim script
at `~/.local/bin/python` and `~/.local/bin/py`:

```sh
#!/bin/sh
exec "/home/tommy/.local/share/pyfix-venv/bin/python" "$@"
```

`exec`'ing the real venv binary by its full path sets `sys.executable` to a
path that actually sits next to the venv's `pyvenv.cfg`, so venv detection
works correctly. Verified:

```
$ python -c "import sys; print(sys.prefix); print(sys.executable)"
/home/tommy/.local/share/pyfix-venv
/home/tommy/.local/share/pyfix-venv/bin/python
$ python -m pytest --version
pytest 9.1.1
$ py -m pytest --version
pytest 9.1.1
```

This is the venv exception the launch order allowed for — flagged plainly:
**`python` and `py` on this box now resolve to a `~/.local/share/pyfix-venv`
virtualenv, not to `/usr/bin/python3` directly**, because that was the only
way to get `pytest` importable without `--break-system-packages` and
without a repo file change. The plain-symlink form the launch order
described as "the intended mechanism" does not work for a venv target for
the CPython-internals reason above; a wrapper script was necessary instead
of a symlink.

## Files/paths created (all under `/home/tommy/.local/`, nothing elsewhere)

- `/home/tommy/.local/share/pyfix-venv/` — venv, built with `--copies`,
  Python 3.12.3, `pytest==9.1.1` installed (plus pip's own upgrade to
  latest).
- `/home/tommy/.local/bin/python` — new file, POSIX shell shim (`exec`'s the
  venv's real python binary). Did not previously exist.
- `/home/tommy/.local/bin/py` — identical shim. Did not previously exist.

No system paths touched, no `sudo`, no `--break-system-packages`, no repo
files touched.

## Verification — real command, repo root

```
$ cd /home/tommy/projects/constellation-skills && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
...
=========================== short test summary info ============================
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
FAILED tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_installed_path_rewritten_template_is_up_to_date
FAILED tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_token_working_copy_up_to_date_against_promoted_baseline
FAILED tests/test_install_constellation.py::InterpreterProbeTests::test_sidecar_records_resolved_via_for_probe_success_and_fallback
FAILED tests/test_install_constellation.py::TemplateBaselineTests::test_seeded_working_copy_reads_up_to_date_against_baseline
FAILED tests/test_run_skill_eval.py::test_real_runner_process_death_leaves_resumable_state
FAILED tests/test_spine_rail.py::test_same_path_windows_normcase_sep_equivalence
7 failed, 2101 passed, 1031 subtests passed in 92.30s (0:01:32)
```

The command now **runs to completion** — that was the deliverable. It is
not green, and I did not touch it (out of scope per the launch order). What
the 7 failures actually are, isolated one at a time with no repo edits:

1. `test_spine_rail.py::test_same_path_windows_normcase_sep_equivalence` —
   asserts `_same_path("C:\\Foo", "c:/foo") is True`. Fails because
   `os.path.normcase` doesn't lowercase or translate `\` on POSIX the way it
   does on Windows. Purely a "this test encodes Windows path semantics,
   host is Linux" mismatch.

2. `test_run_skill_eval.py::test_real_runner_process_death_leaves_resumable_state`
   — fails with `PermissionError: ... hang.cmd`, because the test spawns a
   `.cmd` file as a subprocess, which is a Windows batch-file convention
   with no meaning/executable bit semantics on Linux.

3. `test_install_constellation.py::InterpreterProbeTests::test_sidecar_records_resolved_via_for_probe_success_and_fallback`
   — fails with `NotImplementedError: cannot instantiate 'WindowsPath' on
   your system` — the test directly constructs a `pathlib.WindowsPath`,
   which CPython refuses on POSIX by design.

4. `test_install_constellation.py::TemplateBaselineTests::test_seeded_working_copy_reads_up_to_date_against_baseline`
   and the two `test_feedback_tooling.py::FreshnessPathTokenTests` cases —
   all fail on a freshness/status mismatch (`'up-to-date' !=
   'upstream-changed'`), consistent with the same family: path-token
   rewriting logic that treats Windows-style paths as canonical.

   → Items 1–4 (6 of the 7 failures) are all the same shape: tests that
   assume Windows path semantics (`WindowsPath`, `\`-separated paths,
   `.cmd` execution, `normcase` lowercasing). This is exactly the
   Windows-host-legacy pattern the launch order named as issue #313's
   territory (the ~700 `py ...` references) — these test failures are
   further symptoms of the same deferred cross-device problem, not
   something introduced by this fix. **Named for the permafix, not
   touched.**

5. `test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
   — genuinely different: it diffs the committed `map/INDEX.md` against a
   fresh `python -m scripts.code_map build` run and finds real drift ("53
   modules, 1035 entities" fresh vs. "52 modules, 1027 entities"
   committed). This is ordinary repo content staleness (map/INDEX.md is
   behind the current tree), unrelated to Python/platform. Not mine to
   fix under this launch order's scope fence — named as a separate,
   unrelated finding.

Also note the pass/skip/subtest counts here (2101 passed, 1031 subtests,
7 failed, 0 skipped shown) don't match the epic's recorded baseline (1867
passed / 2 skipped / 829 subtests) — the repo has moved since that baseline
was recorded (recent commits per `git log`, e.g. `ef890dd3`,
`e5f3c4ac`, merges since). That drift is expected and not something this
task should reconcile; it's mentioned only so the numbers aren't confused
for a fix side-effect.

## Cross-device permafix candidates (named, not touched — issue #313's territory)

- The Windows-path-semantics tests above (`WindowsPath` construction,
  `.cmd` subprocess execution, `normcase`/separator assumptions in
  `_same_path`, freshness path-token rewriting) are real coupling to a
  Windows host baked into the test suite. On a POSIX-only dev box they
  will always fail regardless of how `python`/`py`/`pytest` are wired up.
  Whatever normalizes the ~700 `py ...` references under #313 should also
  look at these tests' platform assumptions.
- `map/INDEX.md` drift (item 5) is unrelated to #313 but is a live,
  reproducible staleness finding worth a ticket of its own if one doesn't
  exist: `python -m scripts.code_map build --root .` then commit, per the
  test's own failure message.
- The CPython venv-symlink gotcha documented above (symlinking straight to
  a venv's `bin/python` breaks silently unless the venv was built with
  `--copies`, or the shim execs the real path instead of following a
  symlink) is worth writing down centrally if any other device ends up
  needing a venv-backed `python`/`py` shim — it is not obvious and fails
  quietly (imports the *system* interpreter with no error, just a missing
  module).
