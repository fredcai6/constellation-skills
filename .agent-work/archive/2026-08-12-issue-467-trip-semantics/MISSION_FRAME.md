# Mission frame — #467 (A2: trip semantics)

**Map status: DEGRADED-NO-MAP, discharged.** This repo carries no `docs/architecture`
packet map. The orientation receipt at
`.agent-work/issue-467-trip-semantics/map-orientation.json` hash-pins four substitutes,
and this frame is cut from them, not from code:

- `docs/CHECKLIST_SCHEMA.md` — the shipped-behaviour record for `why_trail`, why-capture
  `advance`, the `DIGEST:` / `REFRESH REQUESTED:` display, the `refresh-request` evidence
  type, and **the Trip two-band gate policy** (§"Trip — two-band context-gauge gate
  policy"). This is the structural authority for everything this issue changes.
- `docs/GAUGE_WRITER_HOOK.md` — the write side: the record's four required fields,
  skip-on-uncertainty, the session→spine binding, and the named residuals.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — project deltas: rigor profile for workflow
  mechanisms ("targeted automated verification plus the relevant broader suite"), and repo
  action authority (pushes/PRs need explicit approval).
- `docs/agents/GLOSSARY.md` — one name for one thing: `gauge`, `trip`, `spine`, `gate`,
  `lease`, `scoped null`, `two-bin rule`, `conjunct`.

## Intent

The governor's HARD band is expressed as a **refusal of `advance`**. `advance` is the only
writer of the append-only `why_trail`, and the latest live why-record **is** the `DIGEST` a
cold successor reads. So the event that forces a handoff is the event that stops the
handoff's brief being written (#431). Convert the trip from a refusal into a **change of
instruction**: the agent still closes its gate, the DIGEST still lands, and what gets
refused is **beginning new work**.

Tommy's framing, load-bearing: *the limits exist so there is room to build the handoff, not
because continuing is unsafe.* HARD means "wrap up", never "you are unsafe".

## Affected capabilities

| Capability | Effect |
|---|---|
| Trip two-band gate policy (`docs/CHECKLIST_SCHEMA.md` §Trip) | HARD's enforcement point moves from `advance` to the verbs that begin work. SOFT unchanged. |
| Why-capture / reach-up (`docs/CHECKLIST_SCHEMA.md` §why_trail, §Refresh requests) | Unchanged in shape; becomes reachable at a trip for the first time. |
| Gauge read side (`docs/GAUGE_WRITER_HOOK.md` companion) | Gains a per-gate headroom argument on the threshold function. The table itself is untouched. |
| Gauge write side (`docs/GAUGE_WRITER_HOOK.md`) | **Not touched.** Read-only context for this run. |

## Structural anchors (from the substitutes)

- **The bands ride the CLI boundary, not the verbs.** `docs/CHECKLIST_SCHEMA.md` records
  that SOFT is a suffix on `current`'s dispatch output and HARD a pre-`advance` guard,
  "so the verb functions stay **pure** (their return values are unchanged, so existing
  exact-equality tests keep passing)". **This line must hold**: the new guard hangs from the
  same chokepoint, a different verb.
- **Both bands are fail-safe on a missing/stale reading.** A stale/absent/corrupt reading
  collapses to `None` inside the reader and yields no advice and no force. Fixed by #467.
- **Both bands are gated-only** (empty for surveys), and check **at gate boundaries only** —
  there is no mid-gate check.
- **`refresh-request` payloads are POINTERS ONLY** (`{seam, why_ref}`), never copies of
  state (`docs/CHECKLIST_SCHEMA.md` §evidence payload table).
