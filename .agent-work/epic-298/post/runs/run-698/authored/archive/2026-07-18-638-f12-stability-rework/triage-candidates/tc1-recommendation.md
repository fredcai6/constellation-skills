# Triage recommendation — tc1

## What
`docs/architecture/packets/physics.md` documented the Phase-1 F12 gate with the pre-#638
raw-space constants/behavior (`RADIUS_SCALE_M = 50.0`, `fit_property_mixture` `k_range=(2,6)`,
"F12 FAILED on real data", rollup k=3). After the #638 rework these are stale.

## Classification
stale generated map (architecture packet drift).

## Importance
Medium — the packet map is the agent-facing structural source of truth; a stale F12
FAIL/RADIUS_SCALE_M would mislead a future agent planning against layer2.

## Evidence
- Flagged by both the g2 implementer and the g2 reviewer (`docs/architecture/packets/physics.md:979`
  RADIUS_SCALE_M=50).
- Source now: `mixture_stability.py` uses `LOG_RADIUS_SCALE=0.30`; `property_mixture.py` fits in
  log space with `k_range=(2,4)` + OR support arm; real-data F12 = PASS 5/5.

## Acceptance criteria
- Packet reflects: log-radius fit, `LOG_RADIUS_SCALE=0.30`, `k_range=(2,4)`, OR support criterion,
  F12 PASS (5/5, k=4); #625 FAIL preserved as history. `check_arch_map.py` OK.

## Out of scope
Source changes (already done in #638 commits 46dc1e28/de2e7420).

## Disposition: FIXED-NOW
Cleared the fix-now ladder (bounded doc edit; adjacent — it WAS the reconcile step's scope;
verifiable via `check_arch_map.py`; no production/structural impact — reconcile handled the
structural record). Fixed in the reconcile step by the Cartographer.
Fix commit: **01c367c8** (`docs(architecture): reconcile physics packet map to #638 F12 PASS`)
— also updated the `index.md` journal. `check_arch_map.py` → OK (commander re-ran).

No repo issues to file this run.
