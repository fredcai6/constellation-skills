# x4-testability — RESULT

**Question:** What is the cheapest *robust* near-term way to make constellation skills
and the checklist engine testable, so "what we're doing makes sense" is backed by
evidence rather than vibes?

**Headline:** The engine is already the robust part — 91% line coverage, every verb
exercised, 906 tests green in 30s. The cheapest robust wins are therefore *not* more
engine tests; they are **(1) wire CI so those 906 tests actually gate merges** and
**(2) resolve the Python launcher once at install time** instead of hardcoding `py`.
The expensive thing — a full per-skill behavioral-eval matrix (#136) — is honestly
**not worth building as a gate yet**; the current 3-scenario + weekly-curator + green-
suite posture is defensible. Details and grades below.

---

## Part 1 — Inventory (every count command-derived)

### Test suite exists and is green

```
$ ls tests/*.py | wc -l                          → 32          # test files
$ grep -rE "^\s*def test_" tests/ | wc -l         → 893          # test functions
$ python -m pytest tests/ -q                      → 906 passed, 1 skipped,
                                                     244 subtests passed in 30.33s
```

32 test files covering: the engine, install/fingerprint (`test_install_constellation.py`),
curator (`test_curate_corpus.py`), the eval runner (`test_run_skill_eval.py`), gauge
reader/writer, spine rail/provenance, and one test per most other `scripts/*.py`. The
whole suite runs in **~30 s** — fast enough to gate on every push.

### The checklist engine is heavily and directly tested

```
$ grep -cE "def test_" tests/test_checklist_engine.py            → 209   # engine test fns
$ python -m coverage run --include="*/checklist_engine.py" \
    -m pytest tests/test_checklist_engine.py -q
$ python -m coverage report -m
  scripts\checklist_engine.py   1046 stmts   95 miss   91%
```

**Every verb is exercised** (call counts in `tests/test_checklist_engine.py`): advance 113,
current 47, attach 38, amend 36, start 34, claim 32, reopen 28, waive 18, attest 17,
release 11, record 11, resume 10, block 9, append 8, `_digest`/journal 7–8,
consolidate 6, heartbeat 6, skip 2, flag-candidate 1. The pure git-policy evaluator
`evaluate_git_change_policy` is directly tested 15×.

Engine tests import the module in-process via `spec_from_file_location` **and** shell
out with `sys.executable` (lines 24, 1061–1062) — so the test suite itself is already
launcher-portable; it does *not* depend on `py`.

### Where the 91% is missing (the named, highest-risk untested surface)

There is **no fully-untested verb** — the "unit/property tests on verbs are table
stakes if gaps exist" constraint is largely **already satisfied**. The real gaps are:

1. **The IMPURE git-change-policy collector `_collect_changed_files` (L375–414).** The
   engine deliberately splits git-change-policy into a pure evaluator (15× tested) and
   a thin git-shelling collector (largely unexercised — L375-378, 386, 405-414). Real
   git edge cases (renames, staged-blob size via `cat-file`, `-\t-` binary detection)
   run only in production, never in a test. **Highest-risk untested surface.**
2. **`_find_posix_shell` git-derived Windows backstop (L446–454)** and the
   `_bash_candidates_from_git` walk — Windows-only shell discovery, only partially hit.
3. **Property space of `_glob_to_regex` (L273–282)** and the **reopen cascade** state
   machine — both are correctness-critical and combinatorial; they are covered by
   examples but not by property/fuzz tests.
4. Defensive error branches: unknown check kind (L556), unknown verb (L1840),
   record/consolidate validation (L1099, 1109) — low risk, trivially cheap to close.

Thinnest-covered *verbs* by count are `skip` (2) and `flag-candidate` (1), but both are
near-trivial state writes; they are low-risk despite low counts.

### The eval runner exists, is wired, and is unit-tested — but has 3 scenarios, one skill

```
$ grep -cE "def test_" tests/test_run_skill_eval.py             → 76    # runner tests
$ ls -d evals/*/                                                 → euler-1-multiples,
                                                                   euler-2-even-fibonacci,
                                                                   euler-5-smallest-multiple
```

- `scripts/run_skill_eval.py` is a PURE, agent-free, test-first core with **one** real
  seam, `launch_agent`. That seam is **now fully wired** (real `subprocess.Popen` with
  monotonic-deadline tree-kill and infra-fencing, L675–760) — the module docstring
  L12–13 still says "inert stubs … wired at g3" and is **stale doc-drift** worth a
  one-line fix.
- **All 3 scenarios invoke `constellation-commander-delegated` only** (verified:
  `evals/euler-1-multiples/task.md` → "Load the constellation-commander-delegated
  skill … run the issue under it"). So issue **#136's premise still holds** — that is
  the *only* skill with an invocation-in-anger behavioral eval. The other ~20 skills
  have selection/unit coverage but no behavioral scenario.
- Governance is explicit that this is intentional (`evals/README.md`): *"Evals are a
  curator instrument, not a merge gate. Nothing in CI blocks on them."* → *"new skill
  or behavior-changing rewrite → ≥1 scenario execution … mechanical edits → existing
  suite + git review; nothing gates on evals. No Iron Law."*
- Cost reality (`run_skill_eval.py` L83–89): an honest low-tier run is **13.5–30+ min
  wall-clock**, N-of-M multiplies it, and it spends real model budget.
- **#205** (atomic `_write_meta` + corrupt-meta resilience) is a real, small, still-open
  durability gap in the runner you already depend on.

### No CI, no test config

```
$ ls .github 2>/dev/null                          → (absent)
$ ls pytest.ini pyproject.toml setup.cfg conftest.py  → (none)
```

The 906 green tests run **only when a human remembers to run them.** There is no
automated regression gate, no coverage floor, no cross-interpreter matrix. This is the
single biggest evidence gap — not test *existence*, but test *enforcement*.

### The `py` launcher is hardcoded in agent-facing doctrine

`skills/_shared/windows.md` §4 mandates `py scripts/x.py` ("bare `python` may not
reliably be on PATH on a Windows box"). That keyword is baked into agent-read SKILL.md
prose across the corpus (`skills/curator/SKILL.md`, `skills/admiral/references/…`,
`skills/write-a-skill/…`, `docs/superpowers/drills/…`). On a non-Windows install `py`
is usually absent (the PEP-397 launcher is a Windows shim), so an agent burns tokens
rediscovering `python`/`python3`. Confirmed both interpreters resolve here
(`py --version` → 3.12.13; `python --version` → 3.14.3), so the tests are fine — the
brittleness lives in the **authored skill bodies**, not the test harness.

---

## Part 2 — Prior art (how other agent-skill / prompt ecosystems test)

The industry has converged on a **three-layer model**, and constellation already sits
squarely inside it:

1. **Deterministic unit tests** for the parts you can pin down — tool-selection logic,
   argument/JSON-schema validation, routing, retries, output format. "Mock the LLM and
   test everything around it," run them **on every commit**. (Kevin Tan, *Testing AI
   Agents in Production*; Guild.ai, *Unit Testing AI Agents*.) → **constellation's
   `checklist_engine.py` + `pytest tests/` is exactly this layer, and it's strong.**

2. **Behavioral evals** for output/agent quality, run **on merge-to-main or nightly**,
   **averaged across 3+ runs** to absorb stochastic variance, with **threshold gates**.
   Three eval categories crystallised in 2025: *deterministic* (exact/format/schema),
   *rubric-based* (LLM-as-judge or human), *composite* (multi-metric). (SitePoint,
   *Testing AI Agents: Validating Non-Deterministic Behavior*.) → **constellation's
   `run_skill_eval.py` is this layer: process-checks-carry-verdict = deterministic
   grader, N-of-M = averaging across runs, infra-fence = stochasticity handling.**

3. **Anthropic's own agent-eval framework** decomposes an eval into *task → trial →
   agent harness → eval harness → transcript/trace → outcome → grader → suite*, and
   names **three grader types with explicit tradeoffs**: *code-based* (fast/cheap/
   brittle), *model-based* (flexible/non-deterministic), *human* (gold/expensive);
   effective evals **combine all three**, using deterministic code for facts/structure
   and LLM judges only for semantic quality. (Anthropic, *Demystifying evals for AI
   agents*, via ai-eval.org.) → constellation deliberately uses **only the code-based
   grader** (process checks), which is the cheapest and least flaky — a defensible
   choice for a gate, at the cost of not measuring semantic quality.

4. **promptfoo** is the reference OSS harness for prompt-regression-as-code: declare
   assertions in `promptfooconfig.yaml` (deterministic + model-graded), run in CI,
   **non-zero exit fails the build**, tracks tokens/cost per run. It is the concrete
   pattern for "test prompts like unit tests." (promptfoo docs / Medium
   *Testing LLM prompts like code*.) → constellation could adopt the *CI-exit-code
   gate* idea for its **unit** layer immediately; adopting promptfoo itself for skill
   bodies is possible but heavier than the repo's own runner already provides.

**Takeaway:** constellation is not behind the field — its layer-1 (engine) is robust
and its layer-2 (runner) already embodies the 2025 best-practice shape (deterministic
graders, N-of-M averaging, infra-fencing, cost-awareness). The gap versus the field is
**enforcement (CI)**, not methodology.

---

## Part 3 — Recommendation, ranked and honestly graded

### 1. Wire CI to run the existing suite on every push. **Grade: A. Do first.**
The biggest evidence gap is that 906 green tests gate nothing. A GitHub Actions
workflow (there is a GitHub remote — `gh issue view` works) on a Windows runner
(git-bash present, satisfies the engine's bash/git shell-outs) running `pytest tests/`
plus a **coverage floor** (`--cov-fail-under=88` on the engine) turns existing work
into a real regression gate. **Cost: ~1 hr. Robustness: high** — deterministic, fast,
no model spend, no flake. This is the cheapest robust win and it is the answer to "back
it with evidence": every merge would then carry a green run.

### 2. Close the named engine gaps + add a coverage floor. **Grade: B+. Do soon, not urgent.**
Add a fixture-git-repo test for `_collect_changed_files` (the impure git-policy
collector, the top untested surface) and property tests for `_glob_to_regex` and the
reopen cascade. Honest framing: the engine is **already 91% with every verb exercised**,
so this is *hardening*, not a fire. The brief's "verb unit/property tests are non-
negotiable table stakes if gaps exist" is **largely already met**; the residue is the
git collector and the combinatorial glob/cascade space. **Cost: ~2–3 hr.**

### 3. Resolve the launcher once at install — recommend **resolve-at-install**. **Grade: A-. Do soon.**
Options assessed:
- **(a) env-var config** (`CONSTELLATION_PY`): pushes setup onto every user/host;
  brittle, and an agent still has to know to read it. **Reject.**
- **(b) probe-once wrapper script** (`scripts/py` shim that finds a working
  interpreter): good for *repo-level* scripts, but the brittle callers are **agent-read
  SKILL.md prose**, and an agent reading "run `py scripts/x.py`" can't source a shell
  wrapper. Useful as a fallback for repo scripts, insufficient for skill bodies.
- **(c) per-install rewrite** — *recommended.* `install_constellation.py` already
  templates/bundles the installed skill trees. Have it **probe the target host once**
  (`py` → `python3` → `python`, first that answers `--version`) and **stamp the
  resolved interpreter into the installed SKILL.md copies** (and a tiny sidecar the
  engine-invoking commands read). The probe runs **once, on the real machine**, so
  every skill body then names an interpreter that exists — **zero per-invocation token
  burn**, and the repo source can keep `py` as the Windows-dev default. **Cost: medium
  (~half a day, touches the installer + its tests).**

Honest caveat: the corpus is dogfooded on Windows (f1brainz etc.), so today `py`
*works* in practice and this is **not an emergency** — but the failure mode (an agent
on a fresh non-Windows box burning tokens discovering `python3`) is real and recurring,
and the fix is cheap enough and portability-defining enough to be worth it.

### 4. Do NOT build a full per-skill behavioral-eval matrix now. **Grade: D for "build it all"; B for "one scenario per high-blast-radius skill, on change."**
This is the honest "not worth it yet" the brief invited. Reasons:
- Each honest low-tier run is **13.5–30+ min**, N-of-M multiplies it, ~20 skills ×
  N-of-M ≈ **hours per full pass** plus real model spend. That is a **batch instrument,
  not a CI gate** — and a 30-min flaky gate is worse than no gate.
- The governance bar **already says so** in `evals/README.md` ("curator instrument, not
  a merge gate … No Iron Law"), and #136 itself says reference/utility skills may
  warrant "only selection checks, with a stated reason."
- The weekly iterative curator cadence + the green 30-s unit suite is **genuinely good
  enough** for the reference/utility tier.

**What to do instead (incremental, cheap):** treat behavioral evals as **eval-on-
change**, not eval-everything — add **one** scenario for an orchestrator-tier skill
(admiral, explorer) *when that skill is being changed anyway*, reusing the wired runner.
This needs the **scripted-principal seam** (canned human answers) #136 flags as new
harness work for human-in-the-loop skills — build that seam **once**, when the first
such skill is next touched, not speculatively.

### 5. Fix #205 (atomic meta write + corrupt-meta resilience). **Grade: B. Cheap, do it.**
Small, self-contained hardening of the runner you already depend on: temp-file +
`os.replace`, and make `_adopt_existing_runs` treat a corrupt meta as an orphan. Add
the regression test the issue names. **Cost: ~1–2 hr.**

### Bottom line
Robustness of the *engine* is not the problem — it is the strongest-tested thing in the
repo. The cheapest robust way to back "this makes sense" with evidence is **CI on the
existing suite (#1)** + **launcher resolve-at-install (#3)**, with **#2/#5 as cheap
hardening**. Full skill-level behavioral testing (#4) should stay a **manual, on-change,
high-blast-radius-only** instrument — the current posture is correct; do not build a
flaky matrix to chase coverage that governance has already, deliberately, declined to
gate on.

---

## Scope statement (what was and was NOT examined)

**Examined:** `scripts/checklist_engine.py` (full, 1956 lines) and its verbs/check-kinds;
`tests/` (32 files, ran the full suite + measured engine coverage with commands shown);
`scripts/run_skill_eval.py` (structure, the `launch_agent` seam, model/timeout config,
76 runner tests); `evals/` (all 3 scenarios + README governance text); `skills/_shared/
windows.md` §4 and the `py`-keyword spread across skills/scripts/docs; GitHub issues
#136 and #205; absence of `.github/` and pytest config; interpreter availability on this
host. Prior art via 3 web searches (Anthropic agent-eval framework, promptfoo, the
three-layer testing consensus) — cited below.

**NOT examined:** individual per-skill SKILL.md *behavioral contracts* beyond the
launcher keyword (I did not derive per-skill process-check sets); the curator's
`curate_corpus.py` internals (only confirmed its test exists); the gauge/hook subsystem
beyond its engine binding; whether a GitHub Actions **Windows** runner actually
provisions git-bash in this org's plan (assumed from the standard `windows-latest`
image — **verify before building #1**); the *content quality* of the 906 tests (I
measured coverage and pass/green, not whether assertions are meaningful vs tautological);
and any non-GitHub CI option. The Anthropic primary post could not be fetched (server
530) — its framework is cited via the ai-eval.org summary of it, not the original.

**Sources (prior art):**
- Anthropic, *Demystifying evals for AI agents* (summary): https://ai-eval.org/post/anthropic-demystifying-evals-for-ai-agents
- Kevin Tan, *Testing AI Agents in Production: Unit Tests, Evals, and Integration Tests*: https://kevinjztan.medium.com/testing-ai-agents-in-production-unit-tests-evals-and-integration-tests-eb0888fde381
- SitePoint, *Testing AI Agents: Deterministic Evaluation in a Non-Deterministic World*: https://www.sitepoint.com/testing-ai-agents-deterministic-evaluation-in-a-non-deterministic-world/
- promptfoo — *Testing LLM prompts like code: regression evals in CI/CD*: https://medium.com/@alexrodriguesj/testing-llm-prompts-like-code-regression-evals-in-ci-cd-with-promptfoo-5242b4dcb9be
- Guild.ai, *Unit Testing (AI Agents)*: https://www.guild.ai/glossary/unit-testing-ai-agents
