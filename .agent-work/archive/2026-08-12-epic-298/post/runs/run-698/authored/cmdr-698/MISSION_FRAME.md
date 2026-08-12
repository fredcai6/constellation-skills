# Mission Frame — cmdr-698

Map-first frame for issue #698 (#666 follow-on hardening). Authored from the map input the
`context` step resolved (RESOLVED, entrypoint `docs/architecture/index.md`, 76 anchors, receipt
`.agent-work/cmdr-698/map-orientation.json`) **before** any source read.

Not skipped as trivial: H1 changes the public read/write surface of a **keystone state store**
whose invariants the map records other components as trusting, so the map genuinely constrains
the plan — most sharply by carrying **one claim about this area that is false against source**.

## Intent

Move the DriverFingerprint cell store's identity arguments from loose primitives onto a validated
value object, so a structurally ill-formed address is refused **at the call** rather than reaching
the row-write loop — without moving a single fitted number, and without disturbing any of the four
keystone invariants `struct:physics.fingerprint` publishes to its consumers. Plus two isolated
hygiene fixes (a script `sys.path` guard, a `.gitignore` omission) with no runtime coupling to it.

## Affected Capabilities

- **Fingerprint cell persistence + retrieval** (`struct:physics.fingerprint`, `store.py`) — today
  keys three public methods on four bare `str` + a `ClassVocabulary`; after this run, on a validated
  slot value object. Behavior of what is stored/returned is unchanged.
- **Fingerprint fitting** (`struct:physics.fingerprint`, `fit.py`) — the sole writer; it only
  changes how it *names* the write target. `purpose:weekend_utilization_prior` is downstream and
  untouched.
- **Pilot orchestration** (`struct:physics.pilot`, `purpose:pilot_orchestration`) — the only
  production *reader*; two call sites re-typed, no logic change.
- **Class-axis coverage diagnostic** (`scripts/fingerprint_class_coverage_675.py`) — gains an
  import guard only; its verdict math is explicitly out of scope.

## Examples / Events

- A caller passing `what_measure="banana"` today gets rows written under a nonsense measure; after
  this run it raises at slot construction. This is the acceptance H1 asks for, and no current
  caller does it.
- A caller passing a **reserved** measure (`"push"`, `"managed"`, …) must **still construct fine**
  and be refused only at write — epic #659 ruling 4's present-but-unused dormant slot. Edge case
  that a naive "validate everything at construction" implementation silently breaks.
- A caller passing an `era` that disagrees with `vocabulary.rules_era` must still raise
  `EraVocabularyMismatchError`, not a construction `ValueError` — so the slot stays vocabulary-blind.
- Running `py scripts/fingerprint_class_coverage_675.py` from a git worktree today resolves
  `src.*` against the MAIN checkout via the editable-install `.pth`; pytest never sees this because
  it inserts its own root.

## Structural Anchors

- `struct:physics.fingerprint` — `src/physics/fingerprint/`, component. Owns `address.py`
  (`CellAddress`), `store.py` (`DriverFingerprintStore`, `FingerprintCell`), `fit.py`,
  `vocabulary.py`, `join.py`. **All H1 code lands here.**
- `struct:physics.pilot` — `src/physics/pilot/`, component. Pure consumer; the two `get_fingerprint`
  call sites at `pipeline.py:257`/`:325`.
- `struct:physics.instrument_panel` — `src/physics/instrument_panel/`, component. **Verified NOT a
  caller** (see Disputes); no change.
- `struct:physics` — parent container; the region boundary this run stays inside.

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — nothing in `src/physics/` may import evo /
  `latent_power` / `compound_prior`. This run adds no import at all beyond intra-package, so the
  constraint is preserved trivially; the reviewer still re-verifies rather than assuming.
- **Assumption (project doctrine, `docs/agents/ORCHESTRATOR_CONTEXT.md`):** physics is a *rigorous*
  region — test-led change, focused region suite, `simplification_limits` on touched paths.
  `address.py` gains a dataclass, so the file-length limit is a live concern, not a formality.
