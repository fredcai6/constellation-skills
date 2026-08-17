# Launch Order: `cmdr-567-d2` — sunset the workbench teaching half, keep the templates (#565, with #561)

Epic **#567** ("the door is the interface"), wave 2, lane **D2**. You are one of five lanes
(D1, D2, E, F and H). You start cold: everything you need is pasted below, not linked.

## Mission

Issue **#565**: *sunset the workbench skill — it teaches what the door's tools now carry,
which is why the CLI keeps growing back.* Plus **#561** (`CREW_CONTEXT.md`'s Python Invocation
section is wrong on the Linux dev host).

You merge **first** in this wave, because lane D1's regrowth guard must be authored against a
tree where the teaching half is already gone.

**The skill splits cleanly in two, and the issue measures it:**

| half | lines | files |
|---|---|---|
| **redundant — the teaching half** | **282** | `references/checklist-engine.md` 181, `references/status-model.md` 58, `SKILL.md` 43 |
| **not redundant — the artifact half** | 119 | `templates/CONSTELLATION_FEEDBACK.template.md` 29, `templates/DEFAULT.template.json` 29, `templates/STATE_NOTE.template.md` 18, `templates/WORKFLOW_CLOSEOUT.template.md` 43 |

(The Admiral re-measured the teaching half at **289** lines on `f05a3d78`; the issue's 282 is
from an older commit. Neither number is the deliverable — report what you actually removed.)

**Delete the teaching half. Deregister the skill. Do not move a single template.**

## Prior-Wave Verdicts (pasted)

**The human's ruling on the template home, which is the question #565 itself calls the
blocking one.** He was given three options — rehome to `skills/_shared/templates/`, rehome each
template to its primary reader, or keep the directory as a template-only package — and chose to
**keep the directory**. His reasoning, as recorded in the contract:

> Rehoming to `skills/_shared/templates/` would mean extending the installer's `_shared`
> fan-out from references to templates — **new mechanism spent to remove old text** — and
> moving each template to its primary reader churns every referencing path, including the
> Admiral spine's own `execute` precondition, which names `STATE_NOTE.template.md` by path.

Measured facts behind that ruling, so you do not re-derive them: `install_constellation.py:19`
and `:242` treat `_shared` as a **reference** bucket only; `:320` skips underscore-prefixed
directories; and the project's tracked `.agent-work/templates/` overlay carries **113** files
and was reconciled from repo source earlier today.

**Wave 1's four lanes all merged green** — PR #623 (per-dispatch spine identity, `spine_bind`),
#621 (ExternalBackend refuses a spineless success, #432), #620 (the Stop hook outranks the
context advisory, #595), #622 (`finish_work` and lease-release-on-archive, #574/#552) — and
`origin/main` is at `f05a3d78`, green. Lane A's `spine_bind` is what makes #565's premise true:
the door's tools now genuinely carry what the teaching half teaches.

**One caution from wave 1 that lands directly on your mission.** A reinstall earlier today
reported 8 templates needing reconciliation, and the Admiral wrongly called one a false
positive, having inferred the freshness check's behaviour from its output instead of reading
it. Corrected in writing after reading `_normalized_hash` at source. Your mission touches the
installer's view of a skill directory: **read the three scripts that name workbench, do not
infer them from their output.**

## Pre-Rulings

Ruled in advance. Each is overridable if evidence contradicts it — **say so when you override
one**, in your return.

### Mission-specific

- `decision:workbench-stays-a-template-package` — **settled/human.** The four templates stay
  at their current `skills/workbench/templates/` paths. Delete the teaching half, deregister
  workbench as a skill, move **nothing**. `@grade: settled/human · leans d2`
- `decision:establish-the-door-carries-it` — #565's second work item is a **claim, not an
  assumption**: that the door's tool descriptions carry what the two references carried — the
  verbs, the two spine types, evidence shape, refusal semantics, and the status vocabulary.
  Establish it by reading both, and **name anything the door does not carry**. If something is
  genuinely lost, that is a float, not a silent deletion.
  `@grade: settled/doctrine · leans d2`
- `decision:three-scripts-must-still-pass` — `install_constellation.py`,
  `verify_skill_registered.py` and `measure_overread.py` each name the workbench skill
  directly. Deregistration must satisfy all three, **checked rather than assumed**. If a
  supported deregistration path does not exist and the change needs installer code, float it —
  new installer mechanism to remove old text is exactly the trade the human declined on the
  template question. `@grade: settled/doctrine · leans d2`
