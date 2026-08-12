# Grading packet
You are grading five independent planning outputs against frozen ground truth.
Score each one and return, per task: the score, and the quoted words from the
claim that decided it. Grade the claimed file list **as written**.

## 1. Ground truth — the correct seam per task  *(grader sees this section)*

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

## 2. Scoring scale — seam identification  *(grader sees this section)*

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

## 3. Coverage axis  *(grader sees this section)*

For any task scored `n/a` under §2:

| Value | Meaning |
|---|---|
| **ACKNOWLEDGED-MISS** | The run states the work is not in this repo, or that it cannot locate a seam here, explicitly. |
| **SILENT-CRAWL** | The run proposes an in-repo seam anyway without stating the gap. |
| **CONFUSED** | Neither — no locatable position taken. |

---

---

# The five claimed seams, verbatim

## Task #690 - claimed file list, in the plan's own words

```
FILES I WOULD CHANGE

```
src/physics/utilization/class_utilization_observable.py
tests/unit/physics/test_class_utilization_observable.py
scripts/build_class_utilization_observables.py
src/physics/utilization/reference_utilization_store.py
src/physics/fingerprint/fit.py
tests/unit/physics/test_build_class_utilization_observables.py
tests/unit/physics/test_reference_utilization_store.py
docs/architecture/decisions/c1-driver-utilization-design.md
docs/architecture/packets/physics.md
```

Why each: **`class_utilization_observable.py`** — adds the public `allocate_sigma_to_classes` law and splits the scalar field into per-class array plus session scalar; this is the defect's home. **`test_class_utilization_observable.py`** — the width-shape test the acceptance names (partition identity, monotonicity, bound, two degenerate limits, strict narrowing, validation), plus the six pre-existing band guard tests that must still pass. **`build_class_utilization_observables.py`** — writes the per-class value into each row instead of the repeated scalar, and fixes a log line that prints a name that no longer exists. **`reference_utilization_store.py`** — the column keeps its name and type but changes meaning, so the vintage marker and schema comment move with the producer. **`fingerprint/fit.py`** — doc-only; its docstring describes `g_sigma_onesided` as the whole-lap quantity, which becomes wrong. **The two sibling test files** — assert distinct per-class values reach distinct rows (a test that passes under the old fan-out is not evidence) and cover the store ruling. **`c1-driver-utilization-design.md`** — the "documented rationale" deliverable, as an Extension in the shape that anchor already uses. **`packets/physics.md`** — two lines describe the column and become wrong; deliberately *not* a gate, it's Cartographer's at the reconcile step, per the architecture bookend.
```

## Task #688 - claimed file list, in the plan's own words

```
FILES I WOULD CHANGE

```
src/data/weather_features.py
scripts/populate_wet_features.py
tests/unit/data/test_wet_features.py
src/physics/layer2/grip_baseline.py
tests/unit/physics/layer2/test_grip_baseline.py
src/physics/layer2/grip_store.py
tests/unit/physics/layer2/test_grip_store.py
tests/unit/physics/layer2/test_grip_batch.py
tests/unit/physics/test_class_utilization_observable.py
scripts/run_grip_batch.py
tests/unit/physics/layer2/test_grip_heldout.py
docs/architecture/decisions/grip-wet-severity-selection.md
docs/architecture/packets/data.md
docs/architecture/packets/physics.md
```

Per-file justification is in `.agent-work/issue-688/OWNERSHIP_SCOPE.md`; the frozen plan is `.agent-work/issue-688/execute.json`.
```

## Task #698 - claimed file list, in the plan's own words

```
FILES I WOULD CHANGE

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
tests/unit/physics/fingerprint/test_script_path_guard.py
.gitignore
```

Why each: **`address.py`** gains `SlotAddress` and re-expresses `CellAddress` as slot + `class_id` — the one place the validation rules may live (g1). **`store.py`** is the retyped boundary; the whole issue is its signature (g2). **`fit.py:356`** is the only production writer. **`pilot/pipeline.py:257,325`** are the two production readers. **`fingerprint_bounded_validation.py:124`** and **`join_bounded_validation_667.py:173`** are script call sites that must migrate with the signature — no other change to either; both already carry the path guard. **`fingerprint_class_coverage_675.py`** takes all of H2 and H3a: the `_REPO_ROOT` guard plus repo-anchoring its two bare relative path constants and an `--out` override. **`test_address.py`** gets the `SlotAddress` tests and the hard-coded `cell_key` characterization test (g1). **`test_store.py` / `test_fit.py` / `test_bounded_validation.py`** hold the ~44 positional call sites; their *call forms* change, their *assertions* must not. **`test_script_path_guard.py`** is new and proves the H2/H3 property — `src` resolves under this repo root from a foreign cwd — rather than grepping for the guard line. **`.gitignore`** gets one narrow rule for the live pre-archive artifact path, coupled to the anchoring change and explicitly not a blanket `*.json` rule.

