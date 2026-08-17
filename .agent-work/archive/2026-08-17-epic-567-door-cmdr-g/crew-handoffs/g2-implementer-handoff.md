# Implementer Handoff

## Gate
`g2` — reap + child-plan release (the #552 mechanism). Gate 2 of 3; g1 shipped the verify/close primitives, g3 composes them into `finish_work`.

## Task
Add two functions to `scripts/spine_lifecycle.py`:

**(a) `force_reap(project_dir) -> dict | None`** — a library call into `spine_rail`'s existing transaction helper, forcing an immediate persist of the already-reaped binding map instead of waiting on some future unrelated session's touch:

```python
return spine_rail._binding_transaction(project_dir, lambda reaped: reaped)
```

Import `scripts/hooks/spine_rail.py` through this module's own `sys.path` insert pattern (it already inserts its own directory; `hooks/` is a subdirectory, so add that path the same way). **Zero edits to `spine_rail.py`.**

Why a no-op mutate works: `_binding_transaction` (`spine_rail.py:397-436`) loads the registry, runs `_reap_binding_entries` (`:311-366`) on it under the lock, hands the *already-reaped* map to `mutate`, and persists when the result differs from what was loaded. So an identity `mutate` is sufficient to make the reap durable **now**. Returns `None` on any fail-open path (lock contention, timeout, replace failure) — that is a real answer, not an error; propagate it.

**(b) `_release_child_plans(spine_path, work_dir, *, root, reason) -> dict`** returning `{"released": [str, ...], "unclaimed_active": [str, ...]}`.

### The three safety properties — each a SHIPPED runtime guard, not test-only discipline

These are the gate. A version that works on the happy path but drops any of these fails review.

**1. LINEAGE, not directory proximity.** A child plan is identified **structurally**: a JSON file whose `realpath` is strictly inside `work_dir` **AND** which some task in the parent spine names in its `child_checklist` field. Resolve each task's `child_checklist` relative to `work_dir`.

An active-leased JSON file under `work_dir` that **no task claims** as its `child_checklist` is **left alone** and reported in `unclaimed_active` — never released.

"Any active-leased JSON under `work_dir`" is explicitly the **wrong** predicate. It would seize a lease that a different, still-working agent genuinely holds. Do not use `_active_engine_session_spine`'s scan as-is for this: that helper answers a different question (is anything active here at all, for `open_work`'s refusal) and is deliberately proximity-based.

**2. HONEST NON-OWNER RELEASE.** Do **not** read a child's own `engine_session.session_id` and hand it back to `release()` as the caller id. `release()`'s ownership check is `session_id != sess.get("session_id")` (`checklist_engine.py:1133-1147`) — echoing the child's own id back makes that check **tautological** and forges an ownership this run does not have.

Release each child as the explicit non-owner it is:

```
release --force --reason "<reason>"
```

where `<reason>` names the parent `work_id` and states this is a parent closeout. The engine records a forced non-owner release, so the override leaves a real audit trail. Route it through g1's `_engine_call` — do not add a second call path.

**3. ESCAPE REFUSAL.** Resolve every candidate with `realpath` and refuse any whose resolved path is not strictly inside `work_dir`, so a symlink inside the work area cannot reach a spine outside it. Prefer an explicit containment predicate (`Path.resolve()` then `is_relative_to(work_dir.resolve())`) over string prefix matching.

## Protected Intent
Archiving a run must leave **zero** active leases behind, child plans included — that is the whole of #552. But it must never release a lease belonging to an agent still working. Both halves matter; a version that reaps aggressively and steals a live lease is worse than the bug it fixes.

## Test Mode
Test-after allowed. The negative tests are load-bearing — they are what proves the safety properties are real rather than asserted.

## Close Criteria
- `force_reap` and `_release_child_plans` exist in `scripts/spine_lifecycle.py`.
- `force_reap` calls `spine_rail._binding_transaction` with an identity mutate; **no** edit to `spine_rail.py`.
- `_release_child_plans` implements all three safety properties as shipped code.
- Child releases go through g1's `_engine_call` with `--force --reason`, never by echoing the child's own session id.
- Tests added to `tests/test_spine_lifecycle.py`, all passing:
  1. `force_reap` — a binding-store entry whose target spine is already `released` is gone **immediately** after the call, asserted via `spine_rail.load_binding(...)`, not by waiting for another transaction.
  2. `_release_child_plans` with **0**, **1**, and **2** children declared via `child_checklist` — each declared child ends `released`, and the returned `released` list names them.
  3. **NEGATIVE** — a spine **outside** `work_dir` that shares the `work_id` prefix is never touched (its lease stays `active`).
  4. **NEGATIVE** — an active-leased JSON **inside** `work_dir` that **no** task declares as a `child_checklist` is **not** released and **is** reported in `unclaimed_active`.
  5. **NEGATIVE** — a symlink inside `work_dir` pointing at a spine outside it is refused (target lease stays `active`).
- Full `tests/test_spine_lifecycle.py` green; state pre/post test counts.

## Allowed Scope
- `scripts/spine_lifecycle.py` — add the two functions.
- `tests/test_spine_lifecycle.py` — add tests, fixtures, helpers.

