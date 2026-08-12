# Launch Order: `commander-w5-readiness` — #458, workstream R

Epic #418, wave 5 (the final wave). Boundary `close-to-w5`, decision `advance`.

## Mission

**There is no way to ask "is this project set up to run Constellation" and get a checkable answer.**
A project can have every capability present and still not run, because the wiring that activates it
lives somewhere that does not ship — and the gap is then found by an agent failing rather than by a
check refusing.

The measured instance: the Context Governor's gauge writer is wired **only in an untracked file**.

| Settings file | Ships? | `spine_rail` | `gauge_writer_hook` |
|---|---|---|---|
| `~/.claude/settings.json` (user) | — | no | **no** |
| `.claude/settings.json` (project) | **tracked** | yes | **no** |
| `.claude/settings.local.json` (project) | **gitignored** | no | **yes** |

**Every governor observation epic #418 has ever made came from configuration that does not ship.**
This is the `built-not-wired` cluster (#345) as a *project* property rather than a code property.

**Live corroboration, from this dispatch:** `install_constellation.py --dry-run`, run minutes ago,
ended with — *"Context Governor hooks: UNWIRED — no PostToolUse entry for `gauge_writer_hook.py` in
`C:\Users\fredc\.claude\settings.json`, so the Context Governor never fires."* The installer already
knows. Nothing asks it.

## Your first job is a discrepancy, not code

**The two statements of this work specify different deliverables, and nobody noticed until now.**

- **Workstream R** (`REVISED_SPEC.md`): *"A fresh clone produces a reading with no machine-local config."*
- **#458's body**: *"One command answers 'is this project constellation ready' and refuses with a named reason when it is not."*

The first **closes** the gap. The second makes it **visible**. Resolve which one you are building
**before you write code**, and say so in your return. This is exactly the defect class the epic
exists to remove, sitting in the epic's own paperwork.

## Pre-Rulings

1. **Standing ruling, overridable with a stated reason: build the CHECK, and treat wiring as a
   separate opt-in decision.** #458's own Fixed section says *"the check reports; it does not silently
   repair"*, and wiring stays behind `install_constellation.py --wire-hooks`. If you conclude
   workstream R's stronger reading is the right one, **say so and float it** — do not just build the
   bigger thing.
2. **NOT OVERRIDABLE — `settings.json` is never touched.** Standing hard constraint of this epic, at
   any scope, tracked or untracked. Nothing you build writes a settings file without an explicit flag
   a human passes.
3. **NOT OVERRIDABLE — run it against a fresh clone.** #458: *"A readiness check that passes on the
   author's own box and has never been run anywhere else is the same defect one level up."* A check
   that has only ever been observed passing is a check that cannot fail. **Observe it refusing** on a
   real unready checkout, and quote the refusal.
4. **Prefer a mode of `install_constellation.py` over a new script**, which already reports
   hook-wiring state and is most of the way there — unless you can argue the separation is worth a
   second entry point.
5. **The list itself is the deliverable.** #458 names four items (engine present and runnable, skills
   installed and registered, hooks wired *in a file that ships*, work area present) and says
   explicitly that this is only what is already known. What else belongs is your call, with reasons.

## Honest-Null Clause

**A measured negative is a complete, successful deliverable.** If "is this project ready" turns out
not to have a checkable answer without a much bigger change, report that with the evidence rather
than shipping a check that always passes. **A check that always passes is worse than no check** — it
is the thing this whole epic is about.

## Inherited Latitude

You may: choose script-vs-mode; define the readiness list; add tests; open and push your PR; comment
on #458. You may **not**: touch `scripts/checklist_engine.py` or `tests/test_checklist_engine.py`
(crew 4 owns them this wave); write any `settings.json`; or promote an observation into
`docs/agents/*` doctrine.

## File Ownership

**Yours alone this wave:** `scripts/install_constellation.py` and its tests, plus any new readiness
script you create.

**Explicitly not yours:** `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` (crew 4);
`scripts/verify_iterative_role_artifacts.py`, `COMMANDER_SPINE.template.json` (crew 1); handoff
templates (crew 3); `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md` (crew 5).

Working notes: `notes-1.md`. **Never `findings-1.md`** — the harness `Write` tool refuses that basename.

## Workspace

- **Worktree:** `C:/Programs/constellation-skills-wt/epic418-w5-readiness` — **provisioned and verified.**
- **Branch:** `epic-418/w5-readiness-458`, based on `ea854471`.
- **Never dispatch a second Commander into this worktree.**
- All nine installed bundles were re-synced immediately before this dispatch. **Re-derive the engine
  hash yourself** rather than copying one from any document.

## Inherited Context

- **This issue is the one that moves a done-condition.** The epic's DC1 — *"the governor writes real
  per-agent readings on a live run and the trip mechanic acts on them"* — was revised to require that
  it hold **on a shipped configuration**, with readings observed to keep arriving rather than to have
  arrived once. The mechanism is done (#419, #440, #488, #467 all merged). The shipping is not. **You
  are the shipping half.**
- Raised by the human directly during the 2026-08-07 spec revision, and carried in that spec as
  workstream **R**.
- Related: #345 (the built-not-wired pattern), #443 (a `config_ref` pointing at a file that does not
  exist — another readiness-shaped gap; already closed, useful as precedent).

## Budget

- **Model tier: Sonnet.** One well-specified issue; the hard part is scope, not difficulty.
- Watch your own context gauge. A HARD reading changes your instruction rather than refusing your
  verb (#467, merged) — write the handoff and hand off cleanly.

## Stop Conditions

Stop and float if: the R-vs-#458 discrepancy resolves toward the stronger reading (a fresh clone
actually *producing* a reading), because that is a scope change; the readiness list grows past what
one command can honestly answer; or you cannot get the check to refuse on a real unready checkout.

## Return Shape

**Open with your resolution of the discrepancy and your reason** — that is the first deliverable.
Then: fixed / honest-null / blocked, the readiness list you settled on with reasons, **the quoted
refusal from a genuinely unready checkout**, the PR number, and anything you did not do.
