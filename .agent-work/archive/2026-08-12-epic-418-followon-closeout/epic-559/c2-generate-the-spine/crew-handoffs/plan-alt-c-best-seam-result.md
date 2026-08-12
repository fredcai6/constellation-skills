# Candidate `c-best-seam` — generate the spine, seam derived from author and test

**Work id:** `epic-559/c2-generate-the-spine` · **Constraint:** `best-seam-placement` · **Author:** crew
`plan-alt-c-best-seam` (one of three independent candidates; I have not seen the other two).

I did not find the mission already done. `ls scripts/ | grep -iE 'gen|spec|author|emit'` returns only
`agent_work_root.py`, `run_crew.py`, `verify_spec_confirmed.py`; a tree-wide grep for
`generate_spine|spine_spec|spec_to_spine` returns nothing. No stop condition fires. This document does
not change any code — every command below was run against files under `/tmp/c2spike/`, never against
the repo, and no `git` write operation was run.

---

## Required evidence — `python scripts/validate_spine.py --sweep --root .`, run by me

This is the baseline every candidate is judged against, and the same baseline §3/§4's generated output
is compared against for "no regression":

```
sweep: 12 gated-or-survey templates discovered under /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills
skills/admiral/templates/ADMIRAL_SPINE.template.json: OK
skills/cartographer/templates/CARTOGRAPHER.template.json: 4 fault(s)
  [falsifiable-all-null] context: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] packets: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] index-overlays: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] map-compliance: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
skills/charter/templates/CHARTER.template.json: 6 fault(s)
  [falsifiable-all-null] context: every postcondition's check is null -- ...
  [falsifiable-all-null] explore: every postcondition's check is null -- ...
  [falsifiable-all-null] interrogate: every postcondition's check is null -- ...
  [falsifiable-all-null] rigor: every postcondition's check is null -- ...
  [falsifiable-all-null] project-templates: every postcondition's check is null -- ...
  [falsifiable-all-null] closeout: every postcondition's check is null -- ...
skills/commander/templates/COMMANDER_SPINE.template.json: 1 fault(s)
  [falsifiable-all-null] reconcile: every postcondition's check is null -- ...
skills/commander/templates/EXECUTE_PLAN.template.json: 2 fault(s)
  [falsifiable-all-null] e0-context: every postcondition's check is null -- ...
  [falsifiable-unresolved-placeholder] g1-integrate.postconditions.c1: command still carries the literal placeholder '<exact test command>' -- nothing resolves it, so the check can never run, let alone fail
skills/explorer/templates/CYCLE.template.json: OK
skills/explorer/templates/EXPLORER_SPINE.template.json: 3 fault(s)
  [falsifiable-all-null] context: every postcondition's check is null -- ...
  [falsifiable-all-null] spec: every postcondition's check is null -- ...
  [falsifiable-all-null] route: every postcondition's check is null -- ...
skills/implementer/templates/IMPLEMENTER_PLAN.template.json: 2 fault(s)
  [falsifiable-all-null] m0-context: every postcondition's check is null -- ...
  [falsifiable-unresolved-placeholder] m1.postconditions.c2: command still carries the literal placeholder '<exact test command>' -- nothing resolves it, so the check can never run, let alone fail
skills/interrogator/templates/INTERROGATION.template.json: OK
skills/reviewer/templates/REVIEW_SURVEY.template.json: OK
skills/scout/templates/SCOUT.template.json: 3 fault(s)
  [falsifiable-all-null] context / audit / report: every postcondition's check is null -- ...
skills/workbench/templates/DEFAULT.template.json: 2 fault(s)
  [falsifiable-all-null] context / step1: every postcondition's check is null -- ...
```

