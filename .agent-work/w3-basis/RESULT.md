# RESULT — w3-basis

## 1. Verdict

Delivered. `CommanderSpineBasisFields` (`tests/test_checklist_engine.py`) now pins to the
**BLOB OID** of `skills/commander/templates/COMMANDER_SPINE.template.json`
(`git rev-parse HEAD:<path>`), not repo-wide `HEAD`, and **FAILs** (never skips) on drift, with
the re-verify path printed inline in the failure message. Both directions of the fix are proven
by a two-direction mutation battery run against an isolated `git clone --local` scratch copy.

Shipped as: commit `8691a40e` (the mission diff) plus 3 archive-phase commits
(`ded71631`, `7b34b096`, `920927f6`, `316965e0`, `0382b2e0` — the spine-close archive move — and
`ccc4220d`, a post-close fix for two suite failures the full-suite run surfaced) on branch
`epic-569/w3-basis`, PR [#659](https://github.com/fredcai6/constellation-skills/pull/659), open,
not merged (Admiral owns integration).

## 2. Evidence

**Granularity fix, both directions, measured at commit `8691a40e`** (the mission diff), reproduced
independently by the implementer, the reviewer, and this Commander:

```
$ python3 -m pytest tests/test_checklist_engine.py::CommanderSpineBasisFields -q -rs
.....                                                                 [100%]
5 passed, 3 subtests passed in 2.82s
```

RED direction — template mutated in an isolated `/tmp` clone (never the shared worktree):
```
AssertionError: CommanderSpineBasisFields' proof is stale: pinned to blob
6953ac90f2568890fddbe187ad5fc8dd095041dd of skills/commander/templates/COMMANDER_SPINE.template.json,
current blob is 0ae37ea6d8487b0da415651606315d5cfdc9f0ef -- the template changed since this
test's shape assumptions were verified (g1 dispatch). Re-verify EXPECTED_BASIS (and the rest of
this class) against the new template content, then re-pin by running:
    git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json
and pasting the result into PINNED_BLOB above.
3 failed in 0.39s
```

GREEN direction — unrelated file committed in the same isolated clone, template untouched:
```
3 passed, 3 subtests passed in 0.12s
```

`PINNED_BLOB` at ship time (`6953ac90f2568890fddbe187ad5fc8dd095041dd`) verified against
`git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json` at the current HEAD
of this worktree (`ccc4220d`): **matches**, re-measured just now, not stale against any
concurrent `w3-promote` edit.

`grep -n skipTest tests/test_checklist_engine.py` → exactly 1 hit, at line 1544, inside an
unrelated class (`CommanderSpineBasisFields` starts at line 8543) — confirmed at commit
`ccc4220d`. Zero `skipTest` remains in `CommanderSpineBasisFields`.

## 3. Suite result

`python3 -m pytest -q`, run **after** the final commit (`ccc4220d`), pasted verbatim:

```
$ git rev-parse HEAD
ccc4220d7693e8ce8f2e1cc8f495764e345746e0
$ python3 -m pytest -q
3734 passed, 6 skipped, 1280 subtests passed in 219.02s (0:03:39)
```

This is the **second** full-suite run this wave. The first, at commit `0382b2e0` (immediately
after `spine_close`), surfaced 3 failures this run's own diff caused and that a pre-commit hook
was supposed to catch but did not fire for on this worktree:

```
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
FAILED tests/test_episode_observations.py::RealStoreTests::test_the_real_store_is_clean_under_strict
FAILED tests/test_episode_observations.py::RealStoreTests::test_the_real_store_scan_actually_examined_the_records
3 failed, 3731 passed, 6 skipped, 1280 subtests passed in 217.93s (0:03:37)
```

Both were this run's own defects, fixed in commit `ccc4220d`, not pre-existing:
- `map/INDEX.md` was stale by exactly the 2 test methods this mission's mutation battery added
  (`tests.test_checklist_engine`: 735 → 737 entities) — rebuilt via
  `python -m scripts.code_map build --root .`.
- Three of this run's own episode assertions (`w3-basis-001.a5`, `w3-basis-002.a5`,
  `w3-basis-003.a4`) tripped `tests/test_episode_observations.py`'s imperative/second-person
  detector — restated (never hand-edited) via `apply_episode_delta.py`'s `restate-assertion` op;
  meaning unchanged, wording only (see commit `ccc4220d`'s message for the exact trigger in each).

The second run at `ccc4220d` (pasted above) is green: 0 failed.

## 4. Map impact

Map rebuild fired: `map/INDEX.md` was rebuilt (`python -m scripts.code_map build --root .`) and
committed at `ccc4220d`, correcting a staleness this run's own diff caused (2 new test methods).
The pre-commit hook the launch order says "now mechanizes this" did **not** fire on any of this
worktree's commits — a real gap, filed below as a triage candidate, not something this lane's
scope covers fixing.

Separately, `map/ids.jsonl` remains empty and `map/INDEX.md`'s own linked per-package packets
(e.g. `map/tests.test_checklist_engine/INDEX.md`) do not exist on disk — this is the pre-existing,
repo-wide `map_orient.py` DEGRADED-UNPARSEABLE condition discovered at `context` (see
`.agent-work/w3-basis/map-orientation.json`, now under
`.agent-work/archive/2026-08-23-w3-basis/`), unrelated to and unfixed by this run's rebuild
(`code_map build` regenerates `map/INDEX.md`'s entity counts, not the `docs/architecture`-shaped
packet tree or `ids.jsonl` that `map_orient.py` reads).

## 5. Triage candidates

1. **Repo map DEGRADED-UNPARSEABLE, repo-wide.** `map/INDEX.md` references per-package packets
   (e.g. `map/tests.test_checklist_engine/INDEX.md`) that do not exist on disk, and `map/ids.jsonl`
   is empty. Not this lane's scope to fix; blocks map-first planning for every future run until
   rebuilt. Recommend for whoever owns map/cartographer maintenance. Routed **recommend-and-defer**
   (no issue filed — issue-filing authority was not clearly within this lane's inherited latitude).
2. **Minor test-scaffolding duplication.** `test_mutation_battery_template_edit_fails_not_skips`
   and `test_mutation_battery_unrelated_commit_stays_green` share ~15-20 lines of near-identical
   isolated-clone scaffolding (Fowler `duplicated-code`, non-blocking). A shared `_isolated_clone()`
   helper could remove it once a second content-pinned test class exists (deferred per the
   plan-alternatives convergence's "one adapter is hypothetical, two is real" reasoning — see
   `PLAN_ALTERNATIVES.md`, now archived). Routed **recommend-and-defer**.
3. **The map-rebuild pre-commit hook did not fire on this worktree.** The launch order states a
   pre-commit hook "now mechanizes" the `map/INDEX.md` rebuild; it did not run on any of this run's
   commits (confirmed: the staleness this run introduced survived 5 commits and was only caught by
   the full-suite run, not by any commit-time gate). Worth investigating whether the hook is wired
   for this worktree/environment at all. Routed **recommend-and-defer**.

## 6. Workflow feedback

- **The MCP door only resolves against the top-level spine (`spine.json`), never a
  `child_checklist` file (`execute.json`).** `mcp__spine__spine_evidence` with `task_id=g1-implement`
  returned `REFUSED: no such item 'g1-implement'`. Driving `execute.json`'s own gates required the
  separate `scripts/checklist_engine.py` CLI directly (`python3 checklist_engine.py --file
  .agent-work/w3-basis/execute.json <verb> ...`), which commander-core.md's "Checklists you own"
  table does name as the driver for `execute.json`, but the launch order and the spine's own
  `execute` imperative text describe driving `execute.json` "gate by gate" without naming which
  tool surface does that — a first-time reader has to already know execute.json is not reachable
  through the same MCP tools before finding the CLI form. Suggest the `execute` step's imperative
  name the CLI invocation explicitly, the way it names `run_crew.py` and `recover_crews.py`.
- **`run_crew.py --verify-result` refuses a plain handoff-based crew's result with "no spine
  evidence and no --accept-mtime-only-risk given"** whenever the dispatch declared no `--spine`
  (the common case for a bounded implementer/reviewer task that drives no engine of its own). This
  is documented behavior (issue #432) but the refusal reads, on first encounter, as though the
  crew dispatch itself failed rather than as an expected two-step confirm-then-accept flow. A
  one-line addition to `crew-dispatch.md`'s existing `run_crew.py` section — "a handoff-only crew
  with no `--spine` will refuse `--verify-result` until you pass `--accept-mtime-only-risk` naming
  what you independently checked" — would remove the moment of "did dispatch fail?" uncertainty.
- **The context HARD-band advisory fired at every gate-begin (`execute`, `reconcile`, `triage`,
  `review`, `feedback`, `archive`) in a single long-running Commander session, each time before any
  real work at that step had happened.** The launch order's own pre-declared resolution (attach
  refresh-request, then start, then continue) worked cleanly every time and no relaunch was ever
  actually needed, but 6 refusals in one run for a mission this small suggests the HARD threshold
  (or its non-reset behavior across gates within one session) is tuned for a much shorter run than
  a full init-through-archive single-instance Commander pass. This is evidence for the launch
  order's own explicitly-requested refresh comparison (below), not a request to change anything
  unilaterally.
- **The archive step's own postcondition set (`c1` episode-captured, `c2`/`c2b` push+PR,
  `c4` git-change-policy) is satisfied by manual `git`/`gh` commands the imperative describes in
  prose but does not name as exact commands** (unlike `execute`'s imperative, which names
  `run_crew.py`/`recover_crews.py` explicitly). Worked fine here, but a first-time reader has to
  infer "push means `git push`" and "open the PR means `gh pr create`" rather than being told.
- **A gauge/telemetry file under `.agent-work/<work-id>/` updates on every mutating engine call**,
  which means "the tree is clean" is a moving target that must be re-verified and re-committed
  immediately before any check (including `spine_close` itself) that inspects `git status`. This
  cost several small "gauge snapshot" commits in this run's history. Not a defect exactly, but
  worth naming: a reader following "commit, then verify tree_clean" literally will hit this same
  churn.
- **What was NOT ambiguous:** the mission itself (blob-OID pin, fail-not-skip, mutation battery),
  the pre-rulings, the file-ownership fence, and the design-it-twice/critic sequence were all
  precisely specified and needed no interpretation. The mechanism-shape latitude the launch order
  explicitly delegated ("where the re-verify path lives") was exactly the right amount of freedom
  for a 2-candidate design-it-twice comparison to resolve cleanly.

## 7. Pre-declared refresh comparison

- **Refresh-request count:** 6 — attached at `execute` (why_ref `w-4`), `reconcile` (`w-5`),
  `triage` (`w-6`), `review` (`w-7`), `feedback` (`w-8`), `archive` (`w-9`).
- **Whether a relaunch actually happened:** No. This single Commander instance (session
  `constellation/w3-basis/commander/commander`, attempt-1) drove the entire spine from `init`
  through `spine_close`, per the launch order's explicit instruction not to read a HARD advisory
  as a hand-off instruction on turn one — at each refusal, the refresh-request was attached, `start`
  was retried (now unblocked), and the step's real work continued in the same turn.
- **Final `attempt` and `total_rework`:** `attempt-1`; `total_rework = 0` — no gate was reopened, no
  crew was sent back for rework, no BLOCK verdict was issued anywhere in this run.
- **Reviewer's verdict and review rounds:** `APPROVE`, 1 round. The g1-review dispatch returned
  APPROVE on its first pass, with every close criterion independently re-run (not just read) by
  the reviewer, and further independently spot-checked by this Commander before integrating.
