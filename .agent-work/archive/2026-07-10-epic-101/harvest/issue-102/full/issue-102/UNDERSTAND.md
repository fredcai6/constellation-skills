# Understand — issue #102 (Cluster A: single-sourcing dedup + regression net)

Delegated mode under Admiral (epic-101). Source of truth: LAUNCH_ORDER-issue-102.md +
issue #102 body. This file records the baseline reconcile (launch-order assumed baseline
vs actual code) required before planning.

## Problem statement
Execute 10 single-sourcing dedup moves + a mechanical regression net. Each duplicated
doctrine moves to exactly one home; carriers keep a one-line pointer naming the shared
file. Every move is reconcile-then-cut (inline copies drifted). Append into EXISTING
bucket files only — never a new `global-*.md` filename (test glob pins bundle composition,
test_install_constellation.py:196-208). Deliverable: green reviewed PR with per-move
before/after carrier-count grep evidence and before/after per-skill word counts.

## Bundling mechanism (confirmed against install_constellation.py:94-113)
- `global-everyone.md` bundles into EVERY installed skill (all four buckets include it).
  → content-pin for an everyone-move can assert on ANY installed skill.
- `global-orchestrator.md` bundles only into orchestrator/all-tier skills (admiral, charter,
  commander, workbench, cartographer, docent, scout, triage, explorer). NOT crew.
  → content-pin for an orchestrator-move must assert on an orchestrator skill (e.g. commander).
- `design-it-twice-brief.md` rides the orchestrator bundle (already there).

## Carrier reconcile (grep-confirmed) — the 10 moves
1. Mandatory-compliance boilerplate → global-everyone. Signature "mandatory, no exceptions"
   in commander; broader "no exceptions" pattern in ~10 SKILL.md. Exact verbatim boilerplate
   to be pinned by implementer at reconcile.
2. Engine-invocation string → global-everyone. "through the engine" in 11 files (drifted).
3. FOLLOW THIS SKILL STRICTLY banners → DELETE. Exactly 6 occurrences, one each in
   charter, commander, explorer, implementer, interrogator, reviewer.
   DELTA vs launch order: order said "6 files (charter twice)" implying 7; grep finds
   exactly 6 (charter carries it ONCE, line 31). Disposition: delete all 6 found; the
   "charter twice" parenthetical is not borne out by code — logged, not a blocker.
4. Scoped-nulls → global-everyone. Carriers: explorer/SKILL.md + prototyper/SKILL.md
   (§Scoped nulls) with domain applications also in prototyper/references/measurement.md
   and ui.md. RECONCILE NUANCE: the GENERAL principle ("a negative is scoped to this
   test/condition, never 'X is impossible'; state what was NOT tested") is the shared rule
   → moves to global-everyone. The spike-domain APPLICATIONS in measurement.md/ui.md
   (board mechanics, variant guidance) stay local (they are prototyper-specific, not
   cross-tier). Explorer + prototyper SKILL.md bodies cut to pointer.
5. World-verification of claimed side-effects → global-everyone. Carriers: commander +
   reviewer SKILL.md ("against the world" / "claimed side-effect").
6. Unchanged-tree shortcut → global-orchestrator. Carriers: commander + admiral.
7. Crew-idle adjudication → global-orchestrator. Carriers: commander + admiral +
   admiral/references/fleet-doctrine.md. fleet-doctrine keeps epic-specific delta only.
8. Delegate-not-replacement → global-everyone. Carriers: commander + admiral
   ("not a replacement"/"asking up"). Principle applies at every tier.
9. Dedup-sibling-ids → single home lessons-auditor/SKILL.md; admiral keeps pointer.
   Carriers: lessons-auditor/SKILL.md + admiral/SKILL.md:56 (fleet harvest substep 4).
10. Design-it-twice restatements → cut to one pointer line each in commander + explorer;
    canonical already in global-orchestrator.md §Design-it-twice + design-it-twice-brief.md.

## Regression net (move 11, added by cluster A)
- Content-pin test per relocated doctrine (moves 1,2,4,5,6,7,8 into a bucket; move 9 into
  lessons-auditor): signature phrase present in the INSTALLED destination. Model on
  test_deep_module_vocabulary_ships_into_installed_skill (test_install_constellation.py:679).
  everyone-moves assert on any skill's bundled global-everyone.md; orchestrator-moves assert
  on commander's bundled global-orchestrator.md; move 9 asserts on lessons-auditor SKILL.md.
- No-residual-duplicate test: retired inline signature must NOT reappear in SKILL.md BODIES
  (and non-bucket references). CRITICAL: the signature legitimately lives in the bundled
  _shared copy inside every skill's references/ after consolidation — the residual test
  must scope to SKILL.md bodies / role references, not the bundled bucket copies, else it
  false-fails. Banner residual: "FOLLOW THIS SKILL STRICTLY" appears 0 times post-move.
- Enforced per-gate grep evidence (before/after carrier counts) + before/after word counts.

## Skips / honest nulls anticipated
None yet. Move 4 (scoped-nulls) carries a semantic-vs-drift split resolved by keeping the
prototyper spike-applications local — a partial move, not a skip. Any move whose wording
proves semantic (not drift) on deeper reconcile is skipped with the inline kept + logged.

## Crew dispatch model (harness)
No headless CLI in this harness → run_crew.py --dispatch external (records durable entry +
duplicate guard, spawns nothing); dispatch implementer/reviewer as background Agent-tool
subagents; verify each with run_crew.py --verify-result <session>. recover_crews.py before
execute and before each dispatch.
