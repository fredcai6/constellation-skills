# G3 Review Result — Rework 2 Fresh Review Attempt 3

gate_id: g3  
verdict: BLOCK  
reviewer_identity: /root/g3_reviewer_3 acting as fresh constellation-reviewer; distinct from all G3 implementers and prior reviewers  
reviewed_diff_digest: sha256:ee7d13260409778468d88bd15190e15d31cd64d61a517074b35108baa7e0c895

## Assigned Gate

`g3 — Iterative role contracts`

## Result

`BLOCK`

The final two rework-2 cases now behave correctly: generic G2 still represents `applicable:false` and `stop`, while `admiral-prelaunch` refuses both. One adjacent launch-authority defect remains: a valid `repair` result returns success from the command that authorizes `NEXT_WAVE`, even though the shipped Admiral doctrine and original handoff require repair to hold the current wave and forecast until blocking evidence is settled.

## Ranked blocker

1. **[P1] `repair` improperly authorizes the next wave.** In a fresh installed corpus, generic G2 correctly validates and renders a strict repair record. With `NEXT_WAVE.json` naming `launch_id: wave-2`, the same record returns exit 0 from `verify_iterative_role_artifacts.py admiral-prelaunch`. The Admiral doctrine states that repair holds the current wave/forecast and that no next launch occurs until blocking evidence is settled. No settled-evidence field or check exists, so this success mechanically clears the launch immediately. Reproduce with:

   ```text
   uv run python .agent-work/issue-418-iterative-planning/g3-review-3/installed_matrix_probe.py
   PASS generic G2 validates and renders repair
   PASS admiral applicable repair authorizes
   ```

   The second line is a successful observation of the current behavior, not the desired acceptance criterion. `admiral-prelaunch` should authorize only applicable `advance` or `replan`; repair must remain valid/renderable through the generic G2 seam but refuse next-launch authorization, like `stop`.

## Handoff compliance

Partial. The installed Explorer and Commander artifact gates are operative. Admiral enforces installed G2 validation, exact-one audit cardinality, repair identity/forecast preservation, dual rendering, `applicable:false` refusal, and `stop` refusal. It does not yet enforce the repair hold at the next-launch boundary.

## Scope drift

Pass. The exact nine-path digest inventory is unique and scoped to the three role contracts, the shared offline helper, installer wiring, and focused tests. No G1/G2 schema, checklist engine, tracker/network path, history/archive, compatibility alias, G4 demonstration artifact, or unrelated production file was changed by this rework. Reviewer-owned files are confined to `g3-review-3/`.

## Evidence verdict

- Digest recomputation: exit 0, exact `sha256:ee7d13260409778468d88bd15190e15d31cd64d61a517074b35108baa7e0c895`.
- Focused role suite: exit 0, `36 passed, 6 subtests passed in 1.77s`.
- Installer suite: exit 0, `108 passed, 379 subtests passed in 13.93s`.
- G1/G2/init compatibility: exit 0, `62 passed, 59 subtests passed in 0.36s`.
- Fresh real-install matrix: exit 0 with 29 assertions, including actual Explorer/Commander artifacts, all generic G2 variants, exact-one audit, repair drift refusal, dual rendering, `applicable:false` refusal, and `stop` refusal.
- All three changed spine JSON files parse.
- Scoped and full `git diff --check`: exit 0.
- Installed Windows command rewriting resolves and executes forward-slash interpreter paths.
- Shared helper imports only standard-library modules and contains no network, tracker, `gh`, or subprocess seam.
- Known mint-frontmatter drift is non-regressed: Explorer, Commander, and Admiral frontmatter each match `HEAD` exactly.

## Per-check findings

- `r0-context`: PASS — complete frozen/prior-review context loaded; digest matched first.
- `r1-handoff`: PASS on the requested matrix reproduction; later semantic reconciliation identified the repair-authorization defect.
- `r2-scope`: PASS — scope, exclusions, and preserved authority/recovery gates hold.
- `r3-evidence`: PASS — all required commands and independent installed checks reproduced.
- `r4-quality`: FAIL — repair does not hold the next-launch boundary.
- `r5-reconciliation`: FAIL — Map Impact overstates next-launch safety by reporting repair preservation without disclosing immediate launch authorization.
- `r6-fowler`: PASS — all 12 smells visited; verified overrides cover required role prose/directive mirroring, strict JSON primitives, and finite three-role wiring.
- `r4a-repair-authority`: FAIL — generic repair is valid, but prelaunch must refuse it.

## Code/doc quality

The helper is compact, fail-fast, standard-library-only, and correctly delegates public G1/G2 schema semantics to installed canonical verifiers. Path safety, exact JSON shapes, audit cardinality, and rendering are clear. The defect is one missing authorization predicate after generic G2 validation: `repair` is a valid transition record but not permission to launch the next wave.

## Map impact verdict

- **Evidence supports claimed change:** Yes for installed role artifacts, ordinary advance/replan, final `applicable:false` and `stop` corrections, and rendering; no for a complete repair hold.
- **Constraints not violated:** Offline/no-network, exact G1/G2 seams, fixed authority, independent review, recovery, and audit constraints pass. Repair launch safety fails.
- **Notes match the diff:** Structural notes match. Capability/authority notes overstate the prelaunch subset because they omit repair.
- **Decision candidates surfaced:** No new human design decision is required; the handoff and shipped doctrine already define repair as a hold.
- **Durable context routed:** Rework belongs in G3. No Cartographer or Triage follow-on is needed.

## Reconciliation check

No architecture map exists. Direct installed-interface review confirms the role seams and shared helper are real, but the Admiral authorization seam still disagrees with its own doctrine and the original epic requirement.

## Required rework

- After generic G2 validation, make `admiral-prelaunch` refuse `decision: repair` as well as `stop`; next-launch authorization should require `applicable is true` and decision in `{advance, replan}`.
- Keep generic G2 validation/rendering of repair unchanged.
- Change the installed-runtime test from “valid repair prelaunch accepts” to “generic repair validates/renders, prelaunch refuses,” retain repair drift checks, recompute the nine-path digest, and dispatch a fresh reviewer.

## Out-of-scope observations

- The direct minting rail still rejects long-standing role frontmatter. Fresh `HEAD` comparison confirms all three role frontmatter blocks are unchanged, so this is pre-existing and not a G3 regression.

## Workflow Feedback

- **Handoff gaps:** The reviewer handoff said “valid repair semantics” and “repair hold” but did not state the authorization table explicitly. The frozen doctrine clarifies it, but an explicit `repair -> generic valid; prelaunch refuse` row would have prevented the ambiguity.
- **Context rediscovered:** The original handoff says a blocking discrepancy holds the forecast and produces a repair pass; the shipped Admiral prose additionally says no next launch occurs until blocking evidence is settled. These were necessary to distinguish repair validation from launch authorization.
- **Instructions improvised around:** I initially recorded the broad matrix check before reconciling the observed repair success against doctrine, then appended a dedicated survey check through the engine rather than editing prior survey state.
- **What would have made this easier:** Freeze a five-row table for `advance`, `replan`, `repair`, `stop`, and `applicable:false`, with separate columns for generic G2 validity/rendering and `NEXT_WAVE` authorization.

## Return status

`complete`
