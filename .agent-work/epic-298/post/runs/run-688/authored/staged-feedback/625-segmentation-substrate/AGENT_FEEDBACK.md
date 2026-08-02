## 2026-07-18 — 625-segmentation-substrate (ShipC-625, delegated under Admiral epic #601; issue #625 Phase 1 segmentation substrate)

**Run shape:** commander (delegated) · full spine driven understand -> plan (plan-alternatives:
2 candidates, smallest-diff vs most-testable, converged to a named hybrid; cold plan critic:
6 findings, all triaged/baked into the converged plan) -> execute (4 crew gates: g1
straight-arc grouping + descriptor axis, g2 soft/fractional property-class mixture, g3 the
mandatory F12 falsifiable gate, g4 regime distance-share rollup + observability router) ->
reconcile (Cartographer, packet + index updated) -> triage (8 candidates routed: 1 fixed-now,
3 filed as 2 GitHub issues #638/#639, 2 recommend-and-deferred as workflow feedback) -> review
-> feedback (this entry) -> archive. Sonnet subagents for all 8 crew dispatches (implement +
review per gate), commander-direct for plan-alternatives convergence, cold critic dispatch,
and Cartographer dispatch.

**Instruction adherence:** fully followed the launch order and skill doctrine, with one
mid-run Admiral float (the F12 real-data FAIL — a genuine capability-ledger/scope-adjacent
decision, correctly routed up rather than adjudicated alone) and one Admiral-authorized
mid-flight plan deviation (waiving the self-authored full-suite regression check after it
proved impractically slow — see Friction below), both explicitly cited through the engine
(`waive g4-integrate --cond c3 --authority "Admiral (team-lead...)"`).

**Friction / unclear:**
- The full-physics-suite regression check I folded into g4-integrate's closing postconditions
  (`py -m pytest tests/unit/physics -q`, my own plan addition, not launch-order-mandated) took
  60-90+ minutes and was reaped by the harness TWICE (a manual background copy at ~90% clean,
  then the engine's own authoritative `advance` invocation) before I floated to the Admiral and
  got authorization to substitute a targeted regression subset (grep the real import graph of
  the two changed EXISTING files — `arcs.py`, `segment_classifier.py` — found 7 test files,
  170/170 pass in ~21 min) plus the partial 90%-clean evidence. This directly confirms
  `lesson:admiral-owns-long-batch-compute`'s core claim (harness-tracked background workers in
  a Commander context are not reliable for multi-hour compute) even though this specific check
  wasn't itself multi-hour by DESIGN — it just turned out to be, because I never sized it
  before freezing it into the plan. Distilled to a new bank-add lesson (see lessons-delta.json)
  since this is the first observed instance of "self-authored plan-time check, unsized before
  freezing" as its own failure shape, distinct from the existing lesson's "Admiral should OWN
  known-long compute" framing.
- `checklist_engine.py current` does not accept `--session-id` (read-only, per doctrine —
  "Read-only current needs no session") — I passed it once out of habit after several
  session-scoped calls in a row and got a usage error; harmless, one-call correction, but a
  small daily-friction point worth naming since the doctrine text states this but it's easy to
  muscle-memory past.
- Two `advance <gate>`/`start <gate>` sequencing slips (g1-implement and g4-integrate's
  `advance` calls were issued before the corresponding `start`) — both self-caught immediately
  from the engine's own `REFUSED: ... must be in-progress to advance` message, corrected by
  running `start` first. Not a doctrine gap, just an ordering mistake under my own
  distraction while multitasking the background-suite wait.

**Crew-reported friction (harvested from gN-integrate Workflow Feedback sections):**
- g1 implementer: my handoff mis-cited `session_braking.py` as `identify_braking_arcs`'s
  caller — the real (and only) caller is `braking_report.py::plot_arcs`. Self-corrected by the
  implementer against real source, zero downstream impact, but a wasted grep round-trip.
  Routed as a triage `recommend-and-defer` (ephemeral handoff file, not worth a GitHub issue)
  rather than fixed, since the handoff itself is archived, not a durable template.
- g3/g4 implementers (independently): my `CONVERGED_PLAN.md` prose was terser than (and in one
  case read as implying a different technical resolution than) the fuller, more current
  implementer handoffs — both correctly deferred to the handoff as binding when the two
  diverged, and both flagged the gap unprompted. This is a real authoring lesson for me
  specifically (write the plan doc's technical details as precisely as the handoff, or
  explicitly mark the plan doc as "superseded by handoff on divergence") — routed as
  `recommend-and-defer`, not GitHub-issue-worthy (wave-scoped planning artifact, archived at
  closeout).
- g4 implementer: the handoff's "Required Evidence" list was narrower than `CONVERGED_PLAN.md`'s
  own Gate-4 prose (which additionally named the full-suite regression + evo-import grep as
  part of "this gate's integrate step") — the implementer correctly read this as
  Commander-integrate-step scope, not theirs, and flagged the ambiguity rather than guessing.
  Confirms the value of explicit "target postcondition id" citations (per
  `references/global-orchestrator.md`'s handoff-completeness guidance) — I had these in most
  handoffs but the Gate-4 handoff's Required Evidence section could have named the integrate-only
  checks explicitly rather than relying on the implementer to cross-read CONVERGED_PLAN.md.

**What worked:**
- The cold plan critic (no authoring context) caught a genuine, load-bearing technical error
  before any code existed: my converged plan's rollup design would have silently labeled a
  corner-gated-only arc-length distance proxy as "time_share," conflating distance with actual
  lap time — a real correctness gap in a deliverable whose whole point is honest,
  believable physics features. All 6 critic findings were triaged and baked into `execute.json`
  before any gate dispatched; zero were discovered mid-execution instead.
- The F12 falsifiable gate's mandatory discriminating test (prove the check can FAIL on a
  shifted-generator scenario, not just PASS on a same-generator one) was independently verified
  genuine by two different reviewers, and it then did its job for real — the real-data run
  FAILED, cleanly and unambiguously (every one of 5 splits hit the pre-declared k-mismatch
  auto-fail before the distance-threshold comparison was even reached). This validates the
  falsifiable-gate design pattern itself, not just the specific substrate under test: a check
  built to be able to fail, and independently proven able to fail on synthetic data, produced a
  trustworthy real-world negative rather than a checkbox that could only ever pass.
- Independently reproducing every crew claim before integrating (test re-runs, real-data script
  re-runs including a byte-identical 5-minute-plus reproduction of the F12 real-data verdict,
  `git status`/`git diff` scope checks) caught zero false claims this run, but is exactly why
  the F12 FAIL could be reported to the Admiral with full confidence rather than hedged.
- Floating the F12 FAIL to the Admiral rather than either (a) silently shipping it as if
  validated, or (b) unilaterally deciding to rework it myself, let the actual epic-owner
  decision (ship provisional now, rework as a tracked follow-on) get made by the party with
  the standing to make it — exactly the "delegate is not a replacement" doctrine working as
  intended.

**Improvement signals:**
- Self-authored plan-time regression checks need cost-sizing before freezing into a gate plan
  → distilled to a new bank-add lesson (needs re-observation across a couple more runs before
  graduating to a standing doctrine statement).
- `lesson:admiral-owns-long-batch-compute` re-confirmed with a new nuance (a Commander without
  Admiral-owned detached infra available should float-and-fallback rather than block
  indefinitely) → confirm op with grounding.
- Plan-doc-vs-handoff precision mismatch (CONVERGED_PLAN.md terser than the binding handoffs,
  flagged independently by two crews) — judged wave-scoped/ephemeral, not worth a standing
  lesson this run, but worth a self-note for future plan authoring: match the handoff's
  precision level in the plan doc's own technical bullets, don't rely on the handoff alone to
  carry the exact mechanics.

No bare-none: all sections carry run-specific content.
