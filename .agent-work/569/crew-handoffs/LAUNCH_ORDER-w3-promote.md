# Launch Order: `w3-promote — turn qualitative conditions into checks that can actually fail`

Epic 569, wave 3 (the final wave). You are one of four independent lanes; the others do not touch your files.

## Mission

**Promote qualitative (`check: null`) conditions in the shipped spine templates into REAL checks — using check kinds that already exist, adding no new mechanism.**

This is the **family A** lane and it is the epic's filed thesis: a condition satisfied by writing the word "attested" proves nothing. It is also the highest-yield work identified at the wave-2 checkpoint, precisely because it costs no new machinery.

## The measurement that scoped this — read it, do not re-derive it

Wave 2's `w2-basis` ran a design-it-twice panel with **N=3 independent candidates** (`structured-field`, `statement-convention`, `artifact-conversion`) against all **19** real `check: null` conditions in `COMMANDER_SPINE.template.json`. All three converged on the same partition:

| bucket | n | meaning |
|---|---|---|
| 1 — no locator expressible at all | **8/19** | a judgement with no artifact behind it |
| 2 — **locator expressible, NO new mechanism needed** | **9/19** | a direct check-kind promotion already gives them everything |
| 3 — gains from the new `basis` field | **2/19** | artifact exists, but the claim is a judgement no mechanical check can make |

**Bucket 2 is your target.** Extrapolated across the ~65 qualitative conditions in the corpus, that is roughly 31 conditions that could become real checks today.

This partition also answered the human's deferred question about where the blocking line falls: **it is not a line across all conditions, it is this three-way partition, and it falls between bucket 2 and bucket 3.**

## A concrete, already-measured starting point

`scripts/validate_spine.py` **refuses the shipped `COMMANDER_SPINE.template.json` itself** — exit 1:

```
$ python3 scripts/validate_spine.py skills/commander/templates/COMMANDER_SPINE.template.json
2 fault(s)
  [falsifiable-all-null] init: every postcondition's check is null -- nothing here can ever refuse
    this gate; give at least one condition a real check, or if it is genuinely qualitative, that is
    still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] reconcile: every postcondition's check is null -- ...
```

**The repo's own validator rejects the template every commander in this project runs, and nobody noticed because nothing calls `validate_spine.py` on the shipped templates.** That is this epic's thesis reproduced inside its own tooling. Those two gates are your first targets, and wiring `validate_spine.py` at the shipped templates is a candidate deliverable in its own right — see the pre-rulings.

For orientation, `COMMANDER_SPINE.template.json` carries **23 postconditions, 11 of them `check: null`**, with `init` and `reconcile` all-null.

## Prior-Wave Verdicts (pasted)

Wave 1 shipped `RegistrationLint` and `VocabularyRule` **blocking** (`tests/test_check_script_registration.py:151`, `:228`) with a 19-entry allowlist, each entry individually verified by an independent clean-room reviewer. Those were ratified by the human at the wave-2 checkpoint on this reasoning, which applies directly to your work:

> A pytest test that does not fail is a test that does nothing — report-only there **is** family A.

Wave 1 also produced `docs/CHECK_SCRIPT_CENSUS.md`: 26 check-shaped scripts, **17 live, 8 unwired, 1 dead**. Read it before deciding whether a check kind you want already has a live enforcement path.

## Pre-Rulings

- `decision:no-new-check-kinds` — **promotion only.** Use check kinds that already exist in the engine. If you find a condition that would need a new kind, that is a bucket-1 or bucket-3 condition: leave it, record it, move on. Inventing a kind is the machinery-first move this epic exists to refuse.
  `@grade: settled/human · leans all-gates`
- `decision:no-basis-backfill` — do **not** roll the `basis` field out across the qualitative conditions. Measured 2/19 gain; shipping a field to ~65 conditions to help ~7 is machinery for machinery's sake. `w3-basis` owns the evidence-basis mechanism and that is a **different population**.
  `@grade: settled/human · leans all-gates`
- `decision:record-the-partition-per-condition` — **this is the ruling with teeth, because the whole lane rests on an extrapolation.** All 19 measured conditions came from **one** template. The other ~46 live in `ADMIRAL_SPINE`, `EXECUTE_PLAN`, `REVIEW_SURVEY` and siblings and may partition differently. For every condition you assess, record which bucket it landed in and whether that matched the predicted split. **If a template partitions materially differently from 9/19, that is a material exception: stop and float it to the Admiral — it triggers a replan rather than being absorbed silently.**
  `@grade: settled/human · leans all-gates`
