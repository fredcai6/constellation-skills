# Mission Frame — C2: generate the spine from a spec

**A note on anchor grammar, up front.** This repo's orientation came back `DEGRADED-UNPARSEABLE`:
there is no `docs/architecture/` map, `map/INDEX.md` is an unfilled template and `map/ids.jsonl` is
empty. Under a degraded orientation `map_orient.py verify-frame` refuses **every** map-anchor id —
correctly, because there is no map for an id to be a member of. So this frame deliberately carries
**no `struct:` / `capability:` / `constraint:` / `assumption:` / `claim:` / `decision:` prefixed
ids**. It is built from the reading the receipt hash-pinned at orient time, and it cites those
substitutes by path. Decisions below are still graded; only the prefix is dropped.

The declared reading this frame is cut from (all hash-pinned in
`.agent-work/epic-559/c2-generate-the-spine/map-orientation.json`):
`docs/CHECKLIST_SCHEMA.md`, `docs/CHECKLIST_ENGINE_DESIGN.md`, `docs/agents/ORCHESTRATOR_CONTEXT.md`,
`docs/agents/GLOSSARY.md`, `README.md`, `SKILL_INDEX.md`.

## Intent

Replace hand-authored spine checks with **generated** ones. An author writes a spec that names *what
must be proven*; a generator turns that into the JSON `checklist_engine.py` already reads, and
**refuses to emit anything `scripts/validate_spine.py` would reject**. Two properties are not
optional in the output: every gate carries a place to record beliefs, concerns and open questions in
the substrate the engine already renders; and a large claim is carried up to its reviewer rather than
buried inside a gate.

The frame is **not** shrunk — this run introduces a new load-bearing interface (a spec format other
authors will write against), which is the opposite of the trivial-mechanical case.

## Affected capabilities

Named in prose, from the declared reading, since no map ids exist here.

- **Driving a gated plan** — `docs/CHECKLIST_SCHEMA.md` is the on-disk contract: a checklist is
  `{work_id, type, config_ref, items[], tasks{}, consolidation, triage_candidates, blockers}`, each
  task carrying `imperative`, `preconditions`, `postconditions`, `constraints`, `directives`,
  `anchors`, `child_checklist`, `why_exempt`, `status`. This run **adds a producer** of that shape
  and changes nothing about the consumer.
- **Refusing a bad spine** — `scripts/validate_spine.py` (shipped by C1 at `0ab7ecab`) is the
  acceptance oracle. Its `validate(spine, repo_root=...)` is importable and returns a
  `ValidationResult` carrying a distinct `.undecidable` channel. This run **becomes its first
  in-repo caller**; it does not move its fault set or acceptance boundary.
