# REVIEW_RESULT — issue #440, gate g1b (ambiguity guard on the guessed rungs)

## Verdict: APPROVE

tc1 is closed, and the regression you were worried about does not reach any live shape. Two minor
findings, neither blocking. Survey at `crew/g1b-ambiguity/review.json` driven to consolidation
(11 checks: `r0`–`r6` plus appended `q1`–`q4`), Fowler pass at `crew/g1b-ambiguity/FOWLER_PASS.json`
(rail exit 0), lease released last.

Baseline `9d44aa6`; diff `scripts/hooks/spine_rail.py +57/-7`, `tests/test_spine_rail.py +156/-4`.

---

## 1. Is tc1 actually closed? YES.

I rebuilt my own g1 adversarial case from scratch rather than re-running the implementer's test
(`<scratchpad>/attack_g1b.py`): real `git init` + real `git worktree add`, both trees holding a valid
checklist at `.agent-work/shared/spine.json`, command carrying **no** `cd` and **no** `--worktree`,
hook driven in a **fresh subprocess**, nothing monkeypatched. I seeded the store with
`{"pre-existing": {}}` first, so "byte-unchanged" is a real comparison rather than empty-vs-empty.

```
main spine     : ...\main\.agent-work\shared\spine.json
worktree spine : ...\wt-0\.agent-work\shared\spine.json
store keys     : ['pre-existing']
BYTE-UNCHANGED : True
VERDICT        : TC1 CLOSED - bound nothing
```

Under g1 this exact case bound the main checkout's copy with `path_source: payload_cwd`. Also
confirmed: two disagreeing rung-4 roots bind nothing, and a single validating rung-4 root still binds
with `path_source: git_worktree`.

## 2. Did the guard overshoot into a regression? NOT ON ANY LIVE SHAPE — I tested your reading.

You asked me to test it rather than take it, so I measured it against the real trees
(`<scratchpad>/reach_g1b.py`, read-only). Method: for every registered worktree, intersect the
relative paths holding a **validating checklist** in the main checkout with those in that worktree,
keep only pairs that are **different files** — those are precisely the paths a relative-`--file` claim
now silences.

```
TOTAL colliding relative paths across all worktrees: 2693
Of those, LIVE (untracked in main => a real in-flight spine): 0
=> no in-flight claim shape is silenced by the guard on the real trees.
```

All 2693 are tracked, archived work areas that will never be claimed again (`epic-298`
harvest/pre/post runs, `explore-*` cycles, `scout-*`). And the two live spines, checked by name:

- `.agent-work/epic-418/spine.json` — **untracked**, present in **only** the main checkout
  (`git ls-files --error-unmatch` errors; a per-tree existence sweep finds it nowhere else).
- `.agent-work/issue-440-binding-cwd/execute.json` — present in **only** this worktree.

Neither the Admiral's claim nor this Commander's claim can be silenced. **Your reading holds.**

I also constructed both regression shapes directly instead of inferring them:

| shape | result |
|---|---|
| main-checkout agent, worktree holds **no** checklist at that path | **binds correctly**, `path_source: payload_cwd` — no regression |
| main-checkout agent, worktree **does** hold one (the silencing shape) | binds nothing — the deliberate trade |

And told-truth rungs are **not** silenced under a real two-tree collision — all three still bind the
worktree spine outright:

```
cd_target (msys) -> cd_target     OK (worktree)
worktree_opt     -> worktree_opt  OK (worktree)
absolute --file  -> absolute      OK (worktree)
```

Agreement is handled as you specified: with `cwd == project_dir`, rungs 3 and 5 resolve to the same
file and it binds, keeping the **earliest** rung's `path_source` (`payload_cwd`, not `project_dir`).
`release` still removes its own entry after the spine file is deleted.

## 3. The 4 deletions — STRENGTHENING, not relaxation.

`git diff --numstat 9d44aa6` → `tests/test_spine_rail.py  156  4`. Enumerating every `-` line confirms
all four sit in `test_git_probe_does_not_run_when_an_earlier_rung_answers`: two docstring lines
(replaced by a nine-line one) and two assertions.

```
- assert calls == [], "git probe ran on the common path"
+ assert calls == [str(proj)], "the guessed-rung scan must probe exactly once"

- assert calls == []
+ assert calls == [str(proj)]  # unchanged -- rung 0 added no probe of its own
```

Neither was loosened **in form** — both were and remain exact list equality; no `>=`, no `len()`
bound, no deletion. The first now pins **both** an exact call count of one **and** the exact
argument, which is strictly more than `== []` said about a call that occurs. The second still proves
rung 0 short-circuits, by asserting the list did **not** grow.

Crucially, I confirmed independently that the new assertions **describe reality rather than being
fitted to it** — my own `subprocess.run` spy shows the guessed-rung claim spawning exactly one
`['git','worktree','list','--porcelain']` and the absolute-`--file` claim adding none.

## 4. Never raises, probe bounded, off the told-truth path.

