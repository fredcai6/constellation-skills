# notes-424 — workstream F, MCP front door (#424)

Commander: delegated, under `LAUNCH_ORDER-424.md`. Worktree
`/home/tommy/projects/constellation-skills-wt/f-424`, branch `epic-418/f-424-mcp-door`, base
`a1eab1f1`. Spine at `.agent-work/epic-418-followon/commander-424/` inside the worktree.

## Status

**Returned incomplete, deliberately and with the reason recorded.** The door is built, independently
reviewed and pushed as PR **#533**, which is **MERGEABLE** with the full suite at **2163 passed, 1 skipped, 0 failed** after merging `origin/main` — the six-test pinned red set this run inherited shrank to zero under us when #531 landed. Gate `g1-integrate` is **blocked in the spine and I did not
override the reviewer**. Gates `g2` (DC4 as a property), `g3` (DC2/DC3) and `g4` (DC5/DC1/DC6) were
not reached, so four of the six done-conditions are **not measured**. Verdicts are in the table at
the bottom. Nothing here is backfilled — the file was written as the run proceeded.

The single most useful thing in this file for the next agent is the section headed *"Two claims of
mine that review falsified"*: the run's own adversarial checks overturned my conclusions twice, and
the second overturn is what blocks the gate.

---

## The pre-build branch point is settled: `decision:mcp-probe-is-the-commanders`

**Question (spec F, "Open / graded"; launch order pre-ruling):** does an interactive session pick up
a fresh `.mcp.json` without a restart? Picked up → project-scope `.mcp.json` suffices. Not picked up
→ per-dispatch config generation is the delivery path and gets designed first.

> ### CORRECTION — my first answer to this was wrong, and the gate caught it
>
> I originally concluded "not picked up → per-dispatch config generation is the delivery path", and
> graded it `settled/measured`. The g1 reviewer, whose handoff I had explicitly instructed to
> **re-verify this rather than inherit it** (a cold-critic fix), returned a **BLOCK**: a plain
> project-scope `.mcp.json` *does* serve a cold headless agent. I reproduced it myself afterwards in
> a fresh project directory with no prior approval state — `claude -p --allowedTools
> "mcp__probe__probe_ping"` with **no** `--mcp-config` and **no** `--strict-mcp-config` returned
> `probe-alive` and the server's start-marker file was written, so the server genuinely launched.
>
> **What survives:** a live session does not hot-reload a fresh `.mcp.json`, and `claude mcp list`
> does report a new project-scope server as `⏸ Pending approval`. Both reproduce.
>
> **What was false:** the inference that `Pending approval` in the interactive listing means the
> server cannot serve a headless agent. Those are two different gates — MCP server *approval* in the
> TUI, and the ordinary per-tool *permission* gate every headless tool call passes. `--allowedTools`
> opens the second. My original probe omitted `--allowedTools` from the no-`--mcp-config` arm, so I
> measured the permission gate and attributed the result to the approval gate.
>
> **What I claimed next, which was ALSO falsified — see "Two claims of mine that review falsified".**
> I argued `gen_mcp_config.py` still earned its place because one shared project-scope file binds one
> `SPINE_FILE` and one `SPINE_SESSION` for everybody, so it "cannot" serve a parent and a subagent
> different spines (DC2) or key identity per agent (DC3). The reviewer's re-review showed that is also
> too strong: `${VAR}` expansion, sourced from the calling process's environment, does exactly that. I
> shipped the fix. `gen_mcp_config.py` remains in the tree but its **necessity is unproven**, and that
> is what blocks `g1-integrate`.
>
> **The process point worth more than the finding:** this is the second time in this run that a
> deliberately adversarial check overturned something I believed. The cold plan critic killed a DC5
> numerator that could not lose; the g1 reviewer killed this. Both were cheap. Neither would have
> fired if I had reviewed my own work.

**Branch taken (as first measured, and later corrected — see above): NOT picked up live.**

The probe was built with a control on each side, because "the tool isn't there" and "the probe was
broken" look identical otherwise.

