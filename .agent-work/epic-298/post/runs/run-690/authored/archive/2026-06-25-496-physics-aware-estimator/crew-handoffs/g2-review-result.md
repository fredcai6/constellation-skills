# Review Result — G2 Portfolio Exploration (5 Spikes)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2-review` — 496-physics-aware-estimator, MAIN checkout, branch feat/physics-aware-estimator-496

## Result
`APPROVE`

**verdict: APPROVE**

## Handoff compliance

Handoff asked for: 5 spikes (M1/M3/M4/M7/M8), each measured on Bahrain/Monaco/Belgium, consolidated
into SPIKE_COMPARISON.md with per-spike result files, prototype code preserved in
`.agent-work/496-physics-aware-estimator/spikes/{mX}/`.

Delivered: All 5 result files present and complete. SPIKE_COMPARISON.md present with per-mechanism
scoreboard table and recommendation. Prototype code in `.agent-work/496-physics-aware-estimator/spikes/{m1,m3,m4,m7,m8}/`.
Both spike run scripts reproduce independently. Compliant.

## Scope drift

No src/ modifications. Working tree is clean for src/ (only `.agent-work/` is untracked).
No evo_predictor/latent_power/compound_prior imports in any spike file.
Prototype code lives in `.agent-work/` and worktree branches — not committed to the feat branch or main.
Scope constraint honored.

## Evidence verdict

Per-spike result files each contain: scoreboard tables for all 3 circuits, sweep tables,
failure modes section, soundness self-assessment, re-run commands, workflow feedback.
SPIKE_COMPARISON.md consolidates with a complete head-to-head table and per-spike verdict.

The two winners were independently re-run by this reviewer:

**M7 reproduction (run from agent-ab5d8f966aa1ff30d worktree):**

| Variant       | Circuit | knee (m/s²) | gap vs raw | ringing | ring_ok |
|---------------|---------|-------------|------------|---------|---------|
| m7_e0_s0.20   | Bahrain | **-50.274** | **+1.857** | -2.924  | OK      |
| m7_e0_s0.30   | Bahrain | -50.037     | +2.094     | -2.995  | OK      |
| lam=0.1       | Bahrain | **-51.822** | **+0.309** | —       | OK      |
| m7_e0_s0.20   | Monaco  | -35.035     | +2.478     | 6.384   | **RING!** |
| m7_e0_s0.30   | Belgium | -36.751     | +2.089     | 4.566   | OK      |

Matches claimed values within 0.01 m/s². Bahrain win confirmed (gap +1.86 better than ~+1.9
threshold). Monaco ringing at roc +0.74 RING! (claimed failure) confirmed.

**M3 reproduction (from main checkout via importlib to worktree filter_m3.py):**

| Variant  | Circuit | knee (m/s²) | gap vs raw | ringing | ring_ok |
|----------|---------|-------------|------------|---------|---------|
| m3       | Bahrain | **-39.489** | **+12.64** | -8.67   | YES     |
| m3       | Monaco  | -38.57      | -1.06      | **2.97**| **YES** |
| m3       | Belgium | -37.32      | +1.52      | -2.21   | YES     |

Matches claimed values within 0.01 m/s². Monaco ringing=2.97 (ring_ok YES) confirmed.
Bahrain unchanged from baseline confirmed. Synthetic sanity check PASS (error -3.97 m/s², |error|<5).

Evidence is sufficient and demonstrates the behavior. Required evidence satisfied.

## Code/doc quality

All 5 result files include honest failure mode sections, soundness self-assessments, and
workflow feedback. Spike code imports only from src.physics.layer2 / src.preprocessing paths.
No mutable module-level state introduced in src/. Belgium RTS leakage artifact in M1
(-22 m/s² non-throttle, physically implausible) is correctly flagged as artifact, not claimed
as real. Quality criterion met.

## Map impact verdict

- **Evidence supports claimed change:** Reproduced M7 Bahrain knee -50.27 and M3 Monaco ring 2.97
  independently. Evidence backs claimed behavior/capability findings.

- **Constraints not violated:** `decision:two_cycle_external_anchor_design` respected across all
  spikes: M7's anchor derives from TV-denoised RAW a_long_raw (never from smoothed trajectory);
  M3 bypasses the anchor channel entirely (parallel 1D estimator). M1's model-anchor extension
  is explicitly justified and identified as the reason for its failure. M4 adds zero anchor
  observations. M8 explicitly notes invariant extension.

