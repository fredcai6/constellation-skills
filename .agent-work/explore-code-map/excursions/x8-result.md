# x8 result — where the why lives: falsifying "comments suffice" against f1Brainz's real map

**Type:** research (falsification pass) · **Date:** 2026-08-05
**Evidence:** `.agent-work/explore-code-map/evidence/x8/classification.csv` (67 record-groups, 454 items),
`.agent-work/explore-code-map/evidence/x8/known-false-census.csv` (58 records)
**Corpus:** `C:\Programs\f1Brainz\docs\architecture\` — 36 files, 7,793 lines, read in full. **READ-ONLY** (no f1Brainz file was modified).

---

## Verdict

**The human is substantially right, and one thing proves him wrong.**

Right: 89% of the map's why-bearing content has a natural code home, and the known-false
record is even better behaved than the rest — **49 of 58 known-false records (84%) sit on
code that still exists**, so a comment on the surviving implementation is a genuinely
adequate home for them. His instinct that "known-false is a small enough case for comments"
is correct as stated.

Wrong, and this is the load-bearing counter-example: **a known-false record's anchor is
exactly the thing most likely to have been deleted.** The record exists *because* the
approach failed, and a failed approach gets removed. Four of the nine unanchorable
known-false records are unanchorable for precisely this reason, and the sharpest one is
`decision:smoother_rounds_braking_knee`'s P1b entry — a braking time-kernel that was
built, validated on synthetic data, then superseded. Its source file
`src/physics/braking_kernel.py` **no longer exists** (only a stale `.pyc` in `__pycache__`
survives), and the record states its own purpose in one sentence:

> "Preserved here because it is the obvious thing to re-propose ('fit the integral the
> smoother preserves') and it does not work."

There is no file in `src/` to put that comment in. Nothing in the repo mentions the P1b
kernel attempt — the nearest thing, `src/preprocessing/trajectory/_hp_search.py:39`,
records that the smoother rounds the decel knee but says nothing about the rescue that was
tried and failed. So the comment-only design would have lost exactly the record whose
stated job is to stop the next agent re-proposing a dead idea. That is a real
falsification, and it generalizes: **the failure mode of comments-for-known-false is
correlated with the record being worth keeping.**

Two smaller classes also resist, described in full below: **artifact-staleness** records
(the code is right, a stored `.db`/`.json` is wrong — there is no wrong line to comment on)
and **freeze-before-look provenance** (the load-bearing fact is a commit ordering; a
comment claiming "I was written first" is unverifiable and survives a re-tune).

Everything else the excursion looked for did *not* prove him wrong. In particular, the
`decisions/` files are far more decomposable than their reputation suggests — see §4.

---

## 1. Coverage

Every why-bearing item in the corpus was read, not sampled.

| Source | Files | What was covered |
|---|---|---|
| `decisions/` | **16** (the brief and x1 both say 15 — there are 16, 1,405 lines) | every file end to end |
| `packets/` | 16 | every judgment section: Responsibility, Known Limits, Notes, Trust limitations, Open Questions, Key Constraints, Decision anchors, Removed-in, Retro notes, Evidence-of-dead |
| `overlays/` | 2 | 18 nodes (10 purpose, 6 constraint, 2 claim) + 46 relationships |
| `index.md` | 1 | 48 node `purpose:` fields + all 27 Open Structural Questions rows |
| `reference/` | 1 | 38-row unit table + 4 rationale sections |
| `MAP_BUILD.md` | 1 | all 5 sections |

**454 why-bearing items classified**, grouped into 67 record-groups in the CSV. Anchor
existence was verified against `C:\Programs\f1Brainz\src\` and `scripts\` by direct file
checks and `git log --diff-filter=D`, not by reading the map's own claims.

---

## 2. The bucket split

| Bucket | Items | Share |
|---|---|---|
| **(a) single-anchor** — one function/class/module; lives as its docstring or comment | 295 | **65%** |
| **(b) multi-anchor** — a small named set; grouped or duplicated comments workable | 108 | **24%** |
| **(c) genuinely unanchorable** — no code location is its natural home | **40** | **8.8%** |
| **(c-soft)** — technically hostable but the host degrades badly (dense measurement tables) | 11 | 2.4% |

So **89% of the map's why-content has a code home**, and the 11% residue splits into a hard
9% and a soft 2%.

Two observations that matter more than the ratio:

**The map is already partly a copy of the code.** `src/physics/layer2/decoupled_longitudinal.py`'s
module docstring carries `decision:decoupled_1d_longitudinal`'s Decision and Rationale
sections in near-identical structure — the energy/force state identity, why the brake-onset
knee is a benign kink, the M3/M7 mechanisms. The decision file's genuinely *additional*
content is the rejected alternatives and the HONEST-NULL tables, not the design rationale.
That is direct evidence for the human's position: where the anchor exists, this repo's
authors already put the why in the code, unprompted.

**The pattern already works in-tree where an anchor exists.** `src/physics/layer2/damage_batch.py:55`
carries the comment *"the spec's per-stint c_down robustness variant was never built"* — a
known-false record living happily as a code comment. Its two siblings from the same audit
(ellipse-u, self-vs-global normalization comparison) have no code at all and survive only
in `packets/physics.md`.

---

## 3. Full bucket-(c) list (all 40 hard items)

### 3a. Anchor code was deleted — 9 items

The record survives; the code it is about does not. **Verified by file check and git log.**

1. **P1b braking time-kernel** (`smoother-rounds-braking-knee.md`). `src/physics/braking_kernel.py` + `braking_kernel_experiment.py` deleted; only `.pyc` remains. *The counter-example.*
2–4. **The retired inline ideal-lap sim** — 3 items in `c1-driver-utilization-design.md` (design choice 4, its Structural Consequence, and the "a second inline scalar sim" rejection). `scripts/ideal_lap_compare.py`, `scripts/ideal_vs_actual.py`, `scripts/ver_monza_kde.py` all deleted.
5. **`regime_rollup.py` disposition** (`index.md` OSQ) — distance-share rollup superseded by #664's time-share. Module **deleted at commit `b9248aef`**. The map row still reads `removal-PROPOSED (FOR-OWNER)`, so this row is *also* live map drift.
6. **`soft_class_membership` bridge disposition** (same OSQ row) — method removed at `b9248aef`.
7–8. **"Removed in #448"** (`preprocessing.md`, 2 bullets naming 12 deleted modules + 2 retired docs): windowed lineage (`windowed_estimator.py`, `windowed_config.py`, `windowed_solver/`, `trajectory_models.py`, `consensus_stitcher.py`) and orphaned utils (`coordinate_transform.py`, `curvature.py`, `spline_basis.py`, `measurement_models.py`, `loess_bootstrap.py`, `robust_reweighter.py`, `irls_reweighter.py`). Instruction: *"do not expect them on disk and do not re-add them."*
9. **"Removed in Task 10"** — `src/preprocessing/trajectory/artifact.py` deleted, zero live consumers at deletion.

### 3b. Artifact staleness — the code is right, the data is wrong — 5 items

No code line is incorrect, so there is no line to comment on; and the fact is time-varying
with no signal that would prompt a comment update when someone re-batches.

10. `physics_estimates.db` / `race_stint_estimates.db` **STALE** vs the wired burn rate (#577) — `packets/physics.md` Known Limits and an OSQ row.
11. `data/physics_fits.db` is the pre-#548/#495 baseline (built 2026-06-23, `engine_sha 6a051ff`), still holding 18 `error` rows the current code resolves (#559).
12. `compound_prior` 2022 gold artifact still uses the pre-#410 per-season path while 2023/24/25 are pooled multi-season fits.
13. `rt_comparison_*` committed artifacts: paths align to 2018–2024 but metric payloads may reuse an older run when live regen hits a singular matrix.
14. FP `estimate_store` backfill: the constructor-name resolution mismatch between `estimate_batch` (live FastF1 `TeamName`) and `session_cumulative_track_laps` (stored `session_classifications.team`) "only bites the real #646 backfill at scale."

### 3c. Freeze-before-look provenance — 3 items

The constants anchor fine. The load-bearing claim is a **commit ordering**, which git
proves and a comment cannot: an assertion "I was written before the model existed" is
copy-paste-survivable into a re-tuned file, which is exactly the failure the discipline exists to prevent.

15. `weekend-state-f6-gate-rubric.md` — `gate_spec.py` authored and committed at g1 *before* any of the four layers existed.
16. Same file — "changing `gate_spec.py`'s constants invalidates that comparison and requires a fresh freeze-before-look cycle."
17. `grip-estimate-record-session-level-pk.md` — "frozen at #663 g-planning, **before the grip fit was run**."

### 3d. Forward roadmap for code that does not exist yet — 9 items

`decisions/builds-2-3-forward-roadmap.md` is the one whole file that is bucket (c) almost
end to end, and it says why in its own preamble: this program "has been built and orphaned
five times because the forward map stopped being read," and its interfaces "otherwise live
only in the #659 issue body (which closes) and the exploration archive."

18–19. The anti-orphan preamble and the allocation-not-gating governing rule — content *about the record's own discoverability*, not about any code.
20–24. Build 2 race-reference interfaces and the carried P6 variant queue (flip the stint-position component; multiplicative rather than additive gate; gap-behind signal; SC/VSC exclusion; the untested kinematic-headroom leg) — measured-and-parked variants with no implementation.
25–26. Build 3 live-loop interfaces — the seeded/supersede `SegmentMap` lifecycle branch is `NotImplementedError` today; the feature-family fusion-choir seam is built but dormant-by-default.

### 3e. Claims above every file in the repo — 3 items

27–29. The three parentless purpose nodes in `overlays/purposes.yml`: `purpose:race_prediction`, `purpose:physics_estimation`, `purpose:data_ingestion`. These say what the *system* is for. No file owns them; a repo-root README is a document, not a code anchor. (The 7 child capability nodes are bucket (b) — e.g. the C→D→E→G→H→PANEL chain plausibly groups on `pilot/pipeline.py`'s `REQUIRED_SLOTS`.)

### 3f. Content about docs, the map itself, or prior map claims — 11 items

30. Parallel canonical schema docs (`docs/report_schemas/gold_module_training_cycle.md` vs `docs/evo/gold_module_training_cycle_report_schema.md` duplicate each other).
31. `purposes.yml` uses the deprecated `purpose:`/`serves` ontology; migration to `capability:`/`supports` is owed.
32. Stale code snippet inside `src/compound_prior/WEATHER_REGRESSION_2022.md` (markdown only, not a live import).
33. `src/physics/diagnostics/` has no `struct:` component node — a statement about the map's node structure.
34. Evo packet module-coverage tail — a *documentation-coverage policy* over ~15 helper modules ("add prose only if a helper becomes a boundary surface").
35. `#325` lambda_ridge spike "deliberately deferred until the v6 metrics stabilized" — a record of a decision *not to work on something*.
36. `packets/reporting.md`: retraction of the earlier map claim that the whole package was a dead path.
37. `packets/publishing.md`: retraction — the `publishing → simulation`/`reporting` edges "were removed from the map as fabricated."
38. `packets/physics.md`: "spec robustness scaffolding (ellipse-u, self-vs-global normalization comparison) was **never built**" — the gap has no code by definition.
39–40. `MAP_BUILD.md`: the deliberately out-of-scope checks, and why the bundled Cartographer builder is not vendored (it expects a packet format this repo does not use).

