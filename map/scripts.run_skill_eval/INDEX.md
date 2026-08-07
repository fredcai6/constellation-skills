# scripts.run_skill_eval
scripts/run_skill_eval.py, 1350 lines, 10 holes

Corpus skill-eval runner — the PURE, agent-free core (#106, gate g2).

Gates a candidate constellation corpus by running each scenario N-of-M times and
scoring the result with PROCESS checks. The verdict is carried by process checks
alone; answer-correctness checks are advisory and can NEVER move it (structural
T3). Environment flake can never FAIL a good corpus — timed-out / usage-limited /
errored runs are FENCED and excluded from the N-of-M tally (infra-fence).

This module is built test-first and is fully agent-free except the single
`launch_agent` seam (the ONLY place a real agent subprocess would be spawned).
`launch_agent` and `temp_install` are the real, live implementations (g3 wiring
shipped) — `subprocess.Popen`/`install_constellation.install_skills` under the
hood — so a `claude` process IS reachable through them. `--dry-run` and
`--dry-run-fail` instead inject a fake launcher + a dry installer through the
same seams the unit layer uses, so no path taken under `--dry-run(-fail)` ever
reaches a real `claude`.

Seam pattern mirrors run_crew.py: the module-level default launcher/installer are
resolved INSIDE the orchestration function at CALL time, so a monkeypatched (or
CLI-selected) seam takes effect.

Arm construction (load-bearing, #153): an installed skill is TWO trees welded
together. The skill SOURCE tree is `<worktree>/skills` — `--worktree` only selects
that source. The bundled engine (the `scripts/` + `references/` copied into each
installed skill) does NOT come from `--worktree`; it comes from `REPO_ROOT/scripts`
of the checkout that INVOKES `run_skill_eval.py` (the invoking checkout). So the
corpus a run fingerprints is source-tree bytes plus invoking-checkout engine bytes;
hashing the source tree alone would omit the bundled engine, which is why the
corpus id is taken over the INSTALLED tree (and normalized for install path — below).

imports stdlib: __future__.annotations, argparse, dataclasses.dataclass, dataclasses.field, datetime.date, datetime.datetime, datetime.timedelta, datetime.timezone, hashlib, importlib.util, json, os, pathlib.Path, shutil, subprocess, sys, tempfile, threading, time, tomllib
imported by: none found

```python
_HERE = Path(__file__).resolve().parent
_install = _load_install_constellation()
_hash_file = _install._hash_file
_source_commit = _install._source_commit
DEFAULT_MODEL = 'claude-sonnet-4-5'
DEFAULT_N = 2
DEFAULT_M = 3
DEFAULT_TIMEOUT_SECONDS = 2400
SCENARIO_TIMEOUT_FLOOR_SECONDS = 2400
DEFAULT_LAUNCHER = 'claude'
DEFAULT_PERMISSION_MODE = 'acceptEdits'
COMPLETION_ARTIFACT = 'work-complete.txt'
CORPUS_MARKER = _install.CORPUS_MARKER
INFRA_MARKERS = ('usage limit', 'rate limit', 'quota', 'overloaded', '429')
PERMISSION_MARKERS = ('requested permissions', 'requires manual approval', 'requires approval', 'requires pe...
EXEC_ALLOWED_TOOLS = ('Bash(python:*)', 'Bash(python3:*)', 'Bash(py:*)', 'Bash(pytest:*)')
compute_corpus_id = _install.compute_corpus_id
write_corpus_marker = _install.write_corpus_marker
assert_corpus = _install.assert_corpus
CORPUS_ROOT_SENTINEL = '<CORPUS_ROOT>'
_STDERR_TAIL_BYTES = 8192
_POLL_INTERVAL_SECONDS = 0.1
_DRAIN_GRACE_SECONDS = 5.0
_PIPE_CHUNK_BYTES = 65536
_HEARTBEAT_INTERVAL_SECONDS = 30.0
```

- [_load_install_constellation](_load_install_constellation.md) function: HOLE: no docstring
- [EvalConfigError](EvalConfigError.md) class: A scenario that violates the directory-is-schema contract (missing task.md,
- [Scenario](Scenario.md) class: HOLE: no docstring
- [CheckResult](CheckResult.md) class: HOLE: no docstring
- [LaunchOutcome](LaunchOutcome.md) class: The observable result of one launch attempt. `launch_agent` (and the fake
- [RunResult](RunResult.md) class: HOLE: no docstring
- [Verdict](Verdict.md) class: HOLE: no docstring
- [load_scenario](load_scenario.md) function: Parse a scenario directory into a Scenario. PURE and total: it reads only
- [build_eval_argv](build_eval_argv.md) function: PURE construction of the headless agent command line. Exactly
- [wrap_prompt](wrap_prompt.md) function: The verbatim task wrapped with the completion clause (contract §(d)).
- [run_check](run_check.md) function: Execute `python <script> <run-dir>` as a subprocess. Exit 0 => passed;
- [is_infra_marker](is_infra_marker.md) function: Whether `text` carries a transient-environment marker (usage/rate limit,
- [is_permission_denial](is_permission_denial.md) function: Whether `text` carries a permission-sandbox refusal marker (issue #115 tc3).
- [classify_run](classify_run.md) function: Resolve one launch attempt to exactly one class (contract §(i) infra-fence
- [verdict](verdict.md) function: The corpus verdict from the per-run classifications. PURE.
- [_hash_normalized_file](_hash_normalized_file.md) function: sha256 hexdigest of a file's TEXT with `needle` (the install root's posix
- [stable_corpus_id](stable_corpus_id.md) function: Install-path-invariant corpus id. Mirrors `_install.compute_corpus_id`'s file
- [write_stable_corpus_marker](write_stable_corpus_marker.md) function: Compute the STABLE (install-path-invariant) corpus id for `skills_dir` and write
- [_read_text_tail](_read_text_tail.md) function: Best-effort tail of a run's stderr OR transcript file, for `is_infra_marker`
- [_tree_kill](_tree_kill.md) function: Hard-kill an entire process tree, best-effort, never raising — a kill failure
- [_drain_pipe](_drain_pipe.md) function: Copy a child pipe to its capture file until EOF. Swallows OSError/ValueError
- [_stamp_meta_field](_stamp_meta_field.md) function: Best-effort merge of `fields` into a run's launch meta.json (only while it is
- [_stamp_meta_heartbeat](_stamp_meta_heartbeat.md) function: Best-effort liveness stamp into a run's launch meta.json while its subject
- [launch_agent](launch_agent.md) function: The ONE real seam — spawn `claude -p ...` (argv built by build_eval_argv)
- [temp_install](temp_install.md) function: Install the candidate corpus ONCE into `<temp_root>/skills` and return that
- [_write_transcript](_write_transcript.md) function: HOLE: no docstring
- [_dry_run_engine_spine](_dry_run_engine_spine.md) function: A minimal ENGINE-SHAPED terminal spine for the dry-run smoke: the gated
- [dry_run_launch](dry_run_launch.md) function: Fake launcher that synthesizes a REAL passing workspace — a non-empty
- [dry_run_fail_launch](dry_run_fail_launch.md) function: Fake launcher that synthesizes a BROKEN workspace (no completion artifact)
- [_dry_installer](_dry_installer.md) function: Fake installer for --dry-run/--dry-run-fail: materializes a minimal, valid
- [_probe_completion](_probe_completion.md) function: Whether the run's completion artifact is present and FRESH (mtime at/after
- [_write_meta](_write_meta.md) function: Write `<run-dir>/meta.json`. Called twice per run (a launch record at spawn,
- [_run_once](_run_once.md) function: Execute (and score) ONE attempt into `run-<index>/`. Fabricates the run-dir
- [_adjudicate_orphan](_adjudicate_orphan.md) function: Adjudicate a run whose launch meta is still `launched` — a run the runner
- [_adopt_existing_runs](_adopt_existing_runs.md) function: Re-adopt the run-<n>/ dirs an earlier (possibly killed) invocation left in
- [_read_corpus_marker](_read_corpus_marker.md) function: Read (corpus_id, source_commit) from an already-installed corpus's
- [run_scenario](run_scenario.md) function: Install the corpus once, then run the completion-seeking M-run loop and
- [build_parser](build_parser.md) function: HOLE: no docstring
- [_apply_overrides](_apply_overrides.md) function: HOLE: no docstring
- [_print_verdict](_print_verdict.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
