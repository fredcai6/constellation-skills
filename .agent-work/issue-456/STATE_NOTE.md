# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch.

- **step**: `execute` (in-progress) · **slug**: `g4-implement` (pending, nothing dispatched)
- **PID**: none in flight — parked at a CLEAN GATE BOUNDARY
- **expected artifact**: `.agent-work/issue-456/crew-handoffs/g4-implement-RESULT.md` (not yet written)
- **lease**: `commander-issue-456` — re-claim IDEMPOTENTLY (same id, NOT a takeover, no `--force`)

## Where the run is

CLOSED: `g0`, `g1`, `g2`, **`g3`** (all three items advanced 2026-08-08; the
engine re-ran `g3-integrate`'s command check itself and it passed).
NEXT: `g4` — the top index must ROUTE, not list. Gate task: a flat list of every
module is not a routing surface; the trial agent read 60 lines and learned
nothing. Add a second tier. **Corpus-shape trap named by critic F9: 75% of this
repo's entities are test code, so a tier that only works for `src/` will look
fine here and fail elsewhere.** `g4` also owns `tc31` (nothing ties a page's
location to its content).
REMAINING AFTER: `g5 gb g6 g7 g8 gs`, then
`reconcile → triage → review → feedback → archive`. **Release the lease LAST.**

## Resume recipe

```
python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py \
  --file .agent-work/issue-456/spine.json resume execute --session-id commander-issue-456 --reason "<why>"
python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py \
  --file .agent-work/issue-456/execute.json current
```

CLI shape: `--file` goes **BEFORE** the verb; `--session-id` **AFTER** it (and
`current` takes no `--session-id`). `advance` needs a positional id **and**
`--why`. `claim` takes no `--actor`. `block` needs `--blocker`. `attest` uses
`--cond` + `--which`. `attach` uses `--type` + `--payload-file`/`--field`.
`flag-candidate` uses `--from` + `--statement`. `amend` uses `--delta <file>` +
`--reason` + `--authority`. `retext-check` corrects a command check's text and
resets satisfaction so nothing is grandfathered.

## Crew model — CHANGED 2026-08-08

The human asked what the crews run on. The registry says **`"model": "opus"` ×9** —
every crew through `g3-implement`. The human wants **sonnet**, or haiku where it
is easy enough. From `g3-review` on: **dispatch crews at `sonnet`.** Haiku is
declined for reviewer roles specifically (a rubber-stamp review is the exact
defect this run is hunting); try haiku on a mechanical gate and **measure it**.
Pass `--model sonnet` to `run_crew.py` so the registry records it, and set
`model: "sonnet"` on the Agent call.

## g3 — RESOLVED, for the record

The gate's whole risk (deleting one of the two independent derivations
`entity_symbol_join` compared) is **retired by measurement**. The reviewer
attacked the re-based check on the real 3711-entity corpus with mutations
neither the implementer nor `g2`'s reviewer chose: control green 6/6;
flattening `extract.child_sym` → `FAIL entity-symbol-join: 3896`; stopping
`checks.SourceScan._walk` qualifying by `ClassDef` → `FAIL: 4367`. Both
isolated to 1 of 6 — both sides load-bearing, not a tautology.
`tc34` closed (8 gained / 0 lost, re-derived, plus an own with-block fixture).
`ids.jsonl` byte-identical under a 24-line code MOVE. `tc40` judged — filed as
`tc41`, non-blocking.

## Standing rules

- **tc38**: a check that can only ever FAIL is as informationless as one that
  cannot fail. Tell every crew its own gate selector up front and make it run the
  selector by hand. This worked at `g3` (21 tests) after failing at `g2` (zero).
- **tc36**: a handoff that names an exclusion without naming **where** the tripwire
  sits makes every successor rediscover it at full cost.
- Reproducing a falsifier its author designed proves only that probe works.
- red-before-green: every reproducer committed in its FAILING state before the fix.

## Numbers at this boundary

- suite **1767 passed, 2 skipped, 0 failed, 0 xfailed** (672 subtests)
- `build` then `check` → **6/6 ok, exit 0**. `check` reads a **stale** tree at
  `<root>/map`; run `build` first or the exit code means nothing.
- `git ls-tree -r HEAD --name-only -- map/` → **0** tracked files
- CARRY-FORWARD SPENT: the old note that `check` "correctly exits 1" is dead.
- Use `python`, **never `py`** (`py -m pytest` dies with "No module named pytest"
  and reads as a silently green run).

## Authority

- Push and a **full non-draft PR** are **PRE-APPROVED**. **Merge to `main` is NOT.**
- Never force-push. Never merge.
- **Do NOT `git add -A`** — the untracked ~3,761-page `map/` tree is staged at `gs`,
  deliberately last. Stage explicit paths only.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Worktree isolation refuses compound Bash with loops, `env -u`, heredocs, or
  `$(...)`. Use plain separate commands, script files, `git commit -F <file>`.
  Working env form: `unset FORCE_COLOR PYTHONIOENCODING && python ...`.
- Ask the human decisions in **plain text**, never `AskUserQuestion`.

## Gate assignments still to honor

- **g4** owns `tc31` (nothing ties a page's location to its content).
- **g5** owns `tc32` (a green determinism run is not evidence of stable caller order).
- **tc35** (INDEX collision family) needs `g1`'s `page-accounting` falsifier rebuilt
  on a different collision FIRST.
- **tc39** (governor HARD band at ~16% of real fill) routes to **feedback**, not a gate.
- **gs** needs an explicit "rebuild, then stage" line and must expect `check` **exit 0**.
