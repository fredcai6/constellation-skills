# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
g2 — delegated entry skill + install wiring + index + tests + admiral description line (issue #107 commander entry-split).

## Result
`APPROVE`

## Handoff compliance
All handoff deliverables present and correct. The new `constellation-commander-delegated` entry skill exists (`skills/commander-delegated/SKILL.md`, frontmatter + prose body pointing at the commander core), is wired into `SKILL_REFERENCE_BUNDLES`, `SKILL_INDEX.md`, and the test roster (`SKILL_NAMES` + two new methods), and the admiral description line carries the reciprocal exclusion. Full suite independently re-run green. No stop condition triggered.

## Scope drift
Clean. Exactly the five allowed paths are modified: `skills/commander-delegated/SKILL.md` (new), `scripts/install_constellation.py` (one line in `SKILL_REFERENCE_BUNDLES`), `SKILL_INDEX.md` (one entry), `tests/test_install_constellation.py` (`SKILL_NAMES` + 2 methods), `skills/admiral/SKILL.md` (description line only, +1/-1). The `skills/commander/**` changes (M SKILL.md, ?? references/) are g1's prior-gate uncommitted state and were correctly NOT touched — not blocked on. No excluded target touched.

## Evidence verdict
Required evidence present and independently reproduced. Test mode is test-after (install plumbing); satisfied.
- `py -m pytest tests/ -q` → **446 passed, 2 skipped, 143 subtests passed** (re-run by me, matches close criteria).
- Two new tests run alone → 2 passed, 4 subtests.
- Both new tests independently confirmed falsifiable, then reverted:
  - Removing the `"commander-delegated": _GLOBAL_ORCHESTRATOR,` line → `test_commander_delegated_installs_with_orchestrator_bucket` reds with 4 subfails (global-everyone/global-orchestrator/design-it-twice-brief/windows).
  - Mangling the `references/commander-core.md` pointer string → `test_commander_delegated_points_at_installed_commander_core` reds at the literal-string assert.
  - Both reverts verified: worktree diff restored to original 5-file state; grep confirms the strings are back.

## Code/doc quality
Minimal, well-targeted wiring; matches surrounding conventions. Per-criterion checks all pass:
- **Orchestrator bucket:** `_GLOBAL_ORCHESTRATOR = (global-everyone.md, global-orchestrator.md, design-it-twice-brief.md, windows.md)`; commander-delegated installs its `references/` with exactly that bucket.
- **Prose pointer non-dangling:** body cites `references/commander-core.md` in prose (no `<…-skill-dir>` token); the target `skills/commander/references/commander-core.md` exists (16206 bytes). Co-install dependency on `constellation-commander` is named.
- **Retired signature absent:** `grep -rc "delegate is not a replacement" skills/**/SKILL.md` = 0 across all 15 skills; the reworded hyphenated `delegate-not-replacement` pointer form (with `see references/global-everyone.md`) is present in both the delegated and admiral bodies — reword confirmed, signature confirmed gone.
- **Not in SKILL_SCRIPT_BUNDLES:** commander-delegated appears only in `SKILL_REFERENCE_BUNDLES`; absent from `SKILL_SCRIPT_BUNDLES`; no source `scripts/`/`templates/`/`references/` dir created.
- **SKILL_INDEX accurate:** entry path and prose describe the launch-order delegated entry over the same commander core.
- **Admiral edit description-only:** git diff is a single `description:` line change; body untouched.
- **Bidirectional exclusion:** admiral → "for ONE issue under a launch order use constellation-commander-delegated"; delegated → "to run an EPIC … use constellation-admiral" (and "do NOT use when a human is driving (use constellation-commander)"). Both directions present; third-person, what+when.
- **Residual guard test untouched:** `test_relocated_doctrine_leaves_no_residual_in_carrier_skill_md` not amended (absent from the diff) and still green.

## Map impact verdict
- **Evidence supports claimed change:** yes — install + falsification evidence backs the new installable skill and its bucket; prose-pointer existence proven.
- **Constraints not violated:** yes — `commander-core.md` does not match the `global-*.md` glob; cross-skill reach is by prose pointer, not token; issue-102 move-8 single-source residual guard preserved; green at gate boundary.
- **Notes match the diff:** yes — the implementer's Map Impact (new leaf, +1 REFERENCE_BUNDLES key, +1 index entry, +1 SKILL_NAMES, +2 tests, admiral description line) matches the diff exactly; nothing overstated or missing.
- **Decision candidates surfaced:** yes — the mid-run collision (verbatim "delegate is not a replacement" tripping the residual guard) was correctly blocked to the Commander, who adjudicated the pointer-not-paste reword; a test carve-out was rejected because it would reintroduce a retired signature. Sound.
- **Durable context routed:** yes — the handoff-defect observation (verbatim body re-pasting single-sourced doctrine) is captured in the implementer result's workflow feedback; no dropped durable context.

## Reconciliation check
No conflict. The change adds a 15th skill leaf and a confusable-pair cross-reference, consistent with the recorded bundle-composition and skill-selection architecture. No structural baseline concern requiring Cartographer reconcile beyond the routine new-leaf note the implementer already recorded.

## Blockers
- none

## Out-of-scope observations
- none blocking. The handoff-authoring defect (a load-bearing verbatim SKILL body re-pasted single-sourced doctrine and collided with the pre-existing residual guard) was already surfaced and resolved this gate via the pointer reword; no residual work.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: the g2 reviewer handoff was precise and fully enumerated the close criteria, exclusions, and the exact grep/bundle checks to run; every check mapped cleanly to an observable in the tree.
- **Context rediscovered:** minor — the handoff correctly flags `skills/commander/**` as g1's uncommitted state, but a reviewer must still manually disambiguate mine-vs-g1 in `git status`; the explicit "do not BLOCK on them" note in the dispatch covered this adequately.
- **Instructions improvised around:** none. The reviewer skill's survey/engine flow fit the work; I appended eight per-criterion checks (r4a–r4h) plus a tests-bite check (r3a) as siblings under the base survey, which is the sanctioned append pattern.
- **What would have made this easier:** none beyond the implementer's already-filed suggestion (dry-run verbatim SKILL bodies against the residual guard during handoff authoring). The gate as delivered is clean.

## Return status
`complete`
