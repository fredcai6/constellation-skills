# Implementation Result

## Assigned gate

`g3` — issue #603, rework 3 (attempt 4, final within the rework cap).

## Completed slice

The handoff named four surviving invalidated claims. There were **seven**. All seven are
corrected. Two more survive in **fenced** files and are reported below, not fixed.

No behaviour changed. The diff is docstrings, comments, one deleted test-setup line, and one
Markdown paragraph.

## Read this first: three departures from the literal allowed scope

Each is a prose-only correction of the same falsified claim, in a **non-fenced** file, made
because the close criterion demands **0 live invalidated claims in `scripts/`, `tests/`,
`examples/`, `docs/`** and leaving them would have failed that criterion. I am naming them
here rather than burying them, because scope is the reviewer's call, not mine.

| # | Where | Allowed scope said | Why I corrected it anyway |
|---|---|---|---|
| 5 | `tests/test_mcp_adoption.py:172-179` | "the rationale at `:98-102`" | Same file, same claim, different lines. Fixing 4 of 5 and reporting the 5th would reproduce the exact mistake this rework exists to correct. |
| 6 | `tests/test_mcp_identity.py:18-23` | "the quoted stale sentence at `:547` only" | Same file, same claim class, different phrasing. Prose in a module docstring, not an assertion. |
| 7 | `docs/CHECKLIST_ENGINE_DESIGN.md:295` | not listed at all | `docs/` is named in the close criterion and is not on the fenced list. Prose only. |

If the reviewer rules any of these out of bounds, each reverts independently: they touch no
code and no assertion.

## Scope

**Files changed** (commit `5a626351`):

- `scripts/mcp_spine_server.py` — docstrings only (findings 1, 2)
- `tests/test_mcp_lifecycle.py` — one comment and one inert line deleted (finding 3)
- `tests/test_mcp_adoption.py` — comment and docstring rationale (findings 4, 5)
- `tests/test_mcp_identity.py` — two docstring quotes (findings 2b, 6)
- `docs/CHECKLIST_ENGINE_DESIGN.md` — one paragraph (finding 7)

**Specific exclusions touched:** `no`. `tests/test_mcp_lifecycle.py:194` and its positive
control are byte-identical — `diff` over lines 183-300 against HEAD is empty.
`_identity_violation`, `checklist_engine.py`, `scripts/hooks/**`, `run_crew.py`,
`gauge_reader.py`, `install_constellation.py`, `episodes/**` and `map/**` are untouched. The
six restatements were not refactored into one source of truth.

## Behavior changed

`no`. Proven by construction rather than by reading the diff — see Evidence §5.

## The four named corrections

### 1. `scripts/mcp_spine_server.py:129-131` — the anchor claim, inverted both ways

**Before:** "`spine_open` never references `SPINE`, `SESSION` or `run_engine` (checked …),
deriving the primary checkout it opens work from fresh off `SPINE_FILE` (ambient,
server-launch-time state) rather than the module's own `SPINE` binding".

**After:** "… never references `SPINE`, `SESSION` or `run_engine` **in its OWN source**
(checked …), taking the primary checkout it opens work from `_primary_checkout_for_lifecycle`
instead. That helper reads no environment at all — not `SPINE_FILE`, not anything: it anchors
on the BOUND spine's own directory when there is one, and on THIS SCRIPT's own when there is
not. The identifier ban is on `_spine_open`'s own source, which that helper is not, so what
the ban buys is that no ARGUMENT on the call can redirect the open onto the bound spine —
never that the bound spine is invisible to the tool."

Measured, not copied from the handoff: the AST reports the anchor as
`SPINE.parent if SPINE is not None else Path(__file__).resolve().parent` and zero `SPINE_FILE`
references in the helper's executable body.

I sharpened rather than merely inverted the sentence. The old text implied the ban meant "the
bound spine is never consulted" — which is what made an inverted sentence read as plausible
for three attempts. The real property is narrower and checkable: no argument can redirect the
open.

### 2. `scripts/mcp_spine_server.py:30` — the correction written down and not made

**Before:** "Ambient state is bound at server-launch time from the environment, NOT exposed as
tool arguments (so a model cannot point the door at a different spine or identity
mid-conversation):"

