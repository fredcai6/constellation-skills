# REVIEW_RESULT — cold plan critic

Verdict: BLOCK

Read: `MISSION_FRAME.md` and `execute.json` only, plus repository source to check
their claims. Tree at `e36e630b` (confirmed HEAD). Baseline measured, not
assumed: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`
→ **3104 passed, 6 skipped, 1165 subtests passed in 123.69s**. The plan's own
integrate command runs and is green today.

Five findings must be fixed before this plan freezes. Two of them (F1, F4) mean
a gate cannot close on its own terms; one (F5) means a gate's justification
rests on a claim that is false.

---

## Findings

### F1 — blocking — testability — no gate has a close criterion that its own deliverable can fail

Each of the four gates closes on exactly two machine checks: a `command` check
running the whole suite, and an `artifact` check that a reviewer said APPROVE.
The suite check is byte-identical in the healthy world and in the world where
the gate did nothing, because the suite is green at baseline. The reviewer check
is an agent attestation, not a reading of the world.

Evidence: baseline run above is green with zero of this plan's work applied.
Every `gN-integrate.c1` therefore passes on an empty diff.

The handoff asks whether the whole-suite postcondition is the right check. It is
a regression floor and a good one. It is not a close criterion, and this plan
has nothing else. Nothing in `execute.json` would go red if an implementer
returned an empty diff and a reviewer wrote APPROVE.

What I would change: give each gate one cheap falsifiable check on the thing it
ships, alongside the suite. They are all one-liners against the tree —
g1: the new equivalence test file exists and passes by name; g2:
`! git grep -qn 'rev-parse --show-toplevel' scripts/checklist_engine.py`;
g3: the new #549-shape test passes by name; g4: the #315 repro test passes by
name. Without these the plan is unfalsifiable end to end.

### F2 — blocking — testability — g2 names an enforcer that cannot detect the impurity g1 introduces

`g2-implement.anchors.constraint` states: *"the predicate must stay PURE -- no
filesystem ... (`tests/test_spine_origin_isolation.py::test_it_is_pure`
enforces it)"*. That test reads names off the compiled code object
(`tests/test_spine_origin_isolation.py:299`):

```python
names = set(self.E.origin_worktree_refusal.__code__.co_names)
for forbidden in ("cwd", "getcwd", "subprocess", "run", "open", "exists",
                  "resolve", "read_text", "write_text", ...):
    self.assertNotIn(forbidden, names, ...)
