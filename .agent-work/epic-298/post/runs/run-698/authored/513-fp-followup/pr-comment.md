**Phase-4 checkpoint expansion (Admiral-directed) — 2 new commits + a running illustrative demo.**

- `a83d843a` — in-flight cleanup: **tc3** `backfill_estimate_store.py` now threads `session_type`+`db_path` into `estimate_session` (the D9-canonical writer #646 uses — unblocks a clean re-pop); **tc1** `FpLapLatent.track_status` → `Optional[str]`/None. Both RED-first.
- `807556b7` — real `fp_gate_real_extractor.py` (reviewer-APPROVED; frozen harness untouched) feeding a **thin ILLUSTRATIVE-NOT-EVIDENTIAL demo** (4 weekends, 4 LOWO folds) — proof the pipeline runs end-to-end on real telemetry, **NOT the F10 verdict**.
- Harness freeze **RE-STAMPED** before any real number: `HARNESS_FREEZE_HASH=349216857e6c09d9` @ `74bfc6aa`. G6 min-max normalization + L2 shrinkage ruled **FAITHFUL** (arm-fairness fix, symmetric, makes the comparison honest not the PASS easier) — see verdict.
- **tc2** (constructor-resolution seam) DEFERRED to #646 with reason (naming-normalization reconcile, only bites the real backfill). **fuel_sigma** per-lap-width → **#652** (why SECONDARY is CONFOUNDED). Parc-fermé = owner-ratified reserved slot.

Full detail: `.agent-work/epic-601/wave8-513-verdict.md` (Phase-4 checkpoint expansion section).
