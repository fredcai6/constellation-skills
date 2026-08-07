# REVIEW_RESULT — g4-review (issue #102, Moves 4, 5, 8)

## Assigned Gate
`g4-review` — three cross-tier doctrines consolidated into `skills/_shared/global-everyone.md`.

## Result
`APPROVE`

## Handoff compliance
All three moves done as asked. Each doctrine now reads once as its own canonical subsection in
`global-everyone.md` (between `## Universal posture` and `## Deep-module vocabulary`); every carrier is
reduced to a pointer + genuine role-specific tail. Move 4 kept partial (prototyper references local),
move 5 was not force-merged, move 8 broadening is treated as ruled. Suite green.

## Scope drift
Clean. `git status --porcelain` = exactly the 6 expected modified files (global-everyone, explorer,
prototyper, commander, reviewer, admiral SKILL.md). `git status --porcelain skills/prototyper/references/`
is EMPTY. No untracked files; no new `global-*.md` (the 5 shared files pre-exist; only global-everyone
was modified). Commander diff = 2 hunks (move-5 `gN-integrate`; move-8 "not a licence to guess"); admiral
diff = 1 hunk (move-8). No other-gate doctrine (unchanged-tree shortcut, crew-idle, closeout, worktree,
design-it-twice) touched — every other passage byte-identical.

## Evidence verdict
Independently reproduced all three before/after grep pairs and the suite:
- M4 `never the idea class`: explorer 0, prototyper 0, global-everyone 1.
- M5 `not on what the result claims|never on what the report asserted`: commander 0, reviewer 0;
  global-everyone `never on what the report asserted` 1.
- M8 `delegate is not a replacement`: commander 0, admiral 0, global-everyone 1.
- `py -m pytest tests/ -q` → 442 passed, 2 skipped, 26 subtests passed in 11.71s.
All match the IMPLEMENTER_RESULT exactly.

## Per-move findings

### Move 4 — scoped-nulls (PARTIAL) — PASS
`## Scoped nulls` in global-everyone carries the full general principle once: negative result kills the
specific test not the idea class; verdicts state what was tested AND NOT tested; empty-scope null =
unfinished; default next move is another variant; impossibility needs class-spanning evidence; report
"this specific test failed," never "X is impossible." Explorer item-2 = pointer + genuine tail (failed
*excursion* scopes its null, next move another excursion variant into the next cycle, optimistic
persistence). Prototyper = pointer + genuine tail (reducer-shape example, `NOT tested` line mandatory).
`prototyper/references/` untouched. No meaning dropped.

### Move 5 — world-verification — PASS (justified one-principle consolidation, NOT a force-merge)
Confirmed the reconcile decision. Commander and reviewer copies expressed the SAME principle (confirm each
claimed side-effect at its source; judgment rests on observation, not assertion) applied to different
objects (commander verifies its dispatched crew's result; reviewer verifies the implementer's report).
Consolidated once as `## Verify claimed side-effects against the world`, using neutral wording ("a claim
you cannot reproduce is a defect"). Role applications kept as tails: commander keeps its integrate/
freshness mechanics (run the verification command; IMPLEMENTER_RESULT fresh via `run_crew.py
--verify-result`; postconditions pass in your hands); reviewer keeps the distinct consequence ("a claim
you cannot reproduce is a **BLOCK finding**"). No genuinely role-specific rule was dropped or merged away.

### Move 8 — delegate-not-replacement — PASS (broadening ruled)
`## A delegate is not a replacement` reads once: escalating upward is a first-class move at every tier,
never a failure; the chain terminates at the human; each tier reaches up when its knowledge/latitude run
out; asking up is always sanctioned. Commander tail = pointer + "the tier you reach up to is the Admiral;
float via your return/stop shape." Admiral tail = pointer + "reach the human out-of-band via the latitude
contract's out-of-taxonomy / expiry escalation." The "I need to talk to my human" phrasing is preserved
in the canonical section. Broadening to all tiers is deliberate per the launch-order pre-ruling — not a
defect. No meaning dropped.

## Map impact verdict
- **Evidence supports claimed change:** yes — grep pairs + suite reproduce.
- **Constraints not violated:** yes — append-only into existing file; each carrier keeps pointer + tail;
  partial move 4 honored; no force-merge on move 5; broadening ruled on move 8.
- **Notes match the diff:** yes — 3 canonical subsections added, 5 carriers inherit-by-pointer,
  prototyper/references unchanged, no new filename.
- **Decision candidates surfaced:** n/a — destinations were pre-ruled; implementer decided only wording/
  tail/pointer phrasing, within latitude.
- **Durable context routed:** yes — Map Impact reuses inbound anchors for Cartographer reconcile.

## Reconciliation check
Doc-only doctrine consolidation to already-ruled destinations. No structural/contract divergence requiring
Commander reconcile beyond the ruled moves. Nothing to escalate.

## Blockers
- None.

## Out-of-scope observations
- Non-blocking (implementer already noted): the move-5 concept name "claimed side-effect" still appears in
  the two carrier pointers because each pointer cites the canonical section by title, while move 8 uses a
  slug reference ("inherited delegate-not-replacement doctrine") that leaves zero echo. If a future gate
  wants carriers to avoid even the section-name echo, standardizing on slug-style pointers would zero it.
  Triage candidate at most (possible g7 content-pin nicety), not a defect — the moved principle *prose* is
  gone from both carriers.

## Workflow Feedback
- **Handoff gaps:** none — the handoff was complete and unambiguous: the three moves, the per-move
  independent-judgment framing, allowed scope, exclusions (prototyper/references, other-gate doctrine),
  the exact 6-file expectation, and the commander/admiral "only the two passages" constraint were all
  explicit and directly checkable.
- **Context rediscovered:** none material. Minor: `config_ref` in the survey template points to
  `docs/agents/engine-config.json`, which does not exist in this worktree; the engine tolerated its
  absence (prior g1/g2/g3-review surveys carry the same dangling ref), so it was a non-issue — noting only
  so the dangling config_ref is known.
- **Instructions improvised around:** the reviewer template's single `r4-quality` check does not fit a
  three-independent-move gate, so — per the skill's "append one check per inherited rule" — I split it
  into `r4-move4` / `r4-move5` / `r4-move8` to keep each move a separately-recorded judgment rather than a
  batch pass. Reported here as the skill directs.
- **What would have made this easier:** nothing needed; a move-style handoff template with a per-move check
  slot would formalize the split I improvised, but the current handoff carried enough to do it correctly.

## Return status
`complete`