**After:** "Ambient state is bound at launch OR at `spine_open` — at launch from the
environment, and thereafter by `_bind_process_to`, the one place `SPINE` and `SESSION` are
assigned outside module scope, when a successful `spine_open` binds this process to the spine
it just minted (`decision:bind-on-open-over-new-verb`, issue #603). What did NOT change is
that neither is ever exposed as a tool argument, so a model still cannot point the door at a
different spine or identity mid-conversation, and `_rebind_refusal` still blocks the swap
while this process holds an active lease — one spine per process stands. The values:"

The wording `_bind_process_to:892` prescribes, plus the two invariants that survived — so the
correction cannot be misread as a loosening it is not.

**2b. `tests/test_mcp_identity.py:547`** — the quote updated to the corrected sentence, then
saying *which half* is DC3's seam (launch-from-the-environment), with the `spine_open` half
noted as out of DC3's scope rather than silently dropped.

### 3. `tests/test_mcp_lifecycle.py:335-341` — comment and inert write, deleted together

Both clauses were false and the second exactly inverted. **Inertness was proven before the
deletion, and proven harder than "remove it and see":** I replaced the write with
`os.environ.pop("SPINE_FILE", None)` — actively *removing* the variable rather than merely not
setting it — and asserted in Python that the substitution matched exactly once, because a
`sed` that matches nothing leaves a green suite that reads exactly like a passing guard.

```
MUTATION APPLIED (assert confirmed it matched exactly once)
341:  os.environ.pop("SPINE_FILE", None)  # MUTATION: inertness probe
$ pytest tests/test_mcp_lifecycle.py -k escape   ->  1 passed
$ pytest tests/test_mcp_lifecycle.py             ->  18 passed
```

Restored from a byte-copy, confirmed `git diff` empty, then made the real deletion. Suite
green again: 18 passed. The stop condition "the write turns out **not** to be inert" did not
fire.

### 4. `tests/test_mcp_adoption.py:98-102` — a rationale #603 falsified

**Before:** "… `mcp_spine_server` reads SPINE_FILE/SPINE_ENGINE from the environment at IMPORT
time and raises KeyError without both set (its own module docstring says so), so importing it
here would make collecting this file itself require a bound spine."

**After:** "… because importing `mcp_spine_server` is not side-effect-free. At module scope the
door binds `SPINE` and `SESSION` from whatever the AMBIENT environment happens to hold, and it
does `sys.path.insert(0, ENGINE.parent)` in the importing process. Either at COLLECTION time
would tie this file's collection to the collecting shell's environment, before any test could
supply a scratch one. (An unbound door has been a first-class state since issue #603: with
neither variable named, the module-scope binding is simply `SPINE = None`.)"

The replacement reason is **measured, not asserted**: the check reads the door's module-scope
statements from the AST and confirms both side effects are really there, so the new rationale
is not a second wrong reason.

**One thing I did and want on the record:** my first draft retracted the old claim by quoting
it ("the reason this used to give … is void"). My own predicate flagged it. I could have
taught the predicate to excuse retractions; I reworded instead. A sweep that understands
negation is a sweep that can be talked out of a finding, and being talked out of findings is
how the previous two attempts reported zero.

## The three the handoff did not know about

**5. `tests/test_mcp_adoption.py:172-179`** — `_load_mcp_spine_server`'s docstring carried the
identical falsified claim. Found by scanning the whole file instead of the line range I was
pointed at.

**6. `tests/test_mcp_identity.py:18-23`** — "binds its ambient state (SPINE_FILE, SPINE_ENGINE,
SPINE_SESSION) from the environment **at server-launch time**". Different words for finding 2,
which is why my own narrower m2 check could not match it; the sweep's claim-class predicate
caught it.

**7. `docs/CHECKLIST_ENGINE_DESIGN.md:295`** — "The server binds `SPINE_FILE`, `SPINE_ENGINE`
and `SPINE_SESSION` **at launch from its environment**". Matched **no predicate at all**. I
found it only by reading the 271-fragment source dump by hand.