- **Surfacing a gate to the agent driving it** — `docs/CHECKLIST_SCHEMA.md` §Rendering records that
  `current` renders a populated `constraints`, `anchors` and `directives` block on the **active**
  gate (issues #420 and #433). This is the substrate the beliefs/concerns/open-questions property
  must ride in; anything else is a field the engine ignores.
- **Dispatching a crew against a spine** — a spine-only dispatch drives its bound spine from the
  prompt alone and is judged on the spine reaching a terminal state, not on a result artifact. This
  run **consumes** that capability to prove a generated spine really drives.

## Examples / events

- The four hand-authored checks that could not do their job (launch order, Prior-Wave Verdicts): an
  unquoted `-k Door or Tie or Registry` the shell split into words; a probe that raised at import
  because no spine was bound; a call passing a flag argparse does not define; a population filter
  wrong twice in opposite directions. These are the **acceptance examples** — a spec format that
  cannot express any of them is the deliverable.
- The corpus's self-checking idiom, which the generator must be able to emit:
  `test $(pytest -q -k 'Selector' --collect-only 2>/dev/null | grep -c '::') -ge N && pytest -q -k 'Selector'`.
- The `implementer-result` census (122 records, 7 distinct shapes) that showed a gate flipping from
  cannot-fail to cannot-pass: the check and the instruction that satisfies it must come out of the
  same place or they drift.

## Structural anchors (named by path, un-prefixed — see the note above)

- `scripts/validate_spine.py` — the oracle. Import surface: `validate`, `validate_file`,
  `ValidationResult`, `Fault`, `Undecidable`, `discover_checklist_templates`. Read, never modified.
- `scripts/checklist_engine.py` — the consumer. `_render_directive_lines` (line 2104) and
  `render_human` (line 2189) are the two functions that decide whether a generated gate's notes ever
  reach the agent. Read, never modified.
- `scripts/init_work_area.py` — owns `_RESOLVER_OWNED_TOKEN_RE`, the single source of truth for which
  `<token>` families are legitimately resolved before a spine is driven. The generator's
  placeholder refusal must key on the same regex, not a second copy of it.
- `skills/*/templates/*.json` — the 12 shipped gated-or-survey templates the lint sweeps. **Not
  edited to make generator output validate.**
- New: a spec directory plus a generator module under `scripts/`, and the role specs it compiles.

## Governing constraints / assumptions

- The engine's on-disk format does not change. The generator emits what the engine already reads.
- Beliefs, concerns and open questions ride in `constraints`/`directives`. A new field the engine
  ignores is worse than no field, because it looks like it works.
- The oracle does not move. Any change to `validate_spine.py`'s fault set or acceptance boundary is a
  float to the Admiral, not a patch.
- No shipped template is edited to make generator output validate; a disagreement is a finding.
- **Measured, and it governs the design:** across 560 spines / 4341 tasks, `constraints` is populated
  on 970 tasks and always as `list[str]` meaning *rules this gate must respect*; `directives` is
  populated on 22 tasks and always as `dict[name -> contract]` meaning *a standing contract this gate
  must satisfy*. Overloading `constraints` with notes would collide with a real, live meaning.
- Assumption, and it is load-bearing: `python` (not `python3`) is the interpreter with pytest
  importable on this host, and `tomllib` is in the 3.12 standard library, so a TOML spec needs no
  third-party dependency. Verified: `python -c "import sys,tomllib"` prints 3.12.3.

## Decision anchors and decision pressure

Graded per the fixedness grammar; the `decision:` prefix is dropped for the reason at the top.

- **no-engine-format-change** — the generator emits what the engine already reads; a format the
  engine cannot carry is a float, not a patch.
  `@grade: settled/human · leans g1, g2, g3`
- **notes-ride-in-existing-substrate** — beliefs/concerns/open questions ride in
  `constraints`/`directives`, never a new field.
  `@grade: settled/human · leans g2`
- **placeholder-template-vs-instance** — a `<placeholder>` is legitimate in a template and a fault in
  an instance; the generator refuses an instance carrying one. Resolver-owned families are not
  placeholders in this sense.
  `@grade: settled/admiral · leans g1, g3`
- **qualitative-must-be-stated** — a gate with no checkable postcondition must say in so many words
  that it is qualitative; silence is refused.
  `@grade: settled/admiral · leans g1`
- **cold-review-every-change** — every change gets a cold reviewer independent of its implementer, and
  reworks until that reviewer approves.
  `@grade: settled/admiral · leans g1, g2, g3, g4`
- **sonnet-crews** — implementers and reviewers run on Sonnet; escalate one crew to Opus only after a
  Sonnet crew has already failed the same task once.
  `@grade: settled/human · leans g1, g2, g3, g4`
- **no-template-edited-to-pass** — a shipped template is never edited to make generator output
  validate.
  `@grade: settled/admiral · leans g3`
- **notes-live-in-directives-not-constraints** — the handback substrate is a `directives` contract,
  because `constraints` already means "rules" on 970 live tasks and `directives` is both nearly empty
  and structurally richer (name plus typed fields, both shapes rendered).
  `@grade: settled/measured · leans g2 · settle: re-measure the two fields' populated counts and read the shipped instances`
- **spec-has-no-raw-command-field** — the spec offers a closed vocabulary of typed check kinds and
  **no** free-text shell field, so extending what can be proven is a code change with a test rather
  than a string typed into a spec. This is the whole answer to the settling question, and it is the
  one choice most likely to be wrong.
  `@grade: guess · leans g1, g3 · settle: write the implementer and reviewer role specs and see whether either needs a shell string the vocabulary cannot express`

**Decision pressure — surfaced to the Admiral, not chosen silently:**

- Whether to fix the four unresolvable `<engine>` tokens in the orchestrator-tier templates this
  wave. Inherited latitude says it is my call; it is recorded as a decision because it changes shipped
  templates.
- What "a large claim" means concretely, and what escalation it forces. The human's rule is verbatim
  (*"greater claim requires greater review"*); the mechanism that implements it is mine and is the
  second-most-likely thing to be wrong.

## Claims / evidence surfaces

Each is a claim this run must leave checkable, with what re-confirms it:

- *The generator cannot emit a spine the lint would reject.* Re-confirmed by feeding a
  deliberately-bad spec to the generator and observing a refusal, paired against the same spec
  accepted by the pre-guard emit path — the pairing is the evidence, not the refusal alone.
- *Every generated gate carries a place to record beliefs, concerns and open questions.* Re-confirmed
  by asserting the field on every emitted gate **and** by rendering the gate through the engine's own
  `render_human`, so the property is asserted against behaviour rather than against JSON that merely
  looks right.
- *A large claim is carried up.* Re-confirmed by a spec that declares one and a generated spine that
  visibly escalates it, plus the negative: a spec that declares a large claim without the escalation
  is refused.
- *A generated spine drives to a terminal state in a real dispatch.* Re-confirmed by an actual
  `run_crew.py` dispatch judged on `spine_terminal`, not by a simulation.
- *The lint baseline does not regress.* Re-confirmed by `python scripts/validate_spine.py --sweep`
  before and after, and by the full suite in the project's declared test mode.

## Map confidence / staleness / disputes

- **The map is absent, not stale — declared and discharged.** All five orientation candidates came
  back absent, unparseable or empty. No gate in this plan trusts a map area: every structural fact in
  this frame was read from the declared substitutes or measured by command, and the measurements are
  pinned to base commit `0ab7ecab`.
- **How it alters the plan:** it does not add a scout gate — the substitute reading is complete for
  this run's blast radius (one producer, one oracle, one renderer) and a scout over an empty map would
  produce nothing. It *is* escalated to the Admiral as a triage candidate, because every commander
  dispatched into this repo will hit the same degraded orientation.
- `docs/agents/engine-config.json`, named in this spine's own `context` imperative, does not exist
  here. `docs/CHECKLIST_SCHEMA.md` stands in for it; the substitution is recorded in the receipt.

## Out of scope

`checklist_engine.py`'s on-disk format; `validate_spine.py`'s fault set and acceptance boundary;
`docs/agents/*`; `settings.json`; the installer; issue creation (triage candidates route to the
Admiral in the return report); and any redesign of `constraints`' existing meaning on the 970 tasks
that already use it.
