# Implementation Result

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3` — `finish_work` composition + dispose + CLI (of 3 gates; g1 shipped verify/close primitives, g2 shipped reap + child-plan release, both reviewed and integrated).

## Completed slice
Added `finish_work` and `open_pr` to `scripts/spine_lifecycle.py`, composing g1's `done_refusal`/`_advance_and_release` and g2's `_release_child_plans`/`force_reap` with the existing, unmodified `close_work`, in the exact order the handoff's part (a) fixes: verify → release children → release the top-level lease → reap → archive → push → (optional) open a PR. Added `scripts/spine_done_cli.py`, a thin CLI wrapping `finish_work` — the reachable-today "one door verb" ahead of `mcp_spine_server.py`'s rewrite. Added 15 tests to `tests/test_spine_lifecycle.py` covering every refusal stage, the composition order, the #552 lease-proof end-to-end scenario, `open_pr`'s off-by-default/`--body-file` contract, and two fresh-process CLI smoke runs.

## Scope
**Files changed:**
- `scripts/spine_lifecycle.py` (+602 lines: `import tempfile`, `finish_work`, `open_pr`)
- `tests/test_spine_lifecycle.py` (+1280 lines: `_census_active_leases`, `TestFinishWorkRefusals`, `TestFinishWorkCompositionOrder`, `TestFinishWorkLeaseProofEndToEnd`, `TestOpenPr`, `TestSpineDoneCli`)
- `scripts/spine_done_cli.py` (new, 78 lines)

**Specific exclusions touched:** no — `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py` all show an empty `git diff --stat` (evidence below). `done_refusal`, `_engine_call`, `_advance_and_release`, `force_reap`, `_release_child_plans`, `close_work`/`closeout_refusal` were composed, never modified — confirmed by re-running the full pre-existing 104-test suite unchanged and green throughout.

## Behavior changed
Yes. Before this gate there was no single call that closed a run out — an agent had to hand-sequence `_release_child_plans` → `_advance_and_release` → `force_reap` → `close_work` → `git push` itself, in the right order, with no CLI door at all. `finish_work`/`spine_done_cli.py` make that one call (or one CLI invocation), refusing cleanly (never raising) when the run isn't ready, and the #552 defect this whole gate exists to close — a stale binding-store entry left behind because reap ran before children released — is now provably closed by `TestFinishWorkLeaseProofEndToEnd`.

## Map Impact
- **Structural anchors touched:** `scripts/spine_lifecycle.py` — `finish_work` (composition, new) and `open_pr` (new) appended after `_release_child_plans` (:798-932, g2, unmodified). `scripts/spine_done_cli.py` — new file, thin CLI, imports `spine_lifecycle` only.
- **Capabilities added/changed/affected:** capability:mechanical-closeout-one-verb — #574's full contract (steps 1-5) is now reachable via one function call (`finish_work`) and one CLI invocation (`spine_done_cli.py`), not three gate-by-gate primitives an agent must sequence itself.
- **Constraints/assumptions touched:** `decision:pr-opening-question-is-not-yours` — honored as specified: `open_pr` ships as an independently-callable helper, `finish_work(open_pr=False)` by default, floated rather than ruled. `decision:new-rot-first-old-rot-maybe` — untouched; `finish_work` stops new stale leases from accruing on a `finish_work`-driven closeout, and does not attempt to sweep the 41 pre-existing stale leases measured separately in `RETURN.md`.
- **Claims/evidence produced:** `TestFinishWorkLeaseProofEndToEnd` is the concrete, reproducible proof of the launch order's Return Shape item 5 — 2 active leases (parent + declared child) collapse to 0 after one `finish_work` call, and the archive contains the child plan file with `engine_session.status == "released"`.
- **Trust limitations / drift found:** none beyond the signature gap noted in Workflow Feedback below — g1's warning (g2-implementer-result.md) that `release` is not a `MUTATING_VERBS` member and produces no journal entry still holds here: `finish_work`'s own `_advance_and_release`/`_release_child_plans` calls carry the same limitation, and no test in this gate assumes journal coverage for a release.
- **Triage candidates:** none raised — sweeping the 41 pre-existing stale leases remains explicitly out of scope per the handoff's own Decision anchors.

## Test mode
**Required:** test-after (same convention as g1/g2).
**Satisfied:** yes — every behavior change (`finish_work`'s six composed steps, `open_pr`, the CLI) has a passing test written against it; no red step was required by the handoff.

## Evidence

### 1. THE #552 lease-proof end-to-end test (load-bearing) — test body

```python
class TestFinishWorkLeaseProofEndToEnd:
    """THE #552 lease-proof end-to-end test -- this gate's actual reason to
    exist (launch order Return Shape item 5)."""

    def test_two_active_leases_become_zero_and_child_lands_in_archive(self, repo):
        work_id = "g3-e2e"
        work_dir = repo / ".agent-work" / work_id
        child_rel = "child-plan.json"
        parent_session = "constellation/g3-e2e/implementer"

        # Child: a real single-gate plan, already terminal (complete), with
        # its OWN lease still ACTIVE -- finish_work is what releases it.
        _write_json(work_dir / child_rel, _leased_plan("child-session-1"))

        # Parent: a real single-gate spine whose gate's postcondition is
        # satisfiable (in-progress, satisfied=True) but not yet advanced,
        # declaring the child via child_checklist, with its OWN lease active.
        parent_spine = _g1_spine(gate_status="in-progress", satisfied=True)
        parent_spine["work_id"] = work_id
        parent_spine["tasks"]["m1"]["child_checklist"] = child_rel
        parent_spine["engine_session"]["session_id"] = parent_session
        spine_path = _write_json(work_dir / "spine.json", parent_spine)

        # A real work area shape beside the spine (a tracked file, an empty
        # dir) -- close_work's own convention, exercised end to end here too.
        (work_dir / "crew-handoffs").mkdir(parents=True, exist_ok=True)
        (work_dir / "crew-handoffs" / "note.md").write_text("hi\n", encoding="utf-8", newline="\n")
        (work_dir / "evidence").mkdir(parents=True, exist_ok=True)

        agent_work_root = repo / ".agent-work"
        active_before = _census_active_leases(agent_work_root)
        assert active_before == 2, "fixture precondition: parent + child both active"

        today = "2026-08-16"
        result = sl.finish_work(
            spine_path, root=repo, session_id=parent_session, today=today,
            tree_clean=True, episodes_captured=True, push=False,
        )
        assert result["ok"] is True, result
        assert result["child_plans_released"], result

        active_after = _census_active_leases(agent_work_root)
        assert active_after == 0, "every lease must be released before finish_work returns"

        archive_dir = repo / ".agent-work" / "archive" / f"{today}-{work_id}"
        assert archive_dir.is_dir()
        archived_child = archive_dir / child_rel
        assert archived_child.is_file(), sorted(p.name for p in archive_dir.rglob("*"))
        assert json.loads(archived_child.read_text())["engine_session"]["status"] == "released"
