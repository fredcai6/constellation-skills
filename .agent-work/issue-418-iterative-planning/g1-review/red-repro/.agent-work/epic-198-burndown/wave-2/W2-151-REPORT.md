# W2-151 Commander Report — Stop-rail subagent misattribution

**Commander:** commander-rail (delegated) · **Model:** opus
**Verdict: SHIPPED — PR open, not merged (Admiral merges).**
**PR:** https://github.com/fredcai6/constellation-skills/pull/201
**Branch:** `fix/stop-rail-attribution-151` @ commit `3743b62` (base main `7be19cf`)

---

## Isolation-script output (first action, from inside the worktree)
```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-rail
worktree OK: in C:/Programs/cs-wt-rail
EXIT: 0
```

## Chosen design + why
**Worktree-comparison** (the launch order's weak preference). The
`session_id -> {spine, engine_session, worktree}` binding written by
`handle_post_tool_use` already records the `worktree` the spine was claimed
under. A turn-end whose `cwd` is positively a **different** worktree than the
binding's is not that spine's driver:
- `decide_stop`: `return {}` (allow) on a foreign worktree, **before** the
  mid-flight/nudge logic — so a foreign stop records no nudge and never blocks.
- `decide_session_start`: re-inject the bound spine only when **not** foreign
  (launch-order direction 4); `_scan_active_spine` fallback unchanged.
- Two pure helpers: `_same_path` (normcase+normpath; **fail-safe `True`** so a
  comparison error never relaxes the rail) and `_foreign_worktree` (True **only**
  on a positive cwd/worktree mismatch, both present). **Absent `cwd` -> no
  relaxation** — the single-agent rail is never weakened.

**Why over the alternatives** (design-it-twice; launch order enumerated 4):
- *Transcript/agent-tagging* — rejected: heavier, and transcript identity is
  closer to agent-context than the already-stored environment fact.
- *SubagentStop registration* — rejected: it fires on the **subagent**, not the
  parent Stop that is the actual false positive, and adds a 4th registration
  against the frozen "three registrations only" contract.
- *decide_session_start same shape (direction 4)* — **adopted** (same guard).

## §D3 + escape hatch preserved
`cwd`/`worktree` are hook-supplied **environment** facts (the same source
PostToolUse already reads), not agent prose — §D3 holds. The 3-strike escape
hatch, `STUCK_MSG` text, all marker substrings, fail-open behavior, and the
binding on-disk structure are byte-unchanged (reviewer verified via `git diff`).
No new hook registration.

## Evidence
- **Regression test (load-bearing, production-shaped):**
  `tests/test_spine_rail.py::test_stop_foreign_worktree_parent_not_blocked` —
  drives the **real** `handle_post_tool_use` claim path (cwd = subagent worktree)
  to WRITE the binding, then `decide_stop` with the parent's (different) cwd
  while the bound spine is mid-flight → asserts `{} ` (parent NOT blocked) AND no
  nudge recorded. This proves the field-case fix through the real writer path,
  not a hand-set fixture.
- Companion tests: `test_stop_same_worktree_and_no_cwd_still_block` (single-agent
  rail intact), `test_session_start_foreign_skip_same_reinject_fallback_reinject`,
  helper fail-safe + Windows normcase coverage.
- **Full suite green:** `py -m pytest tests/test_spine_rail.py -q` → **41 passed**
  (was 33; +8 new). Re-run in the Commander's own hands; reviewer independently
  reproduced it plus a counterfactual probe (disabling `_foreign_worktree` makes
  the parent stop block again — proving the guard is load-bearing).
- **Reviewer verdict: APPROVE** (independent, 11 survey checks 0-fail, Fowler
  pass clean). Result: `.agent-work/archive/stop-rail-151/g1-review-result.md`.

## A verified assumption (cold-critic catch worth flagging)
The cold plan critic returned **NEEDS-REWORK**, headline: the fix rides on the
Stop payload carrying `cwd`, and hand-injected unit fixtures would pass green even
if production lacks it. Resolved: **verified** via the official Claude Code hooks
contract (claude-code-guide) that `cwd` is a common input field on **every** hook
incl. Stop and SessionStart, and **reshaped the regression test to drive the real
writer path**. Nuance: `cwd` is point-in-time (a `cd` can drift it) — launched-in-
different-worktree sessions do not coincide, so the fix holds; drift hardening is
triaged (TC3).

## Map impact
Reasoned **no-op**. Skill-source repo with no `docs/architecture` packet map for
`scripts/hooks/`. The change is a bug-fix within the frozen in-file design
contract (DESIGN_SPEC #138 ch.B docstring), which stays accurate (the `worktree`
field always existed in the binding; the §D3 environment-facts framing already
covers the comparison). No external schema/design doc touched.

## Triage candidates (recommend-and-defer — filing is the Admiral's per my latitude)
Full text: `.agent-work/archive/stop-rail-151/TRIAGE_RECOMMENDATIONS.md`.
- **TC1 (recommended)** — single-slot `binding[sid]` **clobbering**: a subagent's
  claim overwrites the parent's own entry, so the parent's *own* spine is
  unwatched during the overlap. This fix stops the parent being *blocked on the
  subagent's spine*; it does not restore own-spine watch. A **per-worktree-keyed
  multi-entry binding** fixes both the false-positive and this latent
  false-negative, and subsumes this PR. Confirmed real in-pattern: Admirals hold
  their own claimed spine (`ADMIRAL_SPINE.template.json`). Deferred as beyond this
  bounded fix's scope/risk in a safety rail.
- **TC2** — a subagent sharing the parent's **exact cwd** still false-positives;
  a fundamental §D3 (facts-only) discriminator limit. Decision: mandate/document
  worktree isolation for wave dispatch, or accept+document.
- **TC3** — `cwd`-drift hardening: compare against the spine **state-file** lease
  worktree (the claim passes `--worktree`) — a more D3-pure, drift-immune source.
- **TC4** — one-line docstring note for the Stop worktree guard (bundle into TC1).

## Workflow feedback (staged fenced trio — Admiral harvests)
This run is fenced off the read-only main checkout, so the feedback/lessons
closeout is **staged** at:
`C:/Programs/cs-wt-rail/.agent-work/staged-feedback/stop-rail-151/`
containing the trio + citation: `AGENT_FEEDBACK.md`, `lessons-delta.json`
(tick=true + 1 banked project lesson `verify-harness-field-and-drive-real-writer`),
`CONSTELLATION_FEEDBACK.md` (reasoned "none this run"), `FENCE.md`.
`verify_agent_feedback.py stop-rail-151 --phase feedback` and `--phase archive`
both exit 0 against the staged trio. **Harvest before sweeping the worktree.**

Top signals: (1) the cold-critic loop earned its keep (caught the masked
`cwd`-assumption). (2) Crew friction: the handoff's `_same_path` fail-safe spec
lightly contradicted test-case (d) — `str(None)` never raises — the implementer
correctly resolved to the controlling never-relax invariant (non-str → True).
(3) Minor: an unmet-precondition engine refusal could name the `attest` command.

## Merge note
PR #201 is **open, not merged**, per launch order (Admiral merges). No §D3 /
escape-hatch change was needed, so nothing was floated up mid-run.
