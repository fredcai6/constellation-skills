# Scout/recon task — map the race_weekend quali `pi` inference path (issue #420)

You are a READ-ONLY recon crew. Do NOT modify any files. Repo root:
`C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`. Python is `py`.

## Goal

We will productionize a cross-channel pace anchor: at inference, blend the
race_weekend quali head's latent field `pi` with a z-standardized
`best_across_fp` min-sector practice-pace ordering:
`pi' = (1-alpha)*z(-pi) + alpha*z(-best_across_fp_minsector)` per event.

We must attach this INSIDE the race_weekend quali head's output path (where its
latent field `pi` is produced at inference) — NOT at the fusion layer.

Your job: map the exact code path so the Commander can pick a minimal,
single attach point. Return precise file:line citations.

## Questions to answer (cite file:line for each)

1. **Where is race_weekend quali `pi` produced at inference?** Trace from
   `src/evo_predictor/sampled_runtime.py` and `src/evo_predictor/module_runtime.py`
   through to the per-module latent field solve. Which function produces the `pi`
   array for a single module at a single event? What identifies a module as the
   "race_weekend" quali head (module name string, task, evidence_source)? List the
   exact registered module name(s) for the race_weekend quali head — check
   `src/evo_predictor/module_adapters/_registry.py` and
   `src/latent_power/modules.py`.

2. **What is the per-module runtime output object/shape?** When a module is run at
   inference, what structure carries its `pi` field (and sigma/covariance)? Name the
   dataclass/dict and its fields. Where is it consumed next (fusion)? Cite the exact
   handoff point between "module produced pi" and "fusion consumes pi".

3. **Is the `best_across_fp` min-sector source available at the attach point?**
   The prototype computes it via `scripts/diagnose_quali_evidence.best_across_fp_source`
   reading DB sector times directly. In production, the same FP1/2/3 min-sector pace
   flows through `practice_preprocessor/` into `data_adapter/` features. Find:
   - Where `best_across_fp` / theoretical-best min-sector pace is computed in
     `src/evo_predictor/practice_preprocessor/` (cite the function in `_compute.py`
     and `_lap_pipeline.py`).
   - How that value reaches the race_weekend quali module's feature batch (the
     `PairBatch` or feature rows). Is the per-driver `best_across_fp` magnitude (or a
     per-driver ordering derivable from it) available at the point where `pi` is
     produced — i.e. can the attach point see a per-driver best_across_fp scalar
     keyed by driver_id at inference, WITHOUT a new DB read? Cite where the feature
     lives in the batch/features object.
   - If it is NOT directly available at the pi-production point, what is the
     closest seam where BOTH the per-driver `pi` AND the per-driver best_across_fp
     pace are simultaneously in scope? Cite it.

4. **Driver identity alignment.** At the pi-production point, how are array
   positions mapped to driver_ids (so we can align the anchor to pi by driver)? Cite
   the index/entity mapping.

5. **Config plumbing pattern.** How do existing runtime config knobs reach the
   inference path? Trace one recent example end-to-end: the `qs_compound_beta_regime`
   knob (#380) or `recent_history_form_encoding` (#369) — from
   `configs/evo/gold_defaults.toml` → `gold_cycle/config.py` → into the runtime
   `EvoPipeline`/module config. Cite the chain so a new config key can follow the
   same pattern. Where does the sampled-runtime manifest carry per-module runtime
   config that inference reads?

6. **Sign convention.** The latent field: higher `pi` = ranked ahead (per GLOSSARY).
   The prototype's source ordering uses `-pi` (lower=better) and `-best_across_fp`.
   Confirm the sign of `pi` in the runtime output and how best_across_fp magnitude
   relates to pace (lower lap time = faster = should map to higher pi). State the
   exact transform needed so the blend improves ordering (not inverts it).

## Method

- Read, don't run training. You may run read-only `py` one-liners to inspect.
- Use Grep/Glob/Read. Start: `sampled_runtime.py`, `module_runtime.py`,
  `module_adapters/_registry.py`, `module_adapters/_runtime_builders.py`,
  `quali_power_adapter.py`, `practice_preprocessor/_compute.py`,
  `practice_preprocessor/_lap_pipeline.py`, `models/_features.py`,
  `data_adapter/_assemble.py`, `latent_power/field_solve.py`,
  `latent_power/modules.py`, `gold_cycle/config.py`, `configs/evo/gold_defaults.toml`.

## Return format

Return a CONCISE findings report (not files). For each of the 6 questions: the
answer with file:line citations. End with a "RECOMMENDED ATTACH SEAM" section: the
single best function/location to inject the blend, why it is minimal, and whether
best_across_fp is natively available there or must be threaded in from an adjacent
seam. Flag any blocker that would make the production path unable to reproduce the
anchor (e.g. best_across_fp genuinely unavailable at inference).
