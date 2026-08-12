# Candidate gate plan — C2: generate the spine from a spec

The converged design and gate plan for `epic-559/c2-generate-the-spine`, produced by the Commander
from three independent candidates (`plan-alt-a-smallest-diff`, `plan-alt-b-most-testable`,
`plan-alt-c-best-seam`). This document is what the cold critics read.

## The recommendation — a named hybrid, not a menu

**Candidate C's seam, carrying candidate B's vocabulary and escalation mechanism, with C's static
AST guard in place of B's live-import probe.**

Axis by axis:

- **Seam placement → C.** C splits a **pure** `compile_spec(spec: dict) -> dict` from a thin CLI that
  does every I/O act (TOML read, probes, oracle call, file write). This is the best seam for two
  reasons: the translation is unit-testable with plain dicts and no filesystem, and the split *is*
  the control the mission's return shape demands — the same spec is **accepted by the pure emit path
  and refused by the guarded CLI**, which is the pairing that makes the refusal evidence rather than
  an assertion.
- **Vocabulary and depth → B.** B's closed kind set, each kind carrying a **generation-time probe**
  keyed to one of the four historical defects, is a materially stronger answer to the mission than
  A's two kinds. A's own settling-question answer concedes the point: an `argv` list closes the
  shell-tokenization class and leaves the wrong-invocation class wide open.
- **Judgment carried up → B.** B makes a large claim **mechanically change what the gate requires to
  close**, by auto-injecting an escalation postcondition. That is "greater claim requires greater
  review" implemented rather than rendered. C's `claims_rollup` onto the terminal gate is additive
  and is kept alongside it.
- **Probing a named script → C over B.** B imports the author-named module to check the call
  signature, and B itself names the risk: generation then *executes* import-time code, which is
  defect 2's shape one layer up. C reads the target with `ast.parse` and never imports it. C's
  approach is strictly safer and gives up only dynamically-registered flags, which C states plainly.
- **Locality → A, and A loses anyway.** A is the smallest and most readable, and its `git-change-policy`
  omission is a real cost it names honestly. But smallest-diff optimizes the wrong thing here: the
  mission is not "emit JSON with less typing," it is "make the wrong check impossible to author."

**One finding is adopted from C outright, and it is not cosmetic.** `init_work_area.resolve_spine`'s
own docstring records that the engine passes `command` checks **no `cwd`**, so a relative check
inherits the launcher's directory (fragile, tracked as #341). C hit this live: a `pytest -k` check run
from outside the repo found nothing, silently. Every `command` check this generator emits is therefore
anchored `cd <repo-root> && …`. `<repo-root>` is a resolver-owned token — verified by me:
`_RESOLVER_OWNED_TOKEN_RE.fullmatch("<repo-root>")` is true, and `resolve_spine` substitutes it with an
absolute posix path before a spine is ever driven — so this is legitimate in generator output and is
**not** the placeholder class the generator refuses.

## The design

### Spec format

