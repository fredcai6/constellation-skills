# Implementer Handoff — issue-414 G3

You are a fresh crew member. Implement exactly this bounded task. Do not read any transcript. Invoke the `constellation-implementer` skill and drive it.

Repo root (run all commands from here): `C:\Programs\f1Brainz\.claude\worktrees\agent-a82dd9d22cd9863fc`
Set `PYTHONIOENCODING=utf-8`. Python is `py`. This is a docs-only gate — no code, no background work.

## Gate
g3

## Task
Append a NEW subsection `### 7.6.3` to `docs/evo/prediction_ceiling_and_priorities.md`, IMMEDIATELY after the end of §7.6.2 and BEFORE `### 7.7`. §7.6.2 currently ends at the line just before `### 7.7 Exploratory follow-up — γ ...`. Insert the block below verbatim (it is final copy — do not paraphrase, do not edit numbers, do not rewrite §7.6/§7.6.1/§7.6.2/§7.7).

## Protected Intent
APPEND-SHAPED, docs-only. Zero production behaviour change. Do NOT touch any code, the manifest, `src/evo_predictor/fusion.py`, `src/evo_predictor/fusion_training/`, or `docs/evo/fusion_rework_findings.md`. Numbers are from the G2 evidence and are already verified — transcribe exactly.

## Exact text to insert (verbatim)
Insert exactly this, starting on a new line after §7.6.2's last paragraph and before `### 7.7`:

```markdown
### 7.6.3 Targeted-fix scoping (#414): a cross-channel pace anchor recovers the bulk — but globally, not per-context

§7.6.2 routed the residual `race_weekend` quali gap to #375 with a written note to
**scope a cheaper targeted fix first**: anchor the standalone head to the practice-pace
evidence it already receives, or recalibrate its per-context evidence weighting. #414
measures exactly that, **measurement-grade** (a flagged post-processor on the head's
inferred `pi`; no retrain, no production change), on the **identical shared non-tie pair
population** as §7.6.2. Harness `scripts/scope_quali_anchor_414.py` (DB-only; imports the
§7.6 ceiling builders and the §7.6.2 shared-pairs primitive — does not fork them); records
are the §7.6.2 gold-bundle inference records regenerated for this study (`pi` from
`gold_cycle_260603_173742_2018thru2024`, inference only). The `α=0` endpoint reproduces the
§7.6.2 baseline exactly (race_weekend headline 0.6153, EASY/far-apart 0.6926, 23 862 pairs);
the `α=1` endpoint equals the `best_across_fp` ceiling by construction and is **definitional,
not a model win**.

**Candidate C1 — cross-channel pace-anchor blend (the issue's named fix).** Per event,
`pi' = (1−α)·z(−pi) + α·z(−best_across_fp_minsector)` (z = within-event standardise; the
anchor is the *same* min-sector FP1/2/3 pace whose ceiling is 0.8061, i.e. the cross-channel
"who is generally fast" signal the head provably lacks). Sweeping α (shared pairs; recovered
fraction = `(acc(α)−baseline)/(ceiling−baseline)`):

| α | overall | rec-frac | EASY (gap≥9) | EASY rec-frac |
|---|---|---|---|---|
| 0.0 (baseline) | 0.6153 | +0.000 | 0.6926 | +0.000 |
| 0.1 | 0.6660 | +0.266 | 0.7706 | +0.320 |
| 0.2 | 0.6947 | +0.416 | 0.8062 | +0.466 |
| 0.3 | 0.7123 | +0.508 | 0.8243 | +0.540 |
| 0.5 | 0.7452 | +0.681 | 0.8691 | +0.724 |
| 0.7 | 0.7804 | +0.866 | 0.9125 | +0.902 |
| 1.0 (= ceiling, definitional) | 0.8061 | +1.000 | 0.9365 | +1.000 |

A **modest** anchor weight already moves the headline number a lot: α=0.2 recovers **42%** of
the overall gap and **47%** of the EASY/far-apart gap (the slice §7.6.2 localised the deficit
to); α=0.5 recovers **68% / 72%**. The EASY slice — the 0.687→0.937 deficit that *was* the
signature — closes fastest, confirming the diagnosis: the head was missing a general-pace
anchor, and supplying one from its own FP laps fixes most of the coarse-pair mis-ordering.

**Candidate C2 — rank-anchor robustness.** Blending within-event *ranks* instead of
standardised values gives the same picture (α=0.5: overall 0.7399, EASY 0.8737; rec-frac
+0.65 / +0.74), so the recovery is **not** a standardisation artifact.

**Candidate C3 — magnitude-only recalibration is a measured no-op.** Any strictly-monotone
within-event transform of `pi` (e.g. `3·pi+7`) leaves pairwise sign-accuracy **exactly
unchanged** (Δ = 0.0). This is decisive: pairwise sign-accuracy is invariant to how the head
*scales* its scores; it moves only when the **relative ordering** changes. So "recalibrate the
evidence weighting" (a magnitude lever) cannot, by itself, close this gap — only injecting a
**new ordering signal** (the cross-channel anchor) can. The lever is *information*, not
calibration.

**OOS 2025 confirms the pattern** (clean, 18 events, 3 352 pairs): C1 α=0.5 recovers +0.72
overall / +0.80 EASY (0.7097 / 0.8451 vs baseline 0.5674 / 0.6060, ceiling 0.7643 / 0.9055);
C3 Δ = 0.0.

**What this scopes for #375 — and what it does not.** The targeted anchor is genuinely
effective *and* genuinely partial:

- It **recovers the bulk** of the gap cheaply (≈68–72% at α=0.5) and **confirms the §7.6.2
  diagnosis** (general-pace anchor missing; deficit on coarse pairs).
- But the lever that works is a **single global blend weight** applied uniformly to every
  pair. §7.6.2's deficit is **context-dependent** (concentrated on EASY/far pairs, near-ceiling
  on hard adjacent ones). A global α is a crude proxy for the **per-context** weighting a
  conditioned net learns; at α=0.5 it also reaches the ceiling only by weighting the anchor as
  heavily as the head's own signal (and at α=1 it *discards* the head entirely). It does not
  **reconcile** the two signals per context, nor does it live inside the fused, calibrated,
  uncertainty-aware quali path — both of which are #375's job.
- The remaining ~30% sits where a global blend cannot reach without over-weighting the anchor
  on the pairs where the head is already near-ceiling — precisely the per-context trade #375
  conditions on.

**RECOMMENDATION: BOTH-STAGED.** Ship the targeted cross-channel pace anchor as a stage-1
fix — it is cheap, recovers the majority of the localised gap, and de-risks the rest — but
build #375 (the context-conditioned shared net) as stage-2 to capture the per-context
remainder and to fold the anchor into the principled fused/calibrated path rather than a hand-
tuned global α. The #414 measurement makes #375's scope **sharper**: stage-2's job is the
*per-context* weighting and signal *reconciliation*, not the discovery that an anchor helps
(stage-1 already banks that).

**#408 ABSORPTION: fold into #375 as the magnitude/uncertainty component — NOT a standalone
sign-accuracy fix.** #408 is a learned feature-to-gap-*scale* head; it predicts the *magnitude*
of the pairwise gap. C3 shows magnitude has **zero** leverage on pairwise sign-accuracy, so
#408 cannot be the targeted fix for the §7.6.2/#414 *ordering* gap. Its value is calibration
and uncertainty (gap scale feeds the fusion precision-weighting and the sampled runtime), which
is exactly the magnitude/uncertainty role inside #375. Absorb #408 there; do not pursue it as a
separate sign-accuracy lever.
```

## Close Criteria
- The block above is inserted verbatim as `### 7.6.3` between §7.6.2 and §7.7. `### 7.7` still follows it. §7.6/§7.6.1/§7.6.2/§7.7 are byte-identical to before (pure insertion).
- The verdict ends with the explicit `RECOMMENDATION: BOTH-STAGED` line AND the `#408 ABSORPTION:` line.
- All numbers match the G2 evidence (`.agent-work/issue-414-quali-head-scoping/evidence/scope_anchor_numbers.json` and `g2_scope_run.txt`). Cross-check the table you inserted against `g2_scope_run.txt` — they must agree.
- Zero production behaviour change; only the doc modified.

## Allowed Scope
- EDIT: `docs/evo/prediction_ceiling_and_priorities.md` (insert §7.6.3 only).

## Specific Exclusions
- Do NOT rewrite/reflow §7.6/§7.6.1/§7.6.2/§7.7. Do NOT touch any code, the manifest, fusion files, or `docs/evo/fusion_rework_findings.md`.
- Do NOT invent or adjust numbers. Transcribe the block exactly.

## Constraints
- Append-shaped insertion. Markdown must render (table columns aligned, fenced blocks closed).
- Docs reviewer rules: correct repo/domain, existing references valid.

## Required Evidence
- `git diff docs/evo/prediction_ceiling_and_priorities.md` showing a pure insertion (additions only; no deletions to existing sections). Report the added-line count and that §7.7 still immediately follows §7.6.3.
- A grep/confirmation that `### 7.6.3` exists and `RECOMMENDATION: BOTH-STAGED` and `#408 ABSORPTION:` lines are present.
- Confirmation that the inserted table matches `g2_scope_run.txt` (quote a couple of cells).

## Verification Commands
```
git diff --stat docs/evo/prediction_ceiling_and_priorities.md
findstr /n "7.6.3 RECOMMENDATION: #408" docs\evo\prediction_ceiling_and_priorities.md
```

## Suggested Model Tier
simple bounded — faithful insertion of final copy + a fidelity cross-check.

## Authority
The verdict (BOTH-STAGED) and the #408 absorption call are the Commander's, grounded in the G2 numbers. You transcribe; you do not re-decide the verdict or alter numbers. If the numbers in the block disagree with `g2_scope_run.txt`, STOP and report (do not silently "fix").

## Stop Conditions
Stop and return if: the insertion would require changing an existing section; the block's numbers disagree with the G2 evidence; you would need to touch an excluded file.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, added-line count, confirmation §7.6.3 is between §7.6.2 and §7.7, the recommendation + #408 lines present, the table-vs-evidence cross-check, assumptions, stop conditions hit.
