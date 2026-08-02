# Launch Order: `pre-b — the Commander-loaded pre-change arm`

Small, bounded, single-experiment dispatch. **Not** a full Commander run — no spine, no design-it-twice, no cold panel. Run the existing rig with one change, report, PR.

## Mission

Capture **PRE-B**: the same five measured tasks as the #299 baseline, at the same f1Brainz pin, with the **Commander explicitly invoked**.

The #299 arm (call it PRE-A) measured **generic agents** — zero `Skill` invocations across five runs, confirmed robust by the #331 probe under a second brief. Tommy's ruling: *"we should explicitly be calling commander in these tests."* PRE-A is not wrong; it answers a different question, and it answers it cleanly. **PRE-B is a second arm, not a repair of the first.**

## THE CONSTRAINT THAT MATTERS MOST — read it twice

**PRE-B's ordering measure is NOT comparable to PRE-A's.**

PRE-A measured an agent under **no map instruction at all**. Forcing the Commander load also forces the two map-first imperatives to fire — `COMMANDER_SPINE.template.json:22` (context: *"Read the current map (packets, overlays, decision anchors) for the area the ask touches"*) and `:48` (plan: *"Map-first: BEFORE authoring execute.json, produce a mission frame from the current map"*). That is a different treatment, deliberately.

**Three arms, two series. PRE-B pairs with the POST arm. It does NOT pair with PRE-A.**

State this prominently in your record — in the title area, not a footnote. Anyone who later reads the three arms as one series will draw a conclusion from a comparison that was never valid, and **once the data exists and the runs are gone, that error is undetectable.** Guarding against it is part of the deliverable.

## TIME-SENSITIVE — why this runs now

Issue #304 will land the map-input contract and, once installed, changes the corpus. **PRE-B must complete before that happens**, or there is no pre-change arm for the paired comparison, ever.

Do not optimize, do not gold-plate, do not expand scope. Run the rig, capture five, report.

## The corpus question — settled, and it is why no pinned install is needed

Issue #332 resolved during the #331 probe: **the global corpus shadows the project one.** Both register (every constellation name appears twice in `system/init`) but `~/.claude/skills` is what **serves**. Installing a pinned corpus into `<worktree>/.claude/skills` **does not deliver it.**

So **do not attempt a pinned worktree install.** PRE-B measures **the corpus as actually installed**, which is the honest production condition rather than a synthetic pin. The global build is currently `source_commit 74953936` (2026-07-25) — behind main, but genuinely **pre-#304**, which is all this arm requires.

**Fingerprint the global corpus before the first run and again after the last**, and record both. Measured at dispatch: **19 `constellation-*` skills, concatenated `SKILL.md` sha256 prefix `fcb6863163c97273`.** If it changes mid-window, the arm is compromised — **stop and report rather than pooling runs across two corpora.**

**Verify the treatment actually loaded, per run.** The #331 probe found the discriminator: Claude Code prefixes loaded skill content with a literal `Base directory for this skill: <absolute path>` line. It names the serving copy outright, is emitted by the harness rather than planted, and cannot be defeated by truncation. **A run with no Commander load is a failed capture, not a data point** — that is the entire difference between this arm and PRE-A, and an unverified treatment is worse than no arm because it looks valid.

## Method — one change from PRE-A, and everything else held

- **Tasks**: the same five, from the frozen `issues.frozen.json` — **#690, #688, #698, #716, #704**. Do not re-cut. Read the briefs from the snapshot, never live.
- **Pin**: f1Brainz `3541d2929b19de37107ae13e56776b7162d07255`. Per-run pinned worktree, **absolute paths only**. Sweep them after.
- **Model**: `claude-opus-5`, all five. The measured configuration must be the standard one.
- **The one change**: the brief instructs the subject to load `constellation-commander` and drive its spine, stopping after the **plan** step — mission frame authored, `execute.json` authored, then return. That is the same truncation point as PRE-A (plan stage) and it is **after** both map-first imperatives fire.
- **Plan-stage only. Nothing lands in f1Brainz.** No implement, no commit, no push, no PR, no issue comment there. Read-only.
- Do **not** tell the subject it is being measured, beyond what the Commander invocation itself requires.

**Reuse the frozen instruments unmodified**: `extract_ordering.py` (with its 33-check self-test and real-transcript fixture), `verify_capture.py`, and the rubric at `a226642b`. **Do not edit the rubric.** If it does not fit PRE-B, say so in the record and leave it alone — a rubric changed after an arm exists grades that arm.

## What to record per run

Everything PRE-A recorded, plus the treatment check:

- Full tool-call transcript, same archive layout as `runs/run-<N>/`.
- **Treatment verification**: did the Commander load, which copy served it (`Base directory for this skill:` evidence), and at which tool-call index.
- Ordering measure from the frozen extractor: first `docs/architecture/*` index, first `src/*` index, `map_before_src`. Absent reads recorded with the existing distinct literals — **`NO-MAP-READ` / `NO-SRC-READ` are findings; `NOT-CAPTURED` means the instrument failed. Never collapse them.**
- **The discriminated measures**, which are the ones that matter — PRE-A's addendum established them and they are what PRE-B has to be comparable to on the POST side: bootstrap-time vs orientation-time map read; whether the run **returned** to the map after starting source; map-sourced cues cited in the plan; src precision (files opened vs files named in the plan).
- Claimed seam, verbatim, for blind grading.
- Wall-clock and token cost.

**Grading**: a separate agent that has never seen this launch order and does not know which task is the negative control (#704). You do not grade your own runs.

## Honest-null clause

A measured negative is a complete, successful deliverable. **If the Commander-loaded arm orients no better than PRE-A did, that is a real and important result** — it would mean the pathless map-first imperatives do not produce orientation either, which sharpens #304 rather than defeating it. Do not shade the capture toward a result. You are building the instrument, not the answer.

Scoped nulls: report *"this arm at n=1 per task showed X"*, never *"map-first does not work."*

## Stop conditions

- The global corpus fingerprint changes mid-window.
- A run completes without a verified Commander load (report it; do not silently retry until one works — **retrying until you get the result you want is not measurement**; if you retry, record every attempt).
- A subject attempts to push, merge, or comment on f1Brainz — kill it, log it, report.
- The rubric does not fit and you are tempted to edit it.
- You need context this order does not cover — **return-and-query the Admiral; asking up is always sanctioned.**

## Workspace

```
C:/Programs/constellation-skills-wt/e298-preb
branch: epic-298/pre-b
base:   857601d  (origin/main)
```

First command, from inside it: `py scripts/verify_worktree_isolation.py --here "C:/Programs/constellation-skills-wt/e298-preb"` — must exit 0, paste the output.

**Do not touch `C:/Programs/constellation-skills`** — it holds uncommitted work of Tommy's. **Two commanders are live** in `constellation-skills-wt/e298-304` and `e298-309`. Never enter either.

## Platform notes

- `py` is 3.12.13 but has **no pytest**; `python` is 3.14.3 with pytest 9.0.2. Run tests with `python -m pytest`. **A local green is never a merge gate** — gate on the CI check exit code read at source, **and confirm the status reads `pass`, not merely that the command exited 0.** `gh pr checks` has been observed exiting 0 on a **pending** check.
- Write files with explicit `encoding='utf-8', newline='\n'`.
- PR body: write to a temp file, `gh pr create -F <file>`. Heredocs and PowerShell here-strings fail for PR bodies.
- **Backticks inside double-quoted shell strings are executed and silently drop words.** Use `--body-file` for anything with code formatting. The Admiral did this today, in a warning about this exact hazard.
- Absolute paths for `git worktree add`, always.
- Capture detached, not in a foreground tool call: the #331 probe lost a transcript when the parent returned first and killed the pipe-drain threads mid-line at a buffer boundary while the subject kept running.

## Latitude

`gh issue create/comment/close` on `fredcai6/constellation-skills` is pre-cleared — **file findings to the tracker directly, never bank them worktree-locally.** Any `gh` write against `fredcai6/f1Brainz` is **not** cleared. Merge is **not** delegated for this arm: open the PR and hand it to me. The Admiral merged past a commander's hold once already this epic and stranded its best artifact; this one comes to me deliberately.

## Return shape

Deliver your artifact and verdict **before** going idle — an idle notification with no artifact reads as stalled, not done.

1. Verdict: arm captured, or honest null with what blocked it.
2. **Treatment verification per run** — Commander loaded, which copy, at what index. This is the arm's reason to exist.
3. Global corpus fingerprint before and after.
4. Per-run ordering + discriminated measures + claimed seam + rubric score + cost.
5. **The non-comparability statement**, prominent.
6. Confirmation nothing landed in f1Brainz — and note that a worktree-scoped `git status` does **not** prove it. The load-bearing evidence is zero `Write`/`Edit`/`NotebookEdit` calls and zero forbidden git/gh operations across every transcript.
7. Triage candidates, filed, with numbers.
8. Workflow feedback — blunt.
9. `verify_worktree_isolation.py --here` output.
10. PR number and its CI check exit code **and status text**, read at source.
