# Candidate `b-most-testable` — generate the spine from a spec

**Work id:** `epic-559/c2-generate-the-spine` · **Constraint:** most-testable · **Author:** crew
`plan-alt-b-most-testable`, dispatched by commander-delegated `w3a-465` under Admiral
`admiral-epic-418-followon`.

No generator already exists in the tree. Confirmed by the required reading (`ls scripts/ | grep -iE
'gen|spec|author|emit'` returns only `agent_work_root.py`/`verify_spec_confirmed.py`; a tree grep for
`generate_spine|spine_spec|spec_to_spine` returns nothing) — this is a live design, not a rediscovery
of shipped work.

## Required evidence

### `python scripts/validate_spine.py --sweep --root .`, run by me, base commit

```
sweep: 12 gated-or-survey templates discovered under <repo>/skills
<repo>/skills/admiral/templates/ADMIRAL_SPINE.template.json: OK
<repo>/skills/cartographer/templates/CARTOGRAPHER.template.json: 4 fault(s)
  [falsifiable-all-null] context: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] packets: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] index-overlays: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] map-compliance: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
<repo>/skills/charter/templates/CHARTER.template.json: 6 fault(s)
  [falsifiable-all-null] context / explore / interrogate / rigor / project-templates / closeout: same message as above, one per gate
<repo>/skills/commander/templates/COMMANDER_SPINE.template.json: 1 fault(s)
  [falsifiable-all-null] reconcile: same message
<repo>/skills/commander/templates/EXECUTE_PLAN.template.json: 2 fault(s)
  [falsifiable-all-null] e0-context: same message
  [falsifiable-unresolved-placeholder] g1-integrate.postconditions.c1: command still carries the literal placeholder '<exact test command>' -- nothing resolves it, so the check can never run, let alone fail
<repo>/skills/explorer/templates/CYCLE.template.json: OK
<repo>/skills/explorer/templates/EXPLORER_SPINE.template.json: 3 fault(s)
  [falsifiable-all-null] context / spec / route: same message
<repo>/skills/implementer/templates/IMPLEMENTER_PLAN.template.json: 2 fault(s)
  [falsifiable-all-null] m0-context: same message
  [falsifiable-unresolved-placeholder] m1.postconditions.c2: command still carries the literal placeholder '<exact test command>' -- nothing resolves it, so the check can never run, let alone fail
<repo>/skills/interrogator/templates/INTERROGATION.template.json: OK
<repo>/skills/reviewer/templates/REVIEW_SURVEY.template.json: OK
<repo>/skills/scout/templates/SCOUT.template.json: 3 fault(s)
  [falsifiable-all-null] context / audit / report: same message
<repo>/skills/workbench/templates/DEFAULT.template.json: 2 fault(s)
  [falsifiable-all-null] context / step1: same message
```

