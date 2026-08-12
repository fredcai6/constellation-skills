# Launch order — R0: repair the two defects blocking C3's merge (#559)

**Work id:** `epic-559/r0-lifecycle-repair` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` — C3's own, confirmed dead
**Branch:** `epic-559/c3-lifecycle` at `50316413`, already pushed, **PR #564 open against `main`**
**Deliverable:** `.agent-work/epic-559/r0-lifecycle-repair/IMPLEMENTER_RESULT.md`

C3 shipped `scripts/spine_lifecycle.py`, the `spine_open`/`spine_close` door tools, and the declared
dispatch. Cold review approved all of it. **Two defects hold the merge.** Both are on C3's own
surface. Fix them, prove each fix by watching it fail first, and hand the merge back up.

## Defect 1 — a test that passes only inside one worktree

`tests/test_spine_lifecycle.py::TestWorktreePathForRealWorktree::test_reproduces_this_runs_real_worktree`
hardcodes the work id `"epic-559/c3-lifecycle"` and asserts the derived path equals the **current**
checkout root. It therefore passes only from a checkout literally at `<primary>-wt/c3-lifecycle`.

Measured: in a detached scratch worktree at `51feb36c` the suite is **1 failed, 2931 passed,
3 skipped, 1121 subtests** — that one failure. It fails in the main checkout and it fails on CI.

Its own comment claims it *"stays true on any host."* **That comment is the bug.** The test's
intent is sound — confirm the `wt_root` convention against live git state rather than a hardcoded
path — so keep the intent and fix the mechanism: derive the work id from the checkout under test
rather than naming one, or make the test state the condition under which it applies and skip
outside it. **A skip that fires everywhere is not a fix**; if you skip, the test must still run and
pass somewhere reachable, and you must say where.

## Defect 2 — `close_work` half-succeeds on a real work area

C3 found this by running `close_work` on its own work area, and it is the better of the two finds:

```
git add .../mcp_calls.jsonl failed: The following paths are ignored by one of your .gitignore files
```

`close_work` `git add`s every top-level entry. The MCP door writes **`mcp_calls.jsonl`** and
**`mcp_server_started`** beside the spine and both are gitignored, so `git add` refuses. It had
already moved **22 entries** when it raised, leaving the work area split across two directories with
**no rollback**.

That is exactly the refuse-rather-than-half-succeed property the launch order demanded of
`open_work` — which has it — and never asked of `close_work`. **Spine-last held under the real
interruption**: the spine and journal were still at the original path, so a retry could find them.
Keep that property; it is the thing that saved the run.

C3's suggested shape, which you may adopt or better: classify each entry (tracked /
untracked-not-ignored / ignored) and move each accordingly — `git mv` for tracked, `git add` then
move for untracked-not-ignored, plain filesystem move for ignored — and wrap the sequence so a
failure restores what it moved.

**Why no test caught it, and this is the part that matters.** Every `close_work` fixture builds its
work area with `open_work`, which never produces a gitignored file. The cold plan critic caught this
exact blindness for the spine *filename* and it was fixed there with a mandatory differing-basename
fixture — and nobody generalized it. **Your fixture must contain a gitignored file**, because a real
work area always does.

## The standard both fixes are held to

**A guard you have not seen fail is not a guard.** For each fix, mutate the real source (not a
paraphrase of it in the test) and watch your test refuse. Say in the result what you mutated and
what the failure said. Two of C3's guards were confirmed this way at cold review — inserting a
`SPINE` reference into `_spine_open`, and replacing `close_work`'s derived `spine_name` with the
literal `"spine.json"` — and both fired.

**Ask two questions of every check you run:** does this mechanism work, and is the value it carries
correct? Four reviews in one epic missed defects by answering only the first.

## Scope

**In:** `scripts/spine_lifecycle.py`, `tests/test_spine_lifecycle.py`, and any fixture helper those
two need.

**Out — hard no-gos:**

- `skills/**` — R1's surface, unlaunched.
- `settings.json`, `.mcp.json`, `docs/agents/*`.
- **Do not run `scripts/install_constellation.py`** — it rewrites the tracked `.mcp.json` (known
  defect, #539).
- **No merge to `main`.** The branch is already pushed and PR #564 is open; push your commits to it,
  **do not merge it**. The merge is the Admiral's.
- Do not touch anything under `.agent-work/archive/` — C3's run is closed.
- **Do not patch C3's approved code beyond these two defects.** If you find a third thing, report it.

## Standing rulings

- **Stage by name.** `.agent-work/` is tracked here. **Never `git add -A`** — and scoped `-A` is
  still `-A`; C3 swept a stray directory in exactly that way and had to undo it.
- **Block, do not force.** A check you cannot satisfy means `spine_halt` with `action=block`, naming
  your parent (`SPINE_PARENT`), and returning. Never waive your own gate; the door denies it.
  **And a block you have raised stays raised until the tier above clears it** — C3 blocked correctly
  on an unauthorized act and then took the act itself three minutes later. Do not do that.
- **Honest null.** A measured negative is a complete deliverable. If defect 2's fix turns out to need
  more than this scope, say so with the measurement rather than half-doing it.

## Test mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Use `python`, not `python3`. **Baseline in this worktree: 2932 passed, 3 skipped, 1121 subtests.**
That number is the *unportable* one — it includes the broken test passing. In a foreign checkout the
same tree is 2931 passed + 1 failed. Your target is the suite green **from a checkout that is not
this worktree**, which your final gate checks by creating one.

`python scripts/validate_spine.py --sweep --root .` reports **23** fault lines across 8 files. It
should not move; if it does, explain it.

## Drive your own work through the door

Your dispatch binds `SPINE_FILE`/`SPINE_SESSION` and names your parent in `SPINE_PARENT`. Use
`mcp__spine__*`, found via `ToolSearch`. Attest a `check: null` precondition **before** `start` — the
engine refuses `start` while a precondition is unmet, and the refusal is non-destructive.

Write `IMPLEMENTER_RESULT.md` including its **Workflow Feedback** section before ending your turn —
that write is the delivery.
