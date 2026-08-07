# Cold Review — issue-set cut for "step-lighter, step-back"

**Reviewer:** independent (fresh context, not the author)
**Inputs:** ISSUE_SET.json; DESIGN_SPEC.md (incl. 30-finding critic table + dispositions); live open-issue list; bodies of #220, #219, #139, #136, #217, #224, #172, #216, #225, #171.

## Verdict: APPROVE-WITH-EDITS

The cut is faithful and complete on the dimensions that matter most: every spec section S2–S11 lands somewhere, every critic-EDIT correction is honored verbatim in the issue bodies, the single real edge (C→F) is correct and complete, and the AFK/HITL typing is sound. What needs fixing is the **supersede plan's safety**, not the issues themselves: closing four tracked design stubs (#171/#172/#216/#225) is only safe if G/H are actually filed as open tracking issues, and the #220 rewrite must be surgical. None of the defects require re-cutting an issue body; they are filing/comment-precision edits.

### Coverage (PASS)
- S2→A, S3→A(item 6, doctrine line; lint deferred), S4→B, S5→C, S6→D, S7→E, S8→D(folded), **S9→A(item 6 return-thin/write-fat one-liner)**, S10→F, S11-B→G, S11-C→H, S11-D→#139(edit). Nothing silently dropped. S2/S3 correctly collapsed intra-issue (no cross-edge needed); S9 correctly demoted and lands in A.

### Fidelity to critic-EDITs (PASS)
S10 corrected gap list (`_collect_changed_files` already tested; real target `_glob_to_regex` + skipTest), the CI skip-guard (RED not green without git), lint-loud/execute-safe, the deferred S3 lint, INV-1 oracle map, measure_overread instrument, coverage floor current-minus-1, doc-drift three sites, S6 expires/leans deferred-pending-C, S8-into-S6 fold, captured-worktree sweep, burden checkpoint — all present and accurate. All 9 REJECTs correctly kept as-is (ports-lite, INV-3 totality, settle-required, the schema mechanism). No rejected item smuggled in.

## Findings

**1 — MAJOR — epic supersede plan / issues G,H — closing #171/#172/#216/#225 risks orphaning the threads.** #217→A, #224→E, #205→F, #198→F, #216→G, #225→G, #171→split G/H, #172→H all absorb their source content correctly (verified against each body). But G/H carry "UNCONFIRMED — DO NOT CUT," and the epic calls them "NOT dispatchable." If G/H live only in the epic body (not filed as issues), closing four tracked stubs removes the step-back + slice-wise threads from the live backlog. **Fix:** file G and H as *open, non-dispatchable* `design-thread` issues — exactly the status #139 already holds (an open issue bearing the same marker) — and point each closed stub's comment at the new G/H numbers. If filing G/H is not intended, keep #171/#172/#216/#225 **open** with comment-links instead of closing.

**2 — MINOR — issue A / #220 rewrite precision — invented scope + over-strike risk.** A absorbs three #220 items: the preconditions-narration item (authorized by S2.1) ✓, the RAIL-banner ordering (A item 4), and the attest by-reference hint (A item 2). The latter two are **not described in confirmed spec S2** — cohesive and honestly declared, but scope beyond the spec. Also, #220 item 6 has two facets; A absorbs only the *by-reference* facet, **not** the `--field`/`attach` facet. **Fix:** (a) flag A item 4 + by-reference as scope-beyond-S2 the way F flags #198; (b) the REWRITE-#220 step must strike ONLY item 3, item 5, and item 6's by-reference sub-bullet — keeping item 6's `--field` sub-bullet and items 1,2,4,7,8,9,10.

**3 — MINOR — issue F / #198 fold — acceptable, keep the flag.** Folding install_constellation.py:430-431's stale comment (#198) into F's doc-drift sweep is same-class work, transparently flagged ("small scope addition flagged at review"). Judged **acceptable**; spec S10 doesn't name it, so retain the flag for the reviewer.

**4 — MINOR — epic / #219 comment undercount.** "pre-flight thread ships via D; threads 1+3 remain" is imprecise: only #219's *pre-flight plan-conflict scan* minor bullet is absorbed by D. Thread 2 (issues/specs↔architecture) and the other minor bits (model-tier, plain-language lint) also remain. Non-destructive (it's a comment), but **fix:** comment should say only the pre-flight-scan bullet is absorbed; everything else stays.

**5 — MINOR — issue G/H / #171 split — one facet unhomed.** #171's "tied into the network so we can see integrated behavior validated across the codebase" facet isn't clearly captured by G (map-diff-for-review) or H (plan-time scenarios). **Fix:** name that facet explicitly in G's or H's inputs so it isn't lost when #171 closes.

## Dimensions that PASS clean
- **Edges:** C→F is the right and only edge (F's tests need C's CI + skip-guard). The spec's two couplings map correctly: S2/S3 intra-A (no edge), S5↔S10 = C→F. D does NOT wait on H (correctly — D ships now with the deferral noted). No false independence/ordering.
- **Typing:** A–F safely AFK (bounded, spec-ratified, test-gated; A keeps the #145 freeze untouched; C's git-bash pre-check is a resolvable/floatable unknown). G/H HITL reasons are sound (they name the spec's own open questions). The DO-NOT-CUT marker is correct usage, mirroring #139.
- **Admiral-readiness:** waves runnable from the epic body — dispatch {A,B,C,D,E} then F, G/H excluded. Consider stating the dispatchable set explicitly.
- **Comment #136** (re-scope to eval-on-change) and **edit #139** (append S11-D constraints) are faithful and non-destructive; G cross-links #139 correctly.
