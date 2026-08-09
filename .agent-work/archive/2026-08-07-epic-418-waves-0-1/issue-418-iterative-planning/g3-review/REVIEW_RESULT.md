# G3 Review Result

gate_id: g3  
verdict: BLOCK  
reviewer_identity: /root/g1_reviewer acting as fresh G3 constellation-reviewer; distinct from G3 implementer  
reviewed_diff_digest: sha256:c3a48b776e9581b51f74125c72d05e536dac8cecf1e97da7d0afdc32602cbbca

## Assigned Gate

`g3 — Iterative role contracts`

## Result

`BLOCK`

The digest, supplied suites, scope, exclusions, and preserved authority/recovery gates pass. The new iterative chain is not operative in shipped installs and can be satisfied by metadata plus unrelated canonical fixtures.

## Ranked Blockers

1. **[P1] Every structured cross-skill template path breaks after installation.** Source roles use `../to-initial-issues/...` and `../replan/...`, but installed siblings are `constellation-to-initial-issues` and `constellation-replan`. The installer rewrites only `<skill-dir>` tokens and does not rewrite these paths. Reviewer installed-layout replay inspected four paths and resolved zero:

   ```text
   explorer .../to-initial-issues/... exists=False
   commander .../replan/... exists=False
   admiral-input .../replan/... exists=False
   admiral-result .../replan/... exists=False
   unresolved=4 inspected=4
   ```

   Reproduce with:

   ```text
   powershell -File .agent-work/issue-418-iterative-planning/g3-review/installed_path_probe.ps1
   ```

2. **[P1] Explorer and Commander do not produce verified operative artifacts.** Explorer `confirm.c3` is `check:null`; no command reads the run's `.agent-work/<work-id>/SHAPED_BRIEF.json` through `verify_shaped_brief`. Commander defines no REPLAN_INPUT output path, and `execute.c2` is also `check:null`; no run packet reaches `verify_replan_input`. Both roles can attest completion with malformed or missing artifacts.
3. **[P1] Admiral cannot enforce one verified exit before each next launch.** `execute.c3` is one `check:null` attestation after the entire execute step. No pre-launch command parses packets or the audit log, no actual REPLAN_INPUT/RESULT paths are named, and no rendered artifact paths are defined. The `directives` booleans do not alter engine behavior, so they cannot enforce timing, cardinality, repair hold, or rendering at each boundary/material exception.
4. **[P1] The focused tests are marker/fixture-satisfiable.** They assert literal directive dictionaries and separately run public helpers against checked-in G1/G2 template fixtures. They never resolve installed paths, materialize an Explorer or Commander run artifact, or simulate a next launch being refused until an Admiral transition verifies. Consequently all tests remain green while blockers 1–3 reproduce.

## Handoff Compliance

Partial. Role prose and structured metadata state the intended G1/G2 chain accurately, including critic weight, classifications, provisional forecast, repair hold, four exits, rendering fields, fixed-boundary escalation, and authorized posting. The handoff required an operative executable chain; the current change provides declarations without runnable boundary enforcement.

## Scope Drift

Pass. The exact seven-path inventory contains only the three role doctrine/template pairs and the focused test. No G1/G2 schema, engine, tracker implementation, alias, archive/history, external provenance, or G4 artifact changed.

## Evidence Verdict

- Digest helper: exit 0, exact `sha256:c3a48b…`.
- Doctrine suite: exit 0, `31 passed in 1.02s`.
- Confirmatory suite: exit 0, `76 passed, 59 subtests passed in 0.39s`.
- Independent JSON parse: all three changed spines parsed.
- Scoped `git diff --check`: exit 0.
- Scoped executable-network audit: no changed planning-time network/tracker call; existing Commander archive PR checks remain outside the new planning seam.
- Installed-path probe: exit 1, `unresolved=4 inspected=4`.
- Structural inspection: every new artifact/timing postcondition is `check:null`; Commander has no output path and Admiral has no per-boundary mechanical check.

## Per-Check Findings

- `r0-context`: PASS — full context loaded and digest matched before behavior review.
- `r1-handoff`: FAIL — shipped paths and operative artifact/timing chain fail.
- `r2-scope`: PASS — exact scope and exclusions respected.
- `r3-evidence`: FAIL — supplied tests are metadata/fixture-satisfiable.
- `r4-quality`: FAIL — executable-interface/two-bin rule is unmet.
- `r5-reconciliation`: FAIL — Map Impact overstates live contract seams.
- `r6-fowler`: FAIL — speculative generality flagged: structured directives have no runtime consumer. Required Markdown/directive mirroring and finite three-role surgery were standards-overridden.
- `r4a-paths`: FAIL — 0/4 installed paths resolve.
- `r4b-explorer`: FAIL — actual shaped-brief output is not mechanically verified.
- `r4c-commander`: FAIL — no packet path or actual G2 input verification.
- `r4d-admiral`: FAIL — no per-boundary verifier/timing or retained artifact paths.
- `r4e-preserve`: PASS — human latitude, independent review, engine, recovery, audit, state-note and authorized tracker-port gates remain present and operative.
- `r4f-exclusions`: PASS — no forbidden mutation/redesign/history changes.

## Code/Doc Quality

The prose is clear, concise, and internally consistent. The JSON remains parseable and changes are minimal. The design problem is that `directives` metadata is presented as executable structure without a consumer, while actual output/timing checks are manual null attestations.

## Map Impact Verdict

- **Evidence supports claimed change:** The declared doctrine, not the claimed executable capability.
- **Constraints not violated:** Scope, authority, recovery, review, audit, and network constraints pass; executable seam constraints fail.
- **Notes match the diff:** Structural notes match; capability notes overstate operational behavior.
- **Decision candidates surfaced:** No new human design choice is required; these are implementation gaps against the frozen contract.
- **Durable context routed:** Rework belongs in G3, not Cartographer/Triage.

## Reconciliation Check

No architecture map exists. Direct interface review shows the role doctrine changed at the intended anchors, but the installed and runtime interfaces do not yet connect. G3 must reconcile those seams before integration.

## Required Rework

- Use one install-safe cross-skill resolution method. Add installer-resolved cross-skill tokens or bundle the required public contracts/verifiers with each consuming role; test the installed corpus, not source-relative folders.
- Give Explorer and Commander explicit run artifact paths and command postconditions that verify those actual files through the G1/G2 public helpers.
- Add an operative Admiral boundary mechanism that refuses the next launch until one transition packet verifies, the exit is audit-recorded, repair preservation holds, and both rendered artifacts exist. Use existing engine/check mechanisms without redesigning the engine.
- Replace directive-literal tests with installed-layout and run-artifact transition tests that demonstrably fail when a path, packet, or pre-launch check is absent.
- Refresh the seven-path digest and dispatch another fresh review.

## Out-of-Scope Observations

- None.

## Workflow Feedback

- **Handoff gaps:** “relative sibling paths are intentionally interpreted from the role skill root” omitted that source folder names and installed folder names differ by the `constellation-` prefix.
- **Context rediscovered:** Installer rewriting only replaces the current skill's `<skill-dir>` tokens; it has no cross-skill relative-path rewrite.
- **Instructions improvised around:** Direct installer execution was temporarily unavailable because concurrent `uv` cache initialization failed. I inspected installer rewriting and reproduced the exact installed naming layout under the reviewer work area without network or production changes.
- **What would have made this easier:** Require an installed-corpus path-resolution test and name concrete run artifact locations/mechanical postconditions in the frozen handoff.

## Return Status

`complete`
