APPROVE

# Review Result — g3-review

## Assigned Gate
`g3-review` — `archive.c2b` reachability check (issues #439 + #484), work-id `w5-gates`, epic #418 wave 5.

## Result
`APPROVE` at commit **`84d1e998`**.

This gate ran in two passes. **Pass 1 (`ff43e883`) was a BLOCK** on one narrow finding. **Pass 2
(`84d1e998`) is an APPROVE** after the repair. Everything between the rules below is my pass-1
review, **preserved verbatim and unwithdrawn** — the finding was fixed, not softened. The
**Re-verification** section at the end records pass 2 and carries the current verdict.

---

# Pass 1 — BLOCK at `ff43e883` (preserved unchanged)

Target: commit `ff43e883`, baseline `4b8abc12`.

## Result (pass 1)
`BLOCK` — one narrow, in-scope finding. Everything else the gate asked for is independently confirmed.

**The shipped check text is correct and needs no change.** The block is against the test harness's
`gh` stub, which does not refuse what its own docstring promises it refuses.

Read the summary table first; it is the whole review in one screen.

| What the gate required | Verdict | How I proved it |
|---|---|---|
| Confirmation 1 — literal `<branch>` goes RED | **PASS** | Template mutated on disk → selectors exit 1, 6 failed |
| Confirmation 2 — `--state open` goes RED | **PASS** | Template mutated → exit 1, 6 failed. **Fixture: MERGED** |
| Confirmation 3 — no-PR branch goes RED | **PASS** | Shipped text on empty fixture → exit 1; #484 form in template → exit 1 |
| Confirmation 4 — reads text out of the template; `init_work_area.py` zero-line diff | **PASS** | `resolved_c2b()` reads the resolved JSON; zero-line diff confirmed |
| Claim (a) — verdict rides the exit code | **VERIFIED TRUE** | Empty stdout in all 4 states; #484's form exits 0/0/0/0 |
| Claim (b) — old text exited 1 in all four states | **VERIFIED TRUE** | Reproduced independently; `gh` never invoked |
| Claim (c) — stub refuses loudly on unmodelled shapes | **FALSIFIED** | 4 unmodelled flags silently answered |
| No-op audit — any surviving leg a no-op? | **NONE FOUND** | Built all 6 legs myself; all discriminate |
| Selectors collect nonzero; suite reconciles | **PASS** | 4 and 2 collected; 396 passed / 501 subtests |

## Handoff compliance

The change does what the handoff assigned. `archive.c2b` derives the branch at check time from the
existing `<repo-root>` token, accepts `{OPEN, MERGED}`, rejects `{no-PR, CLOSED-unmerged}`, and
compares the count in the shell so the exit code carries the verdict.

I reproduced the four-state matrix with **my own** `gh` and `git` stubs, my own `<repo-root>`
substitution and my own `bash -c` invocation — sharing no code with the implementer's harness:

| PR state | exit | stdout |
|---|---|---|
| no-PR | **1** | `''` |
| OPEN | **0** | `''` |
| MERGED | **0** | `''` |
| CLOSED-unmerged | **1** | `''` |

Identical to the implementer's table and to the Commander's four live-`gh` branches. Three
independent measurements agree.

Test-first was genuinely satisfied: the pre-change text is red on this tree, which I reproduced.

## Scope drift

None. `git show --numstat ff43e883` touches exactly the two allowed tracked files:

```
1	1	skills/commander/templates/COMMANDER_SPINE.template.json
410	0	tests/test_iterative_planning_doctrine.py
```

`scripts/init_work_area.py` took a **zero-line diff** across the whole range. No excluded file was
modified — `checklist_engine.py` is imported read-only, which is an established pattern in this
suite. `.agent-work/epic-418-redux/transitions/**` left unstaged.

After my five template mutations the file is restored **byte-identically**: sha256
`9b113ec9c7802217cd49668f7c6670bcac7e493beb86e9bd1bfb6c061367fd3b` before and after, `git diff`
empty. My runner restores in a `finally` block and refuses to start if its match literal is not
found, so an interrupted run cannot leave production code edited.

**One correction to the handoff:** it says `git diff --numstat 4b8abc12 ff43e883` "should show only
the two." It does not, and that is fine — the range contains two intermediate Commander commits
(`3f73b0f1`, `b711c13a`) that add `.agent-work` artifacts, and `.agent-work` **is tracked** in this
repo, contrary to the handoff's "correctly absent from the tracked diff." Scope is clean at the
commit under review. A reviewer following the handoff literally would have raised a false alarm.

## Evidence verdict

Every number reproduced. Run bare or redirected to a file, never piped.

| command | exit | collected |
|---|---|---|
| `python -m pytest tests/test_iterative_planning_doctrine.py -q -k archive_c2b` | **0** | **4 passed, 4 subtests**, 29 deselected |
| `python -m pytest tests/test_iterative_planning_doctrine.py -q -k archive_mutation` | **0** | **2 passed, 9 subtests**, 31 deselected |
| coupled 8-file suite | **0** | **396 passed, 501 subtests** |
| `git diff --numstat 4b8abc12 ff43e883 -- scripts/init_work_area.py` | — | empty (zero-line) |

Neither selector collected zero.

### The coupled-suite delta reconciles — and it reconciles to 501, not 500

The handoff predicted 500. I measured **501**, and 501 is the correct number. The handoff already
told me why: the implementer measured **pre-commit**, while
`test_context_manifest::RevIsGitBlobOid::test_rev_equals_git_rev_parse_head_for_tracked_clean_files`
had dropped the spine template from its clean set. The change is committed now, so that subtest is
**back**. Confirming the account rather than re-finding it, as instructed.

I derived the delta independently from the diff instead of trusting it. The commit adds exactly six
test methods carrying 4 + 6 + 3 = 13 subtests, so **+6 tests / +13 subtests**. Cross-check: the
doctrine file alone at HEAD is 33 tests / 46 subtests, so the baseline was 27 / 33 — exactly the
implementer's figure. 390 + 6 = 396 and 488 + 13 = 501. No unexplained delta.

### The three required mutations — built by me, at the template level

I mutated the **shipped template on disk** and ran the gate's own selectors, which is the strongest
form: it proves the suite catches a bad artifact, not just a bad string.

| template mutation | selectors | verdict |
|---|---|---|
| *(unmutated baseline)* | exit **0**, 6 passed / 13 subtests | green |
| **M1** literal `<branch>` reintroduced | exit **1**, 6 failed / 2 passed | **RED — caught** |
| **M2** `--state all` → `--state open` | exit **1**, 6 failed / 5 passed | **RED — caught** |
| **M3** #484's stdout form (no-PR would pass) | exit **1**, 4 failed / 5 passed | **RED — caught** |
| M4 `MERGED` arm dropped from selector | exit **1**, 5 failed / 5 passed | **RED — caught** |
| M5 `CLOSED` widened into selector | exit **1**, 2 failed / 6 passed | **RED — caught** |

**On confirmation 2, the fixture I used was MERGED.** I then ran the same `--state open` mutation on
an **OPEN** fixture as a negative control and measured **control 0 / mutant 0 — a genuine no-op**,
exactly as the handoff warned. The fixture choice is load-bearing and the implementer picked the only
one that separates `--state open` from `--state all`.

Also measured: with `gh` absent the command substitution is empty, `test "" -gt 0` exits **2**, so a
broken `gh` reads as unreachable. The check fails closed.

## Code/doc quality

The test reads the command **out of** the resolved template and never restates it — cold critic F2 is
answered. Every variant is a `.replace()` on that string; `grep` confirms no retyped copy exists. I
proved it empirically rather than by reading: five template mutations all drove the suite red, which
a retyped copy could not do.

Fowler pass run over the full baseline catalog; rail exits 0. Record at
`.agent-work/w5-gates/g3-review/fowler-pass.json`.

- **Flagged (all non-blocking):** `data-clumps` — the mutation table's bare 5-tuples end in two
  unlabelled booleans, and transposing them would silently invert a leg's meaning; `divergent-change`
  — the test file now hosts three unrelated subjects; `speculative-generality` — the stub models
  `--state closed`, `--state merged` and bare `length`, which nothing exercises.
- **Overridden with logged standards:** `long-method` (the 90-line mutation test is CREW_CONTEXT's
  Verification Discipline being met — one shared control/mutant harness is what makes a no-op leg
  impossible); `primitive-obsession` (string-level mutation is forced by the F2 requirement to test
  the shipped bytes); `comments-as-deodorant` (the per-leg comments carry the required no-op
  analysis — I used them as the checklist for my own audit and falsified none).

The `speculative-generality` flag is the one that sharpened the review: unused modelled branches are
precisely where the stub answers instead of refusing, which is the same family as the blocker below.

## Map impact verdict

- **Evidence supports claimed change:** Yes. The capability claim — closeout reachability accepts
  `{OPEN, MERGED}` and rejects `{none, CLOSED-unmerged}` with the verdict on the exit code — is what I
  measured on three independent harnesses.
- **Constraints not violated:** `docs/CHECKLIST_SCHEMA.md` honored. The verdict is purely the exit
  code; stdout was empty in all four states, so nothing rides on discarded output.
- **Notes match the diff:** Yes. The structural anchor named (the `archive` task's `c2b` command and
  statement) is exactly what changed. Nothing overstated.
- **Decision candidates surfaced:** The decision anchor — branch derived at **check** time, not
  instantiation — is confirmed **by measurement**, not assumed: `init_work_area.py` took a zero-line
  diff, so the existing `<repo-root>` token carries the whole derivation. The gate's named unmapped
  seam is closed by evidence.
- **Durable context routed:** Yes. Three triage candidates recorded in the survey; the implementer's
  three floats are confirmed rather than re-litigated.

## Reconciliation check

Nothing owed. Orientation is `DEGRADED-NO-MAP`, so there is no map to drift from. The `c2b`
**statement** now carries the rationale for both load-bearing properties, so the next reader inherits
the reasoning with the contract.

## Blockers

**B1 — Claim (c) is falsified: the scoped null is wider than reported. The `gh` stub silently accepts
any flag it does not model.**

The stub's argv loop whitelists nothing — it does `opts[flag] = value` for every `--flag` pair — so an
unmodelled flag is dropped on the floor and the stub answers from the fixture anyway. I drove
`GH_STUB_SOURCE` directly out of the test module:

| shape handed to the stub | exit | stdout | behaviour |
|---|---|---|---|
| *(modelled baseline, OPEN present)* | 0 | `1` | answered |
| `--json number,state` | 3 | — | **refuses** |
| `test()` jq selector | 3 | — | **refuses** |
| `--state draft` | 3 | — | **refuses** |
| `!=` jq operator | 3 | — | **refuses** |
| `--limit 100` | **0** | `1` | **silently answered** |
| `--repo someone/else` | **0** | `1` | **silently answered** |
| `--author @me` | **0** | `1` | **silently answered** |
| `--search is:merged` | **0** | `1` | **silently answered** |

This contradicts two written promises:

1. `g3-implement-RESULT.md`: *"Anything outside the modelled subset **refuses loudly** (nonzero +
   stderr) instead of passing."*
