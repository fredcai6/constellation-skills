# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch.

- **step**: `execute` (in-progress) · **slug**: `g5-implement` (dispatching now)
- **PID**: detached Agent subagent, `constellation/issue-456/g5/implementer/attempt-1`
- **expected artifact**: `.agent-work/issue-456/crew-handoffs/g5-implement-RESULT.md`
- **lease**: `commander-issue-456` — re-claim IDEMPOTENTLY (same id, NOT a takeover, no `--force`)

## Where the run is

CLOSED: `g0`, `g1`, `g2`, `g3`, **`g4`** (all advanced; `g4` closed on APPROVE
with `tc44` filed non-blocking).
NOW: **`g5`** — de-conflate the zero-inbound entities. Unused and untested look
identical today. Split the caller list into production and test callers and fix
the useless `referenced by: none found` line on test pages. **Do NOT delete test
pages — explicit ruling (critic IF7 over SY8).** `g5` also owns **`tc32`** (a
green determinism run is NOT evidence of stable caller ordering).
REMAINING AFTER: `gb g6 g7 g8 gs`, then
`reconcile → triage → review → feedback → archive`. **Release the lease LAST.**

## Resume recipe

```
python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py \
  --file .agent-work/issue-456/spine.json resume execute --session-id commander-issue-456 --reason "<why>"
python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py \
  --file .agent-work/issue-456/execute.json current
```

CLI shape: `--file` goes **BEFORE** the verb; `--session-id` **AFTER** it (and
`current` takes **no** `--session-id`). `advance` needs a positional id **and**
`--why`. `claim` takes no `--actor`. `block` needs `--blocker`. `attest` uses
`--cond` + `--which` (+ `--evidence` for postconditions). `attach` uses `--type`
+ `--payload-file`. **Evidence TYPE is enforced** — a postcondition wanting
`implementer-result` rejects `--type artifact`. **Evidence FIELDS are enforced**
— a postcondition wanting `{'verdict':'APPROVE'}` rejects `APPROVE-WITH-FINDINGS`;
put the reviewer's own three-way label in a second key.
`flag-candidate` uses `--from` + `--statement`.

## Crew model — settled 2026-08-08

The human asked; the registry said **`opus` ×9**. Corrected: from `g3-review` on,
**dispatch crews at `sonnet`** (`--model sonnet` to `run_crew.py` AND
`model: "sonnet"` on the Agent call). Haiku declined for **reviewer** roles (a
rubber-stamp review is the exact defect this run hunts); try haiku on a
mechanical gate and **measure it**. The `g3`/`g4` sonnet crews each caught
something the Commander missed — quality held.

## Standing rules

- **tc38**: a check that can only ever FAIL is as informationless as one that
  cannot fail. Tell every crew its own gate selector up front and make it run the
  selector by hand. `g5` selector: `-k 'refs or caller'` → **11 collected** today.
- **tc36**: a handoff naming an exclusion without naming **where** the tripwire
  sits makes every successor rediscover it at full cost.
- Reproducing a falsifier its author designed proves only that probe works —
  attack with a mutation the author did NOT choose.
- red-before-green: every reproducer committed in its FAILING state before the fix.
- **Six** Commander errors caught by crews so far, every one by running rather
  than reading. Tell each crew it is expected to overrule the handoff.

## Numbers at this boundary

- suite **1772 passed, 2 skipped, 672 subtests, 0 failed, 0 xfailed**
- fresh `build` then `check` → **7/7, exit 0**. `check` reads a **stale** tree at
  `<root>/map`; run `build` first or the exit code means nothing.
- render report: modules **111**, entities **3728**, pages **3840**, ids 0
- `git ls-tree -r HEAD --name-only -- map/` → **0** tracked files
- zero `:<line>` across all 3840 pages (the human's strip-the-line-numbers ruling)
- CARRY-FORWARD SPENT: the old note that `check` "correctly exits 1" is dead.
- Use `python`, **never `py`** (`py -m pytest` dies "No module named pytest" and
  reads as a silently green run).

## Authority

- Push and a **full non-draft PR** are **PRE-APPROVED**. **Merge to `main` is NOT.**
- Never force-push. Never merge.
- **Do NOT `git add -A`** — the untracked ~3,840-page `map/` tree is staged at `gs`,
  deliberately last. Stage explicit paths only.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
  `superCoolSpaceSim` is **C++/Obj-C with ZERO tracked `.py`** — it indexes to 0
  modules. It is a **null test, never a cross-corpus shape test**. `f1Brainz`
  (1227 modules / 15037 entities) is the only real second Python corpus.
- Worktree isolation refuses compound Bash with loops, `env -u`, heredocs,
  `$(...)`, `VAR=x && ...` chaining, or long quoted strings. Use plain separate
  commands, script files, `git commit -F <file>`. Working env form:
  `unset FORCE_COLOR PYTHONIOENCODING && python ...`.
- **Shell-quoting workaround (tc43)**: engine verbs taking free text fail on any
  real message. Wrapper scripts that read text from a file and pass list argv via
  `subprocess` live in `.agent-work/issue-456/evidence/` — `run_record.py`,
  `run_waive.py`, `run_consolidate.py`, `run_flag_candidate.py`. **Reuse them.**
- Ask the human decisions in **plain text**, never `AskUserQuestion`.

## Gate assignments still to honor

- **g5** owns `tc32` (a green determinism run is not evidence of stable caller order).
- **tc35** (INDEX collision family) needs `g1`'s `page-accounting` falsifier rebuilt
  on a DIFFERENT collision FIRST.
- **tc39** (governor HARD band at ~16% of real fill), **tc42** (Fowler rail's
  unsubstitutable `<fowler-pass-record-path>` placeholder — four consecutive
  reviewers force-waived it) and **tc43** route to **feedback**, not a gate.
- **tc44** (routing tier degenerates on the flat 74% tests package) — triage.
- **gs** needs an explicit "rebuild, then stage" line and must expect `check`
  **exit 0**.
- Triage must drain **tc1–tc44**.

## The tripwire map (where each protected thing physically sits)

- `checks.py` `REFS_PREFIX` / `REFS_LEGEND` / `REFS_MODULES` / `parse_refs` are
  declared **independently** of `render.py`'s copies **on purpose** — a check that
  reads its expected text out of the code under test can only ever agree with it.
  **`g5` changes this grammar, so `g5` is the gate most at risk of collapsing that
  independence into an import.**
- `_make_collision_repo`'s `INDEX` collision is `g1`'s only cross-platform
  falsifier for `page-accounting` and must keep colliding.
- `OWN_MODULE_NAMED_MUTATION`'s byte-exact anchor in `render.py`.
- `entity_symbol_join`'s two independent derivations (`extract.child_sym` vs
  `checks.SourceScan`) must stay independent — `g3`'s whole gate proved that.
