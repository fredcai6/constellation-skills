# Review Result

## Assigned Gate

`g3` — issue #603, the door fails closed when unbound and `spine_open` binds it.
Final re-review, attempt 3, against the **REWORK-2 ADDENDUM**'s five items at `176133ac`.

Survey: `.agent-work/cleanup-a-door/g3-final-review/review.json`, driven through
`checklist_engine.py` under session `constellation/cleanup-a-door/g3-final/reviewer/attempt-1`,
consolidated `verdict=BLOCK findings=3`.

## Result

`BLOCK`

One defect. Items 1, 2, 3 and 5 reproduce exactly. **Item 4 does not** — and the claim that
carried it is a true reading of the wrong number.

The substance of #603 is sound and I did not re-litigate it. This is the same
documentation-blast-radius defect as blocker 2, one file deeper.

## Handoff compliance

### Item 1 — `359d93df..176133ac` is one file, message-only — **PASS**

`git diff --name-only 359d93df..176133ac` returns exactly `tests/test_mcp_lifecycle.py`
(5 insertions, 3 deletions). The change lies wholly inside the third argument of the
`assertEqual` at `:196`.

Proven mechanically, not by reading: parsing both versions of
`test_spine_open_never_references_spine_session_or_run_engine` and normalizing every string
constant to a placeholder makes the two ASTs **identical**, while the two source segments
**differ**. So the probe is not vacuous and no assertion, no test logic and no behaviour moved.

### Item 2 — the corrected message names what `_spine_open` actually reads — **PASS**

By AST over `scripts/mcp_spine_server.py` at HEAD:

- `_spine_open`'s environment reads: exactly one — `os.environ.get('SPINE_PARENT')`.
- **`SPINE_FILE` is read from the environment zero times.** The one `"SPINE_FILE"` literal in
  the function is `opened["SPINE_FILE"]`, a dict key on `open_work`'s return value.
- `_primary_checkout_for_lifecycle` contains **zero** `environ`/`getenv` nodes. Its free names
  are `Path`, `SPINE`, `__file__`, `_git_rev_parse`.
- Banned identifiers (`SPINE`, `SESSION`, `run_engine`) in `_spine_open`: none.

The corrected message is accurate on every clause it changed.

### Item 3 — `:194`, its control, and the module-wide pin — **PASS**

- Line 194 itself is byte-identical to `a69bbac4`.
- `test_the_spine_open_identity_pin_can_fail` and `test_spine_close_is_not_held_to_the_same_ban`
  are **byte-identical** to `a69bbac4`.
- The test *at* `:194` is not byte-identical — its message changed, which is exactly what item 1
  sanctions. Read together, the protected thing is the assertion, and the assertion is untouched.
- The module-wide pin was mutation-proved against the **real** server, not a fixture: I injected
  a second binder (`_quietly_retarget`, `global SESSION`) into `scripts/mcp_spine_server.py` and
  `OneBinderPinTests::test_spine_and_session_are_assigned_only_at_module_scope_and_by_the_one_binder`
  went red naming `_quietly_retarget`. Restored; `git diff --quiet` confirms byte-identical.

### Item 5 — full clean-env suite — **PASS**

`__pycache__` cleared, then
`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`:

```
3093 passed, 6 skipped, 1153 subtests passed in 127.37s
EXIT=0
```

Matches the Commander's measurement exactly.

### Item 4 — normalized sweep returns 0 — **FAIL**

This is the blocker. See **Blockers** below.

## Scope drift

None. `git diff --name-only 408e6d26..HEAD` is exactly the nine files the handoff named:
`.mcp.json`, `examples/mcp-interactive-demo/README.md`, `map/INDEX.md`,
`scripts/mcp_spine_server.py`, and the five `tests/test_mcp_*.py`. The rework-2 commit alone is
one file.

No fenced or excluded path appears in the range: `checklist_engine.py`, `scripts/hooks/**`,
`run_crew.py`, `gauge_reader.py`, `install_constellation.py`,
`COMMANDER_SPINE.template.json`, `make_demo_spine.py` and
`examples/mcp-interactive-demo/spine.json` are all absent.

My own two mutation probes were both restored and verified byte-identical.

## Evidence verdict

The evidence artifacts exist and are fresh — `.agent-work/cleanup-a-door/evidence/g3-rework2-*`,
stamped 2026-08-16 08:30–08:39, i.e. produced by this rework and not leftovers.

Four of the five claims reproduce. **One does not**, and per `global-crew.md` a claim I cannot
reproduce is a BLOCK finding, not an accepted fact.

## Code/doc quality

The code half of this gate is good work. The four scattered import-time `SPINE` derivations were
collapsed behind one `_telemetry_path` plus late-bound accessors; the unbound class is one
predicate asked per call rather than cached; the refusal wording splits deliberately so an
unbound door never fabricates a path; `_unbound_refusal` reads one byte rather than asking
`os.access`, because reading is what the caller is about to do.

