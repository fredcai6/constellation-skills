# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit.

Newest entries on top.

---

## `2026-07-19` — `157-drill`

**Run shape:** commander (delegated) · full spine init→archive, execute.json 5 gates (2 reasoning doctrine edits + 2 fresh-auditor drills + 1 independent review) · subagents: opus (2 auditors + 1 reviewer), sonnet (drill arm sub-subagents).

**Instruction adherence:** fully followed.
- Both graduations kept in their launch-order-ruled homes (G1 explorer SKILL Spec-phase + DESIGN_SPEC template; G2 admiral SKILL Latitude); LATITUDE_CONTRACT.template.md (#118) untouched and its cross-reference routed to triage. Drill-required separation honored: two fresh auditors, distinct from the editor and from each other, plus an independent reviewer distinct from all.
- Reasoning gates used for the two doctrine edits (prose I held context for), with the invariant chain pre-authored as grep command-postconditions per the doc-only-gate doctrine — worked cleanly, the greps caught nothing because the wording was authored to satisfy them, which is the point.

**Friction / unclear:**
- Dispatch mechanics: as an in-process teammate I could NOT dispatch named subagents (flat roster) nor background subagents ("in-process teammates cannot spawn background agents"). Both auditors and the reviewer had to run as synchronous, unnamed subagents. This directly contradicts the memory-lodged preference to run SDD-loop dispatches in the background; the delegated-commander-in-a-team harness only allows foreground unnamed subagents. Worth noting in doctrine: a delegated commander running inside a team dispatches its crew synchronously, one at a time.
- Nested spawning asymmetry (useful, non-obvious): although I (a teammate) cannot spawn background/named agents, my auditor subagents COULD spawn their own throwaway sub-subagents for the two drill arms — so the drills got genuine fresh-context before/after arms rather than a cold-read simulation. The blocker is on the top-level teammate, not on nesting.
- Engine RAIL strings flood every mutating call's stdout, so `| tail -1` often shows a RAIL line rather than the verb's own result line; had to grep for `complete|REFUSED|in-progress` to read outcomes. Minor but slowed every step.

**Crew-reported friction:**
- Reviewer: dangling `config_ref` to a non-existent `docs/agents/engine-config.json` in the spine/execute templates (sanctioned graceful degradation for a vendored-scripts repo — confirmed by-design, not a defect); grounded-issue titles (#142/#145) were absent from the reviewer handoff (I gave grounding refs but not the issue titles — a handoff-completeness nicety).
- Both auditors independently hit and documented the SAME contamination trap: a scenario that pre-itemizes or alarm-flags the divergence/mechanics makes the weak-doctrine arm pass too, collapsing the variable. Both had to decontaminate to a positively-described / outcome-only scenario. This is a reusable drill-authoring method worth graduating into the lessons-auditor or drill doctrine (see improvement signal).

**What worked:**
- Two-arm reproduction drill with real fresh sub-subagents, doctrine text the sole variable, verbatim before-arm capture, honest caveats surfaced (drop-branch vs improvise-branch; curate_corpus.py legibility note) — produced genuinely load-bearing evidence, not ceremony.
- Pre-authored grep invariants on doc-only reasoning gates gave the engine a real postcondition to run instead of a proxy.

**Improvement signals:**
- Drill-authoring anti-contamination method (describe the scenario positively / by-outcome so the failure trigger stays latent; a pre-itemized or alarm-flagged scenario passes both arms). Both fresh auditors rediscovered it independently this run. → disposition: distilled to a constellation lesson, EXPORTED to CONSTELLATION_FEEDBACK.md (belongs in the lessons-auditor / repro-drill doctrine home, an upstream skill-corpus change — needs human/Admiral to place).
- Delegated-commander-in-a-team dispatches crew synchronously/unnamed (no background, no named teammates). → disposition: exported to CONSTELLATION_FEEDBACK.md as a platform-doctrine note for the crew-dispatch reference.
