# Reviewer Handoff

## Gate

`g1`

## Survey State Location

`.agent-work/issue-418-iterative-planning/g1-review/review.json`

## What Was Implemented

Hard rename to `constellation-to-initial-issues`; strict shaped-brief/current-wave manifest seam; current-wave-only filing; eight-section epic rendering; stronger receipt recovery; legacy installer migration.

## How to Inspect the Diff

Review the uncommitted shared worktree with `git status --porcelain`, `git diff`, and explicit reads of untracked `skills/to-initial-issues/**` and `tests/test_initial_issues.py`. Compare against `.agent-work/issue-418-iterative-planning/g1-implement/IMPLEMENTER_RESULT.md`. Reviewed digest claimed: `sha256:6cbbac6e4c8bd29cca580e5aca324a107a35f7921ae2a1149311f774adf9db30`; reproduce it with the persisted ordinal/NUL helper and inventory.

## Task Statement

Independently verify the complete frozen G1 contract in `.agent-work/issue-418-iterative-planning/execute.json` and implementer handoff.

## Close Criteria

- Every named shaped-brief/output field, type, enum, and empty/nonempty rule is enforced fail-fast.
- Explorer shaped-brief template feeds initial-cut verifier/renderer directly; title/source mapping is exact.
- Only current-wave issues reach find/create; forecast is structurally non-runnable.
- Zero-edge, dangling-edge, and cycle behavior is correct.
- Exactly eight required epic headings render.
- Epic and every child crash windows recover; stale/mismatched receipt identity refuses before adapter calls.
- Canonical install and exact legacy migration behavior are correct for force/no-force/dry-run/subset/full.
- Rename inventory is complete; historical/legacy/external allowlist is precise; no alias remains.
- Causal TDD evidence and focused green output reproduce.
- Result carries `gate_id: g1`, reviewer identity distinct from implementer, reviewed diff digest, and verdict.

## Allowed Scope

The G1 files named in the implementer result. Existing unrelated `.agent-work` changes are not G1 findings.

## Specific Exclusions

No replanning/G2 work; no broad role-doctrine/G3 work; no archive edits; no live tracker/network calls.

## Constraints

- Use `constellation-reviewer` and drive its survey to completion.
- Review behavior/data shapes, not marker grep alone.
- Treat new untracked files as part of the diff.

## Map Anchors

- **Structural:** `README.md`, `SKILL_INDEX.md`
- **Capability:** initial cut and offline filing
- **Constraints:** one canonical path; adapter/receipt invariants
- **Decision:** hard rename/current-wave-only (`@grade: settled/human`)
- **Evidence:** G1 focused tests, registration rail, exact allowlist audit
- **Confidence:** no architecture map; verify direct interfaces

## Evidence Produced

Implementer result reports identical red/green focused command: RED 27 failed/104 passed; GREEN 120 passed/389 subtests; registration and Explorer tests green; 0 unexpected old-name paths.

## Suggested Model Tier

Stronger — schema, idempotency, and migration defects can be subtle.

## Stop Conditions

Return BLOCK if evidence cannot reproduce, diff digest/scope is inconsistent, strict input behavior is incomplete, or any excluded/live external mutation occurred.

## Return Format

Write `.agent-work/issue-418-iterative-planning/g1-review/REVIEW_RESULT.md` with `gate_id: g1`, `verdict: APPROVE|BLOCK`, `reviewed_diff_digest`, reviewer identity, per-check findings, and workflow feedback; send result to `/root`.
