# Reconcile Handoff — fold issue #373 additions into the architecture map

You are a fresh crew doing a BOUNDED architecture-map reconciliation (constellation-cartographer
discipline: reflect what now EXISTS; do not redesign). Repo: f1Brainz (Windows; `py` not `python`).
cwd = worktree root (`C:\Programs\f1Brainz\.claude\worktrees\agent-a8cafc9a5b22bcd57`). Set
`PYTHONIOENCODING=utf-8` for any python. The single source of truth is `docs/architecture/index.md`
and its packets under `docs/architecture/packets/`.

## What changed on this branch (commits 45e9e8a, e22c090; G1 9f52e75 already in)
ADDITIVE only; NO production behaviour changed. New/changed structural elements:

1. `src/evo_predictor/fusion.py` — NEW pure function `fuse_module_fields_correlated` (opt-in
   correlated-covariance fusion: per-entity GLS with a kxk cross-MODULE error correlation R;
   `Σ_i = D_i R D_i`). Production `fuse_module_fields_ordered` UNCHANGED. The new function is
   OFFLINE/measurement-only — no production or runtime call-site uses it.
2. `src/evo_predictor/fusion_training/_correlation.py` — NEW module:
   `estimate_cross_module_correlation` (R from standardized residuals, pooled over events, shrink
   toward I) + `mask_correlation_to_block` (cheap-B constructor↔driver block mask).
3. `scripts/fusion_replay/` — NEW offline fusion-replay harness package (numpy-only): `records.py`,
   `baseline.py`, `scoring.py`, `variants.py`, `generate_records.py`, `scorecard.py`. Loads #371
   per-event module records, reproduces production fusion, scores baseline vs correlated variants.
   Reads the SQLite DB read-only for the constructor↔driver mapping. Generated records are
   gitignored artifacts.
4. `docs/evo/fusion_rework_findings.md` — NEW findings doc (the #373 measurement + verdict). It is a
   findings artifact, not architecture.

## Task
Update ONLY the architecture map so it reflects the above as current structure. Specifically:
- In `docs/architecture/packets/evo_predictor.md`: under the `fusion.py` section, note the new
  opt-in `fuse_module_fields_correlated` (offline/measurement variant; production default unchanged).
  Under `fusion_training/`, add `_correlation.py` to the file list with a one-line purpose.
- Decide (cartographer judgement) whether the `scripts/fusion_replay/` harness warrants a short
  mention. If the index/packets track `scripts/` tooling (check how `run_static_hierarchical_fusion_training.py`
  is listed), add a one-line entry for the fusion-replay harness in the same style. If scripts are
  not generally mapped, do NOT invent a new section — note in your result that it was intentionally
  left out and why.
- If `docs/architecture/index.md` carries a node/path list that includes `src/evo_predictor/fusion.py`
  or `fusion_training/`, make the minimal consistent update there too.

## Hard constraints
- ADDITIVE doc edits only; reflect reality, do not redesign or re-architect.
- Do NOT touch `docs/evo/prediction_ceiling_and_priorities.md` or any non-architecture doc.
- Do NOT touch code. Do NOT touch `docs/evo/fusion_rework_findings.md`.
- Keep the existing doc voice/format. No emojis.
- Note explicitly that the correlated variant is OFFLINE-only (no production call-site) so the map
  doesn't imply a behaviour change.

## Close criteria
- `git diff` shows only edits under `docs/architecture/`.
- The evo_predictor packet mentions `fuse_module_fields_correlated` (offline) and `_correlation.py`.
- Your result states whether the fusion_replay harness was added to the map or intentionally omitted,
  with the reason.

## Return Format
Return a short result: which files you edited, the exact lines/sections added (quote them), the
harness-mention decision + rationale, and confirmation no code or non-architecture docs were touched.
