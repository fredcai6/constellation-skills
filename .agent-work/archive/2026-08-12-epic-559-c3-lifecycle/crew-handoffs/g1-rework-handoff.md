# Implementer Handoff — g1 REWORK (attempt 2)

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g1` · **Role:** `implementer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (you are already in it)
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g1-rework-result.md`

## Why you are here

`g1` shipped and an independent reviewer returned **BLOCK** on one confirmed finding. The Commander
verified all three of its supporting facts and agrees. **Everything else in `g1` was approved** — 28
tests pass, the suite is at 2852, the sweep is 23, the rollback and self-verify fixtures are real. Do not
redesign anything. This is a narrow rework.

Read `.agent-work/epic-559/c3-lifecycle/crew-handoffs/g1-reviewer-result.md` for the full finding.

## The task — two changes, and only these two

### 1. The write is missing its newline argument

`scripts/spine_lifecycle.py:257`:

```python
spine_path.write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8")
```

`docs/agents/CREW_CONTEXT.md:43` requires `encoding='utf-8', newline='\n'` explicitly on **every** write;
the one sanctioned exception is `checklist_engine.py`'s byte-faithful `save()`, which does not cover this.
`.github/workflows/ci.yml:23` runs this suite on `windows-latest`, so on Windows this writes a CRLF
`spine.json` today.

Fix it. **Then audit every other write in `scripts/spine_lifecycle.py` for the same omission** — the
reviewer found one; the rule is "every write", and a fix that closes only the instance someone happened
to look at is the ubiquity failure this wave's review standard exists to catch.

### 2. Add the test that would have caught it

This is the load-bearing half. A one-line fix with no test leaves a guard with no violating case, and the
same defect returns the next time anyone adds a write.

Add a test asserting the **bytes** of the spine `open_work` writes contain **no `\r\n`**. It must be a
byte-level assertion (`Path.read_bytes()`), not a text-mode read — text mode translates on read and would
make the test pass on Windows regardless, which is a check that cannot fail.

Prove it can fail: mutate the fix out, confirm the test goes red **on this host**, and put it back. If it
cannot go red on Linux (because Linux does not translate), say so plainly and state what the test *does*
pin — an honest scoped null beats a test whose green means nothing. If that is the case, add the
assertion at the layer that *can* fail on any host: assert the exact `newline=` argument is present at
every write site in the module (a source/AST check in the house style of
`tests/test_mcp_adoption.py::_cli_only_verb_violations`, with a mutated copy as the positive control).

## Also fix, non-blocking, since you are in the file

`_rollback()` (`scripts/spine_lifecycle.py:146-153`) repeats
`subprocess.run(["git", ...], cwd=str(root), capture_output=True, text=True)` three times inline instead
of reusing a small best-effort helper. Collapse it. Keep the never-raises contract exactly as it is —
`_rollback` must not start raising.

## Out of scope — do not touch

- `generate_spine.py:910` has the **identical** newline omission. It is **pre-existing and out of this
  gate's scope**; `generate_spine.py` belongs to g4 and g5. Do not fix it here. The Commander has
  recorded it.
- `scripts/episode_capture.py` — the reviewer found a real path-doubling defect there. Out of scope.
- Everything the reviewer approved. No redesign, no renames, no new features.

## Constraints — unchanged, and a violation voids the gate

`checklist_engine.py`'s on-disk format unchanged · `validate_spine.py` unchanged · `settings.json`,
`.mcp.json`, `docs/agents/*` untouched · `skills/**` untouched · never `git add -A` · no push to `main`
· never two crews in one worktree · never waive — `spine_halt` with `action=block` and return.

## Required evidence

1. The diff.
2. The new test, and **the mutation experiment**: the code you broke, the test going red, and it green
   again after you restored the fix. Paste the actual output. If it cannot go red on this host, say so
   and show the source-level assertion you shipped instead.
3. Suite green and the sweep still exactly 23:

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

Baseline to beat: **2852 passed, 3 skipped, 1121 subtests** (2824 + g1's 28); sweep **23**. Your new
test(s) raise the first number. Use `python`, never `python3`.

## Return format

Write the result artifact at the path above **before ending your turn**. It must carry a **`Return
status`** field whose value is exactly `complete` (lowercase), the evidence above pasted verbatim, and a
short **Workflow Feedback** section.
