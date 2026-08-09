# Triage Recommendations — `w5-gates` (epic #418 wave 5, crew 1)

14 candidates, all routed. **Every one is `recommend-and-defer`. Nothing was filed and nothing was fixed now.** The two reasons are stated once here rather than repeated fourteen times.

**Why nothing was filed.** The latitude contract classes *issue filing* as **delegated**, but lists the *tool* `gh issue create` as **pre-clear** — "grounded: #145, and the `gh issue create` gap has now recurred four times". Class-level delegation with no cleared tool is not filing authority, so filing this run would be improvising a decision the run was not authorized to make. This is the fifth recurrence of that gap; it is itself worth an Admiral ruling.

**Why nothing was fixed now.** Several candidates clear the fix-now ladder on their merits (tc1 especially — a genuinely one-line test). They are blocked by something external to the ladder: **this branch's diff is already reviewed and APPROVED at a scope of `tests/test_iterative_planning_doctrine.py` only.** Adding any further production file after approval would slip an unreviewed change into an approved diff — precisely the quiet scope-widening this epic exists to catch. Cheap is not the same as free once a reviewer has signed.

**Recommended disposition for the Admiral.** Tommy has said he would rather not clutter the tracker and that genuinely cheap things should just get done. That argues against filing fourteen issues. The natural resolution: fold **tc1, tc2, tc7, tc14** into a later wave as cheap fixes, file **tc6, tc9, tc10** because they are real defects that will otherwise be rediscovered, and let the rest ride as recorded evidence.

---

## The three this run most wants adjudicated

### tc9 — both #439 and #484 suggest a fix that creates a check that cannot fail
**Labels:** bug, ungrounded claim/decision.
**What.** The replacement command both issues propose — `gh pr list --head '<branch>' --state open --json number --jq 'length > 0'` — prints `false` and **exits 0**. A branch with no PR at all sails through.
**Importance.** This epic's central finding is a check whose signal is identical in the healthy and the defective world. Adopting the suggested fix would have converted a check that cannot *pass* into one that cannot *fail* — strictly worse, because the first one at least announces itself.
**Evidence.** Measured across all four PR states: `#484`'s form exits `0/0/0/0`. This run refused it and gave the verdict to the exit code instead; g3 proves the `-gt 0` → `-ge 0` mutation goes red.
**Acceptance.** The suggestion is annotated on both issues so it is not copied into a future issue or fix.
**Out of scope.** Re-litigating the archive fix, which is done and reviewed.

### tc10 — the Admiral spine template still describes `repair` as an enforced exit
**Labels:** bug, structure/constraint mismatch.
**What.** After fix A, `skills/admiral/templates/ADMIRAL_SPINE.template.json`'s execute prose **and** its directives block both still describe `repair` as an enforced exit. The `stop` branch was corrected for #506; the Admiral-side narrative was not.
**Importance.** The shipped Admiral template now disagrees with verified engine behavior. A template that misdescribes the engine is how the next crew inherits a wrong mental model.
**Evidence.** Fix A's verified behavior versus the template text; also surfaced independently as a g2-reviewer observation.
**Acceptance.** Template prose and directives match verified behavior.
**Out of scope.** Changing engine behavior. **Deliberately not edited here** — not one of this run's four owned files; editing it would create a cross-crew merge hazard with four crews merged or queued behind this branch.

### tc6 — `repair` is still unverifiable at the Admiral boundary
**Labels:** bug, architecture weakness.
**What.** Same defect class as #506, which this wave fixed only for `stop`. A `repair` transition can be refused but never verified.
**Importance.** The defect class is closed for one branch and left open for its sibling. That asymmetry will read as intentional to whoever finds it next.
**Evidence.** g2 reviewer.
**Acceptance.** A repair transition is verifiable, with a mutation floor proving the check can fail.
**Out of scope.** This wave — the fix belongs with whoever owns the replan verifier next.

---

## Cheap fixes for a later wave

