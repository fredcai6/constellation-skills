# Plan alternatives — issue #309 (lightweight, 2 candidates, single-context)

Per `lesson:lightweight-critic-catches-real-findings-on-bounded-issues`: a bounded
single-issue plan whose design space the pre-rulings already narrowed gets a lightweight
design-it-twice (2 candidates, authored single-context, not a parallel-subagent panel)
plus one solo cold-critic subagent — treated as a floor, not skipped. Panel-vs-single
choice, surfaced here: **single (lightweight)**, not a full panel — this plan is a bounded
measurement issue with pre-rulings already fixing the store/destination/copy-not-live
decisions; it does not spawn epics or touch shared architecture. The cold plan critic
below is run as MANDATORY regardless (`lesson:cold-critic-mandatory-for-measurement-dependent-plans`
— this plan's acceptance depends on a recall/noise measurement), not merely bias-to-yes.

## Candidate A — per-file viewpoint dispatch

Each of 2 viewpoints gets one Agent dispatch **per file** in the slice (4 files x 2
viewpoints = 8 dispatches, sequential, well inside the 3-concurrent budget cap run in
small batches). Each dispatch sees exactly one copied file plus its inline doctrine.

- **Depth**: shallow per dispatch — a viewpoint reasoning about `curator-copy.md` alone
  cannot know what `triage-copy.md` claims.
- **Locality**: high — a finding is trivially attributable to (file, viewpoint) pair.
- **Seam placement**: dispatch seam = `(file, viewpoint)`; 8 total dispatches.
- **Testability**: ground-truth scoring is a simple per-(file,viewpoint) lookup.
- **Fatal gap**: **cannot detect a cross-file contradiction by construction** — SD2 (the
  curator/triage cross-file contradiction on whether Triage implements) is invisible to
  every dispatch in this candidate, not merely hard to find. A coherence sweep that
  structurally cannot see the most realistic class of incoherence (two doctrine files
  disagreeing) is not measuring what issue #309 asks it to measure.

## Candidate B — whole-slice viewpoint dispatch

Each of 2 viewpoints gets **one** Agent dispatch covering **all 4 copied files at once**
(2 dispatches total), instructed to always cite `file:line` or a short quote for every
finding so locality is preserved despite the wider scope.

- **Depth**: deeper — a viewpoint can cross-reference `curator-copy.md` against
  `triage-copy.md` in the same reasoning pass, which is exactly what SD2 and DECOY1 need
  to be reachable at all.
- **Locality**: preserved by instruction (mandatory file:line/quote citation), not by
  dispatch boundary — a deliberate, checkable requirement rather than a structural
  guarantee, and the scoring step (g3) verifies every reported finding actually carries a
  citation before counting it.
- **Seam placement**: dispatch seam = `viewpoint`; 2 total dispatches, well under budget.
- **Testability**: ground-truth scoring parses each viewpoint's finding list and matches
  citations against the 6-item ground-truth manifest (5 seeded defects + 1 decoy) — more
  parsing work than Candidate A but bounded and mechanical.

## Comparison and convergence

Candidate A's locality/testability edge is real but not decisive; Candidate B's fatal-gap
finding for A is decisive, because the launch order's own mission is explicit about
*incoherence*, which in a real multi-file doctrine corpus is dominantly a cross-file
property (two skills or two docs disagreeing) — the actual, recurring failure shape this
epic's own LESSONS.md documents repeatedly (e.g.
`lesson:canonical-routing-can-dissolve-a-file-fence`,
`lesson:a-panel-inherits-what-it-was-not-told-to-vary` — both about cross-artifact
disagreement, not single-file defects). A sweep that cannot see that class by construction
would under-measure recall in a way indistinguishable from "the viewpoints are bad at
their job" — confounding the instrument's design with its performance, exactly the kind of
vacuous-check risk `lesson:a-check-that-cannot-fail-is-indistinguishable-from-one-that-passed`
warns about from the other direction (here: a check that cannot even ATTEMPT to catch a
whole class is not silently passing, but it is silently narrowing what "recall" means
without saying so).

**Converged on Candidate B**, with Candidate A's locality guarantee absorbed as an
explicit citation requirement rather than lost. Named untaken road: Candidate A's
per-(file,viewpoint) attributability is traded for cross-file reach; mitigated, not fully
recovered, by the mandatory citation instruction — surfaced here rather than silently
dropped.

## Ground-truth manifest (frozen before any dispatch runs — the ground truth is authored
before the viewpoints see the slice, so scoring cannot be shaped by what they found)

| id | file(s) | shape | findable by the handed context? |
|---|---|---|---|
| SD1 | triage-copy.md | self-contradiction: "No checklist" (kept) vs an injected line demanding the checklist engine gate every candidate | yes |
| SD2 | curator-copy.md + triage-copy.md | cross-file contradiction: curator-copy.md injected line claims Triage implements fixes directly; triage-copy.md's real line says it does not, unless asked | yes, only from the whole-slice view |
| SD3 | debt-cadence-copy.md | internal contradiction: "Dogfood project roots" lists 3 repos; the invocation commands are edited to touch only 2 of them | yes |
| SD4 | episode-store-excerpt-copy.md | self-contradiction: retirement policy states "Never deletion, never truncation" then an injected sentence says retirement deletes the original file's content | yes |
| SD5 | curator-copy.md | issue-number reference changed from the real #106 to a wrong number | **deliberately NO** — verifiable only against the live GitHub tracker, which no viewpoint is given or told to check; this is g0.5's proof-of-miss item, not a findable defect |
| DECOY1 | triage-copy.md + curator-copy.md | real, unmodified text: triage "No checklist" vs curator "Drive every step through the checklist engine" — superficially a cross-file inconsistency, actually two skills legitimately declaring independent process policy; no doctrine requires uniform tooling across skills | N/A — this is g0.5's proof-of-noise item; a viewpoint flagging it is a TRUE POSITIVE on "looks inconsistent," a FALSE POSITIVE on "is a genuine coherence defect", and must be scored as noise if reported as a defect |

Recall = |seeded defects (SD1-SD4) correctly reported| / 4 (SD5 excluded from the
denominator by design — it is the proof-of-miss control, scored separately as
found/not-found, expected NOT FOUND). Noise ratio = |reported findings that are not in
{SD1..SD4}| / |all reported findings|, with DECOY1 as the deliberate noise probe.
