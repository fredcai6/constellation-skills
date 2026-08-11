# Cold plan critic panel — findings and Commander triage

Three cold critics, one lens each, dispatched sequentially on Sonnet against `CANDIDATE_PLAN.md` +
`MISSION_FRAME.md` only. None read the three plan-alternative candidates or the launch order.

| lens | result | BLOCKING | SERIOUS | MINOR |
|---|---|---|---|---|
| intent-fit | `crew-handoffs/plan-critic-intent-fit-result.md` | 2 | — | 1 note |
| testability / falsifiability | `crew-handoffs/plan-critic-testability-result.md` | 0 | 4 | 3 |
| simplicity / YAGNI | `crew-handoffs/plan-critic-simplicity-result.md` | 0 | 3 | 2 (+1 checked-and-holds) |

**Every finding is triaged below by me. The critics did not triage their own.** Both BLOCKING findings
were found by *running the engine*, not by reading the plan — which is the third wave running where
that has been true.

## BLOCKING

### IF-1 — `directives.handback`'s `beliefs`/`concerns`/`open_questions` arrays are unwritable, so they render permanently empty · **ACCEPTED, design changed**

The critic searched for any engine verb that appends to a `directives` sub-field on the gate a crew is
actively working, and there is none. The only verb that can touch `directives` at all is `amend`'s
`rescope` op, which is restricted to **pending** gates — categorically not the gate a crew is inside —
and demands `--authority`/`--reason`. The critic then rendered the exact shape my plan specified
through `render_human` and pasted the output: three fields rendering as a bare label and a trailing
space, on every gate, forever.

That is "looks like it works", one level inside the mechanism built to avoid it. The launch order's own
words: *a new field the engine ignores is worse than no field.* An unwritable sub-field of a real field
is the same defect wearing the real field's clothes.

**Change:** the arrays are gone. `directives.handback` becomes what `directives` actually means — a
**standing contract** — and it names the three channels the engine really persists, which are also the
three E1 proved durable:

| the crew has | the verb | where it lands |
|---|---|---|
| a belief worth recording as evidence | `spine_evidence attach` | the gate's own `evidence[]` |
| an open question that is out of scope | `spine_capture flag-candidate` | top-level `triage_candidates` |
| a concern that must stop the gate | `spine_halt block` | `status: blocked` + top-level `blockers`, bubbling to the recorded parent |

plus `hand_back_to`, carrying the parent the dispatch recorded. The property is then verified against
**behaviour**: a test drives each named verb against a generated spine and asserts the record lands
where the directive says it will — not merely that a block of text renders.

### IF-2 — the escalation postcondition is closable by the same session that made the claim · **ACCEPTED in substance; fix modified, residual floated**

The critic closed a `magnitude = "large"` escalation checkpoint in two in-process calls with no
session, authority, or identity involved, and showed `attach()` takes **no** authority argument at all
(unlike `waive()` three functions below it, which refuses an empty one) and hardcodes
`produced_by: "engine"` regardless of caller. With `evidence_type: "user-decision"` in
`ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH`, the auto-injected condition can ship with `match: {}`, so
nothing constrains what the self-attached decision even says. The critic's verdict is correct and it
is the sharpest thing anyone said this wave: **as designed, the escalation cannot fail against the
very agent it exists to check.**

**Change:** the injected escalation is now `artifact` / `review-result` with
`match: {"verdict": "APPROVE"}`. That is a *checked property* rather than bare arrival, it is the
corpus's own idiom for independent review, and per `docs/CHECKLIST_SCHEMA.md` a `review-result`'s
natural producer is a **survey's consolidation** — a different checklist driven by a different agent.
It raises the bar from "any artifact of a type that needs no match" to "an artifact asserting APPROVE".

**Not adopted:** the critic's option (a), making `attach` check a session id distinct from the
leaseholder. That is a `checklist_engine.py` change and therefore outside my latitude.

**Floated to the Admiral, and it is bigger than my design:** *the engine binds no provenance to
evidence.* `waive` demands an authority; `attach` does not, and stamps `produced_by: "engine"` for
every caller. So **every** `artifact`/`user-decision` human checkpoint in the corpus — including the
four in the shipped Commander spine I am driving right now — is satisfiable by the agent it is meant
to check. My change raises the bar as far as a *generator* can; closing it properly needs an engine
change, which is the Admiral's call. Recorded as a triage candidate and in the return report.

## SERIOUS

### T-S1 — `git_change_policy` (underscore) would emit a kind the engine does not implement · **ACCEPTED, and generalized**
The critic ran the oracle on the literal reading and got `shape-unknown-check-kind`. Resolved by
deletion (see S-S3), but the *class* survives any future kind, so instead of a one-off spelling note I
am adding a general guard: a test asserts every `check.kind` the compiler can emit is a member of
`validate_spine.IMPLEMENTED_CHECK_KINDS`, **imported, never re-declared**.