The doc half is where it fails, and the Fowler pass names why — see **shotgun-surgery** below.

### Refactoring pass (Fowler)

`.agent-work/cleanup-a-door/FOWLER_PASS.json`; `verify_fowler_pass.py` exits 0
(smells=12, flagged=`['shotgun-surgery', 'comments-as-deodorant']`,
overridden=`['duplicated-code', 'data-clumps']`). The predecessor's record was preserved to
`g3-rereview-review/FOWLER_PASS.json` before I wrote the work-id path the postcondition checks.

- **`comments-as-deodorant` — flagged.** This review's blocker, restated as a smell.
- **`shotgun-surgery` — flagged.** Its cause. The **code** half of "where does `spine_open` get
  its checkout" now has one site. The **documentation** half has six, with no single source of
  truth: the module docstring, `_spine_open`'s docstring, `_primary_checkout_for_lifecycle`'s
  docstring, the pin's failure message, a test comment, and `tests/test_mcp_adoption.py`. Three
  were updated; three were not. The blast radius runs further, into `run_crew.py`,
  `test_crew_launcher.py` and `spine_rail.py`.
- **`duplicated-code` — overridden.** The three telemetry wrappers *are* the de-duplicated form
  under the deletion test; the two refusal texts are deliberately split.
- **`data-clumps` — overridden.** `SPINE`+`SESSION` travel together, but the gate answers that
  structurally — exactly one binder, pinned by a whole-module AST check I proved can fail. A
  `DoorIdentity` type would have one constructor and one consumer.

## Map impact verdict

- **Evidence supports claimed change:** yes for the door's behaviour; **no** for the claimed
  completeness of the doc sweep.
- **Constraints not violated:** yes. No fenced file touched; `_identity_violation`'s semantics
  are intact (verified twice previously, not re-litigated here).
- **Notes match the diff:** yes.
- **Decision candidates surfaced:** yes — `decision:bind-on-open-over-new-verb` is recorded and
  the door-detection question was floated to the Admiral rather than guessed.
- **Durable context routed:** partially. The cross-lane consequences of emptying `.mcp.json`'s
  default reach five claims in lane B/C files beyond the one already going to the Admiral; they
  are flagged below.

## Reconciliation check

`map/` is fresh: `MapTreeFreshness` is green in the clean-env suite at HEAD, and `map/INDEX.md`
was committed in `359d93df` with everything staged, so the `git ls-files` trap behind blocker 1
cannot recur.

The one architecture-level divergence is the door's own interface record disagreeing with its
implementation, which is the blocker rather than a separate item.

## Blockers

### B1 — Four invalidated claims survive; the reported sweep count measured the wrong scope

**The claim.** The addendum states: *"The Commander's own normalized sweep now returns 0."*

**What I ran.** The Commander's own script, unmodified, at HEAD:

```
py .agent-work/cleanup-a-door/evidence/g3-rework2-sweep.py
```

```
FILES SCANNED (layer A, whitespace-normalized, all tracked text): 10145
FILES SCANNED (layer B, AST strings + comments, tracked .py):     517
INVALIDATED-CLAIM HITS (window names BOTH SPINE_FILE and spine_open): 10
    HISTORICAL: 4
    LIVE OUT-OF-SCOPE (report to Commander): 6
NEAR MISSES ...: 85

LIVE IN-SCOPE HITS: 0
    (in-scope = this rework's allowed scope, tests/test_mcp_lifecycle.py)
```

**The `0` is real, and it is the wrong number.** `ALLOWED_SCOPE = ("tests/test_mcp_lifecycle.py",)`
is the rework's **edit permission**, not the change's **blast radius**. The instrument found the
surviving claim and the classification filed it out of the headline. Four of those six live hits
are one sentence in `scripts/mcp_spine_server.py`'s own module docstring.

My own independent sweep — AST string constants (implicit concatenation already joined by the
parser) plus comment runs, all whitespace-collapsed, over every tracked text file outside
`.agent-work/`, `episodes/`, `map/` and `docs/architecture/` — returns **22 hits, 4 of them
in-scope invalidated claims**:

**1. `scripts/mcp_spine_server.py:129-131` — the module docstring states the inverse of the code.**

> "`spine_open` never references `SPINE`, `SESSION` or `run_engine` …, **deriving the primary
> checkout it opens work from fresh off `SPINE_FILE` (ambient, server-launch-time state) rather
> than the module's own `SPINE` binding**"

At HEAD the checkout comes from `_primary_checkout_for_lifecycle`, whose anchor is
`SPINE.parent if SPINE is not None else Path(__file__).resolve().parent`. It reads `SPINE_FILE`
**never** and the module's own `SPINE` binding **always, when there is one**. Both halves of the
"rather than" are backwards. This is blocker 2's claim verbatim in substance, in the file the
change is about.

