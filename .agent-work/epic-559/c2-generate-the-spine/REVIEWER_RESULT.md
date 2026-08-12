# Review Result

## Assigned Gate
`rework-review/reviewer` — `.agent-work/epic-559/c2-generate-the-spine/REVIEW_HANDOFF.md`

## Result
`APPROVE`

## Handoff compliance
The rework claimed four blockers fixed (0, 1, 2, 4), one confirmed-not-fixed and reported as required
(the survey escalation gap), two reported out of scope (Blocker 3's dispatch flags, `DESIGN_NOTE.md`
staleness), and one divergence fixed at its source. All of it holds under independent reproduction —
see `v1`–`v6` below, each built from adversarial cases I authored myself, not the crew's or a prior
reviewer's fixtures. Scope held: `git diff --stat 28da8a0f..a9e6e0e1` touches exactly
`scripts/generate_spine.py`, `tests/test_generate_spine.py`, one line each in
`specs/implementer.spine.toml` / `specs/reviewer.spine.toml`, one args-line in
`dispatch-proof/probe.spine.toml`, and a mechanical `map/INDEX.md` regen. All five hard no-go paths
(`checklist_engine.py`, `validate_spine.py`, `run_crew.py`, `settings.json`, `docs/agents/*`) are
confirmed untouched by `git diff --stat` against those exact paths for this commit range.

## Scope drift
None. No shipped template under `skills/*/templates/` touched. No merge or push to `main` (branch is
still ahead of `origin`, unmerged).

## Evidence verdict
Every claimed command reproduced directly, and every non-obvious property attacked adversarially
rather than trusted:

- **v1 — TDD escape hatch.** Reproduced the Admiral's single-condition refusal, then built 5 of my own
  adversarial specs: single-condition, `not_yet_written` + `qualitative` paired, two `not_yet_written`
  conditions in one gate, a multi-gate spread (one real gate + one all-null gate — confirmed the fault
  blocks the **whole spine's write**, not just that gate), and a `survey`-type spec (which **does**
  generate clean). Investigated that last case rather than stopping at the green light: `record()`'s own
  `#422` D-scope ruling means null/artifact postconditions on **any** survey item are already,
  by design, never mechanically evaluated — this is the same pre-existing treatment every `qualitative`
  postcondition already gets, not a new hole `not_yet_written` opened. No BLOCK.
- **v2 — numeric fields, both directions.** Ran `_cond_faults` directly against 7 non-integer cases (all
  fault) and 4 valid cases (all clean). Independently re-derived the unquoted-field enumeration by
  reading `_compile_pytest`/`_compile_script`/`_compile_population` myself: exactly 4 unquoted
  interpolation sites exist (`population.expected`/`expected_min`/`expected_max`, `pytest.min_collect`),
  matching Blocker 1's scope exactly — nothing missed. `test_valid_spec_compiled_output_is_unchanged`
  asserts the literal compiled command string, a real behavioral pin.
- **v3 — the self-reported truthiness bug.** Reproduced directly: `not_yet_written = "false"` (a TOML
  string) compiles to `check: null` and is silently misread as declared, zero spec-shape faults raised.
  Judged **acceptable, not a BLOCK** — see Blockers below for the reasoning.
- **v4 — the divergence fix.** MIXED, recorded `fail` on its own survey check rather than softened to
  pass. The named divergence (`dispatch-proof/probe.spine.toml`) is genuinely fixed: `--check-only`
  regenerates clean, the compiled `m1.c2` command now carries `--out`, and diffing a fresh regen against
  the committed `dispatch-proof/spine.json` shows only resolved-token/driven-evidence differences —
  consistent with "audit trail," not a fresh divergence. But I found a **second, unstated** divergence:
  `.agent-work/epic-559/c2-generate-the-spine/generated/{implementer,reviewer}.spine.json` (evidence
  artifacts from the g2 round) still carry `hand_back_to: "admiral-epic-418-followon"`, while the
  now-fixed `specs/*.spine.toml` regenerate `"<parent>"`. Nowhere in `IMPLEMENTER_RESULT.md` is this
  named as a deliberate exception — it is simply stale. See Blockers below for why this does not change
  the overall verdict.
- **v5 — the stale-parent guard.** Ran `shipped_spec_session_specific_parent_faults` directly against 3
  VIOLATING cases (all fire) and 3 INNOCENT cases (all silent), then against the real shipped specs
  today (both clean). Did not pass this value on trust, unlike the three prior reviewers this handoff
  named.
- **v6 — sweep unmoved.** `python scripts/validate_spine.py --sweep --root .` → exactly 23.
- **Suite.** `2823 passed, 3 skipped, 1121 subtests passed` — matches the claim exactly, reproduced
  myself under the required `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1
  python -m pytest -q tests`.

## Code/doc quality
Fowler pass: all 12 baseline smells rendered `absent`, each with a specific finding (not blank) —
notably `duplicated-code` absent **with a positive finding** (`_run_pytest_collect` was extracted to
remove a duplication risk between `_probe_pytest` and the new `_probe_pytest_not_yet_written`, not add
one), and `speculative-generality` absent because `_numeric_field_faults(where, cond, *fields)` already
has 2 real call sites in this same diff. `verify_fowler_pass.py` exits 0 on
`.agent-work/epic-559/c2-generate-the-spine/FOWLER_PASS.json`. `CREW_CONTEXT.md`'s verification
discipline ("assert against behaviour, never text that describes it") holds — the new fixtures assert
exact compiled command strings and real refusal exit codes.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in `IMPLEMENTER_RESULT.md`'s Map Impact
  section reproduced above.
