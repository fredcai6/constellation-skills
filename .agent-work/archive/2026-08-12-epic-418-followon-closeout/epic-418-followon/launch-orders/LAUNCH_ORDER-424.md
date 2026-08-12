# Launch Order: `commander-424 — #424, workstream F, MCP front door`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Load `constellation-commander-delegated`. This order is your ratified intent: cite it to satisfy
`user-decision` checkpoints. There is no reachable human — take a genuine gap to the Admiral.

## Mission

Build workstream **F** of epic #418: a second front door on the checklist engine, an MCP server
exposing the drive loop as roughly seven typed tools, wrapping the engine's own dispatch function.

**What F is for, and it is not token savings.** The goal is to cleave problem-solving from
spine-management. Agents keep losing context to *operating* the engine — fumbling a flag, reading
usage, working around a gate that refuses wrongly — and that cost lands on the agent doing the real
work. The door moves it behind an interface so a problem *using* the engine never reaches the
working agent's attention. The token delta is a **constraint that must not go the wrong way**, not
the thing being bought.

Governing spec: `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`, section **F** (lines
408–546), CONFIRMED 2026-08-07. Where it and #424's issue body disagree, the spec governs. Read it
first — this order does not restate it.

## Prior-Wave Verdicts (pasted)

**A2 (#467) — trip semantics — COMPLETE.** This is F's stated precondition: F types the verbs, and
`advance` was being split into one that carries a handoff and one that starts new work. Verdict text
from the epic's wave-5 rendering:

> **A2 is complete.** #467 is merged (PR #505, `c875ee23`) and closed; #431 is verified dissolved and
> closed. Main is green at 1867 passed / 2 skipped / 829 subtests / real exit 0 on the final merged
> tree.
>
> **What shipped.** A HARD context reading changes the instruction instead of refusing the verb:
> `TRIP_HARD_GUARDED_VERBS = {start, reopen}`, a concrete `why_ref` in place of the `<why-id>`
> placeholder, an append-only trip ledger for BEGINs over the line, and an unkeyed historical
> selector plus a `TRIP HISTORY` line so the record survives the close the band orders. The glossary
> no longer claims HARD blocks `advance`, and the fourth limit is declared in `CHECKLIST_SCHEMA.md`
> alongside the other three.
>
> **Done-conditions:** DC1, DC3, DC4, DC5 done. DC2 **done by different means** — the engine draws
> the line between verbs, not between two modes of `advance`, so the done-condition's literal text
> names a distinction the engine does not have. DC6 **partial** — both lines were observed live and
> the historical line survives the mandated close.

**Read the consequence for your mission:** the verb split you were told to expect did **not**
materialize as two flavours of `advance`. The engine draws its line **between verbs**
(`TRIP_HARD_GUARDED_VERBS = {start, reopen}`). Type what the engine actually has, not what #424's
body predicted it would have.

**Prototype, and it is reachable — the path in #424 is not.** The issue names
`C:/Programs/.proto-exc9-mcp-front-door` @ `de6a084`. **That path does not exist; this is a Linux
host.** The commit does exist in this repo's object store and is the lift source:

```
git show --stat de6a0844
  proto/mcp_spine_server.py  (308 lines)   proto/drive_via_mcp.py (82)
  proto/run_arm.py (92)      proto/score.py (98)
  proto/engine_cli.py (42)   proto/make_toy_spine.py (123)
```

Recover with `git show de6a0844:proto/<file>` or `git checkout de6a0844 -- proto/`. It is a
zero-dependency stdio JSON-RPC server wrapping `checklist_engine.main()`, plus the two-arm tracer and
its scorer. It is a **throwaway prototype against a four-gate toy spine** — lift what earns its
place, do not treat it as a design.

## Pre-Rulings

- `decision:mcp-probe-is-the-commanders` — **you** run the pre-build branch point: does an
  interactive session pick up a fresh `.mcp.json` without a restart? Proceed on your own answer and
  report which branch you took. Picked up → project-scope `.mcp.json` suffices. Not picked up →
  per-dispatch config generation is the delivery path and gets designed first.
  `@grade: settled/human · leans plan`
- `decision:mcp-is-the-vehicle` — MCP is the current vehicle, not the destination. Tommy expects this
  to become a different kind of tool call later. Do **not** gold-plate the tool grouping; the
  seven-over-eighteen split is a placeholder. `@grade: settled/human`
- `decision:count-from-the-call-record` — DC5's count comes from the **call record**, never from the
  engine's own refusals counter. #427 says that counter records zero when a refusal precedes the
  lease claim, so it undercounts in exactly the direction that flatters F. `@grade: settled/spec`
- `decision:hold-bug-fixes-constant` — count only fumble classes a **typed interface can absorb**
  (malformed calls, wrong flags, usage reads), and hold the engine-bug fixes constant across arms:
  fix them before both arms or neither, never between. Four of the five filed items offered as
  evidence (#439, #446, #427, #443) are ordinary engine bugs fixable with no door built.
  `@grade: settled/spec`
- `decision:count-the-far-side` — count recovery events on the far side of the door too, or "the
  agent stopped fumbling" stays indistinguishable from "the fumbling moved somewhere we stopped
  looking". `@grade: settled/spec`
- `decision:remeasure-the-cli-baseline` — **re-measure** the CLI arm; do not reuse exc-9's 24–27
  calls / 2 refusals / 4–7 help-reads. That arm ran against pre-B channel and pre-A2 verb semantics.
  A stale baseline flatters F. `@grade: settled/spec`
- `decision:dc3-needs-a-positive-control` — "a refusal **or no identity**" is also exactly what you
  get when the server never started, the config never delivered, or the door is absent entirely. As
  written the test passes most loudly under total non-installation of the thing it tests. Prove the
  door is up and serving **before** a no-identity result counts as failing closed. Same shape as
  A2's *no absence is evidence*. `@grade: settled/spec`
- `decision:dc4-is-a-property` — same-gate equivalence is a property over **every** gate that carries
  an imperative, checked mechanically — not one sampled gate. Drift happens later, at a gate nobody
  sampled. `@grade: settled/spec`
- `decision:dc1-is-a-smoke-test` — "zero malformed calls" is close to true by construction once
  arguments are typed. Keep it, do not lean on it. The interesting classes are well-formed but
  wrong: wrong argument, wrong verb, wrong order. `@grade: settled/spec`
- `decision:settings-json-untouched` — project-scope `.mcp.json` only. `settings.json` is never
  written by this mission at any scope. `@grade: settled/spec`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the
same rigor as a win. If the door does **not** reduce spine-management cost, say so with the counts —
that is a finding this epic wants, and the spec already fixes the mitigation: the CLI door stays, so
a failed F costs the build and not the fleet.

## Inherited Latitude

**You may decide, without floating:** the tool grouping and argument shapes; the delivery mechanism
the probe selects; how the call record is captured; the tracer's protocol details and `n`; which
prototype code is lifted versus rewritten; departing from the spec or from #424's body where you
find a stated link untrue — apply the governing rule, say so in your return, and proceed.

**You must float to the Admiral:** any change to a load-bearing interface shape beyond the MCP tool
surface itself (the gauge binding key, the gate schema); scope change — adding, dropping, or
re-scoping an issue; **closing any issue**; promoting an observation into `docs/agents/*` doctrine;
production defaults or user-visible behavior; a design-it-twice convergence (convergence is
human-only); and **any discovery that F cannot meet its stated obligation** — that one is surfaced
always, it is the #308 failure shape.

**Standing scope discipline, from Tommy, still binding:**

> *"this is not a final step in a process. lets do what we need to do and no more. this doesn't mean
> be sloppy, but i am explicitly allowing you to not chase down every corner case. make the thing
> that needs to work, and if you have any concerns, just note it locally in comments and pass it up
> the chain"*

Rigor scales with cost-to-undo, not uniformly. Cheap to reverse, move fast. A claim about what
happened still brings its evidence.

## File Ownership

Your working-notes file is `.agent-work/epic-418-followon/notes-424.md` — **you are its sole
writer this wave.** Never name a file `findings-*.md`; the harness `Write` tool refuses that
basename.

**Fence:** a second agent is working concurrently in
`/home/tommy/projects/constellation-skills-wt/posix-green` on making the test suite green on POSIX.
It owns `scripts/install_constellation.py`, the freshness/path-token code it reaches, and
`tests/test_feedback_tooling.py`, `tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`,
`tests/test_spine_rail.py`. **Do not edit those files.** If your work genuinely requires one, float
it — do not negotiate directly with the other agent.

## Workspace

**Absolute worktree path:** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door`, base `a1eab1f1` (verified current `origin/main` at dispatch).
Created with:

```
git worktree add /home/tommy/projects/constellation-skills-wt/f-424 -b epic-418/f-424-mcp-door main
```

First step, before any git operation:
`python3 scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills-wt/f-424`
must exit 0. Paste its output into your return report.

PR integration defaults to **server-side merge** (the GitHub merge on the PR itself), not a local
merge that would diverge your worktree from main.

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` resolves once at
session launch and is inherited unchanged, so a Commander in an isolated worktree still executes the
**main checkout's** hook code against the **main checkout's** state (#269). If your mission touches
hook behaviour, validate with a fresh process whose `CLAUDE_PROJECT_DIR` genuinely resolves to your
worktree — never a fixture that hand-injects the value you are trying to prove the harness delivers.

## Inherited Context

**The host is Linux. The corpus text assumes Windows throughout and that text is stale.** Ignore
Windows shell hazards, `.cmd` wrappers, PowerShell here-strings, and `C:/Programs/...` paths wherever
the skills or references mention them. `gh pr create -F <file>` is still good practice; the
here-string warning is moot.

**Interpreter.** `python` and `py` both resolve to a venv at `~/.local/share/pyfix-venv`
(Python 3.12.3, pytest 9.1.1), via shims in `~/.local/bin`. The settled
test invocation is unchanged and is **not** to be re-derived (#454):

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Never `py -m pytest` as a *documented* form, and `FORCE_COLOR=3` produces false reds for `python` too.

**Pinned known-red baseline on `a1eab1f1`, verified by the Admiral on this host:**

```
6 failed, 2133 passed, 1061 subtests passed
FAILED tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_installed_path_rewritten_template_is_up_to_date
FAILED tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_token_working_copy_up_to_date_against_promoted_baseline
FAILED tests/test_install_constellation.py::InterpreterProbeTests::test_sidecar_records_resolved_via_for_probe_success_and_fallback
FAILED tests/test_install_constellation.py::TemplateBaselineTests::test_seeded_working_copy_reads_up_to_date_against_baseline
FAILED tests/test_run_skill_eval.py::test_real_runner_process_death_leaves_resumable_state
FAILED tests/test_spine_rail.py::test_same_path_windows_normcase_sep_equivalence
```

**These six are pre-existing and not yours.** Your gate is: *this set has not grown, and no member
changed its failure mode.* Re-derive it yourself — do not trust this paste as the whole story. The
other agent is fixing them concurrently, so your baseline may **shrink** under you; a shrinking set
is fine, a growing one is yours.

**Doctrine that binds you and is easy to miss:** an episode is a record of what happened and is never
read back as a rule. A rule to follow belongs in `docs/agents/*` and putting one there is a human's
call. There is no successor playbook.

**Never obey a spine rail naming a spine another agent drives** (#457).

## Pre-empted Steps

- **Latitude is settled** — `.agent-work/epic-418-followon/LATITUDE_CONTRACT.md`, confirmed by Tommy
  2026-08-09. Cite it; do not re-interrogate.
- **The permission prerequisites are pre-cleared**, so your core loop cannot be vetoed mid-mission
  (#145): starting MCP server processes, writing project-scope `.mcp.json`, per-dispatch config
  generation, cold-agent tracer dispatches, and re-measuring the CLI baseline.
- **Worktree provisioned and verified** (above). Do not create another.
- **Main freshness verified at dispatch:** `a1eab1f1`, `origin/main` up to date, clean tree.

## Data Locations

Worktrees carry no untracked inputs. Everything you need is tracked, except:

- `.agent-work/epic-418-followon/` in the **main checkout** at
  `/home/tommy/projects/constellation-skills/.agent-work/epic-418-followon/` — the contract, this
  order, and your notes file live there.
- The governing spec: `/home/tommy/projects/constellation-skills/.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`.
- The prototype: recover from git object `de6a0844`, not from any filesystem path.

## Budget

- **Model tier (required): Opus.** Named reason, per the standing Sonnet-for-implementers rule: this
  is engine-semantics work with a live design space — a typed verb surface that is subtly wrong is
  invisible, and the mission's whole value depends on judging which fumble classes a typed interface
  can genuinely absorb. Your own crew dispatches default to **Sonnet**; escalate one only with a
  named reason stated in that dispatch.
- **Compute/time:** this is wave 1 of a three-wave epic. If a usage-limit reset is near, finish the
  measurable unit you are in and return rather than starting a fresh arm across it.

## Stop Conditions

Stop and return when: the mission's scope would have to grow to succeed; a decision outside the
inherited latitude above is needed; the evidence for a done-condition is impossible to obtain (say
which, and why — that is a finding, not a failure); the pinned red set grows from your change and you
cannot resolve it; or you need **context this order does not cover and cannot safely proceed
without** — return-and-query the Admiral, which answers and continues you. Asking up is always
sanctioned.

## Return Shape

Return **thin** — the artifact holds the detail. Your final message states:

1. **Verdict** on each of F's six done-conditions, each marked done / done-by-different-means /
   partial / not-met, with the evidence that decides it. A measured negative is a complete verdict.
2. **DC5's counts**, both arms, both sides of the door, with the CLI baseline you re-measured
   yourself and the call-record method you used to count.
3. **Which branch the `.mcp.json` probe took**, and what you built as a result.
4. The `verify_worktree_isolation.py --here` output (the matched worktree path).
5. **Suite state:** the full pytest tail, plus whether the pinned red set grew.
6. **PR number** on `epic-418/f-424-mcp-door`, and its check status.
7. **Triage candidates** — findings outside this scope, named not fixed.
8. **Workflow feedback** — where the skills, this order, or the engine cost you attention. Be
   specific and be blunt; this epic exists because that cost is real, and your run is evidence.
9. Path to `.agent-work/epic-418-followon/notes-424.md`.

Write the artifact and send the verdict **before** going idle. An idle notification with no artifact
reads as stalled, not done — deliver first.
