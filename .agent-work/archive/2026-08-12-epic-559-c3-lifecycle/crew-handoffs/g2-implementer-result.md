# Implementation Result

## Assigned gate
`g2` — close: `closeout_refusal` (pure) and `close_work` (impure) on `scripts/spine_lifecycle.py`.

## Completed slice
Added `closeout_refusal(spine, *, archive_exists)` and `close_work(spine_path, *, root, today)` to
`scripts/spine_lifecycle.py`, plus 19 new tests (51 total in the file, up from 32) to
`tests/test_spine_lifecycle.py`. Both functions match `LIFECYCLE_CONTRACT.md` §4 exactly, including the
ordering fixed there: `close_work` starts at "move the work area, spine file last" and does not perform or
re-implement satisfying the closeout gate's postconditions, the final `advance`, or `release` — those are
the caller's.

## Scope
**Files changed:**
- `scripts/spine_lifecycle.py` (+closeout_refusal, +close_work, +`_has_any_file` helper, docstring update)
- `tests/test_spine_lifecycle.py` (+19 tests covering all 10 close criteria)
- `map/INDEX.md` (regenerated via `python -m scripts.code_map build --root .`, never hand-edited — this
  was required to turn the suite green: `MapTreeFreshnessTests` failed against the two new public
  functions before regeneration)

**Specific exclusions touched:** no. `mcp_spine_server.py`, `generate_spine.py`, `episode_capture.py`,
`checklist_engine.py`, `validate_spine.py`, `settings.json`, `.mcp.json`, `docs/agents/*`, `skills/**` are
all untouched.

## Behavior changed
Yes: `scripts/spine_lifecycle.py` gained two new public functions. No existing function (`open_work` and
its pure helpers, all g1's) was touched — g1's own code needed no correction.

## Map Impact
- **Structural anchors touched:** `scripts/spine_lifecycle.py` — two new module-level functions
  (`closeout_refusal`, `close_work`) plus one private helper (`_has_any_file`); `map/INDEX.md` regenerated
  to reflect them (entity count 1156 → 1160).
- **Capabilities added:** a Constellation work area can now be closed and archived in one call, gated by
  a pure, directly-testable ordering predicate — closing the gap `open_work` (g1) left open.
- **Constraints/assumptions touched:** the archive-naming convention
  (`.agent-work/archive/<YYYY-MM-DD>-<work_id with "/" replaced by "-">/`, `archive_name_for`, shipped in
  g1) is now exercised by a real caller for the first time.
- **Trust limitations found (not fixed, out of scope for g2):** `close_work`'s per-entry move needed a
  behavior the contract's prose did not spell out — see "Instructions improvised around" below. Recorded
  here since it's a genuine property of the module a future reader (or Cartographer) should know, not just
  a workflow note.
- **Triage candidates:** none raised.

## Test mode
**Required:** test-after allowed.
**Satisfied:** yes — 19 new tests, every guard carries a VIOLATING and an INNOCENT fixture, house style
(`tests/test_mcp_adoption.py::_cli_only_verb_violations`).

## Evidence

### Required evidence 1 — differing-basename test (criterion 5), with the mutation experiment

Test (`TestCloseWorkDifferingBasenameMandatory`) closes a spine named `execute.json` (not `spine.json`) and
proves — via a monkeypatched `_git` that raises the first time any call names `execute.json` — that the
spine move is the LAST thing attempted: all other top-level entries (`crew-handoffs/`, `evidence/`,
`triage-candidates/`) have already moved to the archive by the time the interruption fires, and the spine
itself is still at its original path.

**Mutation: hardcode the literal `"spine.json"` instead of deriving from `Path(spine_path).name`.**

```
$ sed -n '404p' scripts/spine_lifecycle.py   # before mutation
    spine_name = absolute_spine_path.name
```

Mutated to `spine_name = "spine.json"` and ran the one test:

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 \
  python -m pytest -q tests/test_spine_lifecycle.py::TestCloseWorkDifferingBasenameMandatory -v
============================= test session starts ==============================
collected 1 item
tests/test_spine_lifecycle.py F                                          [100%]
=================================== FAILURES ===================================
_ TestCloseWorkDifferingBasenameMandatory.test_execute_json_spine_moves_last_not_swept_into_the_early_batch _
    ...
>       assert (archive_dir / "triage-candidates").is_dir()
E       AssertionError: assert False
E        +  where False = is_dir()
E        +    where is_dir = (PosixPath('.../archive/2026-08-12-w1') / 'triage-candidates').is_dir
=========================== short test summary info ============================
FAILED tests/test_spine_lifecycle.py::TestCloseWorkDifferingBasenameMandatory::test_execute_json_spine_moves_last_not_swept_into_the_early_batch
============================== 1 failed in 0.06s ===============================
```

RED, exactly as the contract predicts: with the literal hardcode, `execute.json` no longer matches
`spine_name`, so it falls into the "everything else" batch, sorts alphabetically between `evidence` and
`triage-candidates`, and gets swept (and the interruption fires) before `triage-candidates` ever moves.

**Restored** `spine_name = absolute_spine_path.name` and reran:

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 \
  python -m pytest -q tests/test_spine_lifecycle.py::TestCloseWorkDifferingBasenameMandatory -v
============================= test session starts ==============================
collected 1 item
tests/test_spine_lifecycle.py .                                          [100%]
============================== 1 passed in 0.08s ===============================
```

GREEN again. `git status --porcelain scripts/spine_lifecycle.py` after restoring showed no diff from the
committed derivation — the mutation left no residue.

### Required evidence 2 — the interruption fixture (criterion 6), file listing at the original path

`TestCloseWorkSpineLastUnderInterruption` monkeypatches `_git` to raise the first time any call names
`spine.json` (also catching `spine.json.journal`, a substring match, so whichever the code reaches first is
caught). Explicitly a **simulated** interruption — a real process kill between two git operations is out of
scope.

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 \
  python -m pytest -q tests/test_spine_lifecycle.py::TestCloseWorkSpineLastUnderInterruption -v
============================= test session starts ==============================
collected 1 item
tests/test_spine_lifecycle.py .                                          [100%]
============================== 1 passed in 0.03s ===============================
```

The test asserts, and the assertions hold: `area["spine_path"].is_file()` and `journal_path.is_file()` are
both true after the raised interruption (still at their original path — a retry could find them), while
`archive_dir / "crew-handoffs" / "note.md"`, `archive_dir / "evidence"`, and
`archive_dir / "triage-candidates"` are all already present under the archive.

### Required evidence 3 — end-to-end real-engine close (criterion 8), before/after directory listing

Reproduced standalone outside pytest for a clean paste (the pytest version is
`TestCloseWorkEndToEndRealEngine`, also green — see the full-suite run below):

```
=== BEFORE close_work (worktree/.agent-work/w1/) ===
/tmp/g2evidence2/wt/w1/.agent-work/w1
/tmp/g2evidence2/wt/w1/.agent-work/w1/spine.json
/tmp/g2evidence2/wt/w1/.agent-work/w1/evidence
/tmp/g2evidence2/wt/w1/.agent-work/w1/crew-handoffs
/tmp/g2evidence2/wt/w1/.agent-work/w1/triage-candidates

=== AFTER close_work (worktree/.agent-work/) ===
/tmp/g2evidence2/wt/w1/.agent-work
/tmp/g2evidence2/wt/w1/.agent-work/archive
/tmp/g2evidence2/wt/w1/.agent-work/archive/2026-08-12-w1
/tmp/g2evidence2/wt/w1/.agent-work/archive/2026-08-12-w1/spine.json
/tmp/g2evidence2/wt/w1/.agent-work/archive/2026-08-12-w1/evidence
/tmp/g2evidence2/wt/w1/.agent-work/archive/2026-08-12-w1/crew-handoffs
/tmp/g2evidence2/wt/w1/.agent-work/archive/2026-08-12-w1/triage-candidates
/tmp/g2evidence2/wt/w1/.agent-work/w1        <- now empty; git tracks no directory, so this is invisible to git

=== close_work() return value ===
{
  "work_id": "w1",
  "branch": "w1",
  "head": "359551f2b014e584fa6bbf7b95ea579dce06338c",
  "archive": "/tmp/g2evidence2/wt/w1/.agent-work/archive/2026-08-12-w1",
  "message": "closed w1: branch w1 at 359551f2b014e584fa6bbf7b95ea579dce06338c, archived under /tmp/g2evidence2/wt/w1/.agent-work/archive/2026-08-12-w1 -- ready to PR."
}

=== archived spine: origin + gate evidence intact ===
origin present: True
m1: status=complete evidence_count=1
m2: status=complete evidence_count=1

=== git status --porcelain (worktree) ===
(empty -- the move was fully committed)

=== git log --oneline -3 (worktree) ===
359551f chore: close w1 -- archive under .agent-work/archive/2026-08-12-w1
cdb426a init
```

Driven through `claim → start → attest → advance` on both gates (`m1`, `m2`) of a real `open_work`-compiled
spine, then `release`, then `close_work` — exactly the caller-owns-steps-1-3 ordering the contract requires.

### Differential test (criterion 9)

`TestCloseoutRefusalAgreesWithSpineTerminal` — `closeout_refusal`'s terminality verdict agrees with
`run_crew.spine_terminal` on both a terminal case (both `True`) and a non-terminal case (both `False`),
holding lease/archive constant so the comparison isolates the terminality read alone.

### Confirmatory evidence — refusal messages, suite total, sweep count

```bash
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 \
  python -m pytest -q tests/test_spine_lifecycle.py
...................................................                      [100%]
51 passed in 0.27s

$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2875 passed, 3 skipped, 1121 subtests passed in 114.88s (0:01:54)
# baseline before this change: 2856 passed, 3 skipped, 1121 subtests -- +19 net, exactly matching
# tests/test_spine_lifecycle.py's own growth (32 -> 51 `def test_` methods, +19); no other file's test
# count moved.

$ python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
23
```

Refusal messages, spot-checked directly (`TestCloseoutRefusal`):
- lease active: `"close refused: the lease is still active"` — contains the required phrase verbatim.
- non-terminal gate: `"close refused: gate 'm2' is not terminal (status 'in-progress')"` — names the
  offending gate (`m2`) and *not* the terminal one (`m1`), asserted explicitly.
- archive exists: `"close refused: the archive directory already exists"`.

## TDD evidence, if required
Test-after was allowed and used. The one required red/green cycle (the mutation experiment above) is TDD
evidence in the other direction — proving a plausible wrong implementation is caught, not proving the right
one from red.

## Docs/contracts touched
- None. `scripts/spine_lifecycle.py`'s own module docstring was extended to describe `close_work` (it
  previously said only `open_work` shipped here); `LIFECYCLE_CONTRACT.md` itself is unchanged.

## Assumptions
- `close_work`'s `root` parameter is the **worktree** root (where `.agent-work/<work_id>/` and the git
  repo state to commit into both live), not the main checkout `open_work` cloned from — consistent with
  the g2 handoff's own framing ("Worktree: ... you are already in it") and with how the end-to-end test
  exercises it (`root=worktree`, not `root=repo`).
- The excluded spine/journal basenames are derived from `Path(spine_path).name` (mandatory, per the
  handoff); the **work id** — and so the archive name — is likewise derived structurally, from
  `spine_path`'s location relative to `root/.agent-work`, rather than read from the spine's `origin` field.
  This was not explicitly specified either way in the handoff or contract; deriving it structurally means
  `close_work` never depends on `origin` being present at all (consistent with §8's explicit exclusion of
  "retrofitting `origin` onto spines opened by hand" — a hand-authored spine can still be closed), and it
  is exercised by every fixture in the suite, including the `execute.json` one, without needing to fabricate
  an `origin` block. Flagged here since it is a design choice within latitude, not literally named in either
  source document.

## Stop conditions hit
None. No constraint was violated, the end-to-end close worked with the fixed ordering, and no check needed
more than two attempts.

## Out-of-scope observations
None beyond the map staleness (regenerated, within allowed scope, not a finding for elsewhere).

## Workflow Feedback

- **Handoff gaps:** none in the close-ordering spec itself — §4 was precise enough to implement directly.
  One real gap: neither the handoff nor `LIFECYCLE_CONTRACT.md` mentions that a freshly scaffolded work
  area (via `init_work_area.init_work_area`, g1's own dependency) routinely holds **untracked, and
  sometimes entirely empty, directories** by the time `close_work` runs — `crew-handoffs/`, `evidence/`,
  `triage-candidates/` are created but nothing writes into or commits them during a bare
  `open_work` → drive → `close_work` cycle. A naive `git mv <entry> <dest>` (which is what "git mv every
  top-level entry ... each call naming its own paths" reads as, literally) fails outright on an empty
  directory (`fatal: source directory is empty`) and on an untracked file (`fatal: not under version
  control`) — confirmed empirically before writing the fix. `close_work` now stages each entry by its own
  explicit path first (`git add <path>`, a no-op for already-tracked content, never `-A`/bare `.`) and
  falls back to a plain filesystem rename for an entry with no trackable content at all (an empty
  directory — git tracks no directory, ever, no matter how it's staged). This is genuinely load-bearing:
  without it, the end-to-end test (criterion 8) would fail on the very `evidence`/`triage-candidates`
  directories `init_work_area` itself creates. Naming it here so a future reader of the contract knows this
  isn't an invented complication.
- **Context rediscovered:** had to empirically verify `git mv`'s exact failure modes (empty directory vs.
  untracked file vs. staged-but-uncommitted) via a throwaway repo, since neither git's own docs phrasing
  nor the contract state this. Worth a one-line note in `LIFECYCLE_CONTRACT.md` §4 if this contract is ever
  revisited.
- **Instructions improvised around:** the handoff's criterion 7 says the stage-by-name guard is "asserted
  over `close_work`'s own source." The actual `git add`/`git mv` calls live in a closure
  (`_stage_and_move`) nested *inside* `close_work` rather than as a separate module-level function, so that
  `inspect.getsource(sl.close_work)` — which includes nested `def`s in its returned text — genuinely
  covers every staging call without requiring the guard to also scan a sibling helper. Chose this over a
  separate `_move_entry` module function (my first draft) specifically so "close_work's own source" would
  be literally true rather than requiring a footnote.
- **What would have made this easier:** a one-line note in the handoff that a scaffolded work area's
  subdirectories are commonly empty/untracked at close time would have saved the empirical git
  investigation. Not a blocker — found and fixed within scope — just the single largest time cost in this
  gate.

## Return status
`complete`
