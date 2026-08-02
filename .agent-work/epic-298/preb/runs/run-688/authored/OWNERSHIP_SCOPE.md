# File-ownership scope vs authored gates (pre-freeze enumeration)

Doctrine (`commander-core.md` §Mission frame): before advancing past `plan`, confirm `execute.json`
contains one gate for **every** file and decision-class in the ownership scope. A gate imperative
that merely *references* a decision as "handled elsewhere" is not a substitute for the gate existing.

## Files

| # | File | Owning gate(s) | Why it must move |
|---|---|---|---|
| 1 | `src/data/weather_features.py` | g1 | `populate_wet_features_for_db` iterates races only (`:224`); measured zero non-race `wet_lap_fraction` rows in every season. This is the coverage hole that makes every downstream threshold a no-op for Q/SQ/S/FP. |
| 2 | `scripts/populate_wet_features.py` | g1 | The CLI's scope, counts, and verbose listing are hard-wired to races; they must follow the widened population or the operator sees a false "done". |
| 3 | `tests/unit/data/test_wet_features.py` | g1 | Existing coverage asserts race-only behaviour; the widened scope needs its own cases and the race-parity guarantee needs a test. |
| 4 | `src/physics/layer2/grip_baseline.py` | g2, g3, g4 | Holds all three defects: the any-wet bool (`rain_flag_from_raw:256-263`), the missing drying-window protection for the monotone model (`_saturating:287-289`), and the flat 4× inflation (`:120`, applied `:481-482`/`:548-549`). |
| 5 | `tests/unit/physics/layer2/test_grip_baseline.py` | g2, g3, g4 | Asserts the current `count>0` semantics at `:288-293`; also the home for the frozen 28-session corpus, the guard's non-inertness, and the sigma no-regression test. |
| 6 | `src/physics/layer2/grip_store.py` | g5 | The record has no field to carry a graded severity, and there is no named place for the selection predicate — the absence that let the spike invent its own rule. |
| 7 | `tests/unit/physics/layer2/test_grip_store.py` | g5 | Constructs `GripEstimateRecord` at `:38` and asserts `rain_flag` round-trip at `:100-101`; breaks on a field addition. Also the home for the old-schema migration fixture. |
| 8 | `tests/unit/physics/layer2/test_grip_batch.py` | g5 | Constructs the record at `:28` and `:42`. |
| 9 | `tests/unit/physics/test_class_utilization_observable.py` | g5 | Constructs the record at `:223` — the one **non-grip** consumer site, and the easiest to miss. |
| 10 | `scripts/run_grip_batch.py` *(new)* | g6 | No CLI exists for the grip batch; `run_grip_batch` is reachable only from `pilot/pipeline.py:764`. The re-batch this change requires is otherwise unreproducible. |
| 11 | `tests/unit/physics/layer2/test_grip_heldout.py` | g6 | #678's frozen g4 acceptance harness; imports `rain_flag_from_raw` at `:88` and threads `rain_flag=` into the fit at `:245`. Threading only — its measurement semantics are frozen. |
| 12 | `docs/architecture/decisions/grip-wet-severity-selection.md` *(new)* | g7 | The repo has **no** anchor for any wet/rain rule; discharges the region-crossing obligation. |
| 13 | `docs/architecture/packets/data.md` | g7 | `:88-93` claims the wet columns are "Populated 2019-2026" without saying races-only — measurement contradicts it. A correction, not an extension. |
| 14 | `docs/architecture/packets/physics.md` | g7 | The grip leaf (`:1513-1520`) says nothing about the rain rule or any selection semantics. |

**Read-but-not-changed** (cited so a crew does not "helpfully" edit them):
`src/physics/burn_rate_calibration.py` (the precedent mirrored), `src/physics/layer2/grip_batch.py`
(already stores every session — never the bug), `src/physics/pilot/pipeline.py` (verify-still-green),
`src/data/database/_ingest.py` (the upsert is already correct and non-clobbering).

## Decision classes

| Decision class | Owning gate | Present as a real gate? |
|---|---|---|
| Which wet instrument | g1 + g2 | Yes — g1 supplies the signal, g2 consumes it |
| Threshold values (0.05 / 0.50) | g2 | Yes, with 0.50 flagged unconstrained by data |
| Drying-window guard | **g3 (own gate)** | Yes — split out per critic finding F1 |
| Sigma grading | **g4 (own gate, droppable)** | Yes — isolated for the owner ruling |
| `rain_flag` additive survival | g5 | Yes |
| Predicate placement | g5 | Yes |
| Held-out-worsens framing | g6 | Yes, as surfaced decision pressure |
| Recording the decisions | g7 | Yes |

**Result: every file and every decision class has an owning gate. No orphans, no "handled elsewhere".**