```

`_census_active_leases` mirrors `_active_engine_session_spine`'s own structural scan predicate (any `*.json` under a root, any depth, whose `engine_session.status == "active"`), generalized to COUNT every match instead of returning the first.

Passing output:

```
$ PYTHONIOENCODING=utf-8 py -m pytest tests/test_spine_lifecycle.py -q -k TestFinishWorkLeaseProofEndToEnd
collected 119 items / 118 deselected / 1 selected
tests/test_spine_lifecycle.py .                                          [100%]
1 passed, 118 deselected in 0.07s
```

### 2. Composition-order test (load-bearing)

```python
class TestFinishWorkCompositionOrder:
    def test_children_released_then_top_level_release_then_reap_then_archive(self, tmp_path):
        spine_path = _write_json(tmp_path / ".agent-work" / "g3-order" / "spine.json", {})
        calls: list[str] = []

        def fake_release_children(*args, **kwargs):
            calls.append("release_child_plans")
            return {"released": [], "unclaimed_active": []}

        def fake_advance_and_release(*args, **kwargs):
            calls.append("advance_and_release")
            return {"ok": True, "output": "ok"}

        def fake_force_reap(*args, **kwargs):
            calls.append("force_reap")
            return {"reaped": True}

        def fake_close_work(*args, **kwargs):
            calls.append("close_work")
            return {"work_id": "g3-order", "branch": "b", "head": "h", "archive": "a"}

        real = (sl._release_child_plans, sl._advance_and_release, sl.force_reap, sl.close_work)
        sl._release_child_plans = fake_release_children
        sl._advance_and_release = fake_advance_and_release
        sl.force_reap = fake_force_reap
        sl.close_work = fake_close_work
        try:
            result = sl.finish_work(
                spine_path, root=tmp_path, session_id="s1", today="2026-08-16",
                tree_clean=True, episodes_captured=True, push=False,
            )
        finally:
            sl._release_child_plans, sl._advance_and_release, sl.force_reap, sl.close_work = real

        assert result["ok"] is True, result
        assert calls == [
            "release_child_plans", "advance_and_release", "force_reap", "close_work",
        ], calls
