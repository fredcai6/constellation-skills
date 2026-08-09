# Candidate: smallest-diff — one gate closes the whole crew

Constraint pushed: fewest gates, least churn, each gate the smallest bite that still closes on
real evidence. No hedging toward most-testable or best-seam-placement.

## Why one gate is structurally available

A, B, and C have **no dependency edge** on each other: A and C don't touch B's function, B and C
don't touch A's function, and none of the three reads an artifact another produces. A and B live
in the *same file* (`scripts/verify_iterative_role_artifacts.py`); C lives in a different file
(`skills/commander/templates/COMMANDER_SPINE.template.json`) that neither A nor B touches. Nothing
forces sequencing. The engine's postcondition list already gives one gate room for independently
checked, independently exit-coded evidence — so splitting into more gates buys ordering nothing
here, only more crew dispatches (implement/review/integrate) over the same three files this crew
already owns alone.

## Gate table

| | g1 — fix everything this crew owns |
|---|---|
| **Changes** | `scripts/verify_iterative_role_artifacts.py` (fix A: `_next_wave`/`verify_admiral_prelaunch` decision-aware for `stop`, per pre-ruling 1 — pick `launch_id: null` legal under `stop`, since that's the smaller diff of the two accepted shapes and touches no other template; fix B: `_installed_skills_root()` structural check + `--skills-root`/probe/refuse chain). `skills/commander/templates/COMMANDER_SPINE.template.json` (fix C: `archive.c2b` command text only — `<branch>` resolved through `<repo-root>`, `{OPEN,MERGED}` accepted, verdict compared in-shell). Two new test files: `tests/test_verify_iterative_role_artifacts.py`, `tests/test_commander_spine_archive.py`. `scripts/init_work_area.py` is inspected, not changed (confirms no new resolver token needed). |
| **Precondition on prior gates** | None. This is the only gate in `execute.json`'s `child_checklist`; it inherits only the spine's own `execute` step preconditions (p1 plan approved/context headroom, p2 state note written), not a sibling gate. |
| **Close criteria (all exit 0, all required — none overridable except as noted)** | c1: targeted suite for A+B. c2: targeted suite for C. c3: full repo suite (the "relevant broader suite" the governing constraint requires alongside every targeted test). c-mut: the fix-A mutation test (pre-ruling 2, **NOT OVERRIDABLE**) — folded into c1 as one required test function, not a separate gate, because pre-ruling 2 requires the test to exist and go red on a broken input, not that it live behind its own boundary. |
| **Required evidence** | The four command outputs below, captured as run evidence. Duplicate-collapse confirmation against issue body (`gh issue view <n> --json body`, pre-ruling 3, NOT OVERRIDABLE) is attached as a quoted evidence note per issue in the Return Shape — it is not itself a pass/fail check, so it is not one of the exit-code postconditions; the governing constraint is explicit that only a `command` check's exit code carries verdict, and body-quoting is a human-legible record, not a check. |
| **Exact commands that close it** | `python -m pytest tests/test_verify_iterative_role_artifacts.py -q` · `python -m pytest tests/test_commander_spine_archive.py -q` · `python -m pytest -q` |

### What the two new test files carry (so the close criteria are real, not vacuous)

`tests/test_verify_iterative_role_artifacts.py` (closes c1):
- Fix A: drives `verify_admiral_prelaunch` over a **copy** of the live `w4-to-close` `stop` fixture
  (never the live packet — per notes-1.md and the mission frame's fixture rule) and asserts exit 0
  with `CURRENT_TRUTH.md`/`WAVE_REVIEW.md` written and the authorization clause skipped; asserts the
  G2 validation, unique-audit-entry match, and render still ran.
- Fix A mutation test (c-mut, required): same fixture copy, corrupted (e.g. drop the audit line, or
  set `applicable: false`), asserts the closure check now **fails** (nonzero exit / `RoleArtifactError`).
  This is the one test proving the fix didn't just relax the check into a check that cannot fail.
- Fix B: three subprocess-driven cases invoking the real script from three real locations — an
  installed-bundle layout, the main-checkout layout, and a worktree layout — each built in a `tmp_path`
  fixture that mirrors the actual structural markers (`SKILL.md` + skills-root sibling), asserting the
  guard now answers "where am I running from" correctly in all three, replacing the three red repros in
  notes-1.md with automated, exit-code-carried assertions instead of a manual recheck step.

`tests/test_commander_spine_archive.py` (closes c2), following this repo's own
`tests/test_prototyper_templates.py` pattern of extracting real content from the shipped file rather
than hand-typing a duplicate: reads `archive.c2b`'s `check.command` string out of the real
`COMMANDER_SPINE.template.json`, substitutes `<repo-root>` with a real repo path, and runs it via
`subprocess.run(["sh", "-c", command], ...)` against the four real branch states notes-1.md already
verified (no-PR, MERGED, CLOSED-unmerged, MERGED), asserting the exit-code pattern `1, 0, 1, 0`.

## My own reasoning

**Gate count: 1, and why this constraint produced it.** Fewest-gates pushed to its limit is not
"the smallest gate I can defend," it's "the fewest gate *boundaries* I can defend." Since A, B, and C
share no data dependency and two of the three already share a file, the only thing more gates would
buy is more crew-dispatch overhead (separate implement/review/integrate cycles, separate PR-sized
diffs to review) over exactly the same three files one crew already owns exclusively. Postconditions
inside a single gate are independently exit-coded, so nothing about correctness or falsifiability is
lost by not paying for a second or third gate boundary — only granularity of *where in the process* a
failure is reported is lost, and that's a testability concern, not a smallest-diff one.

**Where a red window could open, and how it's closed.** With one gate there is no *between-gate* red
window by construction — there's only one boundary, so there's nothing to fall between. The real risk
this constraint has to watch for is a different kind: an *intra-gate* illusion of closure, where two
of three fixes are done and the gate is declared closed anyway because "most of it passed." That's
closed by making all four commands (c1, c2, c3, and the mutation test folded into c1) hard
preconditions of the *same* gate-close decision with no partial-credit path — the engine's gate model
requires every postcondition green, and the mutation test is marked not-overridable, so a diff that
does two of three fixes cannot present as done. The other place a red window classically opens —
between "the fix looks right" and "the check can't actually fail" — is closed by pointing every test
at the exit code exactly as the engine will read it (`sh -c` the real extracted command, subprocess
the real script from a real cwd), never at stdout or at a hand-retyped copy of either.

**Weakest point under the other two constraints.** Under **best-seam-placement**, this is the
weakest candidate by design: A+B sharing a file is a legitimate seam to fuse, but folding fix C's
entirely different file, entirely different evidence mechanism (shell/`gh` against real git branches
vs. Python subprocess against a role-artifact verifier), and entirely different concept (archive
postcondition text vs. role-artifact contract checking) into the *same* gate boundary is precisely
the "handoff straddles a concept" failure seam-placement is defined against. A reviewer opening this
gate's diff has to hold two unrelated mental models — a JSON template's shell-check semantics and a
Python verifier's structural-guard semantics — at once, with no boundary between them to set one down
before picking up the other. If best-seam-placement is the panel's pick, the fix is cheap: split at
the one real seam this candidate already respects (the file boundary) into two gates, not three.
