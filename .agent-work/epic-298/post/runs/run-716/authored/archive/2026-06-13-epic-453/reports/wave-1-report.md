# Epic #453 — Wave 1 Report (2026-06-11)

All three Wave-1 issues dispositioned: **2 shipped, 1 measured verdict** (the epic's explicit honest-null bar). Four PRs merged, all check-gated green (pyright/docs/arch-map). Main at `5d2c541` (+ LESSONS repair PR #462 in flight at writing).

## Results by issue

### #413 — train/serve skew guard (SHIPPED, PR #456)
`qs_compound_beta_regime` is now read from the gold artifact manifest at serving time:
- manifest `push` → runtime push-regime normalization
- field absent (legacy manifests) → named constant `DEFAULT_QS_COMPOUND_BETA_REGIME = "race"` (no silent inline fallback)
- invalid value → `ValueError` at parse time

The silent train/serve skew footgun is closed before #440 retrains anything. 38 focused + 1,739 evo unit tests green; zero file overlap with #410.

### #410 — pooled compound β fit (SHIPPED with honest null, PR #457)
Shipped: `scripts/build_pooled_compound_prior.py` + regenerated `params/gold/compound_prior/{2023,2024,2025}` from strictly-prior-season pooled observations (time-safe; schema and `CompoundNormalizer` interface unchanged; 221 tests green).

**Honest null:** the production solver does NOT produce a monotone β ladder even pooled (1–3 seasons). #382's "pooling recovers monotonicity" claim came from the gate's fixed-effects estimator — a different solver design (the production fit's γ terms, sparse prior, and age modifiers compete with β identification). What pooling DOES deliver, measured:
- 2023 β spread stabilized 0.027 → 0.005; the wild C5 outlier −0.026 → −0.0044 (gate reference −0.0055)
- qs_* push-regime injection co-validated: vendored gate constants unaffected; push-beta still improves cross-compound accuracy (+0.0017, 2024)

**Adopt ruling (Admiral):** pooled artifacts adopted — strictly better-identified than the measured-degenerate per-season fits; net effect on predictions is measured at the #440 walk-forward before any promotion (user holds the promotion veto). Risk stated openly: runtime normalization reads these artifacts live post-merge without per-change Brier evidence — accepted per the epic's accumulate-then-measure design.

### #451 — quali-channel under-extraction (MEASURED LOCALIZATION, PR #460)
**Verdict: (a) feature representation.** The race_weekend quali head's 23 input features do not contain (nor linearly encode) the cross-channel min-sector pace ordering whose data ceiling is 0.806:
| probe | result | reading |
|---|---|---|
| G1: linear readout of the head's own features | 0.6513 (~15pp under ceiling) | ordering not in the features |
| G2: + min-sector pace as a 24th input (OOS-2025) | 0.5868 → **0.7700** (ceiling 0.7643) | supplying it closes the gap |
| G3: 3× wider net, same features | 0.5880 ≈ control | capacity excluded |

Training signal excluded via prior measured art (#387 perfect transitive labels; §7.6.3 monotone-invariance). No fix shipped — correct under the scope fence (touches a promoted default). §7.6.5 added to the ceiling doc.

**Direct Wave-2 consequence:** #425 (explicit all-FP min-sector feature) is now evidence-backed as the principled repair, with two design inputs: add a `{name}_missing` companion indicator and consider a within-event-standardised variant. #394/#395 confirmed orthogonal (the missing signal is cross-channel pace, not form).

## Infrastructure / process items
- **PR #459** (Admiral, merge mechanics): fixed the single pre-existing pyright error on main (walkforward annotation) — typecheck had been red since #439, which would have poisoned every check-gate this epic. Main's pyright is green for the first time in days.
- **Concurrent traffic:** physics epic #445 merged PR #458 mid-wave → add/add conflicts on `.agent-work/AGENT_FEEDBACK.md` (resolved by union, ×2).
- **INCIDENT — LESSONS.md clobber (recovered):** PR #457 tracked a playbook generated in a worktree that lacked the canonical (untracked) file, replacing 14 lessons with 3 on merge. Repaired by restoring the canonical copy + mechanically re-applying cmdr-410's archived delta → 15 active / 1 dormant (PR #462). **Wave-2 pre-ruling locked:** commanders never commit LESSONS.md / AGENT_FEEDBACK.md on mission branches; deltas/entries return in reports for central application.
- Minor commander deviation: PR #457's body auto-closed #410 despite no-auto-close instruction (disposition comment added after the fact).

## Parked triage candidates (for closeout / user)
1. **FE-estimator integration into the gold β fit path** — the real monotonicity fix (#410 follow-up, medium).
2. §7.6.2 ceiling-doc number reconciliation — the doc's pre-anchor baselines (0.6149/0.5656) vs the live anchor-active bundle (0.6711/0.7127) (doc touch, low).
3. Persist training seed in module manifests (observability, low).
4. 2022 compound_prior artifact has no prior seasons to pool (data-availability note).
5. Inline argparse default literal vs named constant in run.py (cosmetic).
6. docs/report_schemas may lag the new manifest `runtime.qs_compound_beta_regime` field (doc, low).
7. `run_crew.py` launcher contract broken on stock CLI v2.1.173 — 2nd corroboration of issue-446's finding (constellation-scoped; routed via CONSTELLATION_FEEDBACK).
8. Engine `lease_stale_seconds` (1800s) shorter than one compute-heavy gate (constellation-scoped).

## Wave 2 plan
Dispatch #425 (Sonnet — now the evidence-backed repair for the #451 gap; carries cmdr-451's design inputs), #394 (Sonnet — design note, go/no-go), #395 (Sonnet — investigation note, pursue-or-drop). All parallel-safe; notes-only deliverables for #394/#395. Changes accumulate; no gold regens until #440.
