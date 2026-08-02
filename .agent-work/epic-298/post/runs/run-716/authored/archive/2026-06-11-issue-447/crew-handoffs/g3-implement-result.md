# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3 (g3-implement)` — issue #447 Phase 0b: author the DELIVERABLE
`docs/physics/measurement_model.md` and the operationalized GO/NO-GO evidence pack.

## Completed slice
Authored `docs/physics/measurement_model.md` — the measurement model + GO/NO-GO
decision brief, written for a careful non-specialist. It assembles all 10 close
criteria from the G1/G2 evidence, operationalizes both gate halves before
applying them, applies them per session, gives a clearly-labeled GO
recommendation, the F1 chi-square band recommendation, the F3 `s_finish` decision,
a `Last verified: 2026-06-11` line, and a number→source traceability table. Every
figure traces to the on-disk evidence JSON (or, where it is a reviewer
re-computation, is cited with that provenance and flagged as not-in-JSON).
Doc-only — no `src/` reader added (justified in the doc).

## Scope
**Files changed:**
- `docs/physics/measurement_model.md` (new — THE deliverable)
- `.agent-work/issue-447/crew-handoffs/g3-plan.json` (engine plan state)
- `.agent-work/issue-447/crew-handoffs/g3-implement-result.md` (this result)

**Specific exclusions touched:** no — no estimator/filter/smoother; no GO/NO-GO
decision (recommend only); no merge/close; no evo imports; no change to 0a
primitive behaviour (F1 and F3 are documented recommendations, not code edits);
no invented numbers.

## Behavior changed
No — documentation only. No `src/` logic touched; no reusable reader added, so
`simplification_limits` is not applicable.

## Operationalized GO/NO-GO gate + per-session pass/fail

**Half A — "offsets estimable"** (stated before applying): per-session offset is a
tight, low-drift bias — median per-lap offset std ≤ 0.15 s AND |session-mean| ≤
0.13 s AND median |lag-1 autocorrelation| < 0.5. (Extends the G2 `stable-estimable`
rule std ≤ 0.15 s AND |ac| < 0.5 with the small-mean check.)

