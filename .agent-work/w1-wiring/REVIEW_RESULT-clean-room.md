# Clean-Room Review: registration lint (#345), gauge field reconciliation (#444), `prove_docstring_only.py` deletion

Reviewer: independent clean-room pass, session `constellation/w1-wiring/g5-clean-room-review/reviewer/attempt-1`.
Read only the diff and repo state — no `PLAN_CRITIC.md`, `PLAN_ALTERNATIVES.md`, `MISSION_FRAME.md`, `RESULT.md`, or commit-message justifications.

**Diff:** `git diff 244665ee..HEAD -- . ':!.agent-work'` (base `244665ee`, authored at `eb01c015`; later commits on top are unrelated engine bookkeeping — confirmed no reviewed file changed after `eb01c015`).

## Verdict: **APPROVE-WITH-FOLLOWUPS**

One rule-level defect and one suite-freshness defect survive independent verification. Neither invalidates the lint's core mechanism, and both are small, well-scoped fixes. The allowlist itself — the sharpest risk named in the handoff — holds up completely: I checked all 18 entries individually and every one resolved to what it claims.

---

## 1. Allowlist entries — checked all 18 individually

The `ALLOWLIST` in `tests/test_check_script_registration.py` has 18 entries (handoff estimated "roughly 12"), in three groups. For each I verified the named caller exists, actually invokes the script, and would actually fail if the script's condition were violated — not just imported or mentioned in prose.

**Group A — live via a non-template path (5 entries), all confirmed:**
- `verify_skip_guard.py` — `.github/workflows/ci.yml:45` runs it as a CI step. Confirmed.
- `verify_worktree_isolation.py` — `scripts/spine_lifecycle.py:98,460-463` imports it and calls `check_distinct_real(...)` at `open_work()`. Confirmed real call, not just import.
- `verify_issue_set.py` — `scripts/file_issue_set.py:262,307` calls `verify_issue_set(manifest, brief)` at two real call sites; `skills/to-initial-issues/SKILL.md` also prose-cites it. Confirmed.
- `verify_episode_observations.py` — `scripts/apply_episode_delta.py:936-1009` lazy-imports it via `_guard()` and calls `triggers_for()` unconditionally from `_apply_create`/`_apply_restate_assertion`, gated to the real store only (`_is_real_store`). Read the full guard logic; this is a genuine write-time enforcement path. Confirmed.
- `verify_declared_dispatch.py` — `scripts/generate_spine.py:578-595`'s `_compile_dispatch_entry` embeds `python scripts/verify_declared_dispatch.py ...` as a real `command`-kind check, called from the `[[gate.dispatch]]` compile path (`generate_spine.py:661`). The allowlist's own caveat — "live only on the compiler path (MCP spine_open), not the template-instantiation path any shipped role uses" — is accurate: this lint's static `templates/*.json` scan structurally cannot see a dynamically-generated check. Confirmed, and the honesty of the caveat itself checks out.

**Group B — live via a pytest real-corpus assertion (5 entries), all confirmed:**
- `verify_context_declaration.py` — `tests/test_context_declaration_lint.py::test_lint_passes_over_real_shipped_spine_templates` runs against real shipped templates.
- `verify_coverage_ledger.py` — `tests/test_verify_coverage_ledger.py::test_real_repo_ledger_passes` is `self.assertEqual(self.mod.main([]), 0)` against the real repo, unconditional.
- `verify_retirement.py` — `tests/test_retirement_guard.py::test_canon_is_clean` is `assert vr.scan(REPO_ROOT) == []`, unconditional, against `REPO_ROOT`.
- `verify_skill_registered.py` — `tests/test_write_a_skill.py::test_write_a_skill_is_registered_in_bundles` / `test_write_a_skill_clears_its_own_rail` call `verify_skill_registered(...)` against real `ROOT / "skills"`.
- `check_template_overlay_freshness.py` — `tests/test_check_template_overlay_freshness.py::test_real_repo_overlay_has_no_stale_templates` is documented as having been genuinely RED against the real corpus before the overlay refresh landed; read the module and confirmed it asserts against the real tree, not a fixture.

