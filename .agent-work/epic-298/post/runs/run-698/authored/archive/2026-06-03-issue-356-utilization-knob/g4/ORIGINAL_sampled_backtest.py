"""End-to-end backtesting helpers for schema-v4 sampled evo runtimes."""

from __future__ import annotations

import logging
import math
import sqlite3
import time
from dataclasses import dataclass, field as dataclass_field
from typing import Mapping, Protocol, Sequence

import numpy as np

from src.compound_prior.runtime_normalization import CompoundNormalizer
from src.data.database import DatabaseManager
from src.evo_predictor.runtime_contracts import FinalOrderSampleSet, StageSnapshot
from src.evo_predictor.sampled_runtime import (
    OracleStateUnavailableError,
    SAMPLED_BACKTEST_MODES,
    SampledEvoRuntime,
)
from src.utils.constants import get_calendar

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SampledBacktestRaceResult:
    """Backtest result for one scored race."""

    year: int
    round_num: int
    gp_name: str
    prediction: FinalOrderSampleSet
    actual_results: dict[str, int]
    metrics: dict[str, float]
    diagnostics: dict[str, object]
    per_stage_metrics: dict[str, dict[str, float]] = dataclass_field(default_factory=dict)


@dataclass(frozen=True)
class SampledBacktestResult:
    """Aggregate sampled-runtime backtest result."""

    year: int
    race_count: int
    aggregate_metrics: dict[str, float]
    per_race: tuple[SampledBacktestRaceResult, ...]
    diagnostics: dict[str, object]


class ScoringContractError(ValueError):
    """Raised when the strict scoring contract is violated before metric computation.

    The scorer requires ``set(predicted_driver_ids) == set(actual_driver_ids)``.
    ``scorer_skip_reason`` is one of:
      - ``missing_scoring_target``
      - ``scorer_input_contains_non_scored_entrants``
      - ``missing_predicted_scored_entrants``
      - ``driver_id_canonicalization_failure``
    """

    def __init__(self, scorer_skip_reason: str, diagnostics: dict[str, object]) -> None:
        self.scorer_skip_reason = scorer_skip_reason
        self.diagnostics = dict(diagnostics)
        super().__init__(f"Scoring contract violated: {scorer_skip_reason}")


class NoSampledBacktestRacesError(ValueError):
    """Raised when a sampled backtest cannot score any selected race."""

    def __init__(self, message: str, diagnostics: Mapping[str, object]):
        super().__init__(message)
        self.diagnostics = dict(diagnostics)


def _verify_scoring_contract(
    prediction: _SampledOrderScorable,
    actual_results: Mapping[str, int],
    *,
    scoring_target_source: str = "race",
) -> None:
    """Verify the strict scoring contract before computing metrics.

    Raises ``ScoringContractError`` unless
    ``set(prediction.driver_ids) == set(actual_results.keys())``.
    """
    predicted_ids = set(prediction.driver_ids)
    actual_ids = set(actual_results.keys())
    extra_predicted = sorted(predicted_ids - actual_ids)
    missing_predicted = sorted(actual_ids - predicted_ids)

    base_diag: dict[str, object] = {
        "scoring_target_source": scoring_target_source,
        "predicted_scored_driver_ids": sorted(predicted_ids),
        "actual_scored_driver_ids": sorted(actual_ids),
        "extra_predicted_driver_ids": extra_predicted,
        "missing_predicted_driver_ids": missing_predicted,
        "driver_id_mapping_used": "direct",
    }

    if not actual_results:
        raise ScoringContractError(
            "missing_scoring_target",
            {**base_diag, "scorer_input_status": "missing_scoring_target",
             "scorer_skip_reason": "missing_scoring_target"},
        )

    if extra_predicted:
        raise ScoringContractError(
            "scorer_input_contains_non_scored_entrants",
            {**base_diag, "scorer_input_status": "scorer_input_contains_non_scored_entrants",
             "scorer_skip_reason": "scorer_input_contains_non_scored_entrants"},
        )

    if missing_predicted:
        raise ScoringContractError(
            "missing_predicted_scored_entrants",
            {**base_diag, "scorer_input_status": "missing_predicted_scored_entrants",
             "scorer_skip_reason": "missing_predicted_scored_entrants"},
        )


