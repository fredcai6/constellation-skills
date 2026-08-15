# Launch Order: `epic-568-510 — archive resume`

**Issued:** 2026-08-15 by `admiral-epic-568` · **Boundary:** `wave-2-510-engine-ruling` · **Launch:** `epic-568-wave-2-510-engine`
**Frozen.** Read it as written. Where it is wrong, say so and float rather than quietly working around it.

## Mission

Your lane is finished and merged. Only `archive` remains, blocked solely because its `c2`/`c2b`
postconditions require a pushed branch and an OPEN or MERGED pull request while your order fenced you
from creating either. The Admiral has cleared that. Complete `archive` and release your lease last.

## Prior-Wave Verdicts (pasted)

Your engine change landed. Verified at source, not asserted:

- **PR #581 is MERGED** → `main` at `addf98c6`, squash merge. `gh pr view 581` reports
  `state=MERGED`, `mergeCommit=addf98c6`.
- Because it was squashed, your branch commits are **not** ancestors of `main`. Cite `addf98c6`.
- The merged blobs were read directly: `begin-instructed` is present in
  `scripts/checklist_engine.py` (4 occurrences) and in `docs/CHECKLIST_SCHEMA.md` (3) on `main`.
- Gate re-measured at your published head `bf7953b6`, cache-clean: **2997 passed, 7 skipped, 0
  failed**, against a re-measured `main` baseline of 2986/0 at `c23c3d0f`. CI set difference **empty
  in both directions** (89 vs 89) — the strict gate, no amendment needed.

Two things you raised were acted on:

1. **Your premise correction was accepted and recorded.** The human was told their ruling rested on a
   false premise — that the engine already permitted the obedient start, and that implementing the
   ruling literally would have been a no-op — and confirmed the `begin-instructed` relabel satisfies
   the intent. Refusing to implement a no-op was the right call.
2. **`tc3` was amended by the Admiral** and shipped in the same PR, since `docs/` was outside your
   ownership. Your reading was correct: the doc closed the vocabulary at two values. The
   historical-selector section was deliberately **left unchanged** after checking — it names
   `begin-refused`/`begin-released` because those genuinely are the two the selectors count, which is
   exactly why the third is excluded.

`tc4` (duplicated predicate) and `tc5` (pre-existing #467 nonexistent-gate defect) are recorded and
carried to closeout. Neither blocks this archive.

## Pre-Rulings

1. **`decision:publication-is-done` — settled.** Do not push, open, or modify any PR. Do not merge.
2. **`decision:take-the-lease-over` — settled.** Claim with `force` plus a `reason`, stamping
   `previous_session_id` and `takeover_reason`. Takeover, not recreation.
3. **`decision:release-is-last` — settled.** Terminal advance does not auto-release. Advance archive,
   then release explicitly as your final act.
4. **`decision:clear-caches-before-measuring` — settled.** Clear `__pycache__` before any measurement.
5. **`decision:no-shared-config-edits` — settled.** Do not edit `.mcp.json`.

## The MCP door — bound this time

This dispatch launches through the `cli` backend with `--spine`, which binds `SPINE_FILE` and an
assignment-keyed `SPINE_SESSION` into your process before your MCP servers start. Your predecessor in
this lane had to use the disclosed CLI fallback because its door resolved to the `f-424` demo spine.

**Verify before mutating anything:** `spine_status` must describe `epic-568-510`. **If it resolves to
a foreign spine, stop and report — do not proceed and do not fall back.** A claim from a demo-bound
door mutates the demo spine while looking like success.

## Honest-Null Clause

If `archive` refuses for a reason this order has not anticipated, report it and stop. Two Commanders
this epic refused rather than forced, and both refusals were worth more than an advance would have
been. Do not force a gate and do not hand-edit spine state.

## A known harness defect, so you are not surprised by it

`run_crew.py` judges completion by the `--result` artifact existing, but `archive` **moves the whole
work area** — your result document included — into `.agent-work/archive/<date>-<work-id>/`. The
launcher will therefore likely report your run as `failed` even when the archive is perfectly
correct. **That verdict is the harness being wrong, not you.** Do not react to it, do not retry, and
do not move the result back to satisfy it. The Admiral judges this lane on spine state.

## Inherited Latitude

None beyond completing `archive`.

## File Ownership

Yours: your work-area records under `.agent-work/epic-568-510/` and your episode files.
Not yours: `.mcp.json`, `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`.

## Workspace

Worktree `.worktrees/epic-568-510`, branch `epic-568/510-hard-advisory`. Yours alone.

## Pre-empted Steps

Everything through `feedback` is complete. Start at `archive`. Staged feedback is already at
`.agent-work/staged-feedback/epic-568-510/`.

## Data Locations

Findings: `.agent-work/epic-568-510/FINDINGS-archive.md`. **If the harness refuses that write** — it
refused your predecessor's — fold them into the result document and say so. Do not defeat a
tool-level guard with a shell write.

## Budget

One closeout.

## Stop Conditions

- `spine_status` does not resolve to `epic-568-510`.
- `archive` refuses for a reason not anticipated here.
- Completing it would require hand-editing spine state, bypassing the engine, or editing shared config.

## Return Shape

Report: what `spine_status` resolved to (name it explicitly); whether `archive` completed; whether the
lease is released; what archive verification showed; and anything floated.
