# Design-it-twice Brief: `the projection manifest interface`

Shared brief for the three parallel candidate authors on issue #300 (epic-298, element B).
Read this whole file. You design ONE thing under ONE named constraint. You do not converge —
convergence belongs to the human (Tommy), surfaced via the Admiral.

## The one thing being designed twice

**The projection manifest**: the record, emitted as a free byproduct of every deterministic
assembly of agent-facing context, of *what was loaded and from which canonical revision*.

Design its **interface**: the schema/shape of the manifest, how it is produced, where it is
written, and the API by which a producer emits it and a consumer reads it. You are NOT designing
the corpus, the doctrine, the episode record, or the skill-fragmentation break.

## Count and panel — a surfaced choice

**N = 3 (panel).** Rationale: this is one of epic-298's two declared load-bearing interfaces
(spec §"Load-bearing interfaces and design-it-twice"); the epic's own spec requires design-it-twice
here and the launch order re-rules it non-skippable. "When in doubt, panel."

## Verified baseline at HEAD (b69e6c8) — do not re-derive, do not contradict without evidence

- Canonical storage is **Markdown in git**. No database, no query language, no new backend.
  This is Tommy's explicit direction in the confirmed spec (`decision:markdown-in-git`).
- The **deterministic selector already exists**: `scripts/checklist_engine.py`'s `current` verb is
  exactly `render_human(state(cl))`, where `state(cl) -> dict` is a **pure** state projection port
  (ports-and-adapters, added in issue #227) carrying a `contract` version int. It selects the
  active spine step off spine state and prints that step's `imperative`. See
  `docs/CHECKLIST_ENGINE_DESIGN.md` §"Answerability: `current` as a complete briefing".
  Note: **no public `--json` flag ships today** — the doc states a JSON adapter is `json.dumps`
  behind a flag "once a consumer exists".
- The **assembly does not exist**. Canonical Markdown is named only *inside imperative prose*
  (e.g. `references/global-orchestrator.md`, `references/global-everyone.md`,
  `docs/agents/ORCHESTRATOR_CONTEXT.md`, `.agent-work/LESSONS.md`,
  `templates/MISSION_FRAME.template.md`) and opened by hand by the agent. There is no
  machine-readable declaration of that set, no assembler, and no record of what was loaded.
- Spine shape: `{work_id, type, config_ref, items, tasks, consolidation, triage_candidates,
  blockers}`; `items` is an ordered list of step-id strings; each `tasks[<id>]` has
  `id, title, imperative, preconditions, postconditions, constraints, directives,
  child_checklist, status, status_detail, result, finding, evidence, rework_count`.
- No projection generator and no context manifest exist anywhere (`grep -rniI projection|manifest`
  over `scripts/ skills/ docs/ tests/` returns only the engine's *internal* state projection,
  the installer's `TEMPLATES_MANIFEST.json`, and `file_issue_set.py`'s issue-set manifest).
- Platform: this corpus is developed on **Windows**. Line endings (CRLF vs LF), filesystem
  ordering, and locale are the named real irreproducibility sources.

## Fixed for all candidates (constraints you may NOT trade away)

1. **Acceptance criteria, verbatim from the issue**: a manifest is produced on *every*
   deterministic assembly; **revision identity is present**; the manifest is **consumable as the
   episode record's context field**.
2. **Stochastic boundary (spec B0.1)**: between canonical truth and an agent's active surface,
   every transformation is **deterministic and attributable**. No semantic routing, no LLM
   inference at assembly time. The manifest must be a pure function of (canon, selector state).
3. **Extend, do not parallel** (`decision:extend-dont-parallel`): bind to the existing spine/engine
   selector. Do not design a second, independent assembly path.
4. **Delivery, not use.** The manifest answers *what was made available, at which revision*. It is
   explicitly NOT an access trace and NOT transcript analysis — both are named out of scope by the
   issue. A design that quietly widens toward proving *use* is wrong, not ambitious.
5. **No foreclosure of Stratum A** (`decision:no-foreclosure`): the epic's long-arc truth model is
   *assertions with a source, supporting/challenging evidence, and a qualitative weak/medium/strong
   strength*. You are not building it. Your record must not make it harder to build **over** later.
6. **Determinism is the acceptance test**, exercised not asserted: rebuild from a clean checkout in
   a **second environment**, with a **declared exclusion set** for legitimately varying fields
   (timestamps, run ids) kept **separate from content**. Design so that exclusion set is small,
   explicit, and structurally separable — not scattered through the record.

## Concurrent sibling — an obligation, not a licence

Issue **#301 (episode record + durable store)** is being designed *right now* in a separate
worktree by a different Commander. Your manifest must be **consumable as the episode record's
context field**. You must **not** design or assume the episode record's internals. State the
obligations #301 can rely on (what it can count on your manifest carrying, and its identity/
addressing so an episode can point at one). If you find yourself needing to change something on
#301's side, say so explicitly as a flagged cross-interface risk — do not design around it silently.