class _PredictRuntime(Protocol):
    @property
    def race_start_target_lap(self) -> int: ...

    def predict(
        self,
        *,
        year: int,
        gp_name: str,
        db: DatabaseManager,
        compound_normalizer: CompoundNormalizer,
        mode: str = "sampled_state",
        oracle_grid_positions: Mapping[str, int | float] | None = None,
        oracle_lap_n_positions: Mapping[str, int | float] | None = None,
        oracle_lap_n_target_lap: int | None = None,
    ) -> FinalOrderSampleSet: ...


class _SampledOrderScorable(Protocol):
    """Structural type accepted by the primary final-order scorer.

    ``FinalOrderSampleSet`` satisfies this, as does ``_RestrictedScoringView``
    produced when marginalizing out non-scored (e.g. post-qualifying DNS) drivers.
    """

    @property
    def driver_ids(self) -> tuple[str, ...]: ...
    @property
    def final_order_samples(self) -> np.ndarray: ...
    @property
    def position_distribution(self) -> Mapping[str, Mapping[int, float]]: ...
    @property
    def pairwise_finish_probability_matrix(self) -> np.ndarray: ...


@dataclass(frozen=True)
class _RestrictedScoringView:
    """Final-order sample set restricted to the scored (racing) drivers.

    A full restricted ``FinalOrderSampleSet`` cannot be built because its
    ``stage_snapshots`` store only per-stage aggregates (``position_distribution``)
    that cannot be truthfully re-ranked without raw per-stage ordering samples.
    The primary scorer never touches ``stage_snapshots``, so this view carries
    only the fields ``sampled_order_metrics`` reads.

    Restricting is *exact*, not an approximation: a final order is a pure rank of
    per-driver latent power (``latent_samples_to_order_samples``) with no
    field-interaction term, so marginalizing a driver out of the realized samples
    preserves every surviving pair's relative order bit-for-bit. Dropping his
    column and dense-re-ranking each sample to ``1..N-1`` therefore yields the
    exact sub-marginal of the joint order distribution.
    """

    driver_ids: tuple[str, ...]
    final_order_samples: np.ndarray
    position_distribution: Mapping[str, Mapping[int, float]]
    pairwise_finish_probability_matrix: np.ndarray


def _position_distribution_from_samples(
    samples: np.ndarray, driver_ids: tuple[str, ...]
) -> dict[str, dict[int, float]]:
    """Recompute the position distribution from a ``(sample_count, N)`` order array."""
    n_samples, n_drivers = samples.shape
    distribution: dict[str, dict[int, float]] = {}
    for column, driver_id in enumerate(driver_ids):
        counts = np.bincount(samples[:, column], minlength=n_drivers + 1)[1:]
        distribution[driver_id] = {
            position: float(counts[position - 1]) / n_samples
            for position in range(1, n_drivers + 1)
        }
    return distribution


def _dense_rank_positions(positions: np.ndarray) -> np.ndarray:
    """Dense-rank unique positions to a contiguous ``1..N`` scale (gap-closing).

    ``positions`` must hold unique values (enforced by ``_actual_position_vector``),
    so argsort-of-argsort yields the ascending dense rank with no gaps.
    """
    return (np.argsort(np.argsort(positions)) + 1).astype(float)


def _restrict_prediction_to_scored(
    prediction: FinalOrderSampleSet, scored_ids: set[str]
) -> _RestrictedScoringView:
    """Marginalize non-scored drivers out of a prediction's final-order samples.

    Drops their columns from ``final_order_samples``, dense-re-ranks each sample
    to ``1..K``, slices the pairwise matrix to the survivors, and recomputes the
    position distribution. See ``_RestrictedScoringView`` for why this is exact.
    """
    keep_idx = [i for i, d in enumerate(prediction.driver_ids) if d in scored_ids]
    kept_drivers = tuple(prediction.driver_ids[i] for i in keep_idx)

    sub_samples = np.asarray(prediction.final_order_samples, dtype=int)[:, keep_idx]
    # Source samples are permutations of 1..N, so the surviving columns hold unique
    # values per row; argsort-of-argsort gives a dense ascending rank 1..K.
    restricted_samples = np.argsort(np.argsort(sub_samples, axis=1), axis=1) + 1

    pairwise = np.asarray(prediction.pairwise_finish_probability_matrix, dtype=float)
    restricted_pairwise = pairwise[np.ix_(keep_idx, keep_idx)]

    return _RestrictedScoringView(
        driver_ids=kept_drivers,
        final_order_samples=restricted_samples,
        position_distribution=_position_distribution_from_samples(restricted_samples, kept_drivers),
        pairwise_finish_probability_matrix=restricted_pairwise,
    )


