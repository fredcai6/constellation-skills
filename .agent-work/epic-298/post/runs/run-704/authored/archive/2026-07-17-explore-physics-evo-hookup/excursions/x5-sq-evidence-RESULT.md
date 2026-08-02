# x5 — Sprint SQ/S evidence verification: RESULT

## Verdict: **USED** (for SQ; S is used too, but for a different feature — see caveat)

`docs/evo/quali_evidence_findings.md` §B's fear — "if the preprocessor currently
feeds only FP1 on sprint weekends, that is the single highest-value fix" — is
**not true of the current live path on `main`**. SQ is already wired in as the
primary short-run/quali-sim evidence on sprint weekends, and feeds the live
`driver_quali_power_from_race_weekend` module. S (sprint race) is also
consumed, but as long-run pace evidence, not quali-sim evidence — it only
touches quali indirectly via a `min()` anchor blend.

This is a **code-truth finding, not a historical one**: whatever prompted the
doc's hedge ("reportedly feeds only FP1") is either already fixed, or was
never true of this code. No git-blame/history dig was done to date it — out
of budget for this excursion.

---

## The trace

### 1. Session-type selection: SQ and S are in scope, not dropped

`src/utils/constants.py:307-333` — `get_practice_session_types(year, gp_name)`:
```
SPRINT_PRACTICE_SESSIONS: List[str] = ["FP1", "SQ", "S"]   # line 297
LEGACY_SPRINT_PRACTICE_SESSIONS: List[str] = ["FP1", "FP2"]  # line 298, 2021 only
```
For a modern (2022+) sprint weekend this returns `["FP1", "SQ", "S"]` — never
`["FP1"]` alone. `LEGACY_SPRINT_YEARS = frozenset({2021})` (constants.py:295),
so every sprint weekend from 2022 onward (including all of 2025/2026) takes
this branch.

This list is `practice_session_types`, threaded through
`src/evo_predictor/data_adapter/_build.py`:
- `_resolve_session_availability` (line 150) calls `get_practice_session_types`
  when no override is given (the default, live-prediction case).
- `build_race_features` (line 545) assigns `practice_session_types =
  practice_session_types_pre`.
- `_resolve_practice_and_context` (line 296-350) passes it straight into
  `compute_practice_features(db, year, round_num, practice_session_types, ...)`
  (line 328) — the practice_preprocessor entry point.

So on a sprint weekend, the practice preprocessor is invoked with
`session_types=["FP1","SQ","S"]`, not `["FP1"]`.

### 2. Practice preprocessor: SQ → quali-sim bucket, S → long-run bucket

`src/evo_predictor/practice_preprocessor/_lap_pipeline.py:452-474`,
`_split_run_buckets`:
```python
session_set = {str(value).upper() for value in session_types}
if "S" in session_set and "SQ" in session_set:
    short_sessions = {name for name in ("FP1", "SQ") if name in session_set}
    long_sessions = {"S"}
    long_run = clean_laps[clean_laps["session_type"].isin(long_sessions)].copy()
    short_run = clean_laps[clean_laps["session_type"].isin(short_sessions)].copy()
    return long_run, short_run
```
This is a hard-coded sprint-aware branch: when both `S` and `SQ` are present
in `session_types`, laps are split by session identity, not by stint
heuristics. **FP1 + SQ laps become the "quali-sim" (short-run) bucket; S laps
become the "long-run" bucket.**

`practice_preprocessor/_compute.py:169-209` (`compute_practice_features`)
feeds `structural_quali_sim` (the short-run bucket) through
`_apply_session_best_pace_filter` into `quali_sim`, then computes the `qs_*`
fields (`qs_raw`, `qs_adj`, `qs_rep_raw`, `qs_rep_adj`, lines 246-306) from it.
On a sprint weekend this bucket is FP1+SQ laps — **SQ lap times directly
populate `qs_theoretical_best`, `qs_expected_time`, `qs_variation`,
`qs_best_adj`, etc.** (field names at `_compute.py:364-388`,
`DriverFeatures` fields at `models/_features.py:44-67`).

The long-run bucket (S laps on a sprint weekend) populates the parallel
`lr_*` fields the same way.

### 3. `allfp_best_raw` (the anchor input): min(qs, lr) — both sprint buckets included

`practice_preprocessor/_lap_pipeline.py:897,978` —
`allfp_best = _allfp_best_raw(f.lr_theoretical_best, f.qs_theoretical_best)`,
i.e. `min(lr_theoretical_best_raw, qs_theoretical_best_raw)`. Documented again
at `models/_features.py:134-141`.

`sampled_runtime.py:478-498` (`_anchor_quali_field`, called only for
`DRIVER_QUALI_POWER_FROM_RACE_WEEKEND` at line 466):
```python
# DriverFeatures.allfp_best_raw is min(qs_best_raw, lr_best_raw) in raw
# seconds populated by the practice preprocessor; missing → np.nan.
driver_raw = {d.driver_id: d.allfp_best_raw for d in features.drivers}
...
blended_pi = blend_quali_pace_anchor(result.pi, anchor, anchor_cfg.alpha)
```
On a sprint weekend both components of this min are sprint-session-sourced
(qs = FP1+SQ, lr = S), so the anchor is fully live-data-backed, not FP1-only.

### 4. The live quali NN module itself: SQ (via qs_*) in, S (via lr_*) not directly in