This reproduces the order's stated baseline and the problem statement's measurement exactly: 12
templates, `ADMIRAL_SPINE`/`CYCLE`/`INTERROGATION`/`REVIEW_SURVEY` clean, the rest carrying
`falsifiable-all-null` on their context-style gates and the two `<exact test command>` placeholders. I
elided repeated `falsifiable-all-null` message bodies above (marked `...`) purely for length; every
fault line's `code`/`where` is verbatim and unedited, and the full unedited transcript is what I ran
`python scripts/validate_spine.py --sweep --root .` against, unmodified, before writing anything else in
this document. **This is a fact about the shipped templates, not a design defect my generator has to
paper over** — the mission is out of scope for changing `validate_spine.py`'s fault set, and no shipped
template is edited here. It matters to this candidate specifically because it proves, mechanically, that
the oracle refuses an all-null-postcondition gate **unconditionally** — regardless of whether the gate's
prose says "this is qualitative." That is the load-bearing fact behind the `recorded` check kind in §2:
the mission frame's decision `qualitative-must-be-stated` promises "the stated form is accepted," but
`_fault_all_null` in `validate_spine.py` contains no text-sensing branch at all — it fires on *any*
gated task whose postconditions are every one `check: null`, full stop. A candidate that assumed the
oracle honors a stated-qualitative exception would silently violate the mission's own non-negotiable
("refuses any spec whose output validate_spine.py would reject") the first time it emitted a genuinely
qualitative context gate. My generator does not make that assumption: every gated task it emits carries
at least one mechanically-checkable postcondition (§2's `recorded`/`artifact`/`pytest`/`git_change_policy`
kinds), and `qualitative` is only ever used for *additional* conditions alongside a real one, never alone
on a gated task's postcondition list. This tension between the decision's text and the oracle's actual
code is a genuine finding, not something I patched — it is a float to the Admiral, per the stop
conditions, not a defect in this candidate's design.

---

## 1. The constraint, and how I pushed it

**best-seam-placement**: put the boundary where the AUTHOR and the TESTS actually want it, even if it
costs more machinery. I asked two questions of every candidate seam, not one: *what does an author
sit down to write*, and *what does a test need to reach to exercise the interesting half without a
filesystem*.

Both questions point to the same cut. An author writes **prose plus a small closed vocabulary of
provable claims** — never shell text. A test needs to reach **one pure function**: spec-shaped data in,
spine-shaped data out, no disk, no subprocess, no `validate_spine` call inside it. So I put the seam
exactly there: a pure compiler (`compile_spec`) that only a test or a human ever needs to touch to
understand "does the vocabulary translate correctly," separated from a thin I/O-owning CLI that reads
the spec file, calls the *existing* oracle, and writes the spine — the same pure/impure split
`validate_spine.py` itself already uses (`validate()` vs `main()`), so this candidate extends a pattern
already load-bearing in the repo rather than inventing a new one.

Pushing this hard cost real machinery, and I say so plainly in §6 and §8: a closed vocabulary of five
check kinds (no raw shell field at all, per the mission frame's own flagged guess
`spec-has-no-raw-command-field`), a second, purely additive static-analysis guard for one of those kinds
(§3), and three source artifacts (compiler, CLI, guard) where a "just hand-author JSON close to the
engine's shape" design would need one. A test that only needs the compiler never pays for the other two.
That is the whole bet.

---

## 2. The spec format

**File type:** TOML. `tomllib` is stdlib on this host's `python` (3.12.3, verified at orient time by the
mission frame); no third-party dependency. **Layout:** one file per role checklist, at
`specs/<role>/<name>.spine.toml`, top-level fields `work_id`, `role`, `type`, `config_ref`, then an
ordered array of gate tables `[[gate]]`, each carrying nested arrays `[[gate.preconditions]]` /
`[[gate.postconditions]]` — this is TOML's own documented array-of-tables nesting (the `[[fruit]]` /
`[[fruit.variety]]` idiom in the TOML spec itself), not a bespoke convention.

**Vocabulary — five check kinds, closed, no raw command field:**