### 3g. The soft-(c) 11 — measurement tables

Not listed as hard (c) because a docstring *can* hold a table; listed because the host
degrades. `decoupled-1d-longitudinal.md` carries 6 tables (~95 lines: a 5×3 HP sweep grid,
a before/after sample-count table, per-view σ-shift grids); `smoother-rounds-braking-knee.md`
carries 2; `packets/physics.md` carries the compound-damage 4-confound audit, the #511
tyre-supplant characterization, and the damage-screening verdict. Their *verdict* sentences
("do NOT wire; keep `prepare_coast_samples` incumbent") anchor cleanly as comments. Their
value is that a future agent proposing "just tighten the throttle HP" reads 15 swept numbers
instead of re-running the sweep — and that is 20 lines of tabular data per instance,
eight instances, landing in module docstrings that are already long.

---

## 4. The 15 (really 16) decision files: decomposable or not?

Decomposable = anchored comments + git history reproduce it with nothing important lost.

| File | Verdict | Irreducible remainder |
|---|---|---|
| `two-cycle-external-anchor-design.md` | **Fully decomposable** | none — every one of the four invariants names exactly one function (`emit_accel_obs`, `refine_trajectory`) |
| `ideal-lap-sim-two-sided-evaluator.md` | **Fully decomposable** | none — all 5 fired review triggers name one function each |
| `cross-view-covariance-sparse-representation.md` | **Fully decomposable** | none — the dense-matrix rejection anchors on `_CROSS_VIEW_COVARIANCE_KEYS` |
| `dual-cda-fusion-honest-total-sigma.md` | **Fully decomposable** | none — the record names its own single call site and warns a "simplifier" would regress it |
| `pooled-sigma-shared-systematic-floor.md` | **Fully decomposable** | none |
| `regime-readiness-rubric.md` | **Fully decomposable** | none — thresholds are already named constants awaiting rationale comments |
| `traction-own-measured-frontier.md` | **Fully decomposable** | none — "do not reintroduce a `k × lateral` cap" is a one-liner on the envelope |
| `burn-rate-calibration-design.md` | **Fully decomposable** | none — the rejected fitted knob (`throttle_response_fraction`) is still in-tree, off by default |
| `gold-lifecycle-provenance.md` | Decomposable (multi-anchor) | none — 3 dirs + `promote_gold.py` + the provenance gate is a small named set |
| `tyre-age-g-track-design.md` | Decomposable (multi-anchor) | none, but needs comments at **both** ends: "do not substitute `pooling.py` here" must be readable from `pooling.py` too |
| `c1-driver-utilization-design.md` | **Mostly** | **3 items** — the retired inline-sim record (3 deleted scripts) |
| `decoupled-1d-longitudinal.md` | **Mostly** | **6 soft** — the #523/#546 HONEST-NULL evidence tables |
| `smoother-rounds-braking-knee.md` | **Mostly** | **1 hard + 2 soft** — the P1b kernel record (deleted anchor) and the #505 tables |
| `weekend-state-f6-gate-rubric.md` | **Mostly** | **2** — freeze-before-look provenance |
| `grip-estimate-record-session-level-pk.md` | **Mostly** | **1** — freeze-before-look provenance |
| `builds-2-3-forward-roadmap.md` | **Not decomposable** | **9 of 12** — a forward map for code that does not exist |

