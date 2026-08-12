# Implementation Result — g3-implement

## Return status

**COMPLETE** — the change is in, all required evidence is measured, nothing is blocked.

One caveat the Commander must act on, stated up front: a **hard context trip** fired on
`start m3-coupled-suite`. I did not push through it. Both of m3's checks were already run and are
green (recorded below with real exit codes); m3 and m4 are therefore **evidence-complete but not
engine-advanced**, and a `refresh-request` is filed on m3 (`e-m3-coupled-suite-1`). A relaunched
implementer needs only to `start`/`advance` m3 and m4 — no measurement is left to redo.

## Assigned gate

`g3-implement` — `archive.c2b` reachability check (issues #439 + #484), work-id `w5-gates`, epic #418
wave 5.

## Completed slice

`archive.c2b` in `skills/commander/templates/COMMANDER_SPINE.template.json` rewritten to the
pre-ruled shape, plus a test harness that exercises the **shipped** check text through the engine's
own POSIX shell against a stubbed `gh`.

Shipped text now (read back out of the file, not retyped here):

```sh
test "$(gh pr list --head "$(git -C <repo-root> rev-parse --abbrev-ref HEAD)" --state all --json state --jq '[.[] | select(.state == "OPEN" or .state == "MERGED")] | length')" -gt 0
```

The `c2b` statement was updated to match the new criterion and to record why the shape is what it is
(check-time branch derivation; shell-side count comparison).

## THE FOUR-STATE MEASUREMENT

Measured directly on the resolved shipped text, printed exit codes, stub `gh` on PATH:

| PR state for the branch | exit code | verdict |
|---|---|---|
| **no PR** | **1** | not reachable |
| **OPEN** | **0** | reachable |
| **MERGED** | **0** | reachable |
| **CLOSED-unmerged** | **1** | not reachable |

This reproduces the handoff's four-real-branch verification exactly (no-PR → 1, MERGED → 0,
CLOSED-unmerged → 1, OPEN → 0). stdout was empty in all four cases — the verdict rides the exit code
alone, which is the point.

### An extra fact the handoff did not predict

The shipped check was worse than "OPEN-only". `--head <branch>` is **unquoted**, and `<` is a shell
redirection operator, so under the engine's POSIX shell bash tried to redirect stdin from a file
named `branch` and never ran `gh` at all:

```
/usr/bin/bash: line 1: branch: No such file or directory
```

So the old `archive.c2b` exited **1 for every one of the four states** — it was an **always-fails**
check, not merely a narrow one. It "passed" the no-PR and CLOSED-unmerged cases for entirely the
wrong reason. Worth recording because #484 frames the defect as a criterion problem; it was also a
quoting problem, and the two mask each other.

## Scope

**Files changed** (`git diff --numstat`, mine only):

```
1	1	skills/commander/templates/COMMANDER_SPINE.template.json
410	0	tests/test_iterative_planning_doctrine.py
```

New untracked engine artifacts (mine):
`.agent-work/w5-gates/g3-implement-IMPLEMENTER_PLAN.json` (+ `.journal`),
`.agent-work/w5-gates/context/g3-implement.json`, `.agent-work/w5-gates/mechanical/g3-implement.json`.

`.agent-work/w5-gates/{crew-runs.json,execute.json,execute.json.journal}` are engine-owned, not
hand-edited by me.

**`scripts/init_work_area.py`: ZERO-line diff, as predicted.** No new resolver token was added. It
never needed an edit — the existing `<repo-root>` token carries the whole derivation.

**Left untouched, per the handoff:** `.agent-work/epic-418-redux/transitions/close-to-w5/*` still show
`M` with empty diffs (the CRLF stat artifact). Unstaged, not mine.

**Specific exclusions touched:** no. `scripts/checklist_engine.py` is **imported read-only** by the new
tests (see Assumptions); not modified — it does not appear in the numstat.

## Behavior changed

