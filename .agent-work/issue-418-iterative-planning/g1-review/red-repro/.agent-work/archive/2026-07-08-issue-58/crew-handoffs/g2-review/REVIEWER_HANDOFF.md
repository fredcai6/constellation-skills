# Reviewer Handoff

## Gate
g2 — Explorer engine artifacts: spine/cycle/spec templates + verifier↔template cross-check (issue-58)

## Survey State Location
Create your review survey checklist at `.agent-work/issue-58/g2-review/review.json`.

## What Was Implemented
The three engine-facing constellation-explorer templates (`skills/explorer/templates/EXPLORER_SPINE.template.json` with inline `config.rework_cap: 99` and generic `<skill-dir>` tokens; `CYCLE.template.json` survey with `consolidation: null` as shipped and a shotgun|compare|refine flavor field; `DESIGN_SPEC.template.md` with a standalone `**UNCONFIRMED — DO NOT CUT**` banner, DRAFT Confirmation block with assumptions-exercised lines, and the fixed findings-table columns) plus `tests/test_explorer_templates.py` — the cross-check suite proving the g1 verifiers and these templates agree (22 tests).

## How to Inspect the Diff
Commit `a49c8a0` on branch `constellation/issue-58` (already committed): `git show a49c8a0 --stat` then `git show a49c8a0`. Also `git status --porcelain` to confirm no unexplained extras.

## Task Statement
The full implementer handoff is at `.agent-work/issue-58/crew-handoffs/g2-implement/IMPLEMENTER_HANDOFF.md` — read it; its items 1–4 are the contract. Design contract: `.agent-work/issue-58/DESIGN_SPEC.md` (read-only), section "Chosen design 1" (Spine table, Exploration cycles, Critical review paragraph), "Testing pathways" 1b/2; Output-contract sections in `.agent-work/issue-58/PROBLEM_STATEMENT.md` item 9.

## Close Criteria
- **Spine vs Spec Spine table, line by line**: steps exactly init/context/explore/spec/review/confirm/route in order; explore closes on user-decision evidence AND a `verify_cycles.py` command check; review runs `verify_spec_confirmed.py --phase review`; confirm requires user-decision evidence AND default-phase `verify_spec_confirmed.py`; route statement covers all three human routes + archive + lease release; inline `config` with `rework_cap: 99`; every script path uses `<skill-dir>` (zero `<commander-skill-dir>` occurrences).
- **Spine actually drives**: independently REPRODUCE — instantiate the spine via `python scripts/init_work_area.py <tmp-work-id> --spine skills/explorer/templates/EXPLORER_SPINE.template.json --skill-dir <repo-root-as-posix>` into a scratch area, confirm no unresolved `<skill-dir>` tokens remain, and that `checklist_engine.py` can claim + start it.
- **CYCLE template**: ships with `consolidation: null` (so an as-shipped cycle FAILS `verify_cycles.py`); a consolidated copy passes; flavor field present with the three values named.
- **DESIGN_SPEC template**: run the real verifier yourself — the shipped template must FAIL both `--phase review` and default phase (marker refusal); verify the transformation path: remove the banner + flip Status to CONFIRMED + fill Confirmed-by/Date + fill Disposition/Reason cells → PASSES both phases. Check each Confirmation field's blank case independently (blank Confirmed-by with Date filled, and vice versa) — this exact class was the g1 escaped defect.
- **Findings table** header is exactly `| ID | Lens | Severity | Finding | Disposition | Reason |`.
- **Cross-check test is genuine**: asserts real subprocess/import behavior of the real verifiers against template-derived fixtures (not mocks, not string asserts on the templates alone); red cases present for: marker refusal both phases, incomplete-table review refusal, each Confirmation field blank independently, zero cycles, one-unconsolidated-among-consolidated; engine claim/start exercised.
- `python -m pytest tests/test_explorer_templates.py -q` green — run it yourself.
- **Full-suite status is exactly as claimed**: run `python -m pytest tests/ -q` yourself and confirm ALL failures are in `tests/test_install_constellation.py` and are attributable to `skills/explorer/` lacking `SKILL.md` (g4) or missing expected-skills entries (g5) — zero failures in any other file. This transient is pre-authorized by g2-integrate.c1's override_policy (human authority); it is NOT a BLOCK finding by itself, but ANY non-install failure, or any install failure with a different root cause, IS.
- Diff touches ONLY the allowed scope (below); commit on constellation/issue-58.

## Allowed Scope
NEW only: skills/explorer/templates/EXPLORER_SPINE.template.json, skills/explorer/templates/CYCLE.template.json, skills/explorer/templates/DESIGN_SPEC.template.md, tests/test_explorer_templates.py.

## Specific Exclusions
scripts/** (especially the two verifiers and init_work_area.py — g1 owns them; a script change to make a template pass is a BLOCK), skills/explorer/SKILL.md + other explorer templates (g4), skills/prototyper/** (g3), skills/_shared/**, scripts/install_constellation.py, tests/test_install_constellation.py (g5), skills/commander/**, .agent-work/issue-58/DESIGN_SPEC.md — flag if the diff touches any.

## Constraints the Implementation Must Respect
- Fail visibly: the shipped DRAFT template is REFUSED by the verifier — a template the verifier tolerates as-shipped is a defect.
- Marker discipline: exactly ONE standalone marker line in the template; every other mention inline in prose (the verifier's `_unconfirmed_marker_hit` only trips on standalone lines — verify placement against the script's behavior, not by eye).
- One canonical path: instantiation via existing `init_work_area.py`, no new mechanism.
- Column names, marker string, step names/order, evidence types, rework cap value are contractual — any variance is a finding.
- Python 3 stdlib only in the test.

## Map Anchors (inbound)
- **Structural:** skills/explorer/templates/ (NEW, 3 files), tests/test_explorer_templates.py (NEW); depends on scripts/verify_cycles.py, scripts/verify_spec_confirmed.py, scripts/init_work_area.py::resolve_spine (all read-only here)
- **Capability:** explorer spine instantiation; hard-gate template side; verifier↔template agreement
- **Constraints/assumptions:** spec F1/F3/F4 refusal semantics; inline rework_cap 99 (spec Critical-review paragraph); `<skill-dir>` token resolution
- **Decision anchors:** DESIGN_SPEC.md Spine table rows explore/review/confirm; findings table F1, F3, F4, F6 — flag contradictions
- **Evidence expectations:** targeted suite green (feeds g2-integrate.c1 first half); full-suite transient documented and scoped to install tests only

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g2-implement/IMPLEMENTER_RESULT.md`: 22 targeted tests green; transformation matrix (raw-draft refusals, per-field blank fails, confirmed pass); cycle green+red outputs; engine claim/start transcript; full suite 31 failed / 389 passed with a diagnostic attributing 29 failures to missing SKILL.md and 2 to expected-skills lists. Verify the attribution claim yourself, not just the outputs. Assumptions listed (POSIX --skill-dir for Windows JSON safety; no engine_session key; engine ignores unknown top-level keys) — verify they are sane.

## Suggested Model Tier
stronger — contract-alignment review across four artifacts plus adjudicating a red full suite; the expensive part is verifying the failure attribution, not reading the templates.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, any non-install-test failure exists in the full suite, or a policy decision beyond the pre-authorized install-test transient is required.

## Return Format
Return REVIEW_RESULT at `.agent-work/issue-58/crew-handoffs/g2-review/REVIEW_RESULT.md`: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback. The run is only complete when that file exists.
