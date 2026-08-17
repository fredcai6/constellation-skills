# Cold plan critique — `MISSION_FRAME.md`, `DESIGN_CONVERGENCE.md`, `execute.json`

Cold critic. No authoring context, no transcript, no candidates, no launch order. I read
the three named artifacts, then read `scripts/` and `tests/` only to check whether their
factual claims are true. Every number and every command output below is mine, run in this
worktree or the primary checkout, and the commands are quoted so they can be re-run.

**Bottom line.** The two obligations the convergence calls undodgeable are checkable and
true; the atomicity defect is real; the census is very nearly reproducible. But the
document's central security argument is presented on an unquantified axis, and when I
quantify it under one consistent predicate the argument inverts: the recommended candidate's
containment root is a strict *superset* of the reach the document quantified in order to
kill candidate C, by roughly 34x. Separately, **every mechanical postcondition in the 9-gate
plan already passes at base with zero code written**, so the plan as it stands cannot
distinguish "mission achieved" from "two cooperative crews said so." And the atomic-write
pattern the plan mandates by name installs a *durably corrupt* spine under two concurrent
writers, which this repo has by design.

Counts: **5 blocking, 10 serious, 7 minor, 3 notes.**

---

## BLOCKING

### B1 — The winner's reach is never quantified; quantified, it is ~34x the reach that killed the loser
**blocking · Lens 1 + Lens 3 · attacks the load-bearing argument directly**

`DESIGN_CONVERGENCE.md:57-62` prints a comparison table. Candidate C's "Reach added" cell
carries three bolded numbers (**124 spines, 99 unleased, 674** `--from-child` targets).
Candidate A's cell carries a *sentence*: "any spine-shaped JSON inside this door's own
checkout." No number. Line 111-114 then convicts C: "the only genuinely distinct option, and
it is the maximum-reach one." Line 80-88 says the seam axis "decides the run" and that "B
loses on the boundary, and that outranks both."

A boundary argument decided by an axis where only one side is measured is not an argument.
I measured the other side.

A's containment root is `_primary_checkout_for_lifecycle()` (`DESIGN_CONVERGENCE.md:227`).
That function is at `scripts/mcp_spine_server.py:797` and returns the **primary checkout
root** — `git rev-parse --git-common-dir` from the bound spine's directory, `.resolve().parent`
(`:857-860`). Its own docstring states that worktrees nest *inside* that root:

> `scripts/spine_lifecycle.py`'s `_default_wt_root` is the ONE place that answers "where do
> worktrees live" -- `<root>/.worktrees`, nested under the primary checkout
> — `scripts/mcp_spine_server.py:839-843`

So A's `bound_dir` admits `<primary>/.worktrees/*/**` — every other lane's checkout.
Measured (predicate: parseable JSON dict with `items` list + `tasks` dict + a truthy
`work_id`, i.e. exactly the population A's own corrected rule says it will bind):

```
spine-shaped WITH a work_id anywhere under primary checkout: 4204
  of those inside .worktrees/ (other lanes' checkouts):      3505
  of those with an ACTIVE engine_session (live, leased):      306
```

C's numbers, reproduced: files literally named `spine.json` under `<primary>/.agent-work/`
(archive included) = **126** (doc said 124; drift, see S1); files carrying a `consolidation`
key under the same root = **674**, an exact match to the doc.

```
primary .agent-work incl archive: (spine-shaped=683, unleased=632, consolidation-key=674)
```

C's static-default `SPINE_ROOT` is `<root>/.agent-work`. That directory is a **subset** of
A's `<root>`. Under one predicate, in the same tree: A ≈ 4204 targets, C ≈ 683. The document
killed C for maximum reach and crowned the candidate with strictly more of it, then declined
to print the number.

**Smallest fix.** Put A's reach in the table under C's own predicate, then re-run the
seam-placement axis with both cells populated. If A still wins, narrow A's containment root
so the claim survives: `bound_dir` = the *bound worktree's* `.agent-work/` (i.e.
`_worktree_root_for_lifecycle()/".agent-work"`, `:864`), not the primary checkout. That is a
one-argument change to an existing `_resolve_confined` call and it is the difference between
a widening you can defend and one you have not measured.

---

### B2 — The isolation section contradicts itself about other checkouts, 18 lines apart
**blocking · Lens 1**

`DESIGN_CONVERGENCE.md:220-222`:

> "...anywhere inside the primary checkout of this door's own repository — **including a
> sibling worktree's live spine** — may become the spine this process drives."

`DESIGN_CONVERGENCE.md:238-239`:

> "**What an agent still cannot do:** drive two spines at once; **drive a spine in another
> checkout**; name its own identity..."

A linked worktree *is* another checkout. `git worktree list` in this repo returns six
checkouts, five of them linked and all five nested under the primary path. B1's measurement
says 3505 of the reachable spine-shaped files sit in them, 306 of the repo's spines carry an
active `engine_session`. The second bullet is false, and it is the bullet a human skimming
for the security summary will read.

