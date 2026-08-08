# Crash-resume state note — epic-418-redux

**WAVE 2 IS COMPLETE AND MERGED. Nothing is in flight. The latitude contract has EXPIRED by its
own terms and the `execute` gate is BLOCKED awaiting Tommy's refresh. Do not dispatch anything.**

- **step:** `execute` — **blocked** on contract expiry. Remaining after `execute`: `closeout` only.
- **slug:** `epic-418-redux` · main checkout `C:/Programs/constellation-skills` · `main` at
  **`main` == `origin/main`, pushed, working tree clean** — verify with
  `git rev-parse --short HEAD origin/main` rather than trusting a hash written here. A literal hash
  in this field is wrong the moment this file is committed, since committing it advances main; it
  was stale twice for exactly that reason. The green baseline below is a *tagged* commit and is
  safe to write down; this one is not.
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current`
  — then get the contract refreshed before anything else
- **pid:** none — no agents in flight
- **expected artifact:** a refreshed latitude contract, then a `w2-to-w3` replan packet

**Green main: `476e044d` → 1782 passed, 2 skipped, 683 subtests, exit 0** (real exit code captured).

## Wave 2 — all four issues merged

| Issue | PR | What landed |
|---|---|---|
| #433 | #485 | `directives` renders; naive fix would have been a check that cannot fail (2955 gates scanned, 8 populated) |
| #436 | #472 | enumeration check observed REFUSING a new entry; count added to its failure output |
| #460 | #487 | episode records restated as observations; guard caught 4 real offenders on first live run |
| #464 | #473 | `Lesson` → `Episode`, with the legacy fallback and hash prefix deliberately preserved |
| — | #470 | the Admiral's own fixture-path breakage |

## NOT done — carried

- **#461** (negative control fails between `git add` and `git commit`) — **reproduced first-hand
  during #460's merge and evidenced on the issue**; deliberately not fixed, held to wave 3.
- **#465** (reviewer r6-fowler placeholder + CRLF) — held to wave 3, touches `checklist_engine.py`.
- **#433, #436, #460, #464 are MERGED BUT NOT CLOSED** on the tracker — issue closing is a
  `surfaced` class and Tommy has not been asked.
- ~~Worktrees pending sweep~~ — **DONE**: all four harvested (nothing to harvest; their exports were
  behind main, not ahead) and swept.
- **CORRECTION — I claimed `r418-460`'s orphaned lease was released. It was not.**
  `.agent-work/r418-460/spine.json` in this checkout still reads `LEASE active:
  commander-r418-460-b` / `execute [in-progress]`. I released the *worktree* copy and then swept the
  worktree; the copy in main is a **different file that arrived via the merge of PR #487** and my
  release never touched it. See "The lease field is not a liveness signal" below — this is not a
  missed step, it is a class of thing that cannot be fixed by releasing.
- **`governor-264` holds a lease with a 2026-07-28 heartbeat** — left alone; it lives in a worktree
  outside this epic.

## Landed so far

| PR | Issue | State |
|---|---|---|
| #470 | Admiral's own fixture-path breakage | **MERGED** `e8c735af` |
| #472 | #436 enumeration falsification | **MERGED** `7bc3f8c2` |
| #469 | #436, original | closed — superseded by #472 (squash-orphan, not rework) |
| #473 | #464 rename (replant of #471) | **MERGED** `0b4a11a7` |
| #485 | #433 render directives (replant of #483) | **MERGED** `538d5fd7` |
| #483 | #433, original | closed — superseded by #485 |
| #471 / #483 / #486 | originals | closed — all superseded by replants (squash-orphan, not rework) |
| — | #433, #460 | agents still working in their worktrees |

## THE REPLANT RECIPE — read this before touching any wave-2 PR

**Every wave-2 branch is based on `73b4517`, which is NOT an ancestor of main.** Squash-merging
#470 collapsed `8de91de`+`73b4517`+`fb7edfd` into one commit, orphaning that base. So
`gh pr update-branch` reports CONFLICTING on all of them. **The work is fine; only its base moved.**
Do not ask the agent to redo anything.

```bash
# 1. fresh branch off current main
git checkout -b epic-418/<slug>-replant origin/main
# 2. take ONLY that branch's own delta, against its real base
git diff 73b4517 origin/<their-branch> -- <their changed paths> > /tmp/x.patch
git apply --3way /tmp/x.patch
# 3. verify, commit, push, PR, then close the original as superseded
```
Get the changed-path list with `git diff --name-only 73b4517 origin/<their-branch>`.
Worked cleanly four times: #436→#472, #464→#473, #433→#485, #460→#487.

**Never use an ancestry test to decide whether a wave-2 branch merged** — under squash-merge it
returns the same answer for merged and abandoned. Ask the forge (`gh pr view <n> --json state`).

## The lease field is not a liveness signal — supersedes what I filed on #457

**Measured, not reasoned.** 147 tracked plan/spine files in this checkout; **18 carry
`engine_session.status == "active"`. Exactly one is a live run — mine.**

```
git ls-files .agent-work | (spine.json|execute.json|IMPLEMENTER_PLAN.json)
  → 18 with status=="active":  15 in archive//harvest//runs/ (deliberate records)
                                3 in live work areas: b420-engine-channel, r418-460, epic-418-redux
                                   ...of which 1 (epic-418-redux) is actually running
