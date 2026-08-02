# Reviewer Handoff — issue-304 gate g2: wire the contract at context and plan

## What was implemented

1. **The anchor change** — `skills/commander/templates/COMMANDER_SPINE.template.json`
   `tasks.context.imperative` re-anchored from *"Read the current map …"* to **"Before you open any
   source file, resolve and read the map input."** This is the highest-value item in the gate and the
   epic's only untested variable.
2. **`verify-frame`** in `scripts/map_orient.py` — refuses an absent frame, an unknown anchor (naming
   it), a code-cut frame, and a degraded frame citing an undeclared substitute.
3. **Asymmetric wiring** — `verify-orientation` as a command postcondition at the **context** step
   (`c2`); `verify-frame` at the **plan** step (`c6`); `verify-frame` deliberately **absent** from
   context.
4. **A partial independent oracle for the degraded case** — a fixed corpus-declared fallback set
   (`README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/index.md`, `docs/README.md`) probed by filesystem
   existence, with each substitute labelled by provenance.
5. **Installer registration** — `map_orient.py` in `SKILL_SCRIPT_BUNDLES`.
6. **Three new mutations** on the falsifiability floor.

## How to inspect the diff

```
cd C:/Programs/constellation-skills-wt/e298-304
git diff 6d35fe2..HEAD -- scripts/ skills/ tests/
git log --oneline 6d35fe2..HEAD
```

`6d35fe2` is the g1 baseline (already reviewed and APPROVED — **do not re-review g1**). Everything after
it is this gate.

Implementer's own report: `.agent-work/issue-304/crew-handoffs/g2-result.md`. Read it — it is unusually
candid and names six deviations. Your job includes deciding whether that candour is accurate.

## Task statement it was built against

`.agent-work/issue-304/crew-handoffs/g2-implementer-handoff.md` — the contract — plus
`g2-implementer-handoff-RESUME.md`, the addendum that governed a relaunched attempt.

## THE QUESTION THIS HANDOFF EXISTS TO ASK

**CAN THIS CHECK FAIL?**

Asked because #300 shipped an acceptance test that **survived two independent reviewer rounds** while
being structurally unable to falsify the property it existed to falsify. One of those rounds returned a
correct BLOCK on a *different* real defect — competence was not the problem. The diagnosis: *"a reviewer
given a handoff checks conformance to that handoff, and no handoff asked 'can this test fail?'"*

**This handoff asks it. Answer it with execution, not judgement.**

You MUST:
1. **Devise at least one mutation of your own that is NOT among the eight shipped.** The shipped eight,
   so yours is provably outside them:
   1. `all`→`any` on degraded-completeness
   2. `UNRESOLVABLE-ROOT`→`DEGRADED-NO-MAP` collapse with exit 0
   3. `path.exists()` instead of citable content
   4. `not any`→`not all` on `unmapped`
   5. a sentinel accepted as a hash pin
   6. an absent mission frame credited as a pass
   7. the undeclared-substitute refusal disabled
   8. the known-fallback label granted on set membership alone
2. **Apply it.** 3. **Run the suite.** 4. **Report whether it went red**, with actual output.

A review that reports conformance without attempting a mutation **has not completed this gate** and will
be sent back.

## The specific defect class that already bit this gate — hunt it again

The implementer's audit of its dead predecessor's work found that `probe_fallbacks()`,
`classify_substitute()` and `substitute_label()` **existed, were self-tested, and were never called from
`cmd_orient`**. Every signal was green while the receipt recorded none of the oracle. The stated lesson:
*"green tests are not evidence a deliverable landed — grep for the caller."*

**Apply that test to the whole gate, not just to m3.** For each function the deliverables demand, prove
there is a call site outside its own `def`. If any other shipped helper is reachable only from its own
unit test, that is the same defect and it is a BLOCK.

## Three reconstructed TDD reds — this is the deviation most needing independent eyes

Attempt-1 died on a session usage limit with m2/m4/m5's implementation written but unattested.
Attempt-2 could not observe those reds in TDD order, so it **reconstructed** them: revert the file to
`6d35fe2`, run the tests, observe the failure, restore, verify the restore by **blob OID**.

That was sanctioned in the addendum, and it is honestly labelled — the result says explicitly that it
proves the tests **discriminate**, not that TDD authoring order happened. **Verify the substance, not
the label:**

- **Reproduce at least one reconstruction yourself.** Pick whichever you like. Does reverting that file
  actually produce the pasted failures, at the pasted count?
- **Verify the restores are clean.** `git diff --quiet HEAD -- <path>` and `git status --porcelain`.
  Compare **blob OIDs or normalized content, never raw bytes** — `core.autocrlf` makes working-tree
  bytes differ for identical committed content and it has bitten three agents this epic.
- If a reconstruction does **not** reproduce, that is a BLOCK and a serious one.

## Deviation 5 — a pre-existing assertion was CHANGED. Judge it independently.

