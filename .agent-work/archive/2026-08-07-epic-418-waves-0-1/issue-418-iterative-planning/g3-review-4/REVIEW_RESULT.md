# G3 Review Result — Rework 3 Fresh Review Attempt 4

`gate_id: g3`  
`verdict: BLOCK`  
`reviewer_identity: /root/g3_reviewer_4, fresh constellation-reviewer; distinct from all G3 implementers and prior reviewers`  
`reviewed_diff_digest: sha256:3672b7a33efae2ced6b9e70331f63855f503b1334ead7e42f4ccb19c035cc917`

## Assigned Gate

`g3 — Iterative role contracts`

## Result

`BLOCK`

The installed runtime contract now implements the complete frozen launch table: applicable `advance` and `replan` authorize `NEXT_WAVE`; applicable `repair`, `stop`, and every `applicable:false` result refuse it; generic G2 still validates and renders all five transition variants. One required evidence defect remains: the shipped zero/multiple audit-cardinality assertions are no longer causal after `repair` became non-authorizing.

## Ranked blocker

1. **[P1] Audit-cardinality regression tests pass through the wrong refusal branch.** In `tests/test_iterative_planning_doctrine.py` lines 358–372, both the zero-audit and duplicate-audit cases use the template `repair` result. `admiral-prelaunch` now correctly rejects every repair before `_verify_transition_audit` runs, so both assertions remain green if audit cardinality enforcement is deleted or broken. This violates `docs/agents/CREW_CONTEXT.md`: assert consumer behavior, demonstrate that the guard can fail, and do not present an earlier branch's failure as evidence for the named invariant. A fresh installed probe changed only those reviewer inputs to an otherwise-authorized `advance`; zero and duplicate matching audit entries both refused, proving production behavior is correct but the shipped guard is not causal.

## Handoff compliance

Runtime behavior complies. A fresh five-skill install exercised the exact G1 Explorer artifact, exact G2 Commander packet, all generic G2 transition variants, the full prelaunch table, repair identity/forecast preservation, installed paths, Windows-safe commands, dual rendering, human authority, recovery/audit/tracker boundaries, and exclusions. Required verification evidence does not fully comply because exact-one audit behavior lacks a regression test that reaches its consumer branch.

## Scope drift

Pass. The exact nine-path ordinal inventory is unique and limited to the three role contracts, one offline helper, installer wiring, and the focused runtime test. No G1/G2 schema, checklist engine, tracker/network implementation, archive/history/provenance, compatibility alias, G4 artifact, or unrelated production file changed in Gate 3.

## Evidence verdict

- Digest recomputation: exact `sha256:3672b7a33efae2ced6b9e70331f63855f503b1334ead7e42f4ccb19c035cc917`.
- `uv run python -m pytest -q tests/test_explorer_templates.py tests/test_iterative_planning_doctrine.py`: `36 passed, 6 subtests passed in 1.95s`.
- `uv run python -m pytest -q tests/test_install_constellation.py`: `108 passed, 379 subtests passed in 14.99s`.
- `uv run python -m pytest -q tests/test_initial_issues.py tests/test_replan.py tests/test_init_work_area.py`: `62 passed, 59 subtests passed in 0.35s`.
- Fresh independent install matrix: 28 checks passed, including 4/4 installed sibling paths, Explorer/Commander missing-malformed-exact cases, generic G2 rendering for all five variants, repair drift refusal, the complete launch table, and dual retained Markdown.
- Independent authorized-`advance` audit variants: zero and duplicate matching exits both refused, so runtime exact-one enforcement passes.
- All changed spine JSON parsed; `git diff --check` passed.
- Helper imports only standard-library modules, validates safe path identities and exact object shapes, delegates to installed public G1/G2 verifiers, and contains no network, tracker, `gh`, or subprocess seam.
- Fowler pass: all 12 smells visited and verifier passed with no flagged smell.

