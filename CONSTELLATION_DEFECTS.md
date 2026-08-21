# Constellation defects hit during orrery epic 1, wave 5

Found by the Admiral running `2026-08-15-epic-1-v0-ingestion` against the skills install
timestamped **2026-08-15 21:29**. Four items, ranked by severity. Each carries the command that
produced it and the output it produced, so none of this needs to be taken on trust.

Environment: Linux, Python 3.12 as `py`, skills installed at `/home/tommy/.claude/skills/`,
**no MCP servers configured** (`mcpServers` empty in `~/.claude.json` and `~/.claude/settings.json`,
no `.mcp.json` in the project).

---

## 0. A same-session relaunch never advances `claimed_at`, so the #477 foreign-reading guard can never fire

**Severity: highest — it silently defeats an existing guard and produces the exact relaunch loop that guard
was written to stop. Found after the other four; renumbered to 0 because it subsumes the practical
symptom behind item 3 and behind the "over the band on arrival" workaround.**

**Symptom.** Leg 2 of a commander run was refused `start execute` at "context 18% ≥ 15% hard cap" having
just closed an entire gate. The reading was **not its own**. `gauge.json` in that work area, read from
outside twice, was byte-identical across 40 minutes and two different agents:

```
{"fill_fraction": 0.175885, "model": "claude-sonnet-5", "observed_at": "2026-08-16T04:45:43.624Z"}
```

`0.175885` displays as the "18%" leg 2 was refused on. That sample was taken by **leg 1**.

**Why the existing guard did not catch it.** `_reading_predates_claim` (#477) is exactly the right
mechanism and is correctly written: a reading sampled strictly before the acting session claimed the
lease is foreign and disregarded. It anchors on `engine_session.claimed_at`. But the lease at the time
of the refusal read:

```json
{"session_id": "commander-w5-sb-scoreboard", "status": "active",
 "claimed_at": "2026-08-16T04:37:41.267956+00:00",
 "last_heartbeat": "2026-08-16T05:09:00.474620+00:00"}
```

`claimed_at` is **leg 1's** claim, eight minutes *before* the stale sample — so the sample does not
predate the claim, the guard fails open, and the foreign reading is obeyed. `claimed_at` never moved
because the doctrine's own relaunch instruction is to reuse the same worktree, spine file **and session
id**, and `claim` with a matching active session id takes the idempotent-resume early return at
`checklist_engine.py:1083`, which refreshes `last_heartbeat` and nothing else.

**So the guard protects a *new* claimant and cannot protect a *relaunch* — and a relaunch is the only
situation in which a foreign reading is inherited.** The guard's own comment describes the resulting
loop and prices it:

> The failure that follows is a LOOP — relaunch, inherit, trip, hand off, relaunch — and every cycle
> looks like correct doctrine being followed. It cost that epic four crew relaunches in one wave.

This run was one relaunch from entering it, and the Admiral would have caused it by following doctrine.

**Workaround, verified in the source and now in use.** The idempotent-resume branch is guarded by
`and not force` (line 1087), so a re-claim with the **same** session id plus `--force --reason` skips it,
falls through to line 1127, and stamps `claimed_at` to now:

```
claim --session-id <same id> --claimed-by commander --worktree . \
      --force --reason "relaunch: re-claim so claimed_at post-dates the predecessor's gauge reading"
```

`claimed_at` then post-dates the stale sample, the guard fires, the foreign reading is disregarded, and
the agent's own reading governs.

**Fix direction.** Make the relaunch path advance the anchor without needing `--force`: either treat a
same-session `claim` as a re-claim that restamps `claimed_at` (the heartbeat-only resume is what breaks
it), or have the launching role stamp a fresh claim automatically. Alternatively give the reading an
owner at the **writer**, which the #477 comment already names as the real fix and explicitly puts out of
its own scope. Until one of those lands, every relaunch instruction in the fleet should carry the
`--force` re-claim.

**Related observation, unexplained.** `gauge.json` did not refresh at all across leg 2's entire run —
same `observed_at` before it started and 22 minutes in. If the writer only samples under conditions that
did not occur here, then the per-directory staleness above is not an edge case but the normal state for
every relaunched agent.

---

## 1. The stop hook resolves the spine from the working directory, and hands an orchestrator its subordinate's gates

**Severity: high — this one induces a doctrine violation rather than merely wasting a turn.**

**Symptom.** After dispatching a delegated Commander I left my shell inside that commander's worktree.
The stop hook (`spine_rail.py Stop`) then read the **commander's** `spine.json`, reported its `plan`
gate open, and instructed me — the Admiral — to author its mission frame and `execute.json`:

```
SPINE MID-FLIGHT: gate plan is still open -- you are in the MIDDLE of the spine, not at its end...
Next imperative: Map-first: BEFORE authoring execute.json, produce a mission frame...
Write it to .agent-work/w5-sb-scoreboard/MISSION_FRAME.md
```

The hook's own context block names the lease it read:

```
ENGINE current -> LEASE active: commander-w5-sb-scoreboard (by commander, ...)
```

My own spine's lease, verified from the main checkout at the same moment:

```
LEASE active: c75f7d16-27d1-463a-9d9a-ba746570cb3d (by admiral, ...)
ACTIVE execute [in-progress]
```

**Why it matters.** Complying would have broken the single hard prohibition in the Admiral's own
active imperative — *"Never run a Commander's issue yourself"* — and would have raced a live
commander on state whose lease it holds. Two agents writing one spine is the exact failure the lease
exists to prevent. The hook did not merely misreport; it issued a concrete instruction to violate the
doctrine, and it will fire that way for **any** orchestrator whose shell happens to sit in a
subordinate's worktree, which is the normal state of affairs right after provisioning or verifying one.

**It reproduces.** This fired **twice within twenty minutes**, both times because an ordinary read-only
probe of the commander's state left the shell in its worktree. The second time it ordered me to drive
the commander's `execute` gate — "drive execute.json gate by gate in this conversation", dispatch its
crew, write its `STATE_NOTE.md`. So the trigger is not a rare slip: it is the routine act of an Admiral
inspecting a subordinate, which the doctrine explicitly requires before adjudicating. Any `cd` into a
worktree arms it until the next `cd` out.

**Where to look.** `constellation-workbench/scripts/spine_rail.py`, the `Stop` path — specifically
however it locates `spine.json` when no explicit path is passed.

**Fix direction.** Resolve the spine from the calling session's own binding (`SPINE_FILE` /
`SPINE_SESSION`, or the lease whose `claimed_by`/session id matches this process), not from `cwd`.
Failing that, **refuse** when the resolved spine's lease owner differs from the calling session — a
refusal with "this spine belongs to session X, you are session Y" is strictly better than a confident
instruction to drive someone else's gate. The engine already refuses a cross-worktree `claim` with
exactly that shape of message, so the check exists; the hook just isn't applying it.

