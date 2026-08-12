# IMPLEMENTER_RESULT — `g1-implement` · the generator

Return status: complete

## What I built

Two new files, exactly as scoped:

- `scripts/generate_spine.py` (597 lines) — `CHECK_KINDS`, `spec_shape_faults`, `compile_condition`,
  `compile_spec` (all pure — dict in, dict out, no `Path`/`open`/`subprocess` reachable from them), then
  the probes (`_probe_pytest`, `_probe_script`, `_probe_population`, `probe_spec`), the
  `validate_spine.validate(...)` call, the write, and `main()` — in that order, in the same file, per
  DESIGN_NOTE.md §8.
- `tests/test_generate_spine.py` (978 lines, 76 tests, all fixtures inline — no separate fixture files
  were needed).

No other file was touched. `scripts/validate_spine.py`, `scripts/checklist_engine.py`, and every shipped
template are untouched — imported/called, never edited.

## Required evidence

### 1. The control pairing — both halves, real CLI, nothing written on refusal

```
$ python scripts/generate_spine.py $DEMO/refused.spine.toml --out $DEMO/out.json --root $DEMO
oracle refused: 1
  [falsifiable-unresolved-placeholder] m1.postconditions.c2: command still carries the literal placeholder '<oops>' -- nothing resolves it, so the check can never run, let alone fail
exit: 4
$ test ! -f $DEMO/out.json && echo "CONFIRMED: nothing written"
CONFIRMED: nothing written

$ python scripts/generate_spine.py $DEMO/accepted.spine.toml --out $DEMO/out.json --root $DEMO
wrote /tmp/tmp.QewfdQGr75/out.json
exit: 0
$ test -f $DEMO/out.json && echo "CONFIRMED: exists"
CONFIRMED: exists
$ python -c "...print c2 command..."
items: ['m1']
c2 command: cd <repo-root> && python scripts/target.py --flag real-value
```

Both halves use the **same** spec: a `script` postcondition whose `args` includes a value token
(`<oops>` → `real-value`) that is not a `--flag`, so the generator's own script probe (which only
examines `--`-prefixed tokens) never looks at it. `compile_spec` **translates** both specs identically —
it does not judge. The guarded CLI's refusal comes entirely from `validate_spine.validate()`, the literal
last statement before success: it is the oracle, not the generator's own probes, that is the last word.
Automated in `TestControlPairing` (2 tests, both green).

### 2. Each probe catching VIOLATING, passing INNOCENT, plus a populated ACCEPTED_FALSE_ALARM for the two probes with no oracle behind them

```
tests/test_generate_spine.py::TestPytestProbe::test_violating_is_caught[another nonsense selector] PASSED
tests/test_generate_spine.py::TestPytestProbe::test_violating_is_caught[nonsense selector] PASSED
tests/test_generate_spine.py::TestPytestProbe::test_innocent_is_left_alone[another real class in this file] PASSED
tests/test_generate_spine.py::TestPytestProbe::test_innocent_is_left_alone[real class in this file] PASSED
tests/test_generate_spine.py::TestScriptProbe::test_violating_is_caught[near-miss typo against another real script] PASSED
tests/test_generate_spine.py::TestScriptProbe::test_violating_is_caught[unknown flag against a real script] PASSED
tests/test_generate_spine.py::TestScriptProbe::test_innocent_is_left_alone[exact match] PASSED
tests/test_generate_spine.py::TestScriptProbe::test_innocent_is_left_alone[no flags requested at all -- nothing to check] PASSED
tests/test_generate_spine.py::TestScriptProbe::test_the_accepted_false_alarm_still_fires[long flag in second position] PASSED
tests/test_generate_spine.py::TestScriptProbe::test_never_imports_the_target PASSED
tests/test_generate_spine.py::TestScriptProbe::test_missing_target_is_a_fault PASSED
tests/test_generate_spine.py::TestPopulationProbe::test_violating_too_few PASSED
tests/test_generate_spine.py::TestPopulationProbe::test_violating_too_many PASSED
tests/test_generate_spine.py::TestPopulationProbe::test_innocent_exact_match PASSED
tests/test_generate_spine.py::TestPopulationProbe::test_innocent_band_match PASSED
tests/test_generate_spine.py::TestPopulationProbe::test_the_accepted_false_alarm_still_fires PASSED
tests/test_generate_spine.py::TestMainCLI::test_probe_fault_exit_3 PASSED
tests/test_generate_spine.py::TestUndecidable::test_script_probe_undecidable_refuses PASSED
====================== 19 passed ==========================
```

