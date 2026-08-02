# Plan decisions — #671 (design-it-twice + critic scaling)

## Design-it-twice: gate-slicing candidates (constraint = keep verification green at every boundary)

**Candidate A — "one big fold + verify" (2 gates).** G1 = all map edits (pipeline fold + dispositions + #696 anchor) in one pass; G2 = check_arch_map.py + cartographer verify.
- Pro: fewest boundaries. Con: a single giant reasoning gate mixes three distinct verification chains (node/edge invariants vs disposition-line invariants vs anchor-file invariant); a failure in one forces re-review of all; violates "smallest reasonable bite"; the pre-authored invariant chain (doc-only-gate doctrine) becomes unwieldy.

**Candidate B — "one gate per deliverable class + a verify gate" (4 gates).** G1 = pipeline fold (nodes+edges+packet+overlays+wave anchors, regenerate #663, don't dup #665). G2 = five lineage dispositions + adjacent #587/#559/#577/#642/#654 into the Open-Q table. G3 = graduate #696 into a decisions anchor. G4 = mechanical verify (check_arch_map.py green + invariant grep chain + clean-diff/no-code-change confirm + finalize FOR-OWNER list & triage).
- Pro: each gate carries ONE coherent pre-authored invariant chain; green at every boundary (each gate only ADDS doc content, `check_arch_map.py` stays green after each); a reopen is localized. Con: 4 boundaries (cheap here — all reasoning gates in-context).

**Convergence → Candidate B.** The three deliverable classes (pipeline map / dispositions / #696 anchor) have genuinely different invariant chains, and doc-only-gate doctrine wants each chain pre-authored and checked in isolation. B is the lowest-risk slicing that keeps `check_arch_map.py` green at every boundary. The cartographer independent content-verify runs at the spine's `reconcile` step (after execute), so G4's mechanical check + the reconcile cartographer together satisfy "green check is blind to drift."

Untaken road (named): a 5th gate splitting dispositions from adjacent-issue records — folded into G2 because they share one convention (the Open-Q table) and one invariant shape; splitting would duplicate the convention-consistency check.

## Crew vs reasoning gates
All four gates are **reasoning gates** (deliverable = doc/map prose; I already hold full context from the three research sweeps in notes-671.md). Crew implement/review WAIVED per commander-core "Crew gate vs reasoning gate" — a crew on pure doc edits is shallower, not safer. Independent scrutiny is NOT skipped: (a) each gate carries a pre-authored mechanical invariant chain (check_arch_map.py + grep assertions), and (b) the spine `reconcile` step dispatches a real constellation-cartographer for the code-vs-map content read (the launch order's mandate). This also honors lesson:self-authored-reasoning-gate-checks-need-review-scrutiny.

## Cold plan critic: panel-vs-single (surfaced choice)
**Single critic** chosen (not a 3-lens panel). Rationale: scope is FROZEN by the launch order (what to fold, the disposition convention, the deletion guard are all pre-ruled); design freedom is limited to gate-slicing; blast radius is zero code (doc/map only, propose-only removals). A single cold read of the frame+plan is proportionate. Untaken road (named): a full intent-fit/testability/simplicity panel — skipped as ceremony for a launch-order-frozen doc reconcile, but a single critic IS run (bias-to-yes honored).

## Cold-critic findings — triage (all high-value findings ACCEPTED into execute.json v2)
- **B1 (BLOCKING) ACCEPTED** — `git diff -- src/` is blind to staged/untracked changes (the exact `git add -A` mistake the order forbids). Swapped ALL deletion-guard checks to `git status --porcelain -- src/` (catches staged+unstaged+untracked). g1-c4, g2-c3, g3-c3, g4-c2.
- **B2 (BLOCKING) ACCEPTED** — g2 disposition invariant was false-green (regime_rollup=2, soft_class_membership=1, #654=1 pre-exist). Re-keyed g2-c2 to zero-today tokens (verified counts): apex_obs=0, classify_samples=0, #587/#559/#577/#642=0. L1/L2/L3/#654 (pre-existing tokens) verified by read (attested c3) + cartographer content read.
- **S1 (SHOULD-FIX) ACCEPTED** — check_arch_map.py does NOT validate edges (its docstring excludes edge validation), so nodes-only was passing. Added g1-c5 asserting the real boundary symbols derive_segment_map / reference_utilization_store / join_weekend_prior (all 0 today) appear — proves edges drawn with real import evidence.
- **S2 (SHOULD-FIX) ACCEPTED** — "regenerate #663 grip node" had no check. Added grip_baseline (g1-c2) + grip-estimate-record anchor (g1-c5), both 0 today.
- **S3 (SHOULD-FIX) partial** — added zero-today adjacent tokens; L2 driver_utility_observable=2 and L3 ephemeris=4/ideal_lap=12 pre-exist so can't be presence-grepped — verified by read + cartographer (attested c3).
- **S4 (SHOULD-FIX) ACCEPTED** — segment_classifier live path now VERIFIED not asserted: g2-c3 greps classify_samples in apex_extract/parameter_estimator/session_braking + SegmentClassifier in __init__ (all confirmed matching today).
- **S5 (SHOULD-FIX) ACCEPTED** — added g4-c4 positive scope-subset guard (tracked changes confined to docs/architecture/**; catches DB blobs / stray dirs in one shot).
- **S6 (SHOULD-FIX) ACCEPTED** — corrected the #577 premise: index.md line 981 is the **#575** burn-rate row, and #577 count=0. #577 is the issue TRACKING that #575 re-batch — so ADD the #577 pointer to the existing #575 row (do NOT relabel #575). The single-convention rationale stands on its own (Open-Q table is the existing home for tracked-deferred items generally), not on a false "#577 already there".
- **N1 (NICE) ADDRESSED w/o second convention** — re-burial risk of settled items in an "Open Questions" table: each disposition row's Route column now states the explicit verdict (wired / kept-with-reason [no action] / removal-PROPOSED / Triage #NNN) so settled reads as settled. Honors the order's "don't invent a second convention".
- **N2 (NICE) kept as attested + cartographer** — #665 pooling single-node retention verified by read + cartographer (grep-count of a component decl is fragile).
- **N4 (NICE) ACCEPTED** — purposes.yml deprecated-ontology migration debt added as a triage candidate (g4-c3).
- **N3 (NICE) not actioned** — file-scoped vs table-scoped greps; cartographer content read covers placement.