Yes. A branch whose only PR is **merged** now satisfies `archive.c2b`; a branch with only a
**closed-unmerged** PR, or no PR, still fails it; and the verdict now rides the exit code instead of
being discarded on stdout.

## Test mode

**Required:** test-first. **Satisfied:** yes — RED observed against the shipped template before the
template was touched (exit 1, `['<branch>']` unresolved plus the redirection error above), GREEN
after.

## Evidence — every command run bare or redirected, never piped

Collection counts are included because a zero-match `-k` selector exits 5 and would be a gate failure.

| command | exit | collected |
|---|---|---|
| `python -m pytest tests/test_iterative_planning_doctrine.py -q -k archive_c2b` | **0** | **4 tests, 4 subtests** (29 deselected) |
| `python -m pytest tests/test_iterative_planning_doctrine.py -q -k archive_mutation` | **0** | **2 tests, 9 subtests** (31 deselected) |
| coupled suite (8 files, handoff's list) | **0** | **396 passed, 500 subtests** |
| `test -z "$(git diff --numstat -- scripts/init_work_area.py)"` | **0** | zero-line diff confirmed |

Neither selector collected zero.

### Coupled-suite delta, fully accounted

Baseline given: 390 passed / 488 subtests. **I re-measured the baseline at this HEAD** rather than
trusting the figure (reverted my two files, ran, restored): it reproduced **exactly 390 / 488**. The
handoff's number is current, not stale.

Mine: **396 / 500** — delta **+6 tests / +12 subtests**, stable across two runs.

- **+6 tests, +13 subtests** are the new tests (file alone: 27/33 → 33/46, measured both ways).
- **−1 subtest** is `test_context_manifest.py::RevIsGitBlobOid::test_rev_equals_git_rev_parse_head_for_tracked_clean_files`.
  That test subtests only targets whose working tree matches HEAD, and
  `skills/commander/templates/COMMANDER_SPINE.template.json` is one of its four `TARGETS`. Editing the
  template drops it from the clean list until the change is committed. Benign, self-healing on commit,
  and it cannot go vacuous — the test asserts `clean` is non-empty.

Bisected to that file by running all seven non-doctrine files individually with and without my
template edit (`test_context_manifest` 62 → 61 subtests; the other six unchanged). No unexplained
delta remains.

## THE NO-OP ANALYSIS — per mutation leg

The g2 lesson is built into the harness mechanically, not just argued. Every leg runs **both** the
mutated text and the **unmutated** text on the **identical fixture**, and then asserts they
**disagree**:

```python
self.assertNotEqual(control.returncode == 0, mutant.returncode == 0,
                    f"{label} is a no-op: it agrees with the real check")
```

A leg that "failed" for a reason the real check shares cannot pass that assertion. Per leg:

| # | mutation | fixture | control → mutant | **what would make it a NO-OP** |
|---|---|---|---|---|
| 1 | literal `<branch>`, exactly as shipped | OPEN | 0 → nonzero | If the unmutated command also failed on an OPEN PR — i.e. if the check were broken for every state. The control leg rules that out. Note this leg fails at the **shell redirection**, before `gh` is reached, so on its own it does **not** prove the branch *value* matters — leg 2 exists for that. |
| 2 | quoted `"<branch>"` (matches no PR) | OPEN | 0 → nonzero | If the stub ignored `--head`, or the fixture answered for every branch. The stub keys strictly on `--head`, and the control passes on the same fixture. |
| 3 | `--state all` → `--state open` | **MERGED** | 0 → nonzero | **If run on a fixture holding an OPEN PR**, where `--state open` and `--state all` agree — that would be a pure no-op. MERGED is the only fixture that separates them. |
| 4 | drop `or .state == "MERGED"` from the selector | MERGED | 0 → nonzero | If the stub ignored the `--jq` text. It does not: it compiles the `select()` body into its predicate, so dropping the arm really changes the count. |
| 5 | widen selector to accept `CLOSED` | **CLOSED** | nonzero → 0 | If run on any fixture without a CLOSED PR. This is the inverse leg — it proves the CLOSED *rejection* is real and not incidental. |
| 6 | verdict on stdout (`--jq 'length > 0'`, no shell comparison) | **no PR** | nonzero → 0 | **If run on a fixture with a reachable PR** — there the real command exits 0 too and the leg shows nothing. It must run where nothing is reachable. This is the exact no-op trap for this leg. |

Leg 6's text is **derived** from the shipped command (unwrap the `test "$(...)" -gt 0` shell
comparison, put the boolean filter back) rather than retyped, so it cannot drift away from what ships.