### T-S2 — the promised negative test is unconstructable · **ACCEPTED**
Correct: if `magnitude = "large"` *always* injects, no spec can declare a large claim and lack the
escalation, so the mission frame's promised refusal has no authorable input. The frame's claim is
reworded. In its place: a positive test that the injection is unconditional, plus a
**falsification-floor** test in the `tests/test_mutation_floor.py` style — deleting the injection must
turn a named test red. A guard whose own removal changes nothing is the defect this epic hunts.

### T-S3 — the `population` probe and the command it certifies are two implementations · **ACCEPTED, stronger fix**
The critic is right that a Python glob and a shell count do not agree by default on dotfiles, `**`
recursion, symlinks — and that this is *literally defect 4's shape*, reintroduced inside the kind built
to close it. Rather than testing two implementations against each other, there is now **one**: the
generation-time probe **executes the compiled command string itself** and judges on its exit status.
The thing probed is the thing shipped.

### T-S4 — undecidable refuses hard, with no stated recovery · **ACCEPTED**
The critic showed the interpreter differential is live on this host (`python` has pytest 9.1.1,
`python3` does not). The hard refusal stays — an author-takeable escape is the shape this epic exists
to find — but the plan now names the one sanctioned recovery ("make pytest importable under the
interpreter the check names, then retry"), and a fixture pins the refusal path so it cannot silently
regress to a warning that still writes.

### S-S1 — g1 and g2 are one gate wearing two crew dispatches · **ACCEPTED**
The precedent cited is decisive and in this very epic: C1 built all 665 lines of `validate_spine.py` —
four fault detectors, the subprocess collection probe, shape faults, the CLI — under **one**
implement-then-cold-review cycle. Merged. Six gates become five; four crew gates become three.

### S-S2 — the two-file pure/impure split contradicts this repo's own precedent · **ACCEPTED**
Both modules I cited as authority keep the split at **function** granularity inside one file:
`evaluate_git_change_policy` (pure) sits beside `_collect_changed_files` (shells out to git) in
`checklist_engine.py`; the `_fault_*` functions sit beside `_collects_zero` in `validate_spine.py`.
One file, `scripts/generate_spine.py`. The control pairing is unaffected — calling `compile_spec()`
directly versus `main()` is still two different entry points.

### S-S3 — `git_change_policy` earns nothing this wave · **ACCEPTED**
It is the only row in my kind table whose "defect it addresses" column is empty, neither role spec
instantiates it, and its inline policy is seven fields of schema surface plus a fixture set. Deletion
test: the complexity vanishes and does not reappear in the role specs or the dispatch proof. Cut. It
returns in the wave that authors a closeout-gate spec against a real caller.

## MINOR

- **T-M1 — g0's close criteria asserts against text describing the mechanism.** **ACCEPTED.** The
  design note's kind list is pinned by a test at G1 asserting it equals the compiler's own constant.
  g0 itself still closes on my attestation, and I state plainly that the pin lands one gate later.
- **T-M2 — one fixture per side cannot distinguish a real parser from a fixture-shaped string match.**
  **ACCEPTED.** ≥2 VIOLATING and ≥2 INNOCENT per oracle-less probe, and the `ACCEPTED_FALSE_ALARM`
  bucket is populated for both, not merely named.
- **T-M3 — "accepted by the pure path" oversells what that half of the control shows.** **ACCEPTED.**
  The pure path *translates*; it does not judge. Reworded throughout.
- **S-M1 — `recorded` is `artifact` wearing a different name.** **ACCEPTED.** Cut. `artifact` with
  `evidence_type = "user-decision"` and no `match` is already legitimate to the oracle and produces
  identical JSON. Five kinds remain: `qualitative`, `pytest`, `script`, `population`, `artifact`.
- **S-M2 — TOML is a corpus precedent-break for an undemonstrated ergonomics gain.** **REJECTED, with
  the evidence the critic asked for**, and the critic's *smallest fix* adopted (the judgment is
  recorded as a named, argued choice in the design note). The critic is right that no TOML exists in
  this repo and right that switching costs one line. But the payer is demonstrable and I measured it:
  across the 61 imperatives in the 12 shipped templates, **14 exceed 1000 characters and the longest
  is 3534**; my own spine's `plan` imperative is 3555. In JSON each of those must be authored as a
  single-line string with every quote and newline escaped by hand — which is precisely the
  typed-from-memory-and-wrong class this mission exists to remove, relocated from the check to the
  imperative. TOML's triple-quoted multi-line string needs no escaping. That is the deciding factor,
  and it is now argued rather than asserted.
- **IF-note — my claim about what `render_human` gates on was imprecise.** **ACCEPTED.** What must be
  non-empty is the directives dict, not `how_to_record` specifically. Corrected. The critic's real
  point stands and is uncomfortable: the plan reasoned about the renderer without checking it, in the
  same document that built an unwritable-field design on adjacent reasoning.

## Checked and holds (reported, not a finding)

`claims_rollup` is **not** redundant. The simplicity critic read `render_human` directly and confirmed
it renders `directives` only for the **currently active** task — so once a gate advances, its own
`directives.claim` is never rendered again by anything. The rollup on the terminal gate is the only
channel with the right lifetime for a reviewer reading the final state. Kept, and now kept for a
verified reason rather than an assumed one.
