# Launch Order: `commander-231 — issue #231 (epic-226 item E)`

Commanders start cold. Everything you need is pasted below — do not assume you can
open anything referenced by id alone.

## Mission

**Issue #231 — prototyper: three-valued verdicts, captured-to-worktree disposition,
commander understand→prototyper seam.**

Deliverable: a merged-ready PR against `fredcai6/constellation-skills` implementing
all three build items below, with the acceptance evidence pasted into your verdict.

How it serves the epic intent: epic-226 is "spend agent effort on the actual problem
instead of the scaffolding, and seed the step-back capability." Your issue is the
step-back seed directly — it gives a Commander a cheap, named escape hatch (hand a
load-bearing unknown to the prototyper) instead of either guessing past it or building
heavyweight excursion machinery the human has already rejected for commander. The
other two items sharpen the prototyper's own answer/disposition vocabulary so that
escape hatch returns something structurally trustworthy, not free prose.

**Full issue body, verbatim:**

> Spec S7 (deltas from Pocock excursion x2, adapted on merit). Supersedes #224.
>
> Build:
> (a) Three-valued verdicts in PROTOTYPE_RESULT: answered-yes / answered-no /
> not-immediately-right — the third parks with a named revive condition (kills
> premature nulls structurally; pairs with scoped-nulls doctrine).
> (b) Disposition flavor `captured-to-worktree`: prototype kept as a worktree/branch
> reference with a pointer from the owning issue until the human disposes it (human
> ruling: keep until done). Accumulation cap: captured worktrees are swept at epic
> close — re-affirm or dispose there.
> (c) Commander understand-step doctrine paragraph: when a load-bearing unknown is
> answerable by cheap code, hand it to constellation-prototyper via the existing
> PROTOTYPE_HANDOFF (excursions stay cheap — no new machinery; the human explicitly
> rejected heavyweight excursion scaffolding in commander).
>
> Acceptance: prototyper template round-trip test (verdict enum + disposition enum
> accepted by workbench close); the seam paragraph lands in commander understand
> doctrine. Out of scope: task-type excursions (parked on the board), full excursion
> off-ramps in commander.

## Prior-Wave Verdicts (pasted)

None — you are wave 0. No prior-wave verdict exists for this epic.

Relevant settled history you would otherwise have to rediscover:

- **The explorer skill already dispatches the prototyper this exact way**, and its
  pattern is the one to imitate, not reinvent. `skills/explorer/SKILL.md` §"Excursion
  ramps": an excursion is dispatched via a durable background subagent
  (`python <skill-dir>/scripts/run_crew.py`), and "one brief, no double entry" — the
  `EXCURSION_BRIEF`'s prototype-section fields are **identical** to `PROTOTYPE_HANDOFF`'s
  so nothing is typed twice. Your commander seam paragraph is the same contract at a
  different call site: `PROTOTYPE_HANDOFF` in, `PROTOTYPE_RESULT` out, no new fields
  invented, dispatch mechanics reused from `skills/commander/references/crew-dispatch.md`
  rather than authored fresh.
- **#224 is explicitly superseded** by this issue per its own body — do not go looking
  for #224 as a live parallel thread; it is closed by supersession, not by you.
- **Commander's `understand` step already carries two precedent doctrine bullets** in
  `skills/commander/references/commander-core.md` (~line 63–65): "Shaped-design intake
  (`understand`)" and "Feasibility probe (`understand`)" — both a short bolded-lead-in
  paragraph naming the step in parens, one paragraph, then moving on. Your new paragraph
  is a third bullet in that same family and style, not a new subsection.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- **PR-7 — VERIFY THE ISSUE'S CLAIMS AGAINST THE CODE BEFORE PLANNING.** Already done
  once at launch-order-authoring time; **re-verify it yourself before freezing a plan**,
  code drifts between authoring and dispatch:
  - `skills/prototyper/templates/PROTOTYPE_RESULT.template.md` currently has a freeform
    `## Answer` field (no enum) — item (a) is a genuine gap, not already shipped.
  - `skills/prototyper/SKILL.md` §"Closeout: disposition is mandatory" currently lists
    exactly three dispositions: `deleted`, `absorbed`, `parked-with-owner`. There is
    **no** `captured-to-worktree` anywhere in the repo outside the issue text itself
    (checked: `skills/prototyper/**`, `docs/CONSTELLATION_OVERVIEW.md`,
    `skills/explorer/templates/EXCURSION_BRIEF.template.md`) — item (b) is a genuine
    gap, a fourth disposition value to add, not a replacement for any of the three.
  - `skills/commander/references/commander-core.md` has no prototyper/excursion mention
    at all (grepped for `prototyper`, `PROTOTYPE_HANDOFF`, `excursion` — zero hits) —
    item (c) is a genuine gap.
  - If your own re-check finds any item already shipped, that is an **honest null for
    that item** — report it as a complete result with scope stated, per the Honest-Null
    Clause below, and spend the effort on what is genuinely missing.