This matters beyond wording: the incident the frame itself cites as this wave's grounding
(`MISSION_FRAME.md:48-50`, lane G — "its implementer crew plus its own context-inheriting
fork drove one `spine.json` under one lease id, and the lane could not tell its own writes
from an attacker's") is *exactly* cross-agent access to one live spine. The recommendation
makes the cross-*worktree* version of that reachable through a tool, and then tells the
reader it is not reachable.

**Smallest fix.** Delete the false bullet and add a named refusal: reject any target whose
`git rev-parse --show-toplevel` differs from the door's own. That refusal restores the
sentence to true and costs one `_git_rev_parse` call the module already has.

---

### B3 — Every mechanical postcondition in the plan passes at base, unchanged
**blocking · Lens 2 — checks that cannot fail**

I ran all four of the plan's `command` checks against `600de020` with no change applied.

```
$ cd .worktrees/567-a-spine-identity && py -m pytest tests/test_mcp_lifecycle.py \
      tests/test_mcp_identity.py tests/test_mcp_door_unbound.py -q
61 passed, 10 subtests passed in 4.18s          # g2-integrate c1  -> PASSES AT BASE

$ py -m pytest tests/test_checklist_engine.py -q
456 passed, 140 subtests passed in 2.15s        # g3-integrate c1  -> PASSES AT BASE

$ py scripts/checklist_engine.py --file .agent-work/epic-567-door/cmdr-a/spine.json current
exit 0                                          # g4-selfhost c1   -> PASSES AT BASE
```

`g1-converge c1` is `test -f DESIGN_CONVERGENCE.md && grep -q 'Recommendation'` — satisfied
by the word appearing anywhere in any file of that name.

Now trace what remains. `g2-implement c1` = an `implementer-result` artifact with
`status=complete`; `g2-review c1` = a `review-result` artifact with `verdict=APPROVE`;
`g3-implement c1` and `g3-review c1` the same shape. Those are **crew self-reports**.
`g2-integrate c2` ("the reach-delta negative test exists and is named in the review"),
`g4 c2`, `g4 c3` all have `"check": null` — Commander attestations.

So the *entire* g2 and g3 chain closes if two cooperative crews return the right JSON and
the pre-existing suites stay green. **Nothing in the 9 gates would go red if `spine_bind`
were never written.** The plan produces artifacts about the mission, and the only thing
standing between it and a fully-green empty diff is a human reading prose. That is precisely
the failure mode `g3-review`'s own imperative names — "a test that passes in both the healthy
and the defective world is a check that cannot fail" — applied to the plan and not to itself.

**Smallest fix.** Give g2-integrate and g3-integrate command postconditions that name the new
tests by pytest node id, e.g.
`py -m pytest "tests/test_mcp_door_unbound.py::SpineBindTests::test_a_door_binds_a_spine_it_did_not_mint" -q`,
so the check fails with "no tests ran" (exit 4) if the test does not exist. Add one mutation
postcondition per claim: revert the confinement clause, show the negative test goes red,
paste both.

---

### B4 — The obligation the convergence calls undodgeable appears in no gate
**blocking · Lens 1 — essential thing missing from the 9 gates**

`DESIGN_CONVERGENCE.md:253-261` states obligation 1 in the strongest terms available: the
identity pin will fail by design, the remedy is "a **tool-scoped** exemption plus an
`IDENTITY_TRADE.md` amendment in the same change," and "the cheaper dodge — naming the
argument `work_file` or `plan_path` so the pin passes — **must be refused**."

```
$ grep -c "IDENTITY_TRADE" execute.json
0
```

The gate plan never mentions it. `g2-implement`'s imperative (`execute.json:162`) carries the
`ALLOWED` argument and the `origin.work_id` correction as protected intent and stops there.
No gate requires the amendment, no gate forbids the renaming dodge, and no gate requires the
exemption be property-scoped rather than tool-scoped.

The pin's own failure message asks for exactly this and says why
(`tests/test_mcp_identity.py:832-836`):

> "If the identity trade was deliberately re-opened, update
> .agent-work/archive/.../IDENTITY_TRADE.md in the same change -- **this test exists so that
> cannot happen silently.**"

An obligation stated only in a document the implementer is not required to satisfy is not an
obligation.

**Smallest fix.** Add two postconditions to `g2-implement`: (a) a command asserting the
`IDENTITY_TRADE.md` amendment is non-empty in this diff; (b) a command asserting the pin's
exemption is keyed on `(tool, property)` — grep the exemption for the literal
`spine_bind` *and* `spine_file`, and add a test that `spine_bind.session_id` is still an
offender. Add to `constraints`: "renaming the argument to pass the pin is refused."

---

### B5 — The mandated atomic-write pattern installs a *durably corrupt* spine under two concurrent writers, and this repo has two concurrent writers by design
**blocking · Lens 1 + Lens 2**

`execute.json:384` (`g3-implement`) mandates the pattern by name and forbids inventing one:

> "Replace with the repo's OWN canonical pattern, do not invent one: mirror
> `scripts/hooks/gauge_writer_hook.py:513 _atomic_write_json`"

That function uses a **fixed** temp name:

```python
def _atomic_write_json(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")      # <-- fixed, one per target path
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(record, f)
    os.replace(tmp, path)
```
— `scripts/hooks/gauge_writer_hook.py:513-519`

Two writers of one spine is not hypothetical here. `scripts/run_crew.py` runs
`_parent_lease_heartbeat()`, a **daemon thread** that refreshes the dispatching process's own
lease on its `SPINE_FILE` for the duration of a blocking child dispatch, and the
shared-spine case is explicitly supported:

> "`_parent_lease_heartbeat()` is a context-managed daemon-thread helper, started around the
> blocking call in both `CliBackend.dispatch` and `CliBackend.resume` ... These tests drive
> it both directly ... and through the real `CliBackend.dispatch`/`resume` call sites (**the
> shared-spine case** a first draft's now-removed self-collision guard would have silently
> broken)."
> — `tests/test_crew_launcher.py:3211-3225`

And the very docstring `g3-implement` sends the implementer to fix says a reader hits the
window today (`tests/test_crew_launcher.py:3247-3250`).

I ran the mandated pattern with two writers on one path:

```
installed: b'{"a": "S"}LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"}'
parses: NO -> JSONDecodeError Extra data: line 1 column 11 (char 10)
errors: ["FileNotFoundError: [Errno 2] No such file or directory: 'probe2.json.tmp' -> 'probe2.json'"]
```

Two distinct defects, both worse than the status quo:

1. The loser's file handle still points at the inode that `os.replace` just installed as the
   live spine, so its buffered flush writes **directly into the live target after the
   rename** — bypassing atomicity entirely and producing a durably unparseable document.
   Today's bare `write_bytes` tear is transient: the next successful write heals it. An
   installed corrupt document is permanent, and `checklist_engine.load` meets it with an
   unhandled traceback (see S3's pasted output for `load`'s failure shape).
2. The loser's `os.replace` raises `FileNotFoundError`, an exception `save()`'s callers have
   never had to handle.

Also unaddressed by the mandate: `os.replace` from a fresh temp **loses the target's file
mode**, and there is no `fsync` of the temp before the rename, so the "crash mid-write"
half of the claim (`execute.json:384`) is not actually delivered — a rename can be durable
before the data is.

**Smallest fix.** Delete "mirror `gauge_writer_hook.py:513`" from the imperative and specify
the write directly: `tempfile.mkstemp(dir=path.parent)` for a **unique** temp name,
`os.fchmod` to the existing file's mode when it exists, `f.flush()` + `os.fsync(fd)`, then
`os.replace`, with the temp unlinked in a `finally`. Add a postcondition test with two
concurrent writers asserting the installed document always parses. And file the fixed-name
hazard in `gauge_writer_hook.py` as a triage candidate — it is the same bug there.

---

## SERIOUS

### S1 — Census reproduces to 4/49/0, not 4/48/0, and the population moves while you measure it
**serious · Lens 2**

I re-derived it independently. Predicate: every parseable JSON dict under
`<repo>/.agent-work/` and `<repo>/.worktrees/*/.agent-work/`, excluding any path component
`archive` or `templates`, that has an `items` list and a `tasks` dict.

```
=== strict: dict with items(list)+tasks(dict)
  total spine-shaped : 53      (doc: 52)
  origin.work_id     : 4       (doc: 4)   -- MATCH
  top-level only     : 49      (doc: 48)
  neither            : 0       (doc: 0)   -- MATCH
```

The four `origin.work_id` bearers are exactly the four `spine.json` files minted by
`init_work_area.py --spine` (`567-a`, `567-c`, `567-g`, `issue-610`), which corroborates the
doc's mechanism claim at `DESIGN_CONVERGENCE.md:166-167`. Two looser predicates (`tasks` dict
alone; `type in {gated,survey}` + `tasks`) give the identical 53/4/49/0, so the +1 is not a
predicate disagreement.

