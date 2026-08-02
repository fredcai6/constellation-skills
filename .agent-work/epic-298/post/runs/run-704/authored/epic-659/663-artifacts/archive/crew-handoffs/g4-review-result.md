# Review Result — g4-review (GATING acceptance gate, issue #663)

## Assigned Gate
`g4-implement` reviewed for `g4-review` — held-out cross-session reconciliation GATING harness, `tests/unit/physics/layer2/test_grip_heldout.py`.

## Result
**APPROVE**

## Independent determination: is the negative REAL or an ARTIFACT?
**REAL.** The measured negative (subtracting G worsens held-out cross-session reconciliation by +155.5%, 0/4 circuits improved) is a genuine, correctly-measured property of G's current fit — not a flawed-harness artifact. Basis:
- I re-ran the harness and reproduced every headline number exactly (before RMS 3.019 / after 7.715 / +155.5% / 37 cells).
- I independently re-fit Monaco FP2 on the fit-set drivers and reproduced the degenerate fit to full precision (offset 93.199 s, asymptote **−107640.29 s**, offset↔asymptote corr **−0.99999999996**). An asymptote of −107640 s is physically absurd and the correlation sits on the ±1 identifiability wall — the curve fit really is structurally unidentified on FP-session data.
- The harness has no assertion that could manufacture the sign of the result; the honest-null discipline holds (see criterion 7).
- The null is robust across the implementer's variants (full-field fit, curve-only, swap negative control) and the correct-correspondence `after` (7.715) beats the wrong-correspondence `swap` (8.615), showing G_A−G_B carries directional content — it is just badly over-sized by the degenerate fit.

The harness is trustworthy and the finding stands as a valid, complete deliverable under the Honest-Null Clause.

## Per-criterion findings (all 8 close criteria)

**1. Split integrity — PASS.** `_team_stratified_split` holds out `members[0]` per multi-driver team and fits `members[1:]`; single-driver teams go wholly to fit. Disjoint by construction, asserted at L276 and again at L448. Hand-checked two circuits' printed sets: Monaco fit{BOT,GAS,HAM,LEC,MAG,PIA,SAR,STR,TSU,VER} vs held{ALB,ALO,DEV,HUL,NOR,OCO,PER,RUS,SAI,ZHO} = no overlap; Netherlands fit{ALB,ALO,BOT,GAS,LEC,MAG,NOR,RUS,TSU,VER} vs held{HAM,HUL,OCO,PER,PIA,RIC,SAR,ZHO} = no overlap.

**2. Fit-set-only fit — PASS.** `_fit_and_store` L242: `fit_laps = laps[laps["driver"].isin(fit_drivers)].copy()` is computed **before** the `fit_grip_baseline_from_laps(laps=fit_laps, …)` call. Independently confirmed: my Monaco FP2 reproduction used only the 10 fit-set drivers (205 fit laps of 390 total) and produced the stored fit exactly — held-out drivers contribute zero laps to G.

**3. Held-out-only scoring — PASS.** `pace_a/pace_b = _cell_pace(laps, held_drivers)` (L285–286); `_cell_pace` filters `sub = laps[laps["driver"].isin(drivers)]` with `drivers = held_drivers`. The before/after loop iterates only the held-out (driver, compound) intersection cells. Reconciliation is measured exclusively on held-out drivers.

**4. Leakage-avoidance-by-design — PASS (claim VERIFIED).** Truth side = `_cell_pace` = `nsmallest(3, "lap_time")` → `median`. No regression, no design matrix. `grep -E "lstsq|linalg|polyfit|curve_fit|OLS|race_degradation|LinearRegression"` hits **only** docstring/comment/print lines (36, 44, 47, 48, 134, 390) — zero executable calls on the truth-side path. The only curve fit anywhere is *inside* `fit_grip_baseline_from_laps`, i.e. the correction under test, run on the disjoint fit set. No hidden truth-side regression exists; the leakage-discipline constraint is honored.

**5. Negative-control (swap) logic — PASS.** L304 `after = (pa-ga)-(pb-gb)` uses each session's OWN G; L306 `swap = (pa-gb)-(pb-ga)` uses each session's WRONG G (ga/gb swapped). Swap is genuinely wired to a different G than `after` (algebraically `after = before-(ga-gb)`, `swap = before+(ga-gb)`), and numerically `after_rms 7.715 ≠ swap_rms 8.615` — not accidentally the same computation. The real directionality evidence is `after < swap`, which holds.

**6. The diagnosis reproduces — PASS.** Re-ran `fit_grip_baseline_from_laps` on Monaco FP2 fit-set drivers directly (worktree src, editable-.pth trap avoided): offset=93.19940911, asymptote=−107640.29491, corr=−0.99999999996 — matches the diagnostic printout/JSON to full precision. The cited degeneracy is real, not a mislabeled printout.

**7. Honest-null operationalization — PASS (most important structural property).** Inventoried all 10 asserts (L276, 445, 448, 450, 452, 456, 457, 460, 461, 462). NONE asserts `after_rms < before_rms` or any "G must improve" condition. Every assert is harness-validity only: disjoint split, ran ≥3 circuits, non-degenerate split, finite results, non-vacuous `before_rms > 0`, regression-free flag, swap computed, cells > 0. Explicit "deliberately NO `assert after < before`" comment at L463. The scientific verdict is printed/written to JSON, never encoded in the exit code — pytest passes under the negative.

