# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch (the PID changes every time).

- **step:** execute · item `g3-implement` — **COMMANDER PARKED AT A CONTEXT
  SEAM. THE g3 IMPLEMENTER CREW IS STILL RUNNING and will finish on its own.**
  Refresh-request filed as `e-g3-implement-1`.

  **A FRESH COMMANDER DOES EXACTLY THIS, IN ORDER:**
  1. re-claim the lease `commander-issue-456` **idempotently** — same id, NOT a
     takeover, no `--force`
  2. `--file .agent-work/issue-456/spine.json resume execute --session-id commander-issue-456 --reason "context refreshed"`
  3. `--file .agent-work/issue-456/execute.json resume g3-implement --session-id commander-issue-456 --reason "context refreshed"`
  4. Check whether the crew finished:
     `python scripts/run_crew.py --verify-result constellation/issue-456/g3/implementer/attempt-1`.
     If the result artifact
     `.agent-work/issue-456/crew-handoffs/g3-implement-RESULT.md` exists, read
     it, `attach` it as `implementer-result`, then `start`/`advance`
     `g3-implement`. If the crew parked instead, **abandon and relaunch a
     SUCCESSOR against the same plan** — do not restart the gate.
  5. Then the g3 REVIEW (handoff not yet written), then `g3-integrate`, then
     g4 g5 gb g6 g7 g8 gs, then `reconcile` → `triage` (tc1–tc38) → `review`
     → `feedback` → `archive`. **Release the lease LAST.**

  **CLI SHAPE:** `--file` goes BEFORE the verb, `--session-id` AFTER it.
  `advance` needs `--why "<understanding>"`. `claim` takes no `--actor`.
  `block` needs `--blocker`. `run_crew.py` takes `--result`, not `--expect`,
  and `--abandon --relaunch` TIMES OUT — use `--abandon` alone, then
  `--dispatch external`.

  **DO NOT `git add -A`.** Stage explicit paths. The untracked ~3,761-page
  `map/` tree is staged at `gs`, deliberately last.

  **What g3 has landed so far** (crew commits, may have grown since):
  `91da2500` RED / `0782ff2b` GREEN — the schema can say what a value IS;
  `4246e87d` RED — tc34, a definition inside a `with` block gets no page;
  `0d821d6f` GREEN — **the supplement stage is removed and the join it fed was
  RE-BASED**, which was the gate's named risk; `70b60555` RED / `68f4a2eb`
  GREEN — `ids.jsonl` carries authored ids, `{id, s}`, no position.
  **Verify the re-based join independently** — that is the whole point of the
  gate's risk section, and a re-based join standing on one derivation is a
  check that cannot fail.

  ---
  **ORIGINAL g3 DISPATCH NOTE FOLLOWS.**

  **g0 ✅ g1 ✅ g2 ✅ ARE ALL CLOSED AND INTEGRATED. Do NOT re-dispatch any of
  their crews** (13 registered, 0 unresolved) and do NOT redo their work.
  11 gates: g0 ✅ g1 ✅ g2 ✅ **g3** g4 g5 gb g6 g7 g8 gs

  **CURRENT BASELINE: `1744 passed, 2 skipped, 0 xfailed, 0 failed`.**
  `python -m scripts.code_map check` **exits 0, 6/6**. The old carry-forward
  that it correctly exits 1 is **SPENT**. `check` reads a **STALE** tree at
  `<root>/map` — run `build` first or the exit code means nothing.

  **THE g3 RISK, named in its handoff:** g3 removes the supplement stage, which
  is **one of the two independent derivations** `checks.entity_symbol_join`
  compares. Left standing on one source it becomes a check that CANNOT FAIL —
  the run's signature defect, arriving through a legitimate refactor. The crew
  must either re-base the join on a genuinely independent second derivation
  (proving independence by breaking each side in turn) or delete it and state
  what coverage was lost. Keeping it silently is a BLOCK.

  **tc38 STANDING RULE for every remaining gate:** before advancing any
  `*-integrate`, run its `-k` selector BY HAND and confirm it selects a
  NON-EMPTY set, then confirm that set can go red. `g2`'s matched zero tests,
  pytest exited 5, and the refusal looked like broken code rather than a broken
  check. Each gate's handoff must tell the crew its selector so the crew names
  its test classes to match. g3's is
  `-k 'schema or line_base or ids_jsonl'`.

  **THE OLD g2 NOTE, now history:** all three g2 defects landed red-then-green
  (`80702615`/`6d5b3131`, `fd9170f5`/`103d03b5`, `4ea174b3`/`cdfd8213`), the
  strict-xfail was forced off by its own strict flag, and the `INDEX` collision
  was deliberately LEFT COLLIDING because it is g1's only cross-platform
  falsifier for `page-accounting` (`tc35`).

  **`g2-implement` IS COMPLETE.** Two attempts: attempt-1 parked cleanly at a
  context seam with defect (a) red-committed; attempt-2 resumed the SAME plan and
  lease idempotently and finished all three. **Do NOT re-dispatch either.** All
  three defects red-then-green, each reproducer committed FAILING first:
  `80702615`/`6d5b3131` (a), `fd9170f5`/`103d03b5` (b), `4ea174b3`/`cdfd8213` (c).
  Suite **1729/2/1xfail → 1744 passed, 2 skipped, 0 xfailed, 0 failed** (+15).
  `python -m scripts.code_map check` now **exits 0**, 6/6 — the earlier
  carry-forward that it correctly exits 1 is now SPENT and no longer applies.
  The strict-xfail marker is deleted, forced off by its own strict flag exactly
  as g1 designed.

  **HIGHEST-RISK ITEM FOR THE REVIEWER:** (a) makes the store symbol equal the
  supplement key *by construction*, and the same change STRENGTHENED
  `entity_symbol_join` to a whole-symbol comparison. If both sides are now
  computed by one code path, that check may have become a check that cannot
  fail — the exact defect this run exists to stamp out. The review handoff
  names it as item 1.

  **TWO THINGS THAT MUST NOT HAVE BEEN FIXED:** `_make_collision_repo`'s `INDEX`
  collision must STILL collide (it is g1's only cross-platform falsifier for
  `page-accounting`), and no production symbol may be renamed in
  `scripts/run_skill_eval.py`.

  **g0 ✅ and g1 ✅ ARE BOTH CLOSED AND INTEGRATED. Do NOT re-dispatch any g0 or
  g1 crew** — all ten are terminal (`recover_crews`: 10 crews, 0 unresolved).
  **Do NOT redo any g0 or g1 work.** `g1-integrate` advanced with the engine
  re-running its own command check: exit 0, posix shell, full suite green.

  11 gates: g0 ✅ g1 ✅ **g2** g3 g4 g5 gb g6 g7 g8 gs

  **g2 CARRIES THREE DEFECTS, NOT THE TWO IN THE GATE SPEC.** The third was
  found by the Commander while writing the handoff and is ruled IN SCOPE:
  (a) D2 closure naming, (b) referenced-by count/list disagreement, and
  (c) **the page-filename case collision** — `render.py:414` writes
  `key.split(":",1)[1] + ".md"`, so `run_skill_eval:Verdict` and
  `run_skill_eval:verdict` resolve to ONE file on a case-insensitive
  filesystem. The gate-spec never named it, but `tests/test_code_map.py:917`
  says in its own words that **g2 renames**, and the strict-xfail there goes
  XPASS-red the moment g2 lands the fix, forcing the marker off. If g2 skips
  it, `python -m scripts.code_map check` stays red all the way through `gs`.

  **COMMANDER RULING, binding on the g2 crew:** the fix belongs to the MAP's
  page-naming, NOT to the source. Do **not** rename `class Verdict` or
  `def verdict` in `scripts/run_skill_eval.py` — production symbols are not
  renamed to suit the tool that reads them.

  **CARRY FORWARD TO EVERY LATER GATE:** `python -m scripts.code_map check`
  **exits 1 on this repository, correctly**, until g2 lands (c). `gs` and any
  CI wiring must expect that and must not read it as a regression.

  **Do NOT "fix" `entity_pages` by counting the tree again** — `tc24` corrects
  `tc18`; the root is `sizes` at `render.py:415`, which appends per *emit call*
  and feeds three fields. A second tree-count just manufactures a second
  self-agreeing field.

  **ALL 11 GATE COMMAND CHECKS WERE REPAIRED** at `g0-integrate` (`tc29`): each
  was authored as two commands joined by the prose word `AND` and could only
  ever fail through the engine's POSIX shell. Now ` && ` with
  `env -u FORCE_COLOR -u PYTHONIOENCODING` on each half. Do not reintroduce the
  old form.