- `decision:prove-every-spine-still-starts` — before you claim done: an **Admiral**, a
  **Commander** and an **Explorer** spine each instantiate and reach their first gate in a
  fresh process, and `STATE_NOTE.template.md` still resolves for the Admiral spine's `execute`
  precondition (`verify_state_note.py <work-id>` is the check, and it exits 0 today). A sunset
  that breaks every Admiral run at `execute` is worse than no sunset.
  `@grade: settled/doctrine · leans d2`
- `decision:workbench-clauses-are-yours` — 2 of the epic's 15 `CLI fallback` clauses live in
  your files (`skills/workbench/SKILL.md`, `references/checklist-engine.md`). You remove them
  by deleting their files. Lane D1 takes the other 13 and will not touch your tree.
  `@grade: settled/doctrine · leans d1, d2`

### Standing, this epic

- `decision:reduce-complexity` — judge a change by whether it reduces complexity, and in
  particular by the human's test for trades of this kind: **does this choice reduce work on
  agents by moving it into mechanisms?** Removing a redundant path counts even when your own
  line count rises. Do not over-engineer; note simplification opportunities rather than
  building for them. `@grade: settled/human · leans all lanes`
- `decision:no-net-deletion-rule` — there is **no** rule that every lane must end with
  something deleted. It was withdrawn on 2026-08-17 by the human, who never set it: *"I never
  said that every lane needs to end with something deleted, or at least never intended that."*
  Wave 1 enforced it on four launch orders under his name and it was the Admiral's
  mis-recording. Do not reintroduce it, and do not pad a return with a deletion to satisfy it.
  `@grade: settled/human · leans all lanes`
- `decision:honest-null-is-complete` — a measured negative on the stated question is a
  complete, successful deliverable, reported with the same rigor as a win.
  `@grade: settled/human · leans all lanes`
- `decision:no-issue-filing-mid-run` — **you file no issue.** Stage every triage candidate as
  a file under `.agent-work/567-d2/triage-candidates/`. The human's reason: *"we've been
  ballooning out tracking."* At epic closeout each candidate is paired onto an **open** issue
  as a comment, or recorded as an episode. A lane that wants to file is not floating a
  decision — the answer is already ruled. `@grade: settled/human · leans all lanes`
- `decision:no-doctrine-promotion` — you may not promote an observation into `docs/agents/*`.
  That is the human's call. Record the observation and say so.
  `@grade: settled/project · leans all lanes`
- `decision:records-are-not-instruction` — `docs/superpowers/plans/**` and
  `docs/superpowers/specs/**` are **historical records**. Editing them to make a sweep count
  come out right falsifies the record. Leave them, and say in your return that you did.
  `@grade: settled/doctrine · leans all lanes`
