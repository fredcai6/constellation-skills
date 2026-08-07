# Implementation Result — g2: the replacement capture obligation

## Assigned gate
`g2` — issue #447, epic-418 workstream H. Plan driven through the engine:
`.agent-work/epic418-h-447/crew-plans/g2-implementer.json` (work id `h-447-g2-implementer`,
session `g2-impl-447`, 7 gates, 1 rework).

## Completed slice
The write-side capture gate that replaces `.agent-work/LESSONS.md` and
`.agent-work/AGENT_FEEDBACK.md`: a verifier that asserts an episode was CAPTURED for a run,
and nothing else. No read path was created.

## Scope
**Files changed:**
- `scripts/verify_episode_captured.py` — NEW (223 lines)
- `tests/test_verify_episode_captured.py` — NEW (16 tests, 4 classes)
- `scripts/apply_episode_delta.py` — comment only at `store_root()` (12 added lines,
  all comments; `git diff -U0` reports 0 non-comment additions and 0 deletions)

**Specific exclusions touched:** no. No spine, no install bundle, no guard, no
`episodes/` content, no commit, no git state.

## Behavior changed
Yes — new gate. `verify_episode_captured.py <work-id> [--store-root PATH] [--phase feedback|archive]`:

- **0** — at least one episode in `<store-root>/active` has `- run: <work-id>`. Prints the
  matched ids, the match count, and the number of files scanned.
- **1** — BLOCKED. The store was readable and holds no such episode; or, under
  `--phase archive`, holds one git does not track.
- **2** — REFUSED. The store could not be read: missing root, missing `active/`, or a record
  with no header / no `- run:` line. Refused, not answered — a typo'd `--store-root` must not
  read as an empty store. The two failure codes are distinct, and a test asserts they are.

No ripeness, no apply-or-defer, no dormancy, no counters. Those retired with the playbook.

## THE VALVE — proven, not asserted
The verifier parses exactly two things: the `<!-- episode-state: -->` header line and the
`- run:` mechanical line. `scan_episode()` **stops reading at the `## Agent-supplied`
heading**, so statement text is never read into memory at all.

- `ValveTests.test_no_statement_text_reaches_stdout_or_stderr` — every seeded statement is
  the literal `SENTINEL-DO-NOT-LEAK-9f2a`; the gate runs over **four outcome paths**
  (captured / blocked / archive-blocked / refused) with stdout and stderr both captured, and
  the sentinel must appear in neither. The subtest count is asserted, so the loop cannot pass
  by looping over nothing.
- `ValveTests.test_the_leak_assertion_can_fail` — the in-suite red proof: the read seam is
  patched to echo the record body and the **same** assertion helper is required to raise.
