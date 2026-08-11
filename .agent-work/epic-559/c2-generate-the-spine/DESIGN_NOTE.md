# DESIGN NOTE — the spine spec format and its generator

**Frozen at gate `g0-design` of `epic-559/c2-generate-the-spine`.** This is the contract the `g1`
implementer builds to. Where this note and a crew's judgment disagree, this note wins; where this note
is silent, the crew decides and says so in its result.

Authored by the Commander as a **reasoning gate, no crew** — this is a naming-and-authority decision
that is mine to make, and there is nothing here for a reviewer to run. Its close criterion `c1` asserts
**arrival only**, and I am saying so rather than dressing it up: the kind list below is machine-pinned
one gate later, at `g1-integrate.c3`, by a test asserting it equals the compiler's own constant.

Everything below survived a three-lens cold critic panel; `plan-critic.md` records all 13 findings and
my disposition of each.

## 1. Why this exists

A check is a shell string typed from memory, and a wrong one does not announce itself — it exits 0 and
the gate opens on nothing. Four of roughly seventeen hand-authored spines and surveys last wave carried
checks that could not do their job, and **none was caught by its author**. The spec format removes the
place where that mistake is made: **there is no raw-command field anywhere in it.**

## 2. Format: TOML, and why

`specs/<role>.spine.toml`. `tomllib` is stdlib on this host's `python` (3.12.3, verified).

The simplicity critic challenged this — correctly noting the repo contains no TOML at all, that every
other artifact is JSON, and that switching costs one line. **Kept, with the measurement the critic
asked for:** across the 61 imperatives in the 12 shipped templates, **14 exceed 1000 characters and the
longest is 3534**; the `plan` imperative of the spine I am driving is 3555. In JSON every one of those
must be authored as a single-line string with each quote and newline hand-escaped — which relocates the
typed-from-memory-and-wrong hazard from the check onto the imperative rather than removing it. TOML's
triple-quoted multi-line string needs no escaping. That is the deciding factor and it is now argued
rather than asserted.

## 3. Spec shape

```toml
work_id = "<work-id>"
type    = "gated"                                  # or "survey"
config_ref = "docs/agents/engine-config.json"
parent  = "admiral-epic-418-followon"              # optional; defaults to the string "unknown"

[[gate]]
id    = "m1"
title = "..."
imperative = """
multi-line prose, no escaping
"""
constraints = ["..."]                              # optional; list[str], the field's existing meaning

  [gate.claim]                                     # optional
  magnitude = "large"                              # "normal" (default) | "large"
  text      = "..."

  [[gate.preconditions]]                           # zero or more
  id = "p1"
  statement = "..."
  kind = "qualitative"
  because = "..."

  [[gate.postconditions]]                          # gated: >= 1 required
  id = "c1"
  statement = "..."
  kind = "pytest"
  selector = "Door or Tie or Registry"
  min_collect = 4
  targets = ["tests/test_registry.py"]             # optional
```

`items` order is the `[[gate]]` order. Nothing else in the emitted spine is author-controlled: the
compiler supplies `preconditions: []`, `satisfied: false`, `status: "pending"`, `status_detail: {}`,
`result: null`, `finding: null`, `evidence: []`, `rework_count: 0`, `child_checklist: null`, and the
top-level `consolidation: null`, `triage_candidates: []`, `blockers: []`.

## 4. The closed vocabulary — five kinds

```python
CHECK_KINDS = ("qualitative", "pytest", "script", "population", "artifact")
```

**That tuple is the single source of truth** and is what `g1-integrate.c3`'s test pins this document
against. Any other `kind` value is a spec-shape fault, refused before any probe runs, naming the closed
set. **There is no raw-command field and no escape kind.** Extending what can be proven is a code
change with a test, not a string typed into a spec.

Every emitted `command` check is anchored `cd <repo-root> && …`. The engine passes `command` checks no
`cwd`, so a relative check silently inherits the launcher's directory (fragility tracked as #341 in
`init_work_area.resolve_spine`'s own docstring; a candidate hit it live — a `pytest -k` check run from
outside the repo found nothing, silently). `<repo-root>` is resolver-owned — verified,
`_RESOLVER_OWNED_TOKEN_RE.fullmatch("<repo-root>")` is true — so it is legitimate in output and is not
the placeholder class the generator refuses.

### `qualitative`

Fields: `because` (required, non-empty). Compiles to `"check": null`, **and appends the stated form to
the emitted statement**:

```
<author statement> -- QUALITATIVE: <because>
```

That append is how `decision:qualitative-must-be-stated` becomes mechanical rather than advisory: a
gate with no checkable postcondition cannot be emitted without saying, in the spine itself, that it is
qualitative and why. Silence is refused (missing or empty `because` is a spec-shape fault).

**A `gated` gate whose postconditions are ALL `qualitative` is refused at compile time**, with
`validate_spine`'s own `falsifiable-all-null` wording quoted, because the oracle would refuse it
anyway and failing at the spec is a better error than failing at the spine.

### `pytest`

Fields: `selector` (required), `min_collect` (int ≥ 1, default 1), `targets` (list[str], optional).

Compiles to the corpus's documented self-checking idiom, with the selector quoted by `shlex.quote` and
targets joined by `shlex.join`:

```
cd <repo-root> && test $(python -m pytest -q -k SEL --collect-only TARGETS 2>/dev/null | grep -c '::') -ge N && python -m pytest -q -k SEL TARGETS
```

The author writes a selector and a number and never sees a shell quote. **Defect 1 is structurally
impossible here** — there is no shell-text field to leave unquoted.

**Probe:** run `python -m pytest --collect-only -q -k <selector> <targets>` and refuse below
`min_collect`, reporting the actual count.

### `script`

Fields: `path` (repo-relative, required), `args` (list of literal tokens, optional).

Compiles to `cd <repo-root> && python <shlex.join([path, *args])>`.

**Probe — static, never executed.** `ast.parse` the target file and collect every string literal passed
as the first positional argument to a call named `add_argument`. Every token in `args` beginning with
`--` must be in that set.

- Target path does not exist → fault.
- A `--flag` in `args` that the AST did not find → fault, naming the flag and the script.
- `args` contains `--flags` but the AST found **no** `add_argument` literals at all → **refused as
  undecidable**, not accepted. The probe could not tell, and "could not tell" never passes here.
- `args` contains no `--flags` → nothing to check, accepted.

The target is **never imported**. Importing it would run its import-time code inside the generator,
which is defect 2's own shape one layer up.

### `population`

Fields: `root` (repo-relative dir), `glob`, and exactly one of `expected` (int) or the pair
`expected_min` / `expected_max`.

Compiles to a `command` check that counts with `pathlib.Path(root).glob(pattern)`:

```
cd <repo-root> && test $(python -c 'import pathlib,sys;print(sum(1 for _ in pathlib.Path(sys.argv[1]).glob(sys.argv[2])))' ROOT GLOB) -eq N
```

(band form: capture the count once into a shell variable and compare `-ge MIN` and `-le MAX`.)

**Probe: execute the compiled command string itself** and judge on its exit status. This is the whole
point — the testability critic showed that a Python-side glob and a shell-side count are two
implementations of one filter that do not agree by default on dotfiles, `**` recursion or symlinks,
which is *literally defect 4's shape* reintroduced inside the kind built to close it. There is one
implementation, and the thing probed is the thing shipped.

### `artifact`

Fields: `evidence_type` (required), `match` (table, optional).

Passthrough to `{"kind": "artifact", "evidence_type": …, "match": …}`. A missing `match` is a fault
**unless** `evidence_type` is in `validate_spine.ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH` — **imported,
never re-declared**, so the generator's exception set cannot drift from the oracle's.

The qualitative-but-closes-on-something-real pattern is `kind = "artifact"`,
`evidence_type = "user-decision"`, no `match`. There is no separate `recorded` kind; it was cut as
`artifact` wearing a different name.

## 5. Property 1 — every gate carries a place to record

The compiler injects, on **every** gate, unconditionally:

```json
"directives": {
  "handback": {
    "purpose": "where this gate hands something back -- these are the engine's real, persistent channels, not a field to write prose into",
    "belief_worth_recording": "spine_evidence attach -- lands in this gate's own evidence[]",
    "open_question_out_of_scope": "spine_capture flag-candidate -- lands in the top-level triage_candidates[]",
    "concern_that_must_stop_this_gate": "spine_halt block -- sets status blocked and appends to the top-level blockers[], bubbling to the parent named below",
    "hand_back_to": "<parent, or the literal string \"unknown\">",
    "note": "there is NO engine verb that appends to a directives field on an active gate (amend rescope touches pending gates only), so this contract names verbs that persist rather than offering arrays that would render empty forever"
  }
}
```

