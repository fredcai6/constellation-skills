# Grading packet
You are grading five independent planning outputs against frozen ground truth.
## 1. Ground truth — the correct seam per task

Determined by the author reading f1Brainz at the pin, **before the runs**, and independently
re-verified by a cold critic against the same commit. Every path was located with
`git grep` / `git show` against `3541d292`.

### #690
**Primary seam: `src/physics/utilization/class_utilization_observable.py`**
Boundary counterpart: `src/physics/layer2/grip_store.py` (`get_grip_at`).

Evidence: `class_utilization_observable.py:122` is
`return float(math.hypot(float(mu), float(sigma)))` — the σ⁺ scale at issue. Line 77 imports
`get_grip_at` from `src.physics.layer2.grip_store`; line 188 consumes it. The change belongs
on the **utilization** side (how G is scaled into a per-class band), not in `grip_store`.

*2*: names `class_utilization_observable.py`. *1*: names only `grip_store.py`, or only
`src/physics/utilization/` without the file. *0*: neither.

### #688
**Seam: `src/physics/layer2/grip_baseline.py`** (`rain_flag_from_raw`).
Evidence: `git grep -ln rain_flag_from_raw 3541d292 -- src/*` returns exactly this file.

*2*: names `grip_baseline.py`. *1*: names `src/physics/layer2/` without the file. *0*: neither.

### #698 — scored on seam-finding ONLY
**Seam: `src/physics/fingerprint/store.py`**, with `src/physics/fingerprint/address.py`
(`CellAddress`) as the type the API must be tightened onto.
Evidence: `git grep -ln 'class DriverFingerprintStore' 3541d292` → `src/physics/fingerprint/store.py`;
`class CellAddress` → `src/physics/fingerprint/address.py`. Both unique at the pin.

