# x1 Designer B — Hook-carried rail (harness hooks, engine responses unchanged)

**Constraint:** Claude Code hooks are the ONLY new channel. `checklist_engine.py` is not touched — not one
response string changes. The doctrine force that took commander-delegated to 3/3 is re-delivered at the
harness decision points (turn-end, post-compaction, session start) by a project-local hook suite that
`.claude/settings.json` wires up and the workbench skill ships/installs.

**One-sentence thesis:** the engine already emits the next imperative from `current`; the four winning
clauses are *when* the agent is made to re-read it. Hooks are a pure transport that re-plays the engine's
own `current` output — plus a thin "why it matters" wrapper — at exactly the moments a cheap model wanders:
when it tries to end its turn mid-spine, and when compaction wipes the imperative from context.

Hook capabilities below are cited from the official docs (`https://code.claude.com/docs/en/hooks`, fetched
2026-07-12): SessionStart `source` ∈ {startup, resume, clear, compact} and its
`hookSpecificOutput.additionalContext`; Stop `decision:"block"` + `reason` + `hookSpecificOutput.additionalContext`,
input `last_assistant_message`, **no `stop_hook_active` flag exists** (I build my own loop guard); PreCompact
`compaction_reason` ∈ {manual, auto}; SubagentStop with `agent_id`/`agent_type`; PostToolUse `tool_name`/`tool_input`.

---

## 0. Discovery — which spine is active for THIS session

The hooks receive `session_id`, `cwd`, `transcript_path` — never a work-id. Two-layer discovery:

**Primary (event-driven, exact): a PostToolUse binding.** A `PostToolUse` hook matched to `Bash` inspects
`tool_input.command`; when it sees a `checklist_engine.py … claim … --file <spine> --session-id <eng-id>`
it writes a binding keyed by the Claude `session_id`:

```json
// .agent-work/.session-spine-map.json  (git-ignored; harness scratch)
{
  "claude-sess-abc123": {"spine": ".agent-work/issue-138-x/spine.json",
                          "engine_session": "commander-138", "worktree": "C:/Programs/constellation-skills"}
}
```

When it sees a `… release --session-id <eng-id>` it deletes that entry. Stop/SessionStart then look up
their own `session_id` directly — O(1), and **release removes the binding, which is the natural off-switch
for the whole rail** (ties to the pinned "release is the LAST journaled action" invariant: the last journaled
verb is also the last hook nudge).

**Fallback (scan, for sessions that were already mid-work when hooks were installed):** glob
`.agent-work/*/*.json` (plus sibling worktrees via `git worktree list --porcelain`) for a file with
`engine_session.status == "active"`; disambiguate by matching the lease's recorded `worktree` to the hook's
`cwd`; on a tie prefer exact `worktree == cwd`, else most-recent `last_heartbeat`, and emit the ambiguity in
`systemMessage`. A stale lease still counts as mid-flight (we still nudge its owner).

**PreCompact breadcrumb (compact-case exactness):** because SessionStart(compact) runs in a freshly
compacted context, a `PreCompact` hook writes `.agent-work/.resume-hint-<session_id>.json` containing the
resolved spine path + a live `current` snapshot at compaction time, so post-compact re-injection is exact
even if the binding file is somehow unavailable.

---

## 1. The contract at each decision point (concrete payloads)

Every hook is one small script, `scripts/hooks/spine_rail.py`, dispatched by `hook_event_name`. It shells
`python <skill-dir>/scripts/checklist_engine.py --file <spine> current` and reshapes that output. **All
imperative text originates in the engine/spine — the hook never authors workflow content, only the "why it
matters" wrapper.**

### 1a. Step entry (`start`/`advance`/`current`) — NOT a hook event
There is no per-engine-call hook. Step-entry force stays exactly where it is today: the engine's `current`
and `advance` response strings, unchanged (my constraint). The hook channel adds nothing here — this is a
deliberate gap, see §5/§6.

