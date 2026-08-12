# Cold plan critic — lens: testability / falsifiability

**Reviewed:** `CANDIDATE_PLAN.md` against `MISSION_FRAME.md`, and the repo source the plan names
(`scripts/validate_spine.py`, `scripts/checklist_engine.py`, `scripts/init_work_area.py`,
`docs/CHECKLIST_SCHEMA.md`). Findings below come from running code against the plan's own claims,
not from re-reading prose. Base commit `0ab7ecab`.

## BLOCKING

None. Nothing here makes the plan unsafe to start; the pure-compiler gate (g1) in particular is
soundly falsifiable as written. The items below are things to fix before or during g2/g3, not
reasons to stop.

## SERIOUS

### S1 — The `git_change_policy` kind's "passthrough" claim, taken literally, fails the plan's own oracle

**What is wrong.** The gate table (`CANDIDATE_PLAN.md:66`) names the author-facing spec kind
`git_change_policy` (underscore) and says it "compiles to" a passthrough check. If "passthrough"
means the kind *string* is carried unchanged into the compiled spine's `check.kind`, the emitted
spine carries `"kind": "git_change_policy"` — which the engine does not implement. The real,
shipped kind is spelled `git-change-policy` (hyphen), everywhere: `validate_spine.py`'s own
`IMPLEMENTED_CHECK_KINDS` and `checklist_engine.py`'s dispatch (`if kind == "git-change-policy":`,
line 861).

**The evidence.** I built the minimal spine the literal reading implies and ran the real oracle:

```
$ python -c "... validate({'tasks': {'g1': {'postconditions': [{'check': {'kind': 'git_change_policy'}}]}}})"
1 fault(s)
[shape-unknown-check-kind] g1.postconditions.c1: check kind 'git_change_policy' is not one the
engine implements (['artifact', 'command', 'git-change-policy'])
```

Every other row's "compiles to" is unambiguous about the transform (`pytest`/`script`/`population`
all explicitly compile to a *different* shape, `command`); only `artifact` and `git_change_policy`
say bare "passthrough," and only `git_change_policy` has a name that doesn't already match its
target string.

**What it costs if shipped as planned.** Best case, this is caught immediately — g3's own close
criteria requires `validate_spine.py` clean with zero undecidable on the generated role specs
(`CANDIDATE_PLAN.md:162`), and my repro shows exactly this fault firing. So it likely self-corrects
inside the run. But that is the oracle catching a bug in the generator the design exists to prevent
naming drift in — which is worth surfacing rather than assuming away, and it burns a review cycle
that a one-line clarification avoids. It is also the one row in the table that is genuinely
ambiguous to an implementer reading cold.

**Smallest fix.** State explicitly in the gate table (or g0's `DESIGN_NOTE.md`) that
`compile_condition` for `git_change_policy` emits `check.kind = "git-change-policy"` (the engine's
literal string), independent of the TOML field's snake_case spelling — and add that exact-string
assertion to g1's unit tests, not just to the deferred g3 sweep.

### S2 — The plan promises a negative test that its own mechanism makes unconstructable

**What is wrong.** `MISSION_FRAME.md:148-150` names, as one of the run's checkable claims: *"a spec
that declares a large claim without the escalation is refused."* But `CANDIDATE_PLAN.md:138-142`
(Property 2, item 1) specifies that `magnitude = "large"` **unconditionally auto-injects** the
escalation postcondition at compile time — "The author never has to remember to add a stricter
close criterion for a big claim." Given that mechanism, there is no TOML an author can write that
declares `magnitude = "large"` and lacks the escalation postcondition after compilation: the
compiler always adds it. The "negative" case the frame promises as re-confirmable evidence cannot
be constructed through the documented path, so nothing in the plan can actually exercise a refusal
here — there's no fixture that goes red for it because there's no way to author the violating input.

**What it costs if shipped as planned.** Either the claim in the mission frame goes unfulfilled
silently (no test ever exercises it, and nobody notices because it "sounds" like Property 2's
positive test), or an implementer invents a refusal path that isn't in the design (e.g. rejecting a
raw, hand-edited spine JSON that carries `magnitude` without escalation) — which is scope the plan
never scoped, since hand-edited spines bypass the generator entirely and the oracle knows nothing
about `magnitude`.

