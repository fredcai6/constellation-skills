# Constellation feedback — lane K, #634 (staged; see FENCE.md)

Delegated Commander, epic #567 wave 3, Opus, crews Sonnet. Branch
`feat/567-k-one-spine-mutable-middle`, PR #635.

## How closely the skills, handoffs and checklists were followed

Closely, with one contradiction I could not follow my way out of and did not try to. Every spine
step was driven through the engine; `execute.json` was driven gate by gate; `recover_crews.py` ran
before every dispatch; every crew went through `run_crew.py` with an explicit `--model sonnet`.

**The contradiction:** the `plan` step *mandates* authoring `execute.json` — a second checklist
file, driven off the door under a session id the agent invents. That is the exact defect #634
exists to remove. So the run performed the defect it was sent to fix, under instruction. I
followed the instruction rather than improvising around it, and recorded it as first-hand evidence
instead of treating it as an annoyance. By the end the engine could support the alternative, and
the run demonstrated it on a copy — a Commander at `plan` amending its three work gates directly
into its own spine's middle. The mechanism is now ahead of the doctrine.

## Where I had to improvise or work around instructions

- **`run_crew.py --verify-result` could not verify a handoff-only crew.** It refused with
  *"no spine evidence and no `--accept-mtime-only-risk` given"*, because the dispatch had no
  `--spine` and mtime alone was judged insufficient. Rather than pass the risk flag, I verified by
  **re-running the crew's work myself** — re-ran its tests and independently reproduced all four
  behaviours. That is stronger than the documented check, but the documented check did not fit the
  dispatch shape the same doctrine told me to use for a non-spine crew.
- **`map_orient.py verify-frame` refused a frame it should not have.** The mission-frame template
  asks for `decision:` anchors; under a DEGRADED orientation *any* `<kind>:<id>` token is refused,
  because nothing can resolve. I had written the launch order's **pre-rulings** using that
  grammar. The honest fix was relabelling them `ruling:` — they are launch-order rulings, not map
  anchors, and calling them `decision:` was a category error of mine. Worth noting for others:
  under a degraded orientation the check passes only for a frame citing **zero** map anchors, so
  "FRAME-OK" there means "cited no map", not "cited the map well".
- **The episode delta's shape had to be discovered by failing.** Five successive refusals —
  `work_id`, `mechanical`, assertion-payload-must-be-object, `strength`, then
  `amend-assertion` vs `restate-assertion` — each surfaced one field at a time. The refusals were
  clear individually, but the template in the skill directory does not show the create-op shape,
  so the shape came from reading the writer's source. `restate-assertion` (wording) vs
  `amend-assertion` (standing + history) is a real and correct distinction that nothing pointed me
  to.

## What was ambiguous, missing, or contradictory

- **The file-ownership grant did not cover the work the settled ruling required.**
  `decision:every-planning-role` is `settled/human` and names crew. Crew's plan is
  `IMPLEMENTER_PLAN.template.json`, which does not match the granted pattern
  (`*SPINE*.template.json`), and it is compiled by `scripts/generate_spine.py`, which is in
  **neither lane's** grant nor either fence. A settled human ruling was therefore unreachable from
  the lane assigned to deliver it. This is the single most useful thing to fix before the next
  wave: check that a lane's grant actually covers its rulings.
- **`docs/agents/engine-config.json` is named by the `context` imperative and does not exist** in
  this repo. Handled by substitution and recorded, but it is named as though guaranteed.
- **The map is absent, not merely degraded.** `map/ids.jsonl` is 0 bytes and `map/INDEX.md` links
  to per-module files that do not exist, while `map/INDEX.md` is simultaneously fenced to the
  Admiral. So every lane must declare a degraded reading and none may repair it.

## What would have helped

- **A named tier for "helper agents that are not implementer or reviewer".** The design candidates
  and the plan critic are first-class doctrine requirements (design-it-twice, cold critic) but have
  no dispatch shape of their own, so they ride `run_crew.py` with an invented `--role` and then
  fall outside `--verify-result`'s contract.
- **Naming `TemplateOnlyFieldAllowlist` (#475) in the handoff for any new template-only field.**
  The g2 crew rediscovered it unaided. I would not have known to name it — I had it wrong, and had
  drafted a triage candidate asserting the field was invisible to the suite. It was not; the crew's
  Workflow Feedback is what corrected me. That is the concrete argument for harvesting crew
  feedback rather than skimming it.

## Crew workflow feedback, harvested

- **g1 implementer:** no handoff gaps. Noted that the handoff left it free to derive the ceiling
  arithmetic rather than copy design-B's formula — which mattered, because **the formula was
  wrong** (`max(indices) + 1` permits the append-past-`archive` case B's own prose forbids). Asked
  that such latitude be stated explicitly, since a less careful reader would copy the formula.
- **g2 implementer:** no handoff gaps. Rediscovered `TemplateOnlyFieldAllowlist` (#475); suggested
  naming it up front for template-only-field work, mirroring the `generate_spine.py` durability
  note the handoff already carried.
- **g1 reviewer:** the handoff's differential-testing hint ("verify against the real base rather
  than by reasoning about it") changed its method — its first instinct was to reason from the
  diff, which would have under-verified backward compatibility.
- **g2 reviewer:** its first restore attempt after a red-proof used `git checkout --`, which
  reverted to pre-diff HEAD rather than the implementer's working-tree state. Caught immediately
  and restored from its own backup. A red-proof needs a stated restore procedure, not just a
  "restore afterwards" instruction.

## My own mistakes

Recorded in full in the return (§9) and in the episodes. In short: I mis-scoped my own gate plan
onto a file I was never granted; I authored a proof gate whose postconditions were `check: null`
and therefore could not fail; I silently closed a question my own comparison had called open; I got
the ceiling formula wrong in my own handoff; one of my verification commands was wrong and I
initially read it as a code failure; and I drafted a triage candidate on an unverified claim about
the test suite. **Three of those six were caught by a crew or a critic rather than by me**, which
is the strongest thing I can say for the independent-reviewer premise.
