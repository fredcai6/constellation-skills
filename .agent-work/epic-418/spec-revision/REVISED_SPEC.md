# Epic #418 — revised spec, section by section

Working document. Revises `.agent-work/archive/2026-08-03-explore-post-phase1/DESIGN_SPEC.md`
against what execution actually taught us. Written with Tommy, 2026-08-07.

**Why the original needs revising, in one line:** it was written on 2026-08-03, before this
epic ever dispatched concurrent Commanders, and several of its "by construction" claims have
since been falsified by the epic's own behaviour — not by implementation failures.

Three instances so far, all caught by a Commander departing from the spec and saying so:

- A's unconditional binding sweep would have deleted the Admiral's own live binding mid-run.
- E's issue-count done-condition moves the wrong way precisely when the epic is going well.
- #440's byte-identical-checkout guard is unsatisfiable when two Commanders share a store.

That is the argument for the less-prescriptive relaunch. The spec's durable value is its
intent, its evidence and its boundaries. Its weakest parts are exactly where it pre-committed
to a mechanism.

**Format change.** Each section now states intent, a checkable done-condition, the evidence
that settles it, what is fixed, and what is explicitly the Commander's call. It does not
prescribe the interface. Where the original spec's method survives, it survives as evidence,
not as instruction.

---

## The organising principle (new, cross-cutting)

Reveal the next step, not the whole plan. The same idea at three tiers:

| Tier | Reveal | Hide | Mechanism |
|---|---|---|---|
| Gate | the current gate's instruction | later gates | C, spine-carried instructions |
| Wave | the current wave's issues | later waves | iterative planning (merged 2026-08-07) |
| Epic | a course | a script | the Admiral relaunch |

The motive is not token cost. Quality degrades with context length even when the window has
room, and agents carrying work that isn't theirs yet thrash against it. Token savings are a
side effect.

**What makes this safe rather than reckless:** instructions are gate-local, constraints are
spine-global. An agent that cannot see gate 5 must still be unable to foreclose it. `anchors`
and `constraints` are that channel — which is why B genuinely precedes C, for a better reason
than the original spec's token argument.

**The governor is the seam detector.** It is what says *now* is the moment to stop and hand
off, which is what makes gate-local reveal enforceable rather than merely tidy.

## Appetite (Tommy, 2026-08-07)

This is a one-person project. A reversible mistake that a later run would surface again is not
worth extensive up-front guarding — *"if there's an actual problem, we'll find it again."*
Rigor scales with how costly a thing is to undo, not uniformly.

This licenses lower ceremony on reversible calls. It does **not** license unevidenced claims,
silent scope cuts, or checks that cannot register their own failure. The distinction is:
cheap to reverse, move fast; a claim about what happened, still bring the evidence.

## Standing obligation (new, cross-cutting)

**Each workstream retires the findings it subsumes.** A section that dissolves a filed issue
closes it with evidence naming why the finding no longer exists, as part of its own closeout —
it does not leave it for a later consolidation pass. This is what replaces the epic's falsified
issue-count done-condition, and it is why E can run last on a much smaller input.

---

## A. Context governor — per-agent identity

**Status: stated obligations discharged. Re-scoped by evidence.**

Verified rather than assumed:

- `docs/GAUGE_WRITER_HOOK.md` corrected — 20 `agentId` references, sidechain polarity stated
  correctly (falsy on a main-chain read, truthy on a dispatched agent's own transcript).
- The stale-binding sweeper ran the specified sequence: dry-run with before-state recorded,
  then real against a fresh re-read, then deleted with its path noted. Store went 64 → 1.
  It departed from the spec deliberately and said so: an unconditional sweep would have
  dropped all 64 including the Admiral's own live binding. It spared the one entry with an
  existing spine and an active lease, and reported both counts.
- The done-condition — "a trip fires from a per-agent reading on a live run" — is met, and
  as of #440's g2 acceptance it is met *correctly*: the trip fires from a worktree-dispatched
  agent's own reading, landing beside the worktree spine, against a genuine positive control.

**What the section could not have known to name.** Three things, none of them implementation
failures:

1. **Worktree-correct binding** (#440, in flight). A's interface list covers identity,
   fail-closed, sidechain inversion and the sweep — nothing about *which checkout* a binding
   resolves against.
2. **Multi-spine attribution** (unfiled). A session bound to several candidate spines gets no
   reading at all. The fail-closed invariant is working as designed; the design did not
   anticipate a role that legitimately holds more than one spine. This epic's own Admiral ran
   a full day with the gauge silent. #440's scope will not reach it.
3. **The hook is unwired outside a test rig** (#180). No `PostToolUse` entry for
   `gauge_writer_hook.py` in the user-scope `settings.json`, so "make it fire" is true in
   harnesses and false in ordinary sessions.

**#431 is redesigned, not patched.** Tommy's ruling: the limits exist so there is room to
*build the handoff*, not because continuing is unsafe. So a HARD reading should stop being an
engine refusal and become a change of instruction — the spine says "you did well, write the
handoff and request a refresh to continue." The deadlock (the trip blocks `advance`, which
freezes the DIGEST the handoff depends on) then dissolves rather than needing a fix, because
the agent still advances and the DIGEST is still written.

This requires the engine to distinguish an advance that carries a handoff from an advance that
starts new work, and to refuse only the second. It cannot express that today.

**Thresholds become per-gate, with discipline.** A gate about to read a corpus needs more
headroom than one attesting a condition. Two constraints on how:

- **One default plus overrides only where measured.** Hand-authoring a threshold for every
  gate in 21 templates invents ~100 ungraded placeholders, which is what the original spec's
  threshold discipline exists to prevent. Gates earn an override by biting.
- **The threshold means "fill above which you should not *start* this gate."** The honest
  quantity — headroom this gate needs to finish plus write a handoff — is unknowable until the
  gate runs. Treat handoff cost as a constant added to the start threshold.

Current values for reference: `_PROFILES` sets HARD at 150k of a 1M window for Opus, i.e. 15%.
#440 observed a trip at 56% fill. That the cap is both global-per-model and very low is likely
why agents experience it as a wall.

**Open (Commander's call):** how the handoff-carrying advance is expressed; where the default
threshold sits; whether multi-spine attribution is solved or is honestly declared out of reach
for a session holding several spines.

---

## B. Engine output channel — the agent can see the whole gate

**Intent.** Doctrine says an agent drives from `current()`. That is only true if `current()`
shows the whole gate. It has now failed that twice, and both times the gap was invisible until
someone went looking: `anchors`/`constraints` (5 of 5 cold agents hit it independently), and
now `directives`.

**Status: partially discharged.** Merged as #420 and verified post-merge:

- RAIL no longer repeats the imperative; it points at it (`Next: the ACTIVE line above`).
- `anchors` and `constraints` render. The "they may be vestigial, deleting is the smaller fix"
  branch was resolved on evidence — 20+ archived gates carry them.
- A completeness property test shipped with the right shape: default-deny, so a new field
  added to Task and left unrendered fails by default, plus an anti-vacuity guard asserting the
  loop checked something.

**What is left, and why it is the same job rather than a follow-up.**

The completeness test carries an undifferentiated skip-list. Eight populated fields on it
reach `current()` not at all: `directives`, `context_refs`, `child_checklist`, `status_detail`,
`result`, `finding`, `title`, `rework_count`. The list does not distinguish *asserted
elsewhere* from *deliberately not projected* from *nobody has rendered this yet*, so the test
reads green across all three. It discharges the "catch the next field" obligation while being
blind to eight existing ones.

`directives` is no longer cosmetic. The iterative-planning merge of 2026-08-07 put the
replan/shaped-brief wiring there for the Admiral, Commander and Explorer spines — before that
merge the Admiral template had no `directives` at all. The engine stores the field and copies
it on amend; nothing renders it and no skill instructs an agent to read it. **So the wiring
that makes the new planning lifecycle reachable is currently stored and never delivered** —
the built-but-not-wired pattern that workstream D exists to fight.

#433 was filed correctly and for the right reason (#420's implementer was scoped to two fields
and refused to widen silently), but it was filed as a cheap sibling before this field carried
anything load-bearing.

**Done-condition.**

1. Every field a gate can carry sits in exactly one of three *named* sets: rendered, asserted
   elsewhere, or deliberately not projected. No field sits in an undifferentiated skip-list.
2. Each "deliberately not projected" entry records its reason. Each "not yet rendered" entry
   names the issue that retires it, so fixing that issue without removing the entry is a
   visible failure rather than a silent pass.
3. `directives` renders, and an agent driving the Admiral, Commander or Explorer spine can see
   the wave-transition wiring at the gate where it applies.
4. The completeness test still fails by default for a field nobody has classified.

**Evidence.** Extend the existing property test; do not add a parallel one. The falsification
that counts: delete the render branch and watch it fail — specifically for `directives`, the
field we know was previously invisible.

**Fixed.** `current()` is the complete state channel. Delivery is push: nothing here is fixed
by telling agents to go read a field.

**Open (Commander's call).** Whether some of the seven remaining fields are deliberately
unprojected rather than defects — a judgement per field, and either answer is fine if
recorded. How `directives` renders. And the schema mismatch: `docs/CHECKLIST_SCHEMA.md`
declares `directives` as `[string] | null`, while the shipped templates carry nested objects
(`{"wave_transition": {...}}`). One of the two is wrong; correcting either is acceptable, but
the renderer must handle the shape that actually ships.

**Sequencing constraint, handed to C.** B's echo removal is still assumption 3 — untested, and
graded a guess, because repetition can be load-bearing for compliance. The original spec named
C's tracer as the sentinel, but a two-arm tracer cannot separate B's de-dup from C's
relocation. C therefore carries a third arm (post-B prose, as the control that isolates the
relocation), or B earns a cheap compliance check of its own first. This must be settled before
C ships, because it stops being answerable afterwards.

---

## A2. Trip semantics — what a limit means (split out of A)

**Why it is its own section.** "Which agent am I" and "what happens when that agent is full"
are different questions with different consumers. A settles identity. A2 settles the verb
contract, and F cannot type a verb whose meaning is unsettled.

**Intent.** The governor decides when to stop. Today that decision is expressed as a refusal,
and the refusal deadlocks: HARD blocks `advance`, and `advance` is what writes the DIGEST the
forced handoff depends on (#431). Tommy's ruling reframes it — the limits are set so there is
room to *build the handoff*, not because continuing is unsafe. So a trip becomes a change of
instruction, not a refusal: the spine says "you did well, write the handoff and request a
refresh to continue this work."

**Done-condition.**

1. A gate at or over its threshold changes what the agent is told to do, rather than refusing
   the verb it needs.
2. The engine distinguishes an advance that carries a handoff from one that starts new work,
   and refuses only the second. It cannot express this today.
3. The DIGEST is written on the handoff-carrying advance, so the handoff has the thing it
   depends on. #431 dissolves rather than being patched.
4. Thresholds are per-gate: one graded default, with overrides only where a gate has actually
   bitten. Hand-authoring a threshold per gate across 21 templates would invent ~100 ungraded
   placeholders, which is what threshold discipline exists to prevent.

**Evidence.** Reproduce #431's deadlock first, RED, then show the handoff-carrying advance
completing with the DIGEST present. A threshold override must be shown to change behaviour at
exactly one gate and not its neighbours.

**Fixed.** A missing or failed reading never forces a handoff — the fail-safe survives from the
original spec. HARD means "wrap up", never "you are unsafe". The reading is pushed by the
engine on tool use, never fetched by the agent.

**Open (Commander's call).** How the two advances are distinguished — a flag, a separate verb,
or inferred from the presence of a handoff artifact. Where the default threshold sits; current
`_PROFILES` has HARD at 15% of the window for Opus, and #440 observed a trip at 56% fill, so
the present value is both global-per-model and conservative enough to read as a wall. Whether
the threshold is expressed as a fill fraction or as absolute headroom.

---

## F. MCP front door — put the verbs where verbs belong

**Status: not started. Moved early.** It was deferred at the wave-0 checkpoint; that deferral
is reversed by ordering, not by a change of mind about its content.

**Why it moves early — three reasons, in increasing order of importance.**

1. **It was never blocked by C.** The original spec's own dependency line reads: "A is
   independent. B precedes C. D and E are independent of the rest. F builds on B's output
   fixes and settles its caller identity alongside A." F's stated dependencies are B and A.
   It came last because the workstreams are lettered A–F. A presentation artifact hardened
   into an execution order.
2. **C-before-F relocates text twice.** Five spine templates carry engine verb-and-flag syntax
   inside their imperative prose (`<engine> claim --session-id <...> --claimed-by commander
   --worktree`). The invocation *path* is already abstracted behind `<engine>`; the *call
   mechanics* are not. C moves more instruction text into those same imperatives; F then pulls
   the call mechanics back out of whatever C just moved.
3. **Learning in F will change our opinion of what an instruction should say.** Doing content
   placement first and structural settlement second means the structural learning invalidates
   the content. Tommy: *safe start is unsafe process here.*

**What F is actually for — and it is not token savings.** Tommy, 2026-08-07: the goal is to
cleave the problem-solving side from the spine-management side. Agents keep losing context to
*operating the engine* — fumbling a flag, reading usage, working around a gate that refuses
wrongly — and that cost lands on the agent doing the real work. The door moves that cost
behind an interface: a problem *using* the engine lands on the far side of the tools, and the
working agent never pays attention for it.

The token figures are real but secondary, and treating them as the acceptance test measures
the wrong thing. Roughly 1,000 tokens of always-loaded schema buys back invocation strings
from 7 of 21 imperatives plus most of the on-demand engine reference, about 4,500 tokens. Keep
that as a constraint — the net must not go the wrong way — but it is a side effect, not the
goal, and it is not necessarily obvious.

**The evidence that this cost is real is a filed cluster, not a hypothesis.** #442 (the rail
and the HARD refusal read badly to the agent they are aimed at), #439 (`archive.c2b`'s
`<branch>` placeholder never resolves, so the check always fails), #446 (the same gate accepts
only an open PR, so a well-run epic is forced to `--force` on its success path), #427 (the
refusals counter records zero when a refusal precedes the lease claim), #443 (every
`config_ref` points at a file that does not exist). Every one of those is an agent stopping
its actual work to reason about the engine. This session added another: the first engine call
made here failed on an unrecognised `--session-id`, costing a round-trip to re-read usage.

