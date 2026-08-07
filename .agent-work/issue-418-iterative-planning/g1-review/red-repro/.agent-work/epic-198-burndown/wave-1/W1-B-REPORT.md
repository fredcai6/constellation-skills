# W1-B REPORT — install-path-invariant corpus_id (#153)

**Commander:** commander-corpus (delegated) · **Tier:** opus · **Date:** 2026-07-19
**PR:** https://github.com/fredcai6/constellation-skills/pull/197 (open — Admiral merges)
**Branch:** `fix/corpus-id-153` @ `1365ee4`, base `main` (`467a6b0`) · **Worktree:** `C:/Programs/cs-wt-corpus`

## Verdict: DELIVERED — one green, reviewed PR. Bug confirmed real and fixed.

The #153 pollution is real and present (not already fixed, not narrower than described). Root cause
confirmed against the code: `install_constellation.rewrite_installed_skill_paths` bakes the absolute
install path (`target.as_posix()`) into every installed skill file; `compute_corpus_id` hashes those
bytes; the harness installs into a fresh `tempfile.mkdtemp` per invocation, so byte-identical corpora
hash to a different id every run. Fixed inside the eval harness only.

## Worktree isolation (required)
```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-corpus
worktree OK: in C:/Programs/cs-wt-corpus
EXIT=0
```

## Chosen approach + why
**Path-normalization at hash time** (the pre-ruling's default), NOT a pre-rewrite/source-tree hash.
Justification grounded in the code: the installed corpus includes bundled `scripts/`+`references/`
copied from the **invoking checkout's `REPO_ROOT/scripts`** that are absent from `<worktree>/skills`;
hashing the source tree would fingerprint a different fileset (omitting the bundled engine that is part
of the corpus's runtime behavior). Normalizing the installed tree hashes exactly what was installed,
minus the volatile absolute path.

Implementation (`scripts/run_skill_eval.py` only; `install_constellation.py` untouched):
- `stable_corpus_id(skills_dir, install_root, names=None)` mirrors `compute_corpus_id`'s file selection
  and `"sha256:"+sha256` digest shape exactly, replacing `install_root.as_posix()` with a fixed sentinel
  in each file's text before hashing.
- **Explicit install-root anchor** (the load-bearing subtlety a cold plan critic caught before
  implementation): the baked pollution is always the *original* install root string and survives verbatim
  when the tree is copied. The per-run assert site hashes the COPY `run_skills` but anchors on the
  ORIGINAL `skills_dir`. A naive "strip the dir I'm hashing" would no-op on the copy and false-fence
  **every** run as `corpus_mismatch`. All three id sites (marker write, per-run assert, resume fallback)
  pass the anchor; `workspace_unchanged` fingerprints stay raw (same-path compare).
- Needle built from `.as_posix()` (not `str()`), so Windows normalization is not a silent no-op.

## Evidence — regression test proves two install-paths → one corpus_id
Test: `tests/test_run_skill_eval.py::test_corpus_id_install_path_invariant`. Drives the **real copy
path** (two `run_scenario` invocations at two different temp roots), asserts `v1.corpus_id ==
v2.corpus_id` with both `fenced_count == 0`, AND asserts the **raw** `compute_corpus_id` of the two
installed trees **differs** (canary). It installs a corpus whose `SKILL.md` carries a `<skill-dir>`
token so the installer actually bakes an absolute path — without it the canary would be meaningless.

Re-run in the Commander's own hands (all green):
```
$ python -m pytest tests/test_run_skill_eval.py -k corpus_id_install_path_invariant -q
1 passed, 87 deselected in 1.30s
$ python -m pytest tests/test_run_skill_eval.py -q
88 passed in 19.17s
$ git diff HEAD --exit-code -- scripts/install_constellation.py
UNCHANGED exit=0
$ grep -q 'invoking checkout' scripts/run_skill_eval.py && grep -q 'REPO_ROOT/scripts' scripts/run_skill_eval.py && echo DOC_OK
DOC_OK
```
Independent reviewer (opus): **APPROVE**, all 7 close criteria reproduced at source, Fowler-clean, no blockers.

## Doc graduation (required)
The arm-construction fact is documented in the `run_skill_eval.py` module docstring: the bundled engine
comes from the **invoking checkout's `REPO_ROOT/scripts`**, not from `--worktree` (which only selects the
skill source tree). No separate eval doc exists and `README.md` is out of this wave's ownership, so the
harness docstring is the home (pointer noted here per the launch order).

## Map impact
Skill-source repo, no `docs/architecture` packet map. Structural record for the harness IS the module
docstring (folded — arm-construction fact added). Design docs (`CONSTELLATION_OVERVIEW.md`, `ROADMAP.md`)
mention the harness only at high level, not the hashing mechanism — reasoned no-op, no update needed.

## Triage candidates (recommend-and-defer — filing is the Admiral's call)
- **tc1 (low, cleanup):** three `_run_once` fixtures hand-seed the corpus id rather than routing through
  `run_scenario`, so a future id-shape change touches them by hand. Consider a shared seed helper.
- **tc2 (medium, doc/design-drift):** `install_constellation.py:430-431` still states "an eval run and a
  real install fingerprint a corpus identically." This fix intentionally makes the EVAL id
  install-path-invariant while real-install hashing is unchanged, so that comment is now stale. Follow-up:
  normalize real-install hashing too, or update the comment. **Touches the fenced `install_constellation.py`
  — a separate authorized issue.**
Full recommendations: `.agent-work/archive/2026-07-19-corpus-id-153/triage-candidates/recommendations.md`.

## Workflow feedback (for Admiral harvest)
Staged trio at `C:/Programs/cs-wt-corpus/.agent-work/staged-feedback/corpus-id-153/`
(AGENT_FEEDBACK.md, lessons-delta.json, CONSTELLATION_FEEDBACK.md, FENCE.md) — staged rather than written
to the shared main-checkout durable log because a concurrent wave-1 commander (commander-cg) makes a
direct append clobber-prone; per `constellation-commander-delegated` "stage, do not waive". Highlights:
- The **cold plan critic earned its keep**: it caught the anchor-rule BLOCKER before implementation. Left
  unspotted it would have shipped a fix that silently false-fenced every eval run.
- **Handoff gap (mine):** both crews flagged that "full suite green" didn't warn that three existing
  fixtures hand-seed the raw id and had to be migrated — exactly what `IMPLEMENTER_HANDOFF.template.md:27`
  tells the Commander to pre-empt. Lesson applied-in-reflection: when a change alters a value tests SEED
  (not just assert), enumerate every seeder before freezing the handoff.
- Minor engine friction: null-check preconditions must be attested BEFORE `start` (postconditions after);
  the asymmetry cost one round-trip per step.

## Run shape
Spine driven init→archive through the engine; 1 crew gate (g1: implement+review+integrate), 0 reopens,
0 blockers, reviewer APPROVE first pass. Subagents: sonnet (cold plan critic), opus (implementer),
opus (reviewer). Lease claimed at init, released as the final journaled action.
