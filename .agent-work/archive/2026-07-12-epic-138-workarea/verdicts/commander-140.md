# Verdict — commander-140 (issue #140, engine rail)

**Status: COMPLETE — green, reviewed PR open.** Deliverable met: `_rail(point, cl)` implemented in `scripts/checklist_engine.py`, engine-carried doctrine at every decision point (channel A of #138), full suite green, independent reviewer APPROVE.

## PR
https://github.com/fredcai6/constellation-skills/pull/148 (branch `issue-140` → `main`, commit `9ff2d5c`). **Not merged** — merges are the human's / server-side per the launch order.

## Worktree isolation check (pasted)
```
worktree OK: in C:/Programs/constellation-wt-140
EXIT: 0
```

## Test results (pasted, exit codes)
- Implementer run: `py -m pytest tests/test_checklist_engine.py -q` → `145 passed, 14 subtests passed` (135 existing + 10 new `DoctrineRail` tests). exit 0.
- Commander re-verification (independent, world-check): `145 passed, 14 subtests passed`. exit 0.
- Reviewer re-verification (independent): `145 passed, 14 subtests passed`. exit 0. Verdict **APPROVE**.
- Engine `g1-integrate.c1` command postcondition (engine ran the suite on `advance`): passed. exit 0.
- Final post-archive run: `145 passed, 14 subtests passed`. exit 0.

## What shipped (matches the frozen spec)
- One function `_rail(point, cl)` + helper `_rail_position(cl)` + `_RAIL_STRINGS` table + `RAIL_VERBS` set in `scripts/checklist_engine.py`.
- Rail appended to `claim`, `current`, `start`, `advance`, `attest`, `attach` (in `dispatch()`) and to the `REFUSED` path (in `main()`), gated to `type == GATED` checklists only.
- **Five strings verbatim** from the launch-order/DESIGN_SPEC §D2 table (I byte-checked each; reviewer independently byte-checked each). Tokens `{id}`/`{n}`/`{imperative}` substituted from `items` state via `.replace` (safe against brace-bearing imperatives).
- Position derivation: `n = |non-terminal items|`; `n==0`→terminal, `n==1`→near-terminal, active is first item→early, else mid-flight. check-failure keys on the `EngineError` refusal path (unit-tested by invoking a failing verb).
- Canonicality note present in the `_RAIL_STRINGS` comment block (table canonical; `_shared/global-everyone.md` elaborates and cites it; on conflict table wins).
- **Design invariant honored:** verb functions kept PURE — the rail rides only the two CLI-boundary chokepoints, so all 135 existing exact-equality tests stayed green. No new verb, no schema/journal change, no per-step authored text, no rail on read-only verbs other than `current`.
- Dogfooding confirmed live: the engine's own `advance`/`current` output began carrying the rail mid-run.

## Wording deviations
**None.** No string required a wording change; nothing floated on that basis.

## Fix-now rulings
None taken. The change is confined to the two owned files (`scripts/checklist_engine.py`, `tests/test_checklist_engine.py`); no bounded engine defect was tripped that fell inside my scope. (The one engine-adjacent defect hit — #134 — is a sibling channel, D5, not mine to implement; see Float below.)

## Triage candidates (recommend-and-defer to the Admiral — no issue-filing authority this run)
- **tc1:** Note the #138 channel-A doctrine rail in `docs/CHECKLIST_ENGINE_DESIGN.md` (engine response text now carries decision-point doctrine). Deferred — `docs/` is outside commander-140's stated file ownership.
- **tc2:** **Cross-commander dependency —** commander-142 must add the elaborating scoped-nulls section + canonical-source citation to `_shared/global-everyone.md`, so the rail table's embedded canonicality note is non-dangling (DESIGN_SPEC D4/SY2). Until 142 lands, the note points at a section that does not yet cite back.

## FLOAT to the Admiral — #134 recurrence hit at closeout (needs your ruling / harvest)
My run reproduced the **#134 field-falsification condition exactly**: "a delegated commander still needs a waive to close out." Details:
- `verify_agent_feedback.py` (feedback c1 and archive c1) resolves the durable `.agent-work` root to the **main checkout** (`agent_work_root.durable_root` — the trio is shared across worktrees by design). Writing my `issue-140` feedback entry into that shared durable log **mid parallel-wave** (140/141/142 concurrent) is the clobber the worktree fence exists to prevent.
- Per the archive imperative ("under an Admiral, the epic-level harvest at closeout is the durable record instead") + DESIGN_SPEC §D5, I staged the feedback trio **worktree-local** with a `fence-citation` evidence artifact (spine evidence `e-feedback-1`, `e-archive-1`) naming the staged paths + fence, and **force-waived** feedback.c1 and archive.c1 (authority "admiral (launch-order fence)"). Both waives are recorded (`e-feedback-2`, `e-archive-2`).
- **Action you own:** harvest the worktree-local trio into the durable root at epic closeout:
  - `C:/Programs/constellation-wt-140/.agent-work/AGENT_FEEDBACK.md` (my issue-140 entry)
  - `C:/Programs/constellation-wt-140/.agent-work/LESSONS.md` (one added lesson) / `.agent-work/issue-140/lessons-delta.json`
- This is the standing interim until D5 (fence-aware acceptance of the worktree-local trio) ships. My waives are the sanctioned interim, not a defect in this issue's deliverable.

## Lessons distilled (worktree-local, for harvest)
- `implementer-skill-engine-ref-path-drift` (constellation scope): the `constellation-implementer` skill names `references/checklist-engine.md`, but the actual installed path is `skills/workbench/references/checklist-engine.md`; a dispatched implementer must Glob for it. Target: `skills/implementer/SKILL.md`.

## Workflow feedback
- The frozen launch-order string table (backticks / em dash / straight quotes encoded precisely) was the single biggest reason the gate closed in one pass — both crew members did byte-exact verification with zero ambiguity.
- The pure-verb-function design constraint, pre-stated in the handoff, forestalled the one failure mode (breaking exact-equality tests) that would otherwise have surfaced at review.
- Minor: the `execute` STATE_NOTE precondition framing ("before any detached process") mismatches a synchronous in-turn crew dispatch — had to record `pid: none — foreground`.
- Recurring: the #134 durable-root-vs-fence closeout friction (floated above) — this run is another data point that D5 is load-bearing.

## Spine provenance
Closeout ordered correctly: archive postconditions satisfied/waived → final `advance archive` (spine done) → `release` as the last journaled action. Final `current`: `DONE: no open items. WAIVED: ['feedback.c1', 'archive.c1']`.
