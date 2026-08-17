# Implementer Handoff

## Gate
`g3` — `finish_work` composition + dispose + CLI (of 3 gates; g1 shipped verify/close primitives, g2 shipped reap + child-plan release, both reviewed and integrated).

## Task
Add `finish_work` to `scripts/spine_lifecycle.py`, composing g1's and g2's already-shipped functions. Exact signatures already in the file (read them yourself — the docstrings on each are the authoritative contract, this handoff only states the composition):

```python
def done_refusal(spine: dict, *, tree_clean: bool, episodes_captured: bool) -> str | None
def _advance_and_release(spine_path, session_id: str, *, root, why: str | None = None) -> dict
    # {"ok": True, "output": str} or {"ok": False, "refusal": str, "stage": "start"|"advance"|"release"}
def force_reap(project_dir) -> dict | None
def _release_child_plans(spine_path, work_dir, *, root, reason: str) -> dict
    # {"released": [str, ...], "unclaimed_active": [str, ...]}
def close_work(spine_path, *, root, today: str) -> dict
    # existing, unmodified; raises SpineLifecycleError via closeout_refusal if not ready
```

**(a) `finish_work(spine_path, *, root, session_id, today, why=None, push=True, open_pr=False) -> dict`**

Composition order is **load-bearing** (this is the whole point of both cold critiques — PLAN_CRITIQUE.md finding 1/2, PLAN_CRITIC.md's matching findings 1-3, and the g1/g2 implementers' own independent re-discoveries of the same facts):

