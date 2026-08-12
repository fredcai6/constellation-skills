## Current planning truth -- after wave 3

**B extended is complete.** #433, #436, #460, #464, #461, #465, #488 and #489 are all merged and closed. Main is green at `1789 passed, 2 skipped, 683 subtests`.

### Next: A2 -- and it is uncut

A2 settles what a limit *means*: a trip becomes a change of instruction rather than a refusal, so there is room to build the handoff. Six done-conditions, provisionally three issues -- DC1-3 (the conversion, #431 dissolving), DC4+DC6 (per-gate thresholds with the override exercised once, plus a mechanical compliance signal), and DC5 (the full round trip).

Wave 3 handed A2 two things it did not have before:

- **The round trip ran twice, by hand, successfully.** Both governor trips cost bookkeeping only. DC5 exists precisely because DC1-3 can all pass while continuity never happens once; it happened twice here.
- **The first measurement that the default threshold is wrong for a role.** The Admiral ran a full wave at 33% fill; crews trip at 17-21%. That is the gate-where-it-has-bitten that DC4's override mechanism is for.

### The governor thread, three of four parts already written

| | What | State |
|---|---|---|
| #458 | wire the writer into tracked settings so it ships at all | not done -- it lives only in an untracked `settings.local.json`, so every governor observation this epic made came from config that ships to nobody |
| #264 | assert the gauge is still *measuring* | **1144 lines written, unmerged**, 211 commits behind |
| #488 | stop it silencing itself | **merged** |
| #452 | attribution proper | open, narrower now |

### The lens

A check that cannot fail: a signal whose value is identical in the healthy and defective worlds. It is not a candidate theme -- it is the epic's spine, appearing in critic finding F8 (*"the purest check-that-cannot-fail in the document"*), in A2's own DC6 as a priced design cost, and six times in wave 3's execution.

### Stopped

The latitude contract expired at the wave-3 boundary. Nothing launches until it is refreshed and A2 is cut.
