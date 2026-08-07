# RETURN — `cmdr-440-binding-cwd` · issue #440 · epic-418 wave 1, workstream A2

Branch `epic-418/a2-440-binding-cwd` · base `cbd9aee` · tip of branch · **not pushed, no PR — yours**

> **Archive is BLOCKED on you, by design — see §12.** The run itself is complete and green.

---

## 1. Verdict

**This is a win, not a measured negative, and it clears the done-condition you set.**

You asked for a HARD trip to fire from a per-agent reading produced by an agent **dispatched into a
worktree**, with the reading landing where the engine actually reads it — a fired trip, observed on a
live run, not a path that resolves correctly. That is what happened.

The binding store no longer resolves a relative `--file` against the payload's `cwd`. It walks
ordered candidate roots and takes the first that **validates as a checklist on disk**, deriving the
worktree root from `git worktree list` rather than being handed it, and **refuses to bind at all**
when two guessed roots name different existing files. On a live two-arm run, a subagent dispatched
into a real worktree claimed a spine there with a relative `--file`, filled its own context to **56%**
against a HARD of **15%**, its `gauge.json` landed **beside the worktree spine**, and the engine
**REFUSED its `advance`**:

```
REFUSED: m1: context at 56% is at/over the hard limit — advancing is blocked until you
request a refresh, so work is handed off at a seam rather than lost to a runaway.
EXIT=1
```

The byte-identical control on `cbd9aee` reached **56.2%**, filed its reading in a phantom
`.agent-work/` inside the sandbox main, and **advanced clean at exit 0**.

**Two things you should know before you merge**, both in §7: this run crashed once and was resumed,
and the pre-existing "baseline is exit 0" line in the launch order turns out to be an artifact of
where it was measured. Neither changes the verdict.

---

## 2. The fired trip, with its evidence

| | treatment (HEAD) | control (`cbd9aee`) |
|---|---|---|
| headless run | exit 0, 156.4s | exit 0, 143.5s |
| binding resolved to | **worktree** spine, `path_source: git_worktree` | **sandbox main**, `path_source: null` |
| gauge beside worktree spine | **present**, fill **0.559655** | absent |
| gauge at phantom path in main | absent | **present**, fill **0.562149** |
| `advance` | **REFUSED, real exit 1** | succeeded, **real exit 0** |
| gate after | stayed `in-progress` | `complete` |

HARD for `claude-sonnet-5` is **0.15**. The two fills are **0.44% apart**, so the opposite outcomes
are attributable to the hook path and to nothing else.

### Why I know the trip came from the *worktree-dispatched* agent, not the parent

Three independent signals, captured on both arms and agreeing 3/3:

1. **The binding key is composite** — `9d959dcd-…#a26a9cb68fda52cdc`. Only a dispatched agent keys
   `session_id#agent_id`; a top-level agent keys bare.
2. **`identity_resolution_ms` is present** (0.0433). The writer emits that fifth field **only** on a
   dispatched agent's record (#419), so a 5-field record is positive proof of subagent origin.
3. **`gauge.json`'s own `model` says `claude-sonnet-5`** while the parent ran `opus`. The verifier now
   also asserts the *premise* — that the two tiers ran different models — because signal 3 is vacuous
   otherwise.

Corroborated at source by the reviewer: `gauge_writer_hook.py:608-631` reads only the derived
`subagents/agent-<id>.jsonl` with an **explicit refusal** to fall back to the parent, and
`find_latest_usage:325` further requires `isSidechain` **and** a matching `agentId`. A fill of
0.559655 is structurally incapable of being the parent's.

### Why the control is worth something

**It worked and missed.** It produced a real, over-HARD reading *at the wrong path* rather than going
quiet. That is what rules out the three impostors that would otherwise wear the bug's face: an
incomplete sibling `scripts/` set (the writer nulls **silently** if it cannot import `spine_rail` as
a filesystem sibling), an uncalibrated model, and a subagent that never got an `agent_id`. A quiet
control would have proved nothing, and I would have reported it as inconclusive.

---

## 3. How I know my green is real

You flagged the sharp edge yourself: **the mechanism under repair is the mechanism that makes an
in-worktree validation lie.** Four things stand behind the green.

1. **The arms differ in exactly one file.** Proved by a recursive `diff -rq` over two *complete*
   `scripts/` trees, not a curated subset — `scripts/hooks/spine_rail.py`. The reviewer independently
   diffed the settings (two lines, both `treatment`→`control`) and the prompts (exit 0 after
   normalising the arm name).
2. **Nothing handed the hook the value it was supposed to derive.** The treatment binding records
   `path_source: "git_worktree"`, which is only written when the root came from `git worktree list`.
3. **The reviewer refused to take the harness's word and built its own repro** — and found the
   variant I had not thought to ask for. It moved the engine script token **out** of the worktree
   into `main/bin`. The hook **still** resolved to the worktree. With no worktree-shaped token
   anywhere in the command, the derivation is real and the hand-injection hypothesis is dead. That is
   the single most convincing item in this return, and it is not mine.
4. **The verifier can fail.** `verify_evidence.py` exits 0 over **59 checks** and its `--selftest`
   fails **all 10** deliberately damaged copies. I re-ran both myself rather than reading the crew's
   claim.

---

## 4. Evidence — commands and real exit codes

All gated on real exit codes by redirecting to a file and echoing `$?`, never off a piped tail.

| command | exit |
|---|---|
| `python .agent-work/issue-440-binding-cwd/acceptance/verify_evidence.py` | **0** (59 checks) |
| `… verify_evidence.py --selftest` | **0** (10/10 mutations correctly fail) |
| `NO_COLOR=1 FORCE_COLOR= PY_COLORS=0 python -m pytest tests/ -q` | **0** — 1723 passed, 2 skipped, 550 subtests |
| `python -m pytest tests/ -q` (with harness `FORCE_COLOR=3`) | 1 — 10 false failures, see §7 |
| `python -m pytest tests/test_mutation_floor.py -q` in a `git archive cbd9aee` tree | 1 — **11** failures, pre-existing |
| `python scripts/verify_worktree_isolation.py --here …` | **0** |
| engine's own re-run of `python -m pytest tests -q` at the `g3-close` gate | **0** |

**Baseline:** 1688 → **1723 passed**, strictly greater by +35. **No previously-passing test id
disappeared** — verified by a `--collect-only` id diff against a `git archive` of `cbd9aee`
(1690 → 1725 ids; `comm -23` = **0** disappeared, `comm -13` = 35 added), not by comparing counts.

**PR state:** none. Not pushed, no PR opened, nothing merged — that is your step, per the dispatch.

Commits on top of `cbd9aee`:

(the five that carry the change; four closeout commits follow — triage/return, archive move,
state note, and this file)

```
b2810d9 docs(#440 g3): record the shipped resolution and rule on the existing bindings
89cc99a fix(#440 g2-review): assert the BINDING, not just the gauge, in the acceptance verifier
b332287 test(#440 g2): two-arm live-fire acceptance — a HARD trip fires from a worktree-dispatched agent
38214ec fix(#440 g1b): refuse to guess when two guessed roots name different files
9d44aa6 fix(#440 g1): resolve a relative --file against validated candidate roots
```

---