def _compute_entrant_restriction(
    prediction: FinalOrderSampleSet,
    actual_results: Mapping[str, int],
) -> tuple[_SampledOrderScorable, dict[str, object]]:
    """Restrict a prediction to the scored (racing) drivers before final-order scoring.

    Returns ``(scoring_prediction, diagnostics)``. When
    ``diagnostics["missing_predicted_scored_entrants"]`` is non-empty, the caller
    must skip scoring — a scored entrant cannot be recovered from the prediction.

    When the prediction contains non-scored weekend participants (predicted drivers
    absent from the race classification, e.g. a post-qualifying DNS) and every driver
    who raced *was* predicted, those drivers are marginalized out of the returned
    final-order samples so the survivors can still be scored. This recovers the whole
    race rather than discarding its finishing-order signal. Stage snapshots are left
    to the caller's per-stage branch, which scores each stage against the intersection
    of its drivers and that stage's actual ordering.
    """
    predicted_ids_set = set(prediction.driver_ids)
    scored_entrant_ids = set(actual_results.keys())

    excluded_non_scored = sorted(predicted_ids_set - scored_entrant_ids)
    missing_scored = sorted(scored_entrant_ids - predicted_ids_set)

    driver_signal_status: dict[str, str] = {}
    for d in sorted(predicted_ids_set | scored_entrant_ids):
        if d in excluded_non_scored:
            driver_signal_status[d] = "excluded_non_scored"
        elif d in missing_scored:
            driver_signal_status[d] = "missing_from_prediction"
        else:
            driver_signal_status[d] = "scored"

    diagnostics: dict[str, object] = {
        "predicted_driver_ids_raw": sorted(predicted_ids_set),
        "scored_entrant_driver_ids": sorted(scored_entrant_ids),
        "excluded_non_scored_weekend_participants": excluded_non_scored,
        "missing_predicted_scored_entrants": missing_scored,
        "low_support_scored_entrants": [],
        "entrant_filter_source": "race_classification",
        "driver_signal_status_by_driver": driver_signal_status,
    }

    if not excluded_non_scored:
        # Nothing to filter — return the original prediction unchanged.
        diagnostics["entrant_filter_status"] = "no_restriction_needed"
        return prediction, diagnostics

    if missing_scored:
        # A driver who raced was never predicted; he cannot be recovered from the
        # samples, so the race is unscorable. Preserve the prediction unchanged and
        # let the strict scoring contract surface the skip.
        diagnostics["entrant_filter_status"] = "preserved_unfiltered_prediction"
        diagnostics["entrant_filter_reason"] = (
            "A scored entrant is missing from the prediction; cannot restrict to a "
            "scorable survivor set. Preserving prediction so scoring fails strictly."
        )
        return prediction, diagnostics

    # Everyone who raced was predicted; only non-scored participants remain. Drop
    # them and score the survivors (exact under the latent-power ranking model).
    restricted = _restrict_prediction_to_scored(prediction, scored_entrant_ids)
    diagnostics["entrant_filter_status"] = "restricted_to_scored_entrants"
    diagnostics["marginalized_out_driver_ids"] = excluded_non_scored
    diagnostics["marginalization_reason"] = "predicted_but_absent_from_race_classification"
    diagnostics["entrant_filter_reason"] = (
        "Predicted drivers absent from the race classification (e.g. post-qualifying "
        "DNS) were marginalized out of the final-order samples. This is exact, not an "
        "approximation: final order is a pure rank of per-driver latent power with no "
        "field-interaction term, so removing a driver preserves the survivors' relative "
        "order in every realized sample."
    )
    diagnostics["restricted_driver_ids"] = list(restricted.driver_ids)
    return restricted, diagnostics


