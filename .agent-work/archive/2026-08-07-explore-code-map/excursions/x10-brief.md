# Excursion Brief: storage design-it-twice — node identity + file layout

## The one named question

What is the statement store's on-disk shape — node identity scheme and file layout in git — such that diffs stay reviewable, identity survives renames as well as it can, tag-minted nodes attach cleanly, and the docent can render from it?

## Type

design-it-twice

**Why this type:** load-bearing interface (every producer and consumer touches it); the human commissioned the method explicitly ("agree with storage design it twice - run it").

## What "answered" looks like

Three candidate designs (`excursions/x10-candidate-1.md`, `-2.md`, `-3.md`), each from an independent agent under ONE distinct constraint, followed by an orchestrator comparison + opinionated recommendation (`excursions/x10-result.md`) presented to the human, who picks the winner or a named hybrid.

## Parallel agents (3, distinct constraints)

- **Candidate 1 — diff-ergonomics-first.** Optimize for reviewable git diffs and human-auditable files above all: a small code change should produce a small, legible diff in the store; a reviewer should be able to audit crawler output in a PR. Everything else may be compromised for this.
- **Candidate 2 — rename-survival-first.** Optimize for identity stability: a file move or symbol rename must NOT re-mint the world. Opaque serial identity with path-as-property is the inherited substrate lean — design the id-assignment mechanism concretely (who assigns, when, how a move is detected, what happens on split/merge of an entity). Everything else may be compromised for this.
- **Candidate 3 — minimal-machinery-first (YAGNI).** The least design that satisfies the existing verdicts: full rebuild + diff per Cartographer-workflow run, git as history, no machinery for problems not yet observed. Accept rename re-minting if the mitigation is cheap ruling-time supersession. Everything else may be compromised for simplicity.

## Shared inputs every designer reads first

- The board's Verdicts section (`../IDEAS_BOARD.md`) — especially the shared substrate (JSON-lines statements, markdown prose, git is truth, DB is disposable index, atomic storage + rendered views, current-view-only, per-node content hash, forced supersession) and the grammar/tag verdicts.
- The statement-line shape as prototyped: `evidence/x7b/statements.jsonl` (sample it), `excursions/x7a-result.md` §5 (fact-vs-occurrence hash note), `excursions/x9-result.md` §3 (tag → node/edge mapping, `origin` field, confidence rules).
- Scale numbers: f1Brainz ≈ 44.5k statements for 67 files (x7b), ≈ 217k occurrences repo-wide (x1); the store must stay sane at ~10× that.

## Every candidate MUST deliver

1. **On-disk layout, concretely**: actual example paths and 10–20 lines of sample file content for the `Config.load_config` bundle (structural statements + purpose prose + one `Assumption:`-minted node). Where does directory-per-subject / file-per-layer (the parent's lean) fit, or why deviate.
2. **Identity scheme**: the id on every statement's `s`/`o`, who assigns it, its stability guarantees stated honestly.
3. **The rename scenario, walked**: `src/utils/config.py` → `src/utils/configuration.py` plus `Config.load_config` → `Config.load`. Show what the crawler emits, what the diff looks like, what survives, what re-mints, what a human must rule on.
4. **The re-derive diff scenario, walked**: one function gains a parameter and a new call. Show the store diff a PR reviewer sees.
5. **Tag-attachment**: how an `Assumption:`-minted node and its `origin` live on disk; what happens when the docstring is reworded (slug drift).
6. **Docent feasibility**: 3 sentences on how a static site renders from this layout.
7. **Costs and risks** of its own constraint taken seriously — stated, not hidden.

## Comparison axes (the synthesis scores all three)

Depth (behavior per interface learned), locality (does a change concentrate or scatter), seam placement (where producers/consumers plug in), testability — plus the four walked scenarios above.

## Budget / stop conditions

- ~45 min per designer, independent, no coordination.
- Design documents only — no code, no store built, nothing written outside the work area.
- **Scoped nulls:** a weakness found in one candidate kills that candidate's approach to that scenario, not the axis.

## Return format

Each designer: `x10-candidate-N.md` with the seven deliverables. Orchestrator synthesis: `x10-result.md` — comparison table, opinionated recommendation or named hybrid, presented to the human for the pick.
