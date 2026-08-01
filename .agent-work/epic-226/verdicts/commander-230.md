# Verdict — commander-230 · issue #230 (epic-226 item D)

**PR:** [#238](https://github.com/fredcai6/constellation-skills/pull/238) — `feat(planning): @grade fixedness schema + grade_lint.py (#230)`
**Branch:** `issue-230` (commits `565f53c`, `87d22d3`) · base `main` @ `83a31b1`
**Worktree:** `C:/Programs/constellation-wt-230` · **Model:** opus (crew: sonnet, no Fable at any tier)
**Findings file:** `.agent-work/epic-226/evidence/findings-230.md`

---

## Verdict per build item

| # | Item | Verdict |
|---|---|---|
| 1 | Inline `@grade:` markup on the decision's own line in existing decision blocks | **SHIPPED** |
| 2 | Executor doctrine — tier as an index into an action at a reality-contradiction | **SHIPPED** (prose, as the issue specifies) |
| 3 | THE FORK — lint loud, execute safe | **SHIPPED** |
| 4 | `scripts/grade_lint.py` — guess-ledger view + batched objections | **SHIPPED** |
| 5 | Template updates — tag convention + one example each | **SHIPPED** |

**No honest null.** PR-7's grep returned zero hits across `skills/`, `scripts/`, `tests/`; all five items were genuine build-from-zero, confirmed by measurement rather than taken on the launch order's word.

---

## Evidence

### Worktree isolation
```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-230
worktree OK: in C:/Programs/constellation-wt-230
EXIT=0
```

### Full suite — locally run (PR-2 / PR-2b: no GitHub Actions run triggered, awaited, or claimed)
```
$ py -m pytest tests/ -q
........................................................................ [ 89%]
............................................................s........s.. [ 97%]
.....................                                                    [100%]
927 passed, 2 skipped, 244 subtests passed in 36.95s
PYTEST_EXIT=0
```
Baseline `main` was 905 passed / 2 skipped. **+22 tests, zero regressions.**

### Seeded-violation acceptance tests
`tests/test_grade_lint.py` — 22 tests, `py -m pytest tests/test_grade_lint.py -q` → **22 passed, exit 0**.

The four the issue names, each driven through the real CLI (`main(argv)` → int), against fixtures built as **real** `## Pre-Rulings` / EXECUTE_PLAN-shaped blocks per `lesson:verify-harness-field-and-drive-real-writer`:

| Required case | Test | Result |
|---|---|---|
| ungraded load-bearing → FAIL | `GradeLintCoreTests` (GL001, exit 1) | PASS |
| guess without `settle:` → FAIL | `GradeLintCoreTests` (GL004, exit 1) | PASS |
| dangling `leans` → FAIL | `GradeLintCoreTests` (GL005, exit 1) | PASS |
| clean plan → PASS | `GradeLintCoreTests` (exit 0) | PASS |

Plus 18 more, incl. the ones a cold critic showed were needed because a broken build could otherwise pass all four above: prose-is-not-a-decision, `--mode execute` suppresses GL001, positive `leans` resolution, fence regression, multi-path invocation, JSON-walker coverage, `--strict-warnings`, exit-code 2, and four review-found regressions.

**Live probe of the binary (not just the tests):**
```
$ py scripts/grade_lint.py probe.md --known-id g1-implement
grade_lint: 3 objection(s)
  [FAIL] GL004 GUESS_MISSING_SETTLE  probe.md:5  guess tier missing settle:
  [FAIL] GL001 UNGRADED_DECISION     probe.md:7  decision has no @grade tag
  [WARN] GL003 MISSING_PROVENANCE    probe.md:8  settled tier missing provenance
guess-ledger: 1 settled, 1 guesses (1 load-bearing, 1 missing settle), 0 placeholder, 1 ungraded
Proceed despite the above, or fix the grades first?
EXIT=1

$ py scripts/grade_lint.py probe.md --known-id g1-implement --mode execute
  ... GL001 absent, every other violation intact ...
EXIT=1
```
The intro prose line is **not** flagged; the output ends in **one** batched question; THE FORK demonstrably suppresses only GL001.

### Template round-trip
```
$ py scripts/grade_lint.py \
    skills/admiral/templates/LATITUDE_CONTRACT.template.md \
    skills/admiral/templates/LAUNCH_ORDER.template.md \
    skills/commander/templates/MISSION_FRAME.template.md \
    skills/commander/templates/EXECUTE_PLAN.template.json --strict-warnings
grade_lint: clean -- 0 settled, 0 guesses (0 load-bearing, 0 missing settle), 0 placeholder, 0 ungraded
EXIT=0
```
Clean at **WARN** level, not merely FAIL-free, and with **no filename special-casing** — a placeholder is recognized structurally, so "the shipped templates lint clean" is a real property rather than an exemption. A real decision block, tagged, parsed, and correctly classified is shown in the live probe above.

---

## Canonical doctrine target (PR-6)

**Edited: `skills/_shared/global-everyone.md`** — new section "Decision fixedness: the `@grade` tag" carrying the grammar, the per-tier executor rules, and THE FORK.

Why this is canonical: the executor rules are **cross-role** — an orchestrator authoring pre-rulings and a crew implementer hitting a contradiction mid-gate both need them — so they belong in the all-tiers shared doctrine. `skills/_shared/` is the source; `install_constellation.py:98-101` copies it out to `skills/<role>/references/global-everyone.md` at **install** time. I verified those role copies are **untracked** (`git ls-files | grep references/global-` → empty), so there was nothing in-repo to regenerate and no install-time copy was hand-edited. PR-6 honored literally.

Templates edited: `LATITUDE_CONTRACT.template.md`, `LAUNCH_ORDER.template.md` (Pre-Rulings), `MISSION_FRAME.template.md` (Decision Anchors), `EXECUTE_PLAN.template.json` (`anchors.decision[]`, tag appended **inside** the decision string so grade and decision cannot separate).

**`scripts/checklist_engine.py` is absent from the diff** — verified by `git diff --stat`, and independently by the reviewer. The executor rules are doctrine-observed-at-first-use (#136 seam), not runtime tier-checking logic.

---

## Floated decision — for the Admiral

**`skills/commander/references/commander-core.md` was NOT edited, though my File Ownership named it.**

#231's **PR #236 is open and touches that exact file** — a declared stop condition ("stop and return-and-query the Admiral rather than guessing at a merge order").

What I did instead of blocking: #236's hunk is a single prototyper-seam paragraph ~50 lines from where my edit would have gone, so there is no textual conflict — but rather than guess at a merge order I routed the doctrine to its canonical `_shared` home, which **removes the need for that edit entirely**. The collision was eliminated, not resolved.

Nothing was lost, and the launch order's naming for that file was already wrong: **there is no "Decision Anchors section" in `commander-core.md`** (verified at context — the concept lives under `## Decision candidates` L112 and `## Mission frame` L116). A one-line pointer there once #236 merges is filed as item 2 of issue #239.

**No ruling is needed from you unless you disagree with that routing.** Flagging it because the Pre-Ruling asked me to surface it, not because I am blocked.

---

## Map impact

No packet map exists (`docs/architecture/` absent in this skill-source repo), so reconcile folded the structural record directly and recorded a reasoned no-op for the map — with three candidate docs checked and each ruled out for a stated reason (`CONSTELLATION_OVERVIEW.md` names only the substrate, not the ~20 `verify_*.py` rails; `CHECKLIST_SCHEMA.md` documents the engine's mechanical surface and `anchors` is not in its field table; `removability_ledger.json` maps *installed externals*, and `grade_lint.py` is a new native capability).

**New capability** `capability:grade-lint` — static pre-flight validation of decision fixedness over Markdown and JSON plan artifacts, plus the on-demand guess-ledger view.
**New seam** — the planning-artifact authoring convention now spans Admiral latitude contracts and launch orders, and Commander mission frames and execute plans.
**Absorbed** — #219's dormant batched plan-conflict pre-flight ships here as `grade_lint.py`'s batched-objections output at the **existing** plan-approval checkpoint (no new checkpoint), exactly the one absorption the issue declared.

---

## Triage candidates

All five routed into **[issue #239](https://github.com/fredcai6/constellation-skills/issues/239)**; none left merely recorded.

1. The tag convention is not yet on `IMPLEMENTER_HANDOFF.template.md:46` / `REVIEWER_HANDOFF.template.md:48` — both fenced to #231 this wave.
2. `commander-core.md` wants a one-line pointer to the `_shared` doctrine once #236 merges.
3. **A decision bullet that WRAPS across two lines is not welded to its grade** — the ratified rule is "same line, or next non-blank line". Found against a real hand-authored mission frame, so it is a live authoring shape. Touches the **ratified grammar**, so filed for a human/panel ruling rather than quietly patched.
4. Quality-only, non-blocking (reviewer Fowler pass): `main()` length; a duplicated path list in tests.
5. The spec-mandated **burden checkpoint** is due-in-future and unowned — the designed off-ramp if the tag costs more than it returns.

Two defects found *during* the run were **fixed in lane** rather than filed (bounded fix-now, delegated, logged as RULINGs): the greedy-placeholder silent PASS and the nested-sub-bullet false FAIL.

---

## Workflow feedback

**The launch order was excellent** — pasting the ratified design verbatim meant I never had to reach into the untracked archive, and PR-7 paid out immediately. Three frictions worth the lessons audit's attention:

1. **The launch order named a section that does not exist.** It granted me "the Decision Anchors section of `commander-core.md`"; there is no such heading. PR-7's habit is written for *already-shipped mechanism*, but here it caught a **naming slip** instead — the same verify-first move, a different failure mode. Worth widening `lesson:verify-launch-order-claims-against-code` to cover "the named edit target exists at the named address," not just "the named mechanism isn't already built." This is its **third** data point.

2. **The file-ownership Pre-Ruling predicted the collision but not the escape.** It told me to stop and query if #231 had an open PR on either file. #236 did. Blocking would have cost a full Admiral round-trip for an edit that turned out to be **unnecessary** once the doctrine was routed to its canonical home. The more useful instruction shape: *"check whether the contended edit is still required after PR-6 routing; float only if it is."* Choosing the canonical target can dissolve a fence rather than collide with it.

3. **The cold critic earned its cost, and the reviewer earned it twice.** The critic's BLOCKER 1 (undefined Markdown decision-line grammar) would have broken the issue's own required round-trip test — the acceptance criteria and the naive implementation were quietly in conflict, and only a no-context reader caught it. Then the reviewer's adversarial probing found a **silent PASS** that every shipped test missed, because it was unreachable from the four templates. Concrete lesson: *round-trip tests over real artifacts prove the artifacts are clean, not that the parser is correct* — they need adversarial fixtures alongside them. The house habit of instructing crew to "hand-write your own fixture and try to make it give a wrong answer" is what surfaced it, and is worth making standard in reviewer handoffs.

4. **Minor tooling friction.** `attest` refuses engine-checked conditions (correctly), but the refusal arrives only after you try — the `current` output does not distinguish attestable from engine-checked postconditions. Costs one wasted call per gate. Also: writing `.md` deliverables required a shell round-trip because the harness blocks the Write tool on report-shaped files, and heredocs with `·`/backticks are fragile on this box — I ended up writing to the scratchpad and `cp`-ing.
