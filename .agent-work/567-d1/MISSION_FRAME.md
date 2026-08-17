# Mission Frame — lane D1 (#559, with #596 and #526)

## Intent

Remove the CLI as an **agent-facing second path** from every instruction file the corpus ships,
and land a guard that fails if it grows back. Not a deletion exercise: #559's text has been
deleted twice and regrown twice, so the deliverable is the mechanism that makes the third
deletion stick.

This frame is authored against **declared substitutes, not a map**. `map_orient orient`
returned `DEGRADED-UNPARSEABLE` (receipt `.agent-work/567-d1/map-orientation.json`): this
skill-source repo has no `docs/architecture` packet map, `map/INDEX.md` carries no citable
anchor id, and `map/ids.jsonl` is empty. Every anchor below is one of the five hash-pinned
substitutes from that receipt. The gap is escalated to the Admiral, not fixed here
(`map/INDEX.md` is Admiral-owned this wave, #544).

## Affected Capabilities

- `docs/agents/ORCHESTRATOR_CONTEXT.md` — the project's own delta doctrine. Governs this run
  twice: "Workflow mechanisms and verifiers" require *targeted automated tests plus the
  relevant broader suite* (so the guard is mandatory, not optional), and the **Dogfooding**
  section requires engine/door behaviour to be validated in a **fresh process with explicit
  paths** (which is how the door-cannot-bind-a-second-checklist measurement was taken).
- `docs/agents/GLOSSARY.md` — one name per thing. Relevant gap: it carries **no entry for
  "door"**, which is the very term this epic makes load-bearing. Not fixed here (staged as a
  triage candidate); noted because the replacement wording I author must be self-explaining
  in its absence.

## Examples / Events

- `skills/commander/references/commander-core.md` — the live example of the defect: line 127
  carries both a `CLI fallback` clause and an `<engine>` token, in the delegated-mode
  `user-decision` instruction that this very run executed four times.
- The run's own `init` imperative, read at step one, handed me
  `CLI fallback: <engine> claim --session-id commander-567-d1 ...`. The target is not
  hypothetical; it is what a Commander reads first.

## Structural Anchors

- `skills/commander/references/commander-core.md` — mode-neutral Commander doctrine; one
  clause site, one token site. Sole-writer: mine.
- `specs/implementer.spine.toml` — gated role spec. Zero door mentions. `config_ref` points at
  `docs/agents/engine-config.json`, which **does not exist in this repo**.
- `specs/reviewer.spine.toml` — survey role spec. Zero door mentions. Same dangling
  `config_ref`.
- The clause/token corpus: 10 files under `skills/` holding 13 clauses and 9 target tokens
  (enumerated in `notes-1.md`).

## Governing Constraints / Assumptions

- **one door one spine** — **measured, not assumed.** A door holding its own lease is
  refused when it binds a second checklist ("one door drives one spine at a time"). The only
  escape, releasing the lease first, is barred for a Commander by its own archive provenance
  check. So the door cannot reach a second checklist, and 3 of the 13 clauses describe a real
  path rather than a redundant one.
- **records are not instruction** — `docs/superpowers/**` are historical records.
  Editing one to make a sweep count come out right falsifies the record.
- **no exception list** — the episode-observation guard's exception list reached 11
  entries across five runs. An exception-list-shaped guard is the failure mode to avoid.
- **assert against behaviour** — `global-orchestrator.md` §"A check that cannot fail":
  assert against the text's absence, never against a description of the rule; and any guard
  that loops must **assert what it looped over** and state the count.
- **merge last** — this lane merges last, so the guard is authored against a tree
  where lane E has already changed the door's own refusal text. Expect a rebase before the
  final gate.

## Decision Anchors & Decision Pressure

Carried in `.agent-work/567-d1/decision-anchors.md` and welded into the gate blocks of
`.agent-work/567-d1/execute.json`, **not here**. Reason, stated rather than worked around:
`map_orient.py verify-frame` refuses every `<prefix>:<id>` anchor token when orientation is
DEGRADED — with no map read there is nothing for an anchor to be a member of — while
decision-fixedness doctrine requires graded `decision:<id>` bullets in this very section. In a
repo with no map the two mechanisms cannot both be satisfied in this file. The decisions are
graded where their `leans <gate-id>` resolves; the conflict is staged as a triage candidate.

**Decision pressure** (a choice this run forces, carrying no grade): `tests/test_mcp_adoption.py`
and `tests/data/store_mentions.approved.txt` sit in no lane's ownership list, and the sweep is
impossible without editing the first. Surfaced to the Admiral; proceeding, because no other lane
owns them and there is therefore no collision risk.

## Claims / Evidence Surfaces

- **regrowth had a mechanism** — `test_mcp_adoption.py::TestTier1ImperativeFields::test_field_still_carries_cli_fallback` asserts the exact CLI command line survives in 7 imperative fields and fails with *"the CLI door must stay, never be removed or discouraged."* Verified by reading the test and by the sweep turning it red.
- **door cannot reach a second checklist** — verified by the fresh-process probe recorded in `notes-1.md` (claim → refused bind → release → successful bind).
- **guard is red proofed** — verified by reintroducing a clause and a token, showing the guard fails, removing them, showing it passes. This is the item that closes #559.
- **suite green** — full suite on Linux in a clean **detached** worktree of the branch, `^FAILED` grep pasted, only `MapTreeFreshnessTests` permitted to fail.

## Map Confidence / Staleness / Disputes

- **No map exists.** `DEGRADED-UNPARSEABLE`, discharged with five hash-pinned substitutes, two
  unmapped statements and an escalation. How it alters the plan: the guard's scope cannot be
  cut from a map, so it is cut from the repo's own existing corpus walk — a committed prior
  declaration with a ≥60-file floor — instead of from a scope I assert in the same breath.
- `map/INDEX.md` is stale-by-construction on every parallel branch (#544) and Admiral-owned.
  The plan does not touch it and accepts `MapTreeFreshnessTests` red.

## Out of Scope

- `skills/workbench/**` (lane D2 deletes those files, including 2 of the 15 clauses),
  `scripts/mcp_spine_server.py` and `episodes/**` (lane E), `scripts/run_crew.py` (lane F),
  `scripts/checklist_engine.py` (lane H), `map/INDEX.md` (Admiral).
- `docs/superpowers/**` — historical records, deliberately untouched.
- #595's advisory precedence — settled by lane C, forbidden to reopen.
- Filing any issue — ruled none; candidates staged as files.
- Promoting any observation into `docs/agents/*` — the human's call.