### The mutation suite is anchored to the artifact — verified, not assumed

I mutated the **template file itself** and confirmed `-k "archive_c2b or archive_mutation"` goes RED
(exit 1) for each, restoring the file byte-identically afterwards:

| template variant | result |
|---|---|
| the OLD shipped command | **RED**, exit 1 (9 failed) |
| **#484's suggested replacement** (`gh` exits 0 on an empty list — the check that cannot fail) | **RED**, exit 1 (3 failed) |
| correct shape but `--state open` | **RED**, exit 1 (6 failed) |
| correct shape but selector also accepts `CLOSED` | **RED**, exit 1 (2 failed) |

Template restored byte-identical, confirmed by comparison and by `git diff --stat` showing exactly
`1 insertion(+), 1 deletion(-)` with no line-ending change.

## What is NOT proven — the scoped null

Stated plainly, because the honest-null clause deserves a precise answer rather than a blanket one.

**The `--jq` expression's behavior under `gh`'s real embedded gojq is not proven.** There is no `jq`
on PATH to delegate to, and `gh` cannot evaluate a filter offline, so the expression is exercised
against a **modelled subset**: `.field == "literal"` atoms joined by ` or ` / ` and `, wrapped in
`[.[] | select(...)] | length`, plus bare `length` and `length > N`.

Two things keep that from being a check that cannot fail:

1. The stub **derives its filtering from the `--jq` text it is handed** rather than hardcoding the
   expected answer, so the expression is genuinely load-bearing (legs 4 and 5 prove it).
2. Anything outside the modelled subset **refuses loudly** (nonzero + stderr) instead of passing.
   `test_archive_mutation_the_stub_refuses_an_unmodelled_check_shape` proves this over three drifted
   shapes (`--json number,state`, a `test()` selector, `--state draft`).

So: the check text cannot silently drift into a shape the stub waves through. What remains untested is
whether real gojq parses this specific expression the same way the stub does — and the handoff already
closes that gap from the other side, having verified this exact text against four real branches.

The rest is proven without network: no test here reaches `gh`'s API, and the branch derivation is
additionally checked against **this real checkout** with no `git` stub
(`test_archive_c2b_derives_the_branch_from_the_real_repository`).

## Map Impact

- **Structural anchors touched:** `skills/commander/templates/COMMANDER_SPINE.template.json` — the
  `archive` task's `c2b` postcondition (command text + statement). Test surface added at
  `tests/test_iterative_planning_doctrine.py::ArchiveReachabilityRuntimeTests`.
- **Capabilities changed:** Commander closeout reachability now accepts `{OPEN, MERGED}` and rejects
  `{none, CLOSED-unmerged}`, with the verdict carried by the exit code.
- **Constraints honored:** `docs/CHECKLIST_SCHEMA.md` — a `command` condition's verdict is its exit
  code, stdout discarded. Newly relied on: `checklist_engine._run_check_command` runs
  `[bash, -c, command]`.
- **Decision anchor confirmed by measurement, not assumption:** the branch is derived at check time
  from `<repo-root>`, not resolved at instantiation. `init_work_area.py` needed a zero-line diff, and
  `<branch>` is provably outside `_RESOLVER_OWNED_TOKEN_RE`, so instantiation could never have caught
  it. The gate's named unmapped seam is now closed by evidence.
- **Trust limitation:** the jq-under-real-gojq gap above.

## Floats — findings outside my ownership scope, NOT edited

