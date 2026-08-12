# Design-it-twice Brief: #698 H1 — how to type the fingerprint store's address surface

## The one thing being designed twice

**The shape of the value object the `DriverFingerprintStore` read/write surface is typed on** — and,
consequentially, how the gate plan is cut around it. This is one load-bearing decision (the store's public
signature) with several realizable shapes. H2 and H3 are one-file mechanical fixes with no design space; they
are **untaken roads** below, not candidates.

## Count and panel — a surfaced choice

**Three candidates.** Rationale: this is an architecture-touching change (a keystone state store's public
signature, ~48 binding call sites), and doctrine says *"when in doubt, panel."* Three is enough to span the
real space — the store's surface is small and the axes are not independent enough to reward more.

**Surfaced for overrule:** an approver may collapse this to two (dropping C, which exists mainly to be
rejected on the record) or raise it. Under the engagement dispatch's standing authority the Commander made
this call.

## Execution mode — the honest caveat

Doctrine calls for **N agents in parallel, each in its own context**, and a **cold critic** with no authoring
context. This session carries a standing instruction not to dispatch subagents. So all three candidates and
the critic pass were authored **in this context, by the same author**. That is a **real methodological
weakness, not a formality**: same-author candidates correlate, and a critic who wrote the plan is not cold.
It is recorded as an untaken road below and surfaced at the approval checkpoint. Mitigation actually applied:
each candidate was written to its constraint's conclusion *before* comparing, and the critic pass was run
against the written artifact alone with an explicit remit to attack it.

## The constraints (one per candidate, each distinct and named)

- **Candidate A — `smallest-diff`**: change as little as possible while closing the read-side hole.
- **Candidate B — `best-seam-placement`**: put the boundary where the callers and the invariant actually want it.
- **Candidate C — `most-testable`**: maximize what can be falsified in isolation, cost be damned.

---

## Candidate A — smallest-diff

**Shape.** Leave all three signatures exactly as they are. Add a private
`_validate_slot(driver, era, vocabulary_version, channel, what_measure)` in `address.py`, extracted from
`CellAddress.__post_init__`, and call it at the top of `get_fingerprint` and `row_count`.

- **Depth** — poor. The seam does not move; the five-field clump stays on every signature, and the
  *primitive obsession* H1 names is untouched. It fixes the symptom (unvalidated read) and leaves the cause.
- **Locality** — excellent. Two files, ~15 lines, **zero** call-site churn. No test migration.
- **Seam placement** — none added. Validation becomes a call the next method to be added can silently forget —
  which is precisely how the current asymmetry arose.
- **Testability** — adequate. A malformed-address test on the read path passes. But nothing *structurally*
  prevents a fourth method from repeating the omission; the guarantee is convention, not type.

**Verdict:** cheapest and safest, but it satisfies neither H1's wording nor its intent. It would leave #698
re-openable as "we still pass loose primitives."

## Candidate B — best-seam-placement

**Shape.** Introduce a frozen `SlotAddress(driver, era, vocabulary_version, channel, what_measure)` in
`address.py`, validated by the rules `CellAddress` already enforces (non-empty `str`, no `|`, known
`what_measure`). Re-express `CellAddress` as **slot + `class_id`** — one address ontology, one validator, no
duplicated rules. Type `write_fingerprint` / `get_fingerprint` / `row_count` on `SlotAddress` (plus
`vocabulary` and, for write, `observations`). Provide `SlotAddress.for_vocabulary(driver, vocabulary, channel,
what_measure)`, deriving `era` from `vocabulary.rules_era`. Migrate all ~48 call sites; no shim.

- **Depth** — best. The type now *says* what the method addresses: a slot of k cells. The
  k-cells-always-populated invariant stops being prose-only. Validation is unforgettable because it is
  construction.
- **Locality** — moderate: 3 source files, 2 scripts, 4 test files, ~48 sites. But every site is **positional**,
  so migration is mechanical and a miss is a `TypeError` at collect time — loud, not silent.
- **Seam placement** — exactly where the callers want it. Four of the five production/script call sites build
  the same slot from a vocabulary and immediately pass it; `for_vocabulary` collapses that to one argument and
  **dissolves the era-vs-vocabulary mismatch class** for well-behaved callers, while the explicit constructor
  keeps the mismatch reachable so the refusal stays guard-testable.
