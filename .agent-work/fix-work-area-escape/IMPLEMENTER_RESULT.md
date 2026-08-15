# Implementation Result

## Assigned gate
`fix/work-area-escape` — human-direct handoff, no spine/engine gates required by the dispatcher.
Driven through my own gated plan at `.agent-work/fix-work-area-escape/IMPLEMENTER_PLAN.json`,
session `impl-fix-work-area-escape-1`.

## Completed slice
Both handoff tasks, as one coupled change: `episode_capture.manifest_root` no longer escapes the
work area it belongs to, and `agent_work_root.py`'s docstring no longer misdescribes `.agent-work/`
as gitignored/disposable.

## Scope

**Files changed:**
- `scripts/episode_capture.py` — `manifest_root()`: the unconditional `return base.parent` fallback
  now raises `ValueError` when `base_dir` has no `.agent-work` ancestor to anchor a guess to.
  Docstring extended to explain the refusal; the nested-strip explanation is unchanged.
- `scripts/agent_work_root.py` — module docstring, lines 6–9: dropped the false
  `(gitignored, disposable)` claim, states what's true instead.
- `tests/test_work_id_nesting.py` — two new tests in `ManifestRootNestingTests`: the escape
  refusal (RED before the fix) and a positive control confirming the legitimate scratch-spine
  fallback is untouched.
- `tests/test_episode_capture.py` — one new test in `FailSoft`: an end-to-end proof through the
  real seam (`emit_step_manifest`) that a `base_dir` outside any work area writes nothing at all,
  rather than escaping.
- `map/INDEX.md` — regenerated, entity counts only (3 new tests).

**Specific exclusions touched:** no. Verified: the four stray directories
(`.worktrees/s`, `/t`, `/probe`, and the `constellation-skills-wt` pair) were inspected read-only
for the open lead below and never written to. `durable_root`'s redirect semantics, the
active-epic-lease exception, `origin_worktree_refusal`, and the lexical-vs-git spine ownership
question are all untouched — confirmed by `git diff --stat` showing only the five files above.

## Behavior changed

Yes, one way, precisely scoped. `manifest_root(base_dir, work_id)`:
- **Unchanged**: the nested work-id strip (`epic-418-followon/commander-424` case) and the
  legitimate scratch-spine fallback (`base_dir` under `.agent-work` but not ending in its own
  work-id) — both keep the historical `base.parent` answer.
- **Changed**: when neither of those applies AND `base_dir` has no `.agent-work` component
  anywhere in its ancestry, the function now raises `ValueError` instead of silently returning
  `base.parent`. That fallback was the escape: handed a worktree root directly, it climbed OUT of
  the worktree into `.worktrees/`, a directory shared by every worktree in the repo — exactly the
  shape that produced the four stray directories on disk.

**A documented, narrow side effect on `emit_step_manifest`'s fail-soft contract.** Every other
crash path in that function leaves a failure stub (pinned by
`test_failsoft_an_arbitrary_producer_crash_leaves_a_stub_not_silence`). When `manifest_root` refuses
for the no-`.agent-work`-ancestor reason, `_write_failure_stub`'s own attempt to locate somewhere to
write the stub calls `manifest_root` again and is refused a second time — so this one case is total
silence (no manifest, no stub, `emit_step_manifest` returns `None`). This is deliberate: there is no
known work area to put even a failure record in, and writing one via the old unconditional
`base.parent` would just be the escape again, one level indirect. Covered by
`test_a_base_dir_outside_any_work_area_writes_nothing_at_all`, and called out explicitly in
`FINDINGS.md` rather than left implicit.

## Map Impact
- **Structural anchors touched:** `scripts.episode_capture:manifest_root` (function-level fix, same
  signature `manifest_root(base_dir, work_id=None) -> Path`, now with a raising branch) and
  `scripts.agent_work_root` module docstring (no code change). No new module, no new seam, no
  caller moves.
- **Capabilities added/changed/affected:** `manifest_root` gains a refusal path. Every real
  production caller (`checklist_engine.start`/`reopen` via `emit_step_manifest`) always passes a
  `base_dir` under `.agent-work`, so this is inert for shipped call sites; it only fires for a
  caller that composes the manifest tooling directly against a non-work-area path, which is the
  shape that produced the strays.
- **Constraints/assumptions touched:** honors the model in `HANDOFF.md` — a work area is
  transportable work in progress at `<root>/.worktrees/<slug>/.agent-work/<work-id>/`, tracked on
  that worktree's branch, not gitignored, not disposable. `agent_work_root.py`'s docstring was a
  standing violation of that model and had already fed a design proposal that would have broken it
  (per the handoff).
