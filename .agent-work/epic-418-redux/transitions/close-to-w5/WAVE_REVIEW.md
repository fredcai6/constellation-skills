> **Carried forward.** This is wave 4's review, re-rendered at the `close-to-w5` boundary because that
> boundary is a *material exception* (a human scope change arriving after wave 4 had already exited),
> not a new wave exit. Wave 4's own exit stands at `w4-to-close`, decision `stop`. Wave 5's review will
> be written at its own boundary.

## Wave 4 review

**One issue, one merge, one close -- and the wave found its own subject inside its own fix.**

#467 makes a HARD context reading change the instruction rather than refuse the verb: the band now guards `start`
and `reopen` instead of `advance`, so the advance that *carries* the handoff is never blocked. Zero new CLI surface,
because `advance --why` already failed closed on silence and that `--why` **is** the DIGEST.

**The blocking finding is the story.** The first trip-ledger implementation was erased by the very close the band
orders an agent to make -- at/over hard the only legal close is `advance --why`, that appends a new why-record, and
the selector matched only the live record. Measured at 0.20 fill: 1 after a refused begin, 2 after a released begin,
**0 the moment the agent complies**. A three-gate runaway peaked at 2 and was **absent at the seam**, byte-identical
to an agent that behaved perfectly. And a *passing* test ran the offender's path byte-for-byte while calling it
"a fresh agent" -- a green test certifying the bug. Caught at review, reproduced by the Commander in its own shell,
fixed additively with the live keying at zero diff.

**The acceptance measurement is the strongest evidence this epic has produced.** Two dispatched agents on a separate
spine; B's prompt was the engine's `current` output and nothing else (3754 bytes, sha256 `3da6411...`, asserted
byte-equal in code and independently re-verified by the Admiral). The trip fired on a *real* reading rather than a
large plant, via a per-gate threshold that puts the hard line at 0.001 -- verified in force, because at 0.05 fill the
engine renders the HARD band, which the default cannot do. And the handoff was made load-bearing: A had to invent a
six-hex nonce and was forbidden to write it to disk; B's gate required an item to *be* that nonce. B wrote it.
**B could not have finished without reading A's understanding.**

**Eight specimens of the check-that-cannot-fail defect were found in this one wave** -- four catalogued by the crew,
one inside the fix for those four, one in the acceptance verifier's own self-test, and the engine's `--authority`
field. Three more were found Admiral-side: the installer's interpreter probe, the wave-launch gate's skills-root
guard, and the journal's missing instrument identity. **All three of those sit in verification and provisioning
machinery** -- the layer whose whole job is to be trustworthy, and which nothing reports on.

**Reported honestly:** DC2 done-by-different-means, DC6 **partial**. #504 was filed and deliberately not fixed,
because touching that code would have voided the review the rework cycle had just earned.

The trip fired live **four times** during its own fix, on four different Commanders, each of which handed off cleanly
and stopped. #266's premise -- that the trip had never fired on a correct reading -- is falsified by the work itself.
