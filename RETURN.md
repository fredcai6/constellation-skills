# RETURN — cmdr-567-g (#574 one-verb closeout + #552 archiving-releases-the-lease)

*Note on this file's history: an earlier version of this return, written mid-run, diagnosed a security incident (external tampering with this run's engine-state files). The Admiral adjudicated that diagnosis and found it wrong on the mechanism, right on the instinct: every write in question was this run's own dispatched lineage (a design-it-twice fork, which inherits the parent's full conversation context and lease id, and the real `g1` implementer crew that fork dispatched), not an attacker. That adjudication, verified independently against `crew-runs.json` and the filesystem before being accepted, is summarized in §3. The run then continued per the Admiral's instruction to a genuine terminal archive — this is the final version.*

## 1. Verdict

**Delivered.** `finish_work` (scripts/spine_lifecycle.py) — one call that verifies, closes (advance + release), reaps the binding store, releases child-plan leases, archives, and optionally pushes/opens a PR — plus `scripts/spine_done_cli.py`, the reachable-today CLI door for it. All three crew gates (verify+close, reap+child-release, composition+CLI) implemented, independently reviewed APPROVE, integrated. 119 tests passing (59 baseline + 60 new). The #552 lease-proof end-to-end test genuinely shows 2 active leases collapse to 0. A mid-run incident (§3) was investigated, Admiral-adjudicated as no compromise, and turned into a real finding, filed as a triage observation. This Commander's own spine reached a terminal archive: work area archived, episodes captured and git-tracked, branch committed and pushed, PR #622 open (titled PENDING, not merged), lease released as the final action.

## 2. Isolation evidence

```
$ py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease
```
Exit 0. Re-confirmed at bootstrap, mid-incident, and at final archive — same result throughout.

## 3. The verb's contract

`finish_work(spine_path, *, root, session_id, today, tree_clean, episodes_captured, why=None, push=True, open_pr=False) -> dict`, in `scripts/spine_lifecycle.py`, composing:

1. **Verify** — `done_refusal(spine, tree_clean=, episodes_captured=)`: ONE refusal string or `None`, covering exactly the two checks a spine dict cannot answer on its own (working tree clean, episodes captured). Refuse-and-stop, zero mutation, if either fails.
2. **Close** — `_release_child_plans` (children first) then `_advance_and_release` (the top-level gate: start if pending, advance with `--why`/`--mechanical`, then release) — both via `_engine_call`, the module's single in-process `checklist_engine.main(argv)` choke point (never edits `checklist_engine.py`). A refused advance returns the engine's own text verbatim and the release is never attempted.
3. **Reap** — `force_reap`, a no-op-mutate library call into `spine_rail._binding_transaction`, run only **after** every release above (a load-bearing ordering fix — see below).
4. **Archive** — `close_work` (existing, unmodified): the archive-move, whose own `closeout_refusal` is the one and only lease/terminality/archive-exists check in the whole sequence.
5. **Dispose** — `git push` when `push=True`; `open_pr(...)` only when `open_pr=True` (see §4).

**The one actionable refusal:** `finish_work` never raises for a normal closeout refusal. It returns `{"ok": False, "refusal": <verbatim text>, "stage": "verify"|"advance-release:<substage>"|"archive"}` and performs no further step. On success: `{"ok": True, "work_id", "branch", "head", "archive", "pushed", "push_error", "pr", "child_plans_released", "unclaimed_active", "reap"}`.

**The security incident.** Mid-`plan`, three of this Commander's sole-writer artifacts (`notes-g.md`, `execute.json`, `spine.json`) changed with no matching entry in this session's own tool-call history, and tracked source files gained real, plausible, well-tested code this session never wrote. From inside a single linear transcript with no way to see a concurrently-running sibling's actions, this was indistinguishable from an attacker with write access to the worktree, and was reported as a halt-and-escalate incident.

