# Context step — baseline loaded

## Doctrine sources read
- Inherited global doctrine: `skills/_shared/global-orchestrator.md`, `skills/_shared/global-everyone.md`, `skills/_shared/design-it-twice-brief.md`.
- Commander doctrine: `skills/commander/SKILL.md` + `references/commander-core.md` + `references/crew-dispatch.md`.
- Launch mechanics baseline (reconcile lesson): `scripts/run_crew.py` — `build_crew_argv` shows the current claude-CLI headless form is `claude -p "<prompt>" [--model X]` (issue #91: no `--session`/`--role`/`--handoff` flags; role/handoff/session ride inside the `-p` prompt). My runner reuses this launch form.

## Substitution recorded (no docs/agents/ overlay)
This is a skill-SOURCE repo: there is no `docs/agents/ORCHESTRATOR_CONTEXT.md`, `GLOSSARY.md`, or `engine-config.json`, and no `.agent-work/LESSONS.md`/`AGENT_FEEDBACK.md` at the checkout root. Per the context imperative, substituted the closest repo doctrine: the inherited `_shared/global-*.md` bucket + `README.md`. Engine `config_ref` (docs/agents/engine-config.json) is absent-by-design; engine degrades to built-in defaults (sanctioned).

## Map read
No `docs/architecture/` packet map for the eval-harness area (greenfield: no `evals/`, no `scripts/run_skill_eval.py`). Structural record for this area is the issue #106 spec + launch order. Mission frame at plan will be map-light and say so.

## Binding lessons (from launch order Inherited Context)
- Drive engine from the repo's own templates/scripts.
- One execute gate per deliverable class (design gate, runner, scenarios, unit tests, live acceptance).
- Baseline reconcile: reuse run_crew.py --backend cli launch mechanics (done above).
- New tracked files untracked until staged — say so in diff evidence.
- Never round-trip shipped JSON templates through json.load/dump; surgical text edits.
- Crew spawn prompts must require the crew's final message = complete report before idling.
- Counts/verdicts command-derived with pasted output.
- Engine status vocabulary closed set — use `complete`, never `done`.
