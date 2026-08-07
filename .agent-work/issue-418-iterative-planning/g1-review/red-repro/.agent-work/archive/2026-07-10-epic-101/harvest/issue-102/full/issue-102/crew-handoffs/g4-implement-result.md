# IMPLEMENTER_RESULT — g4-implement (issue #102, Moves 4, 5, 8)

## Summary
Three distinct cross-tier doctrines reconciled-then-cut into `skills/_shared/global-everyone.md`, each as its
own canonical subsection; each carrier reduced to a pointer + genuine role-specific tail. All moves clean; no
stop conditions hit; no force-merge. Suite green. `prototyper/references/` untouched (partial-move honored).

Engine: gated plan `.agent-work/issue-102/g4-implement-plan.json` driven to `DONE` (m0-context → m1-move4 →
m2-move5 → m3-move8 → m4-suite, each command-checked).

## Per-move disposition

### Move 4 — scoped-nulls (PARTIAL move) — DONE, clean
General principle moved to global-everyone `## Scoped nulls`. Explorer item 2 and line-68 pointer, and
prototyper `## Scoped nulls`, reduced to pointer + role tail. `prototyper/references/measurement.md` and
`ui.md` deliberately UNTOUCHED (spike-domain applications are prototyper-specific, not cross-tier).
- Explorer tail kept: "optimistic persistence / the default next move is another *excursion* variant, carried
  into the next cycle".
- Prototyper tail kept: the reducer-shape scoping example + "the `NOT tested` line is **mandatory**".
- Line 68 kept as pointer, now anchored to `references/global-everyone.md`.

### Move 5 — world-verification of claimed side-effects — DONE, clean (shared principle, NOT distinct)
On close reading the commander and reviewer copies are **one shared principle** (never accept a claimed
side-effect without independent reproduction; judgment rests on observation, not assertion) applied to different
objects (commander verifies its own dispatch's crew result; reviewer verifies the implementer's report). Not
genuinely distinct → consolidated to global-everyone `## Verify claimed side-effects against the world`; role
applications stayed local as tails. Did NOT force-merge; the reconcile was warranted.
- Commander tail kept: integrate mechanics — IMPLEMENTER_RESULT freshness via `run_crew.py --verify-result`,
  pasted evidence reproduces, postconditions pass in your hands.
- Reviewer tail kept: "a claim you cannot reproduce is a **BLOCK finding**, not an accepted fact".

### Move 8 — delegate-not-replacement — DONE, clean (deliberately broadened to all tiers, ruled)
Commander + admiral copies consolidated to global-everyone `## A delegate is not a replacement`, deliberately
broadened to EVERY tier per the launch-order pre-ruling (global-everyone bundles into crew skills too). Not
silent scope creep — intended.
- Commander tail kept: "the tier you reach up to is the **Admiral**; float via your return/stop shape".
- Admiral tail kept: "reach the human **out-of-band** via the latitude contract's out-of-taxonomy / expiry
  escalation".

## Files changed (6; all tracked, committed by Commander at gate close)
- `skills/_shared/global-everyone.md` — +3 canonical subsections
- `skills/explorer/SKILL.md` — move-4 carrier → pointer + tail (item 2 + line 68)
- `skills/prototyper/SKILL.md` — move-4 carrier → pointer + tail (§Scoped nulls)
- `skills/commander/SKILL.md` — move-5 (gN-integrate) + move-8 passages → pointer + tail
- `skills/reviewer/SKILL.md` — move-5 carrier → pointer + tail
- `skills/admiral/SKILL.md` — move-8 carrier → pointer + tail
- `skills/prototyper/references/` — UNTOUCHED (porcelain empty) ✓

## THREE before/after grep pairs (command + output)

