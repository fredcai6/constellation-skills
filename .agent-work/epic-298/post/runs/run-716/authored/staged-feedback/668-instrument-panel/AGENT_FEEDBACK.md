# Agent Feedback — staged (fenced) for 668-instrument-panel

## 2026-07-26 — 668-instrument-panel (delegated commander, epic #659 Wave 4b)

**Instruction adherence**
- Drove the full delegated-commander spine through the engine end to end (init → context →
  understand → plan → execute → reconcile → triage → review → feedback → archive), never
  hand-editing a checklist. All artifact-check postconditions satisfied via `attach` (not `attest`)
  on both `gN-review` and `gN-integrate` — the standing `lesson:engine-artifact-attest` pattern.
- All 10 crew dispatches (5 implement + 5 review, incl. one rework pair) used
  `run_crew.py --backend external` + `--verify-result`, with `recover_crews.py` before each.
- F12 HARD GATE honored: `REPLICATION_*` pre-registered evidence-only (support/structure reads only,
  no outcome), floated to the Admiral, real-data run BLOCKED at g5 until the owner's signature; froze
  the signed values EXACTLY.
- Fenced hygiene: shared feedback/lessons staged here, never committed; `data/f1_data_2023.db`
  WAL-touches restored via `git checkout --` at every boundary; no `docs/architecture/*` touched
  (map staged as `notes-668.md` + `668-cartography/`).

**Friction / unclear**
- The `py` launcher's default env lacks `radon`, so `src.utils.simplification_limits` raised a
  RuntimeError there; the PINNED interpreter has it. Re-verifying a crew's `simplification_limits`
  claim must use the pinned interpreter, not bare `py` — a subtle env split beyond the editable-.pth trap.
- `driver_class_observables` is round/circuit-aggregated (not lap-grain), and the launch order's
  "GB-only" data premise was STALE — the archived #666 slice actually holds 4 circuits × 4 drivers.
  A `n_points` support probe (reconciling the order's baseline against the real on-disk state) was
  load-bearing: it flipped the split-half unit from a weak within-session lap split to the
  statistically-correct cross-circuit 2v2, and forced a scope float to the Admiral.

**Where I improvised**
- At the g5 F12 hard gate, with all F12-independent work done and nothing to poll (the sign-off is a
  human-routed decision), I made the block VISIBLE (SendMessage + STATE_NOTE) and yielded the turn as
  a governed reach-up — distinct from the background-watcher anti-pattern. The Admiral resumed me with
  the signature (a query round-trip, context intact). Correct boundary for
  `lesson:delegated-commander-foreground-poll-over-watcher-yield`: foreground-poll a finite compute
  job; yield-with-a-clear-message a human-gated sign-off.

**What would have helped**
- A one-line note in the launch order that the archived own-DBs (#664/#666) live in the MAIN-checkout
  `.agent-work/archive/` and carry more than GB would have saved a reconciliation cycle.
- Naming `src.utils.simplification_limits` as a required close-criterion in the g7 script handoff from
  the start would have avoided the one rework cycle.

**Crew-reported friction**
- The g3 implementer surfaced a genuine mathematical degeneracy (within-class, double-centering ≡
  per-driver-demean because a per-class constant is correlation-invariant) and resolved it so the
  interaction r spans classes — the g3 reviewer re-derived it from scratch (Δr = 1.1e-16). A
  load-bearing catch an output-only test would have missed.
- The g4 implementer flagged that composed-sector `n_eff` wasn't pinned by the handoff (only σ's
  independence-sum was) and chose `min(member n_eff)` as a documented Build-1 default — a real
  handoff-completeness gap I should have pinned up front.
- The g7 reviewer's BLOCK on `simplification_limits` surfaced only because the reviewer ran a project
  gate the implementer skipped — the handoff should have named it a required close-criterion.

**Improvement signals**
- The cold plan critic caught the load-bearing golf-correction defect (per-driver demean leaves the
  shared class main effect → flatters) BEFORE any code was cut — the highest-value moment of the run;
  double-centering + the 3-arm-plus-negative-control falsifier came directly from it. Critiquing the
  plan (not just the code) is what made it cheap.
- Building the four instruments synthetic-only while the F12 set was out for owner signature kept the
  run productive through a human-latency block — the launch order's "build in parallel meanwhile"
  mandate paid off directly.
- The g7 reviewer correctly BLOCKED on a project gate even after confirming every substantive result;
  one surgical refactor rework cleared it, output byte-identical — the evidence gate working as intended.
