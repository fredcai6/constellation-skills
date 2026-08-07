# Reviewer Handoff

## Gate
g1 — Enforcement scripts + spine resolution (issue-58)

## Survey State Location
Create your review survey checklist at `.agent-work/issue-58/g1-review/review.json`.

## What Was Implemented
The mechanical enforcement layer for constellation-explorer: `scripts/verify_cycles.py` (explore-step hard gate), `scripts/verify_spec_confirmed.py` (review/confirm hard gate: Confirmation block, findings-table Disposition cells, loud `UNCONFIRMED — DO NOT CUT` detection), a generic `<skill-dir>` token in `scripts/init_work_area.py::resolve_spine` (commander token untouched), and behavioral tests (2 new test files + 4 additive cases in test_init_work_area.py).

## How to Inspect the Diff
Commit `1f7c460` on branch `constellation/issue-58` (already committed): `git show 1f7c460 --stat` then `git show 1f7c460`. Also confirm the working tree is clean of unexplained extras: `git status --porcelain`.

## Task Statement
The full implementer handoff is at `.agent-work/issue-58/crew-handoffs/g1-implement/IMPLEMENTER_HANDOFF.md` — read it; its section 1–4 bullets are the contract. Design contract: `.agent-work/issue-58/DESIGN_SPEC.md` (read-only), sections "Headline doctrine 3", Spine rows explore/review/confirm, "Testing pathways" 1–2.

## Close Criteria
- Both verifiers exist, are single-purpose (no shared parsing module), stdlib-only, and exit nonzero with a printed reason on EVERY fail path named in the implementer handoff (zero cycles; unparseable cycle JSON; unconsolidated cycle; DRAFT status on confirm phase; missing Confirmed-by/Date; empty Disposition cell; UNCONFIRMED marker line; missing findings table).
- Independently REPRODUCE, don't just read: run at least one green and one red case per verifier yourself (scratch fixtures), plus `python scripts/verify_spec_confirmed.py .agent-work/issue-58/DESIGN_SPEC.md` (must PASS — the marker prose-mention in that file must NOT trip the refusal).
- `--phase review` passes a DRAFT spec with a complete findings table; default/confirm phase refuses the same file.
- `<commander-skill-dir>` behavior byte-identical (inspect the refactor into `_resolve_skill_dir_token`; confirm pre-existing tests unchanged and passing); `<skill-dir>` resolves with and without `--skill-dir`.
- Tests are genuinely behavioral (assert exit codes/messages on real fixtures, not mocks of the verifier itself); red cases present for every fail path class.
- `python -m pytest tests/test_verify_cycles.py tests/test_verify_spec_confirmed.py tests/test_init_work_area.py -q` green and `python -m pytest tests/ -q` green — run both yourself.
- Diff touches ONLY the allowed scope (below); commit is on constellation/issue-58.

## Allowed Scope
NEW: scripts/verify_cycles.py, scripts/verify_spec_confirmed.py, tests/test_verify_cycles.py, tests/test_verify_spec_confirmed.py. EDIT: scripts/init_work_area.py (resolve_spine + docstring/help only), tests/test_init_work_area.py (additive).

## Specific Exclusions
scripts/checklist_engine.py, scripts/install_constellation.py, tests/test_install_constellation.py, skills/**, .agent-work/issue-58/DESIGN_SPEC.md — flag if the diff touches any.

## Constraints the Implementation Must Respect
- Fail visibly, no silent fallback; a parse problem is a FAIL with a reason, never a silent pass.
- One canonical path: two self-contained scripts, no shared framework.
- CLI/exit-code/print style consistent with sibling verify_*.py scripts.
- Python 3 stdlib only.

## Map Anchors (inbound)
- **Structural:** scripts/verify_cycles.py (NEW), scripts/verify_spec_confirmed.py (NEW), scripts/init_work_area.py::resolve_spine, tests/ (3 files)
- **Capability:** work-area/spine instantiation; hard-gate mechanical enforcement
- **Constraints/assumptions:** spec F3 (explore close requires consolidated cycles), spec F1/F4 (confirm refusal semantics), commander-token back-compat
- **Decision anchors:** DESIGN_SPEC.md findings table F1, F3, F4, F6 — flag any contradiction
- **Evidence expectations:** targeted pytest green then full suite green (feeds g1-integrate.c1)

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g1-implement/IMPLEMENTER_RESULT.md`: 29 targeted tests green; full suite 396 passed 1 skipped; live-spec PASS output; red-case examples pasted; assumptions listed (work-id fallback resolves to `.agent-work/<work-id>/DESIGN_SPEC.md`; pipe-table detector keys on ID/Disposition/Reason headers; marker match is full-line after stripping decoration). Verify the assumptions are sane, not just the outputs.

## Suggested Model Tier
simple bounded — verification of well-specified scripts.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT at `.agent-work/issue-58/crew-handoffs/g1-review/REVIEW_RESULT.md`: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback. The run is only complete when that file exists.
