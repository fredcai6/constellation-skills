# REVIEW_RESULT — g1-review: a gauge reading is named for the agent that produced it (#600)

**Verdict: `APPROVE`** (with one recorded `fail` carried as a finding + triage
candidate; see the override reason).

Work id `cleanup-b-context-identity` · worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`
· branch `cleanup/b-context-identity` · reviewed at HEAD `ccb8b8d8`, diff scoped
to commit `3bc87e93`.

Survey driven through the engine at
`.agent-work/cleanup-b-context-identity/crew-handoffs/g1-reviewer-survey.json`
(session `constellation/cleanup-b-context-identity/g1-review/reviewer/attempt-1`),
all seven items visited and recorded, consolidated `APPROVE findings=1`.

**Authority order followed:** `ADMIRAL_RULING-2.md` (top, amends R4) →
`ADMIRAL_RULING-1.md` R1–R5 → gate imperative checks (a)–(i) → handoff. I took
the implementer's word for nothing; every pasted command below I ran myself.

---

## Summary

The change is correct, and the two things the Admiral explicitly held to in
ruling 2 both hold. The defect is real and I reproduced it in both directions
with the same byte-identical script. Normalization is genuinely total. The
fail-safe direction is preserved everywhere I could reach. No fenced file is
touched, and the in-file claim-path fence — the one that needed real work — holds
under AST comparison.

One finding is carried rather than blocking: **R4 row 2 is implemented and works,
but nothing tests it**, and I proved that by mutation.

---

## Findings

### F1 — R4 row 2 is an untested governor branch · **MEDIUM** · recorded `fail` on `r4-quality` · triage `tc1`

R4 row 2 — *2+ **distinct** candidates all under **one** owner → write **every**
candidate* — is implemented and behaves correctly. I drove it: one binding key,
one `engine_session`, two different work directories → **both** owner-keyed files
written, no sidecars.

**Nothing tests it.** Mutation proof — I reverted the branch to the old
skip-on-count rule:

```
old: unattributable = len(targets) > 1 and (None in owners or len(owners) > 1)
new: unattributable = len(targets) > 1        # MUTANT
```

```
mutation applied and ASSERTED present
616 passed, 237 subtests passed in 4.70s
--- restoring ---
RESTORED byte-identical (git diff clean)
```

All 616 gauge tests stay green with row 2 removed. Every existing
multi-candidate test uses two *different* owners (`eng-1`/`eng-2`) and so
exercises the **skip** branch; the #488 test covers the same-*directory* case,
which dedupes to **one** candidate and never enters the multi-candidate write
loop. A future "simplification" back to a count check would restore the
#488-class dark governor for the multi-directory same-owner case with no failing
test anywhere — the exact silent shape this subsystem has been burned by three
times (#252, #271, #488).

**Why it does not block:** the behaviour is verified correct by direct drive, and
the Admiral's *literally required* test (R4: pin #488's exact shape, assert the
write happens) is present and — verified below — same-owner-discriminating. Row 2
is an additional branch I found uncovered, not the ruling's acceptance criterion.

### F2 — the result's "nothing refuses where it previously permitted" is imprecise · **LOW** · observation

I enumerated the refusal paths rather than sampling them. There are exactly two
consumers that can refuse on a gauge reading, both gated on
`_trip_hard_band_reading` and both **byte-unchanged** by this commit:

1. `scripts/checklist_engine.py:2073` — the begin-work guard on `start`.
2. `scripts/checklist_engine.py:3419` — `advance`'s `require_why` at/over hard.

Two paths **can** now refuse where they previously permitted:

- **(R1)** a leased agent now reads its **own** reading instead of whichever
  agent wrote last, so a genuine over-hard fill refuses where a foreign low
  reading used to permit;
- **(R4/#488)** the same-owner multi-candidate case now **writes** where the
  count-based skip produced silence, and a restored reading can trip.

Both are the ruled-on **purpose** of the change, not side effects, and neither is
a new *class* of refusal. **No new refusal requiring a float.** But the blanket
claim in `g1-implementer-result.md` ("Nothing refuses where it previously
permitted. Every change is in the permit or the quiet direction") is not accurate
as written, and the same document elsewhere states the fact that contradicts it
("now gets a reading where it used to get silence"). Worth correcting in the
record, not worth reworking.

### F3 — the unowned name is hardcoded three times beside its single definition · **LOW** · observation

`gauge_reader.GAUGE_FILENAME` is declared the one definition, but `"gauge.json"`
is also hardcoded at `gauge_writer_hook.py:205`, `:209` and
`checklist_engine.py:1420`. Same drift hazard the change's own design note argues
against. Self-limiting: reachable only when `gauge_reader` failed to load, in
which case no owner-keyed read happens either, so drift degrades to today's
behaviour rather than to a dark governor.

### F4 — `handle_post_tool_use` is long and this change grew it · **LOW** · observation

175 lines / 91 non-comment, with four separate `for ... in targets:` fan-out
loops. Extracting the attribution decision (`owners` set + `unattributable`)
would also give **F1** its natural unit-test seam.

### Note for the record — ruling 2's row attribution

`ADMIRAL_RULING-2.md` point 1 says #488's case "lands in row 2 — write every
candidate". It does not: same directory + same owner **dedupes to a single
candidate** (row 1), and takes the single-candidate write branch. The **outcome**
the Admiral required — it still writes — holds, and the required test is present
and discriminating, so the ruling is satisfied. Only its row attribution is off
by one row. Flagging because ruling 2 is the top authority and should be accurate.

---

## The three departures — adjudicated

### 1. R4 narrowed in one branch — **RESOLVED by the Admiral, not mine to adjudicate**

Per the handoff amendment I verified the two obligations the Admiral held to
instead.

**(a) #488's own case still WRITES, and its test pins the SAME-OWNER path
specifically.** The Admiral asked me to confirm it does not pass merely because
there happen to be two candidates. I ran #488's exact shape twice, changing
**only** the owner strings:

```
SAME owner  (the real #488 shape)
    candidates=1  files=['gauge-admiral-418-d82d1d2fe834.json']
    -> WROTE a reading
DIFFERENT owners (the discriminator)
    candidates=2  files=['gauge-skip.json']
    -> SKIPPED (sidecar only)
```

Same-owner-ness is **load-bearing**: flip it and the test's assertion fails. It
pins the same-owner path specifically. ✅

**(b) The skip stays VISIBLE.** Driven, not read for:

```
run-a: files=['gauge-skip.json', 'spine.json']
     sidecar CONTENT: {"schema_version": 1, "reason": "ambiguous-binding",
                       "observed_at": "...", "candidate_count": 2}
run-b: files=['gauge-skip.json', 'spine.json']
     sidecar CONTENT: {"schema_version": 1, "reason": "ambiguous-binding",
                       "observed_at": "...", "candidate_count": 2}
=> skip is VISIBLE on both: True
```
✅

### 2. Three files outside Allowed Scope — **CONFIRMED JUSTIFIED**

The handoff required me to verify the claim **by installing and driving the real
loader**, not by reading the argument. I did.

Real install to `/tmp/g1rev-install`. The destination **is** flat — hook, reader
and rail land as siblings, no `hooks/` subdir:

```
/tmp/g1rev-install/.claude/skills/constellation-workbench/scripts/gauge_reader.py
/tmp/g1rev-install/.claude/skills/constellation-workbench/scripts/gauge_writer_hook.py
/tmp/g1rev-install/.claude/skills/constellation-workbench/scripts/spine_rail.py
```

Driving the **installed** hook in a fresh process with `CLAUDE_PROJECT_DIR`
**unset**:

```
hook module loaded from INSTALLED layout
  _gauge_reader resolved: <module 'gauge_reader' from '.../scripts/gauge_reader.py'>
  owner_key('admiral-418') via installed hook = admiral-418-d82d1d2fe834
  => INSTALLED LOADER WORKS: True
```

Counterfactual — what a checkout-only loader would find in that install:

```
checkout-layout probe: .../constellation-workbench/gauge_reader.py exists = False
flat-layout probe    : .../constellation-workbench/scripts/gauge_reader.py exists = True
```

So a loader written only for this checkout's layout would fail open to **no
owner** in **every** install — writer emitting `gauge.json` while a leased engine
reads `gauge-<owner>.json`. A **dark** governor, exactly as claimed. The
`install_constellation.py` extension is **required, not discretionary**.

`map/INDEX.md` was likewise **forced**, not discretionary — I reverted it and
watched the guard go red:

```
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
1 failed, 147 passed, 63 subtests passed in 13.76s
--- restored ---
148 passed, 63 subtests passed in 13.65s
```

All three out-of-scope files were mechanically compelled by in-scope
requirements. **The extension stands.**

### 3. Sidecars stay per-directory and unowned — **CONFIRMED**, bounded residual

The question was whether one agent's sidecar can be read as another's. Driven:
agent B holds the lease, agent A's unowned `gauge-skip.json` planted in the
shared directory.

```
What agent B is shown:
   > CONTEXT GAUGE SILENT: this session is bound to 2 candidate spines at once...
  advisory rendered to the wrong owner : True   <- the ACCEPTED residual
  did it produce a READING / trip / refusal: False
  gr.read(<sidecar path>) = None
```

A sidecar carries no `fill_fraction`/`model`, so it can **never** become a
`Reading` and can never cause a trip or refusal for **any** owner. B's own
owner-keyed 95% reading still wins over A's sidecar. The residual is exactly what
the implementer declared — an advisory shown to an owner it does not concern —
and it is advisory-only and permit-direction. Filed as `tc2`.

---

## Checks (a)–(i), as amended

| check | verdict | how |
|---|---|---|
| (a) never refuses where it permitted | **PASS** w/ F2 | refusal paths **enumerated**, not sampled |
| (b) R2 holds TOTALLY | **PASS** | 482 real ids → 0 failures, 0 collisions |
| (c) R3 both halves | **PASS** | driven against the real engine |
| (d) R4 + #488 (as amended) | **PASS** | write confirmed, same-owner discriminating, skip visible |
| (e) R1's limit respected, not overclaimed | **PASS** | #601 guard drives correctly; result says "not completed" |
| (f) ONE owner-key definition | **PASS** | defined only in `gauge_reader.py`; both sides delegate |
| (g) blast radius complete + COUNT | **PASS** | re-enumerated: 23 files / 186 occurrences |
| (h) red/green drives real reader + real gauge | **PASS** | no patched `_read_gauge`; real files via `main()` |
| (i) no fenced file edited | **PASS** | whole-file + in-file fences both proven |

### (b) R2 — normalization is total

Harvested every real `session_id`/`engine_session` in the checkout (5496 JSON
files plus `.journal` lines) and fed **all** of them through the normalizer:

```
JSON files scanned: 5496
distinct string session ids found: 482
raw null occurrences: 671
slash-bearing ids: 111
literal '$SID' present: True
other '$'-bearing: ['$SESSION', '$SID', 'impl-300-g3-$(date']

=== TOTALITY: 482 real ids -> 0 failures ===
=== DISTINCTNESS: distinct keys 482; colliding keys 0 ===

owner_key(None)  = None -> 'gauge.json'
owner_key('$SID') = 'sid-b9b4af5d6a41' -> 'gauge-sid-b9b4af5d6a41.json'

=== reserved-word probes ===
owner_key('skip')         = 'skip-42e93b9bb77d'         -> 'gauge-skip-42e93b9bb77d.json'
owner_key('uncalibrated') = 'uncalibrated-78bc0859610f' -> 'gauge-uncalibrated-78bc0859610f.json'
owner_key('///')          = '732c4e971163'              -> 'gauge-732c4e971163.json'
owner_key('   ')          = None                        -> 'gauge.json'
```

**Zero rejections, zero key collisions.** `skip`/`uncalibrated` cannot collide
with `SKIP_FILENAME`/`UNCALIBRATED_FILENAME` — structurally, since every key ends
in `-` plus 12 hex characters. `None`/blank yields the **unowned** file, which is
the absence of an owner, not a rejection.

*(Note: the docstring cites "89 of 426"; the ruling cited "82 of 398"; I measure
111 of 482. The checkout has accumulated sessions since. The ratio ≈ a fifth of
the fleet, as R2 says. Not a defect — a measurement comment aging.)*

### (c) R3 — both halves, against the real engine

```
HALF 1: LEASELESS checklist must read the UNOWNED gauge.json and trip AS TODAY
no lease; unowned gauge.json fill=0.93
   > CONTEXT 93% (>= hard): your instruction has changed. First request a refresh...
   => LEASELESS TRIPS on gauge.json  [PASS]

HALF 2: LEASED checklist with NO owner-keyed gauge -> None, NO fallback
lease session_id = 'constellation/demo/agent/attempt-1'
owner key        = 'constellation-demo-agent-attempt-34a2b22e32b2'
files present: ['gauge.json', 'spine.json']
  (shared gauge.json still on disk, fill=0.93, and NO owner-keyed file exists)
   => LEASED + no owner-keyed file => NO reading, NO fallback to shared  [PASS]

  now write the OWNER-KEYED file and confirm it IS read:
   > CONTEXT 95% (>= hard): your instruction has changed...
   => owner-keyed file IS read  [PASS]
```

The fail-safe is still "no **attributable** reading yields `None`". It has **not**
become "no lease yields nothing".

### (e) R1's limit — #601 present and still firing

Driven on **owner-keyed** files, so the two halves demonstrably compose:

```
--- CASE A: reading sampled BEFORE the claim (the sequential relaunch case) ---
   > CONTEXT GAUGE SILENT: the last recorded reading at this path was 95% full
     on 'claude-opus-4-8', sampled 30m00s ago — too old (or otherwise r...
   => NO trip: #601 timestamp guard FIRED, stale leg-1 reading declined  [PASS]

--- CASE B: same file, reading sampled AFTER the claim ---
   > CONTEXT 95% (>= hard): your instruction has changed...
   => TRIPS  [PASS]
```

Identity picks the **file**; time decides whether the reading in it is **this
leg's**. The result correctly states `identity-not-time` is **not** completed —
no overclaim.

Also driven: the `_owner_mismatch` decline is loud, not silent, and never
refuses —

```
> CONTEXT GAUGE DECLINED: the reading at 'gauge-agent-real-ca7ac7d75630.json' is
  stamped for owner 'some-other-agent-60cb8b0ad812', but this checklist is being
  driven by session 'agent-real'...
=> 0.97 is over HARD, yet it does NOT trip.
```

### (i) fences — whole-file and in-file

Whole-file: `git diff --name-only 3bc87e93^ 3bc87e93` lists **none** of
`spine_rail.py`, `test_spine_rail.py`, `run_crew.py`, `mcp_spine_server.py`,
`.mcp.json`, `episodes/**`. Lane C's edits to `spine_rail.py`/`run_crew.py`
reached the branch through the `main` merge at `ccb8b8d8`, not this commit.

In-file (the real risk — `checklist_engine.py` **is** touched, ~158 lines). I did
not settle for "the file changed for gauge reasons"; I AST-extracted the function
bodies at both revisions and compared:

```
  _active_lease             : IDENTICAL  (7 lines)
  _reading_predates_claim   : IDENTICAL  (29 lines)
  claim                     : IDENTICAL  (110 lines)
  heartbeat                 : IDENTICAL  (13 lines)
  release                   : IDENTICAL  (16 lines)
```

#601's `claimed_at` re-stamp survives at `scripts/checklist_engine.py:1113`. The
only claim-related line anywhere in the diff is a **docstring** mention. The claim
path is untouched.

`measurement/probe_cross_key.py` is untouched and — per the handoff — I do **not**
flag it as stale; retiring it is the Commander's at `g1-integrate`.

---

## Evidence re-run

### The four discriminating node ids

**RED**, reproduced independently: detached worktree at `3bc87e93^`, confirmed
`scripts/` byte-for-byte pre-change (`git diff --stat 3bc87e93^ -- scripts/`
empty), then **only** the four new test files copied across:

```
16 failed, 1 passed in 0.32s
```

Matching the implementer's reported `16 failed, 1 passed` exactly.

**GREEN**, at HEAD:

```
4 passed, 13 subtests passed in 0.18s
```

### The fresh-process demonstration, both directions

Same script, byte-identical in both runs
(`md5 6edb93c35afa3158ea5c4a434d1d6a5b`), run at equal depth in each tree:

**BEFORE** (pre-change source):
```
DISPATCHED agent's file  : gauge.json  -> {... 'fill_fraction': 0.9 ...}
ORCHESTRATOR's file      : gauge.json  -> {... 'fill_fraction': 0.9 ...}
gauge-skip.json          : None

VERDICT: COLLISION -- both agents resolve to ONE file, gauge.json.
  The surviving fill is 0.9; the other agent's reading was destroyed with no
  skip sidecar and no guard.
```

**AFTER** (HEAD):
```
DISPATCHED agent's file  : gauge-owner-dispatched-b6445a5eac4f.json
  -> {..., 'fill_fraction': 0.02, ..., 'owner': 'owner-dispatched-b6445a5eac4f'}
ORCHESTRATOR's file      : gauge-owner-orchestrator-8c6bb04ff8f5.json
  -> {..., 'fill_fraction': 0.9, ..., 'owner': 'owner-orchestrator-8c6bb04ff8f5'}
shared gauge.json        : None

VERDICT: EACH AGENT KEPT ITS OWN READING.
```

**The defect is measured, not assumed.**

### (h) the evidence drives the real reader

`TripGaugeReadingOwnership` does **not** patch `_read_gauge` — its `_write_gauge`
helper writes the acting session's real owner-keyed file and the leaseless test
drives through `main()`. The `mock.patch.object(E, "_read_gauge", ...)` hits in
`test_checklist_engine.py` are a different, pre-existing band-threshold class.

### (g) blast radius, re-enumerated

The prescribed Wiring Grep, re-run verbatim at HEAD:

```
FILE COUNT excluding map/   = 23   (implementer: 23)
OCCURRENCES excluding map/  = 186  (implementer: 186)
TRACKED FILE COUNT (git grep) = 23
```

**Reproduces the implementer's reconciled figures exactly**, and every per-file
disposition in their table matches my per-file counts (`gauge_writer_hook` 25,
`test_checklist_engine` 31, `test_gauge_chain` 37, `test_gauge_writer` 20,
`test_gauge_reader` 13, docs 19+1, episodes sum 15, notes sum 8).

My first unscoped pass returned **68** files; the extra 45 are `map/` per-module
packets, which `.gitignore:73 map/*` excludes (confirmed with `git check-ignore`)
and which are not deliverables. `git grep` over tracked files independently
returns the same 23. The implementer's correction of the dispatch figure
(occurrences vs matching lines) is validated.

### Both suite numbers, and their difference

Both measured by me, `__pycache__` cleared first, `SPINE_*` unset.

| tree | result |
|---|---|
| **branch** HEAD `ccb8b8d8` | `3104 passed, 6 skipped, 1165 subtests passed in 129.46s` |
| **main baseline** `d7b911a7`, re-measured at gate time in a clean detached worktree | `3089 passed, 7 skipped, 1146 subtests passed in 126.52s` |

```
branch failures: 0  main failures: 0
IDENTICAL failure sets (both empty)
```

**Failure-set difference = ZERO** against a green baseline. That is the bar and it
is met. The branch figure matches the Commander's gate-time re-measurement
(3104 / 6 skipped) exactly. As instructed I ignored the stale 3057 and 3089-from-
`LAUNCH_ORDER-3` figures — though note my freshly measured `main` baseline
coincidentally lands on 3089 too.

### Commands run

```bash
git diff --stat 3bc87e93^ 3bc87e93
git show 3bc87e93 -- scripts/gauge_reader.py scripts/hooks/gauge_writer_hook.py \
                     scripts/checklist_engine.py scripts/install_constellation.py
git log --oneline 3bc87e93..HEAD -- scripts/ tests/ docs/
git diff --name-only 3bc87e93^ 3bc87e93 | grep -E 'spine_rail|run_crew|mcp_spine_server|\.mcp\.json|^episodes/'
git worktree add --detach /tmp/g1rev-main-baseline main
git worktree add --detach /tmp/g1rev-red 3bc87e93^
find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q          # both trees
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q <the four node ids>
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_code_map.py
py scripts/install_constellation.py --agent claude --scope project --project /tmp/g1rev-install --force
py .agent-work/cleanup-b-context-identity/measurement/demo_owner_keyed_gauge.py   # both trees
py scripts/verify_fowler_pass.py .agent-work/cleanup-b-context-identity/FOWLER_PASS.json
```

Plus driver scripts for R2 totality, R3 both halves, R4 row 2, the same-owner
discriminator, the visible-skip check, the #601 sequential case, the
`_owner_mismatch` case, the sidecar cross-read, and the two mutation tests.
Output for each is pasted above or in the survey's findings.

**Both mutations were asserted applied and then restored byte-identical**
(`git diff --exit-code` clean for `scripts/hooks/gauge_writer_hook.py` and
`map/INDEX.md`). No implementation file is modified by this review.

---

## Fowler refactoring pass

Recorded at `.agent-work/cleanup-b-context-identity/FOWLER_PASS.json`;
`scripts/verify_fowler_pass.py` exits **0**.

```
fowler pass ok: smells=12,
  flagged=['long-method', 'duplicated-code', 'data-clumps'],
  overridden=['primitive-obsession', 'shotgun-surgery', 'divergent-change',
              'comments-as-deodorant']
```

**Flagged** (all observations, none blocking): `handle_post_tool_use` length
(F4), the triplicated `"gauge.json"` literal (F3), and the `(gauge_path, owner)`
2-tuple earning a `NamedTuple` in a file that already uses a frozen dataclass.

**Overridden**, each with the standard that wins and why it subordinates the
smell: **primitive-obsession** (the owner crosses a process boundary as a
filename and a JSON field; `gauge_reader`'s portability contract forbids the
import, and R2 requires a *total normalizer*, not a constructor that could
reject); **shotgun-surgery** (the ripple is inherent to a cross-process **file
format**, and `SCRIPT_RUNTIME_COMPANIONS` is the repo's own documented mechanism
for that coupling — which this change uses); **divergent-change**
(`ADMIRAL_RULING-1` governs `checklist_engine.py` by explicit **region** fence
rather than by splitting, and splitting would itself breach the fence);
**comments-as-deodorant** (`global-crew.md` "Agent-facing. Dense by design." — the
comments carry decision provenance that lives nowhere else while the map is
DEGRADED, over code that is short and plainly named).

**speculative-generality** was checked specifically rather than waved past:
`resolve_gauge_path` is kept alongside `resolve_gauge_targets` but retains real
current callers and tests, so it is a compatibility view, not an unused seam.

---

## Triage candidates

1. **`tc1` — pin R4 row 2 with a test** (from F1): one binding key, one
   `engine_session`, two **distinct** work directories → **both** owner-keyed
   files written. Today that branch can be reverted with the whole gauge suite
   staying green.
2. **`tc2` — sidecars are per-directory while readings are per-owner**, so one
   owner's `gauge-skip.json` / `gauge-uncalibrated.json` advisory can be rendered
   to a different owner sharing the work directory. Verified advisory-only:
   `gauge_reader.read()` on a sidecar returns `None`, so it can never become a
   `Reading` and never causes a trip or refusal. Bounded residual, widened
   slightly by #600.
3. **`tc3` — a `SessionStart`/stop hook told this crew to drive its parent's
   `execute` gate** (see Workflow Feedback). Same defect class as #600 one layer
   up. **Second occurrence** — the g1 implementer reported it too.

The implementer's own four candidates are accurate and I contradict none of them.

---

## Workflow Feedback

- **The `SessionStart` hook misfire is real, and it is now reproducible.** My
  environment carried
  `SPINE_FILE=.agent-work/cleanup-b-context-identity/spine.json` and
  `SPINE_SESSION=constellation/cleanup-b-context-identity/execute/commander` —
  the **parent Commander's** spine, inherited, plus a `SessionStart` block
  instructing me to load `constellation-commander`, write `STATE_NOTE.md`, and
  drive `execute.json` gate by gate. **That is not my run.** The reviewer skill
  says "`spine_status` is your first call" and "do not author a survey of your own
  when a spine is already bound", which points straight at the wrong spine. I
  concluded nothing was bound *for me* (my `SPINE_SESSION` names the parent's role,
  not `g1-review/reviewer/attempt-1`), authored my own survey at the handoff's
  path per the skill's fallback branch, and never touched the parent's spine.
  The handoff's closing warning is what made this unambiguous and it saved the
  run — **keep that warning in future crew handoffs until the hook is fixed.**
  Cost me one decision, not a wave.
- **`--session-id` is required on every mutating engine verb but omitted from the
  skill walkthrough.** My first `start` was refused. The implementer reported the
  identical friction. This is now two crews in a row losing a cycle to the same
  gap — worth one line in the skill.
- **`advance` vs `record` on a survey.** The skill's step 3 says "integrate it,
  `advance` that check", but on a `survey` checklist `advance` is refused
  (`REFUSED: advance is for gated checklists; use record`) — `record` is the
  advancing verb. Minor, but it cost a refused call to discover.
- **The handoff was excellent on the two things that mattered most.** Telling me
  the diff range had moved (`git show 3bc87e93`, not `git diff a69bbac4`) saved me
  from reviewing lanes C and D's changes as if they were this one. And separating
  the **whole-file** fences from the **in-file** claim-path fence, with an explicit
  "do not settle for 'the file changed for gauge reasons'", is what made me
  AST-extract the claim path instead of eyeballing hunks. More handoffs should
  distinguish those two fence kinds.
- **One evidence-standard gap.** The handoff (rightly) warned about patched
  readers, injected `CLAUDE_PROJECT_DIR`, and stale bytecode. It did not ask
  whether the *new* branches are themselves covered — and that is where the only
  finding is. A line like "for each behavioural row you implement, show a mutation
  that turns it red" would have surfaced F1 at implement time rather than review
  time.
- **Suite figures: state the tree AND the unit.** Three different totals (3057,
  3089, 3104) circulate in this lane's documents, and my freshly measured `main`
  baseline is *also* 3089 — the same number as a stale figure, for a different
  tree. The handoff's instruction to measure both sides at gate time and report a
  **failure-set difference** rather than an absolute is the right standard and it
  disambiguated this cleanly.

---

## Cleanup

Temporary worktrees `/tmp/g1rev-main-baseline` and `/tmp/g1rev-red`, and temp
dirs under `/tmp/g1rev-*`, were created for measurement and are removed. No
implementation file was modified by this review; both mutation tests were
restored byte-identical and verified with `git diff --exit-code`.

## Return status

`complete` — Verdict `APPROVE`.
