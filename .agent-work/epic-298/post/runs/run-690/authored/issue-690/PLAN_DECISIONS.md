# PLAN DECISIONS — issue #690

Design-it-twice (`c4`) and cold plan critic (`c5`) records for the plan step.

---

## Untaken road, named up front: both mechanisms ran IN-CONTEXT, not as subagents

The standing engagement instruction for this run is *"Do not call the AgentTool unless the user
requested it."* The doctrine default is parallel subagent candidate-authors plus a **cold** critic
with no authoring context. The closest compliant thing was done instead: the candidates were authored
in this context under genuinely distinct constraints and compared on the doctrine axes, and the
critic pass was run as a deliberate adversarial re-read against the frozen candidate + frame.

**What that costs, stated rather than hidden:** the critic is not cold — it shares the author's
context and therefore cannot catch a blind spot the author does not already suspect. Findings F1–F5
below are what a same-context adversarial read produced; a genuinely cold panel is a **named untaken
road** and remains available before execution begins. This misfit is reported here rather than
silently absorbed.

---

## 1. Plan-alternatives — three candidates, one distinct constraint each

Shared givens for all three: linear composition `σ⁺_c = w_c · σ_lap` with `w_c` = class transit-time
share (rulings D1/D2), point deficits byte-identical, μ fixed at zero, G consumed not re-fit.

### Candidate A — *minimal-diff* (constraint: touch as few files as possible)

Everything inside `class_utilization_observable.py`. It calls `class_ledger.class_time_ledger(
segment_map, distance_m, v_real)` a second time to obtain `time_share_by_class`, multiplies the
session σ through it, and builds per-class bands. `class_ledger.py` is not touched at all.

- **Depth:** shallow — one module gains one small behaviour.
- **Locality:** excellent; the whole change plus its tests sit in one file pair.
- **Seam:** none introduced.
- **Testability:** good.
- **Cost:** runs the `ds/v` transit integral over `v_real` **twice** per lap (once inside
  `class_deficits`, once inside `class_time_ledger`), and creates a *second* place the real lap's
  per-class time is derived. Bit-identical today because it is literally the same function on the
  same inputs — but consistent by coincidence-of-implementation, not by construction.

### Candidate B — *single-source-of-truth* (constraint: no quantity derived twice)

`ClassDeficits` gains one additive field, `time_by_class_s` (the real lap's per-class transit time,
already computed inside `class_deficits` as `Wᵀ·dt_real_seg` and currently discarded). The observable
derives `w_c = time_by_class_s / Σ time_by_class_s` from it.

- **Depth:** same behaviour, one field wider.
- **Locality:** change spans two files in the same sub-package.
- **Seam:** none introduced; extends an existing dataclass additively.
- **Testability:** strictly better — the weight and the deficit provably come from the *same*
  `dt_real_seg` array, so "the weight matches the deficit it scales" is true by construction and
  cannot drift.
- **Cost:** touches a consumed, frozen g1 module. Mitigation is cheap and already doctrine
  (`lesson:consumed-frozen-module-run-guard-tests`): re-run `test_class_ledger.py` unchanged.

### Candidate C — *policy-seam-first* (constraint: assume #712 will swap the weighting)

Introduces a weighting **policy** abstraction — a `SigmaWeighting` protocol or enum with
`time_share` as the first implementation and a documented slot for a grip-sensitivity variant — so
#712's consumer-contract decision can swap the law without touching the wrap point.

- **Depth:** the deepest-looking, and the least earned.
- **Locality:** worse — behaviour now lives behind an indirection every reader must learn.
- **Seam:** introduces one. **One adapter is a hypothetical seam** (inherited deep-module
  vocabulary): there is exactly one weighting today and the second is speculative.
- **Testability:** slightly worse — tests must now cover a dispatch layer that has one branch.
- **Cost:** speculative abstraction, which the project's own `one canonical path` rule and the
  inherited "no speculative abstraction" posture both push back on.

### Convergence — **B, plus exactly one element of C**

**Recommendation: Candidate B**, with C contributing *one named pure function* —
`per_class_sigma_plus(sigma_lap, time_share_by_class) -> np.ndarray` — and **no** policy/protocol/
enum layer. The function is the documented swap point for #712 (a later issue changes one function
body, not a call graph), while the abstraction that would have been speculative is not built.

**Why B over A:** the decisive axis is testability-by-construction, not diff size. B makes "the σ
weight is the share of the *same* transit-time integral the deficit came from" a structural property;
A makes it an implementation coincidence. The cost B pays — one additive field on a frozen dataclass,
guarded by re-running that module's own tests — is a known, cheap, doctrine-covered move. A also does
redundant work on every lap.