### 1b. Turn-end mid-spine — **Stop hook** (the flagship)
Input the hook sees:
```json
{"hook_event_name":"Stop","session_id":"claude-sess-abc123","cwd":"C:/Programs/constellation-skills",
 "last_assistant_message":"The crew is running in the background; I'll wait for it to finish."}
```
Hook resolves the binding → runs `current` → sees `ACTIVE execute [in-progress] — Before entering this
step…`. `active_id` is not None and the task is not `blocked`, so it refuses the turn-end:
```json
{"decision":"block",
 "reason":"SPINE NOT COMPLETE — you are mid-flight at gate 'execute' (5 of 10, 5 steps from terminal). Ending your turn now abandons the run. The solution is the MIDDLE, not the end. Do not end your turn to wait: poll the crew registry / expected artifact in a loop inside this turn.",
 "hookSpecificOutput":{"hookEventName":"Stop",
   "additionalContext":"ENGINE current -> ACTIVE execute [in-progress] — <full imperative text piped verbatim from checklist_engine.py current>\nNext verb when this gate's evidence is in hand: advance execute --session-id commander-138.\nHonest stops available: `block execute --blocker ... --authority ... --next ...` (bubbles up) or `waive` a specific check on human authority. A genuine block is a valid turn-end; wandering off is not."}}
```
The agent cannot silently stop; it is handed the exact next imperative (engine-sourced) plus the escape
hatches. When `current` reports `ACTIVE … [blocked]`, or the spine is terminal, the hook returns `{}` (exit 0)
and the turn ends normally.

**Escape hatch / loop guard (mandatory — there is no `stop_hook_active`):** the hook keeps a per-session
counter in `.agent-work/<work-id>/.stop-nudges.json`:
```json
{"claude-sess-abc123":{"count":2,"last_active_id":"execute","last_journal_seq":14}}
```
Before blocking it reads the spine's journal tail seq and `active_id`. If **either advanced** since the last
nudge → progress is real → reset `count` to 0 and block again (a working agent is never capped out). If
**neither moved** → increment. At `count >= 3` consecutive no-progress nudges the hook **allows the stop**
with a loud marker so a stuck agent stops honestly instead of loop-burning:
```json
{"continue":true,
 "systemMessage":"⚠ SPINE-RAIL: released turn-end after 3 no-progress nudges on gate 'execute'. The spine is NOT complete and NOT formally blocked — this is an unhealthy stop. If you are stuck, `block` the gate on the engine so it bubbles to your parent; do not leave it dangling."}
```
This satisfies "a stuck agent must be able to stop honestly, never loop-burn" and honors engine `block`/`waive`
as first-class honest stops.

### 1c. Check-FAILURE
Not a hook event and not needed. A failed `command`/`artifact` check already refuses inside the engine
(`REFUSED: gN: postconditions unmet [...]`) — that string is unchanged and already lands in the agent's
context as the tool result. The Stop hook is the backstop only if the agent tries to *end its turn* after a
refusal without resolving it (then §1b fires). Left to the existing engine refusal.

### 1d. Post-compaction — **SessionStart(source=compact)** and **(source=resume)**
```json
{"hook_event_name":"SessionStart","source":"compact","session_id":"claude-sess-abc123","cwd":"C:/Programs/constellation-skills"}
```
Hook resolves binding/breadcrumb → runs `current` → injects:
```json
{"hookSpecificOutput":{"hookEventName":"SessionStart",
  "additionalContext":"⟦SPINE RAIL — you are RESUMING mid-workflow⟧\nWork-id issue-138-x, lease commander-138 ACTIVE.\nENGINE current -> ACTIVE execute [in-progress] — <full imperative piped from `current`>\nYou are 5 of 10 gates; 5 steps from terminal (archive → release). The solution is the MIDDLE, not the end — do NOT treat this fresh context as a finished run.\nEntry ritual: your NEXT action is an engine call against .agent-work/issue-138-x/spine.json, not a summary. Re-issue `current` yourself to confirm, then proceed. Release the lease only as your VERY LAST action, after archive advances."}}
```
`source=resume` injects the identical block (a `--resume`/`--continue` restart is the same orientation
problem). This is the post-compaction rail that a bare one-line doctrine pointer failed to provide.

### 1e. Session start (cold) — **SessionStart(source=startup)**
If discovery finds an active lease at startup (rare — a resumed process), inject the §1d block. If none,
inject a thin entry-ritual reminder only when a `.agent-work/` tree exists:
`"If you load a Constellation role skill this session, your first action after loading is an engine call
(claim + current), not prose."` Otherwise `{}`. Kept minimal — startup is mostly a no-op for this channel.