- `decision:in-session-hook-observation-is-not-evidence` — hooks execute from the **main
  checkout** regardless of worktree (`CLAUDE_PROJECT_DIR` resolves once at session launch,
  #269). Validate engine, door or hook behaviour in a **fresh process** with explicit paths. An
  in-session observation after an edit is struck from any gate that would accept it.
  `@grade: settled/project · leans all lanes`
- `decision:map-index-is-admiral-owned` — **do not regenerate or hand-edit `map/INDEX.md`**
  (#544: it is generated, committed and freshness-tested, so every parallel branch stales it
  and two regenerating lanes conflict by construction — in wave 1 it blocked three of four
  lanes plus a concurrent session in one afternoon). Your branch is accepted green **except**
  `tests/test_code_map.py::MapTreeFreshnessTests`. The Admiral regenerates once on the final
  merged main and re-verifies there. `@grade: settled/doctrine · leans all lanes`
- `decision:no-fork-for-design` — if you dispatch any helper for candidate generation or
  design, use a **fresh** agent, never a `fork`. A fork inherits its dispatcher's full context
  and therefore believes it *is* the Commander: in wave 1 a lane-G fork rewrote its
  sole-writer notes file in the first person and drove its `spine.json` under the identical
  lease id, and lane G halted a delivering run believing its worktree was compromised. Your
  process has no `Agent` tool, so a helper means a fresh `claude -p` through Bash — which is a
  genuinely cold process and therefore the better instrument anyway.
  `@grade: settled/doctrine · leans all lanes`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it
with the same rigor as a win, with the evidence that establishes it. Do not substitute your own
judgement for a measurement your mission calls for and present the result as measured — a lane
that does that has failed while appearing to succeed.

## Inherited Latitude

| Class | Your disposition |
|---|---|
| Implementation choices inside your own files | **yours** |
| How workbench is deregistered | **yours** |
| Replacement wording where a reference pointed into the teaching half | **yours** |
| Moving any template | **forbidden** — settled by the human |
| New installer mechanism | **float** |
| Architecture / structural change | **float to the Admiral** |
| Scope change (issue added, dropped, re-scoped) | **float to the Admiral** |
| Production defaults / user-visible behaviour | **float to the Admiral** |
| Issue filing | **ruled: none.** Stage candidates locally |
| Promoting an observation into `docs/agents/*` | **forbidden** — human's call |
| Fix-now triage inside your own worktree | **yours** |
| Spend / model tier | **yours** within the budget below |
| Anything that fits no class above | **float**, with one line on why it fit none |

Float by writing your question into your return artifact **and** ending your turn with it
stated plainly. The Admiral answers and continues you. Asking up is always sanctioned.

## File Ownership

**You are the sole writer this wave of:** `skills/workbench/**`; `scripts/install_constellation.py`; `scripts/verify_skill_registered.py`; `scripts/measure_overread.py`; `docs/agents/CREW_CONTEXT.md`.

**Fenced — do not edit, another lane owns it this wave:**

| Path | Owner |
|---|---|
| `skills/**` **except** `skills/workbench/**`; `specs/**`; `scripts/init_work_area.py`; `scripts/collect_feedback.py`; `scripts/agent_work_root.py`; `docs/**` **except** `docs/agents/CREW_CONTEXT.md` and **except** `docs/superpowers/**`; `tests/test_retirement_guard.py` plus any new guard test file | lane D1 |
| `scripts/mcp_spine_server.py`; `episodes/**` | lane E |
| `scripts/run_crew.py` | lane F |
| `scripts/checklist_engine.py` | lane H |
| `map/INDEX.md` | the Admiral |
| `.agent-work/epic-567-door/**` except your own results file | the Admiral |

If your mission genuinely needs a file another lane owns, **float it**. Wave 1 had two lanes
write one path and it cost a merge.

Your working-notes file, sole writer, is `.agent-work/567-d2/notes-1.md`. Name it exactly that —
**never** `findings-<n>.md`: the harness `Write` tool refuses any path whose basename contains
"findings", a guard aimed at unprompted report-dumping that cannot tell this file was
deliberately assigned. Three agents hit it in one epic and each worked around it with a shell
heredoc. The guard is not ours to change; the word is.

## Workspace

- **Spine (yours, already provisioned):**
  `/home/tommy/projects/constellation-skills/.worktrees/567-d2-workbench-sunset/.agent-work/567-d2/spine.json`
- **Worktree:** `/home/tommy/projects/constellation-skills/.worktrees/567-d2-workbench-sunset`
- **Branch:** `feat/567-d2-workbench-sunset` · **Base commit:** `f05a3d78`
- **Created by:** `git worktree add -b feat/567-d2-workbench-sunset .worktrees/567-d2-workbench-sunset f05a3d78`
- **Main freshness verified before dispatch:** `origin/main` at `f05a3d78`, full suite **3352
  passed, 6 skipped, 1219 subtests passed, 0 failed, 0 SUBFAILED** on Linux in a clean detached
  worktree.
- **Merge position:** this lane merges **first** in the wave. You merge first because lane D1's guard must be authored against a tree where the workbench teaching half is already gone.

Your first command is to `claim` the engine lease on the spine above.

**Your door is bound to your own spine, and this is the first wave where that is true.** Call
the `spine_lease` MCP tool with `action=claim, claimed_by=commander, worktree=.` — no CLI, no
`spine_bind`, no environment surgery. Your process was launched by
`run_crew.py --backend cli --spine`, which assigned `SPINE_FILE` to your spine and an
assignment-keyed `SPINE_SESSION` into your environment, and started you with your worktree as
cwd. Your door therefore resolved to your own spine at startup. This was measured before the
wave launched, not assumed: a door launched this way anchors to its own worktree and returned
`spine_status` and `spine_lease claim` cleanly.

**This matters to your mission and to the epic.** The epic's definition of done includes *"a
dispatched crew drives its own spine through the door end to end."* You are that crew. Drive
every gate through the MCP verbs. If you ever find yourself reaching for
`scripts/checklist_engine.py` on the command line, stop and float it — you have found either a
verb gap or a defect, and either one is worth more to this epic than the workaround.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not
a local merge that would diverge your worktree from main).

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` is resolved
once, at session launch, so a Commander in an isolated worktree still executes the **main
checkout's** hook code against the **main checkout's** state, even while every git operation
stays correctly fenced (#269). If your change touches anything the hooks read, you cannot
validate it from inside the process that would run the unchanged code. Validate in a **fresh
process** with explicit paths — never a fixture that hand-injects the value you are trying to
prove the harness delivers.

## Inherited Context

- **A bare `cd` may not persist between Bash calls.** Wave 1's lane A ran 47 minutes and wrote
  **zero bytes** stuck on exactly this; its dying words were *"the bash cwd resets between
  calls."* Use a **single compound call** — `cd /abs/path && <command>` — or absolute paths
  everywhere. Your process's cwd starts in your own worktree.
- **The merge gate is the full suite green on Linux**, run in a **clean detached worktree of
  your branch**, never in your working copy. Wave 1's Admiral authored that exact defect four
  times: *a check that runs against your own working copy is not a check on the world.* The
  shape is `git worktree add --detach <tmp> <your-branch-sha>` then run the suite there.
  Windows CI is red on a pre-existing ~122-failure path-casing baseline and is **not** the
  yardstick (#575 is deferred).
- **A failing subtest is now greppable.** The repo-root `conftest.py` (PR #626) restates each
  failed subtest as a line beginning `FAILED `, with a `[subtest …]` marker. Before that,
  `grep '^FAILED'` returned nothing for a failing subtest, because `SUBFAILED` cannot match
  `FAILED ` — the next character is `(`, not a space — and wave 1's Admiral shipped a merge
  gate with that hole and reported "120 tests fixed" from an empty failure list. Grep for
  `^FAILED` and trust it.
- **`episodes/` has exactly one write path**, `scripts/apply_episode_delta.py`, always with
  `--store-root episodes`. Never hand-edit it. To reword an assertion use its
  `restate-assertion` op. If your run touches the store, the order is **write → `git add` →
  suite → commit**: `test_canon_episode_store_untouched` is worktree-vs-index only, so running
  the suite between the write and the stage trips it with a message that reads like store
  corruption.
- **The episode-observation guard cannot tell a past-tense verb from an imperative** ("read",
  "grep"). Rephrase to remove the bare verb; **do not** add to the exception list, which
  already carries 11 entries across five prior runs.
- **GitHub has been returning intermittent 503s all day.** `gh pr create` and `gh pr merge`
  need retrying — up to six attempts in wave 1. **Gate each retry on whether the world
  actually changed** (`git rev-parse origin/main`, `gh pr view`), never on the command's own
  output.
- **A concurrent session works this repo.** `origin/main` moved under wave 1's Admiral twice,
  once breaking it with 9 Linux failures from a pair of individually-green PRs. Check
  `git rev-parse origin/main` before you assume your base is current. Do **not** touch
  `.worktrees/issue-610-stand-up-work-area` — not yours.
- **`.agent-work/` is tracked deliberately** (11,188 files). Your run artifacts, verdict and
  triage candidates are committed on your branch and reach `main` at merge.

## Pre-empted Steps

- **Work-area stand-up is done.** Your worktree, `.agent-work/567-d2/`, and `spine.json`
  were provisioned by the Admiral per `skills/_shared/stand-up-work-area.md`. You do not
  scaffold, and your `init` step means exactly one thing: claim the lease.
- **The `--here` arrival check is retired as an instruction** (#610). Do not run
  `verify_worktree_isolation.py --here`. Isolation was gated by the Admiral across all five
  worktrees before dispatch: `worktree isolation verified: 5 distinct worktrees`, exit 0.
- **Your door-binding was pre-verified** — see Workspace.
- **The wave's replan transition is done and verified.** `.agent-work/epic-567-door/transitions/w2/`
  carries the `REPLAN_INPUT`/`REPLAN_RESULT` pair, `admiral-prelaunch` exited 0, and
  `CURRENT_TRUTH.md` plus `WAVE_REVIEW.md` are rendered from it. You do not replan; you deliver.

## Data Locations

Everything your mission needs is tracked and present in your worktree. There are no untracked
inputs. The main checkout is `/home/tommy/projects/constellation-skills` — readable if you need
it, **never** writable by you.

## Local Unknowns

Named so you do not mistake them for settled:

- Whether deregistering a skill that still ships templates is a supported state in
  `install_constellation.py`, or needs a code change there.
- Whether the tracked `.agent-work/templates/` overlay (113 files) references the teaching half.
- Whether #482's workbench-vs-reviewer dogfooding collision disappears with the teaching half
  or survives it.

## Budget

- **Model tier (required):** **Sonnet**.
- **Compute/time, session-window:** One focused session. The template question is already ruled, so no design work remains — the care goes into proving nothing broke.

## Stop Conditions

Stop and return when: scope is exceeded; a decision outside your inherited latitude is needed;
budget is crossed; the evidence your mission demands is impossible to obtain; or you need
**context this order does not cover and cannot safely proceed without** — return-and-query the
Admiral, which answers and continues you. Asking up is always sanctioned and is never counted
against you.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token
cap, not a share of your window, so a Commander that has loaded its skill, references,
templates and this order can be over it on turn one having done no work. The engine refuses
only the verbs that BEGIN work at a gate (`start`, `reopen`), and only until a refresh-request
exists for that gate. The legal sequence is: **attach the refresh-request against the current
why-record, then `start`, then do the work.** Attaching first sends the guard down its release
path; starting first is what gets refused.

Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as an instruction to
`advance --why` and hand off on turn one. A fresh agent that closes its gate before doing the
gate's work produces an infinite handoff chain — each successor arrives over the band, reads
the same line, and hands off again, with the gate's postconditions never met and no deliverable
ever written. Hand off when you have actually spent the context, not when you inherit the
reading.

**Do not end your turn with an engine gate open.** The Stop hook refuses it and is
authoritative over the context-trip advisory — wave 1's lane C settled that precedence (#595).
The sanctioned exit is the engine's `block` verb (`spine_halt` with `action=block`) naming what
you cannot satisfy and the next action.

## Return Shape

Write your result to
**`.agent-work/epic-567-door/results/lane-d2-RETURN.md`** — that exact path, inside
your own worktree, committed on your branch. **Not** `RETURN.md` at your worktree root: that
path is tracked, and in wave 1 four lanes collided add/add on `main` the moment the first one
merged.

Write the artifact and send your verdict **before** going idle. An idle notification with no
artifact reads as stalled, not done — the Admiral judges completion from what you produced, not
from a message that arrives after you have gone quiet.

Include, in this order:

1. **Verdict** — delivered, or an evidenced honest null.
2. **What you deleted** — file by file, with line counts, and the total against the 289 the
   Admiral measured.
3. **The door-carries-it establishment** — what the two references taught, where the door
   carries each of those things, and **anything it does not**.
4. **Deregistration** — how it was done, and the output of all three scripts that name the
   skill.
5. **Every spine still starts** — Admiral, Commander and Explorer each instantiated and
   reaching their first gate in a fresh process, plus `verify_state_note.py` exiting 0, with
   the commands and their output. Plus #561: before and after.
6. **Suite result** — the full suite on Linux in a **clean detached worktree of your branch**,
   with the tally and the `^FAILED` grep output. `MapTreeFreshnessTests` may fail; nothing else
   may. State the commit sha you verified.
7. **Touched paths** — every file you wrote, so the Admiral can sequence merges. Name any file
   you wanted to touch but did not because another lane owns it.
8. **Map impact** — whether your change touches indexed source. Do not act on it.
9. **Triage candidates** — as files under `.agent-work/D2/triage-candidates/`, listed in
   the return. None filed as issues.
10. **Workflow feedback** — what helped, what got in the way, and **your own mistakes**. Wave
    1's single most useful output was a lane's honest account of its own errors; the Admiral's
    was its account of authoring the epic's own defect four times while holding the doctrine.
11. **PR** — opened against `main` from `feat/D2-567-d2`, with the number and the head
    sha.

On Windows, write the PR body to a temp file and use `gh pr create -F <file>` — never a heredoc
or a PowerShell here-string for a PR body. You are on Linux, so a heredoc is fine.
