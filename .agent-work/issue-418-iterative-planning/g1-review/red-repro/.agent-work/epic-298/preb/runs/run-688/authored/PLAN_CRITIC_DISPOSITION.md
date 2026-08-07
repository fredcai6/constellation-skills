# Cold plan critic — findings and disposition (issue #688)

## Form deviation, recorded loudly as an untaken road

The doctrine calls for a **cold** critic: a reader with **no authoring context**, given only the
candidate plan and the mission frame. This session carries a standing directive — *"Do not call the
AgentTool unless the user requested it"* — so no independent critic could be dispatched.

What was run instead: an **adversarial self-critique** of the authored `execute.json` against the
mission frame, disposing each finding explicitly. What that buys: the eight findings below, seven of
which changed the plan. What it does **not** buy, and the owner should know it: the whole point of a
cold read is catching what the author cannot see, and a self-critique is structurally blind to
exactly that. **A genuine cold read is still owed** and should be run at the top of the
implementation engagement, before g1 opens.

Panel-vs-single: a **panel** (3 lenses — intent-fit, testability, simplicity/YAGNI) is what this
plan's weight calls for (region crossing + stored record contract + a moved acceptance baseline).
Recorded as the scaling call the owner may overturn.

---

## F1 — `g2` conflated two independent changes · **ACCEPTED, plan changed**

The original g2 carried both the graded severity classification and the drying-window guard. They
have different failure modes (classification is testable against a static corpus; the guard changes
*which laps enter the fit*) and different risk (the guard is the largest piece of new logic in the
whole plan). Coupling them means a wrong guard reopens the correct severity work.

**Change:** split into **g2 (severity classification)** and **g3 (drying-window guard)**; everything
downstream renumbered. The plan is now 7 gates.

## F2 — no gate re-ran the *consumed* module's own guard tests · **ACCEPTED, plan changed**

g1 changes `populate_wet_features_for_db`, whose output the fuel subsystem's
`session_wet_fraction` consumes. The original g1 ran only the data-region tests. This is
`lesson:consumed-frozen-module-run-guard-tests` verbatim — "verifying only your own new tests can
pass while silently breaking the guard tests of the module you are extending."

**Change:** `tests/unit/physics/test_burn_rate_calibration.py` added to g1-integrate's command.

## F3 — the re-batch had no rollback and no comparison baseline · **ACCEPTED, plan changed**

The re-batch gate ran `run_grip_batch(force=True)`, which **overwrites the grip store in place**. If
the resulting numbers are bad there would be no prior store left to compare against, and the "before"
half of the required before/after held-out delta would be unrecoverable.

**Change:** the re-batch gate must **snapshot the existing grip DB first**, and the before/after
comparison is computed against that snapshot. This was the most serious finding.

## F4 — `grep -q 'Hungary'` was exactly the proxy check the doctrine warns against · **ACCEPTED, plan changed**

A grep for a circuit name proves a string is in a file, not that the frozen corpus is exercised as
test cases — a comment would satisfy it. Using a test-shaped proxy for "the work was really done" is
the failure `commander-core.md` §doc-only-gates names.

**Change:** demoted to a cheap tripwire; the operative condition is now an **attested inspection**
naming what must be confirmed (each corpus session appears as a parametrized case with its expected
class).

## F5 — two different NULLs were being treated as one · **ACCEPTED, plan changed**

`wet_lap_fraction` is NULL both when a session has no laps at all (`session_wet_lap_features`
returns `(0, 0, None)`) and when the session was simply never populated. Both would land in
`unknown`, but they are different facts — one is an empty session, one is a coverage gap — and
conflating them hides the second.

**Change:** g2's imperative now requires the two to be distinguished in the stored provenance.

## F6 — the `wet` threshold at 0.50 is unconstrained by data · **ACCEPTED as an honesty change**

The measured corpus has sessions at 0.338 and at 0.622 and **nothing in between**. So any threshold
in 0.34–0.62 classifies the real data identically; 0.50 is a midpoint choice, not a fitted one.

**Change:** stated explicitly in the g2 anchors and in the decision's `settle:` line, so nobody later
reads 0.50 as measured. The grade was already `guess`, which is correct.

## F7 — `g5` (now g6) was still doing too much · **ACCEPTED, partially**

New CLI + full re-batch + three measurements + possibly editing the frozen held-out harness. The CLI
is genuinely small so it stays; the risk is the unattended batch.

**Change:** a **mandatory single-circuit-year smoke before the full run** is now a stated constraint
(`lesson:mandatory-full-chain-smoke-before-unattended-run`, and
`lesson:season-batch-runner-per-round-fault-isolation` for the early-round PARK behaviour).

## F8 — the docs gate stalls if the held-out result triggers an owner decision · **REJECTED**

True, and **correct**. The decision anchor is supposed to record what actually happened; writing it
before the outcome is known would produce archaeology rather than current truth. Left as-is,
deliberately.

---

## Findings the critique did *not* dispose, and why

- **"This whole issue is scope creep past a one-line threshold change."** Considered and rejected on
  measured evidence, not judgement: the one-line version (candidate A) provably fails the issue's own
  acceptance in both directions. Recorded in `PLAN_ALTERNATIVES.md`.
- **"The predicate is a one-consumer seam."** True, and left standing as surfaced decision pressure
  in the g5 anchors rather than resolved — the owner may reasonably want it deferred until #678's
  sharpening pass actually wires it.
