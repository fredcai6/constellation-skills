# Launch Order: `w3-ci — restore the merge-ref signal`

Epic 569, wave 3 (the final wave). You are one of four independent lanes; the others do not touch your files.

## Mission

**Add an `ubuntu-latest` job to `.github/workflows/ci.yml`, so that a red CI means something.**

This is a **family C** mission: the instrument is broken, so a true reading gets discarded along with the false ones.

The reasoning matters more than the diff, so here it is in full. This epic went looking for "an automated defence against a PR that turns main red," and was about to build one. Then it measured:

- `.github/workflows/ci.yml` triggers on `pull_request`. GitHub therefore checks out `refs/pull/N/merge` — **CI already tests the merge result, not the branch head.**
- PR #645 merged cleanly, was reviewer-approved with zero findings, reported "0 failed", and **turned main red**. `gh pr checks 645` → **fail**. CI caught it.
- Nobody looked, because `gh run list --limit 12` returns **12 failures out of 12**. The job is `windows-latest` only and is currently failing on `git apply --cached ... patch does not apply` (autocrlf) and a Windows temp-path `git clone --bare`. Test bugs, not regressions.

**A check that always fails carries exactly as much information as a check that cannot fail.** The mechanism was built, wired, correct, and running — and its verdict was worthless. Adding a Linux job is not new machinery; it is restoring a signal that already exists.

## Prior-Wave Verdicts (pasted)

From the Admiral's wave-2 log, verbatim:

> Proved the #645 re-staling claim instead of asserting it, because I have already been burned this epic by reasoning from an unmeasured premise. Method: fresh detached worktree at `origin/main`, `git merge origin/epic-569/w1-verdict` (clean, exit 0), then `pytest tests/test_code_map.py::MapTreeFreshnessTests`. Result: **1 failed**. So a PR that GitHub reports `MERGEABLE`, that merges without conflict, that carries an independent reviewer's APPROVE with zero findings and a commander's correct suite report, produces a RED `main` when merged.

And the measurement that created this lane:

> `.github/workflows/ci.yml:13-23` triggers on `pull_request`, so GitHub checks out `refs/pull/N/merge` — CI already tests the merge result. And it caught it: `gh pr checks 645` → fail. It was ignored because the last 12 runs are 12 failures.

## Pre-Rulings

- `decision:add-one-job-only` — add a single `ubuntu-latest` job. Do not restructure the workflow, do not add a matrix strategy unless that is genuinely the smallest expression, do not touch triggers.
  `@grade: settled/human · leans g1-implement`
- `decision:windows-stays-red` — do **not** attempt to fix the Windows failures. Explicitly out of scope by human ruling. Do not delete or disable the `windows-latest` job either.
  `@grade: settled/human · leans all-gates`
- `decision:ci-changes-beyond-this-are-surfaced` — any CI change beyond adding this one job is a **surfaced** decision class. Float it; do not decide it.
  `@grade: settled/human · leans all-gates`
- `decision:prove-it-can-go-red` — a job that has only ever been green is a check you have not shown can fail. Demonstrate the new job going red on a deliberately broken commit, then remove the break. This is the epic's own standard applied to the epic's own deliverable.
  `@grade: guess/admiral · leans g1-implement · settle: if a scratch-branch red-proof is impractical in CI, say why and propose the cheapest honest alternative`

## Honest-Null Clause

If the `ubuntu-latest` job is **not** green at `135c34eb` — if there is a genuine Linux-only failure the local run does not reproduce — that is a **complete, successful, valuable deliverable**. Report exactly what failed and stop; do not paper over it to get a green tick. A CI-only failure is a real finding about this repo, not a blocker for you.

## Inherited Latitude

**Delegated to you:** the job's Python version, step layout, caching, and naming; whether a matrix is cleaner than a second job.

**Float to the Admiral:** anything touching triggers, the Windows job, branch protection, required checks, or secrets. Any change to `ci.yml` beyond adding this one job.

## File Ownership

`.github/workflows/ci.yml` is **yours alone** this wave. No sibling lane touches it. Your notes file is `.agent-work/w3-ci/notes-1.md`.

## Pre-empted Steps

The Admiral has already established this lane's context and frozen its shape — cite this launch order rather than re-deriving:

- The measurement that CI tests the merge ref and already went red on #645. Do not re-measure it; it is pasted above.
- The decision that the fix is a Linux job rather than an Admiral-side test-merge protocol. That is settled by the human.

## Workspace

- **Worktree:** `/home/tommy/projects/569-w3-ci` — provisioned for you, verified distinct.
- **Branch:** `epic-569/w3-ci`, created by `git worktree add -b epic-569/w3-ci /home/tommy/projects/569-w3-ci origin/main`
- **Base commit:** `135c34eb` — `origin/main`, **verified green by the Admiral in a clean detached worktree: 3729 passed, 9 skipped, 0 failed** in 213.98s. That is a real measurement taken at that exact SHA, not a recollection. If your `git log -1` shows something else, stop and say so.
- **Spine:** `/home/tommy/projects/569-w3-ci/.agent-work/w3-ci/spine.json` — already instantiated from `COMMANDER_SPINE.template.json`.
- **Result artifact:** `.agent-work/w3-ci/RESULT.md` (relative to your worktree).
- **Working notes:** `.agent-work/w3-ci/notes-1.md` — you are the sole writer. Name it `notes-1.md`, **never** `findings-1.md`; the harness `Write` tool refuses any basename containing "findings".

