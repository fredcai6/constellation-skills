# Launch Order: `commander-w5-gates` — the bookend gates (#506, #501+#468, #439+#484+#446)

Epic #418, wave 5 (the final wave). Boundary `close-to-w5`, decision `advance`, prelaunch exit 0.

## Mission

**Every gate at the two ends of a Constellation run is broken, and this epic is about to hit all of
them closing itself.** Fix three defects. Six issues close.

| Fix | Issues | The defect |
|---|---|---|
| **A** | **#506** | `execute.c3` runs `admiral-prelaunch`, which requires `NEXT_WAVE.launch_id` nonempty and `decision ∈ {advance, replan}`. A boundary that exits **`stop`** — the correct exit when a final wave completes — can therefore never satisfy it. **The gate cannot be closed by a run that finishes.** |
| **B** | **#501 + #468** | `_installed_skills_root()` (`scripts/verify_iterative_role_artifacts.py:53`) guards with `skill_root.name.startswith("constellation-")`. **The source repo is named `constellation-skills`, so the guard passes from the repo** and then resolves to a sibling that does not exist, refusing with a message that names the wrong problem. |
| **C** | **#439 + #484 + #446** | `COMMANDER_SPINE.template.json`'s `archive.c2b`. Two defects in one postcondition: `<branch>` is never substituted (`init_work_area.py`'s `_RESOLVER_OWNED_TOKEN_RE` does not own that token), **and** it accepts only an **OPEN** PR, so a merged PR — the strongest possible evidence — fails and forces `--force` on the success path. |

**#501 and #468 are the same defect**, filed once from outside and once from the spine's own
imperative. **#439, #484 and #446 are all `archive.c2b`.** Confirm each collapse against the issue
**body** before you close anything — see the pre-ruling on that below.

## Prior-Wave Verdicts (pasted)

From wave 4's g4-review BLOCK, which is the reason this launch order is worded the way it is:

> The first trip-ledger implementation was erased by the very close the HARD band orders an agent to
> make. Measured at 0.20 fill: **1** after a refused begin, **2** after a released begin, **0 the
> moment the agent complies.** A three-gate runaway peaked at 2 and was **absent at the seam,
> byte-identical to an agent that behaved perfectly.** And a *passing* test ran the offender's path
> byte-for-byte while calling it "a fresh agent" — a green test certifying the bug.

From the wave-4 Admiral ruling that produced #506, pasted because it constrains fix A:

> I did not take either available shortcut. Changing the decision from `stop` to `advance` would make
> c3 green instantly and would be **falsifying a boundary verdict to fit a check** — the exact thing I
> forbade my own Commanders three launch orders in a row.

## Pre-Rulings

All overridable with a stated reason, except where marked **NOT OVERRIDABLE**.

1. **Fix A's shape — c3 becomes conditional on there being a launch.** When `REPLAN_RESULT.decision`
   is `stop`, the closure check verifies the transition is *recorded, G2-verified and rendered* and
   **skips the authorization clause**. The audit value is in the packet, not in the launch. The two
   alternatives (`launch_id: null` becomes legal for `stop`; or a separate `admiral-boundary` mode)
   are both acceptable if you argue for them — pick one and say why.
2. **NOT OVERRIDABLE — fix A needs a mutation test.** Corrupt the transition packet and confirm the
   closure check still goes **red**. A closure check that passes on an unverified packet has moved
   the defect, not fixed it. **The `stop` path must be exercised by a test.** It never has been.
3. **NOT OVERRIDABLE — confirm every duplicate collapse against the issue BODY before closing.**
   `gh issue view <n> --json body`. Do not close an issue because its title looks like another's.
   A title-level check here is a check that cannot fail, in a wave about checks that cannot fail.
4. **Fix B must not widen the guard into a check that cannot fail.** "Accept the repo checkout too"
   makes the guard pass everywhere, which is worse than today. The guard's job is to answer *where am
   I running from* — make it answer that (e.g. detect an installed bundle by its structure, not by its
   name) and give the refusal a message that names the real problem, per #468.