def sampled_order_metrics(
    prediction: _SampledOrderScorable,
    actual_results: Mapping[str, int],
    *,
    probability_epsilon: float = 1e-12,
    scoring_target_source: str = "race",
) -> dict[str, float]:
    """Compute ordinal metrics for sampled final race orders.

    Enforces the strict scoring contract:
    ``set(prediction.driver_ids) == set(actual_results.keys())``.
    Raises ``ScoringContractError`` if the contract is violated.
    Call ``_compute_entrant_restriction`` before this function to record entrant
    diagnostics for skip reporting.
    """
    _verify_scoring_contract(prediction, actual_results, scoring_target_source=scoring_target_source)
    # Dense-rank actual positions to a contiguous 1..N scale so the absolute-position
    # metrics (sample/expected MAE, exact-order rate) compare against the same scale as
    # the sample orders, which are always permutations of 1..N. Official classifications
    # can be non-contiguous (a post-race disqualification leaves a gap, e.g. ..18,19,21);
    # without this the MAE for the survivor below the gap is inflated by the missing slot.
    # Order-invariant metrics (pairwise, Spearman, winner) are unaffected by re-ranking.
    actual_positions = _dense_rank_positions(_actual_position_vector(prediction, actual_results))
    samples = np.asarray(prediction.final_order_samples, dtype=float)
    expected_positions = samples.mean(axis=0)
    sample_mae = np.mean(np.abs(samples - actual_positions[None, :]), axis=1)

    winner_idx = int(np.argmin(actual_positions))
    win_probabilities = np.asarray(
        [prediction.position_distribution[driver_id][1] for driver_id in prediction.driver_ids],
        dtype=float,
    )
    actual_winner_win_probability = float(win_probabilities[winner_idx])
    winner_order = np.argsort(-win_probabilities, kind="mergesort")
    winner_rank = int(np.flatnonzero(winner_order == winner_idx)[0]) + 1

    pairwise = np.asarray(prediction.pairwise_finish_probability_matrix, dtype=float)
    pairwise_log_losses: list[float] = []
    pairwise_briers: list[float] = []
    n_drivers = len(prediction.driver_ids)
    eps = float(probability_epsilon)
    for i in range(n_drivers):
        for j in range(i + 1, n_drivers):
            target = 1.0 if actual_positions[i] < actual_positions[j] else 0.0
            raw_probability = float(pairwise[i, j])
            probability = float(np.clip(raw_probability, eps, 1.0 - eps))
            pairwise_log_losses.append(
                -(target * math.log(probability) + (1.0 - target) * math.log(1.0 - probability))
            )
            pairwise_briers.append((raw_probability - target) ** 2)

    spearman_values = np.asarray(
        [_spearman_positions(sample, actual_positions) for sample in samples],
        dtype=float,
    )
    exact_matches = np.all(samples == actual_positions[None, :], axis=1)

    return {
        "mean_sample_mae": float(np.mean(sample_mae)),
        "median_sample_mae": float(np.median(sample_mae)),
        "expected_position_mae": float(np.mean(np.abs(expected_positions - actual_positions))),
        "winner_probability_assigned_to_actual_winner": actual_winner_win_probability,
        "actual_winner_rank_by_win_probability": float(winner_rank),
        "pairwise_log_loss_against_actual_order": float(np.mean(pairwise_log_losses)),
        "pairwise_brier_against_actual_order": float(np.mean(pairwise_briers)),
        "sample_spearman_mean": _finite_mean(spearman_values),
        "sample_spearman_median": _finite_median(spearman_values),
        "exact_order_sample_rate": float(np.mean(exact_matches)),
    }




