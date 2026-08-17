# Launch Order: `cmdr-567-h` — issue #442, the rail and the HARD refusal read badly to the agent they are aimed at

Epic **#567** ("the door is the interface"), wave 2, lane **H**. You are one of five lanes.
You start cold: everything you need is pasted below, not linked.

## Mission

Issue **#442**: the engine's RAIL banner and its HARD refusal remedy read badly to the agent
they are aimed at. Agents read the banner as a possible prompt injection and discount the
instruction it exists to deliver.

Make a cold agent — no corpus loaded, shown only the rail line and a HARD refusal — able to
state what it is being asked to do, and do it.

**How this serves the epic.** The epic's intent is one interface for agents: the MCP door.
An interface whose own instruction text is discounted by its reader is not an interface. Every
other lane this wave removes a redundant path; you make the surviving path legible.

## Prior-Wave Verdicts (pasted)

Wave 1's lane C owned this file and was **fenced off your exact target text**, so it is
unchanged and waiting for you. Lane C's return, verbatim:

> ### Not delivered (fenced out): #442's target text — `scripts/checklist_engine.py` (Lane A's file this wave)
>
> **Unchanged, both frozen per the file's own comment ("do not paraphrase... measurement precondition for #145"):**
> - RAIL banner (`_RAIL_STRINGS["early"]`): `"Work the engine never saw did not happen. Run the step's checks, then \`attest\` and \`advance {id}\`."`
> - HARD refusal remedy (`_refresh_attach_hint`): `"attach {gate} --type refresh-request --field seam={gate} --field why_ref={why_id}"`
> - (Adjacent, also unedited: the context-trip SOFT advisory's own wording, `_trip_advisory`: `"you've used most of your context. Unless you're basically done, hand off here at {gate} rather than pushing through (advisory — decline with a reason if you're nearly done)."`)

