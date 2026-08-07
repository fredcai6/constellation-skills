# Cartographer reconcile — epic-138 — result: honest null

## Task

Reconcile the architecture map of `constellation-skills` with the epic-138 net change merged to main (a9bb9b3, PRs #146-#150): checklist-engine `_rail()` doctrine-rail surface, new `scripts/hooks/spine_rail.py` + hook registrations, fencing-aware staged-trio acceptance in `verify_agent_feedback.py`, four-clause clamps / pointer-with-force doctrine text across 11 skills, and two new test files.

## Finding

No architecture map exists for this repo, and none ever has.

- No `docs/architecture/` directory anywhere in the working tree.
- No `packets/`, `overlays/`, `index.md`, or `MAP_BUILD.md`.
- `git log --all -- docs/architecture` and `git log --diff-filter=A -- '**/docs/architecture/**'` return nothing — no commit, on any branch, has ever added a file under that path.
- `docs/CONSTELLATION_OVERVIEW.md` documents the *contract* Cartographer is supposed to produce (`docs/architecture/packets/` + `index.md`, consumed by Scout, Commander, Implementer, Reviewer, Docent), so the intent is on record — it just was never executed.
- `scripts/build_architecture_map.py` (+ `tests/test_build_architecture_map.py`) is real, working generator/validator tooling: it reads packets from `docs/architecture/packets/*.md` and overlays from `docs/architecture/overlays/*.yml`, scans source trees for unmapped modules, validates node/edge shape, and writes `docs/architecture/generated/map.json`. It has simply never been pointed at this repo's own source tree with real packets as input.
- `constellation-skills` is the skills-authoring/factory repo: the Cartographer skill it ships (`skills/cartographer/`) is designed to map *downstream target repos* that install these skills. Nobody has run it reflexively, on the factory repo itself, before now.

## Verdict

**Reconcile = honest null.** There is nothing to reconcile the epic-138 net change against, because there is no baseline map. Producing a map now — even one scoped only to the epic-138-touched surface — would misrepresent coverage: a map that only shows the six epic-138 components would read as "this is what the map covers" when in fact the other ~95% of the repo (all other skills, the checklist engine's non-rail surface, the eval harness, docs tooling, etc.) is equally unmapped and no more or less current. Partial coverage born from one epic's diff is not sparse-by-inclusion-rule; it's sparse-by-accident-of-which-PRs-happened-to-land-recently, which is a worse signal than no map at all.

No branch was created and no PR was opened, per this ruling.

## Recommendation for the future initial-build scope (seeds the triage issue)

When a dedicated initial-build run is scheduled, I'd cut containers/components roughly as follows, following the map model's C4-style levels and the Inclusion Rule (sparse, planning-useful, boundary-correct):

- **`scripts/` -> one container ("Engine & Tooling")**, split into components by role: the checklist engine (`checklist_engine.py` + the new `_rail()` doctrine-rail surface as a sub-component — it's a distinct, cross-cutting enforcement surface worth its own packet), the hook layer (`scripts/hooks/*`, notably `spine_rail.py` and its Stop/SessionStart/PostToolUse registrations in `.claude/settings.json` — this crosses a real boundary, session lifecycle to repo state, so it earns a component packet), the feedback/verification tooling (`verify_agent_feedback.py`, including the fencing-aware staged-trio convention under `.agent-work/staged-feedback/<work-id>/`), the map-build tooling itself (`build_architecture_map.py`), the eval harness (`run_skill_eval.py`), and the corpus curator (`curate_corpus.py`). Each of these is independently invoked and independently owned, which is exactly the "consumer depends on provider across a boundary" signal the map model wants.
- **`skills/` -> one container per role ("Cartographer", "Commander", "Explorer", etc.), each a component.** Each skill directory (`SKILL.md` + `templates/` + `references/`) is a natural component boundary already enforced by the repo's own convention (each ships its own checklist engine copy, its own templates). Don't map into `references/*.md` doctrine prose as separate struct nodes — that content becomes `capability:`/`constraint:` overlays or packet prose, not new structural leaves, per the Inclusion Rule (prose isn't structure). The four-clause clamps and pointer-with-force doctrine from epic-138 are a good first example of content that belongs as a `constraint:` overlay anchored to the affected skill components, not a new struct.
- **`docs/` -> mostly *not* struct nodes.** `CONSTELLATION_OVERVIEW.md`, `ROADMAP.md`, `CHECKLIST_SCHEMA.md`, etc. are the shared-contract documents the map model itself points at (Relationship Contract table) — they're better represented as `capability:`/`decision:` anchors and edges *from* struct nodes (e.g., checklist engine `explained-by` a decision anchor sourced from `CHECKLIST_ENGINE_DESIGN.md`) than as their own structural hierarchy. Treat `docs/agents/*` similarly if/when it exists downstream.
- **`tests/` -> not a separate container.** Map tests as `verified-by` claim evidence attached to the struct/capability they cover (e.g., `test_spine_rail.py` -> `verified-by` claim on the `spine_rail.py` component; `test_clamp_presence.py` -> `verified-by` claim on the doctrine-clamp constraint), not as their own structural nodes — this matches the model's "tests are evidence inputs, not a durable node kind" rule.
- **Root-level (`SKILL_INDEX.md`, `README.md`, `LICENSE`)** stay out of the map entirely — navigation/legal, not structure.

This split keeps the initial build's early ceremony proportionate: a handful of containers, one component per skill/tool-cluster, and doctrine text captured as overlays rather than invented struct leaves — consistent with "the map is sparse; every node earns its place."