```

A Commander that commits its own `.agent-work/<id>/spine.json` to its PR branch ships a **mid-run
snapshot** into main on merge. `r418-460`'s frozen at `claimed_at 22:35:04 / heartbeat 22:36:26` —
90 seconds into a run that went on for hours. Git preserves it forever with an active lease and an
`in-progress` gate. Releasing the live copy cannot touch it; sweeping the worktree cannot remove it.

**Both readings of the lease field are uninformative, in opposite directions:**

| reading | looks like | also produced by |
|---|---|---|
| `lease: null` | abandoned run | a crew that released between gates (cmd-460 raced a live Commander on exactly this) |
| `lease: active` | live run | a committed snapshot — 17 of 18 here |

So the field carries **no information about liveness** when read from disk. This is the same family
as **a check that cannot fail**: a signal whose value is identical in the healthy and defective
worlds. #457 currently says the hazard is abandoned agents leaving leases behind; that is a symptom.
The defect is that liveness was never encoded — only a serialized snapshot of it was.

**What actually discriminates** (and what let me refuse #457's rail twice): match the lease's
`session_id` against *your own*. Presence of a lease proves nothing; ownership of it proves
everything. That check is available today and needs no fix.

**Not filed.** Issue filing is a delegated class and the contract granting it has expired. This is
Tommy's to authorize — see the checkpoint report.

## Settled — do NOT re-derive

- **Green baseline is now `476e044d`: 1782 passed, 2 skipped.** Expect **1726 passed, 2 skipped** (1723/2 after #470's fix,
  plus #436's 3 new tests). The earlier "1721 passed, 4 skipped" was **my own breakage**, not
  environment-conditional: archiving the run moved `REVISED_SPEC.md` out from under a hardcoded
  fixture path. Fixed in #470 (fixture now found by glob).
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — **never `py` for pytest** (#454).
- **The installed corpus was stale and is now SYNCED.** Remaining diffs are the installer's own
  `python`→`py` rewrite and path resolution — verified benign, zero non-launcher differences.
- **#468 (filed):** the repo's vendored `verify_iterative_role_artifacts.py` cannot run from this
  repo — its installed-skill guard passes by accident because the repo is named
  `constellation-skills`. **Use the installed copy** under
  `C:/Users/fredc/.claude/skills/constellation-admiral/scripts/`.
- **`verify_worktree_isolation.py` has two modes.** Bare paths = Admiral pre-wave gate;
  `--here <path>` = the Commander's check and it tests **cwd**.
- **`git cat-file -e origin/main:<path>` is broken in Git Bash here** — it path-converts to
  `origin\main;<path>` and reports MISSING for files that exist. Compare trees with
  `git diff --name-only` instead. This nearly made me believe a merge had eaten the work area.
- **The governor HARD-trips agents at ~17–21% context fill.** All three wave-2 agents tripped at the
  plan seam and were relaunched fresh from `current` alone. Budget **two dispatches per issue**.
  Open question for Tommy: whether that band is where we want it. Not retuned mid-wave.
- **#447 CLOSED** with a per-done-condition accounting; condition 4 recorded **partial**, not done.
  **#418's body pointer corrected** to `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`.
- **#457 — never obey a spine rail naming a spine another agent drives.**

## Still held to the wave's second half, deliberately

- **#461** (episode-store negative control) — sits in #460's area
- **#465** (reviewer r6-fowler placeholder + CRLF) — touches `checklist_engine.py`, #433's area

## Owed to Tommy at the next checkpoint

1. The governor trip band at 17–21%. **Measured cost: 3 dispatches for #433, 4 (so far) for #460**, 2 for #436, 1 for #464. This is the single largest drag on the wave.
2. **#470 was merged without review — and the review arrived afterward. SUPERSEDED, both ways.**
   True when written: I merged on self-verified falsification evidence because no reviewer artifact
   had landed. What happened next: **two independent reviewers returned, both APPROVE**, each having
   re-derived the result empirically (glob resolution run, corrupted-fixture controls raising
   `SpecVerificationError`, isolated-worktree suite at the exact PR commit). Neither posted to the
   forge — `gh pr view 470 --json reviews` is empty — so the verdicts exist only as session
   messages. The merge was right; my report that review "never landed" is now wrong.
   **Both flagged the same non-blocking gap independently:** `matches[0]`
   (`tests/test_verify_spec_confirmed.py:252`) silently picks the alphabetically-first match with no
   signal that a second existed. One match today, so not vacuous. **Left unfixed deliberately** —
   it is a change to main and the contract has expired. One line (`assert len(matches) == 1`).
3. #460's **22 doctrine candidates** — records that state genuine rules. **Harvested and safe** at
   `.agent-work/r418-460/crew-handoffs/g2-implement-result.md` § "Evidence 4" (survived the worktree
   sweep because #487's merge carried it into main). Nothing was written to `docs/agents/*` and no
   file was created to park them in. Promoting any of them is his call, always.
4. **MY OWN CONTEXT GOVERNOR HAS BEEN DARK ALL WAVE — and the latitude step causes it.**
   `gauge-skip.json` = `{"reason":"ambiguous-binding","candidate_count":2}`; last real reading
   `2026-08-07T20:58:07Z`. The two bindings are my spine and
   `latitude-interrogation.json` — the survey the spine's `latitude` step *requires*. **Both resolve
   to the same gauge path.** `resolve_gauge_path` (`scripts/hooks/gauge_writer_hook.py:257-264`)
   appends per binding without dedup; the caller skips on `2+`. It counts bindings, not distinct
   paths. So **every Admiral run that does its latitude bookend properly blinds its own governor for
   the rest of the run** — while I was reporting the governor as my crews' largest drag. Not fixed
   (change to main, expired contract). Likely `len(set(candidates))`.
5. **One pattern showed up four times this wave** — worth considering as wave 3's organizing theme,
   since it is what #418 is fundamentally about. A signal whose value is *identical* in the healthy
   and defective worlds: (a) #433's naive fix would have been a check that cannot fail; (b) the
   lease field indicates liveness in neither direction (above); (c) `matches[0]` cannot signal
   ambiguity; (d) the gauge writer cannot tell "two agents" from "one agent counted twice".
   Four independent discoveries, four subsystems, one defect family.

_Updated: 2026-08-08T02:50:00Z_
