# Cold plan critic — issue-716

**Independence caveat, stated up front.** A cold critic is supposed to read the plan and the frame
with no authoring context. No subagent could be dispatched this engagement, so this pass was run in
the authoring context against the frame, the converged plan, and the source. Treat its clean bill on
"is the shape right" as weak evidence; its concrete findings below are grounded in source reads and
stand on their own. **Named as an untaken road at plan approval.**

Findings are triaged inline. Normally the human disposes every one; under this engagement's standing
delegation the commander disposes and records the ruling so it can be overturned cheaply.

---

**F1 — the strict session-name grammar changes a refusal, not just a success.**
Today a name with too few segments (`constellation/issue-420/g2/reviewer`) resolves a registry and
then fails at `find_entry` with "no crew recorded with session name". Under an exact inverse it fails
earlier, with "unrecognized session name". That is a *better* message but a *different* one.
→ **Disposition: accept the change, pin it with a test.** Ruling: validate
`parts[0] == "constellation"`, `len(parts) >= 5`, and no empty segment — but do **not** hard-require
the literal `attempt-` prefix, so a future attempt-naming change cannot brick recovery. Both refusal
paths keep raising `CrewLaunchError` (no new exception type).

**F2 — the archive matcher inherits a leaf-collision looseness, and one consumer is credulous.**
`endswith("-" + work_id)` against a relative path means work_id `659/665` matches an archive package
of `epic-659/665`. The leak scan over all matches only gets *stricter* from a false positive, but the
positive existence check (`no archived run package found`) could be satisfied by the **wrong**
package.
→ **Disposition: constrain, don't redesign.** Ruling: a candidate must match at exactly the work_id's
own segment depth, the suffix boundary must be `-`, and the matcher returns **all** matches (never
"the first"). The residual collision is pinned by a test that documents the behavior rather than
silently improving it — narrowing the match rule further is a separate change with its own blast
radius. Recorded as a triage candidate.

**F3 — a green suite is not a working install; the gap must not straddle a gate boundary.**
Adding the import in one gate and the installer companion declaration in the next leaves a commit
where `tests/` is green and the `explorer` skill install ships a `run_crew.py` that raises on import.
→ **Disposition: accepted into the sequencing.** The import and its companion declaration ship in the
**same** gate; the helper module lands first with nothing importing it.

**F4 — the widened companion-closure guard may light up bundles this issue never touched.**
Generalizing the closure test from `checklist_engine.py` to every script in `SKILL_SCRIPT_BUNDLES`
could surface pre-existing undeclared siblings, which would strand this fix behind unrelated repairs.
→ **Disposition: run it as a probe, with a written fallback.** The gate imperative instructs: run the
widened guard first; if it fails only for scripts unrelated to this issue, narrow the guard to the
two consumer scripts, keep the fix moving, and file the residue as a triage candidate. This is why
`decision:widen-the-companion-closure-guard` is graded **guess** with that exact settle experiment.

**F5 — cross-repo footgun: the commander is hosted in f1Brainz, the edits belong to another repo.**
An implementer crew reading "the repo" ambiguously could edit `~/.claude/skills` (build output) or
f1Brainz itself.
→ **Disposition: made structural.** Every gate names absolute `C:/Programs/constellation-skills/...`
paths; the context gate asserts the toplevel of that repo and that f1Brainz's tree is untouched;
"f1Brainz source/tests/docs" and "the installed `~/.claude/skills` tree" are explicit exclusions in
every handoff.

**F6 — repo-local test conventions the plan had not yet absorbed.**
CI runs `python -m pytest tests/ -q` over the whole suite plus `scripts/verify_skip_guard.py`, which
**fails the build on any undocumented pytest skip**. Tests in this repo are `unittest.TestCase`
classes collected by pytest.
→ **Disposition: written into gate constraints.** New tests are `unittest.TestCase`, no skips
(a platform-conditional skip would need documenting), and the full-suite command is the closing gate's
own postcondition, not just the touched files.

**F7 — "no behavior change for single-segment work ids" is a claim, not an assumption.**
→ **Disposition: proven, not asserted.** Existing `test_crew_launcher.py` /
`test_verify_agent_feedback.py` cases must pass **unmodified** (any edit to an existing assertion is a
review-blocking signal), and the new suite carries an explicit single-segment round-trip.

**F8 — the fix silently widens beyond the issue's headline.**
`load_registry_for_resume` also serves `--resume` and bare `--abandon`; both are repaired by the same
line. Unstated, a reviewer reads it as scope creep.
→ **Disposition: state it in the plan and the handoff.** It is one call site; excluding the other two
callers is impossible without *adding* code.

**Not a finding, recorded so it isn't rediscovered:** the launch path (`--work-id`) was already
slash-safe, `recover_crews.py` takes the work_id as an argument, and no third script shares the
assumption. The blast radius really is two functions.