---

## 2. `verify_worktree_isolation.py --here <path>` ignores its own argument and resolves git from `cwd`

**Severity: medium — first command in every launch order, fails for the wrong reason.**

**Symptom.** Run with an explicit absolute path from a directory that is not a git repo:

```
$ cd /home/tommy/projects
$ py .../constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/orrery-wt-sb
git rev-parse --show-toplevel failed: fatal: not a git repository (or any of the parent directories): .git
rc=1
```

Same command, same argument, from inside the worktree:

```
$ cd /home/tommy/projects/orrery-wt-sb
$ py .../verify_worktree_isolation.py --here /home/tommy/projects/orrery-wt-sb
worktree OK: in /home/tommy/projects/orrery-wt-sb
rc=0
```

**Why it matters.** Every launch order this fleet issues makes this the commander's **first command**,
before any git operation, and gates the dispatch on `rc=0`. The path is passed explicitly precisely so
it does not depend on ambient state. A commander that runs it before `cd`-ing gets a hard failure whose
message points at a missing `.git` rather than at the real cause, and the correct reading — "you are not
isolated" — is the opposite of the truth.

**Fix direction.** Run the `git rev-parse` with `cwd=<the --here path>` (or `git -C <path>`), so the
argument governs. Same file ships under `constellation-admiral/scripts/` and
`constellation-commander/scripts/` — fix both, or fix the shared source and reinstall.

---

## 3. A refresh-request has no consume path, so the agent that *is* the refresh inherits the stop signal

**Severity: medium — known and tracked upstream, but it is live and it misleads the successor.**

**Symptom.** A commander tripped the context gauge at `plan` and filed a `refresh-request`, correctly.
I relaunched a fresh commander into the same worktree and spine, which is the doctrine's prescribed
response. That fresh agent's `current` still renders:

```
REFRESH REQUESTED: plan (why_ref w-3)
CONTEXT 18% (>= hard): your instruction has changed, and the refresh for plan is already requested.
Close THIS gate carrying your handoff (`advance plan --why "<understanding>"`) and stop.
```

**Why it matters.** The successor is told to close the gate and stop — on the first turn, before doing
any of `plan`'s work, with 1 of 7 postconditions met and no deliverables in existence. Taken literally
it produces an infinite handoff chain where each agent immediately hands off again. I had to brief the
relaunch explicitly to disregard it, which means the tooling's instruction and the doctrine's
instruction were in direct contradiction and a human's note broke the tie.