def stage_snapshot_metrics(
    snapshot: StageSnapshot,
    actual_results: Mapping[str, int],
    *,
    probability_epsilon: float = 1e-12,
    score_intersection: bool = False,
) -> dict[str, float]:
    """Compute pairwise log-loss and Brier metrics for a StageSnapshot against actual ordering.

    Uses the same pairwise formulas as sampled_order_metrics but scores the
    StageSnapshot.pairwise_probability_matrix instead of the final-order matrix.

    By default returns an empty dict if actual_results is missing any driver from
    snapshot.driver_ids (graceful skip). When ``score_intersection`` is set, the
    snapshot is instead scored over the drivers present in *both* the snapshot and
    ``actual_results`` (e.g. a post-qualifying DNS present in the stage snapshot but
    absent from that stage's actual ordering). Slicing the pairwise matrix to the
    intersection is exact — pairwise finish probabilities are invariant to which
    other drivers are in the field. The caller handles the empty-dict case.
    """
    if score_intersection:
        keep_idx = [i for i, d in enumerate(snapshot.driver_ids) if d in actual_results]
        if len(keep_idx) < 2:
            return {}
        driver_ids = tuple(snapshot.driver_ids[i] for i in keep_idx)
        pairwise = np.asarray(snapshot.pairwise_probability_matrix, dtype=float)[
            np.ix_(keep_idx, keep_idx)
        ]
    else:
        driver_ids = snapshot.driver_ids
        pairwise = np.asarray(snapshot.pairwise_probability_matrix, dtype=float)
        # Build actual position vector; skip gracefully if truth is incomplete
        missing = [d for d in driver_ids if d not in actual_results]
        if missing:
            return {}

    actual_positions = np.asarray(
        [actual_results[driver_id] for driver_id in driver_ids], dtype=float
    )

    n_drivers = len(driver_ids)
    eps = float(probability_epsilon)
    pairwise_log_losses: list[float] = []
    pairwise_briers: list[float] = []
    for i in range(n_drivers):
        for j in range(i + 1, n_drivers):
            target = 1.0 if actual_positions[i] < actual_positions[j] else 0.0
            raw_prob = float(pairwise[i, j])
            prob = float(np.clip(raw_prob, eps, 1.0 - eps))
            pairwise_log_losses.append(
                -(target * math.log(prob) + (1.0 - target) * math.log(1.0 - prob))
            )
            pairwise_briers.append((raw_prob - target) ** 2)

    if not pairwise_log_losses:
        return {}

    return {
        "pairwise_log_loss_against_actual_order": float(np.mean(pairwise_log_losses)),
        "pairwise_brier_against_actual_order": float(np.mean(pairwise_briers)),
    }

