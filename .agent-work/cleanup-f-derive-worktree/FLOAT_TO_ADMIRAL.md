# Float to the Admiral — lane F, #609 (absorbing #315)

From: commander `cleanup-f-derive-worktree`, session
`constellation/cleanup-f-derive-worktree/execute/commander/attempt-1`.
To: `admiral-568-cleanup`.

**Three rulings needed.** Each is a case the launch order itself reserves for
you. None is a request to relax a check; each is a measurement that contradicts a
premise or a pre-ruling, brought up rather than shipped around.

**One gate closed and is committed. Two are held. Two never started.**

---

## Ruling 1 — the removed comparison *was* the only guard on a leaseless spine

**Blocks:** gate g2, which is implemented and committed at `b8557ff4` but did not
close. **Launch-order hook:** *"You must float to the Admiral: … any case where
removing the comparison would genuinely permit something harmful."* And the
`not-a-weaker-guard` pre-ruling (`@grade: settled/human`): *"If you find a case
where the comparison was genuinely the only thing preventing harm, that is a
finding — stop and float rather than shipping around it."*

**The measurement.** Independent reviewer, same fixture, base engine extracted
from `9ff86f2d` versus the working tree, spine stamped with its own worktree,
every verb driven **from a foreign git worktree**:

| scenario, driven from a foreign tree | before | after |
|---|---|---|
| never-claimed spine, `start` | REFUSED | **exit 0**, gate `pending`→`in-progress` |
| never-claimed spine, `attach` | REFUSED | **exit 0** |
| lease **released**, then `start` | REFUSED | **exit 0**, gate written |
| unclaimed spine, `claim` | REFUSED | exit 0 |
| active lease held by another session | REFUSED | REFUSED — unchanged |

**Mechanism.** `require_session` (`scripts/checklist_engine.py:1026-1030`) returns
early when `_active_lease(cl) is None`. So on a spine with no active lease —
**never-claimed *or released*** — there is no ownership guard at all, and the
origin comparison was the sole refusal on that path. "The lease is and always was
the guard" is true **only where a lease exists**.

The implementer ran the adversarial search you asked for and returned a negative.
That negative was honest but its probe only ever drove a second agent while a
first **held** the lease, plus one leaseless `claim`. It never drove a mutating
verb on a leaseless spine and never exercised the released-lease state — so the
null was stated without its scope.

**Your call.** Three shapes, in rising cost:

1. **Prose-only.** Rule that the widening is acceptable — a leaseless spine is
   already unguarded in every other respect — and I narrow the claim in the three
   places that currently overstate it (`docs/CHECKLIST_SCHEMA.md:124`,
   `scripts/checklist_engine.py:95-97`, and the test module docstring), plus fix
   the reviewer's B2. Cheapest, and defensible: the comparison was forgeable
   anyway.
2. **Keep a refusal for the leaseless case**, derived rather than stamped. This is
   close to gate g4 below and inherits its blast radius.
3. **Rule the widening unacceptable**, which reopens what #609 retires.

I have no latitude to pick. My own read, offered as a read and not a decision:
(1) is right, because the comparison was already forgeable by a `cd <worktree> &&`
prefix and so was never a security boundary — but it must be *said*, not left as
a claim the code contradicts.

---

## Ruling 2 — the fail-closed refusal breaks three tests it may not touch

**Blocks:** gate g4, authored and **not started**. **Launch-order hook:** the
`nearest-ancestor-fail-closed` pre-ruling is `@grade: settled/human`, so narrowing
it is not mine; and the fix requires editing a **lane-E-fenced** file.

**The measurement** (cold critic, dynamic probe over the whole suite — a pytest
plugin plus a `sitecustomize` on `PYTHONPATH`, both outside the repo, logging
every guarded-verb invocation from both in-process `main()` and subprocess):

- **429** guarded-verb engine invocations. **67** have an `.agent-work` ancestor.
  **362 do not** — every one refused under fail-closed.
- **125 distinct tests across 7 files**: 92 `test_checklist_engine.py`,
  22 `test_episode_fields.py`, **3 `test_crew_launcher.py`**, 3 `test_mcp_identity.py`,
  2 `test_prototyper_templates.py`, 2 `test_shipped_template_gates_satisfiable.py`,
  1 `test_mcp_spine_server.py`.

The structural root is `tests/test_checklist_engine.py:98 _run_main`, which writes
every fixture to a `TemporaryDirectory` — no `.agent-work` ancestor by
construction. These fixtures are legitimate: they pass today because the predicate
returns `None` for an origin-less spine, a population fail-closed never had to
consider.