**8. Scope honesty — PASS.** Ran 4 real circuits (Monaco/Spain/Netherlands/Saudi) against `C:/Programs/f1Brainz/data/f1_data_2023.db` (real file, 16.5 MB, verified present), opened read-only. Not synthetic — the only temp DB is a fresh `GripStore` tempdir used solely to store the fitted curves, never as a data source. 37 pooled held-out cells; printed scope matched the claimed scope exactly on re-run.

## Handoff compliance
Built exactly what the handoff asked: driver-split, fit-set-only fit, held-out-only scoring, leakage discipline, honest-null operationalization, exits 0 under the negative. Stop conditions: none hit (DB had ample cross-session overlap). Compliant.

## Scope drift
Only the allowed new file `tests/unit/physics/layer2/test_grip_heldout.py`. Exclusion files (`grip_baseline.py`, `grip_store.py`, `grip_batch.py`) are untracked, their mtimes (09:32–09:53) predate the test file (10:28), the g4 plan journal shows no edits to them, and — decisively — the g2 degenerate fit is **unchanged** (I reproduced it), so no fix was smuggled in. Results JSON is untracked and not staged. No drift.

## Evidence verdict
Required evidence present and reproducible. Re-ran harness → identical numbers; re-ran `simplification_limits --paths` → PASS; independently reproduced the load-bearing degenerate fit. This harness IS the truth-anchored held-out evidence CREW_CONTEXT requires for a physics/evo-quality change.

## Code/doc quality
Small, cohesive helpers; reuses `grip_baseline`'s own readers rather than reimplementing the clean-lap filter. DB read-only via `file:…?mode=ro`. No silent fallback — a missing session yields a status record and `GripRecordNotFoundError` is handled with an explicit `continue`; missingness is represented, not zeroed. Fowler pass: verify_fowler_pass.py exit 0 — flagged (non-blocking) data-clumps (4 parallel metric lists) and long-parameter-list (`_fit_and_store` 7 args); overridden primitive-obsession (minimal-change doctrine) and comments-as-deodorant (comments carry the GATING scientific rationale a reviewer must read). No refactor blocker.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the produced numbers and reproduced fit back the "measured negative" claim.
- **Constraints not violated:** `constraint:db-only-analysis` honored (read-only 2023 DB, no FastF1/Jolpica).
- **Notes match the diff:** Yes — test-only, `struct:physics.layer2`, no production module touched.
- **Decision candidates surfaced:** `decision:held-out-not-in-sample` honored; `decision:heldout-split-axis` (guess) settled by running the real slice (stratified 50/50 worked). No authority-requiring decision was made silently.
- **Durable context routed:** Yes — the G-fit-identifiability finding is routed as a triage candidate for Commander.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation. The one item Commander must adjudicate is a **verdict decision, not a code defect**: whether to reopen g2 to constrain the curve fit, or accept the honest-null as #663's deliverable per the Honest-Null Clause. That is explicitly the Commander's call per the handoff's exclusions.

## Blockers
- None.

## Out-of-scope observations (triage candidates for Commander)
1. **G's saturating-curve fit is structurally unidentified on FP-session data** (offset↔asymptote corr ≈ ±1, physically absurd asymptotes; independently reproduced). G is not usable as a cross-session subtractable baseline on practice data as currently fit. Candidate fixes: bound/regularize asymptote+rate; restrict G to sessions with sufficient cumulative-track-laps spread; or flat-offset fallback when |corr| near 1. **This is the substantive finding behind the negative** — Commander decides reopen-g2 vs accept-null (out of this gate's scope per exclusions).
2. **Sigma-gating:** `get_grip_at` returns an honestly-inflated sigma for these degenerate fits, but the prescribed reconciliation subtracts only the point estimate `mu`. A sigma-weighted/sigma-gated consumer would down-weight degenerate corrections — worth considering whether "subtract G" should be sigma-gated downstream.
3. (Minor, from Fowler) Non-blocking: the 4 parallel metric lists could be a small tuple/dataclass; `_fit_and_store` has 7 params. Local-clarity acceptable; noted only.

## Workflow Feedback
- **Handoff gaps:** The handoff was unusually complete for a GATING review — the 8 enumerated close criteria mapped cleanly onto independent checks and made the "real vs artifact" adjudication tractable. One friction: criterion 4 phrases the leakage check as "no regression anywhere on the truth-side comparison path," but `fit_grip_baseline_from_laps` (the correction under test) *does* run an internal curve fit — a first reading has to disambiguate "truth side" (held-out pace) from "fit side" (G). The distinction is correct and the file is explicit about it, but the criterion could name it ("truth side = held-out pace extraction, excluding G's own internal fit").
- **Context rediscovered:** The editable-install `.pth` worktree trap (ad-hoc scripts in a worktree silently import MAIN `src/`) bit my independent reproduction probe — I had to force worktree-first `sys.path` and assert on `__file__`. This is known project lore but wasn't carried in the handoff; a one-line note for any reviewer who writes an independent probe would save a cycle.
- **Instructions improvised around:** The reviewer skill's `current`-alone survey cold-start caveat and the `current` read-only verb rejecting `--session-id` (harmless) were minor; nothing material. The Fowler rail cleanly accepted a record with two logged overrides.
- **What would have made this easier:** Nothing material — this handoff is a good template for GATING negative-result reviews. If anything, pre-listing the expected fit-diagnostic numbers (offset/asymptote/corr per named session) in the handoff would let a reviewer confirm reproduction against a stated target rather than back-reading the JSON.

## Return status
`complete`
