# Plan alternatives — issue-716 (design-it-twice)

**Untaken road (named, per the bias-to-yes rule).** The contract calls for candidates authored in
*parallel by independent agents* and a *cold* critic with no authoring context. This engagement runs
under a standing instruction not to dispatch subagents, so all three candidates and the critic pass
were authored **in this context**. What is lost is exactly the independence property: a self-critique
cannot be surprised by its own blind spot. Mitigation applied: each candidate was written to its
constraint *first* (before comparing), and the critic pass below attacks the converged plan only,
against the frame and the source — findings are recorded whether or not they were comfortable.

---

## Candidate A — "smallest diff" (constraint: add no new install surface)

Patch each site in place. `load_registry_for_resume` derives `work_id` from `parts[1:-3]`;
`_current_run_archive_dirs` walks to the right depth and matches the archive-relative path. No new
module, no `install_constellation.py` change, no new test file.

- **Depth**: shallow — the same rule is stated twice, in two vocabularies.
- **Locality**: best of the three. Two functions, two test files, zero install risk.
- **Seam**: none created. A third script hitting this next year re-derives the rule a third way.
- **Testability**: fine (both sites already have test homes).
- **Cost it avoids**: the `explorer`-bundle trap entirely — nothing new must travel with anything.
- **Why not**: the issue's own diagnosis is that *two independent ad hoc string-splits* is the
  defect class, not the two bugs. A fix that leaves two ad hoc string-matches (just correct ones)
  fixes the instances and preserves the class.

## Candidate B — "shared contract" (constraint: one written statement of the work_id contract)

New `scripts/work_id_paths.py` exporting `work_id_from_session_name()` and
`archive_dirs_for_work_id()`, imported by both consumers via the established sibling-import idiom,
declared as a runtime companion of both in `install_constellation.py`, with its own test file and a
widened companion-closure guard.

- **Depth**: real — a caller learns two functions and gets the whole "a work_id may be a multi-segment
  path" rule, including the refusal semantics.
- **Locality**: good for future change (one place), worse for this change (four files + tests).
- **Seam**: creates one, and it has two implementers immediately — the "one adapter is a hypothetical
  seam, two is a real one" test passes on day one.
- **Testability**: best — the helper is pure, so the nasty cases (malformed names, leaf collisions,
  Windows separators) are unit-testable without touching a registry or a filesystem archive.
- **Cost**: the install-bundling trap (`explorer` ships `run_crew.py` without `agent_work_root.py`),
  which must be paid down deliberately, not hoped away.

## Candidate C — "delete the inverse" (constraint: remove the need to parse at all)

Stop re-deriving `work_id` from the session name: for recovery, glob `.agent-work/**/crew-runs.json`
and find the registry whose entries contain the session name. For the archive check, resolve the
package by comparing **paths** (the archived work area) rather than matching names.

- **Depth**: highest conceptually — a lookup can never mis-parse.
- **Locality**: poor. A glob across `.agent-work/**` is O(work areas), can match two registries
  (ambiguity where there was none), and turns a pure string operation into filesystem I/O that the
  unit tests must now stage.
- **Seam**: replaces a parsing seam with a search seam that is harder to reason about and easier to
  make silently wrong — directly against the frame's protected intent ("never silently resolve to
  the wrong work area").
- **Testability**: worse; every test needs a filesystem fixture.
- **Salvage**: its *archive-side* insight is right and is grafted below. Matching an archived package
  by **relative path structure** rather than a single `name` string is exactly candidate C's idea,
  scoped to where it costs nothing.

---

## Convergence — B, with C's archive-side graft, and A's constraint honored as a gate

**Recommendation: Candidate B**, because the issue's defect is the *duplicated ad hoc rule*, and B is
the only candidate that retires it. Two amendments taken from the losers:

1. **From C**: the archive matcher compares the **archive-relative path** at the work_id's own segment
   depth (and its flattened form), not a single directory `name`. This is the only correctness change
   that matters at that site; the rest of C is rejected.
2. **From A**: A's real virtue is "no new install surface," and B's real risk is precisely new install
   surface. So B does **not** get to treat the installer edit as an afterthought: the companion
   declaration ships in the **same gate** as the import that needs it, and the closure guard that
   would have caught the omission is widened in that same gate. No gate boundary is ever left in a
   state where the suite is green but an install is broken.

**Sequencing that falls out of that** (each boundary independently green):
`g1` helper module + its own tests (nothing imports it yet, so no install can break)
→ `g2` `run_crew.py` consumer + companion declaration + widened closure guard
→ `g3` `verify_agent_feedback.py` consumer + companion declaration + archive-gate tests
→ `g4` reasoning gate: reproduce the two original field failures end-to-end and write the handover.

**Panel-vs-single**: single-pass, three candidates, no separate judge panel. Rationale surfaced
rather than chosen silently — this is a ~200-line bug fix in a repo with an existing test harness and
an already-ruled shape; a judge panel would be ceremony. If the owner disagrees, the cheapest re-run
is the critic pass, not the candidates.
