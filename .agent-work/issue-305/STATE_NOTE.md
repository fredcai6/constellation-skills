# Crash-resume state note — issue-305

- **step:** execute · **`g1` is CLOSED** · gate **`g2-implement`** is next
- **slug:** issue-305 · branch `epic-298/305` (**PUSHED to origin**) · worktree `C:/Programs/constellation-skills-wt/e298-305` · base `967493c`
- **next command:** `cd "C:/Programs/constellation-skills-wt/e298-305" && python scripts/checklist_engine.py --file .agent-work/issue-305/execute.json current`
- **pid:** none — foreground
- **expected artifact:** `.agent-work/issue-305/crew/g2-implement-result.md`

**Everything is committed AND pushed.** Nothing depends on this machine surviving.

## Leases and engine

Spine + gate plan lease: **`commander-305-e298`**. Spine `.agent-work/issue-305/spine.json`,
gate plan `.agent-work/issue-305/execute.json`.
**Drive the WORKTREE `scripts/checklist_engine.py`** — Admiral APPROVED this explicitly over the
installed copy, because this run modifies the engine and driving a different copy would mean the
change is never exercised by the run that makes it. If the emit path ever wedges a verb, **that is a
finding to report, not a reason to switch engines and hide it.**

## Done

- **g1 COMPLETE** (implement → review → **reopen for the ruled packaging rework** → re-review → integrate).
  Seam emits at `start()`/`reopen()`, write-if-absent; the whole transitive closure
  (`episode_capture.py`, `agent_work_root.py`, `context_manifest.py`) now ships to all ten
  engine-carrying skills via `SCRIPT_RUNTIME_COMPANIONS`; a new detector sees plain `sys.path` +
  sibling imports, which the old regex-only guard was structurally blind to.
- **#362 verified fixed IN THE WORLD**, not just in the dict: installed the `implementer` skill
  (bundle is `checklist_engine.py` *alone*) to a temp dest, all four companions landed, and in a fresh
  process with cwd **outside** the repo the installed engine bound
  `emit_step_manifest.__module__ == 'episode_capture'`, not the fallback.
- **Return item 4 proven:** #300's AC1 can now fail. Pre-seam engine (extracted from `967493c` and
  checked to genuinely lack `emit_step_manifest`) emits `manifests=[]`; post-seam emits `['g1.json']`.

## Next: g2 — read this before dispatching

`g2-implement` was **amended twice** and both amendments are load-bearing:

1. **`refusals` IS in scope** (Admiral). Additive only; **`docs/CHECKLIST_SCHEMA.md` in the same PR**;
   prove the counter can be wrong **and** that the test can fail on the *specific* assertion; **state
   the #344 latency**. Also correct **`docs/EPISODE_STORE.md:781`** — it promises automated capture
   that `_validate_create` forbids; #305 delivers a **mechanical snapshot**, not auto-created episodes.
2. **`project` sourcing is CORRECTED — do NOT use `durable_root()`.** It returns the *worktree*
   whenever an active Admiral epic lease exists (the condition this epic runs under), so `project`
   would be `e298-305` — the exact per-epic drift D5 existed to prevent. Use the parent of
   `git rev-parse --git-common-dir`; **refuse** rather than guess if git is absent. The stability test
   **must run from a linked worktree under an active epic lease**, because a plain-checkout test
   passes on the broken formula. Measured, not read.

`g2-review` was amended to require an **independent mutation outside the implementer's shipped set**,
the both-sides-of-the-boundary rule, and the case a one-sided test misses: **induce a successful verb
and assert the counter did NOT move.**

## Lessons harvested (for the feedback step — do not lose these)

- **A vacuous check plus an honest crew reads exactly like a passing check plus a compliant crew.**
  m3's "the engine diff is an import plus two call sites and nothing else" was checked by
  `git diff --stat`, which exits 0 regardless. Authored by a **Commander into a crew's job file** —
  the grader, not the graded. Sixth #337 costume.
- **A revert-based red proves the assertion matches the tree; only a NOVEL module proves the detector
  parses.** Belongs in the handoff template, not in a reviewer's initiative.
- **`constellation-implementer` has no sanctioned resume or no-plan path**, so a rework dispatch
  contradicts the skill's opening imperative and costs every implementer a judgment call.
- Handoff error to fix: `--session-id` is **required** by `consolidate`, not rejected.

## Issues filed

**#362** packaging (FIXED this run, close it with the PR) · **#359** surveys bypass the seam
(must travel in the PR body alongside the capability, per the Admiral) · **#360** doubled work-id
manifest path — **confirmed live from this run's own artifacts** (`.agent-work/issue-305/issue-305/context/`)
· **#361** unguarded `work_id` + duplicated place-and-write.

**Suite: 1436 passed, 2 skipped, 471 subtests.** **Branch: PENDING** — pushed, no PR yet.

_Updated: 2026-08-02T04:05:00Z_