- **The HARD band keys its release on the current-digest why-record id** (#190), so a new
  trip on a still-open gate cannot ride an earlier request's coattails.
- **`DIGEST:` + `ACTIVE <gate> — <imperative>` is the entire cold-start surface.** No
  separate handoff document is ever written or read.

## Governing constraints and assumptions

- `#467` **Fixed**, not renegotiable: a missing/failed reading never forces a handoff; HARD
  means "wrap up"; the reading is **pushed** by the engine, never fetched by the agent.
- **The global default threshold is not mine to retune** (LO fence). Any per-gate override
  must therefore be **tighten-only**, so no gate can raise the production default.
- Repo action authority (`docs/agents/ORCHESTRATOR_CONTEXT.md`): local commits allowed;
  pushes/PRs need explicit approval — the Admiral's, here.
- Rigor profile for workflow mechanisms: **targeted automated tests plus the relevant
  broader suite**. Main's green baseline, re-measured in this worktree at `d376b786`:
  `1793 passed, 2 skipped, 683 subtests passed`, real exit 0.
- **Two-bin rule** (`docs/agents/GLOSSARY.md`): every enforced invariant is either checked
  by a command or attested by a named human. Prose enforces nothing — which is precisely
  DC6's problem statement.

## Decision anchors and decision pressure

No machine-readable decision anchors exist (`anchor_count: 0`), so this frame cites none —
under a degraded orientation there is no map for an anchor id to be a member of. The
decisions this run must make are the ones #467 hands me under **Open (Commander's call)**;
they are recorded as graded decision ids in `execute.json`, which is where an executor
reads them:

- **HARD guards beginning work, not closing it** — the band refuses `start`/`resume`, never
  `advance`. Converged from a 3-candidate design-it-twice panel.
- **The per-gate override is absolute-token headroom, tighten-only** — not a fraction. All
  three independent candidates converged on this from the read side's own intent-first
  representation.
- **The trip ledger is the compliance record** — the engine appends an engine-only entry
  every time the HARD band is evaluated and found tripped, so "a trip fired" is assertable
  after the fact instead of being an absence.

**Decision pressure carried up, not resolved here:** the trip band is role-blind (one
model-keyed default for every tier). That is a production default and stays the human's.

## Claims and evidence surfaces

- The RED reproducing #431 is an **end-to-end staleness property**, not an exception: at a
  HARD gate, an agent that follows the shipped instruction leaves `_digest` naming the
  pre-trip understanding. `docs/CHECKLIST_SCHEMA.md` §Trip is what makes that reading
  authoritative rather than inferred from code.
- **The RED leaves no residue** (#467): the deadlock is a property of the refusal path being
  deleted, so it is unreproducible by construction afterwards and cannot stand as a
  regression test. The standing guards are DC6's compliance observable and DC2's two-way
  test.
- **No absence is evidence.** Every claim about trip behaviour is paired with an assertion
  that a reading existed. The `trip_log` is the mechanism that makes that assertable after
  the fact rather than a discipline.

## Map confidence, staleness, disputes

- `docs/CHECKLIST_SCHEMA.md` §Trip is **current and specific** — it names the shipped
  functions and the two bands' placement. High confidence; it is the closest thing to a map
  this area has, and this change makes part of it stale, so updating it is in scope.
- `docs/GAUGE_WRITER_HOOK.md` is current but describes a hook that **does not ship**
  (#458: tracked `.claude/settings.json` wires the gauge writer on nothing). Every governor
  observation this epic has made comes from one laptop's local config. **Disputed area** —
  my acceptance plants readings deliberately rather than depending on live wiring, and says
  so.
- **Contested field reading, flagged not acted on:** the LO records crews tripping at 17-21%
  while the Admiral ran to 44% untripped, read as role-blindness. `docs/GAUGE_WRITER_HOOK.md`
  §residuals records that an orchestrator holding several spines under one key writes **no
  reading at all** — the Admiral's exact shape. By #467's own "no absence is evidence" rule
  those two are indistinguishable without an asserted reading. Recorded; not acted on.

## Out of scope

Retuning the global default threshold. Wiring tracked `.claude/settings.json` (#458).
Filing issues. Closing #431 (verify dissolved; the Admiral closes). The identity-durability
constraint #467 records for #441/#452. The gauge **write** side. Mid-gate checks.