Lane C **did** settle the neighbouring question, and you must not reopen it. Its delivered
change (PR #620, merged) established that **the Stop hook outranks the context-trip
advisory** — that precedence is now written down in `scripts/hooks/spine_rail.py`
(`_mid_flight_reason`) and in `skills/commander/references/crew-dispatch.md`. Issue **#595**
is delivered. Do not re-litigate which advisory wins.

Lane C also raised, and never settled, the uncertainty you inherit: **whether a cold-agent
readability measurement fits inside a Sonnet lane's budget.** That is your first gate's
question, not a rhetorical one.

## Pre-Rulings

- `decision:reduce-complexity` — judge a change by whether it reduces complexity, and in
  particular by the human's test for trades of this kind: **does this choice reduce work on
  agents by moving it into mechanisms?** Do not over-engineer; note simplification
  opportunities rather than building for them.
  `@grade: settled/human · leans all lanes`
- `decision:honest-null-is-complete` — a measured negative is a complete, successful
  deliverable, reported with the same rigor as a win. If you measure that the current wording
  already reads correctly to a cold agent, say so with the evidence and stop.
  `@grade: settled/human · leans all lanes`
- `decision:no-issue-filing-mid-run` — **you file no issue.** Stage every triage candidate as
  a file under `.agent-work/567-h/triage-candidates/`. The human's reason: *"we've been
  ballooning out tracking."* At epic closeout each candidate is paired onto an **open** issue
  as a comment, or recorded as an episode. A lane that wants to file is not floating a
  decision — the answer is already ruled.
  `@grade: settled/human · leans all lanes`
- `decision:no-doctrine-promotion` — you may not promote an observation into `docs/agents/*`.
  That is the human's call. Record the observation and say so.
  `@grade: settled/project · leans all lanes`
- `decision:frozen-strings-may-change-but-not-silently` — the file's own comment says *"do not
  paraphrase... measurement precondition for #145."* That forbids **silent** rewording, not
  all rewording: the whole point of #442 is that these strings read badly. You may rewrite
  them. You must state, in your return, exactly what changed and why the #145 measurement
  survives it. If you conclude the comment genuinely forbids the change, that is a float, not
  a unilateral stop. `@grade: guess · leans h1 · settle: read the #145 comment and its
  surrounding test at source before deciding`
- `decision:in-session-hook-observation-is-not-evidence` — hooks execute from the **main
  checkout** regardless of worktree (`CLAUDE_PROJECT_DIR` resolves once at session launch,
  #269). Validate engine or hook behaviour in a **fresh process** with explicit paths. An
  in-session observation after an edit is struck from any gate that would accept it.
  `@grade: settled/project · leans h1`
- `decision:map-index-is-admiral-owned` — **do not regenerate or hand-edit `map/INDEX.md`**
  (#544: it is generated, committed and freshness-tested, so every parallel branch stales it
  and two regenerating lanes conflict by construction — in wave 1 it blocked three of four
  lanes plus a concurrent session in one afternoon). Your branch is accepted green **except**
  `tests/test_code_map.py::MapTreeFreshnessTests`. The Admiral regenerates once on the final
  merged main. `@grade: settled/doctrine · leans all lanes`
- `decision:no-fork-for-design` — if you dispatch any subagent for candidate generation or
  design, use a **fresh** agent, never a `fork`. A fork inherits its dispatcher's full context
  and therefore believes it *is* the Commander: in wave 1 a lane-G fork rewrote its
  sole-writer notes file in the first person and drove its `spine.json` under the identical
  lease id, and lane G halted a delivering run believing its worktree was compromised.
  `@grade: settled/doctrine · leans all lanes`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it
with the same rigor as a win. Specifically: if the cold-agent measurement does not fit your
budget, say so with what you tried and what it would cost — do **not** substitute your own
judgement of the wording and present it as a measurement. #442's acceptance criterion
explicitly demands real agents rather than author judgement, and a lane that quietly swaps in
self-assessment has failed while appearing to succeed.

## Inherited Latitude

| Class | Your disposition |
|---|---|
| Implementation choices inside your files | **yours** |
| Wording of the strings you rewrite | **yours**, with the change stated in your return |
| Measurement design | **yours** |
| Architecture / structural change | **float to the Admiral** |
| Scope change (issue added, dropped, re-scoped) | **float to the Admiral** |
| Reopening #595's advisory precedence | **forbidden** — settled by lane C |
| Issue filing | **ruled: none.** Stage candidates locally |
| Promoting an observation into `docs/agents/*` | **forbidden** — human's call |
| Fix-now triage inside your own worktree | **yours** |
| Anything that fits no class above | **float**, with one line on why it fit none |

Float by writing your question into your return artifact **and** ending your turn with it
stated plainly. The Admiral answers and continues you; asking up is always sanctioned and is
never counted against you.

## File Ownership

**You are the sole writer of `scripts/checklist_engine.py` this wave.** No other lane touches
it. Also yours: `tests/` files covering your change.

**Fenced — do not edit, another lane owns it this wave:**

| Path | Owner |
|---|---|
| `skills/workbench/**`, `scripts/install_constellation.py`, `scripts/verify_skill_registered.py`, `scripts/measure_overread.py` | lane D2 |
| everything under `skills/` except workbench, plus `specs/`, `scripts/init_work_area.py` | lane D1 |
| `scripts/mcp_spine_server.py`, `episodes/` | lane E |
| `scripts/run_crew.py` | lane F |
| `map/INDEX.md` | the Admiral |

Your working-notes file, sole writer, is `.agent-work/567-h/notes-1.md`. Name it exactly that
— **never** `findings-<n>.md`: the harness `Write` tool refuses any path whose basename
contains "findings", a guard aimed at unprompted report-dumping that cannot tell this file was
deliberately assigned. Three agents hit it in one epic.

## Workspace

- **Spine (yours, already provisioned):**
  `/home/tommy/projects/constellation-skills/.worktrees/567-h-rail-readability/.agent-work/567-h/spine.json`
- **Worktree:** `/home/tommy/projects/constellation-skills/.worktrees/567-h-rail-readability`
- **Branch:** `feat/567-h-rail-readability` · **Base commit:** `f05a3d78`
- **Created by:** `git worktree add -b feat/567-h-rail-readability .worktrees/567-h-rail-readability f05a3d78`
- **Main freshness verified before dispatch:** `origin/main` at `f05a3d78`, full suite **3352
  passed, 6 skipped, 1219 subtests passed, 0 failed, 0 SUBFAILED** on Linux in a clean
  detached worktree.

Your first command is to `claim` the engine lease on the spine above.

**Your door is bound to your own spine, and this is the first wave where that is true.** Call
the `spine_lease` MCP tool with `action=claim, claimed_by=commander, worktree=.` — no CLI, no
`spine_bind`, no environment surgery. Your process was launched with `SPINE_FILE` pointing at
your spine, so your door resolved to it at startup. Verified before you were dispatched:
`spine_status` and `spine_lease claim` both returned cleanly against your spine under identity
`constellation/567-h`.

**One thing you will see and should not be alarmed by:** your `spine.json` journal already
records one `claim` and one `release` under `constellation/567-h`, timestamped just before your
dispatch. **That was the Admiral**, proving your door could drive your spine before spending a
Commander on the question. The lease was released deliberately so you claim cleanly rather
than forcing. This is recorded here because wave 1 lost a delivering lane to an agent that
found unexplained writes in its own work area and concluded its worktree was compromised.
`crew-runs.json` is how you resolve "who wrote this" if anything else looks unexplained.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not
a local merge that would diverge your worktree from main).

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` is resolved
once, at session launch, so a Commander in an isolated worktree still executes the **main
checkout's** hook code against the **main checkout's** state, even while every git operation
stays correctly fenced (#269). Your mission touches `checklist_engine.py`, which the hooks
read — so you cannot validate your change from inside the process that would run the unchanged
code. Validate in a **fresh process** with explicit paths, never a fixture that hand-injects
the value you are trying to prove the harness delivers.

## Inherited Context

- **A bare `cd` does not persist between Bash calls.** Wave 1's lane A ran 47 minutes and wrote
  **zero bytes** stuck on exactly this; its dying words were *"the bash cwd resets between
  calls."* Use a **single compound call** — `cd /abs/path && <command>` — every time, or pass
  absolute paths.
- **The merge gate is the full suite green on Linux**, run in a **clean detached worktree of
  your branch**, never in your working copy. Wave 1's Admiral authored that exact defect four
  times: *a check that runs against your own working copy is not a check on the world.*
  Windows CI is red on a pre-existing ~122-failure path-casing baseline and is **not** the
  yardstick (#575 is deferred).
- **A failing subtest is now greppable.** The repo-root `conftest.py` (PR #626) restates each
  failed subtest as a line beginning `FAILED `, with a `[subtest …]` marker. Before that,
  `grep '^FAILED'` returned nothing for a failing subtest because `SUBFAILED` cannot match
  `FAILED ` — the wave-1 Admiral shipped a merge gate with that hole. Grep for `^FAILED` and
  trust it.
- **`episodes/` has exactly one write path**, `scripts/apply_episode_delta.py`, always with
  `--store-root episodes`. Never hand-edit it. If your run captures episodes, the order is
  **write → `git add` → suite → commit**: `test_canon_episode_store_untouched` is
  worktree-vs-index only, so running the suite between the write and the stage trips it with a
  message that reads like store corruption.
- **The episode-observation guard cannot tell a past-tense verb from an imperative** ("read",
  "grep"). Rephrase to remove the bare verb; **do not** add to the exception list, which
  already carries 11 entries across five prior runs.
- **GitHub has been returning intermittent 503s all day.** `gh pr merge` and `gh pr create`
  need retrying — up to six attempts in wave 1. **Gate each retry on whether the world
  actually changed** (`git rev-parse origin/main`, `gh pr view`), never on the command's own
  output.
- **A concurrent session works this repo.** `origin/main` moved under wave 1's Admiral twice,
  once breaking it. Check `git rev-parse origin/main` before you assume your base is current.
  Do not touch `.worktrees/issue-610-stand-up-work-area` — not yours.

## Pre-empted Steps

- **Work-area stand-up is done.** Your worktree, `.agent-work/567-h/`, and `spine.json` were
  provisioned by the Admiral per `skills/_shared/stand-up-work-area.md`. You do not scaffold,
  and your `init` step means exactly one thing: claim the lease.
- **The `--here` arrival check is retired as an instruction** (#610). Do not run
  `verify_worktree_isolation.py --here`; isolation was gated by the Admiral across all five
  worktrees before dispatch (`5 distinct worktrees`, exit 0).
- **Your door-binding was pre-verified** — see Workspace.

## Data Locations

Everything your mission needs is tracked and present in your worktree. No untracked inputs.
The main checkout, if you need to read it (do not write to it), is
`/home/tommy/projects/constellation-skills`.

## Budget

- **Model tier (required):** **Sonnet.** The target is three strings and a measurement; the
  hard part is measurement discipline, not reasoning depth.
- **Compute/time, session-window:** one focused session. If the cold-agent measurement turns
  out to need more than roughly a third of your budget, float rather than spend it — that
  question is explicitly unsettled and the Admiral would rather rule on it than have you
  silently consume the lane.

## Stop Conditions

Stop and return when: scope is exceeded; a decision outside your inherited latitude is needed;
budget is crossed; the evidence #442 demands is impossible to obtain; or you need **context
this order does not cover and cannot safely proceed without** — return-and-query the Admiral,
which answers and continues you.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token
cap, not a share of your window, so a Commander that has loaded its skill, references,
templates and this order can be over it on turn one having done no work. The engine refuses
only the verbs that BEGIN work at a gate (`start`, `reopen`), and only until a refresh-request
exists for that gate. The legal sequence is: **attach the refresh-request against the current
why-record, then `start`, then do the work.** Attaching first sends the guard down its release
path; starting first is what gets refused.

Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as an instruction to
`advance --why` and hand off on turn one. A fresh agent that closes its gate before doing the
gate's work produces an infinite handoff chain. Hand off when you have actually spent the
context, not when you inherit the reading.

**Do not end your turn with an engine gate open.** The Stop hook refuses it and is
authoritative over the context-trip advisory (lane C's #595 settled that precedence). The
sanctioned exit is the engine's `block` verb with a reason and a next action.

## Return Shape

Write your result to **`.agent-work/epic-567-door/results/lane-h-RETURN.md`** — that exact
path. **Not** `RETURN.md` at your worktree root: that path is tracked, and in wave 1 four
lanes collided add/add on `main` the moment the first one merged.

Write the artifact and send your verdict **before** going idle. An idle notification with no
artifact reads as stalled, not done — the Admiral judges completion from what you produced.

Include:

1. **Verdict** — delivered, or an evidenced honest null.
2. **Before/after text** for every string you changed, quoted exactly, plus the statement of
   why the #145 measurement survives the change.
3. **The cold-agent measurement** — how it was run, on what, and the result. If it did not
   fit, what you tried and what it would cost.
4. **Fresh-process validation** — the exact commands, with explicit paths, and their output.
5. **Suite result** — full suite on Linux in a clean detached worktree of your branch, with
   the tally and the `^FAILED` grep. `MapTreeFreshnessTests` may fail; nothing else may.
6. **Touched paths** — every file, so the Admiral can sequence merges.
7. **Map impact** — whether your change touches indexed source (do not act on it; the Admiral
   owns the index).
8. **Triage candidates** — as files under `.agent-work/567-h/triage-candidates/`, listed in
   the return. None filed as issues.
9. **Workflow feedback** — what helped, what got in the way, and your own mistakes. Wave 1's
   most useful output was a lane's honest account of its own errors.
10. **PR** — opened against `main` from `feat/567-h-rail-readability`, with the number.

On Windows, write the PR body to a temp file and use `gh pr create -F <file>` — never a
heredoc or a PowerShell here-string for a PR body. You are on Linux, so a heredoc is fine.