## YOUR constraint

Your dispatch message names exactly one of:

- **minimal-interface** — the smallest manifest that satisfies the three acceptance criteria and
  nothing else. Every field must earn its place; your bias is deletion. Ask of each element: what
  breaks if this is absent? If nothing breaks today, it is out. You are the YAGNI arm of the panel.
- **ports-and-adapters** — mirror the seam the engine already uses. The manifest is a *pure
  projection* behind a port with an explicit contract version, with rendering/serialisation as
  swappable adapters. Your bias is that the record's in-memory shape, its on-disk encoding, and its
  consumers are three separable concerns. You are the seam-placement arm of the panel.
- **common-caller-first** — design backward from the actual first consumers. There are three known
  ones: (a) #301's episode record `context` field; (b) the **drift check** (spec B3: regenerate the
  projection from current canon, diff against the committed artifact, fail loudly on mismatch —
  this is issue H/#307's territory but the manifest is its input); (c) a human reading a git diff to
  review what agents will actually see. Your bias is that the shape the callers want beats the shape
  that is theoretically clean. You are the fitness-for-use arm of the panel.

## Compared on (score YOUR OWN candidate honestly on all four, plus foreclosure)

- **Depth** — does it hide the right complexity behind the seam, or leak it upward to every caller?
- **Locality** — is the change contained, or does it fan out across the codebase?
- **Seam placement** — is the boundary drawn where the caller and the tests actually want it?
- **Testability** — can each pathway be exercised and *falsified* on its own? Specifically: how does
  a test make your design return a **wrong** answer (a false FAIL on a valid input, a silent PASS on
  an invalid one)? A round-trip over the real shipped corpus proves the corpus is clean, NOT that
  your tool is correct — say what adversarial fixture would catch your design being broken.
- **Foreclosure risk** — how hard would it be to express your manifest entries as Stratum A
  assertions later?

## Required output

Write your candidate to the absolute path given in your dispatch message. Structure:

1. **Candidate name and your constraint.**
2. **The shape** — concrete. A worked example of an actual manifest for one real spine step
   (use the Commander spine's `context` step, whose imperative genuinely names
   `references/global-orchestrator.md`, `references/global-everyone.md`,
   `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`,
   `docs/agents/engine-config.json`, `.agent-work/LESSONS.md`). Show real bytes, not a prose
   description of bytes.
3. **Revision identity** — exactly how you establish "from which canonical revision", and what it
   does when the file is uncommitted, untracked, or outside the repo (all three genuinely occur
   here: `docs/agents/` is untracked, `.agent-work/LESSONS.md` lives in a different checkout).
4. **Where it is declared** — how the per-step context set becomes machine-readable, and what
   happens to the prose that currently names those files.
5. **Producer/consumer API** — the call a producer makes and the call a consumer makes.
6. **The exclusion set** — what legitimately varies, and how it stays structurally separate from
   content.
7. **Self-scoring on the five axes above**, including the adversarial fixture that would catch it.
8. **What your constraint made you give up** — the honest cost of your stance.
9. **Obligations you offer #301**, and any cross-interface risk.

Keep it under ~500 lines. Concrete beats exhaustive.

## Hard rules for you

- **Do not modify any repository file.** Write ONLY your own candidate file at the given path.
  You may read anything.
- **Do not converge.** Do not compare yourself to the other candidates. Do not recommend an
  overall winner. You argue *your* constraint's case honestly, including where it hurts.
- You may run read-only commands (`git`, `grep`, `py -c`) to check facts. Prefer checking to
  assuming — the panel's value is that its candidates are grounded.
- **Deliver your result via `SendMessage` to `commander-300` before ending your turn**, with a
  short summary (your candidate's one-line shape, its biggest strength, its biggest cost) and the
  artifact path. A bare idle notification with the report undelivered costs a round-trip.
