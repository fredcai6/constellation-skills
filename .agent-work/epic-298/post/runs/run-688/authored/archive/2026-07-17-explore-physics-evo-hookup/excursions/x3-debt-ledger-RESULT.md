# x3 — Physics/Preprocessing Debt Ledger

**Question:** What physics/preprocessing debt is actually still open, and for each item
what would "settled" mean — build it, or formally close it with a decision record?

**Method:** `gh issue list --state open` (full sweep, 60 open issues) + targeted `gh issue
view` on all candidates + keyword search (`physics OR preprocessing OR estimator OR
smoother OR sigma OR traction OR calibration OR uncertainty`) + `docs/architecture/decisions/`
+ `TODO|FIXME|XXX` grep over `src/physics/` and `src/preprocessing/` (zero hits — this
codebase does not use inline TODO markers; open work lives in GitHub issues) +
`.agent-work/archive/` physics-epic residue.

**Headline finding:** the ledger you're looking for **already exists and is current**:
issue [#609](https://github.com/fredcai6/f1Brainz/issues/609) ("Physics debt burn-down:
retire the standing debt pile to zero," owner-directed 2026-07-12, parent #601) is itself
a live, maintained pile-to-zero tracker with an explicit cluster breakdown and ordering
constraints. I verified every item it lists is still open and accurately described, and
swept for items outside its scope. Nothing found in the sweep is missing from #609 except
items #609 doesn't claim to cover (the C-series physics-state-space carry-forwards #515/
#516/#517, the 2026-regs pair #499/#483, C4 #513, and the composition gate #450) — those
are physics debt but live one level up the epic tree (#509), not in #601's burn-down.

Candidates from the brief that turned out to be **already CLOSED** (verified via `gh
issue view`, not just assumed from memory): **#496** (physics-aware estimator outer loop
— closed 2026-06-25, superseded by the decoupled-1D-longitudinal design, see below),
**#546** (throttle HP retune / coast boundary-lag — closed HONEST-NULL 2026-06-28), **#511**
(C2 race-state — closed 2026-06-29, memory already had this as CONTEXTUAL/done but the
brief's candidate list treated it as open debt; it is not).

---

## Ledger

Columns: **#** = issue number (link), **what** = one-liner, **state**, **blocks evo
feature extraction?** (low bar = per-car capability vector + honest σ per weekend) vs
**only best-possible-physics** (later tier), **settle-or-close rec**, **size**.

### A. The #609 burn-down pile (verified current, 2026-07-17)

| # | What | State | Blocks evo extraction? | Rec | Size |
|---|------|-------|------------------------|-----|------|
| [#589](https://github.com/fredcai6/f1Brainz/issues/589) | Complete/verify `physics_estimates.db` season backfill; confirm ceiling-source flip | open | **Yes, mild** — the pooled `EstimateStore`/`car_prior` ceiling is the canonical input for the per-car capability vector; unverified backfill = unknown coverage gaps by season | Settle (verify, don't rebuild) | S |
| [#577](https://github.com/fredcai6/f1Brainz/issues/577) | Re-batch stored physics estimates against wired burn rate | open, folds into #589 regen wave per #609 ordering | Yes, mild — same data-freshness concern as #589 | Settle (one rerun covers both) | S–M |
| [#587](https://github.com/fredcai6/f1Brainz/issues/587) | Retire or formally demote old `fit_store` per-driver engine | open, gates #559 | No — pipeline-tighten already demoted it to fallback role; canonical path already switched to `EstimateStore` | Close (formalize the decision already made in practice — write it up) | S |
| [#559](https://github.com/fredcai6/f1Brainz/issues/559) | Rebuild per-session `physics_fits.db` on post-#548/#495 code | open, moot if #587 retires fit_store | No — moot pending #587 | Close-if-#587-retires, else settle | S |
| [#591](https://github.com/fredcai6/f1Brainz/issues/591) | `emit_accel_obs` flat `sigma_floor` → real per-sample uncertainty | open, self-acknowledged placeholder in code comment | No — feeds the kind=3 outer-loop refinement channel, not the capability vector directly | Best-possible-physics; settle when outer loop resumes | M |
| [#592](https://github.com/fredcai6/f1Brainz/issues/592) | Audit `a_lat` sigma semantics in `segment_classifier.py` (9×9 smoother-state cov ≠ `np.gradient` cov) | open, docstring-flagged not fixed | No — audit/correctness question, not a known-wrong output yet | Settle (cheap to resolve, cheap to leave) | S |
| [#560](https://github.com/fredcai6/f1Brainz/issues/560) | Minimum flying-laps/sample floor for fit acceptance (thin fits pass as `ok`) | open, informs #513 per #609 ordering | **Conditional** — not blocking today (quali-only fits); becomes relevant the moment #513 (FP fits) is built, since FP sessions are full of thin runs | Settle before or alongside #513 | S–M |
| [#506](https://github.com/fredcai6/f1Brainz/issues/506) | Static `SYSTEMATIC_FLOOR` → data-driven systematic-uncertainty floors | open | **Yes, directly** — this is literally the "honest σ" half of the low bar; today's σ is over-confident by the issue's own description (nuisances conditioned-out, correlated across sessions) | Settle before shipping the σ to evo, or close with a decision record stating the static floor is an accepted interim approximation | M–L |
| [#502](https://github.com/fredcai6/f1Brainz/issues/502) | Per-constructor/per-PU temperature derating of `P_max` | open | No — refines one channel's fidelity, current shared-β model already "works and unmasks the engine fingerprint" per issue body | Best-possible-physics | M |
| [#557](https://github.com/fredcai6/f1Brainz/issues/557) | Corner-indexed/cross-lap-pooled traction frontier (stationarity assumption) | open, explicitly "not immediately actionable — a design discussion" | No | Best-possible-physics; leave open as a design note | L |
| [#553](https://github.com/fredcai6/f1Brainz/issues/553) | Decoupled-estimator coast wiring: tighter coupling / min-segment filter | open, low-pri | No — decision already made (HOLD, keep incumbent `prepare_coast_samples`); this issue is just the parked future-fix note | Close as a documented future path (the decision record `docs/architecture/decisions/decoupled-1d-longitudinal.md` already captures both fix options in prose) | S (to close) |
| [#593](https://github.com/fredcai6/f1Brainz/issues/593) | Trajectory smoother incorporate mass/compound (D2, user-directed long-term) | open | No — mass/fuel already handled via reduced-form paths (`fuel_features.py`, `burn_rate_calibration.py`); this is a smoother-fidelity upgrade, not a missing input | Best-possible-physics, long-term per its own label | L |
| [#594](https://github.com/fredcai6/f1Brainz/issues/594) | De-confounded compound k-prior source (D3, user-directed long-term) | open | No — current path already has a documented workaround (widened σ, clamped mean on the weakened k-prior) | Best-possible-physics, long-term per its own label | L |
| [#566](https://github.com/fredcai6/f1Brainz/issues/566) | Compound-deg sensor research follow-on threads (#443 deferred) | open | No — #443's sensor already productionized and shipped; these are research extensions | Best-possible-physics | M |
| [#515](https://github.com/fredcai6/f1Brainz/issues/515) | C1 car-prior fidelity follow-ups (upgrade-clock, pooled covariance, fallback_channels) | open, carry-forward | No for the low bar (car capability vector doesn't need driver-utilization fidelity); flagged in its own body as "needed before C1 utilization can earn a GO" — so it DOES block a full C1 GO, just not evo extraction | Settle if C1/driver-utilization axis is wanted; else best-possible-physics | M |
| [#516](https://github.com/fredcai6/f1Brainz/issues/516) | C1 regime-utilization refinements (public MC, weighted U_r, config seed/threshold) | open, carry-forward, "not blocking the CONTEXTUAL verdict" | No | Best-possible-physics | M |
| [#517](https://github.com/fredcai6/f1Brainz/issues/517) | C1 utilization cleanup (re-export, dashboard warning) | open, carry-forward, low-pri | No | Best-possible-physics | S |
| [#590](https://github.com/fredcai6/f1Brainz/issues/590) | Split `stint_estimator.py` (over file-size simplification ceiling) | open | No — pure code-health | Settle (mechanical) | S |
| [#582](https://github.com/fredcai6/f1Brainz/issues/582) | `validate_refine_505.py` loads each session twice per run | open | No — perf/script hygiene | Settle | S |
| [#576](https://github.com/fredcai6/f1Brainz/issues/576) | `build_db_session` RuntimeWarning overflow on NaN `lap_time_s` | open | No — warning noise | Settle | S |
| [#578](https://github.com/fredcai6/f1Brainz/issues/578) | Cross-year circuit fallback in `resolve_race_burn_rate` | open | No — fallback-chain completeness, not a current failure | Settle or close as low-pri backlog | S |
| [#568](https://github.com/fredcai6/f1Brainz/issues/568) | `empirical_sensor.py` raw-sqlite3 compromise (bypasses `DatabaseManager`) | open | No — `compound_prior` region, already-shipped and wired sensor; this is an architecture-cleanliness note, annotated in-code | Settle or close with a decision record accepting the compromise (reason already documented in-module) | S–M |
| [#569](https://github.com/fredcai6/f1Brainz/issues/569) | `empirical_sensor` tests mask driver_num join path | open, test gap | No — underlying #443 bug already found/fixed; this is the missing regression test | Settle (cheap) | S |
| [#570](https://github.com/fredcai6/f1Brainz/issues/570) | No semantic-direction test for target vs feature (`b_lap` vs `b_lat`) | open, test gap | No — same, underlying bug already caught and presumably fixed in #443 G3; test-only gap | Settle (cheap) | S |
| [#549](https://github.com/fredcai6/f1Brainz/issues/549) | Ratchet remaining 71 pyright baseline errors to zero | open, ci chore | No | Settle incrementally | L |
| [#529](https://github.com/fredcai6/f1Brainz/issues/529) | GP-name normalization hygiene (`f1_calendar.py`) | open, "pulled into the decomposition layer" per #609 | No | Settle alongside whatever pulls it in | S |
| [#432](https://github.com/fredcai6/f1Brainz/issues/432) | Slim gold-cycle `details.json` (self-indexing + npz sidecars) | open | No — evo-pipeline storage, not physics | Settle or close, low-pri | M |

### B. Physics debt outside #609's scope (one level up the epic tree, #509)

| # | What | State | Blocks evo extraction? | Rec | Size |
|---|------|-------|------------------------|-----|------|
| [#450](https://github.com/fredcai6/f1Brainz/issues/450) | Phase 3: physics-derived features INTO evo (the actual composition gate) | open, child of #445, "Gated on Phase 2 producing attributed forces with covariance" | **This IS the blocker** — no physics feature has entered the evo predictor yet at all (per CLAUDE.md: live predictor is 12 neural latent-power modules, zero physics wiring today). Every other item on this ledger is upstream-quality debt; #450 is the actual unbuilt bridge. | Build — this is the real next step, not a close-or-settle item | L |
| [#513](https://github.com/fredcai6/f1Brainz/issues/513) | C4: FP-session fits enabler (physics on pre-quali sessions, weekend-local path) | open, QUEUED, parent #509 | **Yes for the FP/race-week path specifically** — #604 (race-week command, live #601 push) wants FP1/FP2/FP3 → predict; without #513 that path has no physics-derived pre-quali signal (though the neural FP modules already function independent of physics) | Build if/when the weekend-local physics feed is wanted for #604; else defer | L |
| [#499](https://github.com/fredcai6/f1Brainz/issues/499) | Generic multi-state CdA interface (replace `theta_D` with named aero-config dict) | open, "travels with #483" per #609 | **Yes for 2026 specifically** — 2026 has real active aero (multiple aero states); single-`theta_D` physics can't represent it correctly, and 2026 is the live prediction season | Settle together with #483 before physics features touch 2026 races | M |
| [#483](https://github.com/fredcai6/f1Brainz/issues/483) | RegulationEra: 2026 active-aero/new-PU + 2027 regs handling | open | Same as #499 — bundled dependency | Settle together with #499 | M–L |
| [#492](https://github.com/fredcai6/f1Brainz/issues/492) | Epic: physics — borrow strength across sessions + ship (holding) | open, holding/structural | No — tracker only, children already spawned (#510–#517 etc.) | N/A — close when all children close, no independent content | — |
| [#509](https://github.com/fredcai6/f1Brainz/issues/509) | Super-epic: physics → prediction pipeline | open, structural top-down driver | No — tracker only | N/A — same | — |

### C. Settled / verify-closed (candidates from the brief, confirmed not open debt)

- **#496** (physics-aware estimator outer loop / kind=3 Matérn feedback) — **CLOSED**
  2026-06-25. Superseded: the decision record
  `docs/architecture/decisions/decoupled-1d-longitudinal.md` shows the actual outcome was
  a *different* design (decoupled 1D energy/force filter, not the originally-planned Matérn
  outer loop), WIRED for braking as of #518 G3 (2026-06-25). Throttle/coast were measured
  and HELD (HONEST-NULL, #523 then #546, both closed) — **this is the "physics-blind
  smoother interim workaround" the brief asked about**: it is not an interim workaround
  anymore, it's a settled, decision-recorded, partially-wired state (braking wired, throttle/
  coast intentionally not wired with documented reasons and two named future-fix paths in
  #553).
- **#546** — **CLOSED** 2026-06-28, HONEST-NULL (see decision record above).
- **#511** (C2 race-state) — **CLOSED** 2026-06-29. Superseded by #512 (C3) per memory; not
  open debt.
- **#567** (arch map edge `struct:physics→struct:common`) — open but trivial, already
  scoped as one of five items inside **#608** (housekeeping, parent #601 D5, open). Not
  independent debt — closes when #608 closes.

## Scoped nulls — what was NOT swept

- Did not open or read full bodies of #386/#388/#389/#390 (Thrust B race/race-start
  uncertainty epic) — these are prediction-layer (fusion/Bradley-Terry) uncertainty work,
  not physics/preprocessing per the brief's scope; flagging as adjacent but excluded.
- Did not open #423, #424, #482, #607, #604, #605, #610, #601, #623, #615, #614, #620 —
  swept in the full open-issue list (60 issues) and confirmed by title/label these are
  evo-pipeline/fantasy-push/infra, not physics-region debt.
- Did not re-verify #443 (compound-degradation sensor productionization) end-to-end;
  treated as shipped per #566's context line and memory.
- Did not grep `.agent-work/archive/` beyond a filename glob for "physics"/"509" — did not
  open every archived epic doc for line-level residue debt.
- `TODO|FIXME|XXX` grep across `src/physics/` and `src/preprocessing/` returned **zero
  matches** — confirmed this repo tracks debt in GitHub issues, not inline code markers,
  so the grep sweep is a true negative, not a missed search.

## Bottom line

The "physics debt ledger" isn't something to compile from scratch — **#609 already is
one**, actively maintained, owner-directed, and accurate as of today (2026-07-17). Of its
~26 items, only two (#589 backfill-verify, #577 re-batch) have any real bearing on the evo
low bar, because they affect *whether the data underlying the capability vector is
complete*, and one (#506, systematic-σ floors) bears directly on the *honesty of σ* the
low bar asks for. Everything else in #609 is best-possible-physics tier or pure code
hygiene. The actual blocker for "feature extraction for evo" is not debt at all — it's
that **#450 (Phase 3 compose) hasn't been built yet**; physics features have not entered
the live evo predictor in any form. If 2026 races are in scope, #499/#483 (multi-state
aero for active-aero cars) should settle before physics touches those weekends specifically.
