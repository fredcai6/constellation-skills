# Constellation Agent Feedback

## 671-reconcile (2026-07-27) — architecture reconcile + lineage dispositions (epic #659 Wave 5b, delegated)

**Instruction adherence.** Drove the delegated-commander spine fully through the
engine (init → context → understand → plan → execute → reconcile → triage → review →
feedback → archive), one step at a time, never hand-editing the JSON. All four
execute gates were **reasoning gates** (crew waived per commander-core "Crew gate vs
reasoning gate" — pure doc/map edits, full context held from three read-only research
sweeps); independent scrutiny came from pre-authored mechanical invariant chains + a
cold plan critic + an independent cartographer content-verify at the reconcile step,
not from crew implement/review. No `run_crew.py` dispatch this run — the run had no
crew (code-producing) gates; the Agent-tool subagents used were research/critic/verify
aids for reasoning gates, which is the correct shape, not the `run_crew` path.

**Friction / unclear**
- Engine verb-ordering trap (recurred twice): I attested/attached a step's
  postconditions while it was still `pending` (attest/attach are accepted in `pending`),
  then `advance` refused with "must be in-progress" — had to `start` then `advance`. Hit
  at `plan` and again at `triage`. Minor but repeatable; the imperative doesn't flag that
  you must `start` before the closing attest/advance even though attest works earlier.
- `durable_root()` resolved to the WORKTREE (not main) because a concurrent Admiral
  epic-lease `spine.json` lives in the main checkout — so the fenced staged-trio path
  fired for real. Matches `lesson:shared-files-not-on-mission-branch` history; not new,
  but confirms the mechanism is load-bearing under a live parallel epic.

**Crew-reported friction**
- No crews dispatched (reasoning-gate run). The cold plan critic and the independent
  cartographer-verify both returned via their final message without a nudge (background
  subagents; I integrated their findings in-turn rather than yielding —
  `lesson:delegated-commander-foreground-poll-over-watcher-yield` followed).

**Improvement signals**
- **Self-authored reasoning-gate checks genuinely needed the review scrutiny**
  (`lesson:self-authored-reasoning-gate-checks-need-review-scrutiny`, strong confirm): the
  cold critic found my g2-c2 grep invariant was a **false-green** — 3 of its 10 tokens
  (`regime_rollup`=2, `soft_class_membership`=1, `#654`=1) already existed in `index.md`
  pre-fold, so the AND-chain could pass with ZERO new content; and my g1 deletion-guard
  used `git diff -- src/` which is BLIND to a staged/`git add -A` change (the exact
  forbidden action). Both fixed before execution (re-keyed to zero-today tokens verified
  by count; swapped all guards to `git status --porcelain -- src/`). Concrete reusable
  mechanism: **a presence-grep invariant on a doc-fold must key on tokens that are
  zero-occurrence in the target BEFORE the edit, else it is vacuous** — verify the count
  first.
- **`check_arch_map.py` green really is blind to content drift** (validates the launch
  order's warning): the green check passed at every boundary, yet the independent
  cartographer caught two REAL symbol-attribution errors it could never see —
  `run_panel` is a `scripts/instrument_panel_668_report.py` function, not an
  `instrument_panel` component instrument; and the D→E grip consumer is
  `class_utilization_observable.py` (imports `GripStore`/`get_grip_at`), not
  `reference_utilization_store.py` (which only persists the grip-derived column). Both
  fixed. The reverse-import-scan is what caught them — the mechanical checker's node/parent/
  path validation cannot.
- `lesson:engine-artifact-attest` confirmed: every `user-decision` checkpoint
  (understand/plan/triage/review) satisfied via `attach` (not `attest`); `attest` used only
  for `check:null` conditions; command checks satisfied by `advance` re-running them.
- `lesson:from-child-refuses-on-gated-checklist` confirmed: the spine `execute` step's
  child (`execute.json`, gated) was closed by `attest execute --cond c1` directly — did NOT
  use `--from-child` (which only works for survey children).
