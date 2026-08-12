# Problem statement — C2: generate the spine from a spec instead of writing it by hand

**Work id:** `epic-559/c2-generate-the-spine` · **Base:** `0ab7ecab` · **Mode:** delegated (frozen
`LAUNCH_ORDER.md`, Admiral `admiral-epic-418-followon` is the ratifying tier).

Reconciled against the launch order rather than derived by interrogation, per the delegated
`understand` path. Everything below is either quoted from the order or measured by me on the base
commit.

## The problem

A spine is hand-authored today, and the part that breaks is the **check command**. A check is a shell
string typed from memory. A wrong one does not announce itself: it runs, exits 0, and the gate opens
on nothing.

Measured, from the order's Prior-Wave Verdicts: of roughly **ten work spines and seven review
surveys** the Admiral hand-authored in wave 5, **four carried checks that could not do their job** —
an unquoted `-k` selector the shell split into words; a probe that could only ever raise; a call
using a flag argparse does not define; a population filter wrong twice in opposite directions.
**None was caught by its author.** Each was found downstream.

The epic's thesis applies one level up: prose instruction is a liability because the reader may be
weaker than the writer — and a hand-authored check is that same liability, held by the *author*, so
it does not go away by making the author more capable.

## What exists at base (verified by me, not assumed)

- `scripts/validate_spine.py` (665 lines, shipped by C1 at `0ab7ecab`) **refuses** a bad spine. Its
  `validate(spine, repo_root=...)` is importable and returns a `ValidationResult` — a `list[Fault]`
  carrying a third `.undecidable` channel. Its own docstring anticipates this mission: *"so a future
  spine generator can refuse to emit past it"*.
- **Nothing writes a good spine.** `ls scripts/ | grep -iE 'gen|spec|author|emit'` returns only
  `agent_work_root.py` and `verify_spec_confirmed.py`; a tree-wide grep for
  `generate_spine|spine_spec|spec_to_spine` returns nothing. The order's assumed baseline holds —
  there is no already-shipped generator I would be duplicating.
- My own lint baseline, `python scripts/validate_spine.py --sweep --root .`, reproduces the order's
  stated baseline exactly: 12 templates discovered; `ADMIRAL_SPINE`, `CYCLE`, `INTERROGATION`,
  `REVIEW_SURVEY` are `OK`; `falsifiable-all-null` on the context gate of nine of twelve; the two
  `<exact test command>` placeholders in `EXECUTE_PLAN.template.json` (`g1-integrate.c1`) and
  `IMPLEMENTER_PLAN.template.json` (`m1.c2`).

## The substrate, measured on base

The order's counts reproduce. Over every engine-driven checklist in the tree — **560 spines, 4341
tasks**:

| field | populated tasks | shapes seen |
|---|---|---|
| `constraints` | 970 (22%) | `list[str]`, every one |
| `directives` | 22 (0.5%) | `dict[name -> contract]`, every one |

Read before redefining, as the order instructs:

- **`constraints` already means "rules this gate must respect."** All three populated shipped-template
  instances are that: `"<inherited project or section rules>"`, `"<inherited handoff rules>"`, and the
  Fowler pair (*"smells are subordinate to documented repo standards"*, *"an override needs a logged
  reason"*). Beliefs, concerns and open questions are **not rules**. Putting them here would overload
  a field 970 tasks already use for something else.
- **`directives` means "a standing contract this gate must satisfy,"** and it is all but unused — 22
  tasks, four distinct contracts (`replan_input`, `wave_transition`, `shaped_brief`), mostly the same
  ones copied across archives. `checklist_engine.py::_render_directive_lines` (line 2104) renders the
  dict shape as `name:` plus one indented `field: value` line each, and the flat `[str]` shape as one
  line per item; `render_human` emits the block on the **active gate** (line 2189). That is more
  structure than `constraints` offers, and it is the field that can be given a job without breaking
  anyone.

## Protected intent — what must be true of the result

1. **A spec format an author can write without knowing the engine's JSON shape**, and a **generator**
   that emits a spine from it, which **refuses any spec whose output `validate_spine.py` would
   reject**. The oracle is not moved: moving it is a float, not a patch.
2. **Every generated gate carries a place to record beliefs, concerns and open questions**, riding in
   `constraints`/`directives` — substrate the engine already renders — never a new field the engine
   ignores. A crew that must hand something back needs a gate to hand it back at.
3. **Judgment is carried up, not buried.** Verbatim human rule: *"as a general rule, judgement should
   be highlighted and brought to the higher level. greater claim requires greater review."* A generated
   spine makes a large claim visible to its reviewer rather than letting it sit inside a gate nobody
   opens.
4. **Role specs for at least the implementer and the reviewer**, and **a spine generated from one
   proven to drive to a terminal state in a real dispatch** — `run_crew.py` judges a spine-only
   dispatch on `spine_terminal`, not on a result artifact.
5. **The settling question, answered honestly:** does the role spec still ask its author to type a
   shell command from memory? If yes, the defect **moved rather than went**, and saying so is worth
   more than a clean-looking result (Honest-Null Clause).

## Governing constraints carried into planning

- `decision:no-engine-format-change` (`settled/human`) — the on-disk format does not change; the
  generator emits what the engine already reads.
- `decision:notes-ride-in-existing-substrate` (`settled/human`) — `constraints`/`directives` only.
- `decision:placeholder-template-vs-instance` (`settled/admiral`) — a `<placeholder>` is legitimate in
  a template and a fault in an instance; **the generator refuses an instance that carries one**. The
  resolver-owned families (`<work-id>`, `<repo-root>`, `<*-skill-dir>`, `<skill-dir>`,
  `<*-session-id>`) are not placeholders in this sense — `init_work_area.resolve_spine` substitutes
  every one before a spine is driven, which is why `validate_spine` already accepts them.
- `decision:qualitative-must-be-stated` (`settled/admiral`) — a gate with no checkable postcondition
  must say in so many words that it is qualitative. Silence is refused.
- `decision:sonnet-crews` (`settled/human`) — implementers and reviewers run on Sonnet.
- `decision:cold-review-every-change` (`settled/admiral`) — every change gets a cold reviewer
  independent of its implementer, and reworks until that reviewer approves. Reviewers are told that
  both of last wave's caught defects were found by **running** something, not by reading the diff.
- `decision:no-template-edited-to-pass` (`settled/admiral`) — a shipped template is never edited to
  make generator output validate; a disagreement is a finding.

## Map confidence

**DEGRADED, declared.** This repo has no architecture map: `docs/architecture/` is absent,
`map/INDEX.md` is an unfilled template, `map/ids.jsonl` is empty. `map_orient` was discharged with six
hash-pinned substitutes (`docs/CHECKLIST_SCHEMA.md`, `docs/CHECKLIST_ENGINE_DESIGN.md`,
`docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`, `README.md`, `SKILL_INDEX.md`), two
named unmapped gaps, and an escalation to the Admiral. `docs/agents/engine-config.json` — named in the
spine's own `context` imperative — **does not exist in this repo**; `docs/CHECKLIST_SCHEMA.md` is the
engine's on-disk contract and stands in for it. No planning claim below rests on an unverified map
area: every structural fact above was read from source or measured.

## Out of scope

Changing `checklist_engine.py`'s on-disk format; changing `validate_spine.py`'s fault set or
acceptance boundary; editing `docs/agents/*`; filing issues (no issues are created this wave — triage
candidates route to the Admiral in the return report).
