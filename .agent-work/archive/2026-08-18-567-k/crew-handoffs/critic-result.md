# Cold plan critique — #634, lane K (pinned to 9b38b9d9)

## 1. Verdict in one paragraph

The guard-placement work (g1) is well-sourced and genuinely testable: real line numbers, real
negative tests, a real empirical measurement against the live Admiral spine instead of armchair
reasoning. But the plan as a whole optimizes for the easier half of #634 — freezing bookends — and
does almost nothing for the half the human called out by name: a role, crew included, actually
*capturing* "the plan changed, here's how" as a legible practice. Its own self-hosting proof gate
(g3) closes on two postconditions with `"check": null`, which is unfalsifiable by construction —
exactly the failure mode this repo says it cares most about. It claims `specs/` as in-scope but no
gate ever touches it, and I can show mechanically that touching only the shipped templates (not
the specs that are supposed to match them) leaves the declaration one regeneration away from
silently vanishing. And the comparison's central "trilemma" — immediate protection or backward
compatibility, not both — is a false binary once the two bookends are considered separately rather
than as a package deal.

## 2. Intent-fit findings

**The plan freezes; it does not make replanning legible.** (should-fix)
The human's ask had two co-equal halves: frozen bookends, and "I wouldn't be mad at a crew
updating its plan along the way too... capture 'the plan changed, here's how.'" Every gate in
`execute.json` (e0, g1, g2, g3) is about the first half. `ruling:plan-change-is-legible` in
`MISSION_FRAME.md` answers the second half by pointing at pre-existing machinery — `amend`'s
`cl["amendments"]` audit trail — that this run adds nothing to. I checked whether a crew is ever
told it can do this: `grep -rn "amend" skills/implementer/` returns nothing. `IMPLEMENTER_PLAN`
gets no closing bookend (freedom by omission), but no gate, template prose, or test demonstrates a
crew actually calling `spine_amend` on its own mid-run plan. Removing a restriction is not the
same as making a practice legible. Why it matters: a crew that never learns `amend` exists has the
same experience after this ships as before it. What I'd do instead: at minimum, one line of
`IMPLEMENTER_PLAN`/`skills/implementer/SKILL.md` prose plus a worked example, or an honest
admission in the mission frame that "capture" is out of scope for this run rather than implied
solved.

**IMPLEMENTER_PLAN's no-closing-bookend choice quietly opts crews out of a safety property every
other role spine keeps.** (consider)
`skills/implementer/templates/IMPLEMENTER_PLAN.template.json` has exactly `["m0-context", "m1"]`
(verified by loading it). With no closing bookend, `m1` — the crew's only real-work gate — stays
`drop`-able for the plan's entire life (`amend`'s `drop`, `scripts/checklist_engine.py:3076`, only
checks `status == "pending"`). Every OTHER role spine's closing bookend can never be dropped, so
something always survives to close through. A crew plan can, in principle, be amended down to zero
pending items. This is pre-existing engine behavior, not introduced by this change, but the design
never names the trade-off it's accepting by being the one spine type that opts out.

## 3. Testability findings

**g3-proof's postconditions cannot fail.** (blocking)
`execute.json:394-407` — `g3-proof`'s two postconditions both carry `"check": null`. This is the
gate that is supposed to be the run's actual empirical proof: read-only status on the live spine,
every mutating verb against a copy, full suite green in a clean detached worktree. None of that is
mechanically enforced. The gate's own imperative argues *against* dispatching a crew here because
"delegating the proof of my own change to a crew is exactly the self-grading this repo's
independent-reviewer premise exists to prevent" — but the actual effect of `check: null` is to
remove grading entirely, which is a stronger form of the same problem, not a fix for it. Compare
`g1-integrate`'s `c2` (`execute.json:178-185`), which has a real `command` check running pytest.
g3 could trivially carry an equivalent `command` check (run the suite in the detached worktree,
assert exit 0) or an `artifact` check against a recorded evidence file with the tally/`^FAILED`
grep/sha the imperative already demands be produced. As written, an agent that attests c1/c2
without running anything passes exactly as one that ran everything. Why it matters: this is the
gate meant to catch a regression in the mechanism that every other gate in the run exists to build.
What I'd do instead: give both conditions a real check — command or artifact-with-match — before
this ships.

