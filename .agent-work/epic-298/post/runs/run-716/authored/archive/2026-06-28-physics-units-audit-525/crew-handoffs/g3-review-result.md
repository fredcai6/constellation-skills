# Review Result — #525 G3

## Assigned Gate
`g3-review` — issue #525, branch `feat/physics-units-audit-525`. Docs-only gate.

## Result
`APPROVE`

## Handoff compliance
Handoff requested two deliverables: (1) new `docs/architecture/reference/physics-unit-conventions.md` with a unit-convention table, `_g`/`_ms2` rationale, fit-vs-apply split, and single conversion boundary section; (2) `docs/AGENT_GUIDE.md` extended with one direct reference + a standing review-and-update mandate. Both delivered exactly as specified. `Last verified: 2026-06-27` present. Stop conditions: none hit.

## Scope drift
Clean. `git diff HEAD -- src/` is empty. Only two doc files changed: `docs/AGENT_GUIDE.md` (modified) and `docs/architecture/reference/` (new untracked directory). No specific exclusions were touched.

## Evidence verdict
Integrate check re-run independently — exit 0 confirmed (doc exists + `physics-unit-conventions` substring present in AGENT_GUIDE). Implementer's name spot-check table independently re-verified for all handoff-required fields against source (see r3-evidence and r6-doc-accuracy checks). Evidence is sufficient; behavior is docs-only so no TDD required.

## Code/doc quality
- `Last verified: 2026-06-27` present at doc top.
- No `python` invocations in the doc (reference table, no code examples — correct).
- One job per doc: solely a physics-parameter unit reference.
- Current truth only: old cryptic names (`A0`, `A2`, `theta_*`, `a_b`) appear only in line 5 in the "they are gone" context; not presented as current fields anywhere.
- `docs/AGENT_GUIDE.md` stays thin: two sentences + mandate, no content duplication.

## Map impact verdict
- **Evidence supports claimed change:** Yes. The produced doc accurately records the post-G2 renamed fields, the sanctioned conversion seam, and the fit/apply split. No overclaiming.
- **Constraints not violated:** Yes. Docs describe current truth (post-rename). One job per doc respected. `py` not `python` in examples (no examples in this doc — no constraint to violate).
- **Notes match the diff:** Yes. Map Impact claims: new file under `struct:physics` documentation; `docs/AGENT_GUIDE.md` extended with pointer; `decision:ideal_lap_sim_two_sided_evaluator` and `claim:lateral_car_prior_boundary_conversion` recorded as anchored. All match the diff and the new doc content.
- **Decision candidates surfaced:** Yes. Banking asymmetry and k_tire fit/apply gap named as cross-references to open issues (#527, #511) rather than implicit assumptions — correct escalation path.
- **Durable context routed:** Yes. Triage candidate (DOCUMENTATION.md index gap) flagged by implementer and in this review.

## Reconciliation check
No structural divergence. The new `docs/architecture/reference/physics-unit-conventions.md` adds a durable reference under `struct:physics` documentation — additive, not conflicting. `docs/AGENT_GUIDE.md` is extended at the end; no existing content modified.

One Cartographer-level gap flagged as triage candidate: `docs/DOCUMENTATION.md` does not yet list the new reference doc under Active Domain Reference or Architecture (see Out-of-scope observations).

## Blockers
- none

## Out-of-scope observations
- **DOCUMENTATION.md index gap:** `docs/DOCUMENTATION.md` lists all active domain reference docs but does not include `docs/architecture/reference/physics-unit-conventions.md`. The doc already exists and is referenced from AGENT_GUIDE; the index is just stale. A Cartographer pass or a small dedicated triage issue should add a row for it. Not a blocker for this gate (scope was two files only, and the implementer correctly flagged it as out-of-scope).

## Per-check findings

| Check | Result | Key finding |
|---|---|---|
| r0-context | pass | Handoff, diff, and implement result read; source spot-checked |
| r1-handoff | pass | Both deliverables present; Last verified 2026-06-27; all sections as specified |
| r2-scope | pass | git diff HEAD -- src/ empty; only docs/ changed |
| r3-evidence | pass | Integrate check exit 0 confirmed; 7 field names independently re-verified against source |
| r4-quality | pass | Last verified present; one job; post-rename names only; thin AGENT_GUIDE |
| r5-reconciliation | pass | Map Impact accurate; triage candidate correctly flagged; no structural divergence |
| r6-doc-accuracy | pass | All 10+ handoff spot-check fields confirmed (estimate_store.py, physics_data_models.py, fit_store.py, constants.py, car_prior.py); old names retired not current |
| r7-rationale | pass | _g/_ms2 rationale correct; Jacobian diag(G, G/rho) verified in car_prior.py L460; Monaco 17→63 m/s example matches code comment |
| r8-fit-apply-split | pass | Density/banking/tyre-decay rows accurate; #527 title confirmed ("banking normalized at fit but never re-applied"); #511 title confirmed ("grip-evolution state") |
| r9-agent-guide-wiring | pass | One section; one reference; resolves; mandate explicit; stays thin |

## Workflow Feedback
- **Handoff gaps:** The handoff's "Survey State Location" field was not explicitly named — it said `'.agent-work/<work-id>/<gate>-review/review.json'` in the skill template but the handoff did not repeat it. Reasonable inference: `.agent-work/525/g3-review/review.json`. No friction in practice.
- **Context rediscovered:** `lateral_view.py` L139 is cited in the fit-vs-apply table but the handoff didn't confirm the exact line number. Had to grep `lateral_view.py` was not explicitly in the handoff spot-check list — I verified via the doc text and car_prior.py comments instead (which cross-reference L139). Minor.
- **Instructions improvised around:** The skill says to use the engine's `scripts/checklist_engine.py` — done. The `config_ref: docs/agents/engine-config.json` in the survey JSON points to the repo config; the engine resolves it from cwd on the Windows shell (absolute path prefix used in all engine calls to avoid cwd ambiguity).
- **What would have made this easier:** The handoff's "Close Criteria" section uses an internal numbering error (two items numbered 3). Not confusing in practice but worth fixing in future handoff templates. One concrete change: assign criterion numbers sequentially (1-5, not 1-3-3-4-5).

## Return status
`complete`
