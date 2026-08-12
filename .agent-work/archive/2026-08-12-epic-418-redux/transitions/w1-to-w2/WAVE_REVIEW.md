## Wave review - boundary w1-to-w2

Waves 0 and 1 are merged and closed. Main is green at `ca0e36a`: **1721 passed, 4 skipped, 643
subtests, exit 0**, with the real exit code captured.

### What the boundary found

| Signal | Disposition |
|---|---|
| The installed skill corpus was stale against the repo - 12 skills, 6 in `SKILL.md`, including `commander-delegated` and `workbench` | Resolved here by syncing the install; zero non-launcher differences remain |
| The installed Admiral spine called `apply_lessons_delta.py` and `verify_agent_feedback.py`, both deleted by #447 | Avoided by instantiating from the repo template; the sync fixed the root |
| #447 was open while its core obligation was already met | Closed here with a per-done-condition accounting |
| The predecessor green figures (1723/2 and 1764) do not match this measurement (1721/4) | Recorded, not reconciled; the measured baseline at a named revision governs |
| The playbook retirement is leaking back at the authoring end (#460) | Pulled into the current wave rather than left for E |
| The governor hook is unwired, so the governor fires nowhere on a shipped config | Stays off-chain as #458; it gates done-condition 1, not this wave |

### Honest note on #447

Its fourth done-condition - *nothing reads episodes as prescriptions* - is **partially met**. The
read path is retired and no consumer conditions behaviour on the store, but #460 found the
obligation leaking back at the authoring end. That was stated as partial rather than claimed as
done, and the remainder is tracked and scheduled rather than dropped. This matters because #447
exists precisely to catch a close that claims an unmet obligation.