**Smallest fix.** Either name explicitly, in the plan, which layer performs this refusal and on
what malformed input (e.g. "a spine JSON that sets `directives.claim.magnitude` without a matching
`claims_rollup` entry is not something the generator can ever refuse, because it can only be
produced by hand-editing output — this claim in the mission frame is unfulfillable through the
generator path and should be dropped or reworded to a positive-only test"), or replace the promised
negative test in the frame with the one thing that actually is falsifiable: a unit test that
`magnitude = "large"` **always** compiles the escalation postcondition, with no code path that
skips it.

### S3 — The `population` probe and the command it certifies are two different implementations, and only the probe is fixture-tested

**What is wrong.** Per the module shape (`CANDIDATE_PLAN.md:73-74`), `scripts/spine_spec.py` is
pure and produces the compiled `command` check text for a `population` condition; the
generation-time probe that globs the live worktree and refuses out-of-band counts lives in
`scripts/generate_spine.py` (`CANDIDATE_PLAN.md:64,86`). These are necessarily two separate
implementations — one in Python (`pathlib`-style glob, run at generation time), one in whatever
shell idiom the compiled `command` check uses (run later, by the engine, at drive time). The g2
close criteria (`CANDIDATE_PLAN.md:161`) only commits to "each probe demonstrated once against a
defect-shaped fixture and once against a sound one," which reads as exercising the **Python-side
probe function**, not the **emitted shell command**. Nothing in the plan requires that the compiled
`command` string, run for real, agrees with the Python probe's verdict on the same fixture.

**What it costs if shipped as planned.** This is not a hypothetical class of bug — it is the exact
shape of defect 4 the mission cites as motivation: "a population filter wrong twice, in opposite
directions" (`MISSION_FRAME.md:53`). Python's glob semantics (dotfile handling, `**` recursion,
symlink following, ordering) and a POSIX shell's `find`/glob equivalent do not agree by default. A
`population` condition could pass the generation-time probe and still be wrong (in either
direction) when the engine actually evaluates the compiled command at drive time — reintroducing,
one layer in, the very defect this kind exists to close, and silently: g4 only drives **one**
scratch spine once, which is not systematic coverage of every `population` condition the two role
specs emit.

**Smallest fix.** Extend the three-way guard fixtures for `population` to also run the *compiled
command string* (via subprocess, in the repo root) against the same VIOLATING/INNOCENT fixtures the
Python probe is tested against, and assert both give the same verdict — not just that the Python
probe alone catches the defect-shaped case.

### S4 — "Undecidable refuses, no escape flag" is a real, demonstrated environment hazard the plan never resolves