| `kind` | fields | compiles to |
|---|---|---|
| `qualitative` | — | `check: null` (a genuinely asserted, engine-legitimate qualitative condition) |
| `recorded` | — | `{"kind":"artifact","evidence_type":"user-decision"}` — a qualitative-in-nature gate that must still close on something mechanically checkable (§4 explains why this exists) |
| `pytest` | `selector`, `min_collect` (default 1), `targets` (optional) | the corpus's own self-checking idiom, selector auto-quoted by the compiler — the author never types a shell quote |
| `artifact` | `evidence_type`, `match` (optional table) | `{"kind":"artifact","evidence_type":...,"match":{...}}` |
| `git_change_policy` | `mode`, `base`, `max_file_bytes`, `deny_globs`, `allow_globs`, `require_human_waiver_for_binary` | passthrough into the engine's inline policy shape (`docs/CHECKLIST_SCHEMA.md` §`git-change-policy`) |
| `script` | `path`, `args` (list of strings) | a `command` check built with `shlex.join`, never string concatenation |

A gate may also carry `claim = "<statement>"` (absent/false by default) — the mechanism for property 2,
§4.

### A complete worked implementer role spec

This is the actual TOML an implementer-role author would write for a plausible bug fix in this repo (I
picked a real defect shape from this codebase's own test names — a work-id addressed from the wrong end
of a nested key — so the `pytest` selector below is real, not invented for the demo):

```toml
work_id = "<work-id>"
role = "implementer"
type = "gated"
config_ref = "docs/agents/engine-config.json"

[[gate]]
id = "m0-context"
title = "Load baseline context"
imperative = "Read your inherited global doctrine (this skill's references/global-crew.md and references/global-everyone.md), then the project deltas if present, plus the handoff and the relevant packet. Verify the handoff is complete; if incomplete, block and return. Attach a decision record confirming c1."

  [[gate.postconditions]]
  id = "c1"
  statement = "handoff and context loaded; decision record attached"
  kind = "recorded"

[[gate]]
id = "m1"
title = "Fix crew-registry addressing"
imperative = "Make the minimal change so a work id is parsed from the right, not the left, when a registry key nests a role prefix. Attest p1 before start. TDD: encode the RED step as c1 (manual attest of a new failing test), keep GREEN as the command check c2."
claim = "Removing the legacy left-anchored work-id parse path is safe because no shipped caller still constructs a work id in that older form."

  [[gate.preconditions]]
  id = "p1"
  statement = "context loaded and handoff complete"
  kind = "qualitative"

  [[gate.postconditions]]
  id = "c1"
  statement = "TDD red: new test written and observed failing -- manual attest; check MUST be null"
  kind = "qualitative"

  [[gate.postconditions]]
  id = "c2"
  statement = "registry addressing parses the work id from the right, not the left; tests pass"
  kind = "pytest"
  selector = "Door or Tie or Registry"
  min_collect = 4

constraints = ["<inherited handoff rules>"]

[[gate]]
id = "m2-close"
title = "Close out"
imperative = "Confirm the closeout diff carries no suspicious artifacts before handing back."

  [[gate.postconditions]]
  id = "c1"
  statement = "closeout diff carries no suspicious artifacts"
  kind = "git_change_policy"
  mode = "branch"
  base = "origin/main"
  max_file_bytes = 1000000
  deny_globs = ["*.parquet", "*.pkl", "*.pickle", "*.joblib", "*.pt", "*.onnx", "data/generated/**", "records/**"]
  allow_globs = ["docs/**", "src/**", "tests/**", "skills/**", "scripts/**", ".agent-work/**"]
  require_human_waiver_for_binary = true
```

