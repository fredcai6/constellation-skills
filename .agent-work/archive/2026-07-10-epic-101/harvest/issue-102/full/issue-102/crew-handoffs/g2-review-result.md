# REVIEW_RESULT — g2-review (issue #102, Move 2: engine-invocation string)

## Assigned Gate
g2-review — Move 2 (generic engine-invocation string; outcome: subsumed-by-Move-1 + narrow pointer edit)

## Result
APPROVE

## Handoff compliance
Satisfied. The handoff asked to single-source the generic engine-invocation string / point at
`checklist-engine.md` for the mechanism, keep role-specific spine instructions local, and report
honestly if subsumed by Move 1. The implementer did exactly that:
- The subsumption finding is CORRECT and independently reproduced (see Evidence).
- `global-everyone.md` now carries a one-clause pointer to the canonical engine mechanism.
- The honest-null clause was respected — reporting the narrow scope is treated as a complete
  deliverable, not a failure. Per the stop conditions I did NOT block on narrowness.

## Scope drift
None. `git status --porcelain` shows a single modified file: `skills/_shared/global-everyone.md`
(+4 lines, one hunk). No excluded surface touched — no banners (g3), no prototyper (g1), no hygiene
files (#105), no Move-1 carriers. No new `global-*.md` filename created.

## Evidence verdict
All three required verifications reproduced independently against the working tree:

1. **Residual grep** (`grep -rn "through the engine\|one step at a time\|drive the gated\|drive a
   controller\|gate by gate" skills/*/SKILL.md`) → 11 hits, every one classified as role-specific
   spine (admiral:14 ADMIRAL_SPINE, cartographer:8, commander:12/25/30/36, explorer:33 EXPLORER_SPINE,
   scout:8), a pointer to inherited doctrine (admiral:10, commander:12), or the canonical mechanism
   source (workbench:3, workbench:39). **No generic, role-agnostic engine-invocation duplicate
   remains** outside role-specific/canonical/pointer contexts. Matches the implementer's classification
   table exactly.
2. **Pointer count** (`grep -c "checklist-engine" skills/_shared/global-everyone.md`) → **1**. Points
   exactly once; landed inside the existing `## Engine-drive compliance` section (lines 18–20),
   adjacent to the Move-1 compliance paragraph.
3. **Suite** (`py -m pytest tests/ -q`) → **442 passed, 2 skipped, 26 subtests passed**. Green; matches
   the implementer's reported tail.

## Code/doc quality
Minimal and correct. The added clause references `workbench references/checklist-engine.md` as the
single mechanism source and explicitly states each role skill only names its own spine/survey template
and never re-explains the engine — it does NOT duplicate the mechanism (verbs, evidence shape, rework
guard) content. Role-specific spine instructions are preserved verbatim: commander:30 (COMMANDER_SPINE
10-step), explorer:33 (EXPLORER_SPINE + init instantiation), workbench:39 (canonical driver) all
present and unchanged in substance. No force-merge / semantic loss.

## Map impact verdict
Trivial doc edit reinforcing an existing single-source decision (generic engine doctrine lives in
global-everyone; the mechanism lives in checklist-engine.md). No structural, capability, or constraint
change; no new seam or interface. Implementer's notes match the diff. No decision authority was
required. Nothing to route to Cartographer beyond the already-anticipated g7 content-pin. No block
warranted.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconcile. The edit consolidates toward
the recorded baseline rather than departing from it.

## Blockers
- none — confirmed after independent reproduction: no generic duplicate left behind, no role-specific
  content deleted, no new global-*.md, suite green.

## Out-of-scope observations
- The implementer flagged (and I concur, unverified here) that per-skill bundled
  `references/global-everyone.md` copies exist alongside the canonical `skills/_shared/global-everyone.md`;
  the _shared → per-skill sync/bundling mechanism was not inspected in this gate and is worth the
  content-pin check the g7 pin already anticipates. Triage candidate — not a blocker for this move.

## Workflow Feedback
- **Handoff gaps:** none — the handoff was unusually complete: it pre-named both honest outcomes as
  valid deliverables, supplied the exact classification taxonomy (generic / role-specific / canonical),
  and gave the reproduction commands. No field was missing or ambiguous.
- **Context rediscovered:** none — the implementer result carried the classified grep, the exact added
  quote, and the suite tail; all reproduced cleanly with no digging.
- **Instructions improvised around:** (1) `consolidate` takes `--verdict/--summary`, not the
  `--result/--note` shape used by `record` — the verb-argument asymmetry cost one refused call. (2) I
  released the lease before consolidating and had to re-claim (idempotent, free, but a sequencing
  gotcha). Neither affected the verdict. (3) The survey template's `config_ref` points at
  `docs/agents/engine-config.json`, which does not exist in this repo; the engine did not require it.
- **What would have made this easier:** a one-line note in the reviewer skill/template that
  `consolidate` uses `--verdict/--summary` (distinct from `record`'s `--result/--finding`) and should
  run before `release`.

## Return status
complete
