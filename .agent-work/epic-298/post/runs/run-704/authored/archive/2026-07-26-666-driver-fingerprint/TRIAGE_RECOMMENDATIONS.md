# Triage recommendations — #666 (all recommend-and-defer to the Admiral)

Delegated run: no human issue-filing authorized this run; the epic Admiral consolidates triage across the wave.
All 5 are ineligible for fix-now (each would expand the PR beyond #666's bounded code+tests+schema diff, and
several fold into existing epic issues). Routed **recommend-and-defer**.

## tc1 — Driver-axis predictive_t under-coverage at production driver counts
- **Labels:** research hardening, unresolved decision.
- **What:** On the bounded 4-driver slice the DRIVER axis also under-covers (0.31–0.35), symmetric with the class
  axis. Adjudicated in-run as a bounded-slice few-groups artifact (only 4 drivers; #665's many-driver synthetic had
  the driver axis ~0.90). Question: at production driver counts (~20), does the driver axis calibrate (so no floor
  needed), or does the driver-overall level also need a `shared_floor`?
- **Evidence:** `coverage_675_verdict.json` (driver 0.349 time / 0.309 energy); #665 many-driver ~0.90–0.96.
- **Acceptance (concrete re-measurement condition, per Admiral ratification 2026-07-26):** re-check driver-axis
  `predictive_t` coverage at FULL-SEASON driver count (#670, N≳15 drivers) using the same
  `scripts/fingerprint_class_coverage_675.py` diagnostic; **apply a driver-level `shared_floor` ONLY if the
  under-coverage PERSISTS at that N.** If the driver axis calibrates at N≳15 (as #665's ~20-driver synthetic
  showed, ~0.90–0.96), take no action — flooring on a 4-driver basis would OVERCORRECT at production count.
- **Out of scope for #666:** #675 scoped the floor to the class axis; driver-overall floor is premature here.
- **Disposition:** recommend-and-defer → folds into **#560** (thin-fit floor) / **#670** (full-season). Deferral
  reason: cross-cutting, not resolvable on the bounded slice; no filing authorized this run.

## tc2 — .gitignore for local .agent-work JSON artifacts
- **Labels:** tooling, cleanup.
- **What:** Extend `.gitignore` to cover `.agent-work/**/*.json` (or narrower) so a local verdict/summary artifact
  can't be accidentally `git add -A`'d.
- **Evidence:** `coverage_675_verdict.json`, `bounded_fit_summary.json` are local-only under `.agent-work/`.
- **Acceptance:** a `.gitignore` rule; a `git add -A` no longer stages those artifacts.
- **Disposition:** recommend-and-defer. Deferral reason: low current risk (commander stages explicitly, never
  `git add -A`); adding a non-#666 change to the PR would break the clean code+tests+schema-only diff — better as a
  coordinated epic-level hygiene change.

## tc3 — Store API takes loose primitives rather than the CellAddress value object
- **Labels:** cleanup, architecture weakness (minor).
- **What:** The store's public write/read API takes `(driver, era, vocabulary_version, class_id, channel,
  what_measure)` loose primitives rather than threading the `CellAddress` value object it already defines
  (Fowler data-clumps / primitive-obsession, flagged by both G2 and G3 review Fowler passes).
- **Evidence:** g2-review + g3-review `fowler_pass.json`.
- **Acceptance:** the store API accepts a `CellAddress`; call sites updated; invariants unchanged.
- **Disposition:** recommend-and-defer. Deferral reason: multi-file refactor touching an APPROVED gate's API +
  tests, post-approval; invariants hold as-is, so not fix-now.

## tc4 — Vocabulary-drift migration/purge API gap
- **Labels:** missing feature.
- **What:** No explicit path to migrate/purge stored cells when a `ClassVocabulary` version changes (the store
  loudly refuses a mismatch, but offers no purge/migrate).
- **Evidence:** g2-review finding.
- **Acceptance:** a purge/migrate API keyed on vocabulary version.
- **Disposition:** recommend-and-defer → relevant when **#642** evolves k/vocabulary. Deferral reason: forward-
  looking; #642 is downstream and gated on THIS issue's replication evidence.

## tc5 — F12 provenance gap (Belgium not in #625's holdout corpus)
- **Labels:** research hardening, missing test.
- **What:** The bounded-slice k=4 severity vocab's F12 PASS was inherited from #625's 22-circuit holdout artifact,
  but Belgium (one of the slice's 4 circuits) is NOT in that corpus — so the PASS is inherited-with-caveat, not
  slice-specific.
- **Evidence:** `bounded_fit_summary.json` vocabulary provenance; `docs/physics/625-f12-holdout-stability.json`.
- **Acceptance:** a slice-specific (or full-season #670) F12 stability check covering the run's actual circuits.
- **Disposition:** recommend-and-defer → folds into **#670** (full-season) or a targeted f12 check. Deferral
  reason: the fingerprint machinery correctly REFUSES a non-PASS vocab; closing the caveat needs data coverage
  work outside #666.