| # | What was run | Result | What it rules out |
|---|---|---|---|
| 1 | Minimal one-tool MCP stdio server (`probe_ping`), driven by hand over stdio | `initialize` + `tools/list` answered correctly; start-marker file written | The server itself being broken |
| 2 | Wrote project-scope `.mcp.json` at the live session's project root, then searched this session's tool list for `probe_ping` | **Absent** | — |
| 3 | Same search, for a tool known to exist (`mcp__claude_ai_Gmail__authenticate`) | **Found** | The search mechanism being broken. Step 2's absence is real. |
| 4 | `claude mcp list` in a fresh process | Lists `probe: … - ⏸ Pending approval (run \`claude\` to approve)` | The config being malformed or unreadable. It is valid and seen. |

**The inference I drew from step 4, which was wrong.** I read `⏸ Pending approval` plus the unwritten
start-marker as "a project-scope `.mcp.json` cannot serve a cold or headless agent at all", and built
the plan on it. **That inference is false** — see the CORRECTION box above. Steps 1–4 are all
faithfully reported and all reproduce; the error was entirely in what I concluded from them. The
missing step was an arm that dispatched headlessly against the plain project-scope file **with
`--allowedTools`**, which is the flag that opens the ordinary per-tool permission gate. I never ran
it, so I never saw the server serve.

**Both delivery paths work, and this was verified end to end:**

```
# per-dispatch, private instance
claude -p "<task>" --mcp-config <generated>.json --strict-mcp-config --allowedTools "mcp__spine__spine_status"

# plain project-scope .mcp.json, no generated file at all
SPINE_FILE=<path> claude -p "<task>" --allowedTools "mcp__spine__spine_status"
```

Both reach the server, launch it, and return real engine output. `--strict-mcp-config` additionally
ignores all other MCP configuration, which is what makes an instance private. `settings.json` was
never touched at any scope, so `decision:settings-json-untouched` holds throughout.

This also satisfies the headless **permission-model** probe `commander-core.md` requires at
`understand`: a headless agent has no interactive approver, so a tool needing approval is silently
denied and the agent produces nothing. `--allowedTools` is what avoids that — and my failure to pass
it in one arm is exactly the trap that doctrine warns about, landing on me rather than on a crew.

**Consequence for the build, as finally settled:** the project-scope `.mcp.json` is the primary path
and now carries `${VAR:-default}` expansion so a dispatcher can rebind `SPINE_FILE`/`SPINE_SESSION`
per agent. `gen_mcp_config.py` ships but its **necessity is unproven** and is what blocks
`g1-integrate`.

---

## Baseline corrections against the order's assumed framing

- **The two-flavoured `advance` does not exist.** A2 shipped the line between *verbs*:
  `TRIP_HARD_GUARDED_VERBS = {start, reopen}`. `docs/agents/GLOSSARY.md` already carries this.
  Typing what the engine has; #424's body is superseded per the launch order.
