# Crash-resume state note — 567-d1

- **step:** `execute` is **COMPLETE**. `execute.json` was driven through `g5-final`, its lease
  released, and `verify_iterative_role_artifacts.py commander --work-id 567-d1` returns ok. The
  **result artifact exists**: `.agent-work/epic-567-door/results/lane-d1-RETURN.md` (committed
  `ef3eddfd`). The active step is **`reconcile`**, `pending`, with a `refresh-request`
  (`e-reconcile-1`) attached — the engine refused to START it at 48% context, which is the
  sanctioned handoff point, not a stall.
- **slug:** 567-d1 · branch `feat/567-d1-doctrine-sweep-guard` · worktree
  `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
- **next command:**
  ```sh
  cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
  # door is bound to this spine; no session id argument
  spine_status            # then: spine_start reconcile
  ```
  Remaining steps: **reconcile → triage → review → feedback → archive**, then open the PR.
- **pid:** none — foreground. No crew is running; `recover_crews.py 567-d1` reports 12 crews, 0 unresolved.
- **expected artifact:** `.agent-work/epic-567-door/results/lane-d1-RETURN.md` — **already written.**

## Branch state

Rebased on `origin/main` `5099eea1` (lanes F, H, E merged; **D2 not**). Verified head for the suite
run: **`1037ab86`** — 3 failed, 3371 passed, 6 skipped, 1219 subtests, in a clean detached worktree.
The three failures are `MapTreeFreshnessTests` (permitted, Admiral-owned, #544) and this lane's own
guard on lane D2's two un-merged files.

## What a fresh Commander must NOT re-derive

Read the RETURN artifact first — it is complete and current. Then `notes-1.md` (measurements plus
two corrections this lane made to its own earlier claims) and `REPLAN_INPUT.json`.

1. **`reconcile` has no packet map to fold into.** `map_orient` returns `DEGRADED-UNPARSEABLE`: no
   `docs/architecture`, empty `map/ids.jsonl`. The step's own imperative sanctions reconciling the
   structural record directly, or recording a **reasoned no-op as compliant**. Do **not** regenerate
   or hand-edit `map/INDEX.md` — Admiral-owned, #544.
2. **`triage`: 19 candidates are already staged** under `.agent-work/567-d1/triage-candidates/`, each
   with a disposition line. **File no issues** (`decision:no-issue-filing-mid-run`). One deserves
   priority in the return to the Admiral: `dispatched-crew-spine-is-not-bound.md`, a live
   impersonation hazard reproduced six times.
3. **`feedback`:** episodes go through `scripts/apply_episode_delta.py --store-root episodes` — the
   only write path — proved with `verify_episode_captured.py`. Order is **write → `git add` → suite
   → commit**; running the suite between the write and the stage trips
   `test_canon_episode_store_untouched` with a message that reads like store corruption.
4. **`archive`:** release the engine lease **last**, after the closing `advance` on archive.
5. **The PR is not yet open.** `gh` has been returning intermittent 503s all day — gate each retry on
   whether the world actually changed (`gh pr view`), never on the command's own output.

## The one thing this lane cannot do for itself

**Lane D2 must merge before this lane.** Until it does, the guard is red on exactly
`skills/workbench/SKILL.md` and `skills/workbench/references/checklist-engine.md`. That residual is
**proven** to be the whole of it: with `skills/workbench/` removed in a scratch copy the guard is
fully green, 19 passed. `g5-final`'s postcondition already encodes both halves and becomes the
unfiltered whole-corpus check automatically once D2 lands — no edit required.

_Updated: 2026-08-17T22:35:00Z_