- **Testability** — strong. `SlotAddress` gets its own unit tests in `test_address.py` beside `CellAddress`'s,
  independent of any DB; the store tests then exercise store behaviour, not string validation.

**Verdict:** the one that actually satisfies H1's intent, at a migration cost that is mechanical and
compiler-caught.

## Candidate C — most-testable

**Shape.** B, plus: extract an `AddressValidator` protocol injectable into the store, and add a
`FingerprintAddressPolicy` object so the delimiter, the known-measure set, and the reserved set can be varied
per test.

- **Depth** — negative. It hides nothing; it adds a configuration surface where a frozen invariant belongs.
- **Locality** — worst: a new abstraction plus a new injection point across the store's constructor and every
  test fixture.
- **Seam placement** — wrong. The delimiter and the known-measure set are **frozen constants** by design
  (`address.py:25-50`, `frozen_constants.py`). Making them injectable invites the exact vocabulary drift the
  store's third refusal arm exists to prevent.
- **Testability** — nominally highest, actually lower-value: it makes it easy to test *configurations that must
  never exist*.

**Verdict:** reject. YAGNI, and it weakens a deliberate frozen-constant design. Kept on the record because
"make it injectable" is the obvious next suggestion in review, and this is the reasoned refusal.

---

## Compared on

| Axis | A (smallest-diff) | **B (best-seam)** | C (most-testable) |
|---|---|---|---|
| Depth | leaks the clump upward | **hides it behind the type** | adds surface, hides nothing |
| Locality | best (~15 lines) | moderate (~48 mechanical sites) | worst |
| Seam placement | none added | **where callers already build it** | wrong (freezes → configurable) |
| Testability | adequate | **strong, DB-free address tests** | high but of the wrong things |

## Output — the recommendation

**Candidate B, unmodified.** It is the only candidate that satisfies H1's *intent* (an ill-formed address
cannot reach the store) rather than its symptom, and it does so by *removing* a concept rather than adding one:
after B there is exactly one address ontology and one validator, where today there are five loose strings plus
a six-field object that only the write path constructs.

**One graft taken from A:** A's insight that the *validation rules* must not be duplicated is honoured
explicitly — `CellAddress` is re-expressed **in terms of** `SlotAddress` rather than re-declaring the same six
checks. If that composition proves awkward in code, the fallback is a shared module-private validator called by
both, which is A's mechanism inside B's seam.

**C is rejected on the record** so a later reviewer's "why not make it injectable?" has a written answer.

## Untaken-road record — loud skips

| Untaken road | Why |
|---|---|
| **Independent-context candidate authors** (doctrine's parallel fan-out) | Session standing instruction bars subagent dispatch. Same-author candidates correlate; this is a real weakness, mitigated only by writing each to its conclusion before comparing. **Surfaced, not silent.** |
| **Cold critic with no authoring context** | Same bar. A self-critic pass was run against the artifact alone (`PLAN_CRITIC.md`) and is explicitly labelled *not cold*. |
| **Design-it-twice for H2** | Genuinely trivial: a four-line house-pattern guard with one correct form, already used verbatim at `scripts/build_class_utilization_observables.py:71-75`. No design space. |
| **Design-it-twice for H3** | The design space *was* explored — as interrogation q9, comparing blanket-ignore vs narrow-ignore vs output-anchoring — and converged there with reasons. Re-running it as a brief would be ceremony. |
| **A candidate keeping a primitives-accepting overload** | Excluded by ruling, not by oversight: project rule *"prefer one clear execution path over compatibility shims"*, and an overload would preserve the very unvalidated path H1 exists to close. |
| **A candidate making `CellAddress` the store parameter literally, as H1's wording says** | Excluded on evidence: the store methods are class-agnostic, so it would require a meaningless `class_id`. Recorded as interrogation q2/q3 rather than as a straw candidate. |

## Panel-vs-single record

**Panel of three, because the change touches architecture** (a keystone store's public signature and ~48
binding call sites) — doctrine's "when in doubt, panel." Convergence is normally the human's; under the
engagement dispatch's standing authority the Commander converged on B and records the pick, the axis-by-axis
reason, and the two rejections for overrule.
