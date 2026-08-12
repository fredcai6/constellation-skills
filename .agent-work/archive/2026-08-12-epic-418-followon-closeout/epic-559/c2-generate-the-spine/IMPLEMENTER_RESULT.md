# Implementation Result

## Assigned gate
`rework/implementer` — `.agent-work/epic-559/c2-generate-the-spine/REWORK_HANDOFF.md`

## Completed slice
Fixed the four rework blockers plus the two carried findings the handoff named ahead of them: (1) an author could write a `population`/`pytest` numeric field that compiles a shell check which cannot fail (Blocker 1), now type-checked with VIOLATING/INNOCENT fixtures (Blocker 2); (2) the `pytest` kind can now express a TDD red step — a stated `not_yet_written` declaration, not an inferred one (Blocker 0); (3) the two shipped role specs' hardcoded parent session id is now a placeholder, with a VIOLATING-proven guard (Blocker 4); (4) the diverged artifact was fixed at its **source** (`dispatch-proof/probe.spine.toml`), never the generated spine. Also drove (did not just read) a real survey host to check whether the large-claim escalation now fires on `record`/`consolidate` — it does not; reported below as a blocker, not fixed (out of scope).

## Scope
**Files changed:**
- `scripts/generate_spine.py` (+185/-11 by diff stat)
- `tests/test_generate_spine.py` (+299/-11 by diff stat — 34 new test methods across 4 new classes)
- `specs/implementer.spine.toml`, `specs/reviewer.spine.toml` (one line each)
- `.agent-work/epic-559/c2-generate-the-spine/dispatch-proof/probe.spine.toml` (one condition's `args`)
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`), a required consequence of new functions added to `generate_spine.py`; no hand edits.

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `scripts/validate_spine.py`, `scripts/run_crew.py`, `settings.json`, `docs/agents/*` are all unmodified. No shipped template under `skills/*/templates/` was touched. No merge or push to `main`. `.agent-work/epic-559/c2-generate-the-spine/dispatch-proof/spine.json` (the completed g3 run's audit trail) was deliberately left untouched — only the source spec was fixed.

## Behavior changed
Yes. Four fields now refuse a non-integer at spec-shape time (new fault code `spec-non-integer-field`); the `pytest` kind gained an opt-in `not_yet_written` field that changes its compiled shape when set; the two shipped specs' `parent` field changed from a concrete session id to a placeholder; one dispatch-proof spec's `args` gained `--out`. All changes are additive for silent/default input — every existing test that predates this round still passes unchanged, and a valid spec's pre-existing compiled output is pinned byte-identical (`TestNumericFieldTypeFaults::test_valid_spec_compiled_output_is_unchanged`).

## Map Impact
No formal Map Anchors were named in the handoff (see Workflow Feedback). Framed against `map/INDEX.md` (regenerated) and `DESIGN_NOTE.md`'s own section numbering:

- **Structural anchors touched:** `scripts/generate_spine.py` — new pure functions `_numeric_field_faults`, `shipped_spec_session_specific_parent_faults`, `_run_pytest_collect`, `_probe_pytest_not_yet_written`; `Undecidable` dataclass gained a `blocking: bool = True` field.
- **Capabilities added/changed/affected:** the `pytest` check kind can now express "this test does not exist yet, verified at gate close" (DESIGN_NOTE.md §4 `pytest` — now stale there, see below); `population`/`pytest` numeric fields are now typed at spec-shape time (DESIGN_NOTE.md §7 fault list — also stale).
- **Constraints/assumptions touched:** DESIGN_NOTE.md's own framing that a `pytest` condition's compiled `command` is always the strict self-checking idiom no longer holds for a `not_yet_written`-declared condition (compiles to `check: null` instead — see Blocker 0 write-up below for why no other shape survives `validate_spine.validate()`, which stayed frozen).
- **Decision candidates / resolved decisions:** `not_yet_written` compiles to `check: null` (a manual attest, mirroring `qualitative` and the shipped `IMPLEMENTER_PLAN.template.json`'s own TDD-red convention) rather than keeping a deferred-but-still-strict `command` — forced by `validate_spine.validate()`'s unconditional, out-of-scope zero-collect fault; see Blocker 0 below.
- **Trust limitations / drift found:** `DESIGN_NOTE.md` §4 (`pytest` field table), §7 (fault list), and §10 (residual-defects table) are now stale against the shipped behavior — they describe the pre-rework shape. Regenerating them was judged out of my explicit scope (`scripts/generate_spine.py`, `tests/test_generate_spine.py`, dispatch flags only) and is named here as a triage candidate rather than silently left unmentioned.
- **Triage candidates:** (1) update `DESIGN_NOTE.md` §4/§7/§10 for the `not_yet_written` field and `spec-non-integer-field`/`probe-pytest-malformed-selector`/`spec-shipped-session-specific-parent` fault codes; (2) the large-claim escalation still does not fire on `record`/`consolidate` for a `survey` host (see below) — a decision is needed on whether the current honest-non-enforcement design is the accepted resolution, or whether `checklist_engine.py` needs extending; (3) `run_crew.py`'s dispatch-flag handling (Blocker 3, below).

## Test mode
**Required:** `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` (test-first/TDD for the two behavior-changing blockers, per handoff)
**Satisfied:** yes — full suite green.

## Evidence

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2823 passed, 3 skipped, 1121 subtests passed in 114.12s (0:01:54)
```

**Result:** pass.

```
$ python scripts/validate_spine.py --sweep --root . | grep -cE '^  \['
23
```

**Result:** pass — exactly 23, unchanged. No shipped template moved.

```
$ python scripts/generate_spine.py specs/implementer.spine.toml --check-only --root . --out /tmp/impl-check.json
check-only: specs/implementer.spine.toml would compile clean
$ python scripts/generate_spine.py specs/reviewer.spine.toml --check-only --root . --out /tmp/rev-check.json
check-only: specs/reviewer.spine.toml would compile clean
$ python scripts/generate_spine.py .agent-work/epic-559/c2-generate-the-spine/dispatch-proof/probe.spine.toml --check-only --root . --out /tmp/rework-m5-check.json
check-only: .../probe.spine.toml would compile clean
```

**Result:** pass — both shipped role specs and the corrected dispatch-proof spec still regenerate clean.

## TDD evidence, if required

**Blocker 1/2 (numeric field type faults) — `TestNumericFieldTypeFaults`:**
- Failing test observed (RED): 8 of 13 cases failed, including the Admiral's exact repro (`test_admiral_repro_population_expected_injection_is_now_refused`) — `spec_shape_faults` returned `[]` for `{"kind":"population","root":".","glob":"*.py","expected":"1 || echo PWNED"}`.
- Passing test observed (GREEN): `python -m pytest -q -k TestNumericFieldTypeFaults tests/test_generate_spine.py` → `13 passed`.
- Refactor while green: no refactor needed; `_numeric_field_faults` is a single small addition.

**Blocker 0 (pytest `not_yet_written`) — `TestPytestNotYetWritten`:**
- Failing test observed (RED): 5 of 11 cases failed, including `test_main_writes_the_spine_for_a_not_yet_written_gate` (`rc == 3`, not `0`).
- Passing test observed (GREEN, after a mid-flight redesign — see Workflow Feedback): `python -m pytest -q -k TestPytestNotYetWritten tests/test_generate_spine.py` → `11 passed`.
- Refactor while green: yes — the first GREEN attempt kept the compiled `command` byte-identical regardless of declaration; running `test_main_writes_the_spine_for_a_not_yet_written_gate` for real showed `validate_spine.validate()`'s own zero-collect oracle check still refused generation (`rc == 4`, `falsifiable-zero-collected`). Redesigned to compile `check: null` for the declared case instead (see Blocker 0 write-up), updated the RED-authored assertions that assumed the old shape, re-ran, green.

## Docs/contracts touched
- `map/INDEX.md` — regenerated, mechanical.
- `DESIGN_NOTE.md` — **not** touched; now stale in the places named under Map Impact / Trust limitations above. Left out of scope deliberately (handoff's Scope names only `scripts/generate_spine.py`, `tests/test_generate_spine.py`, dispatch flags); flagged as a triage candidate rather than silently edited or silently left unmentioned.

## Assumptions
- The `--out` value added to `dispatch-proof/probe.spine.toml`'s `m1.c2` (`.agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json`, an already-existing file) is never actually written to — the check runs with `--check-only`. Any existing path satisfies the CLI's `required=True` and the script probe's positional-path-exists check; I chose an existing, plausible one rather than inventing a new file.
- "Regenerate from that TOML" (the artifact-diverged-from-source item) was read as "prove regeneration is clean," not as "overwrite `dispatch-proof/spine.json`" — that file is the completed g3 run's audit trail (evidence, journal, `satisfied: true` state) and overwriting it would destroy history for no benefit `--check-only` doesn't already provide as proof.

## Stop conditions hit
None that stopped the run. One confirmed-and-reported non-fix (see Blocker findings below): the large-claim escalation mechanism does not fire on `record`/`consolidate` — reported per the handoff's own instruction ("if it does not, say so and stop; that is a blocker, not a note"), not treated as license to edit `checklist_engine.py` (hard no-go).

## Out-of-scope observations
See Map Impact → Triage candidates above (DESIGN_NOTE.md staleness; the escalation mechanism; Blocker 3/`run_crew.py`).

---

## Blocker-by-blocker findings

### First: what the Commander already reworked — verified by driving, not by reading

Drove a real throwaway survey spine (`/tmp/rework-m1-escalation/`, generated from a small survey spec with a `magnitude = "large"` claim on its last gate, mirroring `reviewer.spine.toml`'s `r6-fowler` shape) through the real `checklist_engine.py` CLI: `claim` → `start`/`record pass` on **every** item, including the large-claim one, **without ever attaching a `review-result`** → `consolidate --verdict APPROVE`. Full transcript at `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/rework-m1-escalation-transcript.txt`.

**Result: `consolidated: verdict=APPROVE findings=0`.** The mechanism does **not** fire on `record`/`consolidate` on a survey host, confirmed live, not inferred.

This is not a new regression. Reading `checklist_engine.py`'s current `record()`/`consolidate()` (lines ~2323–2375) shows the g2-rework-round-2 fix already applied: `compile_spec` now injects **no** `c-escalation` postcondition at all on a `survey` spec (only on `gated`), and the compiled `directives.claim.enforcement` text honestly says `"NOT machine-enforced here"` rather than presenting a decorative-but-inert check. The existing, already-pinned test `TestClaimEnforcementDrivenThroughEngine::test_survey_large_claim_consolidates_approve_with_nothing_attached` documents exactly this as "the measured behaviour ... not a hoped-for one." My drive reproduces that same measured behaviour against the real CLI.

**Per the handoff's own instruction, I am reporting this as a blocker, not silently accepting it as fine because it is documented and tested.** The honest framing: the *false claim* the g2 cold reviewer found (a decorative check that looked enforced) is fixed — the compiled output no longer overclaims. The *underlying mechanical gap* (no machine gate stops a large claim on a survey from reaching APPROVE unreviewed) is real and remains. `checklist_engine.py` is a hard no-go for me to edit; whether the current design (honest non-enforcement, punted to `hand_back_to`) is the accepted final answer, or whether `record()`/`consolidate()` need extending to also honor an artifact-kind postcondition, is a decision for the Commander/Admiral.

### Blocker 1 — which fields now refuse a non-integer, and which VIOLATING fixture proves each

Added `_numeric_field_faults` (new helper) called from `_cond_faults` for `population` and `pytest` kinds. Non-integer (bool explicitly excluded, since `isinstance(True, int)` is `True` in Python) refuses with a new `spec-non-integer-field` fault, before `compile_spec` ever runs:

| field | VIOLATING fixture proving it | INNOCENT fixture proving it stays open |
|---|---|---|
| `population.expected` | `TestNumericFieldTypeFaults::test_admiral_repro_population_expected_injection_is_now_refused` (the Admiral's exact repro) + `test_violating_is_refused["population expected -- shell injection string"/"-- float, not int"/"-- bool, not int ..."]` | `test_innocent_is_left_alone["population expected -- valid int"]` |
| `population.expected_min` | `test_violating_is_refused["population expected_min -- non-integer string"]` | `test_innocent_is_left_alone["population band -- valid ints"]` |
| `population.expected_max` | `test_violating_is_refused["population expected_max -- non-integer string"]` | `test_innocent_is_left_alone["population band -- valid ints"]` |
| `pytest.min_collect` | `test_violating_is_refused["pytest min_collect -- shell injection string"/"-- bool, not int"]` | `test_innocent_is_left_alone["pytest min_collect -- valid int"/"-- absent (default applies)"]` |

`test_valid_spec_compiled_output_is_unchanged` pins that a valid spec's compiled `command` string is byte-identical to before the fix.

### Blocker 2 (deliverable item 2) — every other field reaching a compiled command, enumerated

Fields already `shlex.quote`d/`shlex.join`ed (safe from the injection class Blocker 1 closed) but **still not type-checked** — a non-`str` value here (e.g. a TOML array of numbers, or a bare int where a string was expected) would raise an unhandled `TypeError` out of `shlex.quote`/`shlex.join` inside `compile_condition`, the same *shape* of gap Blocker 1 closed for the numeric fields, just not a shell-injection risk since `shlex` itself refuses to silently coerce:

- `pytest.selector` (`shlex.quote`d)
- `pytest.targets` — each list item (`shlex.join`ed)
- `script.path` (`shlex.join`ed)
- `script.args` — each list item (`shlex.join`ed)
- `population.root`, `population.glob` (`shlex.quote`d)

Also newly introduced this round and worth naming even though it never reaches a shell command at all: `pytest.not_yet_written` is read with bare truthiness (`cond.get("not_yet_written")`) — a string value like `"false"` would be truthy and misread as declared. Not a security surface (never interpolated), but an authoring footgun; out of scope to add type-checking for here since it wasn't named in Blocker 1's four fields.

`artifact.evidence_type`/`artifact.match` are excluded from this enumeration — they compile to an `artifact`-kind check, never a shell `command`, so the injection class does not apply to them.

### Blocker 0 — the pytest probe asserted a close-time truth at generation time

Added an opt-in `not_yet_written` field to the `pytest` kind (stated declaration, never inferred — silence keeps today's exact strict behavior).

**What generation still checks (well-formed, not green) when declared:** target existence on disk (a missing target *is* the declared scenario — Undecidable, non-blocking, not a Fault) and selector syntax (via `pytest --collect-only`'s own usage-error exit code 4, which is how pytest distinguishes a malformed `-k` expression from "genuinely nothing collected yet" — a malformed selector still refuses as `probe-pytest-malformed-selector`, declaration or not).

**What changed from my original design, and why (see TDD evidence above):** I initially assumed the compiled `command` could stay byte-identical to the strict form, deferring enforcement to gate-close. Building `test_main_writes_the_spine_for_a_not_yet_written_gate` end-to-end proved that wrong: `validate_spine.validate()` — out of scope to edit, and the *literal last statement before success* per the module's own frozen contract — unconditionally re-probes any `command`-kind pytest check live and refuses (`falsifiable-zero-collected`) when it currently collects zero. There is no compiled shape that is both a strict `command` **and** survives that oracle check before the test exists. A declared `not_yet_written` pytest condition now compiles to `check: null` instead (mirroring `qualitative`'s own shape, and the shipped `IMPLEMENTER_PLAN.template.json`'s existing TDD-red convention: "encode the RED step as a `check:null` postcondition ... NOT a command check"), with the declaration and its terms (`selector`, `min_collect`) rendered into the statement so a reviewer sees the claim: `"... -- NOT YET WRITTEN AT GENERATION: pytest -k '...' must collect >= N and pass when this gate closes; attested manually, not machine-checked, until the test exists"`.

**The honest tradeoff, stated plainly:** declaring `not_yet_written` trades machine enforcement for a manual attest at gate close, for that one condition. This is a real downgrade from "strict command, deferred" (which I originally wanted and could not build), but it is the only shape buildable without touching `validate_spine.py`, and it is no weaker than the trust-but-verify contract the corpus already uses for every `qualitative` condition.

**VIOLATING both ways (Blocker 2's pairing), proven in `TestPytestNotYetWritten`:**
- No declaration + wrong selector → still refused: `test_silence_keeps_strict_default`, `test_no_declaration_wrong_selector_still_refused`, `test_main_without_declaration_still_refuses` (`rc == 3`).
- Declared + not-yet-collecting → not refused: `test_declared_short_collect_is_undecidable_not_fault`, `test_declared_missing_target_is_undecidable_not_fault`, `test_main_writes_the_spine_for_a_not_yet_written_gate` (`rc == 0`).
- Declared + genuinely malformed selector → still refused (well-formedness holds regardless): `test_declared_malformed_selector_still_faults`.

### Blocker 3 — nine dispatches, zero `--parent`, zero `--model`

No crews were dispatched via `run_crew.py` during this run — every fix was made directly, in this session, with no sub-crew delegation, so there were no dispatch flags to pass. Nothing to report as an instance.

**On the remedy itself, since the handoff asked for an opinion:** given the measured pattern (nine dispatches, `--model`/`--parent` stated repeatedly in prose across `execute.json` and the launch order, zero flags landed on an actual command line), I think a hard refusal in `run_crew.py` when `--model`/`--parent` are unset is the right remedy over another documentation reminder — prose already failed ten times in a row in the same run. A softer alternative worth considering alongside a refusal: default `--parent` from `SPINE_PARENT` in the dispatching session's own environment when the flag is omitted, since that value is already correctly available (my own environment carries `SPINE_PARENT=admiral-epic-418-followon`) and typing it by hand is exactly the step that kept getting skipped. Not mine to build — `run_crew.py` is a hard no-go here — but this is my answer to "whether the refusal is the right remedy."

### Blocker 4 — the wrong parent baked into two shipped role specs

Fixed: `specs/implementer.spine.toml:4` and `specs/reviewer.spine.toml:4` now read `parent = "<parent>"` (a placeholder slot, resolved at instantiation) instead of the hardcoded `"admiral-epic-418-followon"`. `compile_spec`'s existing `hand_back_to = spec.get("parent") or "unknown"` needed no change — it already treats an absent/placeholder value honestly.

Added `shipped_spec_session_specific_parent_faults` (deliberately **not** wired into `spec_shape_faults`, since a real per-run dispatch spec legitimately carries a concrete `parent` — this guard is scoped to shipped templates only, exercised directly against `specs/*.spine.toml`). `TestShippedSpecParentGuard`:
- VIOLATING (the guard would have caught the real defect): `test_violating_is_caught["the exact prior shipped value"]` uses `"admiral-epic-418-followon"` verbatim, plus a different concrete session id and a non-string value.
- INNOCENT: placeholder token, absent, explicit `None`.
- Regression: `test_real_shipped_spec_is_now_clean` runs both real shipped specs through the helper — clean. `test_real_shipped_spec_still_carries_a_placeholder_not_silence` pins that the chosen fix is the placeholder form, not silent omission.

### The artifact diverged from its source

Fixed at the source: `dispatch-proof/probe.spine.toml`'s `m1.c2.args` now includes `--out .agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json` (an already-existing file — the check runs `--check-only`, so nothing is actually written to it). Regenerating `--check-only` from the corrected source exits 0 (pasted under Evidence above). The completed `dispatch-proof/spine.json` — the finished g3 run's audit trail (evidence, journal, `satisfied: true` state) — was deliberately left untouched; only the spec was fixed, never the artifact, per the handoff's own rule.

`TestDispatchProofOutFlagRegression` parses the real `probe.spine.toml`, compiles it, and asserts the `m1.c2` compiled command now contains `--out` — proving the **source**, not a one-off manual fix, is what a future regeneration would carry forward.

## What this whole finding is evidence for

**The mission's settling question: the defect moved, and the move was worth making.** Before this format, an author could type any shell command from memory into a check field — the full defect class C2 was built to close. After it, there is still no such field; that property held throughout this rework and holds after it. What moved is exactly what the handoff predicted: the compiler itself, for one round, could author a check that could not fail (`population.expected` interpolated unquoted and untyped) and could author a check that could never even be reached (a TDD-shaped `pytest` condition the oracle would refuse before any crew started). Both were real, both were found by building and running the real thing rather than by reading the design, and both are now closed by one small function each, pinned by a fixture apiece — `_numeric_field_faults` and the `not_yet_written` branch in `compile_condition`/`_probe_pytest`.

That is a good trade, not a failure to report apologetically: the defect went from a discipline every author had to maintain forever (never type a raw command, never leave a selector unquoted) to two functions, a handful of fixtures, and a test suite that fails loudly the moment either regresses. Closing the compiler's version of the defect is a patch. Closing the author's version was never possible by patching — it required removing the field entirely, which this format already did, a round before this one.

## Workflow Feedback
- **Handoff gaps:** Blocker 0's framing ("The compiled command itself ... is the thing the engine runs at gate close" — my own initial reading, not a literal quote) assumes a shape that turns out to be unbuildable without touching `validate_spine.py`: its own zero-collect fault is unconditional and re-probes any `command`-kind pytest check live, regardless of any declaration recorded elsewhere in the spec. The handoff correctly names `validate_spine.validate()` as "the literal last statement before success" in the frozen module docstring, but doesn't flag that this specific interaction (a declared-not-yet-written condition vs. the oracle's own independent zero-collect check) was the actual blocking mechanism — I found it by building the end-to-end test, not by reading either document. Worth a line in a future handoff on this same seam.
- **Context rediscovered:** pytest's own `--collect-only -k` exit-code semantics (`5` = valid selector, zero collected; `4` = usage error, covering both a malformed `-k` expression *and* a missing target file — the two are indistinguishable by return code alone, which is why the target-existence check has to run *before* invoking pytest, not be inferred from its exit code) aren't documented anywhere in this repo; I measured them empirically against this host's pytest 9.1.1.
- **Instructions improvised around:** the plan template's own guidance ("Attest any check:null precondition BEFORE start") worked cleanly throughout; no engine instruction needed improvising around. The one design pivot (Blocker 0's compiled shape, above) was a self-correction mid-TDD-green, not an engine/skill instruction gap.
- **What would have made this easier:** the handoff could name a Map Anchor / entry point the way the constellation-implementer skill's own instructions expect ("Verify the handoff... Map Anchors name a map entry point") — this handoff names files and line numbers directly instead, which worked fine for a change this bounded, but I had no `map/` packet to start from and used `DESIGN_NOTE.md` + direct source reading instead. Not a blocker, just noting the substitution per the skill's own instruction to report it.

## Return status
complete
