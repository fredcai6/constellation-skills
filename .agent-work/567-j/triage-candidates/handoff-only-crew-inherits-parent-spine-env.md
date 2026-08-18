# Triage candidate: a handoff-only crew (no `--spine`) inherits the parent's live SPINE_FILE/SPINE_SESSION

**Found at:** two independent crews this wave — g1-review (reviewer) and
g2-implement (implementer) — both flagged the identical shape unprompted in
their own Workflow Feedback.

**What happened:** `run_crew.py` dispatched both crews with `--handoff`/
`--result` and **no** `--spine` (the correct shape for a crew whose job is a
document-described task, not a spine-driven one). Neither crew's own
`crew-runs.json` entry records a `spine` (both show `"spine": null`). But the
spawned child process's environment still carried the **parent Commander's**
live `SPINE_FILE`/`SPINE_SESSION` (`constellation/567-j/lane-j/commander-delegated`)
unchanged, because nothing clears those variables for a handoff-only dispatch.

Both crews independently discovered this only after calling `spine_status`
(or attempting `spine_bind`) and getting back the **Commander's own gate
content** instead of a "no spine bound" refusal. One crew's attempted
`spine_bind` to its own authored plan was correctly refused by the door,
because doing so would have released the Commander's real, live lease out
from under it. Both crews recovered correctly by falling back to driving
their own `IMPLEMENTER_PLAN.json`/`REVIEW_SURVEY.json` through
`checklist_engine.py`'s CLI directly, never touching the parent's spine — but
both had to rediscover this workaround from first principles, and a subagent
that did NOT know the "never drive an inherited spine" rule (this exact
shape is why that rule exists — see prior-session memory `crew-dispatch-spine-null`)
could plausibly have started driving the Commander's own live spine, exactly
the failure mode a previous wave observed with a probe agent and a
journal-read session id.

**Why it matters:** this is not a one-off — it reproduced identically on two
separate crew dispatches in the same run, each arriving independently at the
same recovery. The failure mode it risks (a subagent discovering and driving
its dispatcher's own live spine) is severe enough that a prior wave already
named it as an incident.

**Recommendation (not mine to decide or file):** `run_crew.py`'s cli-backend
dispatch should unset/clear `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` in a
dispatched child's environment whenever the dispatch is handoff-only (no
`--spine` given), rather than leaving the parent's identity ambiently
reachable. That would make `spine_status`'s "no spine is bound to this door"
refusal fire immediately and correctly for the common case, instead of a
crew discovering the mismatch only after reading spine content that clearly
belongs to a different role/gate.

**Disposition:** staged only, per `decision:no-issue-filing-mid-run`. Filed
nowhere; the human or Admiral routes this from here.
