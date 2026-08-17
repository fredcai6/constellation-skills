# Reviewer Handoff

## Gate
g1

## Survey State Location
Create your review survey checklist at
`.agent-work/epic-567-door/cmdr-b/g1-review/review.json`.

## What Was Implemented
Closes #432 on the ExternalBackend crew-dispatch path in `scripts/run_crew.py`. Previously,
`ExternalBackend` (a record-only backend: no process spawns, so nothing supervises the
crew) verified completion on result-artifact mtime alone (`CrewBackend.verify()`), so a
crew that wrote a fresh result file but drove no engine-gated checklist at all read as an
unqualified `completed`. Now:

1. `ExternalBackend.dispatch()` accepts `--spine` (verification-only — still never bound
   into an environment, since nothing spawns to bind it into).
2. `ExternalBackend.verify()` is a new override (not a `CrewBackend` base-class edit) that
   **defaults to REFUSE** when neither spine evidence nor an explicit
   `--accept-mtime-only-risk "<reason>"` override is given. When spine evidence IS given
   (`--spine` at dispatch, or `--verify-spine` at verify time — the latter wins when both
   are given), completion requires BOTH the result fresh AND `spine_terminal(spine)` — AND
   semantics, never rescue/OR.
3. `--verify-result` gains `--verify-spine PATH` and `--accept-mtime-only-risk REASON`, plus
   a new REFUSED message distinguishing "spine never reached terminal" from "no evidence
   and no override given" (citing #432), checked before falling back to the pre-existing
   STALE/absent messages.
4. A self-caught regression fix: removing the old `--spine` refusal exposed a latent crash
   in `_require_handoff(None, ...)` — guarded with an explicit `handoff is None` check.

## How to Inspect the Diff
This is a linked worktree — inspect the **uncommitted working tree**, not
`git diff main...HEAD`:
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend
git status --porcelain
git diff scripts/run_crew.py tests/test_crew_launcher.py
```

## Task Statement
Make it impossible for a dispatched role that drove no spine at all to return a clean
success on the ExternalBackend dispatch path, and delete the mtime-only verification path
that currently lets it (#432 / epic #567 lane B).

## Close Criteria
- `ExternalBackend.dispatch()` accepts `--spine`, recorded on the entry, never bound.
- `ExternalBackend.verify()` default-refuses (no clean pass) when neither spine evidence
  nor `--accept-mtime-only-risk` is given — this is the core fix; confirm the rewritten
  `test_verify_result_absent_then_present_marks_completed` genuinely asserts `code == 1`
  where it used to assert `code == 0`, and that this is the load-bearing behavior change.
- AND semantics (never OR/rescue) confirmed via `test_verify_named_spine_not_terminal_refuses`
  — a fresh result next to a non-terminal spine must still refuse.
- `--verify-spine` (verify-time) is consulted independently of dispatch-time `--spine` and
  takes precedence when both are given.
- `--accept-mtime-only-risk` is loud: printed to BOTH stdout and stderr, recorded on the
  entry as `mtime_only_risk_accepted` with the reason.
- No crash on `result=None` + `spine=<path>` (legal, newly reachable) — `result_exists`/
  `result_fresh` are never called with `result=None`.
- `.get("spine")`/`.get("result")` used throughout the new code, never bracket access, for
  entries that may lack the key entirely.
- `CliBackend`'s own behavior (`finalize_from_exit_code`, its OR/rescue semantics) is
  byte-for-byte untouched — confirm via grep that `CliBackend` never calls `.verify()` in
  production code (only tests exercise it directly).
- No edit inside `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py` (fenced,
  lane A this wave) — `spine_terminal` reused read-only only.
- Full suite green (`pytest tests/test_crew_launcher.py -q`) except the four tests the
  implementer names as intentional scenario rewrites (listed below) — verify each
  rewrite's OLD scenario is genuinely what this change now forbids, not an unrelated
  weakening.

## Allowed Scope
`scripts/run_crew.py`, `tests/test_crew_launcher.py` only.

## Specific Exclusions
`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py` — fenced, lane A this wave.
Flag as BLOCK if either was touched.

## Constraints the Implementation Must Respect
- AND semantics (not rescue/OR) when both a result and a spine are in play.
- `ExternalBackend.verify()` is an override, not a shared base-class change.
- Reads via `.get(...)`, never bracket access, on `entry["spine"]`/`entry["result"]`.

## Map Anchors (inbound)
- **Structural:** `scripts/run_crew.py:ExternalBackend.dispatch`,
  `scripts/run_crew.py:ExternalBackend.verify` (new), `scripts/run_crew.py:CrewBackend.verify`
  (read-only, unchanged), `scripts/run_crew.py:spine_terminal` (read-only reuse),
  `scripts/run_crew.py:finalize_from_exit_code` (read-only precedent for AND-vs-OR polarity).
- **Decision anchors:** the six in MISSION_FRAME.md's "Decision Anchors & Decision
  Pressure" — check each has a real red/green proof behind it, not just an assertion of
  intent.
  `@grade: guess · leans g1-review · settle: independent re-verification of the pasted
  evidence`
- **Evidence expectations:** the four named intentional test-scenario rewrites, each with a
  one-line reason — confirm each reason is honest (i.e., the OLD scenario really is what
  #432 asks this lane to forbid or narrow), not a cover for an unrelated behavior change.

## Evidence Produced
See `.agent-work/epic-567-door/cmdr-b/crew-handoffs/g1-implement-implementer-result.md` in
full — six numbered evidence sections (dispatch-accepts-spine, core-fix red/green,
named-spine paths, CLI-wiring/crash-guard, rewritten backend-invariant tests, full suite:
217 passed) plus a Wiring Grep and an explicit list of the four intentional test-scenario
rewrites. The Commander independently re-ran the full suite (217 passed, matches) and ran
an independent fresh-process CLI demonstration reproducing the #432 scenario end to end
(refuse by default, then pass only with explicit `--accept-mtime-only-risk`) — reproduce at
least one of these yourself rather than trusting the pasted transcript alone.

## Suggested Model Tier
simple bounded — single-file diff, clear precedent, well-evidenced result to verify against.

## Stop Conditions
Stop and return BLOCK if: the diff touches `checklist_engine.py`/`mcp_spine_server.py`; a
named "intentional" test rewrite's OLD scenario turns out to test something unrelated to
#432 (i.e., the rewrite hides an unrelated behavior change); the full suite does not
actually reach 217 passed in your hands; the default-refuse behavior does not actually
reproduce when you try it yourself.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK, per-check findings, blockers, out-of-scope
observations, workflow feedback) to
`.agent-work/epic-567-door/cmdr-b/crew-handoffs/g1-reviewer-result.md` before ending your
turn.
