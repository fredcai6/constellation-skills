# Triage recommendations — `epic-559/c3-lifecycle`

**Authority, and why every disposition below is the same.** The frozen launch order rules, verbatim:
*"`triage` files nothing. No GitHub issues are cut this wave. A finding you cannot fix is recorded in your
return and I file it at epic closeout, per the human's ruling. This is not permission to drop findings —
it is permission to stop asking about the filing."* `docs/agents/ORCHESTRATOR_CONTEXT.md` independently
puts pushes, PRs and merges behind explicit human approval.

So every candidate below is routed **`recommend-and-defer`**, and the deferral reason is the same in each
case: **filing authority was withheld from this run by the ratified launch order, not unclear.** The
Admiral files at epic closeout. Nothing is dropped.

Each candidate was checked against the fix-now ladder first. **None clears all four rungs**, and the
specific failing rung is named per candidate rather than left implied.

All observations are `rev: 51feb36c` unless stated otherwise.

---

## T1 — A Commander drives two checklists, but the door binds one spine per process

**Labels:** architecture weakness · structure/constraint mismatch · tooling
**Priority:** high — it defeats the point of this epic one tier up
**Disposition:** `recommend-and-defer`
**Fix-now ladder:** fails **bounded diff** and **no architecture impact**. This is a door-identity design
change, not a small edit.

### Observation 1 — the door cannot be pointed at a second checklist

- **What's wrong:** `_identity_violation` (`scripts/mcp_spine_server.py:174`) asks the engine's own parser
  what `--file` resolves to and refuses anything that is not the bound spine. A Commander's gate plan is a
  second checklist in the same work area, so it cannot be driven through the door at all.
- **Expected:** an agent drives all of its own engine state through the door, per the standing ruling
  that *"anything that we can only do via the cli is a defect."*
- **Feeding conditions:** any Commander run that authors a gate plan — i.e. every one. Linux, this repo,
  `.mcp.json`'s single `spine` server.
- **`type`:** `measured` — I attempted it and read the refusal predicate; this run executed
  `GATE_PLAN.json` as a frozen document instead.
- **`rev`:** `51feb36c`

### Observation 2 — the only shipped second binding is a hand-edited user-level config

- **What's wrong:** the sole existing example of one agent driving two spines is the Admiral's
  `spine-epic` server, registered by hand in `~/.claude.json` and bound to
  `.agent-work/epic-418-followon/spine.json`. It is a manual config edit that cannot take effect
  mid-session, because MCP servers launch at session start.
- **Expected:** binding a second checklist is an operation, not a config edit — the same argument this
  epic makes about `git worktree add`.
- **Feeding conditions:** present today; found by reading `~/.claude.json`.
- **`type`:** `measured` — read directly from the user-level config.
- **`rev`:** `51feb36c`

**Possible fix (hypothesis, not a spec):** let the door accept a *confined* second binding — a checklist
under the bound spine's own directory tree, the containment `_resolve_confined` already implements for
`--from-child` and `--delta`. That would make a gate plan drivable without weakening the
cannot-be-redirected-elsewhere property. Not attempted; it touches the guard this epic deliberately did
not weaken.

**Open questions:** should a gate plan be an engine checklist at all, or is a Commander's gate plan better
modelled as data the spine consults? The second reading would dissolve the problem instead of solving it.

---

## T2 — `episode_capture.manifest_root()` doubles the work-id path segment

**Labels:** bug · tooling
**Priority:** medium — it silently scatters engine-written provenance for every reviewer crew
**Disposition:** `recommend-and-defer`
**Fix-now ladder:** fails **adjacent to current scope** — `scripts/episode_capture.py` is untouched by
every gate in this run, so fixing it would be a cold-start edit with no reviewer looking at it.

### Observation 1 — a reviewer survey writes its provenance into a nested duplicate path

- **What's wrong:** `manifest_root()` (`scripts/episode_capture.py:181-213`) doubles the work-id segment
  when a checklist lives in a subdirectory of its own work-id directory that does not itself end in the
  work id. Driving `r0-context` on a survey at `.agent-work/<work-id>/g1-review/review.json` wrote
  `.agent-work/epic-559/c3-lifecycle/epic-559/c3-lifecycle/{context,mechanical}/r*.json`.
- **Expected:** `.agent-work/epic-559/c3-lifecycle/{context,mechanical}/`.
- **Feeding conditions:** exactly the path shape the reviewer skill's own convention recommends, so it
  fires for **every** reviewer crew in this corpus, not an edge case. Linux, this repo.
- **`type`:** `measured` — reproduced live by the g1 reviewer and confirmed on disk by the Commander
  (`find` output).
- **`rev`:** `51feb36c`

**Possible fix (hypothesis):** the function's docstring already documents the historical
parent-of-`base_dir` answer as deliberate; the gap is that it does not recognize the
`<work-id>/<gate>-review/` shape. A targeted case for that shape is probably enough.

**Note:** this run *committed* one such stray directory by accident and untracked it again in `51feb36c`.
That mistake is recorded in its own commit message.

---

## T3 — `DESIGN_NOTE.md` §7's fault list is correct but unpinned

**Labels:** missing test · missing doc
**Priority:** medium — it is the exact failure `g5` just repaired, left able to recur
**Disposition:** `recommend-and-defer`
**Fix-now ladder:** fails **verifiable now** in the honest sense — writing the pin is small, but it is a
new test against a doc contract that no reviewer in this run was briefed to check, and slipping it in
after the last review is how an unreviewed change ships.