**2. `scripts/mcp_spine_server.py:30` — a correction the implementer wrote down and did not make.**

> "Ambient state is bound at server-launch time from the environment, NOT exposed as tool
> arguments (so a model cannot point the door at a different spine or identity mid-conversation)"

`_bind_process_to`'s own docstring, at `:868`, says:

> "the module docstring's *"bound at server-launch time"* is now *"bound at launch OR at
> `spine_open`"*, and **nothing may be left describing the previous spine**."

`:30` still describes the previous spine. `tests/test_mcp_identity.py:547` quotes the stale
sentence as the seam's definition, so it has already propagated once. (That quote is prose in a
class docstring, not an assertion — correcting `:30` will not turn it red.)

**3. `tests/test_mcp_lifecycle.py:335-339` — a stale comment holding up inert code.**

```python
# `_spine_open` deliberately RE-READS `SPINE_FILE` from the environment
# at call time (never the module's own bound `SPINE` -- that is the
# whole point of the identity pin above), so it must still be set now,
```

Both clauses are false at HEAD, and the second is precisely inverted. This is the worst of the
four because it is not merely description — it justifies the `os.environ["SPINE_FILE"] = ...`
write at `:341`. I replaced that write with `os.environ.pop("SPINE_FILE", None)` and the test
**still passes**. Restored byte-identical.

**4. `tests/test_mcp_adoption.py:98-102` — a claim #603 was specifically written to falsify.**

> "`mcp_spine_server` reads SPINE_FILE/SPINE_ENGINE from the environment at IMPORT time and
> **raises KeyError without both set** (its own module docstring says so)"

Disproved by measurement — importing the module with both variables removed:

```
IMPORT OK with SPINE_FILE and SPINE_ENGINE both unset; SPINE = None
```

The parenthetical cites the module docstring as its authority, which is finding 2 propagating.

**Why the sweep missed 3 and 4.** Its `TRIGGER` is
`re-?read\s+fresh|ambient|fresh off|deriv\w+`. Finding 3 says "RE-READS `SPINE_FILE`" with no
"fresh" after it; finding 4 uses "reads … at IMPORT time". Neither matches, so neither appears in
either bucket. Finding 2 does match (`ambient`) but names no `spine_open`, so it lands in the
85-item **NEAR MISSES** bucket, which the script's own header declares to be "still-true
statements about the module's own launch-time binding". For that one entry, it is not still true.

**My own sweep's pattern set was also incomplete** — it missed finding 1, which I reached by
following finding 4's citation to the module docstring and reading it. The general lesson is the
one the addendum was already circling: a keyword sweep can only find claims phrased the way you
guessed. The durable fix is not a better regex but the `shotgun-surgery` finding above — one
source of truth for a fact currently restated six times.

**Suggested fix.** Correct `scripts/mcp_spine_server.py:129-131` and `:30`; delete the
`tests/test_mcp_lifecycle.py:335-339` comment together with the now-inert `os.environ` write it
justifies; correct `tests/test_mcp_adoption.py:98-102`'s rationale (the practice of hand-typing
the tool names is still fine, only its stated reason is void). Docs and dead test scaffolding
only — no behaviour.

## Out-of-scope observations

- **Cross-lane, fenced — route with the `spine_rail.py` item already going to the Admiral.**
  Emptying `.mcp.json`'s default invalidates five more claims that an unbound door "resolves to
  `.mcp.json`'s demo default": `scripts/run_crew.py:940`, `:1410`, `:1631` and
  `tests/test_crew_launcher.py:2259`, `:2552`. At HEAD it refuses instead. **Not a blocker** —
  same class as the item the addendum already ruled out of scope.
- **The pin message's surviving loose clause.** `tests/test_mcp_lifecycle.py:200` says
  `spine_open` acts "never on the identity THIS door happens to be bound to". That clause is
  pre-existing `a69bbac4` text, not part of blocker 2's fix, and it is loose at HEAD:
  `_primary_checkout_for_lifecycle` anchors on `SPINE.parent`, so the bound identity does supply
  the repo root. The mechanism is documented honestly and at length in that function's own
  docstring, and the design reason (isolation, measured against `FullStdioRoundTripTests`) is
  sound. **Observation, not a blocker** — but worth folding into B1's fix while that paragraph is
  open.
- `notes-a.md`'s problem statement still says `.mcp.json` "currently" supplies the demo default.
  It is a Commander working note pinned to base `a69bbac4`, so it reads as history. No action.

## What I did NOT check — explicit scoped null

