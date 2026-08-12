# Cartographer Reconcile — epic-198-burndown

**Agent:** cartographer-198
**Date:** 2026-07-19
**Git range reconciled:** `467a6b0..8ba1293` (main) — 31 files, +2721 / -128
**Verdict:** **HONEST NULL** — no baseline map exists to reconcile against; epic-198's structural deltas are folded into issue **#156** (initial self-map), not fabricated into a partial map.

---

## 1. Baseline check (verify, don't assume)

Verified on current `main` (`8ba1293`):

- `docs/architecture/` — **does not exist** (no dir).
- No `packets/`, no `index.md`, no `overlays/`, no `generated/`, no `MAP_BUILD.md` anywhere in-tree (`find` over the whole worktree, `.git` excluded).
- The only `#156` / architecture-adjacent hits are `docs/explainer-demo/*.html` — a `constellation-docent` demo fixture, **not** a real Cartographer map.

So the known context holds: **this repo — the factory that ships the Cartographer — has never been self-mapped.** There is no current-map baseline to diff epic-198 against. A full reconcile is impossible by construction; a *partial* map seeded from just this epic's touched nodes is explicitly forbidden (below).

## 2. Why this is honest-null and not a partial build

Issue **#156** (OPEN) already records the governing ruling from the epic-138 closeout reconcile:

> "A partial map seeded from one epic's diff was explicitly rejected at the epic-138 closeout: sparse-by-accident coverage is a worse signal than no map. A dedicated Cartographer run should do the full initial build."

Epic-198 touched ~10 `scripts/` modules plus doctrine/docs/tests. Authoring `struct:` packets for only those touched nodes would reproduce exactly the rejected pattern — a map whose coverage is an artifact of which files this epic happened to touch, not of the system's real structure. So the doctrinal move is: **leave the map absent, contribute epic-198's structural facts as seed material to #156.**

## 3. Reconcile driven through the engine

Checklist: `.agent-work/epic-198-burndown/cartographer/CARTOGRAPHER.json` (instantiated from `CARTOGRAPHER.template.json`, dogfooded on the source repo's own `scripts/checklist_engine.py`).

| gate | disposition | why |
|---|---|---|
| context | complete | Global doctrine read; no `docs/agents/*` project deltas exist; current-map baseline confirmed empty. |
| packets | complete | Zero touched packets exist to reconcile (no `docs/architecture/`). Vacuous. |
| index-overlays | complete | No index/overlays authored — honest-null creates no map artifacts. Vacuous. |
| map-compliance | complete | Map is trivially compliant (empty); open structural question routed to #156 as the seed contribution below. |

No code was changed. No map artifact was created. That is the correct honest-null footprint.

## 4. Epic-198 structural deltas — seed contribution for #156

When #156's dedicated full self-map runs, these are the current-truth facts epic-198 established, phrased in map terms (all `scripts/` are `component`/`module` structs under a `container` for the engine/tooling layer). This is **seed material, not a map** — it is not authored into any packet.

**Engine / checklist layer (`scripts/checklist_engine.py`)** — deepest node this epic touched; net +189 lines. New current capabilities:
- `resume` verb; `amend` retext-check repair; heartbeat-on-mutate lease refresh.
- `why_ref`-aware refresh-request predicate; survey `why_suffix`; from-child idempotency.
- These are behavior on an existing struct — future `capability:` nodes (resume, why-capture/refresh, lease), not new structs.

**Gauge (`scripts/gauge_reader.py`)** — absolute-token-cap thresholds (intent-first caps). Capability refinement on the Context Governor gauge component.

**Work-root / worktree (`scripts/agent_work_root.py`)** — worktree-aware durable-root resolution under an Admiral epic lease. A `constrained-by` relationship (durable root governed by the epic-lease assumption) worth an overlay edge at build time.

**Eval runner (`scripts/run_skill_eval.py`)** — install-path-invariant `corpus_id`; runner-durability (real-process-death) regression. `verified-by` claim material.

**Stop-rail hook (`scripts/hooks/spine_rail.py`)** — worktree-guard so a subagent's spine is not misattributed to the parent. Boundary-correctness fact for the hooks component.

**Work-area init (`scripts/init_work_area.py`)** — pattern-based placeholder resolver in check commands.

**New module `scripts/stage_feedback.py`** (+211) — a genuinely new `struct:` node (feedback staging helper) for #156 to place under the tooling container. Its tests: `tests/test_stage_feedback.py`.

**Corpus curation (`scripts/curate_corpus.py`)** — status-vocabulary single-source + matcher false-positive tightening (#212, #117 tooling).

**Doctrine/docs (non-structural, mostly capability/decision anchors):** `docs/CHECKLIST_SCHEMA.md`, `docs/CHECKLIST_ENGINE_DESIGN.md`, `docs/superpowers/drills/*` (2 new drills), `skills/_shared/windows.md` headless-probe, several `skills/*/SKILL.md` + template deltas. These are overlay/anchor inputs, not new structure.

## 5. Code/docs mismatch found?

**None that a Cartographer reconcile owns.** This was a burndown epic run under an Admiral with per-issue reviewers and a lessons-auditor; doctrine text and code moved together (e.g. `checklist-engine.md` +28 documenting the resume/retext-check verbs that `checklist_engine.py` added). I did not find a doc asserting a map/packet that does not exist, nor a script referencing `docs/architecture/` as if populated. `references/checklist-engine.md` still correctly describes the reach-up known-gaps as flagged-not-fixed, consistent with the engine's actual `_why_suffix` gated-only behavior.

## 6. Triage candidate raised

One candidate, routed to the existing tracker rather than a new issue:

- **Fold epic-198 structural deltas into #156's seed scope.** Section 4 above is the payload. #156 remains the single home for the initial self-map; this epic adds `scripts/stage_feedback.py` as a new struct and a batch of capability/claim material on the engine, gauge, work-root, runner, and hook components. No new issue needed.

## 7. Docent note (soft pointer)

No published `constellation-docent` explainer site depends on a map here (none exists to go stale). N/A this run.
