# Commander return — `C2: generate the spine from a spec instead of writing it by hand`

**Work id:** `epic-559/c2-generate-the-spine` · **Wave:** `w6-generator` · **Base:** `0ab7ecab`
**Branch:** `epic-559/c2-generate-the-spine` · **Commits:** `b406cc13`, `4333ff84`, `0b27b2b8` (+ the
reconcile commit) · **To:** Admiral `admiral-epic-418-followon`

---

## 1. Verdict

**Built, and it works — with two limits I can name precisely and one I could not have named without
this run breaking its own machinery.**

`scripts/generate_spine.py` compiles a TOML spec into the JSON `checklist_engine.py` already reads and
**refuses to emit anything `scripts/validate_spine.py` would reject** — `validate()` is imported and
called as the literal last statement before writing, never re-implemented. The spec has **no
raw-command field**: a check is one of five typed kinds (`qualitative`, `pytest`, `script`,
`population`, `artifact`), each carrying a generation-time probe, so extending what can be proven is a
code change with a test rather than a string typed into a spec.

`specs/implementer.spine.toml` (gated) and `specs/reviewer.spine.toml` (survey) are the first real role
specs. Both generate spines the oracle accepts with **zero undecidable**. A spine generated from the
implementer spec was dispatched with `run_crew.py --spine`, no handoff and no result path, and reached
a **terminal state** — both items complete, lease released, judged on `spine_terminal`.

**What holds:**

- The shipped `<exact test command>` placeholder becomes `selector = "..."` and a number. The
  shell-tokenization class of defect is **structurally unauthorable** — there is no shell-text field.
- Every generated gate carries a **handback contract** in `directives` naming `attach`,
  `flag-candidate` and `block` — the three channels the engine really persists — plus the recorded
  parent. Verified against behaviour: a reviewer drove all three verbs against a generated spine and
  each record landed where the contract says.
- On a **gated** gate, a large claim injects an escalation postcondition checking `review-result`
  matches `verdict: APPROVE`, and `advance()` genuinely refuses until it is attached.
- The shipped corpus is untouched: `--sweep` reports **23 fault lines before and after**, checked by an
  engine postcondition at every gate boundary.

**What does not hold, stated rather than rounded up:**

- **Property 2 is not enforceable on a `survey`.** `record()` evaluates only `command`-kind
  postconditions on a survey item and `consolidate()` reads only each item's `result` field, so an
  artifact postcondition is never consulted by either closing verb. A cold reviewer proved it by
  driving a generated survey to `APPROVE` with the escalation unsatisfied and nothing attached. The
  generator now **refuses to inject a postcondition the engine will never consult** and states the
  non-enforcement in the rendered gate instead.
- **The wrong-invocation class is narrowed, not closed** — see §4.
- **The generator cannot author a TDD-shaped plan at all.** A `pytest` check is probed by running
  `--collect-only`; a selector for a test that does not exist yet collects zero and the generator
  refuses. The shipped `IMPLEMENTER_PLAN.template.json` is instantiated *before* its test is written.
  Both role specs sidestepped this by pointing at tests that already existed. This is the first thing I
  would settle next.

**Not a manufactured success.** The single most useful thing this run produced is a defect **I**
authored, which the generator emitted and the oracle accepted (§4).

---

## 2. Evidence I personally ran

### Worktree isolation (required in this report)

```
$ python /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py \
    --here /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine
worktree OK: in /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine
exit=0
```

### The suite, in the declared test mode

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2788 passed, 3 skipped, 1121 subtests passed in 109.94s (0:01:49)
```

Baseline at `0ab7ecab` was **2689 passed / 3 skipped / 1121 subtests** — matching the launch order
exactly. **99 tests added.**

### The oracle, unmoved

```
$ python scripts/validate_spine.py --sweep --root .
sweep: 12 gated-or-survey templates discovered under .../skills
$ python scripts/validate_spine.py --sweep --root . | grep -cE '^  \['
23
```

23 before, 23 after. `git diff --stat main..HEAD -- 'skills/*/templates/*'` is empty.

### Every spine this run generated, judged by the oracle

```
$ python scripts/validate_spine.py \
    .agent-work/.../generated/implementer.spine.json \
    .agent-work/.../generated/reviewer.spine.json \
    .agent-work/.../dispatch-proof/spine.json --root .