**Ten of sixteen decompose completely. Five decompose with a small named remainder. One does not.**
That is a stronger result for the human's position than the folk view of "ADRs are irreducible."

The one systematic thing lost across all sixteen: the **decision-to-code index**. Each file
carries a `Structural anchors:` line and each overlay relationship carries an `evidence:`
file list. Scattered as comments, "which files does this decision govern?" becomes a grep
rather than a lookup — a navigation loss, not a content loss, and comment-side markers
(Doxygen `\defgroup`-style, or just a stable decision id in each comment) recover it.

---

## 5. Known-false census

**58 records** found (30 `Rejected Alternatives` bullets across `decisions/` plus 28 embedded
negative results, retractions, and measured nulls in packets and `index.md`). Full census in
`evidence/x8/known-false-census.csv`.

| Anchor status | Records | Comment-viable |
|---|---|---|
| Anchor code exists today | **49 (84%)** | yes |
| Anchor code deleted | 6 | **no** |
| Anchor never existed (a gap, not a build) | 1 | partial |
| No anchor by nature (retraction of a prior map claim) | 2 | **no** |

By kind: 15 rejected-never-built, 12 measured-null, 8 proven-wrong, and a long tail of
retirements, retractions, and disclosed-unfitted placeholders.

**The size question the human asked, answered directly:** 58 records over a 7,793-line map
and a 443-file codebase — roughly one known-false record per 8 source files. That is small.
And 84% of them anchor on live code, because the standard shape of a rejected alternative
is *"we chose A over B"* — and A is implemented, so A's function is B's obituary. The dense
N×N covariance matrix, the three-variance-component likelihood, the row-level bootstrap, the
season-average frontier, the `0.30 × lateral` traction cap: all of these anchor cleanly on
the chosen implementation.