**g2's postconditions never check *which* gates got the flag.** (should-fix)
`g2-implement`/`g2-review`/`g2-integrate` (`execute.json:216-381`) close on "IMPLEMENTER_RESULT
complete" / "REVIEW_RESULT APPROVE" / "verdict reproduced" — none of that verifies that
`bookend: true` actually landed on the correct gate ids in the correct templates. `g2-review`'s
imperative asks the reviewer to eyeball "declarations match what the design comparison and the
human's direction call for" and to confirm "each template still instantiates (init_work_area
round-trip)" — round-tripping proves the JSON parses, not that the right key is on the right gate.
A world where `bookend` is misspelled, applied to the wrong gate, or silently absent from one
template passes this gate as long as the reviewer's prose says APPROVE. Why it matters: this is
precisely the gate whose whole job is "did the declaration land where intended," and nothing
mechanical checks that. What I'd do instead: one test per template asserting the exact set of
bookend-flagged gate ids (e.g. `COMMANDER_SPINE`'s `init` and `archive` are `bookend: true`, every
other gate is not), wired into g2's postcondition as a `command` check.

## 4. Simplicity / YAGNI findings

**`specs/` is claimed in scope; nothing in the plan can actually make it correct.** (blocking)
`execute.json`'s sole-writer-scope constraint on every gate names `specs/` as in-scope, but no
gate's imperative ever mentions `specs/implementer.spine.toml` or `specs/reviewer.spine.toml`. I
checked what happens if they're left untouched: `scripts/generate_spine.py:687-712`
(`compile_spec`) and `:612-684` (`_compile_gate`) build the compiled task dict from a fixed field
list with no `bookend` key at all — and `specs/reviewer.spine.toml`'s own header comment confirms
this is deliberate doctrine: "a new spec key reaches no reader ... it would be dropped silently."
So even if a future author added `bookend = true` to the spec, today's compiler drops it on the
floor. That means: if `g2-implement` hand-edits `IMPLEMENTER_PLAN.template.json` to add the
declaration but leaves `specs/implementer.spine.toml` untouched, the declaration survives only
until someone next regenerates the template from its spec — at which point it silently vanishes,
because the compiler doesn't know the field exists. And the file that would need to change to fix
that, `scripts/generate_spine.py`, is named in neither the sole-writer scope nor the fenced list —
it's simply not addressed anywhere in the run. Why it matters: this is a durability hole in the
exact mechanism the epic exists to add, and it is invisible to every check in the plan because
nothing regenerates from spec as part of this run. What I'd do instead: either bring
`generate_spine.py` into scope and teach it the `bookend` field (and update both specs), or strike
`specs/` from the sole-writer-scope claim and say plainly that spec/template sync is out of scope
this wave.

## 5. The strongest argument AGAINST the recommendation of candidate B

`DESIGN_COMPARISON.md` frames "immediate protection, or backward compatibility. Not both." as a
property of *which candidate you pick*. It isn't — it's a property of *when you apply the
declaration*, which is orthogonal to the candidate, and the comparison's own evidence contains the
fourth option it never names:

B's decisive advantage, by the comparison's own argument, is that it "is the only candidate with a
retrofit path that goes through the engine" — an ordinary `rescope {bookend:true}` call. Nothing
stops that retrofit from being *run once, against every live spine, as part of shipping this
change* — e.g. as a step in `g3-proof` or a follow-on migration gate. That gives B's backward
compatibility (undeclared plans read exactly as before) **and** A's immediate protection (every
live spine gets frozen the moment the change ships), because "backward compatible" only describes
the mechanism's default; it says nothing about whether you also choose to exercise the retrofit
path against today's live spines in the same change.

