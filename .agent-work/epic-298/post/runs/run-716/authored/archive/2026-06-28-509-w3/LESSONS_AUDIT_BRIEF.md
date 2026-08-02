# Lessons-Audit Run Brief — 509-w3

**Epic:** #509 physics→prediction pipeline. **Wave 509-w3:** Phase-F runway-clearing
(harden the fit pipeline + complete single-canonical-longitudinal + fix the CI gate)
BEFORE the deliberate C-phase. Full-autonomy overnight, merge delegated.

**Model tiers:** Admiral = Opus; all 3 commanders + their crews = Sonnet.

**Outcome:** 3 PRs merged to main, 5 issues closed, 2 follow-ons filed.
- Wave 1 (parallel, disjoint fences): cmdr-V #523 (PR #547, HONEST-NULL, #523 closed, #546 filed);
  cmdr-R #495 cluster #542/#543/#544/#538 (PR #548, all closed).
- Wave 2 (sequential): cmdr-C #545 pyright baseline-diff gate (PR #550, #545 closed, #549 filed).

## Artifacts to audit
- ADMIRAL_LOG: `C:\Programs\f1Brainz\.agent-work\509-w3\ADMIRAL_LOG.md` (full rulings/incidents/merges)
- Commander feedback (captured; these hold the verdict content cmdr-R/cmdr-C dropped as idle-without-message):
  `C:\Programs\f1Brainz\.agent-work\509-w3\crew-handoffs\captured-AGENT_FEEDBACK.diff` (cmdr-R + cmdr-V),
  `C:\Programs\f1Brainz\.agent-work\509-w3\crew-handoffs\captured-AGENT_FEEDBACK-cmdrC.diff` (cmdr-C)
- Launch orders: `C:\Programs\f1Brainz\.agent-work\509-w3\launch-orders\cmdr-{R,V,C}-*.md`
- Current playbook: `C:\Programs\f1Brainz\.agent-work\LESSONS.md` (Active section; cap 20, run-tick 15 on main — NOTE cmdr-R's local tick-16 edit was reverted; main is still 15)

## Candidate lessons the Admiral already spotted (audit + route these, plus any you find)

1. **frontier-characterize-v-source** (NEW, from cmdr-V) — When characterizing for frontier-fitting
   views, the x-axis v-source matters as much as the a_long; a comparison that swaps BOTH a_long and
   v-source is confounded. Specify v-source parity in the handoff / characterize the a_long change in
   isolation. Grounding: the cmdr-V parity send-back — Belgium-pass + Monaco-degenerate were pure
   v-source artifact; the real regressions survived only on the isolated (Config-C) comparison.

2. **ci-gate-selftest-in-ci-environment** (NEW, from the cmdr-C send-back) — A CI gate's self-test must
   run in the CI environment, not just locally. A pyright baseline generated locally (Win/py3.14) did
   not match CI (ubuntu/py3.11 + CI pandas-stubs), so the gate failed on its own PR (pre-existing errors
   read as NEW). Fix = compute the baseline from the base branch at CI runtime in the same job. Grounding:
   ADMIRAL_LOG INCIDENT+RULING 2026-06-28 cmdr-C; PR #550 commits 99e0d0c8(fail)→571f258a(env-portable)→
   6fb3f7c4(inject=fail, proof)→d6958be5(revert=pass).

3. **launch-order-shared-files-say-commit-not-edit** (NEW/clarify) — The constellation-commander spine's
   `feedback` step REQUIRES writing AGENT_FEEDBACK.md on disk (its verify checks disk state); a launch
   order that says "DO NOT edit shared files" contradicts the commander's own spine. Phrasing must be
   "do NOT COMMIT shared files on the mission branch (write them on disk uncommitted for your feedback
   step; return lessons-delta.json for the Admiral to apply)". Grounding: cmdr-C feedback names the exact
   contradiction; all 3 commanders wrote AGENT_FEEDBACK on disk (correct); cmdr-R additionally RAN
   apply_lessons_delta (over-reach — only the Admiral applies centrally). Relates to existing
   lesson:shared-files-not-on-mission-branch (possible confirm/extend).

## Confirmations the Admiral observed (verify + count)
- **idle-artifact-completeness-distinguisher** — used 3× (cmdr-R/cmdr-V/cmdr-C all idled without a verdict
  message but were artifact-complete; gated done-vs-stalled on commit+PR, accepted via clean-room review).
- **disjoint-physics-channel-fencing** — Wave-1 fences (calibration/session_fit vs layer2) held with ZERO
  collisions; merge order irrelevant (merged #547 then #548 with no conflict).
- **verify-claimed-side-effects** — every commander's PR/issue/branch claims artifact-verified before merge;
  caught the empty #548 body, the cmdr-C local-baseline CI failure, the v-source confound.
- **diagnose-first-decide-fix** — both send-backs (cmdr-V parity, cmdr-C CI-portability) were evidence-first
  before accepting/merging.
- **py-launcher** — py throughout.

## Other signals (cmdr feedback) — route as template deltas or drop
- IMPLEMENTER_HANDOFF: calibration-test inputs need `_select_slice` contract note (non-empty tp; only tc
  empty to trigger len(tcs)<1). REVIEWER_HANDOFF: artifact type is `review-result` not `reviewer-result`.
- cmdr-V: add "v-source" as a named map/handoff anchor type.
- cmdr-C engine quirks (mostly known/recurring): attest-vs-advance error msg could suggest "advance";
  py-launcher hardcoded in spine command checks; precondition-attest-before-start. (Likely confirm existing
  lessons engine-artifact-attest / py-launcher rather than new.)

## Your task
Return each candidate with a routed disposition: **template delta** (which template/field), **playbook delta**
(add/confirm/retire op for apply_lessons_delta.py — include scope, task_class, statement, grounding citation),
**Charter nomination**, **constellation export**, or **drop-with-reason**. Respect the cap-20 (retire before
add). Be terse. The Admiral applies playbook deltas centrally via apply_lessons_delta.py.
