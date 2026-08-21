# Reconciliation Handoff — defect ledger and live issue graph

## Task

Give every item in `CONSTELLATION_DEFECTS.md` and every issue this epic touched
an explicit, evidence-backed disposition. This is the last outstanding exit
criterion before the human checkpoint.

**Analysis only. You may read GitHub; you may not write to it.** No `gh issue
close`, `comment`, `edit`, `reopen`, or `create`. Every disposition you reach is
a *recommendation* the human rules on. Say plainly what you would do and why;
do not do it.

## Inputs

- `CONSTELLATION_DEFECTS.md` in the main checkout (5 items, numbered 0–4, found
  2026-08-15 against the then-current install).
- The live issue graph: `gh issue view <n>` and `gh issue list`.
- Issue #457 specifically — the contract names its scope reconciliation as
  delegated for analysis.
- This epic's integration branch `afk/20260820-deficiency-integration` at
  `efe92791`, which merged #500, #636, mechanical #638, #613, and a map regen.

## What "evidence-backed" means here

For each defect-ledger item, decide and prove one of:

- **Fixed** — name the commit or shipped code that fixes it, and show the
  mechanism. Do not infer a fix from an issue being closed.
- **Live** — reproduce it, or show the code path that still permits it.
- **Stale premise** — the item describes behavior that no longer exists or never
  did. Retiring a stale item is a valuable result, not a failure.
- **Mis-scoped** — the symptom is real but attributed to the wrong cause.

Same for each related issue: does the live code still support the issue's
premise?

## Findings from this epic you must account for

This epic produced measurements that bear directly on several ledger items. Read
`evidence/CHANNEL-EXPERIMENT.md` and `evidence/LIVED-CLUSTER-EVIDENCE.md`
(including all three Corrections) before you start. In particular:

- A crew on the shipped `run_crew --backend cli` path drove a full seven-gate
  plan with **zero claims and zero releases**; `require_session` permits
  leaseless operation explicitly.
- 58 plans in this checkout hold `active` leases; **all 58 are stale**.
- `_is_stale` is never called in any rendering path, so a dead plan renders as
  live and the rail tells a reader to resume it.
- Ledger item 0 concerns `claimed_at` and the #477 foreign-reading guard. Check
  whether the above changes its standing.
- `origin.parent` is written by `build_origin` and carried by zero plans.

Where a ledger item and this epic's evidence disagree, say so and show which is
right on current code.

## Deliver

A table of every ledger item and every related issue with: current standing, the
evidence, the recommended disposition, and — where the recommendation is to
close or re-scope — the exact text you would post, ready for a human to send or
discard.

Flag separately anything that should become a **new** issue, with a one-line
justification each. Do not file them.

## Hard constraints

No GitHub writes. No source, test, `map/`, or commit changes. Do not call any
`mcp__spine__*` tool. Do not choose or implement an architecture — that decision
is held for the human and two design lanes are running on it now.

## Result

Write `crew-handoffs/wave2-reconciliation-result.md` in the main checkout at
`/home/tommy/projects/constellation-skills/.agent-work/20260820-deficiency-cleanup/`.
Do not commit it.