Sub-concerns H2 (a script's `sys.path` guard) and H3 (gitignore) are **not scored** — score
only the component that owns the store API. Naming H2's script or `.gitignore` is neither
credit nor penalty, and does **not** count against the spurious-file budget.

*2*: names `store.py`. *1*: names `src/physics/fingerprint/` without the file, or only
`address.py`. *0*: neither.

### #716
**Ground truth: there is no seam in this repository.**
Evidence: `git ls-tree -r --name-only 3541d292 | grep -E '(run_crew|verify_agent_feedback)\.py'`
returns nothing; neither script exists in f1Brainz at the pin. `work_id` appears nowhere
under `src/` or `scripts/`.

Because no in-repo seam exists, this task is scored on the **§3 axis instead of §2** — a run
cannot name a correct f1Brainz file, because there is none.

### #704
**Seam: `src/physics/instrument_panel/replication.py`** (`_axis_means` L103,
`main_effect_margin_uncertainty` L408). Evidence: `git grep -n` at the pin returns both
definitions in that one file, and only there.

*2*: names `replication.py`. *1*: names `src/physics/instrument_panel/` without the file.
*0*: neither.

---

## 2. Scoring scale — seam identification

| Score | Meaning |
|---|---|
| **2** | Names the ground-truth owning file. No material miss. |
| **1** | Partial — names the owning component/directory but not the file; or the right file inside a materially spurious list; or only the far side of a cross-module boundary. |
| **0** | Wrong seam — neither the owning file nor its component. |
| **n/a** | Tasks with no in-repo seam; scored on §3 instead. |

Spurious-file tolerance: up to **4** extra plausible files does not reduce a 2. Beyond that,
or a claim centred on an unrelated component, drops to 1.

Score the claimed file list **as written**. Do not credit intent, and do not penalise a run
for naming files that a task's own text told it to consider.

## 3. Coverage axis

For any task scored `n/a` under §2:

| Value | Meaning |
|---|---|
| **ACKNOWLEDGED-MISS** | The run states the work is not in this repo, or that it cannot locate a seam here, explicitly. |
| **SILENT-CRAWL** | The run proposes an in-repo seam anyway without stating the gap. |
| **CONFUSED** | Neither — no locatable position taken. |

---


---

# The five claimed seams, verbatim

## Task #690 — claimed file list, in the plan's own words

```
**`src/physics/utilization/class_utilization_observable.py`** — the core. Add `class_grip_weights()` (delegates to `class_time_ledger` over `v_ideal`; optional sensitivity vector; validates finite/≥0/sums-to-1) and `allocate_grip_sigma(sigma_lap, weights)` (the linear comonotone split). `compute_class_utilization_observable` builds each band with its own `sigma_plus`; new `g_sigma_by_class` field on the dataclass; module docstring gains the units-and-grain rationale (lap-seconds × dimensionless share = class-seconds), the linear-vs-quadrature justification, the ideal-lap choice, and an explicit "this does not fix #721/#717-6" note. No edit to `class_ledger.py` — reusing the public `class_time_ledger` costs one extra O(n) transit pass and keeps g1's frozen dataclass untouched.

**`tests/unit/physics/test_class_utilization_observable.py`** — the acceptance test. A `TestPerClassGripBandWidth` block: widths sum to σ⁺_lap (conservation); widths ∝ ideal-lap class time shares and rank-ordered with them; a zero-share/unpopulated class gets exactly zero width and its band collapses to the point; widths scale linearly in σ⁺_lap and are all zero for `grip=None`; widths identical across two different `v_real` (driver-independence); optional sensitivity vector re-weights but still partitions; and the magnitude guard — no single class ever carries the whole-lap width. Also extend `test_point_deficit_byte_identical_with_and_without_grip` to assert the points are untouched by the per-class widths.

**`scripts/build_class_utilization_observables.py`** — write path. Line ~462 stamps `obs.g_sigma_by_class[j]` instead of the shared scalar; log line reports the lap scale and the width range; docstring soft-degrade paragraph updated. Note for the implementer: this file's line 417 (`grip_lookup(..., 0)`) is #721's fix site — touch only line 462 and the prose so the two issues merge mechanically.

**`src/physics/utilization/reference_utilization_store.py`** — `driver_class_observables` schema comment currently documents `g_sigma_onesided` as "the ONE-SIDED grip σ⁺ scale" session-wide; it becomes the per-class allocated width. I'd also add a `g_sigma_lap` provenance column (the store already has additive `_migrate_missing_class_columns`, so this is a tuple entry + dataclass field) — without it the whole-lap scale is not recoverable from stored rows, which #712's σ-chain diagnosis needs. This is the one optional item; drop it if the reviewer wants minimum surface.

**`tests/unit/physics/test_build_class_utilization_observables.py`** — currently asserts `all(r.g_sigma_onesided == 0.0)` under the soft-degrade. Add the non-degenerate case: with a synthetic grip record, rows differ across classes, sum to the lap scale, and round-trip through the store (plus `g_sigma_lap` if kept).

**`docs/architecture/reference/physics-unit-conventions.md`** — mandated by that document's own header ("any work that … repurposes a physics model parameter — or changes a producer, consumer, or store column — must review and update this document in the same gate"). Module-G has *no* rows in the table today, which is part of why this units mismatch survived. Add a Grip-G / utilization block: `session_offset`/`curve_asymptote` (s, whole-lap), `g_sigma_onesided` (s, **per class** after allocation), producer/store/consumer columns, and the lap→class share as the named conversion seam.

**`docs/architecture/packets/physics.md`** — two prose spots describe the column as the grip-derived session-level value (~line 1522 in the stage-D block, ~line 1741 in the utilization component block). Update both, and add the `@grade`-tagged decision bullet carrying the allocation rationale. Per this repo's stated convention (index.md: one ADR file only for explicitly-required anchors, the rest as graded packet bullets) I would **not** mint a new ADR.

**Verification:** the two touched test files plus `tests/unit/physics/fingerprint/` (the downstream σ consumer) and the pyright baseline-diff gate. Evidence artifact: one plot of per-class band width against class time share on a real weekend with a synthetic grip record — the shape of this change is a width-distribution question, which reads far better plotted than tabulated.

**Knowingly left alone:** `src/physics/fingerprint/fit.py` (its crown invariants all still hold verbatim — per-class values make its per-cell aggregation *more* correct, and re-homing grip out of additive σ is #717/#712), and `scripts/run_heldout_diagnostic_670.py`'s "channel-independent grip term" wording, which describes an archived shipped report and shouldn't be retro-edited.
```

## Task #688 — claimed file list, in the plan's own words

```
```
src/physics/layer2/grip_baseline.py
src/physics/layer2/grip_store.py
src/data/weather_features.py
scripts/populate_wet_features.py
tests/unit/physics/layer2/test_grip_baseline.py
tests/unit/physics/layer2/test_grip_store.py
tests/unit/physics/layer2/test_grip_heldout.py
tests/unit/data/test_wet_features.py
docs/architecture/packets/physics.md
docs/architecture/packets/data.md
```
```

## Task #698 — claimed file list, in the plan's own words

```
src/physics/fingerprint/address.py
src/physics/fingerprint/store.py
src/physics/fingerprint/fit.py
src/physics/pilot/pipeline.py
scripts/fingerprint_bounded_validation.py
scripts/join_bounded_validation_667.py
scripts/fingerprint_class_coverage_675.py
tests/unit/physics/fingerprint/test_address.py
tests/unit/physics/fingerprint/test_store.py
tests/unit/physics/fingerprint/test_fit.py
tests/unit/physics/fingerprint/test_bounded_validation.py
.gitignore
docs/architecture/packets/physics.md
docs/architecture/index.md
```

## Task #716 — claimed file list, in the plan's own words

```
```
C:\Programs\constellation-skills\scripts\work_id_paths.py
C:\Programs\constellation-skills\scripts\run_crew.py
C:\Programs\constellation-skills\scripts\verify_agent_feedback.py
C:\Programs\constellation-skills\scripts\install_constellation.py
C:\Programs\constellation-skills\tests\test_work_id_paths.py
C:\Programs\constellation-skills\tests\test_crew_launcher.py
C:\Programs\constellation-skills\tests\test_verify_agent_feedback.py
C:\Programs\constellation-skills\tests\test_install_constellation.py
C:\Programs\constellation-skills\skills\workbench\SKILL.md
C:\Programs\constellation-skills\skills\commander\references\crew-dispatch.md
```
```

## Task #704 — claimed file list, in the plan's own words

```
```
src/physics/instrument_panel/replication.py
```
```
