# Constellation Feedback — staged for harvest

Staged rather than appended to the durable root. See `FENCE.md` beside this file.
The Admiral harvests this into `.agent-work/CONSTELLATION_FEEDBACK.md`.

---

## 2026-08-07 — issue-440-binding-cwd

**Lesson:** `lesson:falsify-a-check-against-a-decoy-before-trusting-it`
(carried forward on its original id — this is a **recurrence**, not a new finding. Amend the existing
entry rather than minting a slug.)

**Recurrence count: 3.** issue-310 → issue-419-governor-identity → issue-440-binding-cwd.

### What recurred

A purpose-built acceptance **verifier** — `verify_evidence.py`, whose entire job was to guard this
run's central claim — shipped with **8 silent-pass holes**. The worst of them exited **0** on a
treatment arm whose binding pointed at the sandbox main, i.e. **the defect the run existed to fix,
not fixed**. It read the gauge paths and never the `binding_entries` that produced them, so
`path_source == "git_worktree"` — the single most load-bearing fact in the result — was asserted only
for a preflight, never for the live arms.

### Why this recurrence is different from the first two, and why that matters upstream

The first two instances (issue-310, issue-419) were **gate postconditions authored from the spine
template**, which is what the lesson's own bank-reason predicted would discriminate template gap from
author habit: *"If a second commander writes a grep-theatre check from the same template, it is the
template."* That question was already settled at issue-419.

**This one is not from the template at all.** It is a hand-written verifier, produced by a crew whose
handoff stated the hazard **twice** in bold — the positive-control requirement, and *"a test that
cannot fail is worse than no test, and this epic has already filed three issues in that family
(#432, #446, and a finding inside #419's own run)"*. The crew also **wrote its own `--selftest`
harness** with five mutations proving its checks could fail, and still left the central check
unwritten. Its five mutations damaged the *gauge* facts; none damaged the *binding* facts.

So the shape upstream is sharper than "the template invites grep-shaped checks":

> **A decoy suite tests the checks you thought of. It cannot surface the fact you never asserted.**
> Self-falsification proves a check *can* fail; it says nothing about *coverage*. The crew's selftest
> passed 5/5 while the verifier's most important assertion did not exist.

### Concrete upstream shape

Enumerate the claim's load-bearing facts **first, as a list**, then require one check per fact and one
decoy per check. The enumeration is the artifact that would have caught this: the run's own evidence
JSON had `binding_entries` sitting in it, unread by any check. Deriving the decoy set **from the
evidence schema** rather than from the checks already written is what converts a self-falsification
harness from "my checks work" into "my checks are complete".

Corroborating detail: the reviewer's Fowler pass independently flagged **shotgun surgery — the
evidence schema is declared nowhere** — and named it as the mechanism behind five of the eight holes.
That is the same finding arriving from the other direction.

### Verified paid-down in this run (partially)

Closed fix-now at commit `89cc99a`: 46 → 59 checks, 5 → 10 selftest mutations, and the new
`treatment-binds-main` mutation exits non-zero where it exited **0** at `b332287`. The remaining
holes and the undeclared-schema root cause are filed as **#455**.

**This is debt, not trust.** Three recurrences of an unfixed shared-machinery defect. Do not confirm
it a fourth time — fix the upstream shape.