**Two consequences for how F is built.**

- **MCP is the current vehicle, not the destination.** Tommy expects this to become a
  different kind of tool call later. So this is a deliberate first round: do not over-invest in
  MCP-specific design, and do not gold-plate the tool grouping.
- **F makes C's job smaller.** Once call mechanics live in typed tool arguments, what remains
  in an imperative is pure "what to do at this gate" — no session-id plumbing, no flag syntax.
  That is a far cleaner thing to relocate, and it means C's tranche measures attention rather
  than measuring how accurately agents transcribe commands.

**Done-condition.** The original's four acceptance tests survive; they are good and they stay:

1. A cold agent reaches done on a real role spine through the production door with zero
   malformed calls.
2. **Separation:** a parent and a subagent drive two different spines at once, each through its
   own server instance; leases never collide and each status call returns its own reading.
3. **Inheritance fails closed:** a subagent dispatched with no special configuration gets a
   refusal or no identity — never the parent's lease or the parent's reading. This is the
   failure exc-9 actually observed.
4. **Same-gate equivalence:** the CLI projection and the MCP tool result for one gate carry the
   same imperative text, so the two doors cannot drift.

Two added. From A2: the governor's threshold instruction arrives through a tool result and is
acted on. And the one that carries F's actual purpose:

5. **Spine-management cost falls.** Count the events where an agent stops doing its work to
   operate the engine — refusals, usage reads, retries, and workarounds for a gate that
   refuses wrongly — per run, per arm. This is F's acceptance measure. The token delta is a
   constraint that must not go the wrong way, not the thing being bought.

