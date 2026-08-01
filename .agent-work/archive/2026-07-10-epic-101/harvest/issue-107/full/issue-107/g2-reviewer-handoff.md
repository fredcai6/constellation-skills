# Reviewer Handoff

## Gate
g2 — delegated entry skill + install wiring + index + tests + admiral description line.

## Survey State Location
Create your review survey at `.agent-work/issue-107/g2-review/review.json` (under the issue workbench, never the worktree root).

## What Was Implemented
A new `constellation-commander-delegated` entry skill (thin: frontmatter + body pointing at the commander core), wired into the installer's reference bundle map, `SKILL_INDEX.md`, and the test roster, with two new per-skill install tests; plus a one-line edit to `skills/admiral/SKILL.md`'s frontmatter `description` adding the reciprocal confusable-pair exclusion. This is one gate of the issue #107 commander entry-split (g1 already landed the core reference, the crew-dispatch reference, and the thin human `commander/SKILL.md` — those are g1's UNCOMMITTED worktree state, not this gate's change).

## How to Inspect the Diff
Review target is the UNCOMMITTED working tree of `C:\Programs\constellation-wt-107` (branch constellation/issue-107). Inspect with `git status --porcelain` then `git diff` and read the untracked new files directly (`skills/commander-delegated/SKILL.md`). This gate's files: `skills/commander-delegated/SKILL.md` (new), `scripts/install_constellation.py`, `SKILL_INDEX.md`, `tests/test_install_constellation.py`, `skills/admiral/SKILL.md`. The `skills/commander/**` changes (SKILL.md modified + new `references/`) are g1's, NOT this gate's — do not BLOCK on them.

## Task Statement
Create the delegated entry skill and wire it in so the full suite stays green; the load-bearing description texts were Commander-authored verbatim in the implementer handoff (`.agent-work/issue-107/g2-implementer-handoff.md`).

## Close Criteria
- `constellation-commander-delegated` installs (dir + SKILL.md) and its bundled `references/` carries the `_GLOBAL_ORCHESTRATOR` bucket (global-everyone.md, global-orchestrator.md, design-it-twice-brief.md, windows.md).
- The delegated SKILL.md reaches the core + templates by PROSE POINTER at the installed `constellation-commander` skill (no `<…-skill-dir>` token; no dangling path) and names its co-install dependency.
- `py -m pytest tests/ -q` is fully green (446 passed / 2 skipped expected). The two new per-skill tests are real and falsifiable.
- `SKILL_INDEX.md` has an accurate delegated-commander entry (this doc is unpinned by any test — verify it yourself).
- Descriptions are third-person, what+when, and the commander-delegated ↔ admiral exclusion exists BOTH ways.
- The admiral edit is the description line ONLY.
- No retired inline doctrine signature reintroduced: `grep "delegate is not a replacement"` returns 0 across `skills/**/SKILL.md` (the binding was reworded to the hyphenated pointer form after a first-pass collision — confirm the reword is present and correct, not the signature).

## Allowed Scope
`skills/commander-delegated/SKILL.md` (new), `scripts/install_constellation.py` (SKILL_REFERENCE_BUNDLES only), `SKILL_INDEX.md`, `tests/test_install_constellation.py` (SKILL_NAMES + new methods), `skills/admiral/SKILL.md` (description line only).

## Specific Exclusions
`commander-delegated` must NOT be in `SKILL_SCRIPT_BUNDLES`; no delegated source templates/scripts/references dirs; no new `global-*.md` filename; no change to `skills/commander/**` this gate; the existing `test_relocated_doctrine_leaves_no_residual_in_carrier_skill_md` must NOT have been amended.

## Constraints the Implementation Must Respect
- Cross-skill reach by prose pointer (workbench-engine precedent), not a token.
- Core name `commander-core.md` (does not match `global-*.md`).
- Green at gate boundary (whole suite).

## Map Anchors (inbound)
- **Structural:** `skills/commander-delegated/SKILL.md`; `install_constellation.py::SKILL_REFERENCE_BUNDLES`; `SKILL_INDEX.md`; `tests/test_install_constellation.py::SKILL_NAMES`; `skills/admiral/SKILL.md` description.
- **Capability:** skill-install/bundle-composition; skill-selection (confusable pair commander-delegated ↔ admiral).
- **Constraints:** bundle-glob tests stay green; no new global-*.md.
- **Evidence expectations:** `py -m pytest tests/ -q` green; new tests bite (falsification note in the IMPLEMENTER_RESULT).

## Evidence Produced
See `.agent-work/issue-107/g2-IMPLEMENTER_RESULT.md` (includes the Commander rework reconciliation with the green suite tail + falsification note). Re-run the suite yourself to confirm. Target postcondition for the green suite is `g2-integrate.c1`.

## Suggested Model Tier
simple bounded — mechanical wiring against a precise handoff; verify independently.

## Stop Conditions
BLOCK if: the diff cannot be accessed, the suite is not green, a retired signature is present in a SKILL.md body, the admiral edit exceeds the description line, or the prose pointer dangles/uses a token.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback. Write it to `.agent-work/issue-107/g2-REVIEW_RESULT.md` AND make your FINAL MESSAGE the complete REVIEW_RESULT before going idle.
