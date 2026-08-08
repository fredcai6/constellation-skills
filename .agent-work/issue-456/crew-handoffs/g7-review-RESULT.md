# Review Result

## Assigned Gate
`g7` — authored comment-tag pass and the cull test (issue #456). Ninth of eleven gates.

## Result
`BLOCK`

## THE main question: retire vs alias

**Retire was the wrong reading, and shipping it silently is the defect.**

The spec text ("collapse them to Rationale:/Rejected:/See:", "trial vocabulary with an explicit
right to cull after contact") is genuinely compatible with both retire and alias — the crew is
right that this is underdetermined text, and right to have surfaced it as a decision candidate. But
the spec's own reasoning for the vocabulary — "a tag survives when a tool visibly consumes it" —
is not neutral between the two readings once you apply it to code that already exists. Retire's
actual effect on the only real corpus in existence (f1Brainz PR #733, confirmed directly via
`git show e3d6b542`: 4 `Constraint:`, 1 `Rejected:`, 1 `Rationale:`) is that four of six real tags
go from potentially visibly-consumed to never-again-consumed, permanently, with zero signal — the
survival law's own failure condition, landing on real text, not a hypothetical. Reading "4 of 6
tags are one word" as evidence the cull "costs little" (cull-verdict.json's own framing) inverts
the fact: it is evidence retire breaks the majority of the corpus. Concrete proof this bites in
practice, not just in theory: `CommentTagStaleAnchorJoinTests`'s own docstring discloses the
handoff's own worked illustration named `Constraint:`, and the crew had to swap it to `Rationale:`
mid-gate because the cull broke its own example.

**Recommendation: alias, not retire.** Keep recognizing `Assumption:`/`Constraint:` at extraction
and normalize their kind to `Rationale` (widen `TAG_START`'s alternation, add one kind-normalization
lookup at the emission site). This satisfies "the consumer no longer distinguishes them" — the
render path (`tag_lines`) stays exactly as branch-free as shipped, the cull test's own evidence is
untouched — while every real, already-written tag stays visibly consumed. Small, scoped change,
not a redesign.

If the human/Commander instead confirms retire is what "trial vocabulary, right to cull" always
meant — a reasonable reading I disagree with — **it must not be silent.** `g6`, the immediately
preceding gate on this same run, already blocked on the identical failure shape in the opposite
direction: a silent skip converts a fault into permanently-dead detection with no signal. Retiring
a keyword with zero warning is that same defect. Ship a one-line advisory (mirroring `g6`'s own
established advisory pattern) naming the retired keyword when one is used, if retire ships.

This is BLOCKING regardless of which reading ultimately wins — the silence is the defect, not
just the reading.

## Handoff compliance
Otherwise met. Extraction, render, staleness join, and the checkable cull-verdict artifact all
work as specified and are independently reproduced (see Evidence verdict). The one substantive gap
is the main question above.

## Scope drift
None. `git show 0d1af801 --name-only` confirms production changes confined to
`scripts/code_map/extract.py` and `scripts/code_map/render.py`; tests confined to
`tests/test_code_map.py` and new files under `tests/fixtures/comment_tags_corpus/`; the artifact
lands exactly at `.agent-work/issue-456/cull-verdict.json`. Grepped both production diffs for every
named exclusion (`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`,
`page_location_matches_content`, `thresholds`) — zero hits. `g6`'s staleness machinery
(`span_hash`, `anchor()`'s hash-persisting branch, `run()`'s store diff) is unmodified — every
change is either a new function or a new one-line call site. The untracked `map/` tree is correctly
absent from this commit.

## Evidence verdict
All required evidence present and independently reproduced, not taken on the crew's word:
- `-k 'comment_tags'`: reran directly, 18 passed, 8 subtests, exit 0 — exact match.
- `-k 'stale_tag'`: reran directly, 15 passed, 12 subtests, exit 0 — exact match (grown by exactly
  one join test).
- Fresh scratch `build`+`check` (own scratch dirs, never touching the tracked `.code-map`/`map`):
  113/3865/3979 modules/entities/pages, `ids: 0`, `stale_tags: []`; `check` 7/7 exit 0 including
  `deterministic-rebuild`. Small variance from the RESULT's 112/3862/3975 is concurrent-crew churn
  on the tracked tree, the same pattern the `g6`-review reviewer independently observed and ruled
  a non-defect.
- `TAG_START.pattern` and `tag_lines` read directly, match the artifact's claims.
- Full suite (1825/2/692/0) not rerun this review per the dispatching Commander's explicit
  instruction (already independently verified, ~7 min); deferring to that is consistent with this
  run's own established practice.

Four live mutation/attack experiments were run against the actual source (all reverted, confirmed
clean via `git diff --quiet`, never `git status --porcelain`) to test claims rather than accept
them — see the survey's `r1-handoff` finding for full detail on each:
1. AST-walk pin test (`test_comment_tags_render_path_carries_no_branch_on_kind`): catches an
   explicit `if kind ==` branch; **does not** catch a dict-lookup dispatch or a `match` statement
   (zero `ast.Compare` nodes produced by either) — narrower than its own docstring claims, though
   two other content-assertion tests happen to catch the specific dict-lookup mutation by accident.
2. `tags_in` stubbed to `return {}` (empty implementation): 12 of 18 tests correctly failed,
   including both negative-control tests via their positive controls — confirms the "inferred red"
   TDD claim for m1–m4 and the positive-control design both hold under attack.

## Code/doc quality
Fowler pass complete (`.agent-work/issue-456/g7-review/fowler-pass.json`, verified by
`verify_fowler_pass.py`, exit 0): one real, non-blocking duplication flagged (the forward-scan
predicate shared between `tags_in`/`anchors_in`, and the decorator-aware lookup shared between
`tag_check`/`anchor()` — both small, self-disclosed in the new code's own comments); one logged
override (the `{"kind","text"}` tag payload is a direct instance of the module's own pre-existing,
documented statement-payload convention, not a new data-clump). All other baseline smells absent.

One constraint violation: the handoff's own "the run report carries no timings" is violated by
`g7-implement-RESULT.md`'s evidence section, which states literal wall-clock timings ("378s",
"379.42s / 0:06:19"). Minor, easy fix, but a real, named, verbatim-stated constraint.

Also-verify items 3–7 (cull-verdict pinning, staleness-join framing, TDD discipline, negative-test
self-check, convention gap) are graded individually in the survey's `r1-handoff` finding — none
blocking on their own; two produce phrasing corrections (the commit message's "5 tests re-derive"
claim is accurate for 2 of 5, not 5 of 5; the staleness test's "join" framing overstates what is
actually independence-under-coexistence, since g6's machinery never reads tags at all).

## Map impact verdict
- **Evidence supports claimed change:** yes, independently reproduced above.
- **Constraints not violated:** no — see the "run report carries no timings" violation above.
- **Notes match the diff:** yes, with the caveat that "5 tests re-derive from the code" (commit
  message) overstates 3 of the 5 `CullVerdictArtifactTests`, which check only the artifact's own
  internal consistency.
- **Decision candidates surfaced:** yes, correctly — the crew flagged the vocabulary/cull-test
  reach as a decision candidate rather than silently finalizing it. This review confirms that
  escalation was warranted and adds that the silent-failure mode compounds it into an active
  defect.
- **Durable context routed:** two triage candidates flagged via `flag-candidate` (tc1: `See:` tags
  render as literal text, not a link; tc2: document the tag/anchor binding-granularity asymmetry).

## Reconciliation check
BLOCK. The retire-vs-alias reading is a real divergence point the Commander/human must resolve —
see the main question above. Not a new decision invented by this review; it is the same escalation
the crew itself raised, confirmed real and given a concrete recommendation.

## Blockers
- Silent breakage of retired-keyword comments (`Assumption:`/`Constraint:`) — rework to alias
  (recommended), or add a visible advisory if retire is confirmed as the intended reading.
- `g7-implement-RESULT.md` violates "the run report carries no timings" — strip the timing figures
  from its evidence prose.

## Out-of-scope observations
- tc1: `See:` reference tags render as literal text (`See: pkg.mod:Sym`) rather than a real page
  link — a navigability gap once real `See:` tags accumulate.
- tc2: the tag/anchor binding-granularity asymmetry (a tag always binds to its enclosing
  entity/module; an anchor can bind to a finer per-statement symbol via `child_sym`) is worth a
  durable doc note so it is not silently rediscovered later.
- The AST-walk pin test's own docstring claim ("no branch on kind") should read "no explicit
  comparison on kind" — accurate to what it checks, not overclaimed.
- The commit message's "pinned by 5 tests that re-derive the claims from the code" should read
  "2 of 5 re-derive from the code; 3 check the artifact's own internal consistency."

## Workflow Feedback

- **Handoff gaps:** none — the handoff's own framing of the main question (two readings of
  "collapse") was precise and made the investigation directly tractable.
- **Context rediscovered:** the pre-existing anchor convention's actual binding behavior for
  module/class-level `Assign` (`self.child_sym(target.id)`, a finer symbol than "the enclosing
  entity") had to be read directly from `visit_Assign`'s pre-existing code — the handoff's
  convention-gap framing describes the crew's resolution but not the precedent it does or does not
  follow, which this review's also-verify-7 finding had to establish independently.
- **Instructions improvised around:** none.
- **What would have made this easier:** none — the handoff's explicit mutation-attack prescriptions
  (dict lookup, `match`, `getattr`) for the AST-pin question made that experiment fast to design and
  run exactly as asked.

## Return status
`complete`
