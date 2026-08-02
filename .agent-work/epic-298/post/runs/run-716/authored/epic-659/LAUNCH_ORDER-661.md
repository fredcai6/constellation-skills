# Launch Order: `cmdr-659-661 — SegmentMap runtime representation, labeled persistence, versioned store`

Commanders start cold. Read this whole order, then `gh issue view 661` for the full build spec (it embeds the confirmed spec §1 hybrid, verbatim). This order is the wrapper: latitude, pre-rulings, workspace, inherited context.

## Mission
Build issue **#661** (epic #659, Build 1, manifest id `B`): the SegmentMap module — flat-numpy runtime representation + label-safe versioned persistence + the versioned store, **exactly the design-it-twice hybrid the spec already ruled** (CALLER runtime / FLEX identity+persistence / MINIMAL lifecycle). **The interface is frozen — do NOT re-run design-it-twice; do NOT re-litigate the hybrid.** Build 1 implements the **cold/historical derivation path only**; the seeded/supersede branch ships with Build 3 (interface unchanged now). Deliverable: the module + its store + the unit tests named in the issue's Acceptance. This is the substrate every downstream consumer (derivation C/#662, the join, the MC sim) reads — get the hot path and the label-stability guarantee right.

**Scope boundary (from the issue):** the derivation *logic* (applying thresholds to real telemetry) is issue C/#662, NOT this issue. You build the representation, the persistence, the store, and the `reclassify_severity` seam — fed by a severity mixture consumed behind a Protocol. No grip coupling. No live seeding.

## Prior-Wave Verdicts (pasted)
None — this is Wave 0, the first wave. No prior-wave outputs to inherit. You consume existing landed substrate only: #625 `src/physics/segment_classifier.py`, #638 `src/physics/layer2/mixture_stability.py` (the validated class vocabulary Build 1 consumes as-is).

## Pre-Rulings
- decision:frozen-interface — the three-way hybrid in the issue is the ruled design; build it as specified, no alternative generation. If you find a concrete contradiction that makes the ruled shape unbuildable, STOP and float to the Admiral — do not silently redesign.
  @grade: settled/human · leans this-whole-issue
- decision:build1-cold-path-only — implement the cold/historical write path; the deep write entry point carries the full cold/seeded/superseded branch in its *interface signature*, but only the cold branch is implemented now (per review S3). Seeded/supersede = Build 3.
  @grade: settled/human
- decision:build1-consumes-638-vocabulary — consume the existing validated #638 class vocabulary; do NOT refit the per-era Student-t mixture or run the F12 gate here (that's backfill).
  @grade: settled/human
- decision:lowest-dimensionality — dormant schema attributes (sub-phases, adjacency, direction) are marks-only / computed-not-persisted per the issue; reserve them in signatures, do NOT build backing stores.
  @grade: settled/human
- decision:severity-mixture-behind-protocol — the severity mixture is a fitted input consumed behind a Protocol so a future Student-t swap never touches SegmentMap. Do not hard-bind a concrete mixture class.
  @grade: settled/human

## Honest-Null Clause
A measured negative on any sub-question is a complete, successful deliverable — report it with the same rigor as a win (owner no-kill ruling governs the whole epic). This issue is mostly construction, but if a ruled property proves unachievable, that finding *is* the deliverable.

## Inherited Latitude
You may exercise, logged in your return report: bounded fix-now triage within this issue's scope, follow-on debt-issue *proposals* (Admiral files them), and your own implementation/test decisions inside the frozen interface. You must **float to the Admiral** (return-and-query): any scope change (adding/dropping/re-scoping the issue), any architecture/boundary decision that crosses data↔physics↔evo, any contradiction that would require changing the ruled hybrid, and anything outside this list. Merge is the Admiral's — open the PR, do not merge. Model tier for this dispatch is **Opus** (load-bearing interface).

## File Ownership
Your working-notes file this wave: `.agent-work/epic-659/notes-661.md` (sole writer). Do NOT name it `findings-*` (the Write tool refuses that basename). Do NOT commit any `.agent-work/` path on your mission branch — return your lessons-delta and feedback entry in the closeout report; the Admiral applies them centrally.

