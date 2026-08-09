# Candidate gate plan — constraint: most-testable

Every gate below closes on a command whose **exit code** is the verdict (stdout discarded, per the
engine). For every gate I name the concrete broken input that flips that exit code from 0 to
nonzero. Where I could not construct one, I say so rather than inventing one — that did not happen
here, but two gates (G4, G5) exist for no reason *other than* testability, and I flag that plainly
in the closing analysis.

Grounding: `scripts/verify_iterative_role_artifacts.py`, `tests/test_iterative_planning_doctrine.py`
(existing fixture harness `InstalledIterativeRoleRuntimeTests.run_role()`, and the pre-fix
`test_admiral_prelaunch_refuses_until_transition_is_unique_verified_and_rendered` at lines 336–465,
whose final two subTests currently assert `stop` is *refused* — that assertion is what fix A
inverts), and `skills/commander/templates/COMMANDER_SPINE.template.json`'s `archive.c2b`.

## Gate table

### G1 — fix C: archive PR-state check (`archive.c2b`)

- **Changes:** `skills/commander/templates/COMMANDER_SPINE.template.json` (`archive.c2b.check.command`
  only); new `tests/test_commander_archive_pr_check.py`.
- **Close criteria:** exit code of
  `python -m pytest tests/test_commander_archive_pr_check.py -v` is 0. The test itself resolves
  `<repo-root>` to a real disposable fixture repo and runs the **actual** template `check.command`
  text (not a reimplementation) via `subprocess.run(["sh", "-c", resolved_command])`, asserting
  `.returncode` (never stdout) across four checked-out branch states: no-PR, OPEN, MERGED,
  CLOSED-unmerged.
- **Required evidence:** the four-state matrix result (`{1, 0, 0, 1}` on returncode), reusing or
  reproducing the branches already exercised in `notes-1.md`.
- **Falsifying input:** (a) narrow the state filter back to `--state open` — the MERGED-branch
  subtest flips from exit-0-expected to actually-observed-exit-1, going red; (b) reintroduce a
  literal, unsubstituted `<branch>` token in place of the `git -C <repo-root> rev-parse
  --abbrev-ref HEAD` substitution — the OPEN-branch subtest flips red because the shell now queries
  a literal nonexistent ref instead of the real fixture branch. Both are the exact defects #439,
  #484, #446 describe; both are real `sh -c` executions, so this gate cannot be satisfied by
  reading the JSON.
- **Precondition:** none (independent file, independent of G2–G4).
- **Test command(s):** `python -m pytest tests/test_commander_archive_pr_check.py -v`

### G2 — fix B: structural installed-bundle guard (`_installed_skills_root`)

- **Changes:** `scripts/verify_iterative_role_artifacts.py` (`_installed_skills_root` only); new
  test method(s) in `tests/test_iterative_planning_doctrine.py` (e.g.
  `test_installed_skills_root_location_matrix`), reusing the existing
  `InstalledIterativeRoleRuntimeTests` install fixture for the "real installed bundle" case.
- **Close criteria:** exit code of
  `python -m pytest tests/test_iterative_planning_doctrine.py -k installed_skills_root -v` is 0.
  Each location is a `subTest` asserting the **subprocess** returncode from actually running
  `verify_iterative_role_artifacts.py` from that directory (not calling the function in-process),
  matching how the real gate invokes it.
- **Required evidence:** returncode per location — real installed bundle (pass, 0); this repo's own
  checkout root `C:/Programs/constellation-skills` (refuse, 1, message names the real problem, not
  "missing sibling"); a Commander worktree (`epic418-w5-gates`, refuse or resolve-via-probe per the
  precedence rule, never silently pass); `--skills-root` explicit override (wins regardless of
  structural signal).
- **Falsifying input:** create a decoy directory named `constellation-decoy/` with **no** `SKILL.md`
  of its own (or with one but whose parent carries no skills-root marker). Under the guard reverted
  to `.name.startswith("constellation-")`, this decoy wrongly passes — that is pre-ruling 4's exact
  forbidden shape ("accept the repo checkout too"). The test asserting the decoy is refused goes red
  under that reversion. Second falsifying input, aimed at the opposite failure mode: mutate the fix
  to `return skill_root.parent` unconditionally (never raise) — the "refuse when nothing resolves"
  subtest goes red because refusal never fires. Both are real subprocess runs from real directory
  trees, not name inspection.