`script` and `population` (the two probes with no oracle behind them) each carry a **populated**
`ACCEPTED_FALSE_ALARM`, pinned as firing, not fixed, modeled on
`tests/test_mcp_adoption.py::TestTheViolationPredicateItself`:

- **script**: DESIGN_NOTE.md §4 scopes the probe to literals passed as the **first** positional argument
  to `add_argument`. A short-then-long registration (`add_argument("-f", "--foo")`) puts the long form
  second, so a real, legitimately-registered `--foo` is flagged as unknown anyway. This is the design's
  own documented scoping, not a bug I introduced.
- **population**: measured live on this host — `pathlib.Path.glob("**/*.toml")` matches "this directory
  and all subdirectories, recursively," so it **also** matches the top level, not only nested files. An
  author who reads `**/` as "subdirectories only" (the common, intuitive misreading) declares a count
  that excludes the top level and gets a mismatch. I originally assumed the false alarm here was
  dotfile-exclusion (per DESIGN_NOTE.md §4's "do not agree by default on dotfiles" line describing the
  two-implementation disagreement this generator's one-implementation design avoids); I measured it
  directly (`pathlib.Path.glob("*.toml")` against a tree with a dotfile) and found `Path.glob` **does**
  match dotfiles on this host/Python version, so that premise was wrong and I replaced it with the `**`
  case above, which I verified fires.

### 3. `render_human` shows the handback block — actual rendered text

```
ACTIVE m1 [pending] — do the thing
postconditions:
  c1 [unmet] command — tests pass
0/1 met
directives:
  handback:
    purpose: where this gate hands something back -- these are the engine's real, persistent channels, not a field to write prose into
    belief_worth_recording: spine_evidence attach -- lands in this gate's own evidence[]
    open_question_out_of_scope: spine_capture flag-candidate -- lands in the top-level triage_candidates[]
    concern_that_must_stop_this_gate: spine_halt block -- sets status blocked and appends to the top-level blockers[], bubbling to the parent named below
    hand_back_to: admiral-epic-418-followon
    note: there is NO engine verb that appends to a directives field on an active gate (amend rescope touches pending gates only), so this contract names verbs that persist rather than offering arrays that would render empty forever
next: start m1
```

Produced by calling `checklist_engine.current(spine)` directly on the in-memory `compile_spec()` output —
the actual engine adapter, not a JSON-shape assertion (`TestRenderHuman`, 1 test, green). The three
handback verbs are separately driven against a generated spine and asserted to land exactly where the
contract says (`TestHandbackVerbs`, 3 tests, green): `attach` → the gate's own `evidence[]`,
`flag-candidate` → top-level `triage_candidates[]`, `block` → gate `status: "blocked"` + top-level
`blockers[]`.

### 4. Falsification floor — red with the injection deleted, green restored

```
tests/test_generate_spine.py::TestFalsificationFloor::test_baseline_is_green PASSED
tests/test_generate_spine.py::TestFalsificationFloor::test_mutation_kills_it PASSED
======================= 2 passed, 74 deselected in 0.23s =======================
```

`test_baseline_is_green` runs a throwaway single-assertion test (importing the **real**
`generate_spine.py`) in a subprocess and asserts exit 0. `test_mutation_kills_it` reads the real source,
asserts the `c-escalation` injection block occurs **exactly once**, replaces it with `pass`, asserts the
occurrence count dropped by exactly one (the mutation genuinely landed — not a `sed` that silently missed,
the exact hazard `tests/test_mutation_floor.py`'s own docstring names), writes the mutant plus its two
sibling imports (`init_work_area.py`, `validate_spine.py`, so the mutant's own `sys.path` imports still
resolve) to a temp dir, re-runs the same throwaway test against the mutant in a fresh subprocess, and
asserts the run goes **red** and names the specific test that failed.

### 5. `validate_spine.py --sweep` fault count — before and after

Before this change (from the handoff, established baseline): **23**.

```
$ python scripts/validate_spine.py --sweep --root . | grep -cE '^  \['
23
```

Unchanged — I created no new file under `skills/*/templates/` and modified no shipped template, so this
number could not move.

### 6. Full suite, declared test mode

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2765 passed, 3 skipped, 1121 subtests passed in 108.76s (0:01:48)
```

Baseline from the handoff: 2689 passed, 3 skipped, 1121 subtests. `2765 - 2689 = 76` — exactly the new
test count, zero regressions, subtests and skips unchanged.

## Wiring grep

```
$ grep -rn "generate_spine" --include=*.py --include=*.md . | grep -v '\.agent-work'
./tests/test_generate_spine.py:1:"""Tests for scripts/generate_spine.py -- the spine spec compiler and generator.
./tests/test_generate_spine.py:26:import generate_spine as gs  # noqa: E402
./tests/test_generate_spine.py:514:                                                  targets=["tests/test_generate_spine.py"]),
./tests/test_generate_spine.py:516:                                                          targets=["tests/test_generate_spine.py"]),
./tests/test_generate_spine.py:899:# generate_spine.py, and a throwaway test exercising ONLY that postcondition is
./tests/test_generate_spine.py:917:        "import generate_spine as gs\n"
./tests/test_generate_spine.py:947:        original = (ROOT / "scripts" / "generate_spine.py").read_text(encoding="utf-8")
./tests/test_generate_spine.py:957:        (mutant_dir / "generate_spine.py").write_text(mutated, encoding="utf-8")
```

**Every reference is inside `tests/test_generate_spine.py` — its own tests.** `scripts/generate_spine.py`
is built and independently verified, but **nothing outside its own test file calls it yet.** It is not
wired to anything: no role spec, no skill doc, no CI hook, no other script imports it. That wiring — role
specs that call it — is explicitly out of scope for this gate ("Do not write role specs — that is the next
gate") and lands at `g2`.

## Findings

1. **Oracle gap, not fixed (per Specific Exclusions): `checklist_engine.load_config` crashes on a
   non-JSON `config_ref` with an unhandled `JSONDecodeError`, and `validate_spine.py` has no fault for
   it.** DESIGN_NOTE.md §7 names this directly and instructs the generator to refuse it (which
   `spec-config-ref-not-json` in `spec_shape_faults` does) without patching the oracle. Confirmed still
   true by reading `validate_spine.py` in full (no `config_ref` handling anywhere) — restating, not
   discovering, since the design note already named it.
2. **No shipped-template disagreement found.** I compiled representative specs for all five kinds and
   compared shapes against `docs/CHECKLIST_SCHEMA.md`'s Task/Condition tables and the shipped templates I
   read (`COMMANDER_SPINE.template.json`, `EXECUTE_PLAN.template.json`); nothing in the compiler's output
   shape conflicts with what the engine or a shipped template expects.
3. **`validate_spine.py --sweep`'s pre-existing 23 faults are untouched but worth naming for the next
   gate's own awareness:** most are `falsifiable-all-null` on skill templates whose gates are entirely
   qualitative by original design (context-loading gates, mostly), plus two
   `falsifiable-unresolved-placeholder` faults on literal `<exact test command>` placeholders in
   `EXECUTE_PLAN.template.json` and `IMPLEMENTER_PLAN.template.json` — exactly the class of defect this
   generator exists to make unauthorable. Not this gate's scope to fix (no shipped template was touched),
   but a natural target once role specs start replacing hand-authored plan/spine JSON at `g2`.

## Decisions where DESIGN_NOTE.md was silent

1. **`spec-artifact-missing-match` — a tenth spec-shape fault code, not in DESIGN_NOTE.md §7's named
   nine.** §4's artifact section states plainly "a missing `match` is a fault unless `evidence_type` is in
   `ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH`," which is unambiguous *behavior* but was not assigned a code
   in §7's enumerated list. I added `spec-artifact-missing-match`, checked at spec-shape time (before any
   probe), consistent with the note's own stated preference: "failing at the spec is a better error than
   failing at the spine" (used verbatim for `spec-all-qualitative-postconditions`).
2. **Exit code 1 for malformed TOML.** §8 assigns exit 2/3/4 to spec-shape/probes/oracle and exit 0 to
   success, but never names the exit code for step 1 (`tomllib.load` itself failing). I used 1, the next
   available integer, reserving 2–4 exactly as specified.
3. **Undecidable's exit code follows the layer that discovered it, not a single dedicated code.** A
   probe-layer undecidable (e.g. the `script` kind's own "no `add_argument` literals at all" case) exits
   3, folded into the same bucket as an ordinary probe fault, since §4 places the script probe's
   undecidable case inside the probe's own described behavior. An oracle-layer undecidable
   (`validate_spine.validate()`'s `.undecidable` channel) exits 4, alongside an ordinary oracle `Fault`,
   since both come from the same call. §8 never splits these further, and I judged one refusal-exit-code
   per layer (rather than a fifth dedicated "undecidable" exit code) to be the simpler, equally-honest
   reading — both are still refusals, and `main()`'s stdout always names *which* channel fired
   (`"undecidable -- could not tell"` vs `"probe refused"` / `"oracle refused"`), so nothing is
   collapsed into silence.
4. **`directives.claim`'s explanatory field is named `note`, not given a name in the note.** DESIGN_NOTE.md
   §6 says the rendered claim carries "`magnitude`, `text`, and why the extra postcondition is there" but
   does not name the third key. I used `note`, matching the sibling naming already used inside
   `directives.handback`'s own `note` field for the same kind of "why this is here" explanation.
5. **`directives.claims_rollup` is omitted entirely (not an empty dict) on the last gate when no gate in
   the spec carries a large claim.** §6 says the rollup "rolls up into `directives.claims_rollup` on the
   last gate," which is silent on the zero-claims case. I chose omission over an always-present empty dict
   to keep the "populated fields only" convention consistent with `render_human`'s own documented rule
   (`docs/CHECKLIST_SCHEMA.md` §Rendering: "omitted entirely when absent or empty, so an unpopulated field
   adds no output").
6. **Population's band-form shell text.** §4 names the exact command for the exact-count form but only
   describes the band form in prose ("capture the count once into a shell variable and compare `-ge MIN`
   and `-le MAX`"). I wrote: `cd <repo-root> && n=$(<count-command>) && test "$n" -ge MIN && test "$n" -le
   MAX`, quoting `"$n"` for safety and reusing the identical count-command Python one-liner as the exact
   form (same probe, same emitted text — one implementation, per §4's own stated goal).
7. **`main`'s positional spec-file argument name (`spec`) and `--out`/`--root`/`--check-only` flag names**
   were not specified beyond the invocation shape `python scripts/generate_spine.py <spec.toml> --out
   <spine.json> --root . [--check-only]` in §8 — I matched that shape exactly; only the internal
   `argparse` destination name (`args.spec`) was my own choice.

## Workflow Feedback

- **The handoff and DESIGN_NOTE.md were unusually well-matched to the work** — every close criterion had
  a traceable DESIGN_NOTE.md section, and the "where the note and your judgment disagree, the note wins;
  where it is silent, decide and say so" framing made the silent spots (above) easy to resolve
  confidently rather than guess-and-hope. Nothing about the handoff itself blocked or misled me.
- **One friction point, self-inflicted and worth naming so a future generator-author gate doesn't repeat
  it:** I initially wrote an `ACCEPTED_FALSE_ALARM` population fixture based on an *assumption* about
  `pathlib.Path.glob`'s dotfile behavior (extrapolating from DESIGN_NOTE.md §4's prose about a
  two-implementation disagreement) rather than measuring it first. It was wrong — this host's
  `Path.glob("*.toml")` **does** match dotfiles — and the test failed loudly instead of silently, which is
  the system working as intended, but it cost a cycle. The lesson, specific to this codebase: DESIGN_NOTE.md
  prose describing filesystem/stdlib *behavior* (as opposed to *this generator's own design decisions*) is
  a hypothesis to verify with a two-line `python3 -c` probe before it goes into a fixture, not a fact to
  build on directly — the note itself is about a *different* implementation's disagreement (Python-glob vs
  shell-glob), which this generator's one-implementation design sidesteps, so its dotfile claim doesn't
  transfer automatically to my specific probe. I found and fixed this myself during the same TDD cycle
  before advancing the gate, so it never reached a reviewer, but it's worth surfacing since it is exactly
  the kind of "looks right, wasn't measured" defect this whole epic exists to close, and I nearly
  reproduced its shape in my own guard fixture.
- **`docs/agents/engine-config.json` (used as the default `config_ref` in my test fixtures, following
  DESIGN_NOTE.md §3's own example) does not exist in this repo.** Harmless for my tests (my
  `spec-config-ref-not-json` check only fires when the file exists and fails to parse; a missing file is
  silently accepted, matching DESIGN_NOTE.md §7's own precise framing of the crash it names), but worth
  flagging since the design note's own worked example names a config path that isn't present on disk.