Finding 7 is the most important result in this report. It is direct evidence that the sweep's
value is as a **funnel a person then reads** — 207,254 fragments narrowed to 271 — and never
as an oracle. Had I trusted the classifier's headline, this rework would have shipped with a
live invalidated claim in `docs/`, which is exactly how the last two attempts failed.

## Stop conditions hit

**One: live invalidated claims in fenced files. Reported, not fixed, as instructed.**

**`scripts/run_crew.py:468-471`** — a genuine surviving instance of finding 4's exact claim:

> "that module reads `SPINE_FILE` and `SPINE_ENGINE` straight out of the environment at import
> time (raises `KeyError` if either is unset) so importing it here would make importing
> `run_crew` itself require a bound spine even for callers — the CLI, the test suite — that
> have no spine to bind."

Measured false: import with both variables unset succeeds and leaves `SPINE = None`. The
practice it defends (hand-typing the `mcp__spine__*` names) is still fine; only the stated
reason is void — the same shape as finding 4, and it wants the same correction.

**`tests/test_mcp_lifecycle.py:200`** — borderline. The `spine_open` identity pin's failure
message says `spine_open` "must act purely on server-launch-time state". Since bind-on-open,
the `SPINE` that `_primary_checkout_for_lifecycle` anchors on need not date from launch. The
parenthetical immediately after it names exactly what is read and is correct, and rework 2
already corrected this text at `176133ac`. `:194` and its positive control are fenced
byte-identical by three reviews, so I have not touched it. **The reviewer should rule.**

**A conflict in the handoff, surfaced rather than quietly resolved.** The close criterion
demands 0 live invalidated claims in `scripts/`, but `scripts/run_crew.py` is both in
`scripts/` and on the fenced list. I read the criterion as *0 in non-fenced source files, with
fenced ones reported* — the handoff itself fences `spine_rail.py`'s known claim the same way —
and I am stating the interpretation instead of picking one silently.

## Map Impact

- **Structural anchors touched:** none. `map/ids.jsonl` is empty and no entity changed; no
  `map/` rebuild was needed or done.
- **Capabilities added/changed/affected:** none — no behaviour changed.
- **Constraints/assumptions touched:** `decision:bind-on-open-over-new-verb` and
  `decision:one-spine-per-process-stands` are now described correctly at
  `scripts/mcp_spine_server.py:30` and `docs/CHECKLIST_ENGINE_DESIGN.md:295`; both were
  previously described as launch-time-only binding.
- **Claims/evidence produced:** the door's documented identity model now matches its measured
  one across seven restatements. Backed by the four per-finding checks and the sweep, all with
  demonstrated failing controls.
- **Trust limitations / drift found:** **the durable cause is unfixed.** Seven copies of one
  fact across five files, and every attempt at this gate has missed at least one. The handoff
  forbids refactoring them into one source of truth and files it as triage — correctly, it is
  a design change — but until that lands, this class of defect will recur. Finding 7 is the
  proof: it survived four attempts and two purpose-built sweeps.
- **Triage candidates:**
  1. `scripts/run_crew.py:468-471` — same falsified rationale, fenced (above).
  2. `tests/test_mcp_lifecycle.py:200` — "purely on server-launch-time state", fenced (above).
  3. `tests/test_mcp_lifecycle.py:335,343-346` — residual dead scaffolding (below).
  4. The seven-restatement shotgun-surgery pattern itself — already being filed.

## Test mode

**Required:** `evidence-only / inspection` — inferred, not stated (see Workflow Feedback). No
behaviour change is permitted, so TDD does not apply.

**Satisfied:** `yes`. Every correction carries a check that ties prose to a measured fact, and
every check was demonstrated capable of failing against the exact text it was written to catch.

## Evidence

All scripts live in `.agent-work/cleanup-a-door/evidence/`.

### 1. Per-finding checks, each with a demonstrated control

```bash
py .agent-work/cleanup-a-door/evidence/g3-rework3-anchor-check.py --demo-control
py .agent-work/cleanup-a-door/evidence/g3-rework3-anchor-check.py
py .agent-work/cleanup-a-door/evidence/g3-rework3-binding-check.py --demo-control
py .agent-work/cleanup-a-door/evidence/g3-rework3-binding-check.py
py .agent-work/cleanup-a-door/evidence/g3-rework3-inert-check.py --demo-control
py .agent-work/cleanup-a-door/evidence/g3-rework3-inert-check.py
py .agent-work/cleanup-a-door/evidence/g3-rework3-adoption-check.py --demo-control
py .agent-work/cleanup-a-door/evidence/g3-rework3-adoption-check.py
```