## Workspace
Absolute worktree (provisioned for you): **`C:/Programs/f1brainz-wt/epic659-661`** · branch `epic659/661-segmentmap` · base commit `f404d2cb` (current local main, 7 commits ahead of origin/main — this is correct, the epic-spawning commits are local-only).
Created with: `git worktree add C:/Programs/f1brainz-wt/epic659-661 -b epic659/661-segmentmap f404d2cb`
**First step, before any git operation:** run `py C:/Users/fredc/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here C:/Programs/f1brainz-wt/epic659-661` — must exit 0. Paste its output into your return report.
PR integration is **server-side merge** (the Admiral merges on GitHub; do not local-merge into your worktree).

## Inherited Context (lessons + invariants — paste, not pointer)
- **Python is `py`** (launcher), not `python`. Tests: `py -m pytest tests/...`.
- **Editable-install .pth worktree trap (project, critical):** ad-hoc/bespoke scripts run from a worktree silently import the **MAIN** repo `src/` via the global editable `.pth`, NOT your worktree's `src/`. `pytest` is safe (uses conftest/rootdir). Any bespoke script you write in the worktree must put the worktree `src/` first on `sys.path` or you'll test the wrong code. Prefer pytest-driven verification.
- **Crews are Agent-tool subagents, not a CLI binary** (`run_crew.py` expects a `claude --role` binary that doesn't exist here). If you spin crew, dispatch implementer/reviewer via the **Agent tool** and record attempts via `run_crew.py`'s pure registry functions; `recover_crews` before each dispatch.
- **Never idle on a single long watcher** — it gets harness-reaped, stranding the deliverable. Use bounded in-turn polls (<10 min each) or `Start-Process -WindowStyle Hidden` for genuinely long jobs; verify liveness via PowerShell `Get-Process` CPU, not git-bash `ps`. Write your result artifact and post your verdict **before** going idle.
- **Simplification limits:** run `py -m src.utils.simplification_limits` on touched paths (strict) before declaring done; plan file splits if approaching limits.
- **DB-only analysis:** no FastF1/Jolpica/live calls from any analysis/store code — SQLite is the single source. (This issue is representation/store, unlikely to touch data ingestion, but the invariant holds.)
- **Data/physics/evo boundaries:** this module lives in `src/physics/`. Do not couple physics to evo. Crossing a region boundary requires a floated architecture decision.

## Data Locations (untracked inputs — NOT in your worktree)
- 2023 DB: `C:/Programs/f1Brainz/data/f1_data_2023.db` (16MB, main checkout only). This issue is representation/store and should not need real telemetry, but if a test needs a fixture, prefer a synthetic/committed fixture over the real DB.
- #625 substrate: `src/physics/segment_classifier.py` · #638 F12: `src/physics/layer2/mixture_stability.py` · estimate-store pattern precedent: `src/physics/layer2/estimate_store.py`, `estimate_batch.py`.

## Budget
- **Model tier (required): Opus.** Load-bearing interface; subtle numpy hot-path + label-stability correctness.
- Compute/time: this is a build+unit-test issue, no long compute. Keep to bounded in-turn work.

## Stop Conditions
Stop and return when: scope exceeded; a decision outside inherited latitude is needed; the ruled hybrid proves contradictory/unbuildable; or you need context this order doesn't cover and can't safely proceed. Return-and-query the Admiral (it answers and continues you). Asking up is always sanctioned.

## Return Shape
Verdict (built / measured-null / blocked) + evidence (test run output, the four Acceptance test areas: searchsorted hot path incl. wrap+out-of-range, load-boundary round-trip, label-stability under simulated class reorder, read miss-contracts) + `simplification_limits` result + map impact (new module/seam for the Cartographer) + triage candidates (debt proposals for the Admiral to file) + workflow-feedback + your `verify_worktree_isolation.py --here` matched-path output. Open the PR (`gh pr create -F <tempfile>` — never a heredoc/here-string body on Windows) and post the verdict; the Admiral gates checks + reviews + merges. Return thin (verdict + evidence + artifact path), write fat (detail in `notes-661.md`). Deliver the artifact and post the verdict **before** going idle.
