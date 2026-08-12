# Implementer Handoff — g2: close

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g2` · **Role:** `implementer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (you are already in it)
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander. Ask up to
it, not past it.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g2-implementer-result.md`

## Read first

`.agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md` — **§4 is your specification**, and §2's entry
for `closeout_refusal`. Where this handoff and that contract disagree, the contract wins. Read §1b for why
two of these decisions are shaped the way they are — both came from a cold critic and both are load-bearing
here.

`scripts/spine_lifecycle.py` already exists (g1 shipped `open_work` and the pure helpers, including
`archive_name_for`). **You are adding to it, not rewriting it.**

## Task

Add `closeout_refusal` (pure) and `close_work` (impure) to `scripts/spine_lifecycle.py`, with tests in
`tests/test_spine_lifecycle.py`.

### `closeout_refusal(spine: dict, *, archive_exists: bool) -> str | None`

Pure: no `Path`, no `open`, no `subprocess`. Returns `None` when close may proceed, else the refusal
message. **This is the whole close-ordering predicate.** It refuses unless all of:

- `engine_session.status == "released"` — message names "the lease is still active";
- every id in `items` has a terminal task status — message **names the offending gate**;
- `archive_exists` is false — never overwrite a prior archive.

**Do NOT call `run_crew.spine_terminal` from it.** That function takes a **path** and reads the file
(`scripts/run_crew.py:317`), so a pure dict-in predicate cannot call it — a cold critic caught an earlier
draft asserting both. Compute terminality from the dict.

**Instead, ship a differential test**: assert `closeout_refusal`'s terminality verdict **agrees with**
`run_crew.spine_terminal` on the same spine, over one terminal case and one non-terminal case. That pins
the agreement the "never re-derive" instruction was reaching for, without pretending a pure function can
do I/O. Read `spine_terminal` first and match its notion of terminal exactly.

### `close_work(spine_path, *, root, today)`

**The ordering is fixed by the launch order and is NOT your latitude.** Steps 1–3 belong to the *caller*
and `close_work` neither performs nor re-implements them:

1. satisfy the closeout gate's postconditions
2. final `advance`
3. `release` the lease
4. **← `close_work` starts here.** Move the work area, spine file **last**
5. commit the move
6. report readiness

So `close_work`:

- Calls `closeout_refusal` and, if it refuses, **does nothing at all** — no partial move, no staging.
- Otherwise `git mv`s every top-level entry under `.agent-work/<work-id>/` **except the bound spine and
  its journal**, each call naming its own paths; **then** `git mv`s those two, **last**; then
  `git commit`.
- Reports a verdict naming the branch, the new `HEAD`, and **"ready to PR."**

**It never opens a PR. It never removes a worktree. It never judges the work good.**

### The excluded names are DERIVED, never literal — this is the finding that mattered most

They are `Path(spine_path).name` and that name plus `.journal`. **Not** the strings `"spine.json"` and
`"spine.json.journal"`.

Why, measured: both filenames are in heavy use in this repo — `spine.json` 48 vs `execute.json` 40 at
depth 3 under `.agent-work/`, 43 vs 42 excluding the archive — **and this Commander's own driving spine is
named `execute.json`**. A literal hardcode would sweep a live driving checklist into the "everything else"
batch **before** the spine-last step, which is the exact failure the fixed ordering exists to prevent.

It is invisible to every matched-pair fixture, because a spine `open_work` created is always named
whatever `open_work` names it (`spine.json`). So the differing-basename test below is **mandatory**.

### Archive naming

`.agent-work/archive/<YYYY-MM-DD>-<work_id with "/" replaced by "-">/`, via g1's existing
`archive_name_for(work_id, today=...)`. `today` is a parameter so the name is deterministic in a test.
This deviates from the launch order's `.agent-work/archive/<work-id>/` shorthand deliberately: measured,
38 of 41 existing archive entries use the date-prefixed flat form and none is nested.

## Protected intent

The closing advance **puts the work away and says it is ready** — and it must not eat the spine that is
driving it. A close that half-moves a work area is worse than one that refuses.

## Test mode

Test-after allowed. **Every guard needs a violating case** — house style
`tests/test_mcp_adoption.py::_cli_only_verb_violations`, VIOLATING / INNOCENT. Tests build their own
throwaway git repo under `tmp_path` and never touch this worktree's real git state.

## Close criteria

1. **VIOLATING** — `close_work` with the lease still `"active"` refuses and leaves the work area
   **byte-for-byte untouched** (assert the file set and that nothing exists under `archive/`).
2. **VIOLATING** — a non-terminal gate: refuses and **names the offending gate**.
3. **VIOLATING** — the archive directory already exists: refuses rather than overwriting.
4. **INNOCENT** — genuinely terminal and released: proceeds.
5. **MANDATORY, and the reason this gate exists** — close a spine whose basename is **not** what
   `open_work` writes (an `execute.json`) and assert it still moved **last**. A literal hardcode must turn
   this test red; prove it by mutating the derivation to the literal string, watching it go red, and
   restoring.
6. **Spine-last under interruption** — monkeypatch the mover to raise **after** the non-spine entries move
   and **before** the spine-last step; assert the spine and its journal are still at the **original**
   path, so a retry can find them. This is a **simulated** interruption and your result must say so; a
   real process kill between two git operations is out of scope.
7. **Stage-by-name source guard** — no `git add -A` and no bare `.` reaches a staging call, asserted over
   `close_work`'s own source, **with a mutated copy as the positive control** proving the guard can fail.
8. **End to end** — drive a real generated spine to terminal through the **real engine**
   (`claim → start → attest → advance` on every gate), `release`, then `close_work`; assert the spine
   lands under the archive with `origin` and every gate's `evidence[]` intact.
9. Differential test: `closeout_refusal` agrees with `run_crew.spine_terminal`.
10. Suite green; `python scripts/validate_spine.py --sweep --root .` still exactly **23**.

## Allowed scope

`scripts/spine_lifecycle.py` (add to it) · `tests/test_spine_lifecycle.py` (add to it) · `map/`
(regenerated only, never hand-edited). Read anything.

## Specific exclusions

- **No door wiring.** `scripts/mcp_spine_server.py` is g3's — do not touch it.
- `scripts/generate_spine.py` is g4's and g5's — **import it, do not edit it.** Its missing `newline="\n"`
  at line 910 is known, pre-existing, and deliberately out of scope.
- `scripts/episode_capture.py` has a known path-doubling defect — out of scope.
- Do not change anything g1 shipped unless a g2 test proves it wrong; if one does, **say so** rather than
  quietly editing it.

## Constraints — a violation voids the gate

- **`encoding="utf-8", newline="\n"` on EVERY write** (`docs/agents/CREW_CONTEXT.md:43`). CI runs
  `windows-latest`. g1 was BLOCKed for exactly this; the module now carries a source-level pin over every
  `write_text` call site — **do not weaken or exempt yourself from it.**
- `checklist_engine.py`'s on-disk format unchanged. `validate_spine.py` unchanged.
- `settings.json`, `.mcp.json`, `docs/agents/*` untouched. **If the harness refuses an `Edit`/`Write` on
  `.mcp.json`, that guard is deliberate — do not route around it with a `Bash` write. Block and ask.**
- `skills/**` untouched — a different crew owns it. If something there must change, **block and say so.**
- Never run `scripts/install_constellation.py`.
- No merge and no push to `main`.
- **Never `git add -A` and never a bare `.`** — you are shipping the guard for this; do not violate it
  while doing so.
- Never two crews in one worktree.

## Deliverable path check

- **Committed** — `scripts/spine_lifecycle.py`, `tests/test_spine_lifecycle.py`; both already tracked, so
  they appear in `git diff`.
- **Local-only** — your result artifact under `.agent-work/`; the Commander commits it.

## Required evidence

Load-bearing — prove these rigorously:

1. The differing-basename test (criterion 5), **with the mutation experiment**: the literal-string version
   going red, and green again after restoring the derivation. Paste the actual output.
2. The interruption fixture (6), with the file listing at the original path afterward.
3. The end-to-end real-engine close (8), with the before/after directory listing.

Confirmatory — a spot-check suffices: the refusal messages, the suite total, the sweep count.

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_spine_lifecycle.py
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

**Baseline before your change: 2856 passed, 3 skipped, 1121 subtests; sweep exactly 23.** Use `python`,
never `python3` — `python3` on this host has no pytest.

## Stop conditions

- A constraint above would have to be violated → **block**, name it, return.
- The end-to-end close cannot be made to work without changing the fixed ordering → **block and say so
  with the output.** A measured negative is a complete deliverable; inventing a different order is not.
- Two failed attempts at the same check → block rather than a third.
- **Never waive.** `spine_halt` with `action=block`, name what you cannot satisfy, and return.

## Return format

Write the result artifact at the path above **before ending your turn** — that write is the delivery. It
must carry a **`Return status`** field whose value is exactly `complete` (lowercase) when done, the
evidence above pasted verbatim, anything you could not do, and a short **Workflow Feedback** section.
Return thin: the verdict, the deciding evidence, and the path.
