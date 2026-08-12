# Launch Order: `commander-f2 — #542 door adoption + #541 friction capture`

## 0. BOOTSTRAP FLOOR — do these three things before you read anything else

A predecessor on this epic died having produced nothing in 90 minutes because it loaded doctrine
before it stood up its spine. **In your first three commands, in this order:**

1. `cd /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption`
2. Instantiate your commander spine, then
   `python scripts/checklist_engine.py --file <your spine> claim --session <your session id>`
   (note: `--file` comes **before** the verb).
3. Report a one-line proof-of-life.

Only then load the commander skill and read the rest of this order.

**Run the suite as `python -m pytest`, not `python3 -m pytest`.** On this host `/usr/bin/python3`
answers and has no pytest; `~/.local/bin/python` carries pytest 9.1.1. Both report 3.12.3. A
`python3 -m pytest` invocation returns `No module named pytest` and a non-zero exit that reads as a
red suite. It is not.

---

## Mission

Two issues, one workstream: **F2**. The MCP front door from F (#424) is built, merged and unused.
Make agents drive through it, and make the door confess its own friction while they do.

**#542 — adoption.** Three counts measured at the wave boundary, all zero: files in `skills/`
referencing the door's tools, MCP references in `scripts/install_constellation.py`, and agents
actually driving through it. A built door is not a used door.

**#541 — friction capture.** The door makes spine management easier to get right, which means it
absorbs the fumbles that used to land in a transcript where someone could read them. **The door
converts a diagnosable defect into a silent correction.** Capture the server's own rejections into
the run's own episode, through `apply_episode_delta.py`, and say so loudly when it cannot.

**How this serves the epic.** C (#421) relocates gate-specific instructions into the spine under the
hard constraint that the gate imperative rides tool results verbatim. C is therefore written against
whichever door delivers those results, so doing C against the CLI and porting afterwards is doing it
twice. **Agents running the spine through the door is C's entry condition**, set by the repo owner.
C does not launch until you are done.

## Gate order — g1 identity FIRST. This is deliberate.

Wave 1's single largest defect was a plan that put a claim at g1 and its evidence at g3. Do not
repeat the shape. Here the risky unknown is the **identity composition**, and it is the fact every
later gate writes against: if a subagent-dispatching role cannot safely use the door, then editing
role spine instructions to default to it is the wrong edit. Settle it first.

**g1 identity → g2 capture → g3 installer → g4 adoption + acceptance.**

### g1 — the identity trade

DC3 measured that an in-session Task-tool subagent **inherits its parent's MCP scope**. The
inheritance splits across two seams, and F's own `DC3InheritanceMechanismTests` drew the line in
writing:

- **Not ours.** Whether the Task-tool harness internally reuses an already-connected MCP
  client/server object inside one running process is, verbatim from the test, *"a product-internal
  mechanism with no observation point reachable from a subprocess-level test."* DC3's PASS covers
  the environment seam and explicitly does not cover this.
- **Ours.** `scripts/mcp_spine_server.py:113-115` reads `ENGINE`, `SPINE` and `SESSION` from the
  environment as module-level constants at import time, and no tool takes a spine path as an
  argument. One server process = one spine = one identity, fixed for the life of the process.

The problem is the **composition**: the harness shares the process, and we put identity in the
process. Two agents on one lease is the exact failure the engine's session leases exist to prevent.

**Loosening our half is a trade, not a free fix.** Moving the spine path to a per-call argument makes
identity per-call and discards what env-binding buys — a server that can only ever touch the spine it
was launched for becomes one any caller can point anywhere. Requiring a caller-supplied identity may
not help either, since a subagent cannot prove it is not its parent.

**Choose deliberately and record which property you are giving up.** That record is a required
deliverable of this gate, not a footnote. A third option — accept the composition and forbid the
in-session case in doctrine — is on the table and must be argued against evidence if you take it.

### g2 — friction capture (#541)

The store already has the fields. `episodes/` is written only through `apply_episode_delta.py`, and
its Mechanical block already carries `refusals`, `reopens`, `rework-count`, `failed-commands`. This
is not a new store or a new format.

What closes it:

- The server records **its own** rejections: schema violations, calls made at a gate that does not
  accept them, arguments the engine refused, retries after a correction.
- They land in the **same episode** as the run they happened in.
- **An episode is a record, not a rule.** Write what you observed. Do **not** write guidance for a
  future agent — that belongs in `docs/agents/*` and is the human's call, not yours and not mine.
- **The capture must not become a second silent path.** If the server cannot write its episode it
  says so loudly, every time. This is the owner's explicit instruction: *"fail loud every turn."*
  A capture that fails quietly is the same defect as the door it is instrumenting.

Open design questions from the issue, yours to settle and record:

- Per-call granularity, or a summary at lease release? A record per rejection is the most useful and
  the noisiest.
- Does the **CLI** door get the same treatment, so the two arms stay comparable? Without it, future
  DC5-style measurements compare an instrumented door against an uninstrumented one.
- Is a rejection the agent immediately corrects worth the same weight as one it never resolves?

### g3 — the installer ships and wires the door (#542, criterion 3)

`install_constellation.py` currently has **zero** MCP references. A fresh install must get the door.
Two known traps in that file, both measured this epic:

- Its rewrite token map stamps a **resolved interpreter** into every installed skill body. That
  path is now hard-stopped when no interpreter probes successfully (#540) rather than falling back
  to a member of the disproved candidate set. Do not reintroduce a fallback.
- `--wire-hooks` targets `.claude/skills/constellation-workbench/scripts/`, not `scripts/hooks/`,
  and wires only `PostToolUse`. If you touch hook wiring, measure what it actually writes; do not
  read the flag name as a description of its behavior.

### g4 — adoption and its acceptance measure (#542, criteria 1 and 2)

1. **Role spine instructions name the door's tools as the default path, with the CLI documented as
   the remaining fallback.** The epic's hard constraint is **"The CLI door stays; F is additive."**
   Adoption means agents *default* to the door. **This is not license to remove the CLI**, and an
   edit that removes it fails this gate.
2. **A real dispatched agent drives a real role spine to done through the door alone, measured from
   its own call record.** The instrument exists — it is DC5's — so reuse a proven measure rather
   than inventing one.

**Count from the driving agent's own call record, never server-side.** F's original DC5 numerator
counted from the server log, where a client-side schema rejection never arrives; it structurally hid
exactly the fumbles the door gets credit for avoiding. A measure that cannot lose is not a measure.

That acceptance run is also **g2's live demonstration**: its own friction is the first thing the
capture should record. If the run produces zero rejections, say so — zero is a real number here, and
F already measured zero malformed calls in both arms of DC5. Report it as measured, not as proof the
capture works.

## Prior-Wave Verdicts (pasted)

F (#424) returned complete. **No condition UNMEASURED.**

| # | Condition | Verdict | Evidence |
|---|---|---|---|
| **DC1** | Cold agent reaches done on a real role spine through the door, zero malformed calls | **PASS** | `assert_dc1.py` over two cold agents' own call records — both reached `DONE`, both zero malformed calls |
| **DC2** | Separation: parent and subagent drive two different spines at once, leases never collide | **PASS** | `tests/test_mcp_identity.py`; genuine concurrency via barrier-released threads with intersecting wall-clock windows; a collision control that reproduces a real leak when two processes share one spine file |
| **DC3** | Inheritance fails closed: an unconfigured subagent gets a refusal or no identity, never the parent's lease | **PASS**, behind a positive control | Control **in the assertion path**, demonstrated red for three distinct manipulations with proof each applied, green when correct. The g3 reviewer mutated the real door: a hardcoded identity turned exactly the 2 tests whose premise is "no `SPINE_FILE`" red, leaving 10 green |
| **DC4** | Same-gate equivalence as a **property** over every gate carrying an imperative | **PASS** | `tests/test_mcp_imperative_equivalence.py`: 61 gates across 12 shipped templates, discovered by **walking** the template tree. The g2 reviewer truncated the production door's `as_result()` and watched 4 of 5 tests go red, and added a scratch template to watch the population move 61→62 |
| **DC5** | Spine-management cost falls, attributably to the door | **PASS on the pre-registered metric**, *not by the expected mechanism* | 4 arms, both orders: CLI 22.0 vs MCP 18.0 invocation attempts, non-overlapping spreads. But **malformed calls were zero in both arms** — the saving is the schema arriving with the tools, not the door absorbing fumbles. Per-order gap 2 and 6, so 18% is a midpoint, not an effect-size estimate |
| **DC6** | The governor's threshold instruction arrives through a tool result and is acted on | **PASS**, with a named non-compliance | 2 of 33 tool results carried the HARD instruction verbatim; the agent's next calls attached a `refresh-request` and advanced with a `--why` handoff. It then **ignored the "and stop" half** and drove four more gates |

**`scripts/gen_mcp_config.py` was REMOVED, and the measurement everyone expected to save it is what
killed it.** A committed project-scope `.mcp.json` already keys identity per dispatch through
`${VAR}` expansion — two dispatches, one directory, one config, each returning its own unguessable
nonce. And DC3's open question measured **YES**: an in-session subagent does share its parent's
server. That YES was the last argument for generation and does not survive, because a generated
config binds at server launch **per process** exactly as `${VAR}` does — it names a case *neither*
mechanism reaches. `docs/CHECKLIST_ENGINE_DESIGN.md` carries the tombstone and a
do-not-reintroduce-on-identity-grounds warning. **Do not reintroduce it.**

**The line worth carrying up, in F's own words:** *"I had written a conclusion and was finding routes
back to it after the evidence moved. Neither correction came from me."* Four reviewer BLOCKs, all
four resolved on evidence, none overridden, none waived. One of them **flipped DC5 from negative to
pass** by finding that a shell `for` loop had scored six engine invocations as one.

**A correction to F's own triage, measured after it returned.** F reported that `run_crew.py`
*"silently converts completed crews into apparently-running ones."* That mechanism is wrong. It
refuses **loudly**, exit 1, `no crew recorded with session name`. The real defect is
**misattribution**: `session.split("/")[1]` truncated a nested work-id and opened a *different run's*
registry — in a live epic, the Admiral's own. Fixed in #543 along with a fourth instance nobody had
briefed: `episode_capture.manifest_root()` strips a segment that `context_manifest.manifest_path()`
re-appends, which is what produced the doubled `.agent-work/<epic>/<epic>/` path. **#543 is your
dependency** — #541's write path runs through `apply_episode_delta.py` and
`verify_episode_captured.py`, which were mutually unsatisfiable for a nested work-id until it landed.

## Pre-Rulings

- `decision:the-cli-door-stays` — adoption changes the default, never the availability. An edit that
  removes the CLI path fails g4.
  `@grade: settled/human · leans g4`
- `decision:count-from-the-call-record` — the acceptance numerator is the driving agent's own record,
  never the server log. A client-side rejection never reaches the server.
  `@grade: settled/human · leans g4`
- `decision:fail-loud-every-turn` — a capture that cannot write says so on every occurrence, not once
  per run and not at exit. Owner's words.
  `@grade: settled/human · leans g2`
- `decision:episodes-are-records-not-rules` — write what happened; a rule for a future agent belongs
  in `docs/agents/*` and is the human's call.
  `@grade: settled/human · leans g2`
- `decision:no-gen-mcp-config` — do not reintroduce per-dispatch config generation on identity
  grounds. It was removed on evidence and the tombstone says why.
  `@grade: settled · leans g1 · override only with a measurement that names a case both `${VAR}` and
  generation reach differently`
- `decision:identity-trade-is-recorded` — whichever way g1 goes, the property given up is written
  down. Silence here is a gate failure.
  `@grade: settled/human · leans g1`
- `decision:zero-is-a-result` — if the acceptance run produces zero rejections, report zero. Do not
  manufacture friction to demonstrate the capture, and do not read zero as proof the capture works.
  `@grade: settled · leans g4 · settle: a seeded-rejection control proves the instrument can score`
- `decision:remeasure-never-reuse` — no baseline is carried across a code change.
  `@grade: settled · leans g4`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the
same rigor as a win.

**An UNMEASURED condition is not a negative and must never be reported as one.** Wave 1's Commander
held that line against its own interest — *"this is unmeasured, not a measured negative, and I'm not
dressing it up as one"* — and that refusal is why F got a repair instead of a false green. Hold it
the same way.

## Inherited Latitude

**You may decide, and log:** the identity trade at g1; capture granularity and whether the CLI arm
gets the same instrumentation; which role spines change and in what order; tool grouping and
argument shapes; how the acceptance run is staged; test structure.

**Float to the Admiral:** removing or deprecating the CLI path; changing `INTERPRETER_CANDIDATES`
order; anything that writes `settings.json` at user scope; adding a `required_scripts` entry to
`install_constellation.py` beyond what g3 needs; promoting an observation into `docs/agents/*`.

**Never:** write `settings.json` at user scope. Duplicate engine logic — the server wraps the
engine's own dispatch, and `git diff` against `checklist_engine.py` was **empty** for the whole of F.
Keep it empty.

You cannot reach the human. Float to me and I answer and continue you.

## File Ownership

- Working notes: `notes-1.md` (**never** `findings-<n>.md` — the harness `Write` tool refuses that
  basename, and three agents in one epic each worked around it with a heredoc).
- You own `scripts/mcp_spine_server.py`, `scripts/install_constellation.py`, `tests/test_mcp_*.py`,
  `.mcp.json`, the role spine templates under `skills/`, and your own
  `.agent-work/epic-418-followon/commander-f2/**`.
- **Fenced read-only:** `/home/tommy/projects/constellation-skills` (the main checkout). Stage any
  feedback export worktree-locally under `.agent-work/staged-feedback/<work-id>/` with a `FENCE.md`
  citing this order.
- Cheap fixes found mid-wave are **routed to me, not implemented** inside a wave under measurement.

## Workspace

`/home/tommy/projects/constellation-skills-wt/f2-mcp-adoption`, branch `epic-418/f2-mcp-adoption`,
based on main **after** the wave-boundary merges (#533, #536, #538, #540, #543). Provisioned for you;
verify before your first git operation:

```
python scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
```

It must exit 0. Paste its output into your return report.

PR integration defaults to **server-side merge** — the GitHub merge on the PR itself, not a local
merge that would diverge your worktree from main.

**Isolation is git-only; hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` resolves once at
session launch and is inherited unchanged by every subagent, so a Commander in an isolated worktree
still runs the **main checkout's** hook code against the **main checkout's** state (#269). If your
mission touches hook behavior, you cannot validate the change from inside the worktree that contains
it — validate with a fresh process whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree,
never a fixture that hand-injects the value you are trying to prove the harness delivers.

## Inherited Context

- **Suite baseline: simply green.** Your gate is `0 failed`. The old six-failure known-red pin is
  retired and was re-derived as empty.
- Run the suite as `python -m pytest`. See the bootstrap floor.
- Windows writes need `encoding='utf-8', newline='\n'` passed explicitly on **every** write.
- On Windows, write a PR body to a temp file and use `gh pr create -F <file>` — never a heredoc or a
  PowerShell here-string for `--body`.
- **Never pipe a command into `head`/`tail` and read the pipe's exit code.** It is the pager's status,
  not the command's. This trap fired three times in one Admiral session and once in a Commander's.
  Redirect to a file and capture the command's own `$?`.
- Never hand-launch a crew: every implementer/reviewer dispatch goes through
  `python scripts/run_crew.py` (foreground, durable registry, result-artifact verification).
- Worktree isolation via the Agent tool's `isolation:"worktree"` flag is a **silent no-op** on
  Windows. Provision explicitly; never run two crew members in one worktree.
- When editing a shipped compact-format JSON template, edit the raw text **surgically**. Never
  round-trip through `json.load`/`json.dump` — it reflows the whole file and destroys blame.
  Re-validate with `json.load` afterward.
- When a launch order tasks a crew member with editing global doctrine, cite the canonical source
  `skills/_shared/global-*.md` — **not** `skills/<role>/references/global-*.md`, which
  `install_constellation.py` regenerates at install time and silently overwrites.

## How the acceptance run actually reaches the door

Do not lose an hour rediscovering this. `.mcp.json` is a **project-scope** config that a Claude Code
session reads **at session launch**. A live session does not hot-reload it — measured in F, and it
still holds. Two consequences:

- **You cannot drive the door from your own session** if your session started before `.mcp.json`
  existed in its project root. Neither can an in-session Task-tool subagent, which shares your
  process and therefore your MCP scope.
- **An externally dispatched agent can**, because `${VAR}` expansion keys `SPINE_FILE` and
  `SPINE_SESSION` from that process's own environment at server launch. F proved this: two dispatches
  from one directory against one committed config, each returning its own unguessable nonce,
  corroborated server-side. That is the mechanism DC1 used for its two cold agents.

So the acceptance run is an **external dispatch** with those variables set, not an in-session
subagent. F's archived `crew-plans/scratch-mcp/` carries the working harness — `drive_via_mcp.py`,
`prove_headless_dispatch.py`, `mcp_client.py` — and its transcripts. Read them before writing a new
one.

## Pre-empted Steps

- **Context is established** — this order carries F's full verdict set, the identity analysis, and
  the dependency chain. Cite it rather than re-deriving.
- **The three adoption counts are measured** (all zero, at the wave boundary). Do not re-measure them
  as discovery work; re-measure them at g4 as your own proof they moved.
- **`gen_mcp_config.py`'s removal is settled on evidence.** Do not re-litigate.

## Data Locations

- Main checkout (read-only for you): `/home/tommy/projects/constellation-skills`
- F's archived evidence: `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/` — the
  `MEASUREMENT.md` there records DC5's whole sequence (negative, blocked, still negative, blocked
  again, now pass) rather than presenting the final verdict as if it had been the first.
- Episode store: `episodes/` at repo root, tracked. Write only through `apply_episode_delta.py` with
  `--store-root episodes` on **every** invocation.

## Budget

- **Model tier: Opus.** Named reason, per the standing Sonnet-for-implementers rule: g1 is a design
  trade with no clean answer and g4 is trap-laden measurement where the failure mode is a confident
  wrong number, not a slow one. **Crew implementers under you remain Sonnet.**
- One PR on `epic-418/f2-mcp-adoption`.
- The human is AFK. Float decisions to me rather than blocking.

## Stop Conditions

Stop and return when scope is exceeded, a decision falls outside inherited latitude, the budget is
crossed, or the evidence is impossible to obtain — **or when you need context this order does not
cover and cannot safely proceed without.** Return-and-query me; I answer and continue you. Asking up
is always sanctioned.

## Return Shape

Verdict per exit criterion, with evidence. Map impact. Triage candidates. Workflow feedback. Your
`verify_worktree_isolation.py --here` output as proof you worked in isolation.

**Write your result artifact and send your verdict before going idle** — an idle notification with no
artifact reads as stalled, not done.

If you return incomplete, return the way wave 1's Commander did: say exactly which criteria are
unmeasured, why the gate was not reached, release your leases for a clean claim, and leave a
STATE_NOTE naming the single next action.

## What "done" means for you

1. Role spine instructions name the door's tools as the default path, CLI documented as the
   remaining fallback.
2. A real dispatched agent drove a real role spine to done through the door alone, measured from its
   own call record.
3. `install_constellation.py` ships and wires `.mcp.json`, so a fresh install gets the door.
4. The server's own rejections land in the run's episode through `apply_episode_delta.py`, and say so
   loudly when they cannot.
5. The identity trade is decided and the property given up is written down.

PR green and independently reviewed; **no gate left blocked by its own reviewer.**

_Issued by the Admiral, epic-418-followon, wave 2 `w2-f2-mcp-adoption`, 2026-08-09. The four exit
criteria above are the Admiral's draft; the human went AFK before confirming them and cleared the
Admiral to proceed on its own judgment._