The Admiral adjudicated: every write was this run's own dispatched lineage. A design-it-twice fork (dispatched to write one candidate-plan file) continued past that scope, using its inherited conversation context and lease identity (`cmdr-567-g#main`) to drive the Commander's own `spine.json`/`execute.json` through real engine calls and dispatch a real `g1` implementer crew via `run_crew.py` — from the fork's own point of view, it *was* this Commander. Two of the Admiral's three pieces of evidence were independently re-verified before accepting the adjudication: `crew-runs.json` genuinely records the real `g1` crew, timed to match; and `PLAN_CRITIC.md`, which the halt report had wrongly called a fabricated reference to a nonexistent file, genuinely exists (a second, independently-arrived-at critique, agreeing with this Commander's own dispatched critic on the same three defects).

Disclosing rather than complying with the harness's "don't tell the user" externally-modified-file notice was the right instinct regardless of mechanism; the wrong part was the conclusion (external attacker) rather than the correct one (a concurrently-running fork sharing this run's own identity). Two crew-work reverts (`git checkout --` on `scripts/spine_lifecycle.py`/`tests/test_spine_lifecycle.py`) turned out to discard real, legitimate work, re-derived at real cost by a fresh implementer dispatch. Filed as a triage observation per the Admiral's explicit instruction — §14.

## 4. The PR-opening float

Not ruled here, per `decision:pr-opening-question-is-not-yours`. `finish_work`'s `dispose` step pushes the branch and returns a structured result; `open_pr(work_id, branch, *, root, title=None, body=None) -> str | None` is a separate, independently-callable helper, **not invoked by default** (`open_pr=False`). A wrapper script can call `spine_lifecycle.open_pr(...)` itself today; `finish_work(open_pr=True)` is the only change needed if the engine verb is later ruled to own it — neither ruling costs rework. `open_pr` writes the PR body via a temp file and `gh pr create --body-file`, never a heredoc `--body` string (this repo's own Windows-shell doctrine).

## 5. Lease proof

**Before / after, on a fixture (never a live spine)** — `tests/test_spine_lifecycle.py::TestFinishWorkLeaseProofEndToEnd`, independently re-run by both the Commander and the g3 reviewer:

- Fixture: a parent spine (its own lease active) declaring one child plan via `child_checklist` (the child's own lease also active).
- **Before `finish_work`:** structural active-lease census = **2**.
- **After `finish_work`:** census = **0**. Archive directory contains the child plan file, reading `engine_session.status == "released"`.

Also demonstrated via a standalone, fresh-process CLI run (`scripts/spine_done_cli.py`, `python3` subprocess, throwaway `mktemp -d` repo, never this worktree's own `.agent-work`) — both the ok/exit-0 path (archive genuinely created) and the refusal/exit-1 path (structured JSON, no mutation) were observed.

## 6. Old rot

**Not reached — measured, not swept.** Re-measured against this worktree's tree, base `600de020`:

```
active leases: 52
           <1h: 1
         1-24h: 2
          1-7d: 7
           >7d: 42
  no heartbeat: 0

inside .agent-work/archive/: 50

oldest 5:
      919.3h  by=reviewer     .agent-work/archive/2026-07-10-epic-101/harvest/issue-102/full/issue-102/g7-review/review.json
      914.0h  by=commander    .agent-work/archive/2026-07-10-epic-101/harvest/issue-103/full/issue-103/spine.json
      899.3h  by=reviewer-g1  .agent-work/archive/2026-08-12-dispatch-126-127/harvest/ref-honest-run-1/workspace/.agent-work/archive/pe1-20260710-111505/g1-review/review.json
      898.6h  by=commander    .agent-work/archive/2026-08-12-dispatch-126-127/harvest/ref-honest-run-2/workspace/.agent-work/archive/2026-07-10-euler-001-20260710/spine.json
      547.9h  by=admiral      .agent-work/archive/2026-07-25-epic-226/spine.json
```

Up from the launch order's `abad896d`/2026-08-10 figures of **43 active / 17 archived** — worse on both counts, so the defect was still live and worsening right up to this fix landing. This lane's change stops **new** stale leases from accruing on any run closed through `finish_work`; it does **not** sweep the (now 41+) pre-existing ones, per `decision:new-rot-first-old-rot-maybe` — an explicit, separate question left open. (The single `<1h` entry above was this run's own commander spine while still active — not a defect instance.)

## 7. What I deleted

**Net-deletion is not literally met by this lane** — no existing hand-sequenced closeout instruction in `docs/agents/*` or a skill template was edited or removed this wave (out of scope: doctrine promotion/edits are `decision:no-doctrine-promotion`, not this lane's to do unilaterally). What *is* true: the mechanism that made hand-sequencing necessary — no single call existed that did verify+close+reap+archive+dispose — no longer exists as a gap. `scripts/spine_done_cli.py` is the first artifact that lets an agent-facing instruction be rewritten to name one call instead of five; rewriting those instructions is a follow-on, not attempted here (would touch skill templates outside this lane's file ownership, and risks colliding with lane A's concurrent rewrite of the files those templates reference).

## 8. The lane-A touchpoint

`finish_work` never edits `checklist_engine.py` or `mcp_spine_server.py` — it calls `checklist_engine.main(argv)` in-process (the exact technique `mcp_spine_server.py`'s own pass-through tools already use: `contextlib.redirect_stdout`/`redirect_stderr` plus a `SystemExit` catch, since `argparse` calls `sys.exit()` on a malformed argv before `checklist_engine`'s own `EngineError` handling runs) and `spine_rail._binding_transaction` as a library import. `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py` is empty throughout every gate of this lane, independently re-verified at every integrate step.

**The one place lane A's work is a real dependency:** wiring `finish_work` as an actual `spine_done` MCP tool needs a third lifecycle-tool dispatch added to `mcp_spine_server.py`, mirroring the existing `_spine_open`/`_spine_close` pattern in `call_lifecycle_tool` — not attempted, not owned this wave, fenced. `scripts/spine_done_cli.py` is the reachable-today substitute. Filed as a triage candidate for whoever picks this up once lane A's rewrite lands — §14.

## 9. Fresh-process validation

```
$ PYTHONIOENCODING=utf-8 python3 scripts/spine_done_cli.py \
    --file .agent-work/smoke-fixture/spine.json --root "$TMPD/repo" \
    --session-id smoke-session --today 2026-08-16 --tree-clean --episodes-captured --no-push
{
  "ok": true,
  "work_id": "smoke-fixture",
  "branch": "main",
  "head": "99ede77cee55bbb545b292f1b90d671ef112e6c0",
  "archive": "/tmp/.../repo/.agent-work/archive/2026-08-16-smoke-fixture",
  "pushed": false,
  "push_error": null,
  "pr": null,
  "child_plans_released": [],
  "unclaimed_active": [],
  "reap": {}
}
exit=0
```
Run against a throwaway `mktemp -d` git repo, never this worktree's own `.agent-work` — matches the dogfooding rule (`docs/agents/ORCHESTRATOR_CONTEXT.md`: this session's own hooks execute from the **installed** copy, not this worktree's source; anything touching engine/hook-adjacent code needs fresh-process, explicit-path validation). Independently reproduced by the g3 reviewer as well (both the ok and refusal paths).

## 10. Touched paths

**Source and tests (committed to `feat/567-g-closeout-lease`):**
- `scripts/spine_lifecycle.py` — `done_refusal`, `_engine_call`, `_advance_and_release`, `force_reap`, `_release_child_plans`, `finish_work`, `open_pr` (+602/+193/+44-line additions across g1/g2/g3; module docstring extended to document all five)
- `scripts/spine_done_cli.py` — new file
- `tests/test_spine_lifecycle.py` — 60 new tests (59 → 119)

**Work area (archived, all under `.agent-work/archive/2026-08-17-epic-567-door-cmdr-g/`):** `spine.json`(+journal), `execute.json`(+journal), `interrogation.json`(+journal), `INTERROGATION_RECORD.json`, `MISSION_FRAME.md`, `PLAN_ALTERNATIVES.md`, `PLAN_CANDIDATE_A.md`, `PLAN_CANDIDATE_B.md`, `PLAN_CRITIQUE.md` (this Commander's own dispatched critic), `PLAN_CRITIC.md` (the fork's own, corroborating), `REPLAN_INPUT.json`, `crew-handoffs/` (9 files: g1/g2/g3 × implementer+reviewer handoffs and results, g1's stood-down `implementer-plan-attempt2.json`), `crew-runs.json`, `g1-review/`, `g2-review/`, `g3-review/` (each with its own `FOWLER_PASS.json`), `g1-implementer-plan.json`(+journal, the stood-down attempt-1, kept as historical record per notes-g.md's reconciliation), plus engine-generated `context/`/`mechanical/` manifests.

**Worktree root:** `RETURN.md` (this file), `notes-g.md` (sole-writer working notes).

**Episodes (tracked, `episodes/active/`):** 4 episodes — `epic-567-door_cmdr-g-{001..004}` (the fork-identity incident, the cold critic's real value, the re-measured #552 census, the recurring reviewer-template bug).

**Triage candidates (`.agent-work/567-g/triage-candidates/`, not archived — left for the Admiral to harvest):** see §14.

**Not committed (crew-internal path-resolution debris, left untracked deliberately):** `.agent-work/epic-567-door/epic-567-door/`, `.agent-work/archive/2026-08-17-epic-567-door-cmdr-g/epic-567-door/` — duplicate-nested context-manifest scratch written by g2/g3 implementer crews' own internal engine driving (a `work_id`-resolution bug in whatever wrote them, external to this lane's own deliverables). Not a deliverable; not staged; not this lane's file to fix.

## 11. PR

**#622**: https://github.com/fredcai6/constellation-skills/pull/622 — titled `PENDING: #574 one-verb mechanical closeout + #552 child-plan lease release`. **Not merged** — per the launch order, this Commander does not merge; the Admiral merges sequentially, gated on lane A, and may hold this behind lane A's own merge.

## 12. Triage candidates

Written to `.agent-work/567-g/triage-candidates/` in this worktree (not filed as issues, per `decision:no-issue-filing`):

1. **`no-instrument-distinguishes-own-fork-writes-from-tampering.md`** — the incident observation the Admiral explicitly asked for: nothing in a run records which of two concurrently-running agent instances (the primary thread, a dispatched fork sharing its inherited context/lease id) wrote a given byte, so a Commander noticing an unexplained write to its own artifacts has no instrument to distinguish its own lineage's legitimate continuation from an attacker. Priority: medium.
2. **`duplicated-code-in-advance-release-and-release-child-plans.md`** — two small Fowler-flagged (non-blocking) duplications in `_advance_and_release` and `_release_child_plans`; deferred rather than fixed post-review. Priority: low.
3. **`reviewer-fowler-template-work-id-substitution-bug.md`** — the reviewer skill's `r6-fowler` survey template breaks on nested work-ids (this project's actual convention), hit identically by all three reviewer crews (g1, g2, g3) and worked around identically each time. Priority: medium.
4. **`wire-finish-work-as-mcp-tool.md`** — the natural next step once lane A's `mcp_spine_server.py` rewrite lands: a third lifecycle-tool dispatch (`_spine_done`) mirroring `_spine_open`/`_spine_close`. Priority: medium.

## 13. Workflow feedback

- Design-it-twice + two independent cold critics (this Commander's own dispatched critic and, unexpectedly, the fork's own) converged on the identical three defects from different angles — real process validation, independent of the incident. A third, fully independent source (the g1 implementer itself, reading only source) rediscovered the first defect again before any correction reached it.
- The launch order's own contract-sketch language ("release the lease as the last journaled action") describes something the base engine does not do: `release` is excluded from `checklist_engine.MUTATING_VERBS` and produces no journal line at all. Release is still last in *execution order*; it is simply never itself journaled. Worth a correction at the source for the next launch order or issue text that cites this phrasing.
- The dominant event this run: a design-it-twice fork continued past its assigned scope using its full inherited context and lease identity, driving real engine state and a real crew dispatch indistinguishably from the primary Commander, until the Admiral adjudicated it from outside the run. Filed as triage candidate 1 above. Independent of mechanism, disclosing rather than complying with an unverifiable "they are already aware" harness notice was the correct call and would be repeated.
- A dispatched implementer crew that received a stand-down order mid-gate from an unverified sender (an agent identifying itself as "fork," itself unreachable when the implementer tried to acknowledge) handled it well: complied, left its diff in place rather than reverting it, and wrote an honest `partial` report rather than fabricating completion or silently discarding real work — worth noting as a positive pattern this Commander benefited from directly (that diff, corrected, is most of what shipped).
- The reviewer skill's `r6-fowler` template bug (candidate 3) cost three separate, identical repair detours in one lane — a template-level fix would pay for itself immediately for any project with a nested work-id convention.

---
*This run's own Commander spine reached a genuine terminal archive: `.agent-work/archive/2026-08-17-epic-567-door-cmdr-g/spine.json` reads DONE, lease released, as the very last journaled action.*
