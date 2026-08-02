#!/usr/bin/env python3
"""Commander probe: does a BETTER production-derivable anchor close the §7.6.3 gap?

Read-only. Reuses the G2 harness machinery (imports it). Tests anchor variants on
a subset of years to decide whether the PARTIAL reproduction is fixable by
changing the anchor FIELD (cheap, in-machinery) vs requiring a new all-FP feature
or a DB bypass (then ruling-5 verdict holds).

Anchor variants (all blended via the production blend_quali_pace_anchor):
  A  qs_best_raw                         (current production; quali-sim short stints)
  B  min(qs_best_raw, lr_best_raw)       (both practice buckets; existing features)
  C  best_across_fp (DB, all clean FP laps)   (the §7.6.3 prototype anchor = upper bound)

For each: pooled overall + EASY at alpha in {0, 0.5, 1.0} on the SAME shared pairs.
alpha=1.0 is each anchor's pure-ordering ceiling (the key comparison).
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import scripts.accept_quali_anchor_420 as H  # the approved G2 harness
import scripts.diagnose_quali_same_pairs as sp
import scripts.diagnose_quali_evidence as dqe
from src.compound_prior.runtime_normalization import (
    CompoundNormalizer,
    load_time_safe_compound_prior,
)
from src.data.database import DatabaseManager
from src.evo_predictor.data_adapter import build_sampled_runtime_features
from src.evo_predictor.latent_power_bundle import load_latent_power_module_bundle
from src.evo_predictor.module_runtime import (
    build_pair_batch_for_module,
    loaded_runtime_module_from_bundle,
    run_module_field,
)
from src.evo_predictor.quali_pace_anchor import blend_quali_pace_anchor
from src.latent_power.modules import DRIVER_QUALI_POWER_FROM_RACE_WEEKEND
from src.utils.constants import get_calendar

PROBE_YEARS = (2019, 2022, 2024)  # spread across regulation eras; fast subset
ALPHAS = (0.0, 0.5, 1.0)


def _f(x):
    return float(x) if (x is not None and x == x) else float("nan")


def _pools():
    return {a: {v: [0, 0, 0, 0] for v in ("A", "B", "C")} for a in ALPHAS}
    # [agree, total, easy_agree, easy_total]


def main() -> int:
    bundle = load_latent_power_module_bundle(H.BUNDLE_PATH)
    loaded = loaded_runtime_module_from_bundle(bundle)
    pools = _pools()

    for year in PROBE_YEARS:
        artifact = load_time_safe_compound_prior(
            H.COMPOUND_PRIOR_ROOT, target_year=year, allow_same_season_research=False
        )
        cn = CompoundNormalizer(artifact)
        db = DatabaseManager(db_path=str(H.DB_ROOT / f"f1_data_{year}.db"))
        con = dqe.open_db(year)
        ev_meta = {rnd: st for rnd, _gp, st in dqe.events_for_year(con, year)}
        for rnd, gp in enumerate(get_calendar(year), start=1):
            st = ev_meta.get(rnd, set())
            if dqe.is_sprint_weekend(st):
                continue
            if not ({"FP1", "FP2", "FP3"} <= st) or "Q" not in st:
                continue
            try:
                fs = build_sampled_runtime_features(
                    year=year, gp_name=gp, db=db, compound_normalizer=cn,
                    form_lookback=H.FORM_LOOKBACK,
                    memory_window_years=H.MEMORY_WINDOW_YEARS,
                    race_start_target_lap=H.RACE_START_TARGET_LAP, task="quali",
                )
                feats = fs.features
                pb = build_pair_batch_for_module(
                    DRIVER_QUALI_POWER_FROM_RACE_WEEKEND, features=feats,
                    constructor_features=fs.constructor_features,
                    constructor_by_driver=fs.constructor_by_driver,
                )
                result = run_module_field(loaded, pb)
            except Exception:
                continue
            pi = result.pi
            eids = result.entity_ids
            if len(pi) < 2:
                continue

            qs = {d.driver_id: d.qs_best_raw for d in feats.drivers}
            lr = {d.driver_id: d.lr_best_raw for d in feats.drivers}

            target = dqe.classification_order(con, year, rnd, "Q")
            baf = dqe.best_across_fp_source(con, rnd, dqe.agg_theoretical_best, ("FP1", "FP2", "FP3"))
            blr = dqe.session_blend_rank_source(con, rnd, dqe.agg_theoretical_best, ("FP1", "FP2", "FP3"))
            model = {d: -float(pi[i]) for i, d in enumerate(eids)}
            cs = set(model) & set(baf) & set(blr) & set(target)
            if len(cs) < 2:
                continue
            common = sorted(cs)
            m_src = sp._restrict(model, cs); b_src = sp._restrict(baf, cs)
            r_src = sp._restrict(blr, cs); tgt = sp._restrict(target, cs)
            shared = sp._shared_nontie_pairs(common, tgt, [m_src, b_src, r_src])
            if not shared:
                continue

            idx = {d: i for i, d in enumerate(eids)}
            pi_c = np.array([pi[idx[d]] for d in common], dtype=float)

            def anc_A():
                return np.array([_f(qs.get(d)) for d in common], dtype=float)

            def anc_B():
                out = []
                for d in common:
                    a, b = _f(qs.get(d)), _f(lr.get(d))
                    vals = [x for x in (a, b) if x == x]
                    out.append(min(vals) if vals else float("nan"))
                return np.array(out, dtype=float)

            def anc_C():
                # best_across_fp from DB, restricted to common
                return np.array([_f(baf.get(d)) for d in common], dtype=float)

            anchors = {"A": anc_A(), "B": anc_B(), "C": anc_C()}
            for v, anc in anchors.items():
                for a in ALPHAS:
                    bp = blend_quali_pace_anchor(pi_c, anc, a)
                    bsrc = {d: -float(bp[i]) for i, d in enumerate(common)}
                    ag, tot = sp._acc_on_pairs(bsrc, tgt, shared)
                    strat = sp._stratified_pairwise(bsrc, tgt, shared)
                    ea, et = strat.get("far (gap>=9)", (0, 0))
                    p = pools[a][v]
                    p[0] += ag; p[1] += tot; p[2] += ea; p[3] += et
        con.close()
        print(f"[year {year}] done", flush=True)

    print("\n==== ANCHOR VARIANT PROBE (years %s) ====" % (PROBE_YEARS,))
    print("A=qs_best_raw  B=min(qs,lr)_best_raw  C=best_across_fp(DB,all FP)")
    print(f"{'variant':>8} {'alpha':>6} {'overall':>9} {'EASY>=9':>9} {'pairs':>7} {'easy_pr':>8}")
    for v in ("A", "B", "C"):
        for a in ALPHAS:
            p = pools[a][v]
            ov = p[0] / p[1] if p[1] else float("nan")
            ez = p[2] / p[3] if p[3] else float("nan")
            print(f"{v:>8} {a:>6.1f} {ov:>9.4f} {ez:>9.4f} {p[1]:>7} {p[3]:>8}")
    print("\nKEY: compare alpha=1.0 ceilings (pure anchor ordering) across A/B/C.")
    print("If B's a=1 ceiling ~ C's, min(qs,lr) is a viable in-machinery fix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
