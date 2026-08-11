# Commander working notes — `epic-559/c2-generate-the-spine`

Sole writer: the Commander (delegated). Written at `g4-closeout`.

## The settling question, answered without softening

> **Does the role spec still ask its author to type a shell command from memory?**

**No — and the defect it was hiding did not go away, it got smaller and moved somewhere I can name.**

**Closed structurally.** There is no shell-text field anywhere in the format, so there is nothing for an
author to leave unquoted. Defect 1 — `-k Door or Tie or Registry` split by the shell — cannot be
authored: the author writes `selector = "Door or Tie or Registry"` and a number, and `shlex.quote` is
the compiler's job. Defect 2 (a selector collecting zero) and defect 4 (a wrong population count) are
closed by probes that *run the thing* at generation time and refuse on the number.

**Narrowed, not closed: the wrong-invocation class (defect 3).** The `script` kind's probe checks two
things — that every `--flag` the author named exists in the target's `add_argument` literals, and (after
`g3`) that every path-shaped positional argument exists unless it carries a resolver-owned token. Both
were earned: the positional half only exists because the `g2` crew reported its absence as a residual
rather than claiming a clean sweep.

**But there is a third half, and I found it by authoring the defect myself.** The probe verifies that
every flag the author **named** exists. It cannot see a **required** flag the author **failed to name**.
I wrote `g3`'s dispatch-proof check as

```toml
kind = "script"
path = "scripts/generate_spine.py"
args = ["specs/reviewer.spine.toml", "--check-only", "--root", "."]
```

omitting `--out`, which argparse marks `required=True` unconditionally. The generator emitted it. The
oracle accepted it. The check exited 2 — `the following arguments are required: --out` — before a spec
was ever opened, and could never have passed. The mission to remove hand-authored check defects shipped
one into its own machinery, and the machinery did not catch it.

That is the honest headline: **the shell-tokenization class is gone; the wrong-invocation class is
narrowed from silent-and-downstream to loud-and-at-generation-time for flags the author names, and is
untouched for the flags they forget.** The mechanism to close it exists (read the target's parser for
`required=True` arguments) and is named in the run packet as forecast `U-required-flag-probe`.

**The other thing the format cannot express, and it matters more than it looks.** A `pytest` check is
probed by running `--collect-only` and refusing below `min_collect`. So a spine **cannot be generated
for work whose tests do not exist yet** — the selector collects zero at generation time and the
generator refuses. The shipped `IMPLEMENTER_PLAN.template.json` is TDD-shaped by design (a red attest,
then a green command), and its author instantiates it *before* the test is written. **The generator
cannot author that plan.** Both role specs sidestepped this by pointing at tests that already existed.
Recorded as uncertainty `U-tdd-red-target`; it is the first thing I would settle next.

## What the dispatch proof does and does not establish

The `g3` cold reviewer put this better than I had, and it belongs here verbatim in substance:
`spine_terminal` is a **purely structural** predicate — every item complete or skipped. A spine authored
with only `qualitative` postconditions could reach it on a crew's attestation alone, and that would be a
check that cannot fail. This dispatch's proof is real because *this* spine gated its substantive
postcondition behind a `command` check the engine runs itself by subprocess (evidence stamped
`produced_by: engine`), which required the twelve real `TestScriptProbe` tests to exist and pass.

So: **protected intent #4 is proven for this dispatch, not as a property of the `spine_terminal`
completion contract.** I am not rounding that up.

## Floats to the Admiral — recorded, not patched

1. **The engine binds no provenance to evidence.** `attach()` takes no authority argument and stamps
   `produced_by: "engine"` for every caller, while `waive()` three functions below it refuses an empty
   `--authority`. So every `artifact`/`user-decision` human checkpoint in the corpus — including the
   four in the Commander spine this run drove — is satisfiable by the agent it is meant to check. A cold
   critic closed one in two in-process calls. My design raised the bar as far as a generator can (the
   gated escalation checks `review-result` matching `verdict: APPROVE`, a checked property rather than
   bare arrival); closing it properly is a `checklist_engine.py` change, outside a Commander's latitude.

