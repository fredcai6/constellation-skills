# Reviewer Handoff

## Gate
`g4-review` — composition floor, work-id `w5-gates`, epic #418 wave 5.
**This is the last review of the last gate of the last crew in the epic.** The epic's close sequence
runs on this branch's PR.

Worktree: `C:/Programs/constellation-skills-wt/epic418-w5-gates`, branch `epic-418/w5-bookend-gates`.
Use absolute paths — your cwd resets between bash calls.

## Operational facts — each has cost this run real time

1. **Use `python`, never `py`.** Different interpreters here; `py` has no pytest, so `py -m pytest`
   exits nonzero and reads exactly like a red suite when the tests never ran. `references/windows.md`
   §4 says the opposite; it is wrong on this box and has now cost three crews.
2. **Never pipe a pytest command into `tail` or `head`.** `$?` then belongs to the pipe, and a
   zero-match `-k` selector — which exits **5** — reads as exit 0. Redirect to a file and echo `$?`;
   a redirect is not a pipe.
3. **Find code by text, not line number.** The doctrine test file grew ~1385 lines across g1–g4.
4. **Beware `$(...)` in arguments you pass to the engine** — a previous crew had a finding mangled by
   command substitution. Use a heredoc for anything with shell metacharacters.
5. **This host is CRLF, and there are TWO traps here, not one.**
   - A mutation can silently **fail to apply** if your literal is LF. A previous reviewer's probe hit
     this and would have reported a green suite as proof its guard was load-bearing. **Assert the
     mutation applied.**
   - A restore can silently **fail to restore**: `Path.read_text()` + `write_text(..., newline="")`
     converts CRLF to LF, and checking the restore with `read_text() == read_text()` **cannot detect
     it**, because universal-newline translation normalizes both sides. The g4 implementer's probe
     printed `RESTORED IDENTICAL: True` while the bytes had changed; only `git status` caught it.
     **Verify restores with `read_bytes()`, and check `git status` when you are done mutating.**
6. Two files under `.agent-work/epic-418-redux/transitions/close-to-w5/` show `M` with **empty
   diffs** — a CRLF stat artifact. **Leave them unstaged.**

## What to review

The change is **committed**. Your target is a real ref:

```bash
git diff 84d1e998 764a2728 -- tests/test_iterative_planning_doctrine.py
```

`84d1e998` is g3's last commit (the pre-g4 baseline); `764a2728` is the change under review. Name the
commit, not a range — there are Commander work-area commits in between that are not part of the
change.

The implementer's contract is `.agent-work/w5-gates/crew-handoffs/g4-implement-HANDOFF.md`; its
result is `.agent-work/w5-gates/crew-handoffs/g4-implement-RESULT.md`. **Read the result, then verify
it rather than trust it.**

**Read the RESULT's provenance note first.** The implementer measured everything but hit a hard
context trip before writing its own result file, and correctly refused to attest what it had not run.
The Commander ran the one remaining command and transcribed the report, marking which sections are
the implementer's measurements and which are the Commander's. **You are the first independent pair of
eyes on the implementer's numbers.** That makes your job weightier here than at a normal gate: treat
every measurement in that file as a claim.

## The change in one paragraph

One new class `ComposedShippedArtifactTests` in `tests/test_iterative_planning_doctrine.py`, holding
three composition tests. They share one fixture in which the **real installer** lays down a real
bundle, the **real `init_work_area.py` entrypoint** (subprocess, not in-process `resolve_spine`)
instantiates *that bundle's own* spine template, and the **bundle's own verifier** runs as a
subprocess with `HOME`/`USERPROFILE` pointed at an empty directory. Production diff is **the test
file only** — `353 15` — and the other three owned files take zero-line diffs.

## The two required confirmations — this gate's core

The plan's own words: *the reviewer must confirm the composition tests are not tautological — each
must be shown to go red on a stated broken input — and must confirm no owned fix silently depended on
another crew's file.*

**1. Non-tautology. Build each broken input YOURSELF and watch it go red.** The implementer states
these; they are claims until you reproduce them:

| test | broken input | claimed |
|---|---|---|
| `compose_spine` | literal `<branch>` reintroduced into the shipped template | RED, `{} != {'archive.c2b': ['<branch>']}` |
| `compose_spine` | `-gt 0` → `-ge 0` (exit code stops carrying the verdict) | RED, `0 == 0 : no PR at all is not reachable` |
| `compose_verifier` | `_is_installed_bundle` reverted to `path.name.startswith("constellation-")` | RED **twice** — decoy leg returns **exit 0**, and the `constellation-skills`-named checkout refuses for the wrong reason |
| `compose_verifier` | `--skills-root` ignored (`if skills_root is not None:` → `if False:`) | RED, `0 != 1` |
| `compose_terminal` | pre-#506 conflation restored (stop branch deleted) | RED, `0 != 1 ... only advance or replan may authorize NEXT_WAVE` |
| `compose_terminal` | relaxation widened to any null `launch_id` | RED, `0 == 0 : repair must not inherit the stop relaxation` |

The decoy row is the wave's sharpest evidence — **#501 reproduced live against the artifact a user
installs**, not in a repo-side fixture. Verify it specifically.

**2. No owned fix silently depended on another crew's file.** The three fixes touch
`scripts/verify_iterative_role_artifacts.py` and
`skills/commander/templates/COMMANDER_SPINE.template.json`. Confirm none of them reaches into
`scripts/checklist_engine.py`, `scripts/install_constellation.py`, the handoff templates,
`docs/CREW_CONTEXT.md` or `docs/TREND_SNAPSHOT.md` for its correctness in a way that would break when
another crew's branch merges. Four other crews are merged or queued behind this branch, so a silent
cross-crew dependency is a merge-order hazard, not a style point.

## Three things to check hardest

**(a) Is the fixture real, or does it look real?** The whole claim of this gate is that these tests
run the **shipped artifacts** rather than repo-side copies. Confirm the installer really installs,
that `init_work_area.py` is invoked as a subprocess against the **bundle's own** template rather than
the repo's, and that the verifier under test is the **bundle's copy**. If any leg silently falls back
to the repo tree, the composition claim is weaker than stated and that is a finding.

**(b) The no-op guards.** The implementer names its own traps, which is the right instinct, but names
are not measurements. The one worth probing hardest: it says every `compose_verifier` leg must seed a
valid `REPLAN_INPUT` first, because `verify_commander` reads the artifact **before** resolving the
skills root — so an unseeded work area refuses on the missing artifact and never reaches the guard,
and the refusal test becomes a no-op that passes for the wrong reason. **Check that each refusal leg
asserts the refusal REASON and not merely a nonzero exit.** This run has been BLOCKed twice already,
both times for a check that could not fail: at g2 a mutation leg whose mutated field was legitimately
empty, at g3 a stub that answered unmodelled flags instead of refusing.

**(c) The full-suite delta.** Claimed: **1891 passed, 2 skipped, exit 0**, against a base of 1867 at
`aa2038d9` — **+24**, attributed 12 guard (g1) + 3 stop (g2) + 6 archive (g3) + 3 composition (g4),
with 0 tests removed and skips unchanged. **Derive that attribution yourself rather than accepting
it.** Only 3 of the 24 belong to this gate; the other 21 are the earlier gates', and an attribution
that does not reconcile is a finding. Budget ~8-16 minutes for the run (the implementer measured
497s).

## Selector hygiene — a specific thing to verify, not assume

Six selectors are load-bearing close criteria across this checklist: `guard_location`,
`guard_mutation`, `stop_boundary`, `stop_mutation`, `archive_c2b`, `archive_mutation`. They are split
apart precisely so **no gate's floor can be satisfied by a sibling gate's test**. The new class and
its methods are claimed to avoid all six tokens.

The Commander measured each selector after the change and got exactly its pre-g4 count —
`guard_location` 11 / 11 subtests, `guard_mutation` 1 / 6, `stop_boundary` 2, `stop_mutation` 1 / 8,
`archive_c2b` 4 / 4, `archive_mutation` 2 / 11. **Re-derive this.** If any new test matched an old
selector, an earlier gate's mutation floor would have been silently widened after the fact.

Note the implementer's own near-miss, reported honestly: its first plan named a selector
`-k compose_stop`, which **collected zero**, and the engine refused the advance. The method was
renamed to `test_compose_terminal_...` to avoid colliding with g2's `stop_*`. Worth confirming the
rename is complete and no stray `compose_stop` remains.

## One refactor inside the diff that deserves review as a change, not as noise

The 15 removed lines extract the `gh`/`git` stub shim out of
`ArchiveReachabilityRuntimeTests.setUpClass` into a module-level `write_offline_stubs()` now shared by
both classes. The stated reason is good — a check shape one suite proves unmodelled cannot then be
silently answered in the other, which is the g3 BLOCK's lesson applied one level up. **But it is a
change to g3's approved test harness.** Confirm the g3 selectors still collect their exact counts and
that the shared shim did not weaken the flag whitelist the g3 rework installed
(`MODELLED_FLAGS`, and the refusal legs for `--repo someone/else` and `--limit 100`).