def backtest_sampled_runtime(
    runtime: SampledEvoRuntime,
    *,
    year: int,
    db: DatabaseManager,
    compound_normalizer: CompoundNormalizer,
    max_rounds: int | None = None,
    race_names: Sequence[str] | None = None,
    mode: str = "sampled_state",
) -> SampledBacktestResult:
    """Run a sampled runtime over selected races with actual classifications."""

    mode = _validate_sampled_backtest_mode(mode)
    selected_races = _selected_calendar(
        year=int(year), max_rounds=max_rounds, race_names=race_names
    )
    race_filter = tuple(race_names or ())
    per_race: list[SampledBacktestRaceResult] = []
    skipped: list[dict[str, object]] = []
    classification_rounds_found = _classification_rounds_found(db, int(year))
    race_start_target_lap_rounds_found = _race_start_target_lap_rounds_found(db, int(year))

    n_total = len(selected_races)
    _logger.info(
        "Sampled backtest year %d: scoring up to %d races (mode=%s)",
        int(year), n_total, mode,
    )
    backtest_t0 = time.monotonic()
    for race_idx, (round_num, gp_name) in enumerate(selected_races):
        elapsed = time.monotonic() - backtest_t0
        rate = race_idx / elapsed if (elapsed > 0 and race_idx > 0) else 0
        eta_s = (n_total - race_idx) / rate if rate > 0 else 0
        _logger.info(
            "  race %d/%d - round %s %s  (elapsed %.0fm, ETA ~%.0fm)",
            race_idx + 1, n_total, round_num, gp_name, elapsed / 60, eta_s / 60,
        )
        base_diag = {"year": int(year), "round_num": int(round_num), "gp_name": gp_name}
        actual_results = dict(db.get_session_classification(int(year), int(round_num), "R") or {})
        if not actual_results:
            skipped.append({**base_diag, "skip_reason": "missing_actual_race_classification"})
            continue
        # Collect stage truth for per_stage_metrics (quali and race_start; race = actual_results)
        quali_results: dict[str, int] = {
            d: int(p)
            for d, p in (db.get_session_classification(int(year), int(round_num), "Q") or {}).items()
        }
        target_lap = _runtime_race_start_target_lap(runtime)
        race_start_results: dict[str, int] = {
            d: int(p)
            for d, p in (
                db.get_race_start_order(int(year), int(round_num), expected_target_lap=target_lap)
                or {}
            ).items()
        }
        oracle_state, oracle_skip = _oracle_state_for_mode(
            db=db,
            runtime=runtime,
            year=int(year),
            round_num=int(round_num),
            mode=mode,
        )
        if oracle_skip is not None:
            skipped.append({**base_diag, **oracle_skip})
            continue
        try:
            oracle_grid = oracle_state["oracle_grid_positions"]
            oracle_lap_n = oracle_state["oracle_lap_n_positions"]
            oracle_target_lap = oracle_state["oracle_lap_n_target_lap"]
            prediction = runtime.predict(
                year=int(year),
                gp_name=gp_name,
                db=db,
                compound_normalizer=compound_normalizer,
                mode=mode,
                oracle_grid_positions=(
                    oracle_grid if isinstance(oracle_grid, Mapping) else None
                ),
                oracle_lap_n_positions=(
                    oracle_lap_n if isinstance(oracle_lap_n, Mapping) else None
                ),
                oracle_lap_n_target_lap=(
                    int(oracle_target_lap)
                    if isinstance(oracle_target_lap, int)
                    else None
                ),
            )
        except OracleStateUnavailableError as exc:
            skipped.append({
                **base_diag,
                "skip_reason": "missing_oracle_state",
                "mode": mode,
                "oracle_state_diagnostics": exc.diagnostics,
                "missing_oracle_state": exc.diagnostics.get("missing_oracle_state", []),
                "race_start_target_lap": _runtime_race_start_target_lap(runtime),
            })
            continue
        scoring_prediction, entrant_diagnostics = _compute_entrant_restriction(
            prediction, actual_results
        )
        if entrant_diagnostics["missing_predicted_scored_entrants"]:
            skipped.append({
                **base_diag,
                "skip_reason": "missing_predicted_scored_entrants",
                "missing_predicted_scored_entrants": entrant_diagnostics[
                    "missing_predicted_scored_entrants"
                ],
                "entrant_filter_diagnostics": entrant_diagnostics,
            })
            continue
        try:
            metrics = sampled_order_metrics(scoring_prediction, actual_results)
        except ScoringContractError as exc:
            skipped.append({
                **base_diag,
                "skip_reason": exc.scorer_skip_reason,
                "scoring_contract_diagnostics": exc.diagnostics,
                "entrant_filter_diagnostics": entrant_diagnostics,
            })
            continue
        except ValueError as exc:
            skipped.append({
                **base_diag,
                "skip_reason": "unscorable_prediction",
                "message": str(exc),
                "entrant_filter_diagnostics": entrant_diagnostics,
            })
            continue
        # Compute per-stage metrics for each task snapshot
        stage_truth_map: dict[str, dict[str, int]] = {
            "quali": quali_results,
            "race_start": race_start_results,
            "race": {driver: int(pos) for driver, pos in actual_results.items()},
        }
        per_stage: dict[str, dict[str, float]] = {}
        # Record stages scored over a reduced field (snapshot driver absent from that
        # stage's actual ordering). Expected for a DNS in race/race-start; on quali it
        # usually signals incomplete classification data, so keep it auditable rather
        # than silently averaging a partial field into the aggregates.
        stage_field_coverage: dict[str, dict[str, int]] = {}
        for stage_task, stage_actual in stage_truth_map.items():
            snapshot = prediction.stage_snapshots.get(stage_task)
            if snapshot is not None and stage_actual:
                scored_driver_count = sum(1 for d in snapshot.driver_ids if d in stage_actual)
                if scored_driver_count < len(snapshot.driver_ids):
                    stage_field_coverage[stage_task] = {
                        "snapshot_driver_count": len(snapshot.driver_ids),
                        "scored_driver_count": scored_driver_count,
                    }
                # Score each stage against the intersection of its snapshot drivers
                # and that stage's actual ordering, so a driver absent from one stage
                # (e.g. a DNS missing from race/race-start truth) only drops that
                # stage's metrics rather than the whole race.
                stage_m = stage_snapshot_metrics(snapshot, stage_actual, score_intersection=True)
                if stage_m:
                    per_stage[stage_task] = stage_m
        per_race.append(
            SampledBacktestRaceResult(
                year=int(year),
                round_num=int(round_num),
                gp_name=gp_name,
                prediction=prediction,
                actual_results={driver: int(pos) for driver, pos in actual_results.items()},
                metrics=metrics,
                diagnostics={
                    **base_diag,
                    "mode": mode,
                    "available_modes": list(SAMPLED_BACKTEST_MODES),
                    "entrant_filter_diagnostics": entrant_diagnostics,
                    "stage_field_coverage": stage_field_coverage,
                },
                per_stage_metrics=per_stage,
            )
        )

    _logger.info(
        "Sampled backtest year %d complete - %d scored, %d skipped of %d  (total %.0fm)",
        int(year), len(per_race), len(skipped), n_total,
        (time.monotonic() - backtest_t0) / 60,
    )

    diagnostics = {
        "mode": mode,
        "available_modes": list(SAMPLED_BACKTEST_MODES),
        "oracle_modes_available": True,
        "db_path_used": str(getattr(db, "db_path", "unknown")),
        "classification_table_or_query_used": (
            "session_classifications WHERE year = ? AND round_num = ? AND session_type = 'R'"
        ),
        "classification_rounds_found": classification_rounds_found,
        "race_start_target_lap_rounds_found": race_start_target_lap_rounds_found,
        "sampled_backtest_candidate_rounds": [
            {"year": int(year), "round_num": int(round_num), "gp_name": gp_name}
            for round_num, gp_name in selected_races
        ],
        "attempted_race_count": len(selected_races),
        "scored_race_count": len(per_race),
        "skipped_event_count": len(skipped),
        "sampled_backtest_skipped_rounds": skipped,
        "skipped_races": skipped,
        "race_filter": list(race_filter),
    }

    if not per_race:
        raise NoSampledBacktestRacesError(
            f"No sampled backtest races were scored for {year}; skipped_races={skipped!r}",
            diagnostics,
        )

    diagnostics.update({
        "mode": mode,
        "available_modes": list(SAMPLED_BACKTEST_MODES),
        "oracle_modes_available": True,
        "attempted_race_count": len(selected_races),
        "scored_race_count": len(per_race),
        "skipped_event_count": len(skipped),
        "skipped_races": skipped,
        "race_filter": list(race_filter),
    })
    return SampledBacktestResult(
        year=int(year),
        race_count=len(per_race),
        aggregate_metrics=_mean_metrics([race.metrics for race in per_race]),
        per_race=tuple(per_race),
        diagnostics=diagnostics,
    )