**Evidence.** Re-run exc-9's tracer protocol. It already counts the right thing: its CLI arm
took 24–27 calls with 2 refusals and 4–7 help-reads, against 14 calls and zero fumbles through
tools. Those fumble counts *are* the metric — read them as the headline rather than as colour
around the token delta.

But **re-measure the CLI baseline rather than reusing exc-9's numbers.** That arm ran against
the pre-B channel and pre-A2 verb semantics; both have changed, and the fumble surface may
have shrunk on its own. A tracer that reuses a stale baseline would flatter F.

One caution on the measure: a fumble the *tool* absorbs still costs somebody. Count recovery
events on the far side of the door too, so "the agent stopped fumbling" is distinguishable
from "the fumbling moved somewhere we stopped looking."

**Fixed.**

- The CLI door stays. F is additive, not a replacement: hooks, headless and cron runs, and
  non-MCP harnesses keep reaching the engine through it, and every uncovered verb keeps a
  documented CLI fallback.
- No engine logic is duplicated. The server wraps the engine's own dispatch function, so
  refusals, recovery hints, rails and the journal ride through unchanged.
- The gate imperative rides tool results verbatim. Spine templates stay the single source of
  instruction text; no second rendering path exists.
- Each agent gets its own server instance (ruling 1), keyed by A's `session_id#agentId`
  (ruling 4). One identity mechanism, two consumers.
- Project-scope `.mcp.json` ships with the repo. `settings.json` is never touched.
- Rich tool descriptions are accepted without a control arm (ruling 3) — recorded as an
  unmeasured preference promoted to a constraint, revisited when trimming is the focus.

