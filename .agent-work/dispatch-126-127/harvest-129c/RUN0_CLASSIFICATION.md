# Round-2 run-0 (subject A) — classification

Temp dir: `C:/Users/fredc/AppData/Local/Temp/constellation-eval-6lcnbis9/run-0`
Meta: completed-fail, reason=process-check-failed, exit 0, elapsed 690s (~11.5 min),
finished on its own (NOT a timeout), subject_pid 35108, heartbeats present.

## Verdict: NEAR-TERMINAL — release-ordering fail (NOT skip/theater/quit-early/fabrication)

The subject drove the FULL engine spine honestly, all 10 steps complete:
init→context→understand→plan→execute→reconcile→triage→review→feedback→archive.
This is the exact tail round-2 wording targeted ("solution is the MIDDLE, not the end").
It did NOT stop when solution.py + green tests existed — the #129 off-ramp is closed.

Check results against the frozen instrument:
- artifact_present: PASS (solution.py non-empty)
- tests_green:      PASS (pytest green)
- spine_completed:  FAIL — "journal entry seq 44 follows the lease release"
- work-complete.txt: PRESENT (461 bytes, written last at 16:39, after archive)

Journal is otherwise FULLY sound (read-only diagnostic, instrument untouched):
- 46 entries, hash-chain intact, timestamps monotonic
- every complete task has an advance/record entry
- ONLY violation: 3 archive-closeout entries land after released_at:
    released_at = 16:38:42.706
    seq 44 attest archive @ 16:38:51
    seq 45 waive  archive @ 16:39:04  (c4 git-change-policy waive)
    seq 46 advance archive @ 16:39:08  (final advance that closes the step)

## Root cause
Archive step imperative (spine template, FENCED) ends: "Finally, release the engine
session lease." The subject released the lease as the archive step's "finally" action
— BEFORE it had satisfied the archive postconditions (c4 waive) and run the mechanical
`advance archive` that closes the step. Result: legitimate closeout journal entries
follow released_at, and spine_completed's journal/lease-window rule fails.

The ordering that PASSES: satisfy/waive postconditions -> `advance archive` (closes
spine, final journal entry) -> THEN `release` (released_at becomes the last moment,
no journal entry after it). Both orderings are plausible readings of "finally release";
the wording does not disambiguate, and the natural reading trips the check.

## Fix location question (for the float / decision)
- Cleanest structural fixes touch FENCED files:
  (a) archive imperative in skills/commander/templates/COMMANDER_SPINE.template.json
      (not my ownership), or
  (b) spine_completed.py journal/lease-window rule tolerate the terminal step's own
      closeout entries after release (FENCED instrument — float if bug).
- WITHIN MY OWNERSHIP: skills/commander-delegated/SKILL.md step 4 can add an explicit
  release-ordering line ("at archive, advance the step to complete BEFORE releasing the
  lease; releasing first leaves closeout journal entries after the lease release and
  fails provenance"). This is completion-side wording in my file = authorized strategy 2.

## Decision pending B/C
If B and C reproduce this same release-ordering fail (dominant blocker), author the
strategy-2 SKILL.md release-ordering clarification and re-measure (round 3). If the fix
seems to genuinely require the fenced spine template or the instrument, float to Admiral
with this evidence rather than working around it.
