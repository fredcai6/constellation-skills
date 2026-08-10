# Drill: symmetric-recovery-refresh

- **Lesson / doctrine under test:** the uniform reach-up mechanism — `skills/_shared/global-everyone.md`
  §reach-up, `skills/_shared/global-orchestrator.md` §idle-subagent-adjudication, `skills/workbench/references/checklist-engine.md`
  §refresh (issue #183, built on #179's merged `checklist_engine.py` primitives).
- **What this drill exercises:** that an intentional refresh and a simulated crash resume from the
  **identical** `current` read, and that a fresh agent given only that text can continue **without
  re-deriving** the understanding the `why_trail` already holds.
- **Acceptance is a qualitative human judge, not a unit test** (spec TF4) — this drill exists to make that
  judgment **reproducible and cheap**, not to render the verdict itself. Everything below through "Human
  verdict" is fixtures and a real, reproduced transcript; nothing past that point has been declared
  pass/fail by the agent that built this drill.

## Fixtures

Two small `gated` checklists, identical except for one evidence item:

- `docs/examples/symmetric-recovery-refresh.json` — the **intentional-refresh** case. `g1-design-backoff`
  is `complete` with a `why_trail` entry (`w-1`) recording a concrete design rationale; `g2-implement-helper`
  is `in-progress` (the active gate) and carries an attached `refresh-request` (`seam:
  g2-implement-helper`, `why_ref: w-1`).
- `docs/examples/symmetric-recovery-crash.json` — the **crash** case. Byte-identical except the
  `refresh-request` evidence item is absent (the agent died before it ever got the chance to file it).

Both were produced by actually driving the merged engine (`scripts/checklist_engine.py`, #179) through a
real `start` → `advance --why "..."` → `start` sequence, then branching one copy to `attach` the
`refresh-request`; neither file was hand-authored past that point. Reproduce the fixtures yourself:

```
py scripts/checklist_engine.py --file <tmp>/spine.json current                                    # ACTIVE g1-design-backoff [pending]
py scripts/checklist_engine.py --file <tmp>/spine.json start g1-design-backoff
py scripts/checklist_engine.py --file <tmp>/spine.json advance g1-design-backoff --why "chose exponential backoff with jitter (cap 30s) over fixed-delay retry: the upstream API only sometimes returns Retry-After on 429, and fixed-delay caused synchronized thundering-herd reconnects across workers on the days it did not"
py scripts/checklist_engine.py --file <tmp>/spine.json start g2-implement-helper
cp <tmp>/spine.json docs/examples/symmetric-recovery-crash.json
py scripts/checklist_engine.py --file <tmp>/spine.json attach g2-implement-helper --type refresh-request --field seam=g2-implement-helper --field why_ref=w-1
cp <tmp>/spine.json docs/examples/symmetric-recovery-refresh.json
```

## Run it — the two `current` reads (verbatim, reproduced from the checked-in fixtures)

```
$ py scripts/checklist_engine.py --file docs/examples/symmetric-recovery-crash.json current
ACTIVE g2-implement-helper [in-progress] — Implement the retry helper per the chosen backoff strategy.
DIGEST: chose exponential backoff with jitter (cap 30s) over fixed-delay retry: the upstream API only
sometimes returns Retry-After on 429, and fixed-delay caused synchronized thundering-herd reconnects
across workers on the days it did not
```

```
$ py scripts/checklist_engine.py --file docs/examples/symmetric-recovery-refresh.json current
ACTIVE g2-implement-helper [in-progress] — Implement the retry helper per the chosen backoff strategy.
DIGEST: chose exponential backoff with jitter (cap 30s) over fixed-delay retry: the upstream API only
sometimes returns Retry-After on 429, and fixed-delay caused synchronized thundering-herd reconnects
across workers on the days it did not
REFRESH REQUESTED: g2-implement-helper (why_ref w-1)
```

`diff` between the two source files is exactly one JSON evidence object — the attached `refresh-request` —
nothing else differs. That is the symmetric-recovery claim made concrete: the crash arm is the refresh arm
minus the one thing a dead agent never got to write.

**Fulfilment, for reference** (not part of the acceptance judgment, but real and reproducible): advancing
`g2-implement-helper` on the refresh fixture with a fresh `--why` completes the gate, `active_id` moves past
it, and the very next `current` shows `DONE: no open items.` with the updated `DIGEST:` and **no**
`REFRESH REQUESTED:` line — the request clears itself the moment the tripped gate is finished, with no
evidence mutation. (`skills/workbench/references/checklist-engine.md` §refresh documents this and its known
granularity gap.)

## The human's drill — hand this to a fresh agent

Pick either fixture (they read identically past the DIGEST — that symmetry is the point) and open a **brand
new** session/subagent with **no other context about this task**. Give it exactly this prompt, nothing more:

> You are continuing checklist work already in progress. Run:
> `python scripts/checklist_engine.py --file docs/examples/symmetric-recovery-refresh.json current`
> (or the `-crash.json` fixture) and drive the active gate to completion per the engine's instructions. Do
> not ask what happened before this point — the output of `current` is the only briefing you get.

Watch what it does at `g2-implement-helper`. It has no access to why g1 was decided the way it was beyond
the `DIGEST:` line.

## Rubric for the human's qualitative sign-off

- **Resumed cleanly (pass signal):** the fresh agent proceeds straight to implementing the retry helper
  consistent with the DIGEST (exponential backoff, jitter, 30s cap) and, when it advances `g2`, its `--why`
  builds on that decision (e.g. references "the backoff strategy above") rather than re-litigating it.
- **Re-derived instead of resumed (fail signal):** the fresh agent asks a clarifying question about *why*
  backoff-with-jitter was chosen, proposes re-deciding the strategy from scratch, or otherwise treats the
  DIGEST as insufficient context — evidence that `current` alone is not actually carrying enough to resume
  on, contrary to the spec's premise.
- **Symmetry check:** run both fixtures through separate fresh agents (or the same agent twice, in separate
  sessions). Their behavior at `g2` should be indistinguishable except that the refresh-fixture agent may
  also notice and act on the `REFRESH REQUESTED:` line (e.g. treat it as confirmation it was deliberately
  handed off, not just picked up mid-stream) — the crash-fixture agent has no such line and should still
  resume identically well from the DIGEST alone.

## Human verdict

*(left blank — the human or their delegated reviewer records the judgment here; the agent that built this
drill does not self-certify it, per the launch order for #183)*

- Resumed cleanly / re-derived: ****\_\_\_****
- Symmetry held: ****\_\_\_****
- Notes:
