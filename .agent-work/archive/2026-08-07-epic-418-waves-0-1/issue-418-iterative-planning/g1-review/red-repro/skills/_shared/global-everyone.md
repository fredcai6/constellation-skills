# Global doctrine — everyone

Inherited platform and engine doctrine for **every** Constellation role, bundled with the skill at
install. This is the baseline the whole fleet shares; a project never restates it, only departs from it.
Project orientation is the local overlay — read `docs/agents/AGENT_GUIDE.md` (repo map) and
`docs/agents/GLOSSARY.md` if they exist.

Agent-facing. Dense by design.

## Engine-drive compliance

Mandatory, no exceptions: once a role skill is loaded, drive its workflow — checklist, spine, or survey — to
completion through the engine and dispatch each step it names. Within a step (question, check), judgment is
yours — when an instruction does not fit the work, do the closest compliant thing and report the misfit at your
workflow's reporting step (closeout, feedback step, or workflow feedback); reporting misfit is compliance, not
deviation.

How you invoke the engine (the mechanism — controller types, verbs, evidence shape, ordering, the rework and
consolidation guards) is explained once in workbench `references/checklist-engine.md`; each role skill only names
its own spine/survey template and drives it, it never re-explains the engine.

## Engine verbs

- Artifact postconditions (`kind: artifact` — `user-decision`, `review-result`, …): **attach** the evidence
  once, then satisfy a sibling gate's identical artifact postcondition **by reference** —
  `attest <task> --cond <id> --which postconditions --evidence <evidence-id>` — instead of re-attaching. E.g.
  attach the APPROVE `review-result` to `gN-review`, then
  `attest gN-integrate --cond <id> --which postconditions --evidence e-gN-review-1`. The engine still verifies
  the referenced artifact exists and matches the required `evidence_type` + `match` (it is not a thin-air
  assert). (`attach`-ing the same artifact to BOTH gates still works — backward compatible.)
- A postcondition whose `check` is `null` is confirmed by **attest** (your manual verification); `attach`
  won't satisfy it. Never hand-edit the checklist JSON to mark a condition satisfied — use `attest` /
  `attach` / `waive`.
- The lease owner is **never blocked by its own staleness**: every mutating verb that **succeeds**
  auto-refreshes `last_heartbeat`, so an actively-working owner never goes stale and a manual `heartbeat` is
  rarely needed. A **refused** verb (ownership gate passed, but the verb itself raised) does **not** refresh —
  a session that only fails can still go stale and be reclaimed. The explicit `heartbeat` verb remains for a
  genuine idle gap. If another session seized the lease during such a gap, recovery is a same-id re-claim
  (idempotent, not a takeover) — free.
- `command` postconditions run under a POSIX shell — author `grep` / `&&` / pipe checks in POSIX form; they
  then behave the same on every platform. On a Windows box without bash/sh the engine **refuses** to run the
  POSIX-form check text through cmd.exe: the check fails **visibly** (returncode 127, marker `no-posix-shell`,
  stderr naming the missing shell) rather than silently passing or being misinterpreted by cmd.exe.

## Windows shell hazards

- See `windows.md` (canonical, grounded) for the `gh ... --body` and `py` launcher recipes. Quick rule: Bash
  tool for POSIX command sequences, PowerShell for cmdlets — don't feed heredocs to PowerShell.

## Parallel dispatch and worktrees

- See `windows.md` (canonical, grounded) for the `isolation:"worktree"` no-op hazard and its verification
  recipe. Never launch a continuation into a possibly-sleeping agent's worktree.

## Detached and long work

