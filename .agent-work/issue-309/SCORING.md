# Scoring — issue #309, g3-score

## Ground-truth freeze reverified
`git hash-object .agent-work/issue-309/GROUND_TRUTH.json` = `770cc642967853dbcb5c7b03bc41454f71a88b35`,
identical to the hash recorded as evidence at g1-seed. Ground truth was not touched
between freezing it and scoring against it.

## Per-defect scoring (against GROUND_TRUTH.json, recall_denominator = SD1-SD4)

| id | Viewpoint A (Contradiction) | Viewpoint B (Drift) | any-viewpoint outcome |
|---|---|---|---|
| SD1 | FOUND — finding 1, quotes "No checklist..." vs "Every candidate must first clear checklist_engine.py's gated sequence..." | FOUND (as the pivot of its finding 2, quoting the same Gate Discipline line against curator's Mend-section text) | **FOUND** |
| SD2 | FOUND — finding 3, quotes "Triage does not implement..." vs "which implements the recommended fix directly..." | FOUND — finding 1, same two quotes | **FOUND** |
| SD3 | NOT FOUND (explicitly out of its own stated lens — "No contradictions were found involving debt-cadence-copy.md," consistent with a logical-contradiction-only mandate, not a failure of the lens) | FOUND — finding 3, quotes the 3-repo list vs. the 2-repo invocation commands | **FOUND** |
| SD4 | FOUND — finding 2, quotes "Never deletion, never truncation" vs the injected 90-day-clearing bullet | FOUND — finding 4, same two quotes | **FOUND** |
| SD5 | **NOT-FOUND, non-reading.** Viewpoint A's report never mentions issue #199, #106, or the Portfolio duty section at all. Quote supporting this: the report's final line lists only "debt-cadence-copy.md" as fully checked and clean; the Portfolio duty section of curator-copy.md is never referenced anywhere in the report. This is a NON-READING (never considered), not a reading that concluded NOT-FOUND. | **NOT-FOUND, non-reading.** Viewpoint B's report explicitly lists what it checked ("the Fix-Now Ladder's four rungs, Triage's three dispositions, Curator's five measured properties, the template filename") and states "No other enumerated lists, counts, or identifiers... showed disagreement" — the issue-number reference is NOT in that enumerated list, so it was never inspected. Also a NON-READING, not a considered-and-rejected NOT-FOUND. | **NOT-FOUND (miss control fired as designed) — both viewpoints show a non-reading, not a considered rejection.** Per the doctrine "a non-reading must be visibly distinct from an uncollected one," this is recorded as a MISS the instrument could not have been expected to catch (SD5 required verifying an issue number against the live GitHub tracker, which neither viewpoint was given or told to check), not a failure of viewpoint diligence within the slice it was handed. |

## Recall
`recall = |{SD1,SD2,SD3,SD4} found by AT LEAST ONE viewpoint| / 4 = 4/4 = 100%`

Per-viewpoint breakdown (for transparency, not the headline number):
- Viewpoint A (Contradiction Auditor): 3/4 (SD1, SD2, SD4) — SD3 correctly excluded as outside its own declared lens (a drift/list-mismatch, not a logical policy contradiction), not a miss of its mandate.
- Viewpoint B (Drift Auditor): 4/4 (SD1, SD2, SD3, SD4).

**SD5 (miss control): confirmed NOT-FOUND by both viewpoints, both as non-readings.** This
is the demonstrated proof that the instrument CAN miss, satisfying `decision:prove-the-miss`
before any recall number above is treated as final.

## Noise
Every finding either viewpoint reported maps onto {SD1, SD2, SD3, SD4} — 3 findings from
Viewpoint A, 4 from Viewpoint B (Viewpoint B's finding 2 is a secondary citation of the
same SD1 root cause via a different quote pair from curator-copy.md's Mend section — same
underlying seeded defect, recorded once against SD1 per the disposition rule in
PLAN_CRITIC_DISPOSITION.md item 8, not double-counted as a separate item and not noise).
Viewpoint B's "out-of-slice reference" note (§3/§6 of the real EPISODE_STORE.md, not
present in the excerpt) is explicitly labeled by the viewpoint itself as NOT a confirmed
finding ("not claimed as confirmed") — it is a disciplined non-claim, not a reported
defect, so it does not enter the noise count either way.

`noise_ratio (both real viewpoints, this run) = 0 / 7 = 0%`

**DECOY1 (noise control) outcome, real viewpoints: NOT-FLAGGED by either.** Quote support:
neither Viewpoint A's nor Viewpoint B's report contains the pairing "No checklist... /
Drive every step through the checklist engine..." using triage's and curator's ORIGINAL,
unmodified top-of-document lines (Viewpoint B's finding 2 uses curator's *Mend-section*
line, not its top-of-document line, and pairs it with the *injected* Gate Discipline text,
not the original "No checklist" line — a different, SD1-rooted pairing). This is an honest
null on the decoy AS DESIGNED: both lenses' explicit instruction not to flag "two skills
legitimately choosing different tooling for their own steps" worked as intended.

**Because a 0%-noise result from well-instructed viewpoints does not by itself satisfy
`decision:prove-the-miss`'s requirement to demonstrate a false positive BEING RAISED and
then rejected (a null is not a demonstration), a supplementary, explicitly-labeled
instrument-validation probe was run** (see VIEWPOINT_REPORTS.md, "Supplementary
instrument-validation probe") — a deliberately low-bar "fast pattern-matcher" lens, fed
DECOY1's two quotes in isolation (not a slice expansion; not counted as a third sweep
viewpoint or folded into recall/noise arithmetic above). It answered **YES, contradiction**,
while its own text acknowledged "may govern different workflows" — a genuine false
positive, produced on demand.

**Disposition: REJECTED, correctly, as noise.** Per GROUND_TRUTH.json's stated criterion
("no doctrine anywhere in the slice or inline-pasted context requires uniform tooling
across skills"), this finding does not describe a genuine coherence defect — it is scored
as the demonstrated-and-rejected false positive that satisfies the noise half of
`decision:prove-the-miss`. It is NOT added to the 7-item noise denominator above, because
it came from a distinct, explicitly out-of-band probe, not from either of the two real
sweep viewpoints — folding it in would conflate "the pathway CAN produce noise under a
weaker lens" (now demonstrated) with "these two actual viewpoints DID produce noise this
run" (they did not — a materially different, more useful fact, and conflating them would
be exactly the kind of noise-ratio-vacuously-assumed-zero the launch order warns against
from the other side).

## Headline verdict
- **Recall (any-viewpoint, SD1-SD4): 100% (4/4).**
- **Noise ratio (the two real sweep viewpoints, this run): 0% (0/7 findings).**
- **Miss demonstrated:** yes — SD5, both viewpoints, both non-readings (not considered-and-rejected).
- **False positive demonstrated-and-rejected:** yes — via the supplementary low-bar probe against DECOY1, since the two real viewpoints' own discipline produced no false positive to reject on their own.

Scoped nulls, stated explicitly: this result is "this 4-file slice, these two lens
designs, this seeding, got 100% recall / 0% noise from two disciplined viewpoints" — it is
NOT "adversarial coherence sweeps always achieve perfect recall" or "viewpoints never
produce noise." The one data point most worth flagging for a future run: a 0% noise ratio
from the real viewpoints was a genuine result of careful lens wording (the explicit
"do not flag two skills making independent choices" instruction in both lenses), not
evidence that noise is structurally impossible — the supplementary probe proves the
opposite the moment the lens is loosened.
