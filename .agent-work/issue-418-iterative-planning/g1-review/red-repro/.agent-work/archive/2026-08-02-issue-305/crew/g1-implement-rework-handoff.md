# Implementer Handoff — g1 REWORK (packaging)

## Gate
`g1-implement`, rework 1/3. Issue #305, epic #298.

## Why you exist

The g1 seam is built and works — that part is done and is **not** yours to touch. A reviewer BLOCKed it on one finding, and the Admiral has ruled the fix **in scope**:

> **`scripts/episode_capture.py` is not shipped to any installed skill, so the seam is inert in production.**

`checklist_engine.py` imports the sidecar under `try/except ImportError` with a no-op fallback. On every **installed** engine that fallback is what runs: `start` → exit 0, `advance` → exit 0, gate completes, **zero manifests, nothing on stderr**. Confirmed on disk — the installed commander skill has `checklist_engine.py` and neither sidecar.

Filed as **#362**. The Admiral's words: *"a capture that does not ship is not captured."*

## The mechanism already exists — do NOT invent a new one

`scripts/install_constellation.py` already has `SCRIPT_RUNTIME_COMPANIONS` and `expand_script_bundle()`, added by a sibling commander (#304, commit `06ce473`). **Use them.** Do not design a second mechanism.

```python
SCRIPT_RUNTIME_COMPANIONS: dict[str, tuple[str, ...]] = {
    "checklist_engine.py": ("gauge_reader.py",),
    "gauge_writer_hook.py": ("spine_rail.py",),
}
```

## Deliverable 1 — the dependency closure (small)

Add the sidecars as companions of `checklist_engine.py`. **I traced the closure; verify it rather than trusting me:**

- `checklist_engine.py` → `episode_capture.py` (plain import, via `sys.path.insert`)
- `episode_capture.py` → `agent_work_root.py` (module scope) **and** `context_manifest.py` (deferred import inside `emit_step_manifest`, to break an import cycle)
- `context_manifest.py` → `checklist_engine.py` (closes the cycle; already bundled everywhere the engine is)

So the companion set is **`episode_capture.py`, `agent_work_root.py`, `context_manifest.py`**.

`agent_work_root.py` matters more than it looks: it is already in the `admiral` and `commander` bundles but **not** in the other seven engine-carrying skills, so without it those seven still break.

## Deliverable 2 — THE ACTUAL DELIVERABLE: teach the detector to see this class of dependency

This is what you defend in review. The two-filename edit is not the deliverable; **this is.**

`tests/test_install_constellation.py::test_engine_dynamic_loads_are_declared_as_companions` already exists and parses the engine source for sibling loads:

```python
siblings = set(re.findall(r'parent\s*/\s*"([A-Za-z0-9_]+\.py)"', engine_src))
```

**That regex cannot see the #305 dependency.** It only matches `parent / "x.py"` dynamic loads. `checklist_engine.py` reaches `episode_capture.py` by `sys.path.insert(0, ...)` followed by a plain `from episode_capture import emit_step_manifest`. I verified this: the regex returns exactly `{'gauge_reader.py'}` against the current engine, which already contains the `episode_capture` import.

**So the existing guard would NOT have caught this defect, and will not catch the next sidecar added the same way.** Extend the detection to cover sibling modules imported plainly after a `sys.path` insertion — not just `parent / "x.py"` loads — and require each to be declared in `SCRIPT_RUNTIME_COMPANIONS`.

**Design the detector so that it fails on the pre-fix tree.** That is your red proof: reconstruct the state where `episode_capture.py` is imported but undeclared, and confirm your detector goes RED naming that module specifically. A detector that only passes on the fixed tree proves nothing.

Update the `ENGINE_RUNTIME_SIBLINGS` expectation set alongside it — the existing test asserts the parsed set equals the expected set exactly, so both move together, deliberately.

## Deliverable 3 — a comment carrying a false rationale

In `scripts/checklist_engine.py`, `reopen()`'s emit call carries this comment:

```python
emit_step_manifest(cl, iid, base_dir)  # #305: AFTER the mutation — active_id() picks the step.
```

The placement reason is right, but the **justification for the call existing at all** was wrong in the record. The reviewer established, and I confirmed: `reopen` refuses anything not `complete`, and a complete gate necessarily passed `start`, so its manifest already exists and write-if-absent returns early. **`reopen`'s emit is a no-op on every reachable production path** — it fires only for a spine that predates #305 (I observed exactly that this run: reopening a gate started before the seam landed did emit).

Keep the call. **Write the corrected reason into the comment.** The Admiral's instruction: *"a comment carrying a false rationale is a small instance of the same thing this whole float is about."*

## Close criteria

- All three sidecars ship with every engine-carrying skill, verified through `expand_script_bundle()`, not by eyeballing the dict.
- The extended detector **goes red on the pre-fix tree** and green after. Show both.
- The existing companion test (`test_every_skill_bundling_the_engine_also_gets_the_gauge_reader`) still passes, and its generalization to the new companions is real rather than name-only.
- `reopen`'s comment states the true reason.
- Full suite green.

## Constraints

- **Additive only.** Do not change the meaning of any existing bundle entry. Other commanders are live on this installer.
- **`scripts/install_constellation.py` has uncommitted changes in the MAIN checkout** (`C:/Programs/constellation-skills`) — two lines adding new `"clean-codebase"` keys to both bundle dicts. **You edit the VALUES of existing engine-carrying keys; that is a different line.** Do not touch the main checkout. Work only in `C:/Programs/constellation-skills-wt/e298-305`.
- Do **not** touch `scripts/episode_capture.py`'s seam logic, the emit sites, or the tests in `tests/test_episode_capture.py`. That work is reviewed and closed.
- Tests: `python -m pytest` (3.14.3 / pytest 9.0.2). `py` is 3.12.13 with **no pytest**. Neither reproduces CI.
- Windows: explicit `encoding='utf-8', newline='\n'` on every write. `Path.read_text(newline=...)` is 3.13+ and **fails CI**.

## Note on why this was invisible

The g1 reviewer ran six mutants, five outside the implementer's set — **all killed**, and it could not find a survivor inside the diff. It could not, because **the defect is not in the diff.** The only mutation with no killer was the packaging one. Keep that in mind while you build deliverable 2: you are closing a hole that a genuinely rigorous mutation pass could not see.

## Return

Write `IMPLEMENTER_RESULT` to `.agent-work/issue-305/crew/g1-implement-rework-result.md` — what changed, evidence with pasted real output (including the RED run of your detector on the pre-fix tree), close-criteria disposition, blockers, and blunt `Workflow Feedback`. Your final message must contain the same result.
