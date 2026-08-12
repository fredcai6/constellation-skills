# Census — b1-census

Control list for b2-implement. Verbatim per-instruction disposition across all six shipped
role templates, applying the handoff's pre-ruling rather than deliberating each case.

## Run-script imperatives

| # | Template.gate | Script | Mandatory? | Disposition |
|---|---|---|---|---|
| 1 | ADMIRAL_SPINE.init | `init_work_area.py <work-id>` | mandatory-before-proceeding (first sentence of the gate; everything downstream depends on the work area existing) | **CONVERTS** — `init.c1` check is currently `null`. COMMANDER_SPINE and EXPLORER_SPINE both already convert the identical instruction on their own `init` gates (`c1` command check calling the same script) — this is the same slip shape as #562: done right twice elsewhere, missed here. |
| 2 | ADMIRAL_SPINE.execute | `verify_iterative_role_artifacts.py admiral-prelaunch --work-id <work-id>` ("run ... in the foreground before any next launch. A nonzero result refuses launch.") | mandatory | **Already converted.** `execute.c3` already carries this exact command as a `command` check. No action. |
| 3 | ADMIRAL_SPINE.closeout | `verify_episode_captured.py <work-id> --store-root episodes --phase feedback` ("run the capture gate before advancing") | mandatory | **Already converted.** `closeout.c2` already carries this exact command. No action. |
| 4 | COMMANDER_SPINE.init | `init_work_area.py <work-id>` | mandatory | **Already converted.** `init.c1` command check. No action. |
| 5 | COMMANDER_SPINE.context | `map_orient.py orient --root <repo-root> --work-id <work-id>` ("before you open any source file... run...") | mandatory, but not a pass/fail verifier — it is an informational read the agent must consume (RESOLVED/DEGRADED framing, not exit-code framing), and the gate closes with "Attest c1". | **Stays.** Not a verify script; converting it would just be re-running the same read as a boolean, which throws away the qualitative RESOLVED/DEGRADED content the agent must act on. Compliance with running it first is enforced downstream by `c2`'s `verify-orientation` check (already converted, #6). |
| 6 | COMMANDER_SPINE.context | `map_orient.py verify-orientation --root <repo-root> --work-id <work-id>` | mandatory | **Already converted.** `context.c2` command check. No action. |
| 7 | COMMANDER_SPINE.plan | `map_orient.py verify-frame --root <repo-root> --work-id <work-id>` | mandatory (waivable for a trivial change, `override_policy` present) | **Already converted.** `plan.c6` command check. No action. |
| 8 | COMMANDER_SPINE.execute | `run_crew.py` ("NEVER hand-launch a crew: run every implementer/reviewer dispatch through...") | mandatory, but an **action** script (launches a subprocess), not a verifier | **Stays**, and out of scope regardless: hard no-go forbids touching `run_crew.py`/crew skill files (owned by another crew this wave). A postcondition can't sensibly assert "you used the right launcher" after the fact without re-deriving state `run_crew.py` itself owns (its registry); `execute.c2`'s `verify_iterative_role_artifacts.py commander` check already polices the downstream artifact shape a legitimate dispatch produces. |
| 9 | COMMANDER_SPINE.execute | `recover_crews.py <work-id>` ("before this step and before EACH crew dispatch, run...") | mandatory, but scoped to **each** dispatch inside an in-progress gate, not to the gate's close | **Stays** — cannot tell how to express a repeated intra-gate precondition as a single gate-boundary postcondition without changing what it means (a check that only ran before the *last* dispatch would silently stop proving anything about the ones before it). Per pre-ruling: "if you cannot tell, leave it and list it." |
| 10 | COMMANDER_SPINE.execute | `verify_iterative_role_artifacts.py commander --work-id <work-id>` | mandatory ("missing, malformed, or non-G2 run packets refuse execute completion") | **Already converted.** `execute.c2` command check. No action. |
| 11 | COMMANDER_SPINE.feedback | `verify_episode_captured.py <work-id> --store-root episodes --phase feedback` | mandatory | **Already converted.** `feedback.c1` command check. No action. |
| 12 | COMMANDER_SPINE.archive | `verify_episode_captured.py <work-id> --store-root episodes --phase archive` | mandatory | **Already converted.** `archive.c1` command check. No action. |
| 13 | COMMANDER_SPINE.feedback | `apply_episode_delta.py --delta ... --store-root episodes` | mandatory, but a **mutator** (writes the episode store), not a verifier | **Stays** — same shape as admiral's closeout (#3/#22 below): the mutation is verified downstream by the already-converted capture-gate check, not itself check-worthy (a command check must be safely re-runnable/idempotent-as-a-read; running a writer as a "check" is the wrong shape). |
| 14 | EXPLORER_SPINE.init | `init_work_area.py <work-id> --spine ... --skill-dir ...` | mandatory | **Already converted.** `init.c1` command check (see also mismatch B below — the check omits `--spine`/`--skill-dir`, so it doesn't fully prove the statement's "spine.json materialized" clause). |
| 15 | EXPLORER_SPINE.explore | `run_crew.py` (dispatch excursions as background subagents) | mandatory, action script | **Stays**, out of scope — same reasoning as #8. |
| 16 | EXPLORER_SPINE.explore | `recover_crews.py <work-id>` ("before EACH dispatch and before consolidation") | mandatory, per-dispatch loop invariant | **Stays** — same reasoning as #9. |
| 17 | EXPLORER_SPINE.explore | `verify_cycles.py <work-id>` | mandatory | **Already converted.** `explore.c2` command check. No action. |
| 18 | EXPLORER_SPINE.review | `verify_spec_confirmed.py <work-id> --phase review` | mandatory | **Already converted.** `review.c1` command check. No action. |
| 19 | EXPLORER_SPINE.confirm | `verify_spec_confirmed.py <work-id>` | mandatory | **Already converted.** `confirm.c2` command check. No action. |
| 20 | EXPLORER_SPINE.confirm | `verify_iterative_role_artifacts.py explorer --work-id <work-id>` | mandatory | **Already converted.** `confirm.c3` command check. No action. |
| 21 | REVIEW_SURVEY.r6-fowler | `verify_fowler_pass.py <fowler-pass-record-path>` | mandatory | **Already converted.** `r6-fowler.c1` command check. No action. |
| 22 | IMPLEMENTER_PLAN | — | — | **Honest null.** The shipped template is placeholder-only (`m0-context`, `m1` generic steps); it names no script at all. Nothing to convert. |