```

`co_names` is **not transitive**. Under this plan the predicate stops comparing
and answers from g1's derivation, and g1's derivation normalizes with
`realpath` — a filesystem call. The predicate's own `co_names` would then hold
only the derivation function's name. `test_it_is_pure` stays green while the
predicate becomes impure. Healthy world and defective world, identical output.
That is exactly the shape the handoff asked me to hunt for, and unlike g4's
collision the plan does not know about this one.

Underneath it is a three-way contradiction the plan never resolves:

- g1 requires `realpath + normcase` at the derivation boundary;
- g2 requires the predicate to be pure, no filesystem;
- g2 requires the predicate to answer from that derivation.

All three cannot hold. An implementer will pick one silently. What I would
change: rule it explicitly — the derivation the predicate consumes is
**lexical only** (`normcase`, `normpath`, no `realpath`), with any
symlink resolution kept outside the predicate as it is today — and either widen
`test_it_is_pure` to walk the callee or add a direct test that the predicate
touches no filesystem.

### F3 — blocking — intent-fit — g1's "No consumer is rewired in this gate" is false, and g1 breaks an existing test

`g1-implement` generalizes `scripts/hooks/spine_rail.py:712 _worktree_from_spine`
and asserts no consumer is rewired. No call site is *edited*; every call site's
behaviour *changes*. `_worktree_from_spine` has five call sites, of which the
plan names none:

- `spine_rail.py:1117` and `:1122` — inside `_is_valid_claim_target`
- `spine_rail.py:1169` — the door `claim` path
- `spine_rail.py:1274` — the CLI `claim` path
- `spine_rail.py:1565` — `decide_session_start`

Widening the accepted shape widens what the hook accepts as a claimable spine.
That is a behaviour change to the ownership gate, delivered by a gate that says
it changes no behaviour and whose only machine check is the full suite.

It also goes red. `tests/test_spine_rail.py:874`
(`test_worktree_from_spine_accepts_only_absolute_agent_work_json_layout`) pins
the narrow shape. I ran g1's stated rule against that test's own `malformed`
tuple:

```
PASS  derive(None)                                            -> None
FAIL  derive('.agent-work/run1/checklist.json')               -> '.'
FAIL  derive('<wt>/.agent-work/run1/checklist.txt')           -> '<wt>'
FAIL  derive('<wt>/.agent-work/checklist.json')               -> '<wt>'
PASS  derive('<wt>/other/run1/checklist.json')                -> None
```

Three of five assertions flip. Two of the three are recoverable if the
implementer keeps the absolute-path and `.json`-suffix preconditions — but g1
never says to keep them, so that is under-determined at exactly the boundary an
existing test pins. The third (`<wt>/.agent-work/checklist.json`) flips
unavoidably: "arbitrary depth" includes depth zero. So `g1-integrate.c1` fails
as authored, and the plan does not say so.

What I would change: state in g1 which of the existing preconditions survive
(absolute? `.json` suffix? non-empty work-id segment?), name
`tests/test_spine_rail.py:874` as a test this gate must update, and say what its
new contract is.

### F4 — blocking — intent-fit — the measured fail-closed blast radius includes a file g2 is fenced from editing

The handoff asked me to measure this. I did, dynamically rather than by
reading: I ran the full suite under a read-only probe (a pytest plugin plus a
`sitecustomize` on `PYTHONPATH`, both outside the repo — no repo file changed,
suite still 3104 passed) that logged every guarded-verb engine invocation, both
in-process `main()` and subprocess, with the spine path and the owning test.

**429 guarded-verb engine invocations observed. 67 have an `.agent-work`
ancestor. 362 do not — every one of those is refused under g2's fail-closed
rule. 125 distinct tests across 7 files:**

| tests | file |
|---|---|
| 92 | `tests/test_checklist_engine.py` |
| 22 | `tests/test_episode_fields.py` |
| 3 | **`tests/test_crew_launcher.py`** |
| 3 | `tests/test_mcp_identity.py` |
| 2 | `tests/test_prototyper_templates.py` |
| 2 | `tests/test_shipped_template_gates_satisfiable.py` |
| 1 | `tests/test_mcp_spine_server.py` |

Split: 236 in-process, 126 subprocess. Verbs: `start` 87, `advance` 76, `claim`
36, `attest` 33, `amend` 29, `reopen` 24, `attach` 15, `resume` 14, `skip` 11,
`block`/`waive` 7 each, and the rest.

The root cause is structural, not incidental. `tests/test_checklist_engine.py:98
_run_main` writes every fixture to `tempfile.TemporaryDirectory()/c.json`, which
has no `.agent-work` ancestor by construction. These fixtures are legitimate:
they pass today because `origin_worktree_refusal` returns `None` for an
origin-less spine (`scripts/checklist_engine.py:154-158`), and g2 removes that
fallback for a population it never had to consider.

The blocker is these three, in `tests/test_crew_launcher.py`:

```
AssignmentKeyedLeaseTests::test_assignment_keyed_identity_resumes_instead_of_refusing
AssignmentKeyedLeaseTests::test_attempt_tagged_identity_is_refused_on_respawn
DoorHijackRealEngineControlTests::test_child_claims_its_own_spine_dispatcher_lease_untouched
```

`g2-implement.constraints` fences that exact file: *"FENCED, do not edit: ...
`tests/test_crew_launcher.py` (lane E)."* So g2 must break three tests it is
forbidden to fix, while `g2-integrate.c1` demands the suite be green. The gate
cannot close on its own terms. Its only exit is the human override on `c1`,
which converts the plan's central regression floor into a rubber stamp for the
one gate that most needs it.

I take the plan's credit where it is due: `g2-implement` does say *"MEASURE AND
STATE THE COUNT ... that is a FINDING to report, not something to paper over."*
That instruction is right. But the plan then gives the finding nowhere to go —
see F6.

What I would change: decide the fail-closed scope **before** freezing, not
inside g2. Either narrow the refusal (fail closed only when the spine also
carries an `origin` stamp, which preserves every current fixture and still
retires the comparison), or lift the lane-E fence for those three tests as an
explicit pre-ruling, or split the fail-closed rule into its own gate with the
122 non-fenced fixture updates as its declared deliverable. The measured count
belongs in the frozen plan, not in a gate's discovery.

### F5 — blocking — simplicity/verification — g4's justifying constraint is false as stated

`g4-implement.anchors.constraint` asserts: *"`verify_worktree_isolation` ships
in NO template or spec (verified 2026-08-16, zero occurrences), so threading cwd
disarms nothing that ships."* Both halves fail.

Two live, tracked, non-archive files carry it:

1. `.agent-work/templates/COMMANDER_SPINE.template.json:12` — a `command`-kind
   precondition, which is precisely the kind of check g4 relocates:
   ```json
   {"id": "c0", ..., "check": {"kind": "command",
    "command": "python scripts/verify_worktree_isolation.py --here <repo-root>"}}
   ```
   `.agent-work/templates/` is the project-local template overlay that
   `scripts/install_constellation.py:2248-2264` describes as *"what a project
   actually edits and commits"*, resolved project-local-first. This one is stale
   relative to `skills/commander/templates/COMMANDER_SPINE.template.json` (which
   has zero occurrences), but it is checked in and it is what resolves first.

2. `skills/admiral/templates/LAUNCH_ORDER.template.md:43` — the shipped Admiral
   template, in the `admiral` and `commander` bundles
   (`install_constellation.py:212-223`), instructing every Commander to run
   `verify_worktree_isolation.py --here <path>`. Line 45 of that same template
   says, verbatim:

   > Do **not** resolve this by passing the path to git (`git -C <path>`): that
   > compares the worktree to itself, is true for any valid worktree, and
   > disarms the check entirely. Measured — forcing cwd turned a real refusal
   > into a clean pass on a Commander standing in the wrong checkout.

   And line 47: *"**Distinct from, not superseded by, the engine-native
   guard.**"*

So shipped doctrine already names *forcing cwd* as the thing that disarms this
check, and already rules that the check is not superseded. g4 threads cwd. The
justification "disarms nothing that ships" is not merely unverified; it is
contradicted by a template in the bundle.

What I would change: strike that constraint, replace it with the measured truth
(two live carriers, one of them a `command` check), and re-derive whether g4 is
still in scope on an honest premise. This also reframes F9 below.

---

### F6 — serious — intent-fit — two gates have imperatives that contradict their own postconditions

`g4-implement` instructs: *"Measure the collision, state it precisely, and
**STOP** -- the Commander floats it to the Admiral."* Its only postcondition
`c1` requires an `implementer-result` artifact matching `status: "complete"`. An
implementer that stops and floats does not return `complete`. The gate's
success path and its close criterion are mutually exclusive.

`g2-implement` has the same shape: report the fail-closed breakage as a finding
(which F4 shows is certain, not hypothetical), but close only on
`status: "complete"`.

In both gates the honest outcome the plan asks for cannot satisfy the gate. What
I would change: make the artifact match accept the float — e.g. `status` in
`{complete, blocked}` with a required `finding` field — or add an explicit
`gN-float` item that owns the escalation. As written, an implementer's incentive
is to report `complete` and bury the finding, which is the opposite of what the
imperative wants.

### F7 — serious — simplicity — g1's "reuse `normalize_path`, don't mint a second one" is unexecutable under g1's own fence

I verified the constraint the frame leans on, and it holds:
`scripts/hooks/spine_rail.py` imports only stdlib (`errno, json, os, re, shlex,
subprocess, sys, tempfile, time, datetime, pathlib`, plus guarded `msvcrt` /
`fcntl`) — zero cross-module imports, confirmed. And
`SCRIPT_RUNTIME_COMPANIONS` has no `"spine_rail.py"` key; it appears only as a
*value* under `"gauge_writer_hook.py"`. So the single-definition placement does
require a new installer entry. That part of the frame is correct.

I also checked the road the frame did **not** take — put the one definition in
`spine_rail.py` (where a narrower version already lives) and import it from the
engine. That is closed too: it needs `spine_rail.py` added to the existing
`"checklist_engine.py"` companion tuple. Same fenced file. The frame's
conclusion survives a check it did not itself run.

But g1's *other* instruction breaks on the identical rock. "Reuse
`scripts/verify_worktree_isolation.py`'s `normalize_path` definition rather than
minting a second one" means importing it into `checklist_engine.py`. That trips
`tests/test_install_constellation.py:1477
test_engine_runtime_siblings_are_declared_as_companions`, which asserts **exact
set equality** between the engine's parsed runtime-sibling closure and a
hard-coded four-element set — and then requires every reached sibling to be
declared in the FENCED `install_constellation.py`. Seven bundles carry
`checklist_engine.py` without `verify_worktree_isolation.py` (charter,
workbench, interrogator, cartographer, implementer, reviewer, explorer), so the
import would ship broken to all seven.

`scripts/hooks/spine_rail.py` cannot import it at all under the stdlib-only
constraint, so g1 already mandates a second copy of the formula there while
forbidding a second definition. And the repo's own precedent is to inline:
`scripts/agent_work_root.py:56` writes the idiom with the comment *"same idiom
as `verify_worktree_isolation.normalize_path`"*. `normalize_path` has zero
importers today.

What I would change: drop "reuse the definition"; say "use the same idiom,
`os.path.normcase(os.path.realpath(p))`, as `agent_work_root.py:56` already
does" — and then reconcile it with F2, which argues the predicate's derivation
should not `realpath` at all.

On the wider YAGNI question the handoff raised: two implementations plus a
shared case table is **justified**. The stdlib-only constraint is real, the
duplicated logic is about eight lines, and a shared parametrized table is the
cheapest thing that makes drift a test failure. I would not delete that. What I
would delete is the `normalize_path` import instruction and the unstated
`realpath` requirement riding with it.

### F8 — serious — testability — g1 makes a second existing check unfailable, in the hook

`scripts/hooks/spine_rail.py:1113-1122`, inside `_is_valid_claim_target`:

```python
if not _worktree_from_spine(abs_spine):
    return False