- **PR-6 — CANONICAL DOCTRINE SOURCE.** Item (c)'s target is
  **`skills/commander/references/commander-core.md`** — this is the commander skill's
  own owned doctrine file, **not** an install-time regenerated copy. Confirmed by
  reading `scripts/install_constellation.py`'s `_GLOBAL_EVERYONE` /
  `_GLOBAL_ORCHESTRATOR` / `_GLOBAL_CREW` / `_GLOBAL_ALL_TIERS` tuples (lines ~98–101):
  they name exactly `global-everyone.md`, `global-orchestrator.md`, `global-crew.md`,
  `design-it-twice-brief.md`, `windows.md` — `commander-core.md` is not among them, so
  it is not silently overwritten at install time. **Do not** target any
  `skills/<role>/references/global-*.md` for this edit — those ARE the regenerated
  copies and an edit there is silently overwritten. Confirm this reading yourself
  against the current `install_constellation.py` before editing, and state the
  confirmed target file explicitly in your verdict.
- **PR-2 — NO CI EXISTS YET.** `.github/workflows/` does not exist in this repo; issue
  #229 is building it in parallel with you. Your PR therefore has **no status checks**.
  Your acceptance evidence is the **locally-run** `py -m pytest tests/ -q` exit code and
  tail, pasted into your verdict. Do not wait for, or claim, a green CI run.
- **PR-4 — WORKTREE ISOLATION IS NOT FREE.** The Agent-tool `isolation:"worktree"` flag
  is a silent no-op on Windows. Your worktree is real because the Admiral provisioned it
  with `git worktree add` — verify with `--here`, do not create your own.
- **PR-8 — STAY IN YOUR LANE ON #219/#220.** If you find adjacent ergonomics defects
  belonging to #220's surviving items or #219's live threads, **file or comment — do
  not absorb.** Nothing in this issue declares a #219/#220 absorption; unlike #227,
  you have no license to touch either.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable.
Report it with the same rigor as a win. Concretely here: if item (a), (b), or (c)
already exists in the current repo, "item N already shipped — here is the code proving
it, here is what I verified and what I did NOT verify" is a **success**, not a
shortfall. Per repo doctrine, every null states what was tested **and what was not**;
a null with an empty scope is an unfinished result.

## Inherited Latitude

From the epic's latitude contract's decision-class table, applied to this issue:

You may decide, without floating to the Admiral (`[REC] delegated`):
- Implementation shape: exact wording of the verdict/disposition enums, test file
  layout, where in `commander-core.md` the seam paragraph lands (as long as it is the
  `understand`-step family described above), naming.
- The **doctrine edit item (c) specifies** — this is the exact edit the issue names,
  so it is delegated per the contract's "Doctrine / shipped-template edit" row, **once
  you have confirmed the canonical target per PR-6** and said so in your verdict.
- Narrowing scope where an item proves already-shipped (honest null, evidence pasted).
- Bounded fix-now triage: a small defect you trip over and fix in-lane.
- How you design the "workbench close" round-trip proof — the engine has no
  first-class `evidence_type: prototype-result` today; deciding whether to add one, or
  to prove the round-trip via the engine's generic `artifact`/`match` field-checking on
  an attached artifact, is implementation shape.

You must **float to the Admiral** (stop and return, do not guess) — `[REC] surfaced`:
- **Reshaping doctrine beyond what the issue specifies.** The issue names one paragraph
  in commander's understand doctrine. Anything larger — a new spine step, new engine
  machinery, real excursion off-ramps in commander — is explicitly **out of scope**
  per the issue's own last line and per the contract's "Production defaults /
  user-visible behavior" and "Architecture / structural change" rows.
- Adding scope, or dropping any of the three build items for a reason other than a
  measured null.
- Any change to the `PROTOTYPE_HANDOFF`/`PROTOTYPE_RESULT` shape beyond adding the
  named enum and disposition value (e.g., renaming existing fields, changing the
  three existing dispositions' meanings).
- Anything that would require touching another wave-0 issue's files (see File
  Ownership fences below).
- A genuine ambiguity in what "accepted by workbench close" is supposed to mean beyond
  what PR-6/Inherited Latitude above already resolves for you.

