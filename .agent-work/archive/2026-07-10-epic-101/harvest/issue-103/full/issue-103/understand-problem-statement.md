# Problem statement — issue #103 (Cluster B diets, MINUS commander)

Delegated mode: reconciled against frozen LAUNCH_ORDER-issue-103.md (Mission). No reachable human; Admiral is delegate. Interrogation answers sourced from the launch order + issue #103 body (pre-answers most understand questions).

## Scope (four items), reconciled against current post-#108 state (base c25c4a6)

1. **Admiral fold** — `skills/admiral/SKILL.md` "Operating doctrine, learned from field fleets:" list is **10 bullets now**, not 12 (#108 already relocated shared doctrine to `_shared/`). Reconcile-then-cut: for each bullet, keep genuine admiral operating deltas inline; cut what duplicates `fleet-doctrine.md`/`global-orchestrator.md`/`global-everyone.md` to a pointer (pre-ruling: duplicates of #108 moves are CUT, not folded again); rewrite the "learned from field fleets" heading and per-bullet history framing as timeless current truth. Physically move into `fleet-doctrine.md` only detached-survival operative content not already there (likely little — the reference is already comprehensive).

2. **Docent extraction** — extract the "Self-contained HTML — hard constraints" block (+ its self-containment verification detail) from `skills/docent/SKILL.md` into a new `skills/docent/references/self-contained-html.md`; body keeps the method and a one-hop pointer. New reference must NOT match `global-*.md` (test glob pins bundle composition).

3. **History-to-current-truth sweep** over `skills/**/*.md` EXCEPT `skills/commander/**` (sibling owns it). Identified targets:
   - `admiral/SKILL.md:46` "State-note-first is now engine-enforced" (also folded in item 1)
   - `admiral/SKILL.md:56` "g1's git-common-dir resolution now points ... mostly automatic"
   - `admiral/references/fleet-doctrine.md:38` "This is now mechanical, not advisory"
   - `admiral/references/fleet-doctrine.md:118-127` "Live grounding: this epic ... issue-54 had to improvise ... g1's ... now removes" (war story; keep operative rule, cut narrative)
   - `admiral/references/fleet-doctrine.md:165-172` compact-step "removed — ... before this change" migration diary (keep operative caveat, cut removal story)
   - `admiral/references/fleet-doctrine.md:10` "Distilled from field fleets (f1brainz epics ...)" — provenance in a reference; keep grounding, detemporalize only if needed (honest-null: reference is the sanctioned home for platform provenance)
   - `explorer/SKILL.md:63` "Design-it-twice is now a tier-wide standard, not an explorer-only move"
   - `charter/references/rigorous-default.md:3` "is now inherited runtime doctrine, not a Charter-only reference"
   - `workbench/templates/WORKFLOW_CLOSEOUT.template.md:26` "are now lessons carrying a target" (mild; template)
   Meaning-preserving; the rule stays, its origin story goes. Origin stories carrying operative content are rehomed, not silently deleted, and listed in the report.

4. **Interrogator register rewrite** — `skills/interrogator/SKILL.md` stays ONE skill (439 words; do not split, do not bloat). Rewrite in place so agent-loaded/delegated prose leads and the human-at-keyboard case becomes a brief mode note. Preserve all doctrine.

## Testing pathway (cluster B row)
Existing suite is structural only. #108 added content-pin + no-residual-duplicate tests in `tests/test_install_constellation.py`. My edits MUST NOT reintroduce retired inline doctrine signatures (residual test) and MUST NOT remove pointer lines' shared-file names. Doc-only gates use inspection-attestation evidence (quoted before/after + grep + command-derived word counts), not test-shaped proxies. Full suite must stay green.

## Honest-null
Any fold/sweep item that proves load-bearing where it is (cutting loses operative content) is skipped-and-reported per item — a complete deliverable.