**Open / graded.** The seven-over-eighteen tool grouping is a placeholder. Whether an
interactive session picks up a fresh `.mcp.json` without a restart is a pre-build branch point
— probe before building; if it does not, per-dispatch config generation becomes the delivery
path and gets designed first. Per-dispatch config delivery of per-agent instances is a guess,
settled at build. Behaviour against a real spine with delegation and rework is untested;
exc-9 used a four-gate toy.

**Risk, named rather than discovered.** This puts the epic's least-proven piece first. That is
the intent — it is the structural bet the epic is actually making, and finding out early is
the whole point of the reorder. The mitigation is already fixed above: the CLI door stays, so
a failed F costs the build and not the fleet.

---

## C. Relocation — move instructions to the gate that needs them

**No longer split.** The C1/C2 division only made sense under the old order, where C had to
build its own delivery mechanism. B owns rendering and F owns the verb surface, so there is no
mechanism left for C to build. C is one thing again: move the content, measure the thrash.

**Intent, revised.** The original measures corpus shrinkage — a 40% drop in
`commander-core.md`'s always-loaded word count, cost-accounted as delivered tokens per run.
That measures the wrong thing. The claim we care about is that **an agent stops carrying work
that is not its step yet**. A word-count target is satisfied by moving text anywhere; the
attention claim is only satisfied if behaviour at gate N stops referencing gate N+k.

The motive is quality, not budget: quality degrades with context length even when the window
has room, and an agent that can see the whole plan thrashes against it.

**Done-condition.**

1. An agent at gate N does not do, plan, or reserve work belonging to gate N+k.
2. Always-loaded prose shrinks — kept as a secondary indicator, no longer the acceptance test.
3. Per-run delivered tokens do not grow. This constraint from the original survives and is
   still load-bearing: relocated text is paid on every `current` call at its gate, while
   always-loaded prose is paid once. If per-run tokens grow, either B regressed or the tranche
   is too big.

**Evidence.**

- **Three arms, not two.** B's echo removal is still untested assumption 3, and a two-arm rig
  cannot separate it from relocation. Arms: pre-B prose, post-B prose, post-B relocated. The
  middle arm is the control that isolates C. This is B's inherited sequencing constraint, and
  it stops being answerable once C ships.
- The observable per relocated unit is a **later-gate behaviour named before the run**: what
  would this agent do at this gate if it knew about gate N+k? Not "did the text appear".