### Move 4 (signature phrase `never the idea class`)
BEFORE — carriers:
```
$ grep -rnc "never the idea class" skills/explorer/SKILL.md skills/prototyper/SKILL.md
skills/explorer/SKILL.md:1
skills/prototyper/SKILL.md:1
```
AFTER — carriers 0, global-everyone 1:
```
$ grep -rnc "never the idea class" skills/explorer/SKILL.md skills/prototyper/SKILL.md
skills/explorer/SKILL.md:0
skills/prototyper/SKILL.md:0
$ grep -nc "never the idea class" skills/_shared/global-everyone.md
1
```

### Move 5 (signature = moved conclusion clause `not on what the result claims|never on what the report asserted`)
BEFORE — carriers each carry the clause:
```
$ grep -rn "claimed side-effect against the world\|what you observe" skills/commander/SKILL.md skills/reviewer/SKILL.md
skills/commander/SKILL.md:52: ... confirm each claimed side-effect against the world ... advance on what you observe, not on what the result claims.
skills/reviewer/SKILL.md:18: Verify every claimed side-effect against the world ... verdict rests on what you observed, never on what the report asserted.
```
AFTER — carriers 0 on the moved clause, global-everyone 1:
```
$ grep -rEnc "not on what the result claims|never on what the report asserted" skills/commander/SKILL.md skills/reviewer/SKILL.md
skills/commander/SKILL.md:0
skills/reviewer/SKILL.md:0
$ grep -Enc "never on what the report asserted" skills/_shared/global-everyone.md
1
```
(Note: the shared concept name "claimed side-effect" legitimately recurs in the two carrier pointers because
each pointer names the canonical section; the *principle prose* — the conclusion clause — is what moved, and it
is now gone from both carriers.)

### Move 8 (signature phrase `delegate is not a replacement`)
BEFORE — carriers:
```
$ grep -rnc "delegate is not a replacement" skills/commander/SKILL.md skills/admiral/SKILL.md
skills/commander/SKILL.md:1
skills/admiral/SKILL.md:1
```
AFTER — carriers 0, global-everyone 1:
```
$ grep -rnc "delegate is not a replacement" skills/commander/SKILL.md skills/admiral/SKILL.md
skills/commander/SKILL.md:0
skills/admiral/SKILL.md:0
$ grep -nc "delegate is not a replacement" skills/_shared/global-everyone.md
1
```

## Canonical + pointer quotes per move

### Move 4
Canonical (global-everyone `## Scoped nulls`): "A negative result kills *that specific test under those
conditions* … **never the idea class**. Every verdict states what was tested **and what was NOT tested** … The
default next move after a null is **another variant** … Report \"this specific test failed,\" never \"X is
impossible.\""
Explorer pointer: "**2. Scoped nulls, optimistic persistence.** Inherited doctrine — see
`references/global-everyone.md` §\"Scoped nulls\". Explorer-specific: a failed *excursion* scopes its null, and
the default next move is **another excursion variant** …"