**It is the population moving.** Seven minutes later the same script returned **54**. Sorted
by mtime, files were created by concurrent lanes at 22:36, 22:41, 22:48, 22:49, 22:51, 22:59,
23:06, 23:15, 23:26, 23:27, 23:28, 23:29 and 23:33 — including
`.worktrees/567-g-closeout-lease/.../g2-implementer-plan.json` at 23:33, during my run.

I therefore **substantially reproduce** the census and the recommendation does not turn on
the delta: 4-of-N carry `origin.work_id`, the overwhelming majority carry only a top-level
`work_id`, and I found zero with neither under three predicates. The correction from
`origin.work_id` to `work_id` is the right correction and the honest self-falsification at
`DESIGN_CONVERGENCE.md:144` ("A named, in its own §7, the measurement that would prove it
wrong. **I ran it.**") is the single strongest thing in the document.

But the doc presents "0 carry neither" as license to narrow `R7`
(`DESIGN_CONVERGENCE.md:178-180`) and the count grew by two while I read it. A snapshot over
a live tree is not a fact about the population.

**Smallest fix.** Print the exact predicate and the wall-clock timestamp beside the table, and
make `R7`'s fail-closed path a *tested refusal* (a spine with neither field, planted in a
tmpdir, refused with the boundary named) so the posture does not rest on a count at all.

