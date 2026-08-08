# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these five lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch (the PID changes every time).

- **step:** execute · item `g1-implement` — **in-progress, implementer crew
  dispatched.** **`g0` IS FULLY CLOSED** on an APPROVE verdict
  (`e-g0-integrate-1`); do **not** reopen it and do **not** re-dispatch any g0
  crew — all seven are terminal (`recover_crews`: 0 unresolved).

  Crew: handoff `crew-handoffs/g1-implement.md`, slot
  `constellation/issue-456/g1/implementer/attempt-1`, result expected at
  `crew-handoffs/g1-implement-RESULT.md`.

  **`g1` REWRITES `scripts/code_map/checks.py`** — today every function prints
  and `run()` ends in a literal `return 0`, so a broken map passes. Three
  families only: nonzero exit on failure; determinism (double build
  byte-identical); structural assertions provable by mutation (caller set vs an
  independent full scan; referenced-by count vs its own list). Corpus-count
  thresholds and render-shape baselines belong to `gB`, NOT here.

  **THE KEY CALL IN THIS GATE, already made and written into the handoff:** the
  best check available is RED today. `pages - 1 - modules` = 3535 vs
  `entity_pages` = 3536, differing by exactly the `Verdict`/`verdict` filename
  collision. `g1` ASSERTS it; `g2` owns the rename that fixes it. It ships as
  `xfail(strict=True)` so that when `g2` lands the rename the XPASS turns the
  suite red and forces the marker off — the defect cannot be silently left
  behind and the check cannot be silently left disabled. `tc26` (a zero-byte
  page is invisible to `rglob`) folds in here too. **Do NOT "fix"
  `entity_pages` by counting the tree again** — `tc24` corrects `tc18`; the root
  is `sizes`, which feeds three fields.

  **ALL 11 GATE COMMAND CHECKS WERE REPAIRED** at `g0-integrate` (`tc29`): each
  was authored as two commands joined by the prose word `AND` and could only
  ever fail through the engine's POSIX shell. Now ` && ` with
  `env -u FORCE_COLOR -u PYTHONIOENCODING` on each half. Do not reintroduce the
  old form.

  11 gates: g0 ✅ g1 g2 g3 g4 g5 gb g6 g7 g8 gs
- **slug:** work-id `issue-456` · branch `issue-456/code-map` (pushed to origin)
  · worktree `C:/Programs/constellation-skills/.claude/worktrees/issue-456`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-456/spine.json current` — then re-claim lease `commander-issue-456` idempotently (same id, NOT a takeover, no `--force`), read the DIGEST, and drive `.agent-work/issue-456/execute.json` from `current`. Before any crew: `python scripts/recover_crews.py issue-456`, then dispatch only via `python scripts/run_crew.py --dispatch external --verify-result`.
- **pid:** none — the g0 approve-reviewer is an Agent-tool subagent, not an OS
  process. Registry entry:
  `constellation/issue-456/g0/reviewer/attempt-3`. Recover with
  `python scripts/recover_crews.py issue-456`; a `resumable` crew is resumed in
  place via `SendMessage` to its agent id, a `needs-abandon` one via
  `run_crew.py --abandon <session> --relaunch`.
- **expected artifact:** immediate — `.agent-work/issue-456/crew-handoffs/g0-approve-RESULT.md`. Final — `.agent-work/issue-456/execute.json` with all 34 items `complete`, and each gate's `IMPLEMENTER_RESULT`/`REVIEW_RESULT` under `.agent-work/issue-456/crew-handoffs/`

**Baseline:** `1688 / 2 / 0` before `g0`; `1706 / 2 / 0` after the g0 build;
**`1709 passed, 2 skipped, 0 failed` after the remediation**, reproduced
independently by the Commander in a cleared environment twice. Any red below
that line is this run's doing.

**STANDING LESSON, earned at `g0` and binding for the remaining ten gates:**
reproducing a falsifier that a crew designed only proves *that crew's probe*
works. A check claimed to be falsifiable must be attacked with a mutation its
author did **NOT** choose. The Commander missed this twice at `g0`; the
re-reviewer caught it with N4/N5/N8.

**THREE environment traps — all three confirmed real on this run.** Clear
`FORCE_COLOR` and `PYTHONIOENCODING` before trusting any suite number (`tc3`,
`tc7`), and **use `python`, never `py`** (`tc19`) — `py` has no pytest, so
`py -m pytest` dies with "No module named pytest" and reads as a silently green
run. That third one is the dangerous one: it already reached three command
postconditions in a crew's own plan before being caught.

**Registry caveat (`tc22`, `tc25`):** a relaunched crew reuses an abandoned
attempt number and then **cannot be result-verified** — `--verify-result`
refuses with "cannot verify an abandoned crew". `crew-runs.json` also held four
entries under one id, and `--dispatch` refused a slot three times naming a
COMPLETE crew while `--abandon` reported success without clearing it. Verify
such a crew by reading its result artifact and reproducing its evidence by hand.

**Authority reminder for a fresh agent:** push and a full non-draft PR are
PRE-APPROVED for this work. **Merge to `main` is NOT approved.** Never
force-push. `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are
read-only corpora. Do **not** `git add -A` in this worktree — the untracked
3,635-page `map/` tree is staged at `gs`, deliberately last; stage explicit paths.

_Updated: 2026-08-08T00:20:00Z_
