# Corpus skill-evals

Graded scenarios that gate a candidate constellation corpus by running it through a
**real** workflow and scoring the result with **process checks**. The runner is
`scripts/run_skill_eval.py`; the frozen design is `.agent-work/issue-106/design/runner-contract.md`.

## The situational bar (governance — transcribed verbatim, not authored here)

> new skill or behavior-changing rewrite → ≥1 scenario execution (itself N sub-runs)
> before install; mechanical edits → existing suite + git review; nothing gates on
> evals. No Iron Law.

Evals are a curator instrument, not a merge gate. Nothing in CI blocks on them.

## How to run the harness

```
python scripts/run_skill_eval.py evals/<name>
```

Useful flags: `--n N` / `--m M` (override N-of-M), `--model MODEL`, `--permission-mode
MODE`, `--timeout SEC`, `--keep-temp` (preserve + print the temp run tree), `--json`,
and the two agent-free modes below.

### Live-run prerequisite: permission mode (do not skip)

A headless `claude -p` agent has **no interactive approver**, so unless it is launched
with an explicit permission mode every tool action needing approval is **denied** and
the agent can write *nothing* — `solution.py`, the test, the spine, the sentinel all
fail to appear regardless of corpus quality. (This was the epic-101 honest-null: the
harness was proven to the permission wall but could not pass a live pilot.)

The runner therefore passes `--permission-mode` through to the launcher, defaulting to
**`acceptEdits`** — the least-powerful documented mode that clears the file-write wall:
it auto-accepts file edits/writes **in the agent's own isolated temp workspace**
without also auto-approving arbitrary shell. Override with `--permission-mode MODE`
only if a scenario's workflow provably needs a broader mode (e.g. `bypassPermissions`
when the workflow must run non-edit tools headlessly); the default stays minimal and is
operator-visible on every run, never a silent bypass.

### Model tier: pinned LOW and explicit

`--model` defaults to a **pinned low tier (`claude-sonnet-4-5`)** and is *never*
inherited from the session. This is deliberate: a lower tier struggles sooner, which is
the point — it surfaces corpus regressions a frontier model would muscle through. An
eval verdict should come from the **cheapest model that can plausibly drive the
workflow**; `claude-haiku-4-5-20251001` is the preferred, even-cheaper choice wherever
it can complete the workflow. `--model` stays overridable, but the default is pinned,
not silently inherited.

**Exit codes:**

| exit | verdict | meaning |
|---|---|---|
| `0` | PASS | `passed >= N` over completed runs |
| `1` | FAIL | completed but `passed < N` — the corpus regressed |
| `2` | INCONCLUSIVE | `completed < N` — environment blocked (timeout / usage limit / launch error). **Environment flake can only ever yield INCONCLUSIVE, never FAIL a good corpus.** |
| `3` | usage / schema error | bad scenario (missing `task.md`, zero process checks, bad TOML) or bad CLI |

**N-of-M meaning.** The default N=2, M=3 is a **regression-vs-variance smoke, NOT a
statistical guarantee** (contract §(iii)). It separates a corpus that reliably fails
(0–1/3) from one that reliably works (2–3/3) and stops a single lucky/unlucky run
from being the verdict. It answers "did this corpus obviously regress?" — not "what
is its pass-rate?" No confidence interval, no tail-reliability claim.

### Agent-free validation modes

- `--dry-run` runs the whole pipeline with a fake **passing** launcher that
  synthesizes a **real** deliverable set — a non-empty `solution.py`, a green
  `test_solution.py`, the completion artifact, and a terminal spine — so the gating
  checks (`artifact_present`, `tests_green`, `spine_completed`) each bite **strictly**
  on a real artifact, with no sentinel stand-in. Zero agent cost; the CI smoke for the
  runner and the scenarios. Every scenario here exits `0` under `--dry-run`.
- `--dry-run-fail` runs it with a fake **broken** launcher (no solution, no test,
  in-progress spine) — the **agent-free falsification floor**. Every scenario here
  exits `1` under `--dry-run-fail`, which is the proof its process checks genuinely
  bite: a present-but-non-biting check would silently PASS the broken workspace.

## Scenario schema (directory-is-schema, per contract §(a))

```
evals/<name>/
  task.md              REQUIRED — the prompt handed to the agent (prose, no fields)
  checks/*.py          REQUIRED (>=1) — PROCESS checks; these carry the verdict
  checks/answer/*.py   OPTIONAL — ADVISORY answer checks; can NEVER move the verdict
  fixture/             OPTIONAL — seed files copied into each run workspace
  scenario.toml        OPTIONAL — overrides only (id, model, n, m, timeout_seconds)
```

Each check is a plain script: `python checks/<name>.py <run-dir>` — exit `0` pass,
non-zero fail, one stdout line printed verbatim into the verdict. The runner hands
the check a **run-dir** whose shape is: `<run-dir>/workspace/` (the agent's working
copy, a git repo, with the corpus under `workspace/.claude/skills/`), `<run-dir>/spine.json`
(engine spine if written at that level), `transcript.txt`, and `meta.json`.

**Structural T3 (why answer-correctness cannot buy a pass):** the verdict gate reads
**only** `checks/*.py`. `checks/answer/*.py` are executed, recorded, and printed but
can never move the verdict, and a scenario with zero process checks is a hard config
error. A corpus that prints the right Euler number while botching the workflow still
FAILs on the process checks.

## Pilot scenarios in this portfolio

| scenario | Project Euler # | difficulty | known answer (advisory) |
|---|---|---|---|
| `euler-1-multiples` | #1 — multiples of 3 or 5 below 1000 | easy | 233168 |
| `euler-2-even-fibonacci` | #2 — even Fibonacci terms < 4,000,000 | easy–medium | 4613732 |
| `euler-5-smallest-multiple` | #5 — smallest number divisible by 1..20 | medium | 232792560 |

Each drives a **delegated commander** solving "Project Euler #N with tests" as a
bounded issue: run the engine spine to a terminal state, dispatch implementer/reviewer
crew, write a solution file and a passing `pytest` test, and write the completion
sentinel `eval-complete.txt` as the final step. Every scenario carries three biting
process checks: `spine_completed` (parses a spine JSON and asserts a terminal status),
`artifact_present` (a non-empty solution deliverable exists), and `tests_green` (a
test file was written and `pytest` passes) — plus the advisory `answer_matches`.

## Stated limitations

1. **Project Euler exercises workflow machinery** (spines, handoffs, evidence
   discipline), **NOT architecture judgment.** The portfolio MUST diversify beyond
   Euler to test what the corpus is actually for.

## Named next scenario (NOT built here)

The **delegated-commander selection scenario** — cluster F's first non-Euler pilot —
is the named next portfolio addition. It exercises whether a delegated commander
correctly *selects* and sequences work (a judgment surface Euler does not touch),
directly answering stated limitation 1. It is named here, not built.

## Transcripts

Each run's agent stdout/stderr is kept under the temp run-dir (`transcript.txt`,
`stderr.txt`) **for diagnosis only**. The runner never judges a transcript — the
verdict is carried entirely by the process checks. Run trees live under the system
temp dir (never the repo); `--keep-temp` preserves and prints the path.