`--self-test`'s *"that refusal names the undeclared path"* asserted the **lowercased** `claude.md`. The
implementer says that assertion was **pinning a defect** — the refusal renamed the offender the author
has to act on — and changed it to assert the as-cited `CLAUDE.md`, calling it strictly **tighter**.

"Changed a test to green" is exactly the shape a reviewer must not have to discover alone, and the
implementer flagged it rather than burying it. **Confirm the reasoning holds:** is the new assertion
genuinely stricter, is matching still case-insensitive while reporting is as-cited, and is this the
**only** pre-existing assertion altered? Diff the test files against `6d35fe2` and check.

## Deviation 6 — a proposed fix was declined as a false positive. Check the measurement.

The Commander's addendum offered a "free fix": `CONTENT_HASH_RE` uses `{64}` where `{64,}` is correct.
The implementer **declined it with a measurement** — `^[0-9a-f]{64}$` already rejects 65- and 128-char
digests because of the `$` anchor, and `{64,}` would *loosen* the pin (a 128-char sha512 would then
pass as a sha256 pin).

**Re-measure it.** If the implementer is right, say so and the g1 survivor gets closed as not-a-defect.
If it is wrong, that is a finding. Do not accept the reasoning on its face.

## Close criteria

- `python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_context_manifest.py tests/test_context_declaration_lint.py tests/test_context_determinism.py tests/test_install_constellation.py tests/test_map_contract_wiring.py -q`
  green (~165s; the last file is the gate's own addition, which the original required-evidence list
  predates).
- `python scripts/map_orient.py --self-test` green.
- **An ABSENT frame REFUSES.** It must never vacuously pass. This is the single most important negative
  case in the gate — attack it directly, not only through the shipped mutation.
- **`verify-frame` does not run at the context step.** No frame exists there; making "absent frame at
  context = pass" would destroy the anti-vacuity property. Confirm by reading the template, not only by
  trusting `test_verify_frame_never_runs_at_the_context_step`.
- **`orient` never prints an anchor id.** If it did, the citation check becomes self-satisfying — an
  agent could paste back what the tool told it. Load-bearing; verify by running `orient`, not by
  reading the test.
- **The context imperative is anchored to "before you open any source file"** — not to a later artifact.
  A map-first imperative anchored to a late artifact is not a map-first imperative; PRE-B measured the
  late-anchored form producing exact compliance with zero orientation.
- **Gate-vs-report stays a flag flip** (`--report-only`), not a rebuild.
- No new exit codes beyond the frozen g1 vocabulary.
- The three template-pinning suites (`test_context_manifest`, `test_context_declaration_lint`,
  `test_context_determinism`) pass **unchanged** — confirm they were not edited to accommodate the
  template change.

## Allowed scope / exclusions

Review `6d35fe2..HEAD` only. **Out of scope, do not flag as defects:** anything in g1 (already APPROVED);
prose deletion (g3); the dogfood pass (g4); the five fragile relative command checks (#341); the episode
store's missing `confirmed` standing (#342); the stale installed corpus (#344); a bootstrap/`CLAUDE.md`
stanza (**ruled OUT** by the human — the map is orchestrator content, not implementer content).

## Known limitations you should NOT report as novel finds

- The citation check has **measured sensitivity 0/4 and specificity 0/1** against the epic's baseline
  five. It ships as a **regression floor** against map-*ignoring*, explicitly **not** as the fix for the
  measured defect, which is map-*lateness* and needs a harness hook the corpus does not own. Ratified
  framing, not an oversight. **Do flag any place the code or docs overclaim it.**
- The degraded check remains **partly self-attested**. The fallback probe converts half of it to a
  filesystem oracle; the agent still chooses what to declare. Deliberately not described as closing the
  gap — flag it if anything says otherwise.
- The known bypass — crawl source first, write anchors into the frame afterward — is the **measured**
  behaviour, already named. Not a novel find.

## Constraints

- Windows: `encoding='utf-8', newline='\n'`.
- `python -m pytest`, **never** `py -m pytest` (`py` is 3.12, CI's pin, but has no pytest; `python` is
  3.14 with pytest). Neither reproduces CI. **Flag any 3.13+-only API as a BLOCK** —
  `Path.read_text(newline=...)` passed locally and cost 39 CI failures on PR #320.
- **`C:/Programs/f1Brainz` is READ-ONLY, and `orient` WRITES a receipt into whatever `--root` it is
  given.** Do not point any tooling at it. Use a temp fixture.
- Never touch `C:/Programs/constellation-skills` or `C:/Programs/constellation-skills-wt/e298-331`.
- Do not fix anything. Report findings with severities; the Commander adjudicates.

## Required evidence

Paste actual command output for: the suite; the self-test; **your own mutation** (the diff you applied,
plus red/green); your reproduction of one reconstructed red; your caller-grep audit; and your
re-measurement of `CONTENT_HASH_RE`.

## Return format

Write `REVIEW_RESULT` to `.agent-work/issue-304/crew-handoffs/g2-review-result.md` with a verdict of
exactly **APPROVE** or **BLOCK**, findings by severity, and the evidence above. That file on disk is the
contract the Commander polls for and verifies. Return thin.