Asking up is always sanctioned. If you need epic-level context this order does not
carry, **return-and-query the Admiral** — it answers and continues you. That is a
first-class move, not a failure.

## File Ownership

**Sole writer this wave** of:
- `skills/prototyper/templates/PROTOTYPE_RESULT.template.md` (item a, b)
- `skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md` (only if the enum
  additions require a mirrored reference there — check before editing)
- `skills/prototyper/SKILL.md` §"Closeout: disposition is mandatory" and §"Scoped
  nulls" (item a, b — the disposition list and the verdict vocabulary)
- `skills/commander/references/commander-core.md` (item c — the new understand-step
  paragraph ONLY; do not touch any other section)
- A new test module for the round-trip proof (e.g.
  `tests/test_prototyper_templates.py` — name it yourself; `tests/test_explorer_templates.py`
  is the closest existing analog, drive real fixtures against real verifier code, not a
  hand-injected shortcut — see `lesson:verify-harness-field-and-drive-real-writer` below)

Your findings file: `.agent-work/epic-226/evidence/findings-231.md` — you are the
**sole writer** of this document.

**Fenced — do not write:** `scripts/checklist_engine.py` (#227 owns it this wave),
`.github/workflows/**` (#229), `scripts/install_constellation.py` (#228),
`scripts/grade_lint.py` and planning templates (#230), any other role's `skills/*/`
tree beyond the two files named above under `skills/commander/references/` and
`skills/prototyper/`.

## Workspace

Absolute worktree path: `C:/Programs/constellation-wt-231`
Branch: `issue-231` · Base: current `main`
Provisioned by the Admiral with:
```
git worktree add C:/Programs/constellation-wt-231 -b issue-231 main
```

**First step, before any git operation:** run
`py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-231`
— it must exit 0, proving you are in your own worktree and not the shared checkout.
Paste its output into your return report.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR
itself, not a local merge that would diverge your worktree from main).

## Inherited Context

**This repo VENDORS its own scripts.** `scripts/checklist_engine.py` in the repo root
is the real one — drive the engine from the repo copy, not from any
globally-installed `C:/Users/fredc/.claude/skills/...` copy. Same for templates:
prefer `skills/<role>/templates/`.

**Active lessons from `.agent-work/LESSONS.md` that bear on your mission:**

- `lesson:verify-launch-order-claims-against-code` (project / delegated-planning, 2
  data points): verify this order's named defects against the current code (grep the
  named symbol/token) BEFORE planning — this order already did that once at authoring
  time (see PR-7 above); re-run it yourself, code may have drifted.
- `lesson:verify-harness-field-and-drive-real-writer` (project / testing): when a
  decision depends on a harness-supplied payload field, verify the field against the
  harness contract AND make the regression test drive the REAL writer path, not a
  hand-injected fixture. **Directly relevant to your round-trip test:** prove the
  verdict/disposition enums round-trip by actually attaching a `PROTOTYPE_RESULT`-shaped
  artifact through the real engine/workbench close path (or the real template-authoring
  path, mirroring how `tests/test_explorer_templates.py` drives
  `verify_spec_confirmed.py` against a real edited fixture) — not by asserting the enum
  strings appear in a string you constructed yourself.
- `lesson:test-harness-concurrency-failsafe` (project / testing): if any test you write
  exercises concurrent file I/O, wrap per-iteration work in try/except with a
  guaranteed stop-signal in `finally`, and mark helper threads `daemon=True`.

**Platform invariants (Windows):**

- **Command-checks run under a POSIX shell (bash).** Author `grep`/`&&`/pipe checks in
  POSIX form. On a box with no bash the engine stamps `shell: cmd-fallback` and the
  check fails visibly.
- **`gh pr create` body:** write the body to a temp file and use `gh pr create -F <file>`.
  Never a heredoc, never a PowerShell `@'...'@` here-string for `--body`.
- Set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you
  capture — cp1252 pipes corrupt captured output silently.
- The Agent-tool `isolation:"worktree"` flag is a **silent no-op** on Windows. Your
  worktree is real because the Admiral provisioned it with `git worktree add` — verify
  with `--here`.

**Charter-lite carrier:** this repo has no `docs/agents/` overlay, so this block is
your doctrine carrier. Beyond it, your inherited globals are
`references/global-orchestrator.md` + `references/global-everyone.md` bundled with
your skill.

**Doctrine you must not re-derive** (it is inherited, not restated per-handoff):
correctness over velocity for promoted behavior; behavior changes are test-led where a
test surface exists; fail visibly rather than emit plausible wrong output; one
canonical path, no speculative abstraction; scoped nulls (a negative result kills THIS
test under THESE conditions, never the idea class — this is doubly load-bearing on
this issue since item (a) exists specifically to structurally enforce it).

## Pre-empted Steps

- **Latitude / authorization:** settled by the Admiral's confirmed latitude contract.
  This launch order IS the ratified intent — satisfy `user-decision` checkpoints on
  your spine by citing it.
- **Issue triage / scoping:** the issue body is frozen as written. Do not re-scope it.
- **Worktree provisioning:** done for you (verify with `--here`, do not create your own).
- **Design-it-twice:** NOT pre-empted. Unlike #227, this issue's body records no
  design-it-twice panel for its three build items — they are small, additive vocabulary
  extensions to an existing contract, not a new load-bearing interface. Run your own
  `understand` step judgment on whether any of the three needs it (most likely: no,
  but say so explicitly rather than silently skipping).

## Data Locations

Untracked inputs absent from your worktree, in the main checkout at
`C:/Programs/constellation-skills`:

- `.agent-work/` (the whole tree — lessons inbox, prior epic archives, the Admiral's
  live spine). **Read-only for you.**
- No external DB/model artifacts are needed for this issue. Item (b)'s "captured
  worktrees are swept at epic close" is a **documented policy in the template/SKILL.md
  text**, not new sweep automation — the issue explicitly says "no new machinery."
  Do not build a sweep script; describe the cap in prose where the disposition is
  defined, per the issue.

## Budget

- **Model tier (required):** **sonnet** — per the latitude contract's Budget/Model
  Parameters row: B #228, C #229, E #231, F #232 all run Commander at sonnet (A and D
  are the two design-heavy issues that get opus; this is not one of them). **Crew:
  sonnet throughout. No Fable at any tier** (standing rule, no exceptions).
