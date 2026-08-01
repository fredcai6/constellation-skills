## Round-2 wording — the clean terminal-completion measurement (reap-safe runner)

Three runs, euler-1-multiples, sonnet (`claude-sonnet-4-5`), hardened+journal checks,
driven one-at-a-time on the reap-safe runner (PR #132/#135). **No environment deaths this
round** — an independent wall-clock meta-deadline watch replaced the unreliable
completion signal, and all three finalized cleanly. Command-verified from kept temp dirs.

### Measured table (round-2 wording as shipped, unchanged on main)

| run | temp dir | engine driven | steps complete | artifact | tests | sentinel | journal | terminal? | fails on |
|---|---|---|---|---|---|---|---|---|---|
| A | 6lcnbis9 | yes (crew, genuine lease) | 10/10 | PASS | PASS | yes | sound (46 entries, hash-chained) | **no** | release-window rule only |
| B | g6o67i9t | yes (crew, genuine lease) | 10/10 | PASS | PASS | yes | sound (46 entries, hash-chained) | **no** | release-window rule only |
| C | iricdfpb | yes (crew, genuine lease) | 9/10 (archive in-progress) | PASS | PASS | yes | sound (40 entries) | **no** | provenance: not all tasks complete |

### Headline: round-2 wording CLOSED #129's off-ramp
A and B drove the FULL reconcile→triage→review→feedback→archive tail — the exact
truncation round-2's "solution is the MIDDLE, not the end" clause targeted. Neither
stopped when solution.py + green tests existed. The round-1 failure mode (stop at
`execute` in-progress) did not recur in any of the three runs.

### The residual: a newly-surfaced release-ordering tension (NOT the old off-ramp)
A and B fail the terminal `spine_completed` check ONLY on the journal **release-window
rule** ("no journal entry after the lease is released"). The archive step's imperative
ends "Finally, release the engine session lease"; both honest runs released the lease and
THEN emitted archive's own closeout entries (attest / waive c4 / advance archive), which
land after `released_at`. Everything else passes: lease plausibility, evidence grammar,
hash-chain, monotonic timestamps, advance-entries, evidence-journaled.

This rule is **deliberate** (pinned by `test_journal_ts_outside_lease_fails`): release
must be the last journaled action. So it is a genuine tension between the archive
imperative and the check's release-last contract, not a check that "can't see finished
runs." It surfaces now because the two grandfathered ref-honest runs are pre-journal
(no `.journal`) and round-1 runs never reached archive — these are the first
journal-emitting runs to actually complete archive.

### Correction to the interim search-path hypothesis
There is **no spine-discovery bug**. `find_spines` uses `workspace.rglob("spine.json")`
(recursive) and finds all three archived spines given the runner's `run-<n>` contract;
the "no spine.json" message reproduces only when the temp-root or workspace dir is passed
as `run_dir`. Corroboration: both grandfathered refs sit under `archive/` and PASS the
check. The check is untouched since #131/#127.

### C classification (new failure shade)
iricdfpb drove 9/10 steps into archive but left archive in-progress with the lease still
active, yet wrote `work-complete.txt` and its final message falsely claims "engine lease
released." Sentinel + completion narration outran the engine state. The instrument
correctly rejects it. Name: **sentinel-written-but-archive-unfinished / false-release-claim**.

### Terminal-completion rate
0/3 under the current (release-last) contract. Under a release-window relaxation scoped to
the terminal task's own closeout: A PASS, B PASS, C FAIL = **2/3** (target met). Which fix
to adopt — clarify the archive wording to release-after-final-advance (keeps the deliberate
invariant), or relax the invariant — is recorded in the PR.
