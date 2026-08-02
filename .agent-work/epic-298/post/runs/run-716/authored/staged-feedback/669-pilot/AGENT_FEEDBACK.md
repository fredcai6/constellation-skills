# Agent Feedback — staged (fenced)

Staged worktree-local per LAUNCH_ORDER-669 (fenced off the shared durable log). The Admiral harvests this into the
durable `.agent-work/AGENT_FEEDBACK.md` at epic closeout. See FENCE.md.

## 2026-07-27 669-pilot (3-circuit end-to-end pilot / tracer bullet — delegated commander, OPUS)

**What the run was:** wire the six landed epic-659 stages into ONE offline pipeline + run on Monaco/Belgium/GB
2023-Q. Drove the full spine through the engine (init→archive); 3 execute gates (g1 reasoning probe, g2 crew build,
g3 reasoning run). Outcome: all 3 circuits fresh, all C/D/E/H gating PASS, all 6 slots ran, report written.

**Friction / unclear**
- The g3 auto-emitted report is a per-circuit gating dump; the launch-order acceptance ("names anything broken +
  #670 implications") is a COMMANDER-authored synthesis, not something the pipeline emits. I augmented the report by
  hand at g3. A future pilot-style plan should state up front that the run gate owns a narrative synthesis section on
  top of the machine report, so it is not mistaken for auto-generated.
- The spine's reconcile step's default is "dispatch a cartographer to fold into docs/architecture"; my launch order
  hard-fences docs/architecture (→ #671). The compliant path (stage MAP_DELTA prose in 669-cartography/, no map edit)
  is the epic-wide pattern but is not the spine imperative's first reading — I resolved it to the fence, which is the
  closest compliant thing. Worked cleanly; noting the divergence per doctrine.

**Crew-reported friction**
- g2 implementer: the handoff said "run grip fit D as a subprocess" with a 180s timeout, but the landed D entry point
  (`run_grip_batch`) is an in-process function bounded by restricting it to the 3 pilot circuits — wrapping it in a
  subprocess purely to time it would be ceremony. The implementer ran D in-process (circuit-bounded) and enforced the
  wall-time budget on E (the genuinely heavy subprocess) — a sound misfit resolution. Future handoffs should say
  "budget the heavy subprocess stages (E); in-process stages bounded by scope need no subprocess timeout."
- g2 implementer: the handoff named the stage entry points but not that (a) G/H fit needs a `ClassVocabulary` DERIVED
  from the observables DB (found via the #667 harness pattern), and (b) the D held-out logic reconciles a session PAIR
  (FP2/FP3), so a Q-only / missing-FP circuit's held-out sub-score legitimately PARKs. Anchoring these two seam facts
  in the handoff would have saved a read pass each. (Belgium's held-out did park on missing FP data at g3 — expected.)
- g2 implementer: named a real false-positive risk — the FastF1-fallthrough detector first matched a benign "fastf1"
  library mention and parked a genuinely-fresh E run as fell-back (inverting provenance). The MANDATORY GB full-chain
  smoke (cold-critic fix #1) is what caught it; narrowing markers to the precise store-miss warning fixed it.
- g2 reviewer: two non-blocking finds → triage (report-path default writes tracked docs on a bare run; critic-#3
  non-empty-gating negatives under a fixture-level skipif = latent vacuity if fixtures absent).

**Improvement signals**
- The cold-plan-critic's mandatory "first full-chain run must NOT be the unattended run" (fix #1) directly earned its
  keep: it caught a silent provenance-inversion bug that every unit test passed over. Strong evidence for banking a
  lesson that a mandatory end-to-end smoke before an unattended run catches integration-only silent-correctness bugs.
- The g1 feasibility probe (cheap, one circuit) de-risked the whole AFK build: it measured offline-safety + wall-time
  (~65s/circuit) + surfaced the two non-blocking CLI issues (G abs-path, H σ/cp1252) BEFORE the build, so g2 was
  designed against measured reality, not a guess. Confirms the "diagnose-before-fixing / feasibility-probe" posture.
- The delegated-commander foreground-poll held: I polled the detached g3 run in-context (bounded loops + the bg
  completion notify), never ended-turn-to-wait; the run completed and I integrated it in the same turn.
- Reversibility discipline (scratch-copy of the tracked f1_data DB for E's --per-year-db; absolute MAIN paths for the
  gitignored input stores) kept the worktree clean — final diff is code+tests+report only, zero tracked-DB churn.
