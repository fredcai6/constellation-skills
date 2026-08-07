# Epic #418 — revised spec, section by section

_**DRAFT — UNCONFIRMED — DO NOT CUT.** This spec has not passed the confirm gate. Do not cut
issues or waves from this document while this marker stands._

Working document. Revises `.agent-work/archive/2026-08-03-explore-post-phase1/DESIGN_SPEC.md`
against what execution actually taught us. Written with Tommy, 2026-08-07.

## Confirmation

- **Status: DRAFT — UNCONFIRMED — DO NOT CUT**
- Confirmed by:
- Date:
- Critic findings dispositioned: NO — every row in the Critic findings table must carry a
  Disposition before confirm
- Cold panel: four arms dispatched 2026-08-07 — `intent-fit`, `testability`,
  `done-condition fidelity`, `claim accuracy`. The last two are new lenses, added for this
  review; `claim accuracy` is the only arm permitted to read the tree.

**Known gate defect:** #428 reports that `verify_spec_confirmed.py --phase review` refuses
every template-conformant draft by construction, because the any-phase marker check makes the
review phase unpassable while the `UNCONFIRMED` marker can only come off at confirm. Expect the
review-phase gate to refuse this document for that reason rather than for its content. Do not
"fix" it by removing the marker early — that defeats the gate it is protecting.

**Note for triage:** the tree moved under the `claim accuracy` arm mid-review. #440 merged
while the panel was running, changing `scripts/hooks/spine_rail.py`, `docs/GAUGE_WRITER_HOOK.md`
and `tests/test_spine_rail.py`. Any finding touching those three paths must be re-checked
against merged main before it is dispositioned.

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

- **Two arms: post-everything prose, post-everything relocated.** An earlier draft specified a
  third "pre-B" arm to isolate B's echo removal (assumption 3). Critic F5 killed it: once F runs
  ahead of C, a pre-B checkout is necessarily also pre-A2 and pre-F, so that arm would differ in
  verb semantics and the entire call surface as well as the echo, and would settle nothing. The
  same reasoning appears in F, rejecting exc-9's stale CLI baseline — and this draft reused the
  defect it had just rejected, two sections apart.
- **Assumption 3 is retired by observation, not by measurement, and that is a real cost.** The
  echo removal is judged behaviour-neutral if no compliance regression appears across A2's and
  F's runs, which is inference from an absence. It is recorded here rather than left implicit:
  should a compliance problem surface during or after C, B's de-dup is a live suspect and was
  never controlled for.
- The observable per relocated unit is a **later-gate behaviour named before the run**: what
  would this agent do at this gate if it knew about gate N+k? Not "did the text appear".
- **Foreclosure check, per relocated unit** (critic F4). Every other done-condition here
  improves as *more* is hidden — forward-reference behaviour, prose size, token totals all get
  better the more aggressive the relocation. The safety property was the only brake and it was
  connected to nothing, so the spec's incentives pointed one way with no counter-force.
  For each unit moved: **name the later gate it could have foreclosed, and assert that whatever
  protects that gate is still visible spine-globally.** This does not try to detect a
  foreclosure — that is a counterfactual about a run that did not happen, and unfalsifiable by
  construction. It checks the property that makes foreclosure impossible instead, per unit, for
  the cost of a sentence each. It also makes `anchors` and `constraints` do the safety work the
  organising principle claims for them, rather than being asserted as the safe channel and never
  inspected.
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

## R. Constellation-readiness checklist (new — Tommy, 2026-08-07)

**Intent.** A project can have every constellation capability present and still not run, because
the wiring that activates it lives somewhere that does not ship. There is no way today to ask
"is this project set up to run constellation" and get a checkable answer, so the gap is found
by an agent failing rather than by a check refusing.

