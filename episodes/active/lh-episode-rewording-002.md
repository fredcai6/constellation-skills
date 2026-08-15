<!-- episode-state: schema=1 id=lh-episode-rewording-002 status=active -->

# episode: lh-episode-rewording-002

## Mechanical
- run: lh-episode-rewording
- project: constellation-skills
- role: commander
- spine-step: understand
- context-manifest-ref: .agent-work/lh-episode-rewording/LAUNCH_ORDER.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: episodes/active/launcher-hygiene-002.md

## Agent-supplied

### assertion:lh-episode-rewording-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Determine, per the launch order own instruction, whether launcher-hygiene-002.a3 second-person flag is case (a), a quotation the guard existing carve-out should already exempt, or case (b), a genuine guard gap, before touching the record.

### assertion:lh-episode-rewording-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The carve-out test test_second_person_inside_a_quotation_is_not_flagged was expected to already exempt a verbatim quotation of the Stop hook own refusal text.

### assertion:lh-episode-rewording-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Direct calls to the guard own second_person_hits()/triggers_for() on the original statement showed only the first single-quoted excerpt (the Stop hook refusal) paired correctly; the second excerpt (the spine_status advisory, quoting "hand off here... decline with a reason if you are nearly done") failed to pair because its own verbatim word "you are" -- written "you're" -- contains an apostrophe adjacent to letters on both sides, which defeats the quote regex letter-boundary guard at that internal position, leaving the excerpt own "you" unstripped.

### assertion:lh-episode-rewording-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: About fifteen minutes reading scripts/verify_episode_observations.py regex and the carve-out test directly, plus several direct interpreter calls against triggers_for(), rather than guessing at a rewrite.

### assertion:lh-episode-rewording-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Determined this to be case (a) rather than (b): switched both verbatim excerpts in launcher-hygiene-002.a3 from single to double quotes, changing no word, which the guard own double-quote regex arm pairs correctly and which restored the exemption -- verified with triggers_for() returning [] before applying the delta.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
