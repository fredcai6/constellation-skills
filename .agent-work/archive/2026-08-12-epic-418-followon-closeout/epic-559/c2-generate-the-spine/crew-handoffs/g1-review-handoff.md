# Reviewer Handoff — `g1` · the generator

**Work id:** `epic-559/c2-generate-the-spine` · **Gate:** `g1-review` · **Model:** Sonnet
**Dispatched by:** the Commander (delegated) under Admiral `admiral-epic-418-followon`.

You are a **cold** reviewer, independent of the implementer. You did not write this code and you must
not reconstruct the author's reasoning charitably.

## Read this first

**Last wave, three of six workstreams were blocked on first review and one was blocked twice. Two of
those blocks caught a fix that had FLIPPED its defect's sign — a gate that could not fail became one
that could not pass. Neither would have been caught by reading the diff. Both were found by RUNNING
something.** Run things. A review that only reads is not this review.

## What was implemented

`g1` of `epic-559/c2-generate-the-spine`: a spine generator. Two new files, nothing else touched:

- `scripts/generate_spine.py` — `CHECK_KINDS`, `spec_shape_faults`, `compile_condition`, `compile_spec`
  (pure), then the probes, the `validate_spine.validate()` call, the write, and `main()`.
- `tests/test_generate_spine.py` — 76 tests.

The implementer's own result, with its pasted evidence, findings, and the seven decisions it made where
the design note was silent:
`.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g1-implement-result.md`.

## The contract it was built to

`.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` — **frozen, and it is the spec.** Read it in
full before the diff. It gives the exact TOML fields, the exact compiled output per kind, the handback
contract, the claim escalation, the spec-shape faults, the CLI order and exit codes, and §10's table of
what each of the four historical defects forecloses and what it does not.

## How to inspect the diff

```
cd /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine
git status --porcelain
git diff --stat
git diff -- scripts/generate_spine.py tests/test_generate_spine.py
```

Nothing is committed yet, so the change is the working tree against `HEAD` (`0ab7ecab`).

## Task statement

Answer: **does this generator actually make the wrong check impossible to author, or does it only look
like it does?** That is the mission. Everything below serves it.

## Close criteria — verify each by running, not by reading

1. **The control pairing is real.** Re-run it yourself with your own spec, not the implementer's.
   Construct a spec the oracle would reject, confirm `compile_spec` translates it fine, confirm the CLI
   refuses it, and confirm **nothing was written** (`test ! -f <out>`). Then correct the same spec and
   confirm it is written. **Then ask the harder question the plan's own critic asked: would the pairing
   look identical if the guard were a no-op that always refuses?** Show that a good spec really is
   accepted, and that the refusal is caused by the oracle rather than by an unrelated early exit.
2. **`validate_spine.validate()` is the literal last statement before success**, imported and called —
   not re-implemented, not paraphrased. Confirm the oracle's fault text is printed verbatim.
3. **Purity.** `compile_spec` / `compile_condition` reach no `Path`, `open`, or `subprocess`. Prove it —
   do not eyeball it.
4. **All five kinds compile to exactly what DESIGN_NOTE §4 specifies.** Check the emitted `pytest`
   command against the corpus idiom character by character, including the `shlex.quote`ing of a selector
   containing spaces, and confirm `validate_spine`'s own `_pytest_segments` / `_selector` can read the
   emitted command back (that round trip is what stops the generator and the oracle disagreeing).
5. **Every emitted `command` check is anchored `cd <repo-root> && …`.**
6. **The `script` probe never imports its target.** Prove it: give it a target whose import-time code
   would raise or write a file, and confirm nothing happens.
7. **The handback contract renders through the real engine** and each of the three named verbs really
   lands where the contract says. Drive them yourself.
8. **The claim escalation is unconditional**, and the falsification-floor test genuinely goes red when
   the injection is removed. **Re-run the mutation yourself** — a floor test that passes whether or not
   the mutation landed is exactly the defect class this epic exists to find.
9. **Undecidable refuses, with nothing written, and there is no flag that skips it.** Search for an
   escape hatch; if you find one, that is a BLOCK.
10. **The guard fixtures are honest.** ≥2 VIOLATING, ≥2 INNOCENT, and a **populated**
    `ACCEPTED_FALSE_ALARM` for `script` and `population`. Ask of each probe: would this fixture pass if
    the probe were a string match on the one flag the fixture uses? The implementer's own feedback says
    it nearly shipped a false-alarm fixture built on an unmeasured assumption about `Path.glob` — check
    whether any other fixture rests on an unmeasured premise.
11. **No shipped template was edited**, `scripts/validate_spine.py` and `scripts/checklist_engine.py` are
    untouched, and `python scripts/validate_spine.py --sweep --root .` still reports **23** fault lines.
12. **The full suite passes** in the declared test mode.

## Constraints the change had to respect

- The engine's on-disk format does not change.
- The oracle's fault set and acceptance boundary do not move.
- No shipped template edited to make output validate.
- `ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH` and `_RESOLVER_OWNED_TOKEN_RE` are **imported**, never
  re-declared.
- Beliefs/concerns/open questions ride in `constraints`/`directives`, never a new field.

## The seven silent-spot decisions — judge them

The implementer recorded seven decisions where DESIGN_NOTE.md was silent (a tenth fault code, exit code
1 for malformed TOML, undecidable's exit code following the discovering layer, `directives.claim.note`,
omitting an empty `claims_rollup`, the population band-form shell text, argparse naming). Say for each
whether it is sound, and flag any that quietly changes the design note's meaning rather than filling a
gap in it.

## Test mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

`python`, not `python3` — on this host `python` has pytest importable and `python3` does not. Unsetting
the three spine variables matters: `scripts/mcp_spine_server.py` reads `SPINE_FILE` at import time.
Baseline before this change: **2689 passed, 3 skipped, 1121 subtests**. The implementer reports **2765
passed** after.

## Allowed scope

Read and run anything. **Write exactly one file: your result path below.** Do not fix what you find —
report it. Do not commit, do not push, do not run `scripts/install_constellation.py`.

## Stop conditions

Stop and report if the change requires moving `validate_spine.py`'s acceptance boundary, or if you
cannot run the suite.

## Return format

Write your `REVIEW_RESULT` to
`.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g1-review-result.md` **before you end your
turn** — that write is the delivery.

It must open with **`Verdict: APPROVE`** or **`Verdict: BLOCK`** on its own line, uppercase. Then: each
close criterion with the command you ran and its output; every finding ranked BLOCKING / SERIOUS /
MINOR with evidence; and a **Workflow Feedback** section naming where the handoff, the design note or
the tooling got in your way.

**BLOCK is not a failure of the run — it is the mechanism working.** Do not soften a finding to avoid
one. An APPROVE you cannot defend by something you ran is worse than a BLOCK.
