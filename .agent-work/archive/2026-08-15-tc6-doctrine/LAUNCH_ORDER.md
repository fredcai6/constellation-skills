# Launch Order: `tc6-doctrine` — the docs now describe an engine that no longer exists

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

## Mission

Worktree-isolation doctrine disagrees with itself across three surfaces, and **one of them is now
actively false.** Reconcile them against what the engine does at `main` `0646d61b`.

**Measure before you write.** Three merges landed today — #577/#585 earlier, then #588 (`84ecee99`) this
afternoon — and this order was drafted against a snapshot. **Verify every claim below against the live
tree first.** Where I am wrong, say so; that is a finding, not an inconvenience.

## The authority for what is now true

`/home/tommy/projects/constellation-skills/.agent-work/rulings/2026-08-15-worktree-identity.md`

Untracked, in the **primary checkout** — your worktree does not contain it. **Read it in full first.**
It is the ruling #588 implemented, and it is the source of truth for what the engine now does.

---

## Task 1 — `docs/CHECKLIST_SCHEMA.md` is stale as of this afternoon (highest priority)

Lines ~120–126 describe the **superseded** behavior. Verbatim, currently:

> On every **guarded** verb, `origin_worktree_refusal` compares `origin.worktree` against the engine's
> own `Path.cwd()`; when cwd is neither that directory nor inside it, the engine prints `REFUSED:` …
>
> **Containment, not equality**: `<worktree>/scripts` and `<worktree>/.agent-work/<id>` pass, and the
> comparison is segment-wise, so a sibling sharing a name prefix (`/w/repo-2` against `/w/repo`) does not.

**All of that changed in `84ecee99`.** What the engine does now:

- The **call site** in `main()` resolves the engine's cwd to its **git worktree toplevel**
  (`git rev-parse --show-toplevel`) and passes that to the predicate.
- The predicate compares by **equality**, not containment, and stays **pure** — no subprocess, no
  filesystem, no ambient cwd read. `tests/test_spine_origin_isolation.py::test_it_is_pure` enforces that.
- **Fail-closed**: an origin-carrying spine whose cwd yields no git toplevel is **refused**. This check
  is ordered *after* the malformed-shape fallbacks, so origin-less spines stay drivable from anywhere.
- Subdirectory work still passes — but for a different reason. Not containment: toplevel resolved from
  `<worktree>/scripts` **is** `<worktree>`, so equality holds. **Say why, not just that it works.**

Two things in that section are still correct and must **survive** your edit:

- The guarded/exempt verb sets and the reasoning for them (`current` is read cross-tree for a
  `REFRESH REQUESTED` line; `release` is the recovery escape hatch for a spine whose worktree is gone).
- The withdrawal: *"It does not make the comparison unforgeable — the engine reads its ambient cwd, and a
  check authored as `cd <origin.worktree> && …` still satisfies it."* **Still true after #588**, and the
  ruling explains why it is accepted rather than overlooked: `mcp_spine_server`'s
  `_standing_in_the_bound_spines_worktree` structurally depends on it, because `spine_open` creates a new
  worktree and no process can already stand in a directory that did not exist a moment earlier. **Do not
  restate a stronger claim than that.**

---

## Task 2 — the launch-order template still mandates the superseded check

`skills/admiral/templates/LAUNCH_ORDER.template.md:43` tells every Commander:

> First step, before any git operation: run `python <admiral-skill-dir>/scripts/verify_worktree_isolation.py --here <absolute worktree path>` — it must exit 0 …

and `:76` requires its output as return evidence. Meanwhile `CHECKLIST_SCHEMA.md:124` says the
engine-native guard **supersedes** that check.

**This needs judgment, not a mechanical edit, and the judgment is yours to make and defend.** They are
not obviously the same thing: the schema says the engine superseded the *per-template `command` check* on
the Commander spine's `init` precondition `c0`. The template's line 43 is a **first-step instruction to a
human-or-agent**, which is a different mechanism and may still earn its place as an independent,
early, human-readable signal.

Decide **one** of:

- **(a)** It is genuinely redundant now — the engine refuses every guarded verb anyway — so drop or demote it.
- **(b)** It remains valuable as a distinct early check, in which case say **how it differs** from the
  engine guard, so a reader stops perceiving a contradiction.

**Whichever you choose, the contradiction must be gone and the reasoning written down.** Note that lines
46–54 of that template — "Isolation is git-only — hook code is not fenced by it," and the
`CLAUDE_PROJECT_DIR` inheritance problem — are, as far as I know, **still accurate and still load-bearing**.
Verify, then leave them.

---

## Task 3 — the third surface