- **Decision candidates / resolved decisions:** the specific boundary chosen for "resolve with
  confidence" — `.agent-work` present anywhere in `base_dir`'s ancestry — was mine, within the
  handoff's "refuse loudly rather than silently guess" instruction. It was chosen because it is the
  one mechanical signature every real work area shares (per the handoff's own model), it exactly
  covers all three reproduced escape shapes (worktree root under both `.worktrees/` and
  `constellation-skills-wt/`), and it exactly preserves the one existing test that already
  legitimizes a non-matching fallback (`test_a_checklist_not_under_its_own_work_id_keeps_the_old_answer`).
- **Trust limitations / drift found:** none found beyond what's in `FINDINGS.md`.
- **Triage candidates:** none filed. The open lead (who invoked the tooling with `probe`/`s`/`t`)
  is recorded in `FINDINGS.md` as unresolved rather than filed as triage, since there is no further
  action available — the source worktree is gone and the manifest schema records no invoker
  identity.

## Test mode
**Required:** test-first (handoff: "Red before, green after").
**Satisfied:** yes.

## Evidence

### RED — fix reverted, tests present, real functions, no mocking
```
$ git stash push -- scripts/episode_capture.py scripts/agent_work_root.py
$ python -m pytest tests/test_work_id_nesting.py::ManifestRootNestingTests::test_a_worktree_root_with_no_agent_work_ancestor_refuses_rather_than_escapes tests/test_episode_capture.py::FailSoft::test_a_base_dir_outside_any_work_area_writes_nothing_at_all -q
...
>           self.assertIsNone(written)
E           AssertionError: PosixPath('/tmp/tmppbgtm8nk/.worktrees/probe/context/g1.json') is not None
2 failed in 0.06s
$ git stash pop
```
The failure **is** the escape, reproduced live: the real code wrote a manifest at
`.worktrees/probe/context/g1.json`, a sibling of the `.worktrees/epic-568-510` worktree it was
handed — the exact shape reported in the handoff.

### GREEN — fix applied
```
$ python -m pytest tests/test_work_id_nesting.py tests/test_episode_capture.py -q
....................................................... [ 93%]
....                                                                     [100%]
58 passed, 18 subtests passed in 1.08s
```
Also green: `tests/test_episode_fields.py`, `tests/test_episode_negative_control.py`,
`tests/test_install_constellation.py` (251 passed, 495 subtests passed).

### Nested work-id strip still resolves correctly
`ManifestRootNestingTests::test_nested_work_id_writes_beside_its_own_spine` (pre-existing,
unmodified) — `epic-418-followon/commander-424` resolves without doubling. Passing in the same run
above.

### Full suite, cache-clean, before and after

Baseline given in the handoff (main@`bbbf41f6`): **3000 passed, 6 skipped, 0 failed**.

First cache-clean run, taken with the fix applied but **before** committing and before regenerating
the map — caught two real, expected failures:
```
$ find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} + ; python -m pytest -q
4 failed, 3001 passed, 6 skipped, 1127 subtests passed in 118.47s
FAILED tests/test_code_map.py::...test_map_tree_freshness_root_index_matches_a_fresh_build
FAILED tests/test_context_determinism.py::RealCheckoutSkew::test_a_clean_checkout_differs_only_in_rev_never_in_shape (x2 subtests)
```
Both explained, not worked around: `map/INDEX.md` was stale relative to the source edit (expected —
map regen was still pending), and `RealCheckoutSkew` compares this working tree against a fresh
`git worktree add HEAD` checkout with only an `OVERLAY` allowlist copied over — `agent_work_root.py`
isn't in that allowlist, so an *uncommitted* change to a tracked file it reads shows up as skew
until committed. Regenerated the map and committed; re-ran cache-clean:
```
$ find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} + ; python -m pytest -q
3003 passed, 6 skipped, 1130 subtests passed in 120.95s
```
**3003 passed, 6 skipped, 0 failed** — the +3 over baseline is exactly the three new tests.

### Map
`map/INDEX.md` moved (entity-count deltas only, `+4571→4574` tests, `+41→43` in
`test_work_id_nesting`, `+40→41` in `test_episode_capture`) and was committed.

## TDD evidence, if required
- Failing test observed: yes — see RED above, captured live in this session.
- Passing test observed: yes — see GREEN above.
- Refactor while green: no.

## Docs/contracts touched
- `scripts/episode_capture.py`'s `manifest_root` docstring — extended, in scope (Task 1 explicitly
  required reading and preserving it, not skipping the update).
- `scripts/agent_work_root.py`'s module docstring — corrected, in scope (Task 2).

## Assumptions
- None beyond the boundary-choice decision recorded under Map Impact above.

## Stop conditions hit
- None. The refusal does not break any existing caller (verified: every production call site passes
  a `base_dir` under `.agent-work`; the one existing test with a non-matching-but-legitimate
  fallback stays under `.agent-work` and is unaffected). Nothing in the OUT list was touched. The
  nested strip is preserved and tested.

## Workflow Feedback
- No handoff gaps. Task, intent, scope, exclusions, evidence, test mode, and stop conditions were
  all present and unambiguous; the reproduction table and the docstring pointer made the fix
  boundary decidable without guessing.
- One thing worth naming for future handoffs of this shape: fixing a root-resolution function that
  a fail-soft seam calls twice (once for the real write, once for the failure stub) has a
  second-order effect on that seam's own invariants (see "Behavior changed" above). Worth flagging
  explicitly in a handoff when the function under repair sits inside a fail-soft wrapper, so the
  implementer knows to check for exactly this.

## Return status
`complete`. Fenced from push, PR, and merge — neither attempted. Three local commits:
`0488de86` (the fix + tests + docstring + map), plus two more recording the engine-driven work area
itself (`d698ed17`, `169193dd`).
