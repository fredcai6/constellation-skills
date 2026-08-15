# Launch Order: `epic-568-530 — archive resume`

**Issued:** 2026-08-15 by `admiral-epic-568` · **Boundary:** `wave-2-gate-refusal` · **Launch:** `epic-568-wave-2-repair`
**Frozen.** Read it as written. Where it is wrong, say so and float rather than quietly working around it.

## Mission

Your lane is finished and merged. Only `archive` remains, and it was blocked solely because its
`c2`/`c2b` postconditions require a pushed branch and an OPEN or MERGED pull request while your
launch order fenced you from creating either. The Admiral has cleared that. Complete `archive` and
release your lease last.

## Prior-Wave Verdicts (pasted)

Your own blocker, verbatim:

> The frozen LAUNCH_ORDER expressly forbids push, PR, and merge, but archive postconditions c2 and
> c2b require this branch to be pushed and have an open or merged PR. Local commits and tracked
> archive episode verification are complete.

That refusal was correct. Publication is the Admiral's delegated class, not yours and not a human
escalation. It has been exercised:

- **PR #580 is MERGED** → `main` at `c23c3d0f`. Verified at source: `state=MERGED`,
  `mergeCommit=c23c3d0f`, and `git cat-file -e origin/main:tests/test_spine_rail.py` confirms the
  guard is genuinely on `main` rather than merely claimed.
- The merge was a **squash**, so your branch commits are not ancestors of `main`. Cite `c23c3d0f`.
- Your branch was **rebased by the Admiral** onto `e0c998b6` before publication, because merging the
  Codex lane first put both lanes in conflict on `map/INDEX.md`. That conflict was resolved by
  **regenerating** the map, never by hand-editing a generated file. Your published head was
  `4ceace75`.
- Gate re-measured at that exact head, cache-clean: **2988 passed, 7 skipped, 0 failed**, against a
  re-measured `main` baseline of 2986/0. The CI set difference was **empty in both directions**
  (89 vs 89) — your lane passed the strict gate and needed no amendment.

## Pre-Rulings

1. **`decision:publication-is-done` — settled.** Do not push, open, or modify any PR. Do not merge.
2. **`decision:admiral-rebase-stands` — settled.** The rebase and the regenerated map are legitimate
   integration acts. Reconcile them; do not revert or re-attribute them.
3. **`decision:take-the-lease-over` — settled.** Your predecessor's lease is live. Claim with `force`
   plus a `reason`, which stamps `previous_session_id` and `takeover_reason`. Takeover, not
   recreation. Do not create a new spine.
4. **`decision:release-is-last` — settled.** Terminal advance does not auto-release. Advance archive,
   then release explicitly as your final act. Your predecessor deliberately did **not** release, and
   was right: releasing a non-terminal spine strands archive's own closeout outside any lease.
5. **`decision:clear-caches-before-measuring` — settled.** If you measure anything, clear
   `__pycache__` first.
6. **`decision:no-shared-config-edits` — settled.** Do not edit `.mcp.json`.

## The MCP door — bound this time

Your spine is `.agent-work/epic-568-530/spine.json`. This dispatch launches through the `cli` backend
with `--spine`, which binds `SPINE_FILE` and an assignment-keyed `SPINE_SESSION` into your process
before your MCP servers start.

**Verify it before mutating anything:** `spine_status` must describe `epic-568-530`, not
`scratch-mcp-424` or any interactive-demo spine. **If it resolves to a foreign spine, stop and report
— do not proceed and do not fall back.** Three sessions in this epic were handed doors bound to the
demo spine; a `spine_lease claim` from there mutates the *demo* spine while looking like success.
That is the failure this instruction exists to prevent.

## Honest-Null Clause

If `archive` refuses for a reason this order has not anticipated, report it and stop. Your
predecessor's refusal was worth more than a forced advance. Do not force a gate and do not hand-edit
spine state.

## Inherited Latitude

None beyond completing `archive`. The implementation is closed, reviewed, merged.

## File Ownership

Yours: your work-area records under `.agent-work/epic-568-530/` and your episode files.
Not yours: `.mcp.json`, `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`.

## Workspace

Worktree `.worktrees/epic-568-530`, branch `epic-568/530-binding`. Yours alone.

## Pre-empted Steps

Everything through `feedback` is complete. Start at `archive`.

## Data Locations

Findings: `.agent-work/epic-568-530/FINDINGS-archive.md`. **If the harness refuses that write**, fold
your findings into the result document and say so — another Commander hit exactly that collision and
was right not to defeat a tool-level guard with a shell write.

## Budget

One closeout.

## Stop Conditions

- `spine_status` does not resolve to `epic-568-530`.
- `archive` refuses for a reason not anticipated here.
- Completing it would require hand-editing spine state, bypassing the engine, or editing shared config.

## Return Shape

Report: what `spine_status` resolved to (name it explicitly); whether `archive` completed; whether the
lease is released; what archive verification showed; and anything floated.