**Why not C:** one implementation is a guess at a seam. Its genuine value (a nameable swap point for
#712) survives in B's single function; its speculative half does not get built.

**Untaken roads recorded:** (1) C's full policy layer — revisit if and only if #712 lands a second
weighting; (2) A's zero-touch-on-`class_ledger` posture — revisit if `ClassDeficits` ever becomes a
persisted contract rather than an in-process dataclass; (3) the **grip-sensitivity weighting** itself
(zero out `straight`, renormalise over braking + corner classes), which is a modelling claim rather
than a unit reconciliation and belongs to #712/#686, with its settling experiment named in the plan.

---

## 2. Cold plan critic — adversarial read of the converged plan + mission frame

Five findings; each triaged here (no human reachable), with the disposition applied to the plan.

**F1 — "The report's *after* numbers are an analytic re-scale, not a rebuild — so the plan can ship a
green report having never run the real chain."**
*Verdict: REAL, and it is exactly the shape `lesson:mandatory-full-chain-smoke-before-unattended-run`
and `lesson:false-stall-diagnosis` warn about.*
**Disposition: EDIT applied.** g4 is split: g4a is the cheap analytic re-scale over the archived
store (which is legitimate and is what makes the report re-runnable at every W2 chain step), g4b is a
**mandatory one-weekend end-to-end smoke through `compose_and_persist_weekend`** proving the
production path actually writes per-class values. The report must state both, and its
Tested/NOT-tested section must say plainly which numbers came from which.

**F2 — "`w_c` is a *share*, so as the class count grows every band narrows. A `severity:c1` class with
0.1 % of lap time gets a band ~1000× narrower than the lap σ. Is that honesty or is it a
manufactured-precision bug?"**
*Verdict: REAL as a risk, correct as designed — but it must be tested, not assumed.*
A class occupying 0.1 % of lap time genuinely can only carry 0.1 % of a lap-time-level uncertainty
under a common-mode allocation, and its deficit is correspondingly tiny (c1's measured mean deficit
is 0.0036 s). The failure mode would be a class with a *large* deficit and a *small* time share.
**Disposition: EDIT applied.** g1's width-shape test set gains an explicit case pinning that the σ⁺
weight is independent of the deficit magnitude (a large deficit in a thin class does **not** widen its
band), so the property is chosen deliberately and provably rather than emerging silently. g4's report
adds a per-class breakdown so the thin-class behaviour is visible on real data, not just in fixtures.

**F3 — "Nothing forces the *lap-level* σ to remain recoverable. Repurposing the column loses it."**
*Verdict: REAL.* Once the column holds `w_c·σ`, a reader cannot reconstruct `σ_lap` without the
shares — and `fit.py` does not read `reference_laps`.
**Disposition: EDIT applied.** The `ClassUtilizationObservable.g_sigma_onesided` field is **kept** as
the lap-level scale (unchanged meaning) and the per-class vector is added alongside as
`sigma_plus_by_class`; the summation invariant (`Σ_c sigma_plus_by_class == g_sigma_onesided`) is a
tested property, which makes the lap value recoverable from the rows by summation. `FORMAT_VERSION`
`"1"→"2"` marks the stored column's semantic change so a reader can tell which convention a store
holds. Adding a second SQL column was considered and rejected (dual readers; `one canonical path`).

**F4 — "The plan cites #721's fix as landed but this worktree is detached at `3541d292`, which
predates it. An implementer working here will not see the code the plan describes."**
*Verdict: REAL and would have been a live failure* — the exact shape of
`feedback-verify-worktree-base-before-work`.
**Disposition: EDIT applied.** `e0-context` gains an explicit, verifiable base check as its first
postcondition: `onesided_sigma_from_grip` must take a single `sigma` argument and the builder must
call `grip_lookup(..., None)`. If either is false the gate STOPS — the branch was cut from the wrong
base. This is a command-checked grep, not an attestation.

**F5 — "W2's spec says the report runs on the *W0-stamped* substrate. W0's rebuild has not run. The
plan measures on an archived store and could be read as claiming W2's acceptance."**
*Verdict: REAL as a claim-hygiene risk.*
**Disposition: EDIT applied.** The report artifact must carry a substrate-provenance block naming the
exact store, its session count, its `format_version`, and the sentence that this is a **pre-W0
reading, re-runnable against the stamped store**, plus the retained-session fraction (T20). #690 is
accepted on the scaling and its invariant (D7 — deficit scale is aspiration, not bar); it does not
and may not claim W2's H4 verdict.

**Panel-vs-single:** single critic pass, in-context. Weight assessment: this is a bounded numeric
change on a mapped edge with a settled governing decision — not an architecture-touching or
epic-spawning artifact. A 3-lens panel was judged not proportionate; the *coldness* deficit above is
the more material limitation, and it is recorded as an untaken road rather than papered over.