`skills/workbench/references/checklist-engine.md` was recorded as the third disagreeing surface, but my
own grep found only lease/door mechanics there, not isolation doctrine. **Re-measure it.** If it carries
no isolation claim needing reconciliation, **say so plainly** — "the recorded third surface does not
exist as described" is a perfectly good finding and better than inventing an edit to justify the task.

While you are measuring, sweep for **any other** surface asserting containment, `Path.cwd()`, or
`verify_worktree_isolation.py` as current engine behavior. `grep -rn` across `docs/` and `skills/`.
Anything you find and do not fix, record in findings.

---

## Pre-Rulings — settled

1. **`decision:engine-is-truth` — settled.** Docs follow the engine, never the reverse. **You have no
   authority to change behavior** — this lane edits documentation only.
2. **`decision:forgery-stays-named` — settled.** The unforgeability withdrawal stays; do not upgrade it.
3. **`decision:judgment-on-task-2` — settled.** Pick (a) or (b) and defend it. Leaving the contradiction
   standing is not an option.
4. **`decision:honest-null` — settled.** If Task 3's premise is wrong, report that instead of manufacturing work.
5. **`decision:clear-caches-before-measuring` — settled.**

## File Ownership

**Yours:** `docs/CHECKLIST_SCHEMA.md`, `skills/admiral/templates/LAUNCH_ORDER.template.md`,
`skills/workbench/references/checklist-engine.md`, plus any other doc your sweep shows is wrong. Your work
area.

**NOT yours — no behavior changes in this lane:** `scripts/checklist_engine.py`,
`scripts/verify_worktree_isolation.py`, `scripts/hooks/spine_rail.py`, `scripts/mcp_spine_server.py`, any
test file. Also not yours: `scripts/run_crew.py` and
`skills/commander/references/crew-dispatch.md` — a sibling lane `launcher-hygiene` is live in those right
now — and `.worktrees/launcher-hygiene/`.

If a doc is wrong because the **code** is wrong, that is a finding to report, not a licence to edit code.

## Do not park

When your turn ends, your process exits. There is no scheduler and nothing will wake you. The full suite
takes ~2 minutes and the harness auto-backgrounds a command that long — five Commanders lost a dispatch
to this today. Use a blocking shape and stay in your turn:

```bash
rm -f /tmp/tc6-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/tc6-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/tc6-suite.log; do sleep 15; done
tail -5 /tmp/tc6-suite.log
```

The `env -u` is not optional: your own spine lease exports those three vars and
`tests/test_mcp_identity.py:600` asserts they are absent, manufacturing a false failure. That cost two
lanes today. **Do not dispatch a crew.**

## Your own closeout episodes

They face the episode-observation guard, which reds the suite. Write them as **observations of what this
run did** — past tense, describing the run, not addressing a reader. In `workaround` and
`proposed-remedy` kinds, **do not open a clause with a bare verb**. **Do not add to the exception list.**

## Evidence required

- For **every** claim you write, the code that makes it true, cited `file:line`. This lane's whole failure
  mode is asserting doctrine nobody checked.
- A quoted before/after for each stale passage.
- Your Task 2 decision, (a) or (b), with reasoning.
- Task 3's measurement, including an explicit null if that is the answer.
- Full Linux suite, cache-clean, clean env. **Baseline `main` `0646d61b`: 3027 passed, 7 skipped, 0 failed,
  1136 subtests** from the primary checkout; **from inside your worktree expect 3028 / 6** —
  `tests/test_spine_lifecycle.py:161` skips unless the checkout sits directly inside `.worktrees`. Both are
  correct. Docs-only changes should move neither, but `tests/test_shipped_check_commands_resolve.py` and
  the code-map test do read shipped text, so run it.
- Regenerate the map: `python -m scripts.code_map build --root .`, commit if it moves.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/tc6-doctrine`, branch `docs/tc6-doctrine`,
based on `main` at `0646d61b`. Yours alone. Work area `.agent-work/tc6-doctrine/`.

`spine_status` must describe `tc6-doctrine` — if it resolves to anything else, especially an `f-424` demo
spine, **stop and report.**

## Stop Conditions

- `spine_status` does not resolve to `tc6-doctrine`.
- A doc can only be made true by changing code.
- The ruling and the shipped engine disagree — that is a serious finding; stop and report it.
- Green would require touching anything in the not-yours list.

## Return Shape

What `spine_status` resolved to, named explicitly; each passage corrected, quoted before and after, with
`file:line` for the code backing it; your Task 2 decision and why; Task 3's result including an honest
null; clean-env suite counts; whether the map moved; and anything floated.

**You may push and open a PR** — your `archive` gate requires it. **You are fenced from merging.**
