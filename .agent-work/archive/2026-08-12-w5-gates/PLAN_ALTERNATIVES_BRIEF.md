# Design-it-twice Brief: the w5-gates gate plan

Plan-phase form. Three agents in parallel, one candidate each under one named distinct constraint,
converging to a single recommendation.

## The one thing being designed twice

**How the three confirmed fixes are carved into `execute.json` gates and sequenced.** Not *what* to
fix — the fixes are resolved and frozen (below). The single load-bearing decision is the **gate
decomposition**: how many gates, where the boundaries fall between them, what closes each one, and in
what order they run so verification is green at every gate boundary.

Three shapes are obviously realizable and genuinely differ: one gate per fix; one gate per file; or
gates cut by defect-class (red-repro / fix / mutation-floor) crossing the fixes. Each has a different
answer for where a red window would open and how much a reviewer must hold in their head at once.

## Count and panel — a surfaced choice

**N = 3, a panel.** Rationale: this is verification machinery, one gate of it gates the epic's own
close, and a mis-cut plan here costs a reopen at review rather than a rewrite in place. Doctrine says
"when in doubt, panel"; this is not in doubt in the other direction. The scaling call is surfaced at
the approval checkpoint and the approver may overturn it.

## The constraints (one per agent, each distinct and named)

- **Agent 1 — `smallest-diff`.** Fewest gates, least churn, each gate the smallest bite that still
  closes on real evidence.
- **Agent 2 — `most-testable`.** Every gate closes on a test that can be made to go red on a broken
  input; no gate closes on inspection alone.
- **Agent 3 — `best-seam-placement`.** Gate boundaries drawn where the code's real seams are, so a
  reviewer reviews one coherent thing per gate and the handoffs do not straddle a concept.

## Compared on

- **Depth** — does the gate hide the right complexity behind its boundary, or leak it into the next?
- **Locality** — is each gate contained to files this crew owns, or does it fan out?
- **Seam placement** — is the boundary where the reviewer and the tests want it?
- **Testability** — can each gate be exercised and falsified on its own?

## Framing block

**Constraints in play:** the three above, chosen because they are the plan-phase menu and because
each one, pushed hard, produces a visibly different gate count.

**Dependencies — held fixed for all three candidates.** These are resolved and are NOT open:

- **Fix A (#506).** `verify_admiral_prelaunch` becomes decision-aware, keeping the mode name
  `admiral-prelaunch`. Two clauses block a `stop` packet, not one: `_next_wave()` requires a nonempty
  `launch_id`, and a later clause requires `decision in {advance, replan}`. Under `stop` the artifact
  may express "no launch authorized" and the authorization clause is skipped, while G2 validation, the
  unique-audit-entry match, the render, and the `CURRENT_TRUTH`/`WAVE_REVIEW` writes all still run.
  A separate `admiral-boundary` mode is declined (the Admiral spine template names the mode string and
  is not this run's file). `repair` stays refused. **A mutation test on the `stop` path is required
  and not overridable.** A live `stop` fixture exists and must be COPIED, never mutated in place.
- **Fix B (#501 + #468).** Replace the name test in `_installed_skills_root()` with a structural one:
  a directory is an installed bundle when it carries its own `SKILL.md` and its parent is a skills
  root. Then `--skills-root` wins if given; else the installed parent; else probe known user-scope
  roots with a visible stderr note naming the root resolved; else refuse, naming the real problem and
  every root tried. Widening the guard so it passes everywhere is refused.
- **Fix C (#439 + #484 + #446).** Rewrite the spine template's `archive.c2b` to derive its own branch
  through the existing `<repo-root>` token and to accept `{OPEN, MERGED}` while still rejecting
  CLOSED-unmerged, with the count compared **in the shell** so the exit code carries the verdict. No
  new resolver token; `init_work_area.py` stays untouched.
- **Held fixed for everyone:** files this crew owns are `scripts/verify_iterative_role_artifacts.py`,
  `skills/commander/templates/COMMANDER_SPINE.template.json`, `scripts/init_work_area.py`, and their
  tests. `scripts/checklist_engine.py` and its test file are another crew's this wave and are
  untouchable. Every gate closes on an exit code, because the engine records only `{cmd, exit, shell}`.
  Verifier changes owe targeted tests plus the relevant broader suite.

**Illustrative sketch — NOT A PROPOSAL, carries zero weight at convergence.** One plausible shape:
`g1` fix C (template + resolver check), `g2` fix B (guard), `g3` fix A (decision-aware verifier +
mutation test), each as implement / review / integrate. Offered only to prime parallel thinking; it
must not anchor any candidate. Push your own constraint instead.

## Output — a recommendation, never a menu

Each agent returns ONE candidate. The Commander converges to one defended recommendation with an
axis-by-axis reason, and surfaces it at the approval checkpoint.

## Untaken-road record

- **`common-caller-first` and the interface-menu constraints** were not assigned: this is a plan-phase
  run, not an interface-phase one, so the interface menu does not apply.
- **A fourth candidate under "fewest-crew-dispatches"** was not generated: dispatch count is a cost
  axis, not a structural one, and it is already visible in every candidate's gate count.

## Panel-vs-single record

**Panel of 3, because it touches verification machinery that the epic's own closure depends on.**
Surfaced for the approver to overturn.