**Net new conversion from this pass: #1 only** (ADMIRAL_SPINE.init). Everything else that names a
script is either already a command postcondition, an action/mutator script that shouldn't become a
"check", or a per-dispatch loop invariant that can't be expressed as one gate-boundary check.

## Statement/check mismatches (the #562 shape)

A postcondition whose **statement** asserts a property the **check** does not actually prove.

| # | Location | Statement | Check | Verdict |
|---|---|---|---|---|
| A | EXECUTE_PLAN `g1-implement.c1` | "IMPLEMENTER_RESULT returned **with no unresolved blockers**" | `{"kind":"artifact","evidence_type":"implementer-result"}` — no `match` | **#562, the named defect.** Vacuously true — a `blocked`/`failed` result satisfies it. **Fix: constrain the check** (see b2). |
| B | EXPLORER_SPINE `init.c1` | "work area scaffolded **and spine.json materialized**" | `{"kind":"command","command":"python <skill-dir>/scripts/init_work_area.py <work-id>"}` (no `--spine`/`--skill-dir`) | The bare re-run only re-confirms the mkdir'd subdirectories; it does not exercise the `--spine` path that materializes `spine.json`. In practice this can't be genuinely false when the check runs (the engine cannot be executing this `advance` at all without `spine.json` already existing), so it isn't exploitable the way A is — but the statement still claims a property the check itself doesn't test. **Fix: weaken the statement** to what the check actually proves (drop the spine.json clause), matching the already-shipped honest pattern at `g1-review.c1`. |
| C | ADMIRAL `latitude.c2`, `closeout.c5`; COMMANDER `understand.c1`, `plan.c3`, `triage.c2`, `review.c1`; EXPLORER `explore.c1`, `confirm.c1` | Each asserts a human decision was "confirmed"/"approved"/"accepted"/"recorded" | `{"kind":"artifact","evidence_type":"user-decision"}` — no `match` | **Leave, by design.** `skills/commander/references/commander-core.md` states this explicitly: "The engine only requires the `user-decision` artifact to be present; the citation rides in the payload for audit." There is no mechanically-checkable content for "a human really confirmed this" beyond presence of the artifact the agent is trusted to attach honestly — matching content here isn't a stronger check, it's a fiction of one. Not the #562 shape (that shape is exploitable-by-a-machine-actor; this one is inherently a trust boundary with a human). |
| D | EXECUTE_PLAN `g1-review.c1` | "REVIEW_RESULT returned" | `{"kind":"artifact","evidence_type":"review-result"}` — no `match` | **Already correct** — statement claims only presence, check proves only presence. Cited in the handoff as the honest baseline. No action. |
| E | EXECUTE_PLAN `g1-integrate.c2` | "reviewer verdict is APPROVE" | `{"kind":"artifact","evidence_type":"review-result","match":{"verdict":"APPROVE"}}` | **Already correct** — cited in the handoff as the "gets it right" example. No action. |

Net: two edits from the sweep (A constrain, B weaken); C/D/E confirmed correct or by-design and left untouched.
