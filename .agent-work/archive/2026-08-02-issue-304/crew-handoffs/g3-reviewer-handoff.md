# Reviewer Handoff — issue-304 gate g3: delete the superseded prose, then RUN

## What was implemented

**172 words deleted** (86 per template, two templates) — the dead-path block about
`docs/agents/engine-config.json` from `COMMANDER_SPINE.template.json` `tasks.context.imperative` and
`EXECUTE_PLAN.template.json` `tasks.e0-context.imperative` — plus the T3 retarget of the pathless
*"the current map"* phrasing, a fresh spine **actually driven** through `init` and `context` in this
repo, five episodes filed with real observed behaviour, `tests/test_prose_deletions.py`, and a trend
snapshot.

## How to inspect the diff

```
cd C:/Programs/constellation-skills-wt/e298-304
git log --oneline a8d9467..HEAD
git diff a8d9467..HEAD -- skills/ tests/
```

`a8d9467` is the g2 close — **already reviewed and APPROVED twice. Do not re-review g2.**

Implementer's report: `.agent-work/issue-304/crew-handoffs/g3-result.md`.
Pre-registration: `TRIPWIRES.md` at `0119fa4` (T1–T4) and `1662b90` (T5), both **before any deletion
existed**. Outcomes: `.agent-work/issue-304/TRIPWIRE_OUTCOMES.md`. Handoff it was built against:
`.agent-work/issue-304/crew-handoffs/g3-implementer-handoff.md`.

## THE QUESTION THIS HANDOFF EXISTS TO ASK

**CAN THIS CHECK FAIL?**

Asked because #300 shipped an acceptance test that **survived two independent reviewer rounds** while
being structurally unable to falsify the property it existed to falsify. The diagnosis: *"a reviewer
given a handoff checks conformance to that handoff, and no handoff asked 'can this test fail?'"*

**Answer it by execution.** Devise at least one mutation of your own that is **NOT** among the nine
already shipped in `tests/test_mutation_floor.py`, apply it, run the suite, and report whether it went
red with real output. A review that reports conformance without attempting a mutation **has not
completed this gate**.

Aim at least one mutation at **`tests/test_prose_deletions.py`**, which is this gate's own new pin. It
asserts the deleted strings are ABSENT *and* the load-bearing survivor is PRESENT. Absence alone would
pass on a template that deleted everything — so break the **presence** side and confirm it goes red. A
one-directional deletion pin is exactly the "check that cannot fail" this epic keeps finding.

## The deviation that most needs independent eyes

Two **out-of-scope** test files — `tests/test_context_manifest.py` and
`tests/test_map_contract_wiring.py` — pinned prose phrases *of the deleted block* as sentinels. The
implementer's claim is that **no version of this gate deletes the block and leaves them green**, so it
re-pointed each sentinel at surviving degraded-mode prose, "assertion counts and intent unchanged," and
named the deviation rather than burying it. Isolated in `ea52b2f` and `456cac0`.

**"Changed a test to green" is the exact shape a reviewer must not have to discover alone.** Verify it:

- Was the claim true — does the block's deletion genuinely break those sentinels, with no narrower fix?
- Is each re-pointed sentinel **equally strong**, or was an assertion quietly weakened or dropped?
  Diff assertion-by-assertion against `a8d9467`, do not count lines.
- Does each new sentinel pin something that would **actually still be there** for the right reason,
  rather than a phrase that happens to survive?

If any assertion is weaker than what it replaced, that is a BLOCK.

## T4 — the tripwire aimed at the implementer's own edit

The phrase `no docs/agents/ overlay at all` occurred **twice** in `tasks.context.imperative`. The
**first** is the load-bearing substitute-and-record rule — the degraded-mode intake this whole issue
exists to *strengthen*. The second was inside the dead block. A naive string delete removes both and
silently strips degraded-mode intake while appearing to remove only dead prose.

I verified independently before sending you this: the count is now **1**, at **offset 262**, inside the
substitute-and-record sentence, and both dead-path blocks are gone. **Confirm it yourself anyway**, and
check the *pin* rather than the state: does a test fail if the survivor is removed?

## The RUN half — deletion without the run is half this gate

The implementer reports driving a fresh spine through `init` and `context` in **this** repo (which has
`docs/agents/` but no `docs/architecture/`, and is therefore the **degraded common case**), capturing
384 lines of the engine's own output, with the contract **reporting rather than passing silently**:
`RECEIPT-MISSING` (12) → `DEGRADED-NO-MAP … still owed` (10) → `SATISFIED, problems: 0` (0) →
`context -> complete`.