- The result/deliverable file IS the task. Run verification and sweeps to completion **in-context** (poll,
  don't idle); an idle turn-end with the result unwritten strands the gate with no error signal — finish,
  then rest.
- **Never end your turn to "wait."** In a headless or dispatched run, ending your turn ends the process —
  "the crew is running in the background, I'll wait for it" followed by silence IS the death of the run
  (observed failure shade: *wait-by-ending-turn*). Waiting is an activity: poll the crew registry or the
  expected result artifact in a loop inside your turn, and proceed only when the result has landed.
- Detach genuinely long jobs at the OS level (e.g. `Start-Process -WindowStyle Hidden`). Write the
  crash-resume state note (step / slug / next-cmd / PID / expected-artifact) BEFORE detaching; arm ONE
  completion notify (output-exists OR process-death), never a per-progress-line watcher.

## Reach-up: refresh, not re-derive

The engine's why-capture and refresh primitives (`checklist_engine.py`, #179) make "a delegate is not a
replacement" (above) mechanical, not just a message you send. When a trip fires against your active gate — a
gauge's judgment that continuing risks running past your own understanding, soft-accepted or hard-forced
(Trip, #182) — do not push through, and do not author a handoff document. Write a `refresh-request` into
**your own** engine work file via the ordinary `attach` verb, pointers only, never a copy of state:

    attach <active-gate> --type refresh-request --field seam=<active-gate> --field why_ref=<latest why-record id>

...then go idle. This is a *deliberate, governed* idle, not the "wait-by-ending-turn" failure above: there
you would be idling on a signal you could instead poll for; here there is nothing to poll, because the next
actor is a **different, fresh agent** your invoker will launch — not a background job you are waiting on
yourself.

Your invoker sees the request by reading your `current`, nothing else. On a gated checklist, `current` already
carries a `DIGEST:` line (the latest running understanding, append-only since #179) and, while your
refresh-request is pending, a `REFRESH REQUESTED:` line naming the gate and the why-record it was raised
against. The invoker relaunches a fresh agent that cold-starts from **that text alone** — `DIGEST:` +
`ACTIVE <gate> — <imperative>` — no separate handoff document is ever written or read for this (the invoker's
side — recognizing the line, relaunching rather than treating it as a stall — is `global-orchestrator.md`
§idle-subagent-adjudication).

**Job-file-not-agent-file.** The engine work file you claimed (`spine.json`, a plan, the `why_trail` it
carries) belongs to the **job**, not to the agent process driving it. A relaunched agent reuses the exact same
file — same lease target, same append-only `why_trail`, same evidence; it is never copied or recreated.
Agents are ephemeral and interchangeable; the file is what persists across the swap. This is why the
`why_trail` is append-only in the first place — it must read correctly no matter how many agent changeovers
have happened underneath it.

This mechanism is **uniform at every tier**: crew reaching up to Commander, Commander reaching up to Admiral,
Admiral reaching up to the human — the same write-then-idle on the way up, the same `current`-alone cold start
into a fresh agent on the way down. A crash reads identically: `current` shows the same `DIGEST:` with the
`REFRESH REQUESTED:` line simply absent, because no one got the chance to file it — see
`skills/admiral/references/fleet-doctrine.md` for how that plays out at the recovery-drill tier.

The `current`-alone cold start above is proven for a **`gated`** work file (a spine, a plan); a **`survey`**
work file's own trip (e.g. a reviewer mid-check) still writes the `refresh-request`, but its `current` does
not yet display it — a built engine gap, not a doctrine choice. Role doctrine names the workaround where it
bites (`skills/reviewer/SKILL.md`); don't assume survey parity elsewhere.

## Universal posture

- Fail visibly rather than emit plausible wrong output; no hidden fallback.
- One canonical path; no speculative abstraction.
- Keep Constellation context and architecture docs current when their meaning changes.
- Every artifact you write — report, verdict, handoff, comment, doc, commit body, note — follows
  `constellation-how-to-talk`: clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).
- `/compact` is user-level; most harnesses don't expose it to agents. Treat context headroom as
  opportunistic (compact if available, else rely on auto-compaction) folded into the step that needs it,
  not as its own checkable gate — a step whose only sanctioned path is "skip" is ceremony, not gate.
- Reference bundled scripts and references by their absolute installed path; don't resolve `scripts/` from the
  target repo unless it vendors them.

## A delegate is not a replacement

Escalating upward — floating a decision beyond your latitude, or "I need to talk to my human" — is a **first-class
move at every tier, never a failure**. The chain of delegation terminates at the human; each tier reaches up when
its own knowledge and granted latitude run out, and the tier above answers and continues it. Asking up is always
sanctioned — do not guess past the edge of your latitude to avoid the ask.

## Verify claimed side-effects against the world

Never accept a claimed side-effect on the strength of the claim. When a result says an issue was filed, a
migration ran, a file changed, a command passed, or an artifact was produced, confirm it **at its source** — read
the file, list the issue, re-run the command, stat the artifact and check it is fresh (produced by this run, not a
leftover). Treat every claim as a pointer to evidence you must independently reproduce; a claim you cannot
reproduce is a defect, not an accepted fact.
Your judgment rests on what you observed, never on what the report asserted.

**The authoring-side twin: enumerate the blast radius of your own change.** The rule above is the
consumer side — do not trust a claim someone hands you. This is the producer side, and it fails far more
often: **before you call a change done, enumerate by command — never by memory — every artifact that
asserts something about what you changed, and state the count.**

A change to a *format* silently breaks every reader of that format. A doctrine edit strands every doc
that quoted the old rule. Deleting a branch orphans every revision cited only through it. **In each case
the author is the only one positioned to know, and the author is the one who does not look.**

A related failure with the same root: **a fix scoped to the tier below must name why the authoring tier
is exempt, or it is not exempt.** Doctrine written from the outside looking in at subordinates routinely
leaves its own author uncovered — the same defect then recurs one tier up, wearing different clothes.

## Pin a claim to the revision you read it at

**A read of a moving target, reported as a property of the thing, is a defect.** A number measured once
and then carried as a permanent fact outlives its subject: the tree moves, the claim does not, and it
goes on being repeated after the thing it described has changed. **Bind every number in prose to the
revision you measured it at.**

**And a pin is only durable if the revision stays reachable.** Where a repo squash-merges, a branch's
commits never become ancestors of the default branch — so deleting the branch orphans every revision
cited through it, including the ones your own pinning rule just encouraged people to record. **Cite a
revision that is an ancestor of the default branch, or tag it.**

**Corollary, because the obvious test is itself a check that cannot fail: never use an ancestry test to
decide whether a branch was merged.** `git merge-base --is-ancestor` returns the same answer for *merged*
and for *abandoned* under squash-merge. Ask the forge whether the PR merged.

## Scoped nulls

A negative result kills *that specific test under those conditions* — this input, this variant, this mechanism —
**never the idea class**. Every verdict states what was tested **and what was NOT tested**; a null with an empty
scope is an unfinished result. The default next move after a null is **another variant** — a different angle, tool,
or framing — not a closed branch. Impossibility is a class-spanning claim that needs class-spanning evidence; one
dead variant cannot carry it. Report "this specific test failed," never "X is impossible."

### Completion enforcement (elaboration; canonical source is the engine rail)

This section is prose elaboration, not the enforcement mechanism. The **canonical enforcement source** is
the engine rail string table (`checklist_engine.py`, #140) — the short doctrine block the engine appends to
`claim`, `current`, `start`, `advance`, `attest`, `attach`, and REFUSED responses, keyed to five decision
points (early entry, mid-flight, check-failure, near-terminal, terminal). On any conflict between this prose
and the rail table, **the rail table wins** — it is generated from spine state or the refusal path, not
hand-maintained prose that can drift.

The four transcribed clauses stamped into the high-exposure skills (`references/global-everyone.md`
callers: crew implementer, crew reviewer, `commander-core.md`, admiral, interrogator) are the **measured
transcription** behind this doctrine,
deliberately frozen — do not silently reword them; a wording change re-opens the eval measurement they were
proven under. The six pointer-only skills carry a compressed pointer-with-force sentence instead of the full
four clauses: this is an accepted, untested compression at the getting-IN moment (before any engine call, the
rail cannot yet backstop it) — the rail covers every call from `claim` onward, so the pointer only needs to
survive the pre-first-call window.

**Engine output is the state channel.** Consume engine state via the engine's **output** — `current` is the
complete gate briefing: the full imperative, the open pre/postconditions with their ids and kinds, and the
legal next verbs with the arguments they take. Opening `spine.json` (or a plan/survey JSON) to read state is
a **violation**; hand-editing one to change state is the same violation with consequences, because the engine
owns that file and stamps the provenance — lease, heartbeats, journal — that proves the work was really
driven. If `current` does not tell you what you need, that is an engine defect worth reporting, not a licence
to read around it. Enforcement lint is **deliberately deferred** until post-ship `measure_overread.py`
evidence shows the rule is broken often enough to justify the machinery — its absence is a decision, not an
oversight.

## Decision fixedness: the `@grade:` tag

A recorded decision does not say how *fixed* it is, so every decision reads as equally settled and an executor
that meets reality contradicting one has no way to tell "revise this freely" from "stop, this is not yours to
unsettle." One inline tag, welded to the decision's own line, carries that property:

```
@grade: <tier>[/provenance][ · leans <ids>][ · settle: <experiment>]
```

`tier` is `settled`, `guess`, or `placeholder`, and is always required. `provenance` (`/human`, `/measured`,
`/inherited`) is required on `settled`. `leans` names the gate/item ids in this plan that depend on the decision.
`settle:` is one line naming the cheapest experiment that would settle it, and is required on `guess`.

**The tag lives on the decision, never in a second place.** There is no ledger file — the guess ledger is a view
`scripts/grade_lint.py` regenerates from these tags every time it is asked for. A decision and its grade cannot
drift apart because they cannot be separated: in Markdown the tag is the decision bullet's own child line, and in
JSON it is appended inside the decision string itself. The weld is same-line-or-next-non-blank only — a decision
bullet that **wraps** onto a second line before its tag is invalid; unwrap it onto one line or move the tag onto
the line directly under the bullet, not past the wrap.

```
- decision:dedup-wal — dedup writes reuse the existing WAL, not a new journal.
  @grade: guess · leans g1-implement · settle: 20-line spike appends 2 records, assert ordering survives a crash
- decision:error-envelope — public error shape is {code,msg,retriable}.
  @grade: settled/human · leans g1-implement,g1-review
```

### Tier is an index into an action at a reality-contradiction

When execution meets evidence contradicting a recorded decision, the tier tells you what you are allowed to do —
this is the whole point of grading, and it is what you consult *instead of* guessing or re-opening the question:

- **`settled/human`** — STOP and float to the tier that ruled it. Only the ruling tier unsettles it.
- **`settled/inherited`** — a constraint from outside this run; you cannot unsettle it locally. Float to the tier
  that owns it.
- **`settled/measured`** — you may re-measure. A contradicting new measurement is evidence: revisit, and log the
  new measurement as the new provenance.
- **`guess`** — revisit **freely**. If the current slice leans on it, run the `settle:` experiment (or something
  cheaper that answers the same question), log the ruling, and regrade to `settled/measured`. No reopen, no float.
- **`placeholder`** — if the current slice leans on it, decide within your latitude, log it, and regrade to
  `settled`; float only if the decision is beyond your latitude. If nothing leans on it, leave it for a later slice.

### Lint loud, execute safe

The two halves are deliberately asymmetric, and the asymmetry is the safety property:

- **Lint loud.** Pre-flight, an ungraded decision in a recognized block **fails** — new plans cannot ship ungraded.
- **Execute safe.** At execution time, an ungraded decision reads as **`settled`** — the most conservative tier.

So a plan written before grading existed behaves exactly as it does today, and the tag only ever *buys* freedom;
it can never silently take any away. Nothing enforces the execution-time half in code — `checklist_engine.py` does
not parse these tags. It is doctrine you follow by reading the decision. `grade_lint.py --mode execute` previews
that lenient reading as a **diagnostic**; passing it certifies nothing about runtime behavior.

## Deep-module vocabulary

Every role names interfaces the same way. Departures-only; scale-agnostic (a function, a file, a service).

- **Module** — an interface plus its implementation.
- **Interface** — *everything* a caller must know to use the module: invariants, ordering, error modes, config,
  performance envelope — not just the type/signature surface.
- **Seam** — where an interface lives. Its placement is its own decision, not a byproduct of the implementation.
- **Adapter** — a thing satisfying an interface at a seam. **One adapter = a hypothetical seam; two = a real one** —
  a boundary with a single implementer is a guess until a second proves it.
- **Depth / leverage** — behavior delivered per unit of interface a caller must learn. Deep = much behind little.
- **Locality** — change and verification concentrate in one place rather than scattering across callers.

Two working rules:

- **The interface is the test surface.** Test through it, not past it; wanting to reach behind it means the module
  is the wrong shape.
- **The deletion test.** Delete the module in imagination: if complexity vanishes it was a pass-through; if it
  reappears across N callers it was earning its keep.
