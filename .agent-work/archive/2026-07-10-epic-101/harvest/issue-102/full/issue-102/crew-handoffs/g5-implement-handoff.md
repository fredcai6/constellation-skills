# Implementer Handoff

## Gate
g5-implement (issue #102, Moves 6, 7 — two orchestrator rules into global-orchestrator.md)

## Task
Two orchestrator-tier doctrines, each reconcile-then-cut into `skills/_shared/global-orchestrator.md`
as its own canonical subsection; carriers reduced to pointer + genuine role-specific tail. Each move
its own before/after grep pair. Destination = global-orchestrator (both carriers are orchestrator-tier
— commander, admiral — so they still load the rule via the orchestrator bundle; ruled).

### Move 6 — unchanged-tree shortcut
Carriers: `skills/commander/SKILL.md` (~line 54, "Unchanged-tree shortcut.") and
`skills/admiral/SKILL.md` (~line 61, "Unchanged-tree shortcut."). Both carry the SAME evidence
contract: a redundant manual re-verification may be skipped ONLY when `git rev-parse HEAD` matches the
hash recorded with the last green run AND `git status --porcelain` is empty AND the prior green output
is pasted alongside the matched hash; any tree change (different HEAD or dirty tree) voids the
shortcut and forces a fresh run. Move that shared evidence-contract rule to global-orchestrator.
Role-specific tails stay local as a short tail beside each pointer:
- commander: "this does not change what an engine `command` postcondition executes on `advance` — the
  postcondition still runs its declared command every time; the shortcut governs only the manual
  Commander-facing re-verification."
- admiral: the wave-batching application — "batch several merges and re-verify once on the final merged
  main in a fresh worktree, rather than per-PR."

### Move 7 — crew-idle adjudication
Carriers: `skills/commander/SKILL.md` (~line 56, "Crew idle, no verdict.") +
`skills/admiral/SKILL.md` (~line 44, the idle-commander bullet) +
`skills/admiral/references/fleet-doctrine.md` (~line 156, "Adjudication invariants"). Shared rule: an
idle subagent (`idle_notification`, `idleReason: available`) that has produced COMPLETE artifacts is
*done*, not stalled — judge it from the artifact set (result content, files changed, diff), never from
the idle signal alone; complete artifacts → integrate as if the verdict arrived; silence + incomplete/
missing artifacts → *stalled*, rework or relaunch. This judges the VERDICT, not liveness — still
confirm the process dead before you reuse, sweep, or launch a continuation into its worktree. Move
that shared rule to global-orchestrator.
Role-specific tails stay local as a pointer + short tail:
- commander: the Implementer/Reviewer-at-gN-integrate framing.
- admiral: the Commander-at-wave-adjudication framing + "clean-room reviewer subagent" verification method.
- fleet-doctrine "Adjudication invariants": keep ONLY its epic-specific delta (its bite-list framing of
  Admiral errors) + a pointer to the shared rule; do not restate the full shared rule there.

## Test Mode
Inspection-only; keep suite green (`py -m pytest tests/ -q`). g7 adds content-pins (these two assert on
commander's bundled global-orchestrator.md, since orchestrator bucket bundles only to orchestrator tier).

## Close Criteria
- Two new canonical subsections in global-orchestrator.md, dense register, meaning preserved.
- commander + admiral reduced to pointer + genuine tail for BOTH moves; fleet-doctrine keeps epic delta + pointer.
- No new global-*.md filename.
- Two separate before/after carrier-count grep pairs (command + output).
- Full suite green.

## Allowed Scope
skills/_shared/global-orchestrator.md; skills/{commander,admiral}/SKILL.md; skills/admiral/references/fleet-doctrine.md.

## Specific Exclusions
Other gates' doctrine in commander/admiral (delegate-not-replacement, world-verification, sibling-ids,
design-it-twice — done or later). Touch ONLY the unchanged-tree + crew-idle passages. Do not re-open
move-4/5/8 passages.

## Constraints
- Append into existing global-orchestrator.md only; each carrier keeps a pointer + genuine tail.
- Register: dense, agent-facing; emphasis only at mechanism-backed gates.
- Reconcile-then-cut: preserve meaning; keep tier-specific application as tails.
- Pointer phrasing: cite by slug, not by section-title, when the moved phrase equals the heading
  (avoids re-introducing the signature into the carrier — a lesson from g4).

## Map Anchors (inbound)
- Structural: global-orchestrator.md; commander/admiral SKILL.md; admiral/references/fleet-doctrine.md.
- Constraint: global-orchestrator bundles only to orchestrator tier (content-pin will assert on commander).
- Decision: orchestrator-only rules -> global-orchestrator (ruled).

## Deliverable Path Check
- Committed — global-orchestrator.md + commander/admiral SKILL.md + fleet-doctrine.md (tracked).
- Local-only — .agent-work/issue-102/crew-handoffs/g5-implement-result.md.

## Required Evidence
Two per-move before/after grep pairs (command + output); canonical + pointer quotes per move; suite tail.

## Verification Commands
```bash
cd C:/Programs/constellation-wt-102
grep -rn "Unchanged-tree shortcut" skills/commander/SKILL.md skills/admiral/SKILL.md
grep -rn "idle_notification\|Crew idle" skills/commander/SKILL.md skills/admiral/SKILL.md skills/admiral/references/fleet-doctrine.md
grep -c "Unchanged-tree\|idle_notification\|idle subagent" skills/_shared/global-orchestrator.md
py -m pytest tests/ -q
```

## Suggested Model Tier
stronger — two register-sensitive orchestrator reconciles with tier-specific tails.

## Authority
Destinations ruled (global-orchestrator). You decide canonical wording, tails, pointer phrasing.

## Stop Conditions
Stop if: a rule entangles with another gate's doctrine; fleet-doctrine's epic delta can't be cleanly
separated from the shared rule.

## Return Format
Return IMPLEMENTER_RESULT (write to .agent-work/issue-102/crew-handoffs/g5-implement-result.md AND as
your final message): per-move slice, files changed, two before/after grep pairs, canonical + pointer
quotes per move, suite tail, assumptions, stop conditions, out-of-scope observations, workflow
feedback. Your FINAL MESSAGE must be the complete IMPLEMENTER_RESULT.