2. The stub's **own docstring, shipped in the diff**: *"Models only what the shipped check calls and
   refuses everything else, so the check text cannot drift into a shape this stub silently accepts."*

Both are false as written. It also violates a documented repo standard —
`docs/agents/CREW_CONTEXT.md`, Verification Discipline: *"A round-trip test over the real shipped
artifacts proves the artifacts are clean — it does not prove the tool is correct. Pair it with
adversarial fixtures… a silent PASS on invalid input."* The stub is the tool; the adversarial fixture
for the flag dimension is the one that is missing.

`test_archive_mutation_the_stub_refuses_an_unmodelled_check_shape` covers three drift dimensions —
`--json` fields, `--state` values, `--jq` shapes — but not the fourth, **added flags**, which is
exactly where the parser is loosest.

**The concrete exploit:** if `archive.c2b` later grew `--repo someone/else`, the stub would ignore it
and the entire four-state matrix would stay **green** while real `gh` queried the wrong repository —
a green suite over a check that no longer measures this repo's reachability. That is the wave's own
failure mode reappearing one level up, in the harness that is supposed to prove the check is honest.

**The repair is small and inside this gate's ownership** — both sites are in
`tests/test_iterative_planning_doctrine.py`:

1. Whitelist the four flags the check uses (`--head`, `--state`, `--json`, `--jq`) in the stub's argv
   loop and `refuse()` any other.