**What is wrong.** The design deliberately makes any `.undecidable` result from `validate()`, or any
probe that "cannot run" (no interpreter with pytest importable), fatal to generation, with **no**
escape flag (`CANDIDATE_PLAN.md:93-97`). This is *stricter* than the oracle it wraps:
`validate_spine.py` itself treats undecidable as non-fatal to its own exit code ("Exit-code
semantics are unchanged: undecidable conditions never flip `any_faults`," `validate_spine.py:642-646`).
The generator converts a soft "I couldn't check this" signal into a hard, unconditional stop.

**The evidence — this isn't hypothetical on this host.**
```
$ which python python3
/home/tommy/.local/bin/python
/usr/bin/python3
$ python -c "import pytest; print(pytest.__version__)"
9.1.1
$ python3 -c "import pytest"
ModuleNotFoundError: No module named 'pytest'
```
Exactly the interpreter differential `validate_spine.py`'s own `_resolve_interpreter` docstring
warns about (`validate_spine.py:321-336`, "`python3` has no `pytest` importable ... previously
reported 6 spurious zero-collect faults") is live on this very machine, one PATH entry away from
the interpreter the plan's assumption pins ("`python`, not `python3`," `MISSION_FRAME.md:88-90`).
Any spec authored or regenerated under an environment, container, or crew sandbox that resolves
`python3` first — or lacks a `pytest`-importable interpreter under any name — cannot generate a
spine containing a `pytest` (or `script`, if AST-parsing a missing target similarly undecides) kind
at all, and the plan gives that author no path forward: no `--force`, no partial-write-with-warning,
nothing. Question the lens asks directly: does the plan say what happens then? It does not — the
closest is a single sentence asserting this is a virtue ("an escape an author can take is the shape
this epic exists to find," line 97), which addresses why there's no *bypass*, not what an author
*does* when generation is legitimately blocked by environment rather than a bad spec.

**What it costs if shipped as planned.** g3 (role specs) and any future spec authoring both need a
`pytest`-importable interpreter resolvable to generate at all. In a plausible but not contrived
environment (a differently-provisioned sandbox, a crew dispatched without the dev host's exact
interpreter setup), the generator becomes unusable with no documented recovery — not a bug, but an
unstated operational gap in a tool meant to be run repeatedly by future authors.

**Smallest fix.** Name, in the plan, what an author does when generation refuses on
`.undecidable` for environment reasons (e.g., "install pytest under the resolved interpreter and
retry" as the *only* sanctioned path, stated explicitly) rather than leaving it to be discovered
live — and consider whether g2's close criteria should include a fixture that pins this exact
failure mode (probe cannot run at all) alongside the VIOLATING/INNOCENT/ACCEPTED_FALSE_ALARM set,
since right now nothing in the plan's close criteria would go red if this refusal path silently
regressed to a soft warning that still writes.

## MINOR

### M1 — g0's close criteria asserts against text describing the mechanism, not the mechanism

`CANDIDATE_PLAN.md:159` closes g0 on "the note exists and names, for each of the four defects, the
kind that forecloses it and the residual it does not" — a prose document asserting its own
correctness, checked by nothing except a later human/reviewer read. The plan is honest about this
(explicit crew-waiver, "no code ... for a reviewer to run"), so this isn't a hidden gap, but per the
lens: no command in this plan would go red if `DESIGN_NOTE.md`'s claims about what a kind
forecloses turned out to be wrong — that only surfaces downstream, if at all, when g1/g3 are built
against it. Similarly, g3's "every place the generated spine and the shipped template disagree is
written up as a finding" (`CANDIDATE_PLAN.md:162`) asserts a write-up exists, not that it is
complete — no command can distinguish "found every disagreement" from "found some."

### M2 — Single-fixture-pair probe demonstrations can't rule out a probe keyed to the literal example

The g2 close criteria commits to one VIOLATING and one INNOCENT fixture per probe
(`CANDIDATE_PLAN.md:161`, `166-171`). That's the right shape (borrowed faithfully from
`tests/test_mcp_adoption.py::_cli_only_verb_violations`, verified present and matching), but a
single example per side cannot distinguish "the AST scan genuinely parses `add_argument` calls"
from "the AST scan happens to string-match the one flag name used in the fixture." The
`ACCEPTED_FALSE_ALARM` bucket the corpus pattern uses is present in name but the plan doesn't
commit to populating it for the two oracle-less probes specifically — which is exactly where a
narrow, fixture-shaped implementation would hide.

### M3 — "Accepted by the pure `compile_spec` path" oversells what that half of the control shows

The framing at `CANDIDATE_PLAN.md:17-19` and the intro's "the same spec accepted by the pure emit
path and refused by the guarded CLI" implies `compile_spec` performs some acceptance judgment.
Per the stated order of operations (`CANDIDATE_PLAN.md:81-90`), `compile_spec` runs *before* the
spec-shape check, probes, and oracle call — it is pure translation with no rejection logic of its
own. The control is still real (it isolates the refusal to steps the CLI adds beyond translation),
but "accepted" is doing some work that "translation completes" would more honestly do. Purely a
wording finding; the plan's own inclusion of the corrected-and-accepted half of the pairing already
defends against the "guard is a no-op that always refuses" failure mode the lens asks about.

## Summary

The plan's central, most-tested mechanisms (the pure compiler at g1, the handback-renders-through-
`render_human` test, the `<repo-root>` anchoring claim, the three-way fixture borrowing) all checked
out against the real source — I could not find a command in this plan that was faked or a claim
about `checklist_engine.py`/`init_work_area.py` that didn't hold under direct execution. The
weaknesses are concentrated exactly where the plan itself flags risk: the two oracle-less probes
(S3, M2) and the undecidable-refuses-hard design (S4), plus one internal naming inconsistency (S1)
and one frame/plan mismatch on what's actually testable (S2). None of these are reasons to stop;
all four SERIOUS items are fixable in the gate table or close criteria before or during g2 without
touching the recommended design's shape.