## Evidence to reproduce

Run each bare or redirected, never piped. Report exit codes you saw **and collection counts** — zero
collected is a gate failure, not a pass.

- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k compose_spine` — claimed exit 0, 1 collected
- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k compose_verifier` — claimed exit 0, 1 test / 3 subtests
- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k compose_terminal` — claimed exit 0, 1 collected
- Coupled suite — claimed **399 passed / 506 subtests**, exit 0:

```bash
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```

- Full suite — claimed **1891 passed, 2 skipped**, exit 0: `python -m pytest -q`
- The run's own closure check — the Commander measured **exit 0**,
  `iterative role artifact ok: commander (w5-gates)`:

```bash
python scripts/verify_iterative_role_artifacts.py commander --work-id w5-gates --skills-root C:/Users/fredc/.claude/skills
```

  Before fix B this **could not pass from this worktree** — that was this run's own finding 2, in
  neither issue. `--skills-root` is load-bearing: without it the check validates against whatever is
  installed on this machine rather than the branch under review, and would go green or red on machine
  state no PR reviewer can see.

## Map anchors (inbound)

No architecture map — orientation is `DEGRADED-NO-MAP`, anchors named by path, no `struct:`/`decision:` ids.

- **Structural:** all three owned files together plus the doctrine test file — the composition
  surface. **No map id exists for it, which is part of why it needs measuring.**
- **Capability:** all three affected capabilities at once — role-artifact verification, boundary
  transition verification, spine instantiation and archive closure.
- **Constraints:** `docs/agents/ORCHESTRATOR_CONTEXT.md` — a mechanism or workflow behavior change
  owes targeted automated tests **plus** the relevant broader suite, and both commands must be named;
  this gate is where the broader suite is named. A deliberately red suite across gates is a plan
  smell; the coupled-suite condition on g1–g3 was the answer, and this gate is the full-suite
  backstop.
- **Decision anchor:** whether the run's own execute closure check counts as evidence. **It does**,
  and this gate is where it stops being a formality.
- **Map confidence flags:** this gate is itself the response to the unmapped seam — with no map
  asserting how templates, top-level scripts and installed bundles relate, composition is established
  by running the real artifacts end to end rather than by trusting the structure.

## Scope

Tracked files that may change in this diff: **`tests/test_iterative_planning_doctrine.py` only.**
`scripts/verify_iterative_role_artifacts.py`, `skills/commander/templates/COMMANDER_SPINE.template.json`
and `scripts/init_work_area.py` must all be **zero-line diffs** — every mutation was a probe.
`git diff --numstat 84d1e998 764a2728` should show exactly one production path. **Flag anything else.**

Out of bounds: `scripts/checklist_engine.py` and `tests/test_checklist_engine.py` (crew 4),
`scripts/install_constellation.py` (crew 2), the handoff templates (crew 3), `docs/CREW_CONTEXT.md`
and `docs/TREND_SNAPSHOT.md` (crew 5), and `skills/admiral/templates/ADMIRAL_SPINE.template.json`
(not this run's file — its stale `repair` prose is already a recorded triage candidate, not a defect
to fix here). **Any red outside the ownership scope is a FLOAT to the Commander, not an edit.**

## Return format

Write your REVIEW_RESULT to `.agent-work/w5-gates/crew-handoffs/g4-review-RESULT.md`, with
**APPROVE** or **BLOCK** on the first line, then per-criterion findings with evidence you produced
yourself, the no-op analysis, floats, and workflow feedback.

Return **BLOCK** if: the diff cannot be accessed; any composition test does not go red on its stated
broken input; a test is tautological or a leg is a no-op; the fixture is not running the shipped
artifacts it claims to; the full-suite delta cannot be reconciled; a selector collision exists; the
shared-shim refactor weakened g3's whitelist; or an owned fix silently depends on another crew's file.

**A BLOCK with proof is this gate working, and it is not too late to file one.** Both g2 and g3
blocked, both were repaired, and both are stronger for it. Do not soften a real finding to let the
epic close.

## Suggested model tier

Stronger. You are the only independent check on a set of measurements whose author ran out of context
before it could write them down, and the non-tautology proof has to be built rather than read.
