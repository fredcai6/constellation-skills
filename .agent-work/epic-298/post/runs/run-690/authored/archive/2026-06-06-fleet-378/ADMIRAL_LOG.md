# Admiral Log — Epic #378 Fleet (Thrust A: quali mean resolution)

Admiral: orchestrating session (Opus), user delegate. Commanders: one per child issue,
constellation-commander skill, own worktree, sonnet crews. Doctrine: charge around
blockers, log every adjudication here, escalate only genuinely-human calls.

## User-approved parameters (2026-06-05)
- Admiral merges green, pre-reviewed PRs to main autonomously; every merge logged here.
- Waves: 1 = {#379 #380 #382 #383 #384} parallel · 2 = {#381} after #379+#380 merged · 3 = {#391} after #381, reconciled.
- Commanders' subagents run model=sonnet (user directive).
- Merge gate: PR checks are NON-REQUIRED in this repo (main can go red) — Admiral verifies
  pyright + tests green via `gh pr checks` before merging, never relies on GitHub blocking.

## Pre-rulings
| # | Ruling | Rationale |
|---|--------|-----------|
| R1 | #380 injects gate-β behind normalizer interface; no compound_prior re-fit | Fitter is #382's territory; avoids two commanders in one module |
| R2 | #384 aligns consumer→producer (rank_mae+nll) unless design intent for brier/log_loss found | Issue offers both; emitted truth is the conservative default |
| R3 | #381 delivers attribution only, never builds Piece 2 | Epic routes the build to #375 (fusion epic) |
| R4 | #391's #387 coordination fork goes to the user at wave 3 | Genuine cross-epic design call |
| R5 | Missing harnesses (gate fit, quali-evidence) consumed READ-ONLY from `claude/compound-regime-feasibility` via `git show` / scratch copies; never base a branch on it; findings docs = stable reference, scripts = best-effort (branch tip changed encodings) | User-approved 2026-06-05 ("1 is fine"); zero interference with in-flight #368 |

## Launch record
- 2026-06-05: Hold lifted. #369 merged (PR #399), #371 merged (PR #398 — #381's record-dump dep now real). Main checkout on fresh origin/main (fa9e48b).
- Wave 1 dispatched 2026-06-05: five commanders (opus, sonnet crews), isolated worktrees, background.
  cmdr-379 (practice evidence) · cmdr-380 (regime β) · cmdr-382 (γ degeneracy) · cmdr-383 (entity_count) · cmdr-384 (σ key sets).
  Each ordered to branch `constellation/issue-NNN-<slug>` off origin/main (fa9e48b), open PR, not merge.
- WAVE 1 COMPLETE 2026-06-06: #383→#401, #384→#402, #382→#404, #379→#405, #380→#403 all merged; main db426c6.
- Wave 2 dispatched 2026-06-06: cmdr-381 (same-pairs dual-ceiling diagnostic), base db426c6, R3 boundary,
  retrain-needs-approval stop-condition. Wave 3 (#391) remains gated on #381 + user escalation R4.

## Standing notes
- 2026-06-05 (user, CORRECTED from #370): **#368** (median-relative pace encoding drive-home,
  branch `claude/compound-regime-feasibility`) in work externally, lands soon.
  → Before dispatching each wave: fetch + confirm main current.
  → CRITICAL ADJACENCY: that branch is the sole home of `scripts/fit_compound_crossover_gate.py`,
    `scripts/diagnose_quali_evidence.py`, and both findings docs — referenced in #379/#380/#382
    standing orders but ABSENT from main. Not dead-blocking: `docs/evo/prediction_ceiling_and_priorities.md`
    (on main) carries the measured numbers. Rulings to affected commanders at their first return
    (SendMessage unavailable mid-run).
  → #368 tip makes median-relative the SOLE pace-feature encoding (removes minmax) → reshapes
    normalization plumbing → cmdr-380 (qs_* normalization) and possibly cmdr-379 PRs will need
    rebase + re-validation if #368 lands first. Merge order preference: #368 before #379/#380.
- 2026-06-06Z RESOLUTION: #368 LANDED as PR #400 (03:41Z), 9 min before #401 merged. R5 is MOOT —
  harnesses + findings docs now on main. New main also pre-implements sprint FP1+SQ short-run
  buckets in the lap pipeline (part of #379 Part A territory). #380/#382/#384 still run from
  fa9e48b bases: expect rebase + ground-shift reconciliation at their return.

## Commander returns
| When | Commander | Outcome |
|------|-----------|---------|
| 2026-06-05 | cmdr-383 | ✅ PR #401. Producer fix in evaluate_labeled_batches (row-level entity_count), 6 tests, 106 targeted green, pyright-clean on touched files, dof engagement demoed (β grid optimum 0.1 vs inert with None). Lane respected. Triage candidates tc1 (pair_count also None, low) + tc2 (committed details.json stale until next gold cycle) deferred. |
| 2026-06-06 | cmdr-380 | ⚠️→🔄 PR #403 opened: R1 honored (new compound_push_regime.py, fitter untouched; vendored β with provenance; two-normalizer routing at bucket split; default-preserving toml flag; +0.55pp cross-compound vs +0.29pp overall, 322 tests, pyright clean). BUT base = fa9e48b: never saw #400's preprocessor rewrite → PR CONFLICTING (7 files), validation measured on OLD encoding. cmdr-380b dispatched into same worktree: rebase + RE-VALIDATE on median-relative encoding, stop-conditions on bucket-split disappearance and on β effect not surviving. Triage routed: tc(decompose compute fns — #379's lane, held) + Admiral-captured tc(train/serve skew footgun: qs_compound_beta_regime not manifest-plumbed at runtime — flag flipped in training without runtime knowledge = skew; held) |
| 2026-06-06 | cmdr-381c | ✅ PR #406 (scripts+tests+docs, zero prod change). HEADLINE FINDING — prior INVERTED: recent_history is the STRONG channel (0.7803, +0.026 off ceiling); standalone race_weekend head is the weak one (0.6149, +0.191 off 0.8061 ceiling on IDENTICAL pairs); failure concentrated on EASY far pairs (0.687 vs ceiling 0.937, 31% mis-order) = missing cross-channel pace anchor = evidence-weighting deficit. OOS 2025 confirms (0.5656/0.7515 vs ceilings 0.7643/0.7709). Fusion delta honestly OMITTED (no committed fused quali artifact). ROUTING: #375, scope cheaper rw-head fix first. RANK-BLEND TC: HOLD (0.6pp vs 19pp). §7.6.2 appended. Debris from 381b in main checkout deleted by Admiral (3 superseded drafts; final versions on branch) |
| 2026-06-06 | cmdr-381 | RULINGS on its 5 interrogation forks — ALL RECOMMENDED DEFAULTS APPROVED: Q1(c) score BOTH populations with ceiling recomputed on identical event sets, headline 2018–2024 LOSO-held, 2025 as clean-OOS confirm; Q2 backtest --emit-module-record inference on existing bundles ≈ NOT a retrain (annotation: check in if >~1h wall-clock per bundle); Q3 standalone same-pairs per channel primary + fusion delta corroboration (annotation: if committed fusion artifacts can't support it cheaply, report standalone alone and SAY SO — no approximating); Q4 driver-primary, constructor only if cheap; Q5 dual-ceiling per standing order | Population-overlap subtlety (LOSO in-sample vs 2025 OOS) is real and (c) is the only honest framing; "same events, same pairs" invariant enforced both ways |
| 2026-06-06 | cmdr-379c | ✅ PR #405 (2 docs + 1 test, zero prod code — verification-shaped per Q2 ruling). Part A: confirmed landed by #368 (FP1+SQ short-run routing; existing coverage verified, no duplicate tests; stale practice_preprocessor.md "FP1-only" section rewritten). Part B: pooled-min recipe pinned by discriminating regression test; rank-blend deferred to #375 via gated tc (blocked on #381, ~0.6pp). All 5 rulings executed; §7.6→§7.6.1→§7.7 conflict vs #404 self-resolved. Quirk: engine `current` crashes on cp1252 printing ≈/§ → PYTHONIOENCODING=utf-8 |
| 2026-06-06 | cmdr-382 | ✅ PR #404 (docs+scripts only, no prod code, D2 no defaults flipped). β degeneracy = per-season vs pooled identification (§1.3 ridge REFUTED at 0.2%; 8/8 seasons non-monotone at ridge=0; ladder only pooled, spread 0.00726). γ = resolved-but-confounded (VIF 2.5, 4/5 pairs >2SE, ALL wrong-signed) ⇒ better fit cannot rescue. **Piece 3: PARKED→effectively CLOSED on physics grounds — USER RATIFICATION NEEDED at closeout** (§7.7 note appended). Self-merged main mid-run (D1). Seam clean; co-validate #380's vendored β if tc1 pooled-fit ever lands. Triage held: tc1 pooled/rolling gold β fit (medium, THE fix), tc2 de-confounded γ gate (low), tc3 solver bisect (low) |
| 2026-06-06 | cmdr-384 | ✅ PR #402. _SIGMA_ERROR_CORR_KEYS → producer-emitted (nll, rank_mae) per R2; exception ruled out 3 ways (grep, git log -S, gold_report_schema.py); structural producer≡consumer pin proven by mutation; drifted fixtures converted not deleted. SELF-REBASED onto post-#400/#401 main mid-run, resolved §6.2 conflict vs #383, re-verified 79+63 tests. Triage: simplification-limit debt in render_module_uncertainty_diagnostics_markdown (low, held). |

## Commander returns (wave 3)
| When | Commander | Outcome |
|------|-----------|---------|
| 2026-06-06 | cmdr-391c | ✅ PR #409. HONEST NULL, properly priced: neither carry-forward beats global-constant (cf1 0.003258 ~tied vs 0.003255; cf2 0.003825 worse) → shipped default = global constant; label ceiling 0.001949 = ~40% headroom exists but needs the learned head. Flat-ordering EMPIRICALLY confirmed (sign-acc 0.938776 identical across all 4 scales, spread 0.0). #386 contract delivered (expected_gap_ij + label s_e + §9.6 + packet). 54 tests, pyright clean. DEVIATIONS: (1) filed #408 autonomously (contra held-triage pattern; well-formed, cross-linked — user to keep/fold at closeout); (2) cwd slip during G1, self-corrected, main checkout verified clean by Admiral |
| 2026-06-06 | cmdr-387b | ✅ PR #407. s_e spread target built per user order sheet: CV 0.80 quali / 0.31 race / 0.35 race_start (vs 0.001 retro) — event-conditioning restored. Race observable = integrated green-flag pace gap, WON by measurement (~13× dynamic range; final-gap baseline collapses + caution-fragile). track_status verified in DB 2021–25 (proxy = tested fallback). Disagreement rate separate field (3%/16%/19% quali/race/race_start). Artifact params/spread_target/<y>/<r>/<phase>.json × 340, mirrors retro_truth; deterministic via scripts/build_spread_target.py. 86 tests, pyright clean. Internal review caught real caution-transition bug. Lane respected. Triage: 3 recs held (2 likely dupes of #386/#391 scope, 1 low 2018-data note) |
| 2026-06-06 | cmdr-387 | 🛑 MANDATORY STOP at understand (as ordered). MEASURED: option 1 (re-solve) structurally CANNOT restore spread — λ-sweep 1.0→1e-4 leaves cross-event CV≈0 (uniform scaling only); ordering perfectly preserved (Spearman 1.000, 0/127k+ flips) so the feared churn is dead; root cause = binarization discards finishing-gap magnitude upstream of solve (all 173 events are upset-free transitive tournaments ⇒ BT spread forced constant). Recommendation: option 2 (external DB-side spread target) is the only signal carrier. Consequence: #391 will NOT inherit restored-magnitude labels. No tracked changes, no PR (correctly premature). Engine blocked-at-understand, authority Admiral. ESCALATED TO USER (overturns their stated lean) with Admiral pre-rulings D2=build-now, D3=normalized median-relative-consistent statistic, DB-side as-of, evo lane |

## Wave 3 rulings (user-ratified 2026-06-06, after discussion)
- D1: option 2 accepted — external spread target; ordering labels untouched. User's framing: "widening the gaps, not training a new order."
- D2: build the artifact in #387 now.
- D3 order sheet: (1) fraction-of-SAME-median units, reuse #368/#369 machinery, no seconds; (2) exchange-rate frame gap̂≈s_e·Δpi, s_e dimensionless, spread target is a post-event label; (3) race observable = integrated clean-lap pace delta (primary) vs final gap (baseline), chosen by measured discriminating power + late-caution robustness; (4) actionable laps via DB track status if present, else field-median-spike caution proxy, NO new collection; (5) per-event median-of-ratios estimator, positive floor as guardrail only, clamped events flagged; (6) pace-vs-finish disagreement rate recorded SEPARATELY for Thrust B σ (user: don't launder noise into scale); (7) quali s_e from session-best gaps = #391's clean consumer; (8) DB-side derivation, evo lane.

## Decision log (adjudications on user's behalf)
| When | Commander | Decision | Why |
|------|-----------|----------|-----|
| 2026-06-06 | cmdr-391b | PLAN APPROVED w/ one correction: candidate ŝ_e (carry-forward prior s_e) ≡ its proposed persistence baseline → baseline set reduced to global-constant (the must-beat bar); ADDED a second carry-forward variant — same-circuit prior-year s_e — IF trivially cheap (same artifact, different key), winner picked by measurement (spread is plausibly track-structured: Monaco vs Monza). All other defaults approved as planned (pure module, byte-identical default, feature→s_e head deferred to triage as #375-shaped, #386 contract = phase-agnostic expected_gap function + label-s_e reference, no retrain, G1/G2/G3 gates) | Vacuous self-comparison caught at approval; circuit-keyed variant is the better "smallest mechanism" candidate and costs nothing |
| 2026-06-06 | cmdr-391 | RULED (A): #391's measurement = GAP-MAGNITUDE error (predicted s_e·Δpi vs observed gap, fraction-of-median, midfield-sliced, OOS), with the bar = event-conditioned predicted scale must beat a GLOBAL-CONSTANT-scale baseline; ordering KPIs reported as expected-flat decoupling evidence. (B) rejected — ordering work is #375. Issue's literal acceptance metric reconciled (was algebraically unsatisfiable under ratified semantics) | User's ratified design ("widening gaps, not training a new order") already implies order-invariance; issues are revisable problem statements. Flagged for closeout ratification |
| When | Commander | Decision | Why |
|------|-----------|----------|-----|
| 2026-06-05 | cmdr-383 | Accepted unit-level dof-engagement demo in lieu of full gold cycle | Pre-allowed in standing orders; full cycle is hours of CPU for no extra proof |
| 2026-06-05 | cmdr-383 | tc1 (pair_count=None) + tc2 (stale committed details.json) HELD for user batch adjudication, not filed as issues | Low priority, no fleet dependency; issue-filing is user-visible — batching for closeout |
| 2026-06-06 | fleet-wide | SYSTEMIC #2: a commander run ENDS at its final message — background shells die/orphan with it, no notification returns. cmdr-381b lost itself this way mid-inference (data survived: 48/48 record files landed). All future commander prompts carry a FOREGROUND-ONLY order for required work | Burned one dispatch learning it; cheap fix |
| 2026-06-06 | fleet-wide | SYSTEMIC: commanders have no nested agent-dispatch tool — "sonnet crews" directive physically unsatisfiable; crews run in-context on the commander (opus) with role discipline per the engine's documented fallback. Accepted; surfaced to user (cost implication: all crew work bills as opus) | Restructuring mid-wave (Admiral dispatching sonnet crew directly) would split the constellation spine across agents; not worth it |
| 2026-06-06 | cmdr-384 | Triage candidate (render fn simplification debt, low) HELD with the other tc's for closeout batch | Same rationale as cmdr-383's |
| 2026-06-06 | cmdr-379b | RULINGS on its 5 surfaced reconciliation questions: Q1 Part A = already landed by #368, accept with pinning evidence (no duplicate tests). **Q2 Part B = DEFER rank-blend to #375** + pin CURRENT pooled-min recipe with regression test + gated triage candidate (0.6pp: blend_rank 0.8029 vs best_across_fp 0.7968) + §7.6 append note. Q3 = 2021 sprints [FP1,FP2]. Q4 = KPI satisfied by ceiling measurement + honest no-model-change verdict. Q5 = author fresh notes | Q2 rationale: (a) reconciliation dissolved the dilution premise (production ≈0.797 pooled-min, not 0.790 FP3-only — epic's 1.9pp is really 0.6pp); (b) epic assigns evidence-weighting to Piece 2/#375; (c) STRONGEST: changing qs_* inputs now shifts the trained module's input distribution immediately before #381 measures that exact model. CONSEQUENCE for wave 2: #381 must score model vs BOTH ceilings (production recipe + blend_rank). Narrows a written acceptance criterion — flagged to user |
| 2026-06-06 | cmdr-379 | STOPPED mid-run and RELAUNCHED on fresh main | #400 (#368) rewrote its exact target files (_compute.py, _lap_pipeline.py) and pre-implemented sprint FP1+SQ buckets mid-flight; its plan + in-progress recipe test were built on deleted code. Old worktree kept for forensics: .claude/worktrees/agent-a863d149675f0dde2. Relaunch carries explicit reconcile-against-#368 orders; sized-down mission allowed ("already satisfied" verdict per part is a valid outcome) |

## Merge log
| When | PR | Issue | Verification before merge |
|------|----|----|---------------------------|
| 2026-06-06 03:50Z | #401 | #383 | Internal reviewer ✓ · 106 targeted tests ✓ · diff spot-checked by Admiral (6-line producer fix) · CI: docs/arch-map/pyright all pass (verified via gh pr checks; checks non-required so actively gated) |
| 2026-06-06 | #409 | #391 | Internal review ✓ · 54 tests ✓ · footprint verified · CI all green incl. pyright · CLEAN. FLEET COMPLETE — all 8 issues merged, all epic children closed |
| 2026-06-06 | #407 | #387 | Internal 3-gate review ✓ (caught real caution-transition bug) · 86 tests ✓ · footprint verified locally (340 artifacts + 8 real files, purely additive) · CI all green incl. pyright · CLEAN. WAVE 3a COMPLETE |
| 2026-06-06 | #406 | #381 | Internal 3-gate review w/ independent raw re-derivation ✓ · 7 tests ✓ · footprint verified (scripts+tests+docs, zero prod change) · CI all green incl. pyright · CLEAN. WAVE 2 COMPLETE |
| 2026-06-06 | #403 | #380 | Internal review ✓ · 347 targeted tests post-rebase ✓ · re-validated on NEW encoding (+0.60pp cross / +0.26pp overall, monotone-invariance argument verified) · β constants ≡ on-main findings doc · CI all green · CLEAN |
| 2026-06-06 | #405 | #379 | Internal review ✓ · 57+98 targeted tests ✓ · footprint verified (2 docs + 1 test, zero prod code) · CI all green incl. pyright · CLEAN |
| 2026-06-06 | #404 | #382 | Internal 3-gate review ✓ · docs+scripts only, zero prod code, no defaults flipped · diff footprint verified by Admiral · CI all pass incl. pyright · self-merged main mid-run so MERGEABLE clean |
| 2026-06-06 | #402 | #384 | Internal reviewer ✓ · 79+63 targeted tests post-rebase ✓ · diff spot-checked (key-set swap + comment) · CI all pass incl. pyright · self-rebased on post-#400/#401 main. Quirk found: subagent shell cwd LEAKS into Admiral's persistent shell on completion — post-merge commands ran inside cmdr-384's worktree (harmless: reads + branch ff). Countermeasure: Set-Location to repo root after every commander return |

## Closeout — triage dispositions (user-approved 2026-06-06, executed)
- FILED: #410 pooled multi-season β fit (medium, co-validate w/ #380 vendored β) · #413 train/serve skew guard (manifest plumbing) · #411 de-confounded γ reopen gate (low) · #412 compute-fn decomposition (low).
- COMMENTED: #375 (routing input: §7.6.2 target + rank-blend HOLD folds in + #408 absorption candidate) · #362 (stale details.json entity_count/pair_count covered by regeneration).
- DROPPED: render-fn complexity (#384 tc), solver bisect (#382 tc3), 2018 track-status note (#387), 2 #387 recs duplicating #386/#391 scope.
- #408 (filed by cmdr-391c): kept, cross-linked from #375 comment — final keep/fold is user's at ratification.

## Escalations to user
| When | Topic | Status |
|------|-------|--------|
| (pre-logged) | #391 label-magnitude fork (#387 coordination) | RESOLVED 2026-06-06: user chose "fix the training labels" → #387 DRAFTED INTO FLEET from epic #386 as wave 3a, #391 re-gated behind it. User's lean (option 1, re-solve) passed to cmdr-387 as lean-not-mandate; don't-pre-pick + don't-perturb-ordering caveats bind; option-1-fails finding is a mandatory STOP back to user |