- **Assumption (`store.py:10-32`, #666 Protected Intent):** the four keystone invariants —
  non-NULL `cell_key`, k-cells-always-populated, loud refusal with no silent substitution, no
  fit-on-read — are what every downstream consumer trusts. A per-cell API would destroy two of them.

## Decision Anchors & Decision Pressure

- `decision:join-consumer-boundary` — the join is for practice-update/fusion summaries; the race
  sim and the panel read **un-aggregated cells**, not the aggregate. Constrains this run only in
  that the un-aggregated read path (`get_fingerprint`) must keep working identically for both.
  `@grade: settled/inherited · leans g1-slot,g2-callers`
**Decision candidates this run creates** (not yet map anchors — they carry no `decision:` id until
Cartographer records them at reconcile, which is also when the `@grade` tags below get welded on):

- **candidate — slot-is-the-address-prefix.** The store API is typed on a frozen
  `FingerprintSlot(driver, era, channel, what_measure)`, not on `CellAddress`, because the store
  addresses a k-cell group while `CellAddress` addresses one cell. `ClassVocabulary` remains the
  single authority for `vocabulary_version` and `class_ids`. Proposed grade on recording:
  `settled/inherited · leans g1-slot,g2-callers` — the group shape follows from #666 Protected
  Intent, not from this run's preference. The **name** alone would be `guess`, freely revisable.
- **candidate — slot-validation-is-CellAddress-parity.** The slot shares `CellAddress`'s exact
  validator; no channel-set membership check; reserved measures stay constructible-but-refused-at-write.
  Proposed grade on recording: `settled/inherited · leans g1-slot,g3-tests`.
- **Decision pressure (surfaced, not taken):** should `CellAddress`/`FingerprintSlot` enforce
  `channel in FINGERPRINT_CHANNELS`? Deferred — it is a genuine behavior tightening with its own
  blast radius (hard-wires the constant against a future third channel) and `fit.py:347-350`
  already validates channel independently. Routed to triage.
- **Decision pressure (surfaced, not taken):** should the three fingerprint scripts take `--out`
  instead of hardcoding `.agent-work/...` paths? Deferred — it is an interface change, not
  hygiene. Routed to triage.

## Claims / Evidence Surfaces

- `claim:instrument_panel_reads_cells_directly` — **DISPUTED by this run**; see below.
- `claim:pilot-runs-end-to-end-3-circuits` — the pilot's end-to-end run over Monaco/Belgium/GB
  2023-Q exercises both `get_fingerprint` call sites. Not re-run here (it needs real telemetry);
  the scoped `tests/unit/physics/pilot` suite is the standing proxy, and the gate says so honestly
  rather than implying the real pilot was re-run.
- Evidence each gate re-confirms: the store's own pre-existing test files pass **unmodified in
  intent**, with every refusal raising the *same* exception type as before
  (`lesson:consumed-frozen-module-run-guard-tests`); `simplification_limits` clean on touched paths.

## Map Confidence / Staleness / Disputes

- **`claim:instrument_panel_reads_cells_directly` — DISPUTED.**
  `docs/architecture/packets/physics.md:2753` renders it as "reads `fingerprint.store.get_fingerprint`
  cells directly." Against source that is **false as a call/import claim**: no module in
  `src/physics/instrument_panel/`, nor `scripts/instrument_panel_668_report.py`, references
  `DriverFingerprintStore` or `get_fingerprint` at all (the sole fingerprint import is
  `FINGERPRINT_CHANNELS` at `replication.py:61`). The panel *receives* already-fetched cells; the
  pilot is the fetcher. The claim's *intent* (un-aggregated cells rather than the #667 join) is
  true; its wording is not.
  **How this alters the plan:** the caller enumeration was closed by an independent reverse grep
  rather than by trusting the packet — a literal reading would have sent an implementer hunting a
  non-existent call site, or worse, "fixing" one. `instrument_panel` is explicitly named as
  out-of-scope in the plan so a later reader does not re-open it. The wording correction is routed
  to reconcile/triage, **not** patched in a code gate. Corroborates
  `lesson:verify-subagent-self-report-not-just-green-check` — `check_arch_map.py` is green over
  this exact prose.
- **The map is silent on the address space itself.** No anchor names `CellAddress`, and
  `docs/agents/GLOSSARY.md` has no term for it. The plan therefore inherits the name from
  `store.py`'s own docstring prose ("slot", `:22-23`, `:186`, `:301`) rather than coining project
  dialect.
- Confidence on `struct:physics.fingerprint` is `high` and its component description matches
  source on every point checked except the panel claim above.

## Out of Scope

Any behavior change to the fit or the coverage diagnostic (the issue's own exclusion). Channel-set
enforcement. `--out` flags for the three scripts. Any change to `join.py`, `vocabulary.py`,
`frozen_constants.py`, `struct:physics.instrument_panel`, or anything downstream of
`purpose:weekend_utilization_prior`. Rewriting the store to a per-cell API. Migrating existing
`driver_fingerprint.db` rows (the schema and every `cell_key` value are unchanged by construction).