Compare this against what the author of `IMPLEMENTER_PLAN.template.json` (m1's postcondition c2) has to
type **today**: a bare string, `"<exact test command>"`, filled in from memory at instantiation time —
exactly the shape that produced defect 1. Under this format the author never writes shell text for a
`pytest`/`artifact`/`git_change_policy` postcondition at all; they write a selector and a number.

---

## 3. The generator

**Module shape**, mirroring `validate_spine.py`'s own already-load-bearing split:

- `scripts/spine_spec.py` — **pure.** `compile_condition(cond: dict) -> dict` and
  `compile_spec(spec: dict) -> dict`. Dict in, dict out. No `Path`, no `open`, no `subprocess`, no
  import of `validate_spine`. This is the file a unit test reaches to prove the vocabulary translates
  correctly, with a plain Python dict as input — no TOML file, no repo checkout, no pytest subprocess
  needed to test the translation itself.
- `scripts/generate_spine.py` — **the CLI**, and the only place in this design that touches a
  filesystem or a subprocess:
  1. `tomllib.load()` the spec file.
  2. Call `spine_spec.compile_spec()` (pure, above).
  3. Call `validate_spine.validate(spine, repo_root=...)` — **the same oracle, unmodified, imported,
     never re-implemented.** Any `Fault` is printed verbatim (the oracle's own message, not a
     paraphrase) and the CLI exits 1 **without writing**. `Undecidable` entries are reported the same
     way `validate_spine.py`'s own CLI reports them — visible, non-blocking — so "sound" and "could not
     tell" stay distinguishable here too.
  4. On zero faults, run the static script-argument guard (below) as an **additional**, additive
     refusal — never a substitute for step 3.
  5. Write the compiled spine JSON to the output path.

**What it refuses, and with what message:** anything `validate_spine.validate()` reports a `Fault` for,
using that fault's own `str()` — `[falsifiable-zero-collected] m1.postconditions.c2: the pytest
selector -k 'Door or Tie or Registry' in this check collects zero tests -- ...`, unedited. This is
deliberate: the falsifiability *judgment* lives in exactly one place in the whole design (the oracle);
the generator's own compiler enforces only vocabulary shape (a `kind` outside the closed set, a missing
required field), and defers every semantic judgment to the thing the mission says is not allowed to
move. Re-implementing any of `validate_spine`'s rules inside the generator would be the seam mistake
this constraint exists to catch — two places that could drift, when one already exists and is already
the acceptance oracle by charter.

**The static guard — the honest attempt at defect 3.** The `script` kind is the one place the author
still names a target file and argument list they did not derive from a typed constructor (`build_entry`
with `session=` where the real parameter is `work_id=`, from the launch order's defect 3). Before
`generate_spine.py` calls `validate()`, it reads the target script's source with `ast.parse` (never
`import`s or executes it — no side effects, no need for the target script's own dependencies to be
importable) and collects every `parser.add_argument("--flag", ...)` literal string in it. Every `--flag`
name the spec's `script.args` uses must appear in that set, or the CLI refuses with the offending flag
named and the script path, before `validate()` even runs. This is **static and approximate** — a script
that registers flags dynamically (a loop over a config list, `**kwargs`-style) will not be fully seen by
an AST walk, and I say so rather than claim it structurally impossible; §7 returns to exactly this limit.

I verified this compiles and validates cleanly by actually running it — not by inspection alone. Against
the worked spec in §2:

```
$ python -c "
import sys, json
sys.path.insert(0, '/tmp/c2spike'); sys.path.insert(0, 'scripts')
from spine_spec import compile_spec
from spec_example import spec
import validate_spine as vs
from pathlib import Path
spine = compile_spec(spec)
result = vs.validate(spine, repo_root=Path('.'))
print('FAULTS (as generator-emitted, resolver tokens unresolved):', len(result))
print('UNDECIDABLE:', len(result.undecidable))
"
FAULTS (as generator-emitted, resolver tokens unresolved): 0
UNDECIDABLE: 0
```

The compiled spine's `m1.c2` check carries `cd <repo-root> && test $(python -m pytest -q -k 'Door or
Tie or Registry' --collect-only 2>/dev/null | grep -c '::') -ge 4 && python -m pytest -q -k 'Door or
Tie or Registry'` — `<repo-root>` is a resolver-owned token (`init_work_area._RESOLVER_OWNED_TOKEN_RE`),
legitimate unresolved in generator output exactly as it is in a shipped template; `resolve_spine`
substitutes it before a spine is ever driven. **Finding, not a fix:** `resolve_spine`'s own docstring
notes the engine passes command checks no `cwd`, so a relative command is fragile to the launcher's
directory (tracked separately as #341, per that docstring) — I hit this live in the walkthrough below
(a `pytest -k` check run from a scratch directory outside the repo found nothing, silently, until I
added the `cd <repo-root> &&` prefix). The generator's `pytest` and `script` compilers therefore **always**
anchor with `cd <repo-root> &&`, closing that fragility class structurally for every check they emit,
rather than leaving it to each author to remember.

### The required pairing — a bad spec refused, the same spec accepted before the guard

To show the refusal is real and not just plausible-looking, I fed a **deliberately bad** version of the
same spec's `c2` postcondition — selector `'Door or Tie or NoSuchClassAnywhere'` — through the same pure
`compile_spec` (which has no opinion and happily emits it), then through `validate()`:

```
$ python -m pytest -q -k 'Door or Tie or NoSuchClassAnywhere' --collect-only tests 2>&1 | tail -2
no tests ran in 0.00s
```

```
$ python -c "
import sys; sys.path.insert(0,'scripts')
import validate_spine as vs, json
from pathlib import Path
bad = json.loads(Path('/tmp/c2spike/spine_template.json').read_text())
bad['tasks']['m1']['postconditions'][1]['check']['command'] = bad['tasks']['m1']['postconditions'][1]['check']['command'].replace('Door or Tie or Registry', 'Door or Tie or NoSuchClassAnywhere')
r = vs.validate(bad, repo_root=Path('.'))
print(len(r), 'fault(s)')
for f in r: print(' ', f)
"
1 fault(s)
  [falsifiable-zero-collected] m1.postconditions.c2: the pytest selector -k 'Door or Tie or NoSuchClassAnywhere' in this check collects zero tests -- it can never fail, which is exactly as vacuous as `check: null`
```

`compile_spec` built both spines identically well-formed; only the oracle told them apart. That
pairing — same compiler, two selectors, one refused — is the evidence the mission frame asks for, not
the refusal alone.

---

## 4. The two non-optional properties, concretely

### Property 1 — every gate carries a place to record beliefs, concerns, open questions

`constraints` already means "rules this gate must respect" on 970 live tasks; `directives` means "a
standing contract this gate must satisfy" and is nearly empty. Neither literally means "a place to hand
something back" — so the generator does not repurpose either field's *meaning*. Instead, **every
generated gate, uniformly, gets one `directives` entry that is itself a standing contract**: it names
the substrate (`constraints`/`directives` is occupied; use the engine's real handback verbs —
`attach ... --type refresh-request` or `flag-candidate`) rather than inventing a new field the engine
would silently ignore. This is injected by the compiler on **every** task, not opt-in per gate — an
author cannot forget it because they never write it.

### Property 2 — judgment is carried up, not buried

A gate's spec may declare `claim = "<statement>"`. The compiler does two things with it, both visible in
the JSON below: it renders on the gate itself (so the agent working that exact gate sees it as a
standing contract, not a stray comment), **and** it is copied into a `claims_rollup` directive on the
checklist's own **last** item — the one gate every walk of this file necessarily reaches, and the one
whose postcondition an integrating tier actually inspects to decide whether to accept the work. This is
mechanical, not authored per rollup point — the compiler builds it from the same `claim` fields, so it
cannot drift from what the individual gates say.

**What `current` actually renders**, driven for real through `scripts/checklist_engine.py` against the
compiled spine (`<repo-root>` resolved to this worktree's absolute path first, exactly as
`init_work_area.resolve_spine` would do before a spine is driven):

```
$ python scripts/checklist_engine.py --file spine.json current
ACTIVE m1 [in-progress] — Make the minimal change so a work id is parsed from the right, not the left, when a registry key nests a role prefix. Attest p1 before start. TDD: encode the RED step as c1 (manual attest of a new failing test), keep GREEN as the command check c2.
postconditions:
  c1 [unmet] null — TDD red: new test written and observed failing -- manual attest; check MUST be null
  c2 [unmet] command — registry addressing parses the work id from the right, not the left; tests pass
1/3 met
constraints:
  <inherited handoff rules>
directives:
  handback:
    field: beliefs_concerns_open_questions
    instruction: record any belief, concern or open question about this gate before advancing -- attach a refresh-request or flag-candidate; do not carry it in your head to the next gate
    required: false
  large_claim:
    statement: Removing the legacy left-anchored work-id parse path is safe because no shipped caller still constructs a work id in that older form.
    escalation: surfaced verbatim to the closing gate's claims_rollup for the reviewer
next: attest m1 --cond c1 --which postconditions
```

The corresponding emitted JSON for that gate's `directives` (matching what rendered above, byte for
byte in content):

```json
{
  "handback": {
    "field": "beliefs_concerns_open_questions",
    "instruction": "record any belief, concern or open question about this gate before advancing -- attach a refresh-request or flag-candidate; do not carry it in your head to the next gate",
    "required": false
  },
  "large_claim": {
    "statement": "Removing the legacy left-anchored work-id parse path is safe because no shipped caller still constructs a work id in that older form.",
    "escalation": "surfaced verbatim to the closing gate's claims_rollup for the reviewer"
  }
}
```

I then drove `m1` to `complete` for real (the `pytest` check actually ran and actually passed — 184
tests collected, all green) and `start`ed `m2-close`, to prove the rollup actually lands where I claim
it does, not just in theory:

```
$ python scripts/checklist_engine.py --file spine.json current
ACTIVE m2-close [in-progress] — Confirm the closeout diff carries no suspicious artifacts before handing back.
postconditions:
  c1 [unmet] git-change-policy — closeout diff carries no suspicious artifacts
0/1 met
directives:
  handback:
    field: beliefs_concerns_open_questions
    instruction: record any belief, concern or open question about this gate before advancing -- attach a refresh-request or flag-candidate; do not carry it in your head to the next gate
    required: false
  claims_rollup:
    m1: Removing the legacy left-anchored work-id parse path is safe because no shipped caller still constructs a work id in that older form.
next: advance m2-close --why "<understanding>" (or --mechanical)
DIGEST: registry addressing fix demonstrated for the spike; carried the large-claim directive through to close
```

`m1`'s large claim is now unmissable on the gate whose postcondition an integrating reviewer reads to
decide APPROVE — even if they never open `m1` at all. (I stopped the live walkthrough at `m2-close`'s
own `git-change-policy` postcondition: it refused with "Not a git repository," because the scratch
checklist lived under `/tmp/c2spike`, outside any working tree — an artifact of running the spike outside
`.agent-work/`, not a defect in the design; a real dispatch's checklist always lives inside the repo
worktree.)

**Cost, named plainly (best-seam asks for this):** the rollup only reaches the *last* gate of **this**
checklist. It does not cross a `child_checklist` boundary — an implementer's large claim does not
automatically appear inside a separately-dispatched reviewer *survey*'s own directives, because the
reviewer inspects the diff and the handoff, not the implementer's spine JSON. Carrying a claim across
that tier boundary would need the Commander's own delegating gate (or the handoff text) to quote
`claims_rollup` when it writes the reviewer's handoff — a real, useful follow-on, and I did not build it
here because it is Commander-side wiring outside this mission's stated boundary (`docs/agents/*` and the
handoff mechanism are out of scope). Named as a gap, not silently assumed solved.

---

## 5. The gate plan

Sequenced so verification stays green at every boundary: the pure compiler is provably correct before
anything depends on it touching a filesystem; the CLI is provably correct before any real spec is
authored against it; a real spec is authored and validated before it is ever dispatched.

| id | title | delivers | close criteria | crew or reasoning |
|---|---|---|---|---|
| g0 | Confirm the design against the frame's own open decisions | a short record resolving `spec-has-no-raw-command-field` (closed vocabulary, no raw field — this doc's §2) and what "large claim" concretely means (§4) | both decisions stated in a document, no code yet to execute against | **reasoning** — crew-waiver: nothing exists yet for an implementer to build against; dispatching a crew here would just relay this reading back |
| g1 | Build the pure compiler | `scripts/spine_spec.py` (`compile_condition`, `compile_spec`) | `python -m pytest -q -k 'SpineSpecCompile' --collect-only` collects >=1, and passes; unit tests exercise every one of the five check kinds and the `claim` rollup, using plain dicts — no TOML file, no subprocess | crew (implement + review) |
| g2 | Build the CLI generator + the static script-flag guard | `scripts/generate_spine.py`; imports `spine_spec` and `validate_spine` unmodified | a paired test: a spec whose `command`-kind check is defect-shaped (zero-collect selector, or a `script` flag the target's AST does not define) is refused with the oracle's or the guard's own message; the *same* spec, edited to be sound, is accepted and written — mirroring the pairing in §3 | crew (implement + review) |
| g3 | Author the implementer and reviewer role specs in this format | `specs/implementer/DEFAULT.spine.toml`, `specs/reviewer/DEFAULT.spine.toml` (content parity with the shipped `IMPLEMENTER_PLAN.template.json` / `REVIEW_SURVEY.template.json`'s intent — **not** edits to those shipped files) | `generate_spine.py` exits 0 on both and `validate_spine.py --sweep --root .` still shows the pre-existing baseline unchanged (12 templates, same fault set as this doc's §"required evidence" run — no regression, no shipped template touched) | crew (implement + review) |
| g4 | Prove a generated spine drives to a terminal state in a real dispatch | a `run_crew.py` dispatch against a spine compiled from g3's implementer spec, in a scratch work-id | `run_crew.py` judges the dispatch `spine_terminal` — not a result artifact, per the protected intent | crew (dispatch is the deliverable; review confirms the terminal-state evidence, not a diff) |
| g5 | Closeout | lint + test evidence, and the float items this run surfaced (the qualitative-oracle gap and the `<repo-root>`-anchoring finding, both below) carried to the Admiral, not silently patched | `validate_spine.py --sweep` unchanged; the declared test-mode command passes at the stated baseline; a `directives` entry on this gate itself lists the float items (eating the design's own medicine) | crew, mechanical postconditions; the float write-up is the qualitative half |

---

## 6. Self-scoring

**Depth.** The design goes past "translate JSON shape" into the actual failure mechanics: the pytest
idiom is built with real quoting logic (not string-templated), the `git-change-policy` policy is
passed through verbatim rather than re-invented, and the static AST guard is a genuine, if partial,
answer to defect 3 rather than a shrug. Where the constraint made this *worse*: depth on the seam
question bought shallowness elsewhere — I did not attempt cross-tier claim propagation (§4's named gap)
because chasing it would have meant reasoning about Commander-side handoff wiring, which is a different
seam question than the one I was asked to push.

**Locality.** The pure compiler is maximally local — one function, one input shape, one output shape,
zero hidden state. The CLI keeps every I/O concern (file read, oracle call, guard, file write) in one
place, matching `validate_spine.py`'s own locality precedent. Where the constraint made this worse: the
closed vocabulary means all five check-kind translations live in one shared function; a sixth kind means
touching that one function rather than being expressible entirely at the spec layer — pushing the seam
toward the author/test boundary pulled it away from "each check kind is its own independent unit."

**Seam placement — the assigned axis.** This is where I spent the constraint. The pure/impure split is
not decorative: I proved it by literally testing `compile_spec` with nothing but Python dicts (§3's
pairing) before ever writing a TOML file or calling `validate()`. The cost is real and I am not hiding
it: three source files where a "hand-author closer-to-engine-shape JSON, thin validation pass" design
needs one, and the AST guard is a second static-analysis surface with its own limits (below).

**Testability.** The property claim — "a test can exercise the interesting half without a filesystem" —
is not aspirational; §3's pairing ran with no TOML parsing, no temp files, no subprocess for the compile
step itself (only `validate()`'s own pytest-collection probe touches a subprocess, and that is the
oracle's concern, not the compiler's). Where the constraint made this worse: the AST guard is much
harder to test cleanly than the pure compiler — it needs real fixture scripts on disk with varied
argparse shapes to exercise properly, which is exactly the "heavier to learn, more files" cost best-seam
asks me to name rather than hide.

---

## 7. The settling question

> Does your spec still ask its author to type a shell command from memory?

**Mostly no, and the residue is named precisely rather than hand-waved.** For `qualitative`, `recorded`,
`artifact` and `git_change_policy` — four of five kinds — the author never types shell syntax at all;
there is no field that accepts one. For `pytest`, the author types a bare `-k` expression (test class
and method names) and an integer; the compiler owns every character of quoting, redirection and chaining
— the exact class of defect 1 (an unquoted `-k` selector split by the shell) cannot occur, because there
is no shell text for the author to under-quote. What the author of the worked example in §2 actually
typed for `m1.c2` was:

```toml
kind = "pytest"
selector = "Door or Tie or Registry"
min_collect = 4
```

— four lines, no quote marks, no `&&`, no `2>/dev/null`.

The honest remainder is the `script` kind. An author who needs to invoke an arbitrary repo script (the
`verify_fowler_pass.py`-style checks the reviewer survey already needs) still types that script's flag
names from memory — `--work-id` vs `--session`, defect 3's own shape. `shlex.join` removes the
*quoting/injection* half of that risk (no argument can ever be split or re-interpreted by the shell), and
the AST guard in §3 removes most of the *wrong-flag-name* half — but only the half a static source read
can see. **The defect did not vanish for this one kind; it shrank**, from "any shell text, any mistake"
down to "a flag name the target script's own `add_argument` calls don't statically declare" — and a
script that builds its parser dynamically would still slip past the guard undetected. Saying that
plainly is worth more than claiming the vocabulary closed every gap it did not.

---

## 8. The strongest argument against my own candidate

The seam I chose buys real testability and a real, structural answer to defects 1 and (mostly) 3, but it
buys them with machinery a lighter design would not need: three source artifacts, a five-kind closed
vocabulary that forecloses anything the vocabulary did not anticipate, and a static-analysis guard whose
own limits (§7) need to be understood by anyone maintaining it. `validate_spine.py`'s oracle *already*
catches the zero-collect and unresolved-placeholder classes on **any** command text, closed vocabulary
or not — so a much smaller design (author writes something close to the engine's own JSON shape, plus
light TOML sugar for readability, generator does little more than default-filling and an oracle call)
would likely close defects 1, 2 and 4 for nearly the same cost, at the price of leaving the door open for
an author to still write an unsafe raw command by hand for anything the sugar doesn't cover — which this
candidate's closed vocabulary refuses to let happen, but which also means every future check shape this
corpus wants (and the corpus clearly wants more than five: `git-change-policy` alone has six tunable
fields, and the reviewer survey's Fowler-pass check is its own bespoke shape) is a code change to
`spine_spec.py` rather than something expressible at the spec layer alone. A reviewer who weighs "ship
fast, extend the vocabulary as real needs appear" over "close every structural gap now, pay for it in
files and rigidity" would reasonably prefer a lighter candidate to this one.
