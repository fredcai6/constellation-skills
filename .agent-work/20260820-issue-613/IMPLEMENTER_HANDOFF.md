# Implementer Handoff - Wave 2 issue #613

## Mission

Remove only the redundant parent heartbeat writer when a CLI child receives the dispatcher's exact ambient `SPINE_FILE` and `SPINE_SESSION` pair. Preserve parent heartbeating when the child has a different spine/session. This is the residual half of live issue #613; atomic checklist saving already landed and is out of scope.

## Prior-wave truth

Wave 1 integration commit `d3d0c9ac` contains reviewed #636 registry transactions and mechanical #638. Issue #613 says the #607 parent heartbeat is necessary while a child drives its own spine, but becomes a redundant second writer when a handoff-only child inherits the exact parent pair. Current `CliBackend.dispatch` and `resume` build child `env`, then call `_parent_lease_heartbeat()` without telling it what the child received. Current tests incorrectly require heartbeating in the shared-pair case. `checklist_engine.save()` is already atomic, with dedicated `tests/test_checklist_engine_atomic_save.py`; do not reopen that work.

## Protected intent

One active writer owns a shared spine/session during the blocking child call. A parent whose child owns a distinct pair continues heartbeating its own active lease so it does not go stale while blocked.

## Required behavior

- Compare the dispatcher ambient pair with the actual child environment used by both dispatch and resume.
- If child `SPINE_FILE` and `SPINE_SESSION` exactly equal the ambient pair, start no parent heartbeat thread.
- If the child pair differs, preserve the existing parent heartbeat thread, retry/swallow behavior, and joined-before-return ordering.
- If either ambient value is absent, preserve the current no-op.
- Preserve compatibility when the child environment lacks a pair.
- Change the existing shared-spine dispatch and resume regressions so they prove no second parent writer. Add/retain controls proving different-spine dispatch still advances the parent lease.
- Run TDD: capture a focused red against `d3d0c9ac`, then green.

## Allowed scope

- `scripts/run_crew.py`: `_parent_lease_heartbeat` and its two CLI call sites only.
- `tests/test_crew_launcher.py`: `ParentLeaseHeartbeatTests` and minimal coupled fixtures.
- Local artifacts under `.agent-work/20260820-issue-613/`.

## Exclusions

- Do not edit `scripts/checklist_engine.py`, atomic-save tests, registry transactions, identity syntax, MCP/lifecycle code, skills, maps, or architecture docs.
- Do not implement parent authority, one-spine architecture, helper-environment redesign, or issues #632/#634/#638.
- Do not regenerate `map/`; Cartographer owns both map surfaces after this lane integrates.
- Do not mutate GitHub, push, open a PR, or merge to main.

## Evidence

Load-bearing:
- Focused red/green for shared-pair dispatch and resume.
- A different-pair control that demonstrates the parent heartbeat still advances its own lease.
- Full `python -m pytest -q tests/test_crew_launcher.py`.

Confirmatory:
- `python -m pytest -q tests/test_checklist_engine_atomic_save.py`.
- `git diff --check`.
- `rg -n "_parent_lease_heartbeat" scripts/run_crew.py tests/test_crew_launcher.py`.

The known full-suite `map/INDEX.md` freshness failure is pre-existing at this base and belongs to the next Cartographer lane. Do not hide or repair it here.

## Decision fixedness

- decision:shared-pair-suppression — exact same file plus session means no parent heartbeat.
  @grade: settled/human
- decision:different-pair-preservation — keep parent heartbeat when child ownership differs.
  @grade: settled/human
- decision:implementation-seam — helper argument or call-site guard is local Implementer latitude.
  @grade: guess · settle: choose the smallest API that makes both call sites and tests explicit

## Model and authority

Run on `gpt-5.6-terra`, medium reasoning. Tommy delegated bounded #613 implementation and instructed the Admiral to simplify Commander/crew work for Terra. Escalation above Terra, scope widening, architecture, publication, and external mutation float to the Admiral.

## Workspace

- Worktree: `/tmp/constellation-20260820-613`
- Branch: `afk/20260820-613`
- Base: `d3d0c9ac77b43c8894f0358e8b3454e05f1ca644`
- Provision: `git worktree add /tmp/constellation-20260820-613 -b afk/20260820-613 d3d0c9ac77b43c8894f0358e8b3454e05f1ca644`
- Isolation gate: repository-native verifier passed for this worktree and the integration worktree.
- First action: read `constellation-implementer` and `constellation-workbench`, instantiate and claim `.agent-work/20260820-issue-613/implementer-plan.json`, then drive it to terminal done.
- Result: `.agent-work/20260820-issue-613/crew-handoffs/wave2-613-implementer-result.md`.

## Stop conditions

Stop and query the Admiral if suppression cannot be expressed from the ambient pair plus actual child env, if a different-spine compatibility case breaks, if files outside allowed scope are required, or if the observed mechanism contradicts live #613.

## Return

Commit locally before returning. Report status, commit and parent, exact files, red/green and full commands with exit codes, shared/different-pair evidence, scope audit, map impact, out-of-scope observations, and workflow feedback. Do not push.
