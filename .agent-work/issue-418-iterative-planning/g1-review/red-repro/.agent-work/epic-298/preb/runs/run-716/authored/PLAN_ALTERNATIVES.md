# Plan-alternatives + cold critic — issue #716

Both rigor mechanisms are **bias-to-yes** and were run. Their **independence** was not achievable
this engagement — see "Untaken roads" — and that limitation is surfaced, not buried.

## Panel-vs-single choice (surfaced)

**Single-author, three candidates; single critic pass.** Rationale: the change is ~150 lines of
stdlib string/path handling with a fully-known blast radius (three call sites, one installer, four
test files) and no architecture-spanning consequence. Doctrine says panel when in doubt and for a
load-bearing interface; the one genuinely load-bearing choice here — the helper's seam — is settled by
the issue text itself ("a single shared helper both scripts import"). A panel would relitigate a
settled seam.

## Candidates

Three gate plans under distinct constraints.

### Candidate A — "distribution before use, one concern per gate"
*Constraint: no gate boundary may leave the suite red, and each gate carries exactly one review lens.*

- **G1** create `scripts/work_id.py` + `tests/test_work_id.py`. Nothing imports it yet.
- **G2** distribution: declare the module as a runtime companion of both call-site scripts; make the
  existing sibling-import guard companion-aware; assert the module reaches commander/admiral/explorer.
- **G3** rewire all three call sites to the helper; regression tests in the two existing test files;
  fold the invariant into the design doc.

### Candidate B — "defect per gate, partial land is still useful"
*Constraint: each gate independently closes one of the issue's two named defects, end to end.*

- **G1** helper (session parsing only) + `run_crew.py` rewire + its install wiring + regressions.
- **G2** extend the helper (archive + heading matching) + `verify_agent_feedback.py` rewire + its
  install wiring + regressions.

### Candidate C — "single gate, minimum ceremony"
*Constraint: minimize process overhead for a small mechanical change.*

- **G1** everything: helper, both call sites, installer, all tests, doc note.

## Comparison

| Axis | A | B | C |
|---|---|---|---|
| **Seam placement** | Helper API is judged **once, against both callers** at G3 — the seam is real (two adapters) before it is blessed. | Seam is authored at G1 against **one** caller, then extended at G2. G1's reviewer cannot tell whether the API fits the second caller. **One adapter = a hypothetical seam.** | Seam judged against both callers, but inside a diff that also carries distribution. |
| **Locality** | Each gate's diff touches one concern. | Each gate spans module + call site + installer + tests — three concerns per gate. | One diff, four concerns. |
| **Testability** | G2's guard can be **falsified** at G3 against a real import. | Guard is added twice, falsified never. | Guard added and vacuously green in the same commit that makes it meaningful — no independent step can falsify it. |
| **Red-window risk** | **None.** Distribution precedes the first `from work_id import`. | **None** (each gate self-contains its wiring). | None (atomic). |
| **Review depth on the historically-drifting concern** | Distribution gets its **own** reviewer. | Distribution reviewed twice, each time as a footnote to a bigger diff. | Distribution reviewed as a footnote once. This is exactly how `gauge_reader.py` shipped inert. |
| **Cost** | 3 gates. | 2 gates. | 1 gate. |

## Convergence — recommendation

**Candidate A**, with two grafts:

- **From B:** G3 adopts the helper at **all three call sites in one gate** — both or neither. This is
  what makes the seam real before it is blessed, and it is B's genuine advantage (caller-informed API)
  recovered without B's cost (authoring the seam twice).
- **From C:** no separate gate for the design-doc line. It rides G3, where the behaviour it records is
  actually established.

**Why not B:** its "partial land is useful" premise does not hold here. Both defects were hit in the
*same* run by the *same* agent; shipping half leaves the nested convention still unusable end to end,
so the partial-land benefit is nominal while the hypothetical-seam cost is real.

**Why not C:** the one concern with a documented history of silent drift in this repo — a bundled
script's sibling module never reaching the install — is the one C gives no independent review lens.
The installer's own source comment (lines 77-86) is the incident report.

## Untaken roads (named, per bias-to-yes doctrine)

- **Independent (parallel-subagent) authorship of the three candidates.** *Not taken.* This engagement
  carries a standing harness instruction not to dispatch subagents. The candidates were therefore
  authored serially in one context, which weakens their independence: they may share a blind spot.
- **Cold, context-free critic.** *Not taken as specified.* The critic pass below was run by the same
  context that authored the plan, so it is adversarial-by-discipline, not adversarial-by-construction.
  Its findings did change the spec (three of five), which is some evidence it was not merely a rubber
  stamp — but it is **not** a substitute for a fresh reader, and a fresh cold read remains the
  cheapest available hardening if the principal wants it before implementation.
- **A 3-lens critic panel** (intent-fit / testability / simplicity). *Not taken*, same reason, and
  additionally not warranted at this weight per the panel choice above.

## Critic pass — findings and disposition

Triage authority: the Commander, under the engagement's standing delegation.

**F1 — G2 approves on a vacuous green.** *(accepted, spec changed)*
At G2 the companion is declared for a script that does not yet import the module, so the sibling-import
guard passes for the wrong reason and "tests pass" proves nothing. **Disposition:** G2's close criteria
no longer says "tests pass"; it asserts **positively** that a real install writes `work_id.py` into
commander, admiral and explorer, and G3's close criteria requires the guard to be **demonstrated to
fail** with the companion declaration removed.

**F2 — the parser's back-compat fallback trades one silent wrong answer for another.** *(accepted,
spec changed)*
A tolerant "if it doesn't look canonical, fall back to `parts[1]`" would let a malformed session name
resolve to a plausible-but-wrong work-id — the same failure class being fixed. **Disposition:** the
fallback is narrowed to names that **cannot** be the canonical grammar (fewer than 5 segments), where
it exactly reproduces today's behaviour; names with ≥5 segments use the right-anchored parse and no
guessing. The boundary is pinned by test, and the docstring states which branch a name takes.

**F3 — "tolerate a flattened archive name" was a nice-to-have.** *(accepted, promoted)*
It is load-bearing for anyone who already hand-flattened a package, and it is the escape hatch that
makes the rejected naming-convention option cheap to adopt later. **Disposition:** promoted from prose
into an explicit G1 close criterion with its own test.

**F4 — the `_entry_block` tie-break rule as first drafted was backwards.** *(accepted, spec corrected)*
"Prefer the longest matching heading" returns the **child** entry when a parent id is asked for and
both exist — the precise bug being fixed, inverted. **Disposition:** the rule is **prefer an exact,
delimiter-bounded occurrence of the work-id; only if none exists, fall back to today's substring
behaviour.** This is the correction that most changed the plan.

**F5 — changing `_entry_block` risks regressing headings that resolve correctly today.** *(accepted,
new evidence requirement)*
Real headings carry dates, em-dashes and trailing prose. **Disposition:** G3 must run the new matcher
across the **real** `.agent-work/AGENT_FEEDBACK.md` corpus (hundreds of entries, both repos available)
and assert that every work-id resolving today resolves to the **same** heading. Cheap, and it converts
a guess into a measurement.

**F6 — is `_entry_block` scope creep?** *(rejected, with reason)*
Same root cause, same file, same helper, reproduced live. Deferring it guarantees a third waive under
the same convention. It stays in scope, bounded to strictly-widening, and F4/F5 are its guardrails.