My 23 hostile payload shapes from the g1 review, re-run unchanged: **23 rows, 0 failures**, all
returned `{}` with no raise. `GIT_PROBE_TIMEOUT_SECONDS` still `2.0`; non-repo dir → `[]` in 0.029s;
nonexistent cwd → `[]` in 0.001s; `TimeoutExpired` → `[]`, `OSError` → `[]`, `MemoryError` → `[]`.

**But the "off the common path" property changed** — see finding 1.

---

## Findings

| # | Severity | Where | Finding |
|---|---|---|---|
| 1 | Minor (behaviour change, honestly documented) | `scripts/hooks/spine_rail.py` `_candidate_roots` / `resolve_spine_candidate` | The g1 close criterion *"the git probe is off the common path"* **no longer holds in its g1 form**. A plain rung-3 claim now spawns one `git worktree list --porcelain` where g1 spawned none — unavoidable, since a guess cannot be known unambiguous without consulting the later guesses. Told-truth rungs still never probe. Cost is bounded and small: only on an engine `claim`/`release` (~twice per run, not per tool call), capped at 2.0s, degrading to `[]` on any failure. Both the module docstring and the revised test docstring state this plainly rather than hiding it. **Carry this into g2: any probe-cost baseline taken at g1 no longer applies.** |
| 2 | Minor (naming) | `tests/test_spine_rail.py` `test_git_probe_does_not_run_when_an_earlier_rung_answers` | The test is still **named** "does not run when an earlier rung answers" but now asserts the probe **does** run when an earlier *guessed* rung answers. The docstring explains; the name contradicts the assertion. Cheap rename, filed as tc1. |
| 3 | Observation (carried from g1, unchanged) | `resolve_spine_candidate` signature | Still 5 positional params with `tokens`/`file_val` redundant views of `command`. Not touched by this diff; recorded for continuity only. |

**No blockers.**

## Evidence summary

| check | result |
|---|---|
| GREEN `pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q` | **176 passed**, exit 0 (102 → 109 tests) |
| RED (hook reverted to `9d44aa6`, mutation asserted applied — `TOLD_TRUTH_PATH_SOURCES` grep = 0) | **4 failed, 105 passed**, exit 1 |
| RED failed for the right reason | tc1 test failed because the g1 code **wrote to the store**: `assert store.read_bytes() == before` → `b'{...binding...}' != b'{"other-sid": {}}'` |
| Tree restored | sha256 `dee822b0179e03aafa33c6299ccfee6e115527ae197b8fda27286f5e7a562de1` matched pre-swap; numstat back to `57/7` + `156/4`; nothing staged; no commit |

Four of the seven new tests pass in **both** arms — the three told-truth-still-wins tests and
one-worktree-root-still-binds. I read all four: each is a **non-regression guard** for behaviour that
had to survive the guard, not a proof of new behaviour. Same correct shape as the g1 four.

Three new tests monkeypatch `git_worktree_roots` (they test the ambiguity *arithmetic*); that is
acceptable because the load-bearing proof —
`test_post_claim_ambiguous_guessed_rungs_bind_nothing_store_byte_unchanged` — uses a **real** git
worktree with no patching, asserts the command carries no told-truth signal, and compares store
**bytes**.

## Scope and exclusions — verified, not assumed

`git diff --name-only 9d44aa6 -- scripts/ tests/ docs/ skills/` = exactly the two files.
`binding_key`/`BINDING_KEY_SEP` appear only as one reflowed **docstring** line.
`gauge_writer_hook.py`, `checklist_engine.py`, `docs/GAUGE_WRITER_HOOK.md`, `tests/test_gauge_writer.py`
all clean. `resolve_recorded_release_target`'s definition unchanged. `TOLD_TRUTH_PATH_SOURCES` defined
once, used once — wired, not dead. The live main-checkout binding store and every real
`.claude/settings*.json` were never written; all probes ran in `tempfile.mkdtemp()` trees with
`CLAUDE_PROJECT_DIR` overridden, and the one pass over the real trees was read-only.

## Triage candidates (separate from findings)

- **tc1** — rename `test_git_probe_does_not_run_when_an_earlier_rung_answers` (finding 2).
- **tc2** — the guard's silencing reach is a function of *which checklists are tracked* under
  `.agent-work/`. Zero live spines collide **today**, but that is a property of current repo content,
  not an invariant: a future run whose work-id matches a tracked archived work area would bind
  nothing **silently, with no signal**. Consider a diagnostic breadcrumb when the guard refuses, or
  excluding `.agent-work/archive/` from what counts as a candidate.

## Workflow feedback

- Asking me to **test your reading rather than confirm it**, and naming the exact shape you feared,
  is the single thing that made this review fast and worth doing. It converted a judgement call into
  a measurement (2693 collisions, 0 live) that either of us can re-run.
- The deletion count you relayed (4, all in one test, docstring + two assertions) was **exactly
  right** — a noticeable improvement on the g1 handoff, where the "14 tests reseeded" figure sent me
  hunting for deletions that did not exist.
- One thing I'd have liked stated in the handoff: that the probe now runs on guessed-rung claims is a
  **deliberate consequence** of the design, not an accident. The implementer documented it in the
  docstrings, but since it retires a close criterion you set at g1, it deserved to be surfaced to you
  explicitly rather than discovered by a reviewer re-running a spy.