- **Precondition:** none functionally; sequenced after G1, same file as G3/G4 so ordered to avoid
  concurrent edits to `verify_iterative_role_artifacts.py`.
- **Test command(s):**
  `python -m pytest tests/test_iterative_planning_doctrine.py -k installed_skills_root -v`

### G3 — fix A golden path: decision-aware `admiral-prelaunch`

- **Changes:** `scripts/verify_iterative_role_artifacts.py` (`_next_wave`, `verify_admiral_prelaunch`);
  update the existing
  `test_admiral_prelaunch_refuses_until_transition_is_unique_verified_and_rendered` — its final two
  subTests (`launch_authority="applicable:false"` stays refused; `launch_authority="stop"` flips
  from refused to passed) plus a new NEXT_WAVE-schema subtest.
- **Close criteria:** exit code of
  `python -m pytest tests/test_iterative_planning_doctrine.py -k admiral_prelaunch -v` is 0.
- **Required evidence:** the live `w4-to-close` `stop` transition, **copied** (never mutated in
  place) into the test fixture, replayed through `run_role("admiral", "admiral-prelaunch")` →
  exit 0; `NEXT_WAVE.json` with `launch_id: null` now schema-legal **only** when the boundary's
  recorded decision is `stop`; every previously-green subtest for `advance`/`replan` (unique-audit
  match, `applicable is True`, decision-in-set, render, `CURRENT_TRUTH`/`WAVE_REVIEW` writes) still
  green unmodified.
- **Falsifying input:** widen the null-`launch_id` allowance so it isn't gated on `decision == stop`
  — e.g. make `launch_id` unconditionally optional. A new required assertion, "an `advance` or
  `replan` NEXT_WAVE with `launch_id: null` is still REFUSED," goes red under that mutation. This is
  the golden-path gate's own regression guard: it proves the fix narrowed the check correctly, not
  just that it stopped blocking `stop`.
- **Precondition:** G1, G2 closed (file-touch ordering only, no functional dependency).
- **Test command(s):**
  `python -m pytest tests/test_iterative_planning_doctrine.py -k admiral_prelaunch -v`

### G4 — fix A mutation floor on the `stop` path (NOT OVERRIDABLE, pre-ruling 2)

- **Changes:** test-only — new `test_admiral_prelaunch_stop_mutation_floor` in
  `tests/test_iterative_planning_doctrine.py`. No new production code is expected; if closing this
  gate forces a production change, that change belongs to G3 and this gate is reporting a G3 defect,
  not adding new scope.
- **Close criteria:** exit code of
  `python -m pytest tests/test_iterative_planning_doctrine.py -k stop_mutation_floor -v` is 0.
- **Required evidence:** starting from the G3-green copied `stop` fixture, apply each corruption
  independently and assert the verifier subprocess returns **nonzero** for each: (1) audit-log
  decision mismatch (`stop` in `REPLAN_RESULT.json`, something else in `ADMIRAL_LOG.md`); (2) zero
  matching `TRANSITION` audit lines; (3) duplicate matching audit lines; (4) `applicable: false` on
  the `stop` packet; (5) a `REPLAN_RESULT.json` malformed enough that the installed G2
  `verify_replan_result` itself rejects it.
