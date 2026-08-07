# Mission Frame — issue #107 (+ #103 commander diet)

## Intent
Split `constellation-commander` into two thin entry-only skills over one mode-neutral core reference, and diet the crew-dispatch mechanics out of the always-loaded body — so a loaded context holds one audience's binding + a pointer, never competing doctrine. Map is the installer bundle maps + SKILL_INDEX + skills tree (skill-source repo; no `docs/architecture/` packet — frame is built from the structural record directly, not shrunk-as-trivial: the change is load-bearing for live skill selection).

## Affected Capabilities
- **skill-install/bundle-composition** — `install_constellation.py` discovers skills by directory and bundles scripts + `_shared` references per skill; adding `commander-delegated` extends the bundle maps.
- **skill-selection** (agent-facing) — frontmatter descriptions steer which skill an agent loads; the split adds a confusable pair (commander-delegated ↔ admiral) that must stay distinguishable.
- **commander-run doctrine** — the role doctrine now lives once in a core reference; both entries bind their principal and point in.

## Structural Anchors
- `skills/commander/SKILL.md` (rewrite → thin human entry)
- `skills/commander/references/commander-core.md` (NEW — doctrine home, mode-neutral)
- `skills/commander/references/crew-dispatch.md` (NEW — diet move: crew wrapper + backend + recovery)
- `skills/commander-delegated/SKILL.md` (NEW — thin delegated entry)
- `skills/commander/templates/**` (UNCHANGED — shared interface, pre-ruled)
- `scripts/install_constellation.py` — `SKILL_SCRIPT_BUNDLES`, `SKILL_REFERENCE_BUNDLES`
- `SKILL_INDEX.md`
- `tests/test_install_constellation.py` — `SKILL_NAMES`, per-skill assertions
- `skills/admiral/SKILL.md` (frontmatter description line ONLY — granted fence exception)

## Governing Constraints / Assumptions
- Core reference name must NOT match `global-*.md` (bundle-glob test pins composition) → name `commander-core.md`.
- Templates stay in `commander/`; both entries reference them (pre-ruled). Delegated entry ships no templates/scripts of its own.
- `_shared/` untouched beyond an explicit diet-to-windows.md need — none exists (crew-dispatch is commander-lifecycle-specific, not platform-generic).
- No new `global-*.md` filenames.
- Cross-skill reach uses the prose-pointer precedent (reviewer/implementer → workbench's `references/checklist-engine.md`), not a token (`<commander-skill-dir>` only rewrites within the commander install, not inside commander-delegated).
- Source repo is authority; never edit installed copies. Superpowers never cited.
- Green at every gate boundary: the new `skills/commander-delegated/` dir makes `discover_skills` + `SKILL_NAMES` demand wiring, so the dir's creation, installer wiring, and test updates land in ONE gate.

## Decision Anchors & Decision Pressure
- **decision (ratified at epic #101 confirm, issue #107 body):** entry-only-over-core, split-where-heavy — four candidates compared, human-picked. This run implements it; does not re-litigate.
- **decision pressure (resolved by launch-order latitude):** delegated entry name = `constellation-commander-delegated` (launch-order recommendation); core = single file `commander-core.md`; crew-dispatch its own reference. No new durable-structure choice needs floating.

## Claims / Evidence Surfaces
- Selection distinguishability (commander / commander-delegated / admiral) — verified by the manual fresh-context cold-agent selection check (F acceptance), transcript pasted.
- Bundle composition + shipping — verified by `python -m pytest tests/test_install_constellation.py` (existing structural net + new per-skill tests).
- Diet move completeness — verified by grep: moved paragraphs absent from SKILL.md/core, present in crew-dispatch.md; before/after word counts command-derived.

## Map Confidence / Staleness / Disputes
None. The installer + tests ARE the enforced structural record and are read directly this run; no low-confidence/stale/disputed area.

## Out of Scope
`skills/interrogator/**` (sibling #103 register rewrite), `skills/admiral/**` beyond the one description line, `skills/docent/**`, `docs/ROADMAP.md`, `_shared/` content, the commander templates, any generalized split apparatus beyond commander's own instance.
