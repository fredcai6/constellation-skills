# Bit-reproducibility measurement spike — latent-power CPU training (gate G3)

**Status:** measurement spike complete. **NO production code was changed.**
**Recommendation (one line):** **NO-GO** for the set-flags-only deterministic mode as literally
scoped — but the spike pinpoints a one-line, ~1× cost production fix that reaches **exact** bit
reproducibility, which is a strong **GO signal for G4**. See [Recommendation](#go-no-go-recommendation).

---

## 1. Question

Can latent-power CPU training be made (near-)bit-reproducible run-to-run, and at what training-time
cost? Decision criterion set by the Commander (human makes the final call):

- **GO** iff a *deterministic mode* reaches run-to-run weight drift **< 1e-6** at **< 2×** baseline
  wall-time, **AND** without production code changes beyond a contained set-flags call.
- **NO-GO** otherwise (strict mode errors on an op with no deterministic impl, drift stays ≫ 1e-6,
  or cost ≥ 2×).

"Deterministic mode" in the criterion = the set-flags intervention in condition 2 below
(`torch.use_deterministic_algorithms(True)` + `torch.set_num_threads(1)` + applicable env).

## 2. Methodology

**Fair comparison.** Identical seeds, data, and config across every run; only the determinism knobs
vary between conditions. The production training loop re-seeds itself each run
(`torch.manual_seed(seed)` inside a `torch.random.fork_rng()` block for module init, plus
`random.Random(seed)` for batch shuffling), so the two runs of a condition are seed-identical *by
construction* — we do not inject seeds into the training path.

**Reused harness.** The spike imports the bounded #356 determinism harness
(`tests/integration/test_utilization_determinism.py`) by file path and calls its private helpers
unchanged: `_run_plan` (builds the real gold-cycle train+backtest jobs via the production
`build_main_train_backtest_jobs` and runs them through `src.utils.utilization.run_jobs`),
`_load_weights`, and `_max_weight_diff`. At `n_workers=1`, `run_jobs` short-circuits to an
**in-process** sequential loop (no pool, no pickling), so any torch global flag set in the spike
process is in effect during training. The harness's `init_worker` pins `torch.set_num_threads(1)` in
**all** conditions, so the baseline is genuinely single-threaded too — the only thing that varies is
the determinism knob.

**Bounded config (from #356).** 2 `recent_history` quali modules
(`driver_quali_power_from_recent_history`, `constructor_quali_power_from_recent_history`),
`train_years=[2022, 2023]`, `eval_year=2024`, `max_rounds_per_year=1`, `epochs=2`, `seed=0`,
`threads_per_worker=1`, `n_workers=1`. Uses the local `data/f1_data_{2022,2023,2024}.db` and the
retro-truth root; skips cleanly where absent.

**Per condition:** training is run **twice** into separate temp trees. Drift = max absolute
difference over the model `state_dict` (across both modules), run0 vs run1. Wall-time = per-run
`time.perf_counter()`. A discarded **warmup** run precedes the first measured condition so cold-start
(import / allocator / JIT) does not pollute the baseline; all reported wall-times are therefore warm.

**`use_deterministic_algorithms(True)`-raises handling.** Strict mode is wrapped so that if any op
lacked a deterministic implementation, the exact op + `RuntimeError` text would be captured as a
finding; `warn_only=True` is then measured separately to log any nondeterministic ops via Python
warnings. (Neither fired — see findings.)

**`CUBLAS_WORKSPACE_CONFIG`:** CUDA-only knob. `torch.cuda.is_available()` is `False` on this build
(`torch 2.10.0+cpu`), so it is **N/A** and intentionally **not set**. Documented, not applied.

**Conditions.** 1–2 are the handoff conditions; 3 surfaces nondeterministic-op warnings; 4–5 are a
**root-cause diagnostic** — they additionally call `torch.manual_seed(0)` in the spike process
immediately before each run, to test whether the unseeded process-global RNG is the drift source.
The preseed is a *measurement knob in the harness*, not a src/ change.

## 3. Environment

| field | value |
|---|---|
| torch | `2.10.0+cpu` |
| CUDA available | `False` → `CUBLAS_WORKSPACE_CONFIG` N/A (not set) |
| `PYTHONHASHSEED` | unset (irrelevant here; see §5) |
| threads_per_worker / n_workers | 1 / 1 (all conditions) |
| Python | `py` launcher (Windows) |

## 4. Measurements

Two runs per condition (`--runs 2`). Drift is max-abs `state_dict` diff, run0 vs run1. Wall-time is
warm (cold-start absorbed by a discarded warmup). Raw data:
`.agent-work/fn-decomposition-and-bitrepro/evidence/bitrepro_results.json`.

| # | condition | knobs | run0 / run1 wall (s) | wall_mean (s) | ×baseline | **weight drift (max-abs)** | raised? | nondet-op warnings |
|---|---|---|---|---|---|---|---|---|
| 1 | **baseline** | `use_deterministic_algorithms(False)`, threads=1 | 0.093 / 0.095 | 0.094 | 1.00× | **3.78e-4** | no | — |
| 2 | **deterministic-strict** | `use_deterministic_algorithms(True)`, threads=1 | 0.097 / 0.097 | 0.097 | 1.03× | **3.59e-4** | **no** | **none** |
| 3 | deterministic-warn | `use_deterministic_algorithms(True, warn_only=True)`, threads=1 | 0.097 / 0.098 | 0.097 | 1.03× | **3.46e-4** | no | **none** |
| 4 | baseline-seeded *(diag)* | baseline + `manual_seed(0)` before each run | 0.095 / 0.106 | 0.100 | 1.07× | **0.0** | no | — |
| 5 | deterministic-strict-seeded *(diag)* | strict + `manual_seed(0)` before each run | 0.100 / 0.099 | 0.100 | 1.06× | **0.0** | no | none |

Numbers reproduced across two independent end-to-end harness runs (drift stable at ~3.5–3.8e-4 for
flags-only; **exactly 0.0** for both seeded conditions). The ~3e-4 flags-only figure also matches the
inherent drift independently documented by #356.

## 5. Findings

**F1 — `use_deterministic_algorithms(True)` does NOT raise on this training path.** Strict mode ran to
completion for both modules. **No op in the latent-power training path lacks a deterministic
implementation** on torch 2.10 CPU (the `linalg.solve` / `eigh` / `scatter_` in `field_solve.py` run
under `no_grad` in eval and did not trip strict mode). This is the explicit "if it raises, capture the
op" case from the handoff: it did **not** raise. → The strict-mode-errors NO-GO branch does not apply.

**F2 — The determinism flags do not move the drift.** baseline 3.78e-4 → strict 3.59e-4 → warn
3.46e-4 are all the same ~3e-4 magnitude (the spread is itself run-to-run FP noise). `warn_only=True`
emitted **zero** nondeterministic-op warnings. So the ~3e-4 drift is **not** caused by any op that
`use_deterministic_algorithms` governs (reduction-order kernel nondeterminism), which is exactly why
flipping the flag changes nothing.

**F3 — Root cause: the train-mode `nn.Dropout` forward pass draws from UNSEEDED process-global RNG.**
`src/latent_power/network.py` puts three `nn.Dropout(p=config.dropout=0.2)` layers in the backbone,
active during the training-loop forward pass. `src/latent_power/training.py` seeds the RNG **only
inside** `with torch.random.fork_rng(): torch.manual_seed(seed)` — and `fork_rng()` **restores** the
prior global RNG state on exit. So module *init* is seeded/deterministic, but the **training loop's
dropout sampling consumes whatever process-global RNG state happens to exist**, which differs
run-to-run. Conditions 4–5 confirm this decisively: a single `torch.manual_seed(0)` before the run
collapses drift to **exactly 0.0** — even with the determinism flag OFF (condition 4). The drift is a
**seeding-placement** issue, not a kernel-nondeterminism issue. (`PYTHONHASHSEED` is irrelevant: the
randomness is torch RNG, not Python `hash()`.)

**F4 — Wall-time cost of determinism is negligible.** Determinism flags add ~3% (1.03×); the seed
call adds nothing measurable (1.06×, within noise). The `< 2×` budget is not a constraint here. (Note:
the cold first run was ~0.9s; the warmup run isolates that, so the table's warm numbers are the fair
comparison. At this bounded scale all warm runs are ~0.1s.)

## 6. GO/NO-GO recommendation

**Against the criterion as literally written: NO-GO.**

The criterion's "deterministic mode" = the contained set-flags call (condition 2). That mode reaches
drift **3.59e-4**, which is **~360× above** the `< 1e-6` bar. It does meet the cost bar (1.03× < 2×)
and does not require a production change — but it **fails the drift bar**, and adding the flags buys
nothing because they do not address the actual cause (F2/F3). **The set-flags-only path cannot reach
bit-reproducibility, regardless of wall-time.**

**But the spike found the real lever, and it is cheap.** Bit-exact reproducibility (**drift = 0.0**)
is achieved by seeding the process-global RNG so the training-loop dropout is deterministic
(conditions 4–5), at **~1× wall-time**. The catch for *this gate*: the effective fix is **not** a
set-flags call on the outside — it is a one-line change to **`src/latent_power/training.py`** (seed
the global RNG for the training loop, e.g. move/duplicate `torch.manual_seed(seed)` so it also governs
the loop, rather than seeding only inside the restored `fork_rng()` block). That is a **production code
change**, which is **explicitly out of scope for this measurement spike** and is precisely what **G4**
would own.

**Net recommendation:**
- **NO-GO** on "ship deterministic mode as a contained set-flags call" — flags alone leave drift at
  ~3.6e-4; they are the wrong tool for this cause and should **not** be added expecting reproducibility.
- **Strong GO signal for G4** (a separate, human-approved production change): a one-line RNG-seeding
  fix in `training.py` reaches **exact 0.0 drift at ~1× cost**, with `use_deterministic_algorithms`
  **not** required (it neither raises nor helps; it could be left off, or added defensively at ~3% cost
  to guard against future op-level nondeterminism). The human makes the final call at integrate.

Honest caveats: drift = 0.0 is demonstrated at the **bounded** #356 scale (2 modules, 1 round/yr, 2
epochs, single-thread). The seeding fix removes the *dropout* nondeterminism that fully accounts for
the observed drift here; at larger scale or with multi-thread BLAS, reduction-order FP nondeterminism
could reappear — at which point `use_deterministic_algorithms(True)` (shown here to be free and
non-raising) is the right additional guard. G4 should re-confirm 0.0 drift at production scale.

## 7. How to re-run

```bash
# From repo root. Writes the raw measurements JSON and prints the summary table.
py .agent-work/fn-decomposition-and-bitrepro/bitrepro_spike.py \
   --out .agent-work/fn-decomposition-and-bitrepro/evidence/bitrepro_results.json
# Optional: more runs per condition for tighter drift bounds.
py .agent-work/fn-decomposition-and-bitrepro/bitrepro_spike.py --out <path> --runs 4
```

- Harness: `.agent-work/fn-decomposition-and-bitrepro/bitrepro_spike.py` (throwaway; no src/ change).
- Raw results: `.agent-work/fn-decomposition-and-bitrepro/evidence/bitrepro_results.json`.
- Reused (unmodified): `tests/integration/test_utilization_determinism.py`.
- Skips cleanly (exit 2) if local `data/f1_data_{2022,2023,2024}.db` or the retro-truth root is absent.
