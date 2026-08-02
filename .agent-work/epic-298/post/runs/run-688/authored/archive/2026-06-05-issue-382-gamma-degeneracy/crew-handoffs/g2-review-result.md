# REVIEW_RESULT — G2 (measured γ identifiability)

## Verdict
**APPROVE**

## Per-check findings
- r0/r1 — PASS. Delivers the measured γ verdict asked (corr/VIF vs φ, SE, separation, profile likelihood, condition number); imports G1 loaders.
- r2 scope — PASS. Only the new script added; no src change; #380 seam untouched.
- r3 evidence — PASS. Independent re-derivation reproduces γ/SE/corr_phi exactly. Profile-likelihood independently validated.
- r4 quality — PASS. DB-only, py, simplification PASS, pyright 0/0, deterministic, --smoke. Honest: says NOT RECOVERED, sharpens (not overclaims) the gate.
- r5 reconciliation — PASS. scripts/ harness, no contract impact.

## Independent re-derivation (substance)
Recomputed γ from raw SQL + numpy WITHOUT importing the γ script — exact match: C1 +4.170e-4 (se 1.088e-5, corr_phi +0.226) ... C6 +1.277e-4 (se 2.289e-5, corr_phi −0.015). monotone-up False, monotone-down predominantly (one unresolved C2→C3 uptick).
Profile-likelihood validated: for C6 the profile 95% half-width 4.35e-5 ≈ 1.96·SE 4.49e-5 — correct linear-Gaussian behavior (profile slightly tighter from re-optimizing nuisance params).

## Verdict assessment
The measured verdict — **γ NOT RECOVERED; limit is CONFOUNDING not poor identifiability** (VIF 2.5 moderate, 4/5 pairs separable >2 SE, profile CI excludes zero, but all 4 resolved pairs point DOWN = wrong sign) — is correct and well-supported. It is a genuine refinement over the gate's qualitative "non-monotone, spec-sensitive": it pins the failure as confounding (wrong-signed but well-resolved), not sampling noise.

## Blockers
None.

## Out-of-scope / triage
- Per-race φ and stint-phase-controlled variants (which the gate showed degrade γ further) not re-run — timeboxed. Confirms direction; a fuller confounding decomposition is a triage candidate.
