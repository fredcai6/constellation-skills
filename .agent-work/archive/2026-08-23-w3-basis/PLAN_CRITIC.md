# Plan Critic — smallest-diff candidate for `CommanderSpineBasisFields` blob-OID pin

Reviewed: `.agent-work/w3-basis/plan-candidate-smallest-diff.md` (the converged
recommendation per `PLAN_ALTERNATIVES.md`'s "Output — recommendation"),
against `MISSION_FRAME.md` and the live class at
`tests/test_checklist_engine.py:8543-8650` (`CommanderSpineBasisFields`).

## Findings

1. **Concurrent-lane race on the exact file being pinned — likely to self-red
   on merge.**
   `MISSION_FRAME.md`'s Structural Anchors flags
   `skills/commander/templates/COMMANDER_SPINE.template.json` as "read-mostly
   this wave — `w3-promote` owns edits" — i.e. a sibling lane in the *same*
   epic wave is actively editing the exact file this pin keys off, this wave.
   The plan computes `PINNED_BLOB` "at implementation time" (dispatch) and
   has no re-pin-immediately-before-merge step and no stated ordering
   dependency against `w3-promote`. If `w3-promote`'s edit lands (merges to
   the shared branch) between this lane's dispatch and its own
   `g1-integrate`, the freshly-captured `PINNED_BLOB` is already stale before
   this lane ships — the new fail-on-drift mechanism will RED immediately on
   integration, not because of a genuine future drift but because of this
   lane's own sequencing. That is exactly the failure mode
   `constraint:no-skip-on-drift` intends to reserve for real future edits,
   not a self-inflicted one at merge time.
   Why it matters: without a fix, the first thing this gate does after
   shipping is likely fail — undermining trust in the mechanism on day one
   and forcing an emergency re-pin.
   Disposition: **fix-in-plan** — add either an explicit ordering constraint
   (this lane's `PINNED_BLOB` capture, and its merge, happen only after
   `w3-promote` lands) or a "recompute `PINNED_BLOB` as the last step before
   `g1-integrate`, immediately before merge" instruction to the Gate
   structure section.

2. **Mutation battery doesn't specify an isolated execution target, and this
   is a shared, actively-contended worktree.**
   The battery says "checkout a scratch copy, mutate one byte of
   `COMMANDER_SPINE.template.json` ... and commit it" and "on the same
   scratch copy, commit an unrelated change." It never specifies *how* the
   scratch copy is made (e.g. `git worktree add` / `git clone --local` into
   `/tmp`) as distinct from the live shared worktree at
   `/home/tommy/projects/569-w3-basis` on branch `epic-569/w3-basis`. Read
   literally, an implementer could run these mutating commits directly in
   the live worktree, which — combined with finding 1 — means a real risk of
   colliding with `w3-promote`'s concurrent, genuine edits to the very same
   file, or needing a destructive `reset --hard` / branch cleanup in a
   worktree other lanes may be using concurrently.
   Why it matters: this is a correctness-of-test-battery and safety issue,
   not a style nit — a mutation test that runs in-place in a shared worktree
   can corrupt another lane's uncommitted or in-flight work.
   Disposition: **fix-in-plan** — specify the mutation battery runs against
   an isolated clone (e.g. `git clone --local . /tmp/<scratch>`) that is
   discarded afterward, never against the shared worktree in place.