- **slug:** work-id `issue-456` · branch `issue-456/code-map` (pushed to origin)
  · worktree `C:/Programs/constellation-skills/.claude/worktrees/issue-456`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-456/execute.json current` — then re-claim lease `commander-issue-456` idempotently (same id, NOT a takeover, no `--force`) and drive `execute.json` from `current`. Note: `--session-id` goes AFTER the verb, `--file` BEFORE it. Before any crew: `python scripts/recover_crews.py issue-456`, then dispatch only via `python scripts/run_crew.py --dispatch external --verify-result`.
- **pid:** none — the g2 reviewer is an Agent-tool subagent, not an OS
  process. Registry entry: `constellation/issue-456/g2/reviewer/attempt-1`.
  Recover with `python scripts/recover_crews.py issue-456`; a `resumable` crew
  is resumed in place via `SendMessage` to its agent id, a `needs-abandon` one
  via `run_crew.py --abandon <session> --relaunch`.
- **expected artifact:** immediate — `.agent-work/issue-456/crew-handoffs/g2-implement-RESULT.md`. Final — `.agent-work/issue-456/execute.json` with all 34 items `complete`, and each gate's `IMPLEMENTER_RESULT`/`REVIEW_RESULT` under `.agent-work/issue-456/crew-handoffs/`

**Baseline:** `1688 / 2 / 0` before `g0`; `1709 / 2 / 0` after the g0
remediation; **`1729 passed, 2 skipped, 1 xfailed, 0 failed` after g1**. Any red
below that line is this run's doing. When g2 lands (c), the xfail disappears and
the expected shape becomes `1730+ passed, 2 skipped, 0 xfailed`.

**STANDING LESSON, earned at `g0` and binding for the remaining nine gates:**
reproducing a falsifier that a crew designed only proves *that crew's probe*
works. A check claimed to be falsifiable must be attacked with a mutation its
author did **NOT** choose. The Commander missed this twice at `g0`; the
re-reviewer caught it, and `g1` applied it without being asked twice.

**TWO CREW OVERRULES SO FAR, BOTH CORRECT, BOTH FOUND BY RUNNING NOT READING.**
Most recently: the Commander specified a bare `xfail(strict=True)`; the crew
proved it would XPASS on a case-sensitive filesystem and turn CI red on Linux
while looking right on this Windows box. Crews are expected to overrule a
handoff they can falsify.

**THREE environment traps — all three confirmed real on this run.** Clear
`FORCE_COLOR` and `PYTHONIOENCODING` before trusting any suite number (`tc3`,
`tc7`), and **use `python`, never `py`** (`tc19`) — `py` has no pytest, so
`py -m pytest` dies with "No module named pytest" and reads as a silently green
run. That third one already reached three command postconditions in a crew's own
plan before being caught.

**Registry caveat (`tc22`, `tc25`, `tc30`):** `run_crew.py --abandon --relaunch`
TIMES OUT at 2 minutes while still registering the attempt, which then blocks the
follow-up dispatch as a duplicate. Use `--abandon` alone, then
`--dispatch external`. A relaunched crew reusing an abandoned attempt number
cannot be result-verified; verify it by reading its artifact and reproducing its
evidence by hand.

**Authority reminder for a fresh agent:** push and a full non-draft PR are
PRE-APPROVED for this work. **Merge to `main` is NOT approved.** Never
force-push. `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are
read-only corpora. Do **not** `git add -A` in this worktree — the untracked
3,635-page `map/` tree is staged at `gs`, deliberately last; stage explicit paths.

_Updated: 2026-08-08T02:20:00Z_
