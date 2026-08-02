# Implementation Result — G4 Verdict + Done-Done + Remainder

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4-implement` — 496-physics-aware-estimator, branch `feat/physics-aware-estimator-496`, MAIN checkout.
Assembly + judgment gate over the already-landed, already-reviewed G1–G3 work — NOT new estimator code.

## Completed slice
Wrote the GO/CONTEXTUAL/NO-GO **VERDICT** (`.agent-work/496-physics-aware-estimator/VERDICT.md`) keyed
to the #507 acceptance, and confirmed the #509 done-done bar is honestly met by re-running the suite and
the proof. No `src/` changes; no wiring; no retire.

**Verdict: GO** — on the #507 acceptance, for the tested scope (single driver VER, 3 circuits, 2023 Q,
default HPs, MEASURED-not-wired). Production-readiness explicitly deferred to **#518**.

## Verdict justification (from the scoreboard numbers)
The #507 acceptance — knee tracks raw on BOTH a hard-braking (Bahrain) AND a short-straight (Monaco)
circuit, with Monaco ringing under the raw ceiling — is met **literally and in full on both required
circuit types, simultaneously**:
- **Bahrain** (hard-braking): synthesis knee **−50.98** vs raw **−52.13**, gap **+1.15** ≤ 3.0 → PASS.
  The deep ~5 g knee is recovered; the baseline gap was +12.7 (knee rounded to −39.5).
- **Monaco** (short-straight): **ring_ok=True**, roc **−0.09 ≤ 0** → PASS. Under the raw +5.64 ceiling;
  baselines RING at roc +7.5/+7.7.
- **Belgium** (control): synthesis **−38.49**, gap +0.35 — actually **deeper** than the kind3 baseline
  −37.41; no regression → PASS.

Every estimate carries an honest per-sample `sigma_a` from the same RTS posterior (min ≈ 0.09
real-session). The execution path is single and canonical (`[E_total, F_vehicle]`, no `[v,a]` shim).
**Why GO and not CONTEXTUAL:** the acceptance criterion itself is a binary "tracks on both circuit
types" bar, and it is met on both, plus the control. The narrowness of the run (one driver, default HPs,
unwired) is real and is the reason production-readiness is DEFERRED — it does not weaken the acceptance
claim, which is explicitly scoped to "the #507 acceptance for the tested scope." Calling it CONTEXTUAL
would conflate "acceptance met" with "production-ready"; the verdict keeps those separate and honest.

## Done-done checklist (confirmed this gate)
1. **Suite green** — `py -m pytest tests/unit/physics tests/unit/preprocessing -q` →
   **627 passed, 6 skipped** in 820.52s, **exit 0**. (6 skips are pre-existing conditional skips, not
   failures.)
2. **Single canonical path** — confirmed by grep + inspection + git status:
   - Only `src/physics/layer2/decoupled_longitudinal.py` is the longitudinal estimator; state is
     `[E_total, F_vehicle]` over arc-length `s` (1D Kalman-RTS). **No `[v,a]` shim** in the module.
   - `grep decoupled_longitudinal src/**/*.py` → **0 importers** in `src/` (MEASURED-not-wired).
   - `StintSmoother` (`src/preprocessing/trajectory/smoother.py`) and `clean_longitudinal_from_raw`
     (`src/physics/layer2/braking_view.py`) are **untouched**. `git status` is clean — only
     `.agent-work/` untracked; the G3 files (module + test + proof) were already committed in
     `57335e7c`, reports are generated artifacts.
3. **Dashboard traceable** — `py scripts/prove_synthesis_496.py` → **exit 0**; the 3-circuit table
   reproduces identically (Bahrain gap +1.15 / Monaco ring_ok roc −0.09 / Belgium −38.49 deeper than
   kind3); the dashboard `reports/physics/synthesis_proof_2023Q.{json,png}` regenerates from the
   committed code.

## Scope
**Files changed:**
- `.agent-work/496-physics-aware-estimator/VERDICT.md` (NEW — the verdict)
- `.agent-work/496-physics-aware-estimator/g4-plan.json` (NEW — the gated engine plan)
- `.agent-work/496-physics-aware-estimator/crew-handoffs/g4-implement-result.md` (NEW — this file)

**Specific exclusions touched:** no. No `src/` modification, no wiring, no retire of
`clean_longitudinal_from_raw`, no `[v,a]` shim. Verified by `git status` (clean; only `.agent-work/`).

## Behavior changed
No. This gate is a verdict + verification over already-landed code. Zero production behavior change.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` (the estimator, unchanged — assessed, not
  modified) and `struct:physics.utilization` (the #518 consumer, named as the deferral target). No
  structural diff this gate.
- **Decision candidates / resolved decisions:** two durable candidates carried to G4/reconcile for
  authority — (1) decoupled-1D-longitudinal (fed by the raw-onset force anchor, not the 2D smoother;
  honors + extends `decision:two_cycle_external_anchor_design`); (2) total-energy/vehicle-force frame
  (`d(E_total)/ds = F_vehicle`). Plus the governing "evolutionary-not-revolutionary" structure decision.
  `decision:ideal_lap_sim_two_sided_evaluator` is the under-call signal the verdict reads (the C1
  consumer rationale).
- **Claims/evidence produced:** the 3-circuit scoreboard PASSES all three simultaneously (re-run this
  gate, exit 0); the focused suite is green (627 passed); honest `sigma_a` > 0 everywhere. These back the
  GO claim.
- **Triage candidates:** tc1 (terrain handle absent from the `CaseInputs` scoreboard seam) and tc2
  (a_long scoreboard structurally blind to the PE term — needs a gravity-corrected `F_vehicle` frontier
  metric), both #518. Full set-aside remainder enumerated in VERDICT.md.

## Test mode
**Required:** evidence-only (this gate runs no TDD — it re-confirms the landed suite + proof; the
estimator's own L1–L4 tests were authored and reviewed in G3).
**Satisfied:** yes — suite re-run green (627 passed), proof re-run exit 0 with the table reproduced.

## Evidence

```bash
py -m pytest tests/unit/physics tests/unit/preprocessing -q
# 627 passed, 6 skipped in 820.52s (0:13:40)  (exit 0)

py scripts/prove_synthesis_496.py
# 3-circuit table reproduced exactly; Bahrain gap +1.15 / Monaco ring_ok roc -0.09 / Belgium -38.49
# VERDICT: PASS — synthesis clears both acceptance circuits + no Belgium regression  (exit 0)
# Written: reports/physics/synthesis_proof_2023Q.{json,png}

git status
# clean — only .agent-work/ untracked (no src/ modification)

grep -r decoupled_longitudinal src/**/*.py
# 0 importers in src/ (MEASURED-not-wired)
```

**Result:** pass (suite exit 0 + count captured; proof exit 0 + table reproduced; single-path confirmed).

## TDD evidence, if required
N/A — evidence-only gate (no code change). The estimator's TDD (red→green→refactor on the TV denoise,
1D filter, synthetic-step recovery, covariance positivity) was done and reviewed in G3.

## Docs/contracts touched
- none in `docs/` (MEASURED-not-wired; no production contract changed). The estimator module docstring
  remains the interim contract; #518 wiring will update `docs/architecture` + report schemas.

## Assumptions
- The proof's 3-circuit table and terrain table re-derive deterministically from the cache at
  `C:/Programs/f1Brainz/data/telemetry`; both this-gate re-runs matched the committed
  `synthesis_proof_2023Q.json` exactly.
- The 6 suite skips are pre-existing conditional skips (e.g. optional-dependency / data-gated), not
  regressions introduced by #496 — consistent with the G3 evidence (which reported the same families
  green).