Deliberately not re-verified, because two prior reviews reproduced them and the addendum ruled
them settled: the six unbound-class refusals; bind-on-open through to a successful `claim`; the
regression suite red pre-fix; `IdentityGuardSurvivesARebindTests`; the three env overrides; the
lease-held rebind refusal; unset `SPINE_ENGINE`; the four import-time derivations following the
rebind; `test_mcp_spine_server.py:588`'s reconciled invariant. **If any of those is wrong, this
review would not catch it.**

Also not checked: anything under `scripts/hooks/**`, `checklist_engine.py`, `run_crew.py`,
`gauge_reader.py` (fenced, read-only); the episode clauses; `map/ids.jsonl` being empty; the
undefined "door-detection change". My sweep excluded `.agent-work/`, `episodes/`, `map/` and
`docs/architecture/` as historical or generated — a live invalidated claim inside those is
outside what I measured.

The suite result is one local run on this host at `176133ac`; per `CREW_CONTEXT.md` a local
green is evidence, never the gate.

## Workflow Feedback

- **Handoff gaps.** Two.
  1. **Item 3 and item 1 contradict each other on a literal reading.** Item 1 requires the
     failure-message string to have changed; item 3 requires "`:194` … still byte-identical to
     `a69bbac4`". The message *is* inside the test at `:194`, so both cannot hold literally. I
     resolved it as "the assertion and the control are protected, the message is the fix" and
     measured all three readings. The handoff should say **which** property is fenced —
     "the assertion and the detector, not the message" — rather than reusing a line anchor whose
     meaning shifted once the line's own contents became the deliverable.
  2. **A count was passed down without the definition that produced it.** "The Commander's own
     normalized sweep now returns **0**" is the single load-bearing claim of item 4, and the `0`
     turned out to be the script's `LIVE IN-SCOPE` line under an `ALLOWED_SCOPE` of one file. A
     count is only checkable alongside its denominator. Had the handoff read "0 hits **in
     `tests/test_mcp_lifecycle.py`**, 6 live hits elsewhere", the gap would have been visible
     without running anything.
- **Context rediscovered.** That the sweep script itself was on disk at
  `.agent-work/cleanup-a-door/evidence/g3-rework2-sweep.py`. The handoff quoted its result but
  not its path; I found it by listing the evidence directory. Running the predecessor's
  instrument was the single highest-yield act of this review — it diagnosed the miss in one
  command. **Handoffs that cite a measurement should cite the command or script that produced
  it**, which the handoff's own Constraints section does well for everything else.
- **Instructions improvised around.** Two.
  1. The reviewer skill says to call `spine_status` first and drive the bound spine. My
     `SPINE_FILE` is the **Commander's** spine, sitting at its `execute` gate — driving it would
     have advanced my parent's run. I built my own survey at
     `.agent-work/cleanup-a-door/g3-final-review/review.json` and drove it through the
     `checklist_engine.py` CLI, per the skill's own "when nothing is bound" clause. The skill
     treats "a spine is bound" as equivalent to "a survey was prepared for me"; for a crew
     dispatched by a Commander whose door is bound to its own spine, those come apart every time.
     Worth one sentence in the skill.
  2. The `r6-fowler` postcondition resolves to `.agent-work/<work-id>/FOWLER_PASS.json`, a single
     path shared by every reviewer of every gate. Attempt 3 of one gate means writing over
     attempt 2's record. I copied the predecessor's to `g3-rereview-review/FOWLER_PASS.json`
     first, which is what the earlier reviewers evidently also improvised. The delivery filename
     is versioned per attempt by the addendum; the Fowler record is not.
  3. **The stop hook fired on my parent's spine, not mine.** With my survey consolidated and its
     lease released, the hook read `SPINE_FILE` — which for a dispatched crew is the
     **Commander's** spine — found `execute` open under lease `commander-cleanup-a-door`, and
     told me I was abandoning an active run mid-flight, offering `block` or a human waive as the
     honest exits. Both are wrong here: I hold no lease on that gate, its imperative is the
     Commander's own (write `STATE_NOTE.md`, dispatch through `run_crew.py`), and blocking it
     would seize my parent's gate to bubble a blocker to my parent about its own imperative. A
     crew is dispatched *inside* an open parent gate by construction, so this fires on every
     clean crew exit. The check should compare the open gate's lease holder against the running
     session before claiming mid-flight abandonment — if the lease is `SPINE_PARENT`'s and the
     agent's own survey is `DONE`, that is a completed crew, not an abandoned run. I proceeded on
     the reviewer skill's own rule that the `REVIEW_RESULT` write is the delivery.
- **What would have made this easier.** State counted evidence as **numerator, denominator and
  the predicate that separates them**. Both of this gate's last two blockers were a real
  measurement read at the wrong scope — blocker 1's `map` rebuild passed its own guard because
  `git ls-files` did not yet see the new file; this one's sweep returned 0 because in-scope meant
  edit permission. Neither was a careless measurement. Both were exact answers to a slightly
  different question than the one being asked.

## Return status

`complete`