A second, independent way to dissolve the same "trilemma": the two bookends don't have to use the
same declaration strategy. Every candidate's own crew-case analysis shows the *opening* bookend is
uncontested — nobody argues a crew should be free to reopen `m0-context`, and A's positional rule
for `items[0]` breaks nothing there. The real per-role variance the comparison spends most of its
words on is entirely about the *closing* bookend (crew wants none, others want one). So: apply A's
positional rule to freeze `items[0]` universally and immediately (uncontroversial, no declaration
needed, protects every live spine's start today), and reserve B's declared flag for the closing
bookend only, where the actual design tension lives. That is strictly more protection than B alone
ships today, with none of A's crew-case breakage, and the comparison never considers it because it
treats "backward compatible" and "immediate" as attributes of a whole candidate rather than
attributes it could mix per bookend.

## 6. Anything the author overclaimed, hedged, or quietly skipped

- **Overclaimed cheapness.** "Swapping A for B for C is roughly one function, not a rewrite" only
  counts the `checklist_engine.py` helper. It doesn't count keeping `specs/*.toml` and
  `generate_spine.py` in sync with whatever form is chosen (see §4) — a cost the comparison's own
  Claims/Evidence section never surfaces.
- **Quietly resolved a question the comparison called open.** `DESIGN_COMPARISON.md` states
  plainly that the `retext-check` hatch "is a real open question, not a bug any candidate closes,"
  and records candidate A's argument that refusing all correction is worse than leaving the hole
  open ("a bookend whose typo'd check can never be corrected is worse"). `execute.json`'s
  `g1-implement` then silently closes it anyway — "Guards go in add (ceiling), drop, rescope and
  retext-check" plus a negative test requiring retext-check of a bookend to be REFUSED — with no
  line anywhere addressing A's counter-argument or explaining why it's being overridden. This may
  be the right call, but the plan presents it as settled when the document it's built on explicitly
  flagged it as not.
- **Reviewer is silently absent from "every planning role."** `ruling:every-planning-role` says
  "build for Admiral, Commander and crew, not Commanders alone." Reviewer is also dispatched as
  crew, has its own compiled spine (`specs/reviewer.spine.toml` → `REVIEW_SURVEY.template.json`),
  and is never mentioned anywhere in `g2-implement`. The omission may be entirely correct — a
  survey's `amend` is already restricted to `retext-check`-only (`scripts/checklist_engine.py:3013
  -3029`), so add/drop/rescope are structurally impossible regardless of bookends — but that
  reasoning is never written down anywhere in the plan. It reads as an oversight because nothing
  states it as a decision.
- **The "capture" half isn't hedged, it's asserted solved** by citation of pre-existing machinery.
  See §2.

## 7. What is genuinely good (short)

- `g1`'s guard placement is grounded in actual source reads with line numbers
  (`scripts/checklist_engine.py:2971/3036/3076/3089/3115`), not summary or guesswork, and I
  independently confirmed those citations against the file.
- The Admiral-spine measurement in `DESIGN_COMPARISON.md` ("the window to reify waves closes the
  moment `execute` starts") is correct — I verified it against `_floor()`'s status-based logic and
  `drop`'s `status == "pending"` gate; it is a real empirical result, not an assumption.
- `g1`'s negative-test list (drop/rescope/retext-check of a bookend REFUSED, all-or-nothing, an
  explicit undeclared-plan-unchanged test) has real bite and is exactly the kind of check that can
  fail in the defective world.
- The repeated "never touch the live spine, prove against a copy in a fresh process" discipline is
  the right paranoia given this repo's own recorded lease-deadlock incident, and it's enforced as a
  constraint on every single gate rather than assumed once.