def _classification_rounds_found(db: DatabaseManager, year: int) -> list[dict[str, object]]:
    return _rounds_found(
        db,
        """
        SELECT round_num, MIN(gp_name) AS gp_name, COUNT(*) AS row_count
        FROM session_classifications
        WHERE year = ? AND session_type = 'R'
        GROUP BY round_num
        ORDER BY round_num
        """,
        year,
    )


def _validate_sampled_backtest_mode(mode: str) -> str:
    normalized = str(mode)
    if normalized not in SAMPLED_BACKTEST_MODES:
        raise ValueError(f"mode must be one of {SAMPLED_BACKTEST_MODES!r}, got {mode!r}")
    return normalized


def _oracle_state_for_mode(
    *,
    db: DatabaseManager,
    runtime: _PredictRuntime,
    year: int,
    round_num: int,
    mode: str,
) -> tuple[dict[str, object], dict[str, object] | None]:
    state: dict[str, object] = {
        "oracle_grid_positions": None,
        "oracle_lap_n_positions": None,
        "oracle_lap_n_target_lap": None,
    }
    missing: list[str] = []
    if mode in ("oracle_grid", "oracle_all_states"):
        grid = dict(db.get_session_classification(int(year), int(round_num), "Q") or {})
        if not grid:
            missing.append("oracle_grid")
        else:
            state["oracle_grid_positions"] = {driver: int(pos) for driver, pos in grid.items()}
    if mode in ("oracle_lap_n", "oracle_all_states"):
        target_lap = _runtime_race_start_target_lap(runtime)
        lap_n = dict(
            db.get_race_start_order(
                int(year),
                int(round_num),
                expected_target_lap=target_lap,
            )
            or {}
        )
        if not lap_n:
            missing.append("oracle_lap_n")
        else:
            state["oracle_lap_n_positions"] = {
                driver: int(pos) for driver, pos in lap_n.items()
            }
            state["oracle_lap_n_target_lap"] = target_lap
    if missing:
        return state, {
            "skip_reason": "missing_oracle_state",
            "missing_oracle_state": missing,
            "mode": mode,
            "race_start_target_lap": _runtime_race_start_target_lap(runtime),
        }
    return state, None


