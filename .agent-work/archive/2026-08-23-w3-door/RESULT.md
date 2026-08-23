# RESULT — w3-door

## 1. Verdict

Delivered exactly the LAUNCH_ORDER Mission. `_crew_door_env` in `scripts/run_crew.py` now
actively **clears** `SPINE_FILE` and `SPINE_SESSION` together when `spine is None`, instead of
leaving the dispatching process's ambient pair inherited. A crew dispatched without `--spine`
now gets **no door**, not its dispatcher's. Both docstrings that asserted inheritance was the
documented-safe behaviour (`_crew_door_env`'s own, and `crew_env`'s) were corrected in the same
change, per the launch order's non-optional instruction. `crew_env` itself is unchanged — its
generic "leave inherited when omitted" contract stays intact for any other direct caller (none
exist in production code, confirmed by repo-wide grep).

Honest-Null clause did not trigger: no caller was found that legitimately depends on the
inherited pair surviving through `_crew_door_env`.

Shipped across two commits on `epic-569/w3-door`:
- `e1180197` — the implementation (scripts/run_crew.py + tests/test_crew_launcher.py), reviewed
  and APPROVEd.
- `16d6f631` — a map/INDEX.md rebuild, committed by the Commander at `g1-integrate` after the
  full-suite gate surfaced staleness introduced by the new test (see Discrepancy below).

## 2. Evidence