**tc1 — `CORPUS_MARKER` drifts silently.** `verify_iterative_role_artifacts.py` copies the constant from `install_constellation.py:1040` and nothing asserts the two still agree. A rename would make `_is_skills_root` quietly fall back to its sibling-glob clause, which mostly still works — so the drift would never surface as a failure. **A one-line equality test closes it.** This is the single best fix-now candidate in the list and is blocked only by the approved-diff scope.

**tc2 — `--skills-root` validation is shadowed in two of three modes.** `verify_explorer` and `verify_commander` read their work-area artifact *before* resolving the root, so a bad `--skills-root` surfaces as an artifact-missing refusal; only `admiral-prelaunch` reports `--skills-root is not a directory` first. All three still refuse visibly at exit 1 — an ordering nit, not a correctness bug. *(Note: this same read-before-resolve ordering is what made every `compose_verifier` refusal leg need a seeded `REPLAN_INPUT`, so it has already cost test-design effort once.)*

**tc7 — `render_replan_markdown` re-verifies redundantly.** It calls `verify_replan_result` internally although the caller already ran it. This makes the render unfalsifiable by packet data, which is why the render leg of the stop mutation test needed code degradation rather than a data mutation to discriminate. Removing the inner call makes the render testable by data.

**tc14 — the README teaches the inference that caused #501 and #468.** The "Repo layout vs. installed layout" section is where a reader learns installed bundles are named `constellation-<name>/`, and that is exactly the inference behind "is this an installed corpus? is it named `constellation-*`?". Add a sentence: the prefix is an installation **convention**, not the test; a process must decide **structurally** (own `SKILL.md` plus a parent `CORPUS.json`). Surfaced by this run's reconcile step.

---

## Recorded evidence — no action proposed

**tc8 — #501's boundary-freshness sub-ask, deferred with a falsification rather than a shrug.** The stateless variant (refuse unless `NEXT_WAVE.boundary_id` is the last verified `TRANSITION` in `ADMIRAL_LOG.md`) is **green in exactly the world it was written to catch**: run early, the new boundary is not logged yet, so the stale boundary *is* the last entry. Staleness is a mismatch with the **caller's intent**, and the caller's intent lives in no artifact — so #501's other variant, where the caller passes the expected `boundary_id`, is the only sound one, and it is inert unless `ADMIRAL_SPINE.template.json` passes it. **#501's stated Acceptance is met without it**, which is why #501 closes on this PR. Falsification at `notes-1.md` item 3.

**tc3 — shotgun-surgery signal on `--skills-root`.** The option needed edits at five parallel sites and the three `verify_*` functions must change in lockstep. Candidate for a single resolved-root context object rather than a parameter threaded three ways. *(Architecture-shaped: routes through reconcile, never fix-now.)*

**tc4 — corpus-level: `EXECUTE_PLAN.template.json:21`.** Implementer-result conditions carry no `match`, so an `IMPLEMENTER_RESULT` recording **BLOCKED** satisfies them. Verbatim the shipped template, not this plan's invention — a check that cannot fail, in the very machinery this epic is auditing. *(cold critic C1-F9)*

**tc5 — corpus-level: `config_ref` points at a file that does not exist.** `docs/agents/engine-config.json` is nowhere in the repo; `load_config` falls back to `{}` silently and nobody is told. Inherited from the shipped template. *(cold critic C2)*

**tc11 — one composition leg uses the repo copy of `init_work_area.py`.** The gate composes real artifacts everywhere it claims to, but this one seam is repo-side. Worth closing so the composition claim is uniformly end-to-end. *(g4 reviewer)*

**tc12 — the doctrine test file is a divergent-change file.** ~1385 lines across g1–g4, with four unrelated concerns (guard, stop, archive, composition) editing it for different reasons. Flagged by the Fowler pass, overridden with a logged standard, non-blocking. Candidate for splitting per concern. *(g4 reviewer)*

**tc13 — Cartographer note: the seam this run exercised is on no map.** The run executed at `DEGRADED-NO-MAP`, and how skill templates, top-level scripts and the **installed** bundle relate is asserted nowhere. That absence is precisely why this gate had to establish composition by running real artifacts end to end instead of trusting structure. A map entry would let the next run anchor by id rather than by path. *(g4 reviewer)*
