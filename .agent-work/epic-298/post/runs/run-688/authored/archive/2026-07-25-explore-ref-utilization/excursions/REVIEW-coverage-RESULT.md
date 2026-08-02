# Coverage review — ISSUE_SET.json vs DESIGN_SPEC.md

Lens: coverage and invented scope. Read in full; did not edit either file.

## 1. Build-1 coverage

SET-level: clean. Every Build-1 commitment in §8 maps to at least one issue:
pilot slice → J; vocabulary tiling/nesting → B+C; grip module → D; reference
laps + utilization observables (incl. energy channel) → E; pooling-primitive
validation → F; fingerprint store/fit → G; join → H; instrument panel → I;
season-scale run + owner allocation decisions → K; frozen constants (F12
discipline) → A; lineage reconciliation (Intent kill-condition goal) → L.

One thing that looks like a gap but isn't: §4's design-it-twice interface
bullet specifies race-side machinery ("dense (driver×class×{push,managed})
array table," `push_managed_split` as a swappable config object) as part of
the interface "ruled now," yet no issue builds it — G's scope stops at the
utilization cells and explicitly excludes race-side cells. This is NOT a gap:
the epic body states outright that Build-2/3 interfaces, though ruled in the
spec, are "deliberately NOT cut here — they are cut after Build 1's
instrument panel reports signal sizes." Consistent, not missing.

## 2. Invented scope

**MAJOR — issue C.** C's body reads: "Populate the dormant schema attributes
the map carries: sub-phase marks, adjacency (...), turn direction." This
contradicts the spec's own explicit treatment of sub-phase marks as dormant
in Build 1 — §1's convergent bullet: "sub-phases marks-only and dormant
(`resolution="subphase"` reserved in the signature, backing store deferred)"
— and contradicts review S10's disposition, which drops the regeneration
guarantee specifically because "no finer-cell trigger exists" in Build 1. It
also contradicts sibling issues B and G, which both correctly keep sub-phase
dormant and single-homed in SegmentMap (per S5). C should not instruct
building/populating sub-phase data; at most it reserves the marks-only
signature, matching B. (Adjacency and turn direction in the same sentence are
fine — adjacency is "computed, never persisted" per §1, and turn direction is
an active int8 code in the runtime array, so "populate" is accurate for
those two; the defect is specifically the "sub-phase marks" item.)

Everything else checked clean — no issue builds anything the spec places in
Build 2, Build 3, the roadmap tail, or Out of scope (checked: live-prediction
wiring, phases/transitions/direction-split fingerprints/low-rank
factorization/teammate anchoring/drift modeling, absolute ERS/SOC, teammate
machinery, cross-year corner history, and the 12 neural modules — none
appear as deliverables in any issue). Issue L (lineage reconciliation) isn't
literally itemized as a numbered spec deliverable, but it operationalizes an
explicit Intent commitment ("ending that rediscovery loop is itself a goal")
using existing repo convention (hand-off to constellation-cartographer) —
grounded, not invented.

## 3. Critic-disposition spot-check (T1, T4, T7, T9, T10, S3, S5, S8, S11)

All nine carried through cleanly into the issue that would implement them:

- **T1** (G validation was in-sample) → issue D's acceptance is explicitly
  held-out reconciliation + synthetic-recovery identifiability test,
  in-sample scoring dropped. Carried.
- **T4** (braking quantile unfrozen) → issue A freezes the exact quantile and
  the lateral-g gate as named constants; issue C consumes them as "the
  frozen threshold." Carried.
- **T7** (join has no unit invariants) → issue H's acceptance lists the exact
  reduces-to-simple-case invariants (uniform composition → overall mean; all
  cells equal → that constant; single-class → σ collapses; soft memberships
  pass through). Carried near-verbatim.
- **T9** (`fit_two_way` reuse unverified under imbalance) → issue F is
  entirely this validation, with a named PASS/FAIL branch to the #628 direct
  pooling fallback, gating issue G. Carried.
- **T10** (per-era F12 gate sample sufficiency at Build-1 scope) → issue C
  states Build 1 consumes the existing validated vocabulary and defers the
  per-era refit + F12 gate to backfill, citing T10 by name. Carried.
- **S3** (SegmentMap over-builds live seed/supersede lifecycle in Build 1) →
  issue B explicitly phases the write entry point to cold/historical-only,
  citing S3 by name, supersede branch deferred to Build 3. Carried.
- **S5** (sub-phase/transition dimension duplicated in SegmentMap and
  CellAddress) → issue B says single-homed here, not duplicated; issue G
  says not duplicated, derives from the map later; both cite S5. Carried
  (and makes the C defect above stand out more, since B and G get this
  right).
- **S8** (no pilot before season-scale commit) → issue J is exactly the
  3-circuit pilot slice, and it blocks K (the season-scale run). Carried
  with correct ordering.
- **S11** (distance-vs-time-share provenance flag vestigial) → issue G drops
  it from the production path, citing S11 by name. Carried.

## Summary

- 1 MAJOR finding: issue C instructs populating sub-phase marks, which the
  spec (and sibling issues B/G) keep dormant through Build 1. Fix: strike
  "sub-phase marks" from C's populate list.
- No BLOCKING findings.
- No invented Build-2/3/roadmap/out-of-scope work found elsewhere.
- All 9 spot-checked critic dispositions are faithfully reflected in their
  implementing issues.