**Where it breaks** is the other shape: *"we built B, measured it, and removed it."* Then
the obituary outlives the corpse. That is KF08 (inline sim), KF24 (P1b kernel), KF53/54
(the #448 and Task-10 deletions), KF57/58 (`regime_rollup`, `soft_class_membership`).
Six records, one mechanism.

---

## 6. Scoped nulls

- **One repository.** f1Brainz is a research-heavy scientific-computing codebase whose map is unusually decision-dense (16 decision files, 58 known-false records, an epic-driven issue culture that produces HONEST-NULL verdicts as first-class artifacts). A verdict here does not generalize to every codebase's why-content, and probably over-states the (c) fraction for ordinary application code (which has fewer measured nulls) while under-stating it for codebases with heavy cross-cutting policy.
- **Not examined:** any other repository's curated map; whether comments actually *get read* at the moment they matter (a behavioral question this excursion cannot answer from repo content); whether the 89% that *can* live as comments *should* — that is a retrieval and maintenance question, not an anchoring one, and it is outside this excursion's named question.
- **Not measured:** the cost of the (b) bucket. 108 items need a comment in more than one place, and nothing here checked whether duplicated comments in this repo stay in sync. `claim:lateral_car_prior_boundary_conversion` spans two functions, two conventions, a store, and a migration script.
- **The (a)/(b) boundary is a judgment call.** A record naming one function plus one caller was read as (b). Shifting that line moves roughly 30 items either way; it does not move the (c) count, which is what the question turns on.
- **The soft-(c) 11 are contestable.** Someone who considers a 20-line table in a docstring acceptable should read the hard (c) count as **40 of 454 (8.8%)** and stop there.
- **One incidental map-drift finding, reported not acted on:** `index.md`'s Open Structural Questions row for `regime_rollup.py` still says `removal-PROPOSED (FOR-OWNER)`, but the module was removed at commit `b9248aef` ("chore(#671): remove superseded regime_rollup + unwired soft_class_membership bridge (#718)"). f1Brainz was not modified.