1. **A second unresolved-placeholder class exists.** `_assert_no_resolver_placeholders` only guards
   resolver-owned token families, so any *prose-shaped* token an author puts in a **check command**
   (like `<branch>` was) ships unsubstituted and fails at runtime. My
   `test_archive_c2b_ships_no_unresolved_placeholder` is a floor for `archive.c2b` only. A general
   guard — "no `<token>` may appear in any `command` check of any shipped spine template" — would
   catch the whole class, but it touches `scripts/init_work_area.py` / installer tests and is outside
   this gate. **Recommend triage.**
2. **Shell-quoting is an unguarded failure mode in check text.** The old defect's real bite was that
   `<branch>` unquoted is a shell redirection. Nothing lints shipped check commands for shell safety.
   Same triage family as (1).
3. **`references/windows.md` §4 contradicts this run's operational fact.** It says use the `py`
   launcher and that bare `python` is unreliable; on this box `py` has no pytest and `python` is the
   working interpreter. The doctrine file is an exclusion (bundled reference), so I did not touch it —
   but it is actively misleading here and cost this run time before I was warned.

## Docs/contracts touched

None beyond the `c2b` statement text itself, which is the contract. `docs/CHECKLIST_SCHEMA.md` was
read, not modified.

## Assumptions

- The tests import `scripts/checklist_engine.py` **read-only** to reuse `_run_check_command` and
  `_find_posix_shell`, so the measured verdict is literally the verdict the engine would record. This
  couples the tests to two private engine names. That is deliberate — it is the contract this check
  depends on — but crew 4 owns that file, so if they rename either symbol these tests error loudly
  rather than silently weaken. Importing the engine from tests is an established pattern here
  (`test_context_manifest.py`, `test_episode_fields.py`, and others do it).
- The stub asserts `marker == "posix"`, so a host without bash fails these tests visibly instead of
  reading a missing shell as "unreachable".

## Stop conditions hit

- **Hard context trip on `start m3-coupled-suite`** (context at/over the hard limit). I did not push
  through, did not waive, did not re-claim. Filed `refresh-request e-m3-coupled-suite-1` per reach-up
  doctrine. Both m3 checks are nonetheless already measured green (table above), as is m4's content.
- No non-owned file went red. `init_work_area.py` did not need edits. No policy decision was required.

## Workflow Feedback

- **Handoff gaps:** the handoff describes the defect as two problems (unsubstituted token, OPEN-only
  criterion) and a third property to preserve. It is actually **three defects**: the unquoted `<`
  makes the old check an *always-fails* shell redirection, which I only found by running it. Recommend
  the finding be carried into the issue, because "the check accepted only OPEN" is not a true
  description of the shipped behavior.
- **Context rediscovered:** whether `jq` was available. The whole test mechanism hinges on it (`gh
  --jq` uses embedded gojq, and there is no standalone `jq` here), and the handoff's "invent the test
  mechanism" instruction would have been much cheaper with that one probe named. Also the baseline
  commit `bd56ac8a` is not HEAD (`b711c13a`), which reads as a stale pin — I re-measured to be sure it
  was not, and it was fine, but the pin should name the head it is valid at.
- **Instructions improvised around:** the `IMPLEMENTER_PLAN` template's TDD guidance assumes one
  implementation step; the natural cut here was red-then-green on the state matrix and a separate
  mutation item, which the template supports but does not describe. Minor. More significant: the
  reach-up doctrine says to file a refresh-request and *go idle*, while crew doctrine says the result
  file IS the task and an idle turn-end with it unwritten "strands the gate with no error signal."
  Those two collide exactly when a trip fires late in a run. I resolved it by filing the
  refresh-request (not starting the gate) **and** writing this result, since every measurement was
  already complete and discarding it would have cost a full re-run. Flagging the collision rather than
  claiming a clean reading of it.
- **What would have made this easier:** one line in the handoff naming what is on PATH (`gh` yes, `jq`
  no, `bash` yes, `python` yes). The test mechanism was the expensive part of this gate and it was
  entirely determined by that answer.