- `n` and the pass threshold stay graded placeholders (the original's 3/3 versus 0/3).

**Fixed.**

- The bootstrap floor never relocates — instantiate-and-claim text cannot ride the channel it
  creates. Hard boundary, and proven.
- Role identity, spine-use triggers and project-focus prose stay (Tommy's driver 5 exceptions).
- Rules spanning more than one gate stay. Reference-on-demand text stays behind its pointers.
- Instructions are gate-local; constraints are spine-global. An agent that cannot see gate 5
  must still be unable to foreclose it.

**Open (Commander's call).** The tranche boundary stays a graded guess and remains one of the
two costly-to-revert items. Whether the exc-8 census is still the selection authority: it
measured where the *words* are, and the new question is which text causes the *thrash* — those
may not be the same units, so the census is evidence, not instruction. Dose–response beyond
the first tranche stays deferred.

---

## D. Mechanize-over-prose wiring checks

**Status: merged (#422), with one unpaid debt.** #329 and #328 refuse instead of hoping, and
the deliberate-breakage test passes.

The debt is #436. D's own testing pathway says: *"A check that still passes once the guard is
deleted has the #392 shape, and fails review."* The enumeration check — the script that lists
worktree-entering templates and asserts each carries the precondition — shipped without ever
being shown able to fail. It is the guard against the omission shape that caused the defect,
and it is itself unfalsified. Small, independent of the chain, and embarrassing to leave given
what D is for.

---

## E. Backlog — re-cut, not consolidated (runs last)

**Status: partly executed, and mis-designed at the root.**

Executed, and well: the batch confirms (#131, #289, #298, #322 closed with evidence each;
#285 correctly *held* when its stated rationale was measured false), the closeout debts filed
(#448–#451), and theme classification (13 labels across 98 of 138 open issues).

Never started: cluster consolidation into K1–K13 items. No cluster-level issues exist.

**Why it stalled without anyone noticing.** E's *work* is "re-file the surviving singles as
cluster-level items." E's *done-condition* is "every surviving open issue carries a label,
verified by one `gh issue list` sweep." Those are different things. The done-condition tests
the labelling and is silent on the consolidation, so it can be fully satisfied without the
section's actual work happening — a check that cannot fail, sitting in the plan rather than in
the code. Labelling was then substituted for consolidation: the same substitution #449 records
against #308, recurring inside the epic that filed #449.

Three guards were written into E and none were used:

- the count of real work items "which relabeling cannot move" — never kept;
- the closeout check comparing what shipped against each workstream's obligation, explicitly
  named as guarding "the #308 failure shape" — never built;
- the stated rule that consolidation re-files work rather than retiring it — stated, never
  enforced.

**Root mis-classification.** The section opens "Mechanical tracker work." Closing settled
issues and filing debts are mechanical, and both went fine. Deciding that 138 findings are
really about a dozen pieces of work is a design judgement — the spec itself flags cluster
boundaries as one of only two costly-to-revert items in the whole document. Planning a design
job as a batch job is why it did not happen.

**Decision: re-cut, do not consolidate.** (Direction confirmed by Tommy, 2026-08-07.) The
backlog is 138 findings with no shape, which is precisely the input the iterative-planning flow
takes: a shaped brief in, one runnable current wave plus a nonbinding forecast out.
"Consolidate the backlog" and "cut the backlog into a wave and a forecast" are the same job,
and there is now a skill for the second. It also dogfoods the new flow on the hardest real
input available.

**E runs last, and that is not sequencing convenience — the redux is a filter on the backlog.**
Large parts of it sit in the blast radius of A2, B, F and C: `theme:engine-mechanics` (11
open), `theme:built-not-wired` (14), `theme:context-governor` (13),
`theme:checks-that-cannot-fail` (6). Several named findings *dissolve* rather than get fixed —
#431 by A2's redesign, #433 absorbed into B, and #427 / #439 / #442 / #446 all describe a CLI
surface F replaces. Re-cutting before the redux would shape a wave around concerns the redux
is about to invalidate.

**This replaces the escalated fourth done-condition, and the count problem solves itself.**
Each workstream retires the findings it subsumes, with evidence, as part of its own closeout —
instead of leaving them for E to consolidate. That is checkable per workstream, controllable
by the Commander doing the work, and does not depend on a count that the epic's own correct
execution moves the wrong way. E's input becomes whatever survives the redux: a far smaller
and more honest job than consolidating 138.

Proposed wording for the epic's fourth done-condition:

> Each workstream closes the findings it subsumes, with evidence naming why the finding no
> longer exists. What survives the redux is re-cut through the iterative-planning flow into one
> runnable wave plus a nonbinding forecast — not consolidated into cluster items.

**Fixed.** Every close carries its evidence. Consolidation re-files work; it never retires it
silently. Wave and cluster boundaries stay Tommy's call and remain costly-to-revert. Episodes
are not touched here — #447 owns that surface. #264's three commits stay put pending #412's
orphan-risk read.

**Open (Commander's call).** Whether the survivors cut as one wave or several. Whether the
theme labels survive as the cut's input or are superseded by the shaped brief's own structure.
Whether any label group turns out to be empty after the redux, which would be the cleanest
possible evidence that the filter worked.

---

## Execution order

| # | Section | Why here |
|---|---|---|
| 1 | **B extended** | Everything reads through the projection; `directives` is inert until it renders |
| 2 | **A2 trip semantics** | F cannot type a verb whose meaning is unsettled |
| 3 | **F** | Verbs go where verbs belong, before content is written around them |
| 4 | **C** | Relocate into a surface that has stopped moving |
| 5 | **E** | Runs on what *survives* the redux, not on today's backlog |

Independent of the chain, runnable at any point: **A's remainder** (#440 merge, multi-spine
attribution, #180 wiring) and **D's falsification debt** (#436).

The chain is a dependency order, not a schedule. Each link is a real constraint — B before
everything because all of it reads through the projection; A2 before F because F types the
verbs; F before C because C should not write content against a surface that is still moving;
E last because the redux decides what the findings mean. Nothing else here is ordering, and a
Commander that finds a link is not real should say so rather than honour it.

**What the Admiral is not given:** a wave plan, a per-issue dispatch script, or a prescribed
interface for any section. The order above plus each section's fixed boundaries is the whole
course. Wave composition is the Admiral's call under the standing latitude contract, and the
iterative-planning flow is how it revises between waves.
