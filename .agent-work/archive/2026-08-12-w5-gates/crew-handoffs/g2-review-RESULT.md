# Review Result — gate `g2-review`

Gate: `g2-review` — decision-aware `admiral-prelaunch` (issue #506), work-id `w5-gates`, epic #418 wave 5.
Change under review: **`bd56ac8a`** (first reviewed at `57048457`). Baseline: `6f48ece4`.
Survey (engine-driven, 16 checks, lease `g2-review-d`): `.agent-work/w5-gates/g2-review/review.json`.
Fowler pass: `.agent-work/w5-gates/g2-review/fowler-pass.json` (rail exit 0).
My own probes: `.agent-work/w5-gates/g2-review/repro/test_reviewer_probes.py`,
`.agent-work/w5-gates/g2-review/repro/test_leakage_probe.py`.

verdict: APPROVE

**This supersedes a BLOCK.** The review first returned `BLOCK` against `57048457` on close
criterion 1's render leg. The Commander implemented the remedy at **`bd56ac8a`**; I re-verified by
re-running my own shortcuts rather than trusting the report, and the hole is closed. The original
findings are preserved below **unchanged** — the re-verification section at the end records what I
re-ran, its exit codes, and one new non-barring finding.

---

## Blocker — RESOLVED at `bd56ac8a` (see re-verification)

### B1 — a stop-shortcut around the render survives with green tests (close criterion 1)

I built all three stop-shortcuts myself in `verify_admiral_prelaunch` and ran `-k stop_mutation`
unpiped after each, restoring between:

| shortcut I inserted | `-k stop_mutation` |
|---|---|
| skip **G2 validation** when `decision == "stop"` | **RED** — exit 1, `packet_fails_g2` subtest fails |
| skip the **unique-audit-entry match** when `decision == "stop"` | **RED** — exit 1, 3 audit subtests fail |
| skip the **render** when `decision == "stop"` | **GREEN — exit 0, 1 passed, 7 subtests passed** |

With the render shortcut in place the whole file is also green: `27 passed, 32 subtests, exit 0`.
The handoff's own stop condition — "a stop-shortcut survives with green tests" — is met, and
criterion 1 states the rule plainly: a stop path that skips any of those three is a hole, however
green the suite is.

This also violates the repo's own first Verification Discipline rule
(`docs/agents/CREW_CONTEXT.md`): *"A check that cannot fail is indistinguishable from one that
passed... mutate the thing it guards and watch it go red."* The render is named as a survivor in the
commit message and in both stop test docstrings, and the mutation test's docstring claims *"every
requirement that must survive a stop is broken here in turn"* — which is not true of the render.
That is prose standing in for a missing check.

**To be clear about what is and is not wrong.** The shipped code does *not* skip the render — I
verified it runs (see criterion 7). The defect is that nothing in the suite would notice if a future
edit removed it.

**The gap is closable inside the allowed pair, and I proved the remedy discriminates.** The render
guard is live and reachable — it is only unreachable through *packet* data. Degrading the installed
renderer to return an empty string:

- with the delivered code → the stop path **refuses** with `Admiral transition renderer returned
  empty Markdown`; `-k stop_boundary` 2 failed, `-k stop_mutation` 1 failed. **RED.**
- with the render shortcut also applied → the stop path **passes**, `-k stop_boundary` 2 passed,
  exit 0. **GREEN.**

So an eighth mutation — degrade the installed
`constellation-replan/scripts/verify_replan.py` renderer, assert the run refuses with that message
and that neither Markdown file is written, restore — passes today and goes red the moment anyone
shortcuts the render. The test already reaches that installed module (it loads it to assert the
render is nonempty), so no new machinery is needed and nothing outside
`tests/test_iterative_planning_doctrine.py` has to change.

---

## Per-criterion findings

**1. The stop path is not a hole — FAIL.** See B1. G2 and the audit match are genuinely defended;
the render is not.

**2. The `launch_id` relaxation is conditional, not blanket — PASS.** This was the criterion most
likely to be wrong, so I proved it with my own probes rather than by reading:

- `advance` + `launch_id: null` → **REFUSED**, `launch_id must be a nonempty string`
- `replan` + `launch_id: null` → **REFUSED**, same message
- `advance` + `launch_id: "../escape"` → **REFUSED**, `contains unsafe path characters`
- `advance` + `launch_id: "wave-2"` control → **PASSES**, exit 0

The code agrees: `_require_launch_authorization` returns early only when `decision == "stop"` **and**
`launch_id is None`. Every other path falls through to `_string()` + `SAFE_ID`, and `_string`
rejects `None`. The relaxation is gated on the decision.

**3. The mode name is unchanged — PASS.** Still
`choices=("explorer", "commander", "admiral-prelaunch")`; the diff does not touch that line and adds
no mode. `git diff --stat 6f48ece4 57048457 -- skills/ docs/` is empty, so
`ADMIRAL_SPINE.template.json` is untouched as the DECLINE required.

**4. `repair` is still refused — PASS.** I tested the case the delivered mutation does not: `repair`
with a *valid named* `launch_id`. **REFUSED**, exit 1, `only advance or replan may authorize
NEXT_WAVE`.

**5. `boundary_id` validation stayed unconditional — PASS.** It is still inside `_next_wave()`, which
runs before the decision is read, so it cannot be decision-conditional by construction. Measured
anyway: `../escape` is refused under `advance`, `replan`, `repair` **and** `stop`; an empty
`boundary_id` is refused under `stop`.

**6. The inversion IS the fix, not a check bent to pass — PASS.** Stated in my own words below.

**7. All four survivors run under `stop` — PASS.** Each measured, none assumed:

- G2 validation — bypass → RED
- unique-audit-entry match — bypass → RED (3 subtests)
- render — proved it **executes**: degrading the installed renderer makes the stop run refuse
- `CURRENT_TRUTH.md` / `WAVE_REVIEW.md` writes — bypass → RED in both selectors
  (`the control run must reach the writes`)

**8. Both selectors collect nonzero and the coupled suite is green — PASS.** All unpiped, real exit
codes: `-k stop_boundary` 2 passed / 25 deselected / exit 0; `-k stop_mutation` 1 passed / 26
deselected / 7 subtests / exit 0; coupled 8-file suite 390 passed / 487 subtests / exit 0. Matches
the reported numbers exactly.

---

## Criterion 6 — the inversion, in my own words

The assertion `assertNotEqual(0, refused.returncode, "stop cannot authorize NEXT_WAVE")` **was the
defect written into a test. Inverting it IS the fix, not a check bent to pass.** Two independent
grounds:

**(a) The repo's own recorded contract already said so.**
`skills/admiral/templates/ADMIRAL_SPINE.template.json` — untouched by this commit and explicitly
outside this run's scope — declares `"decisions": ["advance", "repair", "replan", "stop"]` and states
that the verifier *"requires a unique advance|repair|replan|stop exit."* Under the contract the repo
had already written down, a `stop` is a legitimate exit the verifier must be able to verify. The old
assertion contradicted that contract. The **code** was out of line with the contract; the test was
not out of line with the code.

**(b) The assertion cannot coexist with any correct implementation.** There is no way to implement
"a stop transition verifies" that leaves `assertNotEqual(0, rc)` true. A check that no correct
implementation of the required behavior can satisfy is not a guard on a general property — it is a
transcription of the *old* behavior. Replacing it is updating the specification, which is what a
contract change is supposed to do.

**The counter-test I applied.** A bent check is an *orthogonal* guard loosened so a new path slips
through. So I checked whether any orthogonal guard was loosened, and none was: the Markdown writes
still refuse when bypassed, an unsafe `launch_id` is still refused **under stop**, `repair` is still
refused, and `boundary_id` safety still holds under every decision. Only the one assertion that
encoded the conflation changed. It also moved no test counts, consistent with swapping an
expectation inside an existing subtest.

**One residual, recorded honestly.** The old assertion incidentally covered "a stop must not bless a
named next launch," and that is genuinely weaker now: a `stop` with a populated `launch_id` passes.
I checked every consumer — nothing outside this verifier reads `NEXT_WAVE.launch_id` — so no launch
is authorized by that field today. Observation, not a blocker.

---

## Constraints

- **Live epic packet `.agent-work/epic-418-redux/transitions/w4-to-close/` — byte-unchanged.**
  Clean `git status`, and untouched by the commit. It was copied into the fixture, never mutated.
- **Pre-ruling 6** — respected. The only changed expectation is the sanctioned inversion.
- **Verifier change owes targeted tests plus the broader suite** — both present and reproduced.
- **Test naming contract** — both `stop_boundary` and `stop_mutation` present; neither selector
  is a zero-match.
- The two `close-to-w5` files showing `M` have empty diffs (CRLF stat artifact). Left unstaged.
- Every file I mutated was restored. `git status --porcelain scripts/ tests/ skills/` is empty and
  `git diff HEAD` over them is empty — the tree is identical to `57048457`.

## Scope

Exactly the two allowed tracked files: `scripts/verify_iterative_role_artifacts.py` (+45/−7) and
`tests/test_iterative_planning_doctrine.py` (+187/−2). No specific exclusion was touched —
`git diff --name-only` over `checklist_engine.py`, `test_checklist_engine.py`,
`install_constellation.py`, `docs/` and `skills/` is empty.

## Observations (not blockers)

- **O1.** A `stop` with a populated `launch_id` passes. Deliberate and documented; no consumer reads
  the field. Worth a conscious ruling if a launcher ever reads it.
- **O2 (Fowler).** The mutation test is ~75 lines with seven nested closures and will strain when the
  eighth mutation lands; the `NEXT_WAVE.json` write is duplicated four times across the new tests.

## Triage candidates

- **tc1.** A `repair` transition cannot be **verified** at all, only refused — the same defect class
  #506 fixed for `stop`. `ADMIRAL_SPINE.template.json` says the verifier handles a unique
  `advance|repair|replan|stop` exit and "enforces repair safety," yet a repair packet exits nonzero
  outright. Ruled out of scope for #506; deserves its own issue.
- **tc3.** The renderer mutation is never restored after the final loop iteration, leaving the
  per-class installed replan bundle degraded for every test that runs after it. Inert today; a
  landmine for the next test added to that class. Fix: restore after the loop or in a `finally`.
- **tc2.** `render_replan_markdown()` re-runs `verify_replan_result()` as its first statement, and
  `verify_admiral_prelaunch` **discards** the rendered value (the writes come from `result[...]`
  directly). So the `"cannot render"` except-branch is unreachable after the verifier's own G2 call
  passes on the same objects — dead code — and it is why the render cannot be falsified by packet
  data. Lives in `skills/replan/scripts/verify_replan.py`, outside the reviewed pair.

## Re-verification at `bd56ac8a`

Remedy commit: `bd56ac8a`, **test-only**, +26/−3 in `tests/test_iterative_planning_doctrine.py`.
`git diff --numstat 57048457 bd56ac8a -- scripts/verify_iterative_role_artifacts.py` is **empty** —
the verifier is byte-clean, so the change under review is unchanged in behavior and only its guard
grew. The new mutation `renderer_returns_empty` degrades the **installed** replan renderer to
`return ""` and is registered as the eighth entry, with `assertEqual(8, len(mutations))`.

### I re-ran my own shortcuts — the leg that was green is now red

| shortcut I re-inserted | `-k stop_mutation` at `bd56ac8a` |
|---|---|
| skip the **render** under stop | **RED — exit 1, `SUBFAILED(mutation='renderer_returns_empty')`** |
| skip **G2 validation** under stop | **RED** — exit 1, `SUBFAILED(mutation='packet_fails_g2')` |
| skip the **unique-audit match** under stop | **RED** — exit 1, 3 audit subtests |

All three legs of close criterion 1 now go red. **Criterion 1: PASS.** Tree restored after each;
`git status --porcelain` over `scripts/ tests/ skills/ docs/` is empty.

### Evidence, re-run unpiped with real exit codes

- `-k stop_boundary` → 2 passed, 25 deselected, **exit 0**
- `-k stop_mutation` → 1 passed, 26 deselected, **8 subtests**, **exit 0**
- coupled 8-file suite → 390 passed, **488 subtests**, **exit 0** (the +1 subtest is exactly this leg)

### Your question 1 — is the new mutation a no-op like the `revised_forecast` case? **No.**

Three independent reasons:

1. **Its applied-assertion is discriminating.** It asserts `'return ""'` is present after the write.
   I checked the pristine renderer: `grep 'return ""' skills/replan/scripts/verify_replan.py` exits
   **1** — the string does not pre-exist anywhere in the file, so that assertion cannot pass unless
   the surgery actually took. This is precisely the property the `revised_forecast` mutation lacked.
2. **The refusal is attributable to the renderer alone.** The loop restores all of `pristine`
   (including the renderer) at the head of each iteration, so this subtest runs on an otherwise
   untouched stop packet, and it asserts the specific message `Admiral transition renderer returned
   empty Markdown`, which exactly one clause emits.
3. **It is load-bearing, proven by discrimination, not by inspection** — re-inserting my render
   shortcut turns this exact subtest red. A mutation that proves nothing cannot do that.

The surgery is also sound: it splices `return ""` in as the first statement of
`render_replan_markdown`, ahead of that function's own internal `verify_replan_result` call, so it
degrades the render **without** disturbing the G2 clause the verifier ran earlier. The module stays
syntactically valid (the injected line precedes the docstring), so nothing fails at import.

### Your question 2 — cross-test leakage? **Yes, real but currently inert.** (finding F1)

`renderer_returns_empty` is the **last** entry in the mutations dict, and the restore loop rewrites
`pristine` at the **start** of each iteration. Nothing restores the renderer after the final
iteration, and there is no `finally` or `tearDown`. I proved this deterministically rather than
guessing at ordering — `repro/test_leakage_probe.py` calls the delivered mutation test and then
inspects state within the same class run:

- `LEAKED=True` — the installed renderer is still degraded when the mutation test returns
- a subsequent `run_role("admiral", "admiral-prelaunch")` in that class returns **rc=1**,
  `REFUSED: Admiral transition renderer returned empty Markdown`

**Blast radius is bounded, and it is harmless today:**

- `IS_TEMP_INSTALL=True` — the mutation writes the per-class `tempfile` install, torn down at
  `tearDownClass`. `REPO_RENDERER_UNTOUCHED=True` — the repo's own
  `skills/replan/scripts/verify_replan.py` is never written. No host or repo pollution.
- Measured collection order puts only `test_all_cross_skill_paths`,
  `test_commander_execute_refuses...` and `test_explorer_confirm_refuses...` after it, and all three
  invoke the admiral mode **zero** times. `verify_commander` loads the replan module but calls
  neither `verify_replan_result` nor `render_replan_markdown`; `verify_explorer` does not touch it.
- So **no test fails and none passes for the wrong reason today.**

**Why it is still worth fixing now, and why it does not bar the gate.** It is a latent landmine: any
future test added to this class that sorts after the mutation test and exercises `admiral-prelaunch`
would fail confusingly — or, if it asserts a *refusal* as three of this class's seven runtime tests
do, **pass for the wrong reason**, which is exactly the hazard `CREW_CONTEXT` names. But it produces
no incorrect result today, never escapes the temp install, and is not a defect in the change under
review. Recorded as a preserved `fail` at `c9-mutation-leakage`, carried through `consolidate` with
an explicit override reason rather than softened, and routed as **tc3**. One-line fix: restore
`pristine` after the loop (or in a `finally`), not only at the head of the next iteration.

### Criterion status after re-verification

All eight close criteria **PASS**. No stop condition from the handoff is met.

---

## Workflow Feedback

- **The handoff's claim that "everything under `.agent-work/` is local-only and correctly absent from
  the tracked diff" is false.** The commit contains nine tracked `.agent-work/w5-gates/` files. It is
  the established convention here (g1's commit did the same), so it is not drift — but a reviewer
  told to "flag any tracked file outside that pair" hits an immediate contradiction and has to go
  read git history to resolve it. Say "workbench artifacts under `.agent-work/` are tracked and
  expected" instead.
- **Criterion 1 and criterion 7 ask different questions about the same four survivors** — 7 asks
  whether they *run*, 1 asks whether the suite would *notice their removal*. They can and here do
  diverge, and nothing in the handoff flags that they might. Naming the distinction would have saved
  a pass of re-reasoning about which one the render was failing.
- The engine's `--session-id` must follow the verb, not precede it; the reference's verb-loop section
  shows it in the flag list but not in positional order, which cost one refused batch.
- Operational facts 1–4 were all accurate and all saved time. `-k probe` matching my class name
  (`ReviewerProbes`) silently widened collection from 7 to 14 — worth the same warning as the
  `tail`/`head` one, since a `-k` selector matching more than intended is as misleading as one
  matching less.
