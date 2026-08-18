# Mission Frame — #634, lane K

All source citations pinned to `9b38b9d9`.

## Intent

Give every planning role (Admiral, Commander, crew) **one spine** whose **bookends are frozen**
and whose **middle is mutable**, so a role stops keeping its real plan in a second file.

**This frame is authored from a declared-degraded map reading, not from map anchors.** This repo
has no architecture map — no `docs/architecture/` packets, a 0-byte `map/ids.jsonl`, and a
`map/INDEX.md` whose per-module links do not resolve. The context step recorded that verdict
with three hash-pinned substitutes (`.agent-work/567-k/map-orientation.json`). Every anchor
below therefore cites a **substitute** or a **source location**, and is labelled as such. I am
not claiming map authority I do not have.

## Affected Capabilities

- **`map/INDEX.md` → `scripts.checklist_engine`** (111 entities, 25 holes) — "work one
  gated/survey plan through its gates". This run changes how a gated plan may be **re-planned**
  mid-run: it adds a declared bookend that `amend` must refuse to touch. It does not change how
  gates are driven.
- **`map/INDEX.md` → `scripts.mcp_spine_server`** (38 entities, 3 holes) — "MCP front door for
  the checklist engine (#424)". Already exposes `spine_amend`; this run must keep the door's
  refusals faithful to the engine's, and must not let the door decide policy the engine owns.
- **`README.md` → "Mechanically-enforced rails"** — the corpus premise that a rail *refuses*
  rather than reminds. A frozen bookend that is only documented is not a bookend. This is the
  substitute-derived constraint that decides candidate selection.

## Examples / Events

- The three role spines are the concrete instances, all `type: gated`:
  `COMMANDER_SPINE` — `init·context·understand·plan·execute·reconcile·triage·review·feedback·archive`;
  `ADMIRAL_SPINE` — `init·latitude·execute·closeout`;
  `EXPLORER_SPINE` — `init·context·explore·spec·review·confirm·route`.
  Each already has the human's shape: fixed opening, fixed closing, a middle that wants to grow.
- The live counter-examples this run exists to retire: `execute.json` (83 entries under
  `commander-567-d1-execute`; 16 under `constellation/567-e/execute`) and the Admiral's
  two-wave nine-lane epic run inside a single `execute` gate with its structure in
  `ADMIRAL_LOG.md` + `transitions/`.

## Structural Anchors

Source locations, read directly (no map anchor exists to cite):

- `scripts/checklist_engine.py:2971` `amend()` — the re-planning verb; add/drop/rescope/retext-check.
- `scripts/checklist_engine.py:3036` `_floor()` — the **only** freeze in the engine today:
  `1 + index of the last non-pending gate`.
- `scripts/checklist_engine.py:3068` — the insert-below-floor refusal.
- `scripts/checklist_engine.py:3076` / `:3089` — `drop` / `rescope`, both gated on
  `status == "pending"` and nothing else.
- `scripts/checklist_engine.py:3180` — the `cl["amendments"]` audit append (ts, reason, authority, ops).
- `scripts/checklist_engine.py:2617` `advance(..., from_child=...)` — the cross-agent verdict seam.
- `scripts/checklist_engine.py:2733` `consolidate()` — survey-only; what `from_child` consumes.
- `scripts/mcp_spine_server.py` — `spine_amend` door tool and its path-containment guards.
- `skills/{commander,admiral,explorer}/templates/*_SPINE.template.json` — the three plans that
  would carry a bookend declaration.

## Governing Constraints / Assumptions

- **`README.md` → rails refuse, they do not remind.** A bookend enforced only in prose fails the
  corpus's own premise. What breaks if ignored: the deliverable is a doc, not a mechanism.
- **`docs/agents/ORCHESTRATOR_CONTEXT.md` → dogfooding delta.** The engine under edit is not the
  engine in play; hooks run from the main checkout (#269). Every behavioural claim must come from
  a **fresh process with explicit paths**. What breaks if ignored: in-session observation is
  accepted as evidence and the claim is unfounded.
- **`docs/agents/ORCHESTRATOR_CONTEXT.md` → retired learning playbook.** No new file that
  accumulates advice for future agents; no promotion into `docs/agents/*`.
- **Self-hosting (LAUNCH_ORDER).** Read-only status on the live spine must exit 0; every mutating
  verb is proven against a **copy**. What breaks if ignored: I corrupt the Admiral's live run.
- **Backward compatibility (assumption, to be verified by the suite).** Every spine in flight
  today — including the Admiral's live one and mine — carries **no** bookend declaration. The
  mechanism must read an undeclared plan exactly as it reads today. What breaks if ignored: every
  existing spine changes behaviour under a running epic.

## Decision Anchors & Decision Pressure

**There are no map decision anchors for this run, because there is no map.** Nothing in this
repo carries an `explained-by` decision node, so this section cites **launch-order rulings**
instead, labelled `ruling:` rather than `decision:` so they are not mistaken for map anchors
they are not. The grades are the order's own, restated verbatim.

- ruling:every-planning-role — build for Admiral, Commander and crew, not Commanders alone.
  @grade: settled/human · leans g2, g3
- ruling:frozen-means-frozen — bookends stay fixed; only the middle is mutable.
  @grade: settled/human · leans g1, g2
- ruling:plan-change-is-legible — reuse `amend`'s authority and the append-only `why_trail`; do
  not invent a third record.
  @grade: settled/human · leans g1
- ruling:design-it-twice — N>=2 candidates under distinct named constraints; **convergence is
  human-only**.
  @grade: settled/doctrine · leans g0
- ruling:establish-from-child-first — settled this run by reading source: `from_child` is a
  cross-agent verdict seam (survey consolidation → parent `review-result`), not a
  gated-can't-grow workaround. It survives untouched and is out of scope.
  @grade: settled/measured · leans g1 · settle: read at `:2617-2645` and `tests/test_checklist_engine.py:429-471` — done
- ruling:reduce-complexity — judge by whether work moves off agents into mechanisms.
  @grade: settled/human · leans g1, g2
- ruling:map-index-is-admiral-owned — do not regenerate or hand-edit `map/INDEX.md`.
  @grade: settled/doctrine · leans reconcile

**Decision pressure** (choices this run forces; surfaced, not decided):

- *How a bookend is declared* — a per-gate flag on the task, a plan-level list of ids, or a
  positional rule (first N / last N). Ungraded: this is what the design-it-twice candidates exist
  to answer, and the order reserves convergence to the human.
- *Whether the doctrine migration ships with the mechanism.* Moving Commander's `execute.json`
  and the Admiral's `ADMIRAL_LOG.md` middle into the spine touches
  `skills/commander/templates/EXECUTE_PLAN.template.json` and role prose that fall in **neither**
  my ownership list nor lane J's fence. Surfaced to the Admiral as a scope question.
- *Whether "only the owner mutates once started" needs enforcement*, given ownership is a
  caller-supplied session-id string that a cold subagent already reused once (#632). Named in the
  order's Local Unknowns; carried as pressure, not taken.

## Claims / Evidence Surfaces

- **claim: a declared bookend cannot be dropped or rescoped by `amend`.** Checked by new tests in
  `tests/test_checklist_engine.py` asserting `EngineError` on `drop`/`rescope` of a declared
  bookend, and by an all-or-nothing test proving a mixed delta leaves the plan unmutated.
- **claim: an undeclared plan behaves exactly as it does today.** Checked by the existing
  `amend` suite passing unchanged, plus an explicit no-declaration test.
- **claim: the door's refusal matches the engine's.** Checked in `tests/test_mcp_spine_server.py`
  / `test_mcp_identity.py` — the door forwards, the engine refuses.
- **claim: the live Admiral spine is readable and unharmed.** Checked by a read-only `current` on
  the live spine exiting 0, and every mutating proof run against a **copy** in a temp dir, in a
  fresh process with explicit paths.
- **claim: the full suite is green on Linux.** Checked in a clean detached worktree of the branch,
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR`, `^FAILED` grep,
  commit sha recorded. `MapTreeFreshnessTests` may fail; nothing else may.

## Map Confidence / Staleness / Disputes

- **The whole map — absent/unusable.** `map/ids.jsonl` is 0 bytes; `map/INDEX.md` links to
  per-module `INDEX.md` files that do not exist; there is no `docs/architecture/` tree.
  **How this alters the plan:** every structural anchor above is a *source read*, and the plan
  carries a source-verification gate (`g1`) that re-reads `amend`'s guards before changing them
  rather than trusting any summary. I do **not** author gates that assume the map.
  `map/INDEX.md` is fenced to the Admiral (#544), so this is escalated, not repaired — already
  recorded in the orientation receipt's escalation field.
- **`scripts.checklist_engine` — 25 holes; `tests.test_checklist_engine` — 484 holes**, per
  `map/INDEX.md`'s own counts. Undocumented entities in exactly the module I am changing. Handled
  the same way: read the guards at source, cite line numbers, pin them to a revision.

## Out of Scope

- `spine_advance --from_child` and the parent/child evidence seam — settled as surviving.
- `scripts/run_crew.py`, `scripts/install_constellation.py`, and both `LAUNCH_ORDER.template.md`
  files — **lane J's**.
- `map/INDEX.md` — the Admiral's.
- Issue filing (ruled: none; stage under `.agent-work/567-k/triage-candidates/`).
- Promoting any observation into `docs/agents/*` — the human's call.
- Enforcing spine ownership against session-id spoofing (#632) — named as pressure, not taken.
- Converging the design candidates — human-only.
