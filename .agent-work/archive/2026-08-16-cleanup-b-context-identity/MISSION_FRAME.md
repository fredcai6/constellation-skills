# Mission frame — cleanup-b-context-identity (#600, #500)

> **Revised 2026-08-16 by leg 2** against `ADMIRAL_RULING-1.md`, which answers leg
> 1's `FLOAT_TO_ADMIRAL.md`. Sections marked **(R1)**–**(R5)** changed; everything
> else is leg 1's and stands. The measurement is accepted and is not redone.

## Intent

Make a context reading belong to an **agent** instead of to a **folder**, so an
agent is never governed by a number it did not produce.

Scope declared per the launch order's Budget section as amended by the ruling's
Scope-for-the-relaunch section: **the measurement plus #600 under R1–R4 ship this
wave; #500 ships under R5 if context allows, and otherwise hands back on
`DESIGN_500.md`, which is already written and accepted.**

## What the Admiral ruled (the amendment this revision carries)

`decision:identity-not-time` is **amended, not satisfied**. Identity handles the
**concurrent** case; time handles the **sequential** one. The frozen order's
"#601's comparison should end up unnecessary" is **withdrawn** — it was written
before the measurement and the measurement contradicts it. So this wave:

- **fixes** the confirmed defect — concurrent agents clobbering one file, which the
  timestamp guard is structurally blind to because a foreign write is *fresh*;
- **does not complete** `identity-not-time`. Passing the harness identity into the
  engine remains the only route to that, and is out of scope this wave.

The return must state that limit rather than claim the decision is discharged.

## Map confidence, staleness, disputes

`map_orient.py orient` returned **DEGRADED-UNPARSEABLE**, `anchor_count: 0`:
`map/ids.jsonl` is empty and every `map/<module>/INDEX.md` target linked from
`map/INDEX.md` is absent. The orientation receipt at
`.agent-work/cleanup-b-context-identity/map-orientation.json` discharges this with
five hash-pinned substitutes. Every anchor below is one of those substitutes.
There is no packet map to be stale against; the risk is the opposite — no map at
all — so this frame is built from prose and from measured artifacts.

## Structural anchors (the hash-pinned substitutes)

- `docs/GAUGE_WRITER_HOOK.md` — the writer's wiring, the binding-store shape, the
  enumerated skip-on-uncertainty set, and the two named residuals. The charter-lite
  carrier for the write side.
- `map/INDEX.md` — names the three modules in scope: `scripts.gauge_reader`,
  `scripts.hooks.gauge_writer_hook`, `scripts.checklist_engine`.
- `.agent-work/cleanup-b-context-identity/LAUNCH_ORDER.md` — the frozen principal:
  mission, pre-rulings, latitude, file ownership, fences.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — subsystem rigor: workflow mechanisms are
  a *strengthened durable system*, so targeted automated tests **plus** the
  relevant broader suite.
- `docs/agents/GLOSSARY.md` — `gauge`, `trip`, `lease` carry fixed meanings; this
  frame and every artifact use them and add no synonyms.

## Affected capabilities

