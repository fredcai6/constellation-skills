# Implementation Result

**Verdict: COMPLETE.** Fix A's cheapest shape was not refuted. The honest-null branch was tested and did
not fire; the evidence for why is in "The seam, measured before changing it" below.

## Assigned gate
`g2-implement` — decision-aware `admiral-prelaunch` (issue #506), work-id `w5-gates`, epic #418 wave 5.

Worktree `C:/Programs/constellation-skills-wt/epic418-w5-gates`, branch `epic-418/w5-bookend-gates`,
started at HEAD `6f48ece4`.

## Completed slice

`verify_admiral_prelaunch` now verifies a `stop` transition instead of refusing it, keeping the mode name
`admiral-prelaunch`. Verification and authorization are separated into two functions rather than one
relaxed condition, because the ordering wrinkle in the handoff is structural rather than cosmetic.

- **`_next_wave(work_area)`** now checks only what holds regardless of the decision: the exact key set,
  `boundary_id` as a nonempty `SAFE_ID`, and `trigger`. `boundary_id` validation stayed exactly where it
  was and stayed unconditional — it is the path component that locates the transition directory, so its
  check is a path-safety guard, not a launch policy. `launch_id` is deliberately not touched here.
- **`_require_launch_authorization(next_wave, decision)`** is new and carries the policy. It runs after
  `REPLAN_RESULT.json` has been read, which is the only point where the decision is known. Under `stop`
  the authorization clause is skipped and `launch_id` may be `null`; under anything else the original
  `advance`/`replan` requirement is unchanged, so `repair` stays refused.
- **`verify_admiral_prelaunch`** replaces the inline `_require(... in {"advance","replan"} ...)` with one
  call to that function, in the same position. Everything after it — the render, the unique-audit match,
  and the `CURRENT_TRUTH.md` / `WAVE_REVIEW.md` writes — is untouched and still runs for a stop, per the
  Admiral's ruling that options 1 and 2 are taken combined.

The third `_require`, asserting `result["applicable"] is True`, was left exactly as it was. A mutation
subtest asserts it still fires.

### One nuance the ruling settles, recorded because it is load-bearing

The ruling says a stop **may** express "no launch authorized". That is permission, not obligation, so
under `stop` a `launch_id` is accepted either as `null` or as a valid `SAFE_ID`. This matters twice:

1. It is what lets the sanctioned assertion inversion below go green without a second fixture edit — that
   test keeps `launch_id: "wave-2"`.
2. Path safety is **not** part of the relaxation. When a `launch_id` is present, it still gets the same
   `_string` + `SAFE_ID` check, so a stop cannot smuggle `../escape` through. This is asserted directly.

## Inversion statement — required explicitly by the handoff

**Before**, at `tests/test_iterative_planning_doctrine.py:466` (located by its message text, not its line
number — g1 had moved it):

```python
self.assertNotEqual(0, refused.returncode, "stop cannot authorize NEXT_WAVE")
```

**After** (now at `:468-475` in the working tree, inside the same `subTest(launch_authority="stop")`):

```python
self.assertEqual(0, verified_stop.returncode, verified_stop.stderr)
```

**What it now asserts:** that a stop transition, whose packet is G2-valid and whose audit entry matches,
**passes** pre-launch — having authorized no launch. The local variable was renamed `refused` →
`verified_stop` so the name stops contradicting the assertion, and a comment on the line records why the
expectation moved.

**Why this is not a pre-ruling 6 violation.** Pre-ruling 6 forbids changing a recorded exit to make a
check pass — that is, bending the evidence to fit a change. The direction of causation here is the
opposite. The old assertion was not incidental to the fix; it *was* the defect, written into a test. It
recorded the conflation issue #506 exists to remove: that a decision authorizing no launch could not be
verified either. Inverting it is the change under review, not a repair applied to the change under review.
Nothing else was reworded to accommodate it — the suite delta below shows the inversion moved no counts,
because it swapped an expectation inside an existing subtest rather than adding or removing coverage.

## The seam, measured before changing it

The Map Anchors flagged the decision-vs-authorization split as this gate's one unmapped seam and asked for
a measurement first. Measured, read-only, against the live epic packet at
`.agent-work/epic-418-redux/transitions/w4-to-close/`:

- `skills/replan/scripts/verify_replan.py` already treats `stop` as first-class: it is in `DECISIONS`, and
  `stop` is the *only* decision permitted to set `current_wave` to null.
- `render_replan_markdown` never reads `current_wave`, so it has no stop-specific failure mode.
- The live packet is `decision=stop`, `applicable=true`; `verify_replan_result` passes on it and the
  render returns 8611 characters.

So the refusal was entirely local to the two clauses in
`scripts/verify_iterative_role_artifacts.py` — nothing inherited from the seam it delegates to. **The
authorization clause is not load-bearing, and the honest null does not fire.** Scoped precisely: this was
tested for `stop` only. `repair` was not tested for relaxation and stays refused by ruling.

## Scope

**Files changed (exactly the two allowed):**
- `scripts/verify_iterative_role_artifacts.py` — +45 / −7
- `tests/test_iterative_planning_doctrine.py` — +187 / −2

`git diff --stat`: 2 files changed, 232 insertions(+), 9 deletions(-).

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `tests/test_checklist_engine.py`,
`scripts/install_constellation.py`, the handoff templates, `docs/CREW_CONTEXT.md`,
`docs/TREND_SNAPSHOT.md`, `skills/commander/templates/COMMANDER_SPINE.template.json`, hooks, any
`settings.json`, and `docs/agents/*` are all untouched. Confirmed by `git status --short`.

**Live epic packet:** never mutated. The tests `shutil.copy2` the two JSON files out of
`.agent-work/epic-418-redux/transitions/w4-to-close/` into a temp work area and mutate only the copies.
The source pair is tracked in git, so the fixture is reproducible rather than incidental.

**The CRLF stat artifacts** under `.agent-work/epic-418-redux/transitions/close-to-w5/` were left
unstaged and untouched, as instructed. They still show `M` and are still not mine.

## Behavior changed

Yes. `admiral-prelaunch` accepts a verified `stop` transition (exit 0) where it previously refused
(exit 1), and still refuses `repair`, an inapplicable transition, a G2-invalid packet, an unsafe
`boundary_id`, an unsafe present `launch_id`, and any audit-entry cardinality or decision mismatch.

## Test mode

**Required:** test-first. **Satisfied:** yes — red observed before the fix, on the real selector, with
each of the two new golden tests failing on a *different* one of the two blocking clauses.

## Evidence — every command run bare, never piped

### Selector: `stop_boundary`

```bash
python -m pytest tests/test_iterative_planning_doctrine.py -q -k stop_boundary
```

**Exit code 0.** `2 passed, 25 deselected`. **Collected: 2** (confirmed separately with
`--collect-only -q`, which printed `tests/test_iterative_planning_doctrine.py: 2` and exited 0). Nonzero,
so the selector does not fail the gate closed.

The two methods:
- `test_admiral_prelaunch_stop_boundary_verifies_a_transition_that_authorizes_no_launch` — the live
  packet with `launch_id: null`. Asserts exit 0 **and** that `CURRENT_TRUTH.md` and `WAVE_REVIEW.md`
  were written with the packet's own field contents. Those writes are the only observable proof the run
  reached the end rather than short-circuiting — which is what makes this test, not the mutation test,
  the thing that would catch a naive early-return-on-stop shape.
- `test_admiral_prelaunch_stop_boundary_permits_but_does_not_require_a_null_launch_id` — a stop with
  `launch_id: "wave-2"` passes, and a stop with `launch_id: "../escape"` is still refused with
  `launch_id contains unsafe path characters`.

### Selector: `stop_mutation`

```bash
python -m pytest tests/test_iterative_planning_doctrine.py -q -k stop_mutation
```

**Exit code 0.** `1 passed, 26 deselected, 7 subtests passed`. **Collected: 1** (confirmed with
`--collect-only -q`, exit 0). Nonzero.

`test_admiral_prelaunch_stop_mutation_every_surviving_requirement_still_goes_red` runs a green control
first (asserting the writes happened), then breaks one surviving requirement at a time and asserts the run
refuses for that exact reason and before the writes. Each mutation asserts it really applied first. The
seven:

| mutation | expected refusal |
| --- | --- |
| `audit_decision_mismatch` | `verified TRANSITION audit decision must match` |
| `audit_entry_absent` | `must have exactly one verified TRANSITION audit entry` |
| `audit_entry_duplicated` | `must have exactly one verified TRANSITION audit entry` |
| `packet_fails_g2` | `Admiral transition violates G2` |
| `packet_is_inapplicable` | `inapplicable transition cannot authorize NEXT_WAVE` |
| `boundary_id_is_unsafe` | `boundary_id contains unsafe path characters` |
| `repair_names_no_launch` | `only advance or replan may authorize NEXT_WAVE` |

**I proved this test has teeth rather than asserting it.** I temporarily over-relaxed the code to the
plausible wrong shape — `if launch_id is None:` instead of `if decision == "stop":` — and re-ran the
selector. It went red (exit 1) on exactly `repair_names_no_launch`, where a `repair` packet sailed through
with exit 0. Restored, re-verified the anchor line, and re-ran both selectors green.

### Coupled suite

```bash
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py \
  tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py \
  tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```

**Exit code 0.** `390 passed, 487 subtests passed` in 38.74s.

**Delta against the `6f48ece4` baseline of 387 passed / 480 subtests: +3 tests, +7 subtests — fully
accounted for.**

- +3 tests = the two `stop_boundary` methods plus the one `stop_mutation` method.
- +7 subtests = that method's seven mutation subtests.
- The inversion contributes **zero** to both counts, because it changed an assertion inside an existing
  subtest. Nothing else moved. No red anywhere, in or out of scope.

## TDD evidence

- **Failing test observed:** `python -m pytest tests/test_iterative_planning_doctrine.py -q -k
  stop_boundary` → **exit 1**, `2 failed, 24 deselected`, against the unmodified verifier. The two
  failures landed on the two different blocking clauses, which is what proved both were real:
  - `...verifies_a_transition_that_authorizes_no_launch` → `REFUSED: Admiral NEXT_WAVE.launch_id must be
    a nonempty string` (the `_next_wave` clause)
  - `...permits_but_does_not_require_a_null_launch_id` → `REFUSED: only advance or replan may authorize
    NEXT_WAVE` (the authorization clause)
- **Passing test observed:** same command → **exit 0**, `2 passed, 25 deselected`.
- **Refactor while green:** yes — one mutation was swapped after the fact (see Assumptions) and the
  over-relaxation teeth check was run and reverted, both with the selectors green on either side.

## Map Impact

No architecture map exists (`DEGRADED-NO-MAP`), so anchors are by path, matching the inbound vocabulary.

- **Structural anchors touched:** `scripts/verify_iterative_role_artifacts.py` — `_next_wave()` narrowed
  to decision-independent structural validation; `_require_launch_authorization()` added directly below it
  as the new policy seam; `verify_admiral_prelaunch()` now calls it where the inline `_require` was.
  `_verify_transition_audit()` unchanged and still reached on the stop path.
- **Capabilities changed:** role-artifact verification at the Admiral's wave boundary now covers the
  terminal outcome. A stop boundary can be verified, rendered, and written rather than only refused.
- **Constraints honored:** the mode name `admiral-prelaunch` is unchanged (a separate admiral-boundary
  mode is declined, and `ADMIRAL_SPINE.template.json` is not this run's file); `boundary_id` path-safety
  validation stayed unconditional; `repair` stays refused.
- **Decision resolved:** the inbound decision anchor — a stop is a legitimate terminal outcome that must
  be verified, not merely refused — is now expressed in code as two functions rather than one clause. The
  seam it named is no longer unmapped: **the boundary between structural validation and launch policy is
  the point where the decision becomes known**, and that is why the split falls where it does.
- **Claims produced:** the `stop_mutation` test is the standing claim that the relaxation is narrow; its
  teeth were demonstrated against a deliberately over-relaxed build, not assumed.
- **Triage candidates:** one, below.

## Assumptions

- A stop packet may carry a populated `launch_id` (permission, not obligation). Read straight from the
  Admiral's "**may** express no launch authorized". If the intent was the stricter "must be null under
  stop", say so and it is a two-line change — but the sanctioned inversion would then also need its
  fixture changed, since it keeps `launch_id: "wave-2"`.
- The live `w4-to-close` packet pair is stable enough to be a test fixture. It is tracked in git, and
  `.agent-work/` is not ignored, so this is reproducible rather than a read of local scratch state.

## Stop conditions hit

None. The restructure preserved `boundary_id` validation, no non-owned file went red, the authorization
clause did not prove load-bearing, and no policy decision was required beyond the "may" reading recorded
under Assumptions.

## Out-of-scope observations

- **Triage candidate (not a defect, not fixed):** `_validate_forecast` accepts an empty
  `revised_forecast`, which is correct — an epic that stops forecasts nothing — but it means the
  "emptied forecast" shape used elsewhere in this file as a G2-breaking mutation is a **no-op against a
  stop packet**. Anyone reusing that idiom on a stop fixture will write a mutation that silently proves
  nothing. It cost me one red subtest here (see Assumptions/below). Worth a note wherever that idiom is
  reused; no change made.
- **Floats:** none. Nothing outside the two owned files went red at any point.

## Workflow Feedback

- **Handoff gaps:** the handoff was unusually complete — task, intent, scope, exclusions, evidence, test
  mode, stop conditions, and return format were all present and the ordering wrinkle was described
  accurately. Two small things. First, its own re-measured line numbers were already stale by two
  (`_next_wave` is at `:188`, not `:186`; `verify_admiral_prelaunch` at `:210`, not `:207`) — harmless
  because the handoff also told me to find code by text, which I did, but it does show the anchors go
  stale faster than the warning about them. Second, the naming contract fixes the substrings but says
  nothing about the **class**; I put the new methods on `InstalledIterativeRoleRuntimeTests`, whose name
  contains neither token, so `-k` still selects on method name alone. `GuardRuntimeTests` has a docstring
  explaining that exact property for the g1 tokens — that convention is real and load-bearing but lives
  only in a docstring, so a crew member who put these on a differently-named class could widen the
  selector without noticing.
- **Context rediscovered:** whether `.agent-work/` is tracked in git. The handoff told me to copy the
  live fixture but not whether the source would exist in a fresh checkout, and the answer decides whether
  a fixture-backed test is reproducible or locally lucky. One `git ls-files` settled it; an anchor line
  saying "the live packet is tracked" would have saved the question.
- **Instructions improvised around:** the plan template's TDD guidance says to encode the red step as a
  `check: null` postcondition, which assumes red and green are separated by the code change alone. Here
  the sanctioned inversion had to land in the *same* slice as the verifier change — invert it later and
  the intervening suite is red; invert it earlier and it is red for a different reason. I folded both into
  m1 and said so in the imperative. That worked, but the template has no vocabulary for "this slice
  contains a sanctioned expectation change."
- **What would have made this easier:** one line in the handoff stating whether "may express no launch
  authorized" is permissive or mandatory. I derived it from the word "may" and cross-checked it against
  the fixture the sanctioned inversion uses, which agreed — but that is inference on the one point where
  the ruling and the test fixture had to be consistent, and it is the single most likely thing for a
  reviewer to read the other way.

## Return status
`complete`
