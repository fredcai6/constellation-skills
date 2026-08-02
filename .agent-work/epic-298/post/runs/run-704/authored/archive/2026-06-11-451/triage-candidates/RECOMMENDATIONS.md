# Triage recommendations — cmdr-451 (issue #451) — NOT FILED (returned to Admiral)

Per launch order LO-451: "triage candidates (do not file)." These route to the Admiral as
recommendations for epic #453 Wave 2 / triage backlog. None filed by the Commander.

## TC1 — Wave-2 #425 design input (HIGH value; directly actionable)
**Recommendation:** #425 (explicit all-FP min-sector practice-pace feature) is the right repair and is
**validated by measurement** — adding `min(qs_best_raw, lr_best_raw)` as a head INPUT lifts OOS-2025 rw
0.5868→0.7700 (≈ ceiling). When landing it: (a) feed it as an INPUT feature to the
`driver_quali_power_from_race_weekend` head (not only post-hoc blend); (b) add a companion
`{name}_missing` indicator (the probe used a bare 0.0 NaN fallback — production needs the missingness
channel, matching the head's existing `_AMBIGUOUS_SPARSE_FEATURES` convention); (c) consider a
within-event-standardised variant (raw seconds mix track scales; LayerNorm partly handles it but a
z-scored pace gap is cleaner). Route: feed into #425's scope.

## TC2 — Doc hygiene: §7.6.2 bundle-number reconciliation (LOW; doc-only)
**Recommendation:** §7.6.2 cites the pre-anchor bundle `gold_cycle_260603_173742` (rw 0.6149 headline /
0.5656 OOS). The live promoted bundle `gold_cycle_260608_043414` (anchor-active retrain) scores rw
0.6711 / 0.7127 on the same harness — materially narrower. §7.6.5 (added this run) notes this, but a
one-line cross-reference in §7.6.2 itself would prevent a future reader treating 0.6149 as the live
number. Route: minor doc follow-up (or fold into #425's doc update).

## TC3 — Observability: persist training seed in latent_power module manifest (LOW; reproducibility)
**Recommendation:** the trained module manifest does not persist the `--seed` in its config object, so
an ablation retrain is not fully reproducible from the manifest alone (G3 reviewer note). Persisting
the seed would close this. Route: small observability triage candidate (not in #451 scope).