### Observation 1 — nothing asserts §7's list equals the codes the generator can raise

- **What's wrong:** §4's `CHECK_KINDS` tuple is machine-pinned by a test asserting it equals the
  compiler's own constant. §7's spec-fault vocabulary has no equivalent, so it stays correct only as long
  as whoever next adds a `spec-*` fault re-runs the enumeration instead of hand-editing the list.
- **Expected:** the same pinning §4 already has, since §7 is the section that just went stale.
- **Feeding conditions:** any future change adding a spec-shape fault.
- **`type`:** `inferred` — inferred from the *absence* of such a test, which the g5 reviewer searched for
  and did not find; the staleness it guards against was itself `measured` (§7 was under-listed before g5).
- **`rev`:** `51feb36c`

### Observation 2 — the six `probe-*` fault codes are never enumerated anywhere

- **What's wrong:** §7 is scoped to spec-shape faults by its own title, and no section enumerates the
  `probe-*` codes at all.
- **Expected:** parity, or an explicit statement that probe faults are deliberately not enumerated.
- **`type`:** `measured` — grepped by the g5 reviewer.
- **`rev`:** `51feb36c`

---

## T4 — "Never two crews in one worktree" is prose in five places and enforced nowhere

**Labels:** architecture weakness · missing test
**Priority:** medium
**Disposition:** `recommend-and-defer`
**Fix-now ladder:** fails **no architecture impact** — changing the duplicate-guard's key is a fleet-wide
concurrency-policy change.

### Observation 1 — the mechanical guard is weaker than the rule it is supposed to carry

- **What's wrong:** `active_duplicate` (`scripts/run_crew.py:253-270`) keys on
  work-id/gate/**role**/worktree, so two crews with *different roles* in the same worktree are permitted
  by the machinery. The launch order states the rule as absolute.
- **Expected:** either the machinery enforces the stated rule, or the rule is restated as
  "never two crews on the same assignment", which is what is actually enforced.
- **Feeding conditions:** any dispatcher running two differently-roled crews concurrently in one worktree.
- **`type`:** `measured` — read from the predicate; this run honoured the *prose* rule and ran its two
  plan-alternative candidates serially because of it, at real wall-clock cost.
- **`rev`:** `51feb36c`

**Open questions:** which is right? `open_work` (shipped this run) now refuses a work id whose spine holds
an active `engine_session`, which enforces the stronger reading at *provisioning* time. Whether the
dispatch-time guard should match it is a fleet decision, not a Commander's.

---

## T5 — `validate_spine.py` has no `not_yet_written` concept

**Labels:** architecture weakness · tooling
**Priority:** low
**Disposition:** `recommend-and-defer`
**Fix-now ladder:** fails **adjacent to current scope** — `scripts/validate_spine.py` is an explicit no-go
for this wave.

### Observation 1 — a TDD-red check and a permanently vacuous one are indistinguishable to the oracle

- **What's wrong:** `generate_spine.py` has `not_yet_written` for a check whose tests do not exist yet;
  the oracle it defers to has no such concept, so both read as `falsifiable-zero-collected`.
- **Expected:** the oracle can tell "not written yet" from "can never fail", or says it cannot.
- **Feeding conditions:** any hand-authored gate plan. This run's own `GATE_PLAN.json` reports **exactly
  five** such faults, one per gate, every one for tests the run's own gates then wrote.
- **`type`:** `measured` — ran `validate_spine.py` against `GATE_PLAN.json`.
- **`rev`:** `51feb36c`

---

## T6 — `generate_spine.py:910`'s missing `newline="\n"` had a twin nobody looked for

**Labels:** cleanup
**Priority:** low
**Disposition:** `fixed-now` → **superseded**; fixed inside `g5` at `51feb36c`, under review.

Recorded because the *pattern* matters more than the instance: `g1` was BLOCKed for one missing
`newline="\n"`, and the identical omission already existed in `generate_spine.py`. The rule is "every
write" (`docs/agents/CREW_CONTEXT.md:43`) and CI runs `windows-latest`. A corpus-wide sweep for
`write_text`/`open(...,"w")` without `newline="\n"` would be worth one pass; this run only fixed the two
files it had open, which is the under-inclusive-enumeration shape this wave keeps naming.

**`type`:** `measured` — found by the g1 reviewer, confirmed by the Commander at
`docs/agents/CREW_CONTEXT.md:43` and `.github/workflows/ci.yml:23`.

---

## Summary for the Admiral

| id | what | priority | disposition |
|---|---|---|---|
| T1 | door binds one spine; a Commander drives two | high | recommend-and-defer |
| T2 | `episode_capture.manifest_root()` doubles the work-id segment | medium | recommend-and-defer |
| T3 | `DESIGN_NOTE.md` §7 correct but unpinned; no `probe-*` list | medium | recommend-and-defer |
| T4 | one-crew-per-worktree is prose; the guard keys on role too | medium | recommend-and-defer |
| T5 | `validate_spine.py` cannot express "not written yet" | low | recommend-and-defer |
| T6 | missing `newline="\n"` twin; a corpus sweep is warranted | low | fixed-now (the instance) |

**Nothing was filed. Nothing was dropped.**
