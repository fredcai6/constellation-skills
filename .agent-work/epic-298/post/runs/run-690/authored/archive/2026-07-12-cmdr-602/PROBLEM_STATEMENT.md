# Problem Statement — cmdr-602 (#602 mission consolidation)

## Reconciled ask (launch order cmdr-602.md, Mission + Pre-Rulings)

Two edits:
1. Consolidate the project mission statement into `AGENTS.md` (fantasy-league-win framing, delta-sum + progressive
   bingo scoring, 674/853/+7.5pts-per-race bar, self-contained decision metric vs. actual results, league
   placement informational-only, co-pilot `race-week` loop, physics-explainer secondary goal).
2. Fix `CLAUDE.md`'s stale `evo_predictor` description (issue text: "it still describes the retired 24-parameter
   vector / scorer.py / ranker.py path. The live system is the 3-stage sampled race-weekend simulator
   (`sampled_runtime.py`) over 12 neural latent-power modules with Bradley-Terry field solve + precision-weighted
   fusion.")

## Verification against source (Pre-Ruling: verify before writing)

**Live architecture — CONFIRMED accurate as described in the launch order:**
- `src/evo_predictor/sampled_runtime.py` — `SampledEvoRuntime.predict_from_features` runs three sequential
  stages: `_run_quali_stage` (quali), `_run_sample_aligned_stage("race_start", ...)`, `_run_sample_aligned_stage("race", ...)`
  — a genuine 3-stage sampled race-weekend simulator (lines 199-296).
- `src/evo_predictor/module_adapters/_registry.py` registers 15 total latent-power modules; of those, 6
  `*_FROM_RACE_WEEKEND` + 6 `*_FROM_RECENT_HISTORY` = 12 form the production sampled-runtime manifest (the
  remaining 3 `*_FROM_RESIDUAL_HISTORY` are `supports_training=False` scaffolding) — matches
  `docs/architecture/packets/evo_predictor.md`'s existing "12 of them" claim.
- `src/latent_power/field_solve.py` line 138 explicitly names the "Bradley-Terry gauge freedom" — Bradley-Terry
  field solve confirmed.
- `src/evo_predictor/fusion.py` `fuse_module_fields_ordered` implements `_apply_ordered_precision_update`
  (`fusion_mode: "ordered_precision_update_v1"`, `prior_precision + obs_precision` composition) — precision-weighted
  fusion confirmed.

**CLAUDE.md's actual current content — issue premise is FALSE.**
`git log --follow -p -- CLAUDE.md` shows CLAUDE.md was created FRESH (`--- /dev/null` / `+++ b/CLAUDE.md`) in
commit `eba82d2b` (2026-07-05, PR #585, an unrelated ideal-lap/ephemeris feature squash-merge). It has never
contained any evo_predictor architecture description, stale or otherwise — current content (14 lines) is a lean
bootstrap pointer file: doc pointers + 3 "Critical runtime notes" bullets (py launcher, pytest command, DB-only
analysis). `grep -i "24-param|scorer.py|ranker.py"` over the whole worktree finds it in exactly 3 files, none of
which is CLAUDE.md: `docs/evo/practice_preprocessor.md`, `docs/architecture/packets/evo_predictor.md`, and an
archived checklist. `src/evo_predictor/ranker.py` does not exist (confirmed by `find`). `src/evo_predictor/scorer.py`
DOES exist but its current content is unrelated small helpers (`_circuit_distance`, `_compound_distance`) — not
the 24-param `score_drivers(...)` function my own session MEMORY.md describes.

**Where the stale description actually lives:** the operator's personal Claude Code memory file
(`C:\Users\fredc\.claude\projects\...\memory\MEMORY.md`, auto-loaded into every session's context) still carries
the Feb-2026 "24-parameter vector / scorer.py / ranker.py" architecture note under "## evo_predictor Architecture".
That file is not part of this git repo and is outside this run's file-ownership fence (`AGENTS.md` + `CLAUDE.md`
only). It is the actual vector by which agents get misled about the retired path — not `CLAUDE.md`.

**Secondary drift found (out of fence, floated as triage):** `docs/architecture/packets/evo_predictor.md` line
122-123 still describes `scorer.py` as "Scores drivers given features and the 24-parameter vector. Used in legacy
path" — that description no longer matches the file's actual current content (verified above). This is real
packet drift the Cartographer reconcile step should pick up, but it is not `CLAUDE.md`/`AGENTS.md` and outside my
fence to edit directly.

## Resolution (Honest-Null Clause: report, don't guess)

Per the launch order's Honest-Null Clause ("if the live-architecture verification reveals the issue's description
is itself wrong in some respect, report that finding rather than encoding a guess") and the delegate-not-replacement
doctrine (asking up is sanctioned but not mandatory when the gap is resolvable from source): this is resolved, not
ambiguous. Plan:
- Edit 1 (AGENTS.md mission) proceeds exactly as specified — the ask there is confirmed accurate and unaffected.
- Edit 2 (CLAUDE.md) — since there is no stale text to literally replace, add a concise, source-verified
  evo_predictor architecture pointer (3-stage sampled runtime / 12 latent-power modules / Bradley-Terry +
  precision-weighted fusion) to CLAUDE.md's existing lean pointer style, satisfying the spirit of "stop agents
  from being misled by a dead-architecture description" without fabricating a "fix" for text that was never
  actually there. Report the false premise plainly rather than silently treating the edit as a no-op.
- Report the MEMORY.md finding and the packet-drift finding to the Admiral for follow-up (not mine to action;
  MEMORY.md is outside the repo and the git-tracked file-ownership fence, packet drift is outside my two-file
  fence).

## user-decision citation

Satisfied by `LAUNCH_ORDER:Mission` + `LAUNCH_ORDER:Pre-Rulings` (first bullet: verify-before-write) +
`LAUNCH_ORDER:Honest-Null Clause`. No Admiral query required — the gap is resolved from source, not a genuine
ambiguity, per Stop Conditions ("you find a genuine architecture ambiguity you cannot resolve from source" — this
one WAS resolved).