Verify the sequence is real and reproducible, and specifically that **one command discharged it and work
continued** — a contract that reports but deadlocks would be a worse outcome than the silence it
replaced.

## The episodes — check that they observed something

Five episodes, `issue-304-g3-001` … `-005`, filed via `apply_episode_delta.py` (the only write path).
Each must carry `expected-behavior` = the pre-registered prediction and `observed-behavior` = **what
actually happened**, citing the pre-registration SHA.

**An episode whose `observed-behavior` restates the prediction has observed nothing.** Read all five and
say so if any does. The store has no `confirmed` standing (#342), so a tripwire that held and one never
checked look identical there — the real observation and the citation are the only things carrying the
weight.

## Three honest nulls — verify they are honest, do not treat them as failures

The launch order is explicit: *"a measured negative on the stated question is a complete, successful
deliverable, reported with the same rigor as a win."*

- **T3's mapped-repo clause: UNTESTED**, scored untested rather than held, because no mapped repo was
  reachable (f1Brainz is off-limits). Correct handling — confirm it was not quietly scored as a pass.
- **T5: NOT DETERMINABLE**, recorded as a measurement gap. `TRIPWIRES.md` asked for exactly this:
  *"Distinguishing the two outcomes matters more than the outcome… if it cannot, that is a measurement
  gap to report, not a result to round off."* Confirm the gap is stated as a gap. The supporting claim —
  `grep map_before_src scripts/map_orient.py` returns nothing, i.e. the gate reads receipt *content* and
  never ordering — should be re-run, not accepted.
- **T1: HELD with a named near-miss** — two pinning tests did fail, both for the exempted literal-string
  reason. Verify that exemption is genuine and not a rationalization: did anything fail for a reason
  *other* than the literal string being absent?

## Also verify

- **`TRIPWIRES.md` is byte-identical to its pre-registration**, and both SHAs are ancestors of the
  deletion commits. If the predictions moved after the outcome was known, the whole pathway is void.
  The implementer claims both; check both.
- **The 172-word count is derived from a command**, not asserted. It was corrected twice earlier in this
  issue (it is not 112). Re-derive it.
- **The trend snapshot names its consumer and its successor.** Admiral amendment: the consumer is *the
  next snapshot*, the successor is due at **epic-298 close**, and the retire-if-unread rule must be
  stated. A baseline with no scheduled successor is decoration wearing a measurement's clothes.
- **T3's premise in the implementer handoff was wrong** — I wrote that g2 had already retargeted the
  plan-side phrase; the implementer verified it byte-identical across all eight commits that ever
  touched the template and did the retarget itself. Confirm the retarget is correct and complete;
  the error was mine, not theirs.

## Allowed scope / exclusions

Review `a8d9467..HEAD` only. **Out of scope, do not flag as defects:** anything in g1 or g2 (both
APPROVED); the g4 dogfood pass and full suite; #341 (relative command checks); #342 (episode standings);
#344 (stale installed corpus); #363; #364; a bootstrap/`CLAUDE.md` stanza (**ruled OUT** by the human —
the map is orchestrator content). Do not fix anything; report findings with severities.

## Known limitations — not novel finds

The citation check has **measured sensitivity 0/4, specificity 0/1** against the epic's baseline five and
ships as a **regression floor**, not the fix for map-lateness. The degraded check remains partly
self-attested. Both are ratified framings. **Do flag any place the code or docs overclaim them.**

## Constraints

- `python -m pytest`, **never** `py -m pytest`. **Flag any 3.13+-only API as a BLOCK.**
- Compare normalized content or blob OIDs, **never raw bytes** — `git status --porcelain` shows a
  phantom `M` from CRLF while `git diff --quiet HEAD` returns 0. This has now bitten four agents in this
  epic, including the g2 reviewer.
- **Do not point any tooling at `C:/Programs/f1Brainz`** — `orient` WRITES a receipt into whatever
  `--root` it is given, and that repo is read-only. Use a temp fixture.
- Never touch `C:/Programs/constellation-skills` or `C:/Programs/constellation-skills-wt/e298-331`.
- Do not rewrite `TRIPWIRES.md` under any circumstances.

## Required evidence

Paste actual output for: the suite; **your own mutation** (the diff and red/green); your re-derivation
of the 172-word count; your check of the `TRIPWIRES.md` byte-identity and SHA ancestry; your
assertion-by-assertion comparison of the re-pointed sentinels; and your read of all five episodes.

## Return format

Write `REVIEW_RESULT` to `.agent-work/issue-304/crew-handoffs/g3-review-result.md` with a verdict of
exactly **APPROVE** or **BLOCK**, findings by severity, and the evidence above. That file on disk is the
contract the Commander polls for. Return thin.
