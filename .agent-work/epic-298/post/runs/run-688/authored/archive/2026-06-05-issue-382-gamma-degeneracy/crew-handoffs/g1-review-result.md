# REVIEW_RESULT — G1 (β degeneracy root-cause)

## Verdict
**APPROVE**

## Per-check findings
- **r1 handoff compliance — PASS.** Script does what the handoff asked. Independent re-derivation (fresh SQL + numpy, no import of the script) reproduces all headline numbers.
- **r2 scope — PASS.** Only `scripts/diagnose_compound_beta_degeneracy.py` added; zero working-tree changes under src/. #380 seam untouched.
- **r3 evidence — PASS.** `beta_degeneracy.json` present and the numbers support the claim. Independent values: ridge collapse **0.18%** (script 0.2%), **8/8** seasons non-monotone, pooled ladder ordered, isotonic PAVA pools non-monotone γ into a plateau.
- **r4 quality — PASS.** DB-only, py, simplification_limits PASS, pyright 0/0, deterministic, --smoke fast path. Honest science: pre-registered H1 (ridge) refuted by data and reported as such.
- **r5 reconciliation — PASS** + NOTE (below).

## Independent re-derivation (the substance of the review)
Recomputed from raw `lap_times` SQL + numpy WITHOUT importing the diagnosis script:
- All-8 pooled β ladder: C1 −0.00278, C2 −0.00103, C3 −0.00104, C4 −0.00042, C5 +0.00079, C6 +0.00448 — **identical to the script**.
- Ridge collapse α=0→1.0: **0.18%** (script said 0.2%) — ridge-dominance refuted, confirmed.
- Pooled monotone (tol 5e-5): **True**; per-season non-monotone: **8/8** — confirmed.
- Isotonic PAVA on a non-monotone γ vector pools distinct 5→4 — mechanism confirmed.

## Blockers
None.

## Reconciliation NOTE for Commander (important)
origin/main advanced **13 commits** during the run. Commit **316f6c9 "Merge PR #400 from claude/compound-regime-feasibility"** means **§7 (incl. §7.4/§7.5), `docs/evo/compound_crossover_gate_findings.md`, and `scripts/fit_compound_crossover_gate.py` are NOW ON main.** This updates decision D1: the §7.5 doc note (G3) can append to the REAL §7. Recommend rebasing/merging onto current origin/main before G3 so the note lands correctly and I work against the merged gate artifacts. Also merged: #383 (entity_count) and median-relative pace-feature normalization commits.

## Out-of-scope observations / triage candidates
- Full component-by-component bisection of the iterative production fit (`fit_tire_wear_model`: baseline residualization + β-upper-bound −1e-6 + race-delta-gamma additive + sparse-prior + monotone-γ) was timeboxed out. The decisive lever (pooling) is established; a finer attribution of the *secondary* per-season distortions is a triage candidate.
