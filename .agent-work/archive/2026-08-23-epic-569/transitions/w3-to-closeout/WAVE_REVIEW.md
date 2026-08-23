## Wave review -- wave 3 (final)

**All four lanes merged.** `#660` `w3-ci`, `#659` `w3-basis`, `#661` `w3-door`, `#662` `w3-promote`,
plus four follow-on fixes. Main green at **3774 passed, 6 skipped, 0 failed**; `test-linux` **GREEN**
in CI for the first time.

### What the wave delivered

| lane | family | result |
|---|---|---|
| `w3-promote` | **A** | 16 of 65 conditions promoted using only existing check kinds; `validate_spine.py` corpus faults **19 -> 5** |
| `w3-basis` | **B** | blob-OID pin, drift **fails** rather than skips, re-verify path shipped with the guard |
| `w3-ci` | **C** | one `ubuntu-latest` job -- and three defects behind the old red |
| `w3-door` | plumbing | `_crew_door_env` clears the spine pair on `spine=None` |

### What the wave refuted

- **The ~31-of-65 extrapolation.** 16, not 31 -- and the guard written to catch a bad extrapolation
  caught it. Bucket-2 density tracks template **shape**, not identity: rich orchestrator spines land
  in the predicted band, thin scaffolding lands at or below the floor. **5 of 7** non-baseline
  templates fell outside, every one low.
- **"A lane fixing a defect stops it spreading."** `w3-promote` copied `w3-basis`'s pre-repair
  skip-on-drift into six new classes -- **35 inert assertions** -- citing in its own docstring the
  very class being repaired three worktrees away.
- **"A completion artifact reports the tree it shipped."** `w3-basis`'s RESULT said 3 failed; the
  failures had been repaired two commits earlier and did not reproduce.
- **"Refresh-requests are load-bearing."** `w3-ci`'s episode records `spine_start` refusing at
  *"context at 17% is at/over the hard limit"* with fill actually at **17-18%**, driven mainly by the
  ~600-word gate imperative echoed back on nearly every engine tool call. They fire on noise.

### Disposition

**`stop`.** Wave 3 was ruled the final wave; every lane is merged and every epic issue is
dispositioned. The epic enters closeout.
