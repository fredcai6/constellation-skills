# `CONSTELLATION_FEEDBACK.template.md` still claims a writer that no gate contains

`skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md:4` says the export is

> "Appended by the feedback/closeout steps; swept by the skills repo's `collect_feedback.py`"

The second half is true — `docs/DEBT_SWEEP_CADENCE.md` and `skills/admiral/SKILL.md:94` both run that
sweep. The first half is not. Measured at gate `g4` of `567-d1`:

```
$ grep -c 'CONSTELLATION_FEEDBACK' skills/commander/references/commander-core.md \
      skills/commander/templates/COMMANDER_SPINE.template.json \
      skills/admiral/templates/ADMIRAL_SPINE.template.json skills/commander/SKILL.md
skills/commander/references/commander-core.md:0
skills/commander/templates/COMMANDER_SPINE.template.json:1   # the archive c4 DENY-glob
skills/admiral/templates/ADMIRAL_SPINE.template.json:0
skills/commander/SKILL.md:0
```

No feedback or closeout step appends it. The `feedback` gate's single postcondition is
`verify_episode_captured.py`; `archive` `c4` deny-globs the file out of the commit.

Gate `g4` reconciled the three *collector*-side sites (`skills/admiral/SKILL.md:96`,
`skills/admiral/references/fleet-doctrine.md:160-173`, `skills/commander-delegated/SKILL.md:22`) to
say the export is collected only where one exists. This is the matching *producer*-side sentence, and
it is the last live claim that something writes one.

**Not acted on:** `skills/workbench/**` is fenced to lane D2 by this lane's launch order. Either the
sentence is corrected to name who actually writes an export (a Commander running in a consuming
project, by hand), or a step is given the job — and choosing between those is a doctrine call, not a
wording fix. Recorded for routing at epic closeout.
