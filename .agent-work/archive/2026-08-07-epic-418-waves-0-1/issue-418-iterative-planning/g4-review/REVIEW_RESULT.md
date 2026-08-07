# G4 Whole-Change Review Result

`gate_id: g4`  
`verdict: APPROVE`  
`reviewer_identity: /root/g4_reviewer, fresh constellation-reviewer; distinct from Gates 1-4 implementers and prior reviewers`  
`reviewed_diff_digest: sha256:251c48b0ae6308d01bbd813f037b06a4f2ad40e468e9cd90dda2baadff720355`

## Assigned Gate

`g4 — Whole-change iterative planning and hash-pinned Epic #418 demonstration`

## Result

`APPROVE`

The complete 39-path product/doc/test change and offline Epic #418 demonstration satisfy the frozen contract at the exact recomputed digest. No blocker remains.

## Handoff compliance

Pass. Independent replay verified the canonical `to-initial-issues` rename and migration, strict initial-cut seam, lean four-exit `replan` seam, operative Explorer/Commander/Admiral lifecycle wiring, and the complete Epic #418 before/after demonstration.

The ten frozen acceptance items all passed. The historical A-E disposition is exact: A/C/D are the runnable current wave; B/E are nonbinding forecast. Independently derived counts are 4,844 to 767 words, 5 to 3 runnable issues, and 3 to 2 dependency edges. The 1-3 issue shape is demonstrated as an evidence-supported initial-wave hypothesis, not encoded as a universal cap.

## Scope drift

Pass. The product identity is the ordinal 39-path digest inventory. Both historical inputs match their frozen hashes and all 28 archived files have identical before/after path+SHA entries. Inherited dirty paths retain their classifications. No archive rewrite, commit, tracker write, push, PR, or network operation was authorized or observed.

The deny harness proves only its scoped offline replay: raise-on-write tracker, first-PATH failing `gh` shim, and network/subprocess spies recorded zero calls. Push/PR/live-issue absence is correctly reported as an authority/tool audit assertion rather than fixture proof.

## Evidence verdict

- Whole-change digest: exact `sha256:251c48b0ae6308d01bbd813f037b06a4f2ad40e468e9cd90dda2baadff720355`.
- Frozen inputs: `DESIGN_SPEC.md` and `ISSUE_SET.json` independently hash to the two expected values.
- Archive: 28/28 entries identical before and after.
- Demo replay: `Epic 418 demo ok ... (5 original items, 28 archive files)`.
- Acceptance replay: all ten named items passed.
- Registration rails: both `to-initial-issues` and `replan` are registered, mechanically clean, and install in dry-run.
- Focused suite: `169 passed, 449 subtests passed`.
- Recorded full suite: `1662 passed, 2 skipped, 636 subtests passed` with exit 0.
- Hygiene: `git diff --check` exited 0; changed JSON templates parse through the focused suite.
- TDD: the demo verifier's causal RED is the missing-demo refusal; the identical public command passes after artifact generation.

## Code/doc quality

Pass. Public serialized boundaries are strict and fail fast; forecast cannot masquerade as runnable issues; the replan verifier validates invariants without choosing planning judgment; and installed role checks mechanically enforce transition timing and launch authorization. Documentation, indexes, installer bundles, coverage ledger, and role contracts agree.

The Fowler rail visited all 12 smells. One nonblocking observation is recorded: `scripts/verify_epic_418_demo.py::_build_packets` is long but remains a bounded deterministic fixture builder. If the demonstration grows, extracting named packet builders would improve review locality. Strict JSON primitives and finite rename/lifecycle surgery are documented project-standard overrides.

## Map impact verdict

- **Evidence supports claimed change:** Yes. Executable verifiers, installed-role tests, the focused suite, and the offline demo reproduce the claimed initial-cut/replan lifecycle.
- **Constraints not violated:** Yes. Fixed intent and human authority remain guarded; forecast is provisional; repair holds current truth; posting authority is not granted by planning.
- **Notes match the diff:** Yes. Structural seams, public capabilities, constraints, and settled launch decisions match the 39-path change.
- **Decision candidates surfaced:** Yes. Fixed-boundary changes become inapplicable and carry typed human escalation; no reviewer-owned decision was silently taken.
- **Durable context routed:** Yes. No architecture map exists, so direct README/index/role/verifier reconciliation is appropriate. One inherited authoring-guidance mismatch is returned as triage.

## Reconciliation check

Pass. Direct reconciliation across README, `SKILL_INDEX`, installer bundles, coverage ledger, role doctrine/spines, and G1/G2 public verifiers found no current architectural divergence.

## Blockers

- None.

## Out-of-scope observations

- Triage candidate: `skills/write-a-skill/SKILL.md` still tells authors to add a name to installer-test `SKILL_NAMES`, while the test now derives skills through `discover_skills()`. Align the prose with the executable registration rail.
- Nonblocking maintainability observation: split the demo's long `_build_packets` function if it gains further scenarios.

## Workflow Feedback

- **Handoff gaps:** The handoff required independent replay but did not name the exact registration-rail commands; they were recovered from prior approved results and `scripts/verify_skill_registered.py`.
- **Context rediscovered:** The sanctioned old-name allowlist is categorical rather than enumerated. Remaining hits had to be classified individually as installer migration, tests, historical fixtures, or external provenance.
- **Instructions improvised around:** The first `uv run` attempt hit the known Windows cache error 183. Pure script verifiers were replayed with the bundled Python, then the exact `uv run` focused suite and both registration rails were retried successfully.
- **What would have made this easier:** Put the two registration commands and concrete legacy-reference allowlist directly in the whole-change reviewer handoff.

## Return status

`complete`
