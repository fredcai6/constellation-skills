# Plan rigor: convergence record

Both mechanisms were run (bias-to-yes, neither skipped, so there is no untaken road to declare).
Panel-vs-single: **single critic, two design candidates.** Rationale surfaced rather than chosen
silently — the gate plan's shape was largely frozen by the launch order (three named parts), so the
only genuinely open design was the guard's mechanism, and that is where the two candidates went.
All three helpers were **cold, fresh `claude -p` processes** with `SPINE_FILE`/`SPINE_SESSION`/
`SPINE_PARENT` stripped from the environment, per `decision:no-fork-for-design`. Stripping was not
ceremony: an earlier headless probe in this worktree inherited the session's Stop hook and began
trying to drive *this* spine before permissions stopped it.

## Design-it-twice — converged to a named hybrid, not a menu

**Candidate A** (constraint: pure corpus-absence, add no new concept) and **Candidate B**
(constraint: make regrowth structurally impossible, attack the mandating test).

**Taken from A** — its shape: reuse the existing `INSTRUCTION_FILES` walk, assert absence, add no
new concept. Exception list length zero.

**Taken from B** — two things A did not have:
1. The **blast radius**. A assumed one mandating test. B named several. I verified: it is **nine**
   assertions across `test_mcp_adoption.py`, not one. A sweep that inverted only the test I first
   found would have left eight others red.
2. The **third pattern**, `checklist_engine.py` as a literal invocation — which is what A's own
   self-attack #2 (displacement: reword to "run the engine script directly" and the guard stays
   green) requires to close.

**Rejected from B** — its consolidation move (fold the 3 door-refused sites into one authority
file). B's own self-attacks #1 and #3 are fatal and I agree with them: it breaks the 3 real cases
by replacing a command with a pointer, and "exactly one authority file" is an exception list of
length 1 that restarts the 11-entry decay under a nicer name. Also rejected: B's meta-test over
test source, out-writable by its own admission and unowned maintenance surface.

**Taken from A's self-attack #1** — "it measures spelling." My own census confirmed it concretely:
the clause has **three** surface forms in this tree (`CLI fallback:` ×10, `CLI fallback,` ×4,
`CLI fallback ` ×1). A colon-only pattern misses a third of them. Candidate A, followed literally,
would have shipped a guard blind to 5 of the 15 occurrences.

**Also found, and it reframes the deliverable**: the ruling this guard enforces is **already pinned
in-tree** at `tests/test_mcp_adoption.py:838` (`TestTier2SpineAlreadyBoundForDispatchedCrews`),
which asserts absence for 2 files and quotes the human verbatim: *"the agents should not know about
the CLI. period."* The guard is a **generalization of an existing precedent from 2 files to the
whole corpus**, not a new invention. That is a materially stronger thing to land.

## Cold plan critic — every finding triaged

The critic read only the frame, `execute.json` and the common brief. Its headline: *"a plan whose
subject is 'a check that cannot fail' closes on four of them."* It was right.

| # | Finding | Disposition |
|---|---|---|
| F1 | Specificity proof vacuous: guard walks `skills/`, so proving it ignores `docs/superpowers/` proves only that an rglob is an rglob | **ACCEPTED.** Replaced with the proof that discriminates: reintroduce a fallback clause at one of the 3 **reworded** sites → RED; the reworded text itself → GREEN |
| F2 | `g2-integrate` `\| tail -5` swallows the exit code; gate closes green when the guard does not exist | **ACCEPTED.** All pipes removed or `set -o pipefail`; checks now read exit codes |
| F3 | `g4-integrate` `test -d .agent-work/567-d1` passed before the run began | **ACCEPTED.** Now asserts non-empty per-issue disposition files |
| F4 | Guard pattern unspecified exactly where discrimination is hardest | **ACCEPTED.** Three patterns pinned in the gate, with the measured three-surface-form census |
| F5 | `g1-integrate` grepped all of `skills/` incl. workbench, passable only by violating the fence | **ACCEPTED.** `--exclude-dir=workbench`; the whole-corpus assertion moves to g5 after the rebase |
| F6 | Full suite, guard count, and post-rebase re-run had no postcondition | **ACCEPTED.** New `g5-final` reasoning gate carries all three |
| F7 | Reorder: author the guard first, against the dirty tree | **ACCEPTED — the best finding.** The red-proof is now produced by the real corpus (13 clause + 9 token sites), not by a scratch string the guard's own author chose to match |
| F8 | `g3` creates door doctrine in `specs/`, outside the guard's walk | **ACCEPTED.** Guard's walk extended to `specs/**/*.toml` in g1 |
| F9 | `grep -i door specs/` near-vacuous | **ACCEPTED.** Both files asserted independently, and both halves of the claim |
| F10 | Where does the ruling live? The lane may not write `docs/agents/*` and files no issue, so a pointer dangles | **ACCEPTED (option b).** The guard's failure message quotes the ruling verbatim, so it is self-contained and deleting the guard destroys the reason too. The durable-home question is floated to the Admiral |
| F11 | `g4` (#596/#526) is a different issue, 23% of the plan | **NOTED, NOT DROPPED.** The launch order welds them to this lane; dropping is a scope change, outside my latitude. Given a real postcondition instead |
| F12 | Anchors duplicated byte-identically nine times — the plan is an instance of the defect it fixes | **ACKNOWLEDGED, NOT FIXED.** The engine's schema carries anchors per task; a plan-level block is an engine change, outside this lane. Staged as a triage candidate. The critic is right that this is the same decay |
| F13 | `config_ref` dangles in `execute.json` too | **CONFIRMED.** `docs/agents/engine-config.json` does not exist; the engine tolerates it (this plan's checks all ran). Staged as a triage candidate |

## Falsifiability proof of the revision

Every `command` postcondition in the revised plan was executed against the pre-work tree. All five
returned non-zero. A check that passes before the work is done cannot discriminate; these do.

    g1-integrate.c2: rc=1    g2-integrate.c2: rc=1    g3-integrate.c2: rc=1
    g4-integrate.c2: rc=1    g5-final.c2:     rc=4
