# Implementer Handoff

## Gate

`g4`

## Task

Build the hash-pinned, fully offline Epic #418 demonstration and corpus acceptance proof. Use `constellation-implementer`. The complete G4 imperative in `.agent-work/issue-418-iterative-planning/execute.json` is frozen and contractual.

## First Action — Before Reading Historical Inputs

Compute SHA-256 and refuse on mismatch:

- `.agent-work/archive/2026-07-18-explore-context-governor/DESIGN_SPEC.md` = `B2EF1B2A51268B2EE806541F625D7FD8C52B28179239ED7291308A140D2E9DDB`
- `.agent-work/archive/2026-07-18-explore-context-governor/ISSUE_SET.json` = `17BB5086744F23956146CDFF02B9CCCF02116595BE9CE93727A5FA12B002F1F6`

Only after both match may you read/generate. Embed both hashes in the demo. Before mutation, persist a complete path+hash inventory of that archive and an initial `git status`/diff snapshot distinguishing this run's pre-existing protected/unrelated changes.

## TDD / Artifact Verifier First

Create tests and `scripts/verify_epic_418_demo.py` plus `scripts/verify_iterative_planning_acceptance.py` before demo artifacts. The exact demo-verifier command must fail on missing artifacts, then pass after generation:

```bash
uv run python scripts/verify_epic_418_demo.py --work-id issue-418-iterative-planning
```

Record identical red/green command and output. Strict fail-fast artifact schemas/interfaces are required.

## Demonstration

Create `.agent-work/issue-418-iterative-planning/demo-epic-418-iterative-planning/` with at least:

- `ISSUE_418_REGENERATED.md`
- `INITIAL_WAVE.md`
- `WAVE_FORECAST.md`
- `UNCERTAINTY_REGISTER.md`
- `COMPARISON.md`

Retain machine-readable packets/receipts needed for verification. Generate/render through the shipped initial-cut and replan seams. Use a deny harness: injected tracker adapter raises on every write; failing `gh` shim first on PATH; subprocess/network entrypoints spied and asserted zero. Persist a stamped zero-call receipt.

Treat 1–3 initial issues as a hypothesis, never a quota. Require one coherent execution-and-validation loop and reject forced bundling that loses independently observable completion evidence.

## Comparison and Proof

Derive—not hand-copy—A–E dispositions and before/after word, issue, and edge counts from frozen inputs and generated packets. Map every original item. Audit preservation of load-bearing intent, constraints, decisions, evidence, and completion. Walk one concrete deficiency through discrepancy classification and `repair` or `replan`, including forecast hold when blocking. Critically judge whether latitude materially increased rather than merely shortening prose.

Prove all ten acceptance items frozen in G4: canonical renamed install; zero-edge validity; forecast non-filing; eight headings; all four exits; blocking repair holds forecast; evidence-only creates no issue; fixed boundaries preserve or escalate; deny-harness zero tracker/network calls; relevant/full tests green.

## Verification

Run and record:

- demo verifier and iterative acceptance verifier;
- `verify_skill_registered.py` for `to-initial-issues` and `replan`;
- installer/corpus validation and the full `tests` suite;
- changed JSON parsing and `git diff --check`;
- exact allowlisted old-name live-reference audit;
- archive after-inventory/hash comparison and git-diff audit;
- initial/final dirty-worktree comparison proving unrelated changes survived.

Push/PR/live-issue absence is an honest authority/tool audit assertion, not fixture proof. No live tracker/GitHub/network write, push, PR, commit, or archive rewrite.

## Allowed Scope

The two new verifier scripts and focused tests; the clearly named local demo directory and receipts under this run; narrowly necessary current docs/tests to prove acceptance. Preserve all G1–G3 product work and unrelated dirty changes.

## Result

Write `.agent-work/issue-418-iterative-planning/g4-implement/IMPLEMENTER_RESULT.md` with `gate_id: g4`, `red_exit: 1`, `green_exit: 0`, a reproducible whole-change ordinal path+byte digest/inventory/helper, tests/verifiers-before-artifacts evidence, archive inventories, deny receipt, exact commands/results, initial/final dirty comparison, scope/map impact, and workflow feedback. Complete/release the checklist and report to `/root`.