**Result:** all `pass`. Selected output:

```
CONTROL OK: predicate C flags the pre-change sentence -> 'primary checkout it opens work from fresh off `SPINE_FILE'
PASS  anchor claim agrees with the code
  A. _primary_checkout_for_lifecycle references SPINE_FILE 0 times
  B. anchor = SPINE.parent if SPINE is not None else Path(__file__).resolve().parent

CONTROL OK: predicate B flags scripts/mcp_spine_server.py:30 -> 'bound at server-launch time'
CONTROL OK: predicate B flags tests/test_mcp_identity.py:547 -> 'bound at server-launch time'
PASS  no launch-time-only binding claim survives  (1611 prose fragments scanned)

CONTROL OK: predicate C flags the deleted comment -> '_spine_open` deliberately RE-READS `SPINE_FILE'
CONTROL OK: predicate B flags the deleted setup write and ignores the restore beside it
PASS  the inverted comment and its inert write are gone
  A. _spine_open reads os.environ once: os.environ.get('SPINE_PARENT')

CONTROL OK: predicate B flags the deleted rationale -> 'IMPORT time and raises KeyError'
PASS  the import-time-KeyError rationale is gone and its replacement is true
  A. measured: import with both vars unset -> SPINE= None
  C. module scope really does: ['SPINE: Path | None = _spine_from_env()',
     "SESSION = os.environ.get('SPINE_SESSION', '')"]; ['sys.path.insert(0, str(ENGINE.parent))']
```

**A control earned its keep.** The binding check's first predicate reported the corrected files
clean **and the pre-change sentences clean** — its negative-lookahead alternative `OR at`
matched unanchored inside "point the d\[oor at] a different spine", excusing every stale claim
nearby. Word-boundary anchoring fixed it. Without running the predicate against the text it was
written to catch, I would have shipped a check that could not fail.

### 2. Proof the deleted `:341` write is inert

See §3 above: the test passes with `SPINE_FILE` **actively removed**, not merely left stale —
consistent with `_spine_open`'s only environment read being `os.environ.get('SPINE_PARENT')`.

### 3. The blast-radius sweep

```bash
py .agent-work/cleanup-a-door/evidence/g3-rework3-sweep.py --controls
py .agent-work/cleanup-a-door/evidence/g3-rework3-sweep.py --assert-clean
```

**Result:** `pass`, exit 0.

| measure | count |
|---|---|
| tracked files listed | 10,178 |
| files with readable prose (**scanned**) | 9,971 |
| prose fragments scanned | 207,254 |
| tier 1 — mentions any touched identifier | 2,689 |
| tier 2 — must be read | 1,109 (271 in the source tree) |
| matching a claim class | 128 |
| classified **and** in the source tree | 21 |
| **live invalidated claims, non-fenced source** | **0** |
| live invalidated claims, fenced (reported) | 2 |

**Scoped to blast radius, not to edit permission.** Every tracked file is scanned regardless of
whether I could touch it — that inversion is the whole point.

**Designed against all three prior failures.** Prose is read from **AST string constants** (the
parser has already joined implicit concatenation — this is what defeats the split-literal
miss) plus **comment runs** joined across consecutive lines, everything whitespace-collapsed.
Triggers are the **identifiers** `#603` touched, never remembered phrasings. And the classifier
is **advisory only**: `--assert-clean`'s exit code comes from a per-hit ledger I filled in by
reading.

**The loop asserts what it looped over.** `scanned_files`, `scanned_frags` and `tier1` are all
asserted non-zero, so a broken extractor dies rather than reporting clean.

**Tier 2 is a union, and the controls are why.** My first cut defined it by distinctive
identifiers alone; `--controls` proved that would have missed findings 2 and 2b, which name no
distinctive identifier at all. It is now *distinctive identifier* **OR** *claim class* — neither
alone catches all six known claims:

```
OK   finding 1 (split across LITERALS)   tier2=True (distinctive-id=True,  classes=['b','c'])
OK   finding 2 (:30)                     tier2=True (distinctive-id=False, classes=['b'])
OK   finding 2b (identity quote)         tier2=True (distinctive-id=False, classes=['b'])
OK   finding 3 (split across LINES)      tier2=True (distinctive-id=True,  classes=['d'])
OK   finding 4 (adoption rationale)      tier2=True (distinctive-id=True,  classes=['a'])
OK   finding 5 (_load_mcp_spine_server)  tier2=True (distinctive-id=True,  classes=['a'])
CONTROLS OK: all 6 corrected claims land in tier 2 and would be read.
```

**Hits read and dismissed** — all 21 classified source hits, each with a written disposition in
the ledger (full text in `g3-rework3-sweep-report.txt`, 1807 lines):

- **6 accurate** — past-tense records of what `#603` fixed, in `_spine_from_env`,
  `_unbound_refusal`, `_bind_process_to`, `test_mcp_door_unbound.py` (×2),
  `test_mcp_identity.py:494`. These are history and rewriting them would erase the record that
  makes the current shape legible. One is an assertion *message* that prints only if the door
  *does* die — the test asserts the opposite of the sentence.
- **13 unrelated** — the class predicates are broad on purpose (a false alarm costs a read, a
  miss costs the gate): companion-import failures (`install_constellation`, `run_crew`'s
  `ModuleNotFoundError`), Python 3.14 frozen-dataclass notes, an eval fixture whose body is
  `print('this check always fails')`.
- **2 live-fenced** — reported under Stop conditions.

The ledger is keyed **per hit**, and a classified source hit absent from it **refuses** rather
than passes — so a claim introduced tomorrow cannot slip through by not being listed. Verified:
a synthetic hit at `scripts/brand_new.py` is refused.

### 4. Full clean-env suite

```bash
find . -name __pycache__ -type d -prune -exec rm -rf {} +
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u SPINE_ENGINE py -m pytest -q
```

**Result:** `pass` — **3093 passed, 6 skipped, 1153 subtests passed, 0 failed** in 128.48s.

Identical to the `176133ac` baseline on all four counts. That identity *is* the no-behaviour-
change evidence: a moved count would have meant an assertion changed underneath me.

### 5. `git diff --stat` and the AST proof of "text only"

```
 docs/CHECKLIST_ENGINE_DESIGN.md |  7 +++++--
 scripts/mcp_spine_server.py     | 27 +++++++++++++++++++--------
 tests/test_mcp_adoption.py      | 23 +++++++++++++++--------
 tests/test_mcp_identity.py      | 22 +++++++++++++++-------
 tests/test_mcp_lifecycle.py     |  6 ------
 5 files changed, 54 insertions(+), 31 deletions(-)
```

I did **not** verify "text only" by reading the diff — reading a diff is precisely the judgment
that has been wrong three times here. I verified it by construction: parse HEAD and the working
tree, strip every docstring, blank every string constant, unparse, compare. Comments never
reach the AST, so anything surviving is real code.

```
scripts/mcp_spine_server.py        IDENTICAL executable skeleton -- prose only
tests/test_mcp_adoption.py         IDENTICAL executable skeleton -- prose only
tests/test_mcp_identity.py         IDENTICAL executable skeleton -- prose only
tests/test_mcp_lifecycle.py        1 executable line(s) changed:
    -        os.environ['<str>'] = str(bound_spine)
TOTAL executable lines changed across all four .py files: 1
```

Asserted `== 1`. The fifth file is Markdown. And `diff` over lines 183-300 of
`tests/test_mcp_lifecycle.py` against HEAD is **empty** — the `:194` pin and its positive
control are byte-identical, as fenced.

## TDD evidence, if required

Not required — no behaviour change. The nearest equivalent is the inertness probe in §3
(observed passing with the variable removed) and the demonstrated failing control on every
check.

## Docs/contracts touched

- `docs/CHECKLIST_ENGINE_DESIGN.md:295` — finding 7; see the scope-departure table.

## Assumptions