- **Constraints not violated:** yes — `validate_spine.validate()` stayed the unconditional last
  statement; no new `command`-kind escape was introduced; `CHECK_KINDS` unchanged.
- **Notes match the diff:** yes, with one addition this review found and the implementer did not: the
  second `generated/*.json` divergence (see v4).
- **Decision candidates surfaced:** yes — the `not_yet_written` compiled-shape pivot (`check: null` vs. a
  deferred command) is explained and correctly attributed to `validate_spine.validate()`'s unconditional
  zero-collect re-probe, out of this crew's scope to change.
- **Durable context routed:** yes — `DESIGN_NOTE.md` staleness, the survey-escalation gap, and Blocker
  3's dispatch-flag remedy are all named as triage candidates rather than fixed silently or dropped. I
  added one more: the stale `generated/*.json` pair (flagged to `r5-reconciliation`'s
  `triage_candidates`).

## Reconciliation check
No divergence from `DESIGN_NOTE.md`'s frozen contract: five closed kinds remain the only vocabulary,
`validate_spine.py` remains the unconditional oracle, `checklist_engine.py` untouched.
`DESIGN_NOTE.md` §4/§7/§10 are stale prose (undocumented `not_yet_written` field and three new fault
codes) — the crew named this itself; confirmed genuinely named, not silently dropped. One new item this
review surfaced: the stale `generated/*.json` pair, filed as a triage candidate.

## Blockers
None.

**Judgment calls recorded, not silently passed:**
- **v3 (truthiness bug):** shipping `not_yet_written`'s bare-truthiness read (`cond.get("not_yet_written")`,
  so a TOML string `"false"` is truthy) is **acceptable this round, not a BLOCK**. It is an authoring
  footgun, not a hostile-author escape — an author who wants a weaker check can already legitimately
  write `true`. It never lets a gate reach the "no check that can ever fail" bar `v1` tested for: in a
  single-condition gate the mistake still surfaces as a hard refusal; in a multi-condition gate it
  silently disables one condition's enforcement while the gate as a whole still has a real check. It was
  self-reported with precise reasoning, not hidden. The fix is small (an `isinstance(value, bool)`-style
  guard, matching Blocker 1's own pattern) but wasn't in Blocker 1's named four-field scope — recommend
  it as a concrete next-round item, not a mention that evaporates.
- **v4 (second divergence):** `.agent-work/epic-559/c2-generate-the-spine/generated/{implementer,reviewer}.spine.json`
  are stale against the now-fixed shipped specs and this was not named anywhere in
  `IMPLEMENTER_RESULT.md`. Not a BLOCK because these are `.agent-work` evidence artifacts from an
  earlier round, not shipped format, and nothing downstream treats them as authoritative — but it is the
  same defect class this whole rework exists to close, recurring one layer down in a place nobody
  checked. Recommend regenerating them or explicitly marking them as a historical snapshot, the same way
  `dispatch-proof/spine.json` is explicitly named as an audit-trail exception.

## Out-of-scope observations
- `DESIGN_NOTE.md` §4/§7/§10 staleness (crew-named; triage, not mine to fix here).
- The survey-escalation mechanical gap (`record()`/`consolidate()` never evaluate artifact-kind
  postconditions on a survey item) — confirmed already floated, not re-litigated per the handoff's own
  instruction; this review's `v1` investigation additionally confirms the same gap covers null-kind
  postconditions too (not just artifact-kind), which the existing triage language doesn't say explicitly
  — worth a one-line addition when that item is drained.
- `run_crew.py`'s dispatch-flag handling (Blocker 3) — not mine, owned by `epic-559/g1-model-record`.
- The stale `generated/*.json` pair (this review's own new finding — see Blockers above and the
  `triage_candidates` entry attached to `r5-reconciliation` in the driven survey).

## Workflow Feedback
- **Handoff gaps:** none I'd call a defect. The handoff's six named questions (`v1`–`v6`) mapped cleanly
  onto adversarial-testable claims; the only friction was mechanical (see below).
- **Context rediscovered:** the `r6-fowler` survey item's postcondition command text
  (`python scripts/verify_fowler_pass.py .agent-work/<work-id>/FOWLER_PASS.json`) still carries the raw
  `<work-id>` template placeholder token when instantiated by copying `REVIEW_SURVEY.template.json` and
  substituting only the top-level `work_id` field (a one-line Python script, the obvious way to
  instantiate). The item's own imperative anticipates this ("no separate placeholder to fill and no way
  to leave it stale") but that's only true if the instantiation step substitutes every embedded
  `<work-id>` occurrence, not just the top-level field. I hit the unresolved token, used the item's own
  named repair path (`amend --delta <file>` with a `retext-check` op, `--authority` = my `SPINE_PARENT`)
  to fix it before `record` would have failed trying to run a literal `.agent-work/<work-id>/...` path.
  Worth either a stock instantiation helper that does the substitution, or dropping the claim that no
  separate fill step is needed.
- **Instructions improvised around:** no `SPINE_FILE`/`SPINE_SESSION` was bound for this dispatch (only
  `SPINE_PARENT`), so per the reviewer skill's own branching I built and drove my own survey via the CLI
  (`.agent-work/epic-559/c2-generate-the-spine/rework-review/review.json`) rather than the MCP door —
  correctly anticipated by the skill, just noting which path this run actually took since the handoff
  itself doesn't say which to expect.
- **What would have made this easier:** a stock `instantiate_survey.py`-style helper (mirroring
  `init_work_area.resolve_spine`'s token resolution, already used elsewhere in this same epic) that
  substitutes every `<work-id>`/`<parent>`-shaped token in a freshly copied survey template, not just the
  top-level field — would remove the one hand-amend step above entirely.

## Return status
complete
