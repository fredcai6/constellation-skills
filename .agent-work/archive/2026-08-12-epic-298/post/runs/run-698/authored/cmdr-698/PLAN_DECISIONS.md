# cmdr-698 — Plan decisions, alternatives, and critic

Companion to `execute.json`. Records the two principal-governed rigor mechanisms the `plan` step
owes (plan-alternatives c4, cold plan critic c5), the untaken roads, and the residual risks a
returning human should see before approving.

---

## Session constraint that shapes both mechanisms

This session carries an explicit standing instruction: **do not call the Agent tool unless the user
requested it**, and the user did not. Both rigor mechanisms are normally *parallel subagent* work.
I therefore ran both **in-context**, and I am labelling exactly what that does and does not buy
rather than claiming a pass I did not earn. Doctrine's escape here is bias-to-yes with any skip
**surfaced as a named untaken road** — that is what this file is.

---

## Plan-alternatives (c4) — RUN, in-context, single author

Three gate-plan candidates generated under **distinct named constraints**, then compared and
converged to one recommendation (not a menu).

### Candidate A — constraint: *fewest gates, cheapest run*
One gate: H1 + H2 + H3 in a single implement/review/integrate cycle.

- **Depth:** poor. One reviewer holds a keystone-store signature change, an import-path fix and a
  gitignore line in one head; the store change is the only risky part and it gets diluted.
- **Locality:** poor. A BLOCK on the trivial gitignore line reopens the store work.
- **Testability:** poor. One verdict over three unrelated evidence shapes (a scoped pytest, a bare
  direct-file import proof, and `git check-ignore` exit codes).
- **Verdict:** rejected. Cheapness is not the binding constraint on a 3-item hardening issue.

### Candidate B — constraint: *green at every gate boundary, smallest reasonable bite*
g1 additive value object → g2 atomic re-type + all callers → g3 hygiene.

- **Depth:** good. g1 isolates the subtle semantics (parity validation, the dormant reserved-measure
  slot) with **zero** callers at risk, so if that reasoning is wrong it is caught while the tree is
  still green. g2 is then a mechanical signature move over an already-proven object.
- **Locality:** good. Each gate's BLOCK surface is disjoint.
- **Seam placement:** g1 places the seam in `address.py` beside `CellAddress`, one file owning the
  whole identity space; g2 merely consumes it.
- **Testability:** good. Three distinct, honest evidence shapes, one per gate.
- **Why g2 must stay atomic:** a signature change with its callers split across gates leaves a
  known-red window bridged by waivers — the doctrine calls that a plan smell, and it would cost a
  human waiver per gate plus a "prove the red is benign" detour in every review.
- **Verdict:** **recommended.**

### Candidate C — constraint: *diagnose before fixing; prove no numbers moved*
g0 evidence-only harness that snapshots written rows before the change, then g1/g2/g3 as in B, with
g2 closing on a before/after row-equality assertion.

- **Depth:** highest confidence on the "no behavior change" claim, which is the issue's own stated
  boundary and the thing a green suite does **not** actually prove.
- **Cost:** a whole extra crew gate for a refactor where every value is carried through untouched by
  construction (the slot only renames how the write target is addressed).
- **Verdict:** rejected as a standalone gate, **but its central idea is grafted into B** — g2's
  evidence anchors now require a same-inputs before/after row-equality check
  (`cell_key`/`mean`/`sigma`/`support_n`/`status`), and `g2-review` item (c) explicitly forbids the
  reviewer from accepting "the suite is green" as proof of numeric identity.

**Converged recommendation: Candidate B with C's row-equality evidence grafted in.** That is what
`execute.json` encodes.

### Untaken road (named)
The **parallel multi-agent** form of design-it-twice — independent authors under separate
constraints with no sight of each other. Not run: agent dispatch is barred this session. What that
costs is real and worth stating: candidates written by one author share that author's blind spots,
so the comparison above is a genuine structured comparison but **not** an independence check.

---

## Cold plan critic (c5) — RUN in-context, and explicitly NOT COLD

A cold critic reads the plan and frame *only*, with no authoring context. I authored both, so this
is an adversarial self-read and I am not going to dress it up as more. Findings I could not dismiss:

1. **A check that could not fail (FIXED).** `g2-integrate.c2` was originally a negative `grep` over
   the store's signature block. That formulation passes **vacuously** when the methods are absent or
   renamed — precisely the failure it exists to catch. Rewritten as an AST parse that raises on a
   missing class or method, and then **dry-run against the unmodified tree, where it exited 1 and
   named all three methods**. A check nobody has watched fail is not evidence.
2. **The interpreter trap (RECORDED as a residual risk).** The first draft of that check imported
   `DriverFingerprintStore`; `src/physics/__init__.py:52` pulls `scipy`, which is missing from some
   agent shells. It failed on the spot when dry-run. The rewritten check is import-free, but
   `g1/g2-integrate`'s pytest and `simplification_limits` commands **do** need the full interpreter —
   see residual risks below.
3. **The `claim:pilot-runs-end-to-end-3-circuits` proxy.** g2 changes both pilot read sites but does
   not re-run the real 3-circuit pilot (it needs real telemetry). The plan says so out loud in g2's
   evidence anchors rather than letting a green unit suite imply the real pathway was exercised.
4. **g3 bundles two unrelated fixes.** Defensible — both are single-file, zero-risk, and one crew
   pass covers them — but each keeps its **own** close criterion, so a failure is attributable.
5. **Residual, accepted:** `pyright` is not a gate here. The repo has a baseline-diff CI gate (#545)
   and a signature change can move that baseline. It is not in `ORCHESTRATOR_CONTEXT`'s evidence
   table and its checks are non-required, so it stays a named risk rather than a fourth gate.

### Untaken road (named)
A **genuine cold critic** — an agent handed only `execute.json` + `MISSION_FRAME.md` with no
authoring context, and for a plan touching a keystone store arguably a 3-lens panel
(intent-fit / testability / simplicity). Not run: agent dispatch is barred this session. This is the
**larger** of the two gaps, because self-critique cannot find the assumptions I do not know I made.
**Recommendation to the returning human: run this before execute begins.** It is cheap relative to
the store's blast radius.

---

## Residual risks a human should see before approving

- **Interpreter environment.** The `execute` engagement must drive the engine from a shell whose
  `py` resolves to the full `pythoncore-3.14-64` install. The Bash-tool `py` lacks `scipy`
  (confirmed live this run), and `g1/g2-integrate`'s pytest postconditions import `src.physics`.
  A wrong shell makes every physics gate fail for a reason that has nothing to do with the change.
- **`git check-ignore` availability.** `g3-integrate.c2` shells out to git; it was not dry-run here
  because the permission layer declined those invocations during planning. The command is standard
  and the control-path arm makes it non-vacuous, but it is the one check in this plan that has
  **not** been observed running.
- **Two of the three ratifying decisions are mine, not a human's** (slot shape, tightening scope).
  Both are graded `settled/inherited` because they follow from #666 Protected Intent rather than my
  preference, and both are recorded verbatim as the question I would have asked — so either can be
  overturned without re-deriving the analysis. The **name** `FingerprintSlot` is graded `guess` and
  is the cheapest thing to change.

---

## Panel-vs-single choice (surfaced, per doctrine)

Weight assessment: this plan touches a keystone state store with a closed, small blast radius and
no new external interface. That sits at the boundary — **single** critic is defensible on blast
radius, **panel** is indicated because it is a keystone store. Doctrine says *when in doubt, panel*.
I could run neither. The choice is therefore surfaced unresolved, with the recommendation above.