The green suites therefore reproduce, but the named audit-cardinality test evidence is insufficient: it cannot distinguish a working audit check from no audit check.

## Per-check findings

- `r0-context`: PASS — complete reviewer doctrine, local context, exact handoff, frozen gate, prior blocks, result, and contracts loaded.
- `r1-handoff`: PASS — installed runtime behavior matches the frozen contract.
- `r2-scope`: PASS — exact scope and exclusions respected.
- `r3-evidence`: FAIL — zero/multiple audit tests are non-causal.
- `r4-quality`: FAIL — the repo's verification-discipline rule is unmet for a launch-safety invariant.
- `r5-reconciliation`: PASS — no architecture map; direct seams and Map Impact claims reconcile.
- `r6-fowler`: PASS — all baseline smells visited; no code-smell finding.
- `r4a-paths`: PASS — 4/4 installed paths and all three command gates resolve.
- `r4b-explorer`: PASS — exact G1 artifact gate, with human confirmation preserved.
- `r4c-commander`: PASS — exact G2 input gate; discrepancy evidence is not auto-filed.
- `r4d-launch-table`: PASS — generic validity/rendering and prelaunch authorization table are correct.
- `r4e-audit`: FAIL — runtime works, shipped regression test does not reach the audit branch.
- `r4f-authority`: PASS — human, review, recovery, audit, and tracker-port boundaries remain.
- `r4g-json`: PASS — JSON, helper purity/wiring/path safety, offline behavior, and diff check pass.
- `r4h-exclusions`: PASS — frozen exclusions and pre-existing frontmatter drift are non-regressed.

## Code/doc quality

Production code is compact, readable, standard-library-only, fail-fast, and correctly separates generic transition validity from next-launch authorization. Role doctrine and installed directives are coherent. The blocker is confined to test construction: reuse of the repair fixture became invalid evidence when the authorization allowlist changed.

## Map impact verdict

- **Evidence supports claimed change:** Yes for installed structure, runtime capability, authority boundaries, and the final repair refusal; not fully for the claimed audit regression coverage.
- **Constraints not violated:** Runtime scope, offline/no-network, exact G1/G2 seams, human authority, review, recovery, and audit constraints pass.
- **Notes match the diff:** Structural, capability, authority, and constraint notes match the production diff.
- **Decision candidates surfaced:** No new design authority is required; this is a test-input correction under the frozen contract.
- **Durable context routed:** Rework belongs in Gate 3. No Cartographer or Triage follow-on is needed.

## Reconciliation check

No architecture map exists. Direct installed-interface review confirms the role seams and authority table. The remaining mismatch is between the test's stated audit claim and the branch its input actually reaches.

## Required rework

- Change the zero-audit and duplicate-audit cases to an otherwise-valid applicable `advance` (or `replan`) result and use matching audit decision lines, so only audit cardinality causes refusal.
- Demonstrate the guard red when `_verify_transition_audit` is bypassed or otherwise show the changed tests fail before the correction; rerun the focused suite and refresh the nine-path digest.

## Out-of-scope observations

- None.

## Workflow Feedback

- **Handoff gaps:** The handoff explicitly required exact-one audit verification but did not state that its negative cases must use an otherwise launch-authorized transition after repair became a hold.
- **Context rediscovered:** The focused test retained the prior repair fixture for audit cases even though rework 3 moved repair refusal ahead of audit verification.
- **Instructions improvised around:** The shared `uv` Python/cache home was sandbox-denied, so the required read-only suites were rerun with approved external cache access. For the independent matrix, I executed a reviewer-only in-memory variant of the prior probe with corrected authorization and audit inputs; no production or prior-review artifact was edited.
- **What would have made this easier:** Freeze the audit cases as `advance + zero matching lines -> refuse`, `advance + two matching lines -> refuse`, and `advance + one matching line -> authorize`, alongside the five-row authorization table.

## Return status

`complete`