**Where to look.** `constellation-workbench/scripts/checklist_engine.py:1251`,
`has_pending_refresh_request`. Its own docstring names the gap:

> It is pending while present and not superseded (the reopen cascade supersedes evidence; **the flow
> that consumes/fulfils it is #183**).

The `why_ref` identity filter (#190) already stops a *hard-band* caller riding a stale request, and
that part works. The `REFRESH REQUESTED:` **display** line in `_why_suffix` matches on gate alone, so
it renders regardless.

**Fix direction.** Implement the consume flow (#183), or — much cheaper as a stopgap — have
`_why_suffix` pass the current why-record id to `has_pending_refresh_request`, so the display line uses
the same identity filter the hard-band path already uses. A request raised against `w-3` then stops
rendering once the successor advances and creates `w-4`.

---

## 4. ~~The commander `init` imperative names an MCP door as its default on machines that have no MCP~~

> **PREMISE WITHDRAWN 2026-08-18 — but the conclusion held, by accident.** This machine **does** have
> an MCP door: `mcp_spine_server.py` runs as pid 1927559, built by Tommy's fleet-tooling work. So the
> title's claim — "machines that have no MCP" — is false for this machine.
>
> **The recommendation it produced was nonetheless right for dispatched commanders**, for a reason this
> entry never identified. Per `checklist-engine.md` §"MCP door: default path, and who it is NOT for",
> the door binds to the **dispatcher's** process environment and *"does not follow you into a Task-tool
> subagent's OWN work"*. A dispatched commander driving its own `spine.json` therefore cannot reach a
> door no matter how many exist on the host — and the workbench SKILL.md says that case is driven by
> the bundled engine *"and by nothing else"*, which is not a fallback at all.
>
> **The real defect is one level up, and it is a documentation defect:** this entry, and the standing
> line built on it, both asserted a property of the **machine** when the governing property is of the
> **process**. That conflation cost a wave-6 over-correction in which four commanders were told to use
> a door none of them could see.
>
> **This entry outlived its truth and cost something.** Standing line 3 was written against it and told
> every wave-6 launch order to use the CLI instead of the door. Four commanders were dispatched on that
> line before Tommy caught it; all four were corrected in flight. The record defect is the same family
> as the fifth-approach phantom and the raw-`curl` blocker — an entry that was true when written,
> inherited later as fact, and never re-checked against the system. The original text is kept below
> unchanged, as the record of what was true in August 2026.

**Severity: low — costs a cold agent one turn, every run.** *(as originally filed)*

**Symptom.** The freshly-installed `COMMANDER_SPINE.template.json` `init` step reads:

> Claim the engine session lease on this spine... **by default, call the spine_lease MCP tool** with
> action=claim... **CLI fallback:** `<engine> claim --session-id ...`

There is no MCP door on this machine. A cold commander follows the default, discovers the tool does not
exist, and recovers — but spends a turn doing it. The same "by default, use the MCP tool" phrasing
recurs at `plan` (`spine_evidence`) and, from the shape of it, at the other gates too, so the cost is
per-gate rather than once.

**Why it matters.** The imperative presents the door as the normal path and the CLI as the exception,
which inverts the truth for any install without MCP configured. `references/checklist-engine.md` states
the correct condition — *"when it is configured for your session"* — but the spine imperative the agent
actually reads drops that qualifier.

**Fix direction.** Carry the qualifier into the imperative: lead with the CLI, and name the door as the
path *when `SPINE_FILE`/`SPINE_SESSION` are bound in this process's environment*. Better still, have
`init_work_area.py` detect whether a door is configured and resolve the placeholder accordingly, the way
it already resolves `<commander-skill-dir>`.

---

## Checked and found NOT broken

- **Engine exit codes on refusal.** A refused `claim` exits **1**, correctly. I initially read it as 0;
  that was my own measurement error — `$?` after a pipe into `head` reports `head`'s status, not the
  engine's. Unpiped, `rc_unpiped=1`. No defect here.
- **Spine template compatibility across the install.** The live Admiral `spine.json`, instantiated from
  the previous template, is field-for-field compatible with the new `ADMIRAL_SPINE.template.json` — no
  differing fields, postcondition ids, or directive keys across all four tasks. The new
  `COMMANDER_SPINE.template.json` instantiates and drives cleanly via
  `init_work_area.py --spine`. Nothing needed regenerating.
- **`verify_iterative_role_artifacts.py admiral-prelaunch`** still exits 0 against artifacts written
  under the previous install.
- **`constellation-commander-delegated` shipping no `templates/`** is by design — its `SKILL.md` states
  it drives from `constellation-commander`'s templates and depends on that skill being installed
  alongside. Worth knowing it is a hard dependency, but it is not a defect.
