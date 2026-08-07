# g6 — the suite count delta, explained BY NAME

`FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` → **EXIT=0 · 1622 passed, 2 skipped, 0 failed,
0 xfailed, 552 subtests passed.**

The claim is **"0 failed"**, never "strictly greater". A retirement that deletes 85 tests cannot
honestly assert a higher count, and this one is higher only because the replacement machinery
carries more tests than the machinery it replaced.

Baseline at `cbd9aee` (before g1): **1688 passed, 2 skipped.**

| step | Δ | what changed, by name |
|---|---|---|
| g1 `bf8819a` | **+12, +1 xfailed** | `tests/test_retirement_guard.py` — the guard, authored before any retirement work so it could be falsified against the real disease. `test_canon_is_clean` carried `xfail(strict=True)`. |
| g2 `dbf9a23` | **+15** | `tests/test_verify_episode_captured.py` — the capture gate, including the sentinel valve test and its own red proof. |
| g3 `100a33c` | **+1** | one GENERAL assertion in `tests/test_install_constellation.py`: every `kind:"command"` postcondition on both spines must name a script that skill installs. |
| g4 `77e428d` | **−85 deleted** | `tests/test_apply_lessons_delta.py` (**70**), `tests/test_verify_agent_feedback.py` (**11**), `tests/test_verify_lessons_applied.py` (**4**) — deleted whole, because the modules they test are gone. |
| g4 `77e428d` | **−13 pruned** | individual methods that loaded a now-deleted module, across `tests/test_agent_work_root.py` (7), `tests/test_feedback_tooling.py` (0 methods; class retargeted), `tests/test_stage_feedback.py` (4), `tests/test_install_constellation.py` (2). A further **6 were retargeted, not pruned** — their subject was a deleted *template* but the machinery under test (`check_skill_freshness`, the baseline manifest) survives, so pruning would have dropped its only coverage. |
| g5 `fd7ef60` | **+3, −2** | +3 tests for the new `retired_names.approved.txt` census (including that it shares one parser rather than forking it); −2 guard tests made redundant by it. |
| g5 `fd7ef60` | **+2** | `test_canon_episode_store_untouched` and `RealCheckoutSkew::…` returned to passing once the g5 edits were committed — they pin tracked paths against `HEAD`, and invariants 3 and 5 mandated editing those files. Working-tree-vs-HEAD artifacts, not regressions. |
| **g6** | **+1 passed, −1 xfailed** | the `xfail(strict=True)` marker came off `test_canon_is_clean`. The xfailed test becomes a passed one. |

**Reconciliation:** 1688 + 12 + 15 + 1 − 85 − 13 + 3 − 2 + 2 + 1 = **1622**. ✓

## What the marker removal actually proves

`test_canon_is_clean` was **strict** on purpose. A strict xfail fails on XPASS, so the moment the
tree really went clean the scaffolding broke the build and forced its own removal. That is what
happened at g5 — the marker did not need remembering, it announced itself.

The assertion is now unconditional: `vr.scan(REPO_ROOT) == []`. From here it is a plain regression
guard.

`python scripts/verify_retirement.py` → **EXIT=0, zero bytes printed.** It was observed **failing**
on the untouched tree at g1 across three legs
(`.agent-work/epic418-h-447/evidence/g1-guard-red.txt`) before it was ever observed passing.