**This shape replaced an earlier one and the reason matters.** My first design gave every gate
`beliefs`/`concerns`/`open_questions` arrays. The intent-fit critic searched the engine, the CLI and
the MCP surface for any verb that appends to a `directives` field on the gate a crew is *actively
working*, found none — `amend`'s `rescope` op is restricted to **pending** gates and demands
`--authority`/`--reason` — and then rendered my exact shape through `render_human` and pasted the
output: three labels with nothing after the colon, on every gate, forever. That is "looks like it
works", which the launch order names as worse than no field at all.

So the contract names the three channels the engine **really persists**, which are also the three E1
proved durable. `hand_back_to` defaults to the literal `"unknown"` when no parent is declared — a real
answer, not a missing one.

`directives`, not `constraints`, on measured grounds: `constraints` already means *rules this gate must
respect* on 970 populated tasks and on all three shipped-template instances; `directives` means *a
standing contract this gate must satisfy* and is populated on 22. A handback channel is a contract, not
a rule.

**Verified against behaviour, not shape.** `g1` must include a test that drives each named verb against
a generated spine and asserts the record lands where the contract says it lands, plus a test that
renders a generated gate through the engine's own `render_human` and asserts the handback block
appears.

## 6. Property 2 — judgment is carried up

`[gate.claim] magnitude = "large"` does three things:

1. **Injects a postcondition** `c-escalation` onto that gate:

   ```json
   {"id": "c-escalation",
    "statement": "LARGE CLAIM -- an independent reviewer must approve this gate before it closes: <text>",
    "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
    "satisfied": false}
   ```

   `c-escalation` is a **reserved id**: a spec that uses it is a spec-shape fault.
2. **Renders on the gate** as `directives.claim` (`magnitude`, `text`, and why the extra postcondition
   is there — an unexplained injected condition is a comprehension cost I am paying down deliberately).
3. **Rolls up** into `directives.claims_rollup` on the **last** gate, keyed by source gate id.

**Why `review-result` matching `verdict: APPROVE` and not `user-decision`.** My first design injected a
match-less `artifact`/`user-decision`. The intent-fit critic closed that checkpoint in two in-process
calls with no session, authority or identity involved, and showed why: `attach()` takes **no** authority
argument (unlike `waive()` three functions below it, which refuses an empty one) and hardcodes
`produced_by: "engine"` for every caller; and `user-decision` is in
`ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH`, so nothing constrains what the self-attached decision even
says. The escalation could not fail against the very agent it exists to check. A `review-result`
matching `verdict: APPROVE` is a **checked property** rather than bare arrival, and its natural producer
is a survey's consolidation — a different checklist driven by a different agent.

**The residual, stated plainly and floated, not patched:** the engine binds no provenance to evidence
at all. A determined single agent can still attach a `review-result` claiming APPROVE. Closing that
needs a `checklist_engine.py` change, which is outside a Commander's latitude, and it affects **every**
`artifact`/`user-decision` human checkpoint in the corpus — including the four in the Commander spine
this run is driving. Floated to the Admiral.

**Testing it.** The mission frame promised "a spec that declares a large claim without the escalation is
refused." That input **cannot be authored** once injection is unconditional, so that promise is
withdrawn. In its place: a positive test that injection is unconditional, and a **falsification-floor**
test in the `tests/test_mutation_floor.py` style — deleting the injection must turn a named test red.

## 7. Spec-shape faults — refused before any probe

`spec-unknown-check-kind` · `spec-missing-field` · `spec-empty-because` ·
`spec-gated-missing-postconditions` · `spec-all-qualitative-postconditions` · `spec-duplicate-gate-id` ·
`spec-duplicate-condition-id` (pre- and postcondition ids must be **disjoint** within a gate — the
schema's stated invariant, since `attest`'s `--which` fallback resolves by first match) ·
`spec-reserved-id` (`c-escalation`) · **`spec-config-ref-not-json`**.

That last one is not theoretical: I hit it in this very run. `checklist_engine.load_config` calls
`json.loads` on **any** `config_ref` that exists, so a `config_ref` pointing at a real non-JSON file
crashes the engine with an unhandled `JSONDecodeError` before any rail text can print — and
`validate_spine.py` has no fault for it. The generator refuses it; the gap in the oracle is a finding
for the return report, not a change to the oracle.

## 8. The generator