- **"0 live invalidated claims in the source tree" means 0 in *non-fenced* source files.**
  `scripts/run_crew.py` is both in `scripts/` and fenced, so no reading satisfies both clauses
  literally. Stated under Stop conditions for the reviewer to confirm or overrule.
- **Test mode is inspection/evidence-only**, inferred from the required-evidence list and the
  no-behaviour-change criterion, since the handoff carries no test-mode field.

## Out-of-scope observations

**Residual dead scaffolding at `tests/test_mcp_lifecycle.py:335, 343-346.`** The deleted write
was bracketed by `saved_spine_file = os.environ.get("SPINE_FILE")` above and a four-line
restore in the `finally` below. Those exist *only* to protect the line I removed, and are now a
no-op that saves a value and hands the same value back. **I did not remove them.** The close
criterion says "one deleted test-setup line" and the stop conditions forbid any logic change
beyond that single write; removing executable lines is a logic change however provably null.
This is the same class as the finding this whole rework is built on — dead scaffolding
surviving because nobody enumerated what a change invalidated — one layer deeper. Cheap to
remove under an explicit instruction.

## Workflow Feedback

- **Handoff gaps:** Two, and the first is the substantive one. **(a) "Allowed scope" and the
  close criterion contradict each other.** Allowed scope is a *line-range* list; the close
  criterion is a *tree-wide* property ("0 live invalidated claims in `scripts/`, `tests/`,
  `examples/`, `docs/`"). A sweep that actually finds everything will find things outside the
  line ranges — it did, three times — and the handoff gives no rule for that case except the
  fenced-file stop condition, which covered only one of the three. This is the same
  edit-permission-vs-blast-radius confusion the handoff itself diagnoses, reappearing in the
  handoff's own structure. **A handoff that demands a tree-wide property must grant tree-wide
  edit permission for that property's own claim class, with fenced files as the explicit
  exception.** **(b) No `test mode` field**, which the template requires; I inferred
  inspection/evidence-only from the required-evidence list.
- **Context rediscovered:** `docs/agents/CREW_CONTEXT.md` says `python3` has no pytest on this
  host (measured 2026-08-10). Today `python3` and `py` both report pytest 9.1.1. I checked
  rather than assuming, as that file instructs — but the pinned measurement is now stale and
  reads as current guidance. It is pinned to a date, which is what let me notice.
- **Instructions improvised around:** The handoff prescribes the sweep method (AST + comment
  runs + identifier triggers) but not how the sweep should *decide*. Given "do not trust the
  classifier to sort them for you", I made the classifier advisory and put the exit code behind
  a per-hit ledger written by reading, with absence-from-ledger as a refusal. Finding 7 —
  matched by no predicate, found only by reading the dump — justifies that choice after the
  fact.
- **What would have made this easier:** One sentence in the handoff: *"Correct every instance
  of these claim classes anywhere outside the fenced list; the line numbers are where they were
  found, not the limit of the work."* That single sentence removes all three scope departures
  above and is the direct fix for gap (a).
- **Harness observation (added after my plan closed).** On finishing — plan `DONE`, lease
  released, this artifact written — the stop hook fired `SPINE MID-FLIGHT: gate execute is
  still open ... ending your turn now abandons an active run`, twice. It is reading
  `SPINE_FILE`, which for a **dispatched crew** is bound to the **parent's** spine
  (`SPINE_SESSION=constellation/cleanup-a-door/execute/commander`), not to the crew's own work
  file. So it reported the Commander's open `execute` gate as my abandoned run. `execute`'s
  lease is `commander-cleanup-a-door`, `claimed_by: commander`; my session does not hold it and
  the engine would refuse me anyway. I did not act on it: driving it would be a lease takeover,
  and `block`-ing it would mark the Commander's own gate blocked because a crew's turn ended —
  a false signal manufactured by the hook's own misattribution. **The hook cannot currently
  tell "this agent abandoned its run" from "this agent is a crew whose door is bound to its
  parent's spine".** Distinguishing them needs the crew's own work file, not `SPINE_FILE` —
  worth fixing, because the instruction it gives a finished crew ("do not end your turn") has
  no compliant action behind it.

## Return status

`complete`