**The instance that motivated it.** The Context Governor's `gauge_writer_hook` is wired only in
`.claude/settings.local.json`, which is untracked. The tracked `.claude/settings.json` wires
`spine_rail` and not the gauge writer, and the user-scope settings has no `PostToolUse` block at
all. The governor therefore fires on one machine and ships to nobody — and every governor
observation this epic has made (#419's live trip, #440's two-arm run) came from a harness that
wired hooks explicitly by absolute path. The capability was never the problem; the delivery was.

This is the `built-not-wired` cluster (#345) as a *project* property rather than a code property,
which is why no existing check catches it.

**Done-condition.** One command answers "is this project constellation ready" and refuses with a
named reason when it is not. It covers at least: engine present and runnable; skills installed
and registered; hooks wired *in a file that ships*; work area present; and the tracked-versus-local
distinction made explicit, so "works here" is never mistaken for "works".

**Evidence.** Run it against a fresh clone — the case that currently fails silently. A readiness
check that passes on the developer's own box and has never been run anywhere else is the same
defect one level up.

**Fixed.** The check reports; it does not silently repair. Wiring is opt-in, as
`install_constellation.py --wire-hooks` already is — nothing writes to a settings file without
an explicit flag.

**Open (Commander's call).** Whether this is its own script or a mode of
`install_constellation.py`, which already reports hook-wiring state and so is most of the way
there. Whether it ships as a skill-invocable check or a plain CLI. What else belongs on the list
— the list itself is the deliverable, and this section names only the items already known.

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

---

## Critic findings and dispositions

The cold adversarial review's findings. The columns below are contractual and machine-parsed —
do not rename them. Disposition is one of `EDIT` / `RE-EXPLORE` / `REJECT`; a RE-EXPLORE
reopens the explore step. Every row must carry a Disposition and a Reason before this spec can
confirm. **Critics never self-triage** — empty Disposition cells on arrival are correct.

| ID | Lens | Severity | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit | BLOCKING | The premise the whole organising principle rests on — "quality degrades with context length even when the window has room" — is asserted flatly and never graded, measured, or cited anywhere in the spec. Every other load-bearing claim in this document is graded (assumption 3, the tranche boundary, the seven-tool grouping, `n` and the pass threshold); this one, the reason the epic exists, is not. No section's done-condition tests it. C's done-condition 1 tests that an agent *stops referencing* gate N+k, which is compliance with the mechanism, not evidence the mechanism buys quality. The epic can pass every done-condition it states and still have bought nothing. Either grade the premise like the rest, or name the one observation that would falsify it and put that observation in C's tracer. | REJECT | Tommy 2026-08-07: the premise is from external research, not worth re-digging up. A spec need not relitigate its own reason for existing. The related observation that C's done-condition tests mechanism-compliance rather than the payoff stands on its own and is not carried by this row. |
| F2 | intent-fit | BLOCKING | The spec names the governor as the enforcement mechanism for its organising principle — "the governor is the seam detector… which is what makes gate-local reveal enforceable rather than merely tidy" — and then leaves the governor's only path to actually firing off the ordered chain. A's own text says the hook has no `PostToolUse` entry outside a test rig, so "make it fire" is "true in harnesses and false in ordinary sessions" (#180), and multi-spine attribution silences it for exactly the role that runs epics (this epic's Admiral ran a full day with the gauge silent). Both are parked as "independent of the chain, runnable at any point," while A2 — a redesign of what a trip *means* — is scheduled second. A2's stated evidence (reproduce #431 RED, then show the handoff-carrying advance) is satisfiable entirely in a harness. That is the built-not-wired shape D exists to fight and B's section calls out by name, reproduced at the top of the execution order. If the governor is load-bearing for the intent, its wiring belongs on the chain ahead of A2, not beside it. | EDIT | Tommy 2026-08-07: wire gauge_writer_hook into the TRACKED project settings so the governor ships like spine_rail already does. Measured state at ruling time: user settings has no PostToolUse block at all; tracked .claude/settings.json wires spine_rail but NOT the gauge writer; untracked .claude/settings.local.json wires the gauge writer. So every governor observation this epic has made came from configuration that does not ship. Also spawns new work: a 'is this project constellation ready' checklist, with hook wiring as one of its items. |
| F3 | intent-fit | BLOCKING | The execution order is justified entirely by build dependency — what must exist before what can be built — and never once by what answers the epic's own question soonest. C is the only workstream that tests the epic's central claim, and it is placed fourth, behind the piece the spec itself calls "the epic's least-proven." The spec argues explicitly for learning-early when it wants F moved up ("finding out early is the whole point of the reorder," "safe start is unsafe process here") and then does the opposite for the workstream that would actually falsify the thesis. The appetite ruling — reversible mistakes are cheap, a later run surfaces them again — cuts the same way: it licenses running C's tracer early and cheaply rather than waiting for a settled surface. As ordered, if F drags or fails, the epic's central claim is never tested at all. | REJECT | Tommy 2026-08-07: 'we dont need to answer the epic's question soonest, that's a false premise.' The finding assumes an epic must be ordered to settle its central claim fastest. It need not. F-first stands: C written against a verb surface that is still moving gets written twice. |
| F4 | testability | BLOCKING | The organising principle's one safety property — "instructions are gate-local, constraints are spine-global; an agent that cannot see gate 5 must still be unable to foreclose it" — has no evidence line in any section. C restates it under **Fixed** but C's three done-conditions test forward-reference behaviour, token growth and prose size, none of which detect a foreclosure. The claim that makes hiding later gates safe rather than reckless is the only cross-cutting claim in the spec with zero falsifier; every section can pass while it is false. | EDIT | Tommy 2026-08-07: add a per-relocated-unit foreclosure check to C. For each unit moved out of always-loaded prose, name the later gate it could have protected and assert the protecting constraint is still spine-visible. Turns an unfalsifiable counterfactual into a per-unit check costing a sentence each, and makes anchors/constraints do the safety work the spec claims for them rather than merely asserting it. Accepted because C's other done-conditions all improve as MORE is hidden, so the safety claim was the only brake and it was connected to nothing. |
| F5 | testability | BLOCKING | C's three-arm tracer cannot isolate what it claims once the execution order is honoured. The arms are pre-B prose / post-B prose / post-B relocated, but the order runs B, A2, F, *then* C — so the "pre-B" arm can only be produced from a checkout that is simultaneously pre-A2 and pre-F, differing in verb semantics and the entire call surface as well as the echo. The spec applies exactly this reasoning to reject exc-9's stale CLI baseline in F ("that arm ran against the pre-B channel and pre-A2 verb semantics"), then reuses a stale pre-B arm without it. Arm 1 measures three merged changes at once and settles nothing about assumption 3. | EDIT | Tommy 2026-08-07: drop C to two arms (post-everything prose / post-everything relocated) and retire assumption 3 by observation rather than by rig. The critic is right that arm 1 was unbuildable once F moved ahead of C — and that I rejected exc-9's stale baseline on exactly this reasoning two sections earlier, then reused the same defect. Accepted cost: assumption 3 never gets a measured answer; it is retired on the absence of a compliance regression across A2's and F's runs, which is inference, not measurement. Recorded rather than left implicit. |
| F6 | testability | BLOCKING | B's done-condition 1 ("every field sits in exactly one of three *named* sets") is satisfied by relabelling the existing amnesty list. Moving all eight unrendered fields into "deliberately not projected" with a reason string passes DC1, DC2 and DC4 while `context_refs`, `child_checklist`, `result`, `finding` and the rest remain exactly as invisible as they are today. Nothing in the done-condition constrains the *correctness* of a classification — the test fails only for an unclassified field, never for a wrongly classified one — so the section's actual work (deciding which fields are defects) can be skipped entirely and the test reads green. Only `directives` is protected, by being named explicitly. |  |  |
| F7 | testability | BLOCKING | F's acceptance measure 5 counts "refusals, usage reads, retries, and workarounds", and #427 — a finding F claims to dissolve — states the refusals counter records zero when a refusal precedes the lease claim. F's headline metric therefore reads from an instrument a subsumed issue says undercounts, in precisely the direction that flatters F. The spec neither requires the counter to be fixed before the tracer runs nor requires the metric to be collected independently of it. |  |  |
| F8 | testability | BLOCKING | Nothing anywhere distinguishes "the governor produced no trip because there was headroom" from "the governor produced no reading at all". The spec records the failure mode itself — multi-spine attribution yields no reading, and this epic's own Admiral "ran a full day with the gauge silent" — yet no section requires a heartbeat, a liveness assertion, or a positive control that fails when readings stop arriving. Every measure downstream of a reading (A's trip, A2's threshold behaviour, F's added condition that the instruction "arrives through a tool result") registers total absence of the mechanism as a quiet pass. |  |  |
| F9 | done-condition fidelity | BLOCKING | The new cross-cutting "standing obligation" is self-scoped and unreconciled. A workstream declares which findings it subsumes, then closes them; nothing ever compares the set it *should* have subsumed against the set it closed. A workstream that declares an empty subsumption set satisfies the obligation completely without doing any of the work, and a finding a workstream forgot flows silently into E's input as an apparent "survivor" — no failure signal at any point. This is offered as the replacement for the falsified issue-count done-condition, so the epic trades its only cross-workstream reconciliation for a per-workstream self-report. At minimum the obligation needs a pre-declared candidate set per workstream — the theme-label groups already exist and are named (`theme:engine-mechanics` 11, `theme:built-not-wired` 14, `theme:context-governor` 13, `theme:checks-that-cannot-fail` 6) — so that "closed 0 of 11" is visible rather than vacuous. |  |  |
| F10 | done-condition fidelity | BLOCKING | E's replacement done-condition reproduces the defect it was written to repair. E's *work* is deciding what 138 findings actually mean; its new *done-condition* is that the survivors are "re-cut through the iterative-planning flow into one runnable wave plus a nonbinding forecast." Running the skill produces a wave artifact and a forecast artifact — so the condition is satisfied by the artifacts existing, exactly as the old one was satisfied by a labelling sweep existing. Nothing states a coverage relation between the input (survivors after the redux) and the output (wave ∪ forecast), so findings can silently fall out of both. The spec's own "consolidation re-files work; it never retires it silently" sits in Fixed with no check behind it. The condition needs to be a relation — every survivor appears in exactly one of wave or forecast, and the input/output delta is itself the evidence — not the presence of two documents. |  |  |
| F11 | done-condition fidelity | BLOCKING | A2's entire premise is that the limits exist "so there is room to *build the handoff*," yet no done-condition tests that a handoff is built or that it works. DC1 checks the instruction changed; DC3 checks the DIGEST is written. Both are satisfiable while every tripped agent produces a useless handoff or none at all, because nothing checks the far end: that a refreshed agent picks the handoff up and continues the work. A2 can pass fully while the only thing the redesign was for — continuity across a trip — never happens once. The missing condition is a round trip: trip, handoff, refresh, resume, with the resumed agent's work verified against what the tripped agent was mid-way through. |  |  |
| F12 | done-condition fidelity | BLOCKING | F's acceptance measure is not attributable to F. DC5 counts "events where an agent stops doing its work to operate the engine — refusals, usage reads, retries, and workarounds for a gate that refuses wrongly." Of the five filed items offered as evidence that this cost is real, at least four are ordinary engine bugs fixable without any MCP door: #439 (`<branch>` placeholder never resolves), #446 (gate accepts only an open PR), #427 (refusals counter records zero), #443 (`config_ref` points at a missing file). Fixing those five makes the count fall with no door built. Worse, the execution order ships A2 and B *before* F, and both change refusal behaviour and the rail — #442's subject — so the pre/post comparison is confounded by the epic's own design. As written, DC5 registers a fall whether or not the door does anything. It must isolate the mechanism: hold the engine-bug fixes constant across arms, or count only fumble classes a typed interface can absorb. |  |  |
| F13 | intent-fit | MAJOR | The F-before-C link is stated as "relocate into a surface that has stopped moving," but F's own section says the surface has not stopped moving: "MCP is the current vehicle, not the destination. Tommy expects this to become a different kind of tool call later." F does not end the churn in the imperative surface; it schedules one more round of it after C ships. The link's stated reason therefore does not hold as written. Either the claim is narrower than stated — F settles the *call-mechanics-out-of-prose* shape and a later vehicle swap does not touch relocated text, which should be said and defended — or the link is not real and C need not wait. |  |  |
| F14 | intent-fit | MAJOR | C's three-arm design is the only instrument that separates B's untested echo removal from relocation, and the execution order makes its controls non-comparable. Arm 1 (pre-B prose) is already historical — B merged as #420 — so it can only be run against a reverted tree, which the spec never says. Arm 3's target and arm 2's control are both measured after F has, by F's own account, rewritten what remains in every imperative ("what remains in an imperative is pure 'what to do at this gate'"). So "post-B prose" at C-time is really post-B-post-F prose, and the control no longer isolates C. B's own text says this "must be settled before C ships, because it stops being answerable afterwards" — but the order inserts two workstreams between B and C, which is precisely the afterwards it warns about. Either the control arms run now, while they are still runnable, or the spec should admit B's assumption 3 will stay untested and stop claiming C can isolate it. |  |  |
| F15 | intent-fit | MAJOR | The intent's premise and A2's threshold direction pull opposite ways, and the spec never reconciles them. The organising principle says long context is bad for quality independent of window room. A2 observes HARD at 15% for Opus with a trip seen at 56% fill and reads this as "both global-per-model and conservative enough to read as a wall" — implying the fix is more headroom. If the premise is true, a low cap is not a wall but the mechanism working, and the correct response is smaller gates, not looser thresholds. The spec resolves this rhetorically ("HARD means wrap up, never you are unsafe") without resolving it substantively: nothing in A2's done-conditions or evidence distinguishes "the threshold was miscalibrated" from "the gate was too big." Name which one the per-gate override is fixing, because the two lead to opposite default values. |  |  |
| F16 | intent-fit | MAJOR | A2 makes the handoff the carrier of continuity across every trip — "write the handoff and request a refresh to continue" — and nothing in the spec sets a bar on what the handoff must carry or tests that a refreshed agent resumes from it. This lands squarely on the intent line: a thin handoff makes the next agent under-informed, and a thorough one makes it re-read the whole plan, which is exactly the state the epic exists to prevent. A2's done-conditions test that the DIGEST *exists* and that the advance is *permitted* — both artifact-existence checks — not that the successor resumes without re-acquiring context that is not its step. The mechanism the intent depends on at every seam is the one thing with no done-condition. |  |  |
| F17 | intent-fit | MAJOR | F is in the epic on a rationale independent of the epic's stated point, and the spec never asks whether the point selects it. F's purpose is stated as cleaving problem-solving from spine-management — engine-operation cost — and its acceptance measure (done-condition 5, counting fumbles and usage-reads) measures that cost, not whether agents stop carrying work that is not theirs. The three reasons given for moving F are all *placement* arguments answering "where does F go," and the strongest of them observes that its old position was an artifact of A–F lettering. That argument dissolves the old ordering; it does not establish that F belongs in this epic at all, and the filed cluster (#442/#439/#446/#427/#443) is a real cost that would justify its own epic just as well. Under the appetite ruling this matters: F is the largest, least-proven, explicitly-temporary piece, and it is being carried on inherited membership rather than on fit. |  |  |
| F18 | intent-fit | MAJOR | The spec mandates next-step-only reveal and then publishes its own whole plan. "What the Admiral is not given: a wave plan…" is immediately followed by a five-link ordered chain covering every section through to E, plus two off-chain items, plus each section's forecast reasoning — which is the epic-tier equivalent of the gate-5 visibility C exists to remove. The Epic row of the organising-principle table promises "a course, not a script," but a fixed total order with per-link justification is closer to a script than to a course. The spec's own Wave tier already has the right instrument merged (iterative planning: one runnable wave plus nonbinding forecast) and does not apply it to itself. If the principle is right, this document should be one wave plus a forecast; if it is not right to do that here, that is worth stating, because it is evidence about the principle. |  |  |
| F19 | intent-fit | MAJOR | The standing obligation is the load-bearing replacement for the falsified count done-condition, and it has no verifier at any level. "Each workstream retires the findings it subsumes" is a per-Commander self-report with no check that any Commander did it — the spec deleted the count check precisely because counts move wrong, and put nothing in its place. E's entire redesign rests on the claim that "E's input becomes whatever survives the redux: a far smaller and more honest job than consolidating 138." If four workstreams close their obligation with a sentence and no retirements, E runs on 138 and inherits the exact mis-designed job the section just diagnosed. Worse, this is the same shape E is being fixed for: a section whose real work is invisible to its own check. The obligation needs something that registers its own failure — the survivor set named per workstream before the redux, or the theme-label counts read at each closeout. |  |  |
| F20 | testability | MAJOR | A's done-condition, "a trip fires from a per-agent reading on a live run", is reported met while the section also records that no `PostToolUse` entry for `gauge_writer_hook.py` exists in user-scope `settings.json` (#180) — so the hook fires in harnesses and not in ordinary sessions. The done-condition is satisfiable, and has been satisfied, without the governor working anywhere a real agent runs. #180 is then filed under "independent of the chain, runnable at any point", which makes the one step that would make the measure honest optional in the ordering. |  |  |
| F21 | testability | MAJOR | A2 converts HARD from a refusal into an instruction, which removes the only mechanism that could register non-compliance. A refusal is self-enforcing and self-recording; advisory prose saying "write the handoff and request a refresh" is satisfied or ignored with identical observable traces, and A2 states no measure of whether the agent obeys. Done-condition 1 asks only that the agent be *told* something different. The compliance half is delegated to F's added condition ("acted on"), which covers only the MCP door — under the CLI door, which **Fixed** says stays, the governor stops enforcing anything and no check notices. |  |  |
| F22 | testability | MAJOR | A2's done-condition 2 — the engine distinguishes a handoff-carrying advance from one that starts new work and "refuses only the second" — is the entire residual enforcement after the refusal is removed, and the evidence list has no test for it. The listed evidence covers the deadlock RED, the handoff-carrying advance completing, and a threshold override; there is no negative case showing a new-work advance at or over threshold actually being refused. Implement the permissive branch only and every stated piece of evidence still passes. |  |  |
| F23 | testability | MAJOR | A2's RED-before-fix requirement leaves no residue and has no failure branch. The deadlock is a property of the refusal path that A2 deletes, so once the fix lands the RED is unreproducible by construction and cannot survive as a standing regression test — nothing will fail if a later change reinstates a blocking refusal on `advance`. Separately, the spec gives no instruction for the case where the deadlock does not reproduce (different threshold, different profile, no reading at all): an unreproducible RED reads as "already fixed" and licenses a GREEN that demonstrates nothing. |  |  |
| F24 | testability | MAJOR | C's done-condition 1 is an absence claim — "an agent at gate N does not do, plan, or reserve work belonging to gate N+k" — and the spec requires no positive control establishing that the behaviour occurs at a measurable rate in the untreated arms. If the control arms also show zero forward references, the tracer nulls and the null is indistinguishable from success. The pre-registered observable ("a later-gate behaviour named before the run") is the right instrument but is stated as a counterfactual, with no floor the control must clear for the treatment result to be interpretable. |  |  |
| F25 | testability | MAJOR | E's replacement done-condition reinstates the shape E was just diagnosed for. The section's own analysis is that "every issue carries a label" tested the adjacent artifact rather than the design judgement, and labelling was substituted for consolidation; the new wording — "re-cut through the iterative-planning flow into one runnable wave plus a nonbinding forecast" — is again satisfied by the *existence* of a wave and a forecast, of any quality, produced by running the flow. Deciding what 138 findings mean is still the work, and producing the two artifacts still does not require having done it. |  |  |
| F26 | testability | MAJOR | The standing obligation — "each workstream retires the findings it subsumes" — has no detector for the failure it is meant to prevent. There is no sweep asserting that every finding a workstream claimed to subsume was closed with evidence, and no way to notice a workstream that subsumes a finding and never says so. The failure mode is silence, whereas the mechanism it replaces (the issue count) at least moved. This is the epic's fourth done-condition and it is currently prose with no instrument. |  |  |
| F27 | testability | MAJOR | F's acceptance test 1 — "a cold agent reaches done ... through the production door with zero malformed calls" — is close to tautological once calls are typed tool arguments, because the schema prevents the malformation the test counts. It was a meaningful count against a CLI where flag syntax could be fumbled; carried onto the MCP door it is a property of the interface, not a result. As written it cannot register the failure it appears to guard, and it will be reported as F's cleanest pass. |  |  |
| F28 | testability | MAJOR | F's acceptance test 3 accepts "a refusal **or no identity**" as inheritance failing closed — which is also what a subagent gets when the server never started, the config never delivered, or the whole door is absent. The test passes under total non-installation of the thing it is testing. It needs a positive control: the same dispatch demonstrably reaching the engine, and *then* carrying no identity. |  |  |
| F29 | testability | MAJOR | D's remaining debt (#436) is a check that shipped without ever being shown able to fail, and the section fixing it states no done-condition, no evidence line and no falsification protocol — it is the only section in the spec with none. Nothing requires the enumeration check to be mutated and observed failing, which is the exact demonstration whose absence is the debt. As written the debt can be closed by inspection. |  |  |
| F30 | testability | MAJOR | B's done-condition 2 asserts that fixing a "not yet rendered" field's issue without removing its entry is "a visible failure rather than a silent pass", but no mechanism is named that could produce that failure. A test cannot see tracker state, and the spec does not authorise it to query one; absent such a link, the issue reference is a comment and the stale entry sits there indefinitely — reproducing the amnesty in a form that now looks documented. |  |  |
| F31 | testability | MAJOR | B's stated falsification ("delete the render branch and watch it fail — specifically for `directives`") exercises done-condition 3 only. Done-condition 4 — the test still fails by default for a field nobody has classified — has no falsifier, and it is the one that governs every *future* field. The corresponding demonstration (add a field to Task, leave it unclassified, watch it fail) is not asked for, and the existing default-deny behaviour is asserted rather than re-shown after the skip-list is restructured. |  |  |
| F32 | testability | MAJOR | The anti-vacuity guard is described as "asserting the loop checked something", which a loop that checks one field satisfies. That guard was in place while eight populated fields were being skipped, so it has already demonstrated it cannot detect the skip-list swallowing the field set — yet the spec cites it as evidence the test "shipped with the right shape" and B's work leaves it unchanged. The guard needs to assert coverage against the field set, not against non-zero iterations. |  |  |
| F33 | done-condition fidelity | MAJOR | A2 deletes the refusal and replaces it with prose, with no compliance check anywhere. Today HARD enforces the stop mechanically; after A2 the stop is a sentence in a spine ("you did well, write the handoff and request a refresh"). DC1 tests that the sentence changed, not that any agent obeys it. The spec treats instruction compliance as needing measurement everywhere else — B's echo removal is graded a guess "because repetition can be load-bearing for compliance," and C carries a third tracer arm to isolate it — but here converts an enforced refusal into unmeasured instruction and files the compliance question nowhere. #442 already reports that this rail "reads badly to the agent it is aimed at," which is direct evidence against assuming compliance. |  |  |
| F34 | done-condition fidelity | MAJOR | A2's DC4 is vacuous at zero overrides. "One graded default, with overrides only where a gate has actually bitten" is satisfied completely by shipping one default and no per-gate mechanism at all — and the accompanying evidence line ("a threshold override must be shown to change behaviour at exactly one gate and not its neighbours") is equally vacuous when no override exists. The per-gate threshold machinery, which is the section's actual deliverable, can be entirely absent while DC4 and its evidence both pass. B shipped an anti-vacuity guard for precisely this failure mode two sections earlier; A2 needs the same: at least one real override, exercised. |  |  |
| F35 | done-condition fidelity | MAJOR | B's DC1/DC2 can be satisfied by reclassification instead of by work. The requirement is that every field sits in exactly one of three named sets and that each "deliberately not projected" entry records a reason. The same agent that must fix the fields chooses which set each goes into, so moving all eight currently-invisible fields into "deliberately not projected" with a one-line reason each satisfies DC1 and DC2 in full, empties the "not yet rendered" set (making DC2's issue-naming requirement trivially true), and renders nothing. Only DC3 survives, and it covers one field. The classification needs an external constraint — e.g. a field that any shipped template populates cannot be classified "deliberately not projected" without naming the consumer that reads it elsewhere. |  |  |
| F36 | done-condition fidelity | MAJOR | B's anti-vacuity guard has the wrong bar, and DC4 re-adopts it unchanged. The guard "asserts the loop checked something" — one field satisfies it. That is why the shipped test read green while eight populated fields reached `current()` not at all; the guard was never capable of noticing. DC4 ("the completeness test still fails by default for a field nobody has classified") preserves the default-deny half but leaves the anti-vacuity bar at "something," so a skip-list that grows again keeps the test green in exactly the way it just did. The guard should assert a coverage count against the classified sets, not non-emptiness. |  |  |
| F37 | done-condition fidelity | MAJOR | B's named falsification tests that `directives` renders, not that it renders where it should. DC3 has two halves — the field renders, *and* "an agent driving the Admiral, Commander or Explorer spine can see the wave-transition wiring at the gate where it applies" — but the evidence is "delete the render branch and watch it fail," which exercises only the first. An implementation that dumps every directive into every gate's projection passes DC3's falsification, satisfies the letter of DC3, and directly violates the organising principle this same spec opens with (gate-local reveal). The falsification must be gate-discriminating: a directive scoped to gate N must be absent from gate M's projection. |  |  |
| F38 | done-condition fidelity | MAJOR | B diagnoses a two-part defect and its done-condition repairs one part. The stated problem is that "the engine stores the field and copies it on amend; **nothing renders it and no skill instructs an agent to read it**" — stored-but-not-delivered *and* delivered-but-not-consumed. DC3 stops at "can see." Nothing checks that any agent's behaviour differs because the directive arrived, so B can ship with the wave-transition wiring visible and still inert — the built-not-wired pattern the spec says workstream D exists to fight, invoked one section earlier. B's Fixed line ("delivery is push: nothing here is fixed by telling agents to go read a field") is right about the mechanism and does not substitute for a consumption check. |  |  |
| F39 | done-condition fidelity | MAJOR | F's DC1 is true by construction. "A cold agent reaches done on a real role spine through the production door with zero malformed calls" — a typed tool interface makes malformed calls structurally impossible at the schema boundary, which is why exc-9 already recorded zero fumbles through tools on a four-gate toy. DC1 therefore confirms that typed arguments are typed, and is met by a door that is otherwise unusable. The spec opens by noting its "by construction" claims have been falsified by execution; this is a fresh one entering under a done-condition rather than under a claim. DC1 should test task completion cost, not call well-formedness. |  |  |
| F40 | done-condition fidelity | MAJOR | F's DC3 is a negative result with no positive control. "A subagent dispatched with no special configuration gets a refusal or no identity" — the "or no identity" branch is indistinguishable from the server not running, the dispatch failing, or the rig being misconfigured. The test passes most loudly when it is broken. A's own #440 acceptance is described as landing "against a genuine positive control" precisely because of this hazard; DC3 needs the paired case (a correctly-configured subagent that *does* get its own identity) run in the same rig, or it certifies nothing. |  |  |
| F41 | done-condition fidelity | MAJOR | F's most important caution sits in prose and not in its done-condition. Evidence warns that "a fumble the *tool* absorbs still costs somebody. Count recovery events on the far side of the door too, so 'the agent stopped fumbling' is distinguishable from 'the fumbling moved somewhere we stopped looking.'" DC5 as written counts only agent-side events. Since the design is explicitly "move the cost behind an interface," a near-side-only measure registers cost relocation and cost elimination identically — the one confusion the section itself identifies. The far-side count belongs in DC5, not in the commentary around it. |  |  |
| F42 | done-condition fidelity | MAJOR | F's DC4 is a single sample standing in for an ongoing property. "The CLI projection and the MCP tool result for one gate carry the same imperative text, so the two doors cannot drift" — one gate matching once establishes nothing about drift, which by definition happens later and at gates nobody sampled. The stated goal ("cannot drift") requires a property over all gates enforced in the suite, of the same default-deny shape B already built for field rendering. As written it passes with 20 gates diverging. |  |  |
| F43 | done-condition fidelity | MAJOR | C is satisfiable at homeopathic dose. DC1 is a per-unit behavioural observable, DC2 is explicitly demoted to a secondary indicator, and DC3 is a do-no-harm constraint that gets *easier* the less text moves. Nothing sets a floor on the tranche or ties it to where the thrash actually is, so relocating a single trivial instruction satisfies all three done-conditions while the section's real work — moving the material that makes agents carry work that is not their step — does not happen. Tranche boundary as the Commander's call is fine; the absence of any coverage obligation the tranche must discharge is not. |  |  |
| F44 | done-condition fidelity | MAJOR | C's observable is chosen after the tranche, by the agent whose work it grades. The evidence names "a later-gate behaviour named before the run," which constrains timing relative to measurement but not relative to *tranche selection*. An implementer who picks the relocation first and then names the observable will name one they already expect to flip. The ordering that makes this evidence mean anything is: name the observables from the thrash hypothesis, then select the tranche to address them, then run. |  |  |
| F45 | done-condition fidelity | MAJOR | The organising principle's safety property has no done-condition in any section. "Instructions are gate-local, constraints are spine-global. An agent that cannot see gate 5 must still be unable to foreclose it" is what makes the reveal-the-next-step design safe rather than reckless, and it appears in C only under Fixed, as an assertion. C's DC1 tests the opposite direction (the agent does not reach *forward* into gate N+k); nothing tests that a relocated-away instruction still constrains behaviour at the gate it was protecting, and no section carries a regression control showing gate-N work is unharmed by the relocation. The one property that could make this epic actively destructive is the one property nothing checks. |  |  |
| F46 | done-condition fidelity | MAJOR | The four items pulled out of the dependency chain carry no done-conditions at all. "A's remainder (#440 merge, multi-spine attribution, #180 wiring) and D's falsification debt (#436)" are listed only as runnable at any point. Multi-spine attribution has no success criterion even though the Open block allows "honestly declared out of reach" as an outcome, with nothing distinguishing a declaration from a stall. #436 is the sharpest case: it is a debt *for an unfalsified check*, and the plan to repay it names no falsification criterion, so it can be closed by touching the script. A section about checks that were never shown able to fail is being repaired by a task that was never told how it could fail. |  |  |
| F47 | done-condition fidelity | MAJOR | A is marked "stated obligations discharged" on a done-condition that is a single-instance existence check. "A trip fires from a per-agent reading on a live run" is satisfied by one trip on one run — and the same section then reports that this epic's own Admiral "ran a full day with the gauge silent" (multi-spine attribution) and that the hook has no `PostToolUse` entry in user-scope `settings.json`, so firing is "true in harnesses and false in ordinary sessions." The condition was met while the feature was non-functional for the epic's principal agent and for every non-harnessed session. The spec acknowledges the gap ("as of #440's g2 acceptance it is met *correctly*") without revising the condition that let it read discharged — the E failure shape, in a section presented as complete. |  |  |
| F48 | done-condition fidelity | MAJOR | A's sweep evidence survives the sweep being done wrong. The reported evidence is a procedure plus a pair of counts: dry-run recorded, real run against a fresh re-read, "store went 64 → 1," one entry spared for having a live spine and an active lease. A sweep that deleted the wrong 63 entries produces byte-identical evidence, because nothing verifies the deleted entries were stale — only that the retained one was live. The check that distinguishes these is a property of the deletions (each deleted binding had no spine and no active lease), and it is exactly the half not reported. |  |  |
| F49 | done-condition fidelity | MAJOR | Only the fourth epic-level done-condition is revised; the other three are left behind in a document this spec declares falsified. The revision opens by stating that several of the original's "by construction" claims "have since been falsified by the epic's own behaviour," then rewrites one done-condition and never restates the rest. A reader of this spec cannot check the epic's completion at all, and whoever eventually does will check three conditions written on premises this document says no longer hold. |  |  |
| F50 | claim accuracy | MAJOR | F's reason 2 claims "**five** spine templates carry engine verb-and-flag syntax inside their imperative prose." Three do, not five: `skills/admiral/templates/ADMIRAL_SPINE.template.json`, `skills/commander/templates/COMMANDER_SPINE.template.json`, `skills/explorer/templates/EXPLORER_SPINE.template.json`. No other template under `skills/*/templates/*.json` contains `<engine>` at all. Commands: `grep -rl '<engine>' skills/*/templates/*.json` (3 files), plus a python pass over each template's `tasks[*].imperative` matching `<engine>` followed by a flag (7 imperatives, 3 files). Re-run at HEAD 1f4c6de. This number is load-bearing: it sizes the "C-before-F relocates text twice" argument that justifies the reorder. |  |  |
| F51 | claim accuracy | MAJOR | "Roughly 1,000 tokens of always-loaded schema buys back invocation strings from **7 of 21 imperatives**." The 7 is right; the 21 is not a count of imperatives. There are **68** imperatives across 21 template *files*. Command: python walk of `skills/*/templates/*.json` counting `tasks` entries, re-run at HEAD 1f4c6de, giving 68 gates of which 7 carry `<engine>`+flag syntax. The spec inherits this verbatim from the archived original (`.agent-work/archive/2026-08-03-explore-post-phase1/DESIGN_SPEC.md:44`, "7 of 21 spine-template imperatives"), so the error is carried, not introduced — but it makes the buyback look like a third of the imperative surface when it is a tenth. |  |  |
| F52 | claim accuracy | MAJOR | "…plus most of the on-demand engine reference, about 4,500 tokens." The on-demand reference is `skills/workbench/references/checklist-engine.md`: 17,755 chars / 2,474 words, roughly 4,400 tokens — so 4,500 is the **whole file**, not the invocation-string share of it. Of its 164 lines, 20 lines (6,555 chars, ~37%) carry `<engine>` / `python scripts/checklist_engine` / flag syntax; the rest is doctrine, invariants, recovery guidance and schema prose that a typed tool surface does not replace. Command: python line-classify over `checklist-engine.md` against regex `<engine>` OR `python scripts/checklist_engine` OR `--[a-z-]+`. F's stated constraint is "the net must not go the wrong way" — that constraint is being set against a number roughly 2.7x the recoverable text. |  |  |
| F53 | claim accuracy | MAJOR | Section A states multi-spine attribution is "**(unfiled)**". It was filed: **#452**, "Governor: a bare-keyed agent driving several spines at once gets NO gauge reading at all", opened 2026-08-07T16:09:18Z, OPEN, with evidence measured against the live binding store. Commands: `gh issue list --state all --limit 400 --json number,title,createdAt` then `gh issue view 452`. The spec's description of the defect matches #452's body — only the "unfiled" status, and the implied obligation to file it, are wrong. |  |  |
| F54 | claim accuracy | MAJOR | A names "**The hook is unwired outside a test rig (#180)**" as an open remainder, and the Execution order lists "#180 wiring" as independent runnable work. **#180 is CLOSED** (`gh issue view 180 --json state,title` → `CLOSED \ |  |  |
| F55 | claim accuracy | MAJOR | Section D says "**Status: merged (#422)**", but #422 is OPEN, and both findings it wired — **#329** and **#328** — are also OPEN. Command: `gh issue view 422/329/328 --json state`. The code is merged (`e74fe55 FINAL: wire #329 worktree isolation + #328 record()-postcondition checks (epic-418 D/#422) (#438)`) and I re-ran the tests: `python -m pytest tests/test_worktree_precondition_wiring.py tests/test_record_postcondition_wiring.py -q` → 12 passed. So the engineering claim holds and the tracker claim does not. This is the standing obligation the spec itself introduces ("each workstream retires the findings it subsumes") going unpaid in a section the spec presents as done — and D is the one section given no done-condition of its own to catch it. |  |  |
| F56 | claim accuracy | MAJOR | D's debt is described as: the enumeration check "**shipped without ever being shown able to fail**… it is itself unfalsified." #436's own body says the opposite: "Its deliberate-breakage test (`tests/test_worktree_precondition_wiring.py`) **proves the check fails** when that one entry's precondition is stripped from a copy of the real template. It does NOT prove the check catches a genuinely NEW second worktree-entering template… **because no second entrant exists yet to test against**," and its suggested scope opens "*when* a second worktree-entering role/template ships." Command: `gh issue view 436 --json body`. The spec calls this "small, independent of the chain, and embarrassing to leave" and lists it as runnable at any point — but by its own issue it is blocked on a second worktree-entering template that does not exist, so a Commander handed it has nothing to do. |  |  |
| F57 | claim accuracy | MAJOR | B claims "The completeness test carries an **undifferentiated** skip-list… The list does not distinguish *asserted elsewhere* from *deliberately not projected* from *nobody has rendered this yet*." It does distinguish them, in prose. `tests/test_checklist_engine.py:3960-4005` gives every excluded field a stated reason on its own line: `preconditions`/`postconditions` "content checked below by dedicated statement-text assertions" (asserted elsewhere), `context_refs` "a separate declared-file-manifest mechanism", `title` "historically never part of the briefing", and `directives` "**KNOWN GAP**, same unrendered-defect class as anchors/constraints… issue **#420** caps this fix's authorized scope". `docs/CHECKLIST_SCHEMA.md:138` carries the same known-gap record. So done-condition 2's "each 'not yet rendered' entry names the issue that retires it" is already met for the only entry in that class. The real deficit is that the classification is comment-only and not machine-checkable — a materially smaller and differently-shaped job than the spec describes. Commands: `sed -n '3960,4070p' tests/test_checklist_engine.py`; `grep -n directives docs/CHECKLIST_SCHEMA.md`. |  |  |
| F58 | claim accuracy | MAJOR | "#440 observed a trip at 56% fill" is offered as evidence that the HARD cap "is very low" and "why agents experience it as a wall". Three problems with the inference, all checkable in `.agent-work/archive/2026-08-07-issue-440-binding-cwd/`: (a) the run was **claude-sonnet-5**, not Opus, though the sentence sits inside a claim about Opus — `crew/g2-implement/IMPLEMENTER_PLAN.json`: "gauge model claude-sonnet-5 (subagent) vs parent opus"; (b) the fills (treatment 0.559655, control 0.562149) were produced by an **acceptance harness that deliberately inflated context to force a trip** — the reviewer records both arms at "~3.7x HARD", and the first launch was quiet because "the dispatched subagent DECLINED the protocol as social engineering"; (c) 56% against a 15% HARD means the trip fired at 3.7x the threshold, which is evidence the reading arrived **late**, not that the cap is set too low. Command: `grep -rn "56%\ |  |  |
| F59 | intent-fit | MINOR | B's extension is justified as serving the intent, but only one of its four done-conditions does. Condition 3 (`directives` renders) is the intent-serving part — the wave-transition wiring is stored and never delivered. Conditions 1, 2 and 4 are a completeness taxonomy over eight fields, satisfiable by moving seven of them into a "deliberately not projected" bucket with a written reason and nothing behaving differently. That is bookkeeping earning a slot at the head of the chain, and it is the same work/done-condition mismatch the spec diagnoses in E, sitting inside the section that runs first. The execution-order table's stated reason for link 1 — "everything reads through the projection; `directives` is inert until it renders" — is a reason for condition 3 alone. If the taxonomy is worth doing it can run beside the chain like A's remainder and D's debt, rather than gating four workstreams. |  |  |
| F60 | intent-fit | MINOR | The three-tier table does more rhetorical work than the epic's contents support. It presents the organising principle as cross-cutting Gate, Wave and Epic, but only the Gate row is work in this spec — the Wave row is already merged and the Epic row is this document's own framing, not a deliverable. So the table reads as three independent instantiations converging on one idea when it is really one workstream (C) plus two things pointed at retrospectively. That matters because the convergence is what makes the principle feel established rather than assumed, which is the gap F1 names. Mark which rows are evidence and which are work. |  |  |
| F61 | testability | MINOR | F's acceptance test 2 asks that leases "never collide" across two concurrently driven spines, with no positive control showing the same two runs *do* collide under a shared identity. Two agents that happen not to contend, or a rig where the second never actually claims, pass. The falsifying arm is the pre-fix configuration, and it is not required. |  |  |
| F62 | testability | MINOR | F's measure 5 keeps no `n`, no pass threshold and no pre-registered list of countable events, while C explicitly grades both as placeholders. exc-9's cited figures (24–27 vs 14) come from a four-gate toy at what appears to be single-digit `n`. The caution to "count recovery events on the far side of the door too" is the right instinct but names no boundary — whether harness-level argument repair, silent model retries after a validation error, or server maintenance counts is left to whoever tallies, which is how a measure gets defined after the result is seen. |  |  |
| F63 | testability | MINOR | The token constraint "the net must not go the wrong way" has no denominator. Roughly 1,000 tokens of always-loaded schema is paid per agent per session regardless of whether that agent touches the engine, while the ~4,500 bought back is on-demand and paid only by agents that read the reference. Per-run, per-agent and per-fleet accounting give different signs, and the spec picks none, so the constraint can be satisfied by choosing the unit. |  |  |
| F64 | testability | MINOR | B's done-condition 3 — an agent "can see the wave-transition wiring **at the gate where it applies**" — is fully satisfied by rendering `directives` at every gate. No check distinguishes correct gate-scoping from render-everywhere, and render-everywhere directly contradicts the organising principle's gate-local reveal. The scoping is the interesting half and it is unfalsified. |  |  |
| F65 | testability | MINOR | A's binding sweep is recorded as a one-off well-executed departure (64 → 1, sparing the entry with a live spine and lease) with no standing test that the sweeper spares live bindings. The next sweep, under a different concurrency shape, re-runs the same risk with the same absence of a guard, and the evidence of correctness is a count of remaining entries — which any single spared entry satisfies. |  |  |
| F66 | testability | MINOR | A2's done-condition 3 reduces to "the DIGEST is present" — an existence check on an artifact, which the spec's own E analysis identifies as the shape that passes while the work is absent. A DIGEST written empty, stale, or from the pre-trip state satisfies it, while "the handoff has the thing it depends on" is the claim that matters. The check should be on the DIGEST's content reflecting the tripped gate. |  |  |
| F67 | testability | MINOR | The `directives` schema mismatch (`docs/CHECKLIST_SCHEMA.md` says `[string] \ |  |  |
| F68 | testability | MINOR | "Overrides only where a gate has actually bitten" (A2 DC4, A's threshold discipline) has no instrument for "bitten" — and with the gauge unwired outside harnesses and silent under multi-spine, no gate can be observed biting. DC4 is then satisfied vacuously by shipping one default and zero overrides. The one evidence line that touches this ("an override changes behaviour at exactly one gate and not its neighbours") tests the mechanism if an override exists, but nothing requires one to. |  |  |
| F69 | testability | MINOR | The appetite clause scales rigor to reversibility but no section states its own reversibility grade, so "cheap to reverse, move fast" is available after the fact to excuse any omitted evidence. The spec names only two costly-to-revert items (cluster boundaries, C's tranche); by omission everything else is implicitly cheap, including A2's verb-contract change and F's door, neither of which is obviously cheap to unwind once 21 templates are written against it. |  |  |
| F70 | testability | MINOR | C's done-condition 3 ("per-run delivered tokens do not grow") is not normalised to a run protocol. Relocated text is paid per `current` call at its gate, and the number of `current` calls is agent- and run-dependent, so the same tranche passes or fails depending on how chatty the tracer agent is and how long the run goes. Without a fixed protocol and repeat count, the constraint meant to catch "the tranche is too big" is dominated by run-to-run variance. |  |  |
| F71 | done-condition fidelity | MINOR | E offers an ambiguous signal as its cleanest evidence. "Whether any label group turns out to be empty after the redux, which would be the cleanest possible evidence that the filter worked" — an empty group is equally produced by the redux subsuming those findings *and* by the re-cut dropping them, which is the failure F2 describes. Emptiness is evidence the filter worked only if each vanished finding is accounted for by a named close; as an aggregate observation it points both ways. |  |  |
| F72 | done-condition fidelity | MINOR | F's token constraint is called load-bearing and given no checkable form. "Keep that as a constraint — the net must not go the wrong way" appears in prose and inside DC5's commentary, but is not an enumerated done-condition item and carries no measurement protocol, baseline, or bound. The one number offered (~1,000 tokens of always-loaded schema against ~4,500 bought back) is a pre-build estimate, not a post-build check. A constraint nobody is obliged to measure will not be measured. |  |  |
| F73 | claim accuracy | MINOR | "**#440, in flight**", and the Execution order lists "**#440 merge**" as remaining independent work. The merge is already on `main`: `90f0343 merge(#440): a worktree-dispatched agent's reading lands in its own tree`, 2026-08-07 09:27:26 -0700, and `git branch --contains 90f0343` → `main`. The tracker issue #440 is still OPEN — the same unpaid-retirement pattern as F6. Commands: `git log -1 --format='%H %ci %s' 90f0343`; `git branch --contains 90f0343`. (Note: the sha `3b0b90f` I was asked to re-check against does not exist in this repository — `git cat-file -t 3b0b90f` → "Not a valid object name". The #440 merge on main is `90f0343`, and it predates every check in this review.) |  |  |
| F74 | claim accuracy | MINOR | E: "theme classification (13 labels across **98 of 138** open issues)" and "consolidating **138**". 13 labels and 98 labelled are both correct; the denominator is stale. `gh issue list --state open --limit 300` returns **142** open, so **44** carry no theme label, not 40. All four per-label counts named in E are exact: `theme:engine-mechanics` 11, `theme:built-not-wired` 14, `theme:context-governor` 13, `theme:checks-that-cannot-fail` 6 (python Counter over `gh issue list --state open --limit 300 --json number,labels`). The drift matters because E's input is "whatever survives the redux" — four issues have arrived since labelling and sit outside the classification E is told to run on. |  |  |
| F75 | claim accuracy | MINOR | B: "**Eight** populated fields on it reach `current()` not at all: `directives`, `context_refs`, `child_checklist`, `status_detail`, `result`, `finding`, `title`, `rework_count`." `_EXCLUDED_FIELDS` holds 14 entries; four of them (`id`, `status`, `preconditions`, `postconditions`) do reach `current()`, leaving **ten** that do not — the eight named plus **`evidence`** and **`why_exempt`**, neither of which is read by `state()` (`scripts/checklist_engine.py:1565-1600`) or emitted by `render_human()` (`:1644-1692`). So B's "Open" item covers nine remaining fields, not seven. Command: `sed -n '4004,4006p' tests/test_checklist_engine.py` read against `sed -n '1565,1700p' scripts/checklist_engine.py`. |  |  |
| F76 | claim accuracy | MINOR | "Hand-authoring a threshold for every gate in 21 templates invents **~100** ungraded placeholders" — stated twice, in A and in A2's done-condition 4. There are **68** gates across the 21 templates, not ~100; python sum over `tasks` in `skills/*/templates/*.json`, re-run at HEAD 1f4c6de. The argument survives at 68; the number is presented without a grade and is ~47% high. |  |  |
| F77 | claim accuracy | MINOR | A: "`docs/GAUGE_WRITER_HOOK.md` corrected — **20 `agentId` references**". The doc contains **2** occurrences of `agentId` and **21** of `agent_id`. Command: `grep -o -i "agent[_-]\?id" docs/GAUGE_WRITER_HOOK.md \ |  |  |
| F78 | claim accuracy | MINOR | F's cost cluster ends: "This session added another: the first engine call made here failed on an unrecognised `--session-id`, costing a round-trip to re-read usage." This is stated as a measured instance inside a paragraph whose whole point is that the cost is "a filed cluster, not a hypothesis," but it carries no issue, no artifact, and no command that reproduces it. `--session-id` is a valid top-level parser argument (`scripts/checklist_engine.py:2396`) and is required on three subcommands (`:2402, :2408, :2410`), so the failure was position-dependent and I cannot reconstruct which call it was. Every other item in that cluster verified: #442, #439, #446, #427, #443 all exist, OPEN, with titles matching the spec's descriptions; `docs/agents/engine-config.json` does not exist while **11** templates point `config_ref` at it; and `COMMANDER_SPINE` `archive.c2b` carries `gh pr list --head <branch> --state open` with `<branch>` unresolved and `--state open` hardcoded, confirming #439 and #446 in one read. |  |  |
| F79 | claim accuracy | MINOR | The exc-9 tracer figures are reproduced correctly — "14 calls and zero fumbles through tools" against "24–27 calls with 2 refusals and 4–7 help-reads" matches `.agent-work/archive/2026-08-03-explore-post-phase1/DESIGN_SPEC.md:43,144` verbatim, and the three prototype worktrees still exist (`C:/Programs/.proto-exc6-governor-subagent-identity`, `.proto-exc8-spine-instructions`, `.proto-exc9-mcp-front-door`), so re-measurement is possible. Two qualifiers the source carries and the spec drops while promoting these numbers to "the headline": **n=2** ("two replicates per arm"), and the source's own confound — "part of the win came from teaching sentences written into the tool descriptions, not from MCP structure; a bare-descriptions control arm is the named next variant." The spec instead records rich descriptions as an accepted constraint with no control arm (ruling 3), which leaves the headline acceptance metric measuring description quality and tool structure together. Command: `grep -n "exc-9" .agent-work/archive/2026-08-03-explore-post-phase1/DESIGN_SPEC.md`. |  |  |
| F80 | claim accuracy | MINOR | B: "the iterative-planning merge of 2026-08-07 put the replan/shaped-brief wiring there… **before that merge the Admiral template had no `directives` at all**." The field was present on all four Admiral gates before the merge, as `null`. Command: `git show 178a980^:skills/admiral/templates/ADMIRAL_SPINE.template.json` against `git show 178a980:…` — before: `init`/`latitude`/`execute`/`closeout` all `directives=null`; after: `execute` populated with `{"wave_transition": {…}}`, the other three still null. The merge commit and date are correct (`178a980`, 2026-08-07 07:18:16 -0700). The load-bearing part of the claim holds and I confirmed it independently: `state()` never reads `directives`, `render_human()` never emits it, the engine copies it on `add` (`:2029`) and lists it as overwritable on `rescope` (`:2143`), no `.md` under `skills/` mentions it, and `docs/CHECKLIST_SCHEMA.md:123` types it `[string] \ |  |  |
| F81 | claim accuracy | MINOR | A asserts "This epic's own Admiral ran a full day with the gauge silent." I could not check the duration and found evidence against the literal reading: `.agent-work/epic-418/gauge.json` and `.agent-work/epic-418/gauge-skip.json` both exist, so the session was not uniformly silent. #452's evidence table supports the mechanism (a bare-keyed orchestrator trips its own ambiguity guard), but nothing in the tree establishes "a full day". A claim presented as observed with no artifact that dates it. |  |  |
