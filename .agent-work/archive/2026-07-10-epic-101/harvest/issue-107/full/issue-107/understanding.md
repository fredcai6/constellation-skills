# Understanding — issue #107 (+ #103 commander diet)

Delegated mode: reconciled against LAUNCH_ORDER-issue-107 (frozen principal), not a live human.

## Problem
`constellation-commander` is the corpus's layering epicenter. It is one skill carrying doctrine for two audiences (a live human driving an issue, and a delegated agent under an Admiral launch order). Issue #107 (cluster F) splits it into two thin **entry-only** skills over a single **mode-neutral core reference**, so a loaded context never holds competing instructions. Issue #103's commander move (folded into this wave) diets the body: crew-dispatch mechanics leave the always-loaded surface for a commander reference.

## Scope (this wave, sole writer of `skills/commander/`)
1. **Entry-split (F).**
   - `skills/commander/SKILL.md` — human entry, thin: description with exclusion clause (not for delegated/launch-order dispatch → use commander-delegated); live-human principal binding (ask and wait); pointer into the core.
   - `skills/commander-delegated/SKILL.md` — delegated entry, thin: description with "do NOT use when a human is driving" + admiral-confusable exclusion (ONE issue under a frozen LAUNCH_ORDER; for an EPIC use constellation-admiral); frozen-principal binding (cite and proceed, gaps go up); pointer into the SAME core.
   - `skills/commander/references/commander-core.md` — full role doctrine, mode-neutral against "your principal". Single source; entries carry no competing doctrine.
2. **Commander diet (B).** The ~250-word crew-backend paragraph + "Never hand-launch a crew" kin move to `skills/commander/references/crew-dispatch.md`; the core keeps a one-line pointer. Crew-backend content is commander-lifecycle-specific, not platform-generic, so it does NOT move to `_shared/windows.md` (leaving `_shared/` untouched, per fence). History-to-current-truth sweep applied to all commander prose I rewrite.
3. **Install mechanics.** New `commander-delegated` skill wired into `install_constellation.py` (script + reference bundle maps). Core + templates reach the delegated entry via the **cross-skill prose-pointer** precedent (reviewer/implementer → workbench's `references/checklist-engine.md`); templates stay in `commander/` (pre-ruled). Core named `commander-core.md` (does NOT match `global-*.md` glob). `SKILL_NAMES` test list + `test_shared_reference_dir_is_not_installed_as_a_skill` updated; per-skill install tests added.
4. **Selection check (F acceptance).** Cold fresh-context agent given only skill descriptions + three invocation contexts must name commander / commander-delegated / admiral. Transcript pasted as gate evidence; iterate descriptions if it fails (honest-null clause).
5. **Admiral description line** (granted fence exception): edit ONLY `skills/admiral/SKILL.md`'s frontmatter description if the commander-delegated↔admiral exclusion needs the admiral side; flag loudly; touch nothing else in that file.

## Map-first frame
Skill-source repo, no `docs/architecture/` packet map. Structural truth = `install_constellation.py` bundle maps + `SKILL_INDEX.md` + the skills tree. Governing constraints (all from launch order + issue bodies): bundle-glob tests stay green; no new `global-*.md`; templates unchanged; `_shared/` untouched beyond diet need (none); superpowers never cited; source repo authority (never edit installed copies). No low-confidence/stale/disputed map areas — the installer + tests ARE the enforced structural record and I read them directly.

## Convergence
Delegated: the split architecture (entry-only-over-core, split-where-heavy) was design-it-twiced with four candidates and human-ratified at epic #101 confirm (issue #107 body). This run plans the IMPLEMENTATION; convergence cites LAUNCH_ORDER:Mission + Pre-Rulings. Admiral ratifies at the epic return boundary.
