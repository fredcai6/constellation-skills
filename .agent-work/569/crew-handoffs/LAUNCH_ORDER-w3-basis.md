# Launch Order: `w3-basis — a proof carries its basis, and drift FAILS`

Epic 569, wave 3 (the final wave). You are one of four independent lanes; the others do not touch your files.

## Mission

**Make `CommanderSpineBasisFields` (`tests/test_checklist_engine.py:8543`) pin to the BLOB OID of the file it actually depends on, and FAIL on drift instead of skipping.**

This is the **family B** lane: evidence that was true when taken and false when relied on. It is one defect with one remedy — a proof carries the basis it was taken against, and relying on it re-checks that basis.

## The two defects, both measured

**1. The pin is the wrong granularity.** The class pins `PINNED_HEAD = "9d5aac6daa58a72fc6a665cb39879ee5705f7f71"`, captured with `git rev-parse HEAD` — the **whole repo**. Any commit to any file anywhere makes it inert. Measured: it is already dead one wave later.

```
$ python3 -m pytest tests/test_checklist_engine.py::CommanderSpineBasisFields -q -rs
sss
SKIPPED [3] pinned to shipped revision 9d5aac6d..., HEAD is now 34e80a9e... -- this test's
assumptions about the template's shape need re-verifying against the current HEAD before they
can be trusted, not silently re-run against drift
3 skipped in 0.11s
```

What it actually depends on is `skills/commander/templates/COMMANDER_SPINE.template.json`. **Pin that file's blob OID.**

**2. Drift calls `skipTest`, and a test that can only skip is a check that cannot fail.** The human ruled this exact shape 20 hours before this wave, in commit `c5ac6662`, verbatim:

> `test_the_measured_stale_set_is_reproducible` pinned the exact 8-file stale set measured when the overlay guard was authored, and skipped whenever the set differed... it skips unconditionally, forever, and **a check that can only skip is not evidence any more than one that cannot fail is.**

So the guard against family B is **itself a family A defect**. Make drift **FAIL**, with a message saying the proof is stale and must be re-run.

## Prior-Wave Verdicts (pasted)

**Why this class exists and why it deserves respect, not just repair.** No launch order asked for the skip-on-drift behaviour. A sonnet crew member, implementing a hand-authored basis field in wave 2, independently refused to certify a HEAD it had not been verified against and wrote the refusal into the test with an explicit message. That is unprompted convergence on the family-B remedy, and it is the strongest evidence this project has that the mechanism is one agents reach for naturally rather than machinery imposed on them. **You are completing a good instinct, not cleaning up a mistake.**

It reached exactly half of #381, whose proposal reads verbatim:

> A red-proof claim carries the **blob OID** of the file it ran against, and the reviewing gate compares that OID to the shipped file. **Divergence is not automatically a failure — it means the proof is stale and must be re-run, which is a mechanical check rather than a judgement.**

Skip means never re-run. That is the half that is missing.

The class's own docstring already states the shipped intent, and is worth reading before you change anything:

> Pinned to this gate's shipped git HEAD per `ruling-red-proof-pinned-to-shipped-revision`: written and run BEFORE the template carried any `basis` key and observed to fail (RED), then made to pass by the surgical text edit (GREEN). If HEAD has moved past the pinned commit, skip rather than assert against a template shape this test was never written against.

## Pre-Rulings

- `decision:blob-oid-not-head` — pin the blob OID of `skills/commander/templates/COMMANDER_SPINE.template.json` (`git rev-parse HEAD:<path>`), not repo `HEAD`. #381 specifies blob OID for exactly this reason.
  `@grade: settled/human · leans g1-implement`
- `decision:drift-fails` — on divergence, **FAIL** with a message naming the stale proof and the re-run path. Do not skip. Do not warn.
  `@grade: settled/human · leans g1-implement`
- `decision:ship-the-re-verify-path` — **this is the ruling most likely to be under-weighted, so weight it.** Fail-on-drift is only a net win if re-establishing the basis is **cheap**. A guard whose only remedy is an expensive manual re-pin is how a guard becomes something agents route around. Ship the re-verify path **alongside** the guard: whoever next legitimately edits that template must have an obvious, cheap, documented way to re-establish the proof and update the pin.
  `@grade: settled/human · leans g1-implement`
- `decision:do-not-generalise-to-qualitative-conditions` — this lane binds **evidence** (proofs, suite runs, review results). It does **not** touch the qualitative-condition population, and it does **not** roll the `basis` field out across the corpus. Measured: only 2 of 19 conditions gain from that field, so the backfill is cancelled. Different populations; do not collapse them.
  `@grade: settled/human · leans all-gates`
- `decision:prove-both-directions` — the granularity fix is only demonstrated if you show **both**: a planted edit to the template makes the tests RED, and an unrelated commit elsewhere in the repo leaves them GREEN. The second is the actual defect being fixed and it is the one a careless proof omits.
  `@grade: settled/admiral · leans g2-integrate`

## Honest-Null Clause

If a case genuinely cannot be made to work from a blob-OID pin, **name it and say why** rather than skipping it, relaxing an assertion, or hollowing out the fixture. A measured negative reported with rigor is a complete deliverable. Making a test pass by making it assert less is the one outcome this lane cannot accept — it would be the epic shipping its own defect.

## Inherited Latitude

**Delegated:** the mechanism's shape; where the re-verify path lives (a helper, a documented command, a make target); the failure message's wording; whether the pin lives in the test or in a shared helper.

**Float to the Admiral:** extending this beyond `CommanderSpineBasisFields`; any engine change to `checklist_engine.py`; anything that would make a currently-passing test fail for reasons unrelated to drift.

## File Ownership

`tests/test_checklist_engine.py` is **yours alone** this wave. `skills/commander/templates/COMMANDER_SPINE.template.json` is **read-mostly**: `w3-promote` owns edits to it, so if your work needs a change there, **float it** rather than making it. Your notes file is `.agent-work/w3-basis/notes-1.md`.

## Pre-empted Steps

Established, cite rather than re-derive: the 3-skipped measurement, the granularity diagnosis, #381's specification, and the human's ruling that drift fails rather than skips. All settled.

## Workspace

- **Worktree:** `/home/tommy/projects/569-w3-basis` — provisioned for you, verified distinct.
- **Branch:** `epic-569/w3-basis`, created by `git worktree add -b epic-569/w3-basis /home/tommy/projects/569-w3-basis origin/main`
- **Base commit:** `135c34eb` — `origin/main`, **verified green by the Admiral in a clean detached worktree: 3729 passed, 9 skipped, 0 failed** in 213.98s. A real measurement at that exact SHA, not a recollection. If your `git log -1` shows something else, stop and say so.
- **Spine:** `/home/tommy/projects/569-w3-basis/.agent-work/w3-basis/spine.json` — already instantiated from `COMMANDER_SPINE.template.json`.
- **Result artifact:** `.agent-work/w3-basis/RESULT.md` (relative to your worktree).
- **Working notes:** `.agent-work/w3-basis/notes-1.md` — sole writer. Name it `notes-1.md`, **never** `findings-1.md`; the harness `Write` tool refuses any basename containing "findings".

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
