# Plan alternatives — #663 gate plan (scaled: single-candidate + named untaken roads)

Panel scaling: single-candidate depth, not a full parallel-dispatch panel. Rationale: the module's
*interface* shape is explicitly precedented (issue #663 states design-it-twice is deliberately skipped
for the estimate-store pattern) and this is a Sonnet-tier, one-issue delegated dispatch under a Build-1
tracer-bullet scope (per DESIGN_SPEC.md S8) — the load-bearing design choices were already made at the
`understand` interrogation (session-scope, thin-session rule, split axis, synthetic criterion), so what
remains at `plan` is GATE SEQUENCING, a narrower decision than the interface shape itself. This scaling
choice is itself surfaced here rather than skipped silently (bias-to-yes: run *something*, name what
wasn't run).

## Chosen candidate: sequential store -> fit -> batch -> held-out gate -> synthetic gate -> verdict (6 gates)
Each gate the smallest reasonable bite that keeps verification green at every boundary: g1 ships the
artifact family first (mirrors the estimate-store precedent's own file split of store vs batch), g2 adds
fit logic on top of a frozen record shape, g3 adds the batch driver + consumer query surface, g4/g5 are
the two GATING acceptance harnesses (each independently reviewable, each producing real run evidence),
g6 synthesizes the verdict (reasoning gate, crew-waived — pure synthesis of g1-g5's own evidence).

## Untaken road A: bundle store+fit+batch into one larger "core module" gate
Rejected: a single implementer dispatch covering 3 files + their fit logic risks a large, harder-to-review
diff, and the estimate-store precedent ITSELF already splits store (estimate_store.py) from batch
(estimate_batch.py) as separate files/tests — mirroring that split gate-by-gate keeps each review scoped
to one concern (record shape vs fit math vs batch orchestration).

## Untaken road B: run g4 (held-out) and g5 (synthetic) as parallel/concurrent gates
Both depend only on g3, not on each other — a true dependency graph would let them run concurrently.
Untaken because the engine's `gated` checklist type is strictly ordered (cannot start a later gate before
the active one advances) and true parallelism would require a second child checklist or a within-gate
dual-crew dispatch, which is more machinery than this bounded issue's compute/complexity budget
justifies — sequential g4-then-g5 is slightly slower wall-clock but simpler to drive correctly through one
engine file. If wall-clock becomes a real constraint (e.g. the held-out harness's 2023-slice fit proves
long per the #650 thread-cap tax), this is the first thing to revisit.

## Untaken road C: fold the synthetic-recovery test (g5) into g2's own implement/review as inline unit tests
Rejected: the synthetic-recovery test is a GATING acceptance criterion named explicitly in the issue, not
an implementation-detail unit test — keeping it as its own reviewed gate (g5) with its own IMPLEMENTER_RESULT
/REVIEW_RESULT makes the acceptance evidence independently auditable (a reviewer can re-run g5 in isolation
to re-verify the acceptance claim) rather than buried inside g2's broader "does the fit code work" review.
