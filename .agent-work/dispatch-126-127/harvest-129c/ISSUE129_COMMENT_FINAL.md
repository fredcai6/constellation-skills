## Clean terminal-completion measurement — the fix drives sonnet 3/3 to terminal archive

The clean measurement rounds 1–2 never got is now in hand (reap-safe runner, one run per
invocation, an independent wall-clock watch replacing the unreliable completion signal).
euler-1-multiples, sonnet (`claude-sonnet-4-5`), hardened+journal checks, kept temp dirs,
all command-verified. **Terminal completion = spine driven to a terminal `archive` with
genuine engine provenance (lease + consistent journal) + `work-complete.txt`.**

### Cumulative table (per-run classification)

| round | run | reached | terminal? | classification |
|---|---|---|---|---|
| 1 (pre-round-2 clause, #128) | ×3 | execute in-progress | 0/3 | quit-early ("implementation complete") |
| 2 (round-2 "MIDDLE not the end", as shipped) | A `6lcnbis9` | archive 10/10 | no | near-terminal — release-ordering fail |
| 2 | B `g6o67i9t` | archive 10/10 | no | near-terminal — release-ordering fail |
| 2 | C `iricdfpb` | archive 9/10 | no | completion theater at the finish (sentinel + false "lease released" claim, archive left in-progress) |
| 3a (ordering fix, pre-wait-loop) | D `ir02q8l0` | execute 4/10 | no | **wait-by-ending-turn** (dispatched crew, ended turn to wait → headless death) |
| 3a | E `rwtnxyih` | execute 4/10 | no | quit-early recurrence |
| 3b (ordering + wait-loop fix) | G `4yqedpsu` | **archive 10/10** | **YES** | terminal — release after final advance, journal consistent (52) |
| 3b | H `h3bten13` | **archive 10/10** | **YES** | terminal — journal consistent (50) |
| 3b | I `d4clr3hp` | **archive 10/10** | **YES** | terminal — 0 post-release entries, `advance archive` then release |

**Round 3b: 3/3 terminal.** Target (≥2/3) met and exceeded, against the UNCHANGED strict
instrument.

### What round-2 wording actually did, and the two residual off-ramps it exposed
Round-2's "solution is the MIDDLE, not the end" clause **closed #129's original off-ramp**:
in round 2, A and B drove the full reconcile→triage→review→feedback→archive tail instead of
stopping at green tests. But the clean read exposed two narrower failures the earlier
runner-deaths had hidden:

1. **Release-ordering** (round-2 A/B). The archive imperative ended "Finally, release the
   lease," so honest runs released and THEN emitted archive's own closeout entries
   (attest/waive/advance), landing after `released_at`. The terminal check's journal rule —
   deliberately (`test_journal_ts_outside_lease_fails`) — requires release to be the last
   journaled action. Honest runs failed the check *because they finished*.
2. **Wait-by-ending-turn** (round-3a D). A commander that dispatches a crew and ends its
   turn to "wait" simply dies mid-`execute` in headless mode.

### Fix (this PR) — wording only; instrument unchanged and fully strict
- Reordered the archive imperative to **release-after-final-advance** (advance archive to
  complete, then release as the very last action) in the ONE shared spine template
  `skills/commander/templates/COMMANDER_SPINE.template.json` (both human and delegated
  commander drive from it), and mirrored the ordering clause in
  `skills/commander-delegated/SKILL.md` step 4.
- Added a **wait-loop clause** (`SKILL.md` step 5): dispatching a crew is never a reason to
  end your turn; wait actively by polling the result, never by yielding.

### Correction: there is NO spine-discovery bug
An interim hypothesis that the check misses `archive/` was a misdiagnosis. `find_spines`
uses recursive `rglob` and finds archived spines given the runner's `run-<n>` contract; the
"no spine.json" message reproduces only when the wrong dir is passed. Both grandfathered
ref-honest spines sit under `archive/` and PASS. The check is untouched since #131/#127.
The earlier release-window "bug" is not a bug — it is a deliberate invariant, and the
doctrine now matches it (release is the true final act).

### Notes
- No regrade: the instrument is unchanged, so round-2's failures stand as correct; round-3b
  is a fresh re-measurement with the fix (not a re-scoring of old workspaces).
- Round-1 comparability holds: those runs never reached archive, so neither the
  release-window rule nor this fix could have affected their verdicts.
- Round-3b mixes the ordering + wait-loop wording; attribution between them is not the
  question — D (ordering fix alone) died at the crew-wait hazard, so the wait-loop clause
  was needed to reach archive, and the ordering clause was needed to pass there. Together: 3/3.