- **Falsifying input:** the canonical wrong-shortcut this gate exists to catch — an implementation
  that special-cases `decision == "stop"` by returning success **before** reaching
  `_verify_transition_audit` / `verify_replan_result` (a plausible "cheap" reading of "skip the
  authorization clause"). Under that shortcut, all five corruptions above wrongly exit 0. This gate
  is the direct, textbook answer to the epic's central finding — "a check that cannot fail" — applied
  to the one path (`stop`) that pre-ruling 2 says has *never* been exercised by a test.
- **Precondition:** G3 closed (the golden path must exist before it can be corrupted).
- **Test command(s):**
  `python -m pytest tests/test_iterative_planning_doctrine.py -k stop_mutation_floor -v`

### G5 — integration / regression floor across all three fixes

- **Changes:** none new; verifies composition. May surface a new assertion in
  `tests/test_iterative_planning_doctrine.py` (e.g. `test_spine_instantiation_leaves_no_literal_tokens`)
  if one does not already exist to make the closing check itself an exit code rather than an eyeball
  read of `spine.json`.
- **Close criteria:** exit code of `python -m pytest tests/ -v` is 0 (targeted-plus-broader-suite,
  per the governing "verifier changes owe targeted tests plus the relevant broader suite" constraint)
  **AND** exit code of a spine-instantiation smoke test asserting (i) `init_work_area.py --spine
  skills/commander/templates/COMMANDER_SPINE.template.json --skill-dir skills/commander <tmp-work-id>
  --root <tmp>` exits 0, (ii) the resulting `spine.json` contains zero regex matches for
  `_RESOLVER_OWNED_TOKEN_RE`, and (iii) zero literal occurrences of the string `<branch>` anywhere in
  `archive.c2b.check.command`.
- **Required evidence:** full-suite pytest output; the instantiated `spine.json` from a throwaway
  work-id, parsed and asserted on in the test (not read by a human).
- **Falsifying input:** reintroduce a leftover `<branch>` token inside the shell command text (e.g.
  forget to swap it for the `git -C <repo-root>` derivation when hand-editing) — the literal-token
  scan goes red even though `_assert_no_resolver_placeholders` in `init_work_area.py` does **not**
  catch it (confirmed in `notes-1.md`: `<branch>` is not in the resolver-owned token family), which
  is exactly why this gate's own scan, not the existing resolver assertion, has to be the thing that
  goes red.
- **Precondition:** G1, G2, G3, G4 all closed.
- **Test command(s):** `python -m pytest tests/ -v` (targeted subset already covered individually by
  G1–G4; this is the broader-suite requirement, run once at the end)

## Order

G1 → G2 → G3 → G4 → G5. G1–G3 are functionally independent (different files, or different functions
within the same file); the stated order exists only to avoid two gates editing
`verify_iterative_role_artifacts.py` concurrently (G2 before G3) and to keep the template-only change
(G1) as the first, lowest-risk close. G4 strictly requires G3. G5 strictly requires all four.

## Reasoning

**Gate count: 5.** Three of the five map one-to-one to a fix (G1=C, G2=B, G3=A-golden); the other two
exist because a single golden-path gate cannot carry two independently falsifiable claims at once.
Fix C needed only one gate because its two sub-defects (`<branch>` substitution, OPEN-only state)
are fused into one shell postcondition — I cannot close them separately without literally splitting
`archive.c2b` into two checks, which is out of scope, so I instead required a four-state matrix that
falsifies each sub-defect independently *inside* one gate. Fix B needed only one gate for the
symmetric reason: the location matrix is variation on a single claim ("does this one function answer
'where am I running from' correctly"), not several claims. Fix A is the one place the brief's own
pre-ruling forces a split: pre-ruling 2 makes the mutation floor **NOT OVERRIDABLE** and explicitly
distinct from "does the golden path work" — a gate going green on G3 alone tells a reviewer "the stop
path can now succeed," while G4 green tells them "the stop path cannot succeed on a lie." Collapsing
those into one gate would hide which of the two claims held if the combined test suite showed red.

**Gates that exist only because of testability, and would collapse under smallest-diff:** G4 and G5.
G4 adds no production code by design — its entire content is proving a negative (corrupted input
still refuses), which a smallest-diff reading would fold into "add a test or two inside the fix A
gate" rather than stand up as its own closeable, orderable, evidence-bearing step. G5 is pure
composition-proving: under smallest-diff, "all four gates are green" would be taken as sufficient and
the spine-instantiation/full-suite pass would be evidence attached to G1 or G3, not a fifth gate.
Under most-testable I refuse that inference, because none of G1–G4 individually exercises the three
fixes *together* going through the one artifact (`spine.json`) the engine actually consumes.

**Biggest weakness under the other two constraints.** Under best-seam-placement: G2, G3 and G4 all
touch `scripts/verify_iterative_role_artifacts.py`, which is one small, cohesive module a reviewer
would naturally review as a single unit — splitting it into three sequential gates (guard, stop-path
fix, stop-path mutation floor) fragments one coherent file-level review into three passes over
overlapping and adjacent code, raising rebase/merge friction between gates rather than reducing it,
and G4 in particular has almost no diff of its own to anchor a seam to — its "seam" is a claim about
test coverage, not a boundary in the code. Under smallest-diff, this plan is close to the maximum
defensible gate count for three fixes touching three files: G4 and G5 in particular are gates whose
sole justification is a falsifiability property rather than a unit of shipped change, which is
exactly the kind of ceremony smallest-diff is built to refuse.
