# Tripwires — issue #304 prose deletions (pre-registration)

**This file is committed BEFORE any deletion. That commit is the pre-registration.**

Git history is the tamper-evident timestamp. The episode store cannot carry a prediction: `create`
requires `observed-behavior` (so filing before the event means inventing an observation), and
`LIFECYCLE_STANDINGS` has no `confirmed` — a tripwire checked and **held** is indistinguishable from one
never checked (issue #342). So the prediction lives here, in a commit, and the episodes are filed
**afterwards** carrying a real `observed-behavior` that cites this commit.

Ratified by the Admiral as the amended rationale for `decision:tripwires-are-episodes`. The ruling
stands (episodes remain the destination); the original rationale — that the store already carries a
prediction and an outcome slot — is withdrawn as falsified by the code.

**Each prediction below is falsifiable and was written before the outcome was known.** A prediction that
fires is recorded as firing. That is the entire point of writing them first.

---

## T1 — deleting the dead-path block from `COMMANDER_SPINE.template.json` `tasks.context.imperative`

**Deleted:** the 86-word block beginning *"The checklist config_ref (docs/agents/engine-config.json) is
absent-by-design…"* through *"…rather than chasing the dead path."*

**Why it goes:** falsified. `docs/agents/` **exists in this repo** (it holds `ORCHESTRATOR_CONTEXT.md`),
so "a skill-source repo has no docs/agents/ overlay at all" is false on its face. And Charter ships a
task that **writes** `docs/agents/engine-config.json`, so "do NOT create the overlay file" contradicts a
sibling role's shipped deliverable (#336).

**Prediction:** no run behaviour changes. The engine's `load_config` already degrades a missing
`config_ref` to built-in defaults **mechanically**, with no reference to this prose. Removing it changes
what an agent *reads*, not what the engine *does*. Specifically: a Commander spine materialized after
the deletion will advance `context` exactly as before, and no test that pins the template will fail for
a reason other than the literal string being absent.

**Fires if:** any spine fails to advance `context`; any pinning test fails for a non-string reason; or
an agent, having lost this prose, creates `docs/agents/engine-config.json` during a run.

## T2 — deleting the same block from `EXECUTE_PLAN.template.json` `tasks.e0-context.imperative`

**Deleted:** the byte-parallel 86-word block.

**Prediction:** identical to T1, one level down. An `execute.json` instantiated from the template
advances `e0-context` unchanged.

**Fires if:** an execute plan fails to advance `e0-context`, or the two templates diverge in behaviour
after being edited in parallel.

## T3 — retargeting the pathless orientation imperatives

**Changed, not deleted:** `tasks.context.imperative`'s *"Read the current map (packets, overlays,
decision anchors) for the area the ask touches…"* and `tasks.plan.imperative`'s *"Map-first: BEFORE
authoring execute.json, produce a mission frame from the current map…"* are retargeted at the resolved
map input instead of an unnamed "current map".

**Prediction — and this is the one I expect to be least comfortable.** Behaviour changes in the
*degraded* case only, and it changes to REPORTING rather than silence: a run in a repo with no
`docs/architecture/` will now be refused at `context` until it records substitutes, an unmapped gap, and
an escalation. In a repo **with** a map, I predict **no measurable ordering change**, because the
baseline says agents already read the map — 4 of 4 returned to it, 4 of 5 cited it — just **late**.

**Fires if:** a mapped repo shows changed orientation ordering attributable to this edit (which would
mean I mis-analysed the baseline), **or** a degraded run is refused in a way that blocks legitimate
work rather than merely recording the gap.

**Honest-null note:** T3 predicting "no ordering change in mapped repos" is a prediction that the
contract does **not** fix the measured defect. That is deliberate and it is the epic's own finding, not
a hedge. If the null holds, it is a successful measured negative, reported as such.

## T4 — the load-bearing occurrence that must SURVIVE

**Not deleted, and this is a tripwire against my own edit.** The phrase `"no docs/agents/ overlay at
all"` occurs **twice** in `tasks.context.imperative`. The **first** occurrence is the
substitute-and-record rule:

> *"Where the repo carries no docs/agents/ overlay at all (e.g. a skill-source repo), substitute the
> closest repo doctrine you can find (README, CONTRIBUTING, top-level docs) and record the substitution"*

That rule is correct, load-bearing, and is the degraded-mode intake this issue is trying to
**strengthen**. Only the **second** occurrence — inside the dead-path block — is falsified.

**Prediction:** a naive string-level deletion removes both and silently strips degraded-mode intake from
the Commander spine while appearing to remove only dead prose. The cold critic caught this before any
edit was made.

**Fires if:** after the deletion, the substitute-and-record rule is absent from the imperative. A test
asserting its **presence** ships alongside the tests asserting the dead prose's absence — the deletion
is pinned in both directions.


## T5 — the anchor change (added after PRE-B, pre-registered before it is made)

**Changed:** `tasks.context.imperative` is re-anchored from *"Read the current map ... for the area the
ask touches"* to **"Before you open any source file, resolve and read the map input."**

**Why:** PRE-B measured five runs with verified Commander loads. Both pathless imperatives fired in every
run and orientation moved not at all — `map_before_src` false on 4 of 4 runs that read source. The
measured diagnosis: *"a map-first imperative anchored to a late artifact is not a map-first imperative."*
The served plan imperative (`:40` at `74953936`) anchors to *"BEFORE authoring execute.json"*, which
happens at the END of a run — so crawling fifty calls, then reading the map, then authoring the frame is
**exact compliance**. Run #698 read source at call 25 and the map at call 57 and satisfied it.

**Prediction — and this one I genuinely do not know the answer to.** Anchoring at `context` to *"before
you open any source file"* is the **untested variable**. I predict it does **not**, on its own, move
`map_before_src`, because it remains prose with no preventive enforcement and the corpus cannot own a
`PreToolUse` hook. But I predict it is **strictly better positioned** than the late anchor, because
`context` precedes `understand` and `plan` in the spine, so the instruction now sits before exploration
rather than after it.

**Fires if:** POST shows orientation unchanged AND the anchor is shown to be irrelevant to that (i.e.
the late-vs-early anchor makes no difference), which would mean the anchor hypothesis is wrong rather
than merely insufficient.

**Distinguishing the two outcomes matters more than the outcome.** "Insufficient" (prose can't enforce
ordering) and "irrelevant" (the anchor location doesn't matter) are different findings with different
consequences, and POST must be able to tell them apart. If it cannot, that is a measurement gap to
report, not a result to round off.

---

## Outcome recording

Outcomes go to `.agent-work/issue-304/TRIPWIRE_OUTCOMES.md`, then into `episodes/active/` via
`scripts/apply_episode_delta.py` (the only write path), each episode carrying `expected-behavior` = the
prediction above and `observed-behavior` = what actually happened, citing this file's commit SHA.

**A tripwire that fires is recorded as firing.** The launch order is explicit: *"If a tripwire fires
against you, record it against the tripwire rather than explaining it away — that is the entire point of
filing predictions before deleting."*
