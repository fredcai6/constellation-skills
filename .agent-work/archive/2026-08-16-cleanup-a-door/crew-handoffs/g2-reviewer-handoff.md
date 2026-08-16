# Reviewer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
`g2` — issue #605, the shipped demo spine is unusable.

## Task statement (what was asked)

`examples/mcp-interactive-demo/spine.json` shipped with six absolute paths into
`/home/tommy/projects/constellation-skills-wt/f-424`, a worktree deleted during the
epic-418-followon closeout. Make the demo runnable where it is installed, on any machine,
and add a guard that keeps a machine-specific absolute path out of a shipped example again.

The dispatch established one constraint that overrides the issue's own fix direction:
**relative-to-the-example-directory cannot work**, because `scripts/checklist_engine.py:883`
runs command checks with `subprocess.run([shell, "-c", command])` and **no `cwd`**.

## What was implemented

**Staged, not yet committed.** Six files:

| File | Change |
|---|---|
| `examples/mcp-interactive-demo/spine.json` | regenerated |
| `examples/mcp-interactive-demo/make_demo_spine.py` | new generator, 168 lines |
| `examples/mcp-interactive-demo/README.md` | rewritten |
| `examples/mcp-interactive-demo/.gitignore` | new |
| `tests/test_shipped_examples_are_portable.py` | new guard, 370 lines |
| `map/INDEX.md` | rebuilt for the new entity |

**The design call: candidate (b)** — ship a spine whose check text is self-locating.
Candidate (a) ("ship the generator, not the generated spine") was rejected because
`tests/test_mcp_spine_server.py:588` json-loads `.mcp.json`'s `SPINE_FILE` default, which is
this very spine, so not committing it fails that test — and the only reconciliation is
editing `.mcp.json`, which is **gate g3's** file and was an explicit stop condition.

Every check and imperative names the workspace as:

```
${SPINE_DEMO_WORKSPACE:-${TMPDIR:-/tmp}/constellation-mcp-demo-$(id -u)}/workspace
```

The shell running the check expands this, so it resolves absolutely on any machine with no
ambient cwd. Drift is closed by a test that imports the generator and asserts the committed
spine is byte-identical to what it produces.

Full `IMPLEMENTER_RESULT`: `.agent-work/cleanup-a-door/crew-handoffs/g2-implementer-result.md`.