- **`archive.c2b`'s `<branch>` placeholder bug (#439) is already fixed** in the spine template this
  run drives — the check resolves the branch with `git rev-parse --abbrev-ref HEAD` and accepts OPEN
  **or** MERGED (which is also #446). Two of the four engine bugs F must hold constant across arms
  are therefore already constant, fixed before both arms rather than between them.
- **`docs/agents/engine-config.json` does not exist.** Recorded as a context-step substitution.
- ~~**No architecture map exists** (`docs/architecture/` absent).~~ **Also wrong, and the tool is why
  — see the triage candidate below.** `map_orient` returned DEGRADED-NO-MAP and I discharged it with
  five hash-pinned substitutes, two unmapped statements and an escalation. A current, enforced code
  map was sitting at `map/INDEX.md` the whole time; the tool never probes there.
- **The engine exposes 18 verbs.** The prototype's 7 tools reach 11 of them; `heartbeat, skip,
  reopen, append, amend, waive, attach, flag-candidate` are uncovered and need either coverage or a
  documented CLI fallback (spec F "Fixed": every uncovered verb keeps one).

## What shipped at g1 — the door

`scripts/mcp_spine_server.py`: zero-dependency stdio JSON-RPC 2.0, **7 tools covering 13 of the
engine's 18 verbs**, every tool building an argv and calling `checklist_engine.main()`.
`git diff -- scripts/checklist_engine.py` is **empty**, which is the mechanical proof that no engine
logic was duplicated.

| Tool | Verbs |
|---|---|
| `spine_status` | `current` (read-only) |
| `spine_lease` | `claim` \| `release` \| `heartbeat` |
| `spine_start` | `start` |
| `spine_advance` | `advance` |
| `spine_evidence` | `attest` \| `attach` \| `waive` |
| `spine_halt` | `block` \| `resume` |
| `spine_survey_result` | `record` \| `consolidate` (survey plans only) |

Uncovered, with a CLI-fallback table in the module docstring: `skip`, `reopen`, `append`, `amend`,
`flag-candidate`.

**The grouping judgement came back better than I specified it.** I told the crew the prototype's
uncovered set was wrong because `attach` and `waive` are load-bearing — a door without `attach`
cannot satisfy a `user-decision` checkpoint, and one without `waive` cannot close a gate whose check
the principal accepted as non-blocking. I expected that to cost tool slots. Instead the crew folded
`attest`/`attach`/`waive` into a single `spine_evidence` tool (all three apply evidence to a
condition; they differ in argument shape, not concern) and slipped `heartbeat` inside `spine_lease` —
fixing the named defect while staying at seven.

Also shipped: `scripts/gen_mcp_config.py` (per-dispatch config, keyed `session_id#agentId`),
`.mcp.json` (project scope, pointed at a throwaway demo spine so opening this worktree interactively
cannot mutate real run state), and `tests/test_mcp_spine_server.py` (24 tests).

**A regression the crew missed and I caught by re-running rather than trusting.** The crew reported
the pinned red set unchanged at 6. I measured **7**: adding two scripts made `map/INDEX.md` stale and
turned `tests/test_code_map.py` red. Rebuilt with `python -m scripts.code_map build --root .`; set
back to exactly the pinned 6 at **2157 passed**. This is the plan smell `commander-core` warns about
— a new artifact family whose validity another layer enforces — and my handoff never mentioned the
code map, because I did not know it existed. Which is the next finding.

## `map_orient.py` reports DEGRADED-NO-MAP on a repo that has a map

This repo carries a machine-generated code map at **`map/INDEX.md`** (55 modules, 1047 entities),
with a freshness test that fails if it is not rebuilt. `map_orient.py` never finds it: it probes
`docs/architecture/generated/map.json`, `docs/architecture/index.md`, `docs/architecture/`, then
falls back to `README.md` / `AGENTS.md` / `CLAUDE.md` / a `docs/` index. **`map/` is in neither
list.** So the tool returned `DEGRADED-NO-MAP`, I planned as if map-blind, and the substitutes I
hash-pinned were doctrine files rather than the structural map that was sitting right there. The g1
reviewer independently flagged the same thing. Triage candidate, not fixed.

## Workflow friction observed so far (feeds the return's item 8)

- `attest` on an engine-checked (`kind: command`) condition is **refused**, but nothing in the
  projection marks which conditions are engine-checked — the `current` output shows
  `c0 [unmet] command` and `c1 [unmet] null` in the same shape. I spent a round-trip attesting two
  conditions the engine intended to check itself. This is precisely the DC5 fumble class: well-formed
  call, wrong verb for the condition kind, cost paid by the agent doing the real work.
- `docs/agents/CREW_CONTEXT.md` still says "use `python`, **not** `py` — `py` has no pytest" and is
  Windows-framed throughout. On this host the launch order's measured fact governs: both shims
  resolve to the same venv (3.12.3, pytest 9.1.1). Stale corpus text, named not fixed.

---

## Two claims of mine that review falsified

Both were caught by checks I had built specifically to catch this class of error, which is the part
worth carrying forward.

**1. The delivery finding (falsified at g1-review).** Covered in the CORRECTION box above.

**2. Its replacement justification (falsified on re-review).** Having lost claim 1, I argued
`gen_mcp_config.py` still earned its place because a single shared `.mcp.json` "cannot" give a parent
and a subagent different spines or key identity per agent. The reviewer showed that is also too
strong: Claude Code's MCP config supports **`${VAR}` environment expansion**, sourced from the
*calling process's* environment at launch. I verified it myself — two headless dispatches, same
directory, same committed `.mcp.json`, **no** `--mcp-config`, differing only in the calling shell's
environment, returned two different spines with imperatives verbatim.

I shipped the fix the reviewer named: `.mcp.json` now uses `${SPINE_FILE:-<default>}` and friends, so
a dispatcher rebinds per agent while an interactive session still lands on a safe demo spine. The
guard test was updated to assert that form and was **demonstrated able to fail** (reverted to a
literal, asserted the mutation applied, watched it go red, restored).

**The process point.** Two adversarial checks, two overturned beliefs, both cheap. The cold plan
critic killed a DC5 numerator that could not lose; the g1 reviewer killed the delivery claim and then
its replacement. Neither would have fired if I had reviewed my own work. The cost of both was a
fraction of one crew dispatch.

## Why g1-integrate is blocked, and the plan defect behind it

The BLOCK is on the **justification** for `scripts/gen_mcp_config.py`, not on the code — every
protected-intent item was independently verified and holds, and `git diff -- scripts/checklist_engine.py`
is empty.

The open question is whether per-dispatch generation is **necessary**. It turns on exactly one
unmeasured fact:

> Does an in-session Task-tool subagent share its parent's already-launched MCP server?

If it does, `${VAR}` expansion cannot reach it (the server was launched once with the parent's
environment) and per-dispatch generation is required. If it spawns its own process, generation is
redundant and `${VAR}` is the whole answer.

**That fact is DC3** — "a subagent dispatched with no special configuration gets a refusal or no
identity, never the parent's lease". This plan places DC3's evidence at gate `g3`.

**So the plan defect is mine and it is structural: I ordered the claim at `g1` and its evidence at
`g3`.** The gate cannot legitimately close on its own evidence, which is why it is blocked rather
than waived. Floated to the Admiral rather than worked around.

## Done-condition verdicts

| DC | Verdict | What decides it |
|---|---|---|
| **DC1** — cold agent reaches done, zero malformed calls | **Partial** | A throwaway spine was driven to DONE through the seven tools alone, exercising all of them. Not yet a *cold* agent on a *real role* spine, which is what DC1 asks. Kept as the smoke test the spec says it is, and not leaned on. |
| **DC2** — separation | **Partial** | Two different spines served concurrently off one config, each returning its own reading (my `${VAR}` verification is itself DC2 evidence). The formal parent-and-subagent test with own instances and non-colliding leases is `g3`, not reached. |
| **DC3** — inheritance fails closed | **Not met — not measured** | `g3` not reached. This is the gap that blocks `g1-integrate`. Note the positive control the spec demands is *already satisfiable*: the door is provably up and serving, so a later no-identity result can legitimately count. |
| **DC4** — same-gate equivalence as a property | **Partial** | Byte-identity proven for a sampled gate, with a negative control the reviewer mutated, watched go red, and reverted. That is the **sample**; the spec is explicit that the **population** is the point ("one gate matching once establishes nothing"). `g2` builds the property; not reached. |
| **DC5** — spine-management cost falls attributably | **Not met — not measured** | `g4` not reached. The measurement design is complete and hardened, and is the most reusable artifact this run produced — see below. |
| **DC6** — governor instruction arrives via tool result and is acted on | **Not met — not measured** | `g4` not reached. |

**The honest-null clause does not apply.** A measured negative would have been a complete
deliverable; this is an **unmeasured** one, which is not the same thing and is not being dressed up
as one.

## The DC5 measurement design survives even though the measurement did not run

The cold critic's sharpest finding, and worth more than the gate it was aimed at: **counting DC5 from
the server's own call log could not lose.** A malformed call rejected by client-side schema validation
never reaches the server, so the server log structurally suppresses exactly the fumbles the typed door
is credited with avoiding — producing a win regardless of whether the door helps.

The corrected design, frozen in `execute.json` at `g4-measure`:

- **One counting unit identical across arms:** an *invocation attempt* read from the driving agent's
  own record, **including attempts the client rejected pre-flight**. The server JSONL is corroborating
  detail, never the numerator.
- **Order control:** run both orders, because whichever arm runs second benefits from having already
  solved the spine navigation once. Cold agents both arms.
- **Independent re-derivation:** `g4-review` re-derives every headline number from raw records; a
  number that cannot be re-derived is a BLOCK. The crew waiver at `g4` covers the *crew*, not the
  *checking* — those were conflated in my first draft.
- Re-measured CLI baseline (exc-9's 24–27 calls / 2 refusals / 4–7 help-reads are stale and were
  ruled non-reusable); far-side recovery events counted; engine-bug fixes held constant.

## Triage candidates — named, not fixed

1. **`map_orient.py` reports `DEGRADED-NO-MAP` on a repo that has a map.** `map/INDEX.md` is a
   current, enforced code map (55 modules, 1047 entities) with a freshness test. The tool probes only
   `docs/architecture/generated/map.json`, `docs/architecture/index.md`, `docs/architecture/`, then
   `README.md`/`AGENTS.md`/`CLAUDE.md`/a `docs/` index. **`map/` is in neither list.** Consequence:
   this run planned map-first while map-blind, and hash-pinned doctrine files as substitutes for a
   structural map that was present. Independently flagged by the g1 reviewer.
2. **Duplicated-path artifact tree** at `.agent-work/epic-418-followon/epic-418-followon/commander-424/{context,mechanical}/`
   — the work-id segment is doubled. Pre-dates this run; looks like path composition against an
   already-qualified work id.
3. **`attest` is refused on engine-checked conditions, and nothing in the projection says which
   conditions those are.** `current` renders `c0 [unmet] command` and `c1 [unmet] null` in the same
   shape. The knowledge exists — in `EXECUTE_PLAN.template.json`'s `gN-integrate` imperative — but not
   at the spine's early gates where it is first needed. This is workstream C's thesis with a live
   example attached.
4. **A blocking read inside an eager assertion message deadlocks a suite.**
   `assertTrue(x, f"...{proc.stderr.read()}")` evaluates its message unconditionally, so a blocking
   pipe read runs even on the success path. It cost the g1 crew real time and reproduced identically
   under pytest and unittest, which made it look like an environment problem.
5. **The engine refuses to start a non-active gate even when the target gate's preconditions are
   already met and it depends on nothing pending.** `g2-implement` was refused with "start g1-review
   first" although its only precondition was satisfied and attested. Strict ordering is deliberate, so
   this is a design question for the epic, not a bug report — but it forecloses genuine parallelism
   across independent gates and cost this run wall-clock it could not spare.

## Workflow feedback — where the corpus cost me attention

- **`map_orient` is the expensive one** (candidate 1). It did not merely fail to help; it produced a
  *confident negative* that I then built a plan around, discharging a DEGRADED verdict with
  ceremony — substitutes, unmapped statements, an escalation — for a condition that was not true. A
  wrong answer delivered with that much process is worse than no answer.
- **`docs/agents/CREW_CONTEXT.md` is stale and Windows-framed**: "Use `python`, **not** `py` — `py`
  has no pytest", plus MAX_PATH and CRLF guidance. On this host both shims resolve to one venv
  (3.12.3, pytest 9.1.1). The launch order's measured facts governed, but a crew reading the project
  delta file directly would be misled.
- **The engine's own refusals are the best available advertisement for F.** My very first two engine
  calls were refused for attesting engine-checked conditions (candidate 3), and I could not have known
  from the projection. That is precisely the fumble class a typed interface absorbs, observed on the
  agent this epic exists to protect.
- **The `verify-frame` gate pushed me toward mislabeling.** It refused four `decision:<id>` citations
  because a DEGRADED run has no map for an anchor to belong to. Those four were *launch-order
  pre-rulings*, not map anchors — so the check was right that they are not map members, but the repo's
  own `@grade:` doctrine uses `decision:` grammar for decisions generally. The honest fix was to
  relabel them as pre-rulings and carry the `decision:` ids on the gates in `execute.json`. A less
  careful agent would have deleted the prefix to satisfy the parser and called it done.
- **What worked, and worth keeping:** the cold plan critic and the reviewer re-verification clause I
  added on its advice. Both were cheap, both fired, and both changed the outcome. The launch order's
  pre-settled facts (the prototype's git object, the Linux correction, the pinned red set, "type what
  the engine has, not what the issue predicted") each saved a discovery round-trip — the run would
  have been materially worse without them.

## For whoever picks this up

The next action is **not** to rebuild anything. It is to run `g3` and answer one question: *does an
in-session Task-tool subagent share its parent's already-launched MCP server?* That single fact
unblocks `g1-integrate`, decides whether `gen_mcp_config.py` stays or is deleted in favour of the
`${VAR}` path already shipped, and is DC3's evidence either way.

The spine is at `.agent-work/epic-418-followon/commander-424/` **inside the worktree**
`/home/tommy/projects/constellation-skills-wt/f-424`, lease released, `g1-integrate` blocked with the
reason recorded. `execute.json` carries the frozen, critic-hardened plan for `g2`, `g3` and `g4`, and
the handoffs for `g2-implement` and `g3-implement` are already written under `crew-handoffs/`.
