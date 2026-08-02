# Lessons-Audit Run Brief — 509-w4

**Epic #509, wave 509-w4.** Two follow-ons from 509-w3, parallel disjoint fences, full autonomy.
Run from a dedicated admiral worktree off origin/main (main checkout on user's feat/541).

**Model tiers:** Admiral=Opus; both commanders+crews=Sonnet.

**Outcome:** 2 PRs merged, #546 closed, #549 kept-open (69/71), follow-on #553 filed.
- cmdr-T #546 (PR #552, `c5c28010`): decoupled throttle/coast re-eval → HONEST-NULL both (retune
  sig_a_soft_throttle infra added default-off, braking bit-identical; coast structural). #553 filed.
- cmdr-P #549 (PR #554, `1986d7ba`): pyright 71→2, type-only groups A–I; 2 deferred to cmdr-T fence.

## Artifacts
- ADMIRAL_LOG: `C:\Programs\f1Brainz-509w4\.agent-work\509-w4\ADMIRAL_LOG.md`
- Commander feedback (captured): `crew-handoffs/captured-AGENT_FEEDBACK-cmdrT.diff`,
  `crew-handoffs/captured-AGENT_FEEDBACK-cmdrP.diff`, `crew-handoffs/cmdr-P-lessons-delta.json`
- Launch orders: `crew-handoffs/`… actually `launch-orders/cmdr-{T,P}-*.md`
- Playbook: `.agent-work/LESSONS.md` (Active, **cap 20, AT CAP, run-tick 16**)

## Candidates the Admiral spotted (audit + route, add anything you find)

1. **commander-committed-own-work-area-to-mission-branch (NEW incident).** cmdr-P committed its
   entire `.agent-work/549/` work area (spine/crew-handoffs/lessons-delta, 18 files) to the mission
   branch; Admiral captured + stripped it (`git rm -rf`) pre-merge so only the 12 src files landed.
   (It correctly kept the SHARED files LESSONS/AGENT_FEEDBACK/CONSTELLATION off-branch.) Grounding:
   ADMIRAL_LOG MERGE #554 entry. **Cap is at 20 → prefer AMEND of `shared-files-not-on-mission-branch`**
   (extend its statement to also cover the commander's own `.agent-work/<id>` work area) over a new slot.
2. **diff-against-merge-base-not-main (cmdr-P).** The #545 pyright gate diffs the PR against the CURRENT
   origin/main; when main advances mid-run, that can mis-handle errors. cmdr-P suggests diffing against
   the merge-base. This is a real refinement to the gate cmdr-C built. Route: a **follow-on issue** to
   improve the gate (and/or a ci-tooling note). Decide which.
3. **cast-not-float-for-pandas-scalar (cmdr-P).** `cast(float, x)` is the correct itertuples-Scalar
   narrowing (float() is rejected by pyright's ConvertibleToFloat). Project-specific tip → template delta
   or drop.
4. **clamp-all-sample-distortion (cmdr-T).** `np.minimum/np.maximum` raw-ceiling clamps distort ALL
   samples below the ceiling, not just boundary ones (caused misleading 2.4–4.5σ CdA shifts). →
   IMPLEMENTER_HANDOFF "Fix candidates" warning.
5. **boundary-lag-magnitude-sanity-check (cmdr-T).** Count recoverable samples BEFORE implementing a
   boundary-lag fix (here <1% of loss was boundary lag). → handoff sub-step.
6. **scope-exclusion-nonoverlap (cmdr-T).** A handoff listed `decoupled_braking_input.py` in BOTH
   Allowed Scope and Specific Exclusions. → plan-time check / template note.

## Confirms the Admiral observed (verify + count)
- **disjoint-physics-channel-fencing** — w4 fences (decoupled/throttle/coast vs the rest of src) held;
  cmdr-T fence untouched by cmdr-P; merge order irrelevant.
- **verify-claimed-side-effects** — caught the committed work-area; verified braking bit-identical (786
  independent tests); caught cmdr-P's 2-deferred-errors claim.
- **idle-artifact-completeness-distinguisher** — cmdr-T idled with NO verdict message, gated on artifacts
  (commit+PR) = done; cmdr-P returned a full verdict.
- **diagnose-first-decide-fix** — cmdr-T's honest-null was thorough (HP sweep + coast magnitude check).
- **engine-artifact-attest** — cmdr-P's `g-integrate-needs-review-result-artifact` = another recurrence
  (now 9). RECURRENCE-DEBT — flag for upstream, don't just confirm.
- **shared-files-not-on-mission-branch** — confirm (commanders kept SHARED files off-branch) AND amend
  per candidate 1.
- py-launcher, handoff-cite-exact-seam-signature, state-note-before-detach, run-crew-cli-launcher-misfit
  (recurrence) — confirm as grounded.

## Your task
Return each candidate with a routed disposition (playbook add/amend/confirm/retire — note the cap-20;
template delta; constellation export; follow-on-issue; or drop-with-reason), each with a grounding
citation. Prefer AMEND over ADD given the cap. Output one structured list the Admiral applies via
apply_lessons_delta.py. Do NOT edit LESSONS.md or run the apply script yourself.
