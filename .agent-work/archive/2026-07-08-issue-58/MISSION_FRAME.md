# Mission Frame — issue-58

No packet map exists in this repo; frame is drawn from the map substitutes read at context (README.md, docs/CONSTELLATION_OVERVIEW.md relationship contract) and the confirmed DESIGN_SPEC.md, which supersedes the issue text.

## Intent

Ship the confirmed design: two new skills (`constellation-explorer`, `constellation-prototyper`), their enforcement scripts with behavioral tests, the deep-module vocabulary in shared global doctrine, one Commander intake line, and installer/test integration — exactly as specified in `.agent-work/issue-58/DESIGN_SPEC.md` (CONFIRMED 2026-07-07).

## Affected Capabilities

- capability: upstream idea shaping (NEW — explorer: cyclic exploration → confirmed spec → routed)
- capability: throwaway prototyping (NEW — prototyper: one question → answer, delete-or-absorb)
- capability: skill install/bundling (install_constellation.py — two new entries, bundle lists)
- capability: work-area/spine instantiation (init_work_area.py — generic `<skill-dir>` token)
- capability: Commander issue intake (one doctrine line: shaped-design confirmation check)

## Structural Anchors

- struct: skills/explorer/ (NEW — SKILL.md + templates/ ×7)
- struct: skills/prototyper/ (NEW — SKILL.md + references/ ×3 + templates/ ×2)
- struct: skills/_shared/global-everyone.md (vocabulary section appended)
- struct: skills/commander/SKILL.md (one intake line in understand guidance)
- struct: scripts/verify_cycles.py, scripts/verify_spec_confirmed.py (NEW)
- struct: scripts/init_work_area.py::resolve_spine (extended)
- struct: scripts/install_constellation.py (SKILL_SCRIPT_BUNDLES / SKILL_REFERENCE_BUNDLES)
- struct: tests/ (new: test_verify_cycles.py, test_verify_spec_confirmed.py; extended: test_init_work_area.py, test_install_constellation.py)

## Governing Constraints / Assumptions

- constraint: hard gate is mechanical (verifier + marker + intake line) — not prose-only (spec F1)
- constraint: explorer spine carries inline engine config, effectively-unbounded rework cap (spec F2)
- constraint: explore cannot close without ≥1 consolidated cycle (spec F3)
- constraint: confirm refuses on empty disposition cells (spec F4)
- constraint: excursions dispatch via run_crew.py/recover_crews.py (spec F5)
- constraint: `<commander-skill-dir>` token back-compat preserved in resolve_spine (existing commander spines must not break)
- constraint: headline doctrine texts (anti-rush/human-only convergence; scoped nulls; hard gate) verbatim-greppable in SKILL.md files
- constraint: explorer never cuts issues itself (route hands off)
- assumption: installer auto-discovery needs no change for new skills/ dirs (verified against source at context)

## Decision Anchors & Decision Pressure

- decision: DESIGN_SPEC.md findings table F1–F10 — all major shape choices fixed there (incl. rejected alternatives with reasons)
- decision pressure: none expected — the spec pre-resolves the known choices; a gate discovering a spec conflict surfaces to the human, never improvises

## Claims / Evidence Surfaces

- claim: full pytest suite green after each gate (command: python -m pytest tests/ -q)
- claim: install dry-run lists both new skills with correct names
- claim: instantiated explorer spine passes engine claim/start with resolved script paths

## Map Confidence / Staleness / Disputes

- The repo has no packet map; the relationship-contract doc (CONSTELLATION_OVERVIEW.md) gains two producer rows at reconcile. No stale/disputed areas — engine mechanics claims were source-verified by the critic panel this run.

## Out of Scope

Per spec: Admiral doctrine, Interrogator changes, other Commander changes beyond the one intake line, to-issues/to-prd changes, durable docs/ spec home, critical-review standardization beyond explorer (triage candidates).
