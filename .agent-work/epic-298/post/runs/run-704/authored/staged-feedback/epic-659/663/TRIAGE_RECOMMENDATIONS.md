# Triage Recommendations — #663 grip module G

9 candidates harvested from execute.json gate reviews (g1-g5) + interrogation record q7. Issue-filing authority: `docs/agents/ORCHESTRATOR_CONTEXT.md` Repo Action Authority table — "Create issues, comments, branches, worktrees | Autonomous for non-trivial tasks"; also explicitly in the launch order's Inherited Latitude ("debt-issue proposals"). Fix-Now ladder applied to all 9: none clear "no architecture/production-default impact" (every candidate either touches a shared statistical/data-path concern or is explicitly deferred pending a future design pass) — 0 fixed-now.

---

## 1. Grip module G: curve+offset structurally non-identifiable
- **Classification:** bug (research hardening)
- **Source:** g4-review tc1, g5-review tc1 (merged — same defect, confirmed both real-data and synthetic)
- **Structural anchor:** `struct:physics.layer2` — `src/physics/layer2/grip_baseline.py`
- **Disposition: `filed`** — **Issue #678**
- **Priority: high** — blocks any real consumer wiring of G; dominant open item from #663's build.

## 2. run_grip_batch doesn't wire weekend-sibling sessions for thin fallback
- **Classification:** bug / missing capability
- **Source:** g3-review tc1
- **Structural anchor:** `struct:physics.layer2` — `src/physics/layer2/grip_batch.py`
- **Disposition: `filed`** — **Issue #679**
- **Priority: medium** — real gap for a future full-season production batch run; non-blocking for #663's own gates.

## 3. sessions.rainfall schema/storage mismatch
- **Classification:** missing doc / cleanup (schema hygiene)
- **Source:** g2-review tc2
- **Structural anchor:** `src/data/schema.sql`, `sessions` table
- **Disposition: `filed`** — **Issue #680**
- **Priority: low** — no behavior bug in #663's own code (decode already correct); future-consumer clarity only.

## 4. Sigma-gate "subtract G" downstream
- **Classification:** feature / research hardening
- **Source:** g4-review tc2, g5-review tc1 (merged)
- **Structural anchor:** `struct:physics.layer2` — `get_grip_at` consumer contract
- **Disposition: `recommend-and-defer`**
- **Reason authority unclear:** no consumer of G exists yet (issue #663 explicitly scopes consumer-wiring out) — filing a concrete issue now would be premature/ungrounded against a not-yet-designed consumer contract. Revisit when the first real consumer is built (likely alongside or after issue #678's fix).
- **Priority:** low (until a consumer exists)

## 5. Shared SQLite-record-store base extraction
- **Classification:** cleanup / architecture weakness (dependency cleanup)
- **Source:** g1-review tc1
- **Structural anchor:** `struct:physics.layer2` — `estimate_store.py` + `grip_store.py`
- **Disposition: `recommend-and-defer`**
- **Reason:** two real instances of the same pattern now exist (deep-module doctrine: "one adapter is a hypothetical seam, two is a real one") — legitimate refactor candidate, but the g1 handoff deliberately mirrored the precedented shape rather than inventing a shared abstraction now (design-it-twice explicitly skipped per #663's own scope). Not urgent; a third instance (if grip module's future work or another physics store needs the same shape) would make the case stronger.
- **Priority:** low

## 6. Fuel confound in G's residual
- **Classification:** research hardening
- **Source:** g2-review tc1
- **Structural anchor:** `src/physics/layer2/tyre_supplant.py` (`race_degradation_slopes`'s fuel term, currently not exposed) + `grip_baseline.py`
- **Disposition: `recommend-and-defer`**
- **Reason authority unclear:** likely subsumed by whatever reparameterization issue #678 produces (a full de-fuel pass may be moot if the curve itself is being redesigned) — sequencing this behind #678 avoids wasted rework.
- **Priority:** low (pending #678)

## 7. get_grip_at query performance (pandas filter vs indexed query)
- **Classification:** performance/resource
- **Source:** g3-review tc2
- **Structural anchor:** `src/physics/layer2/grip_store.py` — `get_grip_at`
- **Disposition: `recommend-and-defer`**
- **Reason:** no current hot-path consumer; premature optimization until one exists.
- **Priority:** low

## 8. tyre_separation.py / G reconciliation
- **Classification:** architecture weakness (structure/constraint mismatch)
- **Source:** interrogation q7 (understand step), confirmed at g3-review scope-check
- **Structural anchor:** `docs/architecture/decisions/tyre-age-g-track-design.md` — its own Review Trigger names this scenario
- **Disposition: `recommend-and-defer`**
- **Reason:** the governing ADR's own Review Trigger states the unification question should be evaluated "if pooling.py is extended to support within-session covariate axes" — that hasn't happened; premature to file now. Confirmed structurally distinct (per-circuit linear vs per-session saturating curve; cross-season pooled vs single-weekend) in this run's interrogation.
- **Priority:** low

## 9. #511 grip_decay_prior_k unification
- **Classification:** dependency cleanup
- **Source:** pre-existing, confirmed still-open by this run's Explore research (not newly discovered)
- **Disposition:** N/A — already tracked as #511, no new issue needed. Untouched by #663's build (G is a new module, does not use `grip_decay_prior_k`).

---

## Not routed to triage (handled elsewhere)
- GripEstimateRecord's session-level PK vs EstimateRecord's per-constructor PK — recorded as a Cartographer decision anchor at reconcile (`docs/architecture/decisions/grip-estimate-record-session-level-pk.md`), not a triage candidate (it's a documented deliberate choice, not open work).
- layer2_evolution.py wiring to consume G — explicitly out of #663's scope per the issue itself; blocked on #678 being resolved first (wiring a known-non-identifiable G would propagate the defect) — noted in notes-663.md as sequencing context, not filed as a standalone issue (it would be redundant with #678's own acceptance criteria, which already requires re-validation before any wiring makes sense).