2. Add an added-flag case to `test_archive_mutation_the_stub_refuses_an_unmodelled_check_shape`.
3. While there, delete the three modelled-but-unexercised branches (`--state closed`, `--state
   merged`, bare `length`) that widen the same surface — the `speculative-generality` flag above.

No production code changes. I did not edit anything; judging, not fixing.

### Why this is a BLOCK and not an observation

I considered recording it as an observation and approving. Three things decided it against that.
The handoff names *"the scoped null is wider than reported"* as a BLOCK condition, and it is wider —
by a whole dimension the implementer asserted was covered. The falsified claim is not only in a
report but **in shipped code**, where the next reader will trust it. And the repair is a few lines in
a file this gate already owns, so blocking costs one tight repair round, not a redo.

Everything else passed. This should be a fast turn.

## Out-of-scope observations

Floated to the Commander, not edited. All three confirm the implementer's own floats.

1. **No guard lints shipped spine check commands** for shell safety or for prose-shaped unresolved
   tokens. The old `archive.c2b` shipped a literal `<branch>` that was *both* an unsubstituted
   placeholder *and* a shell input redirection, and nothing caught either.
   `_assert_no_resolver_placeholders` only covers resolver-owned token families. A general guard — no
   `<token>` in any `command` check of any shipped spine template, plus a shell-safety lint — touches
   `scripts/init_work_area.py` and installer tests. **Recommend triage.**
