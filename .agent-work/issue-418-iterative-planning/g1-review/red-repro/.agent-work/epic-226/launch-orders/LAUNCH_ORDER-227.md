# Launch Order: `commander-227 — issue #227 (epic-226 item A)`

Commanders start cold. Everything you need is pasted below — do not assume you can
open anything referenced by id alone.

## Mission

**Issue #227 — engine: answerability — `current` as complete gate briefing, recovery-bearing REFUSED, over-read instrument.**

Deliverable: a merged-ready PR against `fredcai6/constellation-skills` implementing all six
build items below, with the acceptance evidence pasted into your verdict.

How it serves the epic intent: epic-226 is "spend agent effort on the actual problem instead
of the scaffolding." The measured evidence base is **~8.8k tokens/run of scaffolding over-read**
— agents re-reading spine JSON and engine source because `current` does not tell them enough.
Your issue is the direct attack on that number: make `current` a complete briefing so nothing
else needs opening, and make every refusal carry its own exit.

**Full issue body, verbatim:**

> Spec S2+S3 (+S9 rider). Design ratified via 3-agent design-it-twice panel (archived: dit-I1-*-RESULT.md).
>
> Build, all inside checklist_engine.py:
> 1. `current` becomes a complete gate briefing: full imperative verbatim (never elided) + conditions block for the active task (`id [state] kind — statement` one-liners for open pre/postconditions; satisfied summarized as `n/m met`). INV-1 (completeness): current's output is a superset of every argument the caller's next verb needs — tested against a small maintained verb→required-args map (the oracle; NOT against current's own render). INV-2 (purity): stored condition flags only, never live-runs a command check.
> 2. Every state-caused REFUSED carries a recovery line naming the exact exit verb via a shared (status, attempted-verb)→command helper: blocked→`resume <id> --reason` (+ 'no unblock verb exists'), complete→`reopen`, unmet precondition→the exact `attest --which preconditions` command, unknown cond id on attest→enumerate valid ids. Append 'Do not edit the JSON — use the engine.' INV-3 (recovery totality): every (status, mutating-verb) refusal pair yields a non-generic recovery line, enumerated in a test. Recovery is a separate channel from the five frozen rail strings (#145 freeze untouched).
> 3. Ports-lite internals: implement rendering as a pure state projection (`state(cl) -> view dict` + `render_human(view)`); no public --json flag yet (future conductor adapter is json.dumps behind a flag when a consumer exists).
> 4. Output ordering: the operative result/refusal line must be last on its stream so `tail -1` reads the result, not the RAIL banner (absorbs #220's rail-banner item). SCOPE FLAG (cut review finding 2): this item and the attest by-reference hint in item 2 absorb #220 content beyond confirmed spec S2 — cohesive same-surface work, declared here like F's #198 fold.
> 5. Success instrument: `scripts/measure_overread.py` — transcript scanner counting structural reads (spine/cycle JSON, engine source) per run — plus a committed fixed baseline corpus; acceptance includes a re-run showing engine-driven-run scaffolding reads drop toward zero vs baseline.
> 6. Doctrine riders (same PR): engine-output-only line in _shared global-everyone.md (agents consume engine state via engine output; opening the JSON is a violation — enforcement lint deliberately deferred until post-ship measure_overread evidence demands it); return-thin/write-fat one-liner in the handoff-completeness doctrine.
>
> Absorbs from #220 (rewrite #220 to strike these): 'start refuses on unattested null preconditions but current narrates only postconditions' (the conditions block shows preconditions); 'attest by-reference hint' (the enumeration + recovery lines carry it); 'RAIL banner masks operative result' (item 4).
>
> Acceptance: 906-suite green + new golden-output tests for each active-task state and each refusal family; INV-1 oracle test; INV-3 enumeration test; INV-2 no-subprocess test; measure_overread baseline + post-change delta committed. Out of scope: `explain`/`show` verbs (killed by panel — untaken road), public --json, any SKILL.md body edits beyond the two doctrine riders.

## Prior-Wave Verdicts (pasted)

None — you are wave 0. No prior-wave verdict exists for this epic.

Relevant settled history you would otherwise have to rediscover:

- The **five rail strings are FROZEN under #145** and their wording was proven under an eval
  measurement. Your recovery lines are a **separate channel** — do not reword, reorder, or
  merge them into the rail strings. The rail table remains the canonical enforcement source
  (`global-everyone.md` names it as winning over prose on any conflict).
- **#179/#182/#183/#189/#190/#199 already shipped** the why-capture, `DIGEST:`, `REFRESH
  REQUESTED:`, and Trip machinery in this same file. `_why_suffix` already appends
  `DIGEST:`/`REFRESH REQUESTED:` to `current` for both gated and survey types (#189 fixed the
  gated-only early-return). Your conditions block must compose with that suffix, not replace it,
  and item 4's ordering requirement applies to the combined output.
- **#220 has already been surgically rewritten** at epic-filing time to strike exactly the three
  items you absorb (its item 3 preconditions-narration, item 5 RAIL banner ordering, item 6's
  by-reference sub-bullet). Its remaining items 1, 2, 4, 6(--field/attach facet), 7, 8, 9, 10 are
  **live and NOT yours**. See Pre-Ruling PR-8.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- **PR-1 — SELF-HOSTING, LOAD-BEARING.** You are rewriting `scripts/checklist_engine.py`, which
  is the **live engine driving the Admiral's own epic spine** at
  `C:/Programs/constellation-skills/.agent-work/epic-226/spine.json`, and also the engine driving
  **your own** commander spine. Consequences that are not optional:
  - Build and test **only inside your worktree**. Never run a mutating engine verb against the
    Admiral's `.agent-work/epic-226/spine.json` — not even to test.
  - Your test suite must not mutate any real work-area spine; use tmp fixtures.
  - Before you hand back, run `py scripts/checklist_engine.py --file <a COPY of a real spine> current`
    under your new engine and paste the output. The Admiral runs the live-spine probe itself
    before merging; your job is to make that probe non-scary.
- **PR-7 — VERIFY THE ISSUE'S CLAIMS AGAINST THE CODE BEFORE PLANNING.** Active repo lesson with
  two prior data points: a launch order's named defect is sometimes **already fixed**, and the
  real live defect is an unnamed sibling. Before you freeze a plan, grep the current
  `scripts/checklist_engine.py` for each named mechanism (the `current` render path, the REFUSED
  construction sites, `_why_suffix`, the rail-string table) and record what already exists. If an
  item is already shipped, that is an **honest null for that item** — report it as a complete
  result with scope stated, and spend the effort on the items that are genuinely missing.
- **PR-6 — CANONICAL DOCTRINE SOURCE.** Item 6's doctrine riders go to
  `skills/_shared/global-everyone.md` — the canonical source. Do **NOT** edit
  `skills/<role>/references/global-everyone.md`; those are install-time copies that
  `install_constellation.py` regenerates, so an edit there is silently overwritten. The
  "handoff-completeness doctrine" for the return-thin/write-fat rider lives in
  `skills/_shared/global-orchestrator.md` (§Handoff completeness) — same canonical-source rule.
  After editing, check whether the repo's install/freshness tests expect the role copies to be
  regenerated, and regenerate them the sanctioned way (via the installer) rather than by hand.
- **PR-2 — NO CI EXISTS YET.** `.github/workflows/` does not exist in this repo; issue #229 is
  building it in parallel with you. Your PR therefore has **no status checks**. Your acceptance
  evidence is the **locally-run** `py -m pytest tests/ -q` exit code and tail, pasted into your
  verdict. Do not wait for, or claim, a green CI run.
- **PR-5 — F #232 ALSO TOUCHES THIS FILE, LATER.** Issue #232(a) adds `_glob_to_regex` property
  tests to this same engine, but it is wave 1 and dispatches only after you merge. You have sole
  ownership of `scripts/checklist_engine.py` this wave. Do not pre-empt #232's work.
- **PR-8 — STAY IN YOUR LANE ON #220/#219.** If you find adjacent ergonomics defects that belong
  to #220's surviving items or to #219's live threads, **file or comment — do not absorb**. Only
  the three declared #220 absorptions above are in scope.
- **Design-it-twice is PRE-SATISFIED for the headline design.** The issue records that the design
  was ratified via a 3-agent design-it-twice panel (`dit-I1-*-RESULT.md`, archived). You do **not**
  re-run design-it-twice on the overall shape. You DO run it (or record an untaken road) for any
  load-bearing interface you invent that the panel did not settle — most likely the `state(cl) ->
  view dict` projection's shape, since that dict is a real interface future consumers bind to.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with
the same rigor as a win. Concretely here: if item N's mechanism already exists in the current
engine, "item N already shipped — here is the code proving it, here is what I verified and what I
did NOT verify" is a **success**, not a shortfall. Per repo doctrine, every null states what was
tested **and what was not**; a null with an empty scope is an unfinished result.

## Inherited Latitude

You may decide, without floating to the Admiral:

- Implementation shape, file layout inside `scripts/`, test organization, naming.
- Narrowing scope where an item proves already-shipped (honest null, evidence pasted).
- Bounded fix-now triage: a small defect you trip over and fix in-lane.
- The `view` dict's exact schema (it is internal; no public `--json` flag ships).
- Whether the optional item-3 projection is one function or two, and where it sits in the file.

You must **float to the Admiral** (stop and return, do not guess):

- Any change to the **five frozen rail strings** (#145 freeze) — that reopens an eval measurement.
- Any doctrine edit **beyond** the two riders item 6 names.
- Adding scope, or dropping any of the six build items for a reason other than a measured null.
- Any change to user-visible engine behavior beyond what the issue specifies (e.g. changing what
  a verb *does*, not just what it *prints*).
- A public `--json` flag or an `explain`/`show` verb — both are explicitly killed untaken roads.
- Anything that would require touching another wave-0 issue's files.

Asking up is always sanctioned. If you need epic-level context this order does not carry,
**return-and-query the Admiral** — it answers and continues you. That is a first-class move,
not a failure.

## File Ownership

**Sole writer this wave** of:
- `scripts/checklist_engine.py`
- `scripts/measure_overread.py` (new)
- the baseline corpus you commit for item 5
- `tests/test_checklist_engine.py` and any new test module you add for the golden-output tests
- `skills/_shared/global-everyone.md` and `skills/_shared/global-orchestrator.md` (item 6 riders only)

**Fenced — do not write:** `.github/workflows/**` (issue #229 owns it this wave),
`scripts/install_constellation.py` (issue #228 owns it), `scripts/grade_lint.py` and planning
templates (#230), `skills/prototyper/**` and `skills/commander/**` (#231).

Your findings file: `.agent-work/epic-226/verdicts/commander-227.md`.

## Workspace

Absolute worktree path: `C:/Programs/constellation-wt-227`
Branch: `issue-227` · Base: current `main`
Provisioned by the Admiral with:
```
git worktree add C:/Programs/constellation-wt-227 -b issue-227 main
```

**First step, before any git operation:** run
`py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-227`
— it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its
output into your return report.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a
local merge that would diverge your worktree from main).

## Inherited Context

**This repo VENDORS its own scripts.** `scripts/checklist_engine.py` in the repo root is the real
one — drive the engine from the repo copy, not from any globally-installed
`C:/Users/fredc/.claude/skills/...` copy. The two **can diverge**. Same for templates: prefer
`skills/<role>/templates/`.

**Active lessons from `.agent-work/LESSONS.md` that bear on your mission:**

- `lesson:verify-launch-order-claims-against-code` (project / delegated-planning, 2 data points):
  A delegated commander must verify a launch order's NAMED defect against the current code (grep
  the named symbol/token) BEFORE planning — a headline mechanism already shipped becomes an
  honest-null, and the real live recurrence may be a different, unnamed sibling the prior fix
  never touched. **This is why PR-7 exists. Honor it literally.**
- `lesson:test-harness-concurrency-failsafe` (project / testing): test harnesses driving real
  concurrent file I/O need try/except with a guaranteed stop-signal in `finally`, plus
  `daemon=True` helper threads. A writer thread that dies without signaling stop hangs pytest
  forever. Applies if any of your tests exercise the engine's concurrent-write paths.
- `lesson:verify-harness-field-and-drive-real-writer` (project / testing): when a decision depends
  on a harness-supplied payload field, verify the field against the harness contract AND make the
  regression test drive the REAL writer path, not a hand-injected fixture — a hand-set fixture
  passes green even if production never delivers the field, hiding a silent no-op fix. **Directly
  relevant to your INV-1 oracle:** test `current`'s output against a *maintained verb→required-args
  map*, exactly as the issue says — **NOT** against `current`'s own render, which would be the
  self-confirming fixture this lesson warns about.
- `lesson:observe-midprocess-state-not-via-end-output` (handoff / test-authoring): to observe a
  MID-process state, the observation channel must survive the kill/hang being tested — never
  discover via end-of-process output printed in a `finally`.

**Platform invariants (Windows):**

- **Command-checks run under a POSIX shell (bash).** Author `grep`/`&&`/pipe checks in POSIX form.
  On a box with no bash the engine stamps `shell: cmd-fallback` and the check fails visibly.
- **`gh pr create` body:** write the body to a temp file and use `gh pr create -F <file>`. Never a
  heredoc, never a PowerShell `@'...'@` here-string for `--body` (here-strings work for
  `git commit -m` only).
- Set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you capture —
  cp1252 pipes corrupt captured output silently.
- The Agent-tool `isolation:"worktree"` flag is a **silent no-op** on Windows. Your worktree is
  real because the Admiral provisioned it with `git worktree add` — verify with `--here`.

**Charter-lite carrier:** this repo has no `docs/agents/` overlay, so this block is your doctrine
carrier. Beyond it, your inherited globals are `references/global-orchestrator.md` +
`references/global-everyone.md` bundled with your skill.

**Doctrine you must not re-derive** (it is inherited, not restated per-handoff): correctness over
velocity for promoted behavior; behavior changes are test-led where a test surface exists; fail
visibly rather than emit plausible wrong output; one canonical path, no speculative abstraction.

## Pre-empted Steps

- **Latitude / authorization:** settled by the Admiral's confirmed latitude contract. This launch
  order IS the ratified intent — satisfy `user-decision` checkpoints on your spine by citing it.
- **Design-it-twice on the headline design:** pre-satisfied by the archived 3-agent panel
  (`dit-I1-*-RESULT.md`). Record it as pre-empted; run it only for a new load-bearing interface
  the panel did not settle (see Pre-Rulings).
- **Issue triage / scoping:** the issue body is frozen as written. Do not re-scope it.
- **Worktree provisioning:** done for you (verify with `--here`, do not create your own).

## Data Locations

Untracked inputs absent from your worktree, in the main checkout at
`C:/Programs/constellation-skills`:

- `.agent-work/` (the whole tree — lessons inbox, prior epic archives, the Admiral's live spine).
  **Read-only for you.** In particular, `.agent-work/archive/` holds prior-epic transcripts that
  may be useful as **baseline corpus material for item 5's `measure_overread.py`** — but copy what
  you need into your own worktree and commit a **fixed, small** corpus there; do not make the tool
  depend on paths outside the repo.
- The archived design-it-twice results (`dit-I1-*-RESULT.md`) are referenced by the issue; if you
  cannot locate them under `.agent-work/`, that is a **context query for the Admiral**, not a
  reason to redesign.

## Budget

- **Model tier (required):** **opus** — justified by scope (six coupled build items), three
  named invariants that need genuine test design, and the self-hosting risk of editing the live
  engine. Crew (implementer/reviewer) run at **sonnet**. **No Fable at any tier.**
- **Compute/time, session-window:** you are one of five concurrent wave-0 Commanders drawing on a
  shared usage pool. Keep crew dispatches tight; do not spawn speculative parallel crews. If you
  hit a session limit mid-flight, write your state to your spine and return — do not silently die.

## Stop Conditions

Stop and return when:

- A decision listed as **float to the Admiral** above is needed.
- Your scope would exceed the issue's declared boundaries (`explain`/`show` verbs, public
  `--json`, SKILL.md body edits beyond the two riders).
- The 906-test suite goes red in a way you cannot attribute to your own change within a bounded
  effort — return with the failure attributed by a `uniq -c`-style command over the failure list,
  never from the pytest tail alone.
- The live-engine self-hosting risk in PR-1 turns out to be worse than modeled (e.g. your change
  makes an existing on-disk spine unreadable) — that escalates immediately.
- Budget crossed, or evidence for an acceptance item proves impossible to produce.
- You need **context this order does not cover and cannot safely proceed without** —
  return-and-query the Admiral (it answers and continues you). Asking up is always sanctioned.

## Return Shape

Write `.agent-work/epic-226/verdicts/commander-227.md` **in the main checkout's shared
`.agent-work/`** (git-common-dir resolution points the durable trio at one shared root) containing:

1. **Verdict** — per build item (1–6): SHIPPED / HONEST-NULL (already existed, with the code
   evidence) / BLOCKED (with the reason).
2. **Evidence** —
   - `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-227` output
     (the matched worktree path), proving you worked in isolation.
   - `py -m pytest tests/ -q` exit code + tail, run on your branch.
   - The new golden-output tests, INV-1 oracle test, INV-2 no-subprocess test, INV-3 enumeration
     test — named, with their pass output.
   - `measure_overread.py` baseline number and post-change number, with the command that produced
     each.
   - The PR number and URL.
   - The PR-1 probe: `current` run against a COPY of a real spine under your new engine.
3. **Map impact** — what capabilities/seams changed, for the Cartographer's reconcile.
4. **Triage candidates** — out-of-scope discoveries (especially anything belonging to #220's
   surviving items or #219's live threads), each as a one-line statement.
5. **Workflow feedback** — friction in this launch order, the spine, or the tooling. Be blunt;
   this is the lessons audit's input.

**Deliver before going idle.** Write your result artifact and send your verdict **before** you go
idle: an idle notification with no artifact reads as stalled, not done. The Admiral judges
completion from what you produced, not from a message that arrives after you have gone quiet.

When you open the PR on Windows, write the body to a temp file and use `gh pr create -F <file>`.