The Context Governor's ownership decision: which reading, if any, an engine gate
judges an agent against. Write side (`gauge_writer_hook.py`), read side
(`gauge_reader.py`), policy side (`checklist_engine.py`'s trip block).

## The measured claim this frame is built on

Candidate 2 is **confirmed**, by the real `handle_post_tool_use` in a fresh
process (`measurement/probe_cross_key.py`, output in `probe_cross_key.out`):

- `resolve_gauge_path` enumerates candidates for **one** binding key; the
  ambiguity guard is `len(gauge_paths) > 1`, i.e. **within-key**.
- Two *distinct* keys bound to two spine files in one `.agent-work/<work-id>/`
  each resolve to exactly one candidate, each take the clean single-candidate
  branch, and each write. Measured: an orchestrator's `0.9` overwrote a dispatched
  agent's `0.02` at the same path. No `gauge-skip.json` was written — nothing
  even noticed.
- The overwrite is **fresh**, so `observed_at > claimed_at` and
  `_reading_predates_claim` is False: #477/#601's timestamp guard is
  **structurally blind** to it. It can only catch a reading *older* than the
  claim, which is candidate 1's shape.

## Governing constraints and assumptions

- Isolation is git-only. `gauge_writer_hook.py` is hook code and cannot be
  validated from inside the session that contains it; validation runs in a fresh
  process, never a fixture that hand-injects `CLAUDE_PROJECT_DIR`.
- Measured departure from the launch order's assumption: in this session
  `CLAUDE_PROJECT_DIR` is **unset**, so the hook resolved the project dir from cwd
  and bound `path_source: payload_cwd` into the worktree. The #269 hazard did not
  bite as described here.
- Clear `__pycache__` before every measurement (#597).
- Local Linux is the only real signal; CI is one `windows-latest` job, red at
  baseline.

## Decision anchors and decision pressure

Inherited from the launch order:

- `decision:identity-not-time` — **(R1) amended by the Admiral on the human's
  ruling.** Ownership of a *concurrent* reading is decided by identity: the gauge is
  written to `gauge-<owner>.json`, keyed on the lease session id, and the record
  also carries an `owner` field (the cold critic's graft — the filename makes the
  collision impossible, the field makes a mismatch *detectable* if one ever
  reappears). #601's timestamp comparison **stays, permanently and by design**, for
  the *sequential* relaunch case, where identity cannot help because a relaunch
  reuses its predecessor's lease name. The pre-ruling's "should end up unnecessary"
  is withdrawn.
  @grade: settled/human (amended) · leans g1-implement
- `decision:unattributable-means-no-reading` — a reading the caller cannot be shown
  to own yields `None`, and `None` means no trip. Fail **open**.
  @grade: settled/measured · leans g1-implement
- `decision:no-new-state-file` — attribution rides in the record or the filename,
  never a fifth store.
  @grade: guess · leans g1-implement · settle: if per-agent filenames prove unworkable, float rather than adding a store
- `decision:measure-before-design` — settled by captured artifacts before any
  design freezes. **Discharged**: the probe ran and confirmed candidate 2 before
  this frame was written.
  @grade: settled/measured · leans g0-measure

Raised by this run:

- `decision:owner-in-the-filename` — **(R1) settled, and widened to filename *plus*
  field.** Attribution rides in the gauge **filename** (`gauge-<owner>.json`),
  because a filename *removes* the collision where a field only *reports* it: with a
  shared file the loser gets no reading at all and the governor goes dark for
  exactly the crews it exists to govern. The `owner` field ships alongside it, so a
  reading whose filename and record disagree is visible rather than silent. Full
  comparison in `PLAN_ALTERNATIVES.md`.
  @grade: settled/human · leans g1-implement
- `decision:normalize-never-reject` — **(R2) settled by the human.** Every lease
  session id yields a usable owner key: **slug plus hash**, never a rejection.
  Measured: **82 of 398** distinct session ids in this checkout fail the allowlist
  leg 1 proposed, because slash-bearing lease names are current fleet practice.
  Rejecting an unusable owner would take the governor away from a fifth of the fleet
  *permanently and invisibly* — losing the governor never shows up as a test
  failure, and this repo has been burned twice by silent governors (#252, #271) and
  once by a wave-long dark one (#488). A normalization that is ugly and total beats
  an invariant that is clean and partial.
  @grade: settled/human · leans g1-implement
- `decision:no-lease-keeps-todays-behaviour` — **(R3) settled by the Admiral;
  replaces leg 1's `decision:no-shared-file-fallback`.** Owner-keying applies **only
  where a lease exists**. With no lease there is no owner, so the engine reads the
  unowned `gauge.json` and trips on it *exactly as today*. Going quiet there is the
  permit direction and so inside latitude, but it is a real loss of coverage on
  checklists that are governed today, and taking it as a side effect of a rename is
  how coverage disappears without anyone deciding it should. Fail-safe stays "no
  attributable reading yields `None`"; it does **not** become "no lease yields
  nothing". Where a lease *does* exist and no owner-keyed gauge resolves, the reader
  still returns `None` and does not fall back to the shared file.
  @grade: settled/admiral · leans g1-implement
- `decision:ambiguity-guard-is-about-attribution` — **(R4) settled by the Admiral.**
  `resolve_gauge_path`'s `len(gauge_paths) > 1` skip exists because the writer could
  not tell *whose* reading it held when one key bound two spines. With the owner in
  the filename that question is answered by construction. So: dedupe by resolved
  **owner-keyed** path, write **every** distinct candidate, and fire the guard only
  when a candidate cannot be attributed an owner at all. Two spines in one work
  directory under the same owner still collapse to one file — #488's own case, which
  must stay working and is pinned by a test in #488's exact shape.
  @grade: settled/admiral · leans g1-implement
- `decision:consume-on-lease-change` — **(R5) settled by the Admiral**, no longer a
  guess; the settle condition is answered by `DESIGN_500.md`. Option (a): a re-claim
  retires the agent's **own** pending refresh-request, so its next `start` is
  refused where today it is released. That closes the residual #601 named as a known
  cost. The practical effect is one extra step, not a stall — an agent over the band
  attaches its own refresh-request and then starts, which is the legal sequence the
  launch-order template now teaches. Option (b), exempting a same-`session_id`
  re-claim, is declined: it preserves today's behaviour by refusing to serve the one
  case #500 exists for.
  @grade: settled/admiral · leans g2-implement-500
- `decision:one-owner-key-definition` — **raised by leg 2, not ruled.** The owner
  key is computed on both sides of a process boundary: the hook derives it from the
  binding entry's `engine_session`, the engine from its own active lease
  `session_id`. If the two definitions ever drift, every reading silently stops
  resolving. Recommendation: **one definition** in `scripts/gauge_reader.py`, loaded
  by the hook through the by-path loader idiom the codebase already uses twice
  (`gauge_writer_hook._load_spine_rail`, `checklist_engine._load_gauge_reader`),
  with the existing fail-safe — a load failure yields no owner, which is
  today's behaviour, not a new refusal. The alternative the repo already practises
  for the two sidecar *constants* is deliberate duplication with a literal on each
  side; that is defensible for a constant and weak for a function.
  @grade: guess · leans g1-implement · settle: a cross-module test that asserts both sides produce the identical key for the same session id, including a slash-bearing one

## Claims and evidence surfaces

- `tests/test_checklist_engine.py::TripGaugeReadingOwnership` — #477's guard and
  #601's two relaunch tests. New ownership tests belong in or beside it.
- `tests/test_gauge_writer.py`, `tests/test_gauge_reader.py`,
  `tests/test_gauge_chain_writer_to_trip.py` — the end-to-end chain with real OS
  subprocesses; the natural home for the acceptance probe.
- Evidence standard, from the existing class: drive the **real** reader and a
  **real** gauge file, never a patched `_read_gauge`.

## Out of scope

- `scripts/hooks/spine_rail.py`, `scripts/run_crew.py` (lane C);
  `scripts/mcp_spine_server.py`, `.mcp.json` (lane A). Fenced.
- `checklist_engine.py`'s claim path (#601 landed on `main` this morning) — left
  alone; this design does not require touching it.
- **(R1)** Completing `identity-not-time` — passing the *harness* identity into the
  engine. This wave fixes the concurrent collision only; the timestamp comparison
  stays for the sequential case.
- **(R5)** #500's implementation is **no longer out of scope**: it ships if context
  allows, and otherwise hands back on the already-accepted `DESIGN_500.md`. The
  boundary is declared at the gate, not run past.
- The 150K absolute cap being reachable on turn one for a design wave. The launch
  order names this as intended and not this lane's defect.

## Interaction to watch

Lane C is fixing #549 concurrently — an orchestrator's Stop hook seeing a
subordinate's spine through `session_view`'s per-agent merge. That is the same
neighbourhood as the confirmed candidate 2. **If C lands first, re-measure.**
