# Runner contract — `scripts/run_skill_eval.py` (FROZEN at g1)

Design-it-twice output. Three candidates were generated in parallel under distinct constraints; this note records the comparison, the converged contract, and the three critic-mandated requirements. **This contract is frozen for g2–g5**; g2-review is empowered to reopen g1 if it finds a hole (critic finding 5).

## The one thing designed twice
The runner contract: (a) scenario schema, (b) checks-as-plain-scripts vs DSL, (c) temp-install mechanics, (d) headless-launch mechanics, (e) N-of-M defaults — plus (i) infra-fence, (ii) corpus provenance, (iii) N/M meaning.

## Candidates compared

| Axis | A — minimal-interface | B — max-flexibility | C — common-caller-first |
|---|---|---|---|
| Schema | directory-is-schema, zero declared fields | `scenario.json` manifest + check-kind registry | directory-is-schema + explicit **run-dir contract** |
| T3 enforcement | `weak_` filename prefix (convention) | `weight: process\|answer` field, gate reads process only (structural) | process checks carry verdict (convention) |
| Checks | plain scripts, exit-code | registry of kinds, `script` default | plain scripts, take run-dir arg, exit-code |
| Depth / Locality / Seam / Test | 7 / 9 / 9 / 9 | 4 / 4 / 5 / 4 | 7 / 9 / 9 / 9 |
| Worst weakness | no schema to validate → vacuous-PASS (misnamed/stub check passes invisibly) | manifest drifts from ground truth; extra indirection | implicit run-dir convention; dry-run can mask live-vs-real artifact skew |

All three independently converged on: reuse `run_crew.py`'s call-time-resolved `launch=` seam + module-level `launch_process`; import `install_constellation` (`discover_skills`/`install_skills`/`_hash_file`/`_source_commit`); sha256 corpus id + `CORPUS.json` marker; three/four-way run classification with tally over *completed* runs only; N=2/M=3; plain scripts over a DSL; and `--dry-run` riding the same injectable seam the unit tests use.

## Converged contract — **C's skeleton + B's structural T3 graft**

Rationale: at pilot scale the two real callers are (1) a maintainer gating a change by hand and (2) the agent-free unit layer — **C is bent to exactly those** (one positional arg; pure `verdict`/`classify_run`/`load_scenario`; injected launcher; `--dry-run`/`--dry-run-fail`). B's check-kind registry is extensibility the portfolio does not yet spend (YAGNI — the curator can add it when a non-script check kind actually appears); its one enduring win is **structural T3**, which A/C leave to convention (the critic's vacuous-PASS risk). So the contract takes C wholesale and grafts B's structural T3 in a directory form (no manifest, no fragile filename prefix):

### (a) Scenario schema — directory-is-schema, with a structural process/answer split
```
evals/<name>/
  task.md              REQUIRED — the prompt handed to the agent (prose, no fields)
  checks/              REQUIRED — process/gating checks; every *.py globbed; >=1 REQUIRED
    spine_completed.py
    artifacts_present.py
    tests_green.py
  checks/answer/       OPTIONAL — advisory answer checks; NEVER in the verdict gate
    answer_matches.py
  fixture/             OPTIONAL — seed files copied into each run workspace; absent => empty git repo
  scenario.toml        OPTIONAL — overrides only (tomllib), all keys defaulted
  README.md            OPTIONAL — human notes; never read by the runner
```
`scenario.toml` keys (all optional): `id` (default dir name), `model` (default pilot tier one below prod), `n` (default 2), `m` (default 3), `timeout_seconds` (default 1800).

**Structural T3 (graft from B):** the verdict gate reads **only** `checks/*.py` (process). `checks/answer/*.py` are executed, recorded, and printed but can NEVER move the verdict. A scenario with **zero process checks is a hard config error** — this kills candidate A's vacuous-PASS hole structurally (you cannot pass on answer-only, and you cannot pass with no process check). Directory placement, not a filename prefix, carries the class — legible and code-enforced.

### (b) Checks — plain scripts, no DSL
Decided: **plain executable scripts.** Justification: caller #2 must run a check against a **canned** run-dir with no agent; a script whose only input is a directory and whose only output is an exit code is trivially unit-invokable. A DSL doubles the tested surface (an interpreter the unit layer must also stand up) for zero pilot-scale benefit. Contract:
```
python checks/<name>.py <run-dir>
  exit 0   => pass       exit != 0 => fail (verdict-carrying, for checks/)
  stdout   => one evidence line, printed verbatim into the verdict
```

### run-dir contract (C — the seam that makes canned == live)
The runner produces a fixed shape both a live run and a canned test fabricate:
```
run-dir/
  workspace/       the agent's working copy after the run (a git repo)
  spine.json       engine spine state if the workflow wrote one
  transcript.txt   agent stdout/stderr — kept for diagnosis, NEVER judged
  meta.json        {corpus_id, scenario_id, exit_code, started_at, status}
```

### (c) Temp-install mechanics
`tempfile.mkdtemp(prefix="constellation-eval-")` under the **system temp dir** — outside the repo tree, so "never committed" is structural (no `.gitignore` reliance; a defensive `evals/**/_runs/` ignore is still added in case output is redirected into the tree). Install the candidate corpus **once** via `install_constellation.install_skills(..., scope=project, dest=<temp>/skills)` (reuses token-rewrite + bundle validation); each of the M runs gets a fresh `run-K/workspace/.claude/skills/` via `copytree` (isolation over speed). Cleanup via `TemporaryDirectory` on exit; `--keep-temp` preserves + prints the path.

