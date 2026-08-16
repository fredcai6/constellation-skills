# Implementer Handoff — g1, rework (attempt 3)

## Gate
`g1` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`.

## Context

The g1 slice is **in the tree and otherwise accepted**. An independent reviewer
returned `Verdict: BLOCK` on exactly **one** blocker. Everything else in the
review is APPROVE-shaped or an out-of-scope triage candidate already recorded by
the Commander — **do not act on those.**

Read first:
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g1-reviewer-result.md`,
section **Blockers**, finding **B1**.

## Task — fix B1, nothing else

`tests/test_spine_rail.py::test_worktree_from_spine_walks_to_the_nearest_agent_work_ancestor`
**cannot pass on Windows.** It asserts the derivation's return equals
`str(worktree)` in six places, but the new derivation returns a
**`normcase`-folded** path while `str(tmp_path / ...)` is unfolded. On Windows
`normcase` lowercases, so the two differ for **every** `tmp_path` — the drive
letter alone guarantees it.

The reviewer simulated both copies under `ntpath` with a realistic Windows
`tmp_path`:

```
asserts == str(worktree):
   expected   : C:\Users\Tommy\...\test_Worktree0\worktree
   NEW returns: c:\users\tommy\...\test_worktree0\worktree   -> FAILS on Windows
```

The predecessor test passed there: the old implementation returned
`str(agent_work.parent)`, and `pathlib` preserves case. **So this diff turns a
green Windows test red**, and `windows-latest` is red at baseline, so nothing
would ever attribute it.

**The fix:** construct the expectation from the same predicate the implementation
applies, exactly as your own `tests/test_worktree_derivation.py` `_expected()`
helper already does — `os.path.normcase(os.path.normpath(str(worktree)))` — in
all six assertions. **Nothing in production changes.**

Your sibling table survives the same simulation and is genuine coverage
(`_FOLDS_CASE` is derived from `os.path.normcase(".AGENT-WORK") == ".agent-work"`,
not from `sys.platform`). Keep it as it is. Reuse its construction here rather
than inventing a second one.

You identified this hazard correctly in your own Evidence 8 and then did not
apply it to this test. Also **correct the scoped null** in your result: the fold
is not merely "untested on a real Windows host" — as written the test was
*guaranteed to fail* there.

## Protected Intent

Unchanged. The derivation, its placement, its two-copy shape and the shared table
are all accepted and are **not** reopened.

## Test Mode

Test-after — no production behaviour changes. Prove the fix by construction, not
by the platform: show the corrected expectation is what the implementation
returns under a simulated `ntpath` as well as natively.

## Close Criteria

- All six assertions compare against a **constructed** expectation, not a
  platform-inherited one.
- The Windows simulation the reviewer ran now passes for **both** files.
- `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py` green.
- `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_worktree_derivation.py` green.
- Full suite green, cache cleared, clean env, count stated.
- No production file differs from its current state.

## Allowed Scope

`tests/test_spine_rail.py` **only**.

If `map/INDEX.md` goes stale again because entity counts moved, `map/` is also in
scope — regenerate with `py -m scripts.code_map build --root .`, never by hand.
A test-body edit that adds no entity should not move it; if it does, say so.

## Specific Exclusions

- **Do not touch any production file.** `scripts/checklist_engine.py`,
  `scripts/hooks/spine_rail.py` are **frozen** at this gate.
- **Do not touch `tests/test_worktree_derivation.py`** — the reviewer confirmed it
  is correct.
- **Lane A (#603):** `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
  `scripts/install_constellation.py`, `skills/commander/templates/**`.
- **Lane E:** `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- **#610:** `scripts/verify_worktree_isolation.py`.
- **Any template**, including `.agent-work/templates/**`,
  `skills/admiral/templates/**`.
- **Do not act on the reviewer's `tc1`/`tc2`/`tc3`** — the Commander has recorded
  them as triage candidates and fixed the frame contradiction itself.

## Constraints

- Construct case expectations **explicitly**; never inherit them from
  `sys.platform`. That is the whole content of this blocker.
- `scripts/hooks/spine_rail.py` still imports stdlib only — and you are not
  editing it anyway.

## Map Anchors (inbound)

Unchanged; see the g1 handoff and `MISSION_FRAME.md`. One frame correction landed
since your last attempt: the frame's Governing Constraints section had still
carried the superseded "realpath + normcase, reusing
`verify_worktree_isolation`" wording alongside the revised lexical-only rule. It
now carries only the lexical-only rule, and names
`scripts/hooks/spine_rail.py:677` `_same_path` as the correct in-repo precedent —
your reading was right and the frame was wrong.

## Deliverable Path Check

- **Committed** — `tests/test_spine_rail.py`: `git check-ignore` exits **1**.
- **Local-only** — your result artifact under `.agent-work/`.

## Required Evidence

**Load-bearing:**

1. The Windows simulation, run before and after, showing the six assertions fail
   before and pass after under a folded path.
2. Full suite, cache cleared, clean env, count stated, failure distribution
   derived mechanically (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`) even
   when empty.

**Confirmatory:**

3. `git diff e36e630b --stat` showing **no production file** changed relative to
   the state you inherited.

## Wiring Grep

`none — this rework adds no callable symbol.`

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_worktree_derivation.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

Platform: Linux, Python 3.12 as `py`. Clear `__pycache__` before every
measurement.

## Suggested Model Tier

**Simple bounded** — six assertions, a construction you already wrote once in the
sibling file.

## Authority

The reviewer's B1 is accepted by the Commander and is not up for debate. If you
believe B1 is wrong, **stop and return that finding** rather than implementing
around it.

Everything else about g1 is settled.

## Stop Conditions

Stop and return if the fix requires touching a production file, if B1 turns out
not to reproduce, or if a decision outside the authority above is needed.

## Return Format

Return a full, **self-contained** `IMPLEMENTER_RESULT` covering the whole g1
slice (attempts 1–3), because the reviewer re-reads this file and not its
predecessors. Carry forward attempt 1–2's evidence and add this fix. `Return
status` on its own line, **lowercase**.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g1-implementer-result.md`
**before ending your turn**, overwriting the current file. That write is the
delivery.