3. **Class docstring goes stale and now actively contradicts the new
   behavior.**
   The live docstring (`test_checklist_engine.py:8552-8558`) says: "Pinned to
   this gate's shipped git HEAD per
   `ruling-red-proof-pinned-to-shipped-revision` ... If HEAD has moved past
   the pinned commit, **skip** rather than assert against a template shape
   this test was never written against." The plan's Mechanism section says
   explicitly: "keep everything else (the three test methods,
   `EXPECTED_BASIS`, `_load_spine`) untouched" — the docstring isn't named at
   all, and by omission is left in place. After this change ships, the
   class's own docstring will describe exactly the whole-repo-HEAD +
   skip-on-drift semantics that `constraint:blob-oid-granularity` and
   `constraint:no-skip-on-drift` exist to abolish — actively misleading
   whoever next reads the class (including "whoever next legitimately edits
   the template," the plan's own stated audience for the re-verify path).
   Why it matters: a reader trusting the docstring will believe drift is
   silently skipped, not failed, and will not know to look for the re-verify
   command in the (now-different) failure message.
   Disposition: **fix-in-plan** — add an explicit step to the Mechanism
   section (and a check in `g1-review`'s evidence list) to rewrite the
   docstring's second paragraph to describe blob-OID pinning + fail-on-drift,
   not the retired HEAD+skip design.

4. **Stale "g2 dispatch" label contradicts the plan's own single-gate
   structure.**
   The code snippet's comment reads: "Captured via `git rev-parse
   HEAD:<path>` at implementation time (**g2 dispatch**)." But the plan's own
   "Gate structure in execute.json" section defines only `g1-implement` /
   `g1-review` / `g1-integrate` and states explicitly "No `g2` needed — the
   scope doesn't decompose further without padding." The comment is an
   uncorrected leftover (likely copied from `MISSION_FRAME.md`'s
   "blob-oid-of-template-at-**g1**-dispatch" placeholder crossed with an
   earlier draft's numbering, or vice versa — the two documents don't even
   agree with each other: mission frame says g1, this candidate's prose says
   g1 in one place and g2 in the code comment).
   Why it matters: this text ships verbatim into the source file's comment
   per the plan's own snippet — a future reader will see a reference to a
   "g2 dispatch" that never existed in this issue's own gate plan, a small
   but real correctness defect in an artifact meant to be copy-pasted as-is.
   Disposition: **fix-in-plan** — trivial, change the comment to "at
   implementation time (g1 dispatch)" to match the actual gate structure.

5. **Blob-OID-via-`rev-parse` correctness claim checked and confirmed
   sound** (verification, not a defect). `git rev-parse HEAD:<path>` resolves
   a tree entry at a specific commit directly from the object database; it
   does not touch the working tree and applies no clean/smudge filters, so
   it is unaffected by local `core.autocrlf` or checkout-time line-ending
   settings. In this checkout, `core.autocrlf` is in fact unset (verified via
   `git config --get core.autocrlf`), and the repo's `.gitattributes` (`*
   text=auto`) only normalizes line endings once, at commit time, producing
   one canonical stored blob thereafter — so the blob OID this plan pins to
   is deterministic and platform-independent, and genuinely changes only
   when the path's committed bytes change. No rename- or case-sensitivity
   subtlety applies either, since `w3-promote` owns the file read-mostly and
   no rename is in scope. Disposition: **non-issue** — the plan's central
   correctness claim holds; no fix needed.

6. **`git rev-parse` failure vs. genuine drift: correctly distinguished in
   code, but not called out in prose.**
   `_fail_if_template_drifted`'s `self.assertEqual(out.returncode, 0,
   out.stderr)` runs *before* the blob comparison, so a `rev-parse` failure
   (e.g. path not resolvable at HEAD) raises a plain assertion failure
   carrying raw git stderr, distinct from the deliberate "proof is stale"
   message reserved for real drift — this correctly satisfies the concern
   that a git-command failure shouldn't be silently conflated with drift.
   However, the plan's "Drift detection and fail wording" prose section
   never states this distinction is intentional, so `g1-review`'s checklist
   (which enumerates the four required substrings of the *drift* message)
   has no corresponding instruction to verify the *failure* path stays
   separate and doesn't accidentally get merged into the same `self.fail`
   call during implementation.
   Disposition: **non-issue / minor** — behavior is already correct in the
   plan's own snippet; optionally add one line to `g1-review`'s evidence
   list confirming the two paths (`rev-parse` failure vs. blob mismatch)
   remain distinct, but this is not blocking.

## Triage (delegate disposition, no reachable human — LAUNCH_ORDER:Inherited Latitude)

All 6 findings accepted as the critic disposed them; all within inherited latitude ("the
mechanism's shape" is explicitly delegated by the launch order):

1. **Accepted, fix-in-plan.** `execute.json`'s `g1-implement` recomputes `PINNED_BLOB` as its
   last action, immediately before `g1-integrate`, rather than "at dispatch" — closes the
   concurrent-lane race against `w3-promote`'s ownership of the template file.
2. **Accepted, fix-in-plan.** The mutation battery in `execute.json` specifies an isolated
   `git clone --local . /tmp/<scratch>` (or `git worktree add` to a `/tmp` path), never the shared
   worktree, and specifies teardown.
3. **Accepted, fix-in-plan.** `g1-implement` rewrites the class docstring's second paragraph to
   describe blob-OID pinning + fail-on-drift; `g1-review` confirms the old "skip" language is gone.
4. **Accepted, fix-in-plan (trivial).** Comment reads "g1 dispatch," matching the actual gate
   structure.
5. **Accepted, non-issue.** No action; the verification stands as recorded.
6. **Accepted, non-issue/minor, folded in anyway.** `g1-review`'s evidence list gets one line
   confirming the `rev-parse`-failure path and the drift-fail path stay distinct — cheap enough to
   include even though not blocking.