- **Notes match the diff:** Spikes are throwaway prototypes; no durable src/ changes. Map impact
  notes in result files correctly state "none" for structural changes. One new decision candidate
  ("longitudinal a_long from decoupled 1D physics filter fed by raw-onset anchor") is surfaced
  explicitly as a candidate for G3, not claimed as committed.

- **Decision candidates surfaced:** Decision candidate for G3 (decoupled 1D longitudinal estimator
  as the synthesized path) correctly identified in SPIKE_COMPARISON.md "Invariant-extension surface"
  section and result files. Authority required for that decision is correctly deferred to G3.

- **Durable context routed:** The new decision candidate is documented in SPIKE_COMPARISON.md and
  per-result files for Commander/Cartographer to pick up at G3 closeout. No context dropped.

Map impact: not applicable for architecture blocking (throwaway spike gate); all notes are
appropriate.

## Reconciliation check

No durable architecture changes. Spikes are in `.agent-work/` and worktrees only. The identified
decision candidate (M7+M3 longitudinal decoupling) is surfaced as a G3 input, not committed.
Cartographer reconciliation not required for this gate.

Triage candidate: M8 revival requires ≥10 Hz car telemetry (a separate future scope path).
Surfacing as out-of-scope observation for Commander/Triage below.

## Blockers

- none

## Out-of-scope observations

- **M8 requires ≥10 Hz telemetry**: The M8 result file correctly identifies the revival conditions
  (car telemetry ~44 Hz throttle/brake channels). This is a separate future path not part of the
  current evolutionary scope. Triage candidate if/when that data path is added.
  (SPIKE_COMPARISON.md already notes this under "Drop M1, M4, M8 standalone.")

- **M3 run script path fragility**: The M3 run script (`run_m3_scoreboard.py`) hard-codes the
  worktree path `C:/Programs/f1Brainz/.claude/worktrees/agent-aff9de88b4e6d6d6c`. It ran
  successfully because that worktree still exists, but this is fragile. If worktrees are cleaned,
  the M3 spike is not easily re-runnable without updating the path. The archive copy at
  `.agent-work/.../spikes/m3/filter_m3.py` is the durable copy; G3 should import it differently.
  Not a blocker for this review gate, but worth noting for G3 setup.

- **M7 run script not self-contained from main checkout**: `run_m7_final.py` imports
  `src.physics.layer2.m7_tv_filter` via the standard path — this only works when CWD is the M7
  worktree (where the module is present). Running from main checkout (as the handoff instructs)
  requires the worktree to persist. The archived spike file exists but the import path would need
  adjustment for standalone use post-worktree-cleanup. Not a blocker now; worktrees are still
  present. Note for G3: integrate m7_tv_filter.py explicitly rather than relying on worktree path.

## Workflow Feedback

- **Handoff gaps:** The g2-review.md handoff says to run scripts from "the MAIN checkout (they are
  self-contained — import the committed scoreboard + their own copied module)". This is partially
  inaccurate: both winners' run scripts depend on modules (`m7_tv_filter.py`, `filter_m3.py`)
  that are NOT in the main checkout src/ path — they live in their respective worktrees. The scripts
  only work if those worktrees still exist. The handoff should say: "run from the M7 worktree
  (agent-ab5d8f966aa1ff30d) for M7, and from main checkout (M3 worktree still accessible via
  hard-coded path in run_m3_scoreboard.py)." The "self-contained" claim overstates portability.

- **Context rediscovered:** Had to discover that `m7_tv_filter.py` is not in main checkout
  src/physics/layer2/ and that the spike scripts need the worktree as CWD. This took one
  exploratory step before running correctly. The handoff gave the literal `py` command but not
  which directory to run from.

- **Instructions improvised around:** The engine reference (`references/checklist-engine.md`) was
  not found at the expected path within the skill. Used the `checklist_engine.py` script directly
  from the skill's scripts/ directory, which functioned correctly. The survey type worked as
  expected with `record` + `consolidate`. No behavioral deviation.

- **What would have made this easier:** Add a "CWD for each run script" field to the handoff
  evidence section, e.g., "M7: cd .claude/worktrees/agent-ab5d8f966aa1ff30d then py ...; M3: cd
  C:/Programs/f1Brainz then py ... (uses hard-coded worktree path in script)." One line per winner
  eliminates the worktree-discovery step.

## Return status
`complete`