## 5. Isolation proof

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/epic418-a2-440
worktree OK: in C:/Programs/constellation-skills-wt/epic418-a2-440
ISO_EXIT=0
```

**The live main checkout was never written.** `.agent-work/.spine-rail-binding.json` was read for the
`existing-bindings` ruling and left byte-for-byte alone; no live `.claude/settings*.json` and no real
worktree was touched. The harness ran entirely under `%TEMP%\acc440`. Verified two ways: the arms
record their sandbox root, and the verifier asserts no sandbox path appears in the live store.

---

## 6. The `decision:existing-bindings` ruling

**LEAVE TO AGE OUT. Live store untouched. Regraded `guess` → `measured`** by running the settle
experiment your pre-ruling named.

**A stale binding yields a missing reading, never a wrong one**, for three independent reasons: the
engine reads `gauge.json` beside the spine it was itself invoked with and never through the store, so
a wrong binding can misplace a *write* but never redirect a *read*; a key with more than one
candidate makes the writer **refuse outright** (`gauge_writer_hook.py:595-606`); and a misplaced
reading ages past the reader's 30-minute window into nothing.

I considered retiring the dead entries and **rejected it on measurement, not caution**: the one
silenced key holds **10 entries of which 3 are LIVE**, so deleting all 7 dead ones leaves the guard
still firing. It would buy no behavioural change while risking a lost update against a store two live
sessions were writing at the time. Before-state at
`.agent-work/issue-440-binding-cwd/g3/live-binding-store-before.json`; full reasoning in
`g3/EXISTING_BINDINGS_RULING.md`.

Your "60 of 64" is now **8 of 12** — the store has been rewritten by live activity since, and the
shape is unchanged.

---

## 7. Two things that need your attention

### (a) This run crashed and was resumed — the cause was an account limit, not a defect

The prior session died mid-`g2`. Its engine state was durable and intact, and I resumed under the
same lease rather than restarting. The crash cause is in the evidence verbatim:

```
EXIT: 1
--- STDOUT ---
You've hit your weekly limit · resets Aug 7, 7am (America/Los_Angeles)
```

The limit reset before I resumed. **I re-ran the arms unchanged** — I did not trim the inflation
budget to squeeze under it, which would have risked an under-inflated subagent producing a false
negative wearing the bug's face.

### (b) The launch order's `cbd9aee` baseline of "exit 0" cannot be reproduced, and I found out why

**FOR YOUR ATTENTION — this affects every Commander you dispatch.**

My first full-suite run showed **10 failures**. I attributed them with `uniq -c` rather than reading
the tail (all 10 in `tests/test_mutation_floor.py`), then verified rather than reasoned: a
`git archive cbd9aee` temp tree gives **11** failures — one *more* than my branch. Pre-existing.

The cause is worth more than the pass. The Claude Code harness exports **`FORCE_COLOR=3`**, so pytest
emits ANSI **even into a captured pipe**. `test_mutation_floor.py:255` matches `FAILED` immediately
followed by the test path and does not strip ANSI, so the colour-reset lands between them, every
match breaks, and the meta-harness reports `HARNESS ERROR: non-zero exit with no FAILED test node`
while its own captured output plainly contains those nodes. Clear the variable and that file goes
from **10 failed → 14 passed, exit 0**.

So your recorded baseline was measured **outside** a `FORCE_COLOR` session and mine was inside one.
This is a **second, independent false-red** in the same family as your `py`-is-not-the-test-runner
warning — and unlike that one, **it fires for `python` too**. Filed as **#454**. I would consider
adding it to `_COMMON.md` beside the `py` warning.

---

## 8. Scope-discipline report

Corner cases deliberately **not** chased, each commented at the code site and filed rather than
absorbed:

| not chased | code site | filed |
|---|---|---|
| bare-key multi-spine ambiguity silence | `docs/GAUGE_WRITER_HOOK.md` § Known limits | **#452** |
| `spine_rail` binds an unexpanded shell token | `docs/GAUGE_WRITER_HOOK.md` § Known limits | **#453** |
| `test_mutation_floor` ANSI parse | — (test-harness area this run never opened) | **#454** |
| self-referential freshness check | `acceptance/verify_evidence.py`, above `obs = att.get("observed_at")` | **#455** |
| per-launch log overwrite, declined-protocol flakiness, undeclared evidence schema, `probe()` dead verdict | `acceptance/` | **#455** |

**One thing I did NOT defer, and I want you to check my call.** The g2 reviewer found that
`verify_evidence.py` never read `binding_entries` — so a treatment arm binding to the sandbox **main**
(the defect *not* fixed) still exited 0. I fixed it (`89cc99a`) rather than triaging it, because
shipping an acceptance artifact *for this very issue* that cannot fail is the tests-that-cannot-fail
shape this epic has already filed three issues about (#432, #446, and a finding inside #419's own
run). 46 → 59 checks, 5 → 10 mutations. If you would rather that had been triaged, it reverts cleanly.

Where the issue text and the scope-discipline ruling disagreed on breadth, the ruling won — the
`existing-bindings` question was settled by measurement and left alone rather than migrated.

---

## 9. Map impact

No packet map exists (`DEGRADED-NO-MAP`), so I reconciled the structural record **directly**, which
this step sanctions. The record of governing truth for this area is
`docs/GAUGE_WRITER_HOOK.md` § "Known limits of the binding store itself", which stated this defect as
**open**; it now states it as fixed and describes the shipped resolution with the live verification
beside it. Two **new** limits were added in the same pass rather than left to be rediscovered.

Net structural delta: `scripts/hooks/spine_rail.py` gained a candidate-root resolution path and an
ambiguity refusal. **No load-bearing interface shape moved** — the gauge binding key, the gate schema
and the MCP tool surface are untouched, which matters because changing the binding key is explicitly
outside my latitude.

---

## 10. Triage candidates

All filed under `_COMMON.md` § Inherited Latitude, which delegates issue **filing** outright. No
issue was closed — that is withheld and rides a human batch confirm.

- **#452 — a bare-keyed agent driving several spines at once gets NO gauge reading at all.**
  **Read this one first.** It is not #440 and #440 does not fix it, but it is what actually keeps the
  governor silent for orchestrators. It fell out of the existing-bindings measurement rather than
  from inspection. Its fix may require changing the binding key shape, which is **yours to
  adjudicate, not mine**.
- **#453** — `spine_rail` binds an unexpanded shell token (`--file $E`) verbatim.
- **#454** — `test_mutation_floor` false HARNESS ERROR under `FORCE_COLOR` (see §7b).
- **#455** — acceptance-harness hardening; consolidates the reviewer's five non-material findings and
  the crew's two candidates.

Full recommendations in `.agent-work/issue-440-binding-cwd/TRIAGE.md`.

---

## 11. Workflow feedback

- **The engine's typed-evidence enforcement earned its keep.** It refused an `artifact` where an
  `implementer-result` was required, and refused a `review-result` whose `verdict` was not literally
  `APPROVE`. The second forced me to make the "APPROVE WITH FINDINGS → APPROVE" reduction *explicit
  and recorded* rather than quietly typing the word it wanted. That is the gate working.
- **The `g3-close` gate re-runs its own gated command.** Worth knowing: it took ~4 minutes and looked
  like a hang until I checked the postcondition definition. It also inherits the session environment,
  so it hit the `FORCE_COLOR` trap and refused until I cleared the variable for its subprocess.
- **Backticks in an engine `--why` string are executed by bash.** One of my `--why` values contained
  `` `git worktree list` `` and `` `py` ``; the shell ran both, spawned Python REPLs, and leaked
  `git worktree list` output into a stored `satisfied_by` note on `g3-close.c2`. Cosmetic, but that
  note is polluted. Long `--why` values should be passed via `"$(cat file)"` with no backticks.
- **An externally-dispatched crew is unrecoverable after a session crash.** `recover_crews.py`
  correctly flagged the g2 implementer as RESUMABLE and advised `SendMessage` to its `agentId` — but
  no `agentId` is recorded for `--backend external`, so the only route was
  `--abandon … --relaunch`. Worth either recording the `agentId` or changing the advice.
- **The R2 handoff I wrote contained an ordering conflict** ("treatment first" vs "prioritise the
  control if you can only afford one"). The crew flagged it. Mine to own.

---

## 12. Closeout status — archive is BLOCKED, and it is blocked on you

The run is **complete and green**. Every gate closed with integrated evidence and the spine was
driven through `execute` → `reconcile` → `triage` → `review` → `feedback`. The `archive` step is
**blocked**, bubbled to parent, on its two postconditions I am not permitted to satisfy:

- **`c2` — branch pushed.** Not done.
- **`c2b` — an open PR exists.** Not done.

My dispatch reserves both: *"Do NOT push, open a PR, or merge — that is the Admiral's step."*
`_COMMON.md` **does** pre-clear `git push on epic-418/*` and `gh pr create`, so this is **not** a
permission block and **not** the #145 environmental shape — the capability exists and I declined to
use it because you withheld it. I recorded a `block`, not a `waive`, because a waive would read as
"this did not need doing" and `c2b` is right that a terminal spine without an open PR gets chased.

**The engine session lease `cmdr-440-binding-cwd` is still held, deliberately.** The archive step is
explicit that releasing before the closing `advance` leaves archive's own closeout entries after the
release and fails the terminal provenance check. Releasing now would corrupt the provenance of an
otherwise clean run.

**To finish it:** push `epic-418/a2-440-binding-cwd` (clean tree, 9 commits on `cbd9aee`),
open the PR declaring **FINAL** in the title, satisfy `c2`/`c2b`, check `c4`, run the closing
`advance archive` against the **moved** spine path
`.agent-work/archive/2026-08-07-issue-440-binding-cwd/spine.json`, and release the lease last.
`STATE_NOTE.md` at the worktree root carries the exact commands.

**Also at PR time:** `main` has advanced to `4fbdf6e` while this branch is based on `cbd9aee`. Per the
dispatch that is handled at PR time, so I did not rebase mid-gate. And harvest
`.agent-work/staged-feedback/issue-440-binding-cwd/` — its `FENCE.md` lists the three steps and
pastes the validated dry-run output.
