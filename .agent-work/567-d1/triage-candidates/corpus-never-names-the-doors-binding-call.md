# Triage candidate — after the sweep, the corpus never names the door's binding call

**Found at:** `g2-review`, lane D1, epic #567 wave 2. Reported by the g2 reviewer as `tc1`, and
recorded as the one `fail` on an otherwise-APPROVE survey, under an explicit `--override-reason`
rather than a downgrade.

**What was found.** The sweep removed the CLI clause from the three second-checklist sites and
replaced it with the measured truth. What the removed clause also used to carry, incidentally, was
**the first move**: how an agent gets a door pointed at a checklist in the first place.

Measured: `grep 'spine_open\|spine_bind'` over `skills/` excluding `skills/workbench/` returns
**zero hits**. The single corpus mention is `skills/workbench/references/checklist-engine.md:34` —
**lane D2's file** — and it documents only `spine_open` (mint a new spine), never `spine_bind`
(adopt an existing one), which is the case these three sites are actually in.

**Nobody is stranded, and this is why it is a candidate rather than a blocker.** The door's own
refusal carries its remedy:

> *"REFUSED: no spine is bound to this door … Call `spine_bind` with the path to a spine that
> already exists, or `spine_open` to mint a spine and bind this process to it."*

That is `global-everyone.md`'s *"fail visibly rather than emit plausible wrong output; no hidden
fallback"* working exactly as designed. An agent that reaches for the door learns the move from the
refusal. What is lost is that the corpus no longer teaches it in advance.

**The sharper form of the same gap, and it needs a deliberate answer rather than a discovery.**
Lane D2 deletes `skills/workbench/SKILL.md` and `skills/workbench/references/checklist-engine.md`.
After that merge, **no file in the corpus will tell an in-session crew member how to drive its own
plan or survey** — and the door provably cannot reach a second checklist, so there is no door answer
to substitute. That is the epic-level consequence of the Admiral's F-1 measurement. The g2 reviewer
is itself an instance: it drove its own survey through the engine using knowledge it read from the
not-yet-swept workbench reference.

**Why it is a candidate and not a fix here.** The natural home for half of it is
`skills/workbench/references/checklist-engine.md`, which is lane D2's fenced file this wave, and the
other half is an epic-level scope call about what replaces that reference once it is gone.

**Carried forward within this lane:** confirmed deliberately at `g5-final` against the rebased tree,
so it is met as a measured fact rather than as a surprise.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run`.
