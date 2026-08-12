Verdict: APPROVE

# REVIEW_RESULT — `g1-review` · the generator

Cold review, independent of the implementer. All 12 close criteria were re-run with my own
fixtures — different scripts, different specs, different selectors, different claim text —
never the implementer's own. Full detail and the driven survey live at
`.agent-work/epic-559/c2-generate-the-spine/g1-review/review.json`
(engine-driven: claimed, `record`ed item by item, `consolidate`d to APPROVE) and
`.agent-work/epic-559/c2-generate-the-spine/g1-review/FOWLER_PASS.json`.

## Assigned Gate
`g1-review` — the generator (`scripts/generate_spine.py`, `tests/test_generate_spine.py`)

## Result
`APPROVE`

## Close criteria — what I ran, and what came back

**1. The control pairing is real, with my own spec.** Built a fresh fixture (`scripts/probe_target.py`
with `add_argument("--mode")`, distinct from the implementer's `_gs_target.py`) and two TOML specs
sharing one `script` postcondition, differing only in a non-flag arg value (`<unset-mode>` vs
`fast`) that the script probe never inspects (it only reads `--`-prefixed tokens).
- `compile_spec` on the bad spec: `spec_shape_faults == []`, compiled command contains
  `<unset-mode>` literally — translation completes, no judgment.
- Guarded CLI on the bad spec: `oracle refused: 1 [falsifiable-unresolved-placeholder] ...`,
  exit 4, `test ! -f out.json` confirmed nothing written.
- Same spec corrected (`fast`): exit 0, `wrote .../out.json`, file confirmed present.
- **The harder question.** The refused run's fault code was `falsifiable-unresolved-placeholder`
  — `validate_spine.py`'s own naming family (its probe-layer faults are all named
  `probe-*`, disjoint from the oracle's `falsifiable-*`), and the printed text matched
  `validate_spine.Fault.__str__`'s format (`[{code}] {where}: {message}`) exactly. A no-op guard
  that always refuses cannot also be the code path that wrote the corrected spec — the same
  generator, same script probe, same TOML shape, produced a refusal on one input and a real
  write on the other, and the fault code names the oracle as the source. Not a no-op.

**2. `validate_spine.validate()` is the literal last statement before success.** Read
`main()` directly (`scripts/generate_spine.py:578-591`): `result = validate(compiled,
repo_root=root)` runs immediately before `Path(args.out).write_text(...)`, no code between the
call and the fault check. Imported at line 52 (`from validate_spine import
ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH, validate`), never re-implemented — grepped for any local
`def validate` in the file, none exists. Fault text printed verbatim, confirmed above (criterion 1).

**3. Purity — proven, not eyeballed.** Wrote an independent `ast.walk` over
`compile_condition`, `compile_spec`, and every helper they call transitively
(`_compile_pytest`, `_compile_script`, `_compile_population`, `_compile_artifact`,
`_compile_gate`, `_handback_contract`) and asserted no `Call`/`Attribute`/`Name` node refers to
`open`, `Path`, or `subprocess.*`. Zero findings on all of them. The only `Path` reference
anywhere in the pure layer is inside `spec_shape_faults` (not one of the two functions this
criterion names), which the module's own docstring documents as the sanctioned one-file
exception for the `config_ref` JSON check — confirmed it never reaches `subprocess`.

**4. All five kinds compile to exactly DESIGN_NOTE.md §4, and the round trip works.**
Compiled fresh instances of all five kinds directly and diffed the output against §4's prose
character by character — every one matches, including the population band-form text. For the
round trip: compiled `{"selector": "TestFoo or TestBar and not slow", "min_collect": 2,
"targets": [...]}` (my own selector, contains spaces and a boolean expression, distinct from
every fixture in the test file) and fed the resulting command through
`validate_spine._pytest_segments` / `_selector` directly — both the `--collect-only` segment and
the run segment read the selector back byte-identical to what was authored, in both
`shlex.quote`d occurrences. This is the property that stops the generator and the oracle
disagreeing, and it holds under adversarial-shaped input.

**5. Every emitted `command` check is anchored `cd <repo-root> && …`.** Verified directly on
freshly compiled instances of all five kinds; all four kinds that produce `command` checks
(`pytest`, `script`, `population` ×2 forms) start with the literal anchor.

**6. The `script` probe never imports its target — proven adversarially.** Built a fixture
whose import-time code both raises `RuntimeError` **and** writes a sentinel file to disk
(stronger than the implementer's raise-only fixture). Ran `_probe_script` against it directly:
no exception propagated, the sentinel file was never created. The probe correctly reported
`Undecidable` (no `add_argument` literals found) without ever touching the module's import-time
code.

**7. The handback contract renders through the real engine, all three verbs land where
promised.** Compiled a fresh spec with my own parent (`review-parent-x`) and called
`checklist_engine.current()` directly on the output — the handback block renders with the
correct parent name and all three verb pointers. Then drove `checklist_engine.attach()`,
`.flag_candidate()`, and `.block()` against the generated spine directly: `attach` landed in
`tasks["m1"]["evidence"]`, `flag_candidate` landed in top-level `triage_candidates`, `block` set
`status: "blocked"` and appended to top-level `blockers`. All three exactly as DESIGN_NOTE.md §5
specifies.

**8. Claim escalation is unconditional; the falsification floor genuinely goes red.** Compiled a
two-gate spec with my own claim text (`"my own claim text for review-check8"`) — `c-escalation`
injected with the exact contract shape, `claims_rollup` present on the last gate keyed by source.
Then re-ran the mutation myself: read the real source, confirmed the injection snippet occurs
exactly once, replaced it with a marker comment in a fresh copy (asserted the occurrence count
dropped by exactly 1 — the mutation genuinely landed), ran my own probe (not the implementer's
subprocess-pytest harness, a direct import-and-assert) against the mutant: `c-escalation` absent,
nonzero exit. Ran the same probe against the real unmutated source: `c-escalation` present, exit
0. Floor is real, not vacuously green.

**9. Undecidable refuses, nothing written, no escape hatch.** Built a fresh dynamic-flags fixture
(`FLAG_NAMES = ["--zeta", "--omega"]` registered in a loop, distinct names from the
implementer's `--alpha`/`--beta`). CLI run: `undecidable -- could not tell: 1
[undecidable-script-no-add-argument] ...`, exit 3, nothing written. `--help` lists only `-h`,
`--out`, `--root`, `--check-only` — no skip/force/override flag. `grep -niE
"skip|force|--allow|override|ignore"` over the source found only the comment stating there is no
such flag. Fed an invented `--skip-undecidable` flag: argparse rejects it (exit 2, "unrecognized
arguments"), still nothing written.

**10. Guard fixtures are honest.** Counted directly in the test file: pytest probe 2
VIOLATING / 2 INNOCENT; script probe 2 VIOLATING / 2 INNOCENT / 1 populated
`ACCEPTED_FALSE_ALARM`; population probe 2 VIOLATING (too-few, too-many) / 2 INNOCENT (exact,
band) / 1 populated `ACCEPTED_FALSE_ALARM`. Measured both false-alarm premises live rather than
trusting the docstring: `pathlib.Path.glob("**/*.toml")` against a tree with both a top-level and
a nested `.toml` file returned both (confirms the `**`-matches-top-level premise); and
`pathlib.Path.glob("*.toml")` in a directory with a dotfile matched the dotfile too (confirms the
implementer's *corrected* premise — the original dotfile assumption they self-caught was
genuinely wrong, and the replacement premise they shipped is genuinely right). Ran the
`_add_argument_literals` AST scanner directly against `add_argument("-f", "--foo")`: collected
only `-f`, confirming `--foo` (registered second) really is invisible to the probe as the fixture
claims.

**11. No shipped template edited, oracle/engine untouched, sweep count unchanged.**
`git status --porcelain`: only the two new untracked files. `git diff --stat HEAD --
scripts/validate_spine.py scripts/checklist_engine.py`: empty. `git diff --stat HEAD --
'skills/*/templates/*'`: empty. `python scripts/validate_spine.py --sweep --root . | grep -cE
'^  \['`: **23**, matching the stated baseline exactly.

**12. Full suite passes in the declared test mode.** Re-ran myself:
`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q
tests` → **2765 passed, 3 skipped, 1121 subtests passed in 107.85s** — exact match to the
implementer's reported evidence and to `76` new tests over the `2689`-passed baseline. Collected
`tests/test_generate_spine.py` independently: 76 tests, matching the claim.

## Handoff compliance
Satisfied. Two new files exactly as scoped; every close criterion has a corresponding independent
re-run above, not a re-read of the implementer's evidence.

## Scope drift
None. `git status --porcelain` shows only `scripts/generate_spine.py` and
`tests/test_generate_spine.py` as new; nothing else in the tree changed.

## Evidence verdict
All required evidence present and independently reproduced (see close criteria above). One gap in
the *oracle*, not this change, correctly left unpatched per Specific Exclusions:
`checklist_engine.load_config` crashes with an unhandled `JSONDecodeError` on a non-JSON
`config_ref`; `generate_spine.py`'s `spec-config-ref-not-json` fault refuses it at generation
time but cannot patch the oracle itself. Flagged as a triage candidate below.

## Code/doc quality
Minimal, tested, and matches the repo's own precedent (validate_spine.py's pure/impure split at
function granularity) with two minor style exceptions surfaced by the Fowler pass (see below).
One additional finding surfaced by my own independent AST inspection, not claimed anywhere in the
implementer's result:

- **MINOR — dead import.** `_RESOLVER_OWNED_TOKEN_RE` (`scripts/generate_spine.py:51`, imported
  from `init_work_area`) is never referenced anywhere else in the file or in
  `tests/test_generate_spine.py` — confirmed by walking every `ast.Name` node in the module; none
  match. DESIGN_NOTE.md §4 cites this regex to justify why `<repo-root>` is legitimate output
  (`"verified, _RESOLVER_OWNED_TOKEN_RE.fullmatch(\"<repo-root>\") is true"`), but that
  verification was done by the Commander at design time and never wired into the generator's own
  code or a test. Not a functional defect — `validate_spine.py` (which *does* use the regex) is
  what actually exempts `<repo-root>` from the placeholder fault, and that path is proven live by
  close criterion 1's control pairing — but it is a real unused import that should be removed or
  turned into an actual assertion.

### Fowler pass (r6, `FOWLER_PASS.json`)
`verify_fowler_pass.py` exits 0 (12/12 smells rendered, 0 skipped, 0 unlogged overrides).
Two `flagged`, both non-blocking, ten `absent`:

- **long-method** — `spec_shape_faults` (72 lines) bundles five distinct fault categories inline,
  where `validate_spine.py` (the file DESIGN_NOTE.md §8 names as this module's own precedent)
  gives each fault category its own `_fault_*` function. Defensible: the checks share mutable
  local state accumulated across one pass over gates/conditions, so splitting would either re-walk
  the gate list per check or thread that state across functions. Worth a maintainer's attention if
  a sixth fault category is added.
- **data-clumps** — `_probe_pytest`/`_probe_script`/`_probe_population` all take the identical
  `(gid, cid, cond, *, repo_root)` group and each re-derives `where = f"{gid}.{cid}"`
  independently, where `validate_spine.py`'s own sibling `_fault_*` functions take a pre-built
  `where` once. No documented repo standard mandates one form over the other — style divergence
  from precedent, not a defect.

## Map impact verdict
No map exists in this repo (context step recorded DEGRADED-UNPARSEABLE at plan time); skipped as
not applicable — this is a crew-tier review, not the Commander's own map-orientation gate.

## Reconciliation check
None. The change is wired to nothing yet (`grep -rn "generate_spine" --include=*.py
--include=*.md .` outside `.agent-work` shows every reference living inside
`tests/test_generate_spine.py` itself) — matches the implementer's own wiring-grep finding and the
handoff's stated scope (role-spec authoring is `g2`, not this gate).

## Blockers
- none

## Out-of-scope observations
- `checklist_engine.load_config` crashes with an unhandled `JSONDecodeError` on a non-JSON
  `config_ref` — an oracle gap outside this gate's latitude, flagged as a triage candidate
  (`tc1` in the review survey).
- `validate_spine.py --sweep` still reports 23 pre-existing faults on shipped templates, several
  `falsifiable-unresolved-placeholder` on literal `<exact test command>`-style tokens — exactly
  the class this generator exists to make unauthorable; a natural target once `g2` starts
  replacing hand-authored plan/spine JSON with generated specs (`tc2`).
- MINOR: the dead `_RESOLVER_OWNED_TOKEN_RE` import named above under Code/doc quality.
- MINOR: the two Fowler-flagged style divergences from `validate_spine.py`'s own precedent, named
  above.

## Workflow Feedback

- **Handoff gaps:** None in the reviewer handoff itself — it was precise and every close criterion
  mapped cleanly to a DESIGN_NOTE.md section, matching the implementer's own praise for the same
  property. One gap in the *skill*'s own survey template: `templates/REVIEW_SURVEY.template.json`'s
  `r6-fowler` postcondition command carries a literal, unsubstituted `<work-id>` placeholder
  (`python scripts/verify_fowler_pass.py .agent-work/<work-id>/FOWLER_PASS.json`) and a
  `scripts/`-relative path. Nothing substitutes `<work-id>` automatically for an ad-hoc reviewer
  survey built directly from the template (unlike a spine materialized through
  `init_work_area.py`'s resolver) — I had to notice this myself, `amend --delta ... retext-check`
  it to an absolute path before the fowler-pass script could even be found, with `--authority
  commander` (the dispatching role named in this handoff, per the skill's own instruction not to
  invent an authority string).
- **Context rediscovered:** None beyond the above — DESIGN_NOTE.md and the implementer's own result
  carried everything needed; no digging outside those two documents plus the source/tests was
  required.
- **Instructions improvised around:** The environment handed me `SPINE_FILE`/`SPINE_SESSION`
  pointing at the top-level Commander spine (`execute` gate, session `commander`) rather than
  anything scoped to this review — that is the parent process's own inherited environment, not a
  spine bound to my crew. Per the reviewer skill's own instruction ("do not author a survey when a
  spine is already bound … for the case where nothing is bound"), I built my own survey from
  `REVIEW_SURVEY.template.json` at `.agent-work/epic-559/c2-generate-the-spine/g1-review/review.json`
  rather than touching the Commander's own top-level spine, which I have no authority to drive.
- **What would have made this easier:** Substitute `<work-id>` (and any bundled-script relative
  path) into `r6-fowler`'s postcondition command at template-authoring time, or document
  explicitly in the template that an ad-hoc reviewer survey must do this substitution itself
  before first use — right now the substitution is silently assumed rather than stated as a step.

## Return status
`complete`
