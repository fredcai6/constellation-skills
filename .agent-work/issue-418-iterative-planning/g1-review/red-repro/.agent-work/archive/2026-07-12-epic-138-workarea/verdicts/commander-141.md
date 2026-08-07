# Commander Verdict — issue #141 (hook suite, #138 channel B)

**Status: COMPLETE — green, reviewed PR open. Merge is the human's (server-side).**
Commander: commander-141 (delegated, opus). Spine driven 10/10 → terminal archive, lease released.

## PR
https://github.com/fredcai6/constellation-skills/pull/150 — branch `issue-141`, base `main`, commit `38e61c4` (3 files, +795).

## Deliverables (all committed, all `git check-ignore` exit 1 = tracked)
- `scripts/hooks/spine_rail.py` — one script dispatched by event name: **Stop** (refuse mid-flight turn-end; honor engine `blocked` as honest stop; 3-strike no-progress escape hatch keyed on `(journal_seq, active_id)`), **SessionStart(compact|resume|startup)** (re-inject reconstructed `current`), **PostToolUse(Bash)** (session→spine binding from `claim`/`release`; release = off-switch). Reads the spine STATE FILE directly (no engine subprocess); fail-open on every path; stdlib only.
- `.claude/settings.json` — three registrations. No PreCompact (cut at critic review).
- `tests/test_spine_rail.py` — 33 unit tests, all branches.

## Test results (exit codes)
- `py -m pytest tests/test_spine_rail.py -q` → **33 passed** (re-run by commander at g1-integrate AND by the engine `advance` postcondition; exit 0).
- `py -c "import json;json.load(open('.claude/settings.json'))"` → exit 0 (valid; hooks: Stop, SessionStart, PostToolUse).
- Reviewer (independent, opus) → **APPROVE**, 14/14 survey, 0 findings, 0 triage candidates.
- Scope: `checklist_engine.py` and `skills/` UNTOUCHED (no engine changes — #140 owns the engine this wave).

## Isolation-check output (first step, before any git op)
```
worktree OK: in C:/Programs/constellation-wt-141
EXIT: 0
```

## Probe logs (g2 reasoning gate — out-of-repo sandbox, claude 2.1.206, this box; sandbox deleted, no repo leakage)
**Settings.json fires spine_rail headless: PASS (all three registrations).** End-to-end firing sequence (`firing.log`):
```
SessionStart source=startup
PostToolUse   (agent `claim` -> spine_rail wrote the session->spine binding)
Stop          (spine_rail read binding -> mid-flight -> BLOCKED the turn-end)
PostToolUse   (agent ran `block g1` — the honest-stop path the rail's reason named)
PostToolUse
PostToolUse   (agent ran `release` -> spine_rail DELETED the binding: off-switch)
Stop          (binding gone -> spine_rail allowed the stop -> run ended)
```
The headless agent's unprompted narration: *"A stop hook then insisted the spine's gate g1 stay active... I used the engine's sanctioned exit: blocked gate g1 (bubbled to the parent), then released the lease."* Fixture spine ended `g1: blocked` + lease `released`; binding/nudge scratch ended `{}` (release cleaned them). **Flagship Stop-block + honest-stop path + off-switch, all live headless.**

**SessionStart source coverage:**
- `startup` — live-proven (cold `claude -p`).
- `resume` — **live-proven** (`claude -p --continue` fired `SessionStart source=resume`) — the load-bearing post-restart re-injection path ships proven.
- `compact` — **SCOPED NULL (compact-trigger live probe):** could not force a compaction in a single-turn headless `claude -p` (no context-limit pressure, no `/compact` in headless), so `source=compact` never fired to observe. NOT a hook defect: the matcher is `compact|resume|startup` and the re-injection code is source-agnostic, so the same proven code path runs when `source=compact` fires. Ships on the proven resume/startup paths + x2 docs-evidence, **per the launch-order pre-ruling and the CONFIRMED spec's own TS6 acceptance.** Full detail: `.agent-work/archive/2026-07-12-issue-141/evidence/g2-probe-log.md`.

Gotcha confirmed (matches x2): `--dangerously-skip-permissions`/bypassPermissions is refused headless by the auto-mode "Create Unsafe Agents" classifier; `--allowedTools Bash` (a non-bypass allowlist) is the working recipe for headless tool execution.

## Rulings / decisions taken within latitude
- **Read the spine state file directly vs. subprocess the engine `current`:** chose read-file (robust in headless/subagent, fast, unit-testable). Documented in the module docstring as the spec-accepted locality cost (a 2nd place that re-encodes `TERMINAL={complete,skipped}` — designer-B §6, SY7). Implementation-detail latitude.
- **Binding/nudge file location/format** (inherited latitude): `<project>/.agent-work/.spine-rail-binding.json` and `.spine-rail-nudges.json`, JSON maps keyed by claude `session_id`; git-ignored runtime scratch. `release` deletes both.
- **Compact-trigger null:** shipped re-injection for resume+startup (proven) and recorded the compact null per the pre-ruling — did not block the wave.
- No engine change was needed; nothing floated to the Admiral.

## Triage candidates
None new. The compact-trigger unverified-in-headless residual is already tracked in the CONFIRMED spec ("Deferred to later drills — behavioral measurement of post-compaction re-injection needs a compaction-forcing scenario, not currently constructible on demand"). No new issue filed; no filing authority sought this run.

## Workflow feedback (for the epic harvest)
- Front-loading the implementer handoff with **live-verified engine facts** (current/active_id/journal/lease shapes, `TERMINAL`, block→`blocked`, claim/release not journaled) → zero implementer rework; the crew never opened the engine.
- commander-core's **headless feasibility-probe doctrine** predicted the bypass denial exactly; `--allowedTools Bash` recovered a full end-to-end. Distilled to lesson `headless-hook-probe-allowedtools` (scope constellation) — deferred at feedback (autonomous run, no charter latitude), carried here for the human: **add the `--allowedTools` non-bypass probe recipe to `skills/_shared/windows.md`.**
- Two minor doctrine frictions (recorded in AGENT_FEEDBACK 2026-07-12 issue-141): (1) a spine step's `check:null` **precondition** needs an explicit `attest ... --which preconditions` before `start` — not obvious from the imperatives; (2) the `feedback` step does not say plainly that the durable `AGENT_FEEDBACK.md` is the **primary-checkout** `.agent-work/` copy, not the linked worktree's — hit the invariant once before relocating. Suggest a one-line clarification in the feedback-step imperative.
- Crew: implementer under-applied the exact-string-casing rule for one asserted substring (handled correctly in-flight).