Deliberately **not** in that list: `docs/architecture/packets/physics.md`. The architecture bookend puts map reconciliation at the spine's `reconcile` step under Cartographer, and there's a specific delta waiting for it — the packet says `instrument_panel` reads `get_fingerprint` cells directly, but no store import exists under `src/physics/instrument_panel/`; the call is at `pilot/pipeline.py:325`.
```

## Task #716 - claimed file list, in the plan's own words

```
FILES I WOULD CHANGE

All paths are in `C:\Programs\constellation-skills` (the constellation-skills repo), not f1Brainz.

- `scripts/work_id.py` — **new.** The single work_id-safe helper both defect sites import, as the issue asks: right-anchored session-name parse (`work_id = parts[1:-3]`, valid because gate/role are used verbatim as filename stems and so can never contain `/`), segment-count relative-path archive matching (the current `name == id or endswith('-'+id)` rule is exactly its N=1 case), and exact-match-preferred heading selection. Also tolerates a flattened archive name, which keeps the rejected naming-convention option cheap to adopt later.
- `tests/test_work_id.py` — **new.** Pins the helper, and specifically pins that the slashless case is byte-identical to today's behavior for all three functions.
- `scripts/install_constellation.py` — declare `work_id.py` as a runtime companion of both call-site scripts so it propagates to commander, admiral, and explorer. Without this the module is absent from every install and the fix works only in the source repo — the exact drift the file's own comment records.
- `tests/test_install_constellation.py` — make the sibling-import guard compare against the *expanded* bundle (what actually installs) rather than the raw one, plus a positive test that a real install writes the module into all three skills.
- `scripts/run_crew.py` — `load_registry_for_resume` delegates to the helper. One change fixes all three CLI paths that reach it (`--verify-result`, `--resume`, bare `--abandon`).
- `tests/test_crew_launcher.py` — nested-work_id regression asserting the registry is *found*; current coverage is slashless-only, which is why this shipped.
- `scripts/verify_agent_feedback.py` — `_current_run_archive_dirs` and `_entry_block` delegate to the helper. Changes only how a work-id is matched, never what the invariant requires.
- `tests/test_verify_agent_feedback.py` — `--phase archive` passes for a nested work_id, and the parent/child heading case resolves to the parent.
- `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` — one bounded note (reconcile-step deliverable; this repo has no packet map, so this design doc is the structural record) stating that a work_id may contain `/` and that matching is segment-based, so the next author does not re-assume slashless.
```

## Task #704 - claimed file list, in the plan's own words

```
FILES I WOULD CHANGE

The repo diff is two files. (`.agent-work/` run bookkeeping — `AGENT_FEEDBACK.md`, `lessons-delta.json` — is written but never committed on the mission branch, per `lesson:shared-files-not-on-mission-branch`; and `reconcile` is expected to be a reasoned map no-op, since a private in-module helper is below map resolution.)

```
src/physics/instrument_panel/replication.py
tests/unit/physics/instrument_panel/test_replication_axis_identity.py
```

- `src/physics/instrument_panel/replication.py` — the change itself: add the private `_axis_groups(grid) -> (driver_rows, class_cols)` helper and route both duplicated accumulation loops through it, keeping `_axis_means`'s separate grand-mean pass for bit-exactness. Public surface, `__all__`, thresholds, frozen constants, and the double-centering formula all untouched.
- `tests/unit/physics/instrument_panel/test_replication_axis_identity.py` (new) — the byte-identity harness: `repr`-exact goldens captured from the unmodified module, asserted with `==` on ragged, unbalanced, singleton-row and single-cell grids. A new file rather than an edit to `test_replication_channel.py` so G1's diff is purely additive and G2's "the harness is unchanged" constraint is mechanically checkable.
```

