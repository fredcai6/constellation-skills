# Mission frame — #667 the join (epic #659 Wave 4a)

## Intent
Compose #664 circuit per-class TIME-share composition × #666 driver fingerprint cells into a
per-weekend, quali-side **utilization prior** with honest Student-t σ, for BOTH channels
(utilization/time-deficit + energy), symmetric. THE LINEAR JOIN IS THE PRIOR (no escalation —
that is #670). Correctness gate = the 4 T7 reduces-to-simple-case invariants (a mechanically
broken join can beat a driver-overall baseline through compensating errors, so outcome wins
prove nothing).

## Affected capabilities / structural anchors
- **NEW** `src/physics/fingerprint/join.py` — the pure join (deep module, thin interface).
- Consumes (as-is): `DriverFingerprintStore.get_fingerprint` → k `FingerprintCell`s
  (mean/sigma/support_n/status, `src/physics/fingerprint/store.py`); `ClassVocabulary`
  (class_ids order + `vocabulary_id` version pin, `.../vocabulary.py`); the #664 field-reference
  `ReferenceLapProduct.fingerprint` time-shares (`.../utilization/reference_utilization_store.py`)
  — NOT imported by the pure join; the caller passes a `Mapping[str,float]`.
- Student-t seam: `src/common/student_t.py` `predictive_t` / `PredictiveT` / `FormulaRule` /
  `DEFAULT_NU_LOSS=4.0`. Output prior IS a `PredictiveT`.
- Frozen constants: `FINGERPRINT_FROZEN` (#666) — consume; mint no literal (a needed-unfrozen
  threshold = F12 FLOAT to Admiral).
- Region = Physics (`src/physics/**`); packet `docs/architecture/packets/physics.md`. Map FENCE
  — record impact as prose, no edits.

## Governing constraints / decisions
- **Normalized weighted average (FORCED).** `w_i = comp_i / Σcomp`; `prior_mean = Σ w_i m_i`.
  Invariant 1 (uniform ⇒ driver-overall mean, exact) is an identity ONLY under this form. The
  corner-share sum (Σcomp ≈ 0.42 on GB, NOT 1.0) is surfaced as provenance, NEVER renormalized
  to 1.0. @grade: settled/inherited (DESIGN_SPEC line 132 + T7).
- **Composition = severity classes only** (straights + braking_zone excluded). The join selects
  exactly `vocabulary.class_ids` from the composition mapping; their sum = corner share.
- **σ propagation:** independent-cell linear form `Var = Σ w_i² σ_i²`, wrapped into a
  `PredictiveT` with an honest combined `n_eff` (thin cell drives the tail fat). No baked-in
  normality (ruling 5).
- **Thin/unresolved surfaced** via `thin_classes` + `weight_on_thin`; priced once at fit time,
  join never re-filters / never silently discounts (spec §4 line 93).
- **as_of_round** threaded for provenance (cells already strictly-pre from fit-time cutoff; store
  records no per-cell cutoff — join carries it, cannot re-verify → map/triage note).
- **Vocabulary version pinned:** every cell's `vocabulary_version == vocabulary.vocabulary_id`
  and class_ids match in order; mismatch refuses loudly (#666 precedent).
- **Consumer boundary:** join is for practice-update + fusion summaries; race sim + panel (#668)
  read un-aggregated cells — leave the direct-read API untouched.
- Own-DB (#632); DB-blob guard; no `.agent-work` on branch; pinned 3.14 interpreter.

## Decision candidates (surface at plan)
1. Join form = normalized weighted average — FORCED by invariant 1 (settled/inherited).
2. σ-propagation + unresolved-cell treatment — design-it-twice (below). guess → settle by the
   4 invariants + GB real-slice honest-σ behavior.
3. Pure-function interface (Mapping + cells + vocabulary), #664/#666 store reads live in the
   caller/validation — settled/measured (keeps the 4 invariants testable synthetically).

## Design-it-twice — σ propagation + unresolved treatment (the one load-bearing choice)
- **Candidate MIN (recommended):** combined scale `s=sqrt(Σ w_i² σ_i²)` over resolved cells;
  unresolved cell mean → resolved-weighted-mean μ_res (so prior_mean=μ_res), σ contribution =
  `weight_on_thin × max_resolved_σ` (derived, not a new literal); combined `n_eff` = min resolved
  support among meaningfully-weighted cells (thin dominates). Zero resolved cells ⇒ fully-thin
  prior surfaced loudly (no fabricated value).
- **Candidate PRINCIPLED (untaken road):** per-cell `PredictiveT` + Welch–Satterthwaite df
  combination. Rejected for Build 1 as higher-dimensionality than the problem needs (ruling 4);
  the interface leaves room to swap it in later.
- Convergence: MIN. Both satisfy invariants 1–4; MIN is lowest-dimensionality.

## Map confidence / staleness
- physics.md packet predates the #660–#666 fingerprint subtree (new leaves, closeout reconcile
  pending). Frame relies on SOURCE READS of the actual seams (done at context), not the stale
  packet — no gate silently trusts the map.

## Out of scope
Whether the join beats driver-overall (#670); sequence/interaction escalation (#670); the panel
(#668); race-side (Build 2); moving G μ off zero (#678); grip-store populate (#692); full-season
run (#670).