- `decision:blocking-where-adjudicated` — a promoted check ships **blocking** where the adjudication is available at authoring time. Where the signal is genuinely unmeasured, it ships report-only **and names its promotion trigger in the same PR** — what measurement, taken when, promotes it. A report-only check with no named trigger is this epic committing its own defect.
  `@grade: settled/human · leans g2-integrate`
- `decision:red-proof-each-promotion` — each promoted condition is red-proved against the **shipped revision**: show it failing when the thing it checks is actually absent or wrong, at the revision you ship. Reproducing a falsifier you designed proves only that your probe works; attack with a mutation you did not choose.
  `@grade: settled/admiral · leans g2-integrate`
- `decision:validate-spine-wiring-is-in-scope` — wiring `validate_spine.py` so the shipped templates are actually validated is **in scope and encouraged**, since it is the mechanism that would keep this class of defect from returning. But if wiring it means the suite goes red on faults you are not fixing this wave, **float that** rather than either suppressing faults or expanding scope to fix them all.
  `@grade: guess/admiral · leans g1-plan · settle: count the faults across all shipped templates first, then decide with the Admiral whether the wiring lands this wave`

## Honest-Null Clause

**A small number promoted, honestly measured, is a successful wave.** If you assess the corpus and find that far fewer than the predicted ~31 conditions can honestly become real checks, say so with the per-condition evidence. Report the number promoted **alongside the number assessed**, per template, so a small result reads as a measurement rather than a shortfall. Promoting a condition to a check that cannot really fail would be worse than promoting nothing.

## Inherited Latitude

**Delegated:** which conditions to promote and to which kinds; per-template ordering; whether to split across commits; the shape of any helper you add.

**Float to the Admiral:** a template partitioning materially differently from 9/19; needing a new check kind; wanting to change engine behaviour in `checklist_engine.py`; making the `validate_spine.py` wiring blocking if it reds the suite.

## File Ownership

`skills/*/templates/*.json` are **yours alone** this wave — including `skills/commander/templates/COMMANDER_SPINE.template.json`. `w3-basis` reads that file and will float to the Admiral rather than edit it, so you will not collide. `scripts/validate_spine.py` is also yours. Your notes file is `.agent-work/w3-promote/notes-1.md`.

**Compact-format JSON:** edit these templates as **raw text, surgically**. Never round-trip through `json.load`/`json.dump` — it reflows the whole file and destroys blame. Re-validate with `json.load` afterwards.

## Pre-empted Steps

Established, cite rather than re-derive: the three-bucket partition and its N=3 provenance; the `validate_spine.py` exit-1 measurement on the shipped template; the human's ruling that no census mission runs and the partition is extrapolated. All settled — your job is to promote, not to re-measure the 19.

## Workspace

- **Worktree:** `/home/tommy/projects/569-w3-promote` — provisioned for you, verified distinct.
- **Branch:** `epic-569/w3-promote`, created by `git worktree add -b epic-569/w3-promote /home/tommy/projects/569-w3-promote origin/main`
- **Base commit:** `135c34eb` — `origin/main`, **verified green by the Admiral in a clean detached worktree: 3729 passed, 9 skipped, 0 failed** in 213.98s. A real measurement at that exact SHA, not a recollection. If your `git log -1` shows something else, stop and say so.
- **Spine:** `/home/tommy/projects/569-w3-promote/.agent-work/w3-promote/spine.json` — already instantiated from `COMMANDER_SPINE.template.json`.
- **Result artifact:** `.agent-work/w3-promote/RESULT.md` (relative to your worktree).
- **Working notes:** `.agent-work/w3-promote/notes-1.md` — sole writer. Name it `notes-1.md`, **never** `findings-1.md`; the harness `Write` tool refuses any basename containing "findings".

Your **first command** is to `claim` the engine lease on that spine. You scaffold nothing.

PR integration defaults to **server-side merge**. You open the PR; the Admiral merges.

**Your own spine is one of your targets.** It was instantiated from the template you are fixing, so it currently fails `validate_spine.py` on `init` and `reconcile`. Do not edit your own live `spine.json` to fix that — fix the **template**, and note that your running spine keeps the old shape. Hand-editing a bound spine is a doctrine violation and deadlocks the lease.
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