### Move 5
Canonical (global-everyone `## Verify claimed side-effects against the world`): "Never accept a claimed
side-effect on the strength of the claim … confirm it **at its source** … Your judgment rests on what you
observed, never on what the report asserted."
Reviewer pointer: "Verify claimed side-effects against the world, not against the report, per inherited doctrine
(`references/global-everyone.md` §\"Verify claimed side-effects against the world\") … Reviewer-specific: a claim
you cannot reproduce is a **BLOCK finding** …"

### Move 8
Canonical (global-everyone `## A delegate is not a replacement`): "Escalating upward … is a **first-class move at
every tier, never a failure**. The chain of delegation terminates at the human; each tier reaches up when its own
knowledge and granted latitude run out …"
Commander pointer: "… This is inherited delegate-not-replacement doctrine — see `references/global-everyone.md`.
Commander-specific: the tier you reach up to is the **Admiral** …"

## measurement.md / ui.md untouched — confirmed
```
$ git status --porcelain skills/prototyper/references/
(empty)
```

## Suite tail
```
$ py -m pytest tests/ -q
442 passed, 2 skipped, 26 subtests passed in 12.07s
```
Also run green as the m4-suite engine command postcondition (`advance m4-suite -> complete`).

## Handoff verification block (all carrier greps empty; global section-count 4)
```
$ grep -rn "this specific test failed\|never the idea class" skills/explorer/SKILL.md skills/prototyper/SKILL.md   -> (empty)
$ grep -rn "claimed side-effect against the world\|what you observe" skills/commander/SKILL.md skills/reviewer/SKILL.md -> (empty)
$ grep -rn "delegate is not a replacement" skills/commander/SKILL.md skills/admiral/SKILL.md -> (empty)
$ grep -c "Scoped nulls\|claimed side-effect\|delegate is not a replacement" skills/_shared/global-everyone.md -> 4
```
(The `-c` value is 4, not 3, because "claimed side-effect" legitimately appears on two lines of the move-5
section — the `## Verify claimed side-effects…` header and the body's "claimed side-effect on the strength of the
claim". It is a lines-matched count, not a section count; all three sections are present.)

## Assumptions
- Destinations were ruled (all three → global-everyone); I decided canonical wording, tail content, and pointer
  phrasing.
- Move-8 broadening to all tiers is intended per the launch-order pre-ruling, treated as ruled (not scope creep).
- Placed the three new subsections between `## Universal posture` and `## Deep-module vocabulary`, grouped
  together (append into existing file, no new global-*.md filename).
- Command-check signatures were chosen to track the *moved principle prose*, not the section-name mention, so the
  before/after pairs measure a genuine reduction rather than a phrase the pointer legitimately re-uses.

## Stop conditions — none hit
- Move 4 general principle separated cleanly from role applications (references/ stayed local).
- Move 5 did NOT prove genuinely distinct — it is one shared principle; consolidated as expected, no partial.
- No carrier rule entangled with another gate's doctrine. Commander/admiral touched ONLY at the move-5/move-8
  passages; every other passage (crew-idle, delegated-mode intro, closeout, worktree doctrine, unchanged-tree
  shortcut) left byte-identical.

## Out-of-scope observations (triage candidates)
- None new. The move-5 concept name "claimed side-effect" now appears in three places (canonical + 2 pointers);
  if a future gate wants carriers to avoid even the section-name echo, a slug reference (as used for move 8)
  would zero it — noting as a possible g7 content-pin nicety, not a defect.

## Map Impact
Reusing inbound anchors: structural anchor `skills/_shared/global-everyone.md` gains three canonical
cross-tier subsections (Scoped nulls; Verify claimed side-effects against the world; A delegate is not a
replacement). Carriers `explorer/prototyper/commander/reviewer/admiral SKILL.md` now inherit-by-pointer for
these rules; `prototyper/references/*` unchanged. Decision anchor confirmed: these three are cross-tier →
global-everyone (ruled), with move-8 deliberately broadened to all tiers. No new filename; bundle glob intact.

## Workflow Feedback
- **Line-wrap vs. exact-phrase command checks (real friction).** My move-5 canonical sentence line-wrapped
  mid-phrase ("report\nasserted"), so the single-line `grep` postcondition FAILed on first advance even though
  the text was correct. Fixed by reflowing so the signature phrase stays on one line. Handoff lesson: when a
  gate's evidence is a single-line `grep` of prose you are wrapping at ~110 cols, keep the grepped phrase
  unwrapped, or author the check with `grep -z`/multiline. Worth a one-line note in future move-style handoffs.
- **Pointer-cites-title collides with the move's own signature grep (move 8).** Because the move-8 signature
  phrase *is* the section title, a pointer citing the section by title (§"A delegate is not a replacement")
  re-introduced the phrase into the carrier and failed the "carrier count → 0" check. Resolved by citing the
  section via slug ("inherited delegate-not-replacement doctrine — see …"). Handoff could pre-warn: when the
  moved phrase equals the destination heading, pointers must reference by slug, not by heading title.
- Handoff was otherwise complete and unambiguous: task, intent, scope, exclusions, evidence, test mode, stop
  conditions, return format all present; the PARTIAL-move carve-out for references/ and the move-5
  distinct-vs-shared latitude were both explicit and correct.
