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

## C, D, E, F — pending this conversation