Your **first command** is to `claim` the engine lease on that spine. You scaffold nothing — it is all provisioned.

PR integration defaults to **server-side merge**. You open the PR; the Admiral merges.

**Note on `validate_spine.py`:** your own provisioned spine currently fails it (exit 1) on `init` and `reconcile`, inherited from the shipped template. That is a real corpus defect and it belongs to `w3-promote`. It is **not** something you fix, and it is not a signal your work area is broken.
## Inherited Context

**Platform invariants** — carry these; they have each cost this project a run.

- **Encoding.** `PYTHONUTF8=1`/`PYTHONIOENCODING=utf-8` are set for you by the launcher. Read and write files with an explicit `encoding="utf-8"`.
- **Compact-format JSON templates** (`skills/*/templates/*.json`) are edited as **raw text, surgically**. Never round-trip through `json.load`/`json.dump` — it reflows the whole file and destroys blame. Re-validate with `json.load` afterwards.
- **Canonical doctrine lives at `skills/_shared/global-*.md`.** `skills/<role>/references/global-*.md` is an install-time copy that `install_constellation.py` regenerates; an edit there is silently overwritten.
- **Never `git checkout`/`git restore` a file with uncommitted peer work in the tree** — it reverts to HEAD and discards it. This fired for real and destroyed an implementer's work. Back up by file copy and restore by copy.
- **Verify a revert with `git diff --quiet -- <path>`, never `git status --porcelain`.** This repo runs `core.autocrlf=true` with `.gitattributes text=auto`, and `--porcelain` false-negatives on a byte-perfect revert.
- **Read a command's exit code directly, never through a pipe.** `cmd | tail -3; echo $?` reports `tail`'s status. The Admiral made exactly this mistake this epic and nearly recorded a working guard as vacuous.
- **CI is `windows-latest` only and is red on 100% of recent runs** (autocrlf `git apply` and Windows temp-path failures — test bugs, not regressions). **The local `python3 -m pytest -q` run is the gate.** Do not chase CI unless your mission is `w3-ci`.
- **`pytest --timeout=N` is not available here.** The plugin is not installed.
- **A mutation battery must assert the specific named assertion** — never a bare non-zero exit and never an exception. A red that is a crash certifies nothing.
- **Reproducing a falsifier its author designed proves only that the probe works.** Attack with a mutation the author did not choose.

## Data Locations

Everything this mission needs is tracked in git and present in your worktree. There are no untracked inputs (no DBs, no model artifacts).
## Budget

- **Model tier (required): `sonnet`.** Human ruling, latitude contract v2, re-confirmed at the wave-2 checkpoint. This is a live test of the epic's own thesis: if a well-specified launch order cannot let a smaller model do this work, the checklist is not taking enough off the plate — and that is a finding this epic wants. Wave 2 ran three sonnet lanes through 4,101-line engine surgery with **zero** escalations.
- **Escalation fallback:** returning blocked **twice on the same obstacle** re-dispatches you at opus. Bounded and named — it is evidence about where this order was underspecified, not a failure.
- **Compute/time:** one commander spine, one PR. Do not let scope grow past the Mission.

## Stop Conditions

Stop and return when: scope is exceeded, a decision outside your inherited latitude is needed, or the required evidence is impossible to obtain. **Asking up is always sanctioned** — return-and-query the Admiral for context this order does not cover; it answers and continues you.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap, not a share of your window, so you can be over it on turn one having done no work. The engine refuses only `start` and `reopen`, and only until a refresh-request exists for that gate. The legal sequence is **attach the refresh-request against the current why-record, then `start`, then do the work.** Attaching first sends the guard down its release path; starting first is what gets refused.

Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as an instruction to advance and hand off on turn one. Hand off when you have actually spent the context, not when you inherit the reading.

**This wave the Admiral IS watching for `REFRESH REQUESTED:` and will relaunch you.** Wave 2 raised 8 refresh-requests and the Admiral answered none; that is fixed. If you genuinely trip mid-work, the go-idle path is real this time.

## Return Shape

Write `RESULT.md` at the path named in Workspace, and include:

1. **Verdict** — what you delivered, or the measured negative.
2. **Evidence** — the exact commands and their real output. Every load-bearing number carries what was measured and at which revision. A number recalled from a commit message or a prior report is not evidence.
3. **Suite result** — `python3 -m pytest -q` at your shipped revision, run **after** your final commit, pasted verbatim. Commit, *then* re-run: that sequence's absence is what let wave 2 ship six tests that only passed uncommitted.
4. **Map impact** — whether `map/INDEX.md` needs a rebuild (a pre-commit hook now mechanizes this; say if it fired).
5. **Triage candidates** — anything you found and did not fix.
6. **Workflow feedback** — where this launch order was wrong, thin, or misleading. This is graded and it is genuinely wanted.
7. **The pre-declared refresh comparison** (every lane reports these, they are wave-3 exit criteria): your refresh-request count; whether a relaunch actually happened; your final `attempt` and `total_rework`; your reviewer's verdict and how many review rounds.

Open a PR when green. **Do not merge** — the Admiral owns integration and verifies the merge result before merging.
