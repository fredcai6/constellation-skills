# RESULT — w2-reindex

## Verdict

**Delivered.** A self-install-only git pre-commit hook makes `map/INDEX.md` and `map/ids.jsonl`
correct by construction. All three `execute.json` gates closed with independently-verified
`APPROVE` evidence from 5 real dispatched crews. Full local suite green: **3656 passed, 6 skipped,
0 failed**. Branch `epic-569/w2-reindex` pushed; **PR #657** open against `main`. Spine `w2-reindex`
closed via `spine_close` (`ok: true`); work area archived to
`.agent-work/archive/2026-08-22-w2-reindex`.

**One integration-time issue for the Admiral**: `main` advanced past this branch's base
(`9d5aac6d` → `305b00b3`, merge of PR #652) while this run was in progress. `gh pr view 657` now
reports `mergeable: CONFLICTING`. Not investigated further here — conflict resolution/rebase at
merge time is the Admiral's call, not something in this Commander's latitude to resolve
unilaterally. `map/INDEX.md` is a strong candidate for at least part of the conflict, since its
content is derived from the full corpus and both branches likely touched Python files.

## Alternatives pass and why the loser lost

Two candidates, dispatched in parallel, each under one named distinct constraint (single pass,
N=2 — a fairly-easy bounded-mechanism call, not architecture-touching at corpus scale, so a panel
was judged unnecessary):

- **smallest-diff**: skip the rebuild+stage entirely whenever any tracked path other than the two
  map files shows worktree-vs-index divergence (a `git status --porcelain` safety check). Correct
  and minimal, but only *usually* correct by construction — it silently no-ops whenever the author
  has any unrelated unstaged edit sitting in the tree, a common state during real development, not
  an edge case.
- **most-testable** (winner): build from an **index snapshot** (`git write-tree` → `git
  commit-tree` → `git worktree add --detach`) so the build input is provably the tree about to be
  committed, correct on every commit shape regardless of what else is dirty.

**most-testable won** because the mission's own framing — "so the index is correct by
construction and nobody discovers staleness after a merge" — is not fully satisfied by a mechanism
that silently retreats whenever anything else is dirty. The cost most-testable pays (worktree
materialization machinery) is git-native, not a hand-rolled staleness detector, so the
"smallest-diff" objection to it is weaker than it first appears.

Full comparison, framing block, and untaken-road record: `PLAN_ALTERNATIVES.md`.

## Cold critic and the resolved gaps

A cold critic (no authoring context, given only the mission frame and the converged plan) found 5
**blocking** gaps in the chosen mechanism's operational specification before any code was written:
shared-hooks-directory blast radius across this repo's own sibling worktrees, concurrent-invocation
races on `git worktree add`, no timeout (fail-open doesn't cover a hang), an unspecified copy-back
step from the ephemeral snapshot worktree to the real index, and a truth-source divergence with the
pre-existing freshness test on partial-hunk commits. All 5 were resolved with concrete, git-native
fixes pinned directly into `execute.json`'s gate constraints (unique `tempfile.mkdtemp()` worktree
paths, per-subprocess timeouts, plain-file-I/O copy-back, a shared-`.git` worktree test topology
requirement, a full-suite-green sequencing fix) rather than left for an implementing crew to
invent. Full findings and disposition: `PLAN_CRITIC.md`.

## Evidence

- **Unit** (`tests/test_code_map_precommit.py`, 13 tests): fresh/no-op, stale/rebuild-and-stage,
  both partial-commit shapes, unrelated-dirty-file audit, concurrent-invocation, forced-timeout,
  forced-exception, worktree-run-time-resolution.
- **Installer wiring** (`tests/test_install_constellation.py::GitPreCommitHookWiringTests`, 14
  tests): default no-op, explicit wiring, idempotent, refuse-to-clobber, `--dry-run`, worktree case
  (verified against this actual checkout's real shared hooks dir), self-install-only.
- **Real end-to-end** (`tests/test_code_map_precommit_e2e.py`, 7 test methods covering 8 numbered
  cases): red proof pinned to the shipped SHA, real CLI install + green proof, both partial-commit
  shapes for real, unrelated-dirty-file survives untouched, second-worktree case (installed from
  one worktree, fires on a commit from a second sharing the same `.git`, honestly exercising this
  repo's own real topology), timing.
- **Red-proof pinned SHA**: `9d5aac6d` (this branch's base at the time gate 3 ran) — case 1 confirms
  `MapTreeFreshnessTests` fails without the hook installed, exactly as it does today.
- **Reviewers independently reproduced, not trusted**: g1's reviewer patched a scratch copy to use
  a fixed worktree path and proved the unique-tempfile guard is genuinely load-bearing (it
  collides without it); g3's reviewer independently reproduced both the red proof and the
  second-worktree case by hand outside the test file.
- **Full local suite**: `3656 passed, 6 skipped, 0 failed, 1275 subtests passed` — re-run and
  confirmed independently by this Commander, not only by the dispatched crews.

## Where the new checks run, and proof they can fail there

- `tests/test_code_map_precommit.py`, `tests/test_code_map_precommit_e2e.py`, and
  `GitPreCommitHookWiringTests` in `tests/test_install_constellation.py` all run as ordinary pytest
  tests, collected by `python -m pytest -q` (the local suite / CI's `pytest tests/ -q`). Each
  contains real assertions against real scratch-git behavior; a regression to the shipped mechanism
  fails these tests, not silently passes them.
- `tests/test_code_map.py::MapTreeFreshnessTests` is unmodified — proof it stays live: it fails in
  `test_code_map_precommit_e2e.py`'s case 1 (red proof, hook not installed) and is confirmed to
  pass afterward (case 3, green proof) — the same test both fails and passes depending on hook
  presence, which is direct proof it is still checking something real.
- The pre-commit hook itself is not a new *blocking* check on any existing gate — it is an
  automation layer in front of the pre-existing `MapTreeFreshnessTests` backstop, per the launch
  order's own framing (`decision:regenerate-and-stage-silently`). No new report-only or
  promotion-trigger machinery was needed.

## Map impact

`map/INDEX.md` was rebuilt once during this run (`python -m scripts.code_map build --root .`, 6
lines changed, `map/ids.jsonl` unchanged) to fix a pre-existing staleness gate 3's own regression
check surfaced — this repo's own tracked-file edits from gate 2 had gone unrebuilt because the
mechanism this mission built could not yet fire (no real commit had landed on this branch). This is
the mission's own subject matter recurring inside its own execution, not a defect in the shipped
code — see episode `w2-reindex-004`. `docs/agents/AGENT_GUIDE.md`'s `map/` row was updated to note
the new automatic path alongside the existing manual build instruction (direct reconciliation — no
packet map exists for this repo; `docs/architecture` is empty).

## Triage candidates

Three, all **recommend-and-defer** (recorded as episodes, zero issues filed — filing is the
disfavoured exit per the launch order's standing ruling, and none of these three meets the "high
certainty run impact that can't be immediately fixed" bar):

1. `scripts/code_map/discovery.py:tracked_python_files`'s `git ls-files` subprocess call has no
   `timeout=`. Out of this mission's fenced scope (`discovery.py` was explicitly read-only for gate
   1). Minor hardening candidate.
2. A recurring dispatch-wiring anomaly: all 5 `--spine`-less `cli`-backend crews this run (g1/g2
   implement+review, g3-review) reported their inherited `SPINE_FILE`/`SPINE_SESSION` resolving
   toward this Commander's own bound spine rather than being absent. Every crew self-corrected
   safely (drove its own scratch checklist via `checklist_engine.py`'s CLI, never touched the
   parent spine) — zero actual impact, confirmed by re-checking `spine_status` after every
   dispatch. A `run_crew.py`/door-binding question, not this mission's to fix. Recorded as episode
   `w2-reindex-002`.
3. Fowler `long-parameter-list` flag on `install_constellation.py`'s `main()` (now 9 keyword-only
   params). Non-blocking; worth a config-object refactor only if a third `wire_X`/`X_path` pair is
   ever added.

## Workflow feedback — where this order was underspecified

- **Container-gate closure under a HARD context-band trip.** The engine's generic
  "attach-refresh-request → start → close-this-gate → stop" template assumes every gate is
  closable in one shot. `execute`'s own `c1` ("every gate closed with integrated evidence") cannot
  be honestly attested without driving the entire child `execute.json` checklist first — attempting
  to force-close it on the templated instruction alone would have meant either a fabricated
  attestation or a premature stop mid-mission. The launch order's own Stop Conditions section
  ("do not read a HARD advisory as licence to advance and hand off on turn one") and the Stop
  hook's explicit override language resolved this correctly, but a Commander reading only the
  generic engine advisory in isolation could plausibly have stopped after gate `plan` believing
  that was the sanctioned exit. Worth naming as a genuine engine-doctrine gap: the advisory text
  does not distinguish a leaf gate from a container gate.
- **Child-checklist mechanics were not named in the top-level spine's own `execute` imperative.**
  Driving `g1-implement` required first discovering, unaided, that the parent door does not resolve
  a child `execute.json` task id directly and that `spine_bind` is the required mechanism
  (`checklist-engine.md`'s own text, not the spine's `execute` imperative). This is documented
  doctrine, correctly found, but cost real time to locate.
- **The launch order's decision-pressure items were correctly left open** (staleness-detection
  strategy, hook-script shape) and both were resolved and recorded explicitly in `MISSION_FRAME.md`
  rather than left inferable — this worked as intended, not a gap.
- **5 crew Workflow Feedback items harvested**, none requiring action this run beyond what's
  already folded into the episodes and the two accepted doc/wording notes named in the feedback
  step's own DIGEST.

## Episodes recorded

Four, under `episodes/active/`: `w2-reindex-001` (the partial-commit-hazard investigation and cold
critic findings), `w2-reindex-002` (the recurring `spine: null` dispatch anomaly),
`w2-reindex-003` (g3-implement's attempt-1 wait-by-ending-turn crew death, recovered via
abandon+relaunch), `w2-reindex-004` (the mission's own subject matter — a stale map — surfacing
inside its own execution).
