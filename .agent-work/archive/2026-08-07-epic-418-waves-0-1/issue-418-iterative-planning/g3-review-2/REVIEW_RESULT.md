# G3 Review Result — Rework 1 Fresh Review

gate_id: g3  
verdict: BLOCK  
reviewer_identity: /root/g1_reviewer_2 acting as fresh G3 constellation-reviewer; distinct from G3 implementer and original G3 reviewer  
reviewed_diff_digest: sha256:136a4de0f775630e65726cc03e1967559e79650904925022efbbe98419cca758

## Assigned Gate

`g3 — Iterative role contracts`

## Result

`BLOCK`

The installed path, real run-artifact, audit-cardinality, repair-preservation, rendering, and Windows command-rewrite corrections are operative. Two prelaunch authority/terminal semantics remain unsafe.

## Ranked blockers

1. **[P1] An inapplicable fixed-boundary proposal mechanically clears prelaunch.** A valid G2 result with `applicable:false`, a material change to `intent_and_why`, and an escalation naming `authority_required:"human"` returns exit 0 from the installed `admiral-prelaunch` helper. G2 intentionally validates this as an inapplicable proposal; G3 must not translate that validation into launch authority. This violates the frozen fixed-escalation/human-authority boundary and the role doctrine saying such proposals remain inapplicable until the human decides.
2. **[P1] A terminal `stop` result mechanically clears prelaunch.** A valid G2 `decision:"stop"` with `current_wave:null` also returns exit 0 from `admiral-prelaunch`, even though this mode is the command that authorizes a named next launch. The doctrine says a nonzero result refuses launch, but the terminal exit currently succeeds and therefore cannot mechanically prevent the launch it terminates.

Fresh installed-corpus reproduction:

```text
OBSERVED inapplicable fixed-boundary proposal prelaunch returncode=0
OBSERVED stop decision prelaunch returncode=0
```

Probe: `.agent-work/issue-418-iterative-planning/g3-review-2/installed_runtime_probe.py`.

## Handoff compliance

Partial. The rework successfully makes Explorer, Commander, and the ordinary Admiral transition path executable in a real installed corpus:

- All four canonical installed sibling paths resolve.
- Explorer refuses missing/malformed `SHAPED_BRIEF.json` and accepts the exact G1 artifact.
- Commander refuses missing/malformed `REPLAN_INPUT.json` and accepts the exact G2 packet without filing discrepancies.
- Admiral refuses missing/malformed transition artifacts, zero/multiple matching audit exits, and repair drift; one valid transition writes both retained Markdown artifacts.
- All three checks are real command postconditions, not directive-only metadata.

The chain is not complete because the Admiral command still confuses “G2-valid packet” with “authorized next launch” for inapplicable and terminal results.

## Scope drift

Pass. The exact nine-path inventory contains only the three live role doctrine/spines, one pure verifier, installer wiring/JSON-safe interpreter normalization, and the focused runtime test. No G1/G2 schema, checklist engine, tracker/network implementation, direct `gh`, compatibility alias, archive/history/provenance, or G4 artifact changed.

## Evidence verdict

- Ordinal digest helper reproduced exactly: `sha256:136a4de0f775630e65726cc03e1967559e79650904925022efbbe98419cca758`.
- Focused suite: `36 passed, 4 subtests passed`.
- Installer suite: `108 passed, 379 subtests passed`.
- G1/G2/init suite: `62 passed, 59 subtests passed`.
- Scoped `git diff --check`: pass.
- Fresh real-installer probe: all four paths, all specified missing/malformed/audit/repair refusals, successful rendering, command postconditions, and JSON-safe Windows prefixes passed.
- Additional authority/terminal cases: both incorrectly returned exit 0.

The supplied green tests omit these two launch-safety cases, so their evidence is insufficient for the complete frozen authority claim.

## Per-check findings

