# Cold plan critic — findings and disposition (issue #304)

Cold critic read `execute.json` + `MISSION_FRAME.md` only, with no authoring context. Verdict:
**do not approve — 5 BLOCKERs.**

**Every checkable finding was independently re-verified by the Commander before disposition.** The
critic was right on all of them, including two that corrected the Commander's own reported numbers.

Per doctrine, findings are **triaged by the human, every one**. In delegated mode the Admiral holds
that role; the dispositions below are proposed and the two marked **FLOAT** are not taken unilaterally.

## Verified by re-running / re-reading, not accepted on assertion

| # | sev | finding | verification | verdict |
|---|---|---|---|---|
| 1 | BLOCKER | g3's close command passes green on the untouched tree | ran it at HEAD: `262 passed, 1 skipped, 1144 deselected`, **exit 0** | **TRUE** |
| 5 | BLOCKER | episode store cannot carry a predictive tripwire or record an outcome | `AGENT_SUPPLIED_KINDS` requires all five incl. `observed-behavior` (`create` refuses otherwise, :900-909); `amend-assertion` changes **only** `lifecycle_standing` (:1215) | **TRUE, and worse than stated** |
| 6 | MAJOR | `"no docs/agents/ overlay at all"` occurs **twice**, one load-bearing | `imp.count(...) == 2`; first occurrence is the substitute-and-record rule | **TRUE** |
| 7 | MAJOR | word counts wrong | measured full deletable block: **86 words each, 172 total** | **TRUE — my number was wrong** |
| 10 | MAJOR | the `<repo-root>` premise is a non-sequitur | 5 shipped command checks use relative paths (`--file .agent-work/LESSONS.md`) and work | **TRUE as stated** |

### Finding 1 — the #300 defect, reproduced inside the gate that exists to answer #300

The `-k 'map_orient or template or install or episode'` disjunction is satisfied by pre-existing green
tests in files g3 never touches. The gate's `c1` statement asserts five properties; the command can
falsify **none** of them. This is precisely "a check that cannot fail is indistinguishable from one
that passed" — and I wrote it while holding that finding in the launch order in front of me.

**Disposition: FIX.** Every close command names explicit test files, including at least one file the
gate itself must create (a missing file exits 4, so the gate goes red until the work is done), and the
final gate runs the **full suite**.

### Finding 7 — correcting a number I already reported upward

My earlier extraction counted only sentences literally containing `engine-config`, silently dropping
the trailing sentence of each block. The **substance** of the correction to the launch order stands and
is unaffected: **2 templates, not 11**. The magnitude changes: **172 words, not 112**. Still nowhere
near "several hundred words on every shipped template."

Method lesson, and it is the launch order's own: *derive distribution claims from a command.* I did —
but the command encoded my assumption about sentence boundaries, so it inherited the error. A command
is only as good as its predicate.

### Finding 5 — FLOAT: a settled pre-ruling whose stated rationale is falsified by the code

`decision:tripwires-are-episodes` is graded `settled/human`, justified in the order as:

> "the episode record already carries a prediction and an outcome slot, which is exactly the
> deletion-plus-run pathway's shape."

The code says otherwise:

1. `create` requires **all five** agent-supplied kinds, including `observed-behavior`. A prediction
   filed *before* the deletion has no observed behavior — you must fabricate one at file time, which
   is exactly the "prediction written after the outcome" the pathway forbids.
2. `amend-assertion` changes **only** `lifecycle-standing`, plus one appended history line.
   `kind`/`strength`/`statement` are left exactly as parsed.
3. **`LIFECYCLE_STANDINGS = ("active", "disputed", "superseded", "rejected")` — there is no
   `confirmed`.** A tripwire that was checked and **held** is indistinguishable from one that was
   **never checked**: both sit at `active`.

Point 3 is the #265 lesson recurring inside the mechanism a pre-ruling mandates: *a non-reading must be
visibly distinct from a low reading.* Here a held prediction is invisible against an unchecked one.

The **ruling** (episodes, not `LESSONS.md`) may well still be right — `LESSONS.md` is at its 20/20 cap
and has no outcome field either. It is the **rationale** that is falsified, and the mechanism therefore
needs a decision.

**Proposed (not taken): pre-registration by commit.** Write the predictions into a committed
`TRIPWIRES.md` **before** the deletion commit. Git's own history is the timestamp proof — tamper-evident,
requires no clock (the episode writer is deliberately clock-free), and is *stronger* than anything the
store offers. Then, after running the affected workflows, file each episode with `expected-behavior` =
the pre-registered prediction and `observed-behavior` = what actually happened, citing the
pre-registration commit SHA. This uses the store exactly as built and never fabricates an observation.

The alternative — adding `confirmed` to `LIFECYCLE_STANDINGS` — is a change to #301's shipped store,
which another commander owns. **Not mine to take.**

## Remaining dispositions

| # | sev | disposition |
|---|---|---|
| 2 | BLOCKER | **FIX** — disambiguate: `verify-orientation` at **context**, `verify-frame` at **plan**. The original imperative's "wire it into … context … and a plan-step frame check" was genuinely ambiguous and the cheap resolution would have destroyed the anti-vacuity property. |
| 3 | BLOCKER | **FIX** — add a gate check that *runs* the mutation and asserts red. Falsifiability must not be self-attested by the party being graded. |
| 4 | BLOCKER | **FIX** — the degraded (common-case) oracle was weaker than the resolved one. Substitutes must be recorded at context and **hash-pinned**, so the frame check compares against a committed prior declaration rather than a same-breath assertion. |
| 8 | MAJOR | **FIX** — name the pinning tests (`test_context_manifest`, `test_context_declaration_lint`, `test_context_determinism`, `test_init_work_area`) in the gates that modify what they pin. |
| 9 | MAJOR | **FIX** — add a closeout gate running the full suite; merge still gates on the CI exit code read at source. |
| 10 | MAJOR | **FIX the justification, keep the change, and file the bug.** Relative checks work *because* they inherit the launcher's cwd, which is the repo root in the normal case — they are fragile, not broken. `<repo-root>` is a real robustness fix; the plan's stated premise was wrong. The fragility of the 5 shipped relative checks is a **separate defect** → triage. |
| 11 | MAJOR | **FIX** — specify the run concretely: which workflow, which repo, what artifact records it, what "outcome recorded" looks like on disk. |
| 12 | MAJOR | **FIX** — add a dogfood gate: materialize the edited spine via `init_work_area.py` and run the new checks end-to-end **in this repo**, which is itself the degraded common case. Free, and the highest-value integration test available. |
| 13 | MINOR | **FIX** — exit codes 1/2 collide with argparse (2) and tracebacks (1); the engine can also synthesize 127. Move the semantic vocabulary above the collision range. |
| 14 | MINOR | **PARTIAL** — the trend snapshot is a launch-order deliverable and stays, but gains a location, a schema, and a check. `verify-orientation` gains its wiring (it was built-but-unwired). |
| 15 | MINOR | **ACCEPT with a stated exception** — `e0-context.c1` is `check: null` by engine convention. |

## On the critic's judgement of the mission frame

It called the frame's DEGRADED self-report **decorative** — a confession that changes no gate — and it
was right. Disposition: the banner now does real work or it goes. Finding 4's fix (hash-pinned
substitutes declared at context) is what converts it from a banner into a control.