```

Passing output: `1 passed, 118 deselected` (`-k TestFinishWorkCompositionOrder`).

### 3. Fresh-process CLI smoke run

Two forms of evidence, per the handoff's requirement that this run through a fresh process, not an in-process import.

**(a) `TestSpineDoneCli`** in `tests/test_spine_lifecycle.py` invokes `subprocess.run(["python3", CLI_PATH, ...])` against a `tmp_path`-rooted `repo` fixture — an ok/exit-0 path and a refusal/exit-1 path:

```
$ PYTHONIOENCODING=utf-8 py -m pytest tests/test_spine_lifecycle.py -q -k TestSpineDoneCli -v
collected 119 items / 116 deselected / 3 selected
tests/test_spine_lifecycle.py ...                                        [100%]
3 passed, 116 deselected in 0.12s
```

**(b) A standalone manual run**, outside pytest entirely, against a throwaway `mktemp -d` git repo (never this worktree's own `.agent-work`):

```
$ PYTHONIOENCODING=utf-8 python3 scripts/spine_done_cli.py \
    --file .agent-work/smoke-fixture/spine.json --root "$TMPD/repo" \
    --session-id smoke-session --today 2026-08-16 --tree-clean --episodes-captured --no-push
{
  "ok": true,
  "work_id": "smoke-fixture",
  "branch": "main",
  "head": "99ede77cee55bbb545b292f1b90d671ef112e6c0",
  "archive": "/tmp/tmp.ndhl8e8lWZ/repo/.agent-work/archive/2026-08-16-smoke-fixture",
  "pushed": false,
  "push_error": null,
  "pr": null,
  "child_plans_released": [],
  "unclaimed_active": [],
  "reap": {}
}
exit=0
```
`find .agent-work/archive` confirmed `spine.json` and `spine.json.journal` both moved under the archive directory.

### 4. Full suite, pre/post counts

```
$ PYTHONIOENCODING=utf-8 py -m pytest tests/test_spine_lifecycle.py -q
........................................................................ [ 60%]
...............................................                          [100%]
119 passed in 0.67s
```

Pre-change: 104. Post-change: 119 (+15: 5 `TestFinishWorkRefusals`, 1 `TestFinishWorkCompositionOrder`, 1 `TestFinishWorkLeaseProofEndToEnd`, 5 `TestOpenPr`, 3 `TestSpineDoneCli`).

**Result:** pass.

## TDD evidence, if required
Not required — test mode is test-after (matching g1/g2's convention, confirmed against the handoff's Test Mode field). No red step was written as a manual attest.

## Docs/contracts touched
None. `finish_work`'s and `open_pr`'s docstrings are the only new "contract" text, and they live beside the code they describe in `scripts/spine_lifecycle.py`; no `LIFECYCLE_CONTRACT.md` edit was needed or made (the frozen contract's sections 2-4 cover `open_work`/`close_work`, both unmodified here).

## Assumptions
- **`tree_clean`/`episodes_captured` added to `finish_work`'s signature.** The handoff's headline signature line for `finish_work` (part (a)) does not list `tree_clean`/`episodes_captured`, but step 2 of the same section calls `done_refusal(spine, tree_clean=<caller-supplied>, episodes_captured=<caller-supplied>)`, and the CLI section explicitly names `--tree-clean`/`--episodes-captured` as flags the CLI must collect and pass through. There is no other place for "caller-supplied" to come from, so I added `tree_clean: bool, episodes_captured: bool` as required keyword parameters. Treated as a signature-line omission, not a design decision to make independently — flagged in Workflow Feedback below rather than silently resolved.
- **`open_pr` name collision inside `finish_work`.** `finish_work`'s own `open_pr: bool` parameter shadows the module-level `open_pr` function for the whole function body — this is the exact signature the handoff specifies (`open_pr=False` as a bool kwarg, with a same-named helper function defined separately in part (b)). Resolved by capturing the function via `globals()["open_pr"]` at the top of `finish_work`, which reads the module namespace directly and is unaffected by the local parameter's shadowing. Documented inline at the capture site.
- **`push_error` key added beyond the handoff's exact success-return list.** The handoff's Success Return names `pushed: bool` but also says a push failure reports "plus the git error text" — there is no named key for that text in the literal list, so I added `push_error: str | None` (populated only when `push=True` and the push failed) as an additive key, not a substitution for any named one.
- **CLI `--tree-clean` design.** Implemented as a tri-state pair (`--tree-clean` / `--tree-dirty`, default `None` → auto-detect via `git status --porcelain`) rather than a single flag, since a single `store_true` flag cannot express "explicitly dirty" as distinct from "unspecified, auto-detect."

## Stop conditions hit
None. Allowed scope was not exceeded; no fenced file was touched; the #552 lease-proof test was constructible exactly as specified; all required evidence was producible; no decision outside my authority was needed (the PR-opening question was implemented per the already-decided default, not re-litigated).

## Out-of-scope observations
None beyond what the handoff's own Decision anchors already scope out (the 41 pre-existing stale leases, `decision:new-rot-first-old-rot-maybe`).

## Workflow Feedback

- **Handoff gaps:** `finish_work`'s headline signature (part (a)) omits `tree_clean`/`episodes_captured`, even though step 2 of the very same section and the CLI section both require them as caller-supplied inputs. A reader who took the signature line literally (rather than reading the whole composition) would have no way to satisfy step 2. I resolved it by adding both as required keyword parameters — see Assumptions. This should be corrected in the source contract (`docs/agents/... #574` or wherever this handoff was drafted from) before another gate is drafted from the same template.
- **Context rediscovered:** none — g1/g2's docstrings and the prior implementer results (`g2-implementer-result.md`'s note that `release` is not journaled) were sufficient; no additional digging was needed beyond reading the actual current source as instructed.
- **Instructions improvised around:** the `open_pr` bool-parameter/function-name collision inside `finish_work` isn't called out anywhere in the handoff as a hazard, even though the exact signature given (`open_pr=False` alongside a same-named helper `open_pr(...)`) makes it unavoidable in Python. I used `globals()["open_pr"]` to route around the shadowing; a future handoff reusing this pattern should name the collision explicitly so the implementer doesn't have to discover it by writing the function and hitting `TypeError: 'bool' object is not callable`.
- **What would have made this easier:** naming the `tree_clean`/`episodes_captured` signature gap and the `open_pr` shadowing hazard explicitly in the handoff (both are mechanical facts about the exact signature given, not judgment calls) would have saved the time spent confirming each was a real gap rather than something I was missing.

## Return status
`complete`
