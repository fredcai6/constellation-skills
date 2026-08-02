# Triage Recommendations — #625 Phase 1 segmentation substrate

Authority: `LATITUDE_CONTRACT.md` — "Issue filing (triage / follow-on) | delegated" and
"Fix-now triage (bounded fix applied, not filed) | delegated." No escalation required for
either lane this wave.

## tc4 / tc6 — F12 held-out-circuit stability FAILED (headline finding)
**Classification:** research hardening, bug (in the sense of substrate correctness), unresolved
decision.
**Problem:** the mandatory falsifiable gate found the property-class mixture's class count
unstable across circuit-composition splits (n_pass=0/5, k-mismatch every split).
**Disposition:** `filed` — **issue #638**. Does not clear the fix-now ladder (not a bounded
diff; needs a real investigation + model-structure decision). Filing authority explicit
(Admiral instruction #5).

## tc8 — scikit-learn undeclared dependency
**Classification:** dependency cleanup.
**Problem:** `property_mixture.py`/`mixture_stability.py` import `sklearn`, not declared in
`requirements.txt` — confirmed by direct grep before and after the fix. A fresh clone/CI
environment would fail to import this wave's own new modules without it.
**Disposition:** `fixed-now` — added `scikit-learn>=1.3.0` to `requirements.txt` (installed
version 1.9.0). Clears all 4 fix-now rungs: bounded (1 line), adjacent (the modules needing it
are this wave's own), verifiable now (import already exercised by every gate's green tests),
no architecture impact.

## tc2 — minor duplicated code (Fowler, `fit_property_mixture` fallback path)
**Classification:** cleanup.
**Disposition:** `filed` — **issue #639** (combined with tc3). Technically clears the fix-now
ladder, but deliberately routed to filed rather than reopening an already-reviewed/approved
Gate 2 file at finalization time (would require a fresh review cycle on a closed gate for a
cosmetic nit) — judgment call, not a ladder failure.

## tc3 — `KinematicSample.a_lateral` unit undocumented
**Classification:** missing doc.
**Disposition:** `filed` — **issue #639** (combined with tc2). `physics_data_models.py` is a
file untouched by this wave's own gates — editing it now is genuinely new scope, not
"adjacent... code the run already has open," so routed to filed rather than fixed-now.

## tc1 — g1-implement handoff mis-cited `identify_braking_arcs`'s caller
**Classification:** tooling / process (not a durable code or doctrine gap).
**Problem:** a one-off inaccurate file citation in a transient work-area handoff file
(`.agent-work/625-segmentation-substrate/crew-handoffs/g1-implement-handoff.md`), already
self-corrected live by the implementer with zero downstream impact (the actual signature
requirement was verified correctly against real source regardless).
**Disposition:** `recommend-and-defer` — filing authority is available but the candidate isn't
GitHub-issue-worthy: it's about an ephemeral, wave-scoped artifact (this handoff file gets
archived, not consumed by any future reader), not a repo doctrine file or template that would
recur. Captured instead as workflow feedback at the feedback step below.

## tc5 / tc7 — `CONVERGED_PLAN.md`'s terse phrasing vs. the binding implementer handoffs
**Classification:** stale generated map (of the plan-doc kind, not the architecture-map kind).
**Problem:** `CONVERGED_PLAN.md` Gate 3/4's prose is terser than (and in one place could read as
implying a different resolution than) the fuller implementer handoffs that actually governed
the work — flagged independently by two reviewers as the same pattern.
**Disposition:** `recommend-and-defer` — `CONVERGED_PLAN.md` is a wave-scoped planning artifact
under `.agent-work/625-segmentation-substrate/`, archived at closeout, with no downstream
consumer once this wave closes (the packet doc and the shipped code are the durable record).
Not GitHub-issue-worthy. Captured as workflow feedback below (handoffs should be treated as the
single source of truth over the higher-level plan doc when the two diverge in a future run).

## Summary table

| id | classification | disposition | detail |
|---|---|---|---|
| tc4/tc6 | research hardening / unresolved decision | filed | #638 |
| tc8 | dependency cleanup | fixed-now | `requirements.txt` +1 line, this commit |
| tc2 | cleanup | filed | #639 |
| tc3 | missing doc | filed | #639 |
| tc1 | tooling/process | recommend-and-defer | ephemeral artifact, no GH issue; -> feedback |
| tc5/tc7 | stale generated map (plan-doc) | recommend-and-defer | ephemeral artifact, no GH issue; -> feedback |