2. **`tests/test_iterative_planning_doctrine.py` is accumulating unrelated concerns** — ~1000 lines
   across g1/g2/g3, now three subjects. Stale line numbers are already being paid for by every crew
   in this wave. Split the runtime/stub-based suites out **after** wave 5 closes — not now, because
   the gate's `-k` close criteria are pinned to this file. **Explicitly not a rename request.**
3. **`references/windows.md` §4 is actively misleading on this box.** It tells agents to use the `py`
   launcher and calls bare `python` unreliable; here `py` has no pytest, so `py -m pytest` exits
   nonzero and reads exactly like a red suite when the tests never ran. Every crew in this wave has
   had to be warned by hand in its handoff. It is a bundled reference and an exclusion, so untouched.

## Note on the test naming contract

Held, and I am **not** suggesting any loosening. Four methods carry `archive_c2b`, two carry
`archive_mutation`, and the class name `ArchiveReachabilityRuntimeTests` deliberately carries
neither, so `-k` selects on method names alone. Proven by collection counts: `archive_c2b` collects
exactly 4, not 6; `archive_mutation` exactly 2. No cross-contamination and no zero-match, so neither
selector can exit 5 and fail the gate closed.

## No-op audit

No surviving leg is a no-op. I built all six myself at the shell level; every one discriminates on
its stated fixture.

| leg | fixture | control | mutant | |
|---|---|---|---|---|
| 1 literal `<branch>` | OPEN | 0 | 2 | discriminates |
| 2 quoted `"<branch>"` | OPEN | 0 | 1 | discriminates |
| 3 `--state open` | MERGED | 0 | 1 | discriminates |
| 4 `MERGED` arm dropped | MERGED | 0 | 1 | discriminates |
| 5 `CLOSED` widened | CLOSED | 1 | 0 | discriminates |
| 6 verdict on stdout | no-PR | 1 | 0 | discriminates |

The g2 defect is also prevented **mechanically**, not merely argued: every leg runs the control text
and the mutant on the identical fixture and asserts
`assertNotEqual(control.returncode == 0, mutant.returncode == 0)`. A leg that agreed with the real
check would fail rather than pass quietly. That assertion is the single best thing in this diff.

I checked the three no-op traps the implementer named and found each one real — including measuring
that `--state open` on an OPEN fixture is a true no-op (control 0 / mutant 0). **I looked for an
unflagged no-op and found none.** Legs 3 and 4 are not redundant: one moves the `gh` flag, the other
moves the jq selector, and each needs a MERGED fixture for a different reason. The stub-refusal
test's three shapes all genuinely refuse (exit 3), so that test is not vacuous either.

## Claim (b) — verified independently, and it should go in the PR

The most consequential claim in the diff, and it holds. I ran the **old** text through bash on all
four fixtures myself. All four exit **1**, all four print the same stderr:

```
/usr/bin/bash: line 1: branch: No such file or directory
```

The unquoted `<` in `--head <branch>` is a shell **input redirection**, so bash tried to open a file
named `branch` and `gh` was never invoked at all. The old `archive.c2b` was an **always-fails** check,
not a narrow one — it "passed" the no-PR and CLOSED cases for entirely the wrong reason.

So *"the criterion accepts only an OPEN PR"* was **never** a true description of shipped behaviour.
The correction belongs in the PR body and in the bodies of #439 and #484. I confirm the implementer's
three-defects framing over the issues' two-defect framing.

## Claim (a) — verified, with the counterfactual measured

The shipped text emits **empty stdout in all four states**; the whole verdict is the exit code, which
is what `docs/CHECKLIST_SCHEMA.md` requires. I then ran #484's suggested replacement verbatim on the
same four fixtures:

| state | exit | stdout |
|---|---|---|
| no-PR | **0** | `false` |
| OPEN | **0** | `true` |
| MERGED | **0** | `true` |
| CLOSED-unmerged | **0** | `true` |

Adopting #484 as written really would have converted a check that cannot **pass** into one that
cannot **fail**, inside a wave about checks that cannot fail. The shell comparison is doing the real
work.

## Reproduction artifacts

Written to `.agent-work/w5-gates/g3-review/repro/`, all local-only:

- `reviewer_probe.py` — my independent stubs, shell runner and four-state matrix; also the old text,
  #484's form, my six mutations with paired controls, and the `gh`-missing fail-closed case.
- `template_mutations.py` — mutates the shipped template on disk, runs the selectors, restores
  byte-identically under `finally` with a sha256 check. Refuses to run if its match literal is absent
  or if the unmutated baseline is not green, so it cannot report a vacuous result.
- `stub_refusal_probe.py` — drives `GH_STUB_SOURCE` straight out of the test module across nine
  shapes. This is the probe that found B1.

## Workflow Feedback

- **Handoff gaps:** Two concrete wording errors, both of which would mislead a reviewer following the
  handoff literally. (1) *"Everything under `.agent-work/` is local-only and correctly absent from the
  tracked diff"* and *"`git diff --numstat 4b8abc12 ff43e883` should show only the two"* — `.agent-work`
  **is tracked** here, and the range holds two intermediate Commander commits, so the numstat shows
  twelve paths. I nearly raised a false scope alarm before checking `git show` on the commit itself.
  **Name the commit, not the range**, when the scope assertion is about one commit's contents. (2) The
  Evidence-to-reproduce table says the implementer saw 500 subtests, then the next paragraph explains
  why 501 is correct post-commit. The table should carry the number **I** should expect to see (501),
  with 500 as the pre-commit footnote — as written, the number I was told to reproduce is the one that
  would have been wrong.
- **Context rediscovered:** What is on PATH. I had to determine for myself that `bash` exists (and
  where), that there is no `jq`, and that `gh` is present but unusable offline. The implementer's
  RESULT flags exactly the same gap and asks for exactly the same one line. Two crews on one gate have
  now paid for it — please put `gh` yes / `jq` no / `bash` yes / `python` yes into the handoff
  template, not just this gate's handoff.
- **Instructions improvised around:** Three. (1) The reviewer skill says to `advance` each check after
  recording it; for a `survey` the engine answers `REFUSED: advance is for gated checklists; use
  record`. `record` alone advances. The skill's own instruction does not match its own engine for this
  checklist type — worth one clarifying clause, since a reviewer who trusts the skill will read that
  refusal as an error. (2) `claim` takes `--session-id` on every subsequent verb, but the skill never
  says so and the first `start` fails with a REFUSED that reads like a lease conflict. (3) Engine
  findings are passed as shell arguments, so a finding containing `$(...)` — unavoidable when the
  subject under review **is** a shell command — gets command-substituted before the engine sees it. My
  `c5` finding was recorded with `test "$(...)" -gt 0` mangled to `test "" -gt 0`. Harmless here
  because the substance survives and the full text is in this file, but on a gate about shell quoting
  it is a sharp irony and a real trap. Findings should be passed via a file or stdin.
