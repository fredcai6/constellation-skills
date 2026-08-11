# Candidate `a-smallest-diff` — generate the spine, in one file

**Work id:** `epic-559/c2-generate-the-spine` · **Constraint:** smallest-diff · **Author:** plan-alt-a-smallest-diff crew

## 1. The constraint, named, and how it was pushed

**smallest-diff: fewest new files, least new machinery, that can still emit implementer and reviewer
spines the lint accepts.** I pushed it by refusing every fork in the design that would have added a
second file, a second parser, or a third check kind:

- **One new file total**: `scripts/generate_spine.py`. No `specs/` package, no schema module, no
  separate CLI wrapper — `compile_spine()` is importable the same way `validate()` is, and the CLI at
  the bottom of the same file is the thin wrapper, mirroring `validate_spine.py`'s own shape exactly
  (so a reader who has already read the oracle recognizes the pattern immediately).
- **JSON, not a new syntax.** Every template in the corpus is already JSON; a spec in TOML or YAML
  would be one more parser and one more thing an author has to learn to read. A spec in JSON is
  something the author already half-knows from reading `IMPLEMENTER_PLAN.template.json` — the diff
  between "spec I write" and "spine the engine reads" is a matter of degree, not of kind.
  `tomllib` being stdlib was a live option (per `MISSION_FRAME.md`'s load-bearing assumption) but I
  didn't take it: it's a second syntax for zero mechanical gain over `json.loads`, which the generator
  already needs to read every shipped template it must not edit.
- **Two check kinds, not three, not six.** The engine implements three (`command`, `artifact`,
  `git-change-policy`). Neither role spec this mission requires (implementer, reviewer) uses
  `git-change-policy` anywhere in the shipped templates I read — that check kind exists for
  Commander-tier closeout gates, outside this mission's two required role specs. So the spec format
  drops it. That is a real, stated cost (§6, §8), not a quiet omission.
- **No raw shell field, ever** — `command`-kind checks take `argv: [str]`, a list of tokens, never a
  string. This is the direct, structural answer to defect 1 (the unquoted `-k` selector): there is no
  string for a shell to re-split, because the author never writes one.

Where I did *not* push the constraint: I still emit a `directives.handback` block on every gate and
an aggregated `directives.large_claims` block on the terminal gate (§4). Property 2 could not be
realized with zero new vocabulary at all — the settled decision `notes-live-in-directives-not-
constraints` (`MISSION_FRAME.md`) already requires a shaped write into `directives`, and inventing
literally nothing there would just fail the non-optional property. I minimized it to one directive
name with a fixed four-field contract, reused unchanged for both roles, rather than a per-role shape.

## Baseline — `python scripts/validate_spine.py --sweep --root .`, run by me

```
sweep: 12 gated-or-survey templates discovered under /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/admiral/templates/ADMIRAL_SPINE.template.json: OK
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/cartographer/templates/CARTOGRAPHER.template.json: 4 fault(s)
  [falsifiable-all-null] context: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] packets: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] index-overlays: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] map-compliance: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/charter/templates/CHARTER.template.json: 6 fault(s)
  [falsifiable-all-null] context: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] explore: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] interrogate: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] rigor: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] project-templates: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] closeout: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/commander/templates/COMMANDER_SPINE.template.json: 1 fault(s)
  [falsifiable-all-null] reconcile: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/commander/templates/EXECUTE_PLAN.template.json: 2 fault(s)
  [falsifiable-all-null] e0-context: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-unresolved-placeholder] g1-integrate.postconditions.c1: command still carries the literal placeholder '<exact test command>' -- nothing resolves it, so the check can never run, let alone fail
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/explorer/templates/CYCLE.template.json: OK
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/explorer/templates/EXPLORER_SPINE.template.json: 3 fault(s)
  [falsifiable-all-null] context: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] spec: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] route: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/implementer/templates/IMPLEMENTER_PLAN.template.json: 2 fault(s)
  [falsifiable-all-null] m0-context: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-unresolved-placeholder] m1.postconditions.c2: command still carries the literal placeholder '<exact test command>' -- nothing resolves it, so the check can never run, let alone fail
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/interrogator/templates/INTERROGATION.template.json: OK
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/reviewer/templates/REVIEW_SURVEY.template.json: OK
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/scout/templates/SCOUT.template.json: 3 fault(s)
  [falsifiable-all-null] context: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] audit: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] report: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/skills/workbench/templates/DEFAULT.template.json: 2 fault(s)
  [falsifiable-all-null] context: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
  [falsifiable-all-null] step1: every postcondition's check is null -- nothing here can ever refuse this gate; give at least one condition a real check, or if it is genuinely qualitative, that is still a choice a reviewer should see stated, not the gate's only property
```

This reproduces `PROBLEM_STATEMENT.md`'s stated baseline exactly, and it is the reason §3's compiler
refuses an all-null postcondition list at compile time rather than letting it reach the oracle only to
bounce: eight of twelve shipped templates already carry this exact fault, on this exact commit, and
REVIEW_SURVEY.template.json is one of the four that is clean — which is why the worked implementer
example in §2 gives `m0-context` an `artifact`/`user-decision` check instead of the `check: null`
the shipped `IMPLEMENTER_PLAN.template.json` uses for the identical gate (§4, §7).

## 2. The spec format

One JSON file per role spec. Top-level:

```json
{
  "work_id": "<work-id>",
  "type": "gated",
  "config_ref": "docs/agents/engine-config.json",
  "gates": [ /* ordered list of gate specs — the word "gates" covers both a gated plan's tasks
                and a survey's items, one vocabulary word instead of two */ ]
}
```

Each gate spec:

```json
{
  "id": "m1",
  "title": "…",
  "imperative": "…",
  "preconditions": [ {"id": "p1", "statement": "…", "check": null} ],
  "postconditions": [ {"id": "c1", "statement": "…", "check": <Check>} ],
  "constraints": ["…"],
  "beliefs": ["…"], "concerns": ["…"], "open_questions": ["…"],
  "large_claim": null
}
```

`<Check>` is one of exactly two spec-level kinds, or `{"kind": "qualitative"}` (sugar, §4):

- **`command`** — `{"kind": "command", "argv": ["python", "-m", "pytest", "-q", "-k", "Door or Tie or Registry"]}`.
  `argv` is a list; a `-k` value containing spaces is one list element, never split by a shell,
  because the author never writes a shell line at all. Optional `self_check: false` opts out of the
  automatic collect-only guard the generator applies by default whenever `argv` contains both
  `pytest` and `-k` (§3); optional `min_collect` (default `1`) sets the guard's threshold.
- **`artifact`** — `{"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}}`.
  `match` is required unless `evidence_type == "user-decision"` (the corpus's own accepted exception,
  which `validate_spine.py`'s `ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH` already names).

### Complete worked example — an implementer role spec

```json
{
  "work_id": "<work-id>",
  "type": "gated",
  "config_ref": "docs/agents/engine-config.json",
  "gates": [
    {
      "id": "m0-context",
      "title": "Load baseline context",
      "imperative": "Read your inherited global doctrine (references/global-crew.md, references/global-everyone.md), then project deltas (docs/agents/CREW_CONTEXT.md, docs/agents/GLOSSARY.md), the handoff, and the relevant packet. Verify the handoff is complete.",
      "preconditions": [],
      "postconditions": [
        {"id": "c1", "statement": "crew context + glossary + handoff loaded; handoff complete", "check": {"kind": "qualitative"}}
      ],
      "constraints": [],
      "beliefs": [], "concerns": [], "open_questions": [],
      "large_claim": null
    },
    {
      "id": "m1",
      "title": "Emit the generator and wire the oracle gate",
      "imperative": "Write scripts/generate_spine.py: compile_spine(spec) -> spine dict; refuse (no file written) if validate_spine.validate(spine, repo_root=root) carries any Fault.",
      "preconditions": [
        {"id": "p1", "statement": "context loaded and handoff complete", "check": null}
      ],
      "postconditions": [
        {"id": "c1", "statement": "new test proving an unquoted-style -k selector is impossible to author (argv is a list, never a raw string) is written and observed failing", "check": {"kind": "qualitative"}},
        {"id": "c2", "statement": "generate_spine.py compiles a known-good spec to a spine validate_spine.py accepts, and refuses a known-bad one with the matching Fault code; tests pass", "check": {"kind": "command", "argv": ["python", "-m", "pytest", "-q", "-k", "Door or Tie or Registry"]}}
      ],
      "constraints": ["<inherited handoff rules>"],
      "beliefs": ["a single argv-list check kind, plus one artifact kind, is enough to express both role specs without a raw shell field"],
      "concerns": ["dropping git-change-policy from the spec vocabulary means closeout gates still must be hand-authored"],
      "open_questions": ["should a handback-visibility check become its own mechanical postcondition on every generated reviewer survey, or stay advisory prose?"],
      "large_claim": "this generator is the sole seam through which any future implementer/reviewer spine is authored; if the two-kind vocabulary can't express a needed check, the mission's 'no shell string typed from memory' property silently regresses back to hand-authored JSON, and nothing catches that regression except this candidate's own #518-style vigilance"
    }
  ]
}
```

This is long enough to be judged: it carries a context gate, a work gate, both spec-level check kinds
in use (`qualitative` sugar and `command`), a populated `constraints` passthrough, and one `large_claim`
to show §4's aggregation.

## 3. The generator

**Module**: `scripts/generate_spine.py` — one file, importable (`compile_spine`, `compile_gate`) with
a thin `main()` CLI at the bottom, same shape as `validate_spine.py`.

**CLI**: `python scripts/generate_spine.py <spec.json> --out <spine.json> --root .`

**What it does, in order:**

1. Parse the spec JSON. Shape-check it lightly (`gates` is a list, every id unique, `type` is
   `gated`/`survey`) — cheap, local checks; the heavy lifting is step 4.
2. For every gate spec, build the engine-shaped task: copy `id`/`title`/`imperative` verbatim; compile
   each condition's `check`:
   - `command` → if `self_check` (default-on when `argv` contains `pytest` and `-k`): locate the `-k`
     value in `argv`, quote it with `shlex.quote`, and emit the corpus idiom text directly —
     `test $(<interpreter> -m pytest -q -k <quoted> --collect-only 2>/dev/null | grep -c '::') -ge <min_collect> && <argv, shlex-joined>`
     — reusing the *same* segment-detection shape `validate_spine.py::_pytest_segments` already
     defines, so the generator's idea of "this is a pytest -k check" can never drift from the oracle's.
     Otherwise: `shlex.join(argv)` (Python's own safe re-quoting — never the author's raw text).
   - `artifact` → passthrough `evidence_type`/`match`; refuses at spec-parse time (before even calling
     the oracle) if `match` is absent and `evidence_type != "user-decision"` — this one check *is*
     `validate_spine.py`'s own fault 3 rule, so failing fast here just saves a wasted oracle round-trip.
   - `{"kind": "qualitative"}` → `{"kind": "artifact", "evidence_type": "user-decision"}` (§4).
   - `null` → `null`, passthrough (preconditions only; a `gated` task's postconditions may never all be
     `null` — the oracle refuses that unconditionally, so the generator refuses a spec with an all-
     qualitative postcondition list at compile time, with the same message the oracle would give).
3. Compile `directives.handback` (populated on **every** gate, always — §4) and, on the **last** gate
   only, `directives.large_claims` (the aggregation of every `large_claim` set anywhere in the spec —
   §4).
4. Assemble the full spine dict and call `validate_spine.validate(spine, repo_root=root)` — the actual
   oracle, imported and called, never re-implemented. **This is the hard gate.** If
   `result` or `result.undecidable` is non-empty, refuse:
   ```
   refused: generated spine would not pass scripts/validate_spine.py
     [falsifiable-zero-collected] m1.postconditions.c2: the pytest selector -k 'NoSuchClass' in this check collects zero tests -- ...
   0 files written.
   ```
   exit 1, and **write nothing** — not even a partial file. On a clean result, write `--out` and print
   `wrote <path>: 0 faults, 0 undecidable`.

Nothing here re-implements a falsifiability rule the oracle already owns (the `artifact`-without-
`match` pre-check in step 2 is the one exception, and it exists only to fail fast with a friendlier
message before spending a subprocess on pytest collection — the oracle is still the final word, called
in step 4 regardless).

**Placeholders are the resolver's problem, not the generator's.** An author is free to write
`<work-id>` (or any other resolver-owned family) literally into `argv`/`evidence_type`/`match` — the
generator never touches it, exactly as a shipped template never resolves its own tokens. `step 4`'s
`validate()` call already carries `init_work_area._RESOLVER_OWNED_TOKEN_RE` internally
(`validate_spine.py` imports it, never re-declares it) and accepts those families while refusing
anything else (`<exact test command>`-shaped literals included) with `falsifiable-unresolved-
placeholder`. The generator adds no second copy of that regex anywhere — one more file it did not need
to write.

## 4. The two non-optional properties, concretely

### Property 1 — every gate carries a place to record beliefs, concerns, open questions

Every compiled gate carries a `directives.handback` block, **unconditionally**, even when the spec
author supplied nothing:

```json
"directives": {
  "handback": {
    "beliefs": [],
    "concerns": [],
    "open_questions": [],
    "how_to_record": "attach <gate-id> --type user-decision --field note=<text> for anything new; to promote a claim into THIS gate's own directives so a cold reviewer sees it without re-deriving it, amend --delta <file> (op rescope, id <gate-id>, field directives) --authority human --reason \"<why>\""
  }
}
```

The `how_to_record` field is the load-bearing part: it names the *exact* engine verbs (`attach`,
`amend --delta … rescope`) already documented in `docs/CHECKLIST_SCHEMA.md`'s Amend-delta section, so
a crew that needs to hand something back is never guessing at a mechanism — it is told, in the
substrate the mission specifies, on every single gate it drives.

### Property 2 — judgment carried up

Any gate spec that sets `large_claim` gets that text folded into the **terminal gate's**
`directives.large_claims`, keyed by source gate id — so a cold reviewer reading only the plan's final
state (which is what a reviewer does: read the archived checklist, not replay every gate) cannot miss
a large claim regardless of which gate made it.

### Emitted JSON for `m1` (the terminal — and here, only — gate of the worked example)

```json
"m1": {
  "id": "m1",
  "title": "Emit the generator and wire the oracle gate",
  "imperative": "Write scripts/generate_spine.py: compile_spine(spec) -> spine dict; refuse (no file written) if validate_spine.validate(spine, repo_root=root) carries any Fault.",
  "preconditions": [
    {"id": "p1", "statement": "context loaded and handoff complete", "check": null, "satisfied": false}
  ],
  "postconditions": [
    {"id": "c1", "statement": "new test proving an unquoted-style -k selector is impossible to author (argv is a list, never a raw string) is written and observed failing", "check": {"kind": "artifact", "evidence_type": "user-decision"}, "satisfied": false},
    {"id": "c2", "statement": "generate_spine.py compiles a known-good spec to a spine validate_spine.py accepts, and refuses a known-bad one with the matching Fault code; tests pass", "check": {"kind": "command", "command": "test $(python -m pytest -q -k 'Door or Tie or Registry' --collect-only 2>/dev/null | grep -c '::') -ge 1 && python -m pytest -q -k 'Door or Tie or Registry'"}, "satisfied": false}
  ],
  "constraints": ["<inherited handoff rules>"],
  "directives": {
    "handback": {
      "beliefs": ["a single argv-list check kind, plus one artifact kind, is enough to express both role specs without a raw shell field"],
      "concerns": ["dropping git-change-policy from the spec vocabulary means closeout gates still must be hand-authored"],
      "open_questions": ["should a handback-visibility check become its own mechanical postcondition on every generated reviewer survey, or stay advisory prose?"],
      "how_to_record": "attach m1 --type user-decision --field note=<text> for anything new; to promote a claim into THIS gate's own directives so a cold reviewer sees it without re-deriving it, amend --delta <file> (op rescope, id m1, field directives) --authority human --reason \"<why>\""
    },
    "large_claims": {
      "m1": {"claim": "this generator is the sole seam through which any future implementer/reviewer spine is authored; if the two-kind vocabulary can't express a needed check, the mission's 'no shell string typed from memory' property silently regresses back to hand-authored JSON, and nothing catches that regression except this candidate's own #518-style vigilance"}
    }
  },
  "child_checklist": null,
  "status": "pending", "status_detail": {}, "result": null, "finding": null, "evidence": [], "rework_count": 0
}
```

### What `current` would render, on `m1` active (per `checklist_engine.py::render_human`, `_condition_kind`, `_render_directive_lines`)

```
ACTIVE m1 [pending] — Write scripts/generate_spine.py: compile_spine(spec) -> spine dict; refuse (no file written) if validate_spine.validate(spine, repo_root=root) carries any Fault.
preconditions:
  p1 [unmet] null — context loaded and handoff complete
postconditions:
  c1 [unmet] artifact — new test proving an unquoted-style -k selector is impossible to author (argv is a list, never a raw string) is written and observed failing
  c2 [unmet] command — generate_spine.py compiles a known-good spec to a spine validate_spine.py accepts, and refuses a known-bad one with the matching Fault code; tests pass
0/3 met
constraints:
  <inherited handoff rules>
directives:
  handback:
    beliefs: a single argv-list check kind, plus one artifact kind, is enough to express both role specs without a raw shell field
    concerns: dropping git-change-policy from the spec vocabulary means closeout gates still must be hand-authored
    open_questions: should a handback-visibility check become its own mechanical postcondition on every generated reviewer survey, or stay advisory prose?
    how_to_record: attach m1 --type user-decision --field note=<text> for anything new; to promote a claim into THIS gate's own directives so a cold reviewer sees it without re-deriving it, amend --delta <file> (op rescope, id m1, field directives) --authority human --reason "<why>"
  large_claims:
    m1:
      claim: this generator is the sole seam through which any future implementer/reviewer spine is authored; if the two-kind vocabulary can't express a needed check, the mission's 'no shell string typed from memory' property silently regresses back to hand-authored JSON, and nothing catches that regression except this candidate's own #518-style vigilance
next: start
```

(`_condition_kind` renders a `null` check literally as the string `null`, per `checklist_engine.py:1882`
— shown as-is above, not smoothed over.)

## 5. The gate plan

Three gates to build this candidate. Verification stays green at every boundary: g1 is unit-tested in
isolation before anything drives against it; g2 is the one live proof the mission requires; g3 produces
no code, so it cannot regress g1/g2.

| id | title | delivers | close criteria | kind |
|---|---|---|---|---|
| **g1** | Write the generator | `scripts/generate_spine.py`, importable + CLI | A test feeds a spec shaped like the worked example in §2 through `compile_spine`, asserts the emitted `m1.postconditions.c2.check.command` is byte-identical to the corpus idiom shown in §4; a second test feeds a deliberately-bad spec (a `-k` selector guaranteed to collect zero, e.g. targeting a nonexistent class) and asserts the CLI exits 1, prints the `falsifiable-zero-collected` fault, and writes no output file; `python scripts/validate_spine.py --sweep --root .` fault count is unchanged from baseline (generator touches no shipped template) | crew gate |
| **g2** | Compile both role specs and drive one | an implementer spec + a reviewer spec (JSON, under this work's `.agent-work` tree), each compiled to a real spine by g1's generator | `run_crew.py` dispatches the compiled implementer spine and it reaches `spine_terminal` (the mission's own required proof — a spine-only dispatch is judged on this, not a result artifact); paste the dispatch outcome | crew gate |
| **g3** | Float the scope gap and the qualitative resolution | one document: the `git-change-policy` omission (§6, §8) and the "qualitative postconditions compile to `artifact`/`user-decision`, never `check: null`" resolution (§4), each stated as a decision for the Admiral to ratify or reject | the document exists and names both decisions in the vocabulary `MISSION_FRAME.md` uses for decision pressure | reasoning gate — crew-waiver: no code or diff to review, the deliverable *is* the document; a crew adds a second voice with nothing to verify against |

## 6. Self-scoring

**Depth.** Shallow, deliberately. Two check kinds cover the implementer and reviewer role specs
because neither shipped template used a third kind — but that is a fact about *this mission's* two
required roles, not a fact about the corpus. A Cartographer or Commander-closeout role spec that needs
`git-change-policy` cannot be authored in this format at all; the author would have to drop back to
hand-editing JSON for that one gate, which is exactly the failure mode this mission exists to remove.
Depth is the axis smallest-diff cost the most, on purpose.

**Locality.** The strongest axis for this candidate. One new file. Zero edits to
`checklist_engine.py`, zero edits to any shipped template, zero edits to `validate_spine.py`, zero new
directories. A reviewer can read `scripts/generate_spine.py` start to finish in the fifteen minutes
the handoff asks for, because there is nothing else to read alongside it except the oracle it already
knows.

**Seam placement.** Clean where it exists: spec-JSON → `compile_spine` → spine-JSON → `validate()` is
one seam, and the generator never touches `checklist_engine.py` — it produces exactly the shape the
engine already reads, same as every hand-authored spine before it. Weak where it doesn't: because the
vocabulary can't express `git-change-policy`, the generator is not a *universal* seam for spine
authorship — some gates in the corpus still bypass it entirely, which means the "checks are generated,
never hand-typed" property is a property of *some* gates, not of spines as a whole, until the
vocabulary grows a third kind.

**Testability.** `compile_spine` is a pure function over dicts — trivial to unit test with good/bad
spec fixtures, exactly as `validate_spine.py` itself is tested (feed it a dict, assert on the
`ValidationResult`). The weak spot is Property 2's second half: `directives.large_claims` being
populated and rendered is fully testable (assert the dict shape, assert `render_human` output); a
reviewer *actually reading and acting on it* is not something any check in this candidate can test —
it is a prose ask (§8), and I have no test for prose being heeded.

## 7. The settling question

> Does your spec still ask its author to type a shell command from memory?

**Partially — and the honest split matters.** For the failure mode the mission opens with (defect 1,
the unquoted `-k` selector), the answer is genuinely no: `argv` is a list, `-k`'s value is one list
element regardless of the spaces inside it, and the generator — never the author — decides how it gets
quoted and whether the collect-only guard gets wrapped around it. An author writing the worked example
in §2 types `["python", "-m", "pytest", "-q", "-k", "Door or Tie or Registry"]`; they never type the
string `test $(python -m pytest -q -k 'Door or Tie or Registry' --collect-only …) -ge 1 && …` at all —
that whole line is generator output, not author input.

But the *tokens themselves* are still typed from memory, and that is where the defect moves rather
than goes: `["python", "scripts/verify_fowler_pass.py", ".agent-work/<work-id>/FOWLER_PASS.json"]` is
exactly as authorable-wrong as the free-text version of the same command — a misspelled flag, a
`work_id=` where the script wants `--work-id`, a path that doesn't exist — because `argv` carries no
opinion about what a *correct* invocation of `verify_fowler_pass.py` looks like. Defect 3 in the
launch order (`build_entry(session=...)` where the parameter is `work_id=`) is a wrong-kwarg mistake
that an `argv` list does not structurally prevent; it only prevents the shell from *re-interpreting*
whatever tokens the author chose. So: the shell-tokenization class of defect (1) is closed
structurally; the wrong-invocation class of defect (3) is not, and this candidate does not claim
otherwise.

## 8. The strongest argument against this candidate

**The two-kind vocabulary buys locality by making "judgment carried up" softer than the mission asks
for, and it cannot author a whole class of gate the corpus actually uses.** `directives.large_claims`
guarantees a large claim is *visible* to a cold reviewer — it renders, unconditionally, on the
terminal gate — but nothing in this design makes a reviewer *act* on it; the reviewer's own generated
survey has no mechanical postcondition tied to `large_claims` at all, only the standing convention that
a human reads `current`. A fatter candidate could give the reviewer's own postcondition a `command`
check that fails closed until the survey's consolidation names every claim in `large_claims` by id —
mechanical enforcement instead of a rendered reminder. I did not build that, because it would need
either a third check kind (something that inspects a *sibling* spine's JSON, not just its own) or a
generator subcommand invoked from inside a check — both are exactly the kind of new machinery
smallest-diff exists to refuse. And separately: this candidate cannot emit a `git-change-policy` gate
at all, so any role spec that needs one (Commander closeout, today) is not writable in this format —
an author hits that wall on day one of trying to migrate an existing closeout gate, and the answer is
"drop back to hand-authoring JSON for that gate," which is a real, visible seam in the "spec format an
author can write without knowing the engine's JSON shape" claim this mission makes.