**One file, `scripts/generate_spine.py`**, with the pure/impure split at **function** granularity —
matching what `validate_spine.py` (pure `_fault_*` beside subprocess-calling `_collects_zero`) and
`checklist_engine.py` (pure `evaluate_git_change_policy` beside `_collect_changed_files`) already do.
A second module was cut; both precedents keep this split inside one file.

- `compile_condition(cond, *, repo_root_token) -> dict` and `compile_spec(spec) -> dict` are **pure**:
  dict in, dict out, no `Path`, no `open`, no `subprocess`.
- The probes, the oracle call, the file write and `main()` sit below them.

```
python scripts/generate_spine.py <spec.toml> --out <spine.json> --root . [--check-only]
```

Order, and **nothing is written unless every layer passes**:

1. `tomllib.load`.
2. Spec-shape check (§7) — cheap, no subprocess. Exit **2**.
3. `compile_spec` — pure.
4. Probes (§4) — the expensive, environment-touching layer. Exit **3**.
5. `validate_spine.validate(spine, repo_root=root)` — **the literal last statement before success.**
   Imported and called, never re-implemented. Any `Fault` prints the oracle's own `str()` **verbatim**,
   never a paraphrase. Exit **4**.
6. Write. Exit **0**.

`--check-only` runs 1–5 and writes nothing.

**Undecidable refuses.** Anything on `validate()`'s `.undecidable`, or a probe that cannot run, refuses
and names what could not be judged. This is deliberately *stricter* than the oracle's own exit-code
contract, because a generator that emits while saying "I could not tell" would reintroduce exactly the
undecidable-silence defect C1 shipped a third channel to kill. **There is no flag to skip it** — an
escape an author can take is the shape this epic exists to find.

**The one sanctioned recovery**, stated because the testability critic showed the hazard is live on
this host (`python` has pytest 9.1.1; `python3` does not): make `pytest` importable under the
interpreter the check names, then re-run. There is no other path, and a fixture pins this refusal so it
cannot silently regress to a warning that still writes.

## 9. Guard fixtures

Every probe is pinned the way `tests/test_mcp_adoption.py::_cli_only_verb_violations` is: **≥2
VIOLATING** fixtures it must catch, **≥2 INNOCENT** it must not, and a **populated**
`ACCEPTED_FALSE_ALARM` bucket — populated, not merely named, for `script` and `population`, the two
probes with no oracle behind them. One fixture per side cannot distinguish a real AST parse from a
string match on the one flag the fixture happens to use.

## 10. The four defects: what is foreclosed, and what is not

| defect | kind | foreclosed? | residual |
|---|---|---|---|
| 1 · unquoted `-k Door or Tie or Registry` split by the shell | `pytest` | **Structurally.** There is no shell-text field to leave unquoted; the author writes a selector, the compiler quotes it. | none for this class |
| 2 · a probe that could only ever fail (`python -c 'import mcp_spine_server'` with no spine bound) | `pytest`, `script` | **Largely.** No kind runs an arbitrary interpreter line, and `script` never imports its target. | a `script` whose *runtime* behaviour depends on unbound environment is still authorable; the probe checks flags, not environment |
| 3 · `build_entry(session=…)` where the parameter is `work_id=` | `script` | **Partly. The defect shrinks; it does not vanish.** The author still types flag names and paths from memory; what changes is that a wrong flag is caught loudly at generation time. | a script registering flags dynamically yields no `add_argument` literals — refused as undecidable rather than silently passed, but also not *checked* |
| 4 · a population filter wrong twice, in opposite directions | `population` | **Yes, for the count.** The declared band is asserted against the live tree by executing the emitted command itself. | the *glob* can still be the wrong glob; the probe proves the count matches the declaration, not that the declaration expresses the intent |

**The honest headline: the shell-tokenization class is closed structurally; the wrong-invocation class
is narrowed, not removed.** Section 3 of the return report answers the settling question in exactly
these terms, and does not claim a clean sweep.

## 11. What is deliberately out

`git-change-policy` as a spec kind — cut. It was the only kind in my table with no defect behind it,
neither role spec instantiates it, and its inline policy is seven fields plus a fixture set. Deletion
test: the complexity vanishes and does not reappear in the role specs or the dispatch proof. It returns
in the wave that authors a closeout-gate spec against a real caller.

Also out: any change to `checklist_engine.py`'s on-disk format; any change to `validate_spine.py`; any
edit to a shipped template.
