# AGENT_FEEDBACK (staged) — cmdr-664

## 664-reference-laps — 2026-07-26 (cmdr-664, delegated)

Issue #664, epic #659 Wave 2. Branch `epic659/664-reference-laps-utilization`. Delegated
commander, Admiral AFK-relayed.

### Instruction adherence
Drove the full delegated-commander spine through the engine end-to-end
(init→context→understand→plan→execute→reconcile→triage→review→feedback→archive) with a gated
4-gate `execute.json` child. Zero rework across all 8 crew dispatches; every gate closed
first-pass APPROVE. All four `user-decision` checkpoints satisfied by citing the launch order.
Ground-truthed every crew result (`run_crew.py --verify-result` + re-ran each gate's tests in
my own hands + inspected the g4 artifact) before advancing — no claim accepted on assertion.

### Lessons that held (confirmed this run)
- engine-artifact-attest — attach for every artifact-check postcondition; attest --which for
  null; advance for command postconditions. Standing constellation debt.
- run-crew-cli-launcher-misfit — all 8 dispatches via run_crew.py --backend external + Agent
  tool + recover_crews before each + --verify-result.
- shared-files-not-on-mission-branch — feedback trio staged under
  .agent-work/staged-feedback/664-reference-laps/; .agent-work never committed on the branch.
- from-child-refuses-on-gated-checklist — execute.json driven to done, child lease released,
  then plain attest execute.c1 (no --from-child).
- loo-residual-diagnostic — the g4 jackknife is out-of-sample delete-d/driver-block, not
  self-weighted (strictly_pre scoring ceiling; field reference lap only places boundaries).
  The cold plan critic's F1 forced the leverage design before any code.
- admiral-owns-long-batch-compute — kept the g4 real-data run foreground + bounded (62s, one
  circuit); scoped the g4 regression to the import graph (184 tests), not the full suite.
- delegated-commander-foreground-poll-over-watcher-yield — all crews dispatched synchronous
  foreground; zero idle-yields, zero nudges.

### Where I improvised / worked around
- Harness constraint: an in-process teammate cannot spawn background OR named subagents. I
  adapted to synchronous unnamed Agent(run_in_background=false) — which is exactly the
  foreground pattern delegated-commander-foreground-poll recommends, so the constraint forced
  the good behavior.
- Open async scope float: #661/#662 forward-reference "#664 = Build 3 seeded/supersede write
  path" — a different deliverable than the launch order. I floated it to the Admiral and
  PROCEEDED under Reading A (seeded/supersede OUT of scope, stays NotImplementedError) because
  the order is recent + self-consistent + tells me to consume the map as-is, and my 4 gates
  hold under BOTH readings (a "Build 3 IS in #664" answer only ADDS a gate via amend). The
  Admiral did not reply during the run; cite-and-proceed on the authoritative order. Logged as
  triage T1.
- Map fence: did not dispatch a cartographer (docs/architecture fenced); recorded map impact as
  staged prose for the epic's single closeout cartographer. Closest-compliant.

### My handoff-quality notes (fix in future handoffs — not playbook adds)
- g1 handoff said "ANY new numeric threshold = BLOCK" — over-broad; a float-equality tolerance
  is not a domain threshold. Word it "any new PHYSICAL/domain threshold".
- g3 handoff's read-only schema pointer cited build_driver_utility_observables.py; the actual
  sibling-schema source is driver_utility.py. Harmless (right table mirrored) but cite exactly.
- g4 Deliverable Path Check missed that .agent-work/**/*.db was not gitignored, so the run's
  own-DB was committable; the implementer added the ignore line. Pre-check ignore coverage for
  run-output DBs.

### Crew Workflow Feedback (harvested at each gN-integrate)
- g1: no-ratio test self-caught a docstring token; reworded.
- g2: additive .gitignore line for the own-DB (own-DB wasn't ignored); flagged, benign.
- g3: reviewer confirmed the σ⁺ pace-second scale attaches only to the time-deficit (not m/s);
  routed to triage T2.
- g4: artifact persists only per-class SUMMARIES (not raw replicate vectors), so the reviewer
  re-ran the pure jackknife math to recompute (a stronger check). Note for future validation
  artifacts: persist enough to re-derive, or expect a full recompute.

### What would have helped
A durable epic-level answer on the #664-vs-Build-3 naming up front would have removed the one
open uncertainty; absent it, cite-and-proceed under the authoritative order worked and cost
nothing (gates held under both readings). This is not a 'none' — it is the single named gap.

**Friction / unclear**
- The #664-vs-Build-3 naming discrepancy (stale #661/#662 forward-refs) was the one ambiguity;
  resolved by floating + proceeding under the authoritative launch order (Reading A).
- The engine feedback step's imperative says to `apply_lessons_delta.py` against the shared
  `.agent-work/LESSONS.md`, but the launch-order fence says STAGE the trio; the closest-
  compliant path (stage, let the Admiral apply centrally) had to be reasoned out.
- `verify_agent_feedback.py` requires exact bold signal-section names (Friction / unclear,
  Crew-reported friction, Improvement signals) — not discoverable without reading the script.

**Crew-reported friction**
- g1: the "ANY new numeric threshold = BLOCK" wording was over-broad (a float-eq tolerance is
  not a threshold) — my handoff wording, fix in future.
- g3: my read-only schema pointer was mis-pathed (build_driver_utility_observables.py vs the
  actual driver_utility.py) — harmless but cite exactly.
- g4: the run own-DB under .agent-work was committable (ignore block didn't cover *.db); the
  implementer added the ignore line. Pre-check ignore coverage in the Deliverable Path Check.
- g4: the jackknife artifact persisted only per-class summaries, so the reviewer re-ran the
  pure math to recompute — persist enough to re-derive next time.

**Improvement signals**
- The design-it-twice + cold-plan-critic at plan time paid off decisively: the critic's F1/F2/F3
  SERIOUS findings (jackknife leverage, positive control, no-literal-band) were folded BEFORE
  any code, and the resulting g4 gate produced a real, robust, positive-control-fired result.
- Synchronous foreground crew dispatch (forced by the harness) gave zero strands and zero
  nudges across 8 dispatches — a clean confirmation of the foreground-poll doctrine.
- Ground-truthing every crew result (verify-result + local re-run + artifact inspection) caught
  nothing wrong this run, but is cheap and is what makes "no claim on assertion" real.