def _runtime_race_start_target_lap(runtime: _PredictRuntime) -> int:
    target_lap = getattr(runtime, "race_start_target_lap", 3)
    if not isinstance(target_lap, int) or target_lap < 1:
        raise ValueError(
            "runtime race_start_target_lap must be an integer >= 1, "
            f"got {target_lap!r}"
        )
    return int(target_lap)


def _race_start_target_lap_rounds_found(db: DatabaseManager, year: int) -> list[dict[str, object]]:
    return _rounds_found(
        db,
        """
        SELECT round_num, MIN(gp_name) AS gp_name, COUNT(*) AS row_count
        FROM race_start_order
        WHERE year = ?
        GROUP BY round_num
        ORDER BY round_num
        """,
        year,
    )


def _rounds_found(db: DatabaseManager, query: str, year: int) -> list[dict[str, object]]:
    try:
        with sqlite3.connect(getattr(db, "db_path", ""), timeout=5.0) as conn:
            rows = conn.execute(query, (int(year),)).fetchall()
    except (sqlite3.Error, TypeError, ValueError):
        return []
    return [
        {"round_num": int(row[0]), "gp_name": row[1], "row_count": int(row[2])}
        for row in rows
    ]


def _selected_calendar(
    *, year: int, max_rounds: int | None, race_names: Sequence[str] | None
) -> list[tuple[int, str]]:
    calendar = list(get_calendar(int(year)))
    if max_rounds is not None:
        calendar = calendar[: int(max_rounds)]
    indexed = [(idx, gp_name) for idx, gp_name in enumerate(calendar, start=1)]
    if race_names:
        requested = {str(name).casefold() for name in race_names}
        indexed = [(idx, gp_name) for idx, gp_name in indexed if gp_name.casefold() in requested]
        found = {gp_name.casefold() for _, gp_name in indexed}
        missing = sorted(requested - found)
        if missing:
            raise ValueError(f"Requested race names are not in the {year} calendar: {missing}")
    return indexed


def _actual_position_vector(
    prediction: _SampledOrderScorable, actual_results: Mapping[str, int]
) -> np.ndarray:
    missing = [driver_id for driver_id in prediction.driver_ids if driver_id not in actual_results]
    if missing:
        raise ValueError(
            f"actual_results is missing predicted drivers: {missing}. "
            "Call _compute_entrant_restriction before sampled_order_metrics to exclude "
            "non-scored weekend participants; if restriction was applied, this indicates "
            "a driver_id_canonicalization_failure."
        )
    positions = np.asarray(
        [actual_results[driver_id] for driver_id in prediction.driver_ids], dtype=float
    )
    if not np.all(np.isfinite(positions)):
        raise ValueError("actual_results positions must be finite")
    if np.any(positions <= 0.0):
        raise ValueError("actual_results positions must be positive")
    if len({float(position) for position in positions}) != len(positions):
        raise ValueError("actual_results positions must be unique for predicted drivers")
    return positions


def _spearman_positions(sample_positions: np.ndarray, actual_positions: np.ndarray) -> float:
    if sample_positions.size < 2:
        return float("nan")
    if np.std(sample_positions) == 0.0 or np.std(actual_positions) == 0.0:
        return float("nan")
    return float(np.corrcoef(sample_positions, actual_positions)[0, 1])


def _finite_mean(values: np.ndarray) -> float:
    finite = values[np.isfinite(values)]
    return float(np.mean(finite)) if finite.size else float("nan")


def _finite_median(values: np.ndarray) -> float:
    finite = values[np.isfinite(values)]
    return float(np.median(finite)) if finite.size else float("nan")


def _mean_metrics(rows: Sequence[Mapping[str, float]]) -> dict[str, float]:
    result: dict[str, float] = {}
    for key in sorted({key for row in rows for key in row}):
        values = [float(row[key]) for row in rows if key in row and np.isfinite(float(row[key]))]
        if values:
            result[key] = float(np.mean(values))
    return result


__all__ = [
    "NoSampledBacktestRacesError",
    "SAMPLED_BACKTEST_MODES",
    "SampledBacktestRaceResult",
    "SampledBacktestResult",
    "ScoringContractError",
    "_compute_entrant_restriction",
    "_verify_scoring_contract",
    "backtest_sampled_runtime",
    "sampled_order_metrics",
    "stage_snapshot_metrics",
]