### S2 — The lane's own first-class deliverable has `check: null`
**serious · Lens 2**

`decision:isolation-not-fencing` is graded `guess/admiral` (`MISSION_FRAME.md:115-116`) and
`MISSION_FRAME.md:133` calls the negative test "a first-class deliverable, not a side effect."
Its gate check is `execute.json:329-333`:

```json
{ "id": "c2",
  "statement": "the reach-delta negative test exists and is named in the review",
  "check": null }
```

An attestation. The two constraints beside it ("A green suite is not evidence the reach did
not widen — require the negative test", `:262`) say the right thing to a reader and bind
nothing. Compare what the plan is willing to make mechanical: `grep -q 'Recommendation'`.

**Smallest fix.** Replace `null` with a command that runs the test by node id, plus a second
postcondition pasting a mutation proof (delete the `bound_dir` argument, show the test red).

### S3 — `g4-selfhost c1` cannot fail for the reason it claims, and its path is cwd-dependent
**serious · Lens 2**

The check (`execute.json:611-615`) is
`py scripts/checklist_engine.py --file .agent-work/epic-567-door/cmdr-a/spine.json current`,
with the statement "read-only `current` on the live spine exits 0 **under the edited
engine**."

Three problems.

1. **`current` never calls `save()`.** The g3 change is confined to `save`
   (`checklist_engine.py:237-256`). A read-only verb's exit code is identical in the healthy
   and the defective world. This is an import smoke test presented as a self-hosting proof of
   an atomicity change.
2. **It already passes** (B3).
3. **The path is relative, so nothing pins which engine or which spine.** Run verbatim from
   the primary checkout:

```
$ py scripts/checklist_engine.py --file .agent-work/epic-567-door/cmdr-a/spine.json current
Traceback (most recent call last):
  File "/home/tommy/projects/constellation-skills/scripts/checklist_engine.py", line 3610 ...
  File ".../scripts/checklist_engine.py", line 221, in load
    return json.loads(Path(path).read_text(encoding="utf-8"))
FileNotFoundError: [Errno 2] No such file or directory: '.agent-work/epic-567-door/cmdr-a/spine.json'
exit 1
```

`.agent-work/epic-567-door/cmdr-a/spine.json` does not exist in the primary checkout at all.
So the check's verdict is a function of the harness's cwd — and the frame's own
`assumption:in-session-observation-is-not-evidence` (`MISSION_FRAME.md:96-99`) says hooks and
the engine "execute from the main checkout regardless of worktree," while `g4`'s own
imperative demands "a FRESH process with **explicit paths**." The check violates the
constraint it sits under, and `assumption:engine-under-edit-is-not-engine-in-play`
(`:100-103`) is unenforced because nothing in the command names which copy of
`checklist_engine.py` runs.

(Incidental, from the same output: `load` surfaces a missing spine as an unhandled traceback
rather than a refusal. See M6.)

**Smallest fix.** Absolute paths for both the engine and the spine, and move the
self-hosting proof onto the *mutating* verb against a copy (`c2`) with an asserted
postcondition — that is the only run that exercises `save`.

### S4 — The new atomicity test module is never executed by any postcondition
**serious · Lens 2 — vacuous by absence**

`g3-implement`'s fence is "`scripts/checklist_engine.py` plus a **NEW test module**"
(`execute.json:384`). `g3-integrate c1` runs `tests/test_checklist_engine.py` only
(`:545`). `g4 c4` runs a fixed five-module list (`:635`) that also excludes it. The lane's
`save()` claim therefore has no command that runs the test proving it.

**Smallest fix.** Either require the tests land in `tests/test_checklist_engine.py`, or name
the new module in both commands.

### S5 — `spine_lifecycle.py` is inside g2's fence and none of its suites are run
**serious · Lens 2**

The recommendation extracts `session_id_for(work_id)` into `scripts/spine_lifecycle.py` and
shares it with `open_work` (`DESIGN_CONVERGENCE.md:190-194`), and `g2-implement`'s fence
includes that file (`execute.json:162`). `g2-integrate c1` runs three `test_mcp_*` modules.
It does not run `tests/test_spine_lifecycle.py` or `tests/test_mcp_adoption.py` — both exist
in this worktree. The change touches `open_work`, the one function that mints every spine in
the fleet, and no postcondition exercises it.

**Smallest fix.** Add `tests/test_spine_lifecycle.py tests/test_mcp_adoption.py` to
`g2-integrate c1` and to `g4 c4`.

### S6 — The identity pin's positive control will be silently decoupled from the pin
**serious · Lens 2 — this is the pin's own "check that cannot fail"**

Verified: `tests/test_mcp_identity.py:817` is
`test_no_tool_accepts_an_argument_that_could_redirect_the_door`, walking `module.TOOLS`,
skipping `ADDRESSES_WITHIN_BOUND_SPINE` (`:773`), substring-matching
`IDENTITY_ARG_MARKERS = ("spine", "session", "engine", "checklist_file", "identity")` (`:754`).
Its positive control is `test_the_pin_can_fail` at `:839`, and it plants **literally**
`{"spine_file": {"type": "string"}}`. The convergence's claim at `:255-256` —
"`spine_bind.spine_file` is literally that pin's own positive control" — is **true and exact.**

The problem is what happens next. The control does not call the detector; it **reimplements
the loop inline** (`:845-853`) and applies neither `ADDRESSES_WITHIN_BOUND_SPINE` nor any
future exemption. The moment the real pin at `:817` gains a `spine_bind.spine_file`
exemption, the control stops being a control for it: it will stay green whatever the
exemption's shape, including an exemption written as "skip the whole `spine_bind` tool" that
would let a future `spine_bind.session_id` through unseen. The plan requires the exemption
(via the convergence, not via a gate — B4) and requires nothing about its scope.

**Smallest fix.** Extract the detector into one module-level function called by both the pin
and the control, and add a control asserting the exemption does **not** cover
`spine_bind.session_id`.

### S7 — The `spine_bind`-has-no-population objection is answered with one exception, not with a population
**serious · Lens 3 · the objection the brief asked me to weigh**

`DESIGN_CONVERGENCE.md:276-284` states the objection in its own words — "every dispatch that
*can* call `spine_bind` is one that could have been launched bound, since `run_crew --spine`
already puts that exact string in the child's environment as a matched pair" — calls it "the
strongest objection on the table," and rebuts it with: "**What defeats this objection is the
Admiral's case**, which is not a dispatch at all."

That does not defeat it. The objection is about the tool's **population**; the Admiral is one
member. The rebuttal never counts the rest. If the honest count is "one caller shape, the
top-tier orchestrator," then a new tool on a security boundary is being bought to serve a
population of one — and the document itself supplies the cheaper answer, applied to a
different candidate two pages earlier:

> "`SPINE_ROOT` set per dispatch is safe but **buys nothing**: a launcher that knows the work
> area's path can set `SPINE_FILE` in the same breath." — `:108-109`

The Admiral is a process with a shell. It knows its own spine's path — the frame says it
reproduced the refusal "with my spine on disk and its lease held by me"
(`MISSION_FRAME.md:44-46`). `SPINE_FILE=<abs path>` on relaunch, or a `--spine` flag on
whatever starts it, is the same argument the doc used to kill C's option, and it costs no new
tool, no allow-list widening, no `IDENTITY_TRADE.md` amendment, and no exemption to a
security pin. The doc raises "a launcher fix plus a better refusal message — zero new tools"
and drops it in the same sentence.

The epic's stated need ("the CLI stops being the only path, which is what unblocks deleting
it in wave 2", `MISSION_FRAME.md:25-26`) is also not obviously served by `spine_bind`
specifically — it is served by *any* door path to an existing spine, including
`SPINE_FILE` at relaunch, which already exists.

**Smallest fix.** Count the caller shapes that cannot be launched bound. Print the number. If
it is 1, the human is choosing between a relaunch and a widened security boundary and
deserves to see it framed that way.

### S8 — `_rebind_refusal` is used as the argument against B and the recommendation depends on it too
**serious · Lens 3 · attacks the load-bearing argument**

The single line that decides the run (`DESIGN_CONVERGENCE.md:199-202`):

> "Why A over B, in one line: both widen reach, but A widens it behind a tool that exists only
> to widen it, with nine named refusals ... while B widens it behind an argument on a tool
> that promises creation, guarded by **the module's weakest guard**."

The weakest guard is `_rebind_refusal`. Verified at `scripts/mcp_spine_server.py:920-955`; its
own docstring names three fail-open directions:

> "Fails OPEN, deliberately, in three directions: nothing bound, an unreadable or
> unparseable spine, and no lease." — `:939-940`

And `DESIGN_CONVERGENCE.md:236` lists, among the four things that hold A in:
"**`_rebind_refusal` still forbids orphaning a lease this process holds.**"

`spine_bind` is a rebind. It sits behind the *same* `_rebind_refusal`, with the same
fail-open on "no lease," and the doc's own kill-shot against B is that releasing a lease is
one call (`:130-131`). So the reachable sequence the doc says B "names and does not refuse" —
release the lease, bind another lane's spine, drive it — is reachable through `spine_bind`
verbatim, only now with a wider containment root (B1). The distinction the run turns on is
**the tool's description and its refusal list**, not the strength of the guard.

That may still be worth something: named refusals and an honest description are real
security-usability value, and `R8` (refuse a demonstrably-live identity) is genuinely new.
But the sentence as written attributes to A a guard strength it does not have.

**Smallest fix.** Rewrite the one-line justification to claim only what is true — "A makes the
widening legible and adds `R8`; the guard is the same guard" — and then either strengthen
`_rebind_refusal` for the bind path (refuse a target whose lease is held by *anyone*, not
only by us) or say plainly that it was not strengthened.

### S9 — `decision:net-deletion` is settled/human, cited in nine gate anchor blocks, and delivered by none
**serious · Lens 1 — essential thing missing**

`MISSION_FRAME.md:117-118` grades it `settled/human`: "the lane ends with something deleted."
`grep -on "net-deletion" execute.json` returns 9 hits, all inside `anchors.decision` arrays —
zero inside an imperative, constraint, or postcondition. No gate deletes anything.

Meanwhile the frame puts the deletable material out of scope: "The wave-2 doctrine sweep: 15
`CLI fallback` clauses and 11 `<engine>` tokens ... Deleting them is blocked behind this
lane, not part of it" (`:150`). And the convergence convicts C on exactly this axis —
"C's answer to 'what do we delete' is, honestly, **nothing**" (`:116-118`) — while never once
saying what **A** deletes.

A human-settled decision that the plan cannot satisfy, applied as a weapon against the
loser and not to the winner, is a double standard the human should get to rule on.

**Smallest fix.** Either name A's deletion and give it a postcondition, or take
`decision:net-deletion` back to the human as unsatisfiable in this lane and say why.

### S10 — `constraint:rail-strings-untouched` is asserted in all nine gates and checked nowhere
**serious · Lens 2**

`_RAIL_STRINGS` and `_refresh_attach_hint` are declared fenced-and-fragile in every gate's
`anchors.constraint` block and in `MISSION_FRAME.md:68-70` ("Lane C needs their text intact
for a follow-up"). Byte-identity is a trivially checkable property and no check exists. `g3`
edits the same file.

**Smallest fix.** One command postcondition on `g3-integrate`: `git diff` the file and assert
zero hunks touch either symbol, or hash both constants before and after.

---

## MINOR

### M7 — anchor drift the frame did not catch in itself
**minor · Lens 2**

`MISSION_FRAME.md:142` proudly records the launch order's stale line reference
(`_identity_violation` at `:164` vs `:443`) so "no gate inherits the wrong line." Verified —
`_identity_violation` is at `:443`. Also verified correct: `_spine_from_env:156`,
`SESSION:202`, `_unbound_refusal:393`, `_bind_process_to:878`, `_rebind_refusal:920`,
`checklist_engine.save:237`, `load:220`, `ALLOWED:135`, `IDENTITY_ARG_MARKERS:754`,
`test_no_tool_accepts...:817`, the one-binder pin at `:563`, `LIFECYCLE_TOOLS:1368`,
`call_lifecycle_tool:1067`, `BINDS_WITHOUT_A_BOUND_SPINE:1425`,
`test_empty_spine_file_refuses_rather_than_binding_the_cwd` at `test_mcp_door_unbound.py:223`,
`_atomic_write_json` at `gauge_writer_hook.py:513`, the stale docstring at
`test_crew_launcher.py:3247-3250`. That is a high hit rate.

Two are wrong: `_spine_open (~:1000-1042)` (`MISSION_FRAME.md:65`) — `def _spine_open` is at
**:968**; and `_resolve_confined (~:330-380)` (`:63`) — the `def` is at **:322**. Both are
hedged with `~`, so this is small, but it is the same defect class the frame just convicted
the launch order of, in the document that convicted it.

**Smallest fix.** Correct both, or drop line numbers where the symbol name suffices.

### M8 — `session_id_for` does not exist, and is written about in the present tense
**minor · Lens 2**

`DESIGN_CONVERGENCE.md:174-176`: "`session_id_for(work_id)` **keeps** its single definition and
`open_work` **keeps** calling it."

```
$ grep -rn "def session_id_for" scripts/
(no output)
```

It is a function the change would create. The substantive claim behind it *is* true and I
checked it: `open_work` returns the literal `f"constellation/{work_id}"`
(`scripts/spine_lifecycle.py:357`), so an extraction can be byte-identical. But present tense
for prospective code invites a reviewer to believe the seam was measured rather than
proposed.

**Smallest fix.** "will keep."

### M9 — 52 and 124 are printed as commensurable and are not
**minor · Lens 3**

`DESIGN_CONVERGENCE.md:60` (124 spines) and `:149-155` (52 live spine-shaped files) use
different, unstated predicates over different roots. I recovered both: 124 ≈ files *named*
`spine.json` under `<root>/.agent-work/` including archive (I get 126); 52 ≈ files with
`items`+`tasks` under `.agent-work/` and `.worktrees/*/.agent-work/` excluding archive (I get
53). Under one predicate the primary checkout's `.agent-work/` alone holds **683**. A reader
comparing the two tables is comparing nothing.

**Smallest fix.** One predicate, stated once, applied to every count in the document.

### M10 — `g3-implement p1` is a comment in a precondition slot
**minor · Lens 2**

`execute.json:387-390`: `"statement": "no dependency on g2 — different file, parallel-safe"`.
That is a design note. It has no truth conditions and can never be false.

**Smallest fix.** Move it to `constraints` and leave `preconditions` empty.

### M11 — `g1-converge`'s checks are both unfalsifiable
**minor · Lens 2**

`c1` is `grep -q 'Recommendation'`. `c2` is an `artifact` check for a `user-decision` with
`cite: LAUNCH_ORDER:Pre-Rulings` — attached by the same agent that wrote the recommendation.
`decision:convergence-is-human-only` (`MISSION_FRAME.md:119-120`) is the strongest governance
claim in the frame, and its check is the Commander asserting that it surfaced something. No
human act is required for the gate to close.

**Smallest fix.** Nothing inside the engine can verify a human read a document. Say that
plainly in `c2`'s statement instead of implying the artifact establishes it.

### M12 — the frame names `load` as a site of the atomicity change and no gate touches it
**minor · Lens 1**

`MISSION_FRAME.md:67-68`: "`save` (`:237`) and `load` (`:220`) — the atomicity change lands
here." `g3-implement` changes `save` only. `load` remains `json.loads(read_text())` and
surfaces a bad or missing document as an unhandled traceback (pasted in S3). The read side is
neither in scope nor listed in "Out of Scope."

**Smallest fix.** Move `load` to Out of Scope with one sentence, or add a `try/except` that
refuses with the path named.

### M13 — no gate carries the tool's own description, and the doc leans on it
**minor · Lens 1**

`DESIGN_CONVERGENCE.md:201` justifies A partly on "its own honest description." Nothing in the
9 gates requires the description to say what the tool widens. `spine_open`'s description is
what the doc holds against B (`:38`, "it 'acts on a spine that does not exist yet'"), so tool
descriptions are treated as load-bearing security artifacts elsewhere.

**Smallest fix.** A postcondition grepping the new tool's description for the reach it grants.

---

## NOTES

### N1 — claim verification summary (all four load-bearing claims the brief named)

| Claim | Verdict |
|---|---|
| `checklist_engine.save()` ends in a non-atomic bare `write_bytes` | **TRUE.** `scripts/checklist_engine.py:256`: `Path(path).write_bytes(payload)`, after `_dominant_newline(path)` is read at `:251`. Truncate-then-write, no temp, no rename. |
| `tests/test_mcp_identity.py:817` would flag a property named `spine_file`, and that is the pin's own positive control | **TRUE and exact.** Pin at `:817`, markers at `:754` include `"spine"`, and `test_the_pin_can_fail` at `:839` plants literally `{"spine_file": ...}`. See S6 for the trap this creates. |
| `tests/test_mcp_lifecycle.py:135` holds `ALLOWED = {"_spine_open", "_spine_close"}`; adding a name widens an allow-list without loosening a ban | **TRUE, and the argument is sound but incomplete.** `:135` verbatim. The pin (`:137-154`) asserts a *shape*: every `Return` in `call_lifecycle_tool` must be a bare `Call` to a `Name` in `ALLOWED`. A third named dispatch function preserves that shape exactly, and the failure text at `:151-153` does endorse it ("Route new lifecycle logic through its own top-level dispatch function"). The positive control at `:156` is independent of `ALLOWED`'s contents (it plants a mutate-then-return) so it stays a real control — unlike S6's case. **What the argument omits:** this pin says nothing about what the new dispatch function *does*. The only thing standing between `_spine_bind` and a second identity-assignment site is the module-wide binder pin at `:563`, which the frame correctly identifies as "the strongest constraint in the frame" (`MISSION_FRAME.md:82-83`). The plan should say that the allow-list widening is safe *because* `:563` covers the residual, and require `:563` to be run — which `g2-integrate c1` does. |
| Census: 52 / 4 / 48 / 0 | **SUBSTANTIALLY REPRODUCED at 53 / 4 / 49 / 0**, and 54 seven minutes later. See S1. The `origin.work_id = 4` and `neither = 0` figures match exactly under three independent predicates, and the recommendation's correction does not turn on the delta. |
| `map/ids.jsonl` tracked and 0 bytes; `map/INDEX.md` ~29KB | **TRUE.** `ids.jsonl` 0 bytes, `INDEX.md` 29449 bytes, both in `git ls-files map/`. |
| C's `674` legal `--from-child` targets | **REPRODUCED EXACTLY** (files with a `consolidation` key under `<root>/.agent-work/`, archive included). |

### N2 — ruling on the `c6` verify-frame waiver: legitimate in form, a rigor dodge in effect

`MISSION_FRAME.md:140` says the `plan` step's `c6` verify-frame gate "cannot be satisfied by
any frame, so it will be taken as a **recorded waiver**, not a silent skip," escalated to the
Admiral.

The premise is true (N1: `ids.jsonl` is empty), the disclosure is exemplary, and the escalation
is the sanctioned route. I would not call it dishonest.

I would still call it a dodge, for one reason: the frame conflates *"no map ids exist"* with
*"this frame's anchors cannot be verified."* The second does not follow. The frame's anchors
are `path:symbol:line`, and **they are mechanically checkable** — I checked seventeen of them
in about four minutes (N1, M7) and found two wrong. A blanket waiver discharges the gate and
lets those two through; the frame's own boast about catching the launch order's stale `:164`
shows it knows the value of exactly this check.

A waiver is for a gate whose *property* is unavailable. Here the property — "the frame's
anchors resolve to real code" — is fully available; only the *citation format* the gate
demands is unavailable.

**Smallest fix.** Do not waive. Substitute one command postcondition at the same rigor level:
for each `path:symbol:line` anchor in the frame, `grep -n` the symbol and assert the line
matches. That converts an unsatisfiable-as-written gate into a satisfiable one and costs a
ten-line script.

### N3 — what actually convinced me, and where the documents are strong

I want the human to weigh these against the blocking findings, because they are real:

1. **`DESIGN_CONVERGENCE.md:140-170` is the best passage in either document.** Candidate A
   named its own falsifier; the author ran it; it failed; the recommendation changed. And the
   author noticed *why* he nearly missed it: "an implementer testing this feature on its own
   spine would have seen it work while it failed on every spine the issue names — a check that
   cannot fail" (`:168-170`). That is the discipline the rest of the plan needs applied to
   itself. My independent census confirms the mechanism (all four `origin` bearers are
   `init_work_area.py --spine` mints) and the fix (52/52 → 53/53 coverage).
2. **The `ALLOWED` allow-list-vs-ban distinction is correct** (N1), and the record that a
   previous lane's "extend a pin" proposal was corrected by a cold critic
   (`DESIGN_CONVERGENCE.md:269-272`) is the right way to carry a superseded decision forward.
3. **The reach delta is stated in prose rather than left for tests to certify**
   (`:218-223`, "**That is a real widening on a security boundary.**"). Most designs would not
   have written that sentence. My complaint (B1) is that it was written without a number
   beside it, not that it was hidden.
4. **`decision:atomicity-is-not-mutual-exclusion` is carried into the implementer's docstring
   as protected intent** (`execute.json:384`), with the lost-update half explicitly out of
   scope and the reason given. That is the correct handling of a partial fix, and it is exactly
   what prevents the atomicity change from being read later as concurrency safety.

None of that changes B1 through B5. In particular: a design document that names its widening
honestly, and a gate plan that cannot detect whether the widening happened, are the same
lane.

---

## Lens coverage, explicitly

**Lens 1 — intent-fit.** The plan does not produce the mission; it produces artifacts about
the mission (**B3**). No gate close criterion requires `spine_bind` to exist, work, or refuse
anything; the g2/g3 chain closes on two crew self-reports plus suites that are green today.
Two obligations the convergence declares undodgeable — the `IDENTITY_TRADE.md` amendment and
a property-scoped pin exemption — appear in zero gates (**B4**). A human-settled decision,
`net-deletion`, is cited nine times and delivered zero times (**S9**). The security property
the plan is meant to preserve is contradicted inside the design document itself (**B2**) and
argued on an unmeasured axis (**B1**). What is missing from the 9 gates entirely: a check on
the tool's description (**M13**), a check on the fenced rail strings (**S10**), any execution
of `spine_lifecycle`'s or the new atomicity module's tests (**S4**, **S5**), and any
deletion.

**Lens 2 — testability / falsifiability.** Checks that cannot fail, named: all four command
postconditions pass at base (**B3**); `g1 c1` is a `grep` for a word (**M11**); `g4 c1`
exercises a read-only verb to prove a write-path change and is cwd-dependent (**S3**); the
reach-delta negative test and the fresh-process proof are Commander attestations with
`check: null` (**S2**); the new atomicity module is in no command (**S4**); the identity pin's
positive control will be structurally decoupled from the pin it controls (**S6**); the rail
strings' byte-identity is asserted everywhere and checked nowhere (**S10**);
`g3-implement p1` is a precondition that cannot be false (**M10**). On the two proofs the
brief asked about: the plan **does not force** the reach-delta negative test to exist (its
only gate is an attestation, **S2**), and it **does demand** the red-proof in prose
(`execute.json:458`, `:482`, `:530`) but attaches it to no check — `g3-integrate c1` runs a
suite that is green at base, so a red-proof that was never performed closes the gate
(**S4** + **B3**). The red-proof also needs a design the plan does not specify: a threaded
race against `write_bytes` is *timing-dependent*, so it can be flaky-green against the old
implementation and thereby fake its own red. The discriminating version is mechanical, not
racy — assert that `save` never opens the target path for writing (only a temp sibling) and
that the target's inode changes exactly once, which is deterministic and fails cleanly
against the old code.

**Lens 3 — simplicity / YAGNI.** What can be deleted: the whole tool, possibly. The
population objection is answered by naming one exception rather than by counting the
population (**S7**), and the doc's own reasoning for killing C's per-dispatch `SPINE_ROOT`
("a launcher that knows the path can set `SPINE_FILE` in the same breath") applies verbatim
to the Admiral case that is supposed to defeat the objection. The exchange — a widened
security boundary for a capability — is priced against an unmeasured reach (**B1**) and
justified by a guard the recommendation itself depends on and does not strengthen (**S8**).
Cheaper designs dismissed too quickly: the launcher fix plus a better refusal message
(raised at `:279-281` and dropped in the same sentence), and `SPINE.parent` as the
containment root — which the doc *measured as safe* ("its reach delta is exactly two files
in a real work area," `:104-107`) and discarded on a general-case argument, when B1 shows the
chosen root is ~4204 files instead of two. If the Admiral case is genuinely the only caller
that cannot be launched bound, the smallest thing that solves this lane is a better
`_unbound_refusal` message naming the `SPINE_FILE` relaunch, plus the `save()` atomicity fix
— which is roughly half of `g3` and none of `g2`. The atomicity half of this lane is
independently worth doing and should not be held hostage to the door half.