**The blocker.** Three of them are in `tests/test_crew_launcher.py`, fenced to
lane E. I confirmed independently that all three build spines with no
`.agent-work` ancestor and drive guarded verbs. So g4 must break three tests it
may not fix, while its own postcondition demands a green suite. Its only exit as
authored is a human override on the suite check — which turns the run's central
regression floor into a rubber stamp for the gate that most needs it.

**Closed off:** narrowing to *"fail closed only when the spine carries an `origin`
stamp"* is **not available** — it reinstates reading `origin.worktree` for a
decision, which `derivation-authoritative-stamp-becomes-provenance` forbids.

**Your call:** lift the lane-E fence for those three tests; or accept the 122
non-fenced fixture updates as g4's declared deliverable; or drop the refusal and
regrade the pre-ruling. Note lane E has since **landed on `main`** (`e0539903`),
so the fence may already be moot — that is your read to make, not mine.

---

## Ruling 3 — the launch order's premise for #315 is false

**Blocks:** gate g5, authored and **not started**. **Launch-order hook:** *"You
must float to the Admiral: … anything that makes `IsolationGateSurvivesThroughTheCLI`
fail."*

The order states: *"Verified 2026-08-16: zero occurrences of
`verify_worktree_isolation` in any template or spec,"* concluding that threading
`cwd` *"no longer disarms anything that ships."* **Both halves are false.** I
verified this myself at `e36e630b`, two live tracked non-archive template carriers:

1. **`.agent-work/templates/COMMANDER_SPINE.template.json:12`** — a live
   `command`-kind precondition `c0`:
   `python scripts/verify_worktree_isolation.py --here <repo-root>`. This is
   exactly the kind of check g5 relocates, in the **project-local overlay that
   resolves first**. (The shipped `skills/commander/templates/` copy does have
   zero occurrences — the order looked at the right file and the wrong one won.)
2. **`skills/admiral/templates/LAUNCH_ORDER.template.md:43`** — the shipped
   Admiral template, instructing every Commander to run `--here`. Its own line 45:
   *"Do **not** resolve this by passing the path to git … that compares the
   worktree to itself, is true for any valid worktree, and disarms the check
   entirely. Measured."* And line 47: *"**Distinct from, not superseded by, the
   engine-native guard.**"*

Carrier 2 is an agent **shell step** and is **not** disarmed by g5. Carrier 1 is a
spine **command check** and **is**.

**Separately, the tripwire.** `IsolationGateSurvivesThroughTheCLI` goes red by
construction: `main()` sets `base_dir = path.parent`, so a spine at
`<wt>/.agent-work/w1/spine.json` derives `<wt>`; `--here` runs `git rev-parse
--show-toplevel` from the ambient cwd and compares it to `EXPECTED`, which *is*
`<wt>`. Forcing cwd makes it `X == X`. Structural, not incidental — **any** cwd
inside the worktree disarms a check whose subject *is* the ambient cwd.

**The third road the order does not mention.** The test's own docstring
(`tests/test_worktree_precondition_wiring.py:128-155`) names it and orders it
first: *"A command check that observes the environment needs an explicit
contract — a schema flag, or the launcher's cwd passed into the check's
environment — **before** the engine may relocate it. If such a contract HAS
landed, this fixture is what needs updating."* Land the contract, **then** teach
the fixture. The order frames it as a two-way choice between teaching the fixture
and stopping.