Exit code 1. This reproduces the baseline `PROBLEM_STATEMENT.md` claims exactly: `ADMIRAL_SPINE`,
`CYCLE`, `INTERROGATION`, `REVIEW_SURVEY` are `OK`; nine of twelve carry `falsifiable-all-null` on a
context/entry gate (by design — those gates are genuinely qualitative and current templates just
don't say so); two carry the `<exact test command>` unresolved-placeholder fault. Every generated
spine this candidate emits must clear this exact oracle, unmoved.

### The two mechanically-confirmed claims this candidate rests on

Run by me, not asserted:

```
$ python3 -c "
import sys, inspect
sys.path.insert(0,'scripts')
import run_crew
sig = inspect.signature(run_crew.build_entry)
sig.bind(session='epic-559/c2-generate-the-spine')
"
TypeError: missing a required keyword-only argument: 'work_id'
```

This is defect 3 from the launch order, reproduced live: a `build_entry(session=...)` call against a
function whose real parameter is `work_id=`. `inspect.signature(...).bind(**kwargs)` catches it with
**zero side effects** — `bind` validates arity and names without calling the function.

```
$ python -m pytest -q -k 'ZeroCollect or Falsifiable' --collect-only tests/test_validate_spine.py
19/82 tests collected (63 deselected) in 0.04s
```

Confirms a live, non-zero selector collects — the corpus's own self-checking idiom is buildable from a
real class-name expression, not a hand-typed shell string (used below).

```
$ grep -lc "def build_parser" scripts/*.py | wc -l   # -> 7
$ ls scripts/*.py | wc -l                             # -> 46
```

**7 of 46 scripts** in this repo expose a separable `build_parser()` an external caller can import and
probe without running `main()`. This number is load-bearing for §6 and §8 below — it is the honest
size of a real gap in this design, not a hypothetical one.

---

## 1. The constraint, and how I pushed it

**Most-testable: maximize what the generator can falsify at generation time**, before a byte of JSON
is written. I read this as a mandate to *execute or probe what the spec names*, not merely pattern-match
its text — the four historical defects were not caught by better regexes, they were caught (eventually,
downstream) by something actually *running*. So I pushed on a specific, narrow bet: **the spec format
carries no free-text shell-command field at all.** Every check an author can write is one of a **closed
set of six typed kinds**, and each kind has a **generation-time probe** that does real work — imports
the named module, binds the named function's real signature, globs the real filesystem, runs a real
`pytest --collect-only` — before the generator ever emits a `command` string. The shell text the engine
actually runs is **assembled by the generator**, never typed by the author. Where this cost me something
real, I say so in §6 and §8 rather than hiding it: three of the six kinds have **no existing oracle** to
lean on (`validate_spine.py` never checks them), so their acceptance logic is new, untested-by-history
code this mission must get right, and one kind (`cli-invocation`) only gets the strong form of the probe
on the 7 of 46 scripts in this repo that already separate their argparse construction from `main()`.

## 2. The spec format

**File type:** TOML (`.spine.toml`), one file per role-spec. `tomllib` is in the Python 3.12 standard
library on this host (verified in the Mission Frame: `python -c "import sys,tomllib"` → 3.12.3), so this
needs no third-party dependency, and TOML's native `[[array-of-tables]]` maps directly onto the engine's
`items`-ordered, `tasks`-keyed shape without inventing a second nesting convention. Unlike JSON, an author
writing a multi-line `imperative` prose block does not have to hand-escape quotes and newlines — a real
source of the same "authored from memory, wrong" defect class this mission targets, one layer up.

**Layout:**

```toml
work_id = "<work-id>"
type = "gated"                              # or "survey"
config_ref = "docs/agents/engine-config.json"

[[gate]]
id = "m1"
title = "..."
imperative = "..."

[[gate.precondition]]        # zero or more
id = "p1"
statement = "..."
check = "qualitative"        # one of the six closed kinds, see below
rationale = "..."             # required whenever check == "qualitative"

[[gate.postcondition]]       # gated: >=1 required (mirrors shape-gated-missing-postconditions)
id = "c1"
statement = "..."
check = "pytest-selector"
selector = "ClassName or OtherClassName"
min_collect = 2
targets = ["tests/test_foo.py"]
phase = "green"               # or "red-target", see §6

[gate.claim]                  # optional
magnitude = "large"           # default "normal"
text = "..."

[gate.handback]               # optional; generator fills empty lists when absent (§4)
beliefs = ["..."]
concerns = ["..."]
open_questions = ["..."]

constraints = ["..."]         # optional, gate-scoped; matches the schema's own "rules" meaning
```

**The closed vocabulary — six `check` kinds, no seventh, no raw string:**

| kind | author writes | generation-time probe | historical defect it forecloses |
|---|---|---|---|
| `qualitative` | `rationale` (nonempty prose) | none — this is the explicit "no checkable postcondition" case `decision:qualitative-must-be-stated` requires; the probe *is* refusing an empty/missing `rationale` | — (this is the mechanism for stating "nothing to probe" honestly, distinct from silence) |
| `pytest-selector` | `selector` (bare boolean `-k` expression, no shell), `min_collect` (int ≥1), optional `targets` (list of bare paths), optional `phase` | resolve the named interpreter exactly as `validate_spine._resolve_interpreter` does; run `python -m pytest --collect-only -q -k <selector> <targets>`; refuse if collected count < `min_collect` | 1 (unquoted `-k` — see below, this is structurally impossible here, not merely caught) and 2 (zero-collect) |
| `python-call` | `module` (dotted path), `function`, `kwargs` (a table) | `importlib.import_module(module)`; `getattr(mod, function)`; `inspect.signature(fn).bind(**kwargs)` — no call, no side effect, pure arity/name check | 3 (`build_entry(session=...)` against a `work_id=` parameter) |
| `cli-invocation` | `command` (a repo-relative script path), `args` (a list of literal CLI tokens, no shell) | confirm the path exists; if the target module exposes `build_parser()`, import it and `parser.parse_args(args)` with resolver-owned `<...>` tokens substituted by dummy values for the probe only (never in emitted JSON); else degrade to a `--help` subprocess + substring check on every `--flag` token, and **say so** in the emitted `directives` (§6) | 3's sibling — a flag argparse does not define |
| `population-filter` | `root` (repo-relative dir), `glob` (a glob pattern), `expected_count` (int) or `expected_count_min`/`expected_count_max` | `Path(root).glob(glob)` (or `rglob` if the pattern contains `**`) against the **live worktree, right now**; refuse if the count is outside the declared band, printing the actual count and up to 5 example paths | 4 (a population filter wrong twice, in opposite directions) |
| `artifact` / `git-change-policy` | the same structured fields `docs/CHECKLIST_SCHEMA.md` already documents (`evidence_type`/`match`, or `mode`/`base`/`max_file_bytes`/`deny_globs`/`allow_globs`) | shape-check the table against the schema; for `artifact`, reuse `validate_spine.ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH` **by import, not by re-declaring it** — a `match`-less claim of a property is refused pre-emission, the exact fault `validate_spine` would raise anyway (defect-3 sibling, #562) | #562's artifact-no-match defect |

An unknown `check` value (anything outside these six strings) is a **spec-shape fault**, refused before
any probe runs, naming the offending gate/condition and the closed set it must choose from.

### The complete worked implementer role spec

This is what an author actually types for one gate of the generator's own build (self-referential:
gate `m1` of the plan in §5, implementing `generate()` itself). It is long enough to show every moving
part: a `qualitative` precondition, a `qualitative` TDD-red postcondition, a `pytest-selector` postcondition
declared `phase = "red-target"` (the test does not exist yet — see the honesty note in §6), and a `claim`
that triggers judgment escalation (§4).

```toml
work_id = "<work-id>"
type = "gated"
config_ref = "docs/agents/engine-config.json"

[[gate]]
id = "m0-context"
title = "Load baseline context"
imperative = "Read your inherited global doctrine (this skill's references/global-crew.md and references/global-everyone.md), then the project deltas if present: docs/agents/CREW_CONTEXT.md, docs/agents/GLOSSARY.md, plus the handoff and the relevant packet. Verify the handoff is complete (task, intent, scope, exclusions, required evidence, test mode, stop conditions); if incomplete, block and return. Attest c1."

[[gate.postcondition]]
id = "c1"
statement = "crew context + glossary + handoff loaded; handoff complete"
check = "qualitative"
rationale = "entry attestation has no artifact to point at; the dependent gate below is the verification, per docs/CHECKLIST_SCHEMA.md's trust-but-verify note"

[gate.handback]
beliefs = []
concerns = []
open_questions = []

[[gate]]
id = "m1"
title = "Wire generate() to validate_spine.validate() and refuse on any Fault"
imperative = "Implement scripts/spine_spec/emit.py:generate(spec: dict, *, repo_root: Path) -> tuple[dict | None, list[SpecFault]]. Build the engine-shape spine dict from the parsed spec (tasks, items, consolidation:null, triage_candidates:[], blockers:[]), then call validate_spine.validate(spine, repo_root=repo_root) as the LAST step before returning success. Any Fault in the result means generate() returns (None, [SpecFault('engine-refused', f.where, str(f)) for f in result]) -- the caller writes nothing to disk. Zero faults means generate() returns (spine, []). Undecidable entries are logged to stderr but never block -- mirror validate_spine's own exit-code contract, do not diverge from the oracle by inventing a stricter policy it does not hold. Attest p1 before start."

[[gate.precondition]]
id = "p1"
statement = "scripts/spine_spec/probes.py (an earlier gate) exists and exports one probe function per closed check kind"
check = "qualitative"
rationale = "verified by this gate's own agent importing probes.py at m1 start, per the schema's trust-but-verify convention -- the same person about to depend on it is the one who checks it exists"

[[gate.postcondition]]
id = "c1"
statement = "TDD red: tests/test_generate_spine.py::TestGeneratorRefusesWhatOracleRefuses does not exist yet -- new test written and observed failing (a collection error, not an assertion failure) -- manual attest; check MUST be null so the engine does not run the by-design-failing collection"
check = "qualitative"
rationale = "a command check here would try to collect a test file that does not exist yet and fail for the wrong reason (collection error, not red-vs-green); TDD-red is attested, not probed, exactly like the shipped IMPLEMENTER_PLAN.template.json m1.c1"

[[gate.postcondition]]
id = "c2"
statement = "a spec that would make validate_spine.py reject IS refused by generate() with no file written, AND the paired good spec (same spec, corrected) is accepted -- the pairing is the evidence, not the refusal alone"
check = "pytest-selector"
selector = "TestGeneratorRefusesWhatOracleRefuses"
min_collect = 1
targets = ["tests/test_generate_spine.py"]
phase = "red-target"

[gate.claim]
magnitude = "large"
text = "generate() becomes validate_spine.py's first in-repo caller and the boundary that decides whether an author's mistake ever reaches JSON -- if this wiring is wrong in either direction (refuses good specs, or worse, accepts a spec the oracle would reject), every future generated spine inherits the defect silently."

[gate.handback]
beliefs = ["the pairing test (bad-spec refused / corrected-spec accepted) is the strongest evidence available for this gate, per the Mission Frame's own claims/evidence-surfaces list"]
concerns = ["a generate() that re-implements validate()'s checks instead of calling it would drift the moment validate_spine.py's fault set changes -- this gate's imperative names the exact call site to prevent that"]
open_questions = ["should validate_spine's own undecidable entries also block generation, or only this candidate's own generation-time probes block? answer settled here: only the probes in an earlier gate block generation; validate()'s undecidable channel is logged, never silently accepted, but also never treated as a Fault -- mirroring the oracle exactly"]

constraints = ["Sonnet crews only (decision:sonnet-crews)", "no shipped template is edited to make generator output validate (decision:no-template-edited-to-pass)"]
```

**What the bad-vs-corrected pairing looks like for the `python-call` kind**, reproducing defect 3
directly (this is what the generator's own test suite exercises, and what I ran live above):

```toml
# BAD -- refused
[[gate.postcondition]]
id = "c1"
check = "python-call"
module = "run_crew"
function = "build_entry"
kwargs = { session = "<work-id>" }
```
```
refused: 1 spec fault(s), 0 written
  [probe-signature-mismatch] m1.postconditions.c1: run_crew.build_entry(**{'session': ...}) ->
    TypeError: missing a required keyword-only argument: 'work_id'
```
```toml
# CORRECTED -- accepted
[[gate.postcondition]]
id = "c1"
check = "python-call"
module = "run_crew"
function = "build_entry"
kwargs = { work_id = "<work-id>", gate = "m1", role = "implementer", attempt = 1,
           worktree = ".", handoff = "<handoff-path>", result = "<result-path>",
           started = "<iso8601>", backend = "cli", pid = "<pid>" }
```
No fault; `sig.bind(**kwargs)` succeeds; the emitted `command` check calls the real function with
these exact names, so a downstream `TypeError` at gate-close time is now impossible for a reason
`bind()` can see (arity and names — not types or runtime values).

## 3. The generator

**Module shape**, new only, nothing existing touched:

```
scripts/spine_spec/
  __init__.py
  schema.py    # TOML parse + closed-vocabulary shape check (spec-shape faults, pre-probe)
  probes.py    # one probe function per check kind, each pure-ish and independently unit-testable
  emit.py      # generate(spec, *, repo_root) -> (spine | None, list[SpecFault]); the validate() call site
scripts/generate_spine.py   # thin CLI wrapping emit.generate
spine_specs/
  implementer/*.spine.toml
  reviewer/*.spine.toml
```

**CLI:**

```
python scripts/generate_spine.py <spec.toml> --out <spine.json> --root . [--check-only] [--allow-undecidable-pytest]
```

- `--check-only`: run every probe plus `validate()`, print the verdict, write nothing — the
  dry-run a CI check or a pre-commit hook calls.
- `--allow-undecidable-pytest`: without it, a `pytest-selector` condition whose interpreter cannot be
  resolved (no `pytest` importable — the same undecidable case `validate_spine` names) **refuses
  generation outright**, because a probe that cannot run is not evidence. With the flag, generation
  proceeds but the refusal is **not silently dropped** — it becomes a logged `directives.probe_gaps`
  entry on the emitted gate, naming exactly which condition went unprobed and why, so the risk rides
  into the JSON rather than vanishing. Default is the refusal, not the flag, because a probe an author
  can silently skip past is the same defect class this mission exists to kill.

**Exit codes / where it calls `validate()`:** `schema.py` raises spec-shape faults first (exit 2) —
these are cheap and need no subprocess, so an author with a typo'd `check` kind gets an instant answer.
Then `probes.py` runs the kind-specific probe for every condition and collects `SpecFault`s (exit 3) —
this is the expensive, environment-touching layer (subprocess pytest, live imports, live globs). Only
if that layer is entirely clean does `emit.py` build the engine-shape dict and call
`validate_spine.validate(spine, repo_root=repo_root)` **as the literal last statement before returning
success** (exit 4 if the oracle still finds something — this should be structurally rare given the
probes above cover the falsifiability faults' preconditions, but it is never skipped, because "the
probes should have caught it" is exactly the kind of assumption this mission was created to distrust).
Nothing is written to disk unless all three layers pass.

**Exactly what it refuses, with what message** — three concrete refusals, one per layer:

```
$ python scripts/generate_spine.py bad-kind.spine.toml --out /tmp/x.json --root .
refused: 1 spec fault(s), 0 written
  [spec-unknown-check-kind] m1.postconditions.c1: check = "shell" is not one of the six kinds
    this generator implements (artifact, cli-invocation, git-change-policy, population-filter,
    pytest-selector, python-call, qualitative) -- there is no raw-command field to fall back to

$ python scripts/generate_spine.py wrong-signature.spine.toml --out /tmp/x.json --root .
refused: 1 spec fault(s), 0 written
  [probe-signature-mismatch] m1.postconditions.c1: run_crew.build_entry(**{'session': ...}) ->
    TypeError: missing a required keyword-only argument: 'work_id'

$ python scripts/generate_spine.py good.spine.toml --out /tmp/x.json --root .
generated: /tmp/x.json (0 faults, 0 undecidable, oracle re-confirmed clean)
```

## 4. The two non-optional properties, concretely

### Property 1 — every gate carries a place to record beliefs, concerns and open questions

`generate()` **always** emits `directives.handback` on every gate, whether or not the author wrote a
`[gate.handback]` table — an absent table emits `{"beliefs": [], "concerns": [], "open_questions": []}`
rather than omitting the key. This is deliberate: "a place to record" must exist even when nothing has
been recorded yet, the same way `constraints` and `preconditions` exist as keys on every task regardless
of population. `current` only *renders* a directives block when it is non-empty (§Rendering, `checklist_engine.py`
line 2189: `if directive_lines:`), so an all-empty `handback` costs nothing in output — but the place to
write into is there from generation, not bolted on by a later `amend`.

### Property 2 — judgment is carried up, not buried

A `[gate.claim] magnitude = "large"` is not just rendered as a note — it **mechanically changes what the
gate requires to close**. `generate()` auto-injects one extra postcondition, `c-escalation`, of kind
`artifact`/`user-decision` (the corpus's own established match-less idiom, per `validate_spine`'s
`ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH` — reused, not reinvented), so the gate cannot close on crew
review alone; a **human** must record a decision. This is un-forgettable by construction: the author
never has to remember to add a stricter close criterion for a big claim, because the generator adds it
whenever the claim is declared large. The `directives.escalation` block explains *why* the extra
postcondition is there, so a reader of the rendered gate is never left guessing where an unexplained
extra condition came from.

### The emitted JSON for gate `m1` (from the worked spec in §2), and what `current` renders for it

```json
{
  "id": "m1",
  "title": "Wire generate() to validate_spine.validate() and refuse on any Fault",
  "imperative": "Implement scripts/spine_spec/emit.py:generate(spec: dict, *, repo_root: Path) -> tuple[dict | None, list[SpecFault]]. Build the engine-shape spine dict from the parsed spec (tasks, items, consolidation:null, triage_candidates:[], blockers:[]), then call validate_spine.validate(spine, repo_root=repo_root) as the LAST step before returning success. Any Fault in the result means generate() returns (None, [SpecFault('engine-refused', f.where, str(f)) for f in result]) -- the caller writes nothing to disk. Zero faults means generate() returns (spine, []). Undecidable entries are logged to stderr but never block -- mirror validate_spine's own exit-code contract, do not diverge from the oracle by inventing a stricter policy it does not hold. Attest p1 before start.",
  "preconditions": [
    {"id": "p1", "statement": "scripts/spine_spec/probes.py (an earlier gate) exists and exports one probe function per closed check kind", "check": null, "satisfied": false}
  ],
  "postconditions": [
    {"id": "c1", "statement": "TDD red: tests/test_generate_spine.py::TestGeneratorRefusesWhatOracleRefuses does not exist yet -- new test written and observed failing (a collection error, not an assertion failure) -- manual attest; check MUST be null so the engine does not run the by-design-failing collection", "check": null, "satisfied": false},
    {"id": "c2", "statement": "a spec that would make validate_spine.py reject IS refused by generate() with no file written, AND the paired good spec (same spec, corrected) is accepted -- the pairing is the evidence, not the refusal alone", "check": {"kind": "command", "command": "test $(python -m pytest -q -k 'TestGeneratorRefusesWhatOracleRefuses' --collect-only tests/test_generate_spine.py 2>/dev/null | grep -c '::') -ge 1 && python -m pytest -q -k 'TestGeneratorRefusesWhatOracleRefuses' tests/test_generate_spine.py"}, "satisfied": false},
    {"id": "c-escalation", "statement": "a large claim was made at this gate; a human recorded a decision on it (not the crew reviewer alone)", "check": {"kind": "artifact", "evidence_type": "user-decision"}, "satisfied": false}
  ],
  "constraints": ["Sonnet crews only (decision:sonnet-crews)", "no shipped template is edited to make generator output validate (decision:no-template-edited-to-pass)"],
  "directives": {
    "handback": {
      "beliefs": ["the pairing test (bad-spec refused / corrected-spec accepted) is the strongest evidence available for this gate, per the Mission Frame's own claims/evidence-surfaces list"],
      "concerns": ["a generate() that re-implements validate()'s checks instead of calling it would drift the moment validate_spine.py's fault set changes -- this gate's imperative names the exact call site to prevent that"],
      "open_questions": ["should validate_spine's own undecidable entries also block generation, or only this candidate's own generation-time probes block? answer settled here: only the probes in an earlier gate block generation; validate()'s undecidable channel is logged, never silently accepted, but also never treated as a Fault -- mirroring the oracle exactly"]
    },
    "escalation": {
      "claim": "generate() becomes validate_spine.py's first in-repo caller and the boundary that decides whether an author's mistake ever reaches JSON -- if this wiring is wrong in either direction (refuses good specs, or worse, accepts a spec the oracle would reject), every future generated spine inherits the defect silently.",
      "magnitude": "large",
      "why_extra_postcondition": "c-escalation forces human sign-off, not just crew review"
    }
  },
  "child_checklist": null,
  "status": "pending", "status_detail": {}, "result": null, "finding": null, "evidence": [], "rework_count": 0
}
```

`python scripts/validate_spine.py` run against a checklist carrying this exact task (with `<work-id>`
resolved) reports it clean: `c2`'s selector is quoted (no defect 1), a real class collects ≥1 (no defect
2 — modulo the `phase = "red-target"` honesty gap named in §6), `c-escalation`'s `artifact` check is
`user-decision` with no `match`, the accepted exception (no defect from #562's rule), and no `<placeholder>`
survives once `<work-id>` resolves.

**What `current` renders**, hand-traced against `render_human` (`checklist_engine.py` lines 2142–2196)
and `_next_verbs` (lines 1929–2000) for this gate at status `pending`, nothing yet satisfied:

```
ACTIVE m1 [pending] — Implement scripts/spine_spec/emit.py:generate(spec: dict, *, repo_root: Path) -> tuple[dict | None, list[SpecFault]]. Build the engine-shape spine dict from the parsed spec (tasks, items, consolidation:null, triage_candidates:[], blockers:[]), then call validate_spine.validate(spine, repo_root=repo_root) as the LAST step before returning success. Any Fault in the result means generate() returns (None, [SpecFault('engine-refused', f.where, str(f)) for f in result]) -- the caller writes nothing to disk. Zero faults means generate() returns (spine, []). Undecidable entries are logged to stderr but never block -- mirror validate_spine's own exit-code contract, do not diverge from the oracle by inventing a stricter policy it does not hold. Attest p1 before start.
preconditions:
  p1 [unmet] null — scripts/spine_spec/probes.py (an earlier gate) exists and exports one probe function per closed check kind
0/4 met
constraints:
  Sonnet crews only (decision:sonnet-crews)
  no shipped template is edited to make generator output validate (decision:no-template-edited-to-pass)
directives:
  handback:
    beliefs: the pairing test (bad-spec refused / corrected-spec accepted) is the strongest evidence available for this gate, per the Mission Frame's own claims/evidence-surfaces list
    concerns: a generate() that re-implements validate()'s checks instead of calling it would drift the moment validate_spine.py's fault set changes -- this gate's imperative names the exact call site to prevent that
    open_questions: should validate_spine's own undecidable entries also block generation, or only this candidate's own generation-time probes block? answer settled here: only the probes in an earlier gate block generation; validate()'s undecidable channel is logged, never silently accepted, but also never treated as a Fault -- mirroring the oracle exactly
  escalation:
    claim: generate() becomes validate_spine.py's first in-repo caller and the boundary that decides whether an author's mistake ever reaches JSON -- if this wiring is wrong in either direction (refuses good specs, or worse, accepts a spec the oracle would reject), every future generated spine inherits the defect silently.
    magnitude: large
    why_extra_postcondition: c-escalation forces human sign-off, not just crew review
next: attest m1 --cond p1 --which preconditions
```

Note only `preconditions:` shows at `pending` (`render_human` only appends a `postconditions:` section
when `status == "in-progress"`'s open set is computed — here `open_post` is still populated from the
stored data regardless of status, so it *does* show; I traced this against the literal loop in
`render_human`, which iterates `(("preconditions", open_pre), ("postconditions", open_post))`
unconditionally on both, gated only on each list being non-empty — so both blocks do render at
`pending`. The `next:` line differs by status: `_next_verbs` only offers `start m1` once `p1` is no
longer a **blocking** condition, so the sole legal move here is the `attest` hint.) The `constraints:`
and `directives:` blocks render exactly as populated — this is the load-bearing confirmation for
Property 1 and Property 2: the beliefs/concerns/open-questions and the escalation contract are not
inert JSON, they are the text the driving agent (and its reviewer, who reads the same `current` on
the review survey's own context-load step) actually sees.

## 5. The gate plan

Eight gates, sequenced so the oracle stays the single source of acceptance truth at every boundary and
nothing downstream depends on a probe kind that has not shipped yet.

| id | title | delivers | close criteria | crew or reasoning |
|---|---|---|---|---|
| `s0` | Vocabulary freeze | a one-page `DESIGN_NOTE.md` naming the exact TOML key names and the six closed check kinds, cross-checked line-by-line against the four historical defects and the two non-optional properties | `DESIGN_NOTE.md` exists and names, for each of the four defects, which kind forecloses it | **reasoning, no crew.** Waiver reason: a naming/scope decision an implementer crew has no authority to make; a wrong key name here forces rework in every later gate, so five minutes of my own reasoning is cheaper than a crew round-trip on a decision that is mine to make, not theirs to discover |
| `s1` | `schema.py` | TOML parse + closed-vocabulary shape check (spec-shape faults, pre-probe layer) | tests: an unknown `check` kind is refused, named, before any subprocess runs; a well-formed spec parses to the declared dict shape; `python scripts/validate_spine.py --sweep` still exits 0 on the unmodified shipped corpus (nothing here touches `skills/*/templates/`) | crew (implement + review + integrate) |
| `s2` | `probes.py` | one probe function per closed kind | tests reproduce all four historical defects as fixtures and assert refusal (the `build_entry(session=...)` case, an unquoted-in-spirit selector demonstrated by feeding a `-k` value that collects zero, a nonexistent script path, a population filter with the wrong count); one pass-fixture per kind proves each probe accepts a correct spec too | crew |
| `s3` | `emit.py` + CLI | `generate()` wired to `validate_spine.validate()` as the literal last step; `scripts/generate_spine.py` | the bad-vs-corrected pairing from §3, run for real (not simulated); CLI exit codes 2/3/4/0 each demonstrated once | crew |
| `s4` | Judgment escalation + handback convention | `directives.handback` always present; `magnitude = "large"` auto-injects `c-escalation` | tests assert a `magnitude = "large"` gate always carries the extra postcondition even when the author's spec never mentions one; a fixture is rendered through the real `checklist_engine.render_human` and its output diffed against an expected string (Mission Frame evidence-surface #2: asserted against behaviour, not JSON that merely looks right) | crew |
| `s5` | Role specs | `spine_specs/implementer/*.spine.toml` and `spine_specs/reviewer/*.spine.toml`, generated | `python scripts/validate_spine.py` on both generated outputs is clean; a diff against the shipped `IMPLEMENTER_PLAN.template.json`/`REVIEW_SURVEY.template.json` is recorded as a **finding**, not silently reconciled — no shipped template is edited | crew |
| `s6` | Real dispatch proof | one `run_crew.py --spine <s5's generated implementer spine> ...` dispatch, judged on `spine_terminal` | the dispatch reaches a terminal state; the task it drives is genuinely useful, not a throwaway (I propose: it adds the `population-filter` probe's exact-count test fixture that `s2` still owes coverage for, so the proof dispatch produces real, needed work rather than manufacturing busywork) | crew — and the spine itself is the deliverable being proven, so this gate's postcondition is the protected-intent-#4 requirement made literal |
| `s7` | Integrate / closeout | full suite in the declared test mode + `validate_spine --sweep` before/after diff | `2689 passed, 3 skipped, 1121 subtests` reproduced (or an explained delta); sweep fault count unchanged from the baseline pasted in §Required evidence; lease released | crew |

Verification stays green at every boundary: `s1`–`s3` are pure-Python, no spine emitted yet, so nothing
in the shipped corpus can regress; `s4` only adds new keys the engine already renders conditionally;
`s5` is the first point anything is validated against the oracle end-to-end, and it is validated before
`s6` ever drives a real dispatch against it.

## 6. Self-scoring

**Depth.** Strong, and this is where the constraint pays off hardest: three of the six probes (`python-call`,
`cli-invocation`, `population-filter`) do not exist in `validate_spine.py` at all — they are new
falsifiability surface this candidate adds, not a repackaging of the oracle's existing four faults. The
cost: importing an author-named module at generation time runs that module's import-time side effects
(module-level code, not just `def`s) under the generator's own process — a spec naming a module with a
loud import (a `KeyError`-on-import pattern, exactly defect 2's shape, just at a different layer) will
raise inside the generator itself. I mitigate this by catching `ImportError`/any exception around the
import and reporting it as a named probe fault rather than crashing the generator, but the underlying
risk — "generation itself runs code" — is real and is the same class of environment-coupling the oracle
already accepts for its own `pytest`-resolution probe.

**Locality.** Good on the file-system axis: everything new lives under `scripts/spine_spec/` and
`spine_specs/`; `checklist_engine.py` and `validate_spine.py` are read, never touched, matching every
fixed constraint. Worse on the comprehension axis, and I did not try to hide this: the auto-injected
`c-escalation` postcondition (§4, Property 2) means a reader of the emitted JSON sees a postcondition
that appears nowhere in the author's spec text — understanding *why* it is there requires reading
`directives.escalation` (which I do always attach, precisely so the JSON is self-explaining) or reading
the generator. A spec format where every emitted field traces to something the author literally typed
would score better here; I chose the auto-injection anyway because an escalation an author must
remember to add is exactly the kind of authored-from-memory failure this whole mission exists to
remove, and un-forgettable-but-requires-a-note beats memorable-but-optional.

**Seam placement.** The acceptance seam for the three kinds `validate_spine.py` already covers
(`pytest-selector`, `artifact`, `git-change-policy`) is placed at exactly one call: `generate()`'s final
`validate_spine.validate(spine, repo_root=repo_root)`. It is never re-implemented, so it cannot drift
from the oracle. But the three new kinds have **no seam to inherit** — `python-call` and
`cli-invocation` and `population-filter` are acceptance boundaries this candidate is inventing whole,
with no prior art in the tree to anchor against and no existing test suite to catch a regression in
their logic except the one this mission must also write. That is a real seam-placement weakness, not a
depth strength in disguise, and §8 returns to it as the strongest argument against this candidate.

**Testability.** The whole point of the constraint, and it shows: `schema.py`, `probes.py`, and
`emit.py` are each independently unit-testable with no engine, no spine, no subprocess mocking beyond
what `validate_spine.py` itself already needs (a real `python -m pytest --collect-only` call). The cost
is speed and environment-coupling: every `pytest-selector` condition in a spec triggers one real
subprocess at generation time, so generating a spine with a dozen test-backed gates is not instant, and
CI generating specs in a sandbox without `pytest` importable hits the same "no interpreter with pytest
resolved" undecidable case `validate_spine.py` already documents — my `--allow-undecidable-pytest`
escape hatch (§3) exists because I judged "refuse to generate anything in that sandbox" worse than "generate
with the gap logged," but a candidate that never needed the escape hatch would be strictly simpler to
reason about.

## 7. The settling question

**Does your spec still ask its author to type a shell command from memory? No, for four of the six
kinds, and partially for a fifth.** `qualitative`, `pytest-selector`, `python-call`, and
`population-filter` never touch shell syntax at all — the worked example in §2 shows exactly what an
author types for `m1.c2`: `check = "pytest-selector"`, `selector = "TestGeneratorRefusesWhatOracleRefuses"`,
`min_collect = 1`, `targets = ["tests/test_generate_spine.py"]`. No `test $(...)`, no `&&`, no quoting —
the generator alone assembles that string and applies `shlex.quote()` to the selector, which makes
defect 1 (the unquoted `-k Door or Tie or Registry`) **structurally impossible**, not merely caught: there
is no field in this format an author could leave unquoted, because there is no shell-text field at all.

For `cli-invocation`, the defect **shrinks rather than vanishes**, and I want that stated as plainly as
the brief asks: the author still writes `args = ["--work-id", "<work-id>", "--gate", "m1"]` — literal
flag *names*, typed from memory, exactly like before. What changes is that a wrong flag name is now
caught **loudly, at generation time**, by an argparse dry-run against the real script — but only for the
7 of 46 scripts in this repo that expose a separable `build_parser()` (measured, §Required evidence). For
the other 39, the probe degrades to a `--help` substring check, which is real evidence but weaker: it
would not have caught defect 3 if `build_entry` had been invoked via an inline-`main()` script rather
than a directly-importable function. So the honest answer for this fifth kind is: the defect moved from
*silent-wrong, found downstream* to *loud-wrong, found now* for most of the corpus, and to *silent-wrong,
found downstream* still, for scripts without a `build_parser()` convention — which this candidate cannot
fix without also refactoring those 39 scripts, and refactoring is out of scope.

`git-change-policy` and `artifact` never asked for shell text in the first place (they are already
structured fields per `docs/CHECKLIST_SCHEMA.md`), so the question does not apply to them.

## 8. The strongest argument against my own candidate

**Three of my six probe kinds have no oracle behind them, which means their correctness rests entirely
on tests this mission itself must write, with no independent second check.** `validate_spine.py` is
665 lines shipped by a prior epic, already exercised against 113 archived spines and the shipped corpus,
with a documented incident history behind every fault it raises. My `python-call`, `cli-invocation`, and
`population-filter` probes have none of that: they are new code, judged only by the tests I write for
them in the same wave I write them. If `inspect.signature(...).bind(**kwargs)` accepts a call that the
real function then rejects at runtime for a reason `bind` cannot see (a `**kwargs`-catching function that
silently ignores an extra key, or a type mismatch `bind` never checks), or if the argparse dry-run
accepts flags that `main()`'s runtime logic then refuses for a semantic reason no parser sees, this
candidate would confidently emit a spine that fails downstream anyway — recreating, one level removed
and inside brand-new generator code, the exact "the check exits clean but does not test what it claims"
failure this whole mission exists to prevent. A design that leaned harder on kinds `validate_spine.py`
already polices, and pushed the population-filter and cli-invocation problems into a smaller, more
conservative surface (or deferred them to a later wave once the oracle itself grows fault classes for
them), would trade away some of this candidate's depth for a much shorter list of things a reviewer has
to trust on faith rather than on precedent.