### (d) Headless-launch mechanics
Reuse the `#91` form via a pure argv builder mirroring `build_crew_argv`:
```python
def build_eval_argv(launcher, *, prompt, model):
    argv = [launcher, "-p", prompt]
    if model: argv += ["--model", model]
    return argv
```
Prompt = `task.md` verbatim, wrapped with a completion clause ("the constellation skills are installed in this project; run the workflow to completion; the run is complete only when <artifact> exists"). `cwd = run-dir/workspace`. The ONE real subprocess lives behind an injectable seam threaded exactly like run_crew's `launch=`:
```python
def launch_agent(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome: ...
def run_scenario(scenario_dir, *, worktree, temp_root, launch=launch_agent, ...) -> Verdict: ...
```
Tests and `--dry-run` inject a fake — no test path reaches a real `claude`.

### (e) N-of-M defaults — **N=2, M=3, majority of completed**
Smallest sample that separates a reliably-red corpus from single-run variance while staying inside a brutal usage budget (a wave commander died to a usage limit this epic; pilots run one model tier down). PASS requires `completed >= N and passed >= N` — single-run verdicts are structurally impossible.

## Critic-mandated requirements (settled)

### (i) INFRA-FENCE — tally over completed runs only
`classify_run` is pure; each attempt resolves to exactly one class:

| class | condition | in N-of-M tally? |
|---|---|---|
| completed-pass | agent completed, no infra marker, all process checks pass | yes → pass |
| completed-fail | agent completed (incl. exit 0 with no spine terminal), a process check failed | yes → fail |
| errored / fenced | launch failure, non-zero exit with no marker, **corpus mismatch** | **no — fenced** |
| inconclusive | timeout, or usage/rate-limit/overloaded/429 sniffed in stderr | **no — fenced** |

Loop is completion-seeking: launch until `completed == M` or `attempts == max_attempts` (default `M+2`). Verdict: `completed < N → INCONCLUSIVE (exit 2)`; `passed >= N → PASS (exit 0)`; else `FAIL (exit 1)`. **Environment flake can only ever yield INCONCLUSIVE, never FAIL a good corpus.** Exit codes 0/1/2 let a wrapper distinguish "regressed" from "environment blocked" without parsing text.

### (ii) CORPUS PROVENANCE — assert then surface
After install: `corpus_id = "sha256:" + sha256(sorted (rel_path, _hash_file(p)) over the installed skill tree)`; `source_commit = _source_commit()`. Write `<temp>/skills/CORPUS.json`. Before EACH run, re-hash that run's copied `.claude/skills` and assert it equals `corpus_id` — a mismatch fences the run (`corpus_mismatch`), never silently counts. The verdict header and `verdict.json` surface `corpus_id` + `source_commit`; each per-run record stamps the id it ran against. A silent install bug cannot green a corpus never loaded.

### (iii) N/M MEANING — stated plainly
2-of-3 is a **regression-vs-variance smoke, NOT a statistical guarantee.** It separates a corpus that reliably fails (0–1/3) from one that reliably works (2–3/3) and stops a single lucky/unlucky run from being the verdict. It answers "did this corpus obviously regress?", not "what is its pass-rate?" — no confidence interval, no tail-reliability claim. Printed on every verdict and documented in `evals/README.md`.

## `--dry-run` and `--dry-run-fail`
`--dry-run` runs the whole pipeline (install, provenance, M-run loop, check execution, classification, verdict, exit code) with a fake launcher that synthesizes a passing workspace (spine.json all-done + stub artifact) — zero agent cost; the CI smoke for the runner itself and caller #2's live target. `--dry-run-fail` synthesizes a BROKEN workspace so the checks catch it — the **agent-free falsification floor**. Neither is a substitute for the live acceptance run: the run-dir convention's live-vs-real skew (candidate C's own worst weakness) is exactly what the g5 live broken-variant run validates — so `--dry-run-fail` is the FLOOR and the live broken corpus is the CEILING.

## CLI signature
```
python scripts/run_skill_eval.py SCENARIO_DIR
  [--worktree PATH] [--n N] [--m M] [--model MODEL] [--timeout SEC]
  [--command claude] [--dry-run] [--dry-run-fail] [--keep-temp] [--json]
```
Exit: 0 PASS · 1 FAIL · 2 INCONCLUSIVE · 3 usage/schema error.

## Module seam map (all agent-free-testable except `launch_agent`)
`load_scenario` (pure) · `build_eval_argv` (pure) · `temp_install` (injectable installer) · `compute_corpus_id`/`write_corpus_marker`/`assert_corpus` (pure over a tree) · `run_check` (subprocess of a check, canned run-dir) · `classify_run` (pure) · `verdict`/tally (pure) · `launch_agent`/`launch=` (the one real seam) · `run_scenario(…, launch=…)` · `main`.

## What this contract fixes for downstream gates
- g2 builds `load_scenario`, `classify_run`, `verdict`, `build_eval_argv`, `compute_corpus_id`, `run_check`, `--dry-run`/`--dry-run-fail`, all unit-tested agent-free — including a known-BAD fixture that scores FAIL, a known-GOOD that scores PASS, an infra-abort fixture that is fenced (not FAIL), and a collection-time no-agent guard.
- g3 adds `launch_agent` + `temp_install` live wiring + `assert_corpus`, with fake-subprocess end-to-end tests driving pass AND fail transcripts.
- g4 authors 2–3 Euler scenarios to this directory schema + `evals/README.md`.
- g5 runs one live, N-of-M, + the live broken-variant falsification.