### 1f. Terminal release
No hook fires *on* release; the *absence* of a hook is the design. Once the agent runs
`release --session-id …`, the PostToolUse binding is deleted, so the next Stop hook finds no active spine and
allows the turn to end. Completion-theater ("I released") is caught structurally: if the agent *claims*
release but never ran the verb, the binding still exists and `current` still shows an active lease, so the
Stop hook re-nudges "lease still ACTIVE — release is not done." The engine's truth, not the agent's claim,
gates the exit.

---

## 2. Where the doctrine text lives, and who owns it

| Text | Lives in | Owner |
|---|---|---|
| Every step imperative | spine/template JSON `imperative` fields (unchanged) | template author / Charter |
| Engine `current`/refusal strings | `checklist_engine.py` (unchanged) | engine owner |
| The "why it matters" wrapper (middle-not-end, wait-loop, entry-ritual, release-last) | `scripts/hooks/spine_rail.py` string constants | workbench skill |
| Hook wiring | `.claude/settings.json` `hooks` block | workbench installer, committed to repo |

The key contrast with the engine-string channel: **doctrine text is NOT duplicated.** The imperative stays
single-sourced in the spine templates; the hook pipes `current` verbatim and only adds the framing that #134
asked for ("carry the next imperative AND why it matters") — the *what* comes from the engine, the *why*
from the hook. One place to edit each. `settings.json` (concrete):
```json
{"hooks":{
  "SessionStart":[{"matcher":"compact|resume|startup","hooks":[
     {"type":"command","command":"python","args":["${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py","SessionStart"],"timeout":20}]}],
  "Stop":[{"hooks":[
     {"type":"command","command":"python","args":["${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py","Stop"],"timeout":20}]}],
  "PreCompact":[{"hooks":[
     {"type":"command","command":"python","args":["${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py","PreCompact"],"timeout":10}]}],
  "PostToolUse":[{"matcher":"Bash","hooks":[
     {"type":"command","command":"python","args":["${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py","PostToolUse"],"timeout":10}]}]
}}
```

---

## 3. Eval-check implications (#129 harness)

**The engine, journal, and lease are untouched, so every existing provenance check is unchanged — the
measured bar's *definition* does not move.** The hook only causes the agent to keep calling the same engine
verbs it would have called anyway; every mutation still journals normally, and "release is the last journaled
action" still holds.

Two real implications:
1. **The eval must run in a hooked configuration**, or it measures the un-hooked baseline. The #129 harness
   must install this `settings.json` + hook scripts into the eval sandbox for the runs meant to exercise the
   channel. This *strengthens* the observed bar (turn-end/compaction wander now blocked) **only if hooks
   actually fire in the eval's execution mode** — see the dependency below.
2. **A new, cheap eval assertion becomes possible** (optional): assert the run's transcript contains ≥1
   Stop-block re-injection OR zero (proving the agent never tried to bail) — i.e. the hook fired and was
   obeyed. This is a harness-log check, not an engine check; it does not weaken the terminal provenance check.

**Net:** unchanged where it counts (provenance), *conditionally stricter* on wander/quit-early — conditional
on the dependency in §4.

---

## 4. Dependency & fallback — hooks for subagents / headless

The shared core flags a live excursion verifying whether hooks fire for Agent-tool subagents and headless
`claude -p`. My read of the current docs: SubagentStop exists and "subagents inherit project hooks" — but I
design the fallback as if that is FALSE, because the load-bearing path does not need it:

- **Load-bearing path = the parent commander session.** The commander is the lease owner, the one at risk of
  *wait-by-ending-turn* and post-compaction wander over a long multi-gate run. It is a top-level interactive
  (or headless-driven) session, the case where hooks unambiguously fire. The rail protects it fully with zero
  subagent-hook dependency.
- **Crews (implementer/reviewer subagents)** are dispatched foreground/blocking through `run_crew.py`, which
  already verifies result artifacts, and are gated by the reviewer survey. Their honesty is enforced today by
  that machinery, not by hooks. **If** SubagentStop fires for them, we get a free bonus: add a `SubagentStop`
  matcher that runs `current` on the *child* checklist and blocks a crew that tries to stop with open child
  gates. **If it does not fire, nothing regresses** — crews stay governed exactly as today.
