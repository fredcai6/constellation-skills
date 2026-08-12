# Findings — issue #228 (install: resolve the Python launcher at install time)

Commander: cmd-228 (delegated, sonnet). Worktree: `C:/Programs/constellation-wt-228`, branch `issue-228`.

## PR-7 re-verification (own grep, own read — not the Admiral's paraphrase)

Ran independently at the `understand` step, before any planning, against
`scripts/install_constellation.py` and `tests/test_install_constellation.py` on
branch `issue-228` (forked from `main` at `83a31b1`):

- `_platform_interpreter()` — **confirmed present**, `scripts/install_constellation.py:235-241`.
  Branches purely on `os.name == "nt"`. **No subprocess probe, no `--version` call.**
- `rewrite_installed_skill_paths()` — **confirmed present and wired**,
  `scripts/install_constellation.py:244-260`, called from `install_skills` at line 381.
  Rewrites the literal token `"python <"` -> `f"{_platform_interpreter()} <"` across every
  installed `.json`/`.md`/`.txt` file (`REWRITABLE_TEXT_SUFFIXES` at line 126).
- Three-way fallback chain (`py` -> `python3` -> `python`, first that answers `--version`) —
  **grepped for `python3`/`"python"` as fallback candidates: not found.** Only the hardcoded
  posix branch exists.
- Sidecar file — **grepped `sidecar`, `CONSTELLATION_PY`: zero hits** in
  `scripts/install_constellation.py`. Does not exist.
- Existing tests (`tests/test_install_constellation.py:333-374`):
  `test_platform_interpreter_maps_os_name`, `test_installed_spine_rewrites_interpreter_prefix_on_windows`,
  `test_installed_spine_rewrites_interpreter_prefix_on_posix`. All three cover only the
  `os.name` -> name mapping and the text-rewrite mechanics; all pin `_platform_interpreter`'s
  return value via `mock.patch.object` rather than exercising a real probe (none exists to
  exercise).

**Verdict: matches the Admiral's own first-pass finding in the launch order exactly.**
Interpreter-name *selection* and SKILL.md-body *stamping* are real, shipped mechanisms —
**honest null** for those two sub-items, no work needed. The live, unshipped gap is exactly
the three items the launch order named: (1) host probe, (2) three-way fallback chain,
(3) sidecar file.

## #197 interaction re-verification

`stable_corpus_id` (`scripts/run_skill_eval.py:492`) normalizes only the baked
install-root path string via a sentinel substitution — it does **not** touch interpreter
tokens. `test_corpus_id_install_path_invariant` (`tests/test_run_skill_eval.py:601`) runs
two real installs on the **same host**, so `_platform_interpreter`'s `os.name` branch
already resolves identically across both calls today. A probe-based resolution must
preserve that same-host determinism (a flaky probe resolving differently across two
installer runs on one host would be a *new* #197-shaped regression, per the launch
order's explicit warning) — this governs the plan's approach to caching/determinism.

Findings feed the `plan` step's mission frame and gate authoring.