- **What would have made this easier:** The handoff was otherwise excellent — naming the three
  fixture-dependent no-op traps in advance let me test them as hypotheses rather than hunt for them,
  and the g2 war story is what made me build the stub probe that found B1. One concrete change: state
  the reproduce numbers **as of the target ref**, since the implementer measures pre-commit and the
  reviewer measures post-commit, and that offset will recur on every gate that reviews a committed
  ref.

## Return status (pass 1)
`complete` — survey driven to a consolidated verdict through the engine; all 17 checks visited,
1 fail, 3 triage candidates, verdict BLOCK.

---

# Re-verification (pass 2) — commit `84d1e998`

**APPROVE.** The block is repaired at all three sites I named. I re-ran everything rather than
accepting the Commander's measurements, and I went looking for shapes the Commander did not try.

## Scope of the repair

`git show --numstat 84d1e998` — one file, **12 added / 6 removed**:

```
12	6	tests/test_iterative_planning_doctrine.py
```

**The shipped check text is untouched**, exactly as I said it should be. No production file changed.

## Is the whitelist actually closed? — 21 shapes, all refuse

This is the question the Commander flagged hardest, and rightly: proving four flag *names* refuse
does not prove the *guard* is closed. So I probed flag **shapes**, which is where I expected to break
it. Every one refuses (exit 3):

| dimension | shapes probed | result |
|---|---|---|
| names already proven | `--repo someone/else`, `--limit 100`, `--author @me`, `--search is:merged` | all refuse |
| combined one-token | `--repo=someone/else`, `--limit=100` | all refuse |
| **modelled** flags in combined form | `--json=state`, `--head=BRANCH` | all refuse |
| short flags | `-R someone/else`, `-L 100`, `-s all` | all refuse |
| separators / positionals | bare `--`, positional `someone/else` | all refuse |
| missing values | unknown flag last in argv, **modelled** flag last in argv | all refuse |
| adversarial values | flag whose value looks like a flag, empty-string value | all refuse |
| lookalikes | uppercase `--HEAD`, trailing-space `--repo `, en-dash `–-repo` | all refuse |

**No shape I could construct is still silently answered.** The guard also sits *before* the
flag-with-no-value check, so ordering opens no gap. My original concrete exploit — `--repo
someone/else` — now refuses (exit 3) where it previously answered exit 0 printing `1`.

Three informational rows, none a hole. Repeated `--head` and repeated `--state` answer last-wins,
which is what cobra does in real `gh`, so the stub **matches** rather than diverges. The `--jq`
else-branch is answered below.

## Are the two new legs load-bearing, or decorative?

**Load-bearing — reproduced independently.** I deleted the two guard lines from the stub source
myself and re-ran `-k archive_mutation`:

| | exit | result |
|---|---|---|
| with guard | **0** | 2 passed, **11 subtests** |
| **without guard** | **1** | 2 failed, 2 passed, **9 subtests** |

Exactly the two new legs fail, both with `AssertionError: 0 == 0` — the stub answered where it must
refuse. Restored byte-identically (sha256
`2457cb475a290353eac1b98c556ce2669728d44112da3d67970417f078491aea`), `tests/` clean. This matches
the Commander's report exactly.

**Worth recording:** my probe **refused to run** on its first attempt because its guard literal did
not match — the file is CRLF on this host and my literal was LF. That is CREW_CONTEXT's *"assert the
mutation actually applied"* rule doing precisely its job. Without it I would have deleted nothing,
seen a green suite, and wrongly reported the legs as load-bearing — the exact failure that rule
exists to prevent, caught on me rather than by me.

## Did deleting the three branches cost anything?

**No, measured both directions.** The three deleted branches now refuse (exit 3): `--state closed`,
`--state merged`, bare `length`. The forms the legs genuinely need still answer: `--state open`
(leg 3) and `length > 0` (leg 6, exit 0 printing `true`). Full coupled suite green, so nothing
depended on them. The Commander's reasoning was right; I confirmed it rather than accepted it.

## The Commander's open question: the still-optional `--jq` else-branch

**Cosmetic tidy, not a finding. I am not asking for it, and it should not hold the gate.**

I measured the drift instead of reasoning about it — stripped `--jq` from the shipped text and ran it:

| fixture | exit | stderr |
|---|---|---|
| no-PR | **2** | `test: []: integer expression expected` |
| OPEN | **2** | `test: [{"state": "OPEN"}]: integer expression expected` |
| CLOSED | **2** | `test: [{"state": "CLOSED"}]: integer expression expected` |

It **fails closed in every state, including the reachable one.** That is a real, measured distinction
from the three branches I did name: those answered a **count** — a plausible number the shell
comparison consumes happily, so a wrong count becomes a wrong verdict silently. The raw-JSON path
emits an array the comparison cannot consume at all. Tidy it if the stub is ever revisited; it buys
no safety. Recorded as triage candidate `tc4`, no action asked.

The Commander was right not to freelance past the finding. That instinct is worth keeping.

## No regression — the full original battery, re-run at `84d1e998`

The repair touched the stub every leg depends on, so I re-ran everything I approved in pass 1:

- **Four states unchanged:** no-PR 1, OPEN 0, MERGED 0, CLOSED 1, stdout empty throughout.
- **Claim (b) still reproduces:** the old text exits 1 in all four states with `bash: line 1: branch:
  No such file or directory`.
- **Claim (a) still reproduces:** #484's form exits 0/0/0/0.
- **All six shell-level legs still discriminate**, and the OPEN-fixture no-op control still measures
  control 0 / mutant 0.
- **All five template mutations still RED** (M1 6 failed, M2 8 failed, M3 4 failed, M4 5 failed,
  M5 2 failed) against an unmutated baseline of exit 0 / 6 passed / 15 subtests. Template restored
  byte-identically (sha256 `9b113ec9…`).
- **No tracked production file is dirty** after all mutation runs.

## Counts — reproduced, and they reconcile

| command | exit | collected |
|---|---|---|
| `-k archive_c2b` | **0** | 4 tests / **4 subtests** |
| `-k archive_mutation` | **0** | 2 tests / **11 subtests** (was 9; +2 new legs) |
| coupled 8-file suite | **0** | 396 passed / **503 subtests** |

503 is my own **501** at `ff43e883` plus exactly **2** — the two new legs, and nothing else. Neither
selector collected zero.

## Fowler pass — re-run, one verdict changed

Rail exits 0. **`speculative-generality` moves flagged → absent**: the three modelled-but-unexercised
branches are gone and I re-verified each now refuses. Two non-blocking flags remain, unchanged by the
repair and both for post-wave triage: **`data-clumps`** (the mutation table's bare 5-tuples end in two
unlabelled booleans — transposing them would silently invert a leg) and **`divergent-change`** (the
test file now hosts three unrelated subjects).

## Blockers (pass 2)

None. The pass-1 blocker **B1** is repaired and re-verified; it stands in this document as a record
of what was found, not as an open item.

## Out-of-scope observations (pass 2)

Unchanged from pass 1 — the three floats stand. One added, no action asked: the optional `--jq`
else-branch above (`tc4`).

## Workflow Feedback (pass 2)

- **Handoff gaps:** none — the re-review request was the best-formed instruction I received on this
  gate. It named the commit, listed the three changes against my three findings, stated what it had
  measured so I could reproduce rather than rediscover, and *pre-identified the two places it might
  have fooled itself*. That last move is what made pass 2 cheap. It is worth copying into the handoff
  template as a required field: **"where I could have fooled myself."**
- **Context rediscovered:** none new.
- **Instructions improvised around:** two engine limits. (1) `reopen` refuses on a `survey` —
  *"reopen applies to gated checklists"* — so a fail that gets repaired cannot be formally reopened;
  I re-recorded the check directly, which the engine allows. (2) **The journal does not preserve a
  superseded result.** Its entries record *that* a `record` verb ran, with a hash chain, but not the
  result value or the finding text, so re-recording `c7` as pass leaves **no machine-readable trace
  that it was ever a fail**. The BLOCK survives only because the Commander told me to preserve it in
  this file. That is a real gap for any gate that blocks and then approves: the engine's own record
  would show a clean APPROVE with 0 findings and no history. Recommend the journal carry `result` and
  `finding` on `record`.
- **What would have made this easier:** nothing on this pass.

## Return status
`complete` — survey re-driven through the engine at `84d1e998`: 21 checks visited (17 original + 4
re-verification), 0 fails, 4 triage candidates, verdict **APPROVE**. Lease released.