2. **`record()`/`consolidate()` never evaluate artifact-kind postconditions on a survey item.**
   Measured, reproduced against bare engine dicts. No artifact-based gate can be enforced on any survey
   in this corpus — reviewer and interrogator checklists included. This is why the generator now refuses
   to inject an escalation on a survey and states the non-enforcement instead.

3. **A Commander cannot drive its own `execute.json` through the door.** `mcp_spine_server.py` binds one
   file at import time (`SPINE = Path(os.environ["SPINE_FILE"]).resolve()`) with no per-call addressing,
   while the Commander spine's own `execute` step requires driving a second checklist. Under the human's
   ruling that anything reachable only via the CLI is a defect, this is one — and it is the same family
   as the four `<engine>` tokens, but deeper, because no token substitution fixes it.

## Decision: the four `<engine>` tokens are NOT fixed this wave

Inherited latitude made this my call. **I am not fixing them, and the reason is not scope.**

The tokens tell a spine's driver to use the CLI. They are unresolvable, so today they are *visibly*
broken — an agent that reads one knows something is wrong and goes looking, which is how I found float 3
above. Substituting them for something that resolves would make the instruction *readable* while the
underlying defect — that the door cannot address a second spine — stayed exactly where it is. That
converts a loud defect into a quiet one, which is the escape-hatch shape this epic exists to find.

**Recommendation to the Admiral:** fix the door first (per-call spine addressing, or a door verb that
can drive a named child checklist), then remove the four tokens in the same change. Fixing the tokens
alone would be worse than leaving them.

## Triage candidates routed to the Admiral (no issues filed — none were authorized)

- **tc1** — the door cannot address a second spine (float 3 above).
- **tc2** — `recover_crews.py` misclassifies a **completed** spine-only dispatch as `NEEDS-ABANDON`,
  because its classifier keys on a result artifact such a crew deliberately never writes. Measured:
  `run_crew.py` wrote `status=completed`, `result=None`; `recover_crews.py` then said abandon-and-relaunch.
  This is precisely the failure `recover_crews` exists to prevent — a resumed Commander redispatching
  finished work.
- **tc3** — `checklist_engine.load_config` calls `json.loads` on any `config_ref` that **exists**, so a
  `config_ref` pointing at a real non-JSON file crashes the engine with an unhandled `JSONDecodeError`
  before any rail text prints. `validate_spine.py` has no fault for it. The generator refuses it as
  `spec-config-ref-not-json`; the oracle's gap is reported, not patched.
- **tc4** — this repo ships `map/INDEX.md` as an unfilled template and `map/ids.jsonl` empty, so **every**
  Commander dispatched here gets a structurally DEGRADED `map_orient`. Mine was discharged with six
  hash-pinned substitutes; the next one will pay the same cost.
- **tc5** — `REVIEW_SURVEY.template.json`'s `r6-fowler` postcondition carries a literal `<work-id>` and a
  `scripts/`-relative path. Nothing substitutes it for an ad-hoc reviewer survey built straight from the
  template, so a reviewer must `amend --delta ... retext-check` it before the Fowler script can even be
  found. Reported independently by two of my reviewers.
- **tc6** — a crew dispatched by `run_crew.py` inherits the **parent's** `SPINE_FILE`/`SPINE_SESSION`
  when no `--spine` is given, so a reviewer sees the Commander's own spine bound and must know not to
  drive it. Both g1 and g2 reviewers hit this and handled it correctly; a third might not.

## Wave-6 measurement, for the epic record

- Baseline suite at `0ab7ecab`: 2689 passed / 3 skipped / 1121 subtests. At close: **2788 passed / 3
  skipped / 1121 subtests** — 99 tests added.
- `validate_spine.py --sweep` fault lines: **23 before, 23 after**, checked by an engine postcondition at
  every gate boundary. No shipped template was edited.
- Crews dispatched: 3 plan-alternative authors, 3 cold plan critics, 2 implementers (one reworked), 2
  reviewers (one reworked), 1 spine-only probe crew (relaunched once after a block). **Cold review
  blocked once, and that block changed the design.**
