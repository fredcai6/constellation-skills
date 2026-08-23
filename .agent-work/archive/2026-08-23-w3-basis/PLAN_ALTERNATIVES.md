# Design-it-twice Brief: blob-OID pin + fail-on-drift mechanism for `CommanderSpineBasisFields`

## The one thing being designed twice

Where the blob-OID pin/drift-check/re-verify mechanism lives, and how the re-verify path is
shaped, for `CommanderSpineBasisFields` in `tests/test_checklist_engine.py`.

## Count and panel — a surfaced choice

**2 candidates**, single pass (no 3-lens panel). This is a fairly-easy call scoped to one class in
one file, not a load-bearing interface or an architecture-touching plan — the decision space is
"inline in the class" vs. "extracted module-level helper," which two candidates fully spans.

## The constraints (one per agent, each distinct and named)

- **smallest-diff** — `.agent-work/w3-basis/plan-candidate-smallest-diff.md`. Minimize diff and
  new surface; everything inline in the existing `_skip_if_head_moved`-shaped method; re-verify
  path is the bare `git rev-parse HEAD:<path>` command printed in the failure message.
- **best-seam-placement** — `.agent-work/w3-basis/plan-candidate-best-seam-placement.md`. Extract
  `blob_oid`/`reverify_pin`/`assert_blob_pin_current` as module-level helpers reusable by any
  future content-pinned test; re-verify path is an importable `reverify_pin()` function.

## Compared on

- **Depth** — both fix the actual defect (granularity + fail-not-skip) equally; best-seam adds
  durability for hypothetical future callers, smallest-diff adds nothing beyond the fix itself.
- **Locality** — smallest-diff: one class, ~15 lines, zero new names outside it. best-seam: one
  file still (respects the `tests/test_checklist_engine.py`-only ownership boundary), but ~35
  lines of new module-level surface (`blob_oid`, `reverify_pin`, `assert_blob_pin_current`).
- **Seam placement** — smallest-diff reuses the file's existing `subprocess`+`git` idiom in place.
  best-seam places helpers beside the file's existing shared-helpers block (real precedent, not
  invented), but its re-verify entry point had to dodge a mid-file `if __name__ == "__main__":`
  landmine (line 1581) by using `sys.path.insert` + `importlib`-style module import rather than a
  CLI — a workaround, not a clean fit.
- **Testability** — comparable. Both support the identical two-direction mutation battery
  (template-edit → RED, unrelated commit → GREEN) with FAIL-message substring assertions, not bare
  exit codes. best-seam adds one extra directly-testable unit (`reverify_pin` callable standalone).

## Framing block (presented ahead of convergence)

- **Constraints in play**: smallest-diff (minimize footprint) vs. best-seam-placement (durable,
  discoverable, reusable seam) — chosen because the decision pressure named at `plan` was exactly
  "where does the mechanism live," and these are the two poles of that axis.
- **Dependencies held fixed for both**: `PINNED_HEAD`/`_skip_if_head_moved` are deleted; the
  comparison is `git rev-parse HEAD:<path>` against a stored pin; the fail message must name
  "stale," both OIDs, and a copy-paste re-run command; file ownership stays
  `tests/test_checklist_engine.py`-only; a two-direction mutation battery is required either way.
- **Illustrative sketch (not a proposal)**: a `_fail_if_template_drifted` method that shells out to
  `git rev-parse HEAD:<path>` and calls `self.fail(...)` on mismatch — offered only to prime
  thinking before either candidate landed, carries zero weight at convergence.

## Output — recommendation

**smallest-diff**, not a hybrid. Reasons, in order of weight:

1. **One caller, one adapter.** This repo's own doctrine (`global-everyone.md`, "Deep-module
   vocabulary"): "one adapter = a hypothetical seam; two = a real one." `CommanderSpineBasisFields`
   is the only class that needs this mechanism today. Extracting a shared module-level helper for
   a population of one is exactly the premature abstraction that doctrine warns against — if and
   when a second class needs a content-pinned proof, that is the moment to extract, with two real
   call sites to design the seam from instead of one imagined future one.
2. **The "cheap" re-verify path is actually cheaper under smallest-diff.** best-seam's re-verify
   command is `python3 -c "import sys; sys.path.insert(0, 'tests'); import test_checklist_engine
   as t; t.reverify_pin(...)"` — importing a test module as a library via a manual `sys.path`
   insert, a workaround for the file's own pre-existing mid-file `__main__` landmine. smallest-diff's
   re-verify command is a bare `git rev-parse HEAD:<path>`, already a standard idiom, requiring no
   knowledge of the test file's internals. `decision:ship-the-re-verify-path` asks for *cheap*; the
   simpler invocation wins that axis outright.
3. **Matches the launch order's own framing.** The mission is "surgical text edit" scale (per the
   class's own docstring precedent from wave 2's `basis`-field edit) — a single bounded issue, not
   the start of a reusable-pin-checking library.

The mutation battery from smallest-diff's candidate (2 entries: template-edit → RED with
`"proof is stale"` + the exact `git rev-parse HEAD:<path>` substring; unrelated commit → GREEN) is
adopted as-is for `execute.json`.

## Untaken-road record

- **best-seam-placement's module-level extraction** — not taken. Named and scored above; deferred
  until a second content-pinned test class exists to design the real seam from (per "one adapter =
  hypothetical, two = real"). Not lost: this candidate file stays on disk as the reference design
  for whoever adds the second caller.
- **3-lens critic panel** — not run; single critic used instead (see `PLAN_CRITIC.md`). This is a
  fairly-easy, single-file, single-class decision, not architecture-touching.

## Panel-vs-single record

Single critic (not a 3-lens panel), because the artifact under critique is a converged gate plan
for a bounded, single-file, single-class mechanical fix — not a spec that spawns epics or touches
architecture. Two candidates (not a 3+ panel) for the same reason at the plan-alternatives step.
