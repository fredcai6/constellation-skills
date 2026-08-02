# Mission Frame — cmdr-451 (issue #451 quali race_weekend under-extraction)

Map source: ORCHESTRATOR_CONTEXT.md, docs/architecture/index.md (evo region), docs/evo/prediction_ceiling_and_priorities.md §7.6–§7.6.4, archived runs #381/#387/#391/#414/#420.

## Intent
Localize the ~19pp standalone `race_weekend` quali-head deficit (0.6149 vs ceiling 0.8061 on the
§7.6.2 same-pairs harness) to (a) representation / (b) training signal / (c) capacity, with
harness numbers per probe. Ship a fix only if small. Honest null acceptable.

## Affected capabilities
- `latent_power` driver_quali_power_from_race_weekend head: pairwise ordering from FP-derived
  features. (Evo region; rigorous; probabilistic claim path.)
- §7.6.2 shared-pairs harness (`scripts/diagnose_quali_same_pairs.py`) — the scoreboard.
- Single-module training CLI (`run.py train-latent-power-module`) — the ablation lever.

## Structural anchors
- struct: `src/evo_predictor/quali_power_adapter.py` — 23-feature `qs_*/short_run_*_adj` vector,
  antisymmetric pairwise diffs. The min-sector pace anchor is ABSENT here.
- struct: `src/latent_power/network.py::InnerNetwork` — 3-layer MLP, configurable width (capacity).
- struct: `src/latent_power/modules.py` loss = student_t_nll(pairwise, target_mu).
- struct: `src/latent_power/retro_loader.py::load_target_mu_for_event` — retro power_diff labels.
- struct: `scripts/diagnose_quali_same_pairs.py` / `diagnose_quali_evidence.py` — harness + ceiling.

## Governing constraints / assumptions
- Single-module ablation retrains ONLY; no gold cycle; no Piece-2; no promoted-default change
  unless small. Walk-forward as-of discipline; DB-only; numbers on §7.6.2 harness or flagged.
- ASSUMPTION (to verify in G1): committed bundle `gold_cycle_260608_043414` reproduces §7.6.2
  baseline despite being anchor-active-trained. If it does not reproduce, flag and treat the
  reproduced number as the working baseline.

## Decision anchors / pressure
- decision (§7.6.3 C3, durable): pairwise sign-accuracy is invariant to any monotone rescale →
  only a new ordering signal moves it. This pre-excludes pure-calibration fixes.
- decision pressure: if a representation fix is small (add one min-sector pace feature to the head
  input path), shipping it touches a promoted default → surface to Admiral, do NOT self-merge.

## Claims / evidence surfaces to re-confirm
- claim: rw 0.6149 / rh 0.7803 / ceiling 0.8061 / 23862 pairs (headline) — re-confirm in G1.
- claim (#387): retro quali labels are perfect-ordering, 0/65266 upsets, start_bias=0 — the
  training ORDERING signal is correct; reframes hypothesis (b).

## Map confidence / staleness
- §7.6.2 records dir not preserved (gitignored) → MUST regenerate (G1). Flagged.
- Original §7.6.2 bundle gone; using promoted anchor-active bundle → reproduction-fidelity risk,
  handled as a G1 verification gate.

## Out of scope
Full gold cycles; Piece-2 conditioned net; fusion-layer changes; σ head; non-quali tasks;
rank-blend ceiling switch (#379/#391 HOLD); data collection; #425/#394/#395 builds (Wave 2).

## Why the frame is full (not skipped)
Relevant architecture artifacts exist and the probe correctness depends on harness fidelity,
as-of discipline, and not crossing the single-module fence — the map is load-bearing here.