5. **Fix C: `<branch>` and the OPEN-only criterion are two defects, not one.** Substituting the token
   without fixing the state criterion leaves a gate that fails on every successful epic. Fix both.
   The gate is asking *is there a PR carrying this work* — answer that question, not a narrower one.
6. **You may not change any decision, verdict, or recorded exit to make a check pass.** If a check
   cannot pass, that is a finding — file it or report it. This is the epic's subject.

## Honest-Null Clause

**A measured negative is a complete, successful deliverable.** If fix A's cheapest shape turns out to
be wrong — say the authorization clause is load-bearing for a reason the issue missed — report that
with the evidence and stop. Do not build the expensive version to avoid returning a null.

**Say what you did not do.** A partial is reported as a partial. Wave 4 reported DC2 done-by-different-
means and DC6 partial rather than rounding up, and that was the right call both times.

## Inherited Latitude

You may: choose the implementation shape inside the pre-rulings; add tests; refactor what you touch;
open and push your PR; comment on the issues you fix. You may **not**: touch
`scripts/checklist_engine.py` or `tests/test_checklist_engine.py` (**crew 4 is their sole writer this
wave** — if your fix appears to need them, that is a float, not a decision); wire hooks or edit any
`settings.json`; close an issue you did not verify; or promote an observation into `docs/agents/*`
doctrine.

**Float to the Admiral** anything out of taxonomy. You cannot reach the human; I can.

## File Ownership

**Yours alone this wave:** `scripts/verify_iterative_role_artifacts.py`,
`skills/commander/templates/COMMANDER_SPINE.template.json`, `scripts/init_work_area.py`,
and their tests.

**Explicitly not yours:** `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` (crew 4),
handoff templates (crew 3), `scripts/install_constellation.py` (crew 2),
`docs/CREW_CONTEXT.md` and `docs/TREND_SNAPSHOT.md` (crew 5).

Working notes: `notes-1.md` in your work area. **Never `findings-1.md`** — the harness `Write` tool
refuses that basename.

## Workspace

- **Worktree:** `C:/Programs/constellation-skills-wt/epic418-w5-gates` — **provisioned and verified.**
- **Branch:** `epic-418/w5-bookend-gates`, based on `ea854471`.
- **Never dispatch a second Commander into this worktree.**
- Installed skill bundles were re-synced immediately before this dispatch; all nine carry engine blob
  `c281cb68eaac65d1169dd6737a6a322728df98eb`. **Do not copy that hash forward** — re-derive with
  `git rev-parse HEAD:scripts/checklist_engine.py` at the moment of use.

## Inherited Context

- Epic #418 spec of record: `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`.
- **You are fixing the machinery this epic runs on, while it runs on it.** Fix A is what lets the
  epic close its own `execute` gate without a waiver against the human's name. That is a real
  dependency and it is **not** a reason to report A done when it is not — the fallback (an honest
  waiver) exists precisely so you never have to soften a report.
- The epic's central finding: **a check that cannot fail** — a signal identical in the healthy and
  the defective world. Its mirror is **a check that cannot pass**, which invites a waiver or a
  doctored verdict. #506 and #484 are both the mirror. Twelve specimens were catalogued in wave 4
  alone, and the ones the Admiral found all sit in **verification and provisioning machinery** —
  which is exactly where you are working.

## Budget

- **Model tier: Opus.** Three fixes in verification machinery, one of which gates the epic's close.
- Rework tolerated. A blocked return with evidence beats a soft pass.
- Watch your own context gauge. A HARD reading now **changes your instruction** rather than refusing
  your verb (#467, merged) — write the handoff and hand off cleanly. Four Commanders did that last
  wave and all four were working as designed.

## Stop Conditions

Stop and float if: a fix needs `checklist_engine.py`; a duplicate collapse does **not** hold against
the body; fix A's cheapest shape is refuted; or any check you write cannot be made to fail on a
broken input.

## Return Shape

Per issue: **fixed / honest-null / blocked**, the evidence (a red that no longer reproduces, plus the
mutation test going red on a broken input), the PR number, and — for each of the six issues —
**whether you verified its collapse against the body, quoted.** Name anything you did not do.