## How to inspect the diff

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
git diff --cached --stat
git diff --cached
git diff a69bbac4 -- examples/mcp-interactive-demo/
```

## Close criteria — verify each independently

1. **No absolute or machine-specific path remains anywhere under `examples/`.** Enumerate
   by command and **state the count**.
2. **The demo genuinely drives** from at least **two** different working directories, one of
   which is neither the repo root nor the example directory. **Run it — do not read it.**
   Paste both transcripts, including a gate whose *command* postcondition actually passes
   (that is what proves the path resolved). **Restore the spine afterwards** — driving it
   mutates it, and the committed file must stay pristine and byte-identical to the
   generator's output.
3. **The guard fails on pre-fix content.** Recipe:
   `git checkout a69bbac4 -- examples/mcp-interactive-demo/spine.json`, run the guard,
   then restore (`git checkout HEAD -- ...` will not work — the fix is *staged*, not
   committed; keep a copy first).
4. **The guard is not vacuous.** It must assert what it looped over and must not pass on an
   empty set. Check: does it state the count of files examined? Would it go green if the
   examples directory were empty or if its glob matched nothing? Try it.
5. **`tests/test_mcp_spine_server.py:588` still passes** — `.mcp.json`'s default must still
   resolve to a real, loadable spine.
6. **`README.md`'s regeneration command points at a path that EXISTS.** It previously named
   the pre-archive `.agent-work/epic-418-followon/...`. A dead *relative* path is not caught
   by an absolute-path guard, so check it by running it.
7. **`README.md`'s opening sentence is unchanged** — "This is the checklist the
   project-scope `.mcp.json` points at" is still true until g3 and g3 owns changing it. If
   g2 changed it, that is scope drift.
8. **`map/INDEX.md` freshness passes.**
9. **The generator is wired** — it has a call site outside its own definition and outside
   any self-test (the guard test importing it counts; say so and state the count).

## Allowed scope

Review only. Report findings; do not fix.

## Specific exclusions

- `.mcp.json` — **gate g3's** (#603). It still carries the demo default; that is correct
  at this gate. Do not block g2 for it.
- `scripts/mcp_spine_server.py` — g1's (already closed) and g3's.
- `scripts/checklist_engine.py`, `scripts/hooks/**`, `run_crew.py`, `gauge_reader.py` —
  **lanes B and C, running concurrently.** Read `:883`; never modify.
- Fail-closed / bind-on-open behaviour — g3's.

## Constraints

- **Clear `__pycache__` before every measurement**
  (`find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +`) — stale
  bytecode fabricates failures that look exactly like defects (#597).
- The suite command drops the spine env vars:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q ...`
- **The change is STAGED, not committed.** `git stash` and `git checkout HEAD --` will not
  behave the way they do for a committed change. Copy files aside before mutating them.

## Map anchors (inbound)

Inherited from `g2-implement`. **Map entry point: none** — `map/ids.jsonl` is tracked but
empty (0 bytes), so no map anchor resolves in this repo. Work from source.

- **Structural:** `examples/mcp-interactive-demo/**`; `scripts/checklist_engine.py:883`
  (read only — why relative paths cannot work); `tests/test_mcp_spine_server.py:588`.
- **Capability:** shipped example — must run where it is installed, on any machine.
- **Constraints:** `constraint:shipped-content-must-not-carry-machine-specific-absolute-paths`;
  `constraint:engine-runs-command-checks-with-no-cwd`.
- **Decision:** `decision:demo-spine-is-generated-not-hand-fixed`.
  `@grade: guess · leans g2-implement · settle: whichever is smaller once the example's build is read`
  Resolved this gate as candidate (b), with the reason recorded above — judge whether that
  reasoning holds.
- **Evidence:** `claim:605-demo-unusable`.

## Evidence already produced (reproduce, do not trust)

Commander's own re-verification, all independently run:

- `grep -rn "/home/\|constellation-skills-wt\|f-424" examples/` → **count 0**.
- Guard against the pre-fix spine → **3 failed, 4 passed** (the portability test, the
  generator-drift test, and the drives-from-anywhere test all fire).
- Drove the demo from `cwd=/tmp`: `g1 -> in-progress`, command check passed,
  `g1 -> complete`. Spine restored pristine afterwards.
- `244 passed, 508 subtests` across the portability guard, `test_mcp_spine_server.py`,
  `test_wire_mcp_interpreter.py`, `test_install_constellation.py`.

Your job is not to repeat my list — it is to find what neither of us checked. Attack
criterion 4 (vacuity) and criterion 2 (does it drive from a *second*, genuinely different
cwd, e.g. `$HOME` or a path with a space in it?) hardest.

## Verification commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
grep -rn "/home/\|constellation-skills-wt\|f-424" examples/ ; echo "exit=$?"
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_shipped_examples_are_portable.py tests/test_mcp_spine_server.py \
  tests/test_wire_mcp_interpreter.py tests/test_install_constellation.py
```

## Suggested model tier

`stronger` — the gate made a design call under a cross-gate constraint, and the guard's
vacuity is the kind of defect that reads as green.

## Stop conditions

Stop and return if: the staged diff exceeds the six files named; a fenced file was touched;
required evidence cannot be produced; or a decision outside review authority is needed.

## Return format

Return `REVIEW_RESULT` with a verdict of **`APPROVE`** or **`BLOCK`**, findings (each with
evidence you reproduced yourself), what you checked and found sound, and what you did NOT
check as an explicit scoped null. Include a `Workflow Feedback` section.

**Delivery.** Write the full `REVIEW_RESULT` to
`.agent-work/cleanup-a-door/crew-handoffs/g2-reviewer-result.md` **before ending your
turn** — that write is the delivery.
