# Launch Order: `w3-door — a crew without --spine gets NO door, not its dispatcher's`

Epic 569, wave 3 (the final wave). You are one of four independent lanes; the others do not touch your files.

## Mission

**In `scripts/run_crew.py`, make `_crew_door_env` explicitly CLEAR `SPINE_FILE` and `SPINE_SESSION` when `spine` is `None`, instead of leaving the dispatching process's ambient pair inherited.**

A crew dispatched without `--spine` currently inherits its **dispatcher's** spine binding. If it opens the MCP door, it drives a run it does not own. After your change it gets **no door**, which is honest: it cannot accidentally drive anything.

## Prior-Wave Verdicts (pasted)

All **7** cli-backend implementers and reviewers dispatched in wave 2 hit this, and **each named it independently in its own Workflow Feedback** — one trap rediscovered from scratch seven times. No bad state resulted; every one of them self-corrected. It is tribal knowledge, not a mechanism.

The Admiral's own version of this defect, one tier up, **did** cost: wave 1 dispatched a commander through the wrong path and `w1-wiring` shipped with **no independent review at any gate**, requiring a dedicated clean-room reviewer pass to recover.

## The behaviour you are overturning — read this before you touch anything

**The current behaviour is intentional and documented.** `scripts/run_crew.py:1333-1341` says:

> `spine_file` and `spine_session` are bound as a PAIR, and ONLY when `spine` was given. Deriving `spine_session` unconditionally (even with `spine=None`) used to hand a no-`--spine` child a mismatched pair... No `spine` means the inherited-environment route is genuinely untouched, both variables together, exactly as `crew_env()`'s own contract already promises.

and `crew_env()`'s docstring around `:1280` repeats it:

> a caller with nothing to bind still leaves the inherited value untouched, exactly as before.

Those comments are **right** that the pair stays internally consistent, and **wrong** that consistency is the property that matters. A consistent pair pointing at the **parent's** spine is precisely the hazard.

**Therefore: you must edit both docstrings in the same change.** If you fix the code and leave the prose asserting that inheritance is the safe fallback, the next reader restores the old behaviour as a bug fix. That is not optional polish; it is half the deliverable.

## Pre-Rulings

- `decision:clear-both-or-neither` — clear `SPINE_FILE` and `SPINE_SESSION` **together**. A half-cleared pair is worse than either whole state, and the existing docstring's pair-consistency reasoning is correct on that point.
  `@grade: settled/admiral · leans g1-implement`
- `decision:verify-against-a-real-child` — the acceptance evidence is a **real dispatched child**, not only a unit test of the env dict. A dict-shape test proves the function returns what you wrote; it does not prove the spawned process sees it.
  `@grade: settled/human · leans g2-integrate`
- `decision:dont-break-your-siblings` — you are editing the launcher you were **yourself dispatched through**, and three sibling lanes are running through it concurrently. Do not leave `run_crew.py` broken between commits; test before you commit, not after.
  `@grade: settled/admiral · leans all-gates`

## Honest-Null Clause

If you find a caller that **legitimately depends** on the inherited pair, that is a complete and valuable deliverable: report it precisely and stop, rather than breaking it. The Admiral would rather learn the ruling was wrong than have it forced through.

## Inherited Latitude

**Delegated:** how the clear is expressed; the test's shape; docstring wording.

**Float to the Admiral:** any change to what `--spine` itself means, to `SPINE_PARENT`, to `CREW_SCRATCH_DIR`, or to the registry schema. Any finding that a real caller depends on inheritance.

## File Ownership

`scripts/run_crew.py` and its tests are **yours alone** this wave. Your notes file is `.agent-work/w3-door/notes-1.md`.

## Pre-empted Steps

Context is established — cite this order rather than re-deriving: the 7-for-7 measurement, and the human's ruling that clearing (not inheriting) is the correct behaviour. Both are settled.

## Workspace

- **Worktree:** `/home/tommy/projects/569-w3-door` — provisioned for you, verified distinct.
- **Branch:** `epic-569/w3-door`, created by `git worktree add -b epic-569/w3-door /home/tommy/projects/569-w3-door origin/main`
- **Base commit:** `135c34eb` — `origin/main`, **verified green by the Admiral in a clean detached worktree: 3729 passed, 9 skipped, 0 failed** in 213.98s. A real measurement at that exact SHA, not a recollection. If your `git log -1` shows something else, stop and say so.
- **Spine:** `/home/tommy/projects/569-w3-door/.agent-work/w3-door/spine.json` — already instantiated from `COMMANDER_SPINE.template.json`.
- **Result artifact:** `.agent-work/w3-door/RESULT.md` (relative to your worktree).
- **Working notes:** `.agent-work/w3-door/notes-1.md` — sole writer. Name it `notes-1.md`, **never** `findings-1.md`; the harness `Write` tool refuses any basename containing "findings".

Your **first command** is to `claim` the engine lease on that spine. You scaffold nothing.

PR integration defaults to **server-side merge**. You open the PR; the Admiral merges.

**Note on `validate_spine.py`:** your own provisioned spine fails it (exit 1) on `init` and `reconcile`, inherited from the shipped template. That is a real corpus defect belonging to `w3-promote`. Not yours to fix, and not a sign your work area is broken.
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
