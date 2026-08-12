# Common brief for all three plan-alternative candidates

You are one of **three** independent candidate authors. You do **not** see the other two. You produce
**one** candidate design + gate plan under **one** named constraint, which your own handoff gives you.
Do not hedge toward the middle: your job is to push your constraint hard so the comparison has real
contrast. A candidate that reads like a compromise of all three constraints is a failed candidate.

**You write a document. You change no code.** Do not edit, create or delete anything outside your
own result path. Do not run `git` write operations.

## The problem

Today a human or an Admiral hand-authors every spine: gates, imperatives, and check commands. The
check command is where it breaks. A check is a shell string typed from memory, and a wrong one does
not announce itself — it exits 0 and the gate opens on nothing.

Measured last wave: of ~10 hand-authored work spines and 7 review surveys, **four carried checks that
could not do their job**, and **none was caught by its author**:

1. an unquoted pytest selector — `-k Door or Tie or Registry` — which the shell split into words, so
   the command never selected what it claimed to;
2. a probe running `python -c 'import mcp_spine_server'` with no spine bound, which raises `KeyError`
   at import time, so the probe could only ever fail;
3. a call written as `build_entry(session=...)` where the function's parameter is `work_id=` —
   argparse refused before anything ran;
4. a population filter wrong twice: first over-broad to all of `.agent-work/`, then narrowed by
   filename substring to 14 files when the real population was 25.

**The mission:** build a **spec format** an author can write without knowing the engine's JSON shape,
and a **generator** that emits a spine from it — one that **refuses any spec whose output
`scripts/validate_spine.py` would reject**. Then write **role specs** for at least the implementer
and the reviewer, and prove a spine generated from one **drives to a terminal state in a real
dispatch**.

## What you must read first (all in your worktree)

- `.agent-work/epic-559/c2-generate-the-spine/PROBLEM_STATEMENT.md` — the confirmed problem and
  protected intent.
- `.agent-work/epic-559/c2-generate-the-spine/MISSION_FRAME.md` — the map-first frame, its decision
  grades, and the measurements.
- `scripts/validate_spine.py` — **the acceptance oracle.** 665 lines. Read all of it. `validate(spine,
  repo_root=...)` is importable and returns a `ValidationResult` (a `list[Fault]` with an extra
  `.undecidable` channel). Its docstring already names "a future spine generator" as its caller.
- `docs/CHECKLIST_SCHEMA.md` — the engine's on-disk contract. The `Task` table, the `Condition` table,
  the three check kinds (`command`, `artifact`, `git-change-policy`), and §Rendering.
- `scripts/checklist_engine.py` lines 2089–2140 (`_directive_leaf`, `_render_directive_lines`) and
  2180–2195 (`render_human`) — exactly how `constraints` and `directives` reach the agent.
- `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` and
  `skills/reviewer/templates/REVIEW_SURVEY.template.json` — the two role checklists whose specs the
  generator must be able to produce.
- `scripts/init_work_area.py`, specifically `_RESOLVER_OWNED_TOKEN_RE` and `resolve_spine`.

Run this yourself and paste the output into your candidate — it is the baseline every candidate is
judged against:

```
python scripts/validate_spine.py --sweep --root .
```

## Fixed for every candidate — not yours to redesign

- `checklist_engine.py`'s **on-disk format does not change.** The generator emits what the engine
  already reads.
- `scripts/validate_spine.py`'s **fault set and acceptance boundary do not move.** It is the oracle;
  moving the oracle to make output pass is how a check stops meaning anything.
- Beliefs, concerns and open questions ride in the **`constraints` / `directives`** substrate the
  engine already renders on the active gate — never a new field the engine ignores.
- **No shipped template is edited** to make generator output validate. A disagreement between a
  shipped template and the generator is a *finding*, not a fix.
- A `<placeholder>` is legitimate **in a template** and a fault **in an instance**; the generator
  refuses an instance that carries one. The resolver-owned families (`<work-id>`, `<repo-root>`,
  `<*-skill-dir>`, `<skill-dir>`, `<*-session-id>`) are **not** placeholders in this sense —
  `init_work_area.resolve_spine` substitutes every one before a spine is driven.
- A gate with **no checkable postcondition must say in so many words that it is qualitative.**
  Silence is refused; the stated form is accepted.

## The two properties the output must carry

1. **Every gate carries a place to record beliefs, concerns and open questions.** A crew that has to
   hand something back needs a gate to hand it back at. Measured on the base commit over 560 spines /
   4341 tasks: `constraints` is populated on **970** tasks and is **always** `list[str]` meaning
   *rules this gate must respect*; `directives` is populated on **22** tasks and is **always**
   `dict[name -> contract]` meaning *a standing contract this gate must satisfy*. Design against what
   is actually there.
2. **Judgment is carried up, not buried.** The human's rule, verbatim: *"as a general rule, judgement
   should be highlighted and brought to the higher level. greater claim requires greater review."* A
   generated spine should make a large claim visible to whoever reviews it rather than letting it sit
   inside a gate nobody looks at. **How** is a design question and it is squarely part of your
   candidate.

## The idiom your design must be able to emit

The corpus's documented way to make a test gate self-checking:

```
test $(pytest -q -k 'Selector' --collect-only 2>/dev/null | grep -c '::') -ge 4 && pytest -q -k 'Selector'
```

Quote the `-k` selector. An unquoted one is defect 1 above.

## The settling question — answer it explicitly

> Does your spec still ask its author to type a shell command from memory?

If yes, **the defect has moved rather than gone**, and saying so plainly is worth more than a
clean-looking design. Answer it for *your* candidate, in one paragraph, with the concrete evidence:
show what the author of an implementer role spec would actually type under your design.

## Test mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Use `python`, not `python3`. Unsetting the three spine variables matters:
`scripts/mcp_spine_server.py` reads `SPINE_FILE` **at import time** and raises `KeyError` without it.
Baseline at this commit: **2689 passed, 3 skipped, 1121 subtests** in ~107s. You are not required to
run the suite (you change no code), but any test command you *propose* must be one you have shown
collects a non-zero number of tests.

## What your candidate document must contain

1. **The constraint you were given, named**, and one paragraph on how you pushed it.
2. **The spec format** — its file type, layout and vocabulary, with a **complete worked example**: a
   real implementer role spec written in your format, long enough to be judged, not a fragment.
3. **The generator** — its module shape, its CLI, where it calls `validate()`, and exactly what it
   refuses and with what message.
4. **How the two non-optional properties are realized**, concretely, in emitted JSON — show the
   emitted `constraints`/`directives` for one gate and show what `current` would render for it.
5. **The gate plan** — an ordered list of gates, each with: id, title, what it delivers, its close
   criteria (what evidence closes it), and whether it is a crew gate (implement + review + integrate)
   or a reasoning gate (no crew, deliverable is a document, crew-waiver reason stated). Sequence so
   verification stays green at every gate boundary.
6. **Self-scoring on the four axes** — Depth, Locality, Seam placement, Testability — one honest
   paragraph each, including where your constraint made your candidate *worse*.
7. **The settling question**, answered as specified above.
8. **The strongest argument against your own candidate.** One paragraph. A candidate with no stated
   weakness reads as unexamined.

## Stop conditions

Stop and write what you have if: the oracle would have to move for your design to work (say so —
that is a finding, and it is a float to the Admiral, not something you patch); or the engine format
genuinely cannot carry something the mission needs (say what and why).

## Return format

Write your candidate to the result path your handoff names, **before you end your turn** — that write
is the delivery. Then return a short message: your constraint, your one-sentence recommendation, and
the result path. Return thin, write fat.