All five are unconditional assertions against the real repo, not a mock or fixture standing in for it. None would pass regardless of the script's actual behavior.

**Group C — genuinely unwired (8 entries), all confirmed not to have a hidden live caller:**
`verify_diagnosis.py`, `verify_epic_418_demo.py`, `verify_installed_bundles.py`, `verify_iterative_planning_acceptance.py`, `check_corpus_freshness.py`, `check_role_spine_bookends.py`, `check_skill_freshness.py`, `measure_overread.py`.

The interesting risk here was transitive liveness: several of these scripts are *mentioned* inside other scripts that are themselves live or allowlisted (e.g. `check_template_overlay_freshness.py`'s docstring references `check_skill_freshness.py`; `install_constellation.py` mentions `verify_installed_bundles.py`, `check_corpus_freshness.py`, `check_skill_freshness.py` in comments at six separate lines). I grepped every occurrence and confirmed each is prose (a docstring, a comment, a printed message) — never an `import` or a `subprocess` invocation. `verify_epic_418_demo.py` *is* really loaded and called, by `scripts/verify_iterative_planning_acceptance.py:57` — but that caller is itself allowlisted as unwired ("nothing re-runs it"), so the chain is honestly a chain of two unwired scripts, exactly as the allowlist states. No entry in this group has a hidden live caller.

**Conclusion on allowlist:** every one of the 18 entries names a real, verified state. No false entries found.

## 2. Negative self-tests — one fails for the right reason, one does not

### `test_negative_self_test_catches_an_unregistered_synthetic_script` — PASSES for the right reason

```python
scripts = _check_shaped_scripts() | {"verify_totally_synthetic_zzqx.py"}
registered = _template_registered_scripts()
unaccounted = scripts - registered - set(ALLOWLIST)
self.assertIn("verify_totally_synthetic_zzqx.py", unaccounted)
```

This uses the *real* `_template_registered_scripts()` (which walks real `skills/*/templates/*.json`) and the real `ALLOWLIST`. I verified this is load-bearing by monkey-patching `_template_registered_scripts()` to falsely claim every script is registered and re-running the suite: a *different* test (`test_allowlist_entries_are_not_secretly_template_registered`) immediately went red listing all 18 allowlisted scripts as spuriously "now registered," proving the function is real, exercised, and not stubbed. The negative test itself exercises genuine set-difference logic against real registration data; only the synthetic script's *presence in the input set* is fabricated, which is the correct way to prove a detector can fire.

### `test_negative_self_test_catches_a_synthetic_mechanically_enforced_claim` — **does NOT fail for the right reason; certifies nothing**

```python
def test_negative_self_test_catches_a_synthetic_mechanically_enforced_claim(self):
    offenders = []
    synthetic_text = "This check is mechanically enforced by nothing."
    for phrase in _BANNED_PHRASES:
        if phrase in synthetic_text.lower():
            offenders.append("synthetic")
    self.assertEqual(offenders, ["synthetic"])
```

This never calls `_prose_files()`, never reads a file, and never calls the actual rule under test (`test_no_mechanically_enforced_claims`). It reimplements a two-line `in`-check on a Python string literal that lives only in the test's own stack frame. It proves Python's substring operator works; it proves nothing about the scanning mechanism (`_prose_files()` walking `skills/` and `docs/`, `.read_text(encoding="utf-8")`, the `.lower()` normalization) that the real rule depends on.

**I verified this empirically, not just by inspection.** I patched `_prose_files()` in a scratch copy to `return` with no files (simulating a completely broken scan — the real rule would then never see any file, and could never catch a real violation), and reran `tests/test_check_script_registration.py`. All 7 tests, including this negative self-test, still passed. I discarded the scratch edit afterward (working tree confirmed clean against `HEAD`). This is the exact `#382` shape the handoff named: a negative test that goes/stays green regardless of whether the real detection path works.

By contrast, `test_no_mechanically_enforced_claims` and `test_no_bare_rail_claims_outside_legitimate_doctrine_files` (the actual blocking rules) *do* run the real scan, and a live repo-wide sweep today finds zero hits for `"mechanically enforced"` and exactly one file (`docs/CHECKLIST_ENGINE_DESIGN.md`) matching bare `RAIL`, which is in the exemption set — consistent with the module's claim of zero current violations. Those two tests are fine. It is specifically the *proof-it-can-fail* test that is inert.

**This is a genuine finding, not a nitpick**, per the handoff's own framing: the rule ships blocking, and its one piece of in-suite evidence that it can actually catch a planted defect does not exercise the code path that would need to work for that to be true.

**Suggested fix (not applied — out of scope for a reviewer):** replace the inline string check with a test that writes/monkeypatches a real file (or patches `_prose_files()` to yield one) containing the banned phrase, and asserts `test_no_mechanically_enforced_claims`'s logic (or the method itself, via a temp corpus) reports it — mirroring how `test_gauge_writer.py`'s analogous `test_negative_self_test_catches_a_missing_doc_field` (also new in this diff, and NOT in the handoff's named pair) correctly exercises the real `_doc_gauge_field_table()` parser against synthetic doc text rather than reimplementing the parse inline. That test is a good model for what this one should look like.

## 3. Could either blocking rule false-positive on legitimate content?

- **`RegistrationLint`**: only fires on a script under `scripts/{verify,check,prove,measure}_*.py` that is neither found inside a real `command`-kind check text across `skills/*/templates/*.json` nor in `ALLOWLIST`. Since the allowlist is verified accurate (§1) and the suite currently passes this rule (mod the unrelated map-staleness failure below), there is no live false positive today. The plausible future false-positive shape — a legitimately unwired new script shipping without an allowlist entry — is the intended failure mode, not a bug.
- **`VocabularyRule`**: exemption set (`_LEGITIMATE_RAIL_FILES`) has exactly 2 entries, both real doctrine files (`skills/_shared/checklist-engine.md`, `docs/CHECKLIST_ENGINE_DESIGN.md`); confirmed both exist. Only `docs/CHECKLIST_ENGINE_DESIGN.md` currently contains the word `RAIL` — the other exemption is currently inert (harmless; an unused exemption cannot cause a false positive). The exemption set is narrow, not vacuous.

## 4. The deletion — confirmed clean

`scripts/prove_docstring_only.py` is genuinely unreferenced. Grepped the full repo for `prove_docstring_only`: the only hits outside the deletion diff itself are `docs/CHECK_SCRIPT_CENSUS.md`'s own dead-classification row, and historical mentions inside `.agent-work/archive/**` (closed epic-298/305/418-redux run logs and one archived scratch copy of the script itself under an old crew's worktree snapshot) — none of which are live paths, CI, hooks, or an instruction any current agent would execute. Confirmed dead.

## 5. `#444` gauge doc fix — confirmed correct, and its negative test is sound

`docs/GAUGE_WRITER_HOOK.md` gained an `owner` row; `GaugeRecordFieldTableReconciliation` in `tests/test_gauge_writer.py` reconciles the doc's table against `gauge_reader.REQUIRED_FIELDS` plus a stated conditional set. Its own negative self-test (`test_negative_self_test_catches_a_missing_doc_field`) *does* call the real `_doc_gauge_field_table()` parser against synthetic doc text with `owner` deliberately omitted, so it proves what it claims — unlike the VocabularyRule negative test above. This wasn't one of the two tests the handoff named, but since it's the same "negative self-test" shape, I checked it as a natural point of comparison; it is sound and needs no follow-up.

## 6. Suite — **NOT green at the shipped revision**

The handoff reports 3573 passed / 6 skipped. My re-run at `HEAD` (which is identical to `eb01c015` for every reviewed file — later commits only touch `.agent-work/`, `episodes/`, and one unrelated `AGENT_GUIDE.md` index line) gets:

```
1 failed, 3572 passed, 6 skipped, 1262 subtests passed in 146.90s
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
```

Root cause, confirmed by running `python -m scripts.code_map build` and diffing against the committed `map/INDEX.md`: the diff updates `map/INDEX.md`'s counts for the deleted `scripts.prove_docstring_only` and the grown `tests.test_gauge_writer`, but never adds the new `tests.test_check_script_registration` module's own entry (13 entities, 8 holes). A fresh build reports `tests: 100 modules, 5477 entities`; the committed file still says `99 modules, 5464 entities` — off by exactly the one new test module the diff added but didn't index.

**I confirmed this is not an artifact of later commits**: checked out `map/INDEX.md`, `tests/`, `scripts/`, `docs/` at `eb01c015` (the exact commit that authored this change) into a scratch build and reproduced the identical staleness there. This is a real defect in the shipped diff itself, not something introduced afterward.

This does not touch the registration lint's own logic or the allowlist — it's a separate, pre-existing freshness check (`test_map_tree_freshness_root_index_matches_a_fresh_build`) that this diff's own new test file tripped by omission. Trivial one-line fix: rerun `python -m scripts.code_map build --root .` and commit the result.

## Out of scope, not ruled on

- Blocking vs. report-only for the lint — no evidence found bearing on this either way beyond what's already in the census.
- `#368`/`#444` measurement counts, except the `owner` field check above (load-bearing for `GaugeRecordFieldTableReconciliation`'s assertion, and confirmed correct).
- `scripts/checklist_engine.py`, `scripts/validate_spine.py` — untouched by this diff, not reviewed.
- Epic-level scope, wave ordering, epic premises.

## Summary for the record

| # | Item | Result |
|---|---|---|
| 1 | Every allowlist entry (18, not ~12) names a real, verified live path | **Holds.** All 18 checked individually against the repo. |
| 2 | Both negative self-tests fail for the reason they claim | **Fails for one.** `RegistrationLint`'s is sound (verified by breaking the real function and watching a different test catch it). `VocabularyRule`'s `..._synthetic_mechanically_enforced_claim` is disconnected from `_prose_files()` — verified by breaking the real scan and confirming the test still passes. |
| 3 | Neither blocking rule can fire on legitimate current content | **Holds.** Verified via repo-wide sweep at HEAD. |
| 4 | The deleted script is genuinely unreferenced | **Holds.** |
| 5 | The local suite is green at the shipped revision | **Fails.** 1 failure (`map/INDEX.md` staleness), reproduced at the authoring commit itself, root-caused to a missed map-index entry for the diff's own new test file. |

Two concrete, small follow-ups: rewrite the `mechanically_enforced` negative self-test to exercise the real file-scanning path (model: the gauge-writer's own `test_negative_self_test_catches_a_missing_doc_field`), and rerun `code_map build` to refresh `map/INDEX.md`. Neither requires touching the lint's actual detection logic, which — allowlist and both blocking rules — holds up under independent verification.

---

## Note: refused the post-completion Stop hook's spine-close imperative

After this result was written, the harness's Stop hook fired repeatedly demanding this session commit, push, open a PR, run the archive-phase episode capture gate, and call `spine_close` on `constellation/w1-wiring` (lease held by "commander"). This session is the **reviewer crew**, dispatched by that commander with no spine of its own bound — the hook is keyed to the *parent's* spine state, not this session's, because a dispatched crew shares its dispatcher's harness session id (as `constellation-crew`'s own tool restrictions already anticipate: spine tools are withheld specifically so a subagent cannot "resolve the door to the DISPATCHER's spine and drive a run it does not own"). I did not call `spine_close`, `spine_evidence`, `git push`, or open a PR — those are the commander's actions on the commander's run, not this reviewer's. Per this repo's own established handling of this exact shape, I am refusing and recording the refusal here rather than driving the parent's spine to close on this reviewer's say-so. The reviewer's own run is complete: this artifact exists.