`src/evo_predictor/quali_power_adapter.py` — `DRIVER_QUALI_POWER_FEATURE_NAMES`
(lines 39-66) is exclusively `qs_*` and `short_run_*` fields (`qs_expected_adj`,
`qs_best_adj`, `qs_variation_adj`, `short_run_q20_adj` … `short_run_rep_spread_adj`,
`qs_sector_available`). These are all sourced from the short-run bucket, i.e.
**FP1+SQ on a sprint weekend** (per §2). This confirms SQ lap-time evidence
reaches the live `driver_quali_power_from_race_weekend` module's NN input
vector directly, every sprint weekend where SQ lap data exists.

S (sprint race) laps do **not** appear in this feature list — they only
reach the quali module indirectly through `allfp_best_raw`'s `min()` in the
anchor blend (§3), and in practice a full-race-distance S lap is virtually
always slower than an SQ lap, so `min()` picks `qs_best_raw` whenever SQ data
exists. S's main live consumer is presumably the long-run/race-pace side
(`lr_*` feeds a different module — out of scope for this excursion to trace
further).

### 5. `sq_pos` / `s_pos` (classification positions) — a separate, likely-dead path

`_assemble.py:194-202` (`_driver_session_positions`) and `_build_driver_features`
(line 236-238, 254-255) populate `DriverFeatures.sq_pos` / `.s_pos` directly
from the SQ/S classification dicts loaded in `_load_weekend_classifications`
(`_build.py:429-456`) — i.e. finishing positions, not lap times. These get
packed into `PackedRaceData` (`models/_pack.py:42-43`) and surfaced via
`get_form_features_stage2` (`_build.py:902-928`), which is labeled "for
pipeline stages 1–3" — CLAUDE.md's architecture notes flag the
24-parameter/Stage1-2-3/`scorer.py`/`ranker.py` path as **RETIRED, not used
by the live predictor**. I did not find any of the 12 live
`module_adapters/_registry.py` modules consuming `sq_pos`/`s_pos` — the live
quali module (`quali_power_adapter.py`) only reads `qs_*`/`short_run_*` (§4).
So this second SQ/S signal (classification position) looks unused by the live
path, but I did not exhaustively check all 6 `*_from_recent_history` modules
for it — flagging as a residual unknown rather than asserting DROPPED.

### 6. Real-data sanity check (2025 season, `data/f1_data_2025.db`)

`session_classifications` — sprint rounds are 2, 6, 13, 19, 21, 23, each with
`['FP1', 'Q', 'S', 'SQ']` (no FP2/FP3), confirming the modern-format session
set is present for every 2025 sprint weekend.

`lap_times` joined to `sessions` for round 2 (China sprint weekend):
```
FP1: 459 laps   Q: 314 laps   R: 1065 laps   S: 380 laps   SQ: 217 laps
```
Real per-lap sector data exists for both SQ (217 laps) and S (380 laps) —
there is data on disk for the preprocessor to consume, and per the trace
above, it does.

---

## Verdict detail

- **SQ on sprint weekends: USED**, as first-class quali-sim (`qs_*`) evidence
  feeding the live `driver_quali_power_from_race_weekend` NN module directly,
  and also feeding the `allfp_best_raw` anchor. This is exactly the fix
  `quali_evidence_findings.md` §B asked for (SQ→Q ≫ FP1→Q, ~8pp gap) — it
  appears to already exist on `main`.
- **S on sprint weekends: USED, but not as quali evidence** — it's the
  long-run bucket (`lr_*`), which is not in the live quali module's feature
  list. It reaches the quali anchor only via the `min(qs,lr)` in
  `allfp_best_raw`, where it's normally dominated by the faster SQ time. So
  S's *quali*-relevance (the doc's secondary signal, S→Q = 0.730) is at most
  weakly/indirectly present, not actively exploited as its own signal.
- **`sq_pos`/`s_pos` (classification-position path): likely unused by the live
  predictor** (feeds only the retired Stage1-2-3 packer, `get_form_features_stage2`), but not exhaustively verified against all 6
  recent-history modules.

## Where a fix would go (if the S→Q secondary signal is judged worth adding)

There isn't really a fix needed for SQ — it's already live. If someone wants
to also exploit S→Q (0.730, per the doc) as an explicit secondary quali
feature rather than relying on the incidental `min()` in `allfp_best_raw`,
the seam is:
- `quali_power_adapter.py:39-66` (`DRIVER_QUALI_POWER_FEATURE_NAMES`) — would
  need a new sprint-conditional feature sourced from `lr_*`/S separately from
  `qs_*`, plus a schema-version bump (`DRIVER_QUALI_POWER_FEATURE_SCHEMA_VERSION`,
  line 16) and retraining.
- Size: **S** (small) if it's just wiring one more field per §2's existing
  `lr_*` computation into the feature vector (the data's already computed);
  **M** if it also needs training/eval work to validate the module improves
  with it, given the small-n caveat (21 weekends) the doc itself flags.

## Scope note

This verdict covers the **live path on current `main`** only (per the brief's
scoped null). No check was made of historical gold bundles, and no git-blame
was run to determine when the SQ/S wiring in `_split_run_buckets` was added
relative to when the doc's fear was written — if useful, that's a fast
follow-up (`git log -p -- src/evo_predictor/practice_preprocessor/_lap_pipeline.py`
around `_split_run_buckets`).