TOML (`tomllib` is stdlib on this host's `python`, 3.12.3 — verified), one file per role spec, at
`specs/<role>.spine.toml`. Top level: `work_id`, `type` (`gated`/`survey`), `config_ref`, then an
ordered `[[gate]]` array-of-tables with nested `[[gate.preconditions]]` / `[[gate.postconditions]]`.

**There is no raw-command field anywhere in the format.** A check is one of a closed set of kinds with
typed fields. Extending what can be proven is a code change with a test, not a string typed into a
spec. This is the single most consequential choice in the design and the one most likely to be wrong;
it is graded `guess` in the mission frame and the settling question is its settle-experiment.

| kind | author writes | compiles to | probe at generation time | defect it addresses |
|---|---|---|---|---|
| `qualitative` | `because` (required, non-empty) | `check: null` | refuses an empty/missing `because` | `qualitative-must-be-stated` — silence refused, the stated form accepted |
| `recorded` | — | `artifact` / `user-decision` | none needed | the `falsifiable-all-null` escape for a genuinely-qualitative gate: it still closes on something the engine checks |
| `pytest` | `selector`, `min_collect` (default 1), `targets` | the corpus idiom, selector `shlex.quote`d, `cd <repo-root> &&` anchored | runs `--collect-only` and refuses below `min_collect` | 1 (unquoted selector — structurally impossible, no shell-text field exists) and 2 (zero-collect) |
| `script` | `path`, `args` (list of literal tokens) | `shlex.join`, `cd <repo-root> &&` anchored | `ast.parse` the target, collect every literal `add_argument("--flag")`, refuse an unknown `--flag`; never imports or executes it | 3 (a flag argparse does not define) |
| `population` | `root`, `glob`, `expected` or `expected_min`/`expected_max` | a `command` check that counts and compares | globs the live worktree now, refuses outside the declared band, printing the real count and examples | 4 (a filter wrong twice, in opposite directions) |
| `artifact` | `evidence_type`, `match` | passthrough | refuses a missing `match` unless `evidence_type` is `user-decision`, reusing `validate_spine.ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH` **by import** | #562's artifact-asserts-a-property fault |
| `git_change_policy` | the schema's own inline policy fields | passthrough | shape-check only | — (kept so a closeout gate is authorable at all; A showed what its absence costs) |

Any other `kind` value is a spec-shape fault, refused before any probe runs, naming the closed set.

### Module shape

```
scripts/spine_spec.py       # PURE. compile_spec(spec) -> spine dict. No Path, no open, no subprocess.
scripts/generate_spine.py   # the CLI, and the only place that touches the filesystem or a subprocess
specs/implementer.spine.toml
specs/reviewer.spine.toml
```

CLI: `python scripts/generate_spine.py <spec.toml> --out <spine.json> --root . [--check-only]`

Order of operations, and **nothing is written unless every layer passes**:

1. `tomllib.load` the spec.
2. Spec-shape check (closed vocabulary, unique ids, required fields) — cheap, no subprocess.
3. `spine_spec.compile_spec(spec)` — pure.
4. Generation-time probes (pytest collect, script AST flag scan, population count).
5. `validate_spine.validate(spine, repo_root=root)` — **the literal last word before success.** Any
   `Fault` prints the oracle's own message verbatim and exits non-zero, writing nothing. The oracle is
   imported and called, never re-implemented, so the generator's notion of acceptance cannot drift
   from it.
6. Write.

**Undecidable is refused, not waved through.** If `validate()` reports anything on `.undecidable`, or
a probe cannot run (no interpreter with pytest importable), the CLI refuses and names what it could not
judge. A generator that emits while saying "I could not tell" would reintroduce exactly the
undecidable-silence defect C1 shipped a third channel to kill. There is **no** flag to skip this —
an escape an author can take is the shape this epic exists to find.

### Property 1 — every gate carries a place to record beliefs, concerns and open questions

The compiler injects, on **every** gate, unconditionally, whether or not the author wrote anything:

```json
"directives": {
  "handback": {
    "beliefs": [], "concerns": [], "open_questions": [],
    "how_to_record": "<the real engine verbs, named>",
    "hand_back_to": "<the parent this crew reaches, and the gate to block at>"
  }
}
```

It goes in `directives`, not `constraints`, on measured grounds: `constraints` already means *rules
this gate must respect* on 970 live tasks; `directives` means *a standing contract this gate must
satisfy* and is populated on 22. A handback channel is a contract, not a rule.

**The `how_to_record` field is load-bearing and must never be empty**, because
`checklist_engine.py:2189` renders a directives block **only when it is non-empty**. A gate whose
author recorded nothing yet would otherwise render no handback block at all — the place to record
would exist in JSON and be invisible to the crew, which is the "looks like it works" failure the
launch order names. The always-present instruction is what makes the block render on every gate.

Verified against **behaviour**, not JSON shape: a test renders a generated gate through the engine's
own `render_human` and asserts the handback block appears.

### Property 2 — judgment is carried up, not buried

A gate may declare:

```toml
[gate.claim]
magnitude = "large"     # or "normal" (default)
text = "..."
```

`magnitude = "large"` does three things, and the first is the one that matters:

1. **Auto-injects an escalation postcondition** (`artifact` / `user-decision`) onto that gate. The gate
   cannot close on the crew's own say-so; a tier above must record a decision. The author never has to
   remember to add a stricter close criterion for a big claim — the generator adds it because the
   claim was declared. An escalation an author must remember is the authored-from-memory failure this
   mission exists to remove.
2. **Renders on the gate itself**, as a `directives.claim` entry, so the agent working that gate sees
   it.
3. **Rolls up into a `claims_rollup` directive on the last gate**, keyed by source gate id, so a
   reviewer reading only the terminal state sees every large claim the run made.

The rollup is built by the compiler from the same `claim` fields, so it cannot drift from what the
individual gates say.

## The gate plan

Six gates. Sequenced so verification is green at every boundary: the pure compiler is proven before
anything depends on it; the CLI is proven before a real spec is authored against it; a real spec is
generated and lint-clean before it is ever dispatched.

| id | title | delivers | close criteria (what evidence closes it) | kind |
|---|---|---|---|---|
| **g0** | Freeze the vocabulary and the two property mechanisms | `DESIGN_NOTE.md`: the closed kind list, the handback contract's exact fields, what `magnitude = "large"` injects, and how each of the four historical defects is foreclosed | the note exists and names, for each of the four defects, the kind that forecloses it and the residual it does not | **reasoning gate, no crew.** Crew-waiver: this is a naming and authority decision that is the Commander's to make, and there is no code or independently-verifiable change for a reviewer to run |
| **g1** | The pure compiler | `scripts/spine_spec.py` — `compile_spec`, `compile_condition`, all seven kinds, handback injection, claim escalation + rollup | unit tests over plain dicts (no TOML, no filesystem, no subprocess) covering every kind and both properties; **one test renders a compiled gate through the real `checklist_engine.render_human`** and asserts the handback block appears; `validate_spine.py --sweep --root .` unchanged from baseline | crew |
| **g2** | The CLI, the probes, and the refusal | `scripts/generate_spine.py` — tomllib load, spec-shape check, probes, `validate()` as the last word, write-nothing-on-refusal | **the control pairing, run for real:** one spec accepted by the pure `compile_spec` path and **refused** by the guarded CLI, with the refusal message pasted; and the same spec corrected, accepted and written. Each probe demonstrated once against a defect-shaped fixture and once against a sound one | crew |
| **g3** | The role specs | `specs/implementer.spine.toml`, `specs/reviewer.spine.toml`, and the spines generated from them | `generate_spine.py` exits 0 on both; `validate_spine.py` on each generated spine is clean with zero undecidable; every place the generated spine and the shipped template disagree is written up as a **finding** — no shipped template is edited | crew |
| **g4** | A generated spine drives, for real | one `run_crew.py --spine <generated>` dispatch in a scratch work-id | `run_crew.py` judges it `spine_terminal`; the dispatch transcript and the driven spine's final state are pasted | crew |
| **g5** | Closeout and the honest answer | full suite in the declared test mode; sweep before/after; `REPLAN_INPUT.json`; the settling-question answer; the float items | suite at the declared baseline or an explained delta; sweep fault set unchanged; `verify_iterative_role_artifacts.py commander` exits 0 | **reasoning gate, no crew.** Crew-waiver: the deliverable is the Commander's own evidence packet and float list, which is not a diff a reviewer can run |

### Three-way guard fixtures

Every probe written in g2 is pinned the way `tests/test_mcp_adoption.py::_cli_only_verb_violations`
is: a **VIOLATING** fixture it must catch, an **INNOCENT** one it must not, and an
**ACCEPTED_FALSE_ALARM** it knowingly tolerates. A guard with no test on its own false-positive
boundary is how C1's round 1 shipped an 8-of-9 false-positive rate.

## The settling question, answered in advance for this design

**Partly no, partly yes — and the split is the honest result.**

- **No** for the shell-tokenization class (defect 1). There is no shell-text field in the format, so
  there is nothing for an author to leave unquoted. The author writes `selector = "Door or Tie or
  Registry"` and `min_collect = 4`; the generator alone assembles and quotes the command.
- **No** for zero-collect (defect 2) and the wrong population (defect 4): the probe runs the thing and
  refuses on the number.
- **Partly** for the wrong-invocation class (defect 3). Under `script`, the author still types flag
  names and paths from memory — `args = ["--work-id", "<work-id>"]`. What changes is that a wrong flag
  is caught **loudly at generation time** by the AST scan rather than downstream. It is not caught for
  a script that registers flags dynamically. **The defect shrinks; it does not vanish**, and the run
  will report it that way rather than claiming a clean sweep.

## Known weaknesses of this recommendation

Carried forward from the candidates' own self-criticism, because a plan with no stated weakness reads
as unexamined:

- **Two of the probes have no oracle behind them.** `validate_spine.py` is 665 shipped lines with an
  incident behind every fault. The `script` AST scan and the `population` counter are new code judged
  only by the tests written in the same wave. If either accepts something that fails downstream, the
  design recreates "the check exits clean but does not test what it claims" one level removed — inside
  the very generator built to prevent it. Mitigation: three-way guard fixtures on both, and the oracle
  still runs last regardless.
- **Auto-injection is invisible in the author's spec.** A reader of the emitted JSON sees an
  escalation postcondition that appears nowhere in the TOML. Mitigation: the `directives.claim` block
  always explains why the extra condition is there. It is still a real comprehension cost, chosen
  because forgettable-but-traceable is worse than un-forgettable-but-needs-a-note.
- **Seven kinds is more surface than the two required role specs need.** `git_change_policy` and
  `population` are not used by either role spec. They are kept because A demonstrated what dropping a
  kind costs (a whole gate class becomes unauthorable) and because `population` is the only answer to
  defect 4. A critic who thinks this is YAGNI should say so — it is the most attackable scoping call
  in the plan.

## Untaken roads and scaling records

- **Design-it-twice:** panel of 3, run. Untaken: a fourth `max-flexibility` candidate (a spec that can
  express raw shell) — deliberately not funded, because it is the mission's null hypothesis rather than
  a design, and it is instead carried as the settling question every candidate had to answer.
- **B's `python-call` kind was dropped.** Reason: it imports author-named modules at generation time,
  running their import-time side effects inside the generator — defect 2's own shape one layer up, a
  risk B itself named. `script` + AST covers the CLI case without executing anything.
- **Cold plan critic:** three-lens panel (intent-fit, testability/falsifiability, simplicity/YAGNI),
  run sequentially. Scaling rationale: this plan introduces a load-bearing interface other authors will
  write against, and the doctrine's rule is "when in doubt, panel." Surfaced here for the Admiral to
  overturn.


---

# SUPERSEDED IN PART — read `plan-critic.md` and `execute.json` for what is actually being built

This document is the **pre-critique** candidate plan, kept as written so the critics' findings can be
read against what they actually reviewed. The three-lens cold panel changed it materially. What is no
longer true of this document:

| this document said | what is being built | why |
|---|---|---|
| `directives.handback` carries `beliefs`/`concerns`/`open_questions` arrays | it carries a contract naming `attach`, `flag-candidate` and `block`, plus the parent | no engine verb appends to a `directives` field on an active gate, so the arrays would render empty forever (IF-1, BLOCKING) |
| a large claim injects an `artifact`/`user-decision` postcondition | it injects `artifact`/`review-result` matching `verdict: APPROVE` | a match-less `user-decision` is closable by the same session that made the claim, so the escalation could not fail against the agent it checks (IF-2, BLOCKING) |
| seven check kinds | **five**: `qualitative`, `pytest`, `script`, `population`, `artifact` | `git_change_policy` has no defect behind it and no caller this wave; `recorded` is `artifact` + `user-decision` renamed (S-S3, S-M1) |
| two modules, `spine_spec.py` + `generate_spine.py` | **one** file, `scripts/generate_spine.py` | both cited precedents keep the pure/impure split at function granularity in one file (S-S2) |
| six gates, four of them crew gates | **twelve items over five gates**, three of them crew gates | C1 built the whole 665-line oracle under one implement-then-cold-review cycle (S-S1) |
| the `population` probe globs in Python | the probe **executes the compiled command itself** | two implementations of one filter is literally defect 4's shape (T-S3) |
| "a spec that declares a large claim without the escalation is refused" | a positive test that the injection is unconditional, plus a falsification-floor test | with unconditional injection that negative input cannot be authored (T-S2) |

TOML was challenged and **kept**, with the measurement the critic asked for: 14 of the 61 imperatives
in the shipped templates exceed 1000 characters and the longest is 3534. In JSON each must be authored
as one escaped single-line string.