.../generated/implementer.spine.json: OK
.../generated/reviewer.spine.json: OK
.../dispatch-proof/spine.json: OK
```

No `undecidable` line for any of the three.

### My own `execute.json`, before the generator existed

```
$ python scripts/validate_spine.py .agent-work/epic-559/c2-generate-the-spine/execute.json --root .
.agent-work/epic-559/c2-generate-the-spine/execute.json: OK
```

Zero faults, zero undecidable — where **nine of twelve shipped templates** carry `falsifiable-all-null`.
It also carries the handback contract on every gate: the smallest honest dogfood available before the
generator existed.

### The run packet

```
$ python .../verify_iterative_role_artifacts.py commander --work-id epic-559/c2-generate-the-spine
iterative role artifact ok: commander (epic-559/c2-generate-the-spine)
```

Six discrepancies, each classified; **none auto-filed**.

### The dispatch proof, read from the spine the dispatch actually drove

```
items: [('m0-context', 'complete'), ('m1', 'complete')]
lease: released
registry: status=completed, completed_at set, result=None   # judged on spine_terminal
```

---

## 3. The control — accepted before the guard, refused after

The mission asks for the pairing, not the refusal alone. Run just now, with a spec I wrote for this
report (not a crew's fixture). Both halves use the **same** spec; only one token differs.

**A. The pure translation path — no guard — completes without complaint:**

```
$ python -c "... gs.spec_shape_faults(spec, repo_root=ROOT) ... gs.compile_spec(spec) ..."
spec_shape_faults: []
translation completes -> cd <repo-root> && python scripts/validate_spine.py --root '<not-a-resolver-token>'
```

**B. The guarded path refuses the same spec, and writes nothing:**

```
$ python scripts/generate_spine.py bad.spine.toml --out out.json --root $R
oracle refused: 1
  [falsifiable-unresolved-placeholder] m1.postconditions.c1: command still carries the literal
  placeholder '<not-a-resolver-token>' -- nothing resolves it, so the check can never run, let alone fail
exit=4
$ test ! -f out.json  ->  CONFIRMED: nothing written
```

**C. The same spec corrected is accepted and written:**

```
$ python scripts/generate_spine.py good.spine.toml --out out.json --root $R
wrote out.json
exit=0
$ test -f out.json  ->  CONFIRMED: written
```

Note the wording deliberately: `compile_spec` **translates**; it does not judge. The refusal comes from
the oracle — its own `str(fault)` printed verbatim, never paraphrased — and C is what proves the guard
is not a no-op that always refuses. The `g1` reviewer built a third, independent pairing and reached
the same conclusion by a different route: the fault code belongs to the oracle's `falsifiable-*` family,
disjoint from the generator's own `probe-*` names.

---

## 4. The settling question, answered without softening

> **Does the role spec still ask its author to type a shell command from memory?**

**No. And the defect it was hiding did not go away — it got smaller, and I can now say exactly where it
lives, because I authored it.**

**Closed structurally.** No shell-text field exists, so defect 1 (`-k Door or Tie or Registry` split by
the shell) cannot be authored. Defects 2 and 4 (zero-collect, wrong population) are closed by probes
that *run the thing* and refuse on the number.

**Narrowed.** The `script` probe checks that every `--flag` the author named exists in the target's
`add_argument` literals, and — after `g3` — that every path-shaped positional argument exists unless it
carries a resolver-owned token. The positional half exists **only** because the `g2` crew reported its
absence as a residual instead of claiming a clean sweep.

**Not closed, and here is the proof.** The probe verifies flags the author **named**. It cannot see a
**required** flag the author **failed to name**. I wrote this check into this run's own dispatch-proof
spec:

```toml
kind = "script"
path = "scripts/generate_spine.py"
args = ["specs/reviewer.spine.toml", "--check-only", "--root", "."]
```

`--out` is missing, and argparse marks it `required=True` unconditionally — `--check-only` skips the
*write*, not the CLI's own argument parsing. **The generator emitted it. The oracle accepted it.** The
check exited 2 on `the following arguments are required: --out` before a spec was ever opened, and
could never have passed. It was found by a real dispatch, by a crew that **blocked** rather than
forcing its gate.

So: the shell-tokenization class is gone; the wrong-invocation class moved from *silent and downstream*
to *loud and at generation time* for flags an author names, and is **untouched** for the ones they
forget. The mechanism to close it exists — read the target's parser for `required=True` arguments — and
is in the run packet as forecast `U-required-flag-probe`.

**And what the dispatch proof does not establish.** The `g3` reviewer put this better than I had:
`spine_terminal` is a **purely structural** predicate. A spine authored with only `qualitative`
postconditions could reach it on a crew's attestation alone — *that* would be a check that cannot fail.
This proof is real because *this* spine gated its substantive postcondition behind a `command` check the
engine runs itself by subprocess (evidence stamped `produced_by: engine`), requiring twelve real tests
to exist and pass. **Protected intent #4 is proven for this dispatch, not as a property of the
completion contract.**

---

## 5. Map impact

`python -m scripts.code_map build --root .` run **twice**, because adding `scripts/generate_spine.py`
and then extending it each changed the module and entity counts (**56 → 57 modules, 1113 → 1134
entities**, then again). Both times the staleness surfaced as a red test, and the first time a crew
reasonably — but wrongly — judged it pre-existing: it stashed its own changes, saw the failure persist,
and concluded the cause was not in this run. It was: `g1`'s commit was already underneath. *"It
reproduces with my changes stashed"* proves the cause is not in your diff, **not** that it is not in
this run.

`docs/CHECKLIST_SCHEMA.md` gained a **"Who writes a checklist"** section: the format is unchanged and now
has its first *producer*, plus the three engine behaviours this run measured whose consequences the
document did not draw — no artifact-based gate can be enforced on a survey; `config_ref` crashes the
engine when it exists but is not JSON; a `command` check receives no `cwd`.

`docs/agents/*` is untouched. No Cartographer was dispatched: this repo has **no packet map**
(`map_orient` → `DEGRADED-UNPARSEABLE`), which the reconcile step names as the case for direct
reconciliation.

---

## 6. Triage candidates — routed to you, not filed

**No issues were created.** The launch order withheld that authority explicitly, so all six land as
`recommend-and-defer`. Issue-ready recommendations, each with observations carrying conditions, `type`
and `rev`, are at `.agent-work/epic-559/c2-generate-the-spine/triage-candidates/RECOMMENDATIONS.md`. I
checked each against the fix-now ladder rather than defaulting; `tc2` and `tc5` are small enough to be
tempting and both fail two rungs.

| id | what | priority |
|---|---|---|
| **tc1** | A Commander **cannot drive its own `execute.json` through the door.** `mcp_spine_server.py` binds one file at import time with no per-call addressing, while the Commander spine's `execute` step requires driving a second checklist. | high |
| **tc2** | `recover_crews.py` **misclassifies a completed spine-only dispatch as `NEEDS-ABANDON`** — its classifier keys on a result artifact such a crew deliberately never writes. This is precisely the duplication the tool exists to prevent. | high |
| **tc3** | `load_config` **crashes** with an unhandled `JSONDecodeError` on a `config_ref` that exists but is not JSON; `validate_spine.py` has no fault for it. | medium |
| **tc4** | This repo ships `map/INDEX.md` as an unfilled template and `map/ids.jsonl` empty, so **every** Commander here is structurally DEGRADED. | medium |
| **tc5** | `REVIEW_SURVEY.template.json`'s `r6-fowler` carries an unsubstituted `<work-id>`; a hand-built reviewer survey must `retext-check` it before the Fowler script can be found. Hit independently by **two** of my reviewers. | medium |
| **tc6** | A dispatched crew **inherits its dispatcher's `SPINE_FILE`** — both my reviewers found *the Commander's own spine* bound in their environment. Only their own doctrine stopped them driving it. | medium |

### Floats — decisions beyond my latitude

1. **The engine binds no provenance to evidence.** `attach()` takes no authority and stamps
   `produced_by: "engine"` for every caller, while `waive()` refuses an empty one. Every
   `artifact`/`user-decision` human checkpoint in the corpus — **including the four in the Commander
   spine I just drove** — is satisfiable by the agent it is meant to check. A cold critic closed one in
   two in-process calls. I raised the bar as far as a generator can; closing it is a
   `checklist_engine.py` change.
2. **`record`/`consolidate` never evaluate artifact-kind postconditions on a survey.** No artifact-based
   gate can be enforced on any survey in this corpus. Any future wave migrating reviewer or interrogator
   templates must plan around it, or the engine changes first.
3. **tc1**, above.

### The four `<engine>` tokens: I decided **not** to fix them, and the reason is not scope

Inherited latitude made it my call. The tokens are unresolvable, so today they are **visibly** broken —
an agent that reads one knows something is wrong and goes looking, which is how I found float 3.
Substituting them would make the instruction *readable* while the underlying defect — the door cannot
address a second spine — stayed exactly where it is. That converts a loud defect into a quiet one,
which is the escape-hatch shape this epic exists to find.

**Recommendation: fix the door first, then remove the four tokens in the same change.** Fixing the
tokens alone would be worse than leaving them.

---

## 7. Workflow feedback

**Where the process earned its cost.**

- **The cold-review BLOCK was the highest-value event of the run**, and it was found by *driving* the
  engine, not reading the diff — the third wave running where that is true. It caught one of the two
  non-optional properties being silently inert on every survey-type role spec. No amount of reading the
  emitted JSON would have shown it.
- **The three-lens critic panel changed the plan materially** *before* any crew ran: it deleted an
  unwritable field design, re-pointed the escalation, merged two gates, cut two check kinds and one
  module. Two of its findings were BLOCKING and both came from running code against my plan's claims.
  A panel is expensive; this one paid.
- **The blocked gate + recorded parent + polling parent path worked exactly as E1 predicted.** No
  message was needed or attempted.

**Where it got in my way.**

- **The door cannot drive `execute.json`** (tc1). The Commander spine's own `execute` step instructs
  something the door cannot do, so the most-driven checklist in the corpus is necessarily CLI-driven.
- **Driving the engine through a shell is a hazard the door does not have.** My `advance --why` text
  contained backticks; bash ate the clause as command substitution and the recorded `why` lost a phrase.
  A door tool takes a JSON string and cannot do that. Small, but it is *exactly* the "shell mangles your
  text" class this mission is about, hitting the mission itself.
- **`recover_crews.py` told me to abandon a finished crew** (tc2). I only noticed because I read the
  registry directly. A less suspicious Commander redispatches.
- **The map-staleness trap fired twice** and is invisible at authoring time. Nothing in any crew handoff
  says "if you add or change a module, regenerate `map/INDEX.md`". Both crews met it as a mystery red
  test. **Suggestion:** name it in the implementer handoff template's Deliverable Path Check.
- **`docs/agents/engine-config.json` does not exist**, yet the Commander spine's `context` imperative
  names it as a project delta and every shipped template points `config_ref` at it. Harmless only
  because a *missing* path falls through; an *existing* non-JSON one crashes the engine (tc3).
- **A reasoning gate's close criteria assert arrival, not correctness**, and the testability critic was
  right that this is a real gap. I mitigated it by machine-pinning `DESIGN_NOTE.md`'s kind list against
  the compiler's own constant one gate later, and said so in the gate rather than dressing it up.

**One thing I would tell the next Commander.** The launch order's instruction to *verify claimed
side-effects against the world* paid for itself twice in one run, and both times the crew's report was
honest and its **inference** was wrong: "the failure reproduces with my changes stashed" and "the
escalation is injected, here is the JSON". Both were true statements. Neither was the question.