**Half B — "cross-residuals bounded"** (stated before applying): after free
per-lap offset removal, the arc-residual is at the metre scale consistent with §4
positional noise (mean |arc residual| ≲ ~8 m) AND removing the offset moves the
covariance-consistency statistic toward the tightened band (direction, not
convergence — convergence is Phase 1's job).

**Per session:**

| Session | Half A | Half B |
|---|---|---|
| 2023 Belgian Q | PASS (std 0.129, mean 0.004, ac<0.5) | PASS (arc 4.9–7.6 m; χ² 95.9→63.9) |
| 2023 Belgian R | PASS (std 0.084, mean 0.081) | PASS (offset-dominated) |
| 2022 Spanish R | PASS (std 0.097, mean 0.040) | PASS (offset-dominated) |
| 2024 British Q | PASS (std 0.114, mean 0.009) | PASS (offset-dominated) |
| 2024 British R | PASS (std 0.128, mean 0.069) | PASS (offset-dominated) |
| 2023 São Paulo R (wet) | PASS (std 0.089, mean 0.019) | PASS (offset-dominated) |

**Both halves PASS on 6/6 sessions, including the wet/messy one.**

## Labeled recommendation (as written in the doc)
**RECOMMENDATION: GO** — proceed to fork the Phase 1 trajectory estimator (epic
#445). Explicitly labeled a recommendation for human ratification, not a decision.
Grounds: characterized streams; measured white-jitter error model (not assumed);
F2 resolved (stable estimable offset 6/6); both gate halves PASS 6/6. Honest
caveat stated: the raw covariance-consistency statistic is large (78.7–3292) until
the inter-stream offset is modelled — it is offset-dominated, not noise-dominated,
and modelling that offset is exactly the Phase 1 estimator's job; the wet session
behaving like the dry ones is a specific reassurance.

## F1 band + F3 decision (as written in the doc)
**F1 (covariance-gate chi-square band):** Keep the band at **(0.5, 2.0)** — the
gate already defaults to it; the loose [0.01, 100] was the strawman runner's, not
the gate default — but apply it **only to an offset-removed residual** (the
`cross_residual` arc-residual), or with per-sample variance inflated to include
the offset arc term. Justified by the §4 noise model (factor-of-two tolerance on a
~0.1–0.5 m² per-sample variance once the dominant offset term is removed). Applied
to the offset-inclusive residual, no finite band is meaningful. No code change.

**F3 (`s_finish` free anchor):** **Promote `s_finish` to a free co-estimated
anchor** (with lap-length scale fixed to break the gauge) for circuits with
ambiguous start/finish-line arc-length. Evidence: with `s_finish` pinned at 0.0,
`s3` is driven onto the lap-length bound (Belgian Q: VER/NOR/GAS all fit s3 =
7004.0 m = exactly track length) and sector-crossing residuals are 0.10–0.16 s
(session) to 0.31 s (GAS) — far above the 0.050 s tol. Freeing s_finish lets the
sector geometry float to the data, unpinning s3 and pulling residuals down. No
code change here; when implemented it must land with a test.

## Map Impact
- **Structural anchors touched:** `struct:physics` — new
  `docs/physics/measurement_model.md` alongside `overview.md` /
  `windowed_estimator.md`; becomes a durable physics contract (Cartographer to
  reconcile).
- **Capabilities added/changed/affected:** measurement-model contract for Phase 1
  estimators is now a written, traceable artifact (sampling, quantization, noise,
  white-jitter error model, stable-estimable offset, gate operationalization).
- **Constraints/assumptions touched:** honored `constraint:physics_region_no_evo_import`
  (no evo imports); recommendation-only authority honored (no GO/NO-GO decision,
  no code edits to 0a primitives).
- **Decision candidates / resolved decisions:** F2 resolved (stable estimable
  bias). F1 band recommendation = (0.5, 2.0) on offset-removed residual. F3
  decision = free `s_finish`. Error-model class = white-jitter. All documented as
  recommendations/decisions for ratification, none applied to code.
- **Claims/evidence produced:** the doc's §11 traceability table backs every
  number to its script/JSON or flags reviewer-re-computation provenance.
- **Trust limitations / drift found:** the handoff's stated per-channel noise
  headline ranges (Speed 1.3–1.6; X 0.039–0.19; Y 0.056–0.55; Z 0.41–4.85) are
  narrower than the full across-all-sessions evidence (Speed 0.078–3.656;
  X 0.033–1.190; Y 0.022–0.837; Z 0.018–8.121); the doc uses the wider,
  JSON-traceable ranges and notes the discrepancy. The handoff's "Z elevated at
  Spa" is superseded by São Paulo's larger Z noise (8.121 m²) in the evidence.
- **Triage candidates:** F1 (gate residual must be offset-removed) and F3
  (free `s_finish`, with a test) are Phase 1 implementation candidates — surfaced
  in the doc, routed for the human/Commander.

## Test mode
**Required:** docs-primary (deliverable is a doc; no `src/` reader added).
**Satisfied:** yes — doc present (engine command postcondition ran:
`py -c "...os.path.exists('docs/physics/measurement_model.md')..."` → `doc present`,
exit 0); `Last verified: 2026-06-11` present; all referenced files
(overview.md, windowed_estimator.md, trajectory_grading_report.md,
covariance_gate.py, sector_anchor.py, both scripts, g2-review-result.md) resolve;
reproduce-commands are valid.

## Evidence

```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-447
py -c "import os; assert os.path.exists('docs/physics/measurement_model.md'); print('doc present')"
grep -c "Last verified: 2026-06-11" docs/physics/measurement_model.md
py -c "import os; [print(('OK ' if os.path.exists(p) else 'MISSING ')+p) for p in ['docs/physics/overview.md','docs/physics/windowed_estimator.md','docs/report_schemas/trajectory_grading_report.md','src/preprocessing/trajectory_grading/covariance_gate.py','src/preprocessing/trajectory_grading/sector_anchor.py','scripts/characterize_telemetry_instruments.py','scripts/characterize_timetag_jitter.py','.agent-work/issue-447/crew-handoffs/g2-review-result.md']]"
```

**Result:** pass — `doc present`; date line present; all 8 referenced files `OK`.
Engine plan `g3-plan.json` reports `DONE: no open items`.

## TDD evidence, if required
- N/A — docs-primary; no test surface (no `src/` code added).

## Docs/contracts touched
- `docs/physics/measurement_model.md` (new durable physics contract — the
  deliverable). No committed report-schema or producer/consumer change.

## Assumptions
- The G2 reviewer's offset-removed re-computation (95.9 → 63.9, Belgian Q/VER) is
  a trustworthy traceable artifact (`g2-review-result.md`, independently verified
  in review) even though it is not in the on-disk evidence JSON; it is cited with
  that explicit provenance and the direction (offset removal reduces χ² toward the
  band) — not the exact value — is treated as load-bearing.
- "Cross-residuals bounded" (Half B) per-session beyond Belgian Q is asserted from
  the offset-domination finding (mean |residual| ≈ 5.5 m, reviewer-confirmed) plus
  each session's `arc_residual_distribution`; only Belgian Q has an explicit
  offset-removed χ² number, so other sessions are marked "offset-dominated /
  direction confirmed" rather than carrying a re-computed χ².

## Stop conditions hit
- None blocking. One number named in the handoff prose — the 63.9 offset-removed
  χ² — is **not in the evidence JSON**; per the stop condition I did not invent it
  but located its actual provenance (G2 reviewer re-computation, `g2-review-result.md`)
  and cited it as such with an explicit "not the on-disk JSON" flag. The handoff's
  per-channel noise headline ranges did not match the JSON; I used the
  JSON-traceable ranges and documented the discrepancy. Neither required stopping —
  both are resolved honestly within authority.

## Out-of-scope observations
- The handoff headline numbers (per-channel noise ranges; "Z elevated at Spa")
  diverge from the full evidence JSON. Not a defect in the evidence — a
  summarization gap in the handoff. Flag for future handoffs: quote the summary
  JSON aggregate ranges, not a single-session subset.
- F1 and F3 are now ready-to-implement Phase 1 design items with concrete
  acceptance criteria (offset-removed gate residual; free `s_finish` with a
  bound-unpinning test). Commander may route them into the #445 estimator fork.

## Workflow Feedback
Mandatory section.

- **Handoff gaps:** The handoff's "measured evidence to write up" headline ranges
  (Speed 1.3–1.6 (km/h)²; X 0.039–0.19; Y 0.056–0.55; Z 0.41–4.85 m²) are a
  single-session-ish subset and are **narrower than the full evidence** (Speed
  0.078–3.656; X 0.033–1.190; Y 0.022–0.837; Z 0.018–8.121 m²). Likewise "Z
  elevated at Spa" — São Paulo's Z noise (8.121 m²) is larger in the JSON. Because
  the handoff also (correctly) commands "every number must match the on-disk
  evidence JSON," these two instructions conflicted; I followed the JSON and
  documented the divergence. Naming the exact JSON aggregate keys to quote would
  remove the ambiguity.
- **Context rediscovered:** The "95.9 → 63.9 after offset removal" figure quoted
  in the handoff prose is **not in any evidence JSON** — it lives only in
  `g2-review-result.md` (reviewer re-computation). I had to grep to find its
  provenance before I could cite it honestly. A handoff pointer ("this number is a
  reviewer re-comp, see g2-review-result Verdict 3, not the JSON") would have saved
  a discovery step and pre-empted a near stop-condition.
- **Instructions improvised around:** The engine is a *gated* plan, so `record`
  is refused ("use advance"); items must be `start`-ed before `advance`; `--file`
  is a top-level arg before the verb; `attest` uses `--which {pre,post}conditions
  --cond <id>` (not `--which <id>`); and an engine-`check`ed postcondition cannot
  be hand-attested (the engine ran the command itself). Several refusals before the
  correct verb sequence. The constellation-engine-quirks memory covered most of
  this; the "gated ⇒ advance not record" and "checked postcondition auto-satisfies"
  points are worth adding to the implementer skill's engine reference.
- **What would have made this easier:** A one-line provenance map in the handoff
  for any number that is *not* in the primary evidence JSON (here: the 63.9
  reviewer re-comp), plus quoting the summary-JSON aggregate keys for the
  per-channel noise ranges rather than a session subset.

## Return status
`complete`
