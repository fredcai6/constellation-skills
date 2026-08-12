# CONSTELLATION_FEEDBACK exports — governor-262

**No exports are due from this run**, and this file records *why* rather than being omitted, so the
trio is complete and the absence is auditable rather than looking like a dropped step.

## Verified, not assumed

```
$ py apply_lessons_delta.py --ripe --file <main checkout>/.agent-work/LESSONS.md
(no output — zero threshold-ripe lessons)
```

Zero threshold-ripe lessons means nothing was owed an APPLY, an EXPORT, a RESOLVE, or a DEFER at
this run's feedback step. The `c2` postcondition ("no threshold-ripe lesson left unpaid") is
therefore satisfied vacuously — there were none to pay.

## What this run contributed to the playbook instead

Three confirms and three adds, in `lessons-delta.json`, dry-run validated against the real durable
playbook:

```
$ py apply_lessons_delta.py lessons-delta.json --file <main checkout>/.agent-work/LESSONS.md --dry-run
DRY RUN — no write
confirmed lesson:verify-launch-order-claims-against-code (now 3)
confirmed lesson:verify-harness-field-and-drive-real-writer (now 6)
confirmed lesson:prove-command-fails-postcondition (now 1)
added lesson:name-scoped-test-filter-gates-are-strong-but-structurally-blind
added lesson:crew-blocked-on-a-commander-blocked-on-that-crew-has-no-exit
added lesson:sendmessage-name-in-the-launch-order-is-not-the-reachable-address
tick -> run 38
playbook: 19 active (cap 20, run 38)
recurrence-debt: 2 constellation lesson(s), 2 unfixed recurrence(s) — fix upstream, don't keep confirming
```

**The delta was NOT applied**, because applying it writes `.agent-work/LESSONS.md` in the main
checkout, which this run's launch order fences off. See `FENCE.md`. The Admiral applies it at
harvest.

## Two things worth the Admiral's eye at harvest

1. **The playbook is at 19 active against a cap of 20** once these three adds land. The next run to
   bank anything hits the cap. Each of my three adds carries a `bank_reason` naming what
   re-observation would clarify, so they are retire-able on evidence rather than on age — but the
   cap is close enough to be worth knowing before the next Commander tries to bank.
2. **The tool reports 2 unfixed recurrences** with the standing advice "fix upstream, don't keep
   confirming." I did not act on that: it is pre-existing recurrence debt, not this run's, and
   deciding what "fix upstream" means for those two is outside a single issue's scope. Flagging it
   rather than letting a second run walk past it silently.