1. Load the spine dict from `spine_path` (resolve relative to `root`, same pattern `close_work`/`_advance_and_release` already use).
2. `refusal = done_refusal(spine, tree_clean=<caller-supplied>, episodes_captured=<caller-supplied>)`. If not `None`: **refuse and stop.** Return `{"ok": False, "refusal": refusal, "stage": "verify"}`. No mutation happens on this path — nothing has been touched yet.
3. `_release_child_plans(spine_path, work_dir, root=root, reason=f"closeout: child plan swept by finish_work for {work_id}")` — **BEFORE** the top-level release and **before** any reap. `work_dir` is `spine_path`'s own parent directory. Collect its `released`/`unclaimed_active` lists for the return value. This function's own refusal path (an engine refusal on a specific child) does not raise — it reports that child in `unclaimed_active`, per its own docstring; `finish_work` does not need to special-case this, just collect what it returns.
4. `_advance_and_release(spine_path, session_id, root=root, why=why)` — the top-level spine's own close. If `result["ok"]` is `False`: **refuse and stop**, returning `{"ok": False, "refusal": result["refusal"], "stage": f"advance-release:{result['stage']}"}`. Note: by this point step 3 has already released children — a refusal here still leaves those released (this is fine and intended; a run whose top-level gate isn't ready to close but whose children already finished is a real, valid intermediate state, not a rollback candidate).
5. `force_reap(root)` — **AFTER** every release in steps 3 and 4, never before. This is the ordering fix from PLAN_CRITIQUE.md finding 2 / PLAN_CRITIC.md finding 2: `_reap_binding_entries` only drops an entry whose target already reads `released`, so reaping before children are released would leave every child's binding-store entry stale — reproducing the exact #552 defect this whole gate exists to close. `force_reap` returning `None` (a fail-open path) is not a `finish_work` failure — log it in the return value (e.g. `"reap": None`) and continue; the archive-move below is unaffected by it.
6. `close_work(spine_path, root=root, today=today)` — **existing, unmodified.** This is the one and only place `closeout_refusal` (lease/terminality/archive-exists) is checked — by the time this runs, the lease is already released (step 4), so it will not spuriously refuse. If `close_work` raises `SpineLifecycleError`: catch it, return `{"ok": False, "refusal": str(exc), "stage": "archive"}`. Do not let the exception propagate — `finish_work`'s whole contract is "one call, one clean result or one clean refusal," never a raised exception on a normal-outcome refusal.
7. `git push origin <branch>` (via `subprocess.run(["git", "push", "origin", branch], cwd=root, ...)`, `branch`/`head` read from `close_work`'s own return dict) when `push=True`. A push failure is reported in the return (`"pushed": False`, plus the git error text) but does **not** unwind steps 1-6 — the archive move already committed locally; a failed push is a network/auth problem to retry, not a reason to fail the whole call.
8. `open_pr(...)` — see part (b) below — called **only** when `open_pr=True`. Not called by default.

**Success return:** `{"ok": True, "work_id": ..., "branch": ..., "head": ..., "archive": ..., "pushed": bool, "pr": None | str, "child_plans_released": [...], "unclaimed_active": [...], "reap": dict | None}`.

**Refusal return** (any of steps 2/4/6): `{"ok": False, "refusal": <verbatim text>, "stage": "verify"|"advance-release:<substage>"|"archive"}`. Never raises for a closeout refusal — `SpineLifecycleError` is reserved for genuine faults elsewhere in the stack (e.g. `close_work`'s own git-command failures), not for the normal "not ready yet" outcome.

**(b) `open_pr(work_id: str, branch: str, *, root, title: str | None = None, body: str | None = None) -> str | None`**

A **separate, independently-callable** helper — `finish_work` does **not** call it unless `open_pr=True`. This is the floated PR-opening question (`decision:pr-opening-question-is-not-yours`, launch order Pre-Rulings): Tommy has not ruled whether PR-opening belongs in the engine verb or a wrapper script. This design makes either answer adopt without rework — a wrapper script can call `spine_lifecycle.open_pr(...)` itself today; the only change needed if the engine verb is later ruled to own it is `finish_work(open_pr=True)`, already wired.

Implementation: `subprocess.run(["gh", "pr", "create", "--title", title or f"chore: close {work_id}", "--body-file", <a NamedTemporaryFile path — never a heredoc or --body string, per this repo's own Windows-shell doctrine>, "--head", branch], cwd=root, capture_output=True, text=True)`. Parse the PR URL from stdout (`gh pr create` prints it as the last line on success). Return the URL, or `None` if `gh` fails (do not raise — a failed PR-open is a reportable fact, not a fault). Never called against a live spine — this function takes no spine path at all, only `work_id`/`branch`, so there's nothing to accidentally mutate.

## Protected Intent
"I'm done" should be one call. An agent that has genuinely finished a run should never need to hand-sequence release → reap → archive → push, and a run that is NOT ready should get one clean, actionable refusal — never a partial mutation, never a swallowed exception, never a call into `close_work` that spuriously refuses because the ordering was wrong.

## Test Mode
Test-after allowed (same convention as g1/g2).

## Close Criteria
- `finish_work` and `open_pr` exist in `scripts/spine_lifecycle.py`.
- The composition order matches part (a) exactly: children released → top-level release → reap → archive → push → (optional) PR. A test that asserts this ORDER (not just that all steps eventually happen) is required — e.g. a fixture with a child plan and a spy/call-order assertion, or an assertion that after a deliberately-failing `force_reap` (or a fixture where reap would matter), the child's binding entry is provably gone.
- `finish_work` never raises `SpineLifecycleError` for a normal closeout refusal at any of steps 2/4/6 — it returns the structured refusal dict instead.
- `open_pr` is never called unless `open_pr=True` is explicitly passed — a test asserting this (e.g. mock/spy on `subprocess.run` for the `gh` call, confirm zero calls when `open_pr` is omitted or `False`).
- **THE #552 LEASE-PROOF END-TO-END TEST** (this gate's actual reason to exist — required, load-bearing): build a fixture work area under `tmp_path` with a top-level spine AND a nested child plan declared via `child_checklist`. Claim both. Drive both to their terminal gate (postconditions satisfiable). Run a structural active-lease census (reuse or mirror `_active_engine_session_spine`'s scan predicate) BEFORE `finish_work`: expect 2 active. Call `finish_work`. Run the census AFTER: expect **0** active. Assert the archive directory exists and contains the child plan file. This is the concrete proof the launch order's Return Shape item 5 asks for.
- Fenced files empty diff: `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py`.
- Full `tests/test_spine_lifecycle.py` green; state pre/post counts (pre-change: 104).

## Allowed Scope
- `scripts/spine_lifecycle.py` — add `finish_work`, `open_pr`.
- `tests/test_spine_lifecycle.py` — add tests, fixtures, helpers.
- `scripts/spine_done_cli.py` — **NEW FILE**, not fenced. A thin CLI wrapping `finish_work`: `--file`, `--root`, `--session-id`, `--today`, `--why`, `--tree-clean` (bool flag, or auto-detect via `git status --porcelain`), `--episodes-captured` (bool flag), `--no-push`, `--open-pr`. Prints the returned dict as JSON to stdout; exits 1 if `result["ok"]` is `False`, else 0. This is the reachable-today "one door verb" — usable without waiting on lane A's `mcp_spine_server.py` rewrite to land. Keep it thin: argument parsing plus one call into `finish_work`, nothing else.

## Specific Exclusions
- **`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py` — DO NOT EDIT.** Fenced (checklist_engine.py, mcp_spine_server.py — lane A, this wave) or out-of-scope-by-design (spine_rail.py — g2 already established the library-call-only convention).
- Do not modify `done_refusal`, `_engine_call`, `_advance_and_release`, `force_reap`, `_release_child_plans`, or `close_work`/`closeout_refusal` — compose them, do not change their behavior.
- Do not wire `finish_work` as an MCP tool (`spine_done`) — that needs `mcp_spine_server.py`, fenced. `scripts/spine_done_cli.py` is the in-scope substitute.

## Constraints
- **Never run `finish_work` or the new CLI against a live spine file.** `.agent-work/epic-567-door/spine.json` is the Admiral's active lease; `.agent-work/epic-567-door/cmdr-g/spine.json` and `execute.json` are this Commander's own live spines. Every test fixture lives under `tmp_path`; the CLI smoke-test (required evidence, below) also runs against a `tmp_path` fixture, never a real repo spine.
- `open_pr` must genuinely make no `gh`/`git` call when not invoked — verify with a spy/mock, not by inspection alone.
- POSIX-form commands; `PYTHONIOENCODING=utf-8` for captured subprocess output; `py` works on this host.
- When the CLI writes a PR body (if you exercise `open_pr` in a test — you may mock `subprocess.run` instead of a real `gh` call, which is preferred and avoids any real network/GitHub dependency), write it to a temp file and use `--body-file`, never a heredoc `--body` string — this repo's own doctrine (`windows.md`) is explicit that a heredoc/here-string fails `gh pr create --body` on at least one platform this repo supports.

## Map Anchors (inbound)
- **Map entry point:** none — DEGRADED-UNPARSEABLE, no `docs/architecture` map. Start from `scripts/spine_lifecycle.py`'s own docstrings for `_advance_and_release`, `force_reap`, `_release_child_plans` (all read above) and `close_work` (:384+).
- **Structural:** `scripts/spine_lifecycle.py` — `close_work` (:384+, unmodified), `done_refusal` (:186), `_advance_and_release` (:673), `force_reap` (:753), `_release_child_plans` (:798).
- **Capability:** mechanical-closeout-one-verb — #574's full contract sketch, steps 1-5, reachable via one CLI call today.
- **Constraints/assumptions:** `decision:pr-opening-question-is-not-yours` — FLOAT it, do not rule it; this gate assumes the wrapper opens the PR by default (`open_pr=False`), with the helper available either way.
  `@grade: settled/human · leans g3-implement`
- **Decision anchors:** `decision:new-rot-first-old-rot-maybe` — stopping NEW stale leases from accruing is the deliverable; sweeping the 41 pre-existing stale leases (measured separately, see `RETURN.md`) is out of scope for `finish_work` and this gate does not attempt it.
  `@grade: settled/admiral · leans g3-implement`
- **Evidence expectations:** the #552 lease-proof end-to-end test (close criteria, above) is the single most important piece of evidence this gate produces — it is literally what the launch order's Return Shape item 5 asks the Commander to show.

## Deliverable Path Check
- **Committed** — `scripts/spine_lifecycle.py`; `git check-ignore` exit 1.
- **Committed** — `tests/test_spine_lifecycle.py`; `git check-ignore` exit 1.
- **Committed** — `scripts/spine_done_cli.py` (new); `git check-ignore` exit 1 expected — confirm before claiming it as a deliverable, and note in your result that it is untracked-until-staged (appears in `git status`, not `git diff --name-only`) since it's a new file.

## Required Evidence
**Load-bearing (prove rigorously):**
- The #552 lease-proof end-to-end test — paste the test body and its passing output.
- A composition-order test/assertion (children before reap, reap after every release).
- A **fresh-process** smoke run of `scripts/spine_done_cli.py` against a `tmp_path` fixture (invoke it via `subprocess.run(["python3", "scripts/spine_done_cli.py", ...])`, not an in-process import) — per this repo's dogfooding rule (`docs/agents/ORCHESTRATOR_CONTEXT.md`), a fresh-process run is the only trustworthy validation of anything touching engine/hook-adjacent code, and this CLI is the actual deliverable a future run will invoke.
- `py -m pytest tests/test_spine_lifecycle.py -q` output, pre/post counts (pre-change: 104).

**Confirmatory (spot-check suffices):**
- `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py` → empty.
- `open_pr` not called by default (spy/mock assertion).

## Wiring Grep
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease && \
grep -rn "finish_work\|open_pr" --include=*.py . \
  | grep -v "def finish_work" | grep -v "def open_pr"
```
`finish_work`'s only non-definition callers at the end of this gate: the tests, and `scripts/spine_done_cli.py`. State the count.

## Verification Commands
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease
PYTHONIOENCODING=utf-8 py -m pytest tests/test_spine_lifecycle.py -q
git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py
```

## Suggested Model Tier
Sonnet — bounded; the composition is fully specified, the risk is in getting the ORDER right, which is a read-the-docstrings-and-follow-them task, not an ambiguous design decision. The launch order fixes this lane at Sonnet.

## Authority
Already decided — do not re-litigate:
- The composition order in part (a).
- `open_pr` off by default; `--body-file`, never a heredoc.
- The fence: `checklist_engine.py`, `mcp_spine_server.py`, `spine_rail.py` are not yours to edit.
- `finish_work` never raises for a normal refusal.

**You must not decide alone:** anything requiring an edit to a fenced file; changing g1/g2's functions' behavior; ruling the PR-opening question (float any pressure on this back to the Commander, do not decide it).

## Stop Conditions
Stop and return if: allowed scope must be exceeded; a fenced file must be touched; the #552 lease-proof test cannot be constructed as specified (say so plainly — a measured negative is a real result); required evidence cannot be produced; a decision outside the authority above is needed.

## Return Format
Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

`Return status` lowercase (`complete | partial | blocked | out-of-scope | failed`).

**Delivery.** Write the full `IMPLEMENTER_RESULT` to `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g3-implementer-result.md` before ending your turn.