- **Live defect confirmed at base** (commit `135c34eb`, matching LAUNCH_ORDER's stated base):
  `_crew_door_env`'s `spine is None` branch called `crew_env(parent=..., scratch_dir=...)` with
  no `spine_file`/`spine_session` args, and `crew_env` only assigns those keys when the arg
  `is not None` — omitted means "leave whatever's in `dict(os.environ)` untouched," i.e. the
  dispatching process's own ambient pair.
- **Only two call sites of `_crew_door_env`** in production code: `CliBackend.dispatch` (line
  ~1946) and `CliBackend.resume` (line ~2033). `crew_env` itself has no other production caller
  (grepped all `*.py` excluding tests and `.agent-work` archive snapshots).
- **decision:clear-both-or-neither** — verified: both `env.pop("SPINE_FILE", None)` and
  `env.pop("SPINE_SESSION", None)` are called together, no code path clears one alone.
- **decision:verify-against-a-real-child** — the reviewer independently reproduced this against
  a genuinely spawned OS subprocess (a fake `claude` launcher, non-empty ambient
  `SPINE_FILE`/`SPINE_SESSION`), not just a dict-shape unit test — per `g1-reviewer-result.md`.
- **Test suite, this lane's file only:**
  `tests/test_crew_launcher.py::DispatchDoorBindingTests` — 262/262 passed, including the
  renamed/rewritten `test_dispatch_without_spine_gets_no_door` (was
  `test_dispatch_without_spine_leaves_ambient_pair_untouched`) and a new `resume()`-path
  counterpart, both asserting `SPINE_FILE`/`SPINE_SESSION` are **absent** from the dispatched
  child's env when a door-bound parent dispatches/resumes with no `--spine`.
- **ParentLeaseHeartbeatTests** — `test_dispatch_skips_parent_heartbeat_in_shared_spine_case` and
  `test_resume_skips_parent_heartbeat_in_shared_spine_case` were rewritten: their old "shared
  spine, skip redundant heartbeat" scenario relied on the exact defect being removed (a
  `spine=None` child could coincidentally inherit the parent's exact pair). After the fix that
  scenario is structurally impossible, so the parent must always heartbeat its own lease in that
  case; both rewritten tests pass.

## 3. Suite result

Run **after** the final commit (`16d6f631`), verbatim:

```
$ git log -1 --format='%H %s'
16d6f631... epic-569 w3-door: rebuild map/INDEX.md for the new resume() no-door test

$ python3 -m pytest -q
.............................................. [ 77%]
........................................ [ 78%]
....................................................... [ 80%]
........................................................................ [ 81%]
.................................s................................... [ 83%]
........................................................................ [ 85%]
............................................. [ 86%]
.................................................s......................................................... [ 89%]
........................................................................ [ 91%]
........................................................................ [ 93%]
........................................................................ [ 95%]
.......................................................ss........... [ 97%]
....................................................... [ 98%]
...........................................                         [100%]
3730 passed, 9 skipped, 1277 subtests passed in 212.30s (0:03:32)
```

## 4. Map impact

**Yes, it fired and needed a manual finish.** The implementer's and reviewer's shipped revision
(`e1180197`) added one new test method
(`test_resume_via_cli_backend_with_no_stored_spine_gets_no_door`), which bumped
`tests/test_crew_launcher.py`'s tracked entity count by 1 (5723 → 5724) without a matching
`map/INDEX.md` rebuild. Both implementer and reviewer correctly flagged this as the one expected,
non-blocking pre-existing-style failure named in the handoff's Close Criteria and left it
unfixed, out of this lane's file ownership. No `.git/hooks/pre-commit` exists in this worktree
(checked directly), so no hook auto-regenerated it. At `g1-integrate` the Commander rebuilt it
via `python3 -m scripts.code_map build --root .` and committed the 6-line diff separately
(`16d6f631`); the full suite is green after.

## 5. Triage candidates

- **Map corpus degradation** (not fixed here, out of this lane's file-ownership scope). Per
  `.agent-work/w3-door/map-orientation.json`: mode `DEGRADED-UNPARSEABLE` —
  `docs/architecture/generated/map.json` parses but carries no citable `nodes[].id`;
  `docs/architecture/index.md` is absent; `docs/architecture` packets dir exists but is empty (0
  packets); `map/INDEX.md`/`map/ids.jsonl` carry no citable anchors for `scripts/run_crew.py`.
  Belongs to the map corpus owner / `w3-promote` track, same as the `validate_spine.py` defect the
  launch order already named as out of scope.
- **No pre-commit hook mechanizes `map/INDEX.md` regeneration in this worktree** — the launch
  order's Return Shape describes one as "now mechanized," but `.git/hooks/pre-commit` does not
  exist here, which is exactly how the staleness in §4 reached a shipped commit undetected.
  Recommend the map corpus owner confirm the hook is actually installed by
  `install_constellation.py` (or wherever it's meant to originate) rather than assumed present.
- **`validate_spine.py` fails on this spine's `init`/`reconcile`** — inherited from the shipped
  template per the launch order's own note; not this lane's defect, not fixed here.

Both were recorded via `spine_evidence attest triage.c1` as recommend-and-defer (no filing
sought or authorized — no human reachable this run).

## 6. Workflow feedback

- **The launch order was precise and load-bearing.** The Pre-Rulings (clear-both-or-neither,
  verify-against-a-real-child, don't-break-your-siblings) and the non-optional "edit both
  docstrings" instruction were each directly actionable without re-deriving intent, and the plan
  step's cold-critic pass (folded into a single `PLAN_CRITIC.md`) caught the `ParentLeaseHeartbeatTests`
  interaction *before* implementation — that gap would otherwise have surfaced only at review and
  forced a reopen, per commander-core.md's own warning about unenumerated file-ownership scope.
- **One real gap:** the launch order's Return Shape says a pre-commit hook "now mechanizes"
  `map/INDEX.md` freshness, framed as something to *report on*, not something a lane might have to
  *finish by hand*. In this worktree no such hook exists, so the mechanization claim was false for
  this run, and the Commander had to notice the pytest failure, diagnose it as a genuine staleness
  (not a pre-existing base-commit failure — bisected against `135c34eb` where the suite was
  reported clean), and do the rebuild+commit itself. A more accurate framing: "check whether a
  pre-commit hook exists in your worktree; if not, rebuild and commit `map/INDEX.md` yourself
  before the final suite run."
- **The engine's `mcp__spine__spine_bind` on a plain re-bind to an already-active parent spine
  derives a generic session string** (`constellation/w3-door`) instead of preserving the
  currently-held identity (`constellation/w3-door/commander/commander`), which then requires a
  `claim --force` takeover of your own lease immediately after rebinding back from a
  `child_checklist`. Cosmetically confusing (looked like a conflicting-session error) though
  harmless in practice — worth a one-line note in `checklist-engine.md` that re-binding to a
  spine you already hold the lease on may need a self-force-claim.

## 7. Pre-declared refresh comparison

- **Refresh-request count this session:** 0. No spine trip occurred; no `refresh-request` was
  written to `spine.json` (grepped: zero `REFRESH REQUESTED` occurrences).
- **Relaunch:** none needed. This is `attempt-2` (per this session's own dispatch identity) —
  the prior attempt's implement/review work (commits, handoffs, `g1-review/review.json`) was
  found already complete and durable on disk at session start; this session picked up at
  `g1-integrate`'s unmet `c1` (full suite at the shipped revision) and drove `execute` through
  `review` to completion without needing to redo implement or review.
- **Final `attempt` / `total_rework`:** no explicit `attempt`/`total_rework` counters exist at
  the top level of `spine.json` (checked directly — absent keys). Per-gate `rework_count` in
  `execute.json` is 0 for all four gates (`e0-context`, `g1-implement`, `g1-review`,
  `g1-integrate`) — no gate needed rework.
- **Reviewer's verdict and review rounds:** **APPROVE**, one round. `g1-reviewer-result.md`
  records a single dispatch that independently reproduced the full suite, bisected the one
  (pre-map-rebuild) failure, red/green-proved all 4 new/rewritten tests, ran its own
  real-dispatched-child spot-check, and verified the Fowler pass — no rework loop was triggered.

## PR

Branch `epic-569/w3-door` pushed; PR opened against `main`:
https://github.com/fredcai6/constellation-skills/pull/661. Server-side merge — **not merged**;
the Admiral owns integration.