## Specific Exclusions
- **`scripts/hooks/spine_rail.py` — DO NOT EDIT.** Call `_binding_transaction` as a library import only. (Not fenced to another lane, but out of scope for this gate: the whole design depends on reusing its existing self-heal rather than re-deriving one.)
- **`scripts/checklist_engine.py` — DO NOT EDIT.** Owned by **lane A (epic #567)** this wave, actively being rewritten.
- **`scripts/mcp_spine_server.py` — DO NOT EDIT.** Same owner, **lane A (epic #567)**, same wave.
- Do not modify g1's `done_refusal` / `_engine_call` / `_advance_and_release` behavior — **reuse** `_engine_call`.
- Do not add `finish_work`, `open_pr`, or the CLI — that is g3.
- Do not change `closeout_refusal` or `close_work`.

## Constraints
- **Never run against a live spine file.** `.agent-work/epic-567-door/spine.json` is the Admiral's **active** lease; `.agent-work/epic-567-door/cmdr-g/spine.json` and `execute.json` are this Commander's own live spines. Fixtures under `tmp_path` only.
- `force_reap` takes a `project_dir` — in tests, always a `tmp_path`, never the real repo root, so no test ever mutates this repo's real `.agent-work/.spine-rail-binding.json`.
- Keep the module's pure/impure split at function granularity.
- POSIX-form commands; `PYTHONIOENCODING=utf-8` for captured subprocess output; `py` works here.

## Map Anchors (inbound)
- **Map entry point:** none — `map_orient.py` returned DEGRADED-UNPARSEABLE (no `docs/architecture` map in this repo). Declared substitutes: `map/INDEX.md`, `scripts/spine_lifecycle.py`, `scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py`, `docs/agents/ORCHESTRATOR_CONTEXT.md`. Start at `scripts/hooks/spine_rail.py`'s `_reap_binding_entries` and `_binding_transaction` docstrings — they state the reap contract precisely.
- **Structural:** `scripts/hooks/spine_rail.py` — `_reap_binding_entries` (:311-366), `_binding_transaction` (:397-436), `load_binding` (:135), `binding_path` (:82) — read-only. `scripts/spine_lifecycle.py` — `_active_engine_session_spine` (:180) for contrast (proximity-based, a different question), `close_work`'s spine/journal exclusion pattern (:457-463) for the shape of "exclude the bound spine itself".
- **Capability:** immediate binding-store reap; child-plan lease release (#552's mechanism half).
- **Constraints/assumptions:** never test on a live lease; `spine_rail.py` is library-call-only.
- **Decision anchors:** `decision:child-plans-count` — the archive step must release **child plans'** leases too, not just the top-level spine. This is the mechanism half of #552 and the reason 17 stale leases sit inside `archive/`.
  `@grade: settled/issue · leans g2-implement,g3-implement`
- **Evidence expectations:** `_reap_binding_entries` only drops entries whose target reads `status == "released"` — your `force_reap` test must confirm that precondition holds in the fixture (target already released) rather than assuming the reap is unconditional.
- **Map confidence flags:** `checklist_engine.py` is being rewritten concurrently by lane A — read its current `parse_args` for the `release --force --reason` flag shape rather than trusting a remembered form; `_engine_call`'s `SystemExit` guard (g1) is the backstop.

## Deliverable Path Check
- **Committed** — `scripts/spine_lifecycle.py`; `git check-ignore` exit **1** (not ignored).
- **Committed** — `tests/test_spine_lifecycle.py`; `git check-ignore` exit **1** (not ignored).
- Both already tracked; nothing new appears only in `git status` this gate.

## Required Evidence
**Load-bearing (prove rigorously):**
- All three NEGATIVE tests (close criteria 3, 4, 5) — paste each test body and its passing output. These are the gate's reason to exist.
- The `force_reap` immediacy test — show the binding entry present before and absent after, read via `spine_rail.load_binding`.
- `py -m pytest tests/test_spine_lifecycle.py -q` with pre/post counts.

**Confirmatory (spot-check suffices):**
- `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py` → must be **empty**. Paste it.
- That `_release_child_plans` contains no read of a child's `session_id` for use as the caller id (grep your own diff).

## Wiring Grep
`force_reap` and `_release_child_plans` are consumed by `finish_work` in **g3**, which does not exist yet — their only non-definition callers at the end of this gate are the tests. Expected and bounded; state the count.

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease && \
grep -rn "force_reap\|_release_child_plans" --include=*.py . \
  | grep -v "def force_reap" | grep -v "def _release_child_plans"
```

Also confirm the reuse (g1's choke point must be the call path, not a new one):

```bash
grep -n "_engine_call\|checklist_engine.main" scripts/spine_lifecycle.py
```

`checklist_engine.main` should appear only inside `_engine_call`.

## Verification Commands
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease
PYTHONIOENCODING=utf-8 py -m pytest tests/test_spine_lifecycle.py -q
git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py
grep -n "_engine_call\|checklist_engine.main" scripts/spine_lifecycle.py
```

## Suggested Model Tier
**Sonnet** — bounded and well-specified, but the three safety properties reward careful reasoning; hold to the stated predicates rather than simplifying them. The launch order fixes this lane at Sonnet.

## Authority
Already decided — do not re-litigate:
- Lineage-based child identification (declared via `child_checklist`), not directory proximity.
- Honest non-owner release via `--force --reason`, never echoing the child's own session id.
- `realpath` containment refusal.
- `force_reap` uses an identity mutate through the existing `_binding_transaction`.
- The fence: `checklist_engine.py`, `mcp_spine_server.py`, `spine_rail.py` are not yours to edit.

**You must not decide alone:** widening the child-identification predicate; releasing an `unclaimed_active` file; any edit to a fenced file; any change to g1's primitives.

## Stop Conditions
Stop and return if: allowed scope must be exceeded; a fenced file must be touched; a parent spine's tasks carry no `child_checklist` field at all in a way that makes lineage-based identification unimplementable as specified (report it — do not silently fall back to proximity); required evidence cannot be produced; a decision outside the authority above is needed.

## Return Format
Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

`Return status` must be one of `complete | partial | blocked | out-of-scope | failed`, **lowercase** — copied verbatim into an engine postcondition matching on exact case.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g2-implementer-result.md` **before ending your turn** — that write is the delivery. A `SendMessage` ping is best-effort courtesy only.