if not looks_like_checklist(abs_spine):
    return False
resolved = str(Path(abs_spine).resolve())
return bool(_worktree_from_spine(resolved))
```

The docstring calls this a deliberate symlink-escape guard: check lexically,
then re-check against the resolved path, because a symlink can satisfy the
lexical shape while the real file lives elsewhere. `resolve()` is kept
*outside* `_worktree_from_spine`, which the docstring at `:712` calls
"deliberately lexical".

g1 moves `realpath` *inside* the derivation. Both calls then operate on the same
resolved path and return the same value. The second call becomes redundant and
the guard becomes a check that cannot fail — silently, with no test going red,
because the plan's only check is the suite. Same defect class as F2, in a
different file.

What I would change: this is another reason to keep the derivation lexical
(F2). If `realpath` must live inside it, g1 must say what replaces the
symlink-escape guard and pin the replacement with a test that a symlinked spine
still fails.

### F9 — serious — intent-fit — the g4 collision claim is right, but the plan's response is narrower than the evidence already in the tree

The claim is correct and I verified the mechanism. `main()` computes
`base_dir = path.parent` (`scripts/checklist_engine.py:3608`), so for a spine at
`<wt>/.agent-work/w1/spine.json` the derived cwd is `<wt>`.
`verify_worktree_isolation.py --here EXPECTED` runs `git rev-parse
--show-toplevel` **from the ambient cwd** (`verify_worktree_isolation.py:91`)
and compares it to `EXPECTED`, which in a real spine is `<repo-root>` — the same
`<wt>`. Forcing cwd makes it `X == X`. Structural, not incidental. The plan is
right to call it that, and right to refuse to relax the assertion.

Where the plan is evasive is the set of roads it offers. Its decision anchor
reads: *"whether the tripwire fixture is taught the new contract or the gate
stops."* Two roads. The test's own docstring
(`tests/test_worktree_precondition_wiring.py:128-155`) already names a third and
tells the reader to take it first:

> A command check that observes the environment needs an explicit contract — a
> schema flag, or the launcher's cwd passed into the check's environment —
> before the engine may relocate it. **If such a contract HAS landed, this
> fixture is what needs updating.**

The order is a precondition, not a menu: land the contract, *then* teach the
fixture. The plan inverts it into a choice between teaching the fixture and
stopping, and never mentions the contract. Combined with F5 — the disarm hits a
shipped Admiral template and a live `command` precondition, not just a test —
the float that goes to the Admiral is materially understated.

What I would change: name the third road in g4's decision anchor, quote the
docstring, and attach F5's two carriers to the float so the Admiral rules on the
real blast radius rather than on a fixture.

---

### F10 — minor — intent-fit — g3 is in the plan but not in the frame's intent or evidence surfaces

The frame's **Intent** names three things: derive the worktree, retire
stamp-and-compare, thread the derived worktree into command checks. The frame's
**Evidence surfaces each gate must re-confirm** lists three: Derivation,
Retirement, #315. g3 — the hook stops using the worktree for ownership — appears
in neither.

g3 is also the plan's riskiest behaviour change. Its own constraint says
*"Removing a skip makes the Stop hook block MORE, not less"*, and it reworks two
asymmetric call sites in the rail. That is a real issue; it is not obviously
this issue. What I would change: either add g3 to the frame's intent with its
own evidence surface, or split it out. Riding it along under a "derive the
worktree lexically" mission is how a Stop-hook regression ships unnoticed.

### F11 — minor — testability — a frame-mandated evidence surface has no gate that owns it

The frame requires, for every gate: *"full clean-env, cache-cleared suite, plus
a `main` baseline re-measured at gate time."* The plan's integrate checks do the
first half and never the second. No gate re-measures `main`. The frame also
says, of Windows: *"Say what was done about separators and case regardless."* No
gate requires that statement. Both are frame requirements with no owner.

### F12 — minor — a second line drift, unrecorded, in a file g2 must edit

The frame records one order-vs-tree drift (`spine_rail.py:639` vs `:693`) and
says it is why no gate trusts a supplied line number. I re-checked every line
the frame and plan cite. They are all correct at `e36e630b`: `checklist_engine`
`102`, `102-179`, `871-895`, `883`, `898`, `927`, `3573`, `3573-3578`, `98-99`,
`2505`, `2550`, `2620`; `spine_rail` `677`, `693`, `712`, `1411`, `1546`,
`543-590`; `verify_worktree_isolation:47`; `CHECKLIST_SCHEMA.md:120`;
`test_worktree_precondition_wiring.py:128`. Three `spine_rail` ranges start one
line early on the blank line before the `def` (`1398/1399`, `1426/1427`,
`1531/1532`) — loose, not stale. Good discipline overall.

The stale reference is one level down, inside a file g2 must update:
`docs/CHECKLIST_SCHEMA.md:124` cites the `main()` call site as
`scripts/checklist_engine.py:3411-3444`. The actual site is `3573-3578`. Since
g2 rewrites that paragraph anyway, worth naming so the drift is repaired rather
than carried.

I also confirmed the frame's other measurable claims: **27** tracked paths carry
two `.agent-work` segments (exactly 27, all under
`.agent-work/archive/2026-08-12-dispatch-126-127/harvest/*/workspace/`), so
"nearest, not outermost" is correctly motivated; and `spine_rail.py` really is
stdlib-only.

---

## Claims I could not verify

- **Windows separator and case behaviour.** This host is Linux and
  `os.path.normcase` is the identity function here, so nothing I ran exercises
  the fold. The frame is honest that CI's `windows-latest` job is red at
  baseline. What would settle it: a green targeted run of
  `tests/test_spine_origin_isolation.py` and the new g1 equivalence table on a
  Windows host, or a case-folding test that constructs the fold explicitly
  rather than relying on the platform.
- **Whether `.agent-work/templates/COMMANDER_SPINE.template.json` is reached at
  runtime in a real Commander run.** I confirmed it is tracked, non-archive,
  carries the `--here` command check, and that
  `install_constellation.py:2248-2264` documents project-local-first resolution
  of that directory. I did not run a Commander to observe the resolution. This
  does not change F5, which stands on
  `skills/admiral/templates/LAUNCH_ORDER.template.md:43` alone. What would
  settle it: instantiate a spine through `init_work_area.py` and read which
  template file it resolved.
- **Exact post-g2 test count.** My 125/362 figures measure what the suite does
  today, which is what "blast radius" means. I did not simulate the refusal
  itself, so I cannot say how many of the 125 would be repaired by a fixture
  move versus need a rewrite. The three fenced ones need no such estimate — they
  cannot be touched at all.
- **Whether the `not-a-weaker-guard` ruling survives.** g2 asks the implementer
  to look adversarially for a case where the removed comparison was the only
  thing preventing harm. I did not run that search; it is g2's work and it is
  correctly placed there.

## Workflow Feedback

- The plan's gate *imperatives* are excellent — specific, anchored, honest about
  what they do not know, and they name the traps (F4's count, F9's collision)
  before an implementer can walk into them. The gate *postconditions* carry
  almost none of that. Every finding above except F5 and F12 is some version of
  the same gap: the plan knows things its checks cannot see. Whatever process
  produced the imperatives should also be pointed at the `postconditions` block.
- Two of the plan's four gates instruct an implementer to stop and report, and
  both then require `status: "complete"` to close (F6). If the engine's artifact
  vocabulary has no way to close a gate on an honest float, that is a workbench
  gap worth a triage candidate, not a per-plan workaround.
- The `anchors.constraint` blocks are where the two false claims live (F5's
  "zero occurrences", and F7's reuse instruction). They read with the same
  confidence as the verified structural anchors, which are all correct. Anchors
  cut from a frame inherit the frame's confidence marking; a constraint asserted
  as "verified <date>" and a line number read in tree are different kinds of
  claim and would be worth marking differently.
- The frame's `DEGRADED-UNPARSEABLE` handling is the right call and well
  argued — pinning every structural claim to a line read in tree, and refusing
  to cite anchor ids that cannot resolve, is what made this review checkable at
  all. Twenty-odd line citations, all correct. That discipline is why the two
  false claims stand out rather than hide.
- Measurement note for whoever runs g2: the blast radius is measurable without
  changing the repo. A pytest plugin plus a `sitecustomize.py` on `PYTHONPATH`,
  both outside the tree, logging `(nodeid, verb, --file path)` from both
  `main()` and `sys.argv`, gets the full picture in one 124-second suite run and
  catches the subprocess invocations that in-process patching misses (126 of the
  362 here).
- **Live reproduction of the #549 shape this plan's g3 targets — observed from
  inside this crew session, unprompted.** On finishing my task the Stop hook
  answered *my* Stop with the **Commander's** `plan` gate imperative, twice,
  including its `<engine> waive plan --cond c6` and `attach plan --type
  user-decision` instructions and the parent's lease line (`LEASE active:
  commander-cleanup-f-derive-worktree`). I am a crew session with my own bounded
  handoff; I hold no lease on that spine.

  This is exactly the failure `g3-implement` describes: *"spines are 1:1 with
  work AREAS, not worktrees, so an in-tree implementer reports 'not foreign' and
  the parent's Stop is answered with its crew's gate."* I share the Commander's
  worktree, so `_foreign_worktree` (`spine_rail.py:693`) returns False for me
  and the rail treats the parent's binding as mine.

  Two things follow for the plan. First, g3 is not speculative — the bug is
  firing in this run, which strengthens the case for the gate even as F10
  questions whether it belongs in *this* issue. Second, and more useful: this is
  a ready-made evidence surface. `g3-implement.anchors.evidence` asks for *"the
  #549 shape exercised directly: a Commander and an in-tree implementer sharing
  one worktree, where the parent's Stop must NOT be answered with the crew's
  gate."* That is this session, reproducible from the constructed payload
  `{"cwd": <this worktree>, "session_id": <crew sid>}` against the Commander's
  binding entry. g3 should cite it rather than build a fixture from scratch.

  Noting also what the hook told me to do and why I did not: it instructed me to
  `waive` or `block` the Commander's gate rather than end my turn. Both are
  guarded verbs against a spine another agent holds the lease on, and my handoff
  says *"Change nothing."* A crew member driving the parent's spine to silence
  its own Stop hook is the harm the ownership rule exists to prevent — so the
  correct response to a misattributed gate is to refuse it and say so, which is
  what this note is. That the misattribution's suggested remedy is itself a
  guarded-verb write is worth weighing in g3's "enumerate what newly blocks"
  step.
