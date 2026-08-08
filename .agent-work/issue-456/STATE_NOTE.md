# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch.

- **step**: `execute` (in-progress) · **slug**: `gb-implement` — **DISPATCHED** 2026-08-08
- **PID**: crew `constellation/issue-456/gb/implementer/attempt-1`, Agent name
  `gb-implementer`, model `sonnet`. Recover with `SendMessage` to that name
  (externally dispatched — nudge in place, never relaunch).
- **expected artifact**: `.agent-work/issue-456/crew-handoffs/gb-implement-RESULT.md`
- `gb-implement.p1` already **attested**. Handoff written at
  `.agent-work/issue-456/crew-handoffs/gb-implement.md`.

## `g5` IS CLOSED — `g5-integrate -> complete` on an APPROVE

**CLOSED: `g0` `g1` `g2` `g3` `g4` `g5`.** Six of eleven. Remaining: **`gb` `g6`
`g7` `g8` `gs`**, then `reconcile → triage → review → feedback → archive`.

### `tc47` — the trap that nearly ate the gate close, READ THIS BEFORE ANY GATE

`g5-integrate`'s own postcondition `c1` selected `-k 'caller_split'` — **a name no
test in this repo has ever carried**. It collects **ZERO** tests and pytest exits
**5**, so the `&&` chain could never pass however correct the code was. This is
`tc38`'s defect class in the PLAN's own check. It survived plan review, all of
`g5-implement`, a BLOCK, a remediation and a re-review, because **nothing runs a
gate's own postcondition command until `advance`**.

**Repaired** by `amend --delta ... retext-check` (authority `commander`) to
`-k 'CallerSplit'`, which collects **7** and passes. Only the selector changed;
statement, env prefix and the human-authority override policy untouched — nothing
was waived. Discrimination proved: the remediation's red-before-green ran a test
inside that very class RED at exit 1.

**DO THIS AT EVERY REMAINING GATE:** before dispatching, run that gate's own
`c1`/`c2` command postcondition **by hand** and confirm any test selector collects
a **non-zero** count. Exit 5 is "no tests collected" — categorically different
from a red, and it looks like diligence.

### ALL REMAINING SELECTORS ALREADY SCANNED — done 2026-08-08, do not redo

Scanner: `C:/Users/fredc/.claude/jobs/9cbc67f4/tmp/scan_selectors.py`.

| gate | closing selector | collects today |
|---|---|---|
| `gb-integrate` | `baseline or churn or recall or ascii` | **17** ✅ |
| `g6-integrate` | `stale_tag` | **0** (rc 5) |
| `g7-integrate` | `comment_tags` | **0** (rc 5) |
| `g8-integrate` | `bom or docstring` | **2** ✅ |
| `gs-integrate` | `map_tree_freshness` | **0** (rc 5) |

**The three zeroes are NOT `tc47` defects.** Those gates have not been built yet,
so the selector is a **specification**: "this gate must produce a test matching
this name." That is red-by-absence, a legitimate grade-B falsifier.

**But this is EXACTLY how `g5`'s trap formed** — `g5`'s crew created its tests as
`ProductionTestCallerSplitTests` while the plan waited on `caller_split`, and the
mismatch only surfaced at close. So: **every remaining implementer handoff MUST
state the gate's exact closing selector and require the new tests to match it**,
and the crew must run that selector by hand and report the count. `g6`, `g7` and
`gs` each need a test whose name contains, respectively, `stale_tag`,
`comment_tags`, `map_tree_freshness`.

### Engine details learned this gate

- `amend --delta` op key is **`"op"`, not `"kind"`** (a `"kind"` key fails with the
  unhelpful `unknown op kind None`).
- `retext-check` accepts a **pending or in-progress** gate; `reopen` a complete one.
- **Registry vs recovery disagree:** `recover_crews.py` reports `0 unresolved`
  while `run_crew.py` REFUSES the launch as a duplicate. An externally dispatched
  crew stays `running` until closed with
  `run_crew.py --verify-result <session-name>` — the correct close for a crew that
  finished. `--abandon` also frees the hold but **misrecords a successful attempt**.
- `.agent-work/issue-456/evidence/run_flag_candidate.py` points at the **reviewer's**
  engine and takes 4 args. Commander wrappers that work are in the job tmp dir:
  `run_advance.py`, `run_amend.py`, `run_attest.py`, `run_flag.py`.

### Candidates filed at `g5-integrate` (numbering trap still applies)

`execute.json`'s own counter printed these as **`tc4`/`tc5`**; run-wide they are
**`tc47`/`tc48`**. Run-wide total is now **tc1–tc48**. Triage must not double-count
— and `tc48` is ALSO the g5 re-review survey's own `tc1`, re-filed so the drain
list holds it in one place.

- **`tc47`** = a gate's own postcondition can be a check that could only ever fail;
  run test selectors at authoring time; `exit 5` should never read as a normal red.
- **`tc48`** = the new pinning test guards one literal string, not the defect class.
  The re-reviewer mutation-proved it: four differently-worded top-level-only
  overclaims that avoid the literal "top-level" all survive undetected. Not a
  blocker — its docstring does not overclaim, and its behavioural half is a full
  general pin. Joins **`tc45`**; the robust form derives the legend's prose from the
  predicate's own literal values.

### Also for feedback, new this gate

`tc42` may be **retired**: the g5 re-reviewer resolved `<fowler-pass-record-path>`
to a real path **at instantiation, before `claim`**, and needed **no waiver** —
the first of six reviewers to get the normal path. The template's imperative text
should state that as the default expectation.

## REMEDIATION LANDED — commit `588d5419`, verified by the Commander

The `BLOCK` defect is fixed. Legend reworded in BOTH hand-independent copies to
"a tests package anywhere on the module path"; pinning test added guarding both
directions of drift; `measure_split.py` now carries the definer dimension.
Commander-verified independently: **no import** between the copies; fresh `build`
then `check` → **7/7 exit 0**; modules 111, entities **3753**, pages **3865**;
suite **1781 passed / 2 skipped / 672 subtests / 0 failed**; commit is explicit
paths only with **0** tracked `map/` files.

**The one moved number is benign and confirmed:** `unused_test_defined` 2340 →
2341, because the new pinning test is ITSELF a newly mapped entity with no
callers (this repo self-indexes `tests/`). Corroborated by entities 3752 → 3753
and pages 3864 → 3865. A NEW entity, not a reclassified one. All five other
cells byte-identical: 88 / 2 / 449 / 873 / 0.

**Exactly 1 of 3865 pages** still contains "top-level tests package" — the new
test's own page, whose docstring quotes the old legend to explain what it guards.
Correct behaviour, not a leftover. **Do not "fix" it.**

**NEW candidate for triage (tc47):** this repo's `code_map` self-indexes
`tests/test_code_map.py`, so any test added under TDD changes the repo's own map
by +1 entity/page. It cost the crew one failed `advance` on hardcoded counts.
Belongs in `CREW_CONTEXT.md`.

**NEW for feedback:** `current` does not surface the latest `why_trail` id, so the
`tc39` refresh-request recovery forces a crew to read the plan JSON directly — a
documented exception to "never read the JSON for state". Ask for a
`latest_why_id` field or an `attach ... --why-ref latest` shorthand.
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