- **Headless `claude -p` for the eval:** THIS is the sharp dependency. If the eval drives the cheap model via
  a mode where Stop/SessionStart hooks do NOT fire, the entire hook-carried channel is untested and delivers
  zero force in the measured run. **Fallback if that's the case: the hook-carried design cannot be the eval's
  primary rail** — it degrades to "engine-string channel carries the run, hooks are a defense-in-depth layer
  for interactive commander sessions only." I state this plainly because it is the single biggest risk of my
  constraint and the panel needs it stark: *a rail the eval's runtime can't see is not a rail for the eval.*

---

## 5. Failure-shade coverage

| Shade | Hook-carried treatment | Strength |
|---|---|---|
| **wait-by-ending-turn** | Stop hook refuses the turn-end while `active_id` is open, hands back the poll-in-loop imperative | **PREVENT** (bounded by nudge cap) — flagship |
| **quit-early** | Same Stop-block: cannot end the turn before terminal/`blocked` | **PREVENT** (bounded) |
| **completion-theater-at-finish** ("released"/"done" falsely) | Stop hook checks engine truth (lease still active / `current` not terminal) not the agent's claim; re-nudges | **PREVENT** (structural — engine truth gates exit) |
| **skip** (skip a step) | Can't end the turn mid-spine; but a skip *done inside* the same turn isn't blocked by a Stop hook | **DETER** (turn-end blocked; step-entry ungoverned by this channel) |
| **theater** (fake work / plausible wrong output) | Hooks cannot judge quality | **DOCTRINE + engine evidence checks + reviewer gate** (unchanged) |
| **fabrication** (hand-written spine) | SessionStart re-injection lowers temptation but doesn't detect; journal hash-chain + #129 provenance catches it | **ENGINE/EVAL** (hooks don't help) |

---

## 6. Axis self-assessment (honest, incl. where the constraint hurts)

- **Depth:** high leverage per byte — ~150 lines of hook script + a 20-line `settings.json` deliver turn-end
  and post-compaction rails to **all nine skills at once**, with zero engine change and zero per-skill
  wording. The four winning clauses stop being nine hand-maintained copies; they become one hook wrapper over
  `current`. But behaviorally **shallow**: the hook can only *nudge and refuse-to-stop*, never enforce that
  the work inside a step was real.
- **Locality:** strong — one committed `settings.json`, one hook script, installed once by workbench.
  Doctrine stays single-sourced (§2). **Where it hurts:** the hook script re-encodes a sliver of engine
  semantics — "mid-flight = active lease + non-None `active_id` + status≠blocked" — a *second* place that
  knows what "terminal" means. If the engine's terminal shape ever changes, two files move.
- **Seam placement:** the seam is the **harness↔agent** boundary, and it has exactly **one adapter: Claude
  Code**. Per our own doctrine, one adapter is a *hypothetical* seam — this rail is Claude-Code-shaped and
  does not port to any other harness or to a raw API agent loop. That is the defining cost of the constraint:
  **the rail is exactly as portable as Claude Code hooks, and no further.**
- **Testability:** the hook script is trivially unit-testable (feed it fixture stdin JSON, assert the emitted
  decision) — the *discovery* and *nudge-counter* logic get clean, host-free tests. But the **end-to-end
  behavior** (does the harness actually block the turn? does compact actually re-inject?) is **only** testable
  by running the real Claude Code harness, and is invisible to the existing engine/journal tests. This is the
  weakest testability story of the three channels and it is inherent, not incidental, to the hook constraint.

## 7. What I deliberately did NOT solve (scoped for the comparison)

- **Step-entry / check-failure force** — no hook event exists there; this channel adds nothing at those
  points. It rides on the engine's existing (unchanged) response strings. A channel that wants to strengthen
  step-entry must edit engine responses (designer A's lane) or own the loop (designer C's).
- **Issue #134's gate-vs-fence mandatory-waive** — this is an **engine gate-condition** problem
  (`feedback`/`archive` require writes to the main checkout that fences forbid). My constraint forbids engine
  changes, so **hooks cannot fix #134** — it needs a fencing-aware engine verb or a worktree-local staging
  path in the gate condition. I flag this as a hard miss of the hook-carried channel, not a solved item.
- **Quality / theater / fabrication detection** — left to engine evidence checks + reviewer gate + journal
  provenance, all unchanged.
- **Non-Claude-Code runtimes and (pending §4) headless `claude -p`** — no rail there under this constraint.
