# Archived gold-lifecycle design docs (#440 / #370) — distilled 2026-06-19

Spent design + retrospective for the gold promotion lifecycle. The work landed
(#440: `params/gold/gold_provenance.json`, `scripts/promote_gold.py`,
`gold_candidate`/`gold_archive` gitignored, the `pipeline_validation` provenance
gate). Durable invariants were distilled into the architecture graph; originals
kept here as history. Do not treat as current truth — follow the pointers.

| Archived doc | Status | Durable idea → where it now lives |
|---|---|---|
| `2026-06-10-gold-lifecycle-design.md` | landed (#440) | Slug-free single-provenance gold, 3 physical locations, `gold_provenance.json` + `eval_year ∉ train_years`, atomic promote, no-extra-files validation gate → `decision:gold_lifecycle_provenance` + `packets/evo_predictor.md` (Decision anchors); operational how-to in `docs/evo/analysis_refresh.md` |
| `2026-06-10-gold-lifecycle-p1.md` | landed (#440) | The P1 implementation plan (layout + provenance + validation gate + migration) for the above |
| `gold_artifact_storage_review.md` | retrospective (#370) | Step-back storage review; its primitive (the #371 per-event module record) landed, and the fusion-experiment consumers it unblocks are tracked by #373/#374. No open recommendation left unissued. |