- `r0-context`: PASS — complete doctrine, handoffs, prior BLOCK, result, frozen gate, G1/G2 contracts, diff, helper, spines, and tests loaded after digest match.
- `r1-handoff`: FAIL — inapplicable and stop results clear prelaunch.
- `r2-scope`: PASS — exact scope and exclusions respected.
- `r3-evidence`: FAIL — all claimed positive evidence reproduces, but the test matrix omits the two unsafe prelaunch cases.
- `r4-quality`: FAIL — launch authority does not fail fast at fixed-authority and terminal boundaries.
- `r5-reconciliation`: FAIL — Map Impact's authority claim is overstated although its structural/capability claims are accurate.
- `r6-fowler`: PASS — all 12 smells visited; no Fowler-specific defect. Logged overrides cover required doctrine/directive mirroring, exact JSON primitives, and finite three-role wiring. The original speculative-generality defect is resolved by the real installed consumer.
- `r4a-paths`: PASS — 4/4 installed sibling paths resolve.
- `r4b-explorer`: PASS — actual G1 run artifact is mechanically gated with human confirmation preserved.
- `r4c-commander`: PASS — actual G2 input is mechanically gated; discrepancies remain evidence.
- `r4d-admiral`: PASS — specified packet/audit/repair refusal matrix and dual rendering pass through the real installed helper.
- `r4e-authority`: FAIL — `applicable:false` and `stop` both return success from the next-launch command.
- `r4f-preserve`: PASS — exact G1/G2 seams and pre-existing latitude/review/recovery/audit/tracker boundaries survive.
- `r4g-windows`: PASS — installed JSON parses; forward-slash interpreter spelling remains executable and helper bundling is limited to three consumers.
- `r4h-exclusions`: PASS — helper is standard-library/local-only; mint-rail role metadata failures match unchanged HEAD frontmatter and are genuinely pre-existing.

## Code/doc quality

The helper is compact, readable, standard-library-only, and correctly delegates schema semantics to the installed G1/G2 public validators. The missing logic is at the interface boundary after G2 validation: `verify_admiral_prelaunch` must distinguish a structurally valid transition from one that grants launch authority.

## Map impact verdict

- **Evidence supports claimed change:** Mostly; installed artifacts and ordinary transition enforcement are real, but prelaunch authority is incomplete.
- **Constraints not violated:** Scope, offline, no-engine-redesign, discrepancy-evidence, recovery, and tracker-port constraints pass. Fixed human authority and terminal-exit launch safety fail.
- **Notes match the diff:** Structural and capability notes match. The Authority note overstates enforcement.
- **Decision candidates surfaced:** No new design authority is needed; frozen semantics already say inapplicable proposals escalate and stop ends planning.
- **Durable context routed:** Rework belongs inside G3, not Cartographer/Triage.

## Reconciliation check

No architecture map exists. Direct installed-interface review confirms the repaired role seams but shows the final Admiral authority seam remains incomplete.

## Required rework

- In `admiral-prelaunch`, refuse any `REPLAN_RESULT` whose `applicable` is not `true`; a fixed-boundary escalation remains a proposal until a later human-authorized applicable packet exists.
- Refuse `decision:"stop"` in next-launch authorization mode. It may still be verified/rendered by a non-launch transition path, but it cannot clear `NEXT_WAVE` launch authorization.
- Add both cases to the real installed runtime test, recompute the nine-path digest, and dispatch another fresh review.

## Out-of-scope observations

- The direct minting rail still refuses long-standing Explorer/Commander/Admiral frontmatter (`invoker`, plus Explorer description flags). HEAD/current frontmatter comparison confirms this is pre-existing and non-regressed, as the handoff anticipated.

## Workflow Feedback

- **Handoff gaps:** The phrase “exactly one verified exit before next launch” did not explicitly state that `applicable:false` and `stop` are non-launch-authorizing outcomes. The fixed-authority and stop semantics elsewhere make that intent clear, but naming these two negative cases in the runtime matrix would prevent recurrence.
- **Context rediscovered:** G2's verifier deliberately accepts inapplicable escalation proposals and terminal stop results because they are valid transition records; G3 therefore needs a separate launch-authorization check after generic G2 validation.
- **Instructions improvised around:** The supplied runtime test covered the required happy/refusal matrix but not launch authority. I extended the reviewer-owned real-install probe with the two semantic boundary variants while leaving production untouched.
- **What would have made this easier:** Freeze an explicit table of G2 decisions/applicability versus “may authorize next launch” in the G3 handoff and tests.

## Return status

`complete`
