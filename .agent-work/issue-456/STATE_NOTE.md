# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch.

- **step**: `execute` (in-progress) · **slug**: `g5-remediate` — **DISPATCHED** 2026-08-08
- **PID**: crew `constellation/issue-456/g5/implementer/attempt-2`, Agent name `g5-remediator`,
  model `sonnet`. Recover with `SendMessage` to that name (externally dispatched —
  `recover_crews.py` will report it RESUMABLE, which means nudge in place, never relaunch).
- **REGISTRY GOTCHA (new, 2026-08-08):** `recover_crews.py` reported `0 unresolved` while
  `run_crew.py` still REFUSED the launch as a duplicate — the two disagree. An externally
  dispatched crew stays `running` in the registry until you close it explicitly with
  `run_crew.py --verify-result <session-name>`. That is the correct close for a crew that
  finished; `--abandon` would misrecord a successful attempt. Both `g5` attempt-1 entries
  (implementer and reviewer) were verified and closed this way before attempt-2 registered.
- **expected artifact**: `.agent-work/issue-456/crew-handoffs/g5-remediate-RESULT.md`
- **lease**: `commander-issue-456` — re-claim IDEMPOTENTLY (same id, NOT a takeover, no `--force`)

## Where the run is

CLOSED: `g0`, `g1`, `g2`, `g3`, `g4`.
**`g5` is NOT closed — the review returned `BLOCK` and the block is correct.**
`g5-implement` and `g5-review` are both `complete`; `g5-integrate` must NOT be
advanced on a BLOCK. **Next action: dispatch the remediation crew** with the
ready handoff at `.agent-work/issue-456/crew-handoffs/g5-remediate.md`, at
**`--model sonnet`**, role `implementer`, gate `g5` (it will register as
`attempt-2`). Then re-review, then `g5-integrate` on an APPROVE.

### The block, in one line

`SPLIT_LEGEND` — printed on all **3864** pages — says the split keys on a
**top-level** `tests` package; `is_test_module` is `return "tests" in parts`,
matching a `tests` segment **anywhere**. Confirmed in BOTH hand-independent
copies by reviewer and Commander. **Commander's ruling: fix the LEGEND, keep the
PREDICATE, add the pinning check** (precedent: `RefsAccountingTests.
test_the_legend_names_the_predicates_the_count_actually_counts` pins
`REFS_LEGEND`). Reclassifies zero entities, so all measured numbers stand.

### What g5 already got RIGHT (do not redo)

Two attributed lines per page; `TEST_NOTE` on 2789 test-defined pages and 0
production-defined; test pages NOT deleted (IF7 over SY8); `tc32` genuinely
closed and attacked with three unchosen mutations; the hand-restated
`is_test_module` in `checks.py` **proven load-bearing** (diverging only that copy
made TWO checks go red) — which retires the standing worry that this gate would
collapse `g2`'s two-independent-declarations design.

### The corrected split — measured twice independently, agreeing exactly

| bucket | prod-defined | test-defined |
|---|---|---|
| unused | **88** | **2340** |
| test-only | **2** | 449 |
| production | 873 | 0 |

The crew's shipped headline of "unused 2428 (64.7%)" is **96.4% test-defined**.
Genuinely unused production code is **88**, not 2428 — a 27x difference.

REMAINING AFTER `g5`: `gb g6 g7 g8 gs`, then
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

- **g5** owned `tc32` — **CLOSED and attacked**, no longer outstanding.
- **CANDIDATE NUMBERING TRAP:** `execute.json` has its OWN candidate counter. The
  two candidates filed at `g5-review` print as **`tc2`/`tc3`** but are the
  run-wide **`tc45`/`tc46`**. Triage must not double-count. `tc45` = nothing pins
  a printed legend to the predicate the code applies (generalize past
  `SPLIT_LEGEND`). `tc46` = a gate's own evidence script reproduced the exact
  conflation the gate removed, and evidence scripts get no adversarial read.
- **tc39 CONFIRMED AGAIN, live:** the context governor's HARD band fired at
  **15%** fill and refused `advance` until a `refresh-request` was attached. The
  crew independently hit the undocumented `why_ref` rule — it must cite the
  **CURRENT latest** why-record id, and **every** `advance` mints a new one, so a
  cited id goes stale immediately. Read `why_trail[-1].id` and attach in the same
  breath. Both route to **feedback**.
- **New from the g5 crew, for feedback:** a `command` postcondition ALWAYS
  re-runs and cannot be satisfied by reference to evidence already gathered the
  way `attest --evidence` can — so one `advance` re-ran a ~5-minute full suite
  that had just been run by hand.
- **Non-blocking, carried forward:** 386 pages are non-ASCII, every one traced to
  PRE-EXISTING docstring prose (an em-dash in `scripts/agent_work_root.py`).
  `g5`'s own strings are pure ASCII. Not `g5`'s defect; do not re-litigate.
- **Line-position ruling, precisely restated:** **0 of 3864 page HEADERS** carry a
  line position. Three pages do contain a `.py:<line>` string — all inside
  docstring prose the map reproduces verbatim from source. That is correct
  behaviour, not a header defect. Do not "fix" it by censoring source text.
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
