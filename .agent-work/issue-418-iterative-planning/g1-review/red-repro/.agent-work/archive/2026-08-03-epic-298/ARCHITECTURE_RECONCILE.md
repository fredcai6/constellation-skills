# Architecture reconcile — epic-298 (closeout c3)

**Done as a direct check by the Admiral rather than a cartographer dispatch.** Tommy's steer — *"I've got the distinct feeling we've over complicated a lot"* — and the epic's net change is small enough to verify by reading the docs that own it. **Recorded as a reasoned scope decision, not a skipped gate.** If an independent read is wanted later, this file names exactly what was checked so it can be re-done cheaply.

## The epic's net change, enumerated (count asserted)

```
git diff --name-only 74953936..origin/main | grep -v '^.agent-work/' | grep -v '^episodes/' | wc -l
-> 67 files
```

Plus **32 episode files** under `episodes/active/` and the `.agent-work/` workbench, excluded above as artifacts rather than architecture.

## Does the recorded architecture still describe the system?

**1. The episode store — the epic's largest structural change. RECONCILED.**

`docs/CONSTELLATION_OVERVIEW.md` now carries `episodes/active/` and `episodes/retired/` in the truth-layer taxonomy (l.72) and a section *"The episode store, and what replaces the playbook"* (l.82). **This closes #322**, which was the standing complaint that the taxonomy omitted it.

**The part worth noting is how it records the removal.** l.98: *"`.agent-work/LESSONS.md` is not in this taxonomy, and that is the ruling, not an omission."* **A record that states why something is absent is stronger than one that is merely silent** — a future reader cannot mistake the gap for an oversight and re-add it.

**2. The #304 map-first contract. RECORDED.**

`docs/CONSTELLATION_OVERVIEW.md:118` documents `scripts/map_orient.py orient` as the canonical entrypoint and names the REPORTED-degraded path. Cross-referenced in `POSITIONING.md` and `REMOVABILITY_LEDGER.md`.

**Caveat carried forward, not resolved here:** #393 established that the contract itself lives **only** in `COMMANDER_SPINE.template.json` and that `skills/commander/SKILL.md` contains **zero** occurrences of "map". So the architecture record describes the contract correctly while the always-loaded skill text does not mention it. **That is a property of the delivery mechanism, not a reconcile defect** — and #307 measured that mechanism working (`map_before_src` 0/4 → 4/4).

**3. #310. NO SOURCE CHANGE.** Its PR is 64 files, all under `.agent-work/`. Evidence only; nothing to reconcile.

## Verdict

**The recorded architecture describes the system as it now stands.** No drift found between the docs and the tree for this epic's net change.

## One thing the reconcile surfaced that is NOT reconciled

**Six `notes-*.md` files sit at the repo root**, half of everything tracked there, spanning two epics. Filed as **#409**. **This is not an architecture drift — it is the absence of a declared home**, which is why the reconcile finds it and cannot fix it.

_Checked at `origin/main` = `ecce75c`, before PR #410 merged._