- `ValveTests.test_the_gate_links_to_no_store_reader` — reads the real import graph with
  `ast` (not a grep, because the file's own prose names `query_episodes`): asserts
  `query_episodes` is not imported and that **no** module under `scripts/` is imported at all.

## Test mode
**Required:** test-first (the handoff demands red proofs; it never names a test-mode field).
**Satisfied:** yes. m1 is true TDD red-then-green. The refusal, archive, and valve legs were
authored inside the same file creation as m1, so their honest red is a **mutation proof**:
the guard is disabled, the mutation is asserted to have applied, the tests are watched going
red, and the bytes are restored and re-verified. Transcripts are in
`.agent-work/epic418-h-447/evidence/`.

## Evidence — every command, real exit code (redirect + `echo $?`, never a pipe)

```bash
python -m pytest tests/test_verify_episode_captured.py -q          # EXIT=0  — 15 passed, 4 subtests passed
python scripts/verify_episode_captured.py no-such-run  --store-root episodes                    # EXIT=1
python scripts/verify_episode_captured.py issue-308    --store-root episodes                    # EXIT=0
python scripts/verify_episode_captured.py issue-308    --store-root /nonexistent                # EXIT=2
python scripts/verify_episode_captured.py issue-308    --store-root episodes --phase archive    # EXIT=0
python -m pytest -q                                                # EXIT=1 — see below
```

Required by the handoff: 1, 0, non-zero. Measured: 1, 0, 2. Output lines:

```
BLOCKED - no episode in episodes\active records run 'no-such-run' (32 episode(s) scanned).
episode capture: 25 episode(s) recorded for run 'issue-308' in episodes\active (32 scanned, phase feedback)
REFUSED - missing store: ...\nonexistent is not a directory. ... refused rather than answered.
episode capture: 25 episode(s) recorded for run 'issue-308' in episodes\active (32 scanned, phase archive)
```

**Full suite:** `python -m pytest -q` exits 1 both before and after this change. The failure
set is **identical** to the pre-change baseline: 10 failures, all
`tests/test_mutation_floor.py::MutationFloor::*` (a nested `map_orient` harness, untouched
here). Baseline captured before any edit at
`.agent-work/epic418-h-447/evidence/g2-baseline-failures.txt`; the m6 gate check re-runs the
suite and `diff`s the failure sets, so "no new failures" is a command result, not a claim.
Counts: 1690 passed / 10 failed before; 1705 passed / the same 10 failed after (`diff` of the
two failure sets exits 0).

**One flake seen and characterized, not absorbed.** The first post-change full-suite run showed
an 11th failure — `tests/test_crew_launcher.py::LaunchTests::test_records_entry_before_launch_and_completes`
(`fake_launch` stubbed exit 0; `launch_crew` returned 1). It passes in isolation (74 passed,
whole file), neither new file is imported by `run_crew.py`, and the second full run — the one
the gate accepted — did not reproduce it. Reported rather than dropped: this test touches temp
files and a durable registry while other agents run in this box's work area, so it looks
load-sensitive. Worth a triage line if it recurs.

## The sentinel red proof (`evidence/g2-m4-sentinel-red.txt`)

`print(path.read_text(encoding="utf-8"))` injected at the top of `scan_episode()`, mutation
asserted applied, `ValveTests` re-run, bytes restored and re-verified byte-identical:

```
pytest exit: 1
E   AssertionError: 'SENTINEL-DO-NOT-LEAK-9f2a' unexpectedly found in "<!-- episode-state: schema=1 id=issue-447-001 ...
E   AssertionError: 'SENTINEL-DO-NOT-LEAK-9f2a' unexpectedly found in '<!-- episode-state: schema=1 id=issue-447-001 ...
E   AssertionError: 'SENTINEL-DO-NOT-LEAK-9f2a' unexpectedly found in '<!-- episode-state: schema=1 id=issue-447-001 ...
E   AssertionError: 'SENTINEL-DO-NOT-LEAK-9f2a' unexpectedly found in "<!-- episode-state: schema=1 id=issue-447-001 ...
FAILED tests/test_verify_episode_captured.py::ValveTests::test_no_statement_text_reaches_stdout_or_stderr
FAILED tests/test_verify_episode_captured.py::ValveTests::test_the_leak_assertion_can_fail
5 failed, 1 passed, 1 subtests passed
RESTORED: bytes identical to pre-mutation
```

The leak test fails on 3 of its 4 outcome paths. The `refused` path stays green **by
construction** — it never opens a file — which is a property of that path, not a hole in the
assertion. With the leak removed: 15 passed.

Other red proofs, same method (mutate → assert applied → red → restore → assert restored):
- `evidence/g2-m1-red.txt` — true TDD red: 4 failed, the script did not exist yet.
- `evidence/g2-m2-mutation-red.txt` — 3 of 3 refusal guards disabled → the 4 refusal tests red.
- `evidence/g2-m3-mutation-red.txt` — archive branch disabled → the untracked-fails test red;
  git forced to answer "untracked" → the tracked-passes test red. Both directions.
- `evidence/g2-m3-rework-red.txt` — the `path.resolve()` fix line deleted → the relative-root
  regression test red.

## Defect found and fixed mid-run (engine rework 1/3)
The handoff's own evidence command caught a real bug that the tests had missed.
`_git_tracked` passed a possibly-**relative** path as the git pathspec while running git with
`cwd=path.parent`, so `--store-root episodes` asked git about
`episodes/active/episodes/active/<id>.md`: **25 of 25 genuinely committed episodes reported
untracked** — a false BLOCK that would have failed every real archive gate. Every m3 test used
an absolute temp path, so the shape was uncovered. Reopened `m3-archive-phase` through the
engine, fixed with `path = path.resolve()`, added
`test_archive_phase_accepts_a_relative_store_root` (subprocess, relative `--store-root`, real
temp git repo), red-proved it, and re-ran against the real store: `EXIT=0`.

## Corner cases NOT chased — each named in a comment at the code site
1. **`--store-root` default carries the installed-copy hazard** —
   `scripts/verify_episode_captured.py:196-201`. The default resolves relative to the script
   file, so on a bundled/installed copy it points at the skill install directory, exactly like
   `store_root()`. Not fixed here: g3 wires `--store-root` into the spine commands. Mitigation
   in place: the resolved root is printed on every outcome, so a wrong root is visible in the
   gate log rather than silent.
2. **`_git_tracked` cannot distinguish "untracked" from "not a git repository"** —
   `scripts/verify_episode_captured.py:151-161`. Both answer "not durable", which is the
   answer the archive phase acts on either way; git's own message is carried into the block
   output so a reader can tell them apart.
3. **`retired/` is not searched** — `scripts/verify_episode_captured.py:125-130`. An episode
   captured and then retired within the same run would read as uncaptured. Nothing retires
   mid-run today, and chasing it would mean teaching the capture gate to reach into the
   archive — the exact widening the valve exists to prevent.
4. **`store_root()` itself is unchanged** — `scripts/apply_episode_delta.py:511-522`. The
   hazard is named in a comment, per the handoff; the semantics and the `durable_root()`
   ruling in the docstring are untouched.

## Docs/contracts touched
None. `docs/EPISODE_STORE.md` describes the store's record grammar and write contract, neither
of which changed. The gate's contract lives in its own module docstring.

## Assumptions
- Exit 2 for a refusal: the handoff required only "non-zero". A spine that cannot distinguish
  "you did not capture" from "I could not look" cannot act on either, so the two are split.
  A test asserts they differ; if the Commander wants one code, it is a one-line change.
- A record in `active/` with no header or no `- run:` line is REFUSED, not skipped — matching
  `episodes/README.md`'s refuse-don't-skip rule rather than inventing a lenient one.

## Stop conditions hit
None.

## Unresolved blockers
**None.** Explicitly: nothing is waiting on the Commander, the Admiral, or the human.

Expected-and-not-mine, per the handoff: `scripts/verify_retirement.py`'s `replacement-absent`
leg stays RED until g3 wires the spines. Not touched.

## Out-of-scope observations (triage candidates)
- `tests/test_mutation_floor.py` has 10 failures on `main` in this worktree, all "HARNESS
  ERROR" from a nested `map_orient` self-test — pre-existing, unrelated to #447, and currently
  masking any new failure a future run introduces in that file.
- `docs/agents/engine-config.json` does not exist, though every crew plan in this work area
  (g1's, g2's) names it as `config_ref`. The engine silently accepts the dangling reference.

## Map Impact
- **Structural anchors touched:** new module `scripts/verify_episode_captured.py` (script
  level) — the episode store's first WRITE-side gate; `scripts/apply_episode_delta.py`
  `store_root()` (function level) — comment only.
- **Capabilities added:** "a run must leave an episode behind" is now machine-checkable, at
  two strengths (feedback: captured; archive: captured **and** tracked by git).
- **Constraints touched:** the valve — episodes are a record, not a playbook — is now enforced
  by a test with its own red proof rather than by prose. `episodes/README.md`'s
  "a missing directory is refused, not answered" now has a second implementer.
- **Decision candidates:** exit-code split (1 blocked / 2 refused) — decided within latitude,
  see Assumptions. The `--store-root` default on an installed copy is an open decision that
  g3 must close.
- **Trust limitations:** the gate deliberately has no view of `retired/`.

## Workflow Feedback
- **Handoff gaps:** (a) **test mode was never named** — the template requires
  `test-first | test-after | evidence-only | none` and the handoff instead implies it through
  "prove the valve, do not assert it". I read it as test-first. (b) The required refusal exit
  was specified only as "non-zero", so the 1-vs-2 split was mine to invent; a handoff that
  says which code a spine will branch on would remove the guess. (c) The evidence list gave
  `--store-root episodes` (relative) for the feedback phase but never for `--phase archive`,
  which is precisely where the relative path broke — the missing fifth command is the one that
  would have caught the defect at m3 instead of m6.
- **Context rediscovered:** the delta JSON shape required to seed a temp store through
  `apply_episode_delta.py` (five mandatory `agent_supplied` kinds, exact mechanical field
  allowlist, writer-assigned ids). I read it out of the validator. A pointer to
  `tests/test_episode_store.py`'s seeding helpers would have saved the dig.
- **Instructions improvised around:** the implementer template assumes one TDD red per plan
  item, but three of my slices were implemented in the same file-creation as the first. Rather
  than fake a red, I used the repo's own mutation discipline (`CREW_CONTEXT.md`
  §Verification Discipline) and attested `c1` with the mutation transcript. The template does
  not describe that substitution; the project doc does.
- **Proof-of-life:** the skill requires reporting one as soon as I start, but this dispatch's
  team roster lists my own name as the Commander's, so there was no distinct parent to message
  without guessing. I skipped it rather than send to an unrelated agent.
- **What would have made this easier:** one line in the handoff naming the test mode and the
  refusal exit code, and one evidence command exercising `--phase archive` against the real
  store with a relative `--store-root`.

## Return status
`complete`
