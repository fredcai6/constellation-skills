# Triage Recommendation: Split `render_module_uncertainty_diagnostics_markdown` to clear simplification-limit debt

## Classification
`cleanup`

## Source checklist/artifact
- review finding (g1 review, tc1)
- evidence: `py -m src.utils.simplification_limits --paths src/evo_predictor/module_uncertainty_diagnostics.py`

## Structural anchor
`struct:evo.module_uncertainty_diagnostics` / `src/evo_predictor/module_uncertainty_diagnostics.py`

## Cartographer mismatch class
none (no map mismatch; the function exists and the packet describes the module accurately).

## Problem
`render_module_uncertainty_diagnostics_markdown` exceeds the project simplification limits: cyclomatic_complexity=26 (limit <20) and function_lines=149 (limit <100). The strict `--paths` simplification check flags it whenever the file is touched, creating friction for any future change to this module.

## Current truth
- The violation is PRE-EXISTING; it was not introduced by #384 (the #384 diff only changed a constant + comment and test fixtures).
- The canonical `verify_simplification_limits --baseline` check TOLERATES it today (the baseline FAILs only on 2 unrelated files: `models/_param_dataclasses.py`, `reporting/html_reports/__init__.py`).
- The function works correctly and is covered by markdown-rendering unit tests in `tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py`.

## Desired/future concern
Refactor the markdown renderer into smaller composable section-builders (it already has `_sigma_corr_section_lines` as a precedent) so the function falls under the complexity/length limits and the file stops tripping `--paths` strict mode.

## Evidence
- `simplification_limits --paths` output: `render_module_uncertainty_diagnostics_markdown: cyclomatic_complexity=26 (limit: <20)`, `function_lines=149 (limit: <100)`.
- `simplification_limits --baseline`: 2 violations total, neither in this file → pre-existing-but-tolerated.

## Impact
Low correctness impact (function is correct + tested). Maintenance-erosion / developer-friction impact: every future edit to `module_uncertainty_diagnostics.py` trips the strict per-path check, forcing reviewers to re-confirm the violation is pre-existing.

## Suggested scope
Extract per-section markdown builders (summary table, per-module detail, bins, correlations, event-flag counts) into small helpers mirroring `_sigma_corr_section_lines`; keep output byte-identical (the existing rendering tests pin it). Bring both metrics under limits.

## Non-goals
- No change to report content, schema, or the JSON payload.
- No change to the diagnostic gate logic (that was #384).

## Acceptance criteria
- [ ] `render_module_uncertainty_diagnostics_markdown` (and any new helpers) are each under cyclomatic_complexity <20 and function_lines <100.
- [ ] `py -m src.utils.simplification_limits --paths src/evo_predictor/module_uncertainty_diagnostics.py` passes.
- [ ] Existing markdown-rendering unit tests still pass with no output change.

## Recommended priority
`low`

**Reason:** Pure cleanup; pre-existing; tolerated by the canonical baseline; no correctness or contract risk. Worth doing opportunistically the next time this renderer is edited.

## Related artifacts
- architecture packet: `docs/architecture/packets/evo_predictor.md` (module_uncertainty_diagnostics sidecar)
- review result: `.agent-work/issue-384-sigma-keyset/crew-handoffs/g1-review-result.md`

## Issue creation authority
`ask user` — Admiral approves issue creation (per dispatch standing order + spine triage user-decision checkpoint). Recommendation is issue-ready; NOT filed.