- **Compute/time, session-window:** you are one of five concurrent wave-0 Commanders
  drawing on a shared usage pool. Keep crew dispatches tight; do not spawn speculative
  parallel crews. If you hit a session limit mid-flight, write your state to your
  spine and return — do not silently die.

## Stop Conditions

Stop and return when:

- A decision listed as **float to the Admiral** above is needed.
- Your scope would exceed the issue's declared boundaries (task-type excursions, full
  excursion off-ramps in commander — both explicitly out of scope in the issue body).
- The full `pytest tests/` suite goes red in a way you cannot attribute to your own
  change within a bounded effort — return with the failure attributed by a
  `uniq -c`-style command over the failure list, never from the pytest tail alone.
- Budget crossed, or evidence for an acceptance item proves impossible to produce.
- You need **context this order does not cover and cannot safely proceed without** —
  return-and-query the Admiral (it answers and continues you). Asking up is always
  sanctioned.

## Return Shape

Write `.agent-work/epic-226/verdicts/commander-231.md` **in the main checkout's
shared `.agent-work/`** (git-common-dir resolution points the durable trio at one
shared root) containing:

1. **Verdict** — per build item (a, b, c): SHIPPED / HONEST-NULL (already existed,
   with the code evidence) / BLOCKED (with the reason). For item (c), state the
   confirmed canonical target file explicitly (per PR-6) even though it resolves to
   the expected `skills/commander/references/commander-core.md` — say so, don't just
   imply it.
2. **Evidence** —
   - `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-231`
     output (the matched worktree path), proving you worked in isolation.
   - `py -m pytest tests/ -q` exit code + tail, run on your branch.
   - The new round-trip test(s), named, with pass output, and a one-line statement of
     how they avoid the hand-injected-fixture trap (`lesson:verify-harness-field-and-drive-real-writer`).
   - The exact diff/paragraph added to `commander-core.md` for item (c), and where it
     landed relative to the "Shaped-design intake" / "Feasibility probe" bullets.
   - The PR number and URL.
3. **Map impact** — what capabilities/seams changed, for the Cartographer's reconcile
   (the new commander→prototyper seam is itself a map-relevant edge).
4. **Triage candidates** — out-of-scope discoveries, each as a one-line statement.
5. **Workflow feedback** — friction in this launch order, the spine, or the tooling.
   Be blunt; this is the lessons audit's input.

**Deliver before going idle.** Write your result artifact and send your verdict
**before** you go idle: an idle notification with no artifact reads as stalled, not
done. The Admiral judges completion from what you produced, not from a message that
arrives after you have gone quiet.

When you open the PR on Windows, write the body to a temp file and use
`gh pr create -F <file>`.
