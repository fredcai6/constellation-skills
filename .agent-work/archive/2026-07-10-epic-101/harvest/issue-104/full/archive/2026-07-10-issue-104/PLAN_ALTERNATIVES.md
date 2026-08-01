# Plan-alternatives — gate-plan candidates for issue #104

The curator *design* was already settled by the spec's 3-candidate design-it-twice
(minimal-interface / scout-analog / measurement-first → measure-then-mend hybrid;
`excursions/c2-x1-curator-dit.md`). This design-it-twice is over the **gate plan**
(build sequencing), per the shared standard. Three candidates under distinct
constraints; convergence and untaken roads named.

## Constraint axis
The launch order fences one gate per deliverable class (script, skill, tests,
install wiring, acceptance). The live variable is **sequencing + how tests attach**,
constrained by "verification stays green at every gate boundary" and "the first
gate touching a new artifact family ships its minimal validity-establishing artifact."

## Candidate A — deliverable-class order, tests as their own gate (constraint: honor the launch-order enumeration literally)
G1 script → G2 skill → G3 tests(script golden + falsification) → G4 install wiring
(+ install tests) → G5 acceptance. Green-at-boundary holds: G1 adds an unreferenced
script (suite unaffected); G2 adds a self-valid skill dir (installer accepts a
SKILL.md with no bundle entry — `.get()` returns `()`); G3 adds tests that pass; G4
wires bundles + adds install tests. Con: the script ships in G1 with no test until
G3 — a two-gate red-free-but-untested window.

## Candidate B — TDD-paired (constraint: no deliverable ships untested across a gate boundary)
G1 script+its golden tests → G2 skill → G3 install wiring+install tests → G4
acceptance. Collapses "tests" into the gate that produces the artifact under test.
Con: violates the launch order's explicit "gate each" enumeration (tests as a class);
mixes two deliverable classes in G1.

## Candidate C — skill-first (constraint: establish the new artifact family's validity earliest)
G1 skill (establishes skills/curator/ validity) → G2 script → G3 tests → G4 wiring →
G5 acceptance. Con: the skill's SKILL.md documents invariants of a script that does
not yet exist — the review can't check doc-vs-behavior alignment until G2, inverting
the natural dependency.

## Convergence → Candidate A, with one graft from B
Adopt **A**'s one-gate-per-class sequence (honors the binding enumeration and keeps
each gate a single reviewable class). Graft from **B** the discipline that G1's
implementer writes the script to be *testable in isolation* and hands back a runnable
invocation, so G3 attaches golden tests to an already-exercised surface rather than
discovering an untestable design late. The G1→G3 untested window is accepted and
narrow: the launch order's own two-sided acceptance (own run + independent sweep) is
the backstop, and G3 is the very next code gate.

**Untaken roads (named, revivable):** Candidate B (TDD-paired) — rejected only
because it merges the tests class into the script gate against the launch order's
enumeration; its instinct is preserved via the graft. Candidate C (skill-first) —
rejected for inverting the doc-vs-behavior review dependency.
