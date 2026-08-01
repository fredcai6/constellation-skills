# W3-118 Commander Report — durable-root + epic-101 template/doctrine deltas

**Verdict: COMPLETE.** One green, independently-reviewed PR. Spine driven init→archive, lease released. **PR #207 (do NOT merge — Admiral merges).**
PR: https://github.com/fredcai6/constellation-skills/pull/207
Branch: `fix/durable-root-118` (base main @ 0f354ed) · commits `cfb9b34` (item 4) + `b01ff24` (items 1-3 + doc-debt).

## Worktree isolation (required first step)
```
worktree OK: in C:/Programs/cs-wt-durable
EXIT: 0
```

## Per-item verdict
| Item | Verdict | Evidence |
|---|---|---|
| **4 — durable-root worktree-aware under active epic lease** | DONE | `agent_work_root.py` `_active_epic_lease()` + worktree-honoring branch; 6 tests; independent reviewer APPROVE |
| 1 — IMPLEMENTER_HANDOFF.template.md | DONE | self-check-budget/content-coverage tension + residual-guard dry-run rule; reviewer APPROVE |
| 2 — LATITUDE_CONTRACT.template.md (Budget) | DONE | usage-limit/session-pool wave-sizing line |
| 3 — curator/SKILL.md | DONE | two-sided-acceptance guard + broad-first dedup-move sequencing |
| doc-debt — RECURSIVE_IMPROVEMENT_DESIGN.md §5.5 | DONE | names `scripts/stage_feedback.py` + records item-4 mechanism |

## Item 4 — what resolves where (the mechanism)
`durable_root()` returns the **worktree** (its normal fallback) instead of the main checkout **iff** the main checkout holds an active Admiral epic lease — an `engine_session` with `status=="active"` AND `claimed_by=="admiral"` in `<main>/.agent-work/*/spine.json`. Absent that lease, resolution is **byte-unchanged** (linked → main). Transparent to callers: `verify_agent_feedback.py` / `verify_lessons_applied.py` already call `durable_root()`, so **only `agent_work_root.py` changed** (chosen over threading `--root .`, per pre-ruling).

**Honest-null check:** item 4 was NOT already fixed on main — `agent_work_root.py` at base had no lease branch (it unconditionally redirected linked worktrees to main). The staging workaround (#143/#154) existed; this is the complementary root-resolution fix. Real gap, fully fixed.

**Design decisions:**
- **No staleness gate** (mine, not pre-ruled): `status==active`/`released` + `claimed_by==admiral` only. A staleness gate would re-introduce the fence force-waive whenever the Admiral idles >30 min mid-wave (the common case). The lease is explicitly `release`d at closeout as the clean off-signal. Independent reviewer **concurred** (asymmetric failure directions: frequent+friction vs rare+benign).
- `claimed_by=="admiral"` filter required — an active `explorer` lease (`explore-shared-understanding`) must NOT trigger it.
- `durable_root` never raises: fully defensive scan; glob materialized inside `try` so an OSError can't escape mid-iteration (a reviewer-surfaced nit folded in at integrate + full suite re-run).

## Evidence
- Item-4 worktree-resolution test + full suite:
  - `py -m pytest tests/test_agent_work_root.py -q` → **21 passed**
  - `py -m pytest tests -q` → **894 passed, 2 skipped, 177 subtests** (before == after; no pre-existing test regressed)
- Doc-only gate: pre-authored `check_doc_invariants.py` red pre-edit → **exit 0** post-edit; reviewer word-diff confirms **additions-only, zero paraphrase-drift**.
- Both gates: fresh-context implementer + **independent** reviewer, both **APPROVE** (crew results verified fresh via `run_crew.py --verify-result`).
- **DOGFOOD:** this run's own `feedback` c1 and `archive` c1 (`verify_agent_feedback.py 118-durable-root --phase feedback|archive`, no `--root`) passed **worktree-local** under the live epic-198 admiral lease — no staging dance, no force-waive. The fix demonstrably fixes its own gate.

## Map impact
Skill-source repo, no packet map. Structural record reconciled directly: the item-4 mechanism is folded into its owning design doc (`docs/RECURSIVE_IMPROVEMENT_DESIGN.md` §5.5). No architecture-map delta.

## Triage candidates — FLOATED to Admiral (not filed; issue-filing is outside this run's latitude)
Full text: `.agent-work/archive/20260719-118-durable-root/` is the worktree copy; recommendations authored in `TRIAGE_RECOMMENDATIONS.md`.
- **TR-1 (coordinated follow-up):** `skills/admiral/SKILL.md` harvest-before-sweep should also sweep the **worktree-root** `.agent-work/{AGENT_FEEDBACK,LESSONS,CONSTELLATION_FEEDBACK}.md` trio — under an epic, durable-root now resolves there (not only `staged-feedback/<work-id>/`). My change is **safe standalone** (purely additive: staging path unchanged, gate strictly more permissive, non-epic worktree runs unchanged), but the end-to-end simplification needs this. Owned by another wave-3 commander / admiral SKILL, fenced from this run.
- **TR-2:** Commander doctrine could sanction writing worktree-local durable instead of the staging dance under an epic (sequence after TR-1).
- **TR-3:** minor no-staleness residual (abandoned never-released lease → later standalone worktree run resolves worktree-local) — closeout note or low-pri cleanup.

## Workflow feedback (fenced trio — dogfooded stage-not-needed)
Because item-4's own fix resolved my durable root to the worktree under the active epic lease, the feedback/archive gates passed **without** `stage_feedback.py` staging — so the trio was written to the **normal worktree-local durable path**, not `staged-feedback/`:
- `C:/Programs/cs-wt-durable/.agent-work/AGENT_FEEDBACK.md` (retrospective entry for 118-durable-root)
- `C:/Programs/cs-wt-durable/.agent-work/LESSONS.md` (2 banked lessons, tick=1)
- (no CONSTELLATION_FEEDBACK export — no threshold-ripe constellation lesson this run)

**Harvest note for the Admiral:** this trio is at the worktree ROOT `.agent-work/`, NOT under `staged-feedback/`. Harvest it from there before sweeping the worktree (this is exactly the TR-1 gap in living form). Two lessons banked (both project-scope, deferred needs-human doctrine/engine targets): `engine-attest-preconditions-before-start`, `reviewer-docs-only-fowler-pass-framing`.

Minor engine friction: `start <step>` is REFUSED until null **preconditions** are attested; the `current` imperative narrates only postconditions — cost a few retry round-trips (banked as a lesson).

## Isolation output
`py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-durable` → `worktree OK: in C:/Programs/cs-wt-durable` / EXIT 0 (pasted above).
