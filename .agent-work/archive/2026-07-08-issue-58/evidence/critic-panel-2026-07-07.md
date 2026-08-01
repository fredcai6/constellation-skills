# Critic panel raw findings — issue-58 spec review (2026-07-07)

Cold 3-lens panel over DESIGN_SPEC.md (no exploration-record access). Raw counts: intent-fit 7 findings (1 BLOCKING), testability 10 findings (1 BLOCKING), simplicity 8 findings (0 BLOCKING, 5 MAJOR). Deduplicated to 10 consolidated findings; dispositions in DESIGN_SPEC.md findings table, approved by the human 2026-07-07.

## Key verbatim verdict lines

- Intent-fit: "the design is strongest where enforcement is cheap (greppable doctrine text, templates) and weakest exactly where its intent lives (irreversible gates)."
- Testability: "the four testing pathways verify install wiring, JSON parsing, and the presence of doctrine strings — not one of the behaviors the design exists to guarantee."
- Simplicity: "Around that spine the design has accreted a speculative surface… Cut findings 1–5 and the skill still delivers its stated interface at a fraction of the weight."

## Notable repo-verified facts from the panel

- Default rework cap is 3 (`DEFAULT_REWORK_CAP`, checklist_engine.py); no engine-config file in this repo → inline spine config required.
- `reopen` cascades: downstream complete/in-progress gates reset, evidence superseded (checklist_engine.py:823–842).
- `child_checklist` is a single work-id; `advance --from-child` attaches one child consolidation — N cycles cannot be engine-linked that way.
- `resolve_spine` (init_work_area.py) only handles commander tokens today; install-time `rewrite_installed_skill_paths` handles `<skill-dir>` but is a different code path.
- Vocabulary source file is `skills/_shared/global-everyone.md` (no `references/` subdir in source).
- Commander SKILL.md has no shaped-design/confirmation intake check today.

Full raw reports live in the session transcript; this file preserves the decision-relevant core.

## Plan critic (second review round, 2026-07-07)

Cold review of execute.json + MISSION_FRAME.md against DESIGN_SPEC.md. 7 findings: (1) MAJOR hard-gate verifier and its template built in different gates with no cross-check — fixed: g2 now owns spine+CYCLE+DESIGN_SPEC templates AND tests/test_explorer_templates.py cross-check; (2) MAJOR full-suite pytest passes when new test files are absent — fixed: targeted test paths in every integrate c1; (3) MAJOR g2 oversized — fixed: split engine artifacts (g2) from doctrine/templates (g4); (4) MAJOR plan itself ran at default rework cap 3 — fixed: inline config rework_cap 6; (5) MAJOR excursion-brief/prototype-handoff alignment unowned — fixed: prototyper (g3) now precedes explorer templates (g4), which copies fields from the real file and review verifies; (6) MINOR greppable doctrine had no mechanical owner — fixed: grep checks in g3/g4/g5 integrate commands; (7) MINOR POSIX-shell note — no change, informational. Also fixed: spec findings-table column normalized to 'Disposition | Reason' (verifier parse format now stated in spec). Coverage/ordering/engine-fit verified clean by the critic.
