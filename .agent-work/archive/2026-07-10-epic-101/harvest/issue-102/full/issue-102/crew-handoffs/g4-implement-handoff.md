# Implementer Handoff

## Gate
g4-implement (issue #102, Moves 4, 5, 8 — three cross-tier rules into global-everyone.md)

## Task
Three DISTINCT cross-tier doctrines, each reconcile-then-cut into `skills/_shared/global-everyone.md`
as its own canonical subsection; each carrier reduced to a pointer, keeping only a genuine
role-specific tail. Each move produces its OWN before/after carrier-count grep (three separate pairs).
Destination for all three is global-everyone (each is a cross-tier rule; ruled by the launch order).

### Move 4 — scoped-nulls doctrine (PARTIAL move — read carefully)
Carriers: `skills/explorer/SKILL.md` (item "2. Scoped nulls, optimistic persistence." ~line 20; and
the pointer line ~68 "Every excursion verdict obeys scoped-nulls doctrine.") and
`skills/prototyper/SKILL.md` (§"Scoped nulls" ~lines 24-30).
Move ONLY the GENERAL principle to global-everyone: a negative result kills *that specific test under
those conditions*, never the idea class; every verdict states what was tested AND what was NOT tested;
the default next move after a null is another variant, not a closed branch; impossibility is a
class-spanning claim needing class-spanning evidence; report "this specific test failed," never "X is
impossible."
KEEP LOCAL (do NOT move, do NOT delete): prototyper's spike-domain APPLICATIONS in
`skills/prototyper/references/measurement.md` and `references/ui.md` (board mechanics, variant
guidance) — they are prototyper-specific, not cross-tier. Leave those two files untouched.
After the cut: explorer's item 2 and prototyper's §Scoped nulls become a pointer to global-everyone,
each keeping a genuine tier-specific tail only if one carries real role-specific content (e.g.
explorer's "optimistic persistence / next move is another excursion variant" framing; prototyper's
"the NOT-tested line in the result is mandatory"). Do not lose those role-specific specifics — keep
them as a short tail beside the pointer.

### Move 5 — world-verification of claimed side-effects
Carriers: `skills/commander/SKILL.md` (~line 52, gN-integrate: "confirm each claimed side-effect
against the world ... advance on what you observe, not on what the result claims") and
`skills/reviewer/SKILL.md` (~line 18: "Verify every claimed side-effect against the world, not against
the report ... verdict rests on what you observed, never on what the report asserted").
RECONCILE: these share ONE principle (never accept a claimed side-effect without independent
reproduction; judgment rests on observation, not assertion) applied to different OBJECTS (commander
verifies its own dispatch's crew result; reviewer verifies the implementer's report). The shared
principle is the cross-tier rule → global-everyone. The role-specific APPLICATION stays local as a
tail: commander keeps its integrate mechanics (IMPLEMENTER_RESULT freshness via run_crew
--verify-result, postconditions passing in your hands) + pointer; reviewer keeps its "a claim you
cannot reproduce is a BLOCK finding" tail + pointer. If on close reading the two prove genuinely
semantically distinct rather than one shared principle, do NOT force-merge — keep both and report it
as an honest partial (but the expected outcome is: shared principle consolidates, role tails stay).

### Move 8 — delegate-not-replacement
Carriers: `skills/commander/SKILL.md` (~line 83: "A delegate is not a replacement: asking up is always
sanctioned ... the chain terminates at the human") and `skills/admiral/SKILL.md` (~line 45: "A
delegate is not a replacement: ... 'I need to talk to my human' is a first-class move, not a
failure"). Same principle. Consolidate to global-everyone: escalating upward — floating a decision
beyond your latitude, or "I need my human" — is a first-class move at EVERY tier, never a failure; the
chain terminates at the human, and each tier reaches up when its own knowledge and latitude run out.
NOTE (surfaced decision, ruled): global-everyone bundles into crew skills too, so this deliberately
broadens the principle to every tier — that is intended per the launch-order pre-ruling, not silent
scope creep. Commander keeps its "float to the Admiral" tail + pointer; admiral keeps its "reach the
human out-of-band via the latitude contract" tail + pointer.

## Test Mode
Inspection-only; keep suite green (`py -m pytest tests/ -q`). g7 adds content-pins later.

## Close Criteria
- Three new canonical subsections in global-everyone.md (scoped-nulls, world-verification,
  delegate-not-replacement), dense agent-facing register, meaning preserved.
- Each carrier reduced to a pointer + a genuine role-specific tail where one exists:
  move 4 → explorer + prototyper SKILL.md (measurement.md/ui.md UNTOUCHED);
  move 5 → commander + reviewer; move 8 → commander + admiral.
- No new global-*.md filename.
- THREE separate before/after carrier-count grep pairs (command + output), one per move.
- Full suite green.

## Allowed Scope
skills/_shared/global-everyone.md; skills/{explorer,prototyper,commander,reviewer,admiral}/SKILL.md.
NOT prototyper/references/*.

## Specific Exclusions
prototyper/references/measurement.md + ui.md (keep local — move 4 partial); banners (done, g3); the
compliance pointers (done, g1/g2); manifest/ROADMAP/repo-root stray (#105); design-it-twice &
sibling-ids & unchanged-tree & crew-idle (other gates). Commander/admiral each appear in later gates
too — touch ONLY the move-5/move-8 passages here, leave the rest.

## Constraints
- Append into existing global-everyone.md only; each carrier keeps a pointer.
- Register: dense, agent-facing; emphasis only at mechanism-backed gates.
- Reconcile-then-cut: do not drop meaning; do not force-merge genuinely distinct rules (move 5 watch).
- Move 4 is PARTIAL: general principle moves, prototyper spike applications stay.

## Map Anchors (inbound)
- Structural: global-everyone.md; explorer/prototyper/commander/reviewer/admiral SKILL.md; prototyper/references (stay).
- Constraint: bundle glob green; prototyper spike applications not deleted.
- Decision: these three are cross-tier -> global-everyone (ruled).

## Deliverable Path Check
- Committed — global-everyone.md + the 5 carrier SKILL.md (tracked, not ignored).
- Local-only — .agent-work/issue-102/crew-handoffs/g4-implement-result.md.

## Required Evidence
Three per-move before/after grep pairs (command + output); quoted canonical + one carrier pointer per
move; suite tail. Confirm measurement.md + ui.md are unchanged (`git status` shows them absent).

## Verification Commands
```bash
cd C:/Programs/constellation-wt-102
grep -rn "this specific test failed\|never the idea class" skills/explorer/SKILL.md skills/prototyper/SKILL.md
grep -rn "claimed side-effect against the world\|what you observe" skills/commander/SKILL.md skills/reviewer/SKILL.md
grep -rn "delegate is not a replacement" skills/commander/SKILL.md skills/admiral/SKILL.md
grep -c "Scoped nulls\|claimed side-effect\|delegate is not a replacement" skills/_shared/global-everyone.md
git status --porcelain skills/prototyper/references/   # must be empty
py -m pytest tests/ -q
```

## Suggested Model Tier
stronger — three register-sensitive reconciles with semantic-vs-drift + partial-move + tier-broadening judgments.

## Authority
Destinations ruled (all global-everyone). You decide canonical wording, tail content, pointer phrasing,
and (move 5) whether the two copies are one shared principle or genuinely distinct. Report honestly.

## Stop Conditions
Stop and return if: move 4 cannot separate the general principle from role-specific applications
cleanly; move 5 proves genuinely distinct (keep both, report partial); a carrier's rule entangles with
another gate's doctrine you'd have to touch.

## Return Format
Return IMPLEMENTER_RESULT (write to .agent-work/issue-102/crew-handoffs/g4-implement-result.md AND as
your final message): per-move slice + disposition, files changed, THREE before/after grep pairs,
canonical + pointer quotes per move, confirmation measurement.md/ui.md untouched, suite tail,
assumptions, stop conditions, out-of-scope observations, workflow feedback. Your FINAL MESSAGE must be
the complete IMPLEMENTER_RESULT.
