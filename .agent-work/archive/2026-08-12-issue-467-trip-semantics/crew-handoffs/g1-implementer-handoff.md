# Implementer Handoff

## Gate
`g1-implement` — of `.agent-work/issue-467-trip-semantics/execute.json` (issue #467, epic #418 wave 4).

## Task

Build a **disposable reproduction** under `.agent-work/issue-467-trip-semantics/red-repro/` that
demonstrates issue **#431's deadlock end to end at the current HEAD, with no source change**.

#431 in one sentence: the engine's HARD context band refuses `advance`, and `advance` is the only
writer of the `why_trail` whose latest record **is** the `DIGEST` a cold successor reads — so the
event that forces a handoff is the event that prevents the handoff's brief from being written.

You must reproduce that as an **end-to-end staleness property**, not as "advance raises". Two faces,
both required.

### Face A — the stale DIGEST at the seam

1. Build a real gated spine (use the engine's own verbs; do not hand-write end state).
2. Drive it far enough that a `why_trail` record exists naming an **early** understanding — call it
   the *pre-trip* understanding. Then move to a later gate and get part-way through it, so the agent's
   real current understanding has moved on.
3. Plant a valid, fresh `gauge.json` beside the spine reading **at or over HARD** for a calibrated
   model. `claude-opus-5` → `_PROFILES` `(1_000_000, 80_000, 150_000)` → hard = `0.15`; a
   `fill_fraction` of e.g. `0.30` is comfortably over. The record needs exactly
   `schema_version`, `fill_fraction`, `model`, `observed_at` — and `observed_at` must be recent
   (the reader rejects anything older than 30 min, and anything more than 2 min in the future).
4. Have the agent do **exactly what the shipped engine tells it to do**: run the literal
   `attach <gate> --type refresh-request --field seam=<gate> --field why_ref=<why-id>` command the
   refusal prints, then **stop**. Do not advance.
5. Assert the defect: the `DIGEST:` line that a cold successor reads from `current` **still names the
   pre-trip understanding**, because the advance that would have written the current one was refused.
   Assert it as an equality/`in` against the pre-trip text, not by eyeballing.

### Face B — the refusal hides the agent's real problem

Same setup, but the tripping gate is `in-progress` with an **unmet postcondition**. The shipped
engine's HARD guard runs *before* the postcondition check, so the agent is told
"advancing is blocked until you request a refresh" and never learns that its gate was not
finishable anyway. Capture both: the refusal text it *does* get, and the postcondition refusal it
*would* have got (demonstrate the second by showing the same advance with the gauge removed or
below-hard). One instruction masks the other.

## Protected Intent

A cold successor must be able to pick up a tripped agent's work from `current` alone. Today it
cannot, because the DIGEST it reads is stale by exactly one gate. This gate proves that, before
anything is fixed, so the fix has something to be measured against.

## Test Mode

**Inspection-only, evidence-capturing.** This is not a test. Do not write pytest cases, do not add
anything under `tests/`, do not wire anything into the suite. #467 states the RED "leaves no
residue": the deadlock is a property of the refusal path this issue deletes, so it is unreproducible
by construction after the fix and **must not** be promoted to a regression test. Your output is a
runnable script plus its captured literal output.

## Close Criteria

- `git diff --stat -- scripts tests` is **empty** at the end of this gate. Run it and paste it.
- Face A: captured engine output showing the refusal, the `attach` that satisfies it, and the
  `DIGEST:` line still naming the **pre-trip** understanding. The staleness is asserted in the
  script, not just visible in the transcript.
- Face B: captured output showing the HARD refusal masking an unmet-postcondition refusal, plus the
  same advance below-hard showing the postcondition refusal that was hidden.
- **The reading is proved to have been read.** Show the engine's own
  `CONTEXT <n>% (>= hard)` advisory in the captured output. A repro whose only evidence is that
  something did not happen has proved nothing — this is #467's "no absence is evidence" rule, and it
  is a close criterion, not a nicety.
- The repro re-runs from scratch: a single command rebuilds its scratch spine and reproduces both
  faces. State the command.

## Allowed Scope

- Create anything you need under `.agent-work/issue-467-trip-semantics/red-repro/`.
- Read freely: `scripts/checklist_engine.py`, `scripts/gauge_reader.py`,
  `docs/CHECKLIST_SCHEMA.md` (§"Trip — two-band context-gauge gate policy"),
  `docs/GAUGE_WRITER_HOOK.md`, `tests/test_checklist_engine.py` for spine-construction idiom.

## Specific Exclusions

- **No modification to any file under `scripts/` or `tests/`.** This is the gate's defining
  constraint — the RED must be observable at the unmodified HEAD. (Owner: this gate, #467.)
- Do not touch `.claude/settings.json` (owned by #458).
- Do not write anywhere under `.agent-work/epic-418-redux/**` (owned by the Admiral).
- Do not implement any part of the fix. Gates g2–g4 own that.

## Constraints

- Never use `py` to run pytest (#454 — it produces a false `HARNESS ERROR`). Use
  `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`.
- A piped command's `$?` is the **pipe's** exit code. Redirect to a file and read it, or use
  `${PIPESTATUS[0]}`. This has already produced one false "verified" in this epic.
- Plant the `gauge.json` **directly**. Do not depend on the live hook wiring: `docs/GAUGE_WRITER_HOOK.md`
  describes a hook that tracked `.claude/settings.json` wires on nothing (#458), so every governor
  observation in this epic comes from one laptop's local config.
- The gauge file's location is not negotiable: `_gauge_path` resolves it as a **sibling of the spine
  file** (`Path(spine).parent / "gauge.json"`). Plant it there or the reader returns `None` and the
  whole repro silently becomes a no-trip run — which is exactly the indistinguishable-silence failure
  #467 warns about.

## Map Anchors (inbound)

- **Structural:** `scripts/checklist_engine.py` — `_trip_hard_gate` (the refusal, ~line 1439),
  `advance` (sole `why_trail` writer), `_digest` / `_latest_why_record` (~1121–1145, the DIGEST),
  `_why_suffix` (~1179, the cold-start surface), `dispatch` (~2649, the CLI chokepoint both bands
  ride). `scripts/gauge_reader.py` — `read()`, `thresholds_for()`, `_PROFILES`.
- **Capability:** Trip two-band gate policy, HARD band — `docs/CHECKLIST_SCHEMA.md`
  §"Trip — two-band context-gauge gate policy".
- **Constraints:** `constraint:fail-safe-on-no-reading` — a missing/stale/corrupt reading collapses
  to `None` and never forces; the repro must plant a valid fresh reading and assert it was read.
  `constraint:no-absence-is-evidence` — assert a reading exists before any claim about trip behaviour.
- **Decision anchors:**
  - `decision:red-is-end-to-end-staleness` — the RED reproduces the stale-DIGEST-at-the-seam
    property, not the bare refusal. Why: the shipped refusal already *releases* once a keyed
    refresh-request exists, so an exception-only repro proves nothing about #431.
    `@grade: settled/measured · leans g1-implement,g1-review`
  - `decision:red-leaves-no-residue` — the repro is disposable and is never promoted to a regression
    test. Source: #467 Evidence section. `@grade: settled/inherited · leans g1-implement`
- **Evidence expectations:** `claim:431-deadlock-real` — the literal engine output showing the stale
  DIGEST at the seam, with the planted reading quoted and its being-read proved.
- **Map confidence flags:** this repo carries **no `docs/architecture` packet map**
  (DEGRADED-NO-MAP, discharged). `docs/CHECKLIST_SCHEMA.md` §Trip is the structural authority and is
  current. `docs/GAUGE_WRITER_HOOK.md` is current but describes a hook that does not ship (#458).

## Deliverable Path Check

- **Local-only** — `.agent-work/issue-467-trip-semantics/red-repro/**`. Verified before dispatch:
  `git check-ignore .agent-work/issue-467-trip-semantics/red-repro/x` exits **1**, so `.agent-work/`
  is **untracked but NOT ignored** in this repo — it shows up under `??` in `git status`. Leave it
  there: do **not** `git add` or commit it. The reviewer must not expect these files in the diff, and
  must not read their absence from `git diff` as missing work. The gate's *diff* evidence is the
  opposite claim: `git diff --stat -- scripts tests` must be **empty**.

## Required Evidence

**Load-bearing — prove these rigorously:**

1. `git diff --stat -- scripts tests` empty, pasted verbatim.
2. Face A's stale DIGEST, asserted in code, with the literal engine output.
3. The `CONTEXT <n>% (>= hard)` line proving the planted reading was actually read.

**Confirmatory — a spot-check suffices:**

4. Face B's masked postcondition refusal.
5. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` still at the baseline
   (`1793 passed, 2 skipped, 683 subtests`, real exit 0) — it must be, since you changed no source;
   this is a tripwire against accidental edits, not a claim about your work.

## Wiring Grep

`none — this gate adds no callable symbol to the shipped codebase.` The repro is a standalone
disposable script under `.agent-work/`; by construction nothing in `scripts/` may call it.

## Verification Commands

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-467
git diff --stat -- scripts tests            # MUST be empty
<your single repro command>                  # rebuilds scratch spine, reproduces both faces
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests > /tmp/g1-suite.txt 2>&1; echo "REAL_EXIT=$?"
```

## Suggested Model Tier

`stronger` — the failure mode is a *manufactured* RED (a repro that shows the refusal without showing
the staleness), and that is this epic's central defect. Distinguishing the two requires reading the
engine's release path carefully.

## Authority

Already decided, not yours to reopen:
- The RED is end-to-end staleness, not a bare refusal (converged design + cold critic panel).
- The repro is disposable and never becomes a regression test (#467, Admiral-ruled).
- No source change in this gate.

Yours: the repro's structure, scripting language, spine shape, and how you assert staleness.

## Stop Conditions

Stop and return if: you must modify anything under `scripts/` or `tests/` to reproduce the defect;
the planted gauge cannot be shown to have been read; the deadlock does not reproduce at HEAD (that is
a **finding**, not a failure — report it as a scoped null naming exactly what you tested and what you
observed instead); or a decision outside the authority above is needed.

## Return Format

Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this
handoff or the workflow made the work harder than it needed to be).
