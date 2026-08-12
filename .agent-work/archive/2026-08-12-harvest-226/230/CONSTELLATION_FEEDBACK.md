# Constellation Feedback — exported from `issue-230`

Constellation-scoped signal: defects/gaps in the **shared machinery** (the engine, the role skills, the templates), not in this project. Exported rather than silently worked around, per the recursive-improvement contract.

---

## `2026-07-25` — `issue-230` (epic-226 item D)

### 1. `current` does not distinguish attestable from engine-checked postconditions

**Machinery:** `scripts/checklist_engine.py`

The engine correctly refuses `attest` on a `command`-kind postcondition (`REFUSED: p2 is engine-checked; cannot attest`) — that refusal is right and should stay. The gap is **discoverability**: the `current` verb prints the imperative but not the shape of each postcondition, so an agent cannot tell which conditions it should `attest` and which are satisfied only by `advance` re-running the check. Every gate costs one refused call to find out, and the agent has to read the raw spine JSON to plan ahead.

**Suggested fix:** have `current` (or a `--conditions` flag) list each unmet pre/postcondition with its check kind — `c1 [attestable]`, `c2 [command: py -m pytest tests/ -q]`. Cheap, and it removes a per-gate stumble that every commander run pays.

Note this is adjacent to but distinct from `issue-141`'s already-logged entry (that one was "null preconditions need an explicit attest at all"); this is "you cannot tell which ones those are without reading the JSON."

### 2. Reviewer handoff template lacks a `Survey State Location:` field

**Machinery:** `skills/commander/templates/REVIEWER_HANDOFF.template.md`

The reviewer crew reported having to infer the survey-file convention (`.agent-work/<work-id>/<gate>-review/review.json`) from the reviewer skill's prose rather than reading it off the handoff. It worked, but it is rediscovered context on every review gate. The reviewer skill's own docs describe such a field; the template does not carry one.

**Suggested fix:** add a literal `**Survey state:** <path>` line to the handoff template's header block.

### 3. The consolidation guard's `--override-reason` path is under-documented

**Machinery:** `scripts/checklist_engine.py` consolidation guard + `constellation-reviewer`

The reviewer hit the guard refusing `APPROVE` while any survey item is `fail`, and used `--override-reason` to carry two genuine-but-non-blocking findings through to an APPROVE rather than either suppressing them (dishonest) or blocking a compliant PR over a narrow edge case (disproportionate). It reported this as **first-time use** and was unsure whether it was the sanctioned path.

It is exactly the right use — a non-blocking finding surfaced honestly instead of hidden — but the reviewer doctrine does not say so. **Suggested fix:** name this case explicitly in the reviewer skill: a `fail` item that is real but non-blocking consolidates to APPROVE *with* an override reason; suppressing the item is the failure mode the guard exists to prevent.

### 4. Launch-order stop conditions should be qualified by canonical routing

**Machinery:** `skills/admiral/templates/LAUNCH_ORDER.template.md`

A stop-and-float condition of the form "float if another wave's PR touches this file" can fire on an edit that a canonical-source rule (PR-6) makes unnecessary. In this run, routing cross-role doctrine to `skills/_shared/global-everyone.md` dissolved the contended `commander-core.md` edit entirely — no merge order had to be guessed, and a full Admiral round-trip was avoided.

**Suggested fix:** in the launch-order template's stop-conditions guidance, qualify file-collision stops with "…if the edit is still required after resolving the canonical target." See `lessons-delta.json` op `canonical-routing-can-dissolve-a-file-fence`.