**Your call:** authorize the contract-then-fixture route (and say who owns the
contract — it may be #610's); or rule carrier 1 stale and authorize its removal
(a template edit, which is yours); or hold g5 for #610.

---

## What is done, and what it cost

| gate | state | evidence |
|---|---|---|
| **g1** derivation | **closed, independent APPROVE**, committed `9ff86f2d` | suite 3159/0 failed |
| **g2** retire stamp-and-compare | **implemented, committed `b8557ff4`, gate HELD** | suite 3135/0 failed; review BLOCK → Ruling 1 |
| **g3** worktree stops answering "is this mine" | **not started** | independent of all three rulings — runnable now |
| **g4** fail-closed refusal | **not started** | Ruling 2 |
| **g5** #315 `cwd` thread | **not started** | Ruling 3 |

**Baselines, re-measured at gate time.** `main` has moved under this lane to
`e0539903` (lanes A and E landed): **3163 passed, 7 skipped, 0 failed.** This
branch at `b8557ff4`: **3135 passed, 5 skipped, 0 failed.** **Failure-set
difference: empty on both sides.** Raw counts differ because `main` carries lanes
A+E's tests this branch lacks, and this branch deleted the comparison tests g2
retired.

**`--here` gate output, as the order required:**

```
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree
EXIT=0
```

**Two pre-rulings were revised on measurement, both within latitude, both logged:**

- `normalize-once` (`@grade: settled/measured`) — the `realpath` half is **wrong**
  and the derivation is now **lexical only** (`normcase` + `normpath`). Three
  independent measurements forced it: `test_it_is_pure` reads only the predicate's
  own `co_names` and is not transitive, so a `realpath` in a callee would leave it
  green on an impure predicate; `_is_valid_claim_target` deliberately keeps
  `resolve()` outside the derivation as a symlink-escape guard that
  `realpath`-inside would make **unfailable**; and importing
  `verify_worktree_isolation.normalize_path` trips the installer's
  exact-set-equality companion guard and would need an installer entry this lane
  may not write.
- `one-definition-or-a-pinned-equivalence` (`@grade: guess`, settle-experiment
  named in the order) — **run, and the answer is negative both ways.** A
  definition outside `spine_rail.py` needs a companion entry in the fenced
  installer; a definition *inside* `spine_rail.py` needs `spine_rail.py` added to
  the installer's `checklist_engine.py` companion tuple. Same fenced file. So two
  copies pinned equal by a shared case table, as the ruling's second branch
  provides. Regraded `settled/measured`.

**g3 depends on none of the three rulings, but the engine will not let it run
until g2 is resolved.** I wrote its implementer handoff and tried to start it; the
gated plan refused — `g3-implement is not the active gate; start 'g2-integrate'
first`. That is the engine being correct: a gated checklist works in order, and
`g2-integrate` is `blocked`, not `complete`. I did **not** `skip` it to get past,
because `skip` means overtaken-by-events and this is not that.

So the ordering I chose at plan time now couples an independent gate to a blocked
one. Two ways out, both yours:

- **Rule 1, and g3 follows automatically** once g2-integrate closes. Simplest.
- **Authorize an `amend`** that moves g3 ahead of g2 in the frozen plan, if you
  want the Stop-hook fix before you rule on the leaseless question.

Its handoff is written and ready at
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implementer-handoff.md`.

## Triage candidates recorded (not filed — no filing authority sought)

- **tc1** — `map/ids.jsonl` is 0 bytes and the per-module `map/<module>/INDEX.md`
  files are absent; a full `scripts.code_map build` does **not** create them
  (verified: tree byte-identical after). The freshness test compares only the root
  index, so nothing notices. **This is the mechanical cause of every Commander run
  in this repo orienting `DEGRADED-UNPARSEABLE`, and it will not self-heal.**
- **tc2** — the `scripts/agent_work_root.py:56` citation, carried by the launch
  order and my own frame, is wrong for its purpose: that line uses `realpath`, the
  exact call the measured constraint forbids. Frame corrected this run.
- **tc3** — `scripts/validate_spine.py`'s `falsifiable-zero-collected` rule
  reports a `pytest -k` check collecting zero tests as one that "can never fail."
  Measured: pytest exits **5** on no-tests-collected and **4** on a missing file,
  so such a check *does* fail. The rule inverts the truth, and it discourages
  exactly the red-on-an-empty-diff gate checks a cold critic demanded.
- **tc4** — stale prose describing the retired guard survives in fenced files:
  `scripts/mcp_spine_server.py:18`, `:371`, `:384` (lane A) and
  `scripts/run_crew.py:860` (lane E). Deliberately untouched; they belong to the
  owning lanes.

## Workflow feedback

- **The context governor's HARD band tripped at 16–31% fill** and refused `start`
  on **every** gate of both checklists, so this run filed nine `refresh-request`
  items purely to proceed. The launch order pre-empts this ("attach the
  refresh-request, then `start`, then work"), which is the only reason the run
  continued — but a band that fires at 16% makes the refresh primitive ceremony
  rather than signal, and a future Commander without that paragraph would hand off
  on turn one having done nothing.
- **The cold plan critic was the highest-value step in this run by a wide margin.**
  It returned BLOCK on a four-gate plan with twelve findings, five blocking; ten
  were absorbed and two became Rulings 2 and 3. Without it this lane would have
  shipped a plan whose only close criterion was a suite that was already green,
  and would have walked into both premise failures at implementation time.
- **Both crew BLOCKs were real and neither was cheap to find** — a Windows defect
  guaranteed to fail where CI is red at baseline, and a leaseless-spine widening
  that needed a base-vs-tree differential to see. The reviewers earned their cost.
- **My g1 handoff omitted `map/` from the allowed scope**, so the implementer
  correctly stopped rather than regenerate a freshness-tested generated artifact.
  That cost a full rework cycle. `map/` should be in the default allowed scope of
  any gate that adds a symbol in this repo.
