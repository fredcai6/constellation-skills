# Doctrine prose asserts facts owned by the commander spine, with nothing tying the two together

Measured at gate `g4-review` of `567-d1`, reviewing the #596 disposition.

#596 happened because three doctrine sites claimed the `feedback` gate enforced a
`CONSTELLATION_FEEDBACK.md` export. The gate never did. Its postcondition set, read at
`skills/commander/templates/COMMANDER_SPINE.template.json` and quoted here from the tree:

```
feedback.postconditions == [c1] -> command: verify_episode_captured.py <work-id> --store-root episodes --phase feedback
```

One postcondition, one check, no mention of any export. The cost is on the record: on 2026-08-15 a
lane and the Admiral each did the right thing by the stale doctrine and produced work that had to be
reverted.

Gate `g4` corrected all three sites, and the correction verifies. **The coupling that let them go
stale is unchanged.** The blast radius of one edit to the spine's postconditions is currently:

```
skills/commander-delegated/SKILL.md          — asserts the gate's single postcondition
skills/admiral/SKILL.md                      — asserts "No commander gate writes one"
skills/admiral/references/fleet-doctrine.md  — asserts the same
tests/data/store_mentions.approved.txt       — two entries keyed line-for-line to the first two
```

Five files, none of which any check connects to `COMMANDER_SPINE.template.json`. Move the spine's
postconditions again and all three prose sites go stale silently, in exactly the shape #596 names.
The approval census does not help: it pins the prose to *itself*, so a wrong-but-stable claim stays
approved indefinitely.

**Candidate work:** a check that reads the spine template's real postcondition set and fails when a
doctrine site's claim about it no longer holds — the `two-bin rule` applied to these claims
(`docs/agents/GLOSSARY.md`: every enforced invariant is either checked by a command or attested by a
named human; prose alone enforces nothing). Today these claims are in neither bin.

**Not acted on at `g4`:** the change under review is correct and complete for today's tree, so this
is not a blocker. Closing the coupling needs either new tooling or a rule in `docs/agents/*`, and
`docs/agents/*` promotion is explicitly the human's call under this lane's standing constraints.
Recorded for routing at epic closeout, per the human's *"we've been ballooning out tracking."*