- "Single driver VER, default HPs, MEASURED-not-wired" is the honest scope ceiling on the GO; #518 owns
  the multi-session re-check before wiring.

## Stop conditions hit
- none. Both the suite and the proof reproduced green; the evidence supports an honest GO on the #507
  acceptance for the tested scope; no scope/authority breach.

## Out-of-scope observations
- **tc1 / tc2** (terrain seam + a_long PE-blindness) and the `clean_longitudinal_from_raw` retire are
  all #518 (the C1 consumer re-eval). The a_long acceptance metric will never reward the terrain work —
  #518 needs a gravity-corrected `F_vehicle` frontier metric.
- `validate_refine_505.py` cleanup (#504 territory) and the M8 ≥10 Hz revival are adjacent set-aside
  items, listed in VERDICT.md so Triage inherits the full set.

## Workflow Feedback
- **Handoff gaps:** none material — the handoff was unusually precise (exact close criteria, the 3-circuit
  table targets, the PE-invariance caveat, the retire-assessment carry, the two decision candidates, and
  the named remainder list with tc1–tc5). One small mismatch: the handoff's remainder bullet (criterion 5)
  references "engine triage candidates tc1–tc5," but the inbound g3-review only flagged **two** (tc1, tc2);
  I could not find tc3–tc5 in the read inputs, so I enumerated the named remainder items explicitly by
  topic in VERDICT.md rather than by a tc3–tc5 id I could not source. Naming five tc-ids when two exist is
  the only friction; resolving it by topic is the honest move.
- **Context rediscovered:** the suite count (627 passed, 6 skipped) is NOT in any input — the handoff said
  "re-confirm and capture the count," correctly, but the prior G3 evidence only captured the narrower
  `tests/unit/physics/layer2` runs (26 + 152). The full `tests/unit/physics tests/unit/preprocessing`
  count had to be produced fresh (and it takes ~13.5 min, not the ~85s the layer2-only run takes — worth
  flagging for the next gate's time budget).
- **Instructions improvised around:** the verification commands buffer through `Select-Object -Last N`,
  which holds ALL output until the process exits (so interim reads showed 0 bytes and looked stalled). I
  switched to redirecting to a temp file (`> $env:TEMP\out 2>&1; $LASTEXITCODE`) to get a deterministic
  exit code and the full table. Also: PowerShell wraps FastF1's stderr INFO log as a `NativeCommandError`
  in the captured stream even on exit 0 — benign, but it looks like an error on first read; `$LASTEXITCODE`
  is the truth.
- **What would have made this easier:** one line in the handoff — "the full focused suite is ~13.5 min
  (NOT the ~85s layer2-only run); budget for it" — plus a note that the proof's verification command
  should capture `$LASTEXITCODE` to a file rather than pipe through `Select-Object` (which masks interim
  progress). And reconciling the tc-count (tc1–tc2 actual vs tc1–tc5 named) in the handoff.

## Return status
`complete`
