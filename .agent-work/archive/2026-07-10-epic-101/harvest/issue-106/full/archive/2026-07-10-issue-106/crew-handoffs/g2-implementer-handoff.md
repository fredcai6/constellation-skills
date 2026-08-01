# Implementer Handoff

## Gate
g2 (runner core + agent-free unit tests)

## Task
Build the PURE, agent-free core of `scripts/run_skill_eval.py` test-first (TDD), covered by `tests/test_run_skill_eval.py`. This gate builds NO real agent launch — only the pure logic and the injectable seam that the live wiring (g3) will fill. The frozen contract is at `.agent-work/issue-106/design/runner-contract.md` (READ IT FIRST — it fixes every decision below; do not re-decide).

Build these functions in `scripts/run_skill_eval.py` (contract's module seam map):
- `load_scenario(scenario_dir) -> Scenario` — PURE, total. Parse the directory-is-schema: `task.md` (required), `checks/*.py` globbed sorted (process checks; >=1 REQUIRED — zero is a hard config error), `checks/answer/*.py` (advisory), optional `fixture/`, optional `scenario.toml` (tomllib; keys `id`,`model`,`n`,`m`,`timeout_seconds`, all defaulted: n=2, m=3, timeout=1800, model=pilot tier, id=dir name). A `Scenario` dataclass with named fields: `id, task_prompt, process_checks (list[Path]), answer_checks (list[Path]), fixture_dir (Path|None), n, m, model, timeout_seconds`.
- `build_eval_argv(launcher, *, prompt, model) -> list[str]` — PURE. Exactly: `[launcher, "-p", prompt]` then `+= ["--model", model]` if model. Mirror run_crew.build_crew_argv.
- `run_check(script_path, run_dir) -> CheckResult` — run `python <script> <run-dir>` as a subprocess (this is a CHECK subprocess, NOT an agent; allowed in tests against a canned run-dir), exit 0 => passed, capture stdout as the evidence line. `CheckResult` dataclass: `id, passed (bool), evidence (str), is_answer (bool)`.
- `classify_run(outcome, *, completion_present, completion_fresh, process_results) -> RunResult` — PURE. Per the contract's infra-fence table: timeout or usage/rate-limit/overloaded/429 marker in stderr => `inconclusive` (fenced); launch error / corpus_mismatch / non-zero exit with no marker and no completion => `errored` (fenced); completion present+fresh and all process checks pass => `completed-pass`; completed (incl. exit 0 with no spine terminal) but a process check failed => `completed-fail`. `RunResult` dataclass: `status (str), reason (str|None), check_results (list)`. Provide a pure `is_infra_marker(text) -> bool` (markers: usage limit, rate limit, quota, overloaded, 429).
- `verdict(run_results, *, n, m) -> Verdict` — PURE. `completed = [r for r in run_results if r.status in (completed-pass, completed-fail)]`; `passed = [completed-pass]`. `completed < n => INCONCLUSIVE (exit 2)`; `len(passed) >= n => PASS (exit 0)`; else `FAIL (exit 1)`. `Verdict` dataclass: `status, exit_code, completed_count, passed_count, fenced_count, corpus_id, source_commit, per_run (list)`.
- `compute_corpus_id(skills_dir) -> str` — PURE. `"sha256:" + sha256(sorted (rel_posix_path, _hash_file(p)) over files)`. Reuse `install_constellation._hash_file` (import it). Also `write_corpus_marker(skills_dir, source_commit)` writing `CORPUS.json`, and `assert_corpus(run_skills_dir, expected_id) -> bool`.
- `--dry-run` and `--dry-run-fail` modes wired through the injectable `launch=` seam: a built-in `dry_run_launch` synthesizes a PASSING workspace (spine.json all-done + stub artifact) so checks pass; `dry_run_fail_launch` synthesizes a BROKEN workspace so checks fail. Neither spawns anything. The `main()` CLI parses the contract's signature; you may leave the REAL `launch_agent` + `temp_install` as a thin stub raising NotImplementedError with a "wired at g3" message (g3 fills them) — but `--dry-run`/`--dry-run-fail` MUST work end-to-end now.

## Protected Intent
The verdict is carried by PROCESS checks; answer-correctness can NEVER move it (T3, structural: the gate reads only `checks/*.py`, never `checks/answer/*.py`, and a scenario with zero process checks cannot pass). Environment flake can NEVER fail a good corpus (infra-fence: fenced runs excluded from the tally). The unit layer launches NO agent, ever.

## Test Mode
TDD required — this is pure logic with a clean test surface; write `tests/test_run_skill_eval.py` first.

## Close Criteria
- `scripts/run_skill_eval.py` implements the functions above per the frozen contract.
- `tests/test_run_skill_eval.py` is AGENT-FREE and includes, at minimum:
  - a KNOWN-GOOD canned run-dir/fixture scored PASS by the check engine;
  - a KNOWN-BAD canned run-dir scored FAIL (permanent agent-free falsification, not a manual step);
  - an INFRA-ABORT outcome (timeout / usage-limit marker) classified `inconclusive` and EXCLUDED from the tally — distinct from FAIL;
  - `verdict` math: 2-of-3 passes => PASS; 1-of-3 => FAIL; 1 completed + 2 fenced => INCONCLUSIVE (not FAIL);
  - answer checks never move the verdict (a scenario whose only failing check is an answer check still PASSes; a scenario with zero process checks is a config error);
  - a mechanical guard that importing the module / default pytest collection launches NO agent (e.g. assert the real `launch_agent` is never called during collection; a collection-time assertion or an autouse guard that fails if a real subprocess to `claude` is attempted).
- `--dry-run evals/<throwaway>` exits 0 and `--dry-run-fail` exits 1 against a minimal throwaway scenario you build in a tmp dir within a test (do not commit a half-baked scenario; g4 authors the real ones).
- Full suite green: `py -m pytest -q`.

## Allowed Scope
CREATE: `scripts/run_skill_eval.py`, `tests/test_run_skill_eval.py`. You MAY add a defensive `evals/**/_runs/` line to `.gitignore`. You MAY import (never edit) `scripts/install_constellation.py` and read `scripts/run_crew.py`.

## Specific Exclusions
- Do NOT build the real `launch_agent`/`temp_install` live wiring — that is g3 (#106). Stub with NotImplementedError("wired at g3").
- Do NOT author real `evals/<name>/` scenarios — that is g4 (#106).
- Do NOT edit any other skill, `_shared/`, `run_crew.py`, `install_constellation.py`, or install bundles.
- Do NOT wire the runner into default pytest collection in any way that launches an agent.

## Constraints
- Repo tool, not a skill: `scripts/` + `tests/` + `evals/` only; no `skills/eval-*`, no SKILL.md.
- Source repo is authority; never edit installed copies; temp-installs under system temp / gitignored, never committed.
- Reuse run_crew's call-time-resolved `launch=` seam pattern (resolve the module-level default inside the function so a monkeypatched seam takes effect).
- `Scenario`/`RunResult`/`Verdict`/`CheckResult` are dataclasses with the exact named fields above.
- POSIX-form verification commands; `py` launcher.

## Map Anchors (inbound)
- **Structural:** scripts/run_skill_eval.py (NEW); tests/test_run_skill_eval.py (NEW); scripts/run_crew.py::build_crew_argv (RELIED ON); scripts/install_constellation.py (RELIED ON, import-only).
- **Capability:** corpus eval — pure logic slice.
- **Constraints:** nothing gates on evals; process checks carry verdict (T3); N-of-M contractual (T4).
- **Decision anchors:** runner contract frozen at g1 (`.agent-work/issue-106/design/runner-contract.md`).
- **Evidence expectations:** claim "runner logic correct independent of agents" — verified by the agent-free unit layer green.

## Deliverable Path Check
- **Committed** — `scripts/run_skill_eval.py`: `git check-ignore` exits 1 (not ignored) — confirm before returning.
- **Committed** — `tests/test_run_skill_eval.py`: not ignored — confirm.
- **Local-only** — this handoff + your result under `.agent-work/` (gitignored, intentional).

## Required Evidence
- `py -m pytest tests/test_run_skill_eval.py -q` output (paste the tail).
- `py -m pytest -q` full-suite output (paste the summary line).
- `py scripts/run_skill_eval.py --dry-run <tmp-scenario>` exit 0 and `--dry-run-fail` exit 1 (paste both, with `echo EXIT=$?`).
- `git check-ignore scripts/run_skill_eval.py; echo $?` and same for the test file (expect exit 1 = not ignored).
- New files are untracked until staged — say so.

## Verification Commands
```bash
cd /c/Programs/constellation-wt-106
py -m pytest tests/test_run_skill_eval.py -q
py -m pytest -q
git check-ignore scripts/run_skill_eval.py; echo "want-1: $?"
```

## Suggested Model Tier
stronger — reason: the contract is precise but the infra-fence classification and the agent-free-guard are subtle; correctness of the verdict/T3 math is load-bearing.

## Authority
Every contract decision (schema, N/M=2/3, infra-fence table, provenance, dry-run) is FROZEN at g1 — do not re-decide. If the contract has a genuine hole, STOP and return it as a blocker (g2-review is empowered to reopen g1). You decide only implementation details within the frozen contract.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, the frozen contract cannot be implemented as written (return the specific hole), or the agent-free guarantee cannot be met.

## Return Format
Write your IMPLEMENTER_RESULT to `.agent-work/issue-106/crew-handoffs/g2-implementer-result.md`: completed slice, files changed (with untracked note), test mode satisfied, evidence produced (pasted command output), assumptions, stop conditions hit, out-of-scope observations, workflow feedback. Your final message must be your complete IMPLEMENTER_RESULT before you idle.
